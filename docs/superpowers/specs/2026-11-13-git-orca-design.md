# Git orca — design

## Intent

A pixel-art orca on the GitHub profile README of `kadriudijar`, redrawn every
night from public activity. It is inspired by git-koi (MIT) but is for one
person only.

## Goals

- One looping GIF, `orca/orca.gif`, shown on the profile README.
- Activity drives the orca the way git-koi drives its koi: size, color,
  streak, and the day's behavior.
- A nightly GitHub Actions workflow redraws it and commits only on change.

## Non-goals

- CLI, library, releases, crate or package publishing, docs site.
- Several body variants. The orca has one black-and-white body.
- Private contributions. Only what the built-in token can read.

## Approaches

- **A. Fork git-koi and redraw it in Rust.** Most faithful, but it means a
  rewrite of about 105 KB of procedural koi drawing code and a Rust codebase
  made for a public crate.
- **B. Small Python + Pillow script with hand-drawn sprites (chosen).** About
  200–300 lines. Growth is in stages, not continuous. Sprites make a
  recognisable orca more easily than procedural drawing.
- **C. git-koi's collector plus our own renderer.** Dropped: it couples us to
  their snapshot format and still needs a full renderer.

## Design

Repository: `kadriudijar/kadriudijar` (the profile repo; it does not exist
yet).

```
orca.py                 fetch, signals, drawing, GIF
test_orca.py            asserts for the signal rules
.github/workflows/orca.yml
orca/orca.gif           output, committed by the workflow
README.md               <img src="orca/orca.gif" width="256">
```

**Data.** GitHub GraphQL with `GITHUB_TOKEN`: the contribution calendar for
every year in `contributionYears` (lifetime total and daily counts), and the
languages of the user's public, non-fork repositories, weighted by bytes.

**Signals (my calls, easy to tune):**

| Signal | Source | Effect |
| --- | --- | --- |
| Growth stage | lifetime total | calf < 500, juvenile < 3000, adult ≥ 3000 |
| Accent color | top language color | fills the grey saddle patch behind the dorsal fin |
| Pod | current weekly streak (Mon–Sun weeks with ≥ 1 contribution) | one small calf swims alongside per 4 weeks, max 2 |
| Behavior | the UTC day that just ended | first rule wins, below |

Behavior rules:

1. **Rest** — 3 or more quiet days in a row: the orca logs at the surface and
   bobs slowly.
2. **Spyhop** — first active day of its Mon–Sun week: the head rises out of the
   water and looks around.
3. **Breach** — the day's count is at least twice the daily average of the
   previous 28 days, and at least 5: the orca jumps out with a splash.
4. **Cruise** — anything else: a steady swim with tail strokes.

**Drawing.** Sprites are pixel grids written as strings in `orca.py`, one
character per palette color, so they are easy to read and change. The canvas
is 128×64 pixels on a deep-water background, so the black orca stays visible
in dark mode. Each frame is scaled 2× (256×128) with nearest-neighbour
scaling. A loop has about 8–16 frames.

**Workflow.** It runs at 00:10 UTC, on `workflow_dispatch`, and on a push that
changes `orca.py` or the workflow. Steps: set up Python, `pip install pillow`,
run `python orca.py`, and commit `orca/orca.gif` only when it changed.

**Checks.** `test_orca.py` covers stage, streak, and behavior rules with fixed
day lists. A local run renders the GIF so it can be looked at before pushing.

## Left to the builder

- Exact sprite pixels and animation frames.
- Palette shades.
