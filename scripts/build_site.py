#!/usr/bin/env python3
"""Build a static GitHub Pages site from README.md.

Parses the README's heading and bullet structure and renders a single
self-contained index.html (search, dark mode, table of contents, entry
cards) plus machine-readable exports into site/. Pure Python stdlib, no
dependencies.

Outputs:
    site/index.html      - the browsable site
    site/data.json       - structured copy of the list (optional
                           license/format/update_frequency fields)
    site/data.csv        - flattened copy of the list (same optional fields)
    site/feed.xml        - Atom feed with the latest 20 entries
    site/sitemap.xml     - single-URL sitemap for the site
    site/opensearch.xml  - search plugin (URLs like ?q=linz pre-filter)
    site/404.html        - friendly not-found page

When wayback-report.json (written by scripts/archive_links.py) is present,
entries that could not be archived get a Wayback Machine fallback link so the
content stays reachable even if the original source disappears.

Usage:
    python3 scripts/build_site.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
OUT_DIR = ROOT / "site"
OUT_HTML = OUT_DIR / "index.html"
OUT_JSON = OUT_DIR / "data.json"
OUT_CSV = OUT_DIR / "data.csv"
OUT_FEED = OUT_DIR / "feed.xml"
OUT_SITEMAP = OUT_DIR / "sitemap.xml"
OUT_OPENSEARCH = OUT_DIR / "opensearch.xml"
OUT_404 = OUT_DIR / "404.html"

# Report written by scripts/archive_links.py (uploaded as a workflow
# artifact, not committed). Its presence switches on Wayback fallback links.
WAYBACK_REPORT_PATH = ROOT / "wayback-report.json"
# Prefix for a Wayback Machine "latest snapshot" redirect.
WAYBACK_FALLBACK_PREFIX = "https://web.archive.org/web/2/"

# How many entries the Atom feed carries.
FEED_LIMIT = 20

# Where the site is published. Change this when deploying elsewhere.
SITE_URL = "https://olitreadwell.github.io/new-zealand-data/"
# Where the README that generates this site lives.
GITHUB_REPO_URL = "https://github.com/olitreadwell/new-zealand-data"
GITHUB_README_URL = "https://github.com/olitreadwell/new-zealand-data/blob/main/README.md"

LINK_RE = re.compile(r"\[([^\]]+)\] ?\(([^)]+)\)")
DESC_SEP_RE = re.compile(r"^[-–—:]\s*")

# Sections that are meta content, rendered at the bottom of the page rather
# than inside the category they appear under in the README.
META_SECTIONS = {
    "Browse the site",
    "Contributing",
    "How it's maintained",
    "Help wanted",
    "References and Attributions",
}


def esc(text: str) -> str:
    """HTML-escape text for safe embedding in the page."""
    return html.escape(text, quote=True)


def xml_esc(text: str) -> str:
    """Escape text for safe embedding in XML."""
    return html.escape(text, quote=True)


def slugify(name: str) -> str:
    """Turn a heading into a URL fragment id."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "section"


def strip_fragment(url: str) -> str:
    """Drop a URL fragment so entry and wayback-report URLs can be matched."""
    return url.split("#", 1)[0].strip()


def linkify(text: str) -> str:
    """Turn markdown links in plain text into HTML anchors."""
    parts: list[str] = []
    last = 0
    for m in LINK_RE.finditer(text):
        parts.append(esc(text[last : m.start()]))
        parts.append(
            f'<a href="{esc(m.group(2))}" target="_blank" rel="noopener">'
            f"{esc(m.group(1))}</a>"
        )
        last = m.end()
    parts.append(esc(text[last:]))
    return "".join(parts)


def parse_bullet(line: str) -> dict:
    """Parse a markdown bullet into an item dict."""
    stripped = line.lstrip(" \t")
    level = 1 if len(line) - len(stripped) > 0 else 0
    body = stripped[2:] if stripped.startswith("- ") else stripped[1:]
    if body.startswith("["):
        match = LINK_RE.match(body)
        if match:
            name = match.group(1).strip().replace("`", "")
            url = match.group(2).strip()
            rest = DESC_SEP_RE.sub("", body[match.end():].strip())
            if rest in {".", ":", "-", "–", "—"}:
                rest = ""
            return {
                "type": "entry",
                "name": name,
                "url": url,
                "desc": rest or None,
                "level": level,
            }
    return {"type": "text", "text": body.strip(), "level": level}


