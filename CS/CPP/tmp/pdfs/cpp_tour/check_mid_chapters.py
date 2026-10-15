from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
mapping=json.loads((ROOT/'source_map.json').read_text(encoding='utf-8'))
page_by_pdf={p['pdf_page']:p['printed_page'] for p in mapping['pages']}
errors=[];stats=[]
for n in range(6,11):
    path=ROOT/'chapters'/f'{n:02d}.json'
    raw=path.read_text(encoding='utf-8');ch=json.loads(raw)
    if '\ufffd' in raw:errors.append(f'{n}: replacement character')
    ids={c['id'] for c in ch['codes']}
    for s in ch['sections']:
        for b in s['blocks']:
            if b['type']=='code_ref' and b['id'] not in ids:errors.append(f'{n}: unresolved {b["id"]}')
    def walk(x):
        if isinstance(x,dict):
            if 'source' in x:
                p=x['source']
                if len(p['pdf'])!=len(p['printed']):errors.append(f'{n}: source lengths')
                if any(page_by_pdf.get(a)!=b for a,b in zip(p['pdf'],p['printed'])):errors.append(f'{n}: page map mismatch')
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(ch)
    stats.append({'chapter':n,'sections_and_subsections':len(ch['sections']),'codes':len(ch['codes']),'section_prose_chars':sum(len(b.get('text',''))+sum(map(len,b.get('items',[]))) for s in ch['sections'] for b in s['blocks'])})
report={'errors':errors,'chapters':stats,'source_review':{'only_source':mapping['source_pdf'],'read_ocr_in_full_for_chapters':[6,7,8,9,10],'selected_code_images_reviewed':[139,140,141,143,147,148,150,157,163,167,171,173,174,175,176,183,184,187,188,192,193,194,195,196,197,198,200,201,202,203,204,212,213,214,215,216,217,218,220,223],'scope':'대표 코드 및 주요 표는 원문 이미지와 직접 대조. 전체 원문 모든 문자에 대한 독립적 교정 완료를 뜻하지 않음.','known_original_uncertainties':['인쇄146 T[N];','인쇄153 [=x]','인쇄195 string res(...) 생성','인쇄200·204·205 일부 정규 표현식 기호','인쇄216 is/cin 혼용','인쇄228 확장자 옮긴이 설명']}}
(ROOT/'mid_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'errors':errors,'chapters':stats},ensure_ascii=False))
