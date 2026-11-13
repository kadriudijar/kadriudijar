# Project

## Purpose

The GitHub profile README of `kadriudijar`. It shows a pixel-art orca that a
nightly workflow redraws from the account's GitHub activity, with an activity
card and a languages card below it. The idea comes from git-koi (MIT).

## Architecture

One script, `orca.py`. It fetches data, derives signals, draws sprites, and
writes the GIF and both cards. A workflow runs it every night and commits them
only when they changed.

## Features

- **Orca GIF** — `orca/orca.gif`, 1024×512, 16 frames, looping, full README
  width.
  - Growth stage from lifetime contributions: calf < 500, juvenile < 3000,
    adult ≥ 3000.
  - The saddle patch takes the color of the top language on the languages
    card. It is grey when there is none.
  - The pod: one calf per 4 weeks of the current weekly streak, max 2.
  - The behavior comes from the UTC day that just ended: rest (3+ quiet days),
    spyhop (first active day of the week), breach (≥ 5 and ≥ 2× the 28-day
    average), or cruise.
- **Activity card** — `cards/activity-{light,dark}.svg`, from the contribution
  calendar, so it counts the private and org contributions the profile shares:
  contributions all time and in the last 365 days, the current and longest
  weekly streak, and the best day.
- **Languages card** — `cards/languages-{light,dark}.svg`: the top six
  languages by repository count, from the main language of each non-fork
  repository the account owns or has contributed to. Private org repositories
  count only when the `ORCA_TOKEN` secret is set.
- Both cards sit top-aligned in a row below the orca and follow the viewer's
  color scheme.
- **Nightly redraw** — runs at 00:10 UTC, on manual dispatch, and on pushes
  that change `orca.py` or the workflow.
- Key files: `orca.py`, `test_orca.py`, `.github/workflows/orca.yml`,
  `README.md`.

## Integrations

- GitHub GraphQL API. The workflow uses the `ORCA_TOKEN` secret (a personal
  token with `repo` scope) when it exists, and the built-in token otherwise.

## Key Decisions

- Python and Pillow with hand-drawn string sprites, not a fork of git-koi's
  Rust renderer. The project is for one profile, so the simpler build wins.
- Own cards instead of `github-readme-stats`: its commit count and languages
  read public data only, and most of the work is in private org repositories.
- The script reads the first 100 owned and 100 contributed repositories for
  languages.
