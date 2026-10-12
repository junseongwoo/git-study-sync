"""Original teaching content for the RC restart course."""
CH=[]

def concept(name, body, example, translation, why, judge):
    return dict(name=name,body=body,example=example,translation=translation,why=why,judge=judge)

def chapter(n,title,goals,concepts,confusions,must,summary,pitfalls,checks,expressions,reading):
    CH.append(dict(n=n,title=title,goals=goals,concepts=concepts,confusions=confusions,must=must,
        summary=summary,pitfalls=pitfalls,checks=checks,expressions=expressions,reading=reading,
        practice=[],review=[]))

chapter(1,'영어 문장의 기본 구조',
 ['주어·동사·목적어·보어를 구별한다.','수식어를 덜어 문장의 뼈대를 찾는다.','1~5형식을 TOEIC 문장 분석에 적용한다.'],[
 concept('★ 성분과 품사는 서로 다른 기준이다','주어(S)는 누구·무엇에 관한 문장인지, 동사(V)는 행동·상태, 목적어(O)는 행동의 대상이다. 보어(C)는 주어나 목적어가 누구인지 또는 어떤 상태인지 설명한다. 명사·형용사는 단어의 종류이고, 주어·보어는 문장 안의 역할이다.','The manager approved the proposal.','관리자가 제안을 승인했다.','동사 뒤 빈칸이 목적어인지 보어인지에 따라 필요한 품사가 달라진다.','① 주어와 동사를 찾는다. ② 동사 뒤가 행동 대상이면 O, 주어의 상태·정체를 설명하면 C로 본다.'),
 concept('★★ 1~5형식은 동사 뒤 구조를 보는 틀이다','1형식 S+V: 도착하다처럼 목적어가 없다. 2형식 S+V+C: 상태 보어가 있다. 3형식 S+V+O: 대상을 취한다. 4형식 S+V+간접목적어+직접목적어: 누구에게 무엇을 준다. 5형식 S+V+O+C: 목적어의 상태·행동을 설명한다. 같은 동사도 쓰임에 따라 구조가 달라진다.','The policy made travel easier.','그 정책은 출장을 더 수월하게 만들었다.','made 뒤 travel이 목적어, easier가 목적격 보어이므로 형용사를 고른다.','① 동사의 의미를 정한다. ② 뒤 명사 수와 보어 유무를 본다. ③ O와 C의 의미 관계를 확인한다.'),
 concept('★★★ 수식어를 걷어 내도 핵심은 남는다','전치사구와 관계절은 길어도 주어의 핵심어를 바꾸지 않는다. 다만 수식어에도 필수 정보가 있을 수 있으므로 뼈대를 찾은 뒤 다시 붙여 해석한다. 모든 전치사구가 언제나 생략 가능한 것은 아니다.','The files on the shared drive are ready.','공유 드라이브에 있는 파일들이 준비되었다.','on the shared drive의 drive가 아니라 files에 동사를 맞춘다.','① 주어의 핵심 명사를 표시한다. ② 전치사구를 괄호로 묶는다. ③ 남은 S+V 구조를 확인한다.')],
 [('목적어 vs 보어','She manages the team.에서 team은 대상(O). She is the manager.에서 manager는 주어의 정체(C)이다.'),('수식어 vs 핵심어','The price of the tickets에서 주어의 핵심은 price이다. tickets는 of의 목적어이다.')],
 ['S=주어 / V=동사 / O=목적어 / C=보어 / M=수식어','SVC: remain available','SVO: approve a request','SVOO: send a client an invoice','SVOC: keep the door closed'],
 ['성분은 역할, 품사는 단어의 종류이다.','문장의 핵심은 주어와 정형 동사이다.','목적어는 행동의 대상이다.','보어는 주어나 목적어의 상태·정체를 설명한다.','형식은 동사의 실제 쓰임으로 판단한다.','긴 수식어를 제거한 뒤 다시 의미를 붙인다.'],
 ['동사 뒤 모든 명사를 목적어로 본다.','전치사 뒤 명사를 주어로 착각한다.','5형식 보어를 별도 목적어로 읽는다.'],
 ['핵심 주어는 무엇인가?','동사 뒤 대상과 상태가 각각 있는가?','수식어를 빼도 뼈대가 성립하는가?'],
 ['arrive on time: 제시간에 도착하다','remain open: 열린 상태를 유지하다','approve a request: 요청을 승인하다','send an invoice: 청구서를 보내다','give staff instructions: 직원에게 지시하다','keep records accurate: 기록을 정확하게 유지하다','find the room empty: 방이 빈 것을 알다','make travel easier: 출장을 수월하게 하다','on the shared drive: 공유 드라이브에','in the main lobby: 본관 로비에'],
 ('NOTICE','The visitor desk in the main lobby opens at 8 a.m. Staff members will give each guest a temporary pass. Please keep the pass visible during your visit. The new arrangement makes registration faster.',
  ['첫 문장의 핵심 주어와 동사를 찾으세요.','둘째 문장의 두 목적어를 찾으세요.','셋째 문장의 목적어와 보어를 찾으세요.','마지막 문장이 안내하는 효과는 무엇인가요?'],
  ['S: The visitor desk / V: opens. in the main lobby는 desk를 수식한다.','give + each guest(간접목적어) + a temporary pass(직접목적어).','O: the pass / C: visible. 출입증이 잘 보이는 상태로 두라는 뜻이다.','등록 절차가 더 빨라진다는 효과이다. makes + registration(O) + faster(C).']))

chapter(2,'품사 완전 정리',
 ['일곱 품사의 핵심 기능을 복구한다.','명사·형용사·부사 자리를 구조로 판단한다.','접미사 단서와 실제 문장 역할을 함께 확인한다.'],[
 concept('★ 명사·대명사·동사','명사는 사람·사물·사건·개념을 나타내며 주어·목적어·보어가 된다. 대명사는 앞 명사나 사람을 대신하고 격에 따라 형태가 달라진다. 동사는 시제와 수를 갖추어 서술어가 되며, 조동사와 함께 동사구를 만들기도 한다.','The technician checked it carefully.','기술자가 그것을 주의 깊게 점검했다.','technician은 주어인 명사, it은 목적어인 대명사, checked는 본동사이다.','① 행동·상태를 서술하는 동사를 찾는다. ② 그 주체와 대상을 찾는다. ③ 대명사의 역할에 맞는 격을 고른다.'),
 concept('★★ 형용사·부사','형용사는 명사를 꾸미거나 보어가 된다. 부사는 주로 동사·형용사·다른 부사 또는 문장 전체를 수식한다. -ly가 부사의 단서이지만 friendly처럼 형용사도 있고 fast처럼 같은 형태가 형용사·부사로 쓰이기도 한다.','The response was remarkably quick.','그 응답은 놀랄 만큼 빨랐다.','quick은 주어의 상태를 설명하는 형용사이고 remarkably는 quick을 수식하는 부사이다.','① 빈칸이 꾸미는 대상을 찾는다. ② 명사·보어이면 형용사, 동사·형용사 수식이면 부사를 검토한다.'),
 concept('★★★ 전치사·접속사와 품사 문제의 한계','전치사는 뒤에 명사 역할의 덩어리를 취한다. 접속사는 절이나 병렬 요소를 연결한다. 같은 품사 선택지가 네 개라면 자리만으로 답을 낼 수 없으므로 의미와 결합을 읽어야 한다.','The office closed because of the storm.','폭풍 때문에 사무실이 문을 닫았다.','because of 뒤는 명사구이다. because 뒤라면 주어+동사가 있는 절이 필요하다.','① 빈칸 뒤가 명사구인지 절인지 본다. ② 선택지의 품사를 좁힌다. ③ 남은 후보의 의미를 확인한다.')],
 [('형용사 자리 vs 부사 자리','a careful review에서는 review를 꾸미므로 careful. review carefully에서는 행동을 꾸미므로 carefully.'),('접미사 vs 역할','-tion은 명사, -ive는 형용사, -ly는 부사의 흔한 단서지만 단어의 실제 쓰임을 최종 기준으로 삼는다.')],
 ['관사 + (형용사) + 명사','be/remain + 형용사 보어','부사 + 형용사 / 부사 + 동사','전치사 + 명사구/동명사','접속사 + 절: because + S+V'],
 ['명사는 주어·목적어 자리에 온다.','대명사는 명사를 대신한다.','형용사는 명사 수식과 보어 역할을 한다.','부사는 수식 대상을 찾아 고른다.','전치사 뒤에는 명사 역할이 필요하다.','동일 품사 선택지는 의미·결합까지 읽는다.'],
 ['동사 뒤에는 무조건 부사를 넣는다.','-ly를 보면 항상 부사로 단정한다.','품사만 맞으면 의미를 확인하지 않는다.'],
 ['빈칸의 문장 성분은 무엇인가?','무엇을 수식하는가?','절을 연결하는 자리가 필요한가?'],
 ['a detailed report: 상세한 보고서','respond promptly: 신속히 응답하다','remain available: 이용 가능 상태이다','highly effective: 매우 효과적인','customer satisfaction: 고객 만족','confirm a booking: 예약을 확인하다','because of delays: 지연 때문에','during the meeting: 회의 중에','before the office opens: 사무실이 열기 전에','a friendly receptionist: 친절한 접수 직원'],
 ('E-MAIL','Thank you for your prompt response. Our team reviewed the proposal carefully. The revised schedule is acceptable, and we will confirm the booking tomorrow. Please contact us if you need additional information.',
  ['prompt와 carefully는 각각 무엇을 꾸미나요?','acceptable은 어떤 성분인가요?','and와 if의 기능을 찾으세요.','이메일의 핵심 전달 내용은 무엇인가요?'],
  ['prompt는 명사 response를 꾸미는 형용사. carefully는 reviewed를 꾸미는 부사.','is 뒤 주어 schedule의 상태를 설명하는 보어이다.','and는 두 절을 연결하고 if는 연락해야 하는 조건절을 이끈다.','수정 일정을 수용하며 내일 예약을 확정하겠다는 내용이다.']))

