"""Draws silence.json as an atlas (atlas.svg), adds three small spacetime
drawings of the slowest pattern to fall silent, and writes index.html."""
import json
import numpy as np
from compute import step

D = json.load(open("silence.json"))
MAXN, RULES = D["maxn"], {int(k): v for k, v in D["rules"].items()}
W0 = 3                                   # widths 1 and 2 are degenerate rings
widths = list(range(W0, MAXN + 1))

BG, INK, FAINT, DIM = "#14161f", "#e9e4d8", "#3a3e52", "#8a8aa0"

def colour(t, tmax=16):
    # quick endings warm and pale, slow endings deep rose and violet
    stops = [(0.0, (250, 222, 150)), (0.35, (244, 150, 110)),
             (0.7, (214, 90, 140)), (1.0, (130, 90, 210))]
    x = min(1, (np.log2(t)) / np.log2(tmax)) if t > 1 else 0
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if x <= b:
            f = (x - a) / (b - a)
            return "#%02x%02x%02x" % tuple(round(ca[i] + f * (cb[i] - ca[i])) for i in range(3))
    return "#%02x%02x%02x" % stops[-1][1]

def slowest(rule, n):
    """The starting pattern that stays lit longest, and its rows until dark."""
    S = np.arange(1 << n, dtype=np.uint32)
    alive = np.ones(S.size, bool)
    cur = S.copy()
    last = None
    while alive.any():
        last = np.flatnonzero(alive)[0]
        cur = step(cur, rule, n)
        alive &= cur != 0
    rows, s = [], int(last)
    while True:
        rows.append(s)
        if s == 0:
            return rows
        s = int(step(np.array([s], np.uint32), rule, n)[0])

C = 22                     # cell size
LAB = 46                   # rule-label column
PAD = 40
panel_w = LAB + len(widths) * C
top = 172
out = []
Wsvg = PAD * 2 + panel_w * 2 + 50
rules = sorted(RULES)
half = len(rules) // 2
grid_h = half * C

out.append(f'<text x="{PAD}" y="58" font-size="34" fill="{INK}" font-family="Fraunces, Georgia, serif">Which songs end</text>')
out.append(f'<text x="{PAD}" y="88" font-size="14.5" fill="{DIM}" font-family="Inter, sans-serif">Every elementary cellular automaton that keeps silence silent, on every ring from 3 to {MAXN} cells.</text>')
out.append(f'<text x="{PAD}" y="110" font-size="14.5" fill="{DIM}" font-family="Inter, sans-serif">A coloured note means every starting pattern goes dark; the number is how many steps</text>')
out.append(f'<text x="{PAD}" y="130" font-size="14.5" fill="{DIM}" font-family="Inter, sans-serif">the slowest one takes. A faint dot means some pattern sings forever.</text>')

for p in range(2):
    x0 = PAD + p * (panel_w + 50)
    for i, w in enumerate(widths):
        cx = x0 + LAB + i * C + C / 2
        out.append(f'<text x="{cx}" y="{top - 8}" font-size="10" fill="{DIM}" text-anchor="middle" font-family="Inter, sans-serif">{w}</text>')
    for j, rule in enumerate(rules[p * half:(p + 1) * half]):
        cy = top + j * C + C / 2
        out.append(f'<text x="{x0 + LAB - 8}" y="{cy + 4}" font-size="11" fill="{DIM}" text-anchor="end" font-family="Inter, sans-serif">{rule}</text>')
        for i, w in enumerate(widths):
            t = RULES[rule][w - 1]
            cx = x0 + LAB + i * C + C / 2
            if t is None:
                out.append(f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="{FAINT}"/>')
            else:
                out.append(f'<circle cx="{cx}" cy="{cy}" r="{C/2 - 1.5}" fill="{colour(t)}"/>')
                out.append(f'<text x="{cx}" y="{cy + 3.8}" font-size="10.5" fill="{BG}" text-anchor="middle" font-weight="600" font-family="Inter, sans-serif">{t}</text>')
    out.append(f'<text x="{x0 + LAB + len(widths) * C / 2}" y="{top + grid_h + 22}" font-size="11" fill="{DIM}" text-anchor="middle" font-family="Inter, sans-serif">ring width →</text>')
    out.append(f'<text x="{x0 + 4}" y="{top - 8}" font-size="10" fill="{DIM}" font-family="Inter, sans-serif">rule</text>')

# three small drawings: the last pattern to fall silent
vy = top + grid_h + 70
out.append(f'<text x="{PAD}" y="{vy}" font-size="18" fill="{INK}" font-family="Fraunces, Georgia, serif">The last one out</text>')
out.append(f'<text x="{PAD}" y="{vy + 22}" font-size="13" fill="{DIM}" font-family="Inter, sans-serif">For three endings, the starting pattern that holds on longest, drawn one row per step until the ring is dark.</text>')
picks = [(32, 15, "rule 32, ring of 15: ends only on odd rings"),
         (60, 16, "rule 60, ring of 16: ends only on powers of two"),
         (22, 5, "rule 22, ring of 5: a one-off")]
vx = PAD
cell = 13
maxrows = 0
for rule, n, label in picks:
    rows = slowest(rule, n)
    maxrows = max(maxrows, len(rows))
    col = colour(RULES[rule][n - 1])
    y0 = vy + 50
    out.append(f'<text x="{vx}" y="{y0 - 10}" font-size="12" fill="{DIM}" font-family="Inter, sans-serif">{label}</text>')
    for r, s in enumerate(rows):
        for k in range(n):
            lit = s >> (n - 1 - k) & 1
            fill = col if lit else "#1d2030"
            out.append(f'<rect x="{vx + k * cell}" y="{y0 + r * cell}" width="{cell - 2}" height="{cell - 2}" rx="2" fill="{fill}"/>')
    vx += max(n * cell, 230) + 60
Hsvg = vy + 50 + maxrows * cell + 50

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wsvg} {Hsvg}" width="{Wsvg}" height="{Hsvg}">'
       f'<rect width="100%" height="100%" fill="{BG}"/>' + "".join(out) + "</svg>")
open("atlas.svg", "w").write(svg)
print(Wsvg, Hsvg)

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Which songs end</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz@9..144&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  body {{ margin: 0; background: {BG}; color: {INK}; font-family: Inter, sans-serif; }}
  main {{ max-width: {Wsvg}px; margin: 0 auto; padding: 16px; }}
  svg {{ width: 100%; height: auto; display: block; }}
  p {{ color: {DIM}; line-height: 1.6; max-width: 46em; margin: 0 {PAD}px 1em; font-size: 15px; }}
  p b {{ color: {INK}; font-weight: 600; }}
</style></head>
<body><main>
{svg}
<p><b>How to read it.</b> Each row is a rule, numbered the usual way (Wolfram's). Each column is a ring of that many cells, joined end to end. A rule is played on every possible starting pattern at once. If all of them eventually go dark, the square holds a note, and the number is the length of the longest song. If even one pattern lights up forever, the square is a faint dot. Only the 64 rules that leave a dark neighbourhood dark and a fully lit one unlit can end at all, so those are all there is.</p>
<p><b>What it says.</b> Almost nothing ends. Of the {len(rules)} rules, three end on every ring (0, 8, 64); one ends on every odd ring and never on an even one (32); three end exactly on rings whose size is a power of two (60, 90, 102); and a handful end on one or two small rings by accident and not again up to 20. Everything else hums forever somewhere.</p>
</main></body></html>
"""
open("index.html", "w").write(html)
