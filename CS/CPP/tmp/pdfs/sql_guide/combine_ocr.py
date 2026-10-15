from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
source = ROOT / 'ocr'
pages = []
for page in range(1, 787):
    text = (source / f'{page:04d}.txt').read_text(encoding='utf-8')
    pages.append(f'\n\n===== PDF PAGE {page:04d} =====\n\n{text}\n')
(ROOT / 'ocr_all.txt').write_text(''.join(pages), encoding='utf-8')
for start in range(1, 787, 100):
    end = min(start+99, 786)
    (ROOT / f'ocr_pages_{start:04d}_{end:04d}.txt').write_text(''.join(pages[start-1:end]), encoding='utf-8')
report = {
    'pages_expected':786,
    'pages_text':len(list(source.glob('*.txt'))),
    'pages_word_coordinates':len(list((source/'lines').glob('*.json'))),
    'empty_pages':[i+1 for i,p in enumerate(pages) if len(p.split('=====\n\n',1)[-1].strip())<5],
    'text_characters':sum(len(p) for p in pages),
    'error_logs':[p.name for p in source.glob('*.log')],
}
(ROOT/'ocr_quality_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
