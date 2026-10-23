from pathlib import Path
import json
R=Path(__file__).resolve().parent
OLD=R.parent/'os_notes'
OUT=R/'os/overlays'
OUT.mkdir(parents=True,exist_ok=True)
def f(text,pages,section,evidence):
 return dict(text=text,refs=[dict(source='O',section=section,pages=pages if isinstance(pages,list) else [pages])],evidence=evidence)
def formula(label,expression,fact,note=''):
 return dict(label=label,expression=expression,note=note,refs=fact['refs'],evidence=fact['evidence'])
def term(name,fact):return dict(term=name,definition=fact)
def label(text,ref):return dict(text=text,refs=ref['refs'],evidence=ref['evidence'])
def new(n):
 old=json.loads((OLD/f'chapters/{n:02}.json').read_text('utf-8-sig'))
 return dict(chapter=n,title=old['title'],source_code='O',learning=[],terms=[],summary_basis='',summary=[],review=[],cheat=dict(definitions=[],comparison_title='',comparison_headers=[],comparison_rows=[],formulas=[]),checked_images=[],editor_notes=[],corrections=[])
def save(d):
 # This inventory lists only pages actually viewed as source images by this author.
 ps=set()
 def walk(x):
  if isinstance(x,dict):
   if 'refs' in x:
    for ref in x['refs']:ps.update(ref['pages'])
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(d);d['checked_images']=sorted(ps)
 (OUT/f'{d["chapter"]:02}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf-8')

d=new(1);sec='1.12 요약'
os=f('운영체제는 컴퓨터 하드웨어를 관리하고 응용 프로그램 실행 환경을 제공하는 소프트웨어이다.',60,sec,'컴퓨터 하드웨어를 관리하고 응용 프로그램 실행 환경을 제공')
intr=f('인터럽트는 하드웨어가 운영체제와 상호 작용하는 주요 방법이며 인터럽트 핸들러에 의해 관리된다.',60,sec,'인터럽트 핸들러에 의해 관리된다')
mem=f('메인 메모리는 프로세서가 직접 액세스할 수 있는 유일한 대용량 저장장소이다.',60,sec,'직접 액세스 할 수 있는 유일한 대용량 저장장소')
nvm=f('비휘발성 저장장치는 메인 메모리의 확장이며 대량의 데이터를 영구적으로 보유할 수 있다.',60,sec,'대량의 데이터를 영구적으로 보유')
multi=f('다중 프로그래밍은 여러 작업을 동시에 메모리에 적재하여 CPU가 실행할 작업이 있게 한다.',60,sec,'여러 작업을 동시에 메모리에 적재')
task=f('다중 태스킹은 CPU 스케줄링 알고리즘이 프로세스 간에 빠르게 전환하여 빠른 응답 시간을 제공하는 다중 프로그래밍의 확장이다.',60,sec,'빠른 응답 시간을 제공하는 다중 프로그래밍의 확장')
priv=f('특권을 가진 명령어는 커널 모드에서만 실행될 수 있다.',60,sec,'커널 모드에서만 실행')
virt=f('가상화에는 컴퓨터 하드웨어를 여러 가지 실행 환경으로 추상화하는 작업이 포함된다.',61,sec,'여러 가지 실행 환경으로 추상화')
store=f('저장장치 시스템은 속도와 비용에 따른 계층 구조로 구성되며, 계층이 내려갈수록 일반적으로 비트당 비용은 감소하고 액세스 시간은 증가한다.',60,sec,'비트당 비용은 감소하고 반면 액세스 시간은 증가')
d['learning']=[os,intr,virt];d['terms']=[term(n,v) for n,v in [('운영체제',os),('인터럽트',intr),('메인 메모리',mem),('비휘발성 저장장치',nvm),('다중 프로그래밍',multi),('다중 태스킹',task),('특권 명령어',priv),('가상화',virt)]]
d['summary_basis']='1.12 요약';d['summary']=[os,intr,store,task,priv]
d['review']=[dict(question=q,answer=a) for q,a in [('운영체제는 무엇을 관리하고 어떤 환경을 제공하는가?',os),('하드웨어가 운영체제와 상호 작용하는 주요 방법과 이를 관리하는 것은?',intr),('특권을 가진 명령어는 어느 모드에서 실행되는가?',priv),('가상화에서 컴퓨터 하드웨어는 무엇으로 추상화되는가?',virt)]]
d['cheat']=dict(definitions=[term('운영체제',os),term('인터럽트',intr),term('가상화',virt)],comparison_title='다중 프로그래밍과 다중 태스킹',comparison_headers=['구분','원문 설명'],comparison_rows=[[label('다중 프로그래밍',multi),multi],[label('다중 태스킹',task),task]],formulas=[]);save(d)

