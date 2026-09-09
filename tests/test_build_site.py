"""Tests for the README parser helpers in scripts/build_site.py."""

from __future__ import annotations

from build_site import flatten, parse_bullet, parse_readme


def test_parse_bullet_entry_with_desc():
    item = parse_bullet("- [LINZ](https://data.linz.govt.nz/) - Authoritative data")
    assert item == {
        "type": "entry",
        "name": "LINZ",
        "url": "https://data.linz.govt.nz/",
        "desc": "Authoritative data",
        "level": 0,
    }


def test_parse_bullet_entry_with_en_dash_desc():
    item = parse_bullet("- [Govt.nz](https://www.govt.nz/about/api) – API listing")
    assert item["type"] == "entry"
    assert item["desc"] == "API listing"


def test_parse_bullet_entry_without_desc():
    item = parse_bullet("- [Statistics](https://stats.example.com)")
    assert item["type"] == "entry"
    assert item["name"] == "Statistics"
    assert item["desc"] is None


def test_parse_bullet_strips_backticks_from_name():
    item = parse_bullet("- [`NZ.Stat`](https://nzdotstat.stats.govt.nz/)")
    assert item["name"] == "NZ.Stat"


def test_parse_bullet_nested_entry_has_level_one():
    item = parse_bullet("\t- [Sub item](https://sub.example)")
    assert item["level"] == 1


def test_parse_bullet_plain_text():
    item = parse_bullet("- a note without a link")
    assert item == {"type": "text", "text": "a note without a link", "level": 0, "bullet": True}


def test_parse_readme_structure():
    text = """\
# My List

A tagline.

## Category A

- [Alpha](https://a.example/alpha) - first entry

- a plain note bullet

#### Subsection

- [Beta](https://b.example/beta) - second entry

## Category B

- [Gamma](https://c.example/gamma)
"""
    doc = parse_readme(text)
    assert doc["title"] == "My List"
    assert doc["tagline"] == "A tagline."
    assert [s["name"] for s in doc["sections"]] == ["Category A", "Category B"]

    section_a = doc["sections"][0]
    assert section_a["items"][0]["name"] == "Alpha"
    assert section_a["items"][1]["type"] == "text"
    assert section_a["subs"][0]["name"] == "Subsection"
    assert section_a["subs"][0]["items"][0]["name"] == "Beta"

    section_b = doc["sections"][1]
    assert section_b["items"][0]["name"] == "Gamma"


def test_parse_readme_marks_meta_sections():
    text = """\
# My List

## Category A

- [Alpha](https://a.example/alpha)

#### How it's maintained

- [Tooling](https://tool.example)
"""
    doc = parse_readme(text)
    assert doc["sections"][1]["name"] == "How it's maintained"
    assert doc["sections"][1]["meta"] is True


def test_flatten_includes_top_level_entries_only():
    text = """\
# My List

## Category A

- [Alpha](https://a.example/alpha) - first entry

#### Subsection

- [Beta](https://b.example/beta) - second entry

## Category B

- [Gamma](https://c.example/gamma)
"""
    rows = flatten(parse_readme(text))
    assert rows == [
        {
            "name": "Alpha",
            "url": "https://a.example/alpha",
            "description": "first entry",
            "category": "Category A",
            "license": None,
            "format": None,
            "update_frequency": None,
        },
        {
            "name": "Gamma",
            "url": "https://c.example/gamma",
            "description": "",
            "category": "Category B",
            "license": None,
            "format": None,
            "update_frequency": None,
        },
    ]
"""Tests for scripts/build_site.py."""

import json
import re
import xml.etree.ElementTree as ET

import build_site


ATOM_NS = "http://www.w3.org/2005/Atom"
RFC3339_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)")

SAMPLE_README = """# Test Data Site

An intro line.

## Browse the site

### Sample Section

- [Example Dataset](https://example.com/data) - a test dataset
- [Fragmented](https://example.com/page#anchor) - with a fragment

A plain note.

- Group Name
\t- [Child One](https://example.com/child1) - child description

## Real Data

- [Stats](https://stats.example.com)

#### Help wanted
"""


def parse_sample() -> dict:
    """Parse the shared sample README once per test."""
    return build_site.parse_readme(SAMPLE_README)


def test_parse_readme_basic() -> None:
    doc = parse_sample()
    assert doc["title"] == "Test Data Site"
    assert doc["tagline"] == "An intro line."
    names = [s["name"] for s in doc["sections"]]
    assert names == ["Browse the site", "Sample Section", "Real Data", "Help wanted"]
    assert doc["sections"][-1]["meta"] is True


def test_parse_readme_entries_and_children() -> None:
    doc = parse_sample()
    section = doc["sections"][1]
    entries = [i for i in section["items"] if i["type"] == "entry"]
    assert entries[0] == {
        "type": "entry",
        "name": "Example Dataset",
        "url": "https://example.com/data",
        "desc": "a test dataset",
        "level": 0,
    }
    group = next(
        i for i in section["items"] if i["type"] == "text" and i["text"] == "Group Name"
    )
    assert group["text"] == "Group Name"
    assert group["level"] == 0
    child = next(i for i in section["items"] if i["type"] == "entry" and i["level"] > 0)
    assert child["name"] == "Child One"


