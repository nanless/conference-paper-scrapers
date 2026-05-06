# Conference Paper Scrapers

A collection of scrapers and downloaders for fetching accepted papers from major ML/AI conferences.

| Conference | Status | Auth Required | API / Source |
|------------|--------|---------------|--------------|
| [ICASSP](./icassp) | IEEE Signal Processing | No | IEEE Xplore |
| [ICLR](./iclr) | ML (OpenReview) | No | OpenReview API v2 |
| [ICML](./icml) | ML (OpenReview) | **Yes** | OpenReview API v2 |

## Quick Start

Each conference has its own subdirectory with independent setup and usage instructions:

```bash
# ICASSP — IEEE Xplore scraping + concurrent PDF downloads
cd icassp
pip install requests beautifulsoup4 selenium tqdm
python downloader.py

# ICLR — Public OpenReview metadata + PDF downloads
cd iclr
pip install requests tqdm
python scraper.py
python download_pdfs.py

# ICML — Authenticated OpenReview + audio paper filtering
cd icml
pip install -r requirements.txt
export OPENREVIEW_USERNAME="your@email.com"
export OPENREVIEW_PASSWORD="your_password"
python scraper.py
python filter_audio.py
python download_pdfs.py
```

See the individual `README.md` files in each subdirectory for detailed documentation.

## Shared Features

All scrapers support:

- **Bulk metadata export** to JSON and CSV
- **Concurrent or batched PDF downloading**
- **Resume / skip already-downloaded files**
- **Retry with backoff** for failed requests
- **Progress bars** via `tqdm`

## Repository Structure

```
.
├── icassp/
│   ├── downloader.py      # Selenium scraping + multi-threaded PDF downloads
│   └── README.md
├── iclr/
│   ├── scraper.py         # OpenReview API metadata fetcher
│   ├── download_pdfs.py   # PDF downloader with retry
│   └── README.md
├── icml/
│   ├── scraper.py         # Authenticated OpenReview API fetcher
│   ├── filter_audio.py    # Keyword-based audio paper filter
│   ├── download_pdfs.py   # PDF downloader
│   ├── requirements.txt
│   └── README.md
└── README.md              # This file
```

## Notes

- **ICASSP** papers require free availability on IEEE Xplore; institutional access may be needed for some papers.
- **ICLR** submissions are fully public on OpenReview — no account needed.
- **ICML** submissions are restricted on OpenReview and require a valid account with access permissions.
- All scrapers include rate-limiting to avoid overloading conference servers.
