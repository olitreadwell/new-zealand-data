"""Shared fixtures and import setup for the scripts test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def write_readme(tmp_path, monkeypatch):
    """Write a fake README.md into tmp_path and point the scripts at it."""

    def _write(content: str) -> Path:
        path = tmp_path / "README.md"
        path.write_text(content, encoding="utf-8")
        import archive_links
        import validate_readme

        monkeypatch.setattr(validate_readme, "README_PATH", path)
        monkeypatch.setattr(archive_links, "README_PATH", path)
        return path

    return _write
