const fs = require('node:fs');
const path = require('node:path');
const { createWorker, PSM } = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/tesseract.js');
const root = __dirname;
const out = path.join(root,'ocr_tesseract');
fs.mkdirSync(out,{recursive:true});
fs.mkdirSync(path.join(out,'blocks'),{recursive:true});
const pending=[];
// Prioritize advanced SQL chapters while contributors draft them.
for(let p=465;p<=786;p++) pending.push(p);
for(let p=1;p<465;p++) pending.push(p);
let next=0, completed=0;
const started=Date.now();
async function run(id) {
  const worker=await createWorker(['kor','eng'],1,{cachePath:path.join(root,'tessdata')});
  await worker.setParameters({tessedit_pageseg_mode:PSM.AUTO,preserve_interword_spaces:'1'});
  while(next<pending.length){
    const page=pending[next++];
    const stem=String(page).padStart(4,'0');
    const textPath=path.join(out,stem+'.txt');
    if(fs.existsSync(textPath)) {completed++;continue;}
    try{
      const {data}=await worker.recognize(path.join(root,'images',stem+'.jpg'),{},{text:true,blocks:true});
      fs.writeFileSync(textPath,data.text,'utf8');
      fs.writeFileSync(path.join(out,'blocks',stem+'.json'),JSON.stringify({page,confidence:data.confidence,blocks:data.blocks}),'utf8');
      completed++;
      if(completed%20===0) console.log(JSON.stringify({completed,last:page,seconds:Math.round((Date.now()-started)/1000)}));
    }catch(e){fs.appendFileSync(path.join(out,'errors.log'),stem+': '+e.stack+'\n');}
  }
  await worker.terminate();
}
Promise.all([0,1,2,3].map(run)).then(()=>console.log('COMPLETE '+completed)).catch(e=>{console.error(e);process.exitCode=1;});
