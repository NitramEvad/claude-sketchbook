// Draws preview.svg: the thirty pairs' first second, as tuned (left) and all 30 cents apart (right).
const P=[[136.36,142.65],[147.68,154.66],[160.95,167.69],[203.73,210.92],[216.60,223.72],[272.73,279.06],[295.71,302.97],[321.73,328.87],[406.99,415.06],[433.44,441.02],[295.70,302.46],[320.24,327.73],[405.82,413.87],[432.44,440.25],[550.54,558.22],[598.29,605.24],[650.93,656.97],[818.70,826.30],[871.40,880],[1108.73,1115.80],[597.94,605.59],[648.68,656.22],[813.99,820.59],[872.41,877.97],[1108.73,1116.44],[1196.57,1204.20],[1298.74,1306.38],[1638.35,1646.89],[1742.80,1750.87],[2209.79,2218.74]].sort((a,b)=>a[0]-b[0]);
const mc=P.reduce((s,p)=>s+1200*Math.log2(p[1]/p[0]),0)/P.length;
const W=900,H=585,rowH=16,top=60,colW=400;
let s=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="#f6f1e7"/>`;
s+=`<text x="40" y="38" font-family="Georgia,serif" font-size="22" fill="#2a2219">as tuned: the beat stays put</text><text x="480" y="38" font-family="Georgia,serif" font-size="22" fill="#2a2219">same interval: it speeds up</text>`;
function strip(x0,y0,df,col){const N=260,h=rowH-3;let up=[],dn=[];for(let k=0;k<=N;k++){const t=k/N,e=Math.exp(-t*1.1)*Math.abs(Math.cos(Math.PI*df*t))*h/2;up.push(`${(x0+t*colW).toFixed(1)},${(y0-e).toFixed(1)}`);dn.unshift(`${(x0+t*colW).toFixed(1)},${(y0+e).toFixed(1)}`)}return `<polygon points="${up.concat(dn).join(" ")}" fill="${col}"/>`}
P.forEach((p,i)=>{const y=top+i*rowH+rowH/2;s+=strip(40,y,p[1]-p[0],"#c07f38");s+=strip(480,y,p[0]*(2**(mc/1200)-1),"#a8682a")});
s+=`<text x="40" y="${H-12}" font-family="sans-serif" font-size="13" fill="#6e6152">thirty gamelan pairs, 136 Hz (top) to 2,210 Hz (bottom), first second after the strike</text></svg>`;
require('fs').writeFileSync('preview.svg',s);
