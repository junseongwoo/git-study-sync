import json
from pathlib import Path

R=Path(__file__).resolve().parent
def f(text,p,section,evidence,source='B'):
    return dict(text=text,refs=[dict(source=source,section=section,pages=p if isinstance(p,list) else [p])],evidence=evidence)
def code(label,text,p,section,evidence):
    return dict(label=label,code=text,refs=[dict(source='B',section=section,pages=[p])],evidence=evidence,note=None)
def unit(n,title,scope):
    return dict(unit=n,title=title,part='C++',scope=scope,learning=[],concepts=[],procedures=[],syntax=[],formulas=[],comparisons=[],terms=[],summary_basis='편집 요약',summary=[],review=[],cheat={},checked_images=[],editor_notes=[])
def save(u):
    (R/f'unit_{u["unit"]:02}.json').write_text(json.dumps(u,ensure_ascii=False,indent=2),'utf-8')
def group(u,title,items):
    u['concepts'].append(dict(title=title,items=items)); return items
def term(u,name,fact): u['terms'].append(dict(term=name,definition=fact))
def finish(u,summary,questions,cheatdefs,comparison=None,syntax=None):
    u['summary']=summary
    u['review']=[dict(question=q,answer=a) for q,a in questions]
    u['cheat']=dict(definitions=[dict(term=t,definition=a) for t,a in cheatdefs],comparison_title=comparison['title'] if comparison else '',comparison_headers=comparison['headers'] if comparison else [],comparison_rows=comparison['rows'] if comparison else [],formulas=[],syntax=syntax or [])
    save(u)

u=unit(12,'쓰레드·동기화·atomic·비동기·ThreadPool',[dict(source='B',start=724,end=830)])
a=group(u,'C++ 쓰레드와 실행',[
 f('프로세스는 운영체제에서 실행되는 프로그램의 최소 단위이다.',725,'16장 / 멀티 쓰레드 프로그램','운영체제에서실행되는프로그램의최소단위'),
 f('같은 프로세스 안의 쓰레드들은 메모리를 공유한다.',727,'16장 / 멀티 쓰레드 프로그램','같은메모리를공유하게됩니다'),
 f('thread 객체를 생성하면 인자로 받은 함수를 새로운 쓰레드에서 실행한다.',734,'16장 / C++ 에서 쓰레드 생성하기','새로운쓰레드에서실행'),
 f('쓰레드가 CPU 코어에 어떻게 할당되고 언제 컨텍스트 스위치를 할지는 운영체제가 결정한다.',734,'16장 / C++ 에서 쓰레드 생성하기','전적으로운영체제의마음'),
 f('join 은 해당 쓰레드가 실행을 종료하면 리턴한다.',735,'16장 / join','해당하는쓰레드들이실행을종료하면리턴'),
 f('쓰레드를 detach 하면 main 함수에서는 그 쓰레드가 종료될 때까지 기다리지 않는다.',738,'16장 / detach','더이상쓰레드들이종료될때까지기다리지않습니다'),
 f('thread 생성자의 첫 인자는 Callable 이며, 이어서 그 함수에 전달할 인자들을 적는다.',740,'16장 / 쓰레드에 인자 전달하기','thread 생성자의첫번째인자로함수'),
 f('this_thread::get_id 로 현재 쓰레드의 아이디를 얻을 수 있다.',740,'16장 / 쓰레드에 인자 전달하기','현재내가돌아가고있는쓰레드의아이디')])
b=group(u,'뮤텍스·조건 변수',[
 f('원문의 counter 예제는 mutex 의 lock 과 unlock 사이에서 result += 1 을 수행한다.',749,'16장 / 뮤텍스와 조건 변수','m.lock();'),
 f('lock_guard 는 생성자에서 뮤텍스를 lock 하고 소멸할 때 unlock 한다.',753,'16장 / lock_guard','생성자에서뮤텍스를lock'),
 f('여러 Lock 을 획득해야 한다면 정해진 순서로 획득한다.',759,'16장 / Lock 들을 언제나 정해진 순서로 획득해라','정해진순서로획득'),
 f('생산자(producer)는 처리할 일을 받아오는 쓰레드이고, 소비자(consumer)는 받은 일을 처리하는 쓰레드이다.',759,'16장 / 생산자와 소비자 패턴','받은일을처리하는쓰레드'),
 f('조건 변수(condition_variable)는 특정 조건이 만족될 때까지 쓰레드를 기다리게 하는 데 사용한다.',765,'16장 / condition_variable','어떠어떠한조건을만족할때까지'),
 f('wait 에 전달한 조건이 거짓이면 unique_lock 을 unlock 한 뒤 sleep 한다.',768,'16장 / condition_variable','lk 를unlock 한뒤에'),
 f('unique_lock 은 unlock 후 다시 lock 할 수 있고, cv->wait 는 unique_lock 을 인자로 받는다.',769,'16장 / condition_variable','unlock 후에다시lock'),
 f('notify_one 은 기다리는 쓰레드 중 하나를 깨워 조건을 다시 검사하게 한다.',769,'16장 / condition_variable','쓰레드중하나를깨워서조건을다시검사'),
 f('원문의 생산자·소비자 예제는 생산자들을 join 한 뒤 notify_all 로 잠든 소비자들을 모두 깨운다.',769,'16장 / condition_variable','나머지자고있는쓰레드들을모두깨운다')])
