#!/usr/bin/env python3
"""
批量下载 ICLR 2026 录用论文的 PDF（支持断点续传 + 失败重试）。
"""

import argparse
import json
import os
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm

PDF_DIR = Path("data/pdfs")
BASE_URL = "https://openreview.net"


def make_session():
    """创建带重试机制的 session。"""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def download_pdf(forum_id: str, title: str, pdf_dir: Path, session: requests.Session, delay: float = 0.7) -> bool:
    """下载单篇 PDF，失败返回 False。"""
    url = f"{BASE_URL}/pdf?id={forum_id}"
    pdf_path = pdf_dir / f"{forum_id}.pdf"
    if pdf_path.exists():
        return True  # 已存在，跳过

    try:
        resp = session.get(url, timeout=60)
        resp.raise_for_status()
        # 校验确实是 PDF
        if not resp.content.startswith(b"%PDF"):
            print(f"  [{forum_id}] Not a PDF (content-type issue?), skipping")
            return False
        with open(pdf_path, "wb") as f:
            f.write(resp.content)
        time.sleep(delay)
        return True
    except Exception as e:
        print(f"  [{forum_id}] Failed: {e}")
        time.sleep(delay)
        return False


def main():
    parser = argparse.ArgumentParser(description="Download ICLR 2026 PDFs")
    parser.add_argument("--limit", type=int, default=0, help="最多下载数量（0=全部）")
    parser.add_argument("--input", type=str, default="data/iclr2026_accepted.json")
    parser.add_argument("--delay", type=float, default=2.0, help="每次请求间隔秒数")
    parser.add_argument("--retries", type=int, default=3, help="重试轮数")
    args = parser.parse_args()

    json_path = Path(args.input)
    if not json_path.exists():
        print(f"Input not found: {json_path}")
        print("请先运行: python scraper.py")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        papers = json.load(f)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = set(os.listdir(PDF_DIR))

    targets = papers[:args.limit] if args.limit > 0 else papers
    missing = [p for p in targets if f"{p['forum_id']}.pdf" not in downloaded]
    print(f"Total papers: {len(targets)} | Already downloaded: {len(targets) - len(missing)} | Missing: {len(missing)}")

    if not missing:
        print("All PDFs already downloaded!")
        return

    session = make_session()

    # 多轮重试
    remaining = missing
    for round_idx in range(1, args.retries + 1):
        if not remaining:
            break
        print(f"\n--- Round {round_idx}/{args.retries}: downloading {len(remaining)} papers ---")
        failed = []
        ok = 0
        for p in tqdm(remaining, desc=f"Round {round_idx}"):
            if download_pdf(p["forum_id"], p["title"], PDF_DIR, session, delay=args.delay):
                ok += 1
            else:
                failed.append(p)
        print(f"Round {round_idx} done. Success: {ok} | Failed: {len(failed)}")
        remaining = failed
        if remaining and round_idx < args.retries:
            wait = 10 * round_idx
            print(f"Waiting {wait}s before next retry round...")
            time.sleep(wait)

    if remaining:
        fail_path = Path("data/failed_downloads.json")
        with open(fail_path, "w", encoding="utf-8") as f:
            json.dump(remaining, f, ensure_ascii=False, indent=2)
        print(f"\n最终仍有 {len(remaining)} 篇失败，已记录到 {fail_path}")
    else:
        print("\n全部下载完成！")


if __name__ == "__main__":
    main()
