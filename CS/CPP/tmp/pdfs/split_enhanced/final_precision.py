from pathlib import Path
import json
p=Path(__file__).with_name('part5_extra.json');d=json.loads(p.read_text(encoding='utf-8'))
d['chapters'][16]['blocks'][1]['text']='예제: The committee requested that each new employee review the handbook and _____ the training. 선택지는 (A) completes, (B) complete, (C) completed, (D) completing이다. [The committee requested] [that each new employee review the handbook and _____ the training]에서 이미 쓰인 원형 review가 이 요구절의 원형 용법과 공유 주어 병렬을 확정한다. A·C는 원형 review와 같은 절에서 병렬로 연결할 형태가 아니며 D는 이 절의 원형 정동사 자리를 채우지 못한다. B complete를 넣으면 review와 complete라는 두 요구 행동이 연결된다. 영국 영어의 요구절에는 should 또는 직설법 변형도 나타날 수 있으므로, 요구 의미만 보고 다른 변형을 언제나 비문이라고 단정하지 않는다.'
for c in d['chapters']:
    for q in c['questions']:
        if q['id']=='P5-B27':
            for k in ['prompt','clue','analysis','order']:
                q[k]=q[k].replace('will close','will be closed')
            q['analysis']='[The notice] [states] [_____ the building will be closed at 6 p.m.]이다. be closed는 수동 동사구이며 이 절에는 주어나 직접 목적어의 공백이 없다.'
            q['rule']='완전한 진술 내용을 명사절로 연결하는 that는 절 내부의 명사 성분을 대신하지 않는다. 능동·수동 동사구의 실제 구조를 기준으로 공백을 판단한다.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Refined worked mandative example and complete-clause item')
