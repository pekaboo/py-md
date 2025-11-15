"""Core conversion logic for Markdown -> HTML site generation."""

from __future__ import annotations

import logging
import re
import shutil
import threading
import time
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from markdown_it import MarkdownIt  # type: ignore[import]
from markdown_it.token import Token  # type: ignore[import]
from mdit_py_plugins.container import container_plugin  # type: ignore[import]
from mdit_py_plugins.front_matter import front_matter_plugin  # type: ignore[import]
from mdit_py_plugins.tasklists import tasklists_plugin  # type: ignore[import]
from watchdog.events import FileSystemEventHandler  # type: ignore[import]
from watchdog.observers import Observer  # type: ignore[import]

from .config import AppConfig
from .theme import Theme, ThemeManager
from .utils import copy_static_resource, ensure_directory, is_markdown_file, parse_front_matter, slugify

logger = logging.getLogger(__name__)

_HEADING_PATTERN = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*(?:#+\s*)?$", re.MULTILINE)
_OUTPUT_SEGMENT_SANITISER = re.compile(r"[^0-9A-Za-z\u4e00-\u9fff._-]")
_OUTPUT_SEGMENT_WHITESPACE = re.compile(r"\s+")


def format_segment_title(segment: str) -> str:
    """Convert a path segment into a human friendly title."""

    cleaned = segment.replace("_", " ").replace("-", " ").strip()
    return cleaned or segment


@dataclass
class RenderResult:
    source: Path
    destination: Path
    html: str
    metadata: Dict[str, Any]
    toc: List[Dict[str, Any]]
    front_matter: Dict[str, Any]


@dataclass
class RenderedDocument:
    html: str
    metadata: Dict[str, Any]
    toc: List[Dict[str, Any]]
    front_matter: Dict[str, Any]


class MarkdownRenderer:
    """Render markdown into themed HTML fragments."""

    def __init__(self, theme: Theme, site_metadata: Optional[Dict[str, Any]] = None) -> None:
        self.theme = theme
        self.site_metadata = dict(site_metadata or {})
        self.md = self._create_markdown_parser()

    def render(self, text: str, *, source_path: Path) -> RenderedDocument:
        front_matter, body = parse_front_matter(text)
        env: Dict[str, Any] = {
            "doc_path": str(source_path),
            "front_matter": front_matter,
            "default_hide_title": self.theme.default_hide_title(),
            "admonitions": self.theme.admonition_defaults(),
        }

        tokens = self.md.parse(body, env)
        toc = self._decorate_headings(tokens)
        html_body = self.md.renderer.render(tokens, self.md.options, env)

        metadata = self._build_metadata(front_matter, tokens, source_path)
        rendered_html = self.theme.render(
            content=html_body,
            metadata=metadata,
            toc=toc,
            front_matter=front_matter,
            site_metadata=self.site_metadata,
        )
        return RenderedDocument(
            html=rendered_html,
            metadata=metadata,
            toc=toc,
            front_matter=front_matter,
        )

    def _create_markdown_parser(self) -> MarkdownIt:
        md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})
        md.use(tasklists_plugin, enabled=True)
        md.use(front_matter_plugin)
        md.use(container_plugin, "hide", render=self._render_hide_container, validate=self._validate_container)  # type: ignore[arg-type]
        md.use(container_plugin, "note", render=self._render_admonition("note"), validate=self._validate_container)  # type: ignore[arg-type]
        md.use(container_plugin, "warning", render=self._render_admonition("warning"), validate=self._validate_container)  # type: ignore[arg-type]
        return md

    def _decorate_headings(self, tokens: List[Token]) -> List[Dict[str, Any]]:
        toc: List[Dict[str, Any]] = []
        slug_counts: Dict[str, int] = {}

        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token.type == "heading_open" and token.tag.startswith("h"):
                level = int(token.tag[1])
                inline = tokens[index + 1]
                text = inline.content.strip()
                slug_base = slugify(text)
                count = slug_counts.get(slug_base, 0)
                slug_counts[slug_base] = count + 1
                slug = slug_base if count == 0 else f"{slug_base}-{count}"
                token.attrSet("id", slug)
                toc.append({"level": level, "title": text, "slug": slug})
                logger.debug("Heading '%s' assigned id '%s'", text, slug)
                index += 2
                continue
            index += 1

        return toc

    def _build_metadata(
        self,
        front_matter: Dict[str, Any],
        tokens: List[Token],
        source_path: Path,
    ) -> Dict[str, Any]:
        metadata = dict(front_matter)
        if "title" not in metadata:
            for idx, token in enumerate(tokens):
                if token.type == "heading_open" and token.tag == "h1":
                    inline = tokens[idx + 1]
                    metadata["title"] = inline.content.strip()
                    break
        if not metadata.get("title"):
            metadata["title"] = format_segment_title(source_path.stem)
        return metadata

    @staticmethod
    def _validate_container(params: str, markup: str) -> bool:
        return bool(params.strip())

    def _render_hide_container(self, tokens: List[Token], idx: int, options: Dict[str, Any], env: Dict[str, Any]) -> str:
        token = tokens[idx]
        params = token.info.strip()
        title = params.split(" ", 1)[1].strip() if " " in params else ""
        if token.nesting == 1:
            summary = title or env.get("default_hide_title", "点击展开")
            summary = escape(summary)
            return (
                '<details class="md2html-hide">\n'
                f"  <summary>{summary}</summary>\n"
                "  <div class=\"md2html-hide__body\">\n"
            )
        return "  </div>\n</details>\n"

    def _render_admonition(self, kind: str):
        defaults = self.theme.admonition_defaults()
        default_title = defaults.get(kind, {}).get("title", kind.title())
        css_class = f"md2html-admonition md2html-admonition--{kind}"

        def _renderer(tokens: List[Token], idx: int, options: Dict[str, Any], env: Dict[str, Any]) -> str:
            token = tokens[idx]
            params = token.info.strip()
            label = params.split(" ", 1)[1].strip() if " " in params else ""
            title = escape(label or default_title)
            if token.nesting == 1:
                return (
                    f'<div class="{css_class}">\n'
                    f"  <div class=\"md2html-admonition__title\">{title}</div>\n"
                    "  <div class=\"md2html-admonition__body\">\n"
                )
            return "  </div>\n</div>\n"

        return _renderer


