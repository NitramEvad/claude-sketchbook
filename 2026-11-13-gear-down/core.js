// ---- polar: a mid-range paraglider, sink (m/s) at airspeed v (km/h)
const VMIN = 30, VTRIM = 38, VMAX = 52, BASE = 2000, TASK = 50;
const POL = (() => { const p = [[30, 1.0], [38, 1.1], [52, 2.0]];
  const [[x1, y1], [x2, y2], [x3, y3]] = p;
  const a = ((y3 - y1) / (x3 - x1) - (y2 - y1) / (x2 - x1)) / (x3 - x2);
  const b = (y2 - y1) / (x2 - x1) - a * (x1 + x2); return [a, b, y1 - a * x1 * x1 - b * x1]; })();
const sink = v => POL[0] * v * v + POL[1] * v + POL[2];
// speed to fly: the speed that maximises distance per (sink + air sink + M)
const _stf = new Map();
function stf(M, s) {
  const key = Math.round(M * 20) + ',' + Math.round(s * 20);
  if (_stf.has(key)) return _stf.get(key);
  let best = VMIN, bv = -1e9;
  for (let v = VMIN; v <= VMAX + 1e-9; v += 0.1) { const d = sink(v) + M + s; const g = d > 0 ? v / d : 1e9 + v; if (g > bv) { bv = g; best = v; } }
  _stf.set(key, best); return best;
}
function rng(seed) { seed = seed >>> 0 || 1; return () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }; }
// a day: thermals along the course (x km, w = climb you get in it, m/s) and the air between, km by km (+ = lift)
function makeDay(seed, S) {
  const r = rng(seed * 7919 + 13); const th = []; let x = 0;
  while (x < TASK + 5) { x += 1.5 - Math.log(1 - r()) * 2.5; th.push({ x, w: Math.max(0.2, S * Math.exp((r() - 0.5) * 1.6)) }); }
  const air = []; for (let i = 0; i < TASK + 6; i++) air.push(-0.2 + (r() - 0.5) * 0.8);
  return { th, air, S, seed };
}
// a pilot: M is the climb they're waiting for; geared pilots lower it as they get low
function setting(p, h) { return p.geared ? p.M * Math.min(1, h / 1200) : p.M; }
function fly(day, p, every = 0) {
  let x = 0, h = BASE, t = 0, ti = 0; const tr = every ? [[0, 0, BASE, 0, VTRIM]] : null;
  while (x < TASK) {
    const s = -day.air[Math.floor(x)];
    const M = setting(p, h); const v = p.trim ? VTRIM : stf(M, s);
    x += v / 3600; h -= sink(v) + s; t += 1;
    if (tr && t % every === 0) tr.push([t, x, h, 0, v]);
    if (h <= 0) { if (tr) tr.push([t, x, 0, 2, 0]); return { out: true, x, t, tr }; }
    while (ti < day.th.length && day.th[ti].x <= x) {
      const T = day.th[ti++]; const need = h < 300 ? 0.2 : setting(p, h);
      if (T.w >= need) { const dt = (BASE - h) / T.w;
        if (tr) { tr.push([t, T.x, h, 1, T.w]); tr.push([t + dt, T.x, BASE, 0, T.w]); }
        t += dt; h = BASE; }
    }
  }
  if (tr) tr.push([t, TASK, h, 3, 0]);
  return { out: false, t, v: TASK / (t / 3600), tr };
}
