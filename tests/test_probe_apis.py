"""Tests for scripts/probe_apis.py with urllib mocked."""

import json
import sys
import urllib.error
import urllib.request
from unittest import mock

import pytest

import probe_apis


class FakeResponse:
    """Minimal stand-in for a urllib response object."""

    def __init__(self, status: int = 200, content_type: str = "application/json"):
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def make_http_error(url: str, code: int) -> urllib.error.HTTPError:
    """Build an HTTPError with the given status code and no body."""
    return urllib.error.HTTPError(url, code, "error", {"Content-Type": "text/html"}, None)


def run_main(monkeypatch, argv: list[str], report_dir) -> int:
    """Run probe_apis.main() with controlled argv and report path."""
    monkeypatch.setattr(sys, "argv", ["probe_apis.py", *argv])
    monkeypatch.setattr(probe_apis, "REPORT_PATH", report_dir / "api-probe-report.json")
    return probe_apis.main()


def test_is_api_entry_detects_api_in_text() -> None:
    assert probe_apis.is_api_entry("Digital NZ API", "", "http://digitalnz.org/developers")


def test_is_api_entry_excludes_non_api() -> None:
    assert not probe_apis.is_api_entry("Metlink Realtime Data (non-API)", "", "http://www.metlink.org.nz/")


def test_is_api_entry_detects_url_hints() -> None:
    assert probe_apis.is_api_entry("REC v2.0 (OGC WMS)", "", "http://gs.niwa.co.nz/rec/wms")
    assert not probe_apis.is_api_entry("NZ.Stat", "primary point of access", "http://nzdotstat.stats.govt.nz/wbos/Index.aspx")


def test_collect_api_urls_filters_and_dedupes_real_readme() -> None:
    pairs = probe_apis.collect_api_urls()
    urls = [url for _, url in pairs]
    assert "Digital NZ API" in [name for name, _ in pairs]
    assert "Metlink Realtime Data (non-API)" not in [name for name, _ in pairs]
    assert len(urls) == len(set(urls))


def test_probe_url_success(monkeypatch) -> None:
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse(200, "application/json"))
    record = probe_apis.probe_url("Example API", "https://example.com/api")
    assert record["status"] == 200
    assert record["content_type"] == "application/json"
    assert record["error"] is None
    assert record["bot_blocked"] is False
    assert record["latency_ms"] >= 0


def test_probe_url_http_500_is_hard_fail(monkeypatch) -> None:
    def raise_500(*args, **kwargs):
        raise make_http_error("https://example.com/api", 500)

    monkeypatch.setattr(urllib.request, "urlopen", raise_500)
    record = probe_apis.probe_url("Example API", "https://example.com/api")
    assert record["status"] == 500
    assert record["error"] is None
    assert record["bot_blocked"] is False
    assert probe_apis.is_hard_fail(record) is True


@pytest.mark.parametrize("code", [403, 999])
def test_probe_url_bot_block_is_not_hard_fail(monkeypatch, code: int) -> None:
    def raise_blocked(*args, **kwargs):
        raise make_http_error("https://example.com/api", code)

    monkeypatch.setattr(urllib.request, "urlopen", raise_blocked)
    record = probe_apis.probe_url("Example API", "https://example.com/api")
    assert record["status"] == code
    assert record["bot_blocked"] is True
    assert probe_apis.is_hard_fail(record) is False


def test_probe_url_dns_error_is_hard_fail(monkeypatch) -> None:
    def raise_dns(*args, **kwargs):
        raise urllib.error.URLError("Name or service not known")

    monkeypatch.setattr(urllib.request, "urlopen", raise_dns)
    record = probe_apis.probe_url("Example API", "https://example.com/api")
    assert record["status"] is None
    assert record["error"] == "Name or service not known"
    assert probe_apis.is_hard_fail(record) is True


def test_probe_url_timeout_is_hard_fail(monkeypatch) -> None:
    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", raise_timeout)
    record = probe_apis.probe_url("Example API", "https://example.com/api")
    assert record["status"] is None
    assert record["error"] == "timed out"
    assert probe_apis.is_hard_fail(record) is True


def test_main_dry_run_does_not_probe(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(probe_apis, "collect_api_urls", lambda: [("A", "https://a.example/api"), ("B", "https://b.example/api")])
    urlopen = mock.Mock(return_value=FakeResponse())
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    exit_code = run_main(monkeypatch, ["--dry-run"], tmp_path)
    assert exit_code == 0
    assert urlopen.called is False
    assert not (tmp_path / "api-probe-report.json").exists()


def test_main_limit_caps_probes(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        probe_apis,
        "collect_api_urls",
        lambda: [("A", f"https://a.example/{i}/api") for i in range(3)],
    )
    urlopen = mock.Mock(return_value=FakeResponse())
    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    exit_code = run_main(monkeypatch, ["--limit", "2"], tmp_path)
    assert exit_code == 0
    assert urlopen.call_count == 2
    report = json.loads((tmp_path / "api-probe-report.json").read_text(encoding="utf-8"))
    assert len(report) == 2


def test_main_writes_report_and_exits_zero(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(probe_apis, "collect_api_urls", lambda: [("A", "https://a.example/api")])
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse(200, "application/json"))
    exit_code = run_main(monkeypatch, [], tmp_path)
    assert exit_code == 0
    report = json.loads((tmp_path / "api-probe-report.json").read_text(encoding="utf-8"))
    assert report[0]["status"] == 200
    assert report[0]["content_type"] == "application/json"
    assert report[0]["latency_ms"] >= 0


def test_main_exits_nonzero_on_hard_fail(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(probe_apis, "collect_api_urls", lambda: [("A", "https://a.example/api")])

    def raise_500(*args, **kwargs):
        raise make_http_error("https://a.example/api", 500)

    monkeypatch.setattr(urllib.request, "urlopen", raise_500)
    exit_code = run_main(monkeypatch, [], tmp_path)
    assert exit_code == 1
    report = json.loads((tmp_path / "api-probe-report.json").read_text(encoding="utf-8"))
    assert report[0]["status"] == 500
