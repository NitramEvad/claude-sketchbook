"""Puddles: a 2,000 m race in a single scull, drawn as the puddles its blades leave.

A model, not a recording. Run `python3 make.py` to rebuild puddles.svg and index.html.
"""
import math, random

random.seed(2810)

# ---- the race -------------------------------------------------------------
RACE = 2000.0
def plan(x):
    """target stroke rate at distance x (metres)"""
    if x < 40:   return 40
    if x < 250:  return 38 - 4 * (x - 40) / 210      # wind down from the start
    if x < 330:  return 34 - 2 * (x - 250) / 80      # settle
    if 1000 <= x < 1080: return 34                   # a push at the thousand
    if x < 1500: return 32 - 1.0 * max(0, x - 1100) / 400   # the third 500 sags
    if x < 1750: return 32.5
    return 32.5 + 5 * (x - 1750) / 250               # sprint

strokes = []                # (distance at release, time, rate, d, track y, lean)
x, t, k = 0.0, 0.0, 0
y, heading = 0.0, 0.0       # off the centre of the lane (m), and drift per stroke
while x < RACE:
    k += 1
    rate = plan(x) + random.gauss(0, 0.25)
    if k <= 4: rate = [26, 34, 40, 41][k - 1]
    fatigue = 0.00010 * x
    v = 2.75 + 0.058 * rate - fatigue
    v *= 1 - math.exp(-k / 2.2)
    v *= 1 + random.gauss(0, 0.012)
    d = v * 60 / rate
    # a single scull wanders; when it strays, one hand pulls a little harder
    heading += random.gauss(0, 0.012)
    lean = 0.0
    if abs(y) > 0.45 and y * heading > 0:
        lean = -math.copysign(1, y)            # pull harder on the side that turns it back
        heading -= math.copysign(0.05, y)
    y += heading
    x += d; t += 60 / rate
    strokes.append((x, t, rate, d, y, lean))
last = strokes[-1]
T_FINISH = last[1] - (last[0] - RACE) / (last[3] / (60 / last[2]))
strokes = [s for s in strokes if s[0] <= RACE]
corrections = sum(1 for s in strokes if s[5])
print(f"{len(strokes)} strokes, finish {int(T_FINISH//60)}:{T_FINISH%60:04.1f}, {corrections} steering strokes")

BLADE_BACK = 3.0            # blades leave the water about 3 m behind the bow
puddles = []   # (x, y, age, strength)
for (xr, tr, rate, d, ty, lean) in strokes:
    age = T_FINISH - tr
    for side in (-1, 1):
        px = xr - BLADE_BACK + random.gauss(0, 0.06)
        py = ty + side * (2.3 + random.gauss(0, 0.05))
        # drift: a faint breeze across the course, and a little wander
        py += 0.0020 * age + random.gauss(0, 0.0012 * age)
        px += random.gauss(0, 0.0008 * age)
        st = (0.92 + 0.12 * random.random()) * (rate / 32) ** 0.3
        if lean == side: st *= 1.35
        puddles.append((px, py, age, st))

# ---- drawing --------------------------------------------------------------
ROW_M = 100            # metres per line of the page
PX = 9.0               # pixels per metre
L, R = 70, 260         # margins
W = L + ROW_M * PX + R
ROW_H = 84
TOP = 20
rows = int(RACE // ROW_M)
H = TOP + rows * ROW_H + 20

def spiral(cx, cy, r, turns, cw):
    pts = []
    n = 28
    for i in range(n + 1):
        f = i / n
        a = f * turns * 2 * math.pi * (1 if cw else -1)
        rr = r * (0.1 + 0.9 * f)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)

def mid(i): return TOP + i * ROW_H + ROW_H / 2

out = []
for i in range(rows + 1):
    yl = TOP + i * ROW_H
    out.append(f'<line class="lane" x1="{L}" y1="{yl}" x2="{L+ROW_M*PX}" y2="{yl}"/>')
for i in range(rows):
    out.append(f'<text class="m" x="{L-14}" y="{mid(i)+4:.1f}">{i*ROW_M}</text>')

