"""The eight: a crew of eight, drawn as the water it leaves behind, one colour per seat.

A model, not a recording. Run `python3 make.py` to rebuild eight.svg and index.html.
"""
import math, random

random.seed(3010)

# ---- the crew -------------------------------------------------------------
# Standard rig: stroke (8) and the even seats on port, the odd seats on starboard.
# Seeing the boat from above with the bow pointing right, port is the top of the page.
RATE = 36.0
T = 60 / RATE              # one stroke, seconds
V = 5.55                   # mean boat speed, m/s (a little under 6:00 for 2k)
OUT = 2.30                 # pin to blade centre, metres
SPREAD = 0.84              # boat centre line to pin
SEAT_GAP = 1.42

# each seat: side, colour, and how it rows. Angles in degrees from square;
# lag in seconds (positive = late); depth scales the puddle.
NOTE = {8: "the one everyone follows", 7: "long: reaches further at the catch",
        6: "pulls deep: the biggest puddles", 5: "late: a beat behind at the catch",
        4: "steady", 3: "short: out of the water early",
        2: "a hair early", 1: "splashes going in"}
SEATS = {
    8: dict(side=-1, col="#b8432f", name="stroke", catch=56, rel=34, lag=0.0,   depth=1.0,  splash=0.4),
    7: dict(side=+1, col="#2f63a8", name="seven",  catch=62, rel=34, lag=0.0,   depth=1.0,  splash=0.4),
    6: dict(side=-1, col="#d9822b", name="six",    catch=55, rel=34, lag=0.0,   depth=1.25, splash=0.4),
    5: dict(side=+1, col="#2a8c8c", name="five",   catch=55, rel=34, lag=0.06, depth=1.0,  splash=0.6),
    4: dict(side=-1, col="#c49a1c", name="four",   catch=55, rel=34, lag=0.0,   depth=1.05, splash=0.4),
    3: dict(side=+1, col="#4f9a3e", name="three",  catch=55, rel=24, lag=0.0,   depth=0.7,  splash=0.4),
    2: dict(side=-1, col="#c04f7a", name="two",    catch=55, rel=34, lag=-0.02, depth=1.0,  splash=0.4),
    1: dict(side=+1, col="#7a52a8", name="bow",    catch=54, rel=33, lag=0.0,   depth=0.95, splash=1.6),
}
DRIVE = 0.62               # seconds the blade is in the water

def pin_x(s):              # along the boat, relative to the bow (metres, negative = sternwards)
    return -(3.0 + (s - 1) * SEAT_GAP)

def boat_x(t):
    """bow position in the water's frame: slowest just after the catch"""
    return V * (t - 0.11 * T / (2 * math.pi) * math.sin(2 * math.pi * t / T))

def ease(f): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, f)))

N = 7                      # strokes in the picture
t_now = N * T + 0.55       # the boat is part way through a recovery

def blade(s, t, k, jit):
    """water-frame (x, y) of seat s's blade at time t, in stroke k (catch at k*T + lag)"""
    c = SEATS[s]
    t0 = k * T + c["lag"] + jit
    u = t - t0
    ca, ra = math.radians(c["catch"]), -math.radians(c["rel"])
    if u < DRIVE:          # drive: from catch angle to release angle
        phi = ca + (ra - ca) * ease(u / DRIVE)
    else:                  # recovery: back to the next catch
        phi = ra + (ca - ra) * ease((u - DRIVE) / (T - DRIVE))
    x = boat_x(t) + pin_x(s) + OUT * math.sin(phi)
    y = c["side"] * (SPREAD + OUT * math.cos(phi))
    return x, y

