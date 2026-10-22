import json,re,unicodedata,collections
from pathlib import Path
R=Path(__file__).resolve().parent
sources=json.loads((R/'source_registry.json').read_text('utf-8'))
pages={s:{p['pdf_page']:p['text'] for p in json.loads((R/f'sources/{s}_pages.json').read_text('utf-8'))} for s in sources}
def norm(t):return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',t)).lower()
def walk(x,path=''):
 if isinstance(x,dict):
  if 'refs' in x:yield path,x
  for k,v in x.items():yield from walk(v,path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,path+f'[{i}]')
issues=[];stats=[]
for path in sorted(R.glob('unit_??.json')):
 u=json.loads(path.read_text('utf-8-sig'));facts=list(walk(u));seen=set();miss=[];unchecked=[];checked={(x['source'],p) for x in u['checked_images'] for p in x['pages']}
 for loc,f in facts:
  assert f.get('evidence'),(path,loc,'no evidence')
  text='\n'.join(pages[r['source']][int(p)] for r in f['refs'] for p in r['pages'])
  for r in f['refs']:
   assert r.get('section') and r.get('pages'),(path,loc,r)
   for p in r['pages']:
    assert 1<=p<=sources[r['source']]['pdf_pages'],(path,loc,p)
    if r['source']=='K' and (r['source'],p) not in checked:unchecked.append(p)
  ev=norm(f['evidence']);content=norm(text)
  # Editorial punctuation or ellipses may join brief evidence fragments.
  if ev and ev not in content:
   parts=[norm(t) for t in re.split(r'\s*/\s*|…|\.\.\.|\n|\s*;\s*',f['evidence']) if len(norm(t))>2]
   if not parts or not all(t in content for t in parts):miss.append(dict(location=loc,text=f.get('text',f.get('expression',f.get('label'))),evidence=f['evidence'],refs=f['refs']))
  seen.add((f.get('text',f.get('expression',f.get('code'))),json.dumps(f['refs'],sort_keys=True)))
 stats.append(dict(unit=u['unit'],core=sum(len(x['items']) for x in u['concepts']),items=len(seen),evidence_misses=len(miss),unchecked_K=sorted(set(unchecked))))
 issues.extend(dict(unit=u['unit'],**x) for x in miss)
(R/'content_validation.json').write_text(json.dumps(dict(stats=stats,evidence_review=issues),ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2));print('Evidence fragments to review:',len(issues))
