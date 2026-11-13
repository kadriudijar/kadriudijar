# Project

## Purpose

The GitHub profile README of `kadriudijar`. It shows a pixel-art orca that a
nightly workflow redraws from the account's public GitHub activity. The idea
comes from git-koi (MIT).

## Architecture

One script, `orca.py`. It fetches data, derives signals, draws sprites,
writes a GIF and the activity card. A workflow runs it every night and commits
them only when they changed.

## Features

- **Orca GIF** — `orca/orca.gif`, 1024×512, 16 frames, looping.
  - Growth stage from lifetime contributions: calf < 500, juvenile < 3000,
    adult ≥ 3000.
  - The saddle patch takes the color of the top language by bytes in public,
    non-fork repositories. It is grey when there is none.
  - The pod: one calf per 4 weeks of the current weekly streak, max 2.
  - The behavior comes from the UTC day that just ended: rest (3+ quiet days),
    spyhop (first active day of the week), breach (≥ 5 and ≥ 2× the 28-day
    average), or cruise.
  - Key files: `orca.py`, `test_orca.py`.
- **Nightly redraw** — runs at 00:10 UTC, on manual dispatch, and on pushes
  that change `orca.py` or the workflow. Key file: `.github/workflows/orca.yml`.

- **Bonsai GIF** — `output/bonsai.gif`, beside the orca and linked to the
  git-bonsai playground. The `egorthinks/git-bonsai` Action (MIT, pinned to a
  commit) grows it in a read-only job; a second job with write access commits
  it only when it changed. It runs at 00:20 UTC so its push does not race the
  orca's. Key file: `.github/workflows/bonsai.yml`.

- **Activity card** — `cards/activity-{light,dark}.svg`, drawn by `orca.py` in
  the orca workflow from the contribution calendar, so it counts the private and
  org contributions the profile shares. It shows contributions all time and in
  the last 365 days, the current and longest weekly streak, and the best day.
  `github-readme-stats` is not used for this, because its commit count reads
  public commits only.
- **Languages card** — `cards/languages-{light,dark}.svg`. The
  `stats-organization/github-readme-stats-action` Action (pinned to v2.1.0)
  draws it in a read-only job; a second job commits it only when it changed.
  It runs at 00:30 UTC. Key file: `.github/workflows/cards.yml`.
- Both cards are picked by the viewer's color scheme.
- **Layout** — `README.md` puts the bonsai (28%) and the orca (66%) side by
  side at the same height, with the two cards top-aligned in a row below.

## Integrations

- GitHub GraphQL API, through the workflow's built-in token.
- `egorthinks/git-bonsai` GitHub Action for the bonsai, with a read-only token.
- `stats-organization/github-readme-stats-action` for the cards, with a read-only token.

## Key Decisions

- Python and Pillow with hand-drawn string sprites, not a fork of git-koi's
  Rust renderer. The project is for one profile, so the simpler build wins.
- The script reads only the first 100 public repositories for languages.
