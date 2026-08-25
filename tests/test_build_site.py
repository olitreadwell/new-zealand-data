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
    assert item == {"type": "text", "text": "a note without a link", "level": 0}


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
        },
        {
            "name": "Gamma",
            "url": "https://c.example/gamma",
            "description": "",
            "category": "Category B",
        },
    ]
