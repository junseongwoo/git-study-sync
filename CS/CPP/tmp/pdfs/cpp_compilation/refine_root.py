import json
from pathlib import Path
from write_root_units import f,ld
R=Path(__file__).resolve().parent
def load(n):return json.loads((R/f'unit_{n:02}.json').read_text('utf-8'))
def put(u):(R/f'unit_{u["unit"]:02}.json').write_text(json.dumps(u,ensure_ascii=False,indent=2),'utf-8')
def walk(x):
 if isinstance(x,dict):
  if 'text' in x:yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
u=load(12)
for x in walk(u):
 if x['text'].startswith('memory_order_relaxed 는 서로'):x['text']='memory_order_relaxed 는 단일 쓰레드 관점의 결과가 같다면 서로 다른 변수의 relaxed 메모리 연산을 재배치할 수 있다.'
 if x['text'].startswith('std::async 는 함수를'):x.update(f('std::async 는 실행 결과를 future 로 돌려주며, launch::async 는 바로 새 쓰레드에서 실행하고 launch::deferred 는 future::get 시 새 쓰레드 없이 실행한다.',808,'16장 / std::async','새로운\n쓰레드를생성하지않음'))
u['concepts'][1]['items'].insert(1,f('뮤텍스의 lock 과 unlock 사이에서 한 쓰레드만 실행할 수 있는 코드 부분을 임계 영역(critical section)이라고 부른다.',750,'16장 / 뮤텍스(mutex)','임계영역(critical section)'))
u['concepts'][1]['items'].insert(3,f('원문의 데드락 예제에서는 worker1 이 m1 을, worker2 가 m2 를 잠근 채 서로 상대가 가진 뮤텍스의 해제를 기다려 진행하지 못한다.',[754,755],'16장 / 데드락(deadlock)','데드락상황'))
put(u)
u=load(15)
pre=ld('강의 자료는 디버깅 가능한 Debug 구성을 확인하며, Release 모드에서는 값을 제대로 볼 수 없다고 설명한다.',4,'Preface','Release 모드에서는값을제대로볼수없음')
u['concepts'][0]['items'].insert(1,pre);u['procedures'][0]['steps'].insert(0,pre)
for x in walk(u):
 if x['text'].startswith('중단할 위치의 왼쪽'):x['text']='중단할 위치의 왼쪽 끝 클릭 또는 F9 으로 중단점을 만들고, Debug 구성에서 Ctrl+F5 가 아닌 F5 로 빌드 후 디버깅을 실행한다.'
put(u)
# More direct source pages for the STL storage/comparison descriptions.
u=load(8)
for x in walk(u):
 if any(k in x['text'] for k in ['연속 저장','양방향 연결']):
  for ref in x.get('refs',[]):
   if ref['source']=='B':
    if '연속 저장' in x['text']:ref['pages']=sorted(set(ref['pages']+[500]))
    if '양방향 연결' in x['text']:ref['pages']=sorted(set(ref['pages']+[518,519]))
put(u)
print('source conditions refined')
