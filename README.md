# markdown_webscraper

Scrape websites with `botasaurus`, save raw `.html`, then convert to `.md` with `markdownify`.

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
  "individual_websites": ["https://example.com/", ""],
  "remove_header_footer": true,
  "markdown_convert": true,
  "time_delay": 2
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