chapter(3,'문장에서 동사 찾기',
 ['정형 동사와 준동사를 구별한다.','조동사·be·have가 만드는 동사구를 읽는다.','절마다 주어와 동사를 짝짓는다.'],[
 concept('★ 본동사와 준동사','정형 동사는 절의 서술어로 시제·수 또는 조동사 구조를 가진다. to do, doing, done은 다른 구조의 도움 없이 주절을 서술하지 못한다. -ed 형태는 과거 동사와 과거분사 모양이 같아 문맥으로 구별해야 한다.','The team plans to replace the software.','팀은 소프트웨어를 교체할 계획이다.','plans가 본동사이고 to replace는 plans의 내용을 보충하는 부정사이다.','① 주어를 찾는다. ② 시제·수 표시가 있는 동사를 찾는다. ③ to/-ing/-ed는 역할을 따로 확인한다.'),
 concept('★★ 동사구는 한 덩어리로 읽는다','조동사 뒤에는 동사원형, have 뒤 과거분사는 완료, be 뒤 -ing는 진행, be 뒤 과거분사는 수동태를 만든다. be는 단독으로 상태를 잇는 동사도 된다. 조동사+완료+수동처럼 여러 형태가 한 서술어를 이룰 수 있다.','The equipment has been inspected.','장비는 점검을 마쳤다.','has been inspected 전체가 현재완료 수동 동사구이다. 세 개의 독립 동사가 아니다.','① 앞의 조동사·have·be를 확인한다. ② 뒤에 필요한 형태를 연결한다. ③ 전체 동사구의 태와 시제를 읽는다.'),
 concept('★★★ 동사가 여러 개면 절의 경계를 찾는다','접속사나 관계사가 절을 더할 수 있다. 수식 분사는 동사처럼 보여도 별도 절의 본동사가 아니다. 쉼표만으로 독립절 두 개를 연결할 수 없다. 주어 뒤에 긴 수식어가 오면 주절 동사가 아직 필요한지 확인한다.','The invoices sent yesterday are now available online.','어제 발송된 청구서들은 이제 온라인에서 확인할 수 있다.','sent yesterday는 invoices 수식어이고 are가 주절 동사이다.','① 연결어와 절 경계를 표시한다. ② 각 절의 S+V를 찾는다. ③ 수식 분사를 본동사로 세지 않는다.')],
 [('was reviewing vs reviewed','was reviewing 전체는 과거진행 동사구. reviewed는 단독 과거 동사일 수도, have/be 뒤 과거분사일 수도 있다.'),('수식 분사 vs 동사','documents attached to the message는 명사구. The documents are attached.는 주어와 동사가 있는 절이다.')],
 ['modal + 동사원형','have/has + p.p.','be + -ing: 진행','be + p.p.: 수동','관계절·전치사구를 제외하고 주절 S+V 확인'],
 ['정형 동사는 절의 서술어이다.','to부정사만으로 주절 동사를 대신하지 못한다.','be/have/조동사를 뒤 형태와 묶는다.','-ed는 형태만으로 역할을 확정하지 않는다.','접속사·관계사가 절을 추가한다.','절마다 동사를 찾은 뒤 문장 전체를 해석한다.'],
 ['주어 뒤 -ing를 본동사로 고른다.','과거분사 수식어 뒤 필요한 동사를 놓친다.','수동·완료 동사구를 여러 독립 동사로 센다.'],
 ['이 절에 정형 동사가 있는가?','앞 조동사 뒤 형태가 맞는가?','연결어가 두 번째 절을 허용하는가?'],
 ['plan to expand: 확장할 계획이다','has been approved: 승인되었다','is being repaired: 수리 중이다','must be checked: 점검되어야 한다','documents attached: 첨부된 문서','employees working remotely: 원격 근무하는 직원','to reduce costs: 비용을 줄이기 위해','after reviewing the file: 파일 검토 후','will have finished: 완료했을 것이다','remains valid: 계속 유효하다'],
 ('NOTICE','The forms attached to this notice must be completed by June 12. Employees working at other branches may submit scanned copies. If you have already sent the forms, no further action is required.',
  ['첫 문장의 본동사구는 무엇인가요?','attached와 working은 각각 무엇을 꾸미나요?','if절과 주절의 동사를 찾으세요.','이미 제출한 직원은 무엇을 해야 하나요?'],
  ['must be completed: 조동사+수동태. attached는 본동사가 아니다.','attached는 forms, working은 Employees를 수식한다.','if절: have sent. 주절: is required.','추가 조치가 필요 없다. no further action이라는 부정 정보가 핵심이다.']))

chapter(4,'동사의 형태와 수일치',
 ['핵심 주어에 동사의 수를 맞춘다.','조동사 뒤 원형과 완료·수동 형태를 구분한다.','길어진 주어와 병렬 주어의 함정을 처리한다.'],[
 concept('★ 현재형 수일치와 동사 형태','일반 현재에서 3인칭 단수 주어는 보통 동사에 -s를 붙인다. be는 is/are, have는 has/have로 구별한다. 조동사 뒤에는 주어의 수와 관계없이 원형이 온다. 과거 일반동사는 대부분 수에 따라 형태가 바뀌지 않는다.','Each application requires a signature.','각 신청서에는 서명이 필요하다.','Each application은 단수이다. requires의 -s는 복수가 아니라 동사 단수 표시이다.','① 시제를 확인한다. ② 핵심 주어의 수를 정한다. ③ 조동사가 있으면 뒤를 원형으로 고른다.'),
 concept('★★ 수식어와 수량 표현','each/every는 단수 명사·동사와 쓴다. each of + 복수명사는 전체 주어를 단수로 본다. a number of + 복수명사는 복수, the number of + 복수명사는 수치 자체가 주어라 단수이다. 불가산명사도 단수 동사를 쓴다.','The number of online orders has increased.','온라인 주문 수가 증가했다.','가까운 orders가 아니라 number에 동사를 맞춘다.','① of구를 괄호로 묶는다. ② a number인지 the number인지 읽는다. ③ information/equipment 같은 불가산명사를 확인한다.'),
 concept('★★★ 병렬 주어와 도치','A and B는 보통 복수이다. either A or B / neither A nor B는 동사에 가까운 주어에 맞추는 것이 기본이다. there is/are는 뒤에 나오는 실제 주어를 확인한다. 집합명사는 영어 변종과 의미에 따라 달라질 수 있으므로 무조건 단수라는 과잉 규칙은 피한다.','Neither the assistants nor the manager is available.','보조 직원들도 관리자도 시간이 없다.','가까운 manager가 단수이므로 is를 쓴다.','① 병렬 연결어를 확인한다. ② nor/or 뒤 가까운 주어를 본다. ③ there 뒤 실제 주어를 찾는다.')],
 [('a number of vs the number of','A number of clients are waiting. 여러 고객은 복수. The number of clients is rising. 고객 수는 단수.'),('each vs all','Each employee has a pass. / All employees have passes. 한 명씩인지 전체 복수인지 구별한다.')],
 ['each/every + 단수 명사 + 단수 동사','each of + 복수명사 + 단수 동사','a number of + 복수 동사','the number of + 단수 동사','neither A nor B: 가까운 B에 일치'],
 ['현재 일반동사의 -s는 3인칭 단수 표시이다.','조동사 뒤는 원형이다.','주어의 핵심어를 찾는다.','불가산명사는 단수 취급한다.','and와 or/nor의 일치 방식을 구분한다.','there 뒤 명사가 실제 주어이다.'],
 ['of 뒤 복수명사에 동사를 맞춘다.','will 뒤에 -s를 붙인다.','equipment를 복수 취급한다.'],
 ['핵심 명사의 수는?','조동사가 있는가?','병렬 연결어가 and인가 or/nor인가?'],
 ['each of the applicants: 지원자 각각','every department: 모든 부서 각각','a number of complaints: 여러 불만','the number of visitors: 방문자 수','neither A nor B: A도 B도 아닌','either A or B: A 또는 B','along with the staff: 직원들과 함께','a list of items: 물품 목록','equipment is available: 장비를 이용할 수 있다','there are vacancies: 빈자리가 있다'],
 ('REPORT','The number of service requests has fallen this month. Each of the new agents handles about twenty calls a day. Neither the agents nor their supervisor expects a delay. There are still several open cases from last week.',
  ['첫 문장에서 왜 has를 쓰나요?','둘째 문장의 핵심 주어는 무엇인가요?','셋째 문장의 단수 동사 근거는?','아직 해결되지 않은 것은 무엇인가요?'],
  ['수치 number가 단수 핵심 주어이다.','Each이다. of the new agents는 전치사구이다.','nor 뒤 가까운 supervisor가 단수이다.','지난주 사건 몇 건이 열려 있다. 요청 감소가 모든 사건 해결을 뜻하지 않는다.']))

