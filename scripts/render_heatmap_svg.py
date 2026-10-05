"""data/contributions.json -> contrib-heatmap.svg (diagonal reveal, plays once)."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]  # GitHub levels 0-4
CELL, GAP, LEFT, TOP = 13, 3, 34, 30
STEP = CELL + GAP

data = json.loads((ROOT / "data" / "contributions.json").read_text())
days = data["days"]
offset = (date.fromisoformat(days[0]["date"]).weekday() + 1) % 7  # Sunday-first rows
weeks = (len(days) + offset + 6) // 7
W, H = LEFT + weeks * STEP + 16, TOP + 7 * STEP + 52

cells, months, last_month = [], [], None
for i, d in enumerate(days):
    col, row = divmod(i + offset, 7)
    x, y = LEFT + col * STEP, TOP + row * STEP
    delay = (col + row) * 0.018
    cells.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[d["level"]]}" '
        f'style="animation-delay:{delay:.3f}s"><title>{d["count"]} on {d["date"]}</title></rect>'
    )
    if row == 0 and d["date"][:7] != last_month:  # label the first column of each month
        last_month = d["date"][:7]
        months.append(f'<text x="{x}" y="{TOP - 10}">{date.fromisoformat(d["date"]).strftime("%b")}</text>')

labels = "".join(f'<text x="{LEFT - 8}" y="{TOP + r * STEP + 10}" text-anchor="end">{n}</text>' for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
fy = TOP + 7 * STEP + 22
legend_x = W - 16 - 5 * STEP - 70
legend = (
    f'<text x="{legend_x}" y="{fy}">Less</text>'
    + "".join(f'<rect x="{legend_x + 34 + k * STEP}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>' for k, c in enumerate(PALETTE))
    + f'<text x="{legend_x + 38 + 5 * STEP}" y="{fy}">More</text>'
)
best = data["best_day"]
footer = (
    f'<text x="{LEFT}" y="{fy}"><tspan class="hi">{data["total"]:,}</tspan> contributions in the last year</text>'
    f'<text x="{LEFT}" y="{fy + 20}">streak <tspan class="hi">{data["current_streak"]}d</tspan> · '
    f'longest <tspan class="hi">{data["longest_streak"]}d</tspan> · '
    f'best day <tspan class="hi">{best["count"]}</tspan> ({best["date"]})</text>'
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="11">
<style>
text{{fill:#7d8590}} .hi{{fill:#39d353;font-weight:bold}}
.g rect{{opacity:0;transform-box:fill-box;transform-origin:center;animation:drop .45s cubic-bezier(.2,.8,.3,1) forwards}}
@keyframes drop{{from{{opacity:0;transform:translateY(-8px) scale(.6)}}to{{opacity:1;transform:none}}}}
</style>
<rect width="100%" height="100%" rx="10" fill="#0d1117"/>
{"".join(months)}{labels}
<g class="g">{"".join(cells)}</g>
{legend}{footer}
</svg>
"""
(ROOT / "contrib-heatmap.svg").write_text(svg)
print(f"wrote contrib-heatmap.svg ({weeks} weeks, {data['total']} contributions)")