c=group(u,'원자성·메모리 순서',[
 f('원자적 연산은 중간에 다른 쓰레드가 끼어들 여지가 없으며, 연산을 했거나 하지 않았거나만 존재한다.',[779,780],'16장 / 원자성(atomicity)','이연산을했다혹은안했다'),
 f('atomic 의 템플릿 인자로 원자적으로 만들고 싶은 타입을 전달한다.',781,'16장 / 원자성(atomicity)','원자적으로만들고싶은타입'),
 f('memory_order_relaxed 는 서로 다른 변수의 메모리 연산을 재배치할 수 있다.',784,'16장 / memory_order_relaxed','서로다른변수의relaxed 메모리'),
 f('memory_order_release 는 이전 메모리 명령이 뒤로 재배치되는 것을 금지하고, memory_order_acquire 는 뒤의 메모리 명령이 앞으로 재배치되는 것을 금지한다.',788,'16장 / release 와 acquire','해당명령뒤에오는모든메모리명'),
 f('memory_order_seq_cst 를 사용하는 메모리 연산들은 모든 쓰레드에서 동일한 연산 순서로 관찰되며, atomic 의 기본 memory_order 이다.',792,'16장 / memory_order_seq_cst','모든쓰레드에서동일한연산순서')])
d=group(u,'비동기 연산 도구',[
 f('프로그램 실행이 여러 갈래로 갈라져 동시에 진행되는 것을 비동기적(asynchronous) 실행이라고 부른다.',798,'16장 / 비동기 연산을 위한 도구들','비동기적(asynchronous) 실행'),
 f('promise 가 future 에 값을 전달하기 전까지 wait 가 기다리며, get 으로 전달된 객체를 얻는다.',800,'16장 / std::promise 와 std::future','promise 가future 에값을전달하기전까지'),
 f('future 의 get 은 안의 데이터를 이동하므로 두 번 호출하면 안 된다.',800,'16장 / std::promise 와 std::future','get 을두번호출'),
 f('promise 의 set_exception 으로 전달된 예외는 future 의 get 을 호출할 때 던져진다.',802,'16장 / 예외 전달','get 함수를호출하였을때'),
 f('wait_for 은 정해진 시간 동안 기다리며, future_status 는 ready, timeout, deferred 의 세 상태를 갖는다.',[802,804],'16장 / wait_for','future_status 는총3 가지상태'),
 f('여러 쓰레드에서 future 를 get 해야 하는 경우 shared_future 를 사용한다.',804,'16장 / shared_future','여러개의다른쓰레드에서future'),
 f('packaged_task 는 전달받은 함수를 실행하여 리턴값을 promise 에 설정하고, get_future 로 대응하는 future 를 얻는다.',806,'16장 / packaged_task','그함수의리턴값을promise 에설정'),
 f('std::async 는 함수를 비동기적으로 실행하고 그 결과값을 future 에 전달한다.',807,'16장 / std::async','그결과값을future 에전달')])
e=group(u,'ThreadPool 만들기',[
 f('쓰레드풀 사용자는 쓰레드들을 생성해 두고 수행할 일을 쓰레드풀에 추가한다.',811,'16장 / ThreadPool','그냥쓰레드풀에추가'),
 f('원문의 jobs_ 는 std::queue<std::function<void()>> 이며, 가장 오래전에 추가된 작업을 먼저 얻기 위해 큐를 사용한다.',813,'16장 / ThreadPool 만들기','std::queue<std::function<void()>> jobs_;'),
 f('cv_job_q_ 와 m_job_q_ 는 생산자·소비자 패턴을 구현하고, stop_all 은 Worker 쓰레드의 종료 조건을 나타낸다.',813,'16장 / ThreadPool 만들기','생산자-소비자패턴을구현'),
 f('WorkerThread 는 작업이 생기거나 stop_all 이 설정될 때까지 기다리고, stop_all 이 참이며 큐가 비면 종료한다.',814,'16장 / ThreadPool 첫번째 버전','stop_all && this->jobs_.empty()'),
 f('EnqueueJob 은 큐에 작업을 넣은 뒤 notify_one 으로 쓰레드 하나를 깨운다.',815,'16장 / ThreadPool 첫번째 버전','jobs_.push(std::move(job));'),
 f('원문의 확장 버전은 packaged_task 를 shared_ptr 에 보관하고 람다에 복사본을 전달해 작업 실행 시점까지 객체를 유지한다.',823,'16장 / ThreadPool 확장','람다함수에'),
 f('EnqueueJob 의 반환형에는 std::result_of 로 구한 함수의 리턴 타입을 가지는 future 를 사용한다.',819,'16장 / ThreadPool 확장','함수F 의리턴값은std::result_of')])
