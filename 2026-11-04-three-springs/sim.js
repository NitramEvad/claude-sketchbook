// One thermal climb. Ground frame: x downwind (m), y crosswind, z altitude.
function rng(seed){let s=seed>>>0||1;return()=>{s^=s<<13;s>>>=0;s^=s>>17;s^=s<<5;s>>>=0;return s/4294967296}}
function simulate(o){
  const u=o.wind, w0=o.lift, R=65, V=10.5, r0=22, sink=1.25, zb=o.base||1600, wa=w0+0.5;
  const rand=rng(o.seed||7);
  // wobbles of the core with height (the plume isn't a straight pipe)
  const ph=[rand()*6.3,rand()*6.3,rand()*6.3,rand()*6.3];
  const core=z=>{const x=u*z/wa + 18*Math.sin(z/170+ph[0])+9*Math.sin(z/61+ph[1]);
                 const y=18*Math.sin(z/150+ph[2])+9*Math.sin(z/53+ph[3]);return [x,y]};
  const lift=(x,y,z)=>{const c=core(z),d2=(x-c[0])**2+(y-c[1])**2;
    const strength=w0*(0.75+0.5*Math.min(1,z/400))*(1-0.35*(z/zb)**3);
    return strength*Math.exp(-d2/(R*R))};
  let z=o.start||300,x=core(z)[0]-45,y=core(z)[1]-25,h=0.4,t=0,dt=0.1;
  let vs=0,pts=[],out=false,tOut=null;
  const dir=o.dir||1, om0=V/r0;
  // the pilot's guess at the core, kept in the air's frame (the pilot drifts with the air)
  let ax=x,ay=y, gx=null,gy=null, best=-9,bx=0,by=0, turned=0, hist=[], tb=0, btb=0, zTop=z, tTop=0;
  while(t<3000){
    const L=lift(x,y,z), vnow=L-sink;
    vs+=(vnow-vs)*dt/1.2;                 // the vario lags a little
    let om=om0;
    if(out){ const k=((h%(2*Math.PI))+2*Math.PI)%(2*Math.PI); om=k<0.15?0:om0*0.8; } // roll out, head downwind
    else{
      hist.push([ax,ay]); if(hist.length>12)hist.shift();
      if(vs>best){best=vs;bx=hist[0][0];by=hist[0][1];btb=t-1.2;}
      if(gx!==null){
        const cx=ax-dir*r0*Math.sin(h), cy=ay+dir*r0*Math.cos(h);
        const lead=-u*Math.max(0.2,1-Math.max(0,vs)/wa)*(t-tb), ex=gx+lead-cx, ey=gy-cy, e=Math.hypot(ex,ey);
        if(e>3){const c=(Math.cos(h)*ex+Math.sin(h)*ey)/e; if(c>0) om*=1-Math.min(1,e/15)*c*c;}
      }
      turned+=om*dt;
      if(turned>=2*Math.PI){            // one turn done: the guess moves to where it felt best
        turned=0;
        gx=bx; gy=by; tb=btb;           // the core keeps sliding upwind through the air; lead it
        best=-9;
      }
    }
    h+=dir*om*dt;
    const vx=V*Math.cos(h), vy=V*Math.sin(h);
    ax+=vx*dt; ay+=vy*dt;
    x+=(vx+u)*dt; y+=vy*dt;
    z+=(out?-1.1:vnow)*dt; t+=dt;
    if(!out){ if(z>zTop+5){zTop=z;tTop=t;}
      if(z>=zb-30||t-tTop>50){out=true;tOut=t;} }  // at base, or the lift has died: leave
    if(out&&t-tOut>150)break;
    if(z<0)break;
    pts.push([x,y,z,t,ax,ay,L]);
  }
  return {pts,tOut,zTop,core,u,zb,wa};
}
if(typeof module!=='undefined')module.exports={simulate};
