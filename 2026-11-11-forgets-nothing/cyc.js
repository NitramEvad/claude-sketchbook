const n=17,N=1<<n,rule=45;
function step(s){let o=0;for(let i=0;i<n;i++){const l=(s>>((i+n-1)%n))&1,c=(s>>i)&1,r=(s>>((i+1)%n))&1;if((rule>>((l<<2)|(c<<1)|r))&1)o|=1<<i;}return o;}
const nx=new Int32Array(N);for(let s=0;s<N;s++)nx[s]=step(s);
const inimg=new Uint8Array(N);for(let s=0;s<N;s++)inimg[nx[s]]=1;
console.log('bijective', inimg.every(v=>v));
const seen=new Int32Array(N).fill(-1);const lens={};let best=0,bs=0,cid=0;
for(let s=0;s<N;s++){if(seen[s]>=0)continue;let t=s,L=0;while(seen[t]<0){seen[t]=cid;t=nx[t];L++;}lens[L]=(lens[L]||0)+1;if(L>best){best=L;bs=s;}cid++;}
console.log(best,bs,JSON.stringify(lens));
