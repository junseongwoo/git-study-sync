import argparse,json,re,subprocess,hashlib
from pathlib import Path
import fitz
import render_os as renderer
from pypdf import PdfReader
from PIL import Image,ImageDraw,ImageFont
import io
H=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('pdf',type=Path);ap.add_argument('--render',action='store_true');args=ap.parse_args()
pdf=args.pdf.resolve();d=fitz.open(pdf);r=PdfReader(pdf)
report_path=pdf.with_suffix('.build_report.json');build=json.loads(report_path.read_text(encoding='utf-8'))
text=[p.get_text() for p in d]
bodytext=[]
usedfonts=set()
for p in d:
 lines=[]
 for block in p.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   kept=[]
   for s in line['spans']:
    usedfonts.add(s['font'])
    if 40 < s['bbox'][1] and s['bbox'][3] < 799:kept.append(s['text'])
   if kept:lines.append(''.join(kept))
 bodytext.append('\n'.join(lines).replace('원문 코드·기호 (계속)','').replace('원문 코드·기호',''))
norm=lambda t:re.sub(r'\s+','',t)
whole=norm('\n'.join(bodytext));errors=[];sparse=[];prose_count=0
renderer.register_fonts(Path('C:/Windows/Fonts'))
def prosecheck(t,where):
 global prose_count
 if not t:return
 prose_count+=1
 t=renderer.clean(t)
 t=re.sub(r'`([^`\n]+)`',r'\1',t)
 t=re.sub(r'\*\*([^*\n]+)\*\*',r'\1',t)
 if norm(t) not in whole:errors.append({'type':'prose_text_not_found','at':where,'text':t[:110]})
for ch in sorted((H/'chapters').glob('*.json')):
 ch=json.loads(ch.read_text(encoding='utf-8-sig'))
 if ch['id'] not in {x['id'] for x in build['chapters']}:continue
 for sec in ch['sections']:
  for b in sec['blocks']:
   if b['type']=='p':prosecheck(b.get('text'),ch['id']+':'+sec['number'])
   if b['type'] in ('bullets','steps','flow'):
    for t in b.get('items',b.get('steps',[])):prosecheck(t,ch['id']+':'+sec['number'])
   if b['type']=='formula':
    if norm(b.get('text','')) not in whole:errors.append({'type':'formula_text_not_found','at':ch['id']+':'+sec['number']})
   if b['type']=='table':
    for row in b.get('rows',[]):
     for value in row:prosecheck(str(value),ch['id']+':'+sec['number']+':table')
 for fig in ch.get('figures',[]):
  prosecheck(fig.get('meaning'),fig['id']+':meaning')
 for code in ch.get('codes',[]):
  if code['id'] not in build['code_ids']:continue
  if norm(code['code']) not in whole:errors.append({'type':'code_text_not_found','id':code['id']})
for i,p in enumerate(d,1):
 if abs(p.rect.width-595.2756)>.1 or abs(p.rect.height-841.8898)>.1:errors.append({'type':'not_A4','page':i})
 body=[]
 for block in p.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if x0<42 or x1>554 or y0<10 or y1>829:errors.append({'type':'outside_expected_bounds','page':i,'bbox':list(span['bbox']),'text':span['text']})
    if i>1 and y0>40 and y1<799:body.append(span)
 if i>1 and body and max(s['bbox'][3] for s in body)<350:sparse.append({'page':i,'last_y':round(max(s['bbox'][3] for s in body),1),'chars':sum(len(s['text']) for s in body)})
 if '\ufffd' in text[i-1] or '\u25a0' in text[i-1]:errors.append({'type':'suspicious_glyph','page':i})
 footer=p.get_textbox(fitz.Rect(490,800,555,833)).strip()
 if i>1 and footer!=str(i):errors.append({'type':'footer_mismatch','page':i,'last':footer})
fonts={}
for pg in r.pages:
 for name,font in pg['/Resources'].get('/Font',{}).items():
  f=font.get_object(); desc=f.get('/FontDescriptor');desc=desc.get_object() if desc else {}
  fname=str(f.get('/BaseFont'))
  if fname.lstrip('/').split('+')[-1] in usedfonts:
   fonts[fname]=any(k in desc for k in ('/FontFile','/FontFile2','/FontFile3'))
