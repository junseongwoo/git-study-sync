import json,re,hashlib
from pathlib import Path
from PIL import Image, ImageChops
H=Path(__file__).resolve().parent
mp=json.loads((H/'source_map.json').read_text(encoding='utf-8'))
page_map={p['pdf']:p for p in mp['pages']}
chapters=[json.loads(p.read_text(encoding='utf-8-sig')) for p in sorted((H/'chapters').glob('*.json'))]
errors=[]; warnings=[]; summary=[]; read_pages=set([1,2,3,4,5,6,226,324,429,516,615]);visual_pages=set([1,2,3,4,5,6,226,324,429,516,615]); crop_checks=[]
def sourcecheck(s,where):
 if not isinstance(s,dict): errors.append([where,'missing source']);return
 pp=s.get('printed',[]);pdf=s.get('pdf',[])
 if not isinstance(pp,list) or not isinstance(pdf,list): errors.append([where,'source is not list']);return
 if len(pp)==len(pdf):
  for x,y in zip(pdf,pp):
   if x not in page_map or page_map[x].get('printed')!=y:errors.append([where,'page mapping mismatch',x,y])
 elif pp: errors.append([where,'unequal source lengths',pdf,pp])
 for x in pdf:
  if not 1<=x<=615:errors.append([where,'out of range pdf source',x])
for ch in chapters:
 where=ch['id']; sourcecheck(ch.get('source'),where)
 original=next((x for x in mp['chapters'] if x['number']==ch['order']),None) if ch['id']!='OP7' else None
 if original and original['available'] and ch['source']['pdf']!=original['pdf']:
  errors.append([where,'chapter page coverage differs from map'])
 numbers={s['number'] for s in ch['sections']}
 for section in original['sections'] if original else []:
  if section['number'] not in numbers:errors.append([where,'missing original TOC section',section['number']])
 for sec in ch['sections']:
  sourcecheck(sec.get('source'),where+':'+sec['number'])
  for b in sec['blocks']:
   if b.get('source'):sourcecheck(b['source'],where+':'+sec['number']+':block')
 for c in ch.get('codes',[]):
  sourcecheck(c.get('source'),c['id'])
  if not c.get('output'):errors.append([c['id'],'missing output marker'])
  if c.get('excerpt') and not c.get('excerpt_note'):warnings.append([c['id'],'excerpt note empty'])
  if '\ufffd' in c['code']:errors.append([c['id'],'replacement glyph in code'])
 for fig in ch.get('figures',[]):
  sourcecheck(fig.get('source'),fig['id'])
  fp=Path(fig['file']); fp=fp if fp.is_absolute() else H/fp
  if not fp.is_file():errors.append([fig['id'],'figure file missing']);continue
  crop=fig.get('crop',{})
  if crop.get('image') and crop.get('bbox'):
   with Image.open(crop['image']) as original_image,Image.open(fp) as final:
    expected=original_image.convert('RGB').crop(tuple(crop['bbox']))
    final=final.convert('RGB')
    same=expected.size==final.size and ImageChops.difference(expected,final).getbbox() is None
    crop_checks.append({'figure':fig['id'],'exact_original_crop':same,'size':final.size})
    if not same:errors.append([fig['id'],'figure crop differs from stated original pixels'])
  else:warnings.append([fig['id'],'no crop coordinates; manual proof required'])
 for c in ch.get('comparisons',[]):sourcecheck(c.get('source'),where+':comparison')
 for c in ch.get('checklist',[]):
  if isinstance(c,dict):sourcecheck(c.get('source'),where+':checklist')
 verification=ch.get('verification',{});read_pages.update(verification.get('read_pdf_pages',[]));visual_pages.update(verification.get('visually_checked_pdf_pages',[]))
 if original and original['available']:
  if set(original['pdf'])-set(verification.get('read_pdf_pages',[])):errors.append([where,'reading record does not cover source pages'])
 prose=sum(len(b.get('text',''))+sum(len(str(t)) for t in b.get('items',b.get('steps',[]))) for s in ch['sections'] for b in s['blocks'])
 summary.append({'chapter':where,'available':ch.get('available',True),'sections':len(ch['sections']),'codes':len(ch.get('codes',[])),'figures':len(ch.get('figures',[])),'prose_chars':prose,'limitations':ch.get('limitations',[])})
expected={ch['number'] for ch in mp['chapters'] if ch['available']}
found={c['order'] for c in chapters if c['id']!='OP7' and c.get('available',True)}
report={'chapter_records':len(chapters),'all_provided_chapters_present':expected==found,'actual_provided_chapters':sorted(found),
 'all_615_pages_read':read_pages==set(range(1,616)),'read_page_count':len(read_pages),'visually_checked_pdf_pages':sorted(visual_pages),
 'missing_read_records':sorted(set(range(1,616))-read_pages),'exact_crop_checks':crop_checks,
 'errors':errors,'warnings':warnings,'summary':summary}
(H/'content_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
