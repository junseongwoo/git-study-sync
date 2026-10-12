from pathlib import Path
import re, json, html, sys
from collections import Counter
import pdfplumber
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw
from toeic_data import Q,P6,P7

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'tmp/pdfs'
PDF=ROOT/'output/pdf/TOEIC_RC_Practice_Set_01.pdf'
def norm(t):
    t=re.sub('<[^>]+>',' ',t)
    return ' '.join(html.unescape(t).split())
sources={n:s for s in P7 for n in s['nums']}
evidence_fail=[]
for q in Q:
    if not q['evidence']:continue
    s=sources[q['n']]
    alltext=norm(' '.join(' '.join([d['label'],d['meta']]+d['paras']) for d in s['docs']))
    for loc,t in q['evidence']:
        if norm(t) not in alltext:evidence_fail.append((q['n'],loc,t))
assert not evidence_fail,evidence_fail

manifest=json.loads((BASE/'page_manifest.json').read_text(encoding='utf-8'))
reader=PdfReader(PDF)
assert len(reader.pages)==len(manifest)
issues=[]
question_pages={}
alltexts=[]
with pdfplumber.open(PDF) as book:
    for i,page in enumerate(book.pages):
        assert abs(page.width-595.2756)<.1 and abs(page.height-841.8898)<.1
        chars=[c for c in page.chars if c.get('text','').strip()]
        for c in chars:
            if min(c['x0'],page.width-c['x1'],c['top'],page.height-c['bottom'])<15*72/25.4-.2:
                issues.append(dict(page=i+1,kind='safe_margin',char=c['text'],bbox=[c['x0'],c['top'],c['x1'],c['bottom']]))
        text=page.extract_text(x_tolerance=2,y_tolerance=3) or ''
        alltexts.append(text)
        if i>0 and f'{i+1} / {len(book.pages)}' not in text:issues.append(dict(page=i+1,kind='missing_footer'))
        if '\ufffd' in text or '\x00' in text:issues.append(dict(page=i+1,kind='bad_glyph'))
        if manifest[i]['section'].startswith('PART'):
            for m in re.finditer(r'(?m)^(\d{1,2})\. ',text):
                n=int(m.group(1))
                lo,hi={'PART 5':(1,30),'PART 6':(31,46),'PART 7':(47,70)}[manifest[i]['section']]
                if not lo<=n<=hi:continue
                question_pages[n]=i+1
                # Choice labels must be on the same page after each question.
                rest=text[m.end():]
                nextq=re.search(r'(?m)^\d{1,2}\. ',rest)
                if nextq:rest=rest[:nextq.start()]
                for letter in 'ABCD':
                    if f'({letter})' not in rest:issues.append(dict(page=i+1,kind='split_choice',question=n,letter=letter))
    assert sorted(question_pages)==list(range(1,71)),question_pages

# Explanations must stay whole, with all required labels, on one page.
for q in Q:
    pattern=re.compile(r'(?m)^'+str(q['n'])+r'\. 정답: \('+q['answer']+r'\)')
    matching=[(i+1,t) for i,t in enumerate(alltexts) if pattern.search(t)]
    assert len(matching)==1,(q['n'],len(matching))
    pn,t=matching[0]
    tail=t[pattern.search(t).end():]
    nxt=re.search(r'(?m)^\d{1,2}\. 정답:',tail)
    if nxt:tail=tail[:nxt.start()]
    for label in ['핵심 포인트:','해설:','오답 분석:','700점대 학습자 주의점:','기억할 것:']:
        if label not in tail:issues.append(dict(page=pn,kind='split_explanation',question=q['n'],label=label))
    for letter in 'ABCD':
        if f'({letter})' not in tail:issues.append(dict(page=pn,kind='missing_analysis',question=q['n'],letter=letter))

fonts=set()
for page in reader.pages:
    for ref in page['/Resources']['/Font'].values():
        font=ref.get_object();fonts.add(str(font.get('/BaseFont')))
        if font.get('/Subtype')=='/TrueType':
            descriptor=font['/FontDescriptor'].get_object()
            assert '/FontFile2' in descriptor

report=dict(pages=len(reader.pages),question_count=len(Q),question_pages=question_pages,
            levels=dict(Counter(q['level'] for q in Q)),answers=dict(Counter(q['answer'] for q in Q)),
            evidence_excerpts=sum(len(q['evidence'] or []) for q in Q),fonts=sorted(fonts),issues=issues,
            minimum_font_size=8,output_bytes=PDF.stat().st_size)
(BASE/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['question_pages','issues']},ensure_ascii=False))
print('Issues:',len(issues),issues[:3])
assert not issues, 'See qa_report.json'

if '--contacts' in sys.argv:
    images=sorted((BASE/'render').glob('page-*.png'))
    assert len(images)==len(reader.pages),(len(images),len(reader.pages))
    for group in range(0,len(images),9):
        thumb_w,thumb_h=397,562
        sheet=Image.new('RGB',(3*(thumb_w+18)+18,3*(thumb_h+35)+18),'#d7dce2')
        draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(images[group:group+9]):
            im=Image.open(path).convert('RGB');im.thumbnail((thumb_w,thumb_h))
            x=18+(j%3)*(thumb_w+18);y=18+(j//3)*(thumb_h+35)
            sheet.paste(im,(x,y));draw.text((x,y+thumb_h+6),f'Page {group+j+1} | {manifest[group+j]["section"]}',fill='black')
        sheet.save(BASE/f'contact-{group//9+1:02d}.jpg',quality=90)
    print('Contact sheets created')
