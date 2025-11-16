from pathlib import Path

from md2html.config import AppConfig
from md2html.converter import SiteBuilder
from md2html.theme import ThemeManager


def test_site_builder_respects_ignore(tmp_path):
    source_dir = tmp_path / "docs"
    source_dir.mkdir()
    keep_file = source_dir / "keep.md"
    keep_file.write_text("# Keep\n", encoding="utf-8")
    ignored_dir = source_dir / "mianshiya"
    ignored_dir.mkdir()
    (ignored_dir / "skip.md").write_text("# Skip\n", encoding="utf-8")

    output_dir = tmp_path / "build"

    config = AppConfig()
    config.source_dir = source_dir
    config.output_dir = output_dir
    config.ignore = ["/docs/mianshiya/"]

    theme = ThemeManager().load("github")
    builder = SiteBuilder(config, theme)
    results = builder.build_all()

    assert {result.source for result in results} == {keep_file}
    assert (output_dir / "keep.html").exists()
    assert not any("mianshiya" in str(path) for path in output_dir.rglob("*"))
