import json,re
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).parent
m=json.loads((R/'source_map.json').read_text(encoding='utf-8'))
lookup={p['pdf']:p['printed'] for p in m['pages']};issues=[];allfig=[];stats=[]
for n in range(6,11):
 d=json.loads((R/'chapters'/f'{n:02d}.json').read_text(encoding='utf-8'))
 def walk(o):
  if isinstance(o,dict):
   if 'source' in o:
    s=o['source']
    if [lookup[x] for x in s['pdf']]!=s['printed']:issues.append((n,'source',s))
   for v in o.values():walk(v)
  if isinstance(o,list):
   for v in o:walk(v)
 walk(d)
 ids={x['id'] for x in d['codes']+d['figures']}
 for s in d['sections']:
  for b in s['blocks']:
   if b['type'] in ['code_ref','figure_ref'] and b['id'] not in ids:issues.append((n,'reference',b['id']))
 allfig+=d['figures']
 text=''.join(b.get('text','')+''.join(b.get('items',[])) for s in d['sections'] for b in s['blocks'] if b['type'] not in ['steps'])
 stats.append({'chapter':n,'sections':len(d['sections']),'prose_chars':len(text),'codes':len(d['codes']),'figures':len(d['figures']),'read_pages':len(d['verification']['read_pdf_pages'])})
for off in range(0,len(allfig),6):
 selected=allfig[off:off+6];tiles=[]
 for f in selected:
  im=Image.open(f['file']).convert('RGB');im.thumbnail((600,720))
  tile=Image.new('RGB',(620,770),'white');tile.paste(im,((620-im.width)//2,35));ImageDraw.Draw(tile).text((10,10),f['id'],fill='black');tiles.append(tile)
 canv=Image.new('RGB',(1860,1540),'#bbbbbb')
 for j,t in enumerate(tiles):canv.paste(t,((j%3)*620,(j//3)*770))
 canv.save(R/f'mid_crop_contact_{off//6+1:02d}.jpg')
(R/'mid_validation.json').write_text(json.dumps({'issues':issues,'stats':stats,'all_ocr_winrt':len(list((R/'ocr').glob('*.txt'))),'all_ocr_tesseract':len(list((R/'ocr_tesseract').glob('*.txt')))},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'issues':issues,'stats':stats},ensure_ascii=False,indent=2))