if not all(fonts.values()):errors.append({'type':'nonembedded_font','fonts':fonts})
pixel_hashes=set();seen_xrefs=set()
for page in d:
 for entry in page.get_images():
  xref=entry[0]
  if xref in seen_xrefs:continue
  seen_xrefs.add(xref)
  data=d.extract_image(xref)
  with Image.open(io.BytesIO(data['image'])) as pic:
   pixel_hashes.add(hashlib.sha256(pic.convert('RGB').tobytes()).hexdigest())
embedded_figure_checks=[]
for chapter_file in sorted((H/'chapters').glob('*.json')):
 ch=json.loads(chapter_file.read_text(encoding='utf-8-sig'))
 for figure in ch.get('figures',[]):
  if figure['id'] not in build.get('figure_ids',[]):continue
  fp=Path(figure['file']);fp=fp if fp.is_absolute() else H/fp
  with Image.open(fp) as pic:
   found=hashlib.sha256(pic.convert('RGB').tobytes()).hexdigest() in pixel_hashes
  embedded_figure_checks.append({'id':figure['id'],'pixel_exact_image_embedded':found})
  if not found:errors.append({'type':'figure_pixels_not_embedded','id':figure['id']})
outlines=[]
def walk(items):
 for item in items:
  if isinstance(item,list):walk(item)
  else:outlines.append({'title':item.title,'page':r.get_destination_page_number(item)+1})
walk(r.outline)
for h in build['headings']:
 if not any(x['title']==h['title'] and x['page']==h['page'] for x in outlines):errors.append({'type':'outline_page_mismatch','heading':h})
 # Heading destinations and visible chapter text must agree.
 if norm(h['title']) not in norm(text[h['page']-1]):errors.append({'type':'heading_absent_at_destination','heading':h})
cover=text[0].strip().splitlines()
if norm(''.join(cover))!=norm(build['confirmed_title']+'핵심 개념 및 시험 대비 학습 노트'):errors.append({'type':'extra_or_missing_cover_text','text':cover})
qa={'pdf':str(pdf),'pages':len(d),'a4_all':True,'searchable_pages':sum(bool(x.strip()) for x in text),'fonts':fonts,'outline_count':len(outlines),'outline':outlines,'cover_text':cover,'errors':errors,'sparse_pages':sparse,'code_count':len(build['code_ids']),'figure_count':len(build.get('figure_ids',[])),'embedded_figure_checks':embedded_figure_checks,'prose_segments_checked':prose_count,'source_code_character_replacements':build['code_character_replacements'],'toc_headings':build['headings']}
if args.render:
 render_dir=H/f'qa_pages_{len(d)}';render_dir.mkdir(exist_ok=True)
 digits=len(str(len(d)))
 paths=[render_dir/f'page-{i:0{digits}}.png' for i in range(1,len(d)+1)]
 if not all(p.is_file() and p.stat().st_mtime >= pdf.stat().st_mtime for p in paths):
  rendered=subprocess.run(['pdftoppm','-r','85','-png','-thinlinemode','shape',str(pdf),str(render_dir/'page')],capture_output=True)
  if rendered.returncode:
   print(rendered.stderr.decode('utf-8',errors='replace'))
   rendered.check_returncode()
 # Build sheets with 12 pages each, annotated with actual PDF page numbers.
 sheets=[];tw=290;th=430
 font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',14)
 for k in range(0,len(paths),12):
  pagepaths=paths[k:k+12];im=Image.new('RGB',(tw*4,th*3),'#dae0e5');dr=ImageDraw.Draw(im)
  for j,pp in enumerate(pagepaths):
   page=Image.open(pp).convert('RGB');page.thumbnail((tw-12,th-28))
   x=(j%4)*tw+(tw-page.width)//2;y=(j//4)*th+21
   im.paste(page,(x,y));dr.text(((j%4)*tw+8,(j//4)*th+3),f'PDF {k+j+1}',fill='#172635',font=font)
  sp=render_dir/f'contact_{k//12+1:02}.jpg';im.save(sp,quality=88);sheets.append(str(sp))
 qa['rendered_page_images']=len(paths);qa['contact_sheets']=sheets
(H/'pdf_qa_report.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:qa[k] for k in ['pdf','pages','searchable_pages','fonts','outline_count','cover_text','errors','sparse_pages']},ensure_ascii=False))
