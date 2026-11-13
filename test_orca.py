from datetime import date, timedelta

from orca import activity_svg, behavior, breakdown_svg, longest_weekly_streak, pod_size, stage, top_color, weekly_streak

D = date  # brevity
today = D(2026, 11, 12)  # a Thursday; its week starts Monday 2026-11-09


def span(start, end, count):
    return {start + timedelta(n): count for n in range((end - start).days + 1)}


assert stage(0) == "calf" and stage(499) == "calf"
assert stage(500) == "juvenile" and stage(2999) == "juvenile"
assert stage(3000) == "adult"

assert pod_size(3) == 0 and pod_size(4) == 1 and pod_size(8) == 2 and pod_size(100) == 2

# Five complete active weeks; the current week has no activity yet and does not end the streak.
weeks = {D(2026, 11, 4): 1, D(2026, 10, 28): 1, D(2026, 10, 21): 1, D(2026, 10, 14): 1, D(2026, 10, 7): 1}
assert weekly_streak(weeks, today) == 5
assert weekly_streak({**weeks, D(2026, 11, 9): 1}, today) == 6
assert weekly_streak({k: v for k, v in weeks.items() if k != D(2026, 10, 21)}, today) == 2
assert weekly_streak({}, today) == 0
# Days after today are ignored.
assert weekly_streak({D(2026, 11, 13): 9}, today) == 0

assert behavior({D(2026, 11, 9): 3}, today) == "rest"
assert behavior({}, today) == "rest"
assert behavior({D(2026, 11, 6): 1, D(2026, 11, 12): 2, D(2026, 11, 13): 50}, today) == "spyhop"
assert behavior({**span(D(2026, 10, 15), D(2026, 11, 11), 2), D(2026, 11, 12): 10}, today) == "breach"
assert behavior({**span(D(2026, 10, 15), D(2026, 11, 11), 1), D(2026, 11, 12): 4}, today) == "cruise"
assert behavior({**span(D(2026, 10, 15), D(2026, 11, 11), 2), D(2026, 11, 12): 3}, today) == "cruise"

assert top_color({}) == "#8a8a8a"
assert top_color({"Python": ("#3572A5", 100), "C#": ("#178600", 500)}) == "#178600"
assert top_color({"Weird": (None, 900), "Go": ("#00ADD8", 10)}) == "#8a8a8a"

assert longest_weekly_streak(weeks, today) == 5
assert longest_weekly_streak({**weeks, D(2025, 1, 1): 1, D(2025, 1, 8): 1}, today) == 5
assert longest_weekly_streak({D(2026, 11, 13): 9}, today) == 0

card = activity_svg("octocat", {D(2025, 11, 12): 7, D(2026, 11, 4): 1, D(2026, 11, 12): 3, D(2026, 11, 13): 99}, today, dark=False)
assert card.startswith("<svg") and "octocat" in card
assert ">11<" in card  # all time, ignoring the day after today
assert ">4<" in card  # last 365 days, so the day a year ago drops out
assert "7 on 2025-11-12" in card  # best day

card = breakdown_svg({"commits": 1848, "prs": 1048, "merged": 893, "reviews": 552, "issues": 12}, dark=True)
assert ">1,848<" in card and ">1,048 (893 merged)<" in card and ">552<" in card and ">12<" in card
assert breakdown_svg({"commits": 0, "prs": 0, "merged": 0, "reviews": 0, "issues": 0}, dark=False).startswith("<svg")

print("ok")
