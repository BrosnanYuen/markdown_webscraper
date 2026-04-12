from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from markdown_webscraper.config import ScraperConfig
from markdown_webscraper.fetcher import FetchedPage
from markdown_webscraper.pipeline import WebsiteScraper


@dataclass
class FakeFetcher:
    pages: dict[str, FetchedPage]
    closed: bool = False

    def fetch(self, url: str) -> FetchedPage:
        return self.pages[url]

    def close(self) -> None:
        self.closed = True


def build_config(tmp_path: Path) -> ScraperConfig:
    return ScraperConfig(
        raw_html_dir=tmp_path / "raw",
        markdown_dir=tmp_path / "markdown",
        wildcard_websites=["https://example.com/test/"],
        individual_websites=["https://example.com/single/"],
        remove_header_footer=True,
        markdown_convert=True,
        time_delay=0.0,
    )


def test_recursive_and_individual_scrape(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    pages = {
        "https://example.com/single/": FetchedPage(
            requested_url="https://example.com/single/",
            resolved_url="https://example.com/single/",
            html="<html><body><header>X</header><main>single</main></body></html>",
            links=[],
        ),
        "https://example.com/test/": FetchedPage(
            requested_url="https://example.com/test/",
            resolved_url="https://example.com/test/",
            html="<html><body><main>root</main></body></html>",
            links=[
                "https://example.com/test/laser",
                "https://example.com/other/path",
                "/test/robot/ship",
            ],
        ),
        "https://example.com/test/laser": FetchedPage(
            requested_url="https://example.com/test/laser",
            resolved_url="https://example.com/test/laser",
            html="<html><body><main>laser</main></body></html>",
            links=[],
        ),
        "https://example.com/test/robot/ship": FetchedPage(
            requested_url="https://example.com/test/robot/ship",
            resolved_url="https://example.com/test/robot/ship",
            html="<html><body><main>ship</main></body></html>",
            links=[],
        ),
    }
    fetcher = FakeFetcher(pages=pages)

    scraper = WebsiteScraper(config=config, fetcher=fetcher)
    stats = scraper.run()

    assert stats.pages_fetched == 4
    assert stats.html_files_saved == 4
    assert stats.markdown_files_saved == 4
    assert fetcher.closed is True

    root_html = tmp_path / "raw" / "example.com" / "single" / "index.html"
    assert root_html.exists()
    assert "<header>" not in root_html.read_text(encoding="utf-8")

    md_file = tmp_path / "markdown" / "example.com" / "test" / "laser.md"
    assert md_file.exists()
    assert "laser" in md_file.read_text(encoding="utf-8")
