# ICLR 2026 Paper Scraper & Downloader

Fetch accepted paper metadata from OpenReview API (v2) and download PDFs in bulk.

## Overview

This toolset consists of two scripts:

1. **`scraper.py`** — Queries the OpenReview API v2 for all ICLR 2026 submissions, filters for accepted papers, and exports metadata to JSON and CSV.
2. **`download_pdfs.py`** — Reads the metadata JSON and downloads all accepted paper PDFs with resume support and automatic retry.

## Features

- **No authentication required** — ICLR submissions are publicly visible on OpenReview
- **Pagination handling** — Automatically fetches all submissions across multiple API pages
- **Resume support** — Already-downloaded PDFs are skipped
- **Multi-round retry** — Failed downloads are retried up to 3 times with increasing wait intervals
- **Progress bars** via `tqdm`

## Requirements

```bash
pip install requests tqdm
```

## Usage

### Step 1: Scrape metadata

```bash
python scraper.py
```

This fetches all ICLR 2026 submissions, filters for accepted papers (Poster / Oral), and saves:

- `data/iclr2026_accepted.json`
- `data/iclr2026_accepted.csv`

### Step 2: Download PDFs

```bash
python download_pdfs.py
```

Optional arguments:

```bash
python download_pdfs.py --limit 50      # Download only first 50 papers
python download_pdfs.py --delay 1.0     # 1 second between requests (default: 2.0)
python download_pdfs.py --retries 5     # 5 retry rounds (default: 3)
```

## Output

| File / Directory | Description |
|------------------|-------------|
| `data/iclr2026_accepted.json` | Full metadata for all accepted papers |
| `data/iclr2026_accepted.csv` | Same data in CSV format |
| `data/pdfs/` | Downloaded PDF files |
| `data/failed_downloads.json` | Papers that failed after all retries |

## Data fields

Each paper entry includes:

- `forum_id` — OpenReview forum ID
- `title` — Paper title
- `authors` — Author list
- `abstract` — Paper abstract
- `keywords` — Keywords
- `venue` — Acceptance type (Poster / Oral)
- `primary_area` — Research area
- `tldr` — TL;DR summary
- `code` — Code repository link (if provided)
- `pdf_url` — Direct PDF URL
- `forum_url` — OpenReview forum page
