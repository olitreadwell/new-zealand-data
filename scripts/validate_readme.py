#!/usr/bin/env python3
"""Validate README.md structure.

Reuses the same parser as scripts/build_site.py and flags issues that
would break the site or the link check: malformed links, duplicate URLs,
relative or fragment-only URLs, and inconsistent bullet nesting. Runs in
CI on every pull request.

Usage:
    python3 scripts/validate_readme.py
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from urllib.parse import urlparse

from build_site import README_PATH, parse_bullet, parse_readme

LINK_RE = re.compile(r"\[([^\]]+)\] ?\(([^)]+)\)")


def main() -> int:
    """Run all checks and return a process exit code."""
    errors: list[str] = []
    text = README_PATH.read_text(encoding="utf-8")
    doc = parse_readme(text)

    urls: list[str] = []
    for section in doc["sections"]:
        for item in section["items"]:
            if item["type"] != "entry":
                continue
            urls.append(item["url"])
            if item["url"].startswith("#"):
                errors.append(
                    f"entry '{item['name']}' points at an in-page fragment: {item['url']}"
                )
            elif item["url"].startswith(("/", "./", "../")):
                errors.append(
                    f"entry '{item['name']}' uses a relative URL: {item['url']}"
                )
            elif not urlparse(item["url"]).scheme:
                errors.append(
                    f"entry '{item['name']}' has no URL scheme: {item['url']}"
                )

    for url, count in Counter(urls).items():
        if count > 1:
            errors.append(f"duplicate link ({count}x): {url}")

    prev_level = -1
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip(" \t")
        if not stripped.startswith("- "):
            continue
        if stripped.startswith("- [") and not LINK_RE.match(stripped[2:]):
            errors.append(f"line {lineno}: malformed link: {raw.strip()}")
        item = parse_bullet(raw)
        if item["level"] > prev_level + 1:
            errors.append(f"line {lineno}: bullet jumps {prev_level} -> {item['level']} levels")
        prev_level = item["level"]

    if errors:
        print(f"{len(errors)} problem(s) found in {README_PATH.name}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        f"OK: {README_PATH.name} parses cleanly "
        f"({len(urls)} links, {len(doc['sections'])} sections)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