u['learning']=[a[2],e[0]]
u['procedures']=[dict(title='조건 변수를 쓰는 원문 생산자·소비자 처리 순서',steps=[b[5],b[7],b[8]]),dict(title='원문 WorkerThread 의 처리 순서',steps=[e[3],f('큐 맨 앞의 job 을 꺼내고 pop 한 뒤 lock 을 unlock 한다.',814,'16장 / ThreadPool 첫번째 버전','jobs_.pop();'),f('꺼낸 job 을 실행하고 while 루프에서 다음 작업을 기다린다.',814,'16장 / ThreadPool 첫번째 버전','job();')])]
u['syntax']=[code('lock_guard 를 사용하는 원문 worker 발췌','void worker(int& result, std::mutex& m) {\n  for (int i = 0; i < 10000; i++) {\n    std::lock_guard<std::mutex> lock(m);\n    result += 1;\n  }\n}',752,'16장 / lock_guard','std::lock_guard<std::mutex> lock(m);')]
comp=dict(title='원문의 연산별 허용 memory order',headers=['연산','허용 memory order'],rows=[[f('쓰기(store)',794,'16장 / memory order 표','쓰기(store)'),f('memory_order_relaxed, memory_order_release, memory_order_seq_cst',794,'16장 / memory order 표','memory_order_release')],[f('읽기(load)',794,'16장 / memory order 표','읽기(load)'),f('memory_order_relaxed, memory_order_consume, memory_order_acquire, memory_order_seq_cst',794,'16장 / memory order 표','memory_order_consume')],[f('읽고-수정하고-쓰기',794,'16장 / memory order 표','read - modify - write'),f('memory_order_relaxed, memory_order_consume, memory_order_acquire, memory_order_release, memory_order_acq_rel, memory_order_seq_cst',794,'16장 / memory order 표','memory_order_acq_rel')]])
u['comparisons']=[comp]
for name,fact in [('프로세스',a[0]),('join',a[4]),('lock_guard',b[1]),('condition_variable',b[4]),('원자적 연산',c[0]),('promise·future',d[1]),('packaged_task',d[6]),('ThreadPool',e[0])]: term(u,name,fact)
u['checked_images']=[dict(source='B',pages=[732,752,794,814])]
finish(u,[a[1],b[1],c[4],d[7]],[('join 은 언제 리턴하는가?',a[4]),('lock_guard 는 언제 lock/unlock 하는가?',b[1]),('future::get 을 두 번 호출하면 안 되는 이유는?',d[2]),('WorkerThread 는 어떤 조건에서 종료하는가?',e[3])],[('쓰레드',a[1]),('lock_guard',b[1]),('future::get',d[2])],dict(title='비동기 도구',headers=['도구','원문 기능'],rows=[[f('shared_future',804,'16장 / shared_future','shared_future'),d[5]],[f('packaged_task',806,'16장 / packaged_task','packaged_task'),d[6]],[f('std::async',807,'16장 / std::async','std::async'),d[7]]]))

u=unit(13,'유니폼 초기화·constexpr·decltype',[dict(source='B',start=831,end=870)])
a=group(u,'유니폼 초기화·initializer_list',[
 f('A a(); 는 객체 a 를 만드는 대신, A 를 리턴하고 인자를 받지 않는 함수 a 로 해석된다.',831,'17장 / C++ 유니폼 초기화','인자를받지않는함수'),
 f('유니폼 초기화는 {} 를 이용한 생성자 호출이며, 인자 없는 생성자가 함수의 정의로 오해되는 일을 막는다.',841,'17장 / 뭘 배웠지?','유니폼초기화({} 를이용한생성자호출)'),
 f('중괄호 초기화는 데이터 손실이 있는 Narrowing 변환을 불허하며, 원문의 A b{3.5}; 는 double 에서 int 로 변환할 수 없어 오류가 난다.',834,'17장 / 유니폼 초기화','데이터손실이있는(Narrowing) 변환'),
 f('함수의 리턴 시 {} 를 사용하면 생성하는 객체의 타입을 다시 명시하지 않아도 된다.',834,'17장 / 유니폼 초기화','객체의타입을다시명시하지'),
 f('map 의 초기화 리스트는 pair<Key, Value> 원소를 받으며, pair 의 첫 원소는 키이고 두 번째 원소는 값이다.',837,'17장 / initializer_list','pair 의첫번째원소로키'),
 f('{} 로 객체를 생성할 때 initializer_list 를 받는 생성자가 있으면 오버로딩에서 최우선으로 고려한다.',837,'17장 / initializer_list 사용시 주의할 점','최우선으로'),
 f('원문에서 vector v{10}; 은 10 을 보관한 원소 한 개를 만들고, vector v(10); 은 count 생성자를 호출한다.',[837,838],'17장 / initializer_list 사용시 주의할 점','10 을보관하고있는벡터'),
 f('C++ 17 기준 auto x = {arg1, arg2...} 는 인자들이 같은 타입이면 std::initializer_list<T> 로 추론된다.',840,'17장 / initializer_list 와 auto','모두같은타입이라면'),
 f('C++ 17 기준 auto x {arg1, arg2, ...} 는 인자 한 개이면 그 타입으로 추론하고 여러 개이면 오류가 난다.',840,'17장 / initializer_list 와 auto','인자가단1 개라면'),
 f('auto list = {"a", "b", "cc"}; 의 타입은 initializer_list<const char*> 이다.',841,'17장 / initializer_list 와 auto','initializer_list\n<const char*>')])
