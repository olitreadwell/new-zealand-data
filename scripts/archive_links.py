#!/usr/bin/env python3
"""Archive every link in README.md to the Internet Archive Wayback Machine.

Checks the Wayback CDX API for an existing snapshot of each link, then
submits missing ones to Save Page Now so the content survives even if the
source page disappears. Reuses the README parser from scripts/build_site.py.
Pure Python stdlib, no dependencies.

Auth is optional. With archive.org S3-style keys (archive.org/account/s3)
set as WAYBACK_ACCESS_KEY / WAYBACK_SECRET_KEY, Save Page Now gets a much
higher rate limit. Without keys it still works, just slower.

Usage:
    python3 scripts/archive_links.py                 # check + archive
    python3 scripts/archive_links.py --dry-run       # print the plan only
    python3 scripts/archive_links.py --refresh       # re-save existing snapshots
    python3 scripts/archive_links.py --limit 20      # cap the number of saves
    python3 scripts/archive_links.py --delay 5       # seconds between saves

Outputs:
    wayback-report.json - per-URL result log
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from build_site import README_PATH, flatten, parse_readme

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "wayback-report.json"

CDX_API = "https://web.archive.org/cdx/search/cdx"
SAVE_PAGE_URL = "https://web.archive.org/save/"
USER_AGENT = "new-zealand-data archive job (https://github.com/olitreadwell/new-zealand-data)"


def collect_urls() -> list[tuple[str, str]]:
    """Return (name, url) pairs for every entry, deduplicated by URL."""
    doc = parse_readme(README_PATH.read_text(encoding="utf-8"))
    seen: set[str] = set()
    pairs: list[tuple[str, str]] = []
    for row in flatten(doc):
        url = row["url"].split("#", 1)[0].strip()
        if not url or not urllib.parse.urlparse(url).scheme.startswith("http"):
            continue
        if url not in seen:
            seen.add(url)
            pairs.append((row["name"], url))
    return pairs


def has_snapshot(url: str, timeout: int = 30) -> bool:
    """Check the CDX index for an existing 200 snapshot of a URL."""
    query = urllib.parse.urlencode(
        {
            "url": url,
            "output": "json",
            "limit": "1",
            "filter": "statuscode:200",
        }
    )
    request = urllib.request.Request(f"{CDX_API}?{query}", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            rows = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        # Index unreachable or malformed: re-archive is safer than a silent skip.
        return False
    return len(rows) > 1


def save_page(url: str, access_key: str, secret_key: str, timeout: int = 120) -> tuple[int | None, str | None]:
    """Submit a URL to Save Page Now. Returns (http_status, error)."""
    target = SAVE_PAGE_URL + urllib.parse.quote(url, safe="")
    headers = {"User-Agent": USER_AGENT}
    if access_key and secret_key:
        token = base64.b64encode(f"{access_key}:{secret_key}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    request = urllib.request.Request(target, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, None
    except urllib.error.HTTPError as error:
        return error.code, None
    except urllib.error.URLError as error:
        return None, str(error.reason)
    except TimeoutError:
        return None, "timeout"


def main() -> int:
    """Check and archive README links, writing wayback-report.json."""
    parser = argparse.ArgumentParser(description="Archive README links to the Wayback Machine.")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without archiving")
    parser.add_argument("--refresh", action="store_true", help="re-save links that already have snapshots")
    parser.add_argument("--limit", type=int, default=0, help="maximum number of saves per run (0 = no limit)")
    parser.add_argument("--delay", type=float, default=3.0, help="seconds to wait between saves")
    parser.add_argument("--timeout", type=int, default=120, help="seconds to wait per save request")
    args = parser.parse_args()

    pairs = collect_urls()
    access_key = os.environ.get("WAYBACK_ACCESS_KEY", "")
    secret_key = os.environ.get("WAYBACK_SECRET_KEY", "")
    print(f"found {len(pairs)} unique links in {README_PATH.name}")

    if args.dry_run:
        for name, url in pairs:
            print(f"  would archive: {name} <{url}>")
        return 0

    report: list[dict] = []
    saved = 0
    for name, url in pairs:
        snapshot_exists = has_snapshot(url)
        if snapshot_exists and not args.refresh:
            report.append(
                {
                    "name": name,
                    "url": url,
                    "snapshot_exists": True,
                    "saved": False,
                    "status": None,
                    "error": None,
                }
            )
            continue
        if args.limit and saved >= args.limit:
            report.append(
                {
                    "name": name,
                    "url": url,
                    "snapshot_exists": snapshot_exists,
                    "saved": False,
                    "status": None,
                    "error": "skipped: run limit reached",
                }
            )
            continue
        status, error = save_page(url, access_key, secret_key, timeout=args.timeout)
        saved += 1
        record = {
            "name": name,
            "url": url,
            "snapshot_exists": snapshot_exists,
            "saved": status is not None and 200 <= status < 300,
            "status": status,
            "error": error,
        }
        report.append(record)
        if record["saved"]:
            print(f"  archived: {name}")
        else:
            print(f"  failed:  {name} (status={status}, error={error})")
        time.sleep(args.delay)

    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    failures = [record for record in report if not record["saved"] and not record["snapshot_exists"]]
    print(
        f"{saved} saved, {sum(1 for r in report if r['snapshot_exists'])} already archived, "
        f"{len(failures)} failed; report written to {REPORT_PATH.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
