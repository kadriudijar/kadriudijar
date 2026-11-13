"""Draw a pixel-art city skyline from a GitHub account's activity, as a looping GIF, plus two cards."""

import json
import math
import os
import random
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

from PIL import Image

# ---------- signals ----------

WEEKS = 48  # one building per Monday-Sunday week; the last one is the week in progress


def weekly_totals(days, today, count=WEEKS):
    """Contributions per Monday-Sunday week, oldest first, ending with the week that holds today."""
    monday = today - timedelta(today.weekday())
    weeks = [monday - timedelta(7 * n) for n in range(count - 1, -1, -1)]
    return [sum(days.get(week + timedelta(d), 0) for d in range(7) if week + timedelta(d) <= today) for week in weeks]


def building_heights(totals, tallest=72):
    """Square-root scale against the busiest week, so quiet weeks still read; an empty week is a 3 px shed."""
    peak = max(totals, default=0) or 1
    return [3 if n == 0 else 6 + round((tallest - 6) * math.sqrt(n / peak)) for n in totals]


def weekly_streak(days, today):
    """Consecutive Monday-Sunday weeks with activity; the unfinished current week cannot end it."""
    active = {d - timedelta(d.weekday()) for d, n in days.items() if n and d <= today}
    week = today - timedelta(today.weekday())
    streak = 0
    if week in active:
        streak += 1
    week -= timedelta(7)
    while week in active:
        streak += 1
        week -= timedelta(7)
    return streak


def longest_weekly_streak(days, today):
    weeks = sorted({d - timedelta(d.weekday()) for d, n in days.items() if n and d <= today})
    longest = run = 0
    for i, week in enumerate(weeks):
        run = run + 1 if i and week - weeks[i - 1] == timedelta(7) else 1
        longest = max(longest, run)
    return longest


# ---------- drawing ----------

W, H, SCALE, GROUND, FRAMES = 256, 104, 4, 96, 16
SKY_TOP, SKY_LOW, EARTH = (8, 12, 30), (34, 44, 88), (18, 20, 28)
BODIES = [(40, 50, 75), (48, 58, 86), (34, 44, 68)]
LIGHT, STAR, MOON = (255, 214, 120), (220, 228, 255), (240, 236, 210)
SCAFFOLD, CRANE, BEACON = (120, 104, 72), (236, 184, 40), (255, 70, 60)


