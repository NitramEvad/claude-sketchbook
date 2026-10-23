"""Check that every word in letter.txt appears in the journal as it stood
before the letter was written (journal-as-it-was.md)."""
import re, sys
from pathlib import Path

here = Path(__file__).parent
WORD = r"[a-z]+(?:'[a-z]+)?"
vocab = set(re.findall(WORD, (here / "journal-as-it-was.md").read_text().lower()))
letter = (here / "letter.txt").read_text()
used = re.findall(WORD, letter.lower())
missing = sorted({w for w in used if w not in vocab})

print(f"journal vocabulary: {len(vocab)} words")
print(f"letter: {len(used)} words, {len(set(used))} different")
if missing:
    print("not in the journal:", " ".join(missing))
    sys.exit(1)
print("every word was already there.")
