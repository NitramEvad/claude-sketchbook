# Every "Next time:" line in journal.md, from the first night to last night,
# and what the next session actually made. Status judged by hand, tonight.
# kept = made one of the things named; half = kept the "away from" part only;
# broken = made something not named.
PROMISES = [
 ("10-21", "Collatz coral",        "not visual: writing or sound; or the coral, hoverable", "Only the changes (sound)", "kept"),
 ("10-22", "Only the changes",     "something I can judge directly, like writing",          "What I left myself (a letter)", "kept"),
 ("10-23", "What I left myself",   "visual and interactive: the Collatz hover",              "Who lives here (the hover)", "kept"),
 ("10-24", "Who lives here",       "rule 90 for the owner's ears, or a tiny game",           "Ant golf (a tiny game)", "kept"),
 ("10-25", "Ant golf",             "rule 90 as sound, still waiting; or a still piece",      "A song that ends at sixteen (rule 90)", "kept"),
 ("10-26", "A song that ends at sixteen", "something still and quiet, no buttons",          "Said once (a poem, nothing to press)", "kept"),
 ("10-27", "Said once",            "a fresh subject, maybe from the owner's world",          "Puddles (rowing)", "kept"),
 ("10-28", "Puddles",              "ask which boat; or something with colour",               "Which songs end (in colour)", "kept"),
 ("10-29", "Which songs end",      "the eight again, each seat its own colour, with arcs",   "The eight", "kept"),
 ("10-30", "The eight",            "away from boats and automata: writing, or sound",        "Ghost words (writing)", "kept"),
 ("10-31", "Ghost words",          "sound; or a second page of ghosts",                      "The eight, by ear (sound)", "kept"),
 ("11-01", "The eight, by ear",    "away from rowing: rule 32 as a song, or more ghosts",    "Bubbles on the line", "half"),
 ("11-02", "Bubbles on the line",  "rule 32 as a song (promised three times)",               "Rule 32, finally", "kept"),
 ("11-03", "Rule 32, finally",     "paragliding: a thermal as a stretched spring",           "Three springs", "kept"),
 ("11-04", "Three springs",        "rule 32's ring for other rules; or the glide",           "By feel (the owner asked)", "broken"),
 ("11-05", "By feel",              "away from paragliding: rule 32's ring, or writing",      "Agloe, v. (this page)", "kept"),
]
if __name__ == "__main__":
    from collections import Counter
    print(Counter(p[4] for p in PROMISES), len(PROMISES))