def parse_readme(text: str) -> dict:
    """Parse the README into a structured document."""
    title = "New Zealand Data & APIs"
    tagline = ""
    sections: list[dict] = []
    current: dict | None = None
    current_sub: dict | None = None

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.startswith("[!["):
            continue
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("### "):
            name = line[4:].strip()
            current = {
                "name": name,
                "meta": name in META_SECTIONS,
                "subs": [],
                "items": [],
            }
            sections.append(current)
            current_sub = None
        elif line.startswith("## "):
            name = line[3:].strip()
            current = {
                "name": name,
                "meta": name in META_SECTIONS,
                "subs": [],
                "items": [],
            }
            sections.append(current)
            current_sub = None
        elif line.startswith("#### "):
            name = line[5:].strip()
            if name in META_SECTIONS:
                current = {"name": name, "meta": True, "subs": [], "items": []}
                sections.append(current)
                current_sub = None
            elif current is not None:
                current_sub = {"name": name, "items": []}
                current["subs"].append(current_sub)
        elif line.lstrip(" \t").startswith("- "):
            item = parse_bullet(line)
            if current_sub is not None:
                current_sub["items"].append(item)
            elif current is not None:
                current["items"].append(item)
        elif current is not None:
            current["items"].append({"type": "text", "text": line.strip(), "level": 0})
        elif not tagline:
            tagline = line.strip()

    return {"title": title, "tagline": tagline, "sections": sections}


def collect_search(items: list[dict]) -> list[str]:
    """Collect searchable text for an item and its nested children."""
    parts: list[str] = []
    for item in items:
        if item["type"] == "entry":
            parts.append(item["name"])
            if item["desc"]:
                parts.append(item["desc"])
        else:
            parts.append(item["text"])
    return parts


def entry_is_dead(record: dict) -> bool:
    """True when the wayback report found no snapshot and could not save one."""
    return not record.get("saved") and not record.get("snapshot_exists")


def load_wayback_report(path: Path = WAYBACK_REPORT_PATH) -> dict[str, dict]:
    """Load wayback-report.json as {url: record}; {} when absent or invalid."""
    if not path.exists():
        return {}
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(records, list):
        return {}
    by_url: dict[str, dict] = {}
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("url"), str):
            by_url[strip_fragment(record["url"])] = record
    return by_url


def wayback_fallback_url(url: str) -> str:
    """Latest-snapshot Wayback URL for an entry."""
    return WAYBACK_FALLBACK_PREFIX + url


def entry_json_ld(item: dict) -> dict:
    """Schema.org Dataset JSON-LD for one entry."""
    data = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": item["name"],
        "url": item["url"],
    }
    if item.get("desc"):
        data["description"] = item["desc"]
    if item.get("license"):
        data["license"] = item["license"]
    if item.get("format"):
        data["distribution"] = {
            "@type": "DataDownload",
            "contentUrl": item["url"],
            "encodingFormat": item["format"],
        }
    return data