class SiteBuilder:
    """Build the entire site from source markdown documents."""

    def __init__(self, config: AppConfig, theme: Theme) -> None:
        self.config = config
        self.theme = theme
        site_metadata = dict(config.metadata)
        site_metadata.update(config.extra)
        self.renderer = MarkdownRenderer(theme, site_metadata=site_metadata)
        self._output_path_map: Dict[Tuple[str, ...], List[str]] = {}
        self._used_output_paths: set[Tuple[str, ...]] = set()

    def build_all(self) -> List[RenderResult]:
        logger.info("Starting static site build from %s", self.config.source_dir)
        if not self.config.source_dir.exists():
            raise FileNotFoundError(f"Source directory {self.config.source_dir} does not exist")

        if self.config.clean_output and self.config.output_dir.exists():
            logger.debug("Cleaning output directory %s", self.config.output_dir)
            shutil.rmtree(self.config.output_dir)

        ensure_directory(self.config.output_dir)
        self._output_path_map.clear()
        self._used_output_paths.clear()

        navigation = self._build_navigation_structure()
        results: List[RenderResult] = []
        for path in sorted(self.config.source_dir.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(self.config.source_dir)
            if is_markdown_file(path):
                segments = list(relative.with_suffix("").parts)
                if tuple(segments) not in self._output_path_map:
                    self._register_output_path(segments)
                result = self._build_single_markdown(path, navigation)
                results.append(result)
            elif self.config.copy_static:
                destination = self.config.output_dir / relative
                copy_static_resource(path, destination)
                logger.debug("Copied static asset %s -> %s", path, destination)

        return results

    def _build_single_markdown(
        self,
        source: Path,
        navigation: List[Dict[str, Any]],
    ) -> RenderResult:
        logger.debug("Rendering %s", source)
        relative = source.relative_to(self.config.source_dir)
        current_segments = list(relative.with_suffix("").parts)
        output_segments = self._output_path_map.get(tuple(current_segments))
        if output_segments is None:
            output_segments = self._register_output_path(current_segments)
        destination = self._build_destination_path(output_segments)
        current_url = self._segments_to_url(output_segments)
        ensure_directory(destination.parent)
        self.renderer.site_metadata["navigation"] = navigation
        self.renderer.site_metadata["current_segments"] = current_segments
        self.renderer.site_metadata["current_page"] = current_url
        text = source.read_text(encoding="utf-8")
        rendered = self.renderer.render(text, source_path=source)
        destination.write_text(rendered.html, encoding="utf-8")
        logger.info("Generated %s", destination)
        return RenderResult(
            source=source,
            destination=destination,
            html=rendered.html,
            metadata=rendered.metadata,
            toc=rendered.toc,
            front_matter=rendered.front_matter,
        )

    def _build_navigation_structure(self) -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []
        for path in sorted(self.config.source_dir.rglob("*")):
            if path.is_dir() or not is_markdown_file(path):
                continue
            relative = path.relative_to(self.config.source_dir)
            segments = list(relative.with_suffix("").parts)
            title = self._extract_title(path)
            output_segments = self._register_output_path(segments)
            documents.append(
                {
                    "segments": segments,
                    "title": title,
                    "url": self._segments_to_url(output_segments),
                    "output_segments": output_segments,
                }
            )

        tree: Dict[str, Any] = {}
        for doc in documents:
            current = tree
            segments = doc["segments"]
            for index, segment in enumerate(segments):
                node = current.setdefault(
                    segment,
                    {
                        "title": format_segment_title(segment),
                        "segments": list(segments[: index + 1]),
                        "children": {},
                        "url": None,
                        "is_leaf": False,
                    },
                )
                if index == len(segments) - 1:
                    node["title"] = doc["title"]
                    node["url"] = doc["url"]
                    node["is_leaf"] = True
                current = node["children"]

        return self._serialise_navigation(tree)

    def _serialise_navigation(self, tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for name, data in tree.items():
            children = self._serialise_navigation(data["children"])
            nodes.append(
                {
                    "name": name,
                    "title": data["title"],
                    "url": data["url"],
                    "is_leaf": data.get("is_leaf", False),
                    "segments": list(data["segments"]),
                    "children": children,
                }
            )
        return nodes

    def _register_output_path(self, segments: List[str]) -> List[str]:
        normalised = [self._normalise_segment(segment) for segment in segments]
        if not normalised:
            normalised = ["index"]

        base_name = normalised[-1] or "page"
        candidate = tuple(normalised)
        suffix = 2
        while candidate in self._used_output_paths:
            normalised[-1] = f"{base_name}-{suffix}"
            candidate = tuple(normalised)
            suffix += 1

        self._used_output_paths.add(candidate)
        result = list(normalised)
        self._output_path_map[tuple(segments)] = result
        return result

    def _build_destination_path(self, segments: List[str]) -> Path:
        if not segments:
            return self.config.output_dir / "index.html"

        directory = self.config.output_dir.joinpath(*segments[:-1]) if len(segments) > 1 else self.config.output_dir
        return directory / f"{segments[-1]}.html"

    @staticmethod
    def _segments_to_url(segments: List[str]) -> str:
        if not segments:
            return "index.html"
        parts = list(segments)
        parts[-1] = f"{parts[-1]}.html"
        return "/".join(parts)

    @staticmethod
    def _normalise_segment(segment: str) -> str:
        cleaned = segment.strip()
        cleaned = _OUTPUT_SEGMENT_WHITESPACE.sub("-", cleaned)
        cleaned = _OUTPUT_SEGMENT_SANITISER.sub("-", cleaned)
        cleaned = cleaned.strip("-_.")
        return cleaned.lower() or "page"

    def _extract_title(self, path: Path) -> str:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Unable to read %s: %s", path, exc)
            return format_segment_title(path.stem)

        try:
            front_matter, body = parse_front_matter(text)
        except ValueError as exc:
            logger.warning("Invalid front matter in %s: %s", path, exc)
            front_matter, body = {}, text

        title_value = front_matter.get("title") if isinstance(front_matter, dict) else None
        if isinstance(title_value, str) and title_value.strip():
            return title_value.strip()

        match = _HEADING_PATTERN.search(body)
        if match:
            heading = match.group(2).strip()
            return heading

        return format_segment_title(path.stem)

    def watch(self, on_rebuild: Optional[Callable[[Path], None]] = None) -> None:
        logger.info("Entering watch mode. Monitoring %s", self.config.source_dir)
        observer = Observer()
        handler = _WatchHandler(self, on_rebuild=on_rebuild)
        observer.schedule(handler, str(self.config.source_dir), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info("Stopping watch mode")
        finally:
            observer.stop()
            observer.join()

    def rebuild_path(self, path: Path) -> None:
        if path.is_dir():
            return

        if is_markdown_file(path):
            logger.debug("Markdown change detected; rebuilding entire site")
            self.build_all()
            return

        relative = path.relative_to(self.config.source_dir)
        if self.config.copy_static:
            destination = self.config.output_dir / relative
            copy_static_resource(path, destination)
            logger.info("Copied static asset %s", relative)


class _WatchHandler(FileSystemEventHandler):
    """React to filesystem updates by rebuilding the changed target."""

    def __init__(self, builder: SiteBuilder, *, on_rebuild: Optional[Callable[[Path], None]] = None) -> None:
        super().__init__()
        self.builder = builder
        self._lock = threading.Lock()
        self._callback = on_rebuild

    def on_modified(self, event):  # type: ignore[override]
        self._handle_event(event)

    def on_created(self, event):  # type: ignore[override]
        self._handle_event(event)

    def on_moved(self, event):  # type: ignore[override]
        self._handle_event(event, destination=Path(event.dest_path))

    def on_deleted(self, event):  # type: ignore[override]
        if event.is_directory:
            return
        path = Path(event.src_path)
        with self._lock:
            logger.debug("Detected deletion of %s", path)
            try:
                self.builder.build_all()
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Failed to rebuild after deletion %s: %s", path, exc)
            else:
                if self._callback:
                    try:
                        self._callback(path)
                    except Exception as cb_exc:  # pylint: disable=broad-except
                        logger.error("Watch callback failed for %s: %s", path, cb_exc)

    def _handle_event(self, event, *, destination: Optional[Path] = None) -> None:
        if event.is_directory:
            return
        path = destination or Path(event.src_path)
        if not path.exists():
            return
        with self._lock:
            logger.debug("Detected change in %s", path)
            try:
                self.builder.rebuild_path(path)
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Failed to rebuild %s: %s", path, exc)
            else:
                if self._callback:
                    try:
                        self._callback(path)
                    except Exception as cb_exc:  # pylint: disable=broad-except
                        logger.error("Watch callback failed for %s: %s", path, cb_exc)


def convert_docs_directory(config: AppConfig, *, theme_manager: Optional[ThemeManager] = None) -> List[RenderResult]:
    """High level helper used by the CLI."""

    theme_manager = theme_manager or ThemeManager(config.theme_dirs)
    theme = theme_manager.load(config.theme)
    builder = SiteBuilder(config, theme)
    results = builder.build_all()
    if config.watch:
        builder.watch()
    return results
