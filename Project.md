# Project

## Purpose

The GitHub profile README of `kadriudijar`. It shows a pixel-art orca that a
nightly workflow redraws from the account's public GitHub activity. The idea
comes from git-koi (MIT).

## Architecture

One script, `orca.py`. It fetches data, derives signals, draws sprites, and
writes a GIF. A workflow runs it every night and commits the GIF only when it
changed.

## Features

- **Orca GIF** — `orca/orca.gif`, 1024×512, 16 frames, shown at full README width, looping.
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

## Integrations

- GitHub GraphQL API, through the workflow's built-in token.

## Key Decisions

- Python and Pillow with hand-drawn string sprites, not a fork of git-koi's
  Rust renderer. The project is for one profile, so the simpler build wins.
- The script reads only the first 100 public repositories for languages.
