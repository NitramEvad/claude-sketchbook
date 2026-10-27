"""Check that every word in poem.txt appears exactly once in the journal as it
stood before the poem was written (journal-as-it-was.md), that the poem uses
each of them only once, and say which entry each word was said in."""
import re, sys
from collections import Counter
from pathlib import Path

here = Path(__file__).parent
WORD = r"[a-z]+(?:'[a-z]+)?"
journal = (here / "journal-as-it-was.md").read_text()
counts = Counter(re.findall(WORD, journal.lower()))
hapax = {w for w, n in counts.items() if n == 1}

# which dated entry (or shelf) each word lives in
where, section = {}, "intro"
for line in journal.splitlines():
    m = re.match(r"## (\d{4}-\d\d-\d\d|Ideas shelf)", line)
    if m:
        section = m.group(1)
    for w in re.findall(WORD, line.lower()):
        where.setdefault(w, section)

poem = (here / "poem.txt").read_text()
used = re.findall(WORD, poem.lower())
bad = sorted({w for w in used if w not in hapax})
twice = sorted(w for w, n in Counter(used).items() if n > 1)

print(f"journal: {len(counts)} different words, {len(hapax)} said exactly once")
print(f"poem: {len(used)} words, each one of those")
for w in used:
    print(f"  {w:12} {where[w] if w in where else '?'}")
if bad or twice:
    print("not said-once:", " ".join(bad), "| repeated in poem:", " ".join(twice))
    sys.exit(1)
print(f"all said once. writing them down spends {len(used)} of {len(hapax)}.")
