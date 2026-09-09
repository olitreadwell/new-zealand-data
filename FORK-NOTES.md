# Fork notes

This is a fork of
[WikiNewZealand/new-zealand-data](https://github.com/WikiNewZealand/new-zealand-data),
a community list of New Zealand data and APIs.

## Why this fork exists

The upstream list is still one of the most useful indexes of NZ public data
I've found, but the repo has been quiet since March 2023 and links were
dying. This fork adds the maintenance the list needs: a weekly link check,
Wayback Machine archiving for every link, a CI pipeline, a searchable site,
and contributor docs.

## Upstream status

- The maintenance changes are offered upstream in
  [PR #26](https://github.com/WikiNewZealand/new-zealand-data/pull/26).
- The list lives under the `WikiNewZealand` org, which looks inactive;
  Figure.NZ's active org is `figurenz`. Whether the list stays there or
  moves is an open question.

## Governance

This fork is new and quiet. It is not a replacement for the upstream repo.
If the original maintainers want the changes, they are theirs to take.

## What's different

- `.github/workflows/linkcheck.yml` — weekly dead-link check that opens and
  closes a tracking issue.
- `.github/workflows/archive.yml` and `scripts/archive_links.py` — Wayback
  Machine archiving of every link.
- `.github/workflows/ci.yml` and `scripts/validate_readme.py` — README
  validation on every PR.
- `.github/workflows/pages.yml` and `scripts/build_site.py` — searchable
  GitHub Pages site generated from the README.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and a suggest-a-link issue form.
