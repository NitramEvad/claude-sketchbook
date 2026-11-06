"""Builds index.html (essay + inline map of promises) from promises.py.
Run: python3 make.py"""
from html import escape
from promises import PROMISES

def road_svg():
    W, top, step = 700, 46, 46
    H = top + step * len(PROMISES) + 30
    cx = 335
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="A road map of sixteen nights: at each junction, the line written the night before, and what got built there.">']
    # road: gentle wiggle
    pts = []
    for i in range(len(PROMISES) * 4 + 5):
        y = top - 30 + i * step / 4
        x = cx + 16 * __import__("math").sin(i * 0.3)
        pts.append(f"{x:.1f},{y:.1f}")
    o.append(f'<polyline class="road" points="{" ".join(pts)}"/>')
    o.append(f'<polyline class="roadc" points="{" ".join(pts)}"/>')
    o.append(f'<text class="hd" x="{cx-26}" y="18" text-anchor="end">written the night before</text>')
    o.append(f'<text class="hd" x="{cx+26}" y="18">built there</text>')
    for i, (d, made, said, did, st) in enumerate(PROMISES):
        y = top + i * step
        x = cx + 16 * __import__("math").sin((i * 4 + 4) * 0.3)
        o.append(f'<line class="spur" x1="{x:.1f}" y1="{y}" x2="{cx+18}" y2="{y}"/>')
        o.append(f'<line class="spur" x1="{x:.1f}" y1="{y}" x2="{cx-18}" y2="{y}"/>')
        o.append(f'<text class="said" x="{cx-26}" y="{y-3}" text-anchor="end">{escape(said)}</text>')
        o.append(f'<text class="date" x="{cx-26}" y="{y+11}" text-anchor="end">after {d} · {escape(made)}</text>')
        bx = cx + 26
        if st == "kept":
            o.append(f'<rect class="b kept" x="{bx}" y="{y-8}" width="12" height="10"/><path class="b kept" d="M{bx-1} {y-8} L{bx+6} {y-14} L{bx+13} {y-8}Z"/>')
        elif st == "half":
            o.append(f'<rect class="b half" x="{bx}" y="{y-8}" width="12" height="10"/><path class="b half" d="M{bx-1} {y-8} L{bx+6} {y-14} L{bx+13} {y-8}Z"/>')
        else:
            o.append(f'<rect class="b ghost" x="{bx}" y="{y-8}" width="12" height="10"/><path class="b ghost" d="M{bx-1} {y-8} L{bx+6} {y-14} L{bx+13} {y-8}Z"/>')
        cls = "did" + ("" if st == "kept" else " off")
        o.append(f'<text class="{cls}" x="{bx+20}" y="{y+2}">{escape(did)}</text>')
    yb = top + step * len(PROMISES) - 4
    o.append(f'<text class="date" x="{cx+26}" y="{yb}">■ kept   ▣ only the “away from” part   □ something else</text>')
    o.append('</svg>')
    return "\n".join(o)

ESSAY = open("essay.html").read()
PAGE = open("template.html").read().replace("<!--ROAD-->", road_svg()).replace("<!--ESSAY-->", ESSAY)
open("index.html", "w").write(PAGE)
print("wrote index.html")
