"""Application level configuration management."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import yaml  # type: ignore[import]

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Resolved configuration for the converter."""

    source_dir: Path = Path("docs")
    output_dir: Path = Path("build/html")
    theme: str = "github"
    theme_dirs: list[Path] = field(default_factory=list)
    clean_output: bool = True
    copy_static: bool = True
    watch: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)
    ignore: list[str] = field(default_factory=list)

    def apply_updates(self, data: Mapping[str, Any], base_path: Optional[Path] = None) -> None:
        """Apply updates from a dictionary onto the current configuration."""

        if not data:
            return

        for key, value in data.items():
            if value is None:
                continue

            if self._apply_known_setting(key, value, base_path):
                continue

            # Preserve unknown values for template usage.
            self.extra[key] = value

    def _apply_path_setting(self, key: str, value: Any, base_path: Optional[Path]) -> None:
        path_value = Path(value)
        if base_path and not path_value.is_absolute():
            path_value = (base_path / path_value).resolve()
        setattr(self, key, path_value)

    def _apply_boolean_setting(self, key: str, value: Any) -> None:
        setattr(self, key, bool(value))

    def _merge_metadata(self, value: Any) -> None:
        if isinstance(value, Mapping):
            self.metadata.update(value)  # type: ignore[arg-type]
        else:
            logger.warning("metadata expects mapping, got %s", type(value))

    def _normalise_ignore_setting(self, value: Any) -> list[str]:
        patterns: Iterable[Any]
        if isinstance(value, (str, Path)):
            patterns = [value]
        elif isinstance(value, Iterable):
            patterns = value
        else:
            logger.warning("ignore expects iterable of strings, got %s", type(value))
            return list(self.ignore)

        normalised: list[str] = []
        for item in patterns:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                normalised.append(text)
        return normalised

    def _apply_known_setting(self, key: str, value: Any, base_path: Optional[Path]) -> bool:
        if key in {"source_dir", "output_dir"}:
            self._apply_path_setting(key, value, base_path)
            return True

        if key == "theme_dirs":
            self.theme_dirs = self._normalise_theme_dirs(value, base_path)
            return True

        if key == "theme":
            self.theme = str(value)
            return True

        if key in {"clean_output", "copy_static", "watch"}:
            self._apply_boolean_setting(key, value)
            return True

        if key == "metadata":
            self._merge_metadata(value)
            return True

        if key == "ignore":
            self.ignore = self._normalise_ignore_setting(value)
            return True

        return False

    @staticmethod
    def _normalise_theme_dirs(value: Any, base_path: Optional[Path]) -> list[Path]:
        dirs: Iterable[Any]
        if isinstance(value, (str, Path)):
            dirs = [value]
        elif isinstance(value, Iterable):
            dirs = value
        else:
            logger.warning("theme_dirs expects iterable of paths, got %s", type(value))
            return []

        normalised: list[Path] = []
        for item in dirs:
            if not item:
                continue
            path = Path(item)
            if base_path and not path.is_absolute():
                path = (base_path / path).resolve()
            normalised.append(path)
        return normalised


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    """Load raw configuration from YAML file."""

    if path is None:
        return {}

    path = path.resolve()
    if not path.exists():
        logger.warning("Configuration file %s does not exist", path)
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, Mapping):
            logger.warning("Configuration file %s does not contain a mapping", path)
            return {}
        return dict(data)
    except yaml.YAMLError as exc:
        logger.error("Failed to parse configuration file %s: %s", path, exc)
        raise
