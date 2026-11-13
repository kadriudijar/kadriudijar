# Project

## Purpose

The GitHub profile README of `kadriudijar`. It shows a pixel-art night skyline
that grows with the account's GitHub activity, with an activity card and a
contribution breakdown card below it. A nightly workflow redraws all three.

## Architecture

One script, `skyline.py`. It fetches the contribution calendar and search
counts, draws the skyline GIF and both cards, and a workflow runs it every
night and commits them only when they changed.

## Features

- **Skyline GIF** — `skyline/skyline.gif`, 1024×416 (256×104 pixel art scaled
  4×), 16 frames, looping, full README width.
  - One building per Monday–Sunday week for the last 48 weeks, oldest on the
    left. Its height is the square root of the week's share of the busiest
    week, so quiet weeks still read; an empty week is a low shed.
  - The current week is scaffolding with a crane, and it rises as the week's
    contributions come in.
  - The tallest finished week has a blinking red beacon. Windows light up at
    random and a few flicker; stars twinkle; a crescent moon sits top left.
  - A two-line caption under the GIF in `README.md` explains how to read it.
- **Activity card** — `cards/activity-{light,dark}.svg`, from the contribution
  calendar, so it counts the private and org contributions the profile shares:
  contributions all time and in the last 365 days, the current and longest
  weekly streak, and the best day.
- **Breakdown card** — `cards/breakdown-{light,dark}.svg`: all-time commits,
  pull requests (with how many merged), code reviews on others' pull requests,
  and issues, as a bar and one row each. The counts come from GitHub search,
  because the contribution calendar reports private org work only as an
  untyped "restricted" total. Private repositories count through the
  `ORCA_TOKEN` secret. Commit search covers default branches only.
- Both cards sit top-aligned in a row below the skyline and follow the
  viewer's color scheme.
- **Nightly redraw** — runs at 00:10 UTC, on manual dispatch, and on pushes
  that change `skyline.py` or the workflow.
- Key files: `skyline.py`, `test_skyline.py`,
  `.github/workflows/skyline.yml`, `README.md`.

## Integrations

- GitHub GraphQL and search APIs. The workflow uses the `ORCA_TOKEN` secret (a
  classic token with `repo` scope, covering every organization; the name dates
  from the earlier orca) and falls back to the built-in token without it.

## Key Decisions

- Python and Pillow, drawn pixel by pixel. The project is for one profile, so
  the simplest build wins.
- A skyline instead of the earlier orca: it shows the amount of work week by
  week, like a chart that does not look like one.
- Own cards instead of `github-readme-stats`: its counts read public data
  only, and most of the work is in private org repositories.