def render(totals):
    rng = random.Random(len(totals))  # the layout of stars, shades and windows stays put from night to night
    heights = building_heights(totals)
    stars = [(rng.randrange(W), rng.randrange(GROUND - 30)) for _ in range(60)]
    shades = [rng.choice(BODIES) for _ in totals]
    windows = {}  # (building, row, column) -> (lit, flickers)
    tallest = max(range(len(heights) - 1), key=lambda i: heights[i], default=0)
    frames = []
    for f in range(FRAMES):
        phase = f * 2 * math.pi / FRAMES
        image = Image.new("RGB", (W, H), EARTH)
        px = image.load()
        for y in range(GROUND):
            t = y / GROUND
            row = tuple(round(a + (b - a) * t) for a, b in zip(SKY_TOP, SKY_LOW))
            for x in range(W):
                px[x, y] = row
        for i, (x, y) in enumerate(stars):
            if (i + f) % 7:  # each star blinks out one frame in seven
                px[x, y] = STAR
        for dx in range(-6, 7):
            for dy in range(-6, 7):
                if dx * dx + dy * dy <= 30 and (dx + 2) ** 2 + (dy + 1) ** 2 > 22:  # a crescent
                    px[24 + dx, 14 + dy] = MOON
        for i, h in enumerate(heights):
            x, top = 8 + i * 5, GROUND - h
            if i == len(heights) - 1:  # the week in progress: scaffolding and a crane
                for y in range(top, GROUND):
                    px[x, y] = px[x + 3, y] = SCAFFOLD
                    if (GROUND - y) % 3 == 0:
                        px[x + 1, y] = px[x + 2, y] = SCAFFOLD
                mast = top - 16
                for y in range(mast, top):
                    px[x + 3, y] = CRANE
                for ax in range(x - 12, x + 7):
                    px[ax, mast] = CRANE
                swing = round(2 * math.sin(phase))
                for y in range(mast + 1, mast + 7 + round(2 * math.sin(phase * 2))):
                    px[x - 8 + swing, y] = CRANE
                continue
            for y in range(top, GROUND):
                for dx in range(4):
                    px[x + dx, y] = shades[i]
            for y in range(top + 2, GROUND - 1, 2):
                for dx in (1, 2):
                    lit, flickers = windows.setdefault((i, y, dx), (rng.random() < 0.4, rng.random() < 0.08))
                    if lit != (flickers and (f // 4 + i) % 2 == 1):
                        px[x + dx, y] = LIGHT
            if i == tallest and f % 8 < 4:
                px[x + 1, top - 2] = px[x + 2, top - 2] = BEACON
            if i == tallest:
                px[x + 1, top - 1] = px[x + 2, top - 1] = shades[i]
        frames.append(image.resize((W * SCALE, H * SCALE), Image.NEAREST))
    return frames


def save_gif(frames, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    temporary = path + ".tmp"
    frames[0].save(temporary, format="GIF", save_all=True, append_images=frames[1:], duration=140, loop=0)
    os.replace(temporary, path)  # a failed run keeps the previous GIF


# ---------- activity card ----------


def activity_svg(login, days, today, dark):
    """A 400x195 card from the contribution calendar, which counts the private and org work the profile shares."""
    past = {d: n for d, n in days.items() if d <= today}
    best = max(past.items(), key=lambda item: (item[1], item[0]), default=(today, 0))
    weeks = lambda n: f"{n} week" + ("" if n == 1 else "s")
    rows = [
        ("Contributions (all time)", f"{sum(past.values()):,}"),
        ("Contributions (last year)", f"{sum(n for d, n in past.items() if d > today - timedelta(365)):,}"),
        ("Current weekly streak", weeks(weekly_streak(days, today))),
        ("Longest weekly streak", weeks(longest_weekly_streak(days, today))),
        ("Best day", f"{best[1]} on {best[0]}"),
    ]
    title, text = ("#6fb7e0", "#c9d1d9") if dark else ("#0b4f7c", "#1f2328")
    lines = "".join(
        f'<text x="25" y="{82 + i * 25}">{label}:</text><text x="375" y="{82 + i * 25}" text-anchor="end" font-weight="700">{value}</text>'
        for i, (label, value) in enumerate(rows)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="195" viewBox="0 0 400 195" '
        "font-family=\"'Segoe UI', Ubuntu, Sans-Serif\">"
        f'<text x="25" y="35" font-size="18" font-weight="600" fill="{title}">{login}\'s GitHub activity</text>'
        f'<g font-size="14" fill="{text}">{lines}</g></svg>'
    )


BREAKDOWN_COLORS = {"commits": "#2da44e", "prs": "#8250df", "reviews": "#bf8700", "issues": "#1a7fbf"}


def breakdown_svg(breakdown, dark):
    """A 400x195 card: all-time commits, pull requests, reviews and issues, as a bar and one row each."""
    rows = [
        ("commits", "Commits", f"{breakdown['commits']:,}"),
        ("prs", "Pull requests", f"{breakdown['prs']:,} ({breakdown['merged']:,} merged)"),
        ("reviews", "Code reviews", f"{breakdown['reviews']:,}"),
        ("issues", "Issues", f"{breakdown['issues']:,}"),
    ]
    total = sum(breakdown[key] for key, _, _ in rows) or 1
    title, text = ("#6fb7e0", "#c9d1d9") if dark else ("#0b4f7c", "#1f2328")
    bar, x, lines = "", 25.0, ""
    for i, (key, label, value) in enumerate(rows):
        width, color, y = 350 * breakdown[key] / total, BREAKDOWN_COLORS[key], 100 + i * 25
        bar += f'<rect x="{x:.1f}" y="55" width="{width:.1f}" height="10" fill="{color}"/>'
        x += width
        lines += (
            f'<circle cx="30" cy="{y - 5}" r="5" fill="{color}"/><text x="43" y="{y}">{label}:</text>'
            f'<text x="375" y="{y}" text-anchor="end" font-weight="700">{value}</text>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="195" viewBox="0 0 400 195" '
        "font-family=\"'Segoe UI', Ubuntu, Sans-Serif\">"
        f'<text x="25" y="35" font-size="18" font-weight="600" fill="{title}">Contribution breakdown</text>'
        f'<clipPath id="bar"><rect x="25" y="55" width="350" height="10" rx="5"/></clipPath>'
        f'<g clip-path="url(#bar)">{bar}</g>'
        f'<g font-size="14" fill="{text}">{lines}</g></svg>'
    )


# ---------- GitHub ----------


def graphql(token, query, **variables):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-skyline"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch_breakdown(login, token):
    """All-time counts from search over every repository the token can read. Commit search covers default branches only."""
    counts = graphql(
        token,
        """query($prs: String!, $merged: String!, $reviews: String!, $issues: String!) {
          prs: search(type: ISSUE, query: $prs, first: 0) { issueCount }
          merged: search(type: ISSUE, query: $merged, first: 0) { issueCount }
          reviews: search(type: ISSUE, query: $reviews, first: 0) { issueCount }
          issues: search(type: ISSUE, query: $issues, first: 0) { issueCount } }""",
        prs=f"author:{login} is:pr",
        merged=f"author:{login} is:pr is:merged",
        reviews=f"reviewed-by:{login} is:pr -author:{login}",
        issues=f"author:{login} is:issue",
    )
    request = urllib.request.Request(
        "https://api.github.com/search/commits?per_page=1&q=" + urllib.parse.quote(f"author:{login}"),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-skyline", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        commits = json.load(response)["total_count"]
    return {"commits": commits, **{key: value["issueCount"] for key, value in counts.items()}}


def fetch(login, token):
    """Daily contributions for every year since the account started."""
    years = graphql(
        token,
        "query($login: String!) { user(login: $login) { contributionsCollection { contributionYears } } }",
        login=login,
    )["user"]["contributionsCollection"]["contributionYears"]
    days = {}
    for year in years:
        calendar = graphql(
            token,
            """query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
              contributionsCollection(from: $from, to: $to) { contributionCalendar {
                weeks { contributionDays { date contributionCount } } } } } }""",
            login=login,
            **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"},
        )["user"]["contributionsCollection"]["contributionCalendar"]
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                days[date.fromisoformat(day["date"])] = day["contributionCount"]
    return days


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN or GH_TOKEN.")
    login = os.environ.get("PROFILE_LOGIN", "kadriudijar")
    days = fetch(login, token)
    breakdown = fetch_breakdown(login, token)
    today = datetime.now(timezone.utc).date() - timedelta(1)  # the UTC day that just ended
    totals = weekly_totals(days, today)
    print(f"weeks={totals[-8:]} breakdown={breakdown}")
    save_gif(render(totals), "skyline/skyline.gif")
    os.makedirs("cards", exist_ok=True)
    for theme in ("light", "dark"):
        with open(f"cards/activity-{theme}.svg", "w") as file:
            file.write(activity_svg(login, days, today, dark=theme == "dark"))
        with open(f"cards/breakdown-{theme}.svg", "w") as file:
            file.write(breakdown_svg(breakdown, dark=theme == "dark"))


if __name__ == "__main__":
    main()