d=new(2);d['summary_basis']='본문 미제공';d['editor_notes']=['제2장 운영체제 구조는 목차의 제목·절 구조만 제공되며 본문은 첨부 원문에서 확인 불가이다. 학습 목표·용어·요약·문제·치트시트 내용을 임의로 보충하지 않았다.'];save(d)

d=new(3);sec='3.9 요약'
proc=f('프로세스는 실행 중인 프로그램이며 현재 활동 상태는 프로그램 카운터와 다른 레지스터로 나타낸다.',116,sec,'프로세스는 실행 중인 프로그램')
pcb=f('프로세스 제어 블록(PCB)은 운영체제의 프로세스를 나타내는 커널 데이터 구조이다.',117,sec,'프로세스를 나타내는 커널 데이터 구조')
ctx=f('문맥 교환은 한 프로세스 실행에서 다른 프로세스 실행으로 전환할 때 수행된다.',117,sec,'다른 프로세스 실행으로 전환할 때 문맥 교환')
sh=f('공유 메모리를 사용하는 프로세스 간 통신에서는 두 개 이상의 프로세스가 동일한 메모리 영역을 공유한다.',117,sec,'동일한 메모리 영역을 공유')
msg=f('메시지 전달에서는 두 프로세스가 서로 메시지를 교환하여 통신한다.',117,sec,'메시지를 교환하여 통신')
pipe=f('파이프는 두 프로세스가 통신할 수 있는 통로를 제공하며 일반 파이프와 지명 파이프의 두 형태가 있다.',117,sec,'통신할 수 있는 통로를 제공')
sock=f('소켓을 사용하면 다른 시스템의 두 프로세스가 네트워크를 통해 통신할 수 있다.',117,sec,'네트워크를 통해 통신')
rpc=f('원격 프로시저 호출(RPC)은 다른 컴퓨터의 프로세스에서 함수를 호출할 수 있는 방식으로 함수 호출 개념을 추상화한다.',117,sec,'함수(프로시저) 호출 개념을 추상화')
create=f('fork()와 CreateProcess() 시스템 콜은 각각 UNIX와 Windows에서 프로세스를 생성하는 데 사용된다.',117,sec,'fork() 및 CreateProcess()')
d['learning']=[proc,sh,rpc];d['terms']=[term(n,v) for n,v in [('프로세스',proc),('프로세스 제어 블록(PCB)',pcb),('문맥 교환',ctx),('공유 메모리',sh),('메시지 전달',msg),('파이프',pipe),('소켓',sock),('원격 프로시저 호출(RPC)',rpc)]]
d['summary_basis']='3.9 요약';d['summary']=[proc,pcb,create,sh,rpc]
d['review']=[dict(question=q,answer=a) for q,a in [('프로세스의 현재 활동 상태는 무엇으로 나타내는가?',proc),('프로세스 제어 블록은 어떤 데이터 구조인가?',pcb),('공유 메모리 모델에서 프로세스들은 무엇을 공유하는가?',sh),('RPC는 어떤 호출 개념을 추상화하는가?',rpc)]]
d['cheat']=dict(definitions=[term('프로세스',proc),term('PCB',pcb),term('문맥 교환',ctx)],comparison_title='프로세스 간 통신',comparison_headers=['구분','원문 설명'],comparison_rows=[[label('공유 메모리',sh),sh],[label('메시지 전달',msg),msg]],formulas=[]);save(d)

