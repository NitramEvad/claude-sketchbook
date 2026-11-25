# Who decides where the gaps go: the rock, or the rivers that were there before the rock showed?
# For each run's final water gaps, how far is each from the nearest big river of the old cover-era
# landscape (step 360, when the whole map was still soft cover)? Same rock in every run; only the
# starting noise (seed) and the cover differ.
import numpy as np, json
n = 400; dx = 0.1  # km
THR = 40e6         # a "big river" on the cover: draining more than 40 km²
runs = ["covered", "covered7", "bare"]
old = {}
for r in ["covered", "covered7"]:
    d = np.load(f"run_{r}.npz"); A = d["A360"]; rec = d["rec360"]; idx = np.arange(n*n)
    c = np.where((A > THR) & (rec != idx))[0]
    old[r] = np.stack([c // n, c % n], 1)
res = {}
rng = np.random.default_rng(0)
for r in runs:
    g = np.load(f"gaps_{r}.npy").astype(int)
    pts = np.stack([g // n, g % n], 1)
    res[r] = {}
    for o, P in old.items():
        dd = np.sqrt(((pts[:, None, :] - P[None, :, :])**2).sum(-1)).min(1) * dx
        res[r][f"to_{o}_old_rivers_km"] = [round(float(v), 1) for v in dd]
        res[r][f"to_{o}_median_km"] = round(float(np.median(dd)), 2)
# baseline: random points on the final hard ridges of the covered run
d = np.load("run_covered.npz"); hard = np.where((d["rock"].ravel() == 2) & ~d["out"].ravel())[0]
pick = rng.choice(hard, 2000, replace=False); pts = np.stack([pick // n, pick % n], 1)
for o, P in old.items():
    dd = np.sqrt(((pts[:, None, :] - P[None, :, :])**2).sum(-1)).min(1) * dx
    res[f"random_ridge_points_to_{o}_median_km"] = round(float(np.median(dd)), 2)
print(json.dumps({k: (v if not isinstance(v, dict) else {a: b for a, b in v.items() if "median" in a}) for k, v in res.items()}, indent=1))
json.dump(res, open("inherit.json", "w"), indent=1)
