"""Photo -> self-typing monochrome ASCII portrait (ascii.svg). Run locally only:

    pip install pillow rembg   # rembg optional: removes the background
    python scripts/make_ascii_svg.py path/to/photo.jpg
"""
import sys
from html import escape
from pathlib import Path

from PIL import Image, ImageOps

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears the background
COLS, ROWS = 100, 53
CW, LH = 7.2, 13  # glyph advance / line height at font-size 12
FILL = "#c9d1d9"


def prep(path):
    img = Image.open(path).convert("RGBA")
    try:
        from rembg import remove
        img = remove(img)
    except ImportError:
        print("rembg not installed; keeping background")
    white = Image.new("RGBA", img.size, "white")
    gray = Image.alpha_composite(white, img).convert("L")
    # ponytail: global equalize instead of OpenCV CLAHE; add CLAHE if faces come out flat
    return ImageOps.equalize(ImageOps.autocontrast(gray, cutoff=1))


def to_ascii(gray):
    small = gray.resize((COLS, ROWS))
    px = small.load()
    n = len(RAMP) - 1
    return ["".join(RAMP[n - px[x, y] * n // 255] for x in range(COLS)).rstrip() for y in range(ROWS)]


def svg(lines):
    W, H = int(COLS * CW) + 20, ROWS * LH + 20
    out = []
    for i, line in enumerate(lines):
        if not line:
            continue
        y, w, t = 10 + i * LH, len(line) * CW, 0.2 + i * 0.06
        dur = max(0.15, len(line) / 250)
        out.append(
            f'<clipPath id="c{i}"><rect x="10" y="{y}" height="{LH}" width="0">'
            f'<animate attributeName="width" from="0" to="{w:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<text x="10" y="{y + 10}" clip-path="url(#c{i})" xml:space="preserve">{escape(line)}</text>'
            f'<rect x="10" y="{y + 1}" width="{CW}" height="{LH - 2}" fill="{FILL}" opacity="0">'
            f'<animate attributeName="x" from="10" to="{10 + w:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.8" begin="{t:.2f}s"/><set attributeName="opacity" to="0" begin="{t + dur:.2f}s"/></rect>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="12" fill="{FILL}">'
        f'<rect width="100%" height="100%" rx="10" fill="#0d1117"/>{"".join(out)}</svg>\n'
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    lines = to_ascii(prep(sys.argv[1]))
    (Path(__file__).resolve().parent.parent / "ascii.svg").write_text(svg(lines))
    print("wrote ascii.svg — add it to README.md next to info-card.svg")
