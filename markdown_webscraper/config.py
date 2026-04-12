from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScraperConfig:
    raw_html_dir: Path
    markdown_dir: Path
    wildcard_websites: list[str]
    individual_websites: list[str]
    remove_header_footer: bool
    markdown_convert: bool
    time_delay: float


def _clean_url_list(urls: list[str]) -> list[str]:
    return [url.strip() for url in urls if isinstance(url, str) and url.strip()]


def load_config(config_path: str | Path) -> ScraperConfig:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as infile:
        raw = json.load(infile)

    return ScraperConfig(
        raw_html_dir=Path(raw["raw_html_dir"]),
        markdown_dir=Path(raw["markdown_dir"]),
        wildcard_websites=_clean_url_list(raw.get("wildcard_websites", [])),
        individual_websites=_clean_url_list(raw.get("individual_websites", [])),
        remove_header_footer=bool(raw.get("remove_header_footer", False)),
        markdown_convert=bool(raw.get("markdown_convert", True)),
        time_delay=float(raw.get("time_delay", 0)),
    )