def render_entry_json_ld(item: dict) -> str:
    """Render an entry's Dataset JSON-LD as a safe script tag."""
    body = json.dumps(entry_json_ld(item), ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{body}</script>'


def render_entry(item: dict, dead_urls: set[str] | None = None) -> str:
    """Render a single entry line plus its JSON-LD."""
    if dead_urls is None:
        dead_urls = set()
    indent = item["level"] * 18
    style = f' style="padding-left:{indent}px"' if indent else ""
    name = esc(item["name"])
    url = esc(item["url"])
    wayback = ""
    if strip_fragment(item["url"]) in dead_urls:
        wayback = (
            f' <a class="wayback" href="{esc(wayback_fallback_url(item["url"]))}"'
            ' title="View archived copy" target="_blank" rel="noopener">Wayback</a>'
        )
    desc = f'<span class="desc">{esc(item["desc"])}</span>' if item["desc"] else ""
    return (
        f'<div class="entry"{style}>'
        f'<a class="link" href="{url}" target="_blank" rel="noopener">{name}</a>'
        f"{wayback}{desc}</div>\n"
        f"{render_entry_json_ld(item)}"
    )


def render_text(item: dict) -> str:
    """Render a plain-text item, linkifying any markdown links."""
    return f'<p class="note">{linkify(item["text"])}</p>'


def render_items(items: list[dict], dead_urls: set[str] | None = None) -> str:
    """Render top-level items with their nested children."""
    if dead_urls is None:
        dead_urls = set()
    out: list[str] = []
    i = 0
    while i < len(items):
        item = items[i]
        children: list[dict] = []
        j = i + 1
        while j < len(items) and items[j]["level"] > 0:
            children.append(items[j])
            j += 1

        if item["type"] == "text":
            if children:
                search = " ".join(collect_search([item] + children)).lower()
                out.append(f'<div class="group" data-search="{esc(search)}">')
                out.append(f'<h4 class="group-name">{esc(item["text"])}</h4>')
                out.append('<div class="sub">')
                out.extend(render_entry(child, dead_urls) for child in children)
                out.append("</div></div>")
            else:
                out.append(render_text(item))
        else:
            search = " ".join(collect_search([item] + children)).lower()
            out.append(f'<div class="item" data-search="{esc(search)}">')
            out.append(render_entry(item, dead_urls))
            if children:
                out.append('<div class="sub">')
                out.extend(render_entry(child, dead_urls) for child in children)
                out.append("</div>")
            out.append("</div>")
        i = j
    return "\n".join(out)


def render_section(section: dict, dead_urls: set[str] | None = None) -> str:
    """Render one section of the page."""
    if dead_urls is None:
        dead_urls = set()
    body = render_items(section["items"], dead_urls)
    for sub in section["subs"]:
        body += (
            f'\n<h3 id="{slugify(sub["name"])}">{esc(sub["name"])}</h3>\n'
            + render_items(sub["items"], dead_urls)
        )
    static = " data-static" if section["meta"] else ""
    return (
        f'<section id="{slugify(section["name"])}"'
        f' data-section="{esc(section["name"])}"{static}>\n'
        f"<h2>{esc(section['name'])}</h2>\n{body}</section>"
    )


def flatten(doc: dict) -> list[dict]:
    """Flatten all entry items with their section names."""
    rows = []
    for section in doc["sections"]:
        for item in section["items"]:
            if item["type"] == "entry":
                rows.append(
                    {
                        "name": item["name"],
                        "url": item["url"],
                        "description": item["desc"] or "",
                        "category": section["name"],
                        "license": item.get("license"),
                        "format": item.get("format"),
                        "update_frequency": item.get("update_frequency"),
                    }
                )
    return rows


def csv_encode(value: str | None) -> str:
    """Quote a CSV field when needed."""
    if value is None:
        return ""
    if any(ch in value for ch in '",\n\r'):
        return '"' + value.replace('"', '""') + '"'
    return value


def render_csv(rows: list[dict]) -> str:
    """Render the list as CSV."""
    header = [
        "name",
        "url",
        "description",
        "category",
        "license",
        "format",
        "update_frequency",
    ]
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(csv_encode(row[k]) for k in header))
    return "\n".join(lines) + "\n"


def to_json(doc: dict) -> dict:
    """Shape the parsed document for data.json."""
    sections = []
    for section in doc["sections"]:
        items = []
        for item in section["items"]:
            if item["type"] == "entry":
                items.append(
                    {
                        "name": item["name"],
                        "url": item["url"],
                        "description": item["desc"],
                        "license": item.get("license"),
                        "format": item.get("format"),
                        "update_frequency": item.get("update_frequency"),
                    }
                )
            else:
                items.append({"text": item["text"]})
        sections.append({"name": section["name"], "items": items})
    return {"title": doc["title"], "tagline": doc["tagline"], "sections": sections}


