from __future__ import annotations

import time
import requests
import signal
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from markitdown import MarkItDown

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

_markdown_converter = MarkItDown(enable_plugins=False)


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

    def _handle_timeout(self, signum, frame):
        print("\nTotal timeout reached. Quitting...")
        exit(0)

    def run(self) -> CrawlStats:
        self.config.raw_html_dir.mkdir(parents=True, exist_ok=True)
        self.config.markdown_dir.mkdir(parents=True, exist_ok=True)

        if self.config.total_timeout > 0:
            signal.signal(signal.SIGALRM, self._handle_timeout)
            signal.alarm(int(self.config.total_timeout))

        try:
            for url in self.config.individual_websites:
                self._scrape_one(url)

            for root_url in self.config.wildcard_websites:
                self._scrape_recursive(root_url)
        finally:
            if self.config.total_timeout > 0:
                signal.alarm(0)
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

        resolved_url_lower = fetched.resolved_url.lower()
        if resolved_url_lower.endswith(".pdf") or resolved_url_lower.endswith(".txt"):
            self._download_file(fetched.resolved_url)
            return fetched

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

    def _download_file(self, url: str) -> None:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        ext = url.split(".")[-1].lower()
        output_dir = self.config.raw_html_dir
        
        # Use a safe way to determine the filename/path
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
        if not path or path == "/":
            path = "/index"
            
        file_path = output_dir / parsed.netloc / Path(path.lstrip("/"))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        if self.config.markdown_convert and ext in ("pdf", "html"):
            with open(file_path, "rb") as f:
                result = _markdown_converter.convert(f)
            markdown_path = url_to_output_path(url, self.config.markdown_dir, "md")
            self._write_text_file(markdown_path, result.text_content)
            self.stats.markdown_files_saved += 1

    @staticmethod
    def _write_text_file(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