b=group(u,'컴파일 타임 상수 constexpr',[
 f('constexpr 은 식이 상수식이라고 명시하는 키워드이며, 객체 정의에 붙이면 그 객체를 상수식에 사용할 수 있다.',843,'18장 / constexpr','어떠한식이상수식이라고명시'),
 f('const 로 정의된 상수는 컴파일 타임에 값을 알 필요가 없지만, constexpr 변수의 초기화에는 다른 상수식이 와야 한다.',[843,844],'18장 / constexpr vs const','반드시오른쪽에다른상수식'),
 f('constexpr 함수는 조건이 맞을 때 반환값을 컴파일 타임 상수로 만들 수 있다.',847,'18장 / constexpr 함수','조건이맞을때'),
 f('원문의 Factorial(10) 은 컴파일 타임에 계산되어 클래스 A 의 템플릿 인자로 들어가며 출력은 3628800 이다.',847,'18장 / constexpr 함수','3628800'),
 f('원문은 C++ 14 에서 constexpr 함수의 제약이 완화되었다고 설명하며, goto·리터럴 타입이 아닌 변수·초기화되지 않은 변수 등의 제한을 열거한다.',848,'18장 / constexpr 함수','C++ 14 부터위와같은제약조건들이완화'),
 f('리터럴(Literal) 타입은 컴파일러가 컴파일 타임에 정의할 수 있는 타입이다.',850,'18장 / 리터럴 타입?','컴파일타임에정의할수있는타입'),
 f('constexpr 생성자의 인자는 리터럴 타입이어야 하며, 해당 클래스는 다른 클래스를 가상 상속받을 수 없다.',850,'18장 / constexpr 생성자','다른클래스를가상상속받을수없습니다'),
 f('if constexpr 의 조건은 bool 로 변환될 수 있는 컴파일 타임 상수식이어야 한다.',855,'18장 / if constexpr','컴파일타임상수식이어야'),
 f('if constexpr 이 참이면 else 문은 컴파일되지 않고, 거짓이면 else 부분만 컴파일된다.',855,'18장 / if constexpr','완전히무시')])
c=group(u,'decltype·값 카테고리·std::declval',[
 f('decltype 는 전달된 식의 타입으로 치환된다.',857,'19장 / decltype','식의타입으로치환'),
 f('괄호로 둘러싸이지 않은 식별자 표현식을 decltype 에 전달하면 해당 식의 타입을 얻는다.',858,'19장 / decltype','괄호로둘러쌓이지않은식별자표현식'),
 f('식별자 표현식이 아닌 경우, 식의 타입이 T 이고 값 카테고리가 xvalue 이면 T&&, lvalue 이면 T&, prvalue 이면 T 가 된다.',858,'19장 / decltype','decltype 는T&&'),
 f('모든 C++ 식에는 타입과 값 카테고리(value category)가 따른다.',858,'19장 / Value Category','식의타입과값카테고리'),
 f('정체를 알 수 있는 식들을 glvalue 라고 하며, 이동시킬 수 있는 식들을 rvalue 라고 한다.',859,'19장 / Value Category','정체를알수있는모든식들을glvalue'),
 f('이름을 가진 대부분의 객체는 lvalue 이며, 우측값 레퍼런스 인자 a 도 식 a 의 값 카테고리는 lvalue 이다.',860,'19장 / lvalue','식a 의\n값카테고리는lvalue'),
 f('prvalue 는 우측값 레퍼런스와 상수 좌측값 레퍼런스의 초기화에 사용할 수 있다.',862,'19장 / prvalue','상수좌측값레퍼런스를초기화'),
 f('우측값 레퍼런스를 리턴하는 함수의 호출식은 xvalue 의 대표적인 경우이며 std::move(x) 가 예이다.',862,'19장 / xvalue','대표적으로std::move(x)'),
 f('원문에서 decltype((a)) 는 lvalue 에 대한 타입 추론이므로 int& 가 된다.',863,'19장 / decltype 의 쓰임새','int& 로추론'),
 f('원문의 auto j = i; 는 const 를 없애지만, decltype(i) 는 const 를 보존하며 배열 타입도 그대로 전달한다.',[863,864],'19장 / decltype 의 쓰임새','decltype 의경우이를그대로보존'),
 f('decltype 안의 식은 런타임에 실행되지 않는다.',865,'19장 / std::declval','런타임시에실행되는것이아닙니다'),
 f('std::declval<T>() 는 T 의 생성자를 직접 호출하지 않고 타입 연산에 객체를 나타낼 수 있으며, 런타임에서 사용하면 오류가 난다.',868,'19장 / std::declval','실제로런타임에사용하면오류')])
u['learning']=[a[1],c[0]]
u['syntax']=[code('원문 constexpr 함수 발췌','constexpr int Factorial(int n) {\n  int total = 1;\n  for (int i = 1; i <= n; i++) {\n    total *= i;\n  }\n  return total;\n}',847,'18장 / constexpr 함수','constexpr int Factorial(int n)')]
u['procedures']=[dict(title='원문의 decltype 판별 순서',steps=[c[1],c[2]]),dict(title='원문의 if constexpr 처리',steps=[b[7],b[8]])]
comp=dict(title='식별자 표현식이 아닌 식의 decltype',headers=['값 카테고리','decltype 결과 (식의 타입 T)'],rows=[[f('xvalue',858,'19장 / decltype','xvalue'),f('T&&',858,'19장 / decltype','T&&')],[f('lvalue',858,'19장 / decltype','lvalue'),f('T&',858,'19장 / decltype','T&')],[f('prvalue',858,'19장 / decltype','prvalue'),f('T',858,'19장 / decltype','T 가됩니다')]])
u['comparisons']=[comp]
for name,fact in [('유니폼 초기화',a[1]),('initializer_list',a[5]),('constexpr',b[0]),('const·constexpr',b[1]),('리터럴 타입',b[5]),('if constexpr',b[7]),('decltype',c[0]),('glvalue·rvalue',c[4]),('std::declval',c[-1])]: term(u,name,fact)
u['checked_images']=[dict(source='B',pages=[833,840,847,858])]
u['editor_notes']=['원문 19장 제목의 std::decval 표기와 본문 코드의 std::declval 표기를 구분했다. 본문 설명에는 원문 코드 표기 std::declval 을 사용했다.']
finish(u,[a[1],b[0],c[0],c[-1]],[('A a(); 는 어떻게 해석되는가?',a[0]),('const 와 constexpr 의 차이는?',b[1]),('decltype((a)) 가 int& 가 되는 이유는?',c[7]),('std::declval 을 런타임에서 사용할 수 있는가?',c[-1])],[('유니폼 초기화',a[1]),('constexpr',b[0]),('std::declval',c[-1])],comp)

