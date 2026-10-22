from pathlib import Path
import json,pymupdf as fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
sources={'A':{'id':'A','path':'C:/Users/user/Downloads/(C언어)자료구조 (1).pdf','filename':'(C언어)자료구조 (1).pdf'},'B':{'id':'B','path':'C:/Users/user/Downloads/C언어_자료구조_알고리즘.pdf','filename':'C언어_자료구조_알고리즘.pdf'}}
for k,s in sources.items():
 d=fitz.open(s['path']);s['pdf_pages']=len(d);s['printed_offset']=None
 folder=R/f'{k}_images';folder.mkdir(parents=True,exist_ok=True)
 for i,p in enumerate(d,1):
  target=folder/f'{i:04}.jpg'
  if target.exists():continue
  imgs=p.get_images(full=True)
  assert imgs,(k,i)
  img=d.extract_image(imgs[0][0])
  if img['ext'] in ('jpeg','jpg'):target.write_bytes(img['image'])
  else:
   import io
   Image.open(io.BytesIO(img['image'])).convert('RGB').save(target,quality=96)
 for start in range(1,13,4):
  sheet=Image.new('RGB',(1800,2500),'white');draw=ImageDraw.Draw(sheet)
  for j,n in enumerate(range(start,start+4)):
   im=Image.open(folder/f'{n:04}.jpg');im.thumbnail((880,1200));x=(j%2)*900;y=(j//2)*1250
   sheet.paste(im,(x,y+27));draw.text((x+10,y+5),f'{k} PDF {n}',fill='black')
  sheet.save(R/f'{k}_front_{start:02}.jpg',quality=95)
 print(k,len(d),'images extracted',flush=True)
(R/'source_registry.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),'utf-8')
