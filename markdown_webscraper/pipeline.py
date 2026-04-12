from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .config import ScraperConfig
from .fetcher import BotasaurusFetcher, FetchedPage, PageFetcher
from .html_utils import (
    is_within_scope,
    normalize_link,
    normalize_url,
    prune_header_footer,
    to_markdown,
    url_to_output_path,
)


@dataclass
class CrawlStats:
    pages_fetched: int = 0
    html_files_saved: int = 0
    markdown_files_saved: int = 0


class WebsiteScraper:
    def __init__(
        self,
        config: ScraperConfig,
        fetcher: PageFetcher | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.fetcher = fetcher or BotasaurusFetcher()
        self.sleeper = sleeper
        self.stats = CrawlStats()
        self._visited: set[str] = set()

    def run(self) -> CrawlStats:
        self.config.raw_html_dir.mkdir(parents=True, exist_ok=True)
        self.config.markdown_dir.mkdir(parents=True, exist_ok=True)

        try:
            for url in self.config.individual_websites:
                self._scrape_one(url)

            for root_url in self.config.wildcard_websites:
                self._scrape_recursive(root_url)
        finally:
            self.fetcher.close()

        return self.stats

    def _scrape_recursive(self, root_url: str) -> None:
        queue: deque[str] = deque([normalize_url(root_url)])
        while queue:
            current = queue.popleft()
            if current in self._visited:
                continue
            if not is_within_scope(current, root_url):
                continue

            fetched = self._scrape_one(current)
            for href in fetched.links:
                child = normalize_link(fetched.resolved_url, href)
                if child and child not in self._visited and is_within_scope(child, root_url):
                    queue.append(child)

    def _scrape_one(self, url: str) -> FetchedPage:
        normalized = normalize_url(url)
        if normalized in self._visited:
            return FetchedPage(normalized, normalized, "", [])

        fetched = self.fetcher.fetch(normalized)
        self._visited.add(normalize_url(fetched.resolved_url))
        self.stats.pages_fetched += 1

        html = fetched.html
        if self.config.remove_header_footer:
            html = prune_header_footer(html)

        html_path = url_to_output_path(fetched.resolved_url, self.config.raw_html_dir, "html")
        self._write_text_file(html_path, html)
        self.stats.html_files_saved += 1

        if self.config.markdown_convert:
            markdown_path = url_to_output_path(fetched.resolved_url, self.config.markdown_dir, "md")
            self._write_text_file(markdown_path, to_markdown(html))
            self.stats.markdown_files_saved += 1

        if self.config.time_delay > 0:
            self.sleeper(self.config.time_delay)

        return fetched

    @staticmethod
    def _write_text_file(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
