from pathlib import Path

from markdown_webscraper.config import load_config


def test_load_config_strips_empty_urls(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """
{
  "raw_html_dir": "/tmp/raw",
  "markdown_dir": "/tmp/md",
  "wildcard_websites": ["https://example.com/test", "", "   "],
  "individual_websites": ["https://example.com/", ""],
  "remove_header_footer": true,
  "markdown_convert": false,
  "time_delay": 1
}
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.raw_html_dir == Path("/tmp/raw")
    assert config.markdown_dir == Path("/tmp/md")
    assert config.wildcard_websites == ["https://example.com/test"]
    assert config.individual_websites == ["https://example.com/"]
    assert config.remove_header_footer is True
    assert config.markdown_convert is False
    assert config.time_delay == 1.0
