# Changelog

All notable changes to this fork are documented here. The fork tracks
[WikiNewZealand/new-zealand-data](https://github.com/WikiNewZealand/new-zealand-data),
which is dormant since March 2023. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Pytest test suite for the maintenance scripts: `tests/` covers the README
  parser helpers in `scripts/build_site.py`, the checks in
  `scripts/validate_readme.py`, and URL collection in
  `scripts/archive_links.py`. `make test` runs it, `make check` includes it,
  and a CI job runs it on every pull request.
- Site exports: Atom feed `site/feed.xml` with the latest 20 entries and
  RFC 3339 timestamps, per-entry Dataset JSON-LD in `index.html`, and
  optional `license`/`format`/`update_frequency` fields in `data.json` /
  `data.csv` (null by default).
- Wayback Machine fallback links on entries that could not be archived,
  when `wayback-report.json` is present.
- pytest suite in `tests/` covering the site builder.
- API probes: `.github/workflows/api-probes.yml` runs `scripts/probe_apis.py`
  weekly, GETs the API-ish endpoints listed in the README, and uploads
  `api-probe-report.json` as an artifact.
- Pull request previews: PRs that touch the README or the site build deploy
  a temporary GitHub Pages preview and post its URL as a comment on the PR.
- Wayback Machine archiving: `.github/workflows/archive.yml` runs
  `scripts/archive_links.py` weekly, dedupes against the CDX index, and
  uploads `wayback-report.json` as an artifact.
- Link check now also runs on every pull request, so dead links surface as a
  failed check instead of waiting for the weekly run.
- `.lycheeignore` keeps known false positives (mailto, localhost, example.com)
  out of link-check reports.
- Broken-link issue form for structured dead-link reports.
- README workflow status badges.
- `Makefile` with a single `make check` entry point (validate, build, link
  check, workflow lint) and an actionlint job in CI.
- Dependabot groups GitHub Actions minor/patch updates into one PR.
- `FORK-NOTES.md`: why the fork exists, upstream status, governance stance.
- `CHANGELOG.md`.

### Changed

- `scripts/build_site.py` and the README point at the fork instead of
  upstream, so the Pages site links back to the repo that builds it.
- README documents the maintenance tooling under "How it's maintained".

### Fixed

- Site link counter now counts entries, not containers, so it matches the
  real total.
- Doc sections (Browse the site, Contributing, How it's maintained) no longer
  count as categories and hide during search.
- Theme applies before first paint, so no light-mode flash for dark-mode
  users.
- Markdown links in notes no longer double-escape `&` in URLs.

## [0.1.0] - 2026-08-25

Fork maintenance baseline, also proposed upstream in
[PR #26](https://github.com/WikiNewZealand/new-zealand-data/pull/26).

### Added

- CI: `scripts/validate_readme.py` + `scripts/build_site.py` on every PR and
  push to the default branch.
- Weekly link check with a self-opening/self-closing tracking issue.
- Searchable GitHub Pages site generated from the README.
- Stale issue/PR cleanup and Dependabot.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and the suggest-a-link issue form.

### Fixed

- Broken markdown links in the README.
- lychee v0.24 release archive extraction.
- Tracking issue now skips repos with issues disabled.
- Action and setup-python major version bumps.
