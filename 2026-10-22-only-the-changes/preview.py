"""Draw preview.svg: four rules side by side, births in amber, survivors in slate."""
import random

W, T, C = 29, 64, 6
RULES = [(110, "one"), (30, "one"), (90, "one"), (184, "random")]
GAP, PAD, TOP = 24, 20, 34

def run(rule, mode):
    random.seed(7)
    row = [0] * W
    if mode == "one":
        row[W - 2 if rule == 110 else W // 2] = 1
    else:
        row = [int(random.random() < 0.5) for _ in range(W)]
    prev, out = [0] * W, []
    for _ in range(T):
        out.append([0 if not v else (1 if p else 2) for v, p in zip(row, prev)])
        nxt = [(rule >> (row[(i - 1) % W] * 4 + row[i] * 2 + row[(i + 1) % W])) & 1 for i in range(W)]
        prev, row = row, nxt
    return out

width = PAD * 2 + len(RULES) * W * C + (len(RULES) - 1) * GAP
height = TOP + T * C + PAD
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
         f'<rect width="{width}" height="{height}" fill="#0f1115"/>']
for k, (rule, mode) in enumerate(RULES):
    x0 = PAD + k * (W * C + GAP)
    parts.append(f'<text x="{x0}" y="{TOP - 12}" fill="#b9b4a8" font-family="monospace" font-size="12">rule {rule}</text>')
    for y, r in enumerate(run(rule, mode)):
        for x, v in enumerate(r):
            if v:
                fill = "#f2b25c" if v == 2 else "#3a3f4a"
                parts.append(f'<rect x="{x0 + x * C + 0.5}" y="{TOP + y * C + 0.5}" width="{C - 1}" height="{C - 1}" fill="{fill}"/>')
parts.append("</svg>")
open("preview.svg", "w").write("\n".join(parts))