u=unit(14,'type_traits·정규표현식·난수·시간·파일시스템·유틸리티',[dict(source='B',start=871,end=960)])
a=group(u,'type_traits·SFINAE·enable_if',[
 f('템플릿 메타 함수는 함수처럼 동작하는 템플릿 클래스이며 타입에 대한 연산을 수행한다.',872,'20장 / 템플릿 메타 함수','타입에대해연산'),
 f('type_traits 는 타입에 대한 여러 연산을 수행하는 메타 함수들을 제공한다.',875,'20장 / is_void','타입들에대해서여러가지'),
 f('is_void<void> 는 특수화된 템플릿으로 value 가 true 이고, 다른 타입은 false 이다.',875,'20장 / is_void','value 가false'),
 f('is_integral 은 정수 타입인지 확인하며, static_assert 는 전달한 식의 참·거짓을 컴파일 타임에 확인한다.',[875,876],'20장 / static_assert','컴파일타임에확인'),
 f('is_class 는 전달받은 타입이 클래스인지 확인하는 메타 함수이다.',877,'20장 / is_class','클래스인지아닌지확인'),
 f('SFINAE 는 Substitution Failure Is Not An Error 이며, 문법에 맞지 않는 템플릿 인자 치환 결과를 함수 오버로딩 후보에서 제외한다.',883,'20장 / SFINAE','Substitution Failure Is Not An Error'),
 f('원문은 SFINAE 에서 함수의 인자와 리턴 타입을 확인하며, 함수 내부 전체를 확인하지는 않는다고 설명한다.',883,'20장 / SFINAE','함수의인자들과리턴타입만'),
 f('enable_if 는 참으로 특수화된 버전에 type 을 정의하고, 나머지에는 type 을 정의하지 않는 방식으로 후보를 제한한다.',887,'20장 / enable_if','type 이정의되어있고')])
b=group(u,'정규표현식 <regex>',[
 f('정규표현식은 문자열에서 패턴을 찾아 규칙 확인, 검색, 치환에 사용한다.',899,'20장 / 정규표현식 라이브러리 소개','문자열에서패턴을찾는데'),
 f('regex_match 는 문자열 전체가 정규표현식의 패턴에 부합하면 true 를 리턴한다.',901,'20장 / 전체 문자열 매칭하기','문자열전체가'),
 f('부분 매칭 결과는 match[i].str() 로 접근하며, regex_match 의 첫 결과는 전체 문자열이고 그 뒤는 () 안의 문자열이다.',904,'20장 / 부분 매칭 뽑아내기','첫번째결과에전체문자'),
 f('match.suffix() 는 검색된 패턴 바로 뒤부터 원래 문자열 끝까지를 나타내므로 그 뒤에서 다시 검색할 수 있다.',906,'20장 / 원하는 패턴 검색하기','검색된패턴바로뒤부터'),
 f('regex_iterator 는 생성될 때와 ++ 될 때 regex_search 를 실행하고, 역참조하면 현재 패턴의 match_results 를 얻는다.',908,'20장 / std::regex_iterator','++ 연산자로증감될때마다regex_search'),
 f('regex_replace 는 패턴에 맞는 문자열을 다른 문자열로 치환한다.',908,'20장 / 원하는 패턴 치환하기','다른문자열로치환'),
 f('치환 문자열의 $1 은 첫 번째 캡쳐 그룹을 나타내며, 중첩된 그룹의 번호는 괄호가 열리는 순서로 정해진다.',[909,911],'20장 / 캡쳐 그룹','괄호가열리는순서대로')])
c=group(u,'<random>·<chrono>',[
 f('의사 난수(pseudo random number)는 시드(seed)를 기반으로 난수처럼 보이는 수열을 생성하는 방식이다.',915,'20장 / 난수 생성','의사난수(pseudo random number)'),
 f('원문은 random_device 로 시드값을 얻고, 그 이후의 난수열은 난수 엔진으로 생성하도록 설명한다.',917,'20장 / random_device','시드값처럼난수엔진을초기화'),
 f('std::mt19937 은 메르센 트위스터 알고리즘을 사용하는 난수 생성 엔진이다.',917,'20장 / 난수 엔진','메르센\n트위스터'),
 f('uniform_int_distribution<int> 의 생성자에 범위를 지정하고, 그 분포에 난수 엔진을 전달하여 샘플을 뽑는다.',918,'20장 / 분포','생성자에원하는범위'),
 f('정규분포 예제는 std::normal_distribution<double> dist(0, 1) 로 평균 0, 표준편차 1 을 지정한다.',918,'20장 / 정규분포','평균= */ 0'),
 f('clock 의 now() 는 해당 clock 에 맞는 time_point 객체를 리턴한다.',922,'20장 / chrono 에서 지원하는 clock 들','time_point 객체를리턴'),
 f('원문의 end - start 는 duration 객체를 얻고, count() 는 시간 차이 동안의 틱 횟수를 알려준다.',922,'20장 / duration','시간차이동안몇번의틱'),
 f('실제 시간 단위로 변환하기 위해 duration_cast 를 사용한다.',922,'20장 / duration_cast','duration_cast 를사용'),
 f('날짜 출력 예제는 system_clock::now, to_time_t, localtime, put_time 의 순서로 변환한다.',924,'20장 / 현재 시간을 날짜로','std::put_time')])