# ---- what the water keeps -------------------------------------------------
puddles, arcs, catches = [], [], []
for s, c in SEATS.items():
    jits = [random.gauss(0, 0.012) for _ in range(N + 2)]
    for k in range(N + 1):
        t_c = k * T + c["lag"] + jits[k]
        t_r = t_c + DRIVE
        if t_c > t_now: break
        # the catch: a few drops where the blade goes in
        cx, cy = blade(s, t_c, k, jits[k])
        catches.append((s, cx, cy, t_now - t_c))
        if t_r > t_now: continue
        # the puddle: where the blade comes out
        px, py = blade(s, t_r, k, jits[k])
        px -= 0.25         # slip: the blade has pushed a little water back
        puddles.append((s, px, py, t_now - t_r, c["depth"] * (1 + random.gauss(0, 0.06))))
        # the recovery: drips falling off the feathered blade, thick at first, then thinning
        t_next = (k + 1) * T + c["lag"] + jits[k + 1]
        pts = []
        steps = 46
        for i in range(1, steps):
            f = i / steps
            t = t_r + f * (t_next - t_r)
            if t > t_now: break
            # drips get sparser along the way
            if random.random() > 0.95 * (1 - f) ** 0.9 + 0.12: continue
            x, y = blade(s, t, k, jits[k])
            pts.append((x + random.gauss(0, 0.03), y + random.gauss(0, 0.03), 1 - 0.6 * f, t_now - t))
        arcs.append((s, pts))

# ---- drawing --------------------------------------------------------------
PX = 30.0                  # pixels per metre along the lane
WIN = 44.0                 # metres of water shown behind the bow
bow_now = boat_x(t_now)
X0 = bow_now - WIN + 1.0
L, R = 110, 260
W = L + WIN * PX + R

def fade(age): return 0.25 + 0.75 * math.exp(-age / 9)

def spiral(cx, cy, r, turns, cw, a0):
    pts = []
    n = 26
    for i in range(n + 1):
        f = i / n
        a = a0 + f * turns * 2 * math.pi * (1 if cw else -1)
        rr = r * (0.12 + 0.88 * f)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)

rng = random.Random(7)
def marks(only, sx, sy, out):
    """draw the water's marks for seats in `only`, through the maps sx(x, s), sy(y, s)"""
    for s, pts in arcs:
        if s not in only: continue
        col = SEATS[s]["col"]
        for (x, y, w, age) in pts:
            X, Y = sx(x, s), sy(y, s)
            if X < L - 4: continue
            out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{0.8 + 1.2*w:.1f}" fill="{col}" opacity="{0.8*fade(age):.2f}"/>')
    for s, x, y, age in catches:
        if s not in only: continue
        c = SEATS[s]
        for i in range(int(3 + 5 * c["splash"])):
            a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0.05, 0.2 * (1 + c["splash"]))
            X, Y = sx(x + r * math.cos(a), s), sy(y + r * math.sin(a), s)
            if X < L - 4: continue
            out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="1.2" fill="{c["col"]}" opacity="{0.9*fade(age):.2f}"/>')
    for s, x, y, age, depth in puddles:
        if s not in only: continue
        c = SEATS[s]
        X, Y = sx(x, s), sy(y, s)
        if X < L + 4: continue
        r = (0.17 + 0.035 * math.sqrt(age)) * depth * PX
        turns = 1.7 - 0.5 * min(1, age / 12)
        # two counter-rotating swirls, one from each end of the spoon
        sep = r * 1.05
        out.append(f'<g stroke="{c["col"]}" opacity="{fade(age):.2f}">'
                   f'<path d="{spiral(X, Y - sep, r, turns, True, 0)}"/>'
                   f'<path d="{spiral(X, Y + sep, r, turns, False, math.pi)}"/></g>')

