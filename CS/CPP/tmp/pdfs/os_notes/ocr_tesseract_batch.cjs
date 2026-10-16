const fs = require('node:fs');
const path = require('node:path');
const { createWorker, PSM } = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/tesseract.js');
const root=__dirname,out=path.join(root,'ocr_tesseract');
fs.mkdirSync(path.join(out,'blocks'),{recursive:true});
const pending=Array.from({length:615},(_,i)=>i+1);
let next=0,completed=0;const started=Date.now();
async function run(id){
 const worker=await createWorker(['kor','eng'],1,{cachePath:'C:/Users/user/Desktop/Obsidian/git-study-sync/CS/CPP/tmp/pdfs/cpp_tour/tessdata'});
 await worker.setParameters({tessedit_pageseg_mode:PSM.AUTO,preserve_interword_spaces:'1'});
 while(next<pending.length){
  const page=pending[next++],stem=String(page).padStart(4,'0'),textPath=path.join(out,stem+'.txt');
  if(fs.existsSync(textPath)){completed++;continue;}
  try{
   const {data}=await worker.recognize(path.join(root,'images',stem+'.jpg'),{},{text:true,blocks:true});
   fs.writeFileSync(textPath,data.text,'utf8');
   fs.writeFileSync(path.join(out,'blocks',stem+'.json'),JSON.stringify({page,confidence:data.confidence,blocks:data.blocks}),'utf8');
   completed++;if(completed%20===0) console.log(JSON.stringify({completed,last:page,seconds:Math.round((Date.now()-started)/1000)}));
  }catch(e){fs.appendFileSync(path.join(out,'errors.log'),stem+': '+e.stack+'\n');}
 }
 await worker.terminate();
}
Promise.all([0,1,2,3].map(run)).then(()=>console.log('COMPLETE '+completed)).catch(e=>{console.error(e);process.exitCode=1;});

