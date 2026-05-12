import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests

from group_fuels import group_raw_file

BASE_DIR = Path(__file__).resolve().parent
GROUPED_DIR = BASE_DIR / "grupped_outputs"
FAILED_DIR = BASE_DIR / "failed_batches"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def build_raw_filename() -> str:
    configured_name = os.getenv("RAW_FILENAME")
    if configured_name:
        return configured_name

    stamp = datetime.now(timezone.utc).strftime("%m_%d")
    return f"raw_output{stamp}-full.json"


def run_scraper(raw_filename: str, spider_name: str) -> Path:
    raw_path = BASE_DIR / raw_filename
    cmd = [sys.executable, "-m", "scrapy", "crawl", spider_name, "-o", raw_filename]

    print(f"Running scraper: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=BASE_DIR, check=True)

    if not raw_path.exists():
        raise FileNotFoundError(f"Expected scraper output was not created: {raw_path}")

    return raw_path


def group_output(raw_path: Path) -> Path:
    GROUPED_DIR.mkdir(parents=True, exist_ok=True)
    grouped_name = raw_path.name.replace("raw_output", "grouped_output", 1)
    grouped_path = GROUPED_DIR / grouped_name

    grouped_count = group_raw_file(raw_path, grouped_path)
    print(f"Grouped {grouped_count} stations into {grouped_path.name}")

    return grouped_path


def chunked(items: List[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def write_failed_batch(batch: List[Dict[str, Any]], batch_index: int, reason: str) -> None:
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    failed_name = f"failed_batch_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{batch_index:04d}.json"
    payload = {
        "reason": reason,
        "batch_index": batch_index,
        "count": len(batch),
        "items": batch,
    }

    with (FAILED_DIR / failed_name).open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def post_grouped_data(grouped_path: Path) -> None:
    api_base = os.getenv("BACKEND_API_BASE_URL", "").strip()
    if not api_base:
        raise ValueError("BACKEND_API_BASE_URL is required.")

    endpoint = os.getenv("FUEL_BATCH_ENDPOINT", "/api/fuel/batch").strip()
    batch_size = int(os.getenv("UPLOAD_BATCH_SIZE", "300"))
    timeout = int(os.getenv("UPLOAD_TIMEOUT_SECONDS", "30"))
    max_retries = int(os.getenv("UPLOAD_MAX_RETRIES", "3"))
    retry_backoff = float(os.getenv("UPLOAD_RETRY_BACKOFF_SECONDS", "2"))

    url = f"{api_base.rstrip('/')}/{endpoint.lstrip('/')}"

    token = os.getenv("BACKEND_API_TOKEN", "").strip()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with grouped_path.open("r", encoding="utf-8") as f:
        stations = json.load(f)

    if not stations:
        print("Grouped file is empty, skipping upload.")
        return

    total_batches = (len(stations) + batch_size - 1) // batch_size
    failed_batches = 0

    print(f"Uploading {len(stations)} stations to {url} in {total_batches} batches...")

    for idx, batch in enumerate(chunked(stations, batch_size), start=1):
        success = False
        last_error = "unknown"

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(url, json=batch, headers=headers, timeout=timeout)
                if 200 <= response.status_code < 300:
                    print(f"Batch {idx}/{total_batches} uploaded (size={len(batch)}).")
                    success = True
                    break

                body_preview = response.text[:500]
                last_error = f"HTTP {response.status_code}: {body_preview}"
                print(f"Batch {idx} attempt {attempt} failed: {last_error}")
            except requests.RequestException as exc:
                last_error = str(exc)
                print(f"Batch {idx} attempt {attempt} exception: {last_error}")

            if attempt < max_retries:
                time.sleep(retry_backoff * attempt)

        if not success:
            failed_batches += 1
            write_failed_batch(batch, idx, last_error)

    if failed_batches:
        raise RuntimeError(f"Upload completed with {failed_batches} failed batch(es).")


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    spider_name = os.getenv("SCRAPY_SPIDER", "peco")

    try:
        raw_filename = build_raw_filename()
        raw_path = run_scraper(raw_filename, spider_name)
        grouped_path = group_output(raw_path)
        post_grouped_data(grouped_path)
    except Exception as exc:
        print(f"Pipeline failed: {exc}")
        return 1

    print("Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
