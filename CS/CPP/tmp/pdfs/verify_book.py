from pathlib import Path
import json, re, collections
import pdfplumber
from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parents[2]
TMP=ROOT/'tmp'/'pdfs'
PDF=ROOT/'output'/'pdf'/'Toeic RC.pdf'
RENDER=TMP/'toeic_rc_current_review'; RENDER.mkdir(exist_ok=True)
reader=PdfReader(PDF)
manifest=json.loads((TMP/'manifest.json').read_text(encoding='utf-8'))
issues=[]; info=[]; texts=[]
with pdfplumber.open(PDF) as book:
    for i,page in enumerate(book.pages,1):
        text=page.extract_text(x_tolerance=2,y_tolerance=3) or ''
        texts.append(text)
        if len(text.strip())<40:issues.append({'page':i,'issue':'almost blank'})
        if '\ufffd' in text or '\u25a0' in text:issues.append({'page':i,'issue':'replacement/black-square glyph'})
        if abs(page.width-595.2756)>1 or abs(page.height-841.8898)>1:issues.append({'page':i,'issue':'not A4'})
        spill=[c for c in page.chars if c.get('text','').strip() and (c['x0']<33 or c['x1']>page.width-33 or c['top']<24 or c['bottom']>page.height-22)]
        if spill:issues.append({'page':i,'issue':'outside print safety','characters':''.join(c['text'] for c in spill)[:120]})
        # Footer number must be extracted and remain aligned at the bottom.
        footer=[c for c in page.chars if c['top']>page.height-40]
        footertext=''.join(c['text'] for c in footer).strip()
        if footertext!=str(i):issues.append({'page':i,'issue':'footer mismatch','footer':footertext})
        body=[c for c in page.chars if c['top']>61 and c['bottom']<page.height-50]
        info.append({'page':i,'characters':len(page.chars),'body_bottom':round(max((c['bottom'] for c in body),default=0),2),'body_fonts':dict(collections.Counter(round(c['size'],1) for c in body))})
alltext='\n'.join(texts)
questions=json.loads((TMP/'questions.json').read_text(encoding='utf-8'))
for q in questions:
    if f"{q['id']} 해설 | 정답 ({q['answer']})" not in alltext:
        issues.append({'id':q['id'],'issue':'answer heading absent'})
for item in manifest['toc']:
    if item['title'] not in texts[item['page']-1]:issues.append({'issue':'toc target missing','entry':item})
fonts=[]
for page in reader.pages:
    for ref in page['/Resources'].get('/Font',{}).values():
        font=ref.get_object(); desc=font.get('/FontDescriptor')
        if desc:
            desc=desc.get_object();fonts.append({'name':str(font.get('/BaseFont')),'embedded':any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3'])})
if not all(x['embedded'] for x in fonts):issues.append({'issue':'font not embedded'})
if reader.metadata.title!='Toeic RC':issues.append({'issue':'metadata title'})
if len(reader.pages)!=manifest['pages']:issues.append({'issue':'page count mismatch'})
(TMP/'extracted.txt').write_text('\n\n'.join(f'--- PAGE {i} ---\n{t}' for i,t in enumerate(texts,1)),encoding='utf-8')
report={'pages':len(reader.pages),'issues':issues,'font_files_embedded':all(x['embedded'] for x in fonts),'fonts':list({(x['name'],x['embedded']) for x in fonts}),'page_metrics':info,'answer_distribution':dict(collections.Counter(q['answer'] for q in questions))}
(TMP/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['page_metrics','fonts']},ensure_ascii=False,indent=2),flush=True)
book=pdfium.PdfDocument(str(PDF))
for i in range(len(book)):
    page=book[i]; bitmap=page.render(scale=1.25); im=bitmap.to_pil().convert('RGB')
    im.save(RENDER/f'page-{i+1:03}.png')
    bitmap.close();page.close()
    if (i+1)%20==0:print(f'Rendered {i+1}/{len(book)} pages',flush=True)
book.close()
thumbW,thumbH=350,495; labelH=25; cols,rows=4,3
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
files=[RENDER/f'page-{i:03}.png' for i in range(1,len(reader.pages)+1)]
for start in range(0,len(files),cols*rows):
    sheet=Image.new('RGB',(cols*(thumbW+10),rows*(thumbH+labelH+10)),(220,223,228));draw=ImageDraw.Draw(sheet)
    for k,path in enumerate(files[start:start+cols*rows]):
        im=Image.open(path);im.thumbnail((thumbW,thumbH))
        x=(k%cols)*(thumbW+10)+5;y=(k//cols)*(thumbH+labelH+10)
        draw.text((x+3,y+3),f'Page {start+k+1}',font=font,fill=(20,30,45))
        sheet.paste(im,(x,y+labelH))
    sheet.save(RENDER/f'contact-{start//(cols*rows)+1:02}.png')
print(f'Completed all {len(files)} renders and {(len(files)+11)//12} contact sheets',flush=True)
if issues:raise SystemExit(2)
