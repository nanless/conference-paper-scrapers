# ICML 2026 Paper Scraper (Authenticated)

Scrape ICML 2026 accepted papers from OpenReview using authenticated API access, filter for audio/speech/music papers, and download PDFs.

## Overview

Unlike ICLR, ICML submissions on OpenReview are **not publicly visible** and require authentication. This toolset provides:

1. **`scraper.py`** — Authenticates with OpenReview and fetches all ICML 2026 submissions, exporting accepted papers to JSON and CSV.
2. **`filter_audio.py`** — Filters the accepted papers for audio, speech, and music-related research using keyword matching.
3. **`download_pdfs.py`** — Downloads PDFs for any subset of papers (all accepted or filtered audio papers).

## Features

- **Authenticated API access** via `openreview-py`
- **Audio paper filtering** — Keyword-based search across titles, abstracts, keywords, and research areas
- **Resume support** — Already-downloaded PDFs are skipped
- **Multi-round retry** — Failed downloads are retried with backoff

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies:

- `openreview-py>=1.40.0`
- `requests>=2.31.0`
- `tqdm>=4.66.0`
- `python-dotenv>=1.0.0`

## Usage

### Step 1: Set credentials

**Option A — Environment variables (recommended):**

```bash
export OPENREVIEW_USERNAME="your@email.com"
export OPENREVIEW_PASSWORD="your_password"
```

**Option B — Command-line arguments:**

```bash
python scraper.py --username "your@email.com" --password "your_password"
```

### Step 2: Scrape metadata

```bash
python scraper.py
```

Saves:

- `data/icml2026_accepted.json`
- `data/icml2026_accepted.csv`

### Step 3: Filter audio-related papers

```bash
python filter_audio.py
```

Saves:

- `data/icml2026_audio_papers.json`

### Step 4: Download PDFs

Download all accepted papers:

```bash
python download_pdfs.py
```

Or download only audio-related papers:

```bash
python download_pdfs.py --input data/icml2026_audio_papers.json
```

Optional arguments:

```bash
python download_pdfs.py --limit 100     # Download first 100 papers
python download_pdfs.py --delay 1.0     # Request interval in seconds (default: 0.7)
python download_pdfs.py --retries 5     # Retry rounds (default: 3)
```

## Output

| File / Directory | Description |
|------------------|-------------|
| `data/icml2026_accepted.json` | All accepted papers metadata |
| `data/icml2026_accepted.csv` | Same data in CSV format |
| `data/icml2026_audio_papers.json` | Audio/speech/music related papers |
| `data/pdfs/` | Downloaded PDF files |
| `data/failed_downloads.json` | Papers that failed after all retries |

## Audio filter keywords

The filter matches papers containing any of these keywords (case-insensitive):

`speech`, `speaker`, `asr`, `automatic speech recognition`, `text-to-speech`, `tts`, `voice`, `vocal`, `dialogue`, `spoken language`, `prosody`, `phoneme`, `phonetic`, `audio`, `sound`, `acoustic`, `waveform`, `wave`, `music`, `musical`, `song`, `singing`, `melody`, `binaural`, `spatial audio`, `audio generation`, `audio synthesis`, `audio super-resolution`, `neural audio`, `audio codec`, `audio compression`, `signal processing`, `spectrogram`, `stft`, `mfcc`, `wav2vec`, `whisper`, `hubert`, `wavlm`

## Notes

- OpenReview has rate limits; the script includes a 0.3s delay between API requests.
- Scraping all submissions typically takes 1–3 minutes.
- Ensure your OpenReview account has permission to view ICML 2026 submissions.
