# Builds index.html from story.txt. Sections: "@ <beats per second> | <title>".
import html, re
src = open('story.txt').read().strip().split('\n')
secs = []
for line in src:
    if line.startswith('@'):
        b, t = line[1:].split('|')
        secs.append({'b': int(b), 't': t.strip(), 'p': []})
    elif line.strip():
        secs[-1]['p'].append(line.strip())
def esc(x):
    x = html.escape(x, quote=False)
    x = re.sub(r"(\w)'", r"\1&rsquo;", x); x = x.replace("'", "&lsquo;")
    return x
out = []
for i, s in enumerate(secs):
    lab = 'one key' if i == 0 else f"{s['b']} a second"
    btn = '' if i == 0 else f' <button class="hear" data-b="{s["b"]}" aria-label="Hear the pair {s["b"]} beats a second apart">hear</button>'
    body = '\n'.join(f'<p>{esc(p)}</p>' for p in s['p'])
    out.append(f'<section data-b="{s["b"] if i else -1}"><h2>{esc(s["t"])} <span>· {lab}</span>{btn}</h2>\n{body}\n</section>')
page = open('template.html').read().replace('<!--STORY-->', '\n'.join(out))
open('index.html', 'w').write(page)
print(len(secs), 'sections')