chapter(5,'시제',
 ['과거·현재·미래의 기준점을 구별한다.','완료와 진행의 의미를 복구한다.','시간 부사절에서 현재형이 미래를 나타내는 경우를 익힌다.'],[
 concept('★ 단순 시제와 진행','현재는 습관·일반 사실, 과거는 끝난 과거 사건, 미래는 예정·예측을 나타낸다. 진행형은 특정 시점에 진행 중인 활동이다. know, own 같은 상태 동사는 보통 진행형으로 쓰지 않는다. 시간 표현은 단서이지 기계적 정답표가 아니다.','The store opens at nine, but it is opening at ten today.','매장은 보통 9시에 열지만 오늘은 10시에 연다.','일반 운영 시간과 일시적인 오늘 일정의 차이를 읽는다.','① 언제 일어나는가? ② 반복인가 일시적 진행인가? ③ 문맥과 시간 표현을 함께 확인한다.'),
 concept('★★ 현재완료와 과거완료','현재완료 have/has+p.p.는 과거 사건을 현재의 경험·결과·계속과 연결한다. yesterday처럼 끝난 특정 과거 시점에는 보통 과거형을 쓴다. 과거완료 had+p.p.는 또 다른 과거 기준점보다 앞선 일을 나타낸다. since는 시작점, for는 기간을 나타낸다.','The team has worked here for three years.','그 팀은 여기서 3년째 일하고 있다.','현재까지 이어지는 기간인지, 과거에 끝난 기간인지 구분한다.','① 현재와 연결되는가? ② 끝난 과거 시점이 있는가? ③ 과거 두 사건의 선후 관계가 필요한가?'),
 concept('★★★ 미래완료와 시간 부사절','미래완료 will have+p.p.는 미래 기준점까지 완료될 일을 나타낸다. when, before, until, as soon as 같은 시간 부사절은 미래를 말해도 현재형을 쓴다. 단, 명사절의 when은 미래형을 쓸 수 있으므로 절의 역할을 구분한다.','We will call you as soon as the shipment arrives.','배송품이 도착하는 즉시 연락드리겠습니다.','arrives가 현재형이어도 의미는 미래이다.','① 시간 부사절인지 확인한다. ② 미래 시점까지 완료인지 본다. ③ 주절과 부사절의 시제를 별도로 고른다.')],
 [('since vs for','since Monday는 시작점. for three days는 기간. 둘 다 현재까지 계속되면 현재완료와 함께 쓸 수 있다.'),('has worked vs had worked','has는 현재와 연결. had는 과거 기준점 이전. 단지 오래전 일이라는 이유로 had를 쓰지 않는다.')],
 ['yesterday/last year: 끝난 과거 시점 확인','since + 시작점 / for + 기간','has/have been -ing: 과거부터 지금도 활동 중','had + p.p.: 과거보다 이전','by a future time: will have + p.p. 검토'],
 ['시제는 기준 시점과 사건 관계로 판단한다.','과거형은 끝난 과거를 나타낸다.','현재완료는 현재와 연결된다.','과거완료에는 과거 기준점이 필요하다.','진행형은 활동의 진행을 강조한다.','미래 시간 부사절에는 현재형을 쓴다.'],
 ['since 뒤 과거형을 보고 주절도 과거형으로 고른다.','과거완료를 오래된 과거로만 외운다.','시간 부사절에 무조건 will을 넣는다.'],
 ['기준점은 현재·과거·미래 중 무엇인가?','완료인가 진행인가?','빈칸이 시간 부사절 안인가?'],
 ['so far this month: 이번 달 지금까지','since the launch: 출시 이후','for several weeks: 몇 주 동안','by next Friday: 다음 금요일까지','as soon as it arrives: 도착하는 즉시','before the office closes: 사무실이 닫기 전에','had already left: 이미 떠났었다','is currently reviewing: 현재 검토 중이다','has recently expanded: 최근 확장했다','will have completed: 완료했을 것이다'],
 ('E-MAIL','We placed the order on March 2, but the supplier has not confirmed the shipping date yet. Our team has been preparing the display since Monday. We will open the showroom as soon as the equipment arrives.',
  ['placed와 has not confirmed의 시제 차이는?','has been preparing은 어떤 의미인가요?','arrives가 현재형인 이유는?','쇼룸 개장 조건은 무엇인가요?'],
  ['3월 2일은 끝난 과거. 아직 확인되지 않은 결과는 현재와 연결된다.','월요일부터 지금까지 전시 준비를 계속하고 있다.','미래 의미의 as soon as 시간 부사절이다.','장비 도착이다. 주문 완료나 준비 시작만으로 개장하지 않는다.']))

chapter(6,'능동태와 수동태',
 ['주어와 동사의 행위 관계를 판단한다.','조동사·완료·진행 수동태를 읽는다.','목적어와 전치사의 역할로 함정을 구분한다.'],[
 concept('★ 주어가 하는가, 받는가','능동태는 주어가 행위자이고 수동태는 주어가 행위의 대상이다. 기본 수동태는 be+p.p.이다. 원래 목적어를 취하는 동사의 수동태에서 그 목적어가 주어가 된다. arrive, happen처럼 목적어가 없는 자동사는 이런 수동태를 만들지 않는다.','The invoice was sent yesterday.','청구서는 어제 발송되었다.','청구서가 발송하는 것이 아니라 발송되는 것이므로 수동태이다.','① 주어가 동작을 수행하는지 본다. ② 동사의 목적어 필요 여부를 확인한다. ③ 받는 대상이면 be+p.p.를 검토한다.'),
 concept('★★ 동사구 안의 수동태','will be sent는 미래 수동, must be signed는 조동사 수동, has been approved는 완료 수동, is being repaired는 진행 수동이다. be동사의 시제·수와 과거분사 형태를 모두 갖추어야 한다.','The entrance is being repaired.','출입구를 수리하고 있다.','is being repaired 전체가 지금 진행 중인 수동 동사구이다.','① 조동사/완료/진행 표시를 본다. ② 수동 be가 필요한지 본다. ③ 마지막 동사가 p.p.인지 확인한다.'),
 concept('★★★ by가 없어도 수동태이다','행위자를 밝힐 필요가 없으면 by구를 생략한다. 전치사 with는 장비·재료 등 다른 관계를 나타낼 수 있다. 수여동사는 수동 뒤에 물건 목적어가 남기도 한다. 전치사 뒤 명사가 있다는 이유만으로 능동태의 직접목적어로 보지 않는다.','Employees were given new badges.','직원들은 새 출입증을 받았다.','직원이 받은 대상이고 new badges는 남아 있는 직접목적어이다.','① 주어·행위 관계를 우선 판단한다. ② by 유무에 의존하지 않는다. ③ 목적어가 남는 수여동사인지 확인한다.')],
 [('is repairing vs is being repaired','The technician is repairing the printer. / The printer is being repaired. 주어의 역할이 다르다.'),('equipped with vs repaired by','with 뒤에는 장비, by 뒤에는 수리 행위자 등이 온다. 수동태라고 항상 by만 쓰지 않는다.')],
 ['be + p.p.','modal + be + p.p.','have/has + been + p.p.','be + being + p.p.','arrive/happen/occur: 일반적인 목적어 수동태 불가'],
 ['수동태는 주어가 행위를 받는 구조이다.','수동 be의 수·시제도 확인한다.','조동사 뒤 수동은 be+p.p.이다.','완료 수동은 been을 포함한다.','진행 수동은 being을 포함한다.','by구는 선택적이다.'],
 ['주어 의미를 보지 않고 by만 찾는다.','been과 being을 혼동한다.','자동사를 수동태로 만든다.'],
 ['주어는 행위자·대상 중 어느 쪽인가?','목적어가 필요한 동사인가?','수동 동사구 형태가 완성되었는가?'],
 ['be approved: 승인되다','be issued: 발급되다','be submitted: 제출되다','be assigned to: 배정되다','be equipped with: ~을 갖추다','be covered by: ~에 의해 보장되다','has been repaired: 수리가 완료되었다','is being inspected: 점검 중이다','must be signed: 서명되어야 한다','be given instructions: 지시를 받다'],
 ('NOTICE','The east entrance is being repaired this week. Visitors will be directed to the west lobby. All appointments have been confirmed, so no changes to meeting times are required. Please follow the signs posted near the parking area.',
  ['진행 수동태와 미래 수동태를 찾으세요.','완료 수동태는 무엇인가요?','posted는 무엇을 꾸미나요?','방문자는 시간을 바꿔야 하나요?'],
  ['is being repaired / will be directed.','have been confirmed: 예약 확인을 마쳤다.','posted near the parking area는 signs를 수식한다.','아니다. 입구는 바뀌지만 미팅 시간 변경은 필요 없다.']))

