from __future__ import annotations

import os

import pytest

from markdown_webscraper.config import ScraperConfig
from markdown_webscraper.pipeline import WebsiteScraper


def _integration_enabled() -> bool:
    return os.getenv("RUN_INTEGRATION") == "1"


def _full_textbook_enabled() -> bool:
    return os.getenv("RUN_FULL_TEXTBOOK_INTEGRATION") == "1"


@pytest.mark.integration
@pytest.mark.skipif(not _integration_enabled(), reason="Set RUN_INTEGRATION=1 to run live integration tests.")
def test_integration_example_com(tmp_path) -> None:
    config = ScraperConfig(
        raw_html_dir=tmp_path / "raw_html",
        markdown_dir=tmp_path / "markdown",
        wildcard_websites=[],
        individual_websites=["https://example.com/"],
        remove_header_footer=True,
        markdown_convert=True,
        time_delay=1,
        total_timeout=180,
    )

    stats = WebsiteScraper(config).run()
    assert stats.pages_fetched >= 1
    assert stats.html_files_saved >= 1
    assert stats.markdown_files_saved >= 1

    html_files = list((tmp_path / "raw_html").rglob("*.html"))
    markdown_files = list((tmp_path / "markdown").rglob("*.md"))
    assert html_files
    assert markdown_files


@pytest.mark.integration
@pytest.mark.skipif(
    not (_integration_enabled() and _full_textbook_enabled()),
    reason="Set RUN_INTEGRATION=1 and RUN_FULL_TEXTBOOK_INTEGRATION=1 for full textbook crawl integration.",
)
def test_integration_allaboutcircuits_textbook_recursive(tmp_path) -> None:
    config = ScraperConfig(
        raw_html_dir=tmp_path / "raw_html",
        markdown_dir=tmp_path / "markdown",
        wildcard_websites=["https://www.allaboutcircuits.com/textbook"],
        individual_websites=[],
        remove_header_footer=True,
        markdown_convert=True,
        time_delay=1,
        total_timeout=180,
    )

    stats = WebsiteScraper(config).run()
    assert stats.pages_fetched > 1
    assert stats.html_files_saved == stats.pages_fetched
    assert stats.markdown_files_saved == stats.pages_fetched

    html_files = list((tmp_path / "raw_html").rglob("*.html"))
    markdown_files = list((tmp_path / "markdown").rglob("*.md"))
    assert len(html_files) == stats.pages_fetched
    assert len(markdown_files) == stats.pages_fetched