d=new(4)
thread=f('스레드는 CPU 이용의 기본 단위이며 스레드 ID, 프로그램 카운터, 레지스터 집합과 스택으로 구성된다.',122,'4.1 개요','CPU 이용의 기본 단위')
conc=f('병행 시스템은 모든 작업이 진행되게 하여 둘 이상의 작업을 지원한다.',125,'4.2 다중 코어 프로그래밍','모든 작업이 진행되게')
para=f('병렬 시스템은 둘 이상의 작업을 동시에 수행할 수 있다.',125,'4.2 다중 코어 프로그래밍','둘 이상의 작업을 동시에 수행')
user=f('사용자 스레드는 커널 위에서 지원되며 커널의 지원 없이 관리된다.',128,'4.3 다중 스레드 모델','커널의 지원 없이 관리')
kern=f('커널 스레드는 운영체제에 의해 직접 지원되고 관리된다.',128,'4.3 다중 스레드 모델','직접 지원되고 관리')
data=f('데이터 병렬 처리는 동일한 데이터의 부분 집합을 다른 컴퓨팅 코어에 분산시키고 각 코어에서 동일한 연산을 수행한다.',162,'4.8 요약','각 코어에서 동일한 연산')
task=f('작업 병렬 처리는 여러 코어에 작업을 분산시키며 각 작업은 고유한 연산을 수행한다.',162,'4.8 요약','각 작업은 고유한 연산')
impl=f('암묵적 스레딩은 작업을 식별하고 언어 또는 API 프레임워크가 스레드를 만들고 관리할 수 있게 한다.',162,'4.8 요약','언어 또는 API 프레임워크가 스레드를 만들고 관리')
share=f('동일한 프로세스에 속한 스레드는 코드와 데이터를 포함하여 많은 프로세스 자원을 공유한다.',161,'4.8 요약','많은 프로세스 자원을 공유')
benefit=f('다중 스레드 응용 프로그램의 네 가지 주요 이점은 응답성, 자원 공유, 경제성 및 확장성이다.',161,'4.8 요약','응답성, (2) 자원 공유, (3) 경제성')
mapping=f('사용자 수준 스레드는 궁극적으로 CPU에서 실행되도록 커널 스레드에 매핑되어야 한다.',162,'4.8 요약','커널 스레드에 매핑되어야')
am=f('Amdahl의 법칙은 순차 실행 구성요소와 병렬 실행 구성요소로 이루어진 응용에 계산 코어를 더할 때 얻을 수 있는 잠재적 성능 이득을 나타낸다.',126,'4.2 Amdahl의 법칙','잠재적인 성능 이득')
d['learning']=[thread,conc,impl];d['terms']=[term(n,v) for n,v in [('스레드',thread),('병행성',conc),('병렬성',para),('사용자 스레드',user),('커널 스레드',kern),('데이터 병렬 처리',data),('작업 병렬 처리',task),('암묵적 스레딩',impl)]]
d['summary_basis']='4.8 요약';d['summary']=[share,benefit,mapping,data,impl]
d['review']=[dict(question=q,answer=a) for q,a in [('스레드를 구성하는 네 요소는?',thread),('병행 시스템과 달리 병렬 시스템이 할 수 있는 것은?',para),('데이터 병렬 처리는 각 코어에서 어떤 연산을 수행하는가?',data),('암묵적 스레딩에서는 무엇이 스레드를 만들고 관리하는가?',impl)]]
d['cheat']=dict(definitions=[term('스레드',thread),term('병행성',conc),term('병렬성',para)],comparison_title='병렬 실행의 두 유형',comparison_headers=['구분','원문 설명'],comparison_rows=[[label('데이터 병렬 처리',data),data],[label('작업 병렬 처리',task),task]],formulas=[formula('Amdahl의 법칙','speedup ≤ 1 / (S + (1 − S) / N)',am,'S는 반드시 순차 실행되는 부분, N은 처리 코어 수이다.')]);save(d)

