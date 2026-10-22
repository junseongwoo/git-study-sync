from pathlib import Path
import hashlib
import json
import runpy
import sys
import pymupdf as fitz

ROOT=Path(__file__).resolve().parent
paths=json.loads((ROOT/'deliverables.json').read_text(encoding='utf-8'))
old_registry=(ROOT/'registry.json').read_bytes()
old_audit=hashlib.sha256(Path(paths['audit']).read_bytes()).hexdigest()

def content_signature(page):
    rows=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            rows.extend((s['text'],tuple(round(v,3) for v in s['bbox']),round(s['size'],3),s['font']) for s in line['spans'])
    return rows

before={}
for key in ['notes','cheat']:
    with fitz.open(paths[key]) as d:
        before[key]=[content_signature(p) for p in d]

sys.argv=['build_notes.py','--study-only']
runpy.run_path(str(ROOT/'build_notes.py'),run_name='__main__')
assert (ROOT/'registry.json').read_bytes()==old_registry,'Source references changed'
assert hashlib.sha256(Path(paths['audit']).read_bytes()).hexdigest()==old_audit,'Audit unexpectedly changed'

quality=json.loads((ROOT/'quality_report.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'final_manifest.json').read_text(encoding='utf-8'))
for key,label in [('notes','정리 및 요약'),('cheat','확인 및 시험')]:
    with fitz.open(paths[key]) as d:
        assert len(d)==len(before[key]),(key,len(d),len(before[key]))
        assert all(content_signature(d[i])==before[key][i] for i in range(1,len(d))),f'{key}: later pages changed'
        first=d[0].get_text()
        assert all(s in first for s in ['컴퓨터 네트워킹','하향식 접근',label])
        assert 'A4 세로' not in first and '원문 기반 학습 노트' not in first
        mm=72/25.4
        for block in d[0].get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for s in line['spans']:
                    x0,y0,x1,y1=s['bbox']
                    assert x0>=20*mm-.5 and y0>=20*mm-.5 and x1<=d[0].rect.width-20*mm+.5 and y1<=d[0].rect.height-20*mm+.5,(key,s)
        assert '\ufffd' not in first and '\u25a1' not in first
        d[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(ROOT/'render'/key/'001.png')
        manifest['files'][key].update(bytes=Path(paths[key]).stat().st_size,sha256=hashlib.sha256(Path(paths[key]).read_bytes()).hexdigest())
        quality['files'][key]['visual_checked_pages']=[i for i in quality['files'][key].get('visual_checked_pages',[]) if i!=1]
        print(f'{key}: {len(d)} pages; first-page title updated; all later page content and positions unchanged',flush=True)
quality['visual_review_complete']=False
(ROOT/'quality_report.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'final_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Source references and audit PDF unchanged.',flush=True)
