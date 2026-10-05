"""Neofetch-style info card -> info-card.svg. Edit LINES, rerun. STATIC=1 for a frozen frame."""
import os
from html import escape
from pathlib import Path

USER = "uday@github"
# TODO: replace placeholders. Values over ~44 chars run off the card.
LINES = [
    ("Now", "<school / role> · Summer 2027 intern"),
    ("Prev", "<previous role / project>"),
    ("Stack", "Python · TypeScript · SQL · <add yours>"),
    ("Focus", "<what you're building or learning>"),
    ("Highlights", "<a number or win you're proud of>"),
    ("", "<another highlight>"),
    ("Contact", "<email / site / LinkedIn>"),
]
KEY_COLOR, VAL_COLOR = "#39d353", "#c9d1d9"
W, LH, TOP = 490, 26, 70
H = TOP + len(LINES) * LH + 40
static = os.environ.get("STATIC") == "1"

rows = []
for i, (k, v) in enumerate(LINES):
    style = "" if static else f' style="animation-delay:{0.3 + i * 0.12:.2f}s"'
    rows.append(
        f'<text class="l" x="24" y="{TOP + i * LH}"{style}>'
        f'<tspan fill="{KEY_COLOR}" font-weight="bold">{escape(k + ":" if k else "")}</tspan>'
        f'<tspan x="130" fill="{VAL_COLOR}">{escape(v)}</tspan></text>'
    )
palette = "".join(f'<rect x="{24 + j * 22}" y="{H - 28}" width="18" height="10" rx="2" fill="{c}"/>'
                  for j, c in enumerate(["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#7d8590", "#c9d1d9"]))
anim = "" if static else ".l{opacity:0;animation:in .4s ease-out forwards}@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="13">
<style>{anim}</style>
<rect width="100%" height="100%" rx="10" fill="#0d1117"/>
<circle cx="20" cy="18" r="5" fill="#ff5f56"/><circle cx="36" cy="18" r="5" fill="#ffbd2e"/><circle cx="52" cy="18" r="5" fill="#27c93f"/>
<text x="24" y="48" fill="{KEY_COLOR}" font-weight="bold">{USER}</text>
<line x1="24" y1="54" x2="{24 + len(USER) * 8}" y2="54" stroke="#7d8590"/>
{"".join(rows)}
{palette}
</svg>
"""
(Path(__file__).resolve().parent.parent / "info-card.svg").write_text(svg)
print("wrote info-card.svg")
