"""Scrape the public contribution calendar (no token) -> data/contributions.json."""
import json
import re
import sys
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

USER = "udayjain2102"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}  # td id -> {date, level}
        self.counts = {}  # td id -> count
        self._tip_for = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and a.get("data-date"):
            self.cells[a["id"]] = {"date": a["data-date"], "level": int(a.get("data-level", 0))}
        elif tag == "tool-tip":
            self._tip_for = a.get("for")

    def handle_data(self, data):
        if self._tip_for:
            m = re.match(r"\s*(\d[\d,]*) contribution", data)
            self.counts[self._tip_for] = int(m.group(1).replace(",", "")) if m else 0
            self._tip_for = None


def parse(html):
    p = Calendar()
    p.feed(html)
    days = [{**c, "count": p.counts.get(i, 0)} for i, c in p.cells.items()]
    return sorted(days, key=lambda d: d["date"])


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    # today may not have contributions yet; don't break the streak on it
    for i, d in enumerate(reversed(days)):
        if d["count"]:
            current += 1
        elif i:
            break
    return current, longest


def stats(days):
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    return {
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": months,
    }


def demo():
    start = date(2026, 1, 1)
    days = [{"date": str(start + timedelta(i)), "level": 0, "count": c} for i, c in enumerate([1, 2, 0, 3, 3, 3, 0])]
    s = stats(days)
    assert s["total"] == 12 and s["longest_streak"] == 3 and s["current_streak"] == 3, s
    assert s["best_day"]["count"] == 3
    html = '<td data-date="2026-01-01" id="d0" data-level="2"></td><tool-tip for="d0">1,234 contributions on Jan 1st.</tool-tip>'
    assert parse(html) == [{"date": "2026-01-01", "level": 2, "count": 1234}]
    print("ok")


if __name__ == "__main__":
    if "--test" in sys.argv:
        demo()
        sys.exit()
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "profile-art"})
    days = parse(urllib.request.urlopen(req, timeout=30).read().decode())
    if len(days) < 300:  # page layout changed; don't overwrite good data with garbage
        sys.exit(f"only parsed {len(days)} days, refusing to write")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"user": USER, **stats(days), "days": days}, indent=1))
    print(f"{len(days)} days, {stats(days)['total']} contributions -> {OUT}")
