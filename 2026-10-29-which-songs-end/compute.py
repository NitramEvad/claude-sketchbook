"""For every elementary CA rule that keeps silence silent (000 -> 0) and every
ring width n, find how many steps it takes until *every* starting pattern has
gone dark, or None if some pattern never does. Writes silence.json."""
import json, sys
import numpy as np

MAXN = int(sys.argv[1]) if len(sys.argv) > 1 else 16

def step(s, rule, n):
    mask = (1 << n) - 1
    l = ((s << 1) | (s >> (n - 1))) & mask   # left neighbour in each bit
    r = ((s >> 1) | (s << (n - 1))) & mask
    c = s
    out = np.zeros_like(s)
    for k in range(8):
        if rule >> k & 1:
            a = l if k & 4 else ~l
            b = c if k & 2 else ~c
            d = r if k & 1 else ~r
            out |= a & b & d
    return out & mask

def silence(rule, n):
    S = np.arange(1 << n, dtype=np.uint32)
    t = 0
    while True:
        if S.size == 1 and S[0] == 0:
            return t
        T = np.unique(step(S, rule, n))
        t += 1
        if T.size == S.size:
            return None
        S = T

if __name__ == "__main__":
  res = {}
  for rule in range(0, 128, 2):  # 111 -> 1 keeps all-ones lit forever
    res[rule] = [silence(rule, n) for n in range(1, MAXN + 1)]
    print(rule, res[rule], flush=True)
  json.dump({"maxn": MAXN, "rules": res}, open("silence.json", "w"))
