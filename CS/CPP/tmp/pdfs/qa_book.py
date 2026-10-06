from pathlib import Path
import json, re, collections
from pypdf import PdfReader
import build_book
import pdfplumber
from PIL import Image, ImageOps, ImageDraw, ImageFont
BASE=Path(__file__).resolve().parent
ROOT=Path.cwd();PDF=ROOT/'output/pdf/TOEIC_900_Vocabulary_60_Day_Challenge.pdf'
data=json.loads((BASE/'all_content.json').read_text(encoding='utf-8'))
audit=json.loads((BASE/'final_audit.json').read_text(encoding='utf-8'))
r=PdfReader(str(PDF));texts=[p.extract_text() for p in r.pages]
fonts={}
for p in r.pages:
    for ref in p['/Resources']['/Font'].values():
        f=ref.get_object()
        if f.get('/Subtype')=='/TrueType':fonts[str(f['/BaseFont'])]=f
assert len(fonts)>=2
for name,f in fonts.items():
    desc=f['/FontDescriptor'].get_object()
    assert '/FontFile2' in desc or '/FontFile3' in desc,('unembedded font',name)
assert r.outline
assert len(r.pages[2].get('/Annots',[]))>=20, 'TOC links missing'
assert len(texts)==373
for i,t in enumerate(texts,1):
    assert t.rstrip().endswith(f'{i:03d}') or re.search(r'(?m)^'+f'{i:03d}'+r'$',t),('footer',i)
    assert '\ufffd' not in t and '\u25a1' not in t,('broken glyph',i)
    assert len(t)>100,('empty page',i)
    assert abs(float(r.pages[i-1].mediabox.width)-595.2756)<.1
    assert abs(float(r.pages[i-1].mediabox.height)-841.8898)<.1
for d in data['days']:
    n=d['day'];p=audit['sections'][f'day{n}']
    for part in range(3):
        t=texts[p+part-1]
        assert 'No.' in t and 'TOEIC 표현' in t and '예문 / 해석' in t
        for j in range(10):assert re.search(r'(?m)^'+f'{part*10+j+1:02d}'+r'\b',t),(n,part,j)
    testp=audit['sections'][f'mini{n}'];ansp=audit['sections'][f'answer{n}']
    assert testp+1==ansp
    assert 'Mini Test' in texts[testp-1] and 'Answers' in texts[ansp-1]
    assert "Today's Review" in texts[ansp-1] and '30개' in texts[ansp-1]
    assert '가장 중요한 단어 5개' in texts[ansp-1] and '헷갈리기 쉬운 단어 5개' in texts[ansp-1]
    assert '오늘 반드시 외울 표현 5개' in texts[ansp-1]
    for q in __import__('build_book').daily_questions(d):
        if 'options' in q:assert q['options'][q['answer']]==q['word']
    if n in [7,14,21,28,35,42,49,56]:assert str(audit['sections']['week'+str(n)]) in texts[ansp-1]
for group in [data['weekly'], {'final':data['final']}]:
    for name,qs in group.items():
        for q in qs:assert len(q['options'])==4 and q['options'][q['answer']]==q['word'] and q['why']
cmap=set(build_book.pdfmetrics.getFont('KR').face.charToGlyph)
missing=sorted(set(ord(ch) for t in texts for ch in t if not ch.isspace())-cmap)
assert not missing,('unsupported characters',missing)
allbounds=[];bad=[]
with pdfplumber.open(str(PDF)) as doc:
    for no,p in enumerate(doc.pages,1):
        for ch in p.chars:
            if ch['text'].strip() and (ch['x0']<38 or ch['x1']>p.width-38 or ch['top']<12 or ch['bottom']>p.height-12):bad.append((no,ch['text'],ch['x0'],ch['x1'],ch['top'],ch['bottom']))
        body=[ch for ch in p.chars if ch['top']>43 and ch['bottom']<p.height-35]
        allbounds.append(dict(page=no,chars=len(p.chars),lowest_body=max([c['bottom'] for c in body] or [0])))
        if no%50==0:print('Geometry reviewed:',no,flush=True)
        p.close()
assert not bad,('out-of-bounds characters',bad[:20])
for key,pg in audit['sections'].items():
    if key.startswith('day'):
        assert f'Day {int(key[3:]):02d}' in texts[pg-1]
toc=texts[2]
for key in ['use','plan','method','day1','day11','day21','day31','day41','day51','week7','final','finalanswers','weak','check']:
    assert f'{audit["sections"][key]:03d}' in toc,(key,'toc mismatch')
qa=dict(pages=len(texts),a4=True,page_numbers=True,table_bounds=True,unsupported_glyphs=missing,replacement_glyphs=0,mini_answer_separation=True,question_keys_checked=True,toc_checked=True,font_embedded=True,body_bounds=allbounds)
(BASE/'quality_audit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('All structural, font, page, answer-key and geometry checks passed.',flush=True)

def montage():
    imgs=sorted((BASE/'rendered').glob('page-*.png'))
    assert len(imgs)==373,len(imgs)
    mdir=BASE/'montages';mdir.mkdir(exist_ok=True)
    for block in range((len(imgs)+19)//20):
        sheet=Image.new('RGB',(1200,1840),'#DDE4EB');draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(imgs[block*20:block*20+20]):
            im=Image.open(p).convert('RGB');im.thumbnail((284,400));x=(j%4)*300+(300-im.width)//2;y=(j//4)*368+20
            im.thumbnail((250,345));sheet.paste(im,(x,y));draw.text((j%4*300+15,y+340),f'PAGE {block*20+j+1:03d}',fill='#15334F')
        sheet.save(mdir/f'sheet-{block+1:02d}.jpg',quality=90)
    print('All-page visual contact sheets:',len(list(mdir.glob('*.jpg'))))
if (BASE/'rendered').exists():montage()
