#!/usr/bin/env python3
"""
ICML 2026 Paper Scraper (Authenticated)
使用 OpenReview API v2 + 账号认证，爬取 ICML 2026 录用论文。
"""

import argparse
import csv
import json
import os
import time
from pathlib import Path

import openreview

BASE_URL = "https://api2.openreview.net"
OUTPUT_DIR = Path("data")
ICML_INVITATION = "ICML.cc/2026/Conference/-/Submission"


def get_client(username: str, password: str):
    """使用账号密码创建已认证的 OpenReview API v2 客户端。"""
    return openreview.api.OpenReviewClient(
        baseurl=BASE_URL,
        username=username,
        password=password,
    )


def fetch_all_notes(client, invitation: str) -> list:
    """分页拉取所有 notes，返回 list[dict]。"""
    all_notes = []
    offset = 0
    limit = 1000
    while True:
        notes = client.get_all_notes(
            invitation=invitation,
            offset=offset,
            limit=limit,
        )
        if not notes:
            break
        all_notes.extend(notes)
        print(f"  fetched {len(all_notes)} notes...")
        offset += len(notes)
        if len(notes) < limit:
            break
        time.sleep(0.3)
    return all_notes


def _get_val(content, field: str):
    """处理 OpenReview API v2 content 字段为 {value: ...} 结构。"""
    v = content.get(field, "")
    if isinstance(v, dict):
        return v.get("value", "")
    return v


def is_accepted(note) -> bool:
    """判断论文是否被 ICML 2026 录用。"""
    venue = _get_val(note.content, "venue")
    venue_str = str(venue)
    # 录用 venue: "ICML 2026 spotlight" / "ICML 2026 regular"
    return venue_str.startswith("ICML 2026") and not any(
        bad in venue_str for bad in ["Submitted", "Rejected", "Withdrawn", "Desk"]
    )


def extract_paper_info(note) -> dict:
    """从 note 中提取结构化元数据。"""
    content = note.content
    forum_id = note.id
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
    parser = argparse.ArgumentParser(description="Scrape ICML 2026 accepted papers")
    parser.add_argument("--username", default=os.getenv("OPENREVIEW_USERNAME"), help="OpenReview 邮箱")
    parser.add_argument("--password", default=os.getenv("OPENREVIEW_PASSWORD"), help="OpenReview 密码")
    args = parser.parse_args()

    if not args.username or not args.password:
        print("Error: 需要提供 OpenReview 账号密码")
        print("方式 1: 环境变量 OPENREVIEW_USERNAME / OPENREVIEW_PASSWORD")
        print("方式 2: 命令行参数 --username / --password")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Logging in as {args.username}...")
    client = get_client(args.username, args.password)
    print("Login successful.")

    print("Fetching all ICML 2026 submissions...")
    all_notes = fetch_all_notes(client, ICML_INVITATION)
    print(f"Total submissions fetched: {len(all_notes)}")

    accepted = [n for n in all_notes if is_accepted(n)]
    print(f"Accepted papers: {len(accepted)}")

    papers = [extract_paper_info(n) for n in accepted]

    # JSON
    json_path = OUTPUT_DIR / "icml2026_accepted.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {json_path}")

    # CSV
    csv_path = OUTPUT_DIR / "icml2026_accepted.csv"
    if papers:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=papers[0].keys())
            writer.writeheader()
            writer.writerows(papers)
        print(f"Saved CSV:  {csv_path}")

    print("Done.")


if __name__ == "__main__":
    main()
