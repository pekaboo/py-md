"""Theme management and rendering utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml  # type: ignore[import]
from jinja2 import Environment, Template
from jinja2.loaders import DictLoader
from pygments.formatters.html import HtmlFormatter

logger = logging.getLogger(__name__)

THEME_PACKAGE = "md2html.themes"


class ThemeNotFoundError(RuntimeError):
    """Raised when the requested theme cannot be located."""


@dataclass
class Theme:
    name: str
    template: Template
    config: Dict[str, Any]
    inline_styles: str
    syntax_styles: str

    def render(
        self,
        *,
        content: str,
        metadata: Dict[str, Any],
        toc: Iterable[Dict[str, Any]],
        front_matter: Dict[str, Any],
        site_metadata: Dict[str, Any],
    ) -> str:
        inline_block = ThemeManager._wrap_style_block(self.inline_styles)
        syntax_block = ThemeManager._wrap_style_block(self.syntax_styles)
        context = {
            "content": content,
            "metadata": metadata,
            "front_matter": front_matter,
            "site": site_metadata,
            "style_block": inline_block,
            "syntax_block": syntax_block,
            "theme": self.config,
            "toc": list(toc),
        }
        rendered_html = self.template.render(context)
        snippet = site_metadata.get("live_reload_snippet") if isinstance(site_metadata, dict) else None
        if snippet:
            closing_tag = "</body>"
            if closing_tag in rendered_html:
                return rendered_html.replace(closing_tag, f"{snippet}\n{closing_tag}", 1)
            return f"{rendered_html}\n{snippet}"
        return rendered_html

    def default_hide_title(self) -> str:
        return str(self.config.get("default_hide_title", "点击展开"))

    def default_hide_collapse_title(self) -> str:
        return str(self.config.get("default_hide_collapse_title", "收起"))

    def admonition_defaults(self) -> Dict[str, Dict[str, str]]:
        return self.config.get("admonitions", {})


class ThemeManager:
    """Locate and load theme assets."""

    def __init__(self, extra_paths: Optional[Iterable[Path]] = None) -> None:
        self.extra_paths = [Path(path) for path in (extra_paths or [])]

    def load(self, theme_name: str) -> Theme:
        logger.debug("Loading theme '%s'", theme_name)

        theme = self._load_from_path_arguments(theme_name)
        if theme:
            return theme

        theme = self._load_from_builtin(theme_name)
        if theme:
            return theme

        raise ThemeNotFoundError(f"Theme '{theme_name}' not found")

    def _load_from_path_arguments(self, theme_name: str) -> Optional[Theme]:
        # Allow direct path usage
        candidate = Path(theme_name)
        if candidate.exists():
            return self._build_theme(candidate, candidate.name)

        for root in self.extra_paths:
            candidate = root / theme_name
            if candidate.exists():
                return self._build_theme(candidate, theme_name)

        return None

    def _load_from_builtin(self, theme_name: str) -> Optional[Theme]:
        package = f"{THEME_PACKAGE}.{theme_name}"
        try:
            traversable = resources.files(package)
        except ModuleNotFoundError:
            return None

        with resources.as_file(traversable) as temp_path:
            return self._build_theme(Path(temp_path), theme_name)

    def _build_theme(self, root: Path, theme_name: str) -> Theme:
        logger.debug("Building theme from %s", root)

        config = self._load_yaml(root / "config.yaml")
        template_name = config.get("template", "base.html")
        template_content = (root / template_name).read_text(encoding="utf-8")

        styles_path = root / "styles.css"
        inline_styles = styles_path.read_text(encoding="utf-8") if styles_path.exists() else ""

        pygments_style_name = config.get("pygments_style", "friendly")
        syntax_styles = self._resolve_syntax_styles(root, pygments_style_name)

        env = Environment(loader=DictLoader({template_name: template_content}))
        template = env.get_template(template_name)

        return Theme(
            name=theme_name,
            template=template,
            config=config,
            inline_styles=inline_styles,
            syntax_styles=syntax_styles,
        )

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:  # type: ignore[attr-defined]
            logger.error("Failed to parse theme config %s: %s", path, exc)
            raise

        if not isinstance(data, dict):
            logger.warning("Theme config %s must contain a mapping", path)
            return {}
        return data

    @staticmethod
    def _resolve_syntax_styles(root: Path, pygments_style_name: str) -> str:
        syntax_css_path = root / "syntax.css"
        if syntax_css_path.exists():
            return syntax_css_path.read_text(encoding="utf-8")

        formatter = HtmlFormatter(style=pygments_style_name)  # type: ignore[arg-type]
        return formatter.get_style_defs(".md2html-code")

    @staticmethod
    def _wrap_style_block(css: str) -> str:
        css = css.strip()
        if not css:
            return ""
        return f"<style>\n{css}\n</style>"
