import json,re
from pathlib import Path
root=Path(__file__).parent
out=[]
for p in sorted((root/'ocr'/'lines').glob('*.json')):
 d=json.loads(p.read_text(encoding='utf-8-sig')); cand=[]
 for l in d['lines']:
  ws=l['words']; yy=min((w['y'] for w in ws),default=0)
  if yy<d['height']*.087 or yy>d['height']*.9:
   nums=[w['text'] for w in ws if re.fullmatch(r'\d{1,4}',w['text'])]
   for n in nums:cand.append({'n':int(n),'y':round(yy),'t':l['text']})
 out.append({'pdf':d['page'],'candidate':cand,'head':' | '.join(l['text'] for l in d['lines'][:2])})
(root/'footer_candidates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'footer_candidates.txt').write_text('\n'.join(f"{x['pdf']:04d}: {x['candidate']} :: {x['head']}" for x in out),encoding='utf-8')
print(len(out))