def rfc3339(dt: datetime) -> str:
    """Format a datetime as an RFC 3339 UTC timestamp."""
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def render_feed(doc: dict, rows: list[dict], updated: str) -> str:
    """Render an Atom feed with the latest FEED_LIMIT entries."""
    feed_url = SITE_URL.rstrip("/") + "/"
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"  <title>{xml_esc(doc['title'])}</title>",
        f'  <link href="{xml_esc(feed_url)}"/>',
        f'  <link rel="self" href="{xml_esc(feed_url + "feed.xml")}"/>',
        f"  <id>{xml_esc(feed_url)}</id>",
        f"  <updated>{updated}</updated>",
        "  <generator>scripts/build_site.py</generator>",
    ]
    for row in rows[:FEED_LIMIT]:
        lines.extend(
            [
                "  <entry>",
                f"    <title>{xml_esc(row['name'])}</title>",
                f'    <link href="{xml_esc(row["url"])}"/>',
                f"    <id>{xml_esc(row['url'])}</id>",
                f"    <updated>{updated}</updated>",
                f'    <category term="{xml_esc(row["category"])}"/>',
            ]
        )
        if row["description"]:
            lines.append(f"    <summary>{xml_esc(row['description'])}</summary>")
        lines.append("  </entry>")
    lines.append("</feed>")
    return "\n".join(lines) + "\n"


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__TAGLINE__">
<meta name="color-scheme" content="light dark">
<link rel="search" type="application/opensearchdescription+xml" title="__TITLE__" href="opensearch.xml">
<link rel="alternate" type="application/atom+xml" title="__TITLE__" href="feed.xml">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "__TITLE__",
  "description": "__TAGLINE__",
  "url": "__SITE_URL__",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "__SITE_URL__?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
</script>
<style>
:root {
  --bg: #f6f8fa;
  --surface: #ffffff;
  --text: #1f2937;
  --muted: #6b7280;
  --accent: #0f766e;
  --accent-soft: #ccfbf1;
  --border: #e5e7eb;
  --radius: 10px;
  --shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
}
[data-theme="dark"] {
  --bg: #0f172a;
  --surface: #1e293b;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --accent: #2dd4bf;
  --accent-soft: #134e4a;
  --border: #334155;
  --shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.55;
}
.wrap { max-width: 1100px; margin: 0 auto; padding: 0 20px; }
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 0;
  background: var(--accent);
  z-index: 30;
}
.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow);
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding-top: 14px;
  padding-bottom: 14px;
}
h1 { font-size: 1.35rem; margin: 0; }
.tagline { margin: 2px 0 0; color: var(--muted); font-size: 0.95rem; }
.stats { margin-top: 4px; font-size: 0.85rem; color: var(--muted); }
.header-actions { display: flex; gap: 10px; align-items: center; }
#search {
  width: 260px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.95rem;
  background: var(--bg);
  color: var(--text);
}
#search:focus { outline: 2px solid var(--accent); outline-offset: -1px; background: var(--surface); }
.btn, .theme-btn {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}
.btn {
  background: var(--accent);
  color: #fff;
  text-decoration: none;
}
.btn:hover { background: #115e59; }
.theme-btn {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
}
.theme-btn:hover { border-color: var(--accent); color: var(--accent); }
.layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
  padding-top: 24px;
  padding-bottom: 48px;
}
.toc {
  position: sticky;
  top: 90px;
  align-self: start;
  max-height: calc(100vh - 120px);
  overflow: auto;
}
.toc-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  margin: 0 0 8px;
}
.toc ul { list-style: none; margin: 0; padding: 0; }
.toc a {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 5px 8px;
  border-radius: 6px;
  color: var(--text);
  text-decoration: none;
  font-size: 0.9rem;
}
.toc a:hover { background: var(--accent-soft); color: var(--accent); }
.toc-count { color: var(--muted); font-size: 0.8rem; }
section[data-section] { margin-bottom: 28px; }
section[data-section] h2 {
  font-size: 1.15rem;
  margin: 0 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--accent);
  display: inline-block;
}
h3 { font-size: 1rem; margin: 20px 0 10px; color: var(--accent); }
.item, .group {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 14px;
  margin-bottom: 8px;
  box-shadow: var(--shadow);
}
.group-name { margin: 0 0 6px; font-size: 0.95rem; font-weight: 700; }
.entry { padding: 2px 0; }
.entry .link { color: var(--accent); text-decoration: none; font-weight: 600; }
.entry .link:hover { text-decoration: underline; }
.entry .desc { color: var(--muted); font-size: 0.9rem; }
.entry .desc::before { content: "\\2013  "; color: var(--border); }
.entry .wayback {
  color: var(--muted);
  font-size: 0.85rem;
  margin-left: 8px;
  text-decoration: none;
  white-space: nowrap;
}
.entry .wayback:hover { color: var(--accent); text-decoration: underline; }
.note {
  color: var(--muted);
  font-size: 0.92rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 14px;
}
.note a { color: var(--accent); }
.result-count { color: var(--muted); font-size: 0.9rem; margin: 0 0 16px; }
.site-footer {
  margin-top: 40px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.85rem;
}
.site-footer a { color: var(--accent); }
.back-to-top {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--accent);
  font-size: 1.1rem;
  cursor: pointer;
  box-shadow: var(--shadow);
}
.back-to-top:hover { background: var(--accent-soft); }
@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  .toc { position: static; max-height: none; }
  #search { width: 100%; }
  .header-inner { flex-direction: column; align-items: stretch; }
}
@media print {
  .site-header, .toc, .back-to-top, .result-count, .scroll-progress { display: none; }
  .layout { display: block; }
  .item, .group { break-inside: avoid; }
}
</style>
<script>
// Apply the saved or system theme before first paint to avoid a light flash.
try {
  const saved = localStorage.getItem("theme");
  const dark = saved
    ? saved === "dark"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.dataset.theme = dark ? "dark" : "light";
} catch (e) {}
</script>
</head>
<body>
<div id="progress" class="scroll-progress" aria-hidden="true"></div>
<header class="site-header">
  <div class="wrap header-inner">
    <div>
      <h1>__TITLE__</h1>
      <p class="tagline">__TAGLINE__</p>
      <p class="stats">__STATS__</p>
    </div>
    <div class="header-actions">
      <input id="search" type="search" placeholder="Search datasets and APIs…"
        autocomplete="off" aria-label="Search datasets and APIs">
      <button id="theme" class="theme-btn" aria-label="Toggle dark mode">Dark</button>
      <a class="btn" href="__GITHUB_REPO_URL__"
        target="_blank" rel="noopener">View on GitHub</a>
    </div>
  </div>