d=new(5);sec='5.9 요약'
cpu=f('CPU 스케줄링은 준비 큐에서 대기 프로세스를 선택하고 CPU를 할당하는 작업이다.',220,sec,'준비 큐에서 대기 프로세스를 선택')
fcfs=f('선입 선처리(FCFS) 스케줄링은 가장 간단하지만 짧은 프로세스가 매우 긴 프로세스를 기다리게 할 수 있다.',220,sec,'짧은 프로세스가 매우 긴 프로세스를 기다리게')
sjf=f('최단 작업 우선(SJF) 스케줄링은 최적이며 평균대기 시간이 가장 작지만 다음 CPU 버스트의 길이를 예측하기 어려워 구현이 어렵다.',[220,221],sec,'다음 CPU 버스트의 길이를 예측하기 어려우므로')
rr=f('라운드 로빈(RR) 스케줄링은 CPU를 시간 할당량 동안 프로세스에 할당하며, 만료 전에 CPU를 포기하지 않으면 선점한다.',221,sec,'시간 할당량이 만료되기 전에 CPU를 포기하지 않으면')
priority=f('우선순위 스케줄링은 각 프로세스에 우선순위를 배정하고 CPU를 우선순위가 가장 높은 프로세스에 할당한다.',221,sec,'우선순위가 가장 높은 프로세스에 할당')
mlq=f('다단계 큐 스케줄링은 프로세스를 우선순위에 따라 여러 큐로 분할하고 가장 높은 큐에서 실행하며, 큐마다 다른 알고리즘을 사용할 수 있다.',221,sec,'큐마다 다른 스케줄링 알고리즘')
rm=f('Rate-monotonic 실시간 스케줄링은 선점과 정적 우선순위 정책을 사용하여 주기적 작업을 스케줄한다.',221,sec,'정적 우선순위 정책')
edf=f('EDF 스케줄링은 마감시한에 따라 우선순위를 지정하며 마감시한이 빠를수록 우선순위가 높다.',221,sec,'마감시한이 빠를수록 우선순위가 높고')
criteria=f('스케줄링 알고리즘은 CPU 이용률, 처리량, 총처리 시간, 대기 시간 및 응답 시간의 다섯 기준으로 평가할 수 있다.',220,sec,'5가지 기준')
fb=f('다단계 피드백 큐는 프로세스가 다른 큐 간에 이주할 수 있다는 점을 제외하면 다단계 큐와 유사하다.',221,sec,'다른 큐 간에 이주')
bound=f('N개 프로세스를 스케줄하는 Rate-monotonic의 최악의 경우 CPU 이용률 경계는 N(2^(1/N)−1)이다.',201,'5.6.3 Rate-Monotonic 스케줄링','최악의 경우 CPU 이용률')
d['learning']=[cpu,criteria,rm];d['terms']=[term(n,v) for n,v in [('CPU 스케줄링',cpu),('선입 선처리(FCFS)',fcfs),('최단 작업 우선(SJF)',sjf),('라운드 로빈(RR)',rr),('우선순위 스케줄링',priority),('다단계 큐',mlq),('Rate-monotonic',rm),('EDF',edf)]]
d['summary_basis']='5.9 요약';d['summary']=[cpu,criteria,rr,fb,edf]
d['review']=[dict(question=q,answer=a) for q,a in [('CPU 스케줄링은 어느 큐에서 프로세스를 선택하는가?',cpu),('스케줄링 알고리즘의 다섯 평가 기준은?',criteria),('RR에서 시간 할당량이 만료되기 전에 CPU를 포기하지 않으면 어떻게 되는가?',rr),('다단계 피드백 큐와 다단계 큐의 차이는?',fb)]]
d['cheat']=dict(definitions=[term('CPU 스케줄링',cpu),term('SJF',sjf),term('RR',rr)],comparison_title='실시간 스케줄링의 우선순위',comparison_headers=['구분','원문 설명'],comparison_rows=[[label('Rate-monotonic',rm),rm],[label('EDF',edf),edf]],formulas=[formula('Rate-monotonic의 이용률 경계','N(2^(1/N) − 1)',bound,'N은 스케줄할 프로세스 수이다. 원문의 최악의 경우 CPU 이용률 경계이다.')]);save(d)

