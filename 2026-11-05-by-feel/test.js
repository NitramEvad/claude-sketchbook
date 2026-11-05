const S = require('./sim.js');
for (const bubbly of [0, 0.5, 1]) for (const kind of ['still', 'hand']) {
  let base = 0, ts = [], hs = [], lost = 0;
  for (let s = 1; s <= 40; s++) {
    const { g, p } = S.fly(s, bubbly, kind);
    if (g.done === 'base') { base++; ts.push(g.t); }
    hs.push(Math.max(...g.track.map(q => q[2]))); lost += p.losses;
  }
  const med = a => a.sort((x, y) => x - y)[a.length >> 1] | 0;
  console.log(`bubbly ${bubbly} ${kind.padEnd(5)} base ${base}/40  median time ${med(ts)}s  median top ${med(hs)}m  lost ${lost}`);
}