</header>
<main class="wrap layout">
  <nav class="toc" aria-label="Table of contents">
    <p class="toc-title">Contents</p>
    <ul id="toc-list"></ul>
  </nav>
  <div class="content">
    <p class="result-count" id="count" role="status"></p>
__SECTIONS__
    <footer class="site-footer">
      <p>Generated from
        <a href="__GITHUB_README_URL__">README.md</a>
        by <code>scripts/build_site.py</code>. Machine-readable copies:
        <a href="data.json">data.json</a>, <a href="data.csv">data.csv</a>,
        <a href="feed.xml">feed.xml</a>.
        Found a dead link or a missing dataset? Open an issue or pull request
        on <a href="__GITHUB_REPO_URL__">GitHub</a>.</p>
    </footer>
  </div>
</main>
<button id="top" class="back-to-top" aria-label="Back to top" hidden>&#8593;</button>
<script>
const search = document.getElementById("search");
const count = document.getElementById("count");
const topBtn = document.getElementById("top");
const progress = document.getElementById("progress");
const themeBtn = document.getElementById("theme");
const sections = Array.from(document.querySelectorAll("[data-section]"));
const tocList = document.getElementById("toc-list");

sections.forEach((section) => {
  const li = document.createElement("li");
  const a = document.createElement("a");
  a.href = "#" + section.id;
  a.textContent = section.dataset.section;
  const span = document.createElement("span");
  span.className = "toc-count";
  span.textContent = section.querySelectorAll(".entry").length;
  a.appendChild(span);
  li.appendChild(a);
  tocList.appendChild(li);
});

const totalLinks = document.querySelectorAll(".entry").length;
count.textContent = totalLinks + " links";

function update() {
  const q = search.value.trim().toLowerCase();
  let visible = 0;
  sections.forEach((section) => {
    if (section.dataset.static !== undefined) {
      section.hidden = !!q;
      return;
    }
    let any = false;
    section.querySelectorAll("[data-search]").forEach((el) => {
      const hit = !q || el.dataset.search.includes(q);
      el.hidden = !hit;
      if (hit) {
        any = true;
        visible += el.querySelectorAll(".entry").length;
      }
    });
    section.hidden = !any;
  });
  count.textContent = q
    ? visible + " of " + totalLinks + " links match"
    : totalLinks + " links";
}