d=new(6);sec='6.10 요약'
race=f('경쟁 조건은 프로세스가 공유 데이터에 병행하게 접근할 때 발생하며 최종 결과는 병행 접근의 특정 순서에 따라 다르다.',259,sec,'최종 결과는 병행 접근이 발생한 특정 순서에 따라 다르다')
critical=f('임계구역은 공유 데이터가 조작될 수 있으며 경쟁 조건이 발생할 수 있는 코드 영역이다.',259,sec,'경쟁 조건이 발생할 수 있는 코드 영역')
mutual=f('상호 배제는 한 프로세스가 자신의 임계구역에서 실행된다면 다른 프로세스는 자신의 임계구역에서 실행될 수 없다는 요구 조건이다.',230,'6.2 임계구역 문제','다른 프로세스들은 그들 자신의 임계구역에서 실행될 수 없다')
progress=f('임계구역에서 실행되는 프로세스가 없고 진입하려는 프로세스들이 있으면, 나머지 구역에서 실행 중이지 않은 프로세스들만 다음 진입자를 결정하며 선택은 무한정 연기될 수 없다.',230,'6.2 임계구역 문제','이 선택은 무한정 연기될 수 없다')
bounded=f('한정된 대기는 프로세스가 임계구역 진입을 요청한 후 허용될 때까지 다른 프로세스들의 임계구역 진입 허용 횟수에 한계가 있어야 한다는 요구 조건이다.',231,'6.2 임계구역 문제','진입하도록 허용되는 횟수에 한계')
mutex=f('Mutex 락은 임계구역에 들어가기 전에 락을 획득하고 나올 때 해제하도록 요구하여 상호 배제를 제공한다.',259,sec,'락을 획득하고 임계구역에서 나올 때 락을 해제')
sema=f('세마포는 정수 값을 가지며 상호 배제뿐 아니라 다양한 동기화 문제를 해결하는 데 사용될 수 있다.',259,sec,'세마포는 정수 값을 가지므로')
monitor=f('모니터는 프로세스 동기화의 높은 수준 형태를 제공하는 추상 데이터 유형이다.',259,sec,'추상 데이터 유형')
req=f('임계구역 문제의 해결책은 상호 배제, 진행 및 한정된 대기의 세 요구 사항을 충족해야 한다.',259,sec,'상호 배제, (2) 진행 및 (3) 한정된 대기')
hardware=f('임계구역 문제의 하드웨어 지원에는 메모리 장벽, compare_and_swap 같은 하드웨어 명령 및 원자적 변수가 포함된다.',259,sec,'메모리 장벽, compare_and_swap')
live=f('임계구역 문제의 해결책은 교착 상태를 포함한 라이브니스 문제를 겪을 수 있다.',259,sec,'교착 상태를 포함한 라이브니스 문제')
d['learning']=[race,critical,monitor];d['terms']=[term(n,v) for n,v in [('경쟁 조건',race),('임계구역',critical),('상호 배제',mutual),('진행',progress),('한정된 대기',bounded),('Mutex 락',mutex),('세마포',sema),('모니터',monitor)]]
d['summary_basis']='6.10 요약';d['summary']=[race,req,hardware,mutex,live]
d['review']=[dict(question=q,answer=a) for q,a in [('임계구역 문제의 해결책이 충족해야 하는 세 요구 사항은?',req),('한정된 대기는 어떤 횟수에 한계를 요구하는가?',bounded),('Mutex 락은 임계구역 진입 전과 퇴출 때 무엇을 요구하는가?',mutex),('프로세스 동기화의 높은 수준 형태를 제공하는 추상 데이터 유형은?',monitor)]]
d['cheat']=dict(definitions=[term('경쟁 조건',race),term('임계구역',critical),term('모니터',monitor)],comparison_title='동기화 도구',comparison_headers=['도구','원문 설명'],comparison_rows=[[label('Mutex 락',mutex),mutex],[label('세마포',sema),sema]],formulas=[]);save(d)

