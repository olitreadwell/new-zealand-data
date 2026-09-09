"""Tests for the README checks in scripts/validate_readme.py."""

from __future__ import annotations

import validate_readme


def test_valid_readme_passes(write_readme, capsys):
    write_readme(
        """\
# My List

## Category A

- [Alpha](https://a.example/alpha) - first entry
- [Gamma](https://c.example/gamma)
"""
    )
    assert validate_readme.main() == 0
    assert "OK:" in capsys.readouterr().out


def test_duplicate_url_fails(write_readme, capsys):
    write_readme(
        """\
# My List

## Category A

- [Alpha](https://a.example/alpha)
- [Alpha copy](https://a.example/alpha)
"""
    )
    assert validate_readme.main() == 1
    assert "duplicate link (2x): https://a.example/alpha" in capsys.readouterr().out


def test_fragment_relative_and_schemeless_urls_fail(write_readme, capsys):
    write_readme(
        """\
# My List

## Category A

- [Fragment](#section)
- [Relative](/local/page)
- [No scheme](example.com/page)
"""
    )
    assert validate_readme.main() == 1
    out = capsys.readouterr().out
    assert "in-page fragment" in out
    assert "relative URL" in out
    assert "no URL scheme" in out


def test_malformed_link_fails(write_readme, capsys):
    write_readme(
        """\
# My List

## Category A

- [Broken](https://a.example/page
"""
    )
    assert validate_readme.main() == 1
    assert "malformed link" in capsys.readouterr().out