chapter(7,'동명사와 to부정사',
 ['명사 역할의 -ing와 to부정사를 구별한다.','동사·전치사 뒤 결합을 익힌다.','목적·보어·의미 차이에 맞게 준동사를 고른다.'],[
 concept('★ 명사 역할과 목적 표현','동명사(-ing)는 주어·목적어·전치사 목적어가 된다. to부정사(to+원형)도 주어·목적어·보어가 될 수 있고 목적을 나타내기도 한다. 하나의 동명사구·부정사구가 주어이면 보통 단수로 본다.','Reducing waste saves money.','낭비를 줄이면 비용을 절약할 수 있다.','Reducing waste 전체가 단수 주어이다. 단어 두 개라고 복수가 아니다.','① 빈칸이 명사 역할인지 목적 수식인지 본다. ② 전치사가 있으면 동명사를 검토한다. ③ 주어인 구 전체의 수를 확인한다.'),
 concept('★★ 동사마다 뒤 형태가 다르다','enjoy, avoid, consider, finish는 보통 동명사를 목적어로 취한다. decide, plan, agree, hope는 to부정사와 결합한다. allow/ask/encourage + 사람 + to do처럼 목적어와 부정사를 함께 요구하는 동사도 있다.','We agreed to extend the deadline.','우리는 마감일을 연장하기로 합의했다.','agree 뒤 원형 extend만 쓰거나 extending으로 바꾸면 이 구조가 성립하지 않는다.','① 앞 동사를 확인한다. ② 목적어가 사람인지 확인한다. ③ 동사+준동사 결합을 통째로 적용한다.'),
 concept('★★★ to의 역할과 의미 차이','look forward to, be committed to의 to는 전치사이므로 뒤에 명사·동명사가 온다. stop doing은 하던 일을 중단, stop to do는 다른 일을 하려고 멈춤이다. remember doing은 과거 경험을 기억, remember to do는 해야 할 일을 잊지 않음이다.','Please remember to lock the cabinet.','수납장을 잠그는 것을 잊지 마세요.','이미 잠근 경험을 떠올리는 것이 아니라 앞으로 해야 할 행동을 요청한다.','① to가 전치사인지 부정사 표지인지 본다. ② stop/remember는 행동의 선후와 목적을 읽는다.')],
 [('to do vs to doing','plan to reduce는 부정사. be committed to reducing은 전치사 to+동명사.'),('stop doing vs stop to do','stopped talking: 말하기를 멈췄다. stopped to talk: 이야기하려고 다른 행동을 멈췄다.')],
 ['avoid/consider/finish + -ing','decide/plan/agree + to do','ask/allow/encourage + 사람 + to do','look forward to + 명사/-ing','remember to do: 앞으로 할 일'],
 ['동명사는 명사 역할을 한다.','to부정사는 to+원형이다.','전치사 뒤에는 동명사가 가능하다.','목적어 형태는 앞 동사와 함께 외운다.','to가 항상 부정사 표지는 아니다.','일부 동사는 준동사 형태에 따라 의미가 달라진다.'],
 ['전치사 to 뒤에 원형을 쓴다.','avoid to do로 기억한다.','앞으로 할 일에 remember doing을 쓴다.'],
 ['전치사 뒤인가?','앞 동사가 요구하는 결합은?','행동이 이미 일어났는가, 앞으로 할 일인가?'],
 ['avoid making errors: 실수를 피하다','consider relocating: 이전을 고려하다','finish reviewing: 검토를 마치다','agree to pay: 지불하기로 합의하다','plan to expand: 확장할 계획이다','encourage staff to apply: 직원의 지원을 권하다','look forward to meeting: 만남을 기대하다','be committed to improving: 개선에 전념하다','remember to submit: 제출을 잊지 않다','stop to check: 확인하려고 멈추다'],
 ('E-MAIL','We plan to update the booking system next month. Please avoid making new reservations during the test period. Remember to save any unfinished requests before signing out. We look forward to receiving your feedback.',
  ['plan과 avoid 뒤 형태를 비교하세요.','remember to save는 과거 경험인가요?','before signing out의 before는 어떤 역할인가요?','마지막 to 뒤 receiving인 이유는?'],
  ['plan+to update / avoid+making. 동사별 결합이 다르다.','앞으로 해야 할 저장 행동을 잊지 말라는 요청이다.','뒤 동명사구를 취하는 전치사이다.','look forward to의 to는 전치사이다.']))

chapter(8,'분사',
 ['현재분사와 과거분사의 수식 관계를 구별한다.','분사 수식어와 진행·수동 동사구를 분리한다.','감정 분사와 분사구문을 문맥으로 읽는다.'],[
 concept('★ 명사와의 능동·수동 관계','현재분사(-ing)는 수식받는 명사가 행위하는 관계, 과거분사(p.p.)는 대체로 행위를 받거나 완료된 상태를 나타낸다. 자동사의 과거분사는 fallen leaves처럼 완료 의미일 수 있어 모든 p.p.를 수동이라고 외우면 안 된다.','The documents attached to the e-mail are confidential.','이메일에 첨부된 문서는 기밀이다.','문서가 첨부되는 대상이므로 attached가 맞고, are가 본동사이다.','① 꾸밈받는 명사를 찾는다. ② 그 명사가 하는가 받는가를 본다. ③ 본동사가 따로 있는지 확인한다.'),
 concept('★★ 감정 분사는 사람이냐 사물이냐만의 문제가 아니다','interesting은 흥미를 일으키는 성질, interested는 흥미를 느끼는 상태이다. 사람도 an interesting speaker처럼 감정을 일으키면 -ing로 꾸밀 수 있다. 반드시 수식 대상과 감정의 방향을 본다.','The audience was interested in the new design.','청중은 새로운 디자인에 관심을 보였다.','청중은 흥미를 느끼는 쪽이므로 interested in을 쓴다.','① 감정을 느끼는 쪽인가 유발하는 쪽인가? ② 뒤 전치사까지 확인한다.'),
 concept('★★★ 분사구문의 숨은 주어','분사구문은 부사절을 줄여 시간·이유 등을 나타낸다. 기본적으로 분사의 행위자는 주절 주어와 일치한다. Having+p.p.는 주절보다 앞선 완료를 명시한다. 주어가 다르면 독립구문 같은 별도 구조가 필요하며 임의로 줄이면 안 된다.','Having reviewed the estimate, Ms. Lee approved the repair.','견적을 검토한 후 이 씨는 수리를 승인했다.','검토한 사람과 승인한 사람이 모두 Ms. Lee이다.','① 주절 주어를 먼저 찾는다. ② 분사 행동의 행위자가 같은지 본다. ③ 능동·수동과 선행 완료를 확인한다.')],
 [('working staff vs repaired equipment','직원이 일하는 능동 관계는 working. 장비가 수리된 수동·완료 상태는 repaired.'),('interesting person vs interested person','흥미로운 사람은 interesting. 관심을 가진 사람은 interested. 사람이라고 항상 -ed가 아니다.')],
 ['명사가 하는 행동: -ing 검토','명사가 받는 행동: p.p. 검토','be interested in / be satisfied with','Having + p.p.: 앞선 완료','분사구문의 기본 행위자 = 주절 주어'],
 ['분사는 명사를 수식할 수 있다.','현재분사는 능동 관계를 주로 나타낸다.','과거분사는 수동·완료 관계를 나타낸다.','분사와 본동사를 구분한다.','감정의 방향을 확인한다.','분사구문의 주어 일치를 확인한다.'],
 ['사람은 무조건 -ed로 고른다.','수식 분사를 본동사로 읽는다.','주절 주어와 분사 행위자가 다르다.'],
 ['수식받는 명사는 무엇인가?','능동·수동 관계가 맞는가?','분사구문의 숨은 주어가 일치하는가?'],
 ['attached documents: 첨부 문서','remaining seats: 남은 좌석','employees attending: 참석하는 직원','a revised estimate: 수정 견적','be interested in: ~에 관심 있다','be satisfied with: ~에 만족하다','a disappointing result: 실망스러운 결과','an experienced instructor: 경험 많은 강사','having reviewed: 검토한 후','located near the station: 역 근처에 위치한'],
 ('NOTICE','Employees attending the workshop should read the attached guide. The revised agenda includes a short product demonstration. Having tested the new devices, the trainer will explain the most common problems. Participants interested in a loan device should contact reception.',
  ['attending은 무엇을 꾸미나요?','attached와 revised의 관계는?','Having tested의 행위자는 누구인가요?','대여 기기가 필요한 참가자가 할 일은?'],
  ['Employees를 꾸미며 직원이 워크숍에 참석하는 능동 관계이다.','guide는 첨부되고 agenda는 수정된 대상이다.','주절 주어 the trainer이다.','접수처에 연락한다. interested in이 Participants를 뒤에서 수식한다.']))

chapter(9,'관계대명사',
 ['선행사와 관계절의 역할을 찾는다.','who/which/whom/whose/that을 구별한다.','제한적·비제한적 관계절과 전치사 위치를 이해한다.'],[
 concept('★ 관계절 안의 빈 역할을 찾는다','관계대명사는 앞 명사를 설명하는 절을 연결하면서 그 절 안에서 주어·목적어 역할을 한다. 사람 주격은 who, 사물은 which/that, 사람 목적격은 whom 등이 쓰인다. 선행사의 종류만 보지 말고 관계절에서 빠진 역할을 찾는다.','The technician who installed the system will return tomorrow.','시스템을 설치한 기술자가 내일 다시 올 것이다.','installed의 주어가 who이고 선행사는 technician이다.','① 선행사를 찾는다. ② 관계절의 S/V/O를 확인한다. ③ 빠진 역할과 선행사의 종류를 함께 맞춘다.'),
 concept('★★ 소유격 whose와 목적격 생략','whose+명사는 소유 관계를 나타내며 사람과 사물 선행사 모두에 쓸 수 있다. 제한적 관계절의 목적격은 생략 가능하지만 주격이나 바로 앞에 전치사가 있는 관계사는 같은 방식으로 생략하지 않는다.','We selected a supplier whose prices were competitive.','우리는 가격 경쟁력이 있는 공급업체를 선정했다.','whose prices 전체가 관계절 주어이다. who prices라고 쓰지 않는다.','① 빈칸 바로 뒤 명사가 있는지 본다. ② 선행사와 그 명사가 소유 관계인지 확인한다.'),
 concept('★★★ 쉼표와 전치사 뒤의 형태','쉼표가 있는 비제한적 관계절은 부가 정보를 주며 that을 쓰지 않는다. 전치사 바로 뒤에는 사람 whom, 사물 which를 쓴다. 관계절 내부의 동사는 관계대명사가 가리키는 선행사와 수를 맞춘다.','The consultant to whom we sent the report is unavailable.','우리가 보고서를 보낸 컨설턴트는 지금 연락할 수 없다.','to의 목적격이 필요하므로 whom이다.','① 쉼표 유무를 본다. ② 전치사가 관계사 앞으로 왔는지 본다. ③ 관계절 동사의 수를 확인한다.')],
 [('who vs whose','who develops software: 소프트웨어를 개발하는 사람. whose software is popular: 그 사람의 소프트웨어가 인기인 사람.'),('which vs that','사물 제한적 관계절에서는 둘 다 가능하다. 쉼표 뒤 비제한적 관계절이나 전치사 바로 뒤에는 which를 쓴다.')],
 ['who + 동사: 사람 주격','whose + 명사: 소유 관계','전치사 + whom/which','쉼표 뒤 that 사용 불가','제한적 목적격 관계사는 생략 가능'],
 ['관계절은 선행사를 수식한다.','관계대명사는 절 안에서 역할도 한다.','주격·목적격·소유격을 구분한다.','whose는 사물에도 가능하다.','쉼표 관계절에는 that을 쓰지 않는다.','전치사 뒤 격을 확인한다.'],
 ['사람이면 항상 who를 고른다.','whose 뒤 명사를 놓친다.','which와 that을 항상 서로 바꾼다.'],
 ['선행사는 사람인가 사물인가?','관계절 안에서 빠진 성분은?','쉼표·전치사가 있는가?'],
 ['staff who work remotely: 원격 근무 직원','a device that saves energy: 절전 장치','a client whose order arrived: 주문품을 받은 고객','the file we requested: 요청한 파일','a report which was revised: 수정 보고서','the person to whom: ~에게 해당하는 사람','the system on which: ~에 기반한 시스템','a supplier whose prices: 가격이 ~인 업체','the office, which is nearby: 가까운 그 사무실','applicants who meet the criteria: 기준 충족 지원자'],
 ('E-MAIL','The supplier whose quotation we accepted will deliver the tables on Tuesday. The driver, who has our contact number, will call before arrival. Please check the list that is attached to this message and report any missing items.',
  ['whose quotation에서 소유 관계는?','who절은 어떤 종류인가요?','that절의 주어와 동사는?','이메일이 요청하는 두 행동은?'],
  ['공급업체의 견적이라는 관계이다.','쉼표 사이의 부가 설명이다. who가 has의 주어이다.','that(=the list)이 주어, is attached가 동사이다.','첨부 목록을 확인하고 누락 물품을 보고하는 것이다.']))

