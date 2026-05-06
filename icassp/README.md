# ICASSP Paper Scraper & Downloader

Crawl and download ICASSP 2026 papers from IEEE Xplore when freely available.

## Overview

This script automates two tasks:

1. **Paper list scraping** — Uses Selenium to browse IEEE Xplore conference proceedings pages and extract all paper arnumbers and titles.
2. **PDF downloading** — Uses `requests` with concurrent workers to download PDFs in bulk.

## Features

- **Headless browser scraping** with Selenium + Chrome
- **Concurrent downloads** with 8 workers via `ThreadPoolExecutor`
- **Resume support** — Already-downloaded PDFs are skipped
- **Retry with exponential backoff** — Up to 3 retries per paper
- **Progress tracking** via `tqdm`

## Requirements

```bash
pip install requests beautifulsoup4 selenium tqdm
```

Also requires [ChromeDriver](https://chromedriver.chromium.org/) (or use Chrome's built-in driver if Chrome >= 115).

## Usage

```bash
python downloader.py
```

The script runs in two phases automatically:

### Phase 1: Scrape paper list

If `papers_2026.json` does not exist, the script launches a headless Chrome browser and scrapes all ICASSP 2026 papers from IEEE Xplore. Results are saved to `papers_2026.json`.

### Phase 2: Download PDFs

Using the paper list from `papers_2026.json`, the script downloads all PDFs to the `papers_2026/` directory.

## Output

| File / Directory | Description |
|------------------|-------------|
| `papers_2026.json` | Paper metadata (arnumber, title) |
| `papers_2026/` | Downloaded PDF files |

## Notes

- IEEE Xplore pages are scraped with a 12-second delay per page to allow dynamic content to load.
- PDF download URL: `https://ieeexplore-custom.ieee.org/stampPDF/getPDF.jsp`
- Only freely available papers can be downloaded without institutional access.