d=new(7)
buf=f('유한 버퍼 문제에서는 n개의 버퍼로 구성된 풀을 가정하며 각 버퍼는 한 항목을 저장할 수 있다.',263,'7.1.1 유한 버퍼 문제','각 버퍼는 한 항목(item)을 저장')
rw=f('Readers-Writers 문제는 writer가 쓰기 작업 동안 공유 데이터베이스에 대한 배타적 접근 권한을 갖도록 보장하는 동기화 문제이다.',264,'7.1.2 Readers-Writers 문제','배타적 접근 권한')
ph=f('식사하는 철학자들 문제의 다섯 철학자는 생각과 식사를 반복하며, 식사하려면 자신에게 가장 가까운 두 젓가락을 모두 집어야 한다.',266,'7.1.3 식사하는 철학자들 문제','가장 가까이 있는 두 개의 젓가락')
named=f('POSIX의 기명 세마포는 관련 없는 여러 프로세스가 단순히 이름을 참조하여 같은 세마포에 액세스할 수 있다.',288,'7.6 요약','관련이 없는 여러 프로세스가 단순히 이름을 참조')
unnamed=f('POSIX의 무명 세마포를 공유하려면 공유 메모리 영역에 세마포를 배치해야 한다.',288,'7.6 요약','공유 메모리 영역에 세마포를 배치')
trans=f('메모리 트랜잭션은 메모리 읽기와 쓰기 연산의 원자적인 연속적 순서이다.',285,'7.5.1 트랜잭션 메모리','원자적인 연속적 순서')
imperative=f('명령형 혹은 절차형 언어는 상태에 기반을 둔 알고리즘을 구현하는 데 사용되며 상태는 변수와 다른 자료구조를 통해 표현된다.',288,'7.5.3 함수형 프로그래밍 언어','상태는 변수와 다른 자료구조')
functional=f('함수형 언어에서는 변수가 정의되어 값을 배정받으면 그 값은 변경될 수 없어 상태가 변하지 않는다.',288,'7.5.3 함수형 프로그래밍 언어','그 값은 변경될 수 없기 때문에')
classic=f('고전적인 프로세스 동기화 문제에는 유한 버퍼, reader-writer 및 식사하는 철학자 문제가 포함된다.',288,'7.6 요약','유한 버퍼, reader-writer 및 식사하는 철학자')
windows=f('Windows는 dispatcher 객체와 event를 사용하여 프로세스 동기화 도구를 구현한다.',288,'7.6 요약','dispatcher 객체와 event')
linux=f('Linux는 경쟁 조건을 방지하기 위해 원자적 변수, 스핀락 및 mutex 락을 포함한 다양한 접근 방식을 사용한다.',288,'7.6 요약','원자적 변수, 스핀락 및 mutex 락')
posix=f('POSIX API는 mutex 락, 세마포 및 조건 변수를 제공한다.',288,'7.6 요약','mutex 락, 세마포 및 조건 변수를 제공')
alternative=f('임계구역 문제를 해결하기 위한 대안으로 트랜잭션 메모리, OpenMP 및 함수형 언어가 있다.',289,'7.6 요약','트랜잭션 메모리, OpenMP 및 함수형 언어')
init=f('유한 버퍼 문제에서 mutex는 1, empty는 n, full은 0으로 초기화된다.',263,'7.1.1 유한 버퍼 문제','semaphore mutex = 1')
d['learning']=[classic,posix,alternative];d['terms']=[term(n,v) for n,v in [('유한 버퍼',buf),('Readers-Writers 문제',rw),('식사하는 철학자들 문제',ph),('기명 세마포',named),('무명 세마포',unnamed),('메모리 트랜잭션',trans),('명령형·절차형 언어',imperative),('함수형 언어',functional)]]
d['summary_basis']='7.6 요약';d['summary']=[classic,windows,linux,posix,alternative]
d['review']=[dict(question=q,answer=a) for q,a in [('고전적인 세 가지 프로세스 동기화 문제는?',classic),('Readers-Writers 문제에서 writer가 쓰기 동안 가져야 하는 접근 권한은?',rw),('POSIX의 무명 세마포는 공유를 위해 어디에 배치해야 하는가?',unnamed),('메모리 트랜잭션은 어떤 연산 순서인가?',trans)]]
d['cheat']=dict(definitions=[term('유한 버퍼',buf),term('Readers-Writers 문제',rw),term('메모리 트랜잭션',trans)],comparison_title='POSIX 세마포의 두 형태',comparison_headers=['구분','원문 설명'],comparison_rows=[[label('기명 세마포',named),named],[label('무명 세마포',unnamed),unnamed]],formulas=[formula('유한 버퍼의 초기값','mutex = 1, empty = n, full = 0',init,'n개의 버퍼가 있으며 각 버퍼는 한 항목을 저장한다.')]);save(d)

