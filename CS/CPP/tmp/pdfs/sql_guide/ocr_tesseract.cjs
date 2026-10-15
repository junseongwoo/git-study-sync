const fs = require('node:fs');
const path = require('node:path');
const { createWorker, PSM } = require('C:/Users/user/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/tesseract.js');
const root = __dirname;
async function main() {
  const worker = await createWorker(process.argv[4] || ['kor','eng'], 1, { cachePath: path.join(root, 'tessdata') });
  await worker.setParameters({ tessedit_pageseg_mode: PSM.AUTO, preserve_interword_spaces: '1' });
  const t = Date.now();
  const result = await worker.recognize(process.argv[2], {}, {text:true, blocks:true, tsv:true});
  fs.writeFileSync(process.argv[3],result.data.text,'utf8');
  fs.writeFileSync(process.argv[3]+'.json', JSON.stringify({confidence:result.data.confidence,blocks:result.data.blocks}),'utf8');
  console.log(JSON.stringify({seconds:(Date.now()-t)/1000,confidence:result.data.confidence,text:result.data.text}));
  await worker.terminate();
}
main().catch(e => { console.error(e); process.exit(1); });
