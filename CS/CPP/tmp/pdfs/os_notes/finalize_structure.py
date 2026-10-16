import json
from pathlib import Path
H=Path(__file__).resolve().parent
mp=json.loads((H/'source_map.json').read_text(encoding='utf-8'))
for f in sorted((H/'chapters').glob('*.json')):
 ch=json.loads(f.read_text(encoding='utf-8-sig'))
 if ch['id']=='OP7':continue
 original=next(x for x in mp['chapters'] if x['number']==ch['order'])
 if not original['available']:
  ch['available']=False
  ch['overview']=['원본 목차에서 제2장의 제목과 절 구성을 확인했으나 본문은 제공되지 않았다.']
  ch['sections']=[{'number':'2','title':'본문 미제공 안내','source':{'pdf':[1],'printed':[]},'blocks':[
   {'type':'p','text':'제공 PDF는 인쇄 59쪽 다음에 117쪽으로 이어진다. 제2장 본문은 원문에서 확인되지 않음. 아래는 목차에서 확인한 절 이름이며, 해당 개념의 정의나 작동 원리를 요약한 것으로 표시하지 않는다.'},
   {'type':'table','headers':['목차의 절','절 이름'],'rows':[[s['number'],s['title']] for s in original['sections']]}
  ]}]
  ch['index_terms']=[];ch['checklist']=[];ch['review']=[];ch['key_points']=[]
 else:
  ch['available']=True
  existing={s['number'] for s in ch['sections']}
  additions={s['number']:{'number':s['number'],'title':s['title'],'source':{'pdf':s['pdf'],'printed':s['printed']},'blocks':[]} for s in original['sections'] if s['number'] not in existing}
  for n,s in additions.items():
   if not any(x.startswith(n+'.') for x in existing):
    raise ValueError(f'Main section absent without child coverage: {ch["id"]}:{n}')
   ch['sections'].append(s)
   ch['coverage'].append({'number':n,'title':s['title'],'source':s['source'],'topics':['관련 하위절에 상세 내용 정리']})
  def numberkey(s):
   n=s['number'];return [int(x) if x.isdigit() else 10000 for x in n.split('.')]
  ch['sections'].sort(key=numberkey)
 f.write_text(json.dumps(ch,ensure_ascii=False,indent=2),encoding='utf-8')
print('main chapter/section structure finalized')