d=new(8)
dead=f('집합의 모든 프로세스가 같은 집합의 다른 프로세스에서만 발생할 수 있는 이벤트를 기다리는 경우 그 프로세스 집합에서 교착 상태가 발생한다.',320,'8.9 요약','같은 집합의 다른 프로세스에서만 발생')
safe=f('안전 상태는 시스템이 안전 순서를 찾을 수 있어, 스레드들이 최대 요구 수를 요구하더라도 교착 상태 없이 차례로 모든 자원을 할당해 줄 수 있는 상태이다.',307,'8.6.1 안전 상태','시스템이 안전 순서(safe sequence)를 찾을 수 있다면')
unsafe=f('모든 스레드를 무사히 마칠 수 있는 순서를 찾을 수 없으면 불안전 상태이며, 불안전 상태가 반드시 교착 상태를 뜻하지는 않는다.',307,'8.6.1 안전 상태','반드시 교착 상태로 간다는 것을 뜻하는 것은 결코 아니다')
sequence=f('안전 순서에서는 각 스레드의 요청을 현재 남은 자원과 앞서 수행을 마친 스레드가 반환한 자원으로 만족시킬 수 있다.',307,'8.6.1 안전 상태','현재 남아있는 자원과 앞에서 수행을 마칠 모든 스레드')
bank=f('은행원 알고리즘은 시스템을 불안전 상태로 이끌 수 있는 자원 요청을 허가하지 않아 교착 상태를 회피한다.',320,'8.9 요약','불안전 상태로 이끌 수 있는 자원 요청을 허가하지 않는다')
prevention=f('교착 상태에 필요한 네 조건 중 하나가 발생하지 않도록 하여 교착 상태를 예방할 수 있다.',320,'8.9 요약','4가지 조건 중 하나가 발생하지 않도록')
detect=f('교착 상태 탐지 알고리즘은 실행 중인 시스템의 프로세스와 자원을 평가하여 프로세스들이 교착 상태에 있는지 결정한다.',320,'8.9 요약','프로세스 및 자원을 평가')
need=f('Need는 각 스레드가 향후 요청할 수 있는 자원 개수를 나타내는 n×m 행렬이다.',310,'8.6.3 은행원 알고리즘','향후 요청할 수 있는 자원의 개수')
conditions=f('교착 상태는 상호 배제, 점유하며 대기, 비선점 및 순환 대기의 네 조건이 모두 존재할 때만 가능하다.',320,'8.9 요약','네 가지 조건이 모두 존재할 때만')
recover=f('교착 상태 발생 후에는 순환 대기 프로세스 하나를 중단하거나 교착 프로세스에 지정된 자원을 선점하여 복구를 시도할 수 있다.',320,'8.9 요약','자원을 선점하여 교착 상태에서 복구')
needf=f('Need[i][j] = Max[i][j] − Allocation[i][j]이다.',310,'8.6.3 은행원 알고리즘','Need[i][j] = Max[i][j] − Allocation[i][j]')
d['learning']=[dead,conditions,safe];d['terms']=[term(n,v) for n,v in [('교착 상태',dead),('안전 상태',safe),('불안전 상태',unsafe),('안전 순서',sequence),('은행원 알고리즘',bank),('교착 상태 예방',prevention),('교착 상태 탐지',detect),('Need',need)]]
d['summary_basis']='8.9 요약';d['summary']=[dead,conditions,prevention,bank,recover]
d['review']=[dict(question=q,answer=a) for q,a in [('교착 상태가 가능하려면 어떤 네 조건이 함께 있어야 하는가?',conditions),('불안전 상태는 반드시 교착 상태를 뜻하는가?',unsafe),('은행원 알고리즘의 Need 행렬은 무엇을 나타내는가?',need),('교착 상태가 발생한 후 복구를 시도하는 두 방법은?',recover)]]
d['cheat']=dict(definitions=[term('교착 상태',dead),term('안전 상태',safe),term('Need',need)],comparison_title='예방과 회피',comparison_headers=['구분','원문 설명'],comparison_rows=[[label('예방',prevention),prevention],[label('회피: 은행원 알고리즘',bank),bank]],formulas=[formula('추가 요청 가능 자원','Need[i][j] = Max[i][j] − Allocation[i][j]',needf,'Max는 최대 요구, Allocation은 현재 할당 자원의 개수이다.')]);save(d)
