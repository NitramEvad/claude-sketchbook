# Water gaps: the Taken away landscape, but with rock that isn't all the same.
# Beneath a flat-lying soft cover lie tilted bands of hard and soft rock, striking east-west,
# so every river on its way to the sea (south edge) must cross every hard band.
# Usage: python sim.py <cover_m> <seed> <steps> <name>
import numpy as np, sys, time
from core import step, fill

N = 400; dx = 100.0
U = 1e-3; m = 0.5; D = 0.01; dt = 2000.0
K_SOFT = 4e-5; K_HARD = 4e-6           # hard rock is ten times harder to wear away
COVER = float(sys.argv[1]); SEED = int(sys.argv[2]); STEPS = int(sys.argv[3]); NAME = sys.argv[4]
DIP = np.radians(35)                   # layers dip north (up the page) at 35 degrees
HARD_W = 1200.0; SOFT_W = 2800.0       # true thicknesses, measured across the layers
PERIOD = HARD_W + SOFT_W

y = (np.arange(N)[:, None] * dx) * np.ones((1, N))
x = (np.arange(N)[None, :] * dx) * np.ones((N, 1))
wobble = 900 * np.sin(2*np.pi*x/31000 + 0.7) + 400 * np.sin(2*np.pi*x/11000 + 2.0)   # a gentle bend in the strike

def rock(h, up):
    """0 = cover, 1 = soft band, 2 = hard band, for rock now at the surface."""
    z0 = h - up                         # where this rock sat at time zero (it has been lifted by `up`)
    c = (y + wobble) * np.sin(DIP) - z0 * np.cos(DIP)    # distance across the layers
    ph = np.mod(c, PERIOD)
    r = np.where(ph < HARD_W, 2, 1)
    if COVER > 0: r[z0 > -COVER] = 0
    return r

if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    h = rng.random((N, N)) * 1.0 + (N - 1 - np.arange(N)[:, None]) * 0.002   # nearly flat, tilted faintly to the sea
    out = np.zeros((N, N), np.bool_); out[-1, :] = True; h[out] = 0
    t0 = time.time(); snaps = {}; up = 0.0
    keep = {int(STEPS*f) for f in (0.05, 0.12, 0.25, 0.5, 1.0)}
    for s in range(1, STEPS+1):
        r = rock(h, up)
        K = np.where(r == 2, K_HARD, K_SOFT).astype(np.float64)
        A, rec = step(h, U, K, m, D, dt, dx, out)
        up += U*dt
        if s in keep: snaps[s] = (h.copy(), rock(h, up), A.copy(), rec.copy())
        if s % 250 == 0: print(NAME, s, round(h.mean(), 1), round(h.max(), 1), round(time.time()-t0, 1), flush=True)
    np.savez_compressed(f"run_{NAME}.npz", h=h, out=out, A=A, rec=rec, rock=rock(h, up), up=up,
        **{f"h{k}": v[0] for k, v in snaps.items()}, **{f"r{k}": v[1] for k, v in snaps.items()},
        **{f"A{k}": v[2] for k, v in snaps.items()}, **{f"rec{k}": v[3] for k, v in snaps.items()})
