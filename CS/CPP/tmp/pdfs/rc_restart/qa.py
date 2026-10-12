from pathlib import Path
import json,re,sys,html
from collections import Counter
from pypdf import PdfReader
import pdfplumber
from PIL import Image,ImageDraw
from questions import ALL,CH

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
PDF=ROOT/'output/pdf/TOEIC_RC_Restart_Concepts_Practice_Explanations.pdf'
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
loc=json.loads((BASE/'locations.json').read_text(encoding='utf-8'))
starts=json.loads((BASE/'chapter_starts.json').read_text(encoding='utf-8'))
reader=PdfReader(PDF);assert len(reader.pages)==len(manifest)
issues=[];texts=[];safety=15*72/25.4
def norm(s):return re.sub(r'\s+','',html.unescape(s))
with pdfplumber.open(PDF) as book:
    for i,pg in enumerate(book.pages):
        assert abs(pg.width-595.2756)<.1 and abs(pg.height-841.8898)<.1
        bad=[]
        for ch in pg.chars:
            if not ch['text'].strip():continue
            if min(ch['x0'],pg.width-ch['x1'],ch['top'],pg.height-ch['bottom'])<safety-.2:
                bad.append([ch['text'],round(ch['x0'],2),round(ch['top'],2)])
        if bad:issues.append(dict(page=i+1,kind='safe_area',examples=bad[:4],count=len(bad)))
        txt=pg.extract_text(x_tolerance=2,y_tolerance=3) or '';texts.append(txt)
        if i and f'{i+1} / {len(book.pages)}' not in txt:issues.append(dict(page=i+1,kind='footer'))
        if '\ufffd' in txt or '\x00' in txt:issues.append(dict(page=i+1,kind='glyph'))
        if not txt.strip():issues.append(dict(page=i+1,kind='blank'))
        if i%50==0:print('Checked page',i+1,flush=True)

for q in ALL:
    qp=loc[q['id']]['question_page'];ep=loc[q['id']]['explanation_page']
    text=texts[qp-1];m=re.search(r'(?m)^'+f'{q["n"]:02d}'+r'\.\s',text)
    assert m,(q['id'],'question missing',qp)
    tail=text[m.start():];nxt=re.search(r'(?m)^'+f'{q["n"]+1:02d}'+r'\.\s',tail)
    if nxt:tail=tail[:nxt.start()]
    if norm(q['stem']) not in norm(tail):issues.append(dict(id=q['id'],kind='question_text',page=qp))
    for i,opt in enumerate(q['opts']):
        if norm(f'({chr(65+i)}) '+opt) not in norm(tail):issues.append(dict(id=q['id'],kind='choice_split',page=qp,letter=chr(65+i)))
    assert not any(x in tail for x in ['핵심 문법','시험장에서는','정답:','★★']),q['id']
    text=texts[ep-1];m=re.search(r'(?m)^'+f'{q["n"]:02d}'+r'\. 정답: \('+q['answer']+r'\)',text)
    assert m,(q['id'],'explanation answer missing',ep)
    tail=text[m.start():];nxt=re.search(r'(?m)^'+f'{q["n"]+1:02d}'+r'\. 정답:',tail)
    if nxt:tail=tail[:nxt.start()]
    for label in ['문장 구조','풀이','오답','핵심 문법','시험장에서는','이 문제에서 가져가야 할 것']:
        if label not in tail:issues.append(dict(id=q['id'],kind='explanation_split',label=label,page=ep))
    for i,opt in enumerate(q['opts']):
        if norm(f'({chr(65+i)}) '+opt) not in norm(tail):issues.append(dict(id=q['id'],kind='analysis_missing',page=ep,letter=chr(65+i)))
    expected=norm(re.sub(r'\{[SVOCM]+\}','',q['structure']).replace(' / ',' ').rstrip('.'))
    # Compare the whole completed sentence after removing the structure labels.
    cleaned=re.sub(r'\[[SVOCM]\]','',tail).replace(' / ',' ')
    if expected.replace('/','') not in norm(cleaned).replace('/',''):issues.append(dict(id=q['id'],kind='structure_mismatch',page=ep))

for c in CH:
    assert len(c['practice'])==8 and len(c['review'])==10
    for sec in ['practice','review']:
        items=c[sec];ep=loc[items[0]['id']]['explanation_page']
        found={int(n):a for n,a in re.findall(r'(\d{2})\s+\(([ABCD])\)',texts[ep-1])}
        assert found=={q['n']:q['answer'] for q in items},(c['n'],sec,found)
    n=c['n'];cp=int(starts[str(n)])
    assert f'Chapter {n:02d}.' in texts[cp-1]
    for i,co in enumerate(c['concepts']):
        allconcept=' '.join(texts[j] for j in range(cp-1,cp+1))
        assert norm(co['example']) in norm(allconcept),(n,i,'example')
        assert norm(co['translation']) in norm(allconcept),(n,i,'translation')

assert len(reader.outline)==21
assert 'RC 필수 문법 한 장 요약' in texts[-1]
assert Counter(q['answer'] for q in ALL)=={'A':83,'B':83,'C':83,'D':83}
fonts=set()
for pg in reader.pages:
    for ref in pg['/Resources']['/Font'].values():
        ft=ref.get_object();fonts.add(str(ft.get('/BaseFont')))
        if ft.get('/Subtype')=='/TrueType':assert '/FontFile2' in ft['/FontDescriptor'].get_object()
report=dict(pages=len(reader.pages),questions=len(ALL),concepts=sum(len(c['concepts']) for c in CH),
            reading_passages=len(CH),notes_pages=18,chapter_count=len(CH),answers=dict(Counter(q['answer'] for q in ALL)),
            fonts=sorted(fonts),issues=issues,bytes=PDF.stat().st_size)
(BASE/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='issues'},ensure_ascii=False),flush=True)
print('Issues',len(issues),issues[:5],flush=True)
assert not issues

if '--contacts' in sys.argv:
    images=sorted((BASE/'render').glob('page-*.png'));assert len(images)==len(reader.pages)
    for start in range(0,len(images),16):
        tw,th=310,439
        sheet=Image.new('RGB',(4*(tw+14)+14,4*(th+28)+14),'#d7dce2');draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(images[start:start+16]):
            im=Image.open(path).convert('RGB');im.thumbnail((tw,th))
            x=14+(j%4)*(tw+14);y=14+(j//4)*(th+28)
            sheet.paste(im,(x,y));draw.text((x,y+th+3),f'{start+j+1} | {manifest[start+j]["section"]}',fill='black')
        sheet.save(BASE/f'contact-{start//16+1:02d}.jpg',quality=90)
    print('Contact sheets', (len(images)+15)//16,flush=True)
