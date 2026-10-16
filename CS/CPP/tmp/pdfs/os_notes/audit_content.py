import json,re,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
mp=json.loads((H/'source_map.json').read_text(encoding='utf-8'))
page_map={p['pdf_page']:p for p in mp['pages']}
chapters=[json.loads(p.read_text(encoding='utf-8-sig')) for p in sorted((H/'chapters').glob('*.json'))]
errors=[]; warnings=[]; summary=[]
def sourcecheck(s,where):
 if not isinstance(s,dict): errors.append([where,'missing source']);return
 pp=s.get('printed',[]);pdf=s.get('pdf',[])
 if not isinstance(pp,list) or not isinstance(pdf,list): errors.append([where,'source is not list']);return
 if len(pp)==len(pdf):
  for x,y in zip(pdf,pp):
   if x not in page_map or page_map[x].get('printed_page')!=y:errors.append([where,'page mapping mismatch',x,y])
 elif pp: errors.append([where,'unequal source lengths',pdf,pp])
 for x in pdf:
  if not 1<=x<=351:errors.append([where,'out of range pdf source',x])
for ch in chapters:
 where=ch['id']; sourcecheck(ch.get('source'),where)
 original=next(x for x in mp['chapters'] if x['chapter']==ch['order'])
 if ch['source']['pdf']!=original['pdf_pages_in_reading_order']:
  warnings.append([where,'chapter page coverage differs from map'])
 numbers={s['number'] for s in ch['sections']}
 for section in original['sections']:
  if section['section'] not in numbers:errors.append([where,'missing original TOC section',section['section']])
 for sec in ch['sections']:
  sourcecheck(sec.get('source'),where+':'+sec['number'])
  for b in sec['blocks']:
   if b.get('source'):sourcecheck(b['source'],where+':'+sec['number']+':block')
 for c in ch.get('codes',[]):
  sourcecheck(c.get('source'),c['id'])
  if not c.get('output'):errors.append([c['id'],'missing output marker'])
  if c.get('excerpt') and not c.get('excerpt_note'):warnings.append([c['id'],'excerpt note empty'])
  if '\ufffd' in c['code']:errors.append([c['id'],'replacement glyph in code'])
 for c in ch.get('comparisons',[]):sourcecheck(c.get('source'),where+':comparison')
 prose=sum(len(b.get('text',''))+sum(map(len,b.get('items',[]))) for s in ch['sections'] for b in s['blocks'])
 summary.append({'chapter':where,'sections':len(ch['sections']),'codes':len(ch.get('codes',[])),'prose_chars':prose,'limitations':ch.get('limitations',[])})
report={'chapter_count':len(chapters),'all_chapters_present':set(c['order'] for c in chapters)==set(range(1,17)),
 'errors':errors,'warnings':warnings,'summary':summary}
(H/'content_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
