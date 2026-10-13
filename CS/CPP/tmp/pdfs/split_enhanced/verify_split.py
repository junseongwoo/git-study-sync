from pathlib import Path
import json,collections,sys,hashlib
import pdfplumber,pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'tmp'/'pdfs'/'split_enhanced'
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
results=json.loads((BASE/'qa_report.json').read_text(encoding='utf-8'))['files'] if (BASE/'qa_report.json').exists() else []
stems={'Part 5':'part5','Part 6':'part6','Part 7':'part7','실전 모의고사':'mock'}
selected=set(sys.argv[1:])
for item in manifest['files']:
    stem=stems[item['label']]
    if selected and stem not in selected:continue
    pdf=Path(item['file']);reader=PdfReader(pdf);issues=[];texts=[]
    with pdfplumber.open(pdf) as doc:
        for n,page in enumerate(doc.pages,1):
            text=page.extract_text(x_tolerance=2,y_tolerance=3) or '';texts.append(text)
            if len(text.strip())<40:issues.append(f'page{n}: nearly blank')
            if '\ufffd' in text or '\u25a0' in text:issues.append(f'page{n}: replacement/tofu')
            if abs(page.width-595.2756)>1 or abs(page.height-841.8898)>1:issues.append(f'page{n}: not A4')
            unsafe=[c for c in page.chars if c.get('text','').strip() and (c['x0']<33 or c['x1']>page.width-33 or c['top']<24 or c['bottom']>page.height-22)]
            if unsafe:issues.append(f'page{n}: outside print safety')
            footer=''.join(c['text'] for c in page.chars if c['top']>page.height-40).strip()
            if footer!=str(n):issues.append(f'page{n}: footer {footer!r}')
    alltext='\n'.join(texts)
    questions=json.loads((BASE/(stem+'_questions.json')).read_text(encoding='utf-8'))
    assert len(questions)==item['questions']
    for q in questions:
        if f"{q['id']} 해설 | 정답 ({q['answer']})" not in alltext:issues.append(f"{q['id']}: missing answer heading")
        for field in ['clue','analysis','why','wrong','order','rule']:assert q[field],(q['id'],field)
    for entry in item['toc']:
        if entry['title'] not in texts[entry['page']-1]:issues.append('incorrect TOC target '+entry['title'])
    for page in reader.pages:
        for ref in page['/Resources'].get('/Font',{}).values():
            f=ref.get_object();desc=f.get('/FontDescriptor')
            if desc and not any(k in desc.get_object() for k in ['/FontFile','/FontFile2','/FontFile3']):issues.append('unembedded font')
    if reader.metadata.title!='Toeic RC':issues.append('title mismatch')
    (BASE/(stem+'_extracted.txt')).write_text('\n\n'.join(f'--- PAGE {n} ---\n{t}' for n,t in enumerate(texts,1)),encoding='utf-8')
    target=BASE/('review_'+stem);target.mkdir(exist_ok=True)
    doc=pdfium.PdfDocument(str(pdf))
    for n in range(len(doc)):
        page=doc[n];bitmap=page.render(scale=1.25)
        bitmap.to_pil().convert('RGB').save(target/f'page-{n+1:03}.png');bitmap.close();page.close()
    doc.close()
    thumbW,thumbH,labelH=350,495,25;cols,rows=4,3
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
    for start in range(0,len(reader.pages),cols*rows):
        sheet=Image.new('RGB',(cols*(thumbW+10),rows*(thumbH+labelH+10)),(220,223,228));draw=ImageDraw.Draw(sheet)
        for k in range(min(cols*rows,len(reader.pages)-start)):
            im=Image.open(target/f'page-{start+k+1:03}.png');im.thumbnail((thumbW,thumbH))
            x=k%cols*(thumbW+10)+5;y=k//cols*(thumbH+labelH+10)
            draw.text((x+3,y+3),f'{stem} - Page {start+k+1}',font=font,fill=(20,30,45));sheet.paste(im,(x,y+labelH))
        sheet.save(target/f'contact-{start//12+1:02}.png')
    result=dict(label=item['label'],pages=len(reader.pages),questions=len(questions),issues=issues,rendered_pages=len(reader.pages),contact_sheets=(len(reader.pages)+11)//12,bytes=pdf.stat().st_size,sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),answer_distribution=dict(collections.Counter(q['answer'] for q in questions)))
    results=[x for x in results if x['label']!=item['label']]+[result]
    print(json.dumps(result,ensure_ascii=False),flush=True)
results.sort(key=lambda x:['Part 5','Part 6','Part 7','실전 모의고사'].index(x['label']))
report=dict(files=results,total_pages=sum(x['pages'] for x in results),total_questions=sum(x['questions'] for x in results),issues=sum(len(x['issues']) for x in results))
(BASE/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('QA completed: '+json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False),flush=True)
if report['issues']:raise SystemExit(2)
