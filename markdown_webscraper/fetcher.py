from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from botasaurus.browser import Driver, browser


@dataclass(frozen=True)
class FetchedPage:
    requested_url: str
    resolved_url: str
    html: str
    links: list[str]


class PageFetcher(Protocol):
    def fetch(self, url: str) -> FetchedPage:
        ...

    def close(self) -> None:
        ...


@browser(
    headless=True,
    reuse_driver=True,
    close_on_crash=True,
    raise_exception=True,
    output=None,
)
def _fetch_with_botasaurus(driver: Driver, payload: dict[str, str]) -> dict:
    url = payload["url"]
    driver.get(url)

    # Explicitly use human-like movement + click as required.
    driver.enable_human_mode()
    moved = driver.move_mouse_to_element("body")
    if moved:
        driver.click("body", skip_move=False)

    html = driver.page_html
    links = driver.get_all_links()
    return {
        "requested_url": url,
        "resolved_url": driver.current_url,
        "html": html,
        "links": links,
    }


class BotasaurusFetcher:
    def fetch(self, url: str) -> FetchedPage:
        data = _fetch_with_botasaurus({"url": url})
        return FetchedPage(
            requested_url=data["requested_url"],
            resolved_url=data["resolved_url"],
            html=data["html"],
            links=list(data.get("links", [])),
        )

    def close(self) -> None:
        if hasattr(_fetch_with_botasaurus, "close"):
            _fetch_with_botasaurus.close()
