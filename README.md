# markdown_webscraper

Scrape websites with `botasaurus`, save raw `.html`, then convert `.html` and `.pdf` to `.md` with `markitdown`.

## API Reference

### Core Classes

#### `markdown_webscraper.WebsiteScraper`
The main class for running the scraping process.

**Constructor:**
`WebsiteScraper(config: ScraperConfig, fetcher: PageFetcher | None = None, sleeper: Callable[[float], None] = time.sleep)`

* `config`: A `ScraperConfig` object containing scraping parameters.
* `fetcher`: An optional implementation of `PageFetcher`. Defaults to `BotasaurusFetcher`.
* `sleeper`: A function to handle time delays. Defaults to `time.sleep`.

**Methods:**
* `run() -> CrawlStats`: Starts the scraping process based on the provided configuration. Returns `CrawlStats` containing the results.

#### `markdown_webscraper.ScraperConfig`
A dataclass representing the scraper configuration.

**Attributes:**
* `raw_html_dir (Path)`: Directory to save raw HTML files.
* `markdown_dir (Path)`: Directory to save converted Markdown files.
* `wildcard_websites (list[str])`: List of root URLs for recursive scraping.
* `individual_websites (list[str])`: List of specific URLs to scrape.
* `remove_header_footer (bool)`: Whether to prune `<header>` and `<footer>` tags.
* `markdown_convert (bool)`: Whether to convert HTML to Markdown.
* `time_delay (float)`: Delay between requests in seconds.
* `total_timeout (float)`: Maximum time in seconds for the entire scraping process.

#### `markdown_webscraper.CrawlStats`
A dataclass containing statistics from a completed crawl.

**Attributes:**
* `pages_fetched (int)`: Total number of pages requested.
* `html_files_saved (int)`: Total number of HTML files written to disk.
* `markdown_files_saved (int)`: Total number of Markdown files written to disk.

### Utilities

#### `markdown_webscraper.load_config(config_path: str | Path) -> ScraperConfig`
Loads a `ScraperConfig` from a JSON file.

---

## Usage Example

```python
from pathlib import Path
from markdown_webscraper import WebsiteScraper, load_config

# Load configuration from a JSON file
config = load_config("config.json")

# Initialize and run the scraper
scraper = WebsiteScraper(config=config)
stats = scraper.run()

print(f"Scraped {stats.pages_fetched} pages.")
print(f"Saved {stats.markdown_files_saved} markdown files.")
```

---

## Local Development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run with local script:

```bash
python scrape.py --config config.json
```

Run as installed package CLI:

```bash
markdown-webscraper --config config.json
```

## Configuration

The CLI expects a JSON config file:

```json
{
  "raw_html_dir": "/home/brosnan/markdown_webscraper/raw_html/",
  "markdown_dir": "/home/brosnan/markdown_webscraper/markdown/",
  "wildcard_websites": ["https://www.allaboutcircuits.com/textbook", ""],
  "individual_websites": ["https://example.com/", "https://www.ti.com/lit/ds/sprs590g/sprs590g.pdf"],
  "remove_header_footer": true,
  "markdown_convert": true,
  "time_delay": 2,
  "total_timeout": 180
}
```

## Tests

```bash
pytest tests/unit -q
```

Integration example.com:

```bash
RUN_INTEGRATION=1 pytest tests/integration/test_live_scrape.py::test_integration_example_com -m integration -q
```

Integration allaboutcircuits textbook:

```bash
RUN_INTEGRATION=1 RUN_FULL_TEXTBOOK_INTEGRATION=1 pytest tests/integration/test_live_scrape.py::test_integration_allaboutcircuits_textbook_recursive -m integration -q
```

## Build and Publish to PyPI

1. Update version in `pyproject.toml`.
2. Build distributions:

```bash
python -m pip install --upgrade build twine
python -m build
```

3. Check artifacts:

```bash
python -m twine check dist/*
```

4. Upload:

```bash
python -m twine upload dist/*
```
