# Contributing

Thanks for helping keep this list of New Zealand data and APIs useful. There
are two ways to contribute: open an issue (no coding needed) or open a pull
request.

## Option 1: suggest a link via issue

Use the [suggest-a-link issue form](../../issues/new?template=add-link.yml).
Fill in what you know. Someone will verify it and add it as a pull request.

## Option 2: add a link via pull request

### 1. Edit README.md

Find the section that fits and add your link as a bullet:

```markdown
- [Name](https://example.govt.nz) - one-line description of what it is
```

If the link belongs to a group (for example an agency with several
datasets), add it as an indented bullet under the group name.

### 2. Verify, don't invent

Every link must resolve to a live page. Open it and check before submitting.
If a link is dead, open a pull request to remove or fix it rather than
leaving it in the list.

### 3. Check the link locally (optional)

If you have [lychee](https://github.com/lycheeverse/lychee) installed:

```bash
lychee README.md
```

### 4. Open a pull request

Include what you verified and how in the PR description.

## How links are maintained

The [weekly link check workflow](.github/workflows/linkcheck.yml) checks every
link in `README.md` once a week. If it finds genuinely dead links (404, DNS
failure, refused connection) it opens a tracking issue and keeps it updated;
when the links recover, the issue closes automatically. Bot-blocked links
(403 / 999, common for LinkedIn) are not treated as failures.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) style, plain
language, one idea per line:

```
feat: add Stats NZ API link

- Added the Stats NZ API under Central Government & Agencies, verified
  against stats.govt.nz.
```

Don't add a `Co-Authored-By` trailer for AI tools: the tool is a
facilitator, not a co-author.
