from pathlib import Path

import pytest

from markdown_webscraper.html_utils import (
    is_within_scope,
    normalize_link,
    normalize_url,
    prune_header_footer,
    to_markdown,
    url_to_output_path,
)


def test_normalize_url_rejects_non_http_scheme() -> None:
    with pytest.raises(ValueError):
        normalize_url("ftp://example.com/file")


def test_normalize_link_handles_relative_and_skips_mailto() -> None:
    assert normalize_link("https://example.com/base/", "../page") == "https://example.com/page"
    assert normalize_link("https://example.com/base/", "mailto:test@example.com") is None


def test_scope_matching_for_prefixed_paths() -> None:
    assert is_within_scope("https://example.com/test/a", "https://example.com/test")
    assert is_within_scope("https://example.com/test/a", "https://example.com/test/")
    assert not is_within_scope("https://example.com/testing", "https://example.com/test")
    assert not is_within_scope("https://other.com/test/a", "https://example.com/test")


def test_prune_header_footer_removes_tags() -> None:
    html = "<html><body><header>head</header><main>body</main><footer>foot</footer></body></html>"
    cleaned = prune_header_footer(html)
    assert "<header>" not in cleaned
    assert "<footer>" not in cleaned
    assert "body" in cleaned


def test_to_markdown_basic() -> None:
    markdown = to_markdown("<h1>Hello</h1><p>World</p>")
    assert "# Hello" in markdown
    assert "World" in markdown


def test_url_to_output_path_creates_domain_and_query_suffix(tmp_path: Path) -> None:
    path = url_to_output_path("https://example.com/docs/page?x=1&y=2", tmp_path, "html")
    assert path == tmp_path / "example.com" / "docs" / "page__q_x_1_y_2.html"