def test_flatten_defaults_optional_fields_to_none() -> None:
    rows = build_site.flatten(parse_sample())
    assert len(rows) == 4
    for row in rows:
        assert set(row) == {
            "name",
            "url",
            "description",
            "category",
            "license",
            "format",
            "update_frequency",
        }
        assert row["license"] is None
        assert row["format"] is None
        assert row["update_frequency"] is None
    stats = next(r for r in rows if r["name"] == "Stats")
    assert stats["description"] == ""
    assert stats["category"] == "Real Data"


def test_flatten_keeps_populated_optional_metadata() -> None:
    doc = parse_sample()
    doc["sections"][1]["items"][0]["license"] = "CC-BY-4.0"
    doc["sections"][1]["items"][0]["format"] = "CSV"
    doc["sections"][1]["items"][0]["update_frequency"] = "monthly"
    row = build_site.flatten(doc)[0]
    assert row["license"] == "CC-BY-4.0"
    assert row["format"] == "CSV"
    assert row["update_frequency"] == "monthly"


def test_to_json_null_defaults() -> None:
    data = build_site.to_json(parse_sample())
    entry = next(e for s in data["sections"] for e in s["items"] if "url" in e)
    assert entry["license"] is None
    assert entry["format"] is None
    assert entry["update_frequency"] is None
    assert entry["description"] == "a test dataset"


def test_render_csv_header_and_null_cells() -> None:
    rows = build_site.flatten(parse_sample())
    csv_text = build_site.render_csv(rows)
    lines = csv_text.strip().splitlines()
    assert lines[0].split(",") == [
        "name",
        "url",
        "description",
        "category",
        "license",
        "format",
        "update_frequency",
    ]
    # Null fields render as empty cells, and quoted descriptions survive round-trip.
    import csv as csv_module

    parsed = list(csv_module.reader(lines[1:]))
    row = next(r for r in parsed if r[0] == "Example Dataset")
    assert row[4:] == ["", "", ""]
    assert row[2] == "a test dataset"


def test_csv_encode_handles_none_and_quotes() -> None:
    assert build_site.csv_encode(None) == ""
    assert build_site.csv_encode("plain") == "plain"
    assert build_site.csv_encode('has, comma') == '"has, comma"'
    assert build_site.csv_encode('say "hi"') == '"say ""hi"""'


def test_load_wayback_report_absent(tmp_path) -> None:
    assert build_site.load_wayback_report(tmp_path / "missing.json") == {}


def test_load_wayback_report_invalid(tmp_path) -> None:
    bad = tmp_path / "wayback-report.json"
    bad.write_text("not json")
    assert build_site.load_wayback_report(bad) == {}
    bad.write_text('{"url": "https://example.com"}')
    assert build_site.load_wayback_report(bad) == {}


def test_load_wayback_report_keys_by_fragmentless_url(tmp_path) -> None:
    report = tmp_path / "wayback-report.json"
    report.write_text(
        json.dumps(
            [
                {
                    "name": "Example",
                    "url": "https://example.com/data",
                    "snapshot_exists": False,
                    "saved": False,
                },
                {"not": "a record"},
            ]
        )
    )
    loaded = build_site.load_wayback_report(report)
    assert loaded == {"https://example.com/data": loaded["https://example.com/data"]}
    assert len(loaded) == 1


def test_entry_is_dead() -> None:
    assert build_site.entry_is_dead({"saved": False, "snapshot_exists": False}) is True
    assert build_site.entry_is_dead({"saved": True, "snapshot_exists": False}) is False
    assert build_site.entry_is_dead({"saved": False, "snapshot_exists": True}) is False
    assert build_site.entry_is_dead({}) is True


def test_wayback_fallback_rendered_for_dead_entry() -> None:
    item = {"type": "entry", "name": "Fragmented", "url": "https://example.com/page#anchor", "desc": None, "level": 0}
    plain = build_site.render_entry(item)
    assert 'class="wayback"' not in plain
    fallback = build_site.render_entry(item, {"https://example.com/page"})
    assert 'class="wayback"' in fallback
    assert (
        'https://web.archive.org/web/2/https://example.com/page#anchor'
        in fallback
    )


def test_entry_json_ld_and_safe_script() -> None:
    item = {
        "type": "entry",
        "name": "Example Dataset",
        "url": "https://example.com/data",
        "desc": "a test dataset",
        "level": 0,
        "license": "CC-BY-4.0",
        "format": "CSV",
    }
    data = build_site.entry_json_ld(item)
    assert data["@type"] == "Dataset"
    assert data["name"] == "Example Dataset"
    assert data["license"] == "CC-BY-4.0"
    assert data["distribution"]["encodingFormat"] == "CSV"
    script = build_site.render_entry_json_ld(
        {**item, "desc": 'closing tag </script> in text'}
    )
    assert "<\\/script>" in script
    assert '"description": "closing tag <\\/script> in text"' in script
    assert ">\"</script>" not in script