chapter(10,'관계부사',
 ['where/when/why의 수식 대상을 찾는다.','관계대명사와 관계부사를 절 구조로 구별한다.','전치사+which로 바꾸어 관계를 확인한다.'],[
 concept('★ 관계부사는 절 안의 장소·시간·이유를 보충한다','where는 장소, when은 시간, why는 이유를 설명하는 절을 이끈다. 뒤 절에는 보통 주어·동사·필요한 목적어가 갖추어진다. 관계대명사는 그 절의 주어·목적어 자리를 채운다는 점이 다르다.','This is the room where we hold interviews.','여기는 우리가 면접을 진행하는 방이다.','we hold interviews는 목적어까지 있고 where는 장소 관계를 보충한다.','① 선행사를 찾는다. ② 뒤 절에 필요한 목적어가 있는지 본다. ③ 장소·시간 관계만 빠졌으면 관계부사를 검토한다.'),
 concept('★★ 장소 명사라고 항상 where는 아니다','the room which we reserved에서 reserve의 목적어가 빠져 있으므로 which가 필요하다. the room where we met에서 we met는 기본 구조가 갖추어져 있어 장소를 나타내는 where를 쓴다. 선행사의 뜻만으로 고르면 틀린다.','The room which we reserved has a projector.','우리가 예약한 방에는 프로젝터가 있다.','방은 장소이지만 reserved의 목적어이므로 관계대명사이다.','① 동사가 목적어를 요구하는지 본다. ② 목적어가 없으면 which/that, 장소 관계면 where를 검토한다.'),
 concept('★★★ 전치사+which와 간접의문절','where는 문맥에 따라 in/at which, when은 on/in/at which, why는 for which로 바꿀 수 있다. 전치사는 동사와 명사 사이의 실제 관계로 고른다. I know where the office is.의 where절은 앞 명사를 꾸미지 않고 know의 목적어인 간접의문절이다.','We remember the day on which the branch opened.','우리는 지점이 문을 연 날을 기억한다.','on which는 시간 선행사 day를 받는 when과 같은 관계이다.','① 앞에 선행사가 있는지 본다. ② 전치사 관계를 복원한다. ③ 절이 명사를 수식하는지 목적어인지 구분한다.')],
 [('where vs which','the office where she works: 그곳에서 일함. the office which she manages: 그 사무실을 관리함.'),('when vs on which','the day when we met = the day on which we met. 날짜에는 on을 쓰되 다른 시간 명사에서는 전치사가 달라질 수 있다.')],
 ['where: 장소 관계','when: 시간 관계','why: reason의 이유 관계','전치사 + which: 문맥에 맞는 전치사','선행사 뜻보다 뒤 절의 빠진 역할 확인'],
 ['관계부사는 앞 명사를 수식한다.','뒤 절의 주어·목적어 유무를 본다.','장소 명사도 목적어로 쓰이면 which가 필요하다.','when은 시간 관계이다.','why는 이유 관계이다.','명사절의 의문 부사와 역할을 구분한다.'],
 ['place만 보면 where를 고른다.','동사의 목적어가 빠진 것을 못 본다.','모든 where절을 관계절로 본다.'],
 ['뒤 절에 필요한 목적어가 있는가?','장소·시간 중 어떤 관계가 빠졌는가?','전치사+which로 바꾸면 맞는가?'],
 ['the venue where we met: 만났던 행사장','the day when it opened: 개장한 날','the reason why it failed: 실패한 이유','the office in which we work: 일하는 사무실','the date on which payment is due: 지급 기일','the building which we own: 소유 건물','the room that we booked: 예약한 방','the period during which: ~한 기간','the stage at which: ~한 단계','the place where records are kept: 기록 보관 장소'],
 ('ANNOUNCEMENT','The center where our team trains will close in July. We have reserved a room which holds thirty people in a nearby hotel. Staff will receive an e-mail on the day when registration opens. The reason why the center is closing is scheduled maintenance.',
  ['첫 where절의 주어와 동사는?','which holds에서 which의 역할은?','when이 받는 선행사는?','폐쇄 이유와 대체 장소는?'],
  ['our team / trains. where는 훈련 장소 관계이다.','관계절 주어이며 room을 가리킨다.','the day이다.','정기 보수 때문에 닫고 인근 호텔 방을 예약했다.']))

chapter(11,'접속사',
 ['등위·종속 접속사의 기능을 구별한다.','조건·이유·양보·시간 관계를 읽는다.','접속부사와 접속사의 문장 연결 방식을 구분한다.'],[
 concept('★ 절 연결과 병렬','and, but, or 같은 등위접속사는 문법적으로 대등한 요소를 잇는다. both A and B, either A or B 같은 짝도 형태를 맞춘다. because, although, if 등은 종속절을 이끌고 주절과 의미 관계를 만든다.','The app stores receipts and generates reports.','앱은 영수증을 저장하고 보고서를 생성한다.','stores와 generates가 같은 주어를 공유하며 병렬로 연결된다.','① 연결되는 두 요소를 찾는다. ② 같은 역할·형태인지 본다. ③ 종속절이라면 주절도 있는지 확인한다.'),
 concept('★★ 문맥 관계를 먼저 정한다','because는 이유, although는 양보, if/provided that은 조건, unless는 ~하지 않는 한, until은 지속의 끝점이다. 접속사 뒤에는 절이 오지만 문법적으로 가능한 후보가 여럿이면 앞뒤 사실 관계로 정답을 골라야 한다.','The order will remain on hold until payment arrives.','대금이 도착할 때까지 주문은 보류된다.','on hold 상태가 끝나는 조건을 until절이 나타낸다.','① 앞뒤의 주장을 짧게 요약한다. ② 이유·대조·조건·시간 중 관계를 정한다. ③ 연결어를 대입한다.'),
 concept('★★★ however는 접속부사이다','however, therefore, otherwise는 문장 간 논리 관계를 나타내는 부사이다. 독립절 두 개를 쉼표와 however만으로 잇는 것은 표준적인 연결 방식이 아니다. 세미콜론이나 마침표 등 문장 경계를 함께 확인한다.','The item is popular; however, it is temporarily unavailable.','그 제품은 인기가 있지만 일시적으로 품절이다.','세미콜론이 절을 연결하고 however가 대조 관계를 나타낸다.','① 빈칸 앞 문장부호를 본다. ② 문법상 접속사인지 부사인지 구분한다. ③ 의미 관계를 확인한다.')],
 [('although vs however','Although S+V, S+V. / S+V; however, S+V. 의미는 비슷해도 연결 구조가 다르다.'),('unless vs if','unless는 if ... not과 비슷하다. 이미 부정이 있는 문장에서 부정 방향을 다시 확인한다.')],
 ['because + 이유 절','although + 양보 절','unless = ~하지 않는 한','until + 지속 종료 시점 절','S+V; however/therefore/otherwise, S+V'],
 ['접속사는 절과 병렬 요소를 연결한다.','병렬 요소는 역할을 맞춘다.','종속절만으로 완전한 주절을 대신하지 않는다.','연결어는 주장 관계로 판단한다.','unless의 부정 방향을 확인한다.','접속부사는 문장부호를 함께 본다.'],
 ['문법만 맞으면 문맥은 읽지 않는다.','because와 therefore를 같은 구조로 쓴다.','unless를 if와 같은 긍정 조건으로 읽는다.'],
 ['뒤가 절인가?','앞뒤가 이유·양보·조건 중 무엇인가?','문장부호가 연결 방식을 허용하는가?'],
 ['because demand increased: 수요가 늘어서','although prices rose: 가격이 올랐지만','unless otherwise stated: 달리 명시되지 않으면','provided that: ~라는 조건으로','as soon as: ~하는 즉시','until payment arrives: 대금 도착까지','both efficient and reliable: 효율적이고 신뢰할 만한','either online or by mail: 온라인 또는 우편으로','therefore: 따라서','otherwise: 그렇지 않으면'],
 ('E-MAIL','Although the repair is complete, the machine cannot be used until a safety check is performed. Please keep the area clear because the inspector needs access. The check should finish by noon; otherwise, we will move the afternoon session to another room.',
  ['although절과 주절의 대조는?','until은 어떤 끝점을 나타내나요?','because절의 이유는?','otherwise 뒤 조치가 생기는 조건은?'],
  ['수리는 끝났지만 안전 점검 전에는 사용하지 못한다.','안전 점검이 수행되는 시점이다.','점검자가 접근해야 하므로 구역을 비워 둔다.','점검이 정오까지 끝나지 않으면 오후 세션을 옮긴다.']))

