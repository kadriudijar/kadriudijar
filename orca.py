"""Draw a pixel-art orca from a GitHub account's public activity, as a looping GIF."""

import json
import math
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone

from PIL import Image

# ---------- signals ----------

GREY = "#8a8a8a"


def stage(total):
    return "calf" if total < 500 else "juvenile" if total < 3000 else "adult"


def pod_size(streak_weeks):
    return min(streak_weeks // 4, 2)


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


def behavior(days, today):
    count = lambda d: days.get(d, 0)
    quiet = 0
    while quiet < 3 and count(today - timedelta(quiet)) == 0:
        quiet += 1
    if quiet >= 3:
        return "rest"
    monday = today - timedelta(today.weekday())
    if count(today) and not any(count(monday + timedelta(n)) for n in range(today.weekday())):
        return "spyhop"
    average = sum(count(today - timedelta(n)) for n in range(1, 29)) / 28
    if count(today) >= 5 and count(today) >= 2 * average:
        return "breach"
    return "cruise"


def top_color(languages):
    if not languages:
        return GREY
    color, _ = max(languages.values(), key=lambda v: v[1])
    return color or GREY


# ---------- drawing ----------

# Adult orca facing right. K black, W white, S saddle (language color), E eye.
ORCA = """
.........................KK.........................
........................KKK.........................
.......................KKKK.........................
......................KKKKK.........................
.....................KKKKKK.........................
....................KKKKKKK.........................
...................KKKKKKKK.........................
..............KKKKKKKKKKKKKKKKKKKKKKKKKK............
...........KKKKKKSSSSSSSKKKKKKKKKKKKKKKKKKKKK.......
KK.......KKKKKKKKKSSSSSKKKKKKKKKKKKKKKKKKWWWWKKK....
KKK....KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKWWWWKKKK..
.KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK.
..KKKKKKKKKKKWWWKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
.KKKKKKKKKKWWWWWWWKKKKKKKKKKKKKKKKKKKKKKKKKKKKWWWWW.
KKK....KKKKKWWWWWWKKKKKKKKKKKKKKKKKKKKKKKWWWWWWWWW..
KK.......KKKKKKKKKKKKKKKKKKWWWWWWWWWWWWWWWWWWWWWW...
.............KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK.....
.............................KKKKK..................
..............................KKKK..................
................................KK..................
""".strip().splitlines()

SKY, SURFACE, FOAM = (24, 52, 84), (64, 140, 190), (200, 230, 245)
WATER_TOP, WATER_BOTTOM = (12, 80, 124), (5, 32, 58)
WATERLINE, W, H, SCALE = 24, 128, 64, 8
SIZES = {"calf": 0.5, "juvenile": 0.75, "adult": 1.0}
FRAMES = 16


def orca_sprite(color, flex=0.0, size=1.0):
    """The orca as an RGBA image; flex bends the tail up (-) or down (+)."""
    rgb = {"K": (10, 10, 14), "W": (240, 244, 248), "S": color}
    width, height = max(map(len, ORCA)), len(ORCA)
    image = Image.new("RGBA", (width, height + 4), (0, 0, 0, 0))
    for y, row in enumerate(ORCA):
        for x, c in enumerate(row):
            if c in rgb:
                shift = round(flex * max(0, 14 - x) / 14 * 2)  # only the tail stock and flukes move
                image.putpixel((x, y + 2 + shift), rgb[c] + (255,))
    if size != 1.0:
        image = image.resize((max(1, round(image.width * size)), max(1, round(image.height * size))), Image.NEAREST)
    return image


def background(frame):
    image = Image.new("RGB", (W, H), SKY)
    for y in range(WATERLINE, H):
        t = (y - WATERLINE) / (H - WATERLINE)
        color = tuple(round(a + (b - a) * t) for a, b in zip(WATER_TOP, WATER_BOTTOM))
        for x in range(W):
            image.putpixel((x, y), color)
    for x in range(W):  # a slow wave along the surface
        wave = round(math.sin((x / 9) + frame * 2 * math.pi / FRAMES))
        image.putpixel((x, WATERLINE + wave), SURFACE)
        if (x + frame * 2) % 23 == 0:
            image.putpixel((x, WATERLINE + wave - 1), FOAM)
    return image


def paste(scene, sprite, cx, cy, above_water=True):
    """Paste centred at (cx, cy); with above_water False, anything above the waterline is hidden."""
    x, y = round(cx - sprite.width / 2), round(cy - sprite.height / 2)
    if not above_water and y < WATERLINE + 1:
        sprite = sprite.crop((0, WATERLINE + 1 - y, sprite.width, sprite.height))
        y = WATERLINE + 1
    scene.paste(sprite, (x, y), sprite)


def splash(scene, cx, strength):
    for n in range(strength):
        for side in (-1, 1):
            x, y = round(cx + side * (2 + n * 1.5)), WATERLINE - 1 - (n * (strength - n)) // 2
            if 0 <= x < W and 0 <= y < H:
                scene.putpixel((x, y), FOAM)


def render(stage_name, color, pod, behavior_name):
    rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
    size = SIZES[stage_name]
    frames = []
    for f in range(FRAMES):
        phase = f * 2 * math.pi / FRAMES
        scene = background(f)
        for p in range(pod):  # calves trail behind and below
            calf = orca_sprite(rgb, math.sin(phase * 2 + p), size * 0.45)
            paste(scene, calf, 34 - p * 20, 54 + p * 4 + math.sin(phase + p))
        if behavior_name == "cruise":
            paste(scene, orca_sprite(rgb, math.sin(phase * 2), size), 78, 40 + 2 * math.sin(phase))
        elif behavior_name == "rest":
            orca = orca_sprite(rgb, 0.3 * math.sin(phase), size)
            paste(scene, orca, 66, WATERLINE + orca.height * 0.12 + math.sin(phase))
        elif behavior_name == "spyhop":
            orca = orca_sprite(rgb, 0, size).rotate(90, expand=True)
            paste(scene, orca, 72, WATERLINE + orca.height * 0.35 + 2 * math.sin(phase))
            splash(scene, 72, 2)
        else:  # breach: one arc out of the water and back in
            t = f / (FRAMES - 1)
            cx, cy = 26 + 76 * t, WATERLINE + 28 - 4 * (WATERLINE + 18) * t * (1 - t)
            angle = math.degrees(math.atan2(4 * (WATERLINE + 18) * (1 - 2 * t), 76))
            orca = orca_sprite(rgb, 0.5 * math.sin(phase * 2), size).rotate(angle, expand=True)
            paste(scene, orca, cx, cy)
            if t < 0.35:
                splash(scene, 30 + 30 * t, 4)
            if t > 0.75:
                splash(scene, 90, 5)
        frames.append(scene.resize((W * SCALE, H * SCALE), Image.NEAREST))
    return frames


def save_gif(frames, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    temporary = path + ".tmp"
    frames[0].save(temporary, format="GIF", save_all=True, append_images=frames[1:], duration=110, loop=0)
    os.replace(temporary, path)  # a failed run keeps the previous GIF


# ---------- GitHub ----------


def graphql(token, query, **variables):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "git-orca"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch(login, token):
    """Daily contributions for every year, and public non-fork repository languages by bytes."""
    data = graphql(
        token,
        """query($login: String!) { user(login: $login) {
          contributionsCollection { contributionYears }
          repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
            nodes { languages(first: 20) { edges { size node { name color } } } } } } }""",
        login=login,
    )["user"]
    languages = {}
    for repo in data["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name, color = edge["node"]["name"], edge["node"]["color"]
            languages[name] = (color, languages.get(name, (None, 0))[1] + edge["size"])
    days = {}
    for year in data["contributionsCollection"]["contributionYears"]:
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
    return days, languages


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN or GH_TOKEN.")
    login = os.environ.get("ORCA_LOGIN", "kadriudijar")
    days, languages = fetch(login, token)
    today = datetime.now(timezone.utc).date() - timedelta(1)  # the UTC day that just ended
    total = sum(n for d, n in days.items() if d <= today)
    signals = stage(total), top_color(languages), pod_size(weekly_streak(days, today)), behavior(days, today)
    print(f"total={total} stage={signals[0]} color={signals[1]} pod={signals[2]} behavior={signals[3]}")
    save_gif(render(*signals), "orca/orca.gif")


if __name__ == "__main__":
    main()
