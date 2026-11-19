# Draws preview.svg: the pair's loudness for one second after a strike, at each point in the story.
import math
rows = [(-1,'Pour'),(31,'Rough'),(9,'Closer'),(1,'Too close'),(7,'Seven'),(5,'Cold'),(7,'Filed again')]
W, H, x0, x1 = 1200, 630, 230, 1150
rh = 74; y0 = 60
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       f'<rect width="{W}" height="{H}" fill="#efe8da"/>']
for i,(b,lab) in enumerate(rows):
    cy = y0 + i*rh + rh/2
    top, bot = [], []
    for k in range(0, 461):
        t = k/460; x = x0 + t*(x1-x0)
        d = math.exp(-t/0.9)
        a = 0.5*d if b < 0 else abs(math.cos(math.pi*b*t))*d
        h = a*rh*0.44
        top.append(f'{x:.1f},{cy-h:.1f}'); bot.append(f'{x:.1f},{cy+h:.1f}')
    col = '#4f6f7a' if b < 0 else ('#a8652a' if b == 7 else '#b99a78')
    out.append(f'<polygon points="{" ".join(top+bot[::-1])}" fill="{col}"/>')
    sub = 'one key' if b < 0 else f'{b} a second'
    out.append(f'<text x="{x0-24}" y="{cy-2}" text-anchor="end" font-family="Georgia,serif" font-size="22" fill="#26231e">{lab}</text>')
    out.append(f'<text x="{x0-24}" y="{cy+22}" text-anchor="end" font-family="Georgia,serif" font-style="italic" font-size="17" fill="#7d776c">{sub}</text>')
out.append('</svg>')
open('preview.svg','w').write('\n'.join(out))