chapter(12,'전치사',
 ['전치사 뒤 명사 역할을 확인한다.','시간·장소·기한 표현을 구별한다.','동사·형용사와 전치사의 고정 결합을 복구한다.'],[
 concept('★ 전치사 뒤의 덩어리','전치사 뒤에는 명사·대명사·동명사 등 명사 역할이 온다. because of/despite/during은 뒤 절을 직접 이끌지 않는다. before/after/since처럼 전치사와 접속사 두 쓰임이 가능한 단어는 뒤 구조로 판단한다.','Please check the label before opening the package.','포장을 열기 전에 라벨을 확인하세요.','before 뒤 opening the package는 동명사구이다.','① 뒤가 명사구·동명사구·절 중 무엇인지 본다. ② 해당 단어가 그 구조를 받을 수 있는지 확인한다.'),
 concept('★★ by·until·within과 시간 표현','by는 완료 마감, until은 상태·행동의 지속 끝점, within은 일정 기간 안을 나타낸다. at은 시각, on은 날짜·요일, in은 월·연도·기간 등의 흔한 쓰임이 있다. in two days는 지금부터 이틀 후, within two days는 이틀 이내이다.','Submit the form by Friday; the desk will remain open until six.','금요일까지 양식을 제출하세요. 창구는 6시까지 열려 있습니다.','제출은 완료 기한, 개방은 지속 상태이다.','① 완료인가 지속인가? ② 시점인가 기간인가? ③ at/on/in의 대상 단위를 확인한다.'),
 concept('★★★ 결합과 다단어 전치사','comply with, depend on, be responsible for처럼 앞 단어와 함께 외워야 한다. in addition to, in accordance with, instead of 같은 덩어리도 하나의 전치사처럼 명사 역할을 취한다. 의미가 비슷한 동사라도 전치사는 다를 수 있다.','All suppliers must comply with the policy.','모든 공급업체는 그 정책을 준수해야 한다.','comply with를 conform to와 혼동하지 않는다.','① 앞 동사·형용사를 본다. ② 결합 전체를 복원한다. ③ 뒤가 명사 역할인지 확인한다.')],
 [('because vs because of','because the truck was late: 절. because of the delay: 명사구.'),('by vs until','send by noon: 정오까지 보내기 완료. remain open until noon: 정오까지 개방 지속.')],
 ['by + 완료 기한','until + 지속 끝점','within + 기간','despite/because of + 명사구','in addition to + 명사/-ing'],
 ['전치사는 명사 역할을 취한다.','동명사도 전치사 목적어가 된다.','시간의 시점과 기간을 구분한다.','by와 until은 행위 성격으로 판단한다.','다단어 전치사는 한 덩어리로 본다.','전치사는 앞 단어와 함께 외운다.'],
 ['전치사 뒤에 완전한 절을 붙인다.','~까지를 항상 until로 옮긴다.','동의어 동사의 전치사를 같게 쓴다.'],
 ['뒤 구조가 명사 역할인가?','완료·지속 중 무엇인가?','앞 단어의 고정 결합은?'],
 ['comply with rules: 규정을 준수하다','depend on demand: 수요에 달려 있다','be responsible for training: 교육을 담당하다','in accordance with policy: 정책에 따라','in addition to fees: 수수료 외에','instead of waiting: 기다리는 대신','by the deadline: 마감까지','within five days: 5일 이내','on arrival: 도착 시','at no extra charge: 추가 비용 없이'],
 ('POLICY','Expense claims must be submitted within seven days of a trip. Keep the original receipts until the claim is approved. In addition to completing the online form, employees must attach a copy of the itinerary. Claims without receipts may be rejected.',
  ['within seven days는 시점인가 기간인가요?','until절이 끝내는 상태는?','completing 앞 to는 어떤 역할인가요?','거절될 수 있는 청구는?'],
  ['출장 후 7일 이내라는 기간이다.','영수증을 보관하는 상태의 끝점이다.','in addition to의 전치사 to이므로 동명사를 취한다.','영수증이 없는 청구이다. may이므로 모든 건이 반드시 거절된다는 뜻은 아니다.']))

chapter(13,'대명사',
 ['주격·목적격·소유격·소유대명사를 구분한다.','재귀대명사의 필수·강조 용법을 익힌다.','지시·부정대명사의 지칭 범위를 읽는다.'],[
 concept('★ 격은 문장 역할로 고른다','주어는 she/they, 동사·전치사 목적어는 her/them, 명사 앞 소유격은 her/their, 명사 없이 소유를 나타내면 hers/theirs이다. her처럼 목적격과 소유격 형태가 같은 단어도 뒤 명사 유무로 구분한다.','Their office is larger than ours.','그들의 사무실은 우리 사무실보다 크다.','Their는 office를 꾸미고 ours는 our office를 대신한다.','① 빈칸의 역할을 찾는다. ② 바로 뒤 명사가 있는지 본다. ③ 주격·목적격·소유격·소유대명사를 고른다.'),
 concept('★★ 재귀대명사','주어와 목적어가 같은 대상을 가리키면 herself/themselves 등을 쓴다. 주어가 직접 했다는 강조에도 쓸 수 있다. by oneself는 혼자 또는 도움 없이이다. 주어와 다른 사람을 가리키는 목적어를 자동으로 재귀대명사로 바꾸면 안 된다.','The team prepared the display themselves.','팀원들이 직접 전시물을 준비했다.','목적어 display가 이미 있고 themselves는 직접 했다는 강조이다.','① 주어와 빈칸의 지칭 대상이 같은지 본다. ② 목적어가 이미 있는지 본다. ③ 필수 목적어인지 강조인지 구분한다.'),
 concept('★★★ one·another·others·those','one은 단수 가산명사를 대신할 수 있다. another는 추가·다른 하나, the other는 둘 중 나머지 하나, others는 불특정 다른 여럿, the others는 정해진 나머지 전부이다. those who는 ~하는 사람들, those of는 앞 복수명사를 대신하는 비교 표현이다.','Some applicants applied online; others mailed their forms.','어떤 지원자들은 온라인으로 지원했고 다른 지원자들은 서류를 우편으로 보냈다.','others 뒤에 명사가 없으며 불특정 다른 지원자들을 뜻한다.','① 단수·복수인지 본다. ② 뒤 명사 유무를 본다. ③ 정해진 나머지인지 불특정 다른 대상인지 확인한다.')],
 [('their vs theirs','their proposal: 뒤 명사 필요. The proposal is theirs.: 소유대명사로 명사 없이 사용.'),('other vs others','other branches: 형용사처럼 명사를 수식. others: 다른 대상들을 자체적으로 가리키는 대명사.')],
 ['소유격 + 명사 / 소유대명사 단독','by oneself: 혼자·도움 없이','another + 단수 가산명사','the other: 둘 중 나머지 하나','those who: ~하는 사람들'],
 ['격은 문장 역할로 판단한다.','소유격은 뒤 명사를 확인한다.','재귀대명사는 주어와 지칭을 맞춘다.','강조 재귀대명사는 목적어가 이미 있을 수 있다.','another와 other의 수를 구분한다.','정해진 범위에는 the를 확인한다.'],
 ['전치사 뒤에 주격을 쓴다.','명사 없이 their를 쓴다.','others 뒤에 명사를 덧붙인다.'],
 ['어떤 격이 필요한가?','지칭 대상과 수가 맞는가?','뒤에 명사가 있는가?'],
 ['on their behalf: 그들을 대신해','by herself: 혼자서','of our own: 우리 소유의','those who registered: 등록한 사람들','those of competitors: 경쟁사의 것들','another copy: 추가 사본 한 부','the other entrance: 둘 중 다른 출입구','other branches: 다른 지점들','some ... others: 일부는 ... 다른 이들은','each other: 서로'],
 ('E-MAIL','Your team may use our meeting room while yours is being repaired. Please ask staff to bring their own laptops. We will provide adapters for those who need them. If one adapter does not fit, reception can lend you another.',
  ['yours가 대신하는 명사는?','their own은 누구의 노트북인가요?','those와 them은 각각 무엇을 가리키나요?','another 뒤 생략된 명사는?'],
  ['your meeting room이다.','직원들 자신의 노트북이다.','those는 어댑터가 필요한 사람들, them은 adapters이다.','adapter이다.']))