d=group(u,'<filesystem>',[
 f('fstream 은 파일 데이터의 입출력을 담당하고, filesystem 은 파일 메타데이타에 대한 접근을 돕는다.',926,'20장 / 파일시스템 라이브러리 소개','파일메타데이타'),
 f('path 는 파일과 폴더의 경로를 다루는 객체이다.',942,'20장 / 뭘 배웠지?','파일과폴더의경로'),
 f('exists, is_regular_file, is_directory 는 각각 경로의 존재, 파일 여부, 디렉토리 여부를 확인한다.',926,'20장 / 파일을 찾아보자','std::filesystem::is_regular_file'),
 f('current_path() 는 프로그램 실행 경로를 리턴하며, 상대경로는 이 경로를 기준으로 구한다.',930,'20장 / 경로','프로그램의현재실행경로'),
 f('directory_iterator 로 디렉토리 안의 파일을 살피고, recursive_directory_iterator 로 안의 모든 파일·폴더를 탐색한다.',942,'20장 / 뭘 배웠지?','recursive_directory_iterator'),
 f('create_directory 는 디렉토리를 생성하고 copy 와 remove 는 파일·폴더를 복사·삭제한다.',942,'20장 / 뭘 배웠지?','copy, remove')])
e=group(u,'optional·variant·tuple·structured binding',[
 f('std::optional 은 원하는 값을 보관할 수도, 보관하지 않을 수도 있는 클래스이다.',945,'20장 / std::optional','원하는값을보관할수도'),
 f('optional 의 has_value() 로 값의 존재를 확인하고, value() 또는 * 로 값에 접근한다.',947,'20장 / std::optional','has_value 함수'),
 f('값이 없는 optional 은 보관할 타입의 디폴트 객체를 가질 필요가 없다.',947,'20장 / std::optional','디폴트객체를가질필요가없다'),
 f('std::optional<std::reference_wrapper<A>> 로 A 객체의 레퍼런스를 보관할 수 있으며, std::ref 로 wrapper 를 만들고 get() 으로 참조한 객체를 얻는다.',950,'20장 / 레퍼런스를 가지는 std::optional','std::reference_wrapper'),
 f('std::variant 는 컴파일 타임에 정한 여러 타입 중 한 타입의 객체를 보관하는 one-of 클래스이다.',951,'20장 / std::variant','one-of'),
 f('std::monostate 를 사용해 variant 가 아무것도 들고 있지 않은 상태를 표현할 수 있다.',954,'20장 / std::monostate','아무것도들고있지않은상태'),
 f('std::tuple 은 서로 다른 타입의 객체들을 묶으며, make_tuple 로 만들고 std::get 으로 원소에 접근한다.',[955,956],'20장 / std::tuple','std::make_tuple'),
 f('structured binding 은 auto [age, name, is_male] = student; 처럼 tuple 의 원소들을 받으며, 모든 원소를 받아야 한다.',958,'20장 / Structured binding','모든원소들을반드시받아야'),
 f('structured binding 에서 auto& 를 사용하면 복사 대신 레퍼런스를 취할 수 있으며, 구조체나 pair 에도 사용할 수 있다.',[958,959],'20장 / Structured binding','그냥레퍼런스만')])
u['learning']=[a[1],d[0]]
u['procedures']=[dict(title='원문의 난수 생성 순서',steps=[c[1],c[2],c[3]]),dict(title='원문의 현재 시간을 날짜로 변환하는 순서',steps=[f('system_clock::now() 로 현재 time_point 를 얻는다.',924,'20장 / 현재 시간을 날짜로','system_clock::now()'),f('system_clock::to_time_t 로 time_t 로 변환한다.',924,'20장 / 현재 시간을 날짜로','to_time_t(now)'),f('localtime 으로 tm 객체를 얻고 put_time 으로 출력 형식을 만든다.',924,'20장 / 현재 시간을 날짜로','std::localtime(&t)')])]
u['syntax']=[code('원문 정규분포 초기화 발췌','std::random_device rd;\nstd::mt19937 gen(rd());\nstd::normal_distribution<double> dist(/* 평균= */ 0, /* 표준편차= */ 1);',918,'20장 / 정규분포','std::normal_distribution<double> dist')]
comp=dict(title='정규표현식 함수 비교',headers=['함수','원문 기능'],rows=[[f('regex_match',901,'20장 / 전체 문자열 매칭하기','regex_match'),b[1]],[f('regex_iterator',908,'20장 / std::regex_iterator','regex_iterator'),b[4]],[f('regex_replace',908,'20장 / 원하는 패턴 치환하기','regex_replace'),b[5]]])
u['comparisons']=[comp]
for name,fact in [('템플릿 메타 함수',a[0]),('SFINAE',a[5]),('정규표현식',b[0]),('시드·의사 난수',c[0]),('path',d[1]),('std::optional',e[0]),('std::variant',e[4]),('std::tuple',e[6])]: term(u,name,fact)
u['checked_images']=[dict(source='B',pages=[900,918])]
finish(u,[a[1],b[0],d[0],e[6]],[('SFINAE 는 치환 오류를 어떻게 처리하는가?',a[5]),('regex_match 의 매칭 범위는?',b[1]),('filesystem 과 fstream 은 무엇을 담당하는가?',d[0]),('structured binding 은 원소 일부만 받을 수 있는가?',e[7])],[('SFINAE',a[5]),('optional',e[0]),('variant',e[4])],dict(title='값의 묶음',headers=['클래스','원문 기능'],rows=[[f('optional',945,'20장 / std::optional','std::optional'),e[0]],[f('variant',951,'20장 / std::variant','std::variant'),e[4]],[f('tuple',955,'20장 / std::tuple','std::tuple'),e[6]]]))

