import json,re
from pathlib import Path
import pymupdf as fitz
from pypdf import PdfReader
import render_book

base=Path(__file__).parent
pdf=base.parents[2]/'output'/'pdf'/'SQL_전문가_가이드_요약.pdf'
doc=fitz.open(pdf)
build=json.loads(pdf.with_suffix('.build_report.json').read_text(encoding='utf-8'))
chapters=sorted([json.loads(p.read_text(encoding='utf-8')) for p in (base/'chapters').glob('*.json')],key=lambda x:x['order'])
render_book.register_fonts(Path('C:/Windows/Fonts'))
norm=lambda v:re.sub(r'\s+','',render_book.clean(v).replace('**','').replace('`',''))
body=''.join(pg.get_text(clip=fitz.Rect(35,44,pg.rect.width-35,pg.rect.height-42)) for pg in doc)
body=body.replace('SQL 원문 (계속)','').replace('SQL 원문(계속)','')
body_norm=norm(body)
missing_prose=[]; missing_sql=[]
for ch in chapters:
 for section in ch['sections']:
  for block in section['blocks']:
   if block['type']=='p' and norm(block['text']) not in body_norm:missing_prose.append([ch['id'],block['text'][:60]])
 for code in ch['codes']:
  if norm(code['sql']) not in body_norm:missing_sql.append(code['id'])
outside=[];blank=[];folios=[]
for i,pg in enumerate(doc):
 if not pg.get_text().strip():blank.append(i+1)
 if i and pg.get_text(clip=fitz.Rect(0,pg.rect.height-42,pg.rect.width,pg.rect.height)).strip()!=str(i+1):folios.append(i+1)
 for block in pg.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if x0<35 or x1>pg.rect.width-35 or y0<10 or y1>pg.rect.height-12:outside.append([i+1,span['text'][:50]])
heading_bad=[h for h in build['headings'] if norm(h['title']) not in norm(doc[h['page']-1].get_text())]
reader=PdfReader(pdf);fonts=set()
for pg in reader.pages:
 for value in pg['/Resources'].get('/Font',{}).values():
  fo=value.get_object();fd=fo.get('/FontDescriptor')
  if fd:fonts.add((str(fo.get('/BaseFont')),any(k in fd.get_object() for k in ['/FontFile','/FontFile2','/FontFile3'])))
result=dict(pages=len(doc),file_bytes=pdf.stat().st_size,chapters=len(chapters),sections=sum(len(c['sections']) for c in chapters),source_sql_examples=sum(len(c['codes']) for c in chapters),syntax_entries=len(json.loads((base/'review.json').read_text(encoding='utf-8'))['syntax']),a4_all=all(abs(pg.rect.width-595.2756)<.1 and abs(pg.rect.height-841.8898)<.1 for pg in doc),cover_title_exact=doc[0].get_text().strip()=='SQL 전문가 가이드 요약',text_characters=sum(len(pg.get_text()) for pg in doc),blank_pages=blank,folio_errors=folios,text_outside_safe_area=outside,unknown_glyphs=build['unknown_glyphs'],missing_prose=missing_prose,missing_sql=missing_sql,heading_destination_errors=heading_bad,bookmarks=len(doc.get_toc()),link_count=sum(len(pg.get_links()) for pg in doc),link_destinations_valid=all(0<=lk['page']<len(doc) for pg in doc for lk in pg.get_links() if 'page'in lk),embedded_fonts=sorted(fonts))
(base/'final_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
