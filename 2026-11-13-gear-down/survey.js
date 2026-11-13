const fs=require('fs');eval(fs.readFileSync(__dirname+'/core.js','utf8'));
const out={};const Ms=[];for(let M=0;M<=3.001;M+=0.25)Ms.push(+M.toFixed(2));
for(const [k,S] of [['weak',1],['fair',1.6],['strong',2.5]]){out[k]={};
 for(const kind of ['plain','geared','trim']){out[k][kind]=Ms.map(M=>{let home=0,sum=0;const N=500;
  for(let d=0;d<N;d++){const r=fly(makeDay(d+1000,S),{M,geared:kind==='geared',trim:kind==='trim'});if(!r.out){home++;sum+=r.v;}}
  return [M,+(sum/N).toFixed(2),+(home/N).toFixed(3),home?+(sum/home).toFixed(2):null];});}}
console.log(JSON.stringify({Ms,out}));
