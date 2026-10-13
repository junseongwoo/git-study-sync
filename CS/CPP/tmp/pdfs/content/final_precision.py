import json
from pathlib import Path
p=Path(__file__).with_name('part5.json')
d=json.loads(p.read_text(encoding='utf-8'))
for s in d['chapters'][16]['sections']:
    if s['label']=='핵심 단서':
        s['text']=s['text'].replace('recommend가 제안인지 단순한 사실 전달인지 구별하면','suggest가 제안인지 사실을 시사하는 뜻인지 구별하면')
for s in d['chapters'][18]['sections']:
    if s['label']=='헷갈리는 문법 비교':
        s['text']='few requests는 요청이 매우 적다는 점을, a few requests는 일부 요청이 있다는 점을 강조한다. little space와 a little space도 같은 방식으로 적은 양과 일부 존재를 강조하지만, 충분·부족 또는 좋고 나쁨의 평가는 문맥에 따라 판단한다. either는 두 대상 중 어느 하나, neither는 둘 중 어느 것도 아니라는 의미를 나타낸다.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Applied final concept precision corrections')
