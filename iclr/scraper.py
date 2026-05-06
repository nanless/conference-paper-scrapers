#!/usr/bin/env python3
"""
ICLR 2026 Paper Scraper
从 OpenReview API (api2) 拉取全部录用论文元数据。
"""

import csv
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

BASE_URL = "https://api2.openreview.net"
OUTPUT_DIR = Path("data")
ICLR_INVITATION = "ICLR.cc/2026/Conference/-/Submission"


def fetch_notes(invitation: str, offset: int = 0, limit: int = 1000) -> dict:
    params = {
        "invitation": invitation,
        "details": "replyCount,original",
        "offset": offset,
        "limit": limit,
    }
    url = f"{BASE_URL}/notes?{urlencode(params)}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all_notes(invitation: str) -> list:
    """分页拉取所有 notes，返回 list[dict]。"""
    all_notes = []
    offset = 0
    limit = 1000
    while True:
        data = fetch_notes(invitation, offset, limit)
        notes = data.get("notes", [])
        if not notes:
            break
        all_notes.extend(notes)
        print(f"  fetched {len(all_notes)} notes...")
        offset += len(notes)
        if len(notes) < limit:
            break
        time.sleep(0.3)
    return all_notes


def _get_val(content: dict, field: str):
    """处理 OpenReview API v2 content 字段为 {value: ...} 结构。"""
    v = content.get(field, "")
    if isinstance(v, dict):
        return v.get("value", "")
    return v


def is_accepted(note: dict) -> bool:
    """判断论文是否被 ICLR 2026 录用（Poster 或 Oral）。"""
    venue = _get_val(note.get("content", {}), "venue")
    venue_str = str(venue)
    # 录用 venue 如 "ICLR 2026 Poster" / "ICLR 2026 Oral"
    # 拒绝/撤回 venue 如 "Submitted to ICLR 2026" / "ICLR 2026 Conference Rejected Submission"
    return venue_str.startswith("ICLR 2026") and not any(
        bad in venue_str for bad in ["Submitted", "Rejected", "Withdrawn", "Desk"]
    )


def extract_paper_info(note: dict) -> dict:
    """从 note 中提取结构化元数据。"""
    content = note.get("content", {})
    forum_id = note.get("id", "")
    return {
        "forum_id": forum_id,
        "title": _get_val(content, "title"),
        "authors": _get_val(content, "authors"),
        "abstract": _get_val(content, "abstract"),
        "keywords": _get_val(content, "keywords"),
        "venue": _get_val(content, "venue"),
        "primary_area": _get_val(content, "primary_area"),
        "tldr": _get_val(content, "TLDR"),
        "code": _get_val(content, "code"),
        "pdf_url": f"https://openreview.net/pdf?id={forum_id}",
        "forum_url": f"https://openreview.net/forum?id={forum_id}",
    }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Fetching all ICLR 2026 submissions from OpenReview (api2)...")
    all_notes = fetch_all_notes(ICLR_INVITATION)
    print(f"Total submissions fetched: {len(all_notes)}")

    accepted = [n for n in all_notes if is_accepted(n)]
    print(f"Accepted papers: {len(accepted)}")

    papers = [extract_paper_info(n) for n in accepted]

    # JSON
    json_path = OUTPUT_DIR / "iclr2026_accepted.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {json_path}")

    # CSV
    csv_path = OUTPUT_DIR / "iclr2026_accepted.csv"
    if papers:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=papers[0].keys())
            writer.writeheader()
            writer.writerows(papers)
        print(f"Saved CSV:  {csv_path}")

    print("Done.")


if __name__ == "__main__":
    main()
