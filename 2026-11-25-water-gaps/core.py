# Uplift + stream-power erosion on a grid (Braun & Willett style implicit scheme),
# with depressions filled each step. Everything the landscape becomes is what is taken away.
import numpy as np, heapq, sys
from numba import njit

N = int(sys.argv[1]) if len(sys.argv) > 1 else 256
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 21
rng = np.random.default_rng(SEED)
dx = 100.0           # m per cell
U = 1e-3             # uplift, m/yr
K = 2e-5             # erodibility (m=0.5, n=1)
m = 0.5
D = 0.01             # hillslope diffusion m^2/yr
dt = 2000.0          # yr
STEPS = int(sys.argv[3]) if len(sys.argv) > 3 else 1500

NB = np.array([(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)])
DIST = np.array([np.hypot(a,b) for a,b in NB]) * dx

@njit(cache=True)
def fill(h, eps, out):
    n = h.shape[0]
    # priority flood (Barnes) with a simple binary heap implemented by arrays
    closed = np.zeros((n,n), np.bool_)
    heap_v = np.empty(n*n); heap_i = np.empty(n*n, np.int64); size = 0
    def_push = 0
    for i in range(n):
        for j in range(n):
            if out[i,j]:
                closed[i,j] = True
                # push
                k = size; size += 1
                heap_v[k] = h[i,j]; heap_i[k] = i*n+j
                while k > 0:
                    p = (k-1)//2
                    if heap_v[p] > heap_v[k]:
                        heap_v[p],heap_v[k] = heap_v[k],heap_v[p]; heap_i[p],heap_i[k] = heap_i[k],heap_i[p]; k = p
                    else: break
    while size > 0:
        v = heap_v[0]; c = heap_i[0]
        size -= 1
        heap_v[0] = heap_v[size]; heap_i[0] = heap_i[size]
        k = 0
        while True:
            l = 2*k+1; r = l+1; s = k
            if l < size and heap_v[l] < heap_v[s]: s = l
            if r < size and heap_v[r] < heap_v[s]: s = r
            if s == k: break
            heap_v[s],heap_v[k] = heap_v[k],heap_v[s]; heap_i[s],heap_i[k] = heap_i[k],heap_i[s]; k = s
        ci = c//n; cj = c%n
        for di in range(-1,2):
            for dj in range(-1,2):
                if di==0 and dj==0: continue
                a = ci+di; b = cj+dj
                if a<0 or b<0 or a>=n or b>=n or closed[a,b]: continue
                closed[a,b] = True
                if h[a,b] <= v + eps: h[a,b] = v + eps
                k = size; size += 1
                heap_v[k] = h[a,b]; heap_i[k] = a*n+b
                while k > 0:
                    p = (k-1)//2
                    if heap_v[p] > heap_v[k]:
                        heap_v[p],heap_v[k] = heap_v[k],heap_v[p]; heap_i[p],heap_i[k] = heap_i[k],heap_i[p]; k = p
                    else: break
    return h

@njit(cache=True)
def receivers(h, dx, out):
    n = h.shape[0]
    rec = np.arange(n*n)
    rd = np.ones(n*n)*dx
    for i in range(n):
        for j in range(n):
            if out[i,j]: continue
            best = 0.0; bk = i*n+j; bd = dx
            for di in range(-1,2):
                for dj in range(-1,2):
                    if di==0 and dj==0: continue
                    if i+di<0 or j+dj<0 or i+di>=n or j+dj>=n: continue
                    d = dx*np.sqrt(di*di+dj*dj)
                    s = (h[i,j]-h[i+di,j+dj])/d
                    if s > best: best = s; bk = (i+di)*n+(j+dj); bd = d
            rec[i*n+j] = bk; rd[i*n+j] = bd
    return rec, rd

@njit(cache=True)
def step(h, U, K, m, D, dt, dx, out):
    # K is now a grid: each cell's erodibility, from the rock it currently sits in
    n = h.shape[0]
    fill(h, 1e-6, out)
    rec, rd = receivers(h, dx, out)
    flat = h.ravel()
    order = np.argsort(flat)          # low to high
    A = np.ones(n*n)*dx*dx
    for t in range(n*n-1, -1, -1):
        c = order[t]
        r = rec[c]
        if r != c: A[r] += A[c]
    # uplift interior
    for t in range(n*n):
        c = order[t]; i = c//n; j = c%n
        if out[i,j]: continue
        flat[c] += U*dt
    # implicit stream power, receivers first
    for t in range(n*n):
        c = order[t]; r = rec[c]
        if r == c: continue
        f = K.ravel()[c]*dt*A[c]**m/rd[c]
        flat[c] = (flat[c] + f*flat[r])/(1+f)
    # explicit diffusion
    hh = flat.reshape(n,n)
    lap = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            if out[i,j]: continue
            a = hh[i+1,j] if i+1<n else hh[i,j]
            b = hh[i-1,j] if i>0 else hh[i,j]
            c2 = hh[i,j+1] if j+1<n else hh[i,j]
            d2 = hh[i,j-1] if j>0 else hh[i,j]
            lap[i,j] = (a+b+c2+d2-4*hh[i,j])/(dx*dx)
            continue
            lap[i,j] = (hh[i+1,j]+hh[i-1,j]+hh[i,j+1]+hh[i,j-1]-4*hh[i,j])/(dx*dx)
    for i in range(n):
        for j in range(n):
            hh[i,j] += D*dt*lap[i,j]
    return A, rec