chapter(14,'비교급과 최상급',
 ['원급·비교급·최상급 구조를 구별한다.','비교급 강조와 병렬 비교를 익힌다.','비교 대상이 같은 범주인지 확인한다.'],[
 concept('★ 두 대상 비교와 범위 내 최상','비교급은 -er 또는 more+형용사/부사로 만들고 than과 자주 쓴다. 최상급은 -est 또는 most로 범위 안의 최고 수준을 나타낸다. 형용사 최상급 앞에는 보통 the가 오지만 소유격 등이 대신할 수 있다. good/better/best 같은 불규칙형도 있다.','This route is faster than the previous one.','이 경로는 이전 경로보다 빠르다.','than이 있으면 비교급을 먼저 검토한다.','① 비교 대상 수와 범위를 본다. ② than/among/in을 확인한다. ③ 비교급·최상급 형태를 고른다.'),
 concept('★★ 원급 비교와 강조','as+형용사/부사 원급+as는 동등 비교이다. 비교급은 much/far/even/considerably 등으로 강조할 수 있고 very는 보통 비교급을 직접 꾸미지 않는다. 형용사를 비교하는지 동작 방식을 비교하는지도 본다.','The new system is much more reliable.','새 시스템은 훨씬 더 안정적이다.','much가 비교급 more reliable을 강조한다.','① as ... as 안이면 원급을 본다. ② 비교급 앞 강조어를 확인한다. ③ 형용사·부사 자리를 구분한다.'),
 concept('★★★ 같은 대상을 비교한다','가격과 회사를 직접 비교하지 않는다. The price is lower than that of ...에서 that은 단수 price, those는 복수 prices를 대신한다. the+비교급, the+비교급은 한쪽 변화에 따라 다른 쪽이 변하는 관계이다.','Our prices are lower than those of nearby stores.','우리 가격은 인근 매장의 가격보다 낮다.','prices와 stores가 아니라 prices와 those(가격)를 비교한다.','① 무엇과 무엇을 비교하는지 적는다. ② 생략된 명사를 that/those로 복원한다. ③ 수가 같은지 본다.')],
 [('more efficient vs most efficient','than과 두 시스템 비교는 more. 정해진 여러 시스템 중 최고는 the most.'),('very vs much','very useful은 가능. much more useful이 비교급 강조이다.')],
 ['as + 원급 + as','비교급 + than','the + 최상급 + 범위','much/far/even + 비교급','단수 비교 that / 복수 비교 those'],
 ['than은 비교급 단서이다.','as ... as에는 원급이 온다.','최상급의 비교 범위를 확인한다.','비교급 앞 강조어를 구분한다.','비교하는 명사 범주를 맞춘다.','that/those는 앞 명사의 수를 따른다.'],
 ['as와 than을 섞는다.','very more로 강조한다.','가격과 회사를 직접 비교한다.'],
 ['원급·비교급·최상급 중 무엇인가?','강조어가 형태와 맞는가?','비교 대상의 범주와 수가 같은가?'],
 ['more reliable than: ~보다 안정적인','as quickly as: ~만큼 빨리','the most efficient option: 가장 효율적 선택','much lower costs: 훨씬 낮은 비용','far more convenient: 훨씬 편리한','even better service: 더 나은 서비스','one of the largest firms: 가장 큰 기업 중 하나','less expensive than: ~보다 저렴한','those of other suppliers: 다른 공급자의 것들','the sooner, the better: 빠를수록 좋은'],
 ('ADVERTISEMENT','Our new scanner is twenty percent faster than the previous model. It is also as compact as the older device. Of the three scanners in this series, it offers the lowest running costs. The more pages your team scans, the greater the potential savings.',
  ['비교급과 원급 비교를 각각 찾으세요.','최상급의 비교 범위는?','the more ... the greater는 무슨 관계인가요?','더 작다는 광고인가요?'],
  ['faster than / as compact as.','이 시리즈의 스캐너 세 종이다.','스캔 장수가 늘수록 잠재 절감액이 커진다는 비례 관계이다.','아니다. 이전 기기만큼 작다는 동등 비교이다.']))

chapter(15,'가정법',
 ['현실 조건과 반대 가정을 구분한다.','현재·과거 가정의 동사 형태를 복구한다.','if 생략 도치와 요구·권고절을 구분한다.'],[
 concept('★ 현실 조건과 현재 반대 가정','If+현재, will+원형은 현실적인 미래 조건이다. 현재 사실과 다르거나 실현 가능성이 낮은 가정은 If+과거형, would/could+원형을 쓴다. 가정의 be는 격식 문맥에서 were를 모든 주어와 쓸 수 있다. 과거형이 언제나 과거 시간을 뜻하는 것은 아니다.','If we had more space, we would install another printer.','공간이 더 있다면 프린터를 한 대 더 설치할 텐데요.','현재 공간이 부족하다는 가정을 had로 나타낸다.','① 현실적 미래 조건인가 반대 가정인가? ② 현재 상황이면 과거형+would 원형을 검토한다.'),
 concept('★★ 과거 반대 가정','이미 끝난 과거 사실의 반대는 If+had+p.p., would/could have+p.p.이다. 과거에 확인하지 않아 생긴 오류처럼 실제 결과와 가정 결과를 함께 읽는다. 혼합 가정은 과거 조건과 현재 결과처럼 기준 시점이 다를 때 가능하다.','If we had checked the address, the parcel would have arrived on time.','주소를 확인했더라면 소포가 제시간에 도착했을 텐데요.','과거 확인 실패와 배송 지연의 반대를 가정한다.','① 실제 과거 사건을 찾는다. ② if절과 결과절을 각각 과거완료·완료형 조동사로 맞춘다.'),
 concept('★★★ if 생략 도치와 당위절','If you should need help는 Should you need help로, If we had known은 Had we known으로 도치할 수 있다. recommend/request/require that절의 동사원형은 요구·권고 내용을 나타내는 별도 구조이다. 수동이면 be+p.p.가 된다. 이를 모두 과거 반대 가정으로 해석하지 않는다.','The director requested that the draft be revised.','책임자는 초안을 수정하도록 요청했다.','요청 내용의 수동 당위절이므로 be revised이다.','① 문두 should/had 도치인지 본다. ② 요구·권고 동사 뒤 that절이면 원형을 검토한다. ③ 수동 관계를 확인한다.')],
 [('If we have vs If we had','실현 가능한 미래 조건은 have. 현재 공간이 부족하다는 반대 가정이면 had.'),('had known vs would have known','if절은 had known, 가정의 결과절은 would have known이 기본이다.')],
 ['If + 과거형, would + 원형','If + had p.p., would have p.p.','Should you need ... = If you should need ...','Had we known ... = If we had known ...','request that S + be p.p.'],
 ['가정은 실제 시점과 가능성을 먼저 본다.','현재 반대 가정은 과거형을 쓴다.','과거 반대 가정은 had+p.p.를 쓴다.','과거 결과 가정은 would have+p.p.이다.','if 생략 시 조동사가 주어 앞으로 온다.','당위절은 반대 가정과 구별한다.'],
 ['if절에 would를 기계적으로 넣는다.','과거 가정 결과에 would 원형만 쓴다.','요구절의 원형을 수일치 오류로 본다.'],
 ['현재 가정인가 과거 가정인가?','조건절과 결과절을 구분했는가?','도치·당위절의 별도 구조인가?'],
 ['if I were available: 시간이 있다면','would reduce costs: 비용을 줄일 텐데','had we known: 알았더라면','would have avoided: 피했을 텐데','should you need assistance: 도움이 필요하면','were it possible: 가능하다면','request that it be sent: 발송하도록 요청하다','recommend that staff attend: 참석을 권고하다','without your help: 당신 도움 없이는','otherwise we would have failed: 아니면 실패했을 것이다'],
 ('E-MAIL','If we had received the estimate earlier, we would have approved the repair last week. We now need the work completed by Friday. The manager has requested that a revised schedule be sent today. Should you need access to the building, call reception.',
  ['첫 문장은 실제 과거와 어떤 관계인가요?','당위절의 동사구는?','Should you need의 일반 어순은?','오늘 보내야 하는 것은?'],
  ['견적을 늦게 받아 지난주 승인하지 못한 상황의 반대를 가정한다.','be sent: 요청된 일정표가 발송되는 수동 관계이다.','If you should need access ...','수정 일정표이다. 수리 자체의 기한 금요일과 구분한다.']))

chapter(16,'명사와 관사',
 ['가산·불가산명사의 수를 구별한다.','a/an/the의 선택 기준을 복구한다.','수량 표현과 명사 수식 구조를 읽는다.'],[
 concept('★ 가산명사와 불가산명사','가산 단수명사는 보통 a/the/my 같은 한정사가 필요하다. 불가산명사는 information, equipment, advice, furniture처럼 보통 a/an이나 복수 -s를 쓰지 않는다. 단위는 a piece of information처럼 별도로 표현한다. 명사는 뜻에 따라 가산성이 달라질 수 있다.','We need additional information about the equipment.','장비에 관한 추가 정보가 필요합니다.','information과 equipment는 이 의미에서 불가산명사이다.','① 명사의 해당 의미가 가산인지 본다. ② 단수 가산이면 한정사를 확인한다. ③ 수량 표현을 맞춘다.'),
 concept('★★ a/an과 the','a/an은 불특정 하나를 소개하고, the는 이미 알려졌거나 문맥상 특정되는 대상을 나타낸다. an은 철자가 아니라 다음 단어의 모음 소리 앞에 쓴다. an hour, a university가 대표적이다. 소유격·지시어와 관사를 겹쳐 쓰지 않는다.','An employee left a folder at the desk. The folder is blue.','한 직원이 창구에 폴더를 놓고 갔다. 그 폴더는 파란색이다.','처음 소개한 folder를 다시 특정하므로 the folder이다.','① 특정 대상인가? ② 불특정 단수이면 발음으로 a/an을 고른다. ③ 소유격 등 다른 한정사가 있는지 본다.'),
 concept('★★★ 수량 표현과 복합명사','many/few는 가산 복수, much/little은 불가산명사와 쓴다. a few/a little은 조금 있다는 긍정, few/little은 거의 없다는 부정적 의미를 띤다. 명사+명사 구조에서는 앞 명사가 종류를 수식한다. customer satisfaction처럼 뒤 핵심 명사가 전체 역할을 결정한다.','Only a few seats remain, but we have little time to register.','좌석이 조금 남아 있지만 등록할 시간은 거의 없다.','seats는 가산 복수, time은 여기서 불가산이다.','① 뒤 명사의 가산성을 확인한다. ② a의 유무로 의미 방향을 본다. ③ 복합명사의 마지막 핵심어를 찾는다.')],
 [('many vs much','many applications: 셀 수 있는 복수. much information: 불가산.'),('a few vs few','a few options는 몇 가지가 있음. few options는 선택지가 거의 없음을 강조한다.')],
 ['information/equipment/advice/furniture: 불가산','a piece of advice: 조언 한 가지','a/an: 다음 단어의 발음 기준','many/few + 복수 / much/little + 불가산','a few/a little: 조금은 있음'],
 ['명사의 뜻에 맞는 가산성을 확인한다.','가산 단수에는 보통 한정사가 필요하다.','불가산명사는 단위 표현으로 센다.','a/an은 소리로 고른다.','the는 특정 대상을 가리킨다.','수량 표현과 명사의 수를 맞춘다.'],
 ['informations처럼 복수형을 만든다.','an university처럼 철자로 관사를 고른다.','much applicants처럼 수량 표현을 혼동한다.'],
 ['셀 수 있는 해당 의미인가?','관사가 필요한 단수인가?','이미 특정된 대상인가?'],
 ['a piece of equipment: 장비 한 점','additional information: 추가 정보','some advice: 약간의 조언','an hour: 한 시간','a university: 한 대학교','the attached invoice: 첨부된 청구서','many applicants: 많은 지원자','much progress: 큰 진전','a few remaining seats: 조금 남은 좌석','customer satisfaction: 고객 만족'],
 ('NOTICE','An orientation session will take place on June 9. The session lasts an hour and includes a tour. Please bring a pen; all other equipment will be provided. A few places remain, so submit your application today.',
  ['두 번째 session 앞 the인 이유는?','an hour에서 an인 이유는?','equipment는 어떤 수인가요?','자리가 전혀 없다는 뜻인가요?'],
  ['첫 문장에서 소개한 특정 세션을 다시 가리킨다.','hour의 첫 소리가 모음이기 때문이다.','불가산명사로 단수 취급한다.','아니다. a few는 소수이지만 남아 있음을 뜻한다.']))

