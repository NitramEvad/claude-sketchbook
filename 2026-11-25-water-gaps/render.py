import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
n = 400
num = json.load(open("numbers.json")); inh = json.load(open("inherit.json"))
PAPER = "#f3eee3"; INK = "#2b2a28"; WATER = "#2f5f8f"; SEA = "#c9d6dc"; OLD = "#b0503a"
ROCK = np.array([matplotlib.colors.to_rgb(c) for c in ("#e6d6ae", "#cdd5b4", "#94664c")])   # cover, soft, hard

def shade(h):
    gy, gx = np.gradient(h, 100.0)
    az, alt = np.radians(315), np.radians(35)
    slope = np.arctan(1.0*np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    s = np.sin(alt)*np.cos(slope) + np.cos(alt)*np.sin(slope)*np.cos(az-aspect)
    return np.clip(s, 0, 1)

def rivers(ax, A, rec, thr, color, wscale=1.0, cap=3.6, alpha=0.95, ls="-", z=2):
    idx = np.where((A > thr) & (rec != np.arange(n*n)))[0]; r = rec[idx]
    segs = np.stack([np.stack([idx % n + .5, idx//n + .5], 1), np.stack([r % n + .5, r//n + .5], 1)], 1)
    w = wscale*0.35*(A[idx]/thr)**0.4
    ax.add_collection(LineCollection(segs, linewidths=np.minimum(w, cap), colors=color, capstyle="round", alpha=alpha, linestyles=ls, zorder=z))

def plate(ax, h, rk, out, A=None, rec=None, thr=2e6, wscale=1.0):
    rgb = ROCK[rk] * (0.42 + 0.7*shade(h)[..., None])
    rgb[out] = matplotlib.colors.to_rgb(SEA)
    ax.imshow(np.clip(rgb, 0, 1), interpolation="bilinear", extent=(0, n, n, 0))
    if A is not None: rivers(ax, A, rec, thr, WATER, wscale)
    ax.set_xlim(0, n); ax.set_ylim(n, 0); ax.set_axis_off()

plt.rcParams.update({"font.family": "DejaVu Serif", "text.color": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK, "axes.edgecolor": INK})
fig = plt.figure(figsize=(10, 15.6), facecolor=PAPER)
fig.text(0.07, 0.963, "Water gaps", fontsize=30, weight="bold")
fig.text(0.07, 0.942, "Two blocks of land, made of exactly the same rock: tilted bands of hard (brown) and soft (green), buried under\n"
         "a kilometre of soft cover. Both are raised a millimetre a year for six million years and carved by their rivers.\n"
         "The only difference is the first rain: a different scatter of centimetre bumps on the flat ground at the start.",
         fontsize=9.6, va="top", linespacing=1.5)
for i, (name, lab) in enumerate([("covered", "First rain A"), ("covered7", "First rain B")]):
    d = np.load(f"run_{name}.npz"); out = d["out"]
    ax = fig.add_axes([0.07 + i*0.445, 0.565, 0.415, 0.32])
    plate(ax, d["h"], d["rock"], out, d["A"], d["rec"])
    rivers(ax, d["A360"], d["rec360"], 40e6, "#e8784a", wscale=0.7, cap=1.6, alpha=1, ls=(0, (2, 2)), z=4)
    g = np.load(f"gaps_{name}.npy").astype(int)
    ax.scatter(g % n + .5, g//n + .5, s=70, facecolors="none", edgecolors=INK, linewidths=1.3, zorder=5)
    ax.set_title(f"{lab}: after six million years", fontsize=11, pad=6)
    if i == 0:
        ax.plot([10, 110], [n-12, n-12], color=INK, lw=2, solid_capstyle="butt"); ax.text(60, n-17, "10 km", ha="center", fontsize=8.5)
    ax.text(n-6, n-4, "sea", ha="right", va="bottom", fontsize=8.5, style="italic", color="#4a5a62")
# legend
lx = 0.07; ly = 0.545
fig.text(lx, ly, "■", color=ROCK[2], fontsize=13, va="center"); fig.text(lx+0.022, ly, "hard rock (ridges)", fontsize=8.8, va="center")
fig.text(lx+0.2, ly, "■", color=ROCK[1], fontsize=13, va="center"); fig.text(lx+0.222, ly, "soft rock (valleys)", fontsize=8.8, va="center")
fig.text(lx+0.4, ly, "—", color=WATER, fontsize=13, va="center", weight="bold"); fig.text(lx+0.425, ly, "rivers now", fontsize=8.8, va="center")
fig.text(lx+0.56, ly, "- -", color="#e8784a", fontsize=11, va="center", weight="bold"); fig.text(lx+0.59, ly, "big rivers on the cover, 5.3 Myr ago", fontsize=8.8, va="center")
fig.text(lx, ly-0.018, "○", color=INK, fontsize=12, va="center"); fig.text(lx+0.022, ly-0.018,
         "water gaps: where a river cuts straight through a hard ridge instead of going round", fontsize=8.8, va="center")
# time strip for run A
d = np.load("run_covered.npz"); out = d["out"]
for i, (k, lab) in enumerate([(150, "300 thousand years\nstill on the cover"), (750, "1.5 million\nthe bands appear"),
                               (1500, "3 million"), (3000, "6 million")]):
    a = fig.add_axes([0.07 + i*0.2225, 0.345, 0.19, 0.122])
    plate(a, d[f"h{k}"], d[f"r{k}"], out, d[f"A{k}"], d[f"rec{k}"], thr=8e6, wscale=0.6)
    a.set_title(lab, fontsize=8.3, pad=3)
fig.text(0.07, 0.505, "First rain A, through time", fontsize=10.5, weight="bold")
# panel: gaps per ridge over time
ag = fig.add_axes([0.07, 0.05, 0.25, 0.17]); ag.set_facecolor(PAPER)
for name, c, lab in [("covered", INK, "A"), ("covered7", "#7d6a55", "B")]:
    hst = num[name]["history"]; ks = [k for k in hst if hst[k]["mean_gaps_per_ridge"] is not None]
    ag.plot([int(k)*0.002 for k in ks], [hst[k]["mean_gaps_per_ridge"] for k in ks], "o-", color=c, ms=4, lw=1.3, label=f"first rain {lab}")
ag.set_ylim(0, 6); ag.set_xlim(0, 6.3); ag.set_xlabel("million years", fontsize=8); ag.tick_params(labelsize=7.5)
ag.set_title("Water gaps per ridge", fontsize=9.5, loc="left"); ag.legend(fontsize=7.5, frameon=False)
for s in ["top", "right"]: ag.spines[s].set_visible(False)
# panel: soft rock share
asb = fig.add_axes([0.42, 0.05, 0.22, 0.17]); asb.set_facecolor(PAPER)
g1 = num["covered"]["soft_share_of_ground"]; g2 = num["covered"]["soft_share_of_river_length"]; g3 = num["covered"]["soft_share_of_big_river_length"]
asb.bar([0, 1, 2], [g1*100, g2*100, g3*100], color=[ROCK[1], "#8fa7bf", WATER], width=0.65)
for x, v in zip([0, 1, 2], [g1, g2, g3]): asb.text(x, v*100+2, f"{v*100:.0f}%", ha="center", fontsize=8.5)
asb.set_xticks([0, 1, 2]); asb.set_xticklabels(["ground", "all\nrivers", "big\nrivers"], fontsize=7.8)
asb.set_ylim(0, 100); asb.set_yticks([0, 50, 100]); asb.tick_params(labelsize=7.5)
asb.set_title("Share on soft rock (A, now)", fontsize=9.5, loc="left")
for s in ["top", "right"]: asb.spines[s].set_visible(False)
# panel: distances
ad = fig.add_axes([0.73, 0.05, 0.22, 0.17]); ad.set_facecolor(PAPER)
vals = [(inh["covered"]["to_covered_median_km"] + inh["covered7"]["to_covered7_median_km"])/2,
        (inh["covered"]["to_covered7_median_km"] + inh["covered7"]["to_covered_median_km"])/2,
        (inh["random_ridge_points_to_covered_median_km"] + inh["random_ridge_points_to_covered7_median_km"])/2]
ad.bar([0, 1, 2], vals, color=[OLD, "#d4a99a", "#cfc6b5"], width=0.65)
for x, v in zip([0, 1, 2], vals): ad.text(x, v+0.06, f"{v:.1f} km", ha="center", fontsize=8.5)
ad.set_xticks([0, 1, 2]); ad.set_xticklabels(["its own\nold rivers", "the other\nrun's", "random\nridge spot"], fontsize=7.8)
ad.set_ylim(0, 2.6); ad.tick_params(labelsize=7.5)
ad.set_title("Gap to nearest old river", fontsize=9.5, loc="left")
for s in ["top", "right"]: ad.spines[s].set_visible(False)
fig.text(0.07, 0.3, "The rock decides where the ridges are. The first rain decides where the rivers cut through them.\n"
         "Every gap sits on a river that was already flowing across the cover before the ridge existed (median distance: 0 km);\n"
         "the other run's old rivers are no closer to it than a random spot on the ridge. Over time small gaps are abandoned\n"
         "and only the big rivers keep theirs. Rivers do favour soft rock, but less than I expected: they still have to get to the sea.",
         fontsize=8.9, va="top", linespacing=1.55)
fig.savefig("water-gaps.png", dpi=160, facecolor=PAPER)
fig.savefig("preview.png", dpi=50, facecolor=PAPER)
