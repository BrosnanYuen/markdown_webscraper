from __future__ import annotations

import argparse

from . import WebsiteScraper, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape websites to HTML and Markdown.")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config.json (default: config.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    stats = WebsiteScraper(config).run()
    print(
        f"Done. pages_fetched={stats.pages_fetched}, "
        f"html_files_saved={stats.html_files_saved}, "
        f"markdown_files_saved={stats.markdown_files_saved}"
    )