u=unit(15,'Visual Studio 디버깅·Make',[dict(source='L02D',start=1,end=13),dict(source='B',start=961,end=983)])
def ld(text,p,section,evidence): return f(text,p,section,evidence,'L02D')
a=group(u,'Visual Studio 디버깅',[
 ld('디버깅은 버그(오류)를 제거하는 것이다.',3,'What is debugging?','버그(=오류)를제거'),
 ld('중단점은 임의의 위치에서 프로그램을 정지시키는 기능이다.',5,'Debugging Tool 1 - Break point','임의의위치에서프로그램을정지'),
 ld('중단할 위치의 왼쪽 끝 클릭 또는 F9 으로 중단점을 만들고, F5 로 빌드 후 디버깅을 실행한다.',5,'Debugging Tool 1 - Break point','F9을통해중단점생성'),
 ld('노란 화살표는 현재 중단된 위치를 표시하며, 그 명령문은 아직 실행되지 않은 상태이다.',5,'Debugging Tool 1 - Break point','해당명령문은아직실행되지않은상태'),
 ld('F10 은 명령문을 실행하고 다음 줄로 진행하는 step over 이고, F11 은 호출되는 추가 코드로 들어가는 step into 이다.',6,'Debugging Tool 1 - Break point','step over'),
 ld('F5 는 다음 중단점까지 진행하고 Shift+F11 은 상위 stack 으로 나가는 step out 이다.',6,'Debugging Tool 1 - Break point','step out'),
 ld('변수 위에 마우스를 올리거나 하단 창에서 값을 확인하며, 방금 명령줄로 값이 변한 변수는 빨간색으로 표시된다.',7,'Debugging Tool 1 - Break point','값이변한변수가빨간색'),
 ld('메모리 윈도우는 변수가 메모리에 저장된 모습을 살피며, 주소 부분에 &변수이름 을 입력한다.',[8,9],'Debugging Tool 2 - Memory Window','주소부분에'),
 ld('디버깅에서 의도한 명령 실행 순서와 메모리 데이터가 맞는지 확인한다.',10,'How to debugging?','내가생각하는순서대로'),
 ld('Conditional & Action breakpoint 는 특정 조건에서 중단점을 활성화할 수 있고 재컴파일이 필요 없다.',12,'Conditional & Action breakpoint','재컴파일이필요없음'),
 ld('디스어셈블리 창은 변환된 어셈블리 코드를, 레지스터 창은 현재 레지스터에 저장된 값을 보여준다.',13,'Disassembly & Register','레지스터에저장된값')])
b=group(u,'컴파일·링킹·Makefile',[
 f('컴파일은 소스코드를 컴퓨터가 이해할 어셈블리어로 변환하는 과정이다.',965,'22장 / 컴파일(Compile)','어셈블리어로변환'),
 f('링킹은 서로 다른 파일에 흩어진 함수나 클래스들을 묶어 연결하는 과정이다.',967,'22장 / 링킹(Linking)','한데묶어서링크'),
 f('make 는 주어진 쉘 명령어를 조건에 맞게 실행하며, 조건을 담은 파일을 Makefile 이라고 한다.',969,'22장 / make','조건에맞게실행'),
 f('Makefile 은 target, recipe, prerequisites 의 세 요소로 구성된다.',969,'22장 / make','3 가지요소'),
 f('target 은 make 할 대상으로 전달하는 이름이며, recipe 는 그 타겟을 만들 때 실행할 명령어의 나열이다.',969,'22장 / target·recipes','명령어들의나열'),
 f('recipe 의 명령어는 반드시 탭으로 한 번 들여쓴다.',969,'22장 / 실행할 명령어(recipes)','반드시탭한번'),
 f('prerequisites 는 타겟에 사용할 파일의 목록이며 의존 파일(dependency)이라고도 한다.',969,'22장 / 필요조건들(prerequisites)','의존파일(dependency)'),
 f('타겟이 의존 파일들의 수정 시점보다 나중에 수정되었다면 그 타겟의 명령어를 실행하지 않는다.',969,'22장 / 필요조건들(prerequisites)','명령어를실행하\n지않습니다')])
