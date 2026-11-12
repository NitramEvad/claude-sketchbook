# Builds index.html from story.txt. Run: python3 make.py
import html, re
src = open('story.txt').read()
secs = []
for block in src.split('## ')[1:]:
    head, body = block.split('\n', 1)
    name, h = [s.strip() for s in head.split('|')]
    paras = [p.strip() for p in body.strip().split('\n\n') if p.strip()]
    secs.append((name, int(h), paras))

def esc(t):
    t = html.escape(t, quote=False)
    return re.sub(r'"([^"]*)"', r'&ldquo;\1&rdquo;', t).replace("'", '&rsquo;')

parts = []
for name, h, paras in secs:
    parts.append(f'<section data-h="{h}"><h2>{esc(name)}</h2>')
    parts += [f'<p>{esc(p)}</p>' for p in paras]
    parts.append('</section>')
body = '\n'.join(parts)
words = sum(len(p.split()) for _, _, ps in secs for p in ps)
page = open('template.html').read().replace('{{BODY}}', body).replace('{{WORDS}}', f'{round(words, -2):,}')
open('index.html', 'w').write(page)
print('sections', len(secs), 'words', words)
