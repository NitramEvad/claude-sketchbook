# Draws preview.svg (then rendered to preview.png with Chromium).
import math, random
random.seed(12)
W,H=1200,630
o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
'<defs><linearGradient id="sky" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#e6d7bd"/><stop offset=".35" stop-color="#dfe6ea"/><stop offset="1" stop-color="#e9eff5"/></linearGradient>',
'<radialGradient id="warm" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#d98a5c" stop-opacity=".35"/><stop offset="1" stop-color="#d98a5c" stop-opacity="0"/></radialGradient></defs>',
f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
G=560
o.append(f'<rect y="{G}" width="{W}" height="{H-G}" fill="#5a4632"/>')
for i in range(14):
    o.append(f'<line x1="0" y1="{G+4+i*5}" x2="{W}" y2="{G+4+i*5}" stroke="#7a604a" stroke-width="1.4" opacity=".7"/>')
for x in range(0,W,9):
    o.append(f'<circle cx="{x}" cy="{G-2}" r="{7+random.random()*5:.1f}" fill="#4f6142" opacity=".9"/>')
x0,x1,base=430,640,170
top=base+30
def col(y):  # centre of the leaning column at height y
    f=(G-10-y)/(G-10-top); return x0+(x1-x0)*f**1.2+math.sin(f*7)*8, f
for k in range(26):
    y=G-10-k/25*(G-10-top); x,f=col(y); r=26+f*40
    o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r:.0f}" ry="{r*0.8:.0f}" fill="url(#warm)"/>')
for (dx,dy,r) in [(-80,0,40),(-40,-30,52),(10,-45,60),(60,-20,48),(95,0,36),(0,0,50),(40,2,44)]:
    o.append(f'<circle cx="{x1+dx}" cy="{base-25+dy}" r="{r}" fill="#fbfbfa"/>')
o.append(f'<rect x="{x1-120}" y="{base-25}" width="251" height="50" fill="#fbfbfa"/>')
o.append(f'<line x1="{x1-120}" y1="{base+25}" x2="{x1+131}" y2="{base+25}" stroke="#c9ced3" stroke-width="2"/>')
pts=[]
for i in range(500):
    t=i/499; a=t*2*math.pi*6
    y=470-t*(470-base-40); cx,f=col(y); r=22+f*26
    pts.append((cx+r*math.cos(a), y+r*0.25*math.sin(a)))
o.append('<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'" fill="none" stroke="#b5562e" stroke-width="1.6" stroke-dasharray="5 4" opacity=".85"/>')
x,y=pts[-1]; y-=6
o.append(f'<path d="M{x-22},{y-14} Q{x},{y-24} {x+22},{y-14}" fill="none" stroke="#b5562e" stroke-width="4" stroke-linecap="round"/>')
o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#26231e"/>')
bx,by=560,335
o.append(f'<path d="M{bx-18},{by-4} Q{bx-8},{by-10} {bx},{by} Q{bx+8},{by-10} {bx+18},{by-4}" fill="none" stroke="#26231e" stroke-width="2.2"/>')
o.append('<path d="M452,505 q6,-14 2,-30" fill="none" stroke="#7d776c" stroke-width=".8"/><circle cx="452" cy="506" r="1.8" fill="#26231e"/>')
o.append('<text x="60" y="110" font-family="Georgia, serif" font-size="64" fill="#26231e">Release</text>')
o.append('<text x="62" y="148" font-family="Georgia, serif" font-style="italic" font-size="22" fill="#7d776c">a short story, told by a thermal</text>')
o.append('</svg>')
open('preview.svg','w').write('\n'.join(o))
