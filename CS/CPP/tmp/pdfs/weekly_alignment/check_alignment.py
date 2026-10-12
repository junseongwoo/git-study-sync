from pathlib import Path
import json, sys
from pypdf import PdfReader
import pdfplumber

ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'output/pdf/.source'))
import build_book as b

base=ROOT/'tmp/pdfs/weekly_alignment'
old=PdfReader(base/'before.pdf')
new=PdfReader(ROOT/'output/pdf/TOEIC_900_Vocabulary_60_Day_Challenge.pdf')
changed=[i+1 for i,(a,z) in enumerate(zip(old.pages,new.pages))
         if a.get_contents().get_data()!=z.get_contents().get_data()]
assert changed==list(range(309,338,4)),changed
days=b.load_days()
assert len(old.pages)==len(new.pages)==373
with pdfplumber.open(ROOT/'output/pdf/TOEIC_900_Vocabulary_60_Day_Challenge.pdf') as pdf:
    for n,day in enumerate(b.WEEKLY):
        source=days[day-7:day]
        entries=[d['entries'][i] for d in source for i in [0,10,20,27]]+[source[-1]['entries'][i] for i in [1,11]]
        p=pdf.pages[308+n*4]
        first=next(w for w in p.extract_words() if w['text']=='01' and abs(w['x0']-46)<.1)
        for index,e in enumerate(entries):
            half,row=divmod(index,15)
            expected_x=158+half*b.CW/2
            top=first['top']+row*35
            chars=[c for c in p.chars if expected_x-.1<=c['x0']<expected_x+(b.CW/2-112)-6
                   and abs(c['top']-top)<.2]
            text=''.join(c['text'] for c in chars)
            assert text==e['meaning'],(n+1,index+1,text,e['meaning'])
            assert abs(chars[0]['x0']-expected_x)<.01
            assert max(c['x1'] for c in chars)<expected_x+(b.CW/2-112)-12
            assert b.P(e['colloc'],'cell').wrap(b.CW/2-12,100)[1]<=12.5
        p.close()
report={'changed_pages':changed,'unchanged_pages':365,'aligned_meanings':240,
        'same_row_pairs':120,'total_pages':373,'layout_checks_passed':True}
(ROOT/'output/pdf/.source/weekly_alignment_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