def test_render_feed_limits_entries_and_rfc3339() -> None:
    doc = parse_sample()
    rows = [
        {
            "name": f"Entry {i}",
            "url": f"https://example.com/{i}",
            "description": f"desc {i}",
            "category": "Sample Section",
        }
        for i in range(25)
    ]
    feed = build_site.render_feed(doc, rows, "2026-08-25T00:00:00+00:00")
    root = ET.fromstring(feed)
    assert root.tag == f"{{{ATOM_NS}}}feed"
    entries = root.findall(f"{{{ATOM_NS}}}entry")
    assert len(entries) == 20
    assert entries[0].find(f"{{{ATOM_NS}}}title").text == "Entry 0"
    assert entries[0].find(f"{{{ATOM_NS}}}link").attrib["href"] == "https://example.com/0"
    assert entries[0].find(f"{{{ATOM_NS}}}id").text == "https://example.com/0"
    assert entries[0].find(f"{{{ATOM_NS}}}summary").text == "desc 0"
    assert re.fullmatch(RFC3339_RE, root.find(f"{{{ATOM_NS}}}updated").text)


def test_render_feed_escapes_xml() -> None:
    doc = parse_sample()
    rows = [
        {
            "name": "R&D <live>",
            "url": "https://example.com/?a=1&b=2",
            "description": "x < y & z",
            "category": "A & B",
        }
    ]
    feed = build_site.render_feed(doc, rows, "2026-08-25T00:00:00+00:00")
    root = ET.fromstring(feed)
    entry = root.find(f"{{{ATOM_NS}}}entry")
    assert entry.find(f"{{{ATOM_NS}}}title").text == "R&D <live>"
    assert entry.find(f"{{{ATOM_NS}}}summary").text == "x < y & z"
    assert entry.find(f"{{{ATOM_NS}}}category").attrib["term"] == "A & B"


def _redirect_outputs(monkeypatch, tmp_path):
    """Point every build_site output path at a temp directory."""
    monkeypatch.setattr(build_site, "README_PATH", tmp_path / "README.md")
    monkeypatch.setattr(
        build_site, "WAYBACK_REPORT_PATH", tmp_path / "wayback-report.json"
    )
    out_dir = tmp_path / "site"
    monkeypatch.setattr(build_site, "OUT_DIR", out_dir)
    monkeypatch.setattr(build_site, "OUT_HTML", out_dir / "index.html")
    monkeypatch.setattr(build_site, "OUT_JSON", out_dir / "data.json")
    monkeypatch.setattr(build_site, "OUT_CSV", out_dir / "data.csv")
    monkeypatch.setattr(build_site, "OUT_FEED", out_dir / "feed.xml")
    monkeypatch.setattr(build_site, "OUT_SITEMAP", out_dir / "sitemap.xml")
    monkeypatch.setattr(build_site, "OUT_OPENSEARCH", out_dir / "opensearch.xml")
    monkeypatch.setattr(build_site, "OUT_404", out_dir / "404.html")
    return out_dir


def test_main_writes_all_outputs(monkeypatch, tmp_path) -> None:
    out_dir = _redirect_outputs(monkeypatch, tmp_path)
    (tmp_path / "README.md").write_text(SAMPLE_README)
    assert build_site.main() == 0

    assert (out_dir / "index.html").exists()
    assert (out_dir / "data.json").exists()
    assert (out_dir / "data.csv").exists()
    assert (out_dir / "feed.xml").exists()
    assert (out_dir / "sitemap.xml").exists()
    assert (out_dir / "opensearch.xml").exists()
    assert (out_dir / "404.html").exists()

    feed_root = ET.parse(str(out_dir / "feed.xml")).getroot()
    assert len(feed_root.findall(f"{{{ATOM_NS}}}entry")) == 4
    assert re.fullmatch(
        RFC3339_RE, feed_root.find(f"{{{ATOM_NS}}}updated").text
    )

    data = json.loads((out_dir / "data.json").read_text())
    entry = next(e for s in data["sections"] for e in s["items"] if "url" in e)
    assert entry["license"] is None

    html_text = (out_dir / "index.html").read_text()
    scripts = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html_text, re.S
    )
    assert len(scripts) == 1 + 4  # one WebSite block plus one per entry
    assert 'class="wayback"' not in html_text


def test_main_adds_wayback_fallback_when_report_present(
    monkeypatch, tmp_path
) -> None:
    out_dir = _redirect_outputs(monkeypatch, tmp_path)
    (tmp_path / "README.md").write_text(SAMPLE_README)
    (tmp_path / "wayback-report.json").write_text(
        json.dumps(
            [
                {
                    "name": "Example Dataset",
                    "url": "https://example.com/data",
                    "snapshot_exists": False,
                    "saved": False,
                }
            ]
        )
    )
    assert build_site.main() == 0
    html_text = (out_dir / "index.html").read_text()
    assert (
        'class="wayback" href="https://web.archive.org/web/2/https://example.com/data"'
        in html_text
    )