search.addEventListener("input", update);

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeBtn.textContent = theme === "dark" ? "Light" : "Dark";
}
const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(savedTheme || (prefersDark ? "dark" : "light"));
themeBtn.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
});

window.addEventListener("scroll", () => {
  const doc = document.documentElement;
  const max = doc.scrollHeight - doc.clientHeight;
  progress.style.width = (max > 0 ? (doc.scrollTop / max) * 100 : 0) + "%";
  topBtn.hidden = window.scrollY < 400;
});
topBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

document.addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== search) {
    e.preventDefault();
    search.focus();
  }
});

const params = new URLSearchParams(window.location.search);
const q = params.get("q");
if (q) {
  search.value = q;
  update();
}
</script>
</body>
</html>
"""

NOT_FOUND_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found — __TITLE__</title>
<meta name="robots" content="noindex">
<style>
  body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg, #f6f8fa);
    color: var(--text, #1f2937);
    text-align: center;
  }
  .card { max-width: 480px; padding: 24px; }
  h1 { font-size: 2.5rem; margin: 0 0 8px; color: var(--accent, #0f766e); }
  p { color: var(--muted, #6b7280); }
  a { color: var(--accent, #0f766e); }
</style>
</head>
<body>
  <div class="card">
    <h1>404</h1>
    <p>That page doesn't exist, but the list of New Zealand data and APIs is
    all on one page anyway.</p>
    <p><a href="./">Back to the list</a></p>
  </div>
</body>
</html>
"""


def main() -> int:
    """Build the site and exports from the README."""
    if not README_PATH.exists():
        print(f"error: {README_PATH} not found", file=sys.stderr)
        return 1
    doc = parse_readme(README_PATH.read_text(encoding="utf-8"))
    rows = flatten(doc)
    wayback_report = load_wayback_report(WAYBACK_REPORT_PATH)
    dead_urls = {
        url for url, record in wayback_report.items() if entry_is_dead(record)
    }
    sections_html = "\n".join(render_section(s, dead_urls) for s in doc["sections"])
    categories = [s["name"] for s in doc["sections"] if not s["meta"]]
    stats = f"{len(rows)} links across {len(categories)} categories"
    page = (
        PAGE_TEMPLATE.replace("__TITLE__", esc(doc["title"]))
        .replace("__TAGLINE__", esc(doc["tagline"]))
        .replace("__SITE_URL__", esc(SITE_URL.rstrip("/")))
        .replace("__GITHUB_REPO_URL__", esc(GITHUB_REPO_URL))
        .replace("__GITHUB_README_URL__", esc(GITHUB_README_URL))
        .replace("__STATS__", esc(stats))
        .replace("__SECTIONS__", sections_html)
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(page, encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(to_json(doc), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    OUT_CSV.write_text(render_csv(rows), encoding="utf-8")
    updated = rfc3339(datetime.now(timezone.utc))
    OUT_FEED.write_text(render_feed(doc, rows, updated), encoding="utf-8")
    OUT_SITEMAP.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{esc(SITE_URL)}</loc>"
        f"<lastmod>{date.today().isoformat()}</lastmod></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    OUT_OPENSEARCH.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">\n'
        f"  <ShortName>{esc(doc['title'])}</ShortName>\n"
        f"  <Description>{esc(doc['tagline'])}</Description>\n"
        f'  <Url type="text/html" template="{esc(SITE_URL)}?q={{searchTerms}}" />\n'
        "  <InputEncoding>UTF-8</InputEncoding>\n"
        "</OpenSearchDescription>\n",
        encoding="utf-8",
    )
    OUT_404.write_text(
        NOT_FOUND_TEMPLATE.replace("__TITLE__", esc(doc["title"])),
        encoding="utf-8",
    )
    try:
        out_rel = OUT_DIR.relative_to(ROOT)
    except ValueError:
        out_rel = OUT_DIR
    print(
        f"wrote {len(list(OUT_DIR.iterdir()))} files to {out_rel} "
        f"({len(categories)} categories, {len(rows)} links)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
