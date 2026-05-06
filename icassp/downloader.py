import os
import json
import time
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


def scrape_paper_list(driver, max_pages=100):
    """Scrape all paper arnumbers and titles from conference pages."""
    papers = []
    seen_arnumbers = set()

    for page_num in tqdm(range(1, max_pages + 1), desc="Scraping pages"):
        url = (
            f"https://ieeexplore-custom.ieee.org/xpl/conhome/11460365/proceeding"
            f"?rowsPerPage=100&pageNumber={page_num}"
        )
        driver.get(url)
        time.sleep(12)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        items = soup.find_all(class_="List-results-items")
        page_papers = []
        for item in items:
            link = item.find("a", href=re.compile(r"^/document/(\d+)/?$"))
            if not link:
                continue
            href = link.get("href")
            match = re.search(r"/document/(\d+)/?", href)
            if not match:
                continue
            arnumber = match.group(1)
            title = link.get_text(strip=True)
            if not title or len(title) <= 5:
                continue
            if arnumber not in seen_arnumbers:
                seen_arnumbers.add(arnumber)
                page_papers.append({"arnumber": arnumber, "title": title})

        if not page_papers:
            print(f"Page {page_num}: no papers found, stopping.")
            break

        papers.extend(page_papers)
        print(f"Page {page_num}: collected {len(page_papers)} papers (total: {len(papers)})")

    return papers


def download_pdf(arnumber, title, download_dir, headers, max_retries=3):
    """Download a single paper PDF with retries."""
    pdf_url = (
        f"https://ieeexplore-custom.ieee.org/stampPDF/getPDF.jsp"
        f"?tp=&arnumber={arnumber}&ref="
    )

    safe_title = "".join(
        c for c in title if c.isalnum() or c in " ._-"
    ).strip()
    if not safe_title:
        safe_title = arnumber
    filename = f"{safe_title}.pdf"
    filepath = os.path.join(download_dir, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        return True, "already_exists"

    for attempt in range(max_retries):
        try:
            response = requests.get(
                pdf_url, headers=headers, timeout=60, allow_redirects=True
            )
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "pdf" in content_type.lower():
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return True, "downloaded"
                else:
                    return False, f"wrong_content_type: {content_type}"
            else:
                time.sleep(2 ** attempt)
        except Exception as e:
            if attempt == max_retries - 1:
                return False, f"exception: {e}"
            time.sleep(2 ** attempt)

    return False, "max_retries_exceeded"


def main():
    download_dir = "papers_2026"
    metadata_file = "papers_2026.json"
    os.makedirs(download_dir, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf",
    }

    # Phase 1: Scrape paper list
    if os.path.exists(metadata_file):
        print(f"Loading existing paper list from {metadata_file}...")
        with open(metadata_file, "r", encoding="utf-8") as f:
            papers = json.load(f)
        print(f"Loaded {len(papers)} papers.")
    else:
        print("Starting Chrome to scrape paper list...")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=options)
        try:
            papers = scrape_paper_list(driver, max_pages=100)
        finally:
            driver.quit()

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(papers)} papers to {metadata_file}")

    # Phase 2: Download PDFs with concurrent workers
    success_count = 0
    fail_count = 0
    skip_count = 0
    counter_lock = Lock()

    def download_worker(paper):
        nonlocal success_count, fail_count, skip_count
        success, status = download_pdf(
            paper["arnumber"], paper["title"], download_dir, headers
        )
        with counter_lock:
            if success:
                if status == "already_exists":
                    skip_count += 1
                else:
                    success_count += 1
            else:
                fail_count += 1
        return success, status, paper

    print(f"\nStarting download of {len(papers)} papers with 8 concurrent workers...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(download_worker, paper): paper for paper in papers
        }
        pbar = tqdm(total=len(papers), desc="Downloading PDFs")
        for future in as_completed(futures):
            paper = futures[future]
            try:
                success, status, _ = future.result()
                if not success:
                    print(f"Failed [{paper['arnumber']}]: {status} - {paper['title'][:60]}")
            except Exception as e:
                with counter_lock:
                    fail_count += 1
                print(f"Exception [{paper['arnumber']}]: {e} - {paper['title'][:60]}")
            pbar.update(1)
        pbar.close()

    print(f"\nDone! Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")


if __name__ == "__main__":
    main()
