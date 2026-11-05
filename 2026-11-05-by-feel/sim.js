// By feel: one glider, one thermal, no eyes. Shared by the page and by test.js.
(function (root) {
  function rng(seed) { let s = (seed >>> 0) || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

  const BASE = 1500, FLOOR = 60, START = 320;

  // A thermal in the air's frame. It widens and strengthens with height, its core wanders,
  // it pulses, it is lumpy, and it is rough at the edges.
  function makeThermal(seed, bubbly) {
    const r = rng(seed * 7919 + 13);
    const ph = Array.from({ length: 10 }, () => r() * Math.PI * 2);
    const amp = 0.85 + 0.3 * r();
    return {
      seed, bubbly, base: BASE,
      core(z) {
        return [55 * amp * Math.sin(z / 240 + ph[0]) + 22 * Math.sin(z / 95 + ph[1]),
                55 * amp * Math.sin(z / 210 + ph[2]) + 22 * Math.sin(z / 105 + ph[3])];
      },
      radius(z) { return 40 + 0.035 * Math.min(z, BASE); },          // ~51 m low, ~92 m near base
      peak(z, t) {
        const grow = 2.2 + 2.3 * Math.min(1, z / 1150);              // ~2.8 m/s low, ~4.5 m/s high
        const fade = z > 1380 ? 1 - 0.35 * (z - 1380) / 120 : 1;
        const pulse = 1 + (0.12 + 0.3 * bubbly) * Math.sin(t / 21 + ph[4]) * Math.sin(t / 8.3 + ph[5]);
        return grow * fade * pulse;
      },
      w(x, y, z, t) {
        const [cx, cy] = this.core(z), R = this.radius(z);
        const dx = x - cx, dy = y - cy, d = Math.hypot(dx, dy);
        const ang = Math.atan2(dy, dx);
        const lump = 1 + (0.12 + 0.25 * bubbly) * Math.cos(ang - t / 37 - ph[6]);
        const lift = this.peak(z, t) * lump * Math.exp(-((d / R) ** 2));
        const ring = -0.8 * Math.exp(-(((d - 1.9 * R) / (0.7 * R)) ** 2));
        const turb = (0.2 + 1.1 * bubbly) * Math.sin(x / 13 + t / 2.7 + ph[7]) * Math.sin(y / 15 - t / 3.4 + ph[8])
                     * Math.exp(-((d / (2.4 * R)) ** 2));
        return lift + ring + turb;
      }
    };
  }

  const V = 10, G = 9.81, SPAN = 5.5; // airspeed m/s, half-span m
  const BANK_TURN = 38, BANK_OPEN = 6, ROLL = 20; // degrees, deg/s

  function makeGlider(th, seed) {
    const r = rng(seed * 31 + 7);
    const [cx, cy] = th.core(START);
    const a = r() * Math.PI * 2, off = 10 + 25 * r();
    return { x: cx + off * Math.cos(a), y: cy + off * Math.sin(a), z: START, hdg: r() * Math.PI * 2,
             bank: BANK_TURN, t: 0, climb: 0, vario: 0, feel: 0, done: null, track: [], sample: 0 };
  }

  // hold = rolling out. The glider always turns left; holding opens the turn.
  function step(g, th, hold, dt) {
    if (g.done) return;
    const target = hold ? BANK_OPEN : BANK_TURN;
    const db = target - g.bank, mx = ROLL * dt;
    g.bank += Math.max(-mx, Math.min(mx, db));
    const b = g.bank * Math.PI / 180;
    g.hdg += G * Math.tan(b) / V * dt;
    g.x += V * Math.cos(g.hdg) * dt;
    g.y += V * Math.sin(g.hdg) * dt;
    const sink = 1.1 / Math.pow(Math.cos(b), 1.5);
    const air = th.w(g.x, g.y, g.z, g.t);
    g.climb = air - sink;
    g.z += g.climb * dt;
    g.t += dt;
    g.vario += (g.climb - g.vario) * Math.min(1, dt / 0.9);       // the instrument lags
    // the seat: one wing lifted more than the other (left = inside of the turn)
    const lx = g.x + SPAN * Math.cos(g.hdg + Math.PI / 2), ly = g.y + SPAN * Math.sin(g.hdg + Math.PI / 2);
    const rx = g.x - SPAN * Math.cos(g.hdg + Math.PI / 2), ry = g.y - SPAN * Math.sin(g.hdg + Math.PI / 2);
    const f = th.w(lx, ly, g.z, g.t) - th.w(rx, ry, g.z, g.t);
    g.feel += (f - g.feel) * Math.min(1, dt / 0.4);
    g.sample += dt;
    if (g.sample >= 0.5) { g.sample = 0; g.track.push([g.x, g.y, g.z, g.vario, g.bank]); }
    if (g.z >= th.base) g.done = 'base';
    else if (g.z <= FLOOR) g.done = 'ground';
    else if (g.t > 900) g.done = 'time';
  }

  // Pilots who fly by feel. Each sees only a lagged, noisy vario.
  // 'still': turns at constant bank, never adjusts.
  // 'hand': the textbook rule: when the lift gets stronger, straighten for a moment; when it fades, turn tight.
  function makePilot(kind, seed, bubbly, opts = {}) {
    const r = rng(seed * 101 + 3);
    const noise = (opts.noise ?? 1) * (0.2 + 0.6 * bubbly);
    const lag = opts.lag ?? 0.25;                 // how slowly the seat's feeling becomes a decision
    const thr = opts.thr ?? 0.18;
    let prevClimb = null, seat = 0, holdLeft = 0, lostFor = 0, searching = 0;
    return {
      kind, losses: 0, gusts: 0,
      decide(g, dt) {
        if (kind === 'still') return false;
        // the seat feels the change in climb (a push up, a drop), not the climb itself
        const push = prevClimb === null ? 0 : (g.climb - prevClimb) / dt;
        prevClimb = g.climb;
        seat += (push + noise * (r() + r() + r() - 1.5) * 2 - seat) * Math.min(1, dt / lag);
        if (searching > 0) { searching -= dt; if (g.vario > 0.8) searching = 0; return searching > 0 && searching < 7; }
        lostFor = g.vario < 0 ? lostFor + dt : 0;
        if (lostFor > 20) { lostFor = 0; searching = 9; this.losses++; return false; } // lost it: fly out and look
        if (holdLeft > 0) {
          holdLeft -= dt;
          if (seat < -thr * 1.5) { holdLeft = 0; this.gusts++; }  // it was a gust, not the core: turn again
          return holdLeft > 0;
        }
        if (seat > thr && g.bank > 25) { holdLeft = 1.5 + Math.min(2.5, seat * 3); return true; }
        return false;
      }
    };
  }

  function fly(seed, bubbly, kind, opts, dt = 0.1) {
    const th = makeThermal(seed, bubbly), g = makeGlider(th, seed), p = makePilot(kind, seed, bubbly, opts);
    while (!g.done) step(g, th, p.decide(g, dt), dt);
    return { g, th, p };
  }

  const api = { makeThermal, makeGlider, makePilot, step, fly, BASE, FLOOR, START, BANK_TURN, BANK_OPEN, V };
  if (typeof module !== 'undefined') module.exports = api; else root.BYFEEL = api;
})(this);
