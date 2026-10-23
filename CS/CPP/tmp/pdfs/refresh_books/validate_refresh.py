from pathlib import Path
import json

root=Path(__file__).resolve().parent
results={}
for book in ['tour','os']:
    folder=root/book
    cfg=json.loads((folder/'config.json').read_text('utf-8'))
    issues=[]
    count=0
    all_pages=set()
    for path in sorted((folder/'overlays').glob('??.json')):
        overlay=json.loads(path.read_text('utf-8-sig'))
        checked=set(overlay.get('checked_images',[]))
        if overlay.get('pending_image_pages'):issues.append([path.name,'pending images'])
        def walk(value):
            global count
            if isinstance(value,dict):
                if 'refs' in value:
                    count+=1
                    for ref in value['refs']:
                        for p in ref['pages']:
                            all_pages.add(p)
                            if not 1<=p<=cfg['pdf_pages']:issues.append([path.name,'out of range',p])
                            if p not in checked:issues.append([path.name,'unchecked image',p])
                for key,child in value.items():
                    if key!='corrections':walk(child)
            elif isinstance(value,list):
                for child in value:walk(child)
        walk(overlay)
    registry=json.loads((folder/'registry.json').read_text('utf-8'))
    ids=[r['id'] for r in registry]
    assert len(ids)==len(set(ids)),book
    assert all(r['refs'] for r in registry),book
    results[book]={'overlay_facts':count,'checked_source_pages':sorted(all_pages),'registered_entries':len(ids),'issues':issues}
    print(book,'facts',count,'checked pages',len(all_pages),'entries',len(ids),'issues',issues)
(root/'content_validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf-8')
assert not any(x['issues'] for x in results.values()),results
