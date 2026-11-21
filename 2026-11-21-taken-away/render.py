import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
d = np.load("run_400_21_coast.npz"); n = d["h"].shape[0]; out = d["out"]
L = np.load("L.npy")
num = json.load(open("numbers.json"))
PAPER = "#f3eee3"; INK = "#2b2a28"; WATER = "#2f5f8f"; SEA = "#c9d6dc"
tint = LinearSegmentedColormap.from_list("t", ["#d9dcc4", "#e8dfc4", "#dcc9a8", "#c9b59a", "#efe9e0"])

def shade(h):
    gy, gx = np.gradient(h, 100.0)
    az, alt = np.radians(315), np.radians(35)
    slope = np.arctan(1.1*np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    s = np.sin(alt)*np.cos(slope) + np.cos(alt)*np.sin(slope)*np.cos(az-aspect)
    return np.clip(s, 0, 1)

def plate(ax, h, A=None, rec=None, hmax=800, thr=1.2e6, wscale=1.0):
    base = tint(np.clip(h/hmax, 0, 1))[..., :3]
    s = shade(h)[..., None]
    rgb = base*(0.45 + 0.65*s)
    rgb[out] = matplotlib.colors.to_rgb(SEA)
    ax.imshow(np.clip(rgb, 0, 1), interpolation="bilinear", extent=(0, n, n, 0))
    if A is not None:
        idx = np.where((A > thr) & (rec != np.arange(n*n)))[0]
        r = rec[idx]
        segs = np.stack([np.stack([idx % n + .5, idx//n + .5], 1), np.stack([r % n + .5, r//n + .5], 1)], 1)
        w = wscale*0.35*(A[idx]/thr)**0.4
        ax.add_collection(LineCollection(segs, linewidths=np.minimum(w, 4.2), colors=WATER, capstyle="round", alpha=0.95))
    ax.set_xlim(0, n); ax.set_ylim(n, 0); ax.set_axis_off()

plt.rcParams.update({"font.family": "DejaVu Serif", "text.color": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.edgecolor": INK})
fig = plt.figure(figsize=(10, 15.2), facecolor=PAPER)
fig.text(0.07, 0.962, "Taken away", fontsize=30, weight="bold")
fig.text(0.07, 0.94, "A range of hills raised a millimetre a year for six million years, and carved by its own rivers.\n"
         "Nothing was drawn. Every valley is rock the water carried to the sea along the bottom edge.", fontsize=10.5, va="top", linespacing=1.5)
ax = fig.add_axes([0.07, 0.355, 0.86, 0.545])
plate(ax, d["h"], d["A"], d["rec"])
# scale bar
ax.plot([10, 110], [n-12, n-12], color=INK, lw=2, solid_capstyle="butt"); ax.text(60, n-16, "10 km", ha="center", fontsize=9)
ax.text(n-6, n-5, "sea", ha="right", va="bottom", fontsize=9, style="italic", color="#4a5a62")
# time strip
snaps = [("snap60", "120 thousand years"), ("snap150", "300 thousand"), ("snap360", "720 thousand"), ("snap900", "1.8 million")]
for i, (k, lab) in enumerate(snaps):
    a = fig.add_axes([0.07 + i*0.2225, 0.205, 0.19, 0.115])
    hs = d[k]
    plate(a, hs, hmax=800)
    steps = int(k[4:]); up = steps*2.0
    a.set_title(f"{lab}\n{100*(1-hs[~out].mean()/up):.0f}% already gone", fontsize=8.5, pad=4)
# bars: what came up vs what is left
ab = fig.add_axes([0.07, 0.04, 0.30, 0.11]); ab.set_facecolor(PAPER)
up = num["rock_uplifted_m"]; left = num["mean_height"]
ab.barh([1], [up], color="#d8ccb6", height=0.55); ab.barh([0], [left], color="#9c8466", height=0.55)
ab.text(up*0.98, 1, f"rock raised: {up/1000:.0f} km", ha="right", va="center", fontsize=9)
ab.text(left + 120, 0, f"still here: {left:.0f} m ({100*left/up:.0f}%)", ha="left", va="center", fontsize=9)
ab.set_yticks([]); ab.set_xlim(0, up*1.02); ab.set_xticks([0, 2000, 4000, 6000]); ab.set_xticklabels(["0", "2", "4", "6 km"], fontsize=8)
for s in ["top", "right", "left"]: ab.spines[s].set_visible(False)
ab.set_title("Average column of rock, per place", fontsize=9.5, loc="left")
# Hack's law
ah = fig.add_axes([0.47, 0.04, 0.22, 0.11]); ah.set_facecolor(PAPER)
A = d["A"]/1e6; sel = (A > 1) & (L > 0)
rng = np.random.default_rng(0); pick = rng.choice(np.where(sel)[0], 2500, replace=False)
ah.loglog(A[pick], L[pick]/1e3, ".", ms=1.6, color=WATER, alpha=0.5)
xx = np.logspace(0, np.log10(A.max()), 20)
ah.loglog(xx, 1.44*xx**0.614, color=INK, lw=1)
ah.loglog(xx, 1.27*xx**0.6, color="#b0503a", lw=1, ls="--")
ah.set_xlabel("area drained (km²)", fontsize=8); ah.set_ylabel("longest river (km)", fontsize=8)
ah.tick_params(labelsize=7)
for s in ["top", "right"]: ah.spines[s].set_visible(False)
ah.set_title("Hack's law", fontsize=9.5, loc="left")
fig.text(0.72, 0.155, f"Measured here\n  length ∝ area to the {num['hack_exponent']:.2f}\n"
         f"Real rivers (Hack, 1957)\n  length ∝ area to the 0.6 (dashed)\n\n"
         f"Streams of each order\n  {num['strahler_counts']['1']} · {num['strahler_counts']['2']} · {num['strahler_counts']['3']} · {num['strahler_counts']['4']}\n"
         f"each about 4.7 times fewer\n  (real networks: 3 to 5)", fontsize=8.6, va="top", linespacing=1.45)
fig.savefig("taken-away.png", dpi=160, facecolor=PAPER)
fig.savefig("preview.png", dpi=50, facecolor=PAPER)
