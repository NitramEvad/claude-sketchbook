import numpy as np, json
d = np.load(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "run_400_21_coast.npz"); h = d["h"]; A = d["A"]; rec = d["rec"]; n = h.shape[0]; dx=100.0
flat = h.ravel(); order = np.argsort(flat)[::-1]   # high to low
idx = np.arange(n*n)
dist = np.where(rec!=idx, np.hypot((rec//n - idx//n), (rec%n - idx%n))*dx, 0)
L = np.zeros(n*n)                      # longest upstream flow path ending at cell
for c in order:
    r = rec[c]
    if r != c: L[r] = max(L[r], L[c] + dist[c])
# Hack's law over channel cells
ch = A > 1e6   # > 1 km^2
sel = ch & (L>0)
hk, hc = np.polyfit(np.log10(A[sel]), np.log10(L[sel]), 1)
# main stem of the biggest basin
outl = np.where(d["out"].ravel())[0]
big = outl[np.argmax(A[outl])]
# slope-area
S = np.where(rec!=idx, (flat - flat[rec])/np.maximum(dist,1), 0)
s2 = ch & (S>0)
th, tc = np.polyfit(np.log10(A[s2]), np.log10(S[s2]), 1)
# Strahler
order_s = np.zeros(n*n, int); maxin = np.zeros(n*n,int); cnt = np.zeros(n*n,int)
for c in order:
    if not ch[c]: continue
    o = order_s[c] if order_s[c] else 1
    if maxin[c]: o = maxin[c] + (1 if cnt[c]>=2 else 0)
    order_s[c] = o
    r = rec[c]
    if r == c: continue
    if o > maxin[r]: maxin[r] = o; cnt[r] = 1
    elif o == maxin[r]: cnt[r] += 1
# count streams of each order: segments start where order changes from upstream
nseg = {}
for c in np.where(ch)[0]:
    r = rec[c]
    if r == c or order_s[r] != order_s[c] or not ch[r]:
        nseg[order_s[c]] = nseg.get(order_s[c],0)+1
ks = sorted(nseg); Rb = [nseg[k]/nseg[k+1] for k in ks[:-1]]
uplifted = 1e-3*2000*len(d["mean"])
res = dict(hack_exponent=round(hk,3), hack_coef=round(10**hc,3), slope_area_exponent=round(th,3),
  strahler_counts={int(k):int(nseg[k]) for k in ks}, bifurcation_ratios=[round(x,2) for x in Rb],
  mean_height=round(float(h[~d['out']].mean()),1), max_height=round(float(h.max()),1),
  rock_uplifted_m=uplifted, fraction_remaining=round(float(h[~d['out']].mean())/uplifted,4),
  biggest_basin_km2=round(A[big]/1e6,1), biggest_main_stem_km=round(L[big]/1e3,1), n_outlets_draining=int((A[outl]>1e6).sum()))
print(json.dumps(res, indent=1)); json.dump(res, open("numbers.json","w"), indent=1) if len(__import__("sys").argv)<2 else None
np.save("L.npy", L)
np.save("ord.npy", order_s)
