// For every elementary rule and ring size: map every start to its fate.
// A ring's song either falls silent or falls into a loop (period 1 = a held chord).
function nexts(rule,n){const N=1<<n,out=new Int32Array(N);
  for(let s=0;s<N;s++){let o=0;for(let i=0;i<n;i++){
    const l=(s>>((i+1)%n))&1,c=(s>>i)&1,r=(s>>((i-1+n)%n))&1;
    if((rule>>((l<<2)|(c<<1)|r))&1)o|=1<<i;}out[s]=o;}return out;}
function fates(nx){const N=nx.length,st=new Int8Array(N),per=new Int32Array(N),tr=new Int32Array(N);
  const loops=[];
  for(let s0=0;s0<N;s0++){if(st[s0])continue;const path=[];let s=s0;
    while(!st[s]){st[s]=1;path.push(s);s=nx[s];}
    let baseT,baseP;
    if(st[s]===1){const k=path.indexOf(s);const p=path.length-k;
      for(let j=k;j<path.length;j++){per[path[j]]=p;tr[path[j]]=0;st[path[j]]=2;}
      loops.push({p,rep:s});path.length=k;baseT=0;baseP=p;}
    else{baseT=tr[s];baseP=per[s];}
    for(let j=path.length-1,t=baseT+1;j>=0;j--,t++){per[path[j]]=baseP;tr[path[j]]=t;st[path[j]]=2;}}
  return {per,tr,loops};}
module.exports={nexts,fates};
if(require.main===module){
 const M=+process.argv[2]||14, out={};
 for(let rule=0;rule<256;rule++){out[rule]={};for(let n=3;n<=M;n++){
   const {per,tr,loops}=fates(nexts(rule,n));
   let maxp=0,maxt=0,silent=0;for(const L of loops)maxp=Math.max(maxp,L.p);
   for(let s=1;s<per.length;s++){maxt=Math.max(maxt,tr[s]);}
   // silence = ends at state 0 with 0 a fixed point
   const zeroFixed=nexts(rule,n)[0]===0;
   out[rule][n]={maxp,maxt,nloops:loops.length,ends:zeroFixed&&loops.length===1};}}
 require('fs').writeFileSync('survey.json',JSON.stringify(out));
}
