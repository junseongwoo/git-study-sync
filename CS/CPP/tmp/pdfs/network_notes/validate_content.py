from pathlib import Path
import difflib
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parent
RANGES={1:(1,74,8),2:(75,169,8),3:(171,279,7),4:(281,340,6),5:(341,402,6),6:(403,475,6)}

def clean(t):
    return re.sub(r'[^가-힣a-zA-Z0-9]','',unicodedata.normalize('NFKC',str(t))).lower()

def facts(o,path=''):
    if isinstance(o,dict):
        if {'text','section','pages','evidence'}<=o.keys():
            yield path,o
        elif {'expression','section','pages','evidence'}<=o.keys():
            yield path,{**o,'text':o['expression']}
        else:
            for k,v in o.items():
                yield from facts(v,path+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o):
            yield from facts(v,path+f'[{i}]')

def main():
    all_results={}
    for ch in range(1,7):
        p=ROOT/f'chapter_{ch}.json'
        if not p.exists():
            continue
        data=json.loads(p.read_text(encoding='utf-8-sig'))
        lo,hi,offset=RANGES[ch]
        checked=set(data.get('checked_images',[]))
        rows=[]
        for path,f in facts(data):
            pages=f['pages']
            assert pages and all(lo<=int(p)<=hi for p in pages),(ch,path,pages)
            assert f['text'] and f['evidence'],(ch,path)
            source='\n'.join((ROOT/'ocr'/f'{int(p)+offset:04d}.txt').read_text(encoding='utf-8') for p in pages)
            src=clean(source)
            parts=[clean(x) for x in str(f['evidence']).split(' / ') if clean(x)]
            score=[]
            for e in parts:
                if e in src:
                    score.append(1)
                else:
                    match=difflib.SequenceMatcher(None,e,src,autojunk=False).find_longest_match()
                    score.append(match.size/max(1,len(e)))
            rows.append({'path':path,'text':f['text'],'pages':pages,'evidence':f['evidence'],'ocr_match':round(min(score,default=0),3),'image_checked':all(int(p)+offset in checked for p in pages)})
        all_results[str(ch)]={'facts':len(rows),'checked_images':len(checked),'low_ocr_match':[r for r in rows if r['ocr_match']<.45],'unchecked_citations':[r for r in rows if not r['image_checked']]}
        print(f'chapter {ch}: {len(rows)} facts, low OCR matches {len(all_results[str(ch)]["low_ocr_match"])}, unchecked citations {len(all_results[str(ch)]["unchecked_citations"])}',flush=True)
    (ROOT/'content_validation.json').write_text(json.dumps(all_results,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
