for(let n=3;n<=16;n++){const N=1<<n,M=N-1;const st=s=>{let o=0;for(let i=0;i<n;i++){const l=(s>>((i+n-1)%n))&1,c=(s>>i)&1,r=(s>>((i+1)%n))&1;if((45>>((l<<2)|(c<<1)|r))&1)o|=1<<i;}return o;};
const first=new Int32Array(N).fill(-1);let alt=0,bad=0,lost=0;const A1=[...Array(n)].reduce((a,_,i)=>a|(i%2?0:1<<i),0),A2=M^A1;
for(let s=0;s<N;s++){const y=st(s);if(first[y]<0)first[y]=s;else{const d=s^first[y];(d===A1||d===A2)?alt++:bad++;}}
console.log(n,'collisions',alt,'non-alternating',bad);}
