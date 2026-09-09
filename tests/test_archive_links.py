"""Tests for the URL collection helper in scripts/archive_links.py."""

from __future__ import annotations

from archive_links import collect_urls


def test_collect_urls_deduplicates_and_filters(write_readme):
    write_readme(
        """\
# My List

## Category A

- [One](https://example.com/one) - first
- [One again](https://example.com/one) - duplicate
- [Fragment](https://example.com/two#part)
- [FTP](ftp://files.example.com/data)
- [Relative](/local/page)
- [Plain](no scheme here)
"""
    )
    assert collect_urls() == [
        ("One", "https://example.com/one"),
        ("Fragment", "https://example.com/two"),
    ]


def test_collect_urls_returns_empty_list_without_entries(write_readme):
    write_readme(
        """\
# My List

Some text with no bullets.
"""
    )
    assert collect_urls() == []
