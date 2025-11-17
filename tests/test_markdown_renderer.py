from pathlib import Path

import pytest  # type: ignore[import]

from md2html.converter import MarkdownRenderer
from md2html.theme import ThemeManager
from md2html.utils import parse_front_matter, slugify


@pytest.fixture()
def renderer() -> MarkdownRenderer:
    theme = ThemeManager().load("github")
    return MarkdownRenderer(theme)


def test_hide_container_renders_details(renderer: MarkdownRenderer) -> None:
    markdown = """::: hide 更多

隐藏内容
:::
"""
    result = renderer.render(markdown, source_path=Path("doc.md"))
    assert "<details" in result.html
    assert "更多" in result.html
    assert "隐藏内容" in result.html
    assert "data-md2html-hide-collapse" in result.html
    assert "收起" in result.html


def test_hide_container_shorthand_without_keyword(renderer: MarkdownRenderer) -> None:
    markdown = """::: 自定义标题

内容
:::
"""
    result = renderer.render(markdown, source_path=Path("doc.md"))
    assert '<details class="md2html-hide"' in result.html
    assert "自定义标题" in result.html
    assert "内容" in result.html
    assert "data-md2html-hide-collapse" in result.html


def test_note_container_renders_admonition(renderer: MarkdownRenderer) -> None:
    markdown = """::: note 提示
内容
:::
"""
    result = renderer.render(markdown, source_path=Path("doc.md"))
    assert "md2html-admonition--note" in result.html
    assert "提示" in result.html


def test_front_matter_parser() -> None:
    markdown = "---\ntitle: 示例\n---\n\n正文"  # noqa: S105
    front_matter, body = parse_front_matter(markdown)
    assert front_matter["title"] == "示例"
    assert body.strip() == "正文"


def test_slugify_generates_unique_slug() -> None:
    assert slugify("Hello World") == "hello-world"
    assert slugify("中文 标题") == "中文-标题"


def test_table_markdown_renders_table(renderer: MarkdownRenderer) -> None:
    markdown = """| 列1 | 列2 |
| --- | --- |
| A   | B   |
"""
    result = renderer.render(markdown, source_path=Path("table.md"))
    assert "<table" in result.html
    assert "<td" in result.html
