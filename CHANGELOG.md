# Changelog

All notable changes to this fork are documented here. The fork tracks
[WikiNewZealand/new-zealand-data](https://github.com/WikiNewZealand/new-zealand-data),
which is dormant since March 2023. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Wayback Machine archiving: `.github/workflows/archive.yml` runs
  `scripts/archive_links.py` weekly, dedupes against the CDX index, and
  uploads `wayback-report.json` as an artifact.
- Link check now also runs on every pull request, so dead links surface as a
  failed check instead of waiting for the weekly run.
- `.lycheeignore` keeps known false positives (mailto, localhost, example.com)
  out of link-check reports.
- `FORK-NOTES.md`: why the fork exists, upstream status, governance stance.
- `CHANGELOG.md`.

### Changed

- `scripts/build_site.py` and the README point at the fork instead of
  upstream, so the Pages site links back to the repo that builds it.
- README documents the maintenance tooling under "How it's maintained".

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
