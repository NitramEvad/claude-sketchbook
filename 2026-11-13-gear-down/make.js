// builds index.html from template.html + core.js + survey.json (run: node survey.js > survey.json; node make.js)
const fs=require('fs');const d=__dirname;
let t=fs.readFileSync(d+'/template.html','utf8');
t=t.replace('/*CORE*/',fs.readFileSync(d+'/core.js','utf8')).replace('/*SURVEY*/',fs.readFileSync(d+'/survey.json','utf8').trim());
fs.writeFileSync(d+'/index.html',t);
