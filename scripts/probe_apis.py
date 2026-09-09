#!/usr/bin/env python3
"""Probe the API-ish endpoints listed in README.md.

Reuses the README parser from scripts/build_site.py, keeps the entries
whose name, description, or URL marks them as an API endpoint, then GETs
each one and records status, content-type, and latency. Pure Python
stdlib, no dependencies.

Hard failures (5xx responses, DNS/connection errors, timeouts) make the
process exit non-zero so CI surfaces them. Bot-blocked responses (403 and
999, common for LinkedIn-style protection) are recorded but are not
failures. The per-URL report is written to api-probe-report.json; nothing
is committed back to the repo.

Usage:
    python3 scripts/probe_apis.py                 # probe all API-ish endpoints
    python3 scripts/probe_apis.py --dry-run       # print the plan only
    python3 scripts/probe_apis.py --limit 10      # cap the number of probes

Outputs:
    api-probe-report.json - per-URL probe result log
"""

from __future__ import annotations

import argparse
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
REPORT_PATH = ROOT / "api-probe-report.json"

PROBE_TIMEOUT = 15
USER_AGENT = "new-zealand-data api probe (https://github.com/olitreadwell/new-zealand-data)"

# URL substrings that mark a link as an API endpoint even when the entry
# text does not say "API" (OGC WMS/WMTS, ArcGIS REST, GeoServer, OData).
API_HINTS = ("api", "arcgis/rest", "geoserver", "odata", "wms", "wmts")
# Entry text that explicitly says the link is not an API.
NON_API_MARKERS = ("non-api", "non api")

# Status codes that mean a bot-block (usually LinkedIn or WAF protection),
# not an outage.
BOT_BLOCK_STATUSES = {403, 999}


def is_api_entry(name: str, description: str, url: str) -> bool:
    """Return True when an entry looks like an API endpoint."""
    text = f"{name} {description}".lower()
    if any(marker in text for marker in NON_API_MARKERS):
        return False
    if "api" in text:
        return True
    return any(hint in url.lower() for hint in API_HINTS)


def collect_api_urls() -> list[tuple[str, str]]:
    """Return (name, url) pairs for every API-ish entry, deduplicated by URL."""
    doc = parse_readme(README_PATH.read_text(encoding="utf-8"))
    seen: set[str] = set()
    pairs: list[tuple[str, str]] = []
    for row in flatten(doc):
        url = row["url"].split("#", 1)[0].strip()
        if not url or not urllib.parse.urlparse(url).scheme.startswith("http"):
            continue
        if url in seen:
            continue
        if is_api_entry(row["name"], row["description"], url):
            seen.add(url)
            pairs.append((row["name"], url))
    return pairs


def probe_url(name: str, url: str) -> dict:
    """GET one endpoint and return a result record."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=PROBE_TIMEOUT) as response:
            status = response.status
            content_type = response.headers.get("Content-Type")
            error = None
    except urllib.error.HTTPError as http_error:
        status = http_error.code
        content_type = http_error.headers.get("Content-Type")
        error = None
    except (urllib.error.URLError, TimeoutError, OSError) as net_error:
        # Covers DNS failures, refused connections, and timeouts; URLError
        # and socket.timeout are both OSError subclasses.
        status = None
        content_type = None
        reason = net_error.reason if isinstance(net_error, urllib.error.URLError) else net_error
        error = str(reason)
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "name": name,
        "url": url,
        "status": status,
        "content_type": content_type,
        "latency_ms": latency_ms,
        "error": error,
        "bot_blocked": status in BOT_BLOCK_STATUSES,
    }


def is_hard_fail(record: dict) -> bool:
    """Return True when a record means the endpoint is genuinely down."""
    if record["error"] is not None:
        return True
    if record["bot_blocked"]:
        return False
    return record["status"] is not None and record["status"] >= 500


def main() -> int:
    """Probe API-ish endpoints, write api-probe-report.json, and return an exit code."""
    parser = argparse.ArgumentParser(description="Probe API-ish endpoints listed in README.md.")
    parser.add_argument("--dry-run", action="store_true", help="print the probe plan without probing")
    parser.add_argument("--limit", type=int, default=0, help="maximum number of URLs to probe (0 = no limit)")
    args = parser.parse_args()

    pairs = collect_api_urls()
    if args.limit > 0:
        pairs = pairs[: args.limit]
    print(f"found {len(pairs)} API-ish endpoints in {README_PATH.name}")

    if args.dry_run:
        for name, url in pairs:
            print(f"  would probe: {name} <{url}>")
        return 0

    report = [probe_url(name, url) for name, url in pairs]
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    hard_fails = [record for record in report if is_hard_fail(record)]
    bot_blocks = [record for record in report if record["bot_blocked"]]
    ok = len(report) - len(hard_fails) - len(bot_blocks)
    print(
        f"{ok} ok, {len(bot_blocks)} bot-blocked, {len(hard_fails)} hard failures; "
        f"report written to {os.path.relpath(REPORT_PATH, ROOT)}"
    )
    for record in hard_fails:
        print(f"  FAIL: {record['name']} <{record['url']}> status={record['status']} error={record['error']}")
    return 1 if hard_fails else 0


if __name__ == "__main__":
    sys.exit(main())