chapter(17,'형용사와 부사',
 ['명사 수식과 보어 자리를 구별한다.','부사의 수식 범위와 위치를 읽는다.','비슷한 형태이지만 의미가 다른 단어를 구분한다.'],[
 concept('★ 형용사는 명사 수식 또는 보어','형용사는 a reliable service처럼 명사 앞이나 The service is reliable.처럼 연결동사 뒤에 온다. 목적어의 상태를 나타내는 keep the area clean에서도 형용사가 필요하다. something useful처럼 부정대명사 뒤에 오기도 한다.','Please keep the walkway clear.','통로를 비워 두세요.','clear는 keep을 꾸미는 부사가 아니라 walkway의 상태 보어이다.','① 빈칸이 명사 수식인지 보어인지 본다. ② 주어나 목적어의 상태를 설명하면 형용사를 고른다.'),
 concept('★★ 부사가 무엇을 꾸미는지 찾는다','부사는 동사·형용사·다른 부사·문장 전체를 수식한다. carefully reviewed, exceptionally helpful, very quickly처럼 대상에 따라 위치가 달라진다. be동사 뒤에도 부사가 올 수 있지만 뒤 형용사나 분사를 수식하는지 확인해야 한다.','The instructions are exceptionally clear.','설명은 매우 명확하다.','exceptionally는 clear를, clear는 주어 instructions를 설명한다.','① 수식 대상을 정확히 찾는다. ② 전체 문장 뼈대가 완성되었는지 본다. ③ 의미 강도와 위치를 확인한다.'),
 concept('★★★ hard/hardly, late/lately의 의미 차이','hard는 열심히·단단하게, hardly는 거의 ~않다. late는 늦게, lately는 최근에이다. fast는 형용사·부사 형태가 같다. highly successful처럼 결합에 따라 자연스러운 정도 부사도 달라진다. 형태가 비슷해도 뜻이 자동으로 같아지지 않는다.','We have hardly any spare parts left.','남은 예비 부품이 거의 없다.','hardly는 부정에 가까운 수량 의미이며 열심히가 아니다.','① -ly 유무만으로 답을 고르지 않는다. ② 문맥의 긍정·부정 방향을 읽는다. ③ 고정 결합을 확인한다.')],
 [('careful vs carefully','a careful inspection: 명사 수식. inspect carefully: 행동 수식.'),('hard vs hardly','work hard는 열심히 일하다. hardly work는 거의 일하지 않다. 의미가 크게 다르다.')],
 ['remain/become/seem + 형용사','keep + 목적어 + 형용사','부사 + 형용사 / 부사 + 분사','hardly = 거의 ~않다','late = 늦게 / lately = 최근에'],
 ['형용사는 명사와 보어 자리를 채운다.','목적격 보어도 형용사일 수 있다.','부사는 수식 대상을 찾는다.','be 뒤라고 반드시 형용사만 오는 것은 아니다.','-ly가 의미까지 보장하지 않는다.','고정 결합과 부정 방향을 함께 본다.'],
 ['keep 뒤 동작 수식이라고 부사를 쓴다.','be 뒤 부사를 모두 제거한다.','hardly를 열심히로 해석한다.'],
 ['수식 대상은 명사·동사·형용사 중 무엇인가?','보어가 필요한가?','긍정·부정 방향이 맞는가?'],
 ['remain fully operational: 완전히 가동 중이다','highly recommended: 적극 추천되는','closely monitor: 면밀히 관찰하다','reasonably priced: 합리적 가격의','keep files secure: 파일을 안전하게 유지하다','exceptionally helpful: 매우 도움이 되는','work hard: 열심히 일하다','hardly any: 거의 없는','arrive late: 늦게 도착하다','have recently changed: 최근 바뀌었다'],
 ('SERVICE UPDATE','The help desk is fully operational again. Our technicians worked hard to restore access, and the system is now considerably faster. Please keep your password secure. If a page still loads slowly, send us a brief description of the problem.',
  ['fully와 considerably의 수식 대상은?','secure는 어떤 역할인가요?','hard가 hardly이면 뜻은 어떻게 바뀌나요?','느리게 열리는 페이지가 있으면 무엇을 보내나요?'],
  ['fully는 operational, considerably는 비교급 faster를 꾸민다.','password의 상태를 설명하는 목적격 보어이다.','열심히 복구했다가 거의 일하지 않았다는 뜻으로 바뀐다.','문제의 간단한 설명을 보낸다. brief는 description 수식 형용사이다.']))

chapter(18,'어휘와 콜로케이션',
 ['문맥에 맞는 뜻과 목적어를 고른다.','단어를 결합과 예문으로 기억한다.','지문 속 동의 표현과 논리 연결을 확인한다.'],[
 concept('★ 뜻보다 결합까지 기억한다','address는 명사 주소, 동사 문제를 다루다 또는 청중에게 연설하다이다. address an issue / mailing address / address the audience처럼 품사·목적어·상황을 함께 익힌다. 한글 뜻 하나로 모든 문장에 대입하지 않는다.','The manager addressed the concern during the briefing.','관리자는 브리핑에서 그 우려를 다뤘다.','concern을 목적어로 취하므로 주소가 아니라 문제를 다루는 동사이다.','① 빈칸의 품사를 본다. ② 목적어와 상황을 읽는다. ③ 결합으로 뜻을 확정한다.'),
 concept('★★ 동사와 목적어·전치사를 묶는다','raise funds, meet a deadline, place an order, issue a refund처럼 자연스러운 짝이 있다. attend a meeting은 전치사 없이 목적어를 취하고 participate in a meeting은 in이 필요하다. rise는 자동사, raise는 타동사이다.','The store issued a refund after checking the receipt.','매장은 영수증 확인 후 환불을 처리했다.','refund와 자연스럽게 결합하는 issue를 고른다.','① 목적어를 확인한다. ② 동사가 직접 목적어를 받는지 본다. ③ 전치사까지 결합을 확인한다.'),
 concept('★★★ 동의어와 문맥 연결','postpone은 일정 연기, cancel은 취소, revise는 수정, replace는 교체이다. 같은 긍정·부정 방향의 단어라도 행동이 다르다. 독해에서는 reschedule/move to a later date 같은 바꿔 표현을 연결한다. however/therefore도 문맥의 대비·결과를 확인해야 한다.','The seminar was postponed, so the tickets remain valid for the new date.','세미나가 연기되어 표는 새 날짜에도 유효하다.','일정만 이동했으며 행사가 취소되었다고 추론하지 않는다.','① 실제로 바뀐 것이 날짜·내용·대상 중 무엇인지 본다. ② 원문과 선택지가 같은 행동을 나타내는지 확인한다.')],
 [('raise vs rise','raise prices는 가격을 올리다. prices rise는 가격이 오르다. 목적어 유무가 다르다.'),('postpone vs cancel','postpone은 나중으로 옮김. cancel은 계획을 취소함. 둘을 같은 사건으로 읽지 않는다.')],
 ['address an issue / a concern','meet a deadline / requirements','place an order / issue a refund','attend + 행사 / participate in + 행사','raise + 목적어 / rise: 자동사'],
 ['어휘는 품사·뜻·결합으로 익힌다.','동사의 목적어를 함께 확인한다.','전치사 유무도 결합 일부이다.','자동사와 타동사를 구분한다.','연기·취소·수정·교체를 구별한다.','동의 표현은 문맥에서 의미가 유지되는지 본다.'],
 ['한글 뜻이 비슷하면 서로 바꾼다.','attend to a meeting으로 쓴다.','일정 연기를 행사 취소로 읽는다.'],
 ['품사 자리가 맞는가?','목적어·전치사 결합이 자연스러운가?','앞뒤 문맥의 실제 행동과 같은가?'],
 ['address an issue: 문제를 다루다','mailing address: 우편 주소','address the audience: 청중에게 연설하다','meet a deadline: 기한을 지키다','raise funds: 자금을 모으다','place an order: 주문하다','issue a refund: 환불을 처리하다','participate in training: 교육에 참여하다','accommodate guests: 손님을 수용하다','renew a subscription: 구독을 갱신하다'],
 ('E-MAIL','We have postponed the training session to July 18 to accommodate a larger group. Your existing registration remains valid. Please check your mailing address in the account settings so that we can send the revised materials. Contact us if the new date does not meet your needs.',
  ['postponed는 취소인가 일정 변경인가요?','accommodate의 목적어와 뜻은?','mailing address에서 address의 품사는?','다시 등록해야 하나요?'],
  ['7월 18일로 옮긴 일정 변경이다.','a larger group을 수용한다는 뜻이다.','주소를 뜻하는 명사이다.','기존 등록이 유효하므로 재등록 지시는 없다.']))
