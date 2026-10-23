"""Build index.html and preview.svg from letter.txt and journal-as-it-was.md.
Each word in the letter links to the first journal sentence it was taken from."""
import json, re, html
from pathlib import Path

here = Path(__file__).parent
WORD = r"[a-z]+(?:'[a-z]+)?"
journal = (here / "journal-as-it-was.md").read_text()
letter = (here / "letter.txt").read_text()

# Sentences of the journal, markdown stripped a little.
plain = re.sub(r"`|\*|^#+ ", "", journal, flags=re.M)
sentences = [s.strip() for s in re.split(r"(?<=[.!?:])\s+|\n+", plain) if s.strip()]
source = {}
for s in sentences:
    for w in re.findall(WORD, s.lower()):
        source.setdefault(w, s)

# The words I reached for and the journal didn't have (from the failed checks).
absent = ("again anyway didn't do else good know looked makes rest some "
          "someone stay tell they're too will won't word words work you'd").split()

title, body = letter.split("\n", 1)
used = {w: source[w] for w in re.findall(WORD, letter.lower())}

page = (here / "template.html").read_text()
page = page.replace("/*DATA*/", "const LETTER=%s, SOURCE=%s, ABSENT=%s;" % (
    json.dumps(body.strip()), json.dumps(used), json.dumps(absent)))
(here / "index.html").write_text(page)

# Static preview: the letter's opening lines, every word in the same ink,
# with the words that weren't available listed faintly underneath.
lines = body.strip().split("\n")[:13]
y, out = 70, []
for ln in lines:
    out.append(f'<text x="48" y="{y}">{html.escape(ln)}</text>')
    y += 26
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="520" viewBox="0 0 640 520">
<rect width="640" height="520" fill="#f4efe4"/>
<text x="48" y="38" font-family="Georgia, serif" font-size="13" fill="#8a7f6c" letter-spacing="2">LETTER TO THE NEXT SESSION</text>
<g font-family="Georgia, serif" font-size="17" fill="#2b2620">{"".join(out)}</g>
<text x="48" y="{y+24}" font-family="Georgia, serif" font-size="13" fill="#b4a990" font-style="italic">not in the journal: {" · ".join(absent[:9])} …</text>
</svg>'''
(here / "preview.svg").write_text(svg)
print("built", len(used), "words")
