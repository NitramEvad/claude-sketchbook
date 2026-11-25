# Do rivers find the soft rock? And how many cut straight through the hard ridges?
import numpy as np, json, sys
from scipy import ndimage

def measure(path, thr_ch=1e6, thr_gap=8e6, suffix=""):
    d = np.load(path); h = d["h"+suffix]; A = d["A"+suffix]; rec = d["rec"+suffix]; rk = d["r"+suffix] if suffix else d["rock"]
    n = h.shape[0]; out = d["out"].ravel(); idx = np.arange(n*n)
    rf = rk.ravel()
    land = ~out
    ch = (A > thr_ch) & (rec != idx) & land
    dist = np.hypot(rec//n - idx//n, rec % n - idx % n)
    res = {}
    exposed = land & (rf > 0)
    res["soft_share_of_ground"] = round(float((rf[exposed] == 1).mean()), 3) if exposed.any() else None
    res["cover_share_of_ground"] = round(float((rf[land] == 0).mean()), 3)
    che = ch & (rf > 0)
    if che.any():
        res["soft_share_of_river_length"] = round(float(dist[che & (rf == 1)].sum() / dist[che].sum()), 3)
        # big rivers only
        big = che & (A > thr_gap)
        res["soft_share_of_big_river_length"] = round(float(dist[big & (rf == 1)].sum() / dist[big].sum()), 3)
    # direction: share of river length running east-west (along the strike) vs north-south (across it)
    di = rec//n - idx//n; dj = rec % n - idx % n
    for name, sel in [("soft", ch & (rf == 1)), ("hard", ch & (rf == 2)), ("cover", ch & (rf == 0))]:
        if sel.sum() < 20: continue
        ew = dist[sel & (di == 0)].sum(); ns = dist[sel & (dj == 0)].sum(); tot = dist[sel].sum()
        res[f"{name}_rivers_east_west_share"] = round(float(ew/tot), 3)
        res[f"{name}_rivers_north_south_share"] = round(float(ns/tot), 3)
    # water gaps: for every hard band that crosses most of the map, count the rivers that leave it southwards
    hard = (rk == 2) & ~d["out"]
    lab, nl = ndimage.label(hard, structure=np.ones((3, 3)))
    gaps = []; gap_cells = []
    labf = lab.ravel()
    for k in range(1, nl+1):
        cols = np.unique(np.where(lab == k)[1])
        if len(cols) < 0.6*n: continue          # only ridges that run most of the way across
        sel = (labf == k) & (A > thr_gap) & (rec != idx)
        exits = np.where(sel & (labf[rec] != k) & (rec//n > idx//n))[0]
        # one river can leave a ridge by two or three neighbouring cells; count exits within 1.5 km as one gap
        exits = exits[np.argsort(A[exits])[::-1]]; kept = []
        for e in exits:
            if all(np.hypot(e//n - q//n, e % n - q % n) > 15 for q in kept): kept.append(e)
        gaps.append(len(kept)); gap_cells += kept
    res["ridges"] = len(gaps); res["gaps_per_ridge"] = gaps
    res["mean_gaps_per_ridge"] = round(float(np.mean(gaps)), 2) if gaps else None
    outl = np.where(out)[0]
    res["rivers_reaching_sea_over_8km2"] = int((A[outl] > thr_gap).sum())
    res["biggest_basin_km2"] = round(float(A[outl].max()/1e6), 1)
    res["mean_height"] = round(float(h.ravel()[land].mean()), 1); res["max_height"] = round(float(h.max()), 1)
    return res, np.array(gap_cells)

if __name__ == "__main__":
    allres = {}
    for name in sys.argv[1:]:
        d = np.load(f"run_{name}.npz")
        r, g = measure(f"run_{name}.npz"); np.save(f"gaps_{name}.npy", g)
        r["history"] = {}
        for k in sorted(int(f[1:]) for f in d.files if f.startswith("h") and f[1:].isdigit()):
            rr, _ = measure(f"run_{name}.npz", suffix=str(k))
            r["history"][k] = {kk: rr.get(kk) for kk in ("cover_share_of_ground", "soft_share_of_ground", "soft_share_of_river_length", "mean_gaps_per_ridge", "gaps_per_ridge", "rivers_reaching_sea_over_8km2")}
        allres[name] = r
    print(json.dumps(allres, indent=1))
    json.dump(allres, open("numbers.json", "w"), indent=1)