out = []
# -- panel 1: the water as it is (true scale) --
TOP1 = 50; H1 = 9.0 * PX
def sx1(x, s=None): return L + (x - X0) * PX
def sy1(y, s=None): return TOP1 + H1 / 2 + y * PX
out.append(f'<text class="h" x="{L}" y="{TOP1 - 22}">the water as it is</text>')
out.append(f'<line class="lane" x1="{L}" y1="{sy1(0):.1f}" x2="{L + WIN*PX:.1f}" y2="{sy1(0):.1f}"/>')
marks(SEATS, sx1, sy1, out)
bx, by = sx1(bow_now), sy1(0)
hl = 17.4 * PX; hw = 0.3 * PX
out.append(f'<path class="hull" d="M{bx:.1f},{by:.1f} Q{bx - hl*0.5:.1f},{by - hw:.1f} {bx - hl:.1f},{by:.1f} Q{bx - hl*0.5:.1f},{by + hw:.1f} {bx:.1f},{by:.1f}Z"/>')
k_now = int(t_now // T)
for s, c in SEATS.items():
    px_, py_ = sx1(bow_now + pin_x(s)), sy1(c["side"] * SPREAD)
    bxx, byy = blade(s, t_now, k_now, 0)
    X, Y = sx1(bxx), sy1(byy)
    hx, hy = px_ - (X - px_) * 0.5, py_ - (Y - py_) * 0.5
    out.append(f'<line class="oar" x1="{hx:.1f}" y1="{hy:.1f}" x2="{X:.1f}" y2="{Y:.1f}"/>')
    out.append(f'<ellipse cx="{X:.1f}" cy="{Y:.1f}" rx="5" ry="2.2" transform="rotate({math.degrees(math.atan2(Y-py_, X-px_)):.0f} {X:.1f} {Y:.1f})" fill="{c["col"]}"/>')
    out.append(f'<circle cx="{px_:.1f}" cy="{by:.1f}" r="2.6" class="seat"/>')
out.append(f'<text class="n" x="{L + WIN*PX + 22}" y="{sy1(-3.0)+4:.1f}">port: stroke, 6, 4, 2</text>')
out.append(f'<text class="n" x="{L + WIN*PX + 22}" y="{sy1(3.0)+4:.1f}">starboard: 7, 5, 3, bow</text>')
for m in range(0, int(WIN) - 1, 10):
    X = sx1(bow_now - m); Yb = TOP1 + H1
    out.append(f'<line class="tick" x1="{X:.1f}" y1="{Yb:.1f}" x2="{X:.1f}" y2="{Yb+5:.1f}"/>')
    out.append(f'<text class="m" x="{X:.1f}" y="{Yb+19:.1f}">{m} m</text>')

# -- panel 2: the same water, unpicked: one stave per seat --
STRETCH = 4.0              # the staves stretch across-the-lane distances, to show the arcs
STAVE = 86
TOP2 = TOP1 + H1 + 90
out.append(f'<text class="h" x="{L}" y="{TOP2 - 26}">the same water, unpicked, one seat to a line</text>')
order = [8, 7, 6, 5, 4, 3, 2, 1]
last_catch = max(x for s0, x, y, a in catches if s0 == 8)
X0_2 = last_catch - WIN + 1.5
def sx2(x, s): return L + (x - pin_x(s) + pin_x(8) - X0_2) * PX     # slid so a perfect crew lines up
def sy2(y, s):
    i = order.index(s)
    return TOP2 + i * STAVE + STAVE / 2 + (abs(y) - 2.75) * PX * STRETCH / 3.2
for i, s in enumerate(order):
    c = SEATS[s]
    yb = TOP2 + i * STAVE + STAVE / 2
    out.append(f'<line class="stave" x1="{L}" y1="{yb:.1f}" x2="{L + WIN*PX:.1f}" y2="{yb:.1f}"/>')
    label = c["name"] if s in (8, 1) else str(s)
    out.append(f'<text class="seatname" x="{L - 18}" y="{yb + 5:.1f}" fill="{c["col"]}">{label}</text>')
    out.append(f'<text class="n" x="{L + WIN*PX + 22}" y="{yb + 5:.1f}">{NOTE[s]}</text>')
    marks({s}, sx2, sy2, out)
# faint guides at stroke's catches, so the others can be read against them
for s0, x, y, age in catches:
    if s0 != 8: continue
    X = sx2(x, 8)
    if X < L: continue
    out.append(f'<line class="guide" x1="{X:.1f}" y1="{TOP2:.1f}" x2="{X:.1f}" y2="{TOP2 + 8*STAVE:.1f}"/>')
H = TOP2 + 8 * STAVE + 30

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="An eight seen from above, moving right, with the marks its blades leave on the water: puddles where each blade comes out, arcs of drips on the way to the next catch, one colour per seat. Below, the same marks pulled apart into eight lines, one per rower, so the crew can be read.">
<style>
path{{fill:none;stroke-width:1.1;stroke-linecap:round}}
.lane{{stroke:var(--faint,#b9b2a5);stroke-width:.6;stroke-dasharray:2 7}}
.stave{{stroke:var(--faint,#b9b2a5);stroke-width:.5;stroke-dasharray:1 5}}
.guide{{stroke:#b8432f;stroke-width:.6;opacity:.35}}
.tick{{stroke:var(--faint,#9a9284);stroke-width:.8}}
.m{{fill:var(--faint,#9a9284);font:13px Georgia,serif;text-anchor:middle}}
.h{{fill:var(--ink,#23303a);font:italic 17px Georgia,serif}}
.n{{fill:var(--faint,#8a8274);font:italic 14px Georgia,serif}}
.seatname{{font:15px Georgia,serif;text-anchor:end}}
.hull{{fill:var(--bg,#f3efe6);stroke:var(--ink,#23303a);stroke-width:1.2}}
.oar{{stroke:var(--ink,#23303a);stroke-width:1.2;opacity:.7}}
.seat{{fill:var(--ink,#23303a)}}
</style>
{chr(10).join(out)}
</svg>"""
open("eight.svg", "w").write(svg)
print(len(puddles), "puddles", sum(len(p) for _, p in arcs), "drips", f"{W:.0f}x{H:.0f}")

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The eight</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f3efe6;--ink:#23303a;--faint:#8a8274}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14181c;--ink:#d9e2e8;--faint:#7a848e}}}}
html,body{{margin:0;background:var(--bg);color:var(--ink)}}
body{{font-family:"EB Garamond",Georgia,serif;font-size:19px;line-height:1.5;padding:8vh 16px 12vh}}
header,footer{{max-width:34em;margin:0 auto}}
h1{{font-weight:400;font-style:italic;font-size:1.5em;margin:0 0 .2em}}
.sub{{color:var(--faint);margin:0 0 2.5em}}
figure{{margin:0 auto;max-width:{W:.0f}px;overflow-x:auto}}
figure svg{{width:100%;min-width:900px;height:auto;display:block}}
footer{{margin-top:3em;color:var(--faint);font-size:.85em}}
footer p{{margin:0 0 1em}}
</style></head>
<body>
<header><h1>The eight</h1>
<p class="sub">a crew of eight, as the water remembers it, one colour to a seat</p></header>
<figure>
{svg}
</figure>
<footer>
<p>Seen from above, the boat moving right at about thirty-six strokes a minute. Each blade leaves a puddle where it comes out of the water, a pair of small whirlpools turning opposite ways, and then, on the way forward to the next catch, an arc of drips from the feathered blade. A few drops mark where it goes back in. Stroke side (stroke, 6, 4, 2) is above the boat, bow side (7, 5, 3, bow) below.</p>
<p>All together, the eight blades tile the water into a pretty, unreadable braid. Underneath, the same marks are pulled apart, one rower to a line, each slid along by its distance from the stroke seat so that a perfect crew would line up on the faint red guides. The lines are stretched across the lane about four times so the arcs show. Then the crew starts to read: who is late, who is long, who is short, who digs.</p>
<p>It is a model, not a recording, and the crew is invented. The water may still be wrong in ways only a rower would see.</p>
</footer>
</body></html>"""
open("index.html", "w").write(html)
