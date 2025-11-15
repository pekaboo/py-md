"""Utility helpers for the markdown site generator."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml  # type: ignore[import]

FRONT_MATTER_BOUNDARY = "---"
MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}


def ensure_directory(path: Path) -> None:
    """Create directory if it does not exist."""

    path.mkdir(parents=True, exist_ok=True)


def is_markdown_file(path: Path) -> bool:
    return path.suffix.lower() in MARKDOWN_EXTENSIONS


def copy_static_resource(source: Path, destination: Path) -> None:
    """Copy static assets preserving metadata."""

    ensure_directory(destination.parent)
    shutil.copy2(source, destination)


def slugify(value: str) -> str:
    """Generate URL friendly slug from a heading."""

    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-") or "section"


def parse_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    """Split YAML front matter from the markdown body."""

    if not text.startswith(FRONT_MATTER_BOUNDARY):
        return {}, text

    lines = text.splitlines()
    if len(lines) < 2:
        return {}, text

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONT_MATTER_BOUNDARY:
            closing_index = index
            break

    if closing_index is None:
        return {}, text

    raw_front_matter = "\n".join(lines[1:closing_index])
    body_lines = lines[closing_index + 1 :]
    body = "\n".join(body_lines)

    if raw_front_matter.strip():
        try:
            data = yaml.safe_load(raw_front_matter) or {}
        except yaml.YAMLError as exc:  # type: ignore[attr-defined]
            raise ValueError(f"Invalid front matter: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("Front matter must be a YAML mapping")
    else:
        data = {}

    return data, body
