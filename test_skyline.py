from datetime import date, timedelta

from skyline import activity_svg, breakdown_svg, building_heights, longest_weekly_streak, weekly_streak, weekly_totals

D = date  # brevity
today = D(2026, 11, 12)  # a Thursday; its week starts Monday 2026-11-09

# Oldest week first; the last week is the one in progress and ignores days after today.
totals = weekly_totals({D(2026, 11, 9): 2, D(2026, 11, 12): 3, D(2026, 11, 13): 50, D(2026, 11, 2): 4, D(2026, 10, 1): 9}, today, count=3)
assert totals == [0, 4, 5]
assert len(weekly_totals({}, today)) == 48

assert building_heights([0, 1, 4, 16], tallest=38) == [3, 14, 22, 38]  # square root of the share of the busiest week
assert building_heights([0, 0]) == [3, 3]

# Five complete active weeks; the current week has no activity yet and does not end the streak.
weeks = {D(2026, 11, 4): 1, D(2026, 10, 28): 1, D(2026, 10, 21): 1, D(2026, 10, 14): 1, D(2026, 10, 7): 1}
assert weekly_streak(weeks, today) == 5
assert weekly_streak({**weeks, D(2026, 11, 9): 1}, today) == 6
assert weekly_streak({k: v for k, v in weeks.items() if k != D(2026, 10, 21)}, today) == 2
assert weekly_streak({}, today) == 0
# Days after today are ignored.
assert weekly_streak({D(2026, 11, 13): 9}, today) == 0

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
