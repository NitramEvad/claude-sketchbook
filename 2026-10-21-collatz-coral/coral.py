"""Grow a Collatz coral as an SVG.

Every whole number n <= N is followed backwards from 1 to n.
Even steps bend one way, odd steps bend the other, so numbers that
share a history share a branch. Branch thickness is how many of the
starting numbers pass through that stretch.
"""
import math, sys
from collections import defaultdict

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
EVEN_TURN = math.radians(float(sys.argv[2]) if len(sys.argv) > 2 else 9.0)
ODD_TURN = math.radians(float(sys.argv[3]) if len(sys.argv) > 3 else -16.0)
STEP = 7.0
W, H = 1200, 1500

def nxt(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1

# which numbers pass through each value
count = defaultdict(int)
parent = {}
for s in range(2, N + 1):
    n = s
    while n != 1:
        count[n] += 1
        if n in parent:
            # the rest of the path is known; still count it
            m = parent[n]
            while m != 1:
                count[m] += 1
                m = parent[m]
            break
        parent[n] = nxt(n)
        n = parent[n]

pos = {1: (0.0, 0.0, math.pi / 2)}
def place(n):
    stack = []
    while n not in pos:
        stack.append(n)
        n = parent[n]
    for m in reversed(stack):
        x, y, a = pos[parent[m]]
        a += EVEN_TURN if m % 2 == 0 else ODD_TURN
        pos[m] = (x + STEP * math.cos(a), y + STEP * math.sin(a), a)

for n in parent:
    place(n)

# stand it upright: turn the whole thing so its centre of mass sits above the root
cx = sum(p[0] for p in pos.values()) / len(pos)
cy = sum(p[1] for p in pos.values()) / len(pos)
r = math.pi / 2 - math.atan2(cy, cx)
cr, sr = math.cos(r), math.sin(r)
pos = {n: (x * cr - y * sr, x * sr + y * cr, a) for n, (x, y, a) in pos.items()}

xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
pad = 60
scale = min((W - 2 * pad) / (maxx - minx), (H - 2 * pad) / (maxy - miny))
def tx(x, y):
    return ((x - minx) * scale + pad + (W - 2 * pad - (maxx - minx) * scale) / 2,
            H - pad - (y - miny) * scale)

# bucket edges by thickness so the file stays small
buckets = defaultdict(list)
maxc = max(count.values())
for n, p in parent.items():
    c = count[n]
    b = min(11, int(round(math.log2(c)))) if c > 1 else 0
    buckets[b].append((tx(*pos[p][:2]), tx(*pos[n][:2])))

def colour(t):
    # violet at the fine tips, coral in the branches, pale bone at the trunk
    stops = [(0.0, (120, 90, 190)), (0.35, (225, 95, 130)),
             (0.7, (255, 150, 120)), (1.0, (255, 232, 205))]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return "#%02x%02x%02x" % tuple(int(a + (b - a) * u) for a, b in zip(c0, c1))
    return "#%02x%02x%02x" % stops[-1][1]

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<defs><radialGradient id="sea" cx="50%" cy="85%" r="90%">'
       '<stop offset="0" stop-color="#14304a"/><stop offset="1" stop-color="#050b16"/>'
       '</radialGradient></defs>',
       f'<rect width="{W}" height="{H}" fill="url(#sea)"/>',
       '<g fill="none" stroke-linecap="round">']
for b in sorted(buckets):
    t = b / 11
    width = 0.35 + 0.55 * b ** 1.25
    opacity = 0.55 + 0.45 * t
    d = "".join(f"M{a[0]:.1f} {a[1]:.1f}L{c[0]:.1f} {c[1]:.1f}" for a, c in buckets[b])
    out.append(f'<path d="{d}" stroke="{colour(t)}" stroke-width="{width:.2f}" stroke-opacity="{opacity:.2f}"/>')
out.append('</g>')
out.append(f'<text x="{W-pad}" y="{H-24}" fill="#6f8aa3" font-family="Georgia, serif" font-size="15" text-anchor="end" font-style="italic">every n &#8804; {N}, traced home to 1</text>')
out.append('</svg>')
sys.stdout.write("\n".join(out))
print(f"nodes {len(parent)} max count {maxc}", file=sys.stderr)
