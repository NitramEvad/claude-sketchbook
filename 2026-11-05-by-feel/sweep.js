const S = require('./sim.js');
for (const bubbly of [0, 1]) for (const lag of [0.25, 0.6, 1, 1.5, 2.2]) for (const noise of [1, 3]) {
  let base = 0, ts = [], losses = 0, gusts = 0;
  for (let s = 1; s <= 30; s++) { const { g, p } = S.fly(s, bubbly, 'hand', { lag, noise }); if (g.done === 'base') { base++; ts.push(g.t | 0); } losses += p.losses; gusts += p.gusts; }
  ts.sort((a, b) => a - b);
  console.log(`bubbly ${bubbly} lag ${lag} noise x${noise}: base ${base}/30 median ${ts[ts.length >> 1]}s losses ${losses} gusts ${gusts}`);
}