for (px, py, age, st) in puddles:
    if px < 0: continue
    row = min(int(px // ROW_M), rows - 1)
    cx = L + (px - row * ROW_M) * PX
    cy = mid(row) + py * PX
    r = (0.34 + 0.028 * math.sqrt(age)) * st * PX
    op = 0.14 + 0.86 * math.exp(-age / 190)
    turns = 1.8 - 0.9 * min(1, age / 450)          # old swirls have unwound a little
    sep = r * 1.05
    # a puddle is a pair of counter-rotating swirls, from the two edges of the blade
    out.append(f'<g opacity="{op:.2f}"><path d="{spiral(cx, cy - sep, r, turns, True)}"/>'
               f'<path d="{spiral(cx, cy + sep, r, turns, False)}"/></g>')

# the boat, bow on the finish line
y0 = mid(rows - 1) + strokes[-1][4] * PX
bx = L + ROW_M * PX
hull_len = 8.2 * PX
out.append(f'<path class="hull" d="M{bx:.1f},{y0:.1f} Q{bx - hull_len*0.5:.1f},{y0 - 0.42*PX:.1f} {bx - hull_len:.1f},{y0:.1f} Q{bx - hull_len*0.5:.1f},{y0 + 0.42*PX:.1f} {bx:.1f},{y0:.1f}Z"/>')
sx = bx - 4.4 * PX
for side in (-1, 1):
    # oars squared and reaching forward to the next catch
    ex, ey = sx + 1.6 * PX, y0 + side * 2.6 * PX
    out.append(f'<line class="oar" x1="{sx - 0.5*PX:.1f}" y1="{y0 - side*0.2*PX:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
    out.append(f'<line class="blade" x1="{ex - 0.05*PX:.1f}" y1="{ey - side*0.1*PX:.1f}" x2="{ex + 0.15*PX:.1f}" y2="{ey + side*0.45*PX:.1f}"/>')
out.append(f'<line class="finish" x1="{bx:.1f}" y1="{TOP + (rows-1)*ROW_H}" x2="{bx:.1f}" y2="{TOP + rows*ROW_H}"/>')

notes = {
    0: "the start: short, quick strokes",
    2: "the rate comes down; the gaps open",
    4: "settled: about nine metres a stroke",
    10: "a push at the thousand",
    13: "the third 500 sags a little",
    17: "the sprint: rate up, gaps shorter",
    19: "finish",
}
for i, txt in notes.items():
    out.append(f'<text class="n" x="{L + ROW_M*PX + 22}" y="{mid(i)+4:.1f}">{txt}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="A 2,000 metre race drawn as the puddles left by a single sculler's blades, in twenty lines of 100 metres. The start has faded; the finish is crisp.">
<style>
path{{fill:none;stroke:var(--ink,#23303a);stroke-width:1;stroke-linecap:round}}
.lane{{stroke:var(--faint,#b9b2a5);stroke-width:.5;stroke-dasharray:2 6}}
.m{{fill:var(--faint,#9a9284);font:13px Georgia,serif;text-anchor:end}}
.n{{fill:var(--faint,#8a8274);font:italic 14px Georgia,serif}}
.hull{{fill:var(--bg,#f3efe6);stroke-width:1.2}}
.oar{{stroke:var(--ink,#23303a);stroke-width:1.1}}
.blade{{stroke:var(--ink,#23303a);stroke-width:3;stroke-linecap:round}}
.finish{{stroke:#b5523b;stroke-width:1.3}}
</style>
{chr(10).join(out)}
</svg>'''
open("puddles.svg", "w").write(svg)

mins = f"{int(T_FINISH//60)}:{T_FINISH%60:04.1f}"
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Puddles</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f3efe6;--ink:#23303a;--faint:#9a9284}}
@media (prefers-color-scheme:dark){{:root{{--bg:#12161a;--ink:#d9e2e8;--faint:#66707a}}}}
html,body{{margin:0;background:var(--bg);color:var(--ink)}}
body{{font-family:"EB Garamond",Georgia,serif;font-size:19px;line-height:1.5;padding:8vh 16px 12vh}}
header,footer{{max-width:34em;margin:0 auto}}
h1{{font-weight:400;font-style:italic;font-size:1.5em;margin:0 0 .2em}}
.sub{{color:var(--faint);margin:0 0 2.5em}}
figure{{margin:0 auto;max-width:{W:.0f}px}}
figure svg{{width:100%;height:auto;display:block}}
footer{{margin-top:3em;color:var(--faint);font-size:.85em}}
footer p{{margin:0 0 1em}}
</style></head>
<body>
<header><h1>Puddles</h1>
<p class="sub">a 2,000 metre race in a single scull, as the water remembers it at the finish</p></header>
<figure>
{svg}
</figure>
<footer>
<p>When a blade comes out of the water it leaves a puddle: a pair of small whirlpools, one from each edge of the spoon, turning opposite ways. Coaches read them. The gap between one stroke's puddles and the next is how far the boat ran.</p>
<p>Read it like a page, left to right, a hundred metres to a line. Each stroke leaves two puddles, one from each blade. Where one is bigger than its partner, the boat had wandered and one hand pulled harder to bring it back. The drawing is the moment the bow crosses the line, {len(strokes)} strokes and {mins} after the start, so the oldest puddles have spread wide and nearly gone, and the newest are still tight under the boat. A breeze has nudged the old ones across the lane.</p>
<p>It is a model, not a recorded race: the stroke rates and speeds are a plausible plan, with a little noise in every stroke,, a slowly wandering line, and a breeze.</p>
</footer>
</body></html>'''
open("index.html", "w").write(html)
