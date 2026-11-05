const S = require('./sim.js');
for (const bubbly of [0, 0.5, 1]) { let base=0, tops=[];
 for (let s=1;s<=40;s++){ const th=S.makeThermal(s,bubbly), g=S.makeGlider(th,s);
  while(!g.done){ const [cx,cy]=th.core(g.z); const dx=cx-g.x, dy=cy-g.y, d=Math.hypot(dx,dy);
    let a=Math.atan2(dy,dx)-g.hdg; a=Math.atan2(Math.sin(a),Math.cos(a));
    S.step(g,th, d>12 && Math.abs(a)<0.6, 0.1);}
  if(g.done==='base')base++; tops.push(Math.max(...g.track.map(q=>q[2]))|0);}
 console.log('cheat',bubbly,base+'/40',tops.sort((a,b)=>a-b)[20]); }
