from pathlib import Path
import json,re,collections
R=Path(__file__).resolve().parent;OLD=R.parent/'cpp_tour'
def split(s):return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[가-힣A-Za-z<\[])',s.replace('**','')) if x.strip()]
def norm(t):return re.sub(r'[^a-z0-9가-힣]','',t.lower())
def make(n):
 c=json.loads((OLD/'chapters'/f'{n:02}.json').read_text('utf-8-sig'));return c,{s['number']:s for s in c['sections']}
def fact(text,s,term=None,narrow=True):
 pages=s['source']['pdf']
 if narrow and len(pages)>1:
  ns=norm(text);grams={ns[i:i+3] for i in range(max(0,len(ns)-2))};rank=[]
  for p in pages:
   content=norm((OLD/'ocr_tesseract'/f'{p:04}.txt').read_text('utf-8-sig'));score=sum(g in content for g in grams);rank.append((score,p))
  rank.sort(reverse=True);pages=sorted(p for _,p in rank[:2])
 return dict(text=text,refs=[dict(source='T',section=s['number']+' '+s['title'],pages=pages)],evidence=term or text[:24])
def F(sec,text,term=None):return fact(text,S[sec],term)
def oldf(sec,block=0,sentence=0,term=None):return fact(split(S[sec]['blocks'][block]['text'])[sentence],S[sec],term)
DATA={
9:[('string','9.2','string은 문자 시퀀스를 저장하고 조작하는 Regular 타입이다.'),('짧은 문자열 최적화','9.2.1','짧은 문자열 최적화는 짧은 값을 객체 자체에 두고 긴 값에만 자유 저장소를 이용한다.'),('string_view','9.3','string_view는 연속된 문자 시퀀스를 나타내는 포인터와 길이의 쌍으로 볼 수 있으며, 문자를 소유하지 않는다.'),('정규 표현식','9.4','정규 표현식은 텍스트 안의 패턴을 간단히 기술하고 찾는 도구다.'),('smatch','9.4.1','smatch는 string의 매치 결과들을 저장하는 컨테이너다.'),('regex_iterator','9.4.3','regex_iterator는 시퀀스에서 패턴을 차례로 찾아 순회한다.')],
10:[('입출력 스트림','10.1','입출력 스트림 라이브러리는 텍스트와 수치 값의 형식화·비형식화 및 버퍼링된 입출력을 지원한다.'),('cout·cerr','10.2','cout은 표준 출력, cerr은 에러 보고 스트림이다.'),('cin','10.3','cin은 표준 입력 스트림이며, >>는 istream에서 값을 가져오는 연산이다.'),('조정자','10.6','조정자는 입력·출력 형식을 제어한다.'),('파일 스트림','10.7','<fstream>의 ifstream은 읽기, ofstream은 쓰기, fstream은 읽기와 쓰기용이다.'),('문자열 스트림','10.8','<sstream>의 istringstream은 string에서 읽고 ostringstream은 string에 쓰며 stringstream은 둘 다 한다.'),('path','10.10','path는 운영체제의 기본 문자 집합과 관례를 다루는 경로 표현이다.')],
11:[('컨테이너','11.1','컨테이너는 객체를 저장하는 일이 주목적인 클래스다.'),('vector<T>','11.2','vector<T>는 T 타입 요소가 메모리에 연속적으로 저장되는 시퀀스다.'),('list','11.3','list는 이중 연결 리스트이며, 다른 요소를 이동시키지 않고 시퀀스 중간에 삽입·삭제할 때 사용한다.'),('map','11.4','map은 키와 값의 쌍을 담고 조회에 최적화된 연관 컨테이너다.'),('unordered_map','11.5','unordered_map은 해시 테이블을 이용하며 요소 사이의 순서를 유지하지 않는다.'),('at()','11.2.2','at()은 구간 밖 인덱스에 out_of_range를 던진다.')],
12:[('반개구간','12.1','입력 시퀀스는 첫 요소를 포함하고 끝 위치는 포함하지 않는 반개구간 [begin:end)이며, 첫 요소와 마지막 요소 다음을 가리키는 반복자 쌍으로 나타낸다.'),('반복자','12.3','반복자는 특정 타입의 객체이며 저장 구조에 맞는 정보를 가진다.'),('술어','12.5','술어는 알고리즘이 각 요소에 적용할 조건을 전달하는 수단이다.'),('ostream_iterator','12.4','ostream_iterator는 스트림과 출력 타입을 지정해 만들며, 역참조 위치에 대입하면 스트림으로 출력한다.'),('표준 알고리즘','12.6','표준 알고리즘은 요소 시퀀스에 적용되는 함수 템플릿 연산이며, std에 정의되고 <algorithm>에서 제공된다.'),('병렬 실행·SIMD','12.9','병렬 실행은 여러 스레드에서 작업하고 벡터화된 실행(SIMD)은 한 스레드에서 벡터화로 작업한다.'),('find','12.2','find는 찾은 요소의 반복자를 반환하고, 찾지 못하면 입력 구간의 end()를 반환한다.'),('find_if','12.5','find_if는 전달된 술어가 참이 되는 첫 요소를 찾는다.')],
13:[('자원','13.2','자원은 획득한 후 언젠가 해제해야 하는 것으로 메모리·소켓·스레드 핸들·파일 핸들이 예다.'),('unique_ptr·shared_ptr','13.2.1','unique_ptr은 유일한 소유권을, shared_ptr은 공유된 소유권을 표현한다.'),('gsl::span','13.3','gsl::span은 요소 시퀀스의 포인터와 길이를 함께 표현하는 구간 참조이며, 그 요소를 소유하지 않는다.'),('optional<A>','13.5.2','optional<A>는 A 또는 아무것도 없음을 나타낸다.'),('any','13.5.3','any는 임의의 타입을 저장하며 저장된 객체가 있으면 그 타입을 기억한다.'),('function','13.8.3','function 객체는 ()로 호출할 수 있는 대상을 저장한다.'),('타입 함수','13.9','타입 함수는 타입 자체를 인자로 받거나 타입을 반환하며 컴파일 시간에 평가된다.')],
14:[('수치 알고리즘','14.3','<numeric>은 시퀀스의 합·내적·부분합·이웃한 차이 등을 일반화한다.'),('reduce','14.3.1','reduce는 accumulate와 달리 요소 연산의 순서가 정해지지 않는다.'),('complex<Scalar>','14.4','<complex>의 complex<Scalar>는 실수부와 허수부 타입을 매개변수로 받는 복소수 템플릿이다.'),('난수 엔진·분포','14.5','엔진은 난수 또는 의사 난수 시퀀스를 만들고, 분포는 그 값을 수학적 분포의 특정 구간으로 매핑한다.'),('valarray','14.6','<valarray>의 valarray는 일반성이 다소 낮은 대신 수치 계산 최적화에 더 적합하도록 제공되는 배열 템플릿이다.'),('numeric_limits','14.7','<limits>의 numeric_limits는 내장 수치 타입의 속성을 기술한다.')],
15:[('동시성','15.1','동시성은 여러 태스크를 동시에 실행하는 것이다.'),('태스크·thread','15.2','태스크는 다른 계산과 동시에 실행할 수 있는 작업이며, thread는 이를 표현하는 시스템 수준 개념이다.'),('mutex','15.5','mutex는 상호 배제 객체이며 lock()으로 획득하고 unlock()으로 해제한다.'),('condition_variable','15.6','condition_variable은 다른 태스크의 행동으로 조건이나 이벤트가 생기기를 기다리는 수단이다.'),('future·promise','15.7.1','promise에 값을 넣으면 연결된 future에서 그 값을 볼 수 있으며, future<X>::get()은 필요한 경우 계산이 끝날 때까지 기다린다.'),('packaged_task','15.7.2','packaged_task는 태스크의 반환값이나 예외를 promise에 넣는 래퍼를 제공하고, get_future()로 대응 future를 돌려준다.'),('async()','15.7.3','async()는 잠재적으로 비동기 실행할 태스크를 함수 호출과 유사하게 시작한다.')],
16:[('WG21','16.1.3','ISO C++ 위원회는 WG21로 불린다.'),('C++11','16.1.3','두 번째 표준 C++11은 2011년 8월 21:0으로 승인됐다.'),('표준과 스타일','16.1.4','표준은 기능의 동작을 규정하지만 효과적인 사용법을 모두 알려주지는 않는다.'),('지원 중단','16.2.7','지원 중단은 해당 기능을 피하라는 강한 신호이지만 즉시 제거와 동일하지 않다.'),('void*','16.3.2.2','C에서 void*를 다른 포인터 타입의 대입 우측이나 초깃값으로 사용할 수 있는 경우에도 C++에서는 항상 허용되지 않는다.'),('C 링크','16.3.2.3','C 함수와 C++ 코드 사이에서 호출할 수 있게 하려면 C 링크를 명시한다.')]
}
COMPS={9:(0,2),10:(4,5),11:(3,4),12:(6,7),13:(3,4),14:(1,4),15:(4,5),16:(2,3)}
QUESTIONS={9:['string의 주된 역할은?','string_view가 문자를 소유하는가?','smatch는 무엇을 저장하는가?','regex_iterator의 역할은?'],10:['입출력 스트림 라이브러리가 지원하는 작업은?','cout과 cerr은 각각 어떤 스트림인가?','파일 스트림 세 종류의 용도는?','문자열 스트림 세 종류의 용도는?'],11:['컨테이너란 무엇인가?','vector<T>의 요소 저장 방식은?','없는 구간을 at()으로 접근하면?','unordered_map은 어떤 저장 방식을 사용하며 요소 순서를 유지하는가?'],12:['알고리즘 입력의 반개구간은 어떻게 표현하는가?','술어의 역할은?','find가 검색에 실패하면 무엇을 반환하는가?','find_if는 어떤 요소를 찾는가?'],13:['책에서 자원은 무엇을 뜻하는가?','unique_ptr과 shared_ptr의 소유권 차이는?','optional<A>가 나타내는 두 상태는?','function 객체는 무엇을 저장하는가?'],14:['<numeric>이 일반화하는 작업은?','reduce의 연산 순서는 accumulate와 어떻게 다른가?','난수 엔진과 분포는 각각 무엇을 하는가?','numeric_limits는 무엇을 기술하는가?'],15:['태스크와 thread의 관계는?','mutex의 획득·해제 연산은?','promise와 future는 결과를 어떻게 전달하는가?','packaged_task는 어떤 래퍼를 제공하는가?'],16:['ISO C++ 위원회의 이름은?','원문에서 C++11의 승인 시점과 표결은?','지원 중단은 즉시 제거와 같은가?','C와 C++ 코드 사이의 호출을 위해 무엇을 명시하는가?']}
ANS={9:[0,2,4,5],10:[0,1,4,5],11:[0,1,5,4],12:[0,2,6,7],13:[0,1,3,5],14:[0,1,3,5],15:[1,2,4,5],16:[0,1,3,5]}
for n,data in DATA.items():
 c,S=make(n);defs=[dict(term=term,definition=F(sec,text,term)) for term,sec,text in data]
 last=next((s for s in c['sections'] if s['title']=='조언'),None)
 if n!=16:
  items=next(b['items'] for b in last['blocks'] if b['type']=='bullets');summary=[fact(t,last,narrow=False) for t in items[:4]];basis=last['number']+' 조언'
 else:summary=[defs[i]['definition'] for i in [1,2,3,5]];basis='편집 요약: 16.1~16.3의 수록 본문. 16.5 조언 본문은 원문에서 확인 불가.'
 rows=[]
 for i in COMPS[n]:
  d=defs[i];label={**d['definition'],'text':d['term']};rows.append([label,d['definition']])
 selected=[defs[i] for i in ([0,2,3] if n==9 else [0,1,2])]
 o=dict(chapter=n,title=c['title'],source_code='T',learning=[defs[0]['definition'],defs[1]['definition']],terms=defs,summary_basis=basis,summary=summary,review=[dict(question=q,answer=defs[i]['definition']) for q,i in zip(QUESTIONS[n],ANS[n])],cheat=dict(definitions=selected,comparison_title='원문에서 설명한 역할·특징',comparison_headers=['항목','책의 설명'],comparison_rows=rows,formulas=[]),checked_images=[],editor_notes=[],corrections=[])
 pages=sorted({p for d in defs for ref in d['definition']['refs'] for p in ref['pages']}|{p for d in summary for ref in d['refs'] for p in ref['pages']})
 o['pending_image_pages']=pages
 (R/'tour/overlays'/f'{n:02}.json').write_text(json.dumps(o,ensure_ascii=False,indent=2),'utf-8')
print('Wrote Tour 09-16 overlays; image verification pending')