c=group(u,'Makefile 변수·패턴·의존 목록',[
 f('변수는 $(CC) 와 같이 $() 안에 이름을 써서 사용하며, 정의하지 않은 변수는 빈 문자열로 치환된다.',[971,972],'22장 / 변수','빈문자열로치환'),
 f('원문의 = 는 참조 변수가 나중에 정의될 때까지 결정을 미루고, := 는 정의하는 시점의 값만 확인한다.',972,'22장 / 변수를 정의하는 두 가지 방법','해당시점에의변수의값만'),
 f('.PHONY: clean 으로 등록하면 clean 파일의 존재와 관계없이 타겟의 명령을 실행한다.',974,'22장 / PHONY','clean 파일의유무와상관없이'),
 f('%.o: %.cc %.h 패턴은 대응하는 파일의 규칙을 나타내며, 패턴은 target 과 prerequisite 부분에 사용한다.',975,'22장 / 패턴 사용하기','패턴은타겟과prerequisite 부분에만'),
 f('$@ 는 타겟 이름, $< 는 첫 의존 파일, $^ 는 의존 파일 목록 전체에 대응한다.',976,'22장 / 자동 변수','$@ : 타겟이름'),
 f('$? 는 타겟보다 최신인 의존 파일이며, $+ 는 중복된 파일 이름도 포함한 의존 파일 목록이다.',976,'22장 / 자동 변수','중복된파일이름들까지'),
 f('-MD 옵션으로 컴파일하면 의존 파일 목록을 담은 .d 파일이 생성된다.',[976,977],'22장 / 자동으로 prerequisite 만들기','-MD 옵션'),
 f('include main.d 는 해당 파일 내용을 포함하고, -include 는 포함할 파일이 없어도 make 메시지를 출력하지 않는다.',[977,978],'22장 / 자동으로 prerequisite 만들기','파일이\n존재하지않아도'),
 f('patsubst 는 $(patsubst 패턴,치환후형태,변수) 꼴로 패턴을 치환한다.',981,'22장 / 최종 정리','patsubst 패턴,치환후형태,변수'),
 f('원문의 분리된 헤더 파일 경로 예제는 컴파일러 옵션에 -Iinclude/ 를 추가한다.',983,'22장 / 헤더 파일들을 따로 뽑는 경우','-Iinclude/'),
 f('원문은 make 의 -j 뒤에 사용할 쓰레드 수를 적고 make -j8 을 예로 든다.',983,'22장 / 멀티코어를 활용해서 Make 속도를 올리자','make -j8')])
u['learning']=[a[1],b[2]]
u['procedures']=[dict(title='강의 자료의 디버깅 진행 순서',steps=[a[2],a[4],a[6],a[8]]),dict(title='원문 make main 의 최초 빌드 순서',steps=[f('Makefile 에서 main 타겟을 찾고 의존 파일 foo.o, bar.o, main.o 의 타겟을 찾는다.',970,'22장 / Makefile 처리 순서','타겟이main'),f('foo.o 가 없으므로 컴파일 명령을 실행하고, bar.o 와 main.o 도 컴파일한다.',[970,971],'22장 / Makefile 처리 순서','마찬가지로bar.o, main.o 도컴파일'),f('마지막으로 g++ foo.o bar.o main.o -o main 을 실행한다.',971,'22장 / Makefile 처리 순서','g++ foo.o bar.o main.o -o main')])]
u['syntax']=[code('원문 Makefile 일부 발췌','foo.o : foo.h foo.cc\n\tg++ -c foo.cc\n\nbar.o : bar.h bar.cc\n\tg++ -c bar.cc',970,'22장 / Makefile','foo.o : foo.h foo.cc')]
u['syntax'][0]['note']=f('원문 주의사항에 따라 recipe 앞의 들여쓰기는 탭이다.',970,'22장 / 주의사항','탭으로바꾸어서')
comp=dict(title='강의의 디버깅 진행 키',headers=['키','동작'],rows=[[ld('F10',6,'Break point','F10'),ld('step over: 해당 명령문 실행 후 다음 명령줄로 진행',6,'Break point','다음명령줄로진행')],[ld('F11',6,'Break point','F11'),ld('step into: 명령문에서 호출하는 추가 코드로 들어감',6,'Break point','추가코드')],[ld('Shift+F11',6,'Break point','Shift+F11'),ld('step out: 상위 stack 으로 나가기',6,'Break point','상위stack으로나가기')]])
u['comparisons']=[comp]
for name,fact in [('디버깅',a[0]),('중단점',a[1]),('메모리 윈도우',a[7]),('컴파일',b[0]),('링킹',b[1]),('make',b[2]),('prerequisites',b[6]),('PHONY',c[2])]: term(u,name,fact)
u['checked_images']=[dict(source='B',pages=[970,976]),dict(source='L02D',pages=[5,6,10,12,13])]
u['editor_notes']=['B 21장은 회고·외부 학습 안내이므로 추가 설명을 끌어오지 않았다. 디버깅의 환경과 단축키는 첨부 강의 자료의 설명이다.']
finish(u,[a[8],b[2],b[5],c[5]],[('F10 과 F11 은 어떤 차이가 있는가?',a[4]),('중단점의 노란 화살표 명령문은 실행되었는가?',a[3]),('recipe 의 들여쓰기 조건은?',b[5]),('.PHONY: clean 은 왜 등록하는가?',c[2])],[('디버깅',a[0]),('make',b[2]),('prerequisites',b[6])],comp)
print('Wrote units 12-15')
