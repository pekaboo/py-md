"""Command line interface for md2html."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .config import AppConfig, load_config
from .converter import convert_docs_directory
from .theme import ThemeManager

LOG_FORMAT = "[%(levelname)s] %(message)s"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2html",
        description="Convert Markdown documents under a directory into themed HTML output.",
    )
    parser.add_argument(
        "--exclude-hide",
        dest="exclude_hide",
        action="store_true",
        help="Exclude all ::: hide blocks from output HTML",
    )
    parser.add_argument("--src", dest="source_dir", help="Source directory containing markdown files")
    parser.add_argument("--dst", dest="output_dir", help="Destination directory for generated HTML")
    parser.add_argument("--theme", dest="theme", help="Theme name or path to use")
    parser.add_argument(
        "--theme-dir",
        action="append",
        dest="theme_dirs",
        help="Additional directory to look for custom themes (can be supplied multiple times)",
    )
    parser.add_argument(
        "--config",
        dest="config",
        default="md2html.config.yaml",
        help="Path to configuration YAML file (default: md2html.config.yaml)",
    )
    parser.add_argument(
        "--no-clean",
        dest="clean_output",
        action="store_false",
        help="Do not clean the output directory before building",
    )
    parser.add_argument(
        "--no-copy-static",
        dest="copy_static",
        action="store_false",
        help="Disable copying non-markdown static assets",
    )
    parser.add_argument(
        "--watch",
        dest="watch",
        action="store_true",
        help="Watch source directory and rebuild on file changes",
    )
    parser.add_argument(
        "--site-title",
        dest="site_title",
        help="Override site title metadata for templates",
    )
    parser.add_argument(
        "--site-description",
        dest="site_description",
        help="Override site description metadata for templates",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser


def resolve_configuration(args: argparse.Namespace) -> AppConfig:
    cli_updates: Dict[str, Any] = {}
    if getattr(args, "exclude_hide", False):
        cli_updates["exclude_hide"] = True
    config = AppConfig()

    config_path = Path(args.config).resolve() if args.config else None
    file_payload = load_config(config_path)
    base_path = config_path.parent if config_path else Path.cwd()
    config.apply_updates(file_payload, base_path=base_path)

    for key in ("source_dir", "output_dir", "theme", "theme_dirs"):
        value = getattr(args, key, None)
        if value is not None:
            cli_updates[key] = value

    if hasattr(args, "clean_output") and args.clean_output is not None:
        cli_updates["clean_output"] = args.clean_output
    if hasattr(args, "copy_static") and args.copy_static is not None:
        cli_updates["copy_static"] = args.copy_static
    if getattr(args, "watch", None):
        cli_updates["watch"] = True

    config.apply_updates(cli_updates, base_path=Path.cwd())

    if getattr(args, "site_title", None):
        config.metadata["title"] = args.site_title
    if getattr(args, "site_description", None):
        config.metadata["description"] = args.site_description

    return config


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format=LOG_FORMAT)

    try:
        config = resolve_configuration(args)
        logging.debug("Resolved configuration: %s", config)
        convert_docs_directory(config, theme_manager=ThemeManager(config.theme_dirs))
    except Exception as exc:  # pylint: disable=broad-except
        logging.error("md2html failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
