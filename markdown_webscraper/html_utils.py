from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from markdownify import markdownify as md


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported URL scheme: {url}")
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, ""))


def normalize_link(base_url: str, href: str) -> str | None:
    if not href:
        return None
    absolute = urljoin(base_url, href)
    parsed = urlsplit(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return normalize_url(absolute)


def is_within_scope(candidate_url: str, root_url: str) -> bool:
    candidate = urlsplit(normalize_url(candidate_url))
    root = urlsplit(normalize_url(root_url))
    if candidate.netloc != root.netloc:
        return False

    root_path = root.path or "/"
    if root_path == "/":
        return True
    if root_path.endswith("/"):
        return candidate.path.startswith(root_path)
    return candidate.path == root_path or candidate.path.startswith(f"{root_path}/")


def prune_header_footer(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["header", "footer"]):
        tag.decompose()
    return str(soup)


def to_markdown(html: str) -> str:
    return md(html, heading_style="ATX")


def _safe_segment(segment: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", segment)
    return cleaned.strip("._") or "index"


def url_to_output_path(url: str, output_dir: Path, extension: str) -> Path:
    parsed = urlsplit(normalize_url(url))
    path_segments = [seg for seg in parsed.path.split("/") if seg]
    if not path_segments or parsed.path.endswith("/"):
        path_segments.append("index")

    file_stem = _safe_segment(path_segments[-1])
    if parsed.query:
        file_stem = f"{file_stem}__q_{_safe_segment(parsed.query)}"

    directory_segments = [_safe_segment(seg) for seg in path_segments[:-1]]
    return output_dir / _safe_segment(parsed.netloc) / Path(*directory_segments) / f"{file_stem}.{extension}"
