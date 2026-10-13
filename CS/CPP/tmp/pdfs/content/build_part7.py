import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

STRATEGY = {
    '목적': ('제목과 발신·수신 관계를 확인하고, 첫 문장의 요청과 마지막 행동 지시를 연결한 뒤 글 전체를 설명하는 보기를 고른다.', '목적은 한 문장의 소재보다 발신자가 독자에게 기대하는 행동 또는 전달하려는 변화로 판단한다.'),
    '세부 정보': ('질문의 대상과 조건을 표시하고 같은 대상을 다루는 문장을 찾은 뒤, 시간·수량·조건까지 보기와 대조한다.', '같은 명사가 보인다는 이유로 고르지 말고, 그 명사에 붙은 조건과 행위자를 함께 확인한다.'),
    '추론': ('질문 대상에 관한 직접 진술을 찾고 필요한 전제만 결합한 뒤, 지문이 뒷받침하는 최소 범위의 결론을 고른다.', '추론은 근거의 결합이다. 일반 상식이나 가능성만으로 지문보다 강한 결론을 만들지 않는다.'),
    'NOT/EXCEPT': ('부정형 질문 표시를 먼저 하고 보기 네 개의 근거를 각각 찾은 뒤, 확인된 세 항목을 제외한다.', '부정형 문제는 지문에 언급되거나 성립하는 세 선택지를 확인해 남은 하나를 선택한다.'),
    '문맥상 의미': ('해당 표현의 앞뒤 문장과 목적어를 확인하고 후보 표현으로 바꾸어 문장의 의도가 유지되는지 검토한다.', '문맥상 의미는 익숙한 첫 뜻보다 해당 문장이 수행하는 기능과 결합 관계로 결정한다.'),
    '지칭': ('지시어의 수·문법적 역할을 확인하고 앞 문장의 후보들을 대입해 실제 행동이나 속성이 맞는지 검토한다.', '가장 가까운 명사가 항상 지칭 대상은 아니다. 문법적 일치와 문맥상 행동의 적합성을 함께 검증한다.'),
    '문장 삽입': ('삽입 문장의 지시어와 연결어를 표시하고 앞쪽 선행 정보와 뒤쪽 전개를 모두 연결하는 위치를 찾는다.', '문장 삽입은 앞 문장과의 연결만으로 결정하지 않는다. 뒤 문장의 논리와 반복 정보도 확인한다.'),
    '대화 의도': ('발언 앞의 질문과 뒤의 응답을 읽고, 말하는 사람이 해결하려는 상황에 맞추어 의미를 바꾸어 표현한다.', '채팅 발언의 의도는 직역보다 발언을 유발한 문제와 이어지는 행동에서 확인한다.'),
    '복수 지문 연계': ('질문의 연결 대상인 이름·날짜·번호를 각 문서에서 찾고 두 근거를 나란히 놓은 뒤 공통 조건을 적용한다.', '복수 지문 정답은 서로 다른 문서의 사실이 같은 대상에 적용될 때 성립한다. 작성 시점과 갱신 내용도 확인한다.'),
}

def Q(i, prompt, options, answer, typ, level, evidence, analysis, why, wrong):
    assert len(options) == 4
    assert set(wrong) == set('ABCD') - {answer}
    order, rule = STRATEGY[typ]
    return dict(id=i, prompt=prompt, options=options, answer=answer, type=typ, level=level,
                clue=evidence, analysis=analysis, why=why, wrong=wrong, order=order, rule=rule)

def D(title, text):
    return dict(title=title, text=text.strip())

def S(title, documents, questions):
    return dict(title=title, documents=documents, questions=questions)

data = {'intro': [
    'Part 7은 한 문장의 해석을 문서 전체의 행동·조건·시간과 연결하는 훈련이다. 아래 지문과 문제는 이 교재를 위해 새롭게 만든 업무·생활 상황으로 구성하였다.',
    '단일 지문에서는 문장 구조와 정보 위치를, 복수 지문에서는 같은 대상의 조건과 변경 사항을 연결한다. 연습 문제를 푼 뒤 정답뿐 아니라 모든 오답의 근거가 어디서 어긋나는지 확인한다.'
], 'sections': [], 'training': [], 'mock': []}

data['sections'] = [
    {'title': '01 핵심 성분을 먼저 잡는 독해', 'paragraphs': [
        '문장을 볼 때 모든 단어를 같은 비중으로 번역하지 않는다. 먼저 주어와 시제가 표시된 동사를 묶고, 그 동사가 목적어를 필요로 하는지 또는 주어의 상태를 설명하는 보어를 취하는지 확인한다. 전치사구·관계절·분사구는 핵심 골격에 붙는 정보다. 수식어를 잠시 괄호로 묶어도 본동사는 반드시 남아 있어야 한다.',
        '예문: The coordinator sent the revised schedule to all department heads after the supplier confirmed delivery. 주어 The coordinator, 본동사 sent, 목적어 the revised schedule이 주절의 골격이다. to all department heads는 수신 대상, after절은 발송 시점을 제한한다. after절 안에서는 the supplier가 주어이고 confirmed가 동사다. 질문이 발송 시점을 묻는다면 주절만 이해해서는 부족하고 after절의 완료 사건까지 읽어야 한다.'
    ]},
    {'title': '02 긴 수식어·관계절·분사·동격 분석', 'paragraphs': [
        '관계절은 앞 명사를 특정하거나 추가 설명한다. 관계절의 동사가 보인다고 그것을 문장 전체의 본동사로 오인하지 않는다. 콤마로 둘러싸인 동격 명사구와 삽입구는 잠시 제외하고 주어와 본동사를 연결한다. 분사 뒤 목적어·전치사구까지 수식 범위에 포함될 수 있으므로 분사 한 단어에서 끊지 않는다.',
        '예문: The replacement units, which were inspected by Mira Chen, our quality manager, arrived on Friday. 골격은 The replacement units arrived다. which were inspected by Mira Chen은 units를 설명하는 수동 관계절이고, our quality manager는 Mira Chen과 같은 인물을 가리키는 동격이다. inspected의 행위자와 arrived의 주체를 혼동하면 검사자와 배송 물품을 뒤바꾸는 오답에 걸린다.',
        '예문: Having reviewed the revised plan, the committee approved the smaller venue. Having reviewed는 주절 주어 the committee의 선행 행동을 나타낸다. approved가 본동사이고 the smaller venue가 목적어다. 선행 검토와 승인이라는 사건 순서를 보존한다. 긴 문장의 질문도 보통 행위자·대상·조건 중 하나를 묻기 때문에 이 골격 표시가 속도와 정확성을 함께 높인다.'
    ]},
    {'title': '03 문장 간 논리와 글의 전개', 'paragraphs': [
        '각 문장을 고립해서 이해하면 변경 공지의 최종 행동을 놓치기 쉽다. 문제 제기 → 원인 → 조치 → 독자 행동의 순서를 간단히 표시한다. however는 앞 정보의 제한이나 반전을, therefore는 앞 근거에 따른 결과를, for example은 일반 설명을 구체화하는 사례를 연결한다. 연결어가 없어도 원인과 조치의 관계가 성립할 수 있다.',
        'The east entrance is being repaired. Visitors should use the gate beside the loading area. 두 번째 문장은 방문자에게 행동을 지시한다. 목적은 수리 사실의 단순 소개보다 출입 동선 안내에 가깝다. 뒤에 The loading area itself remains closed가 나오면 gate beside와 loading area를 같은 장소로 처리하지 않는다. 위치 수식어와 제한 조건을 함께 읽는다.'
    ]},
    {'title': '04 목적·세부 정보·추론의 근거 범위', 'paragraphs': [
        '목적 문제는 글 전체를 대표하는 행동을 찾는다. 이메일의 첫 요청과 마지막 마감 지시를 연결하면 소재에만 맞는 오답을 줄일 수 있다. 세부 정보 문제는 질문의 인물·날짜·장소를 찾은 뒤 exactly, only, before, unless처럼 범위를 제한하는 표현을 확인한다. 답과 근거의 표현이 달라도 행위와 조건이 같으면 연결된다.',
        '추론 문제는 직접 진술보다 한 단계 연결이 필요하지만 자유로운 상상은 허용하지 않는다. Only registered members may reserve a desk와 Mina reserved a desk가 함께 주어지면 Mina의 등록 상태를 추론할 수 있다. 반면 Mina의 근무지나 방문 횟수는 알 수 없다. must와 may, 확정과 계획, 요청과 실행을 구별하고 지문이 뒷받침하는 가장 약한 충분한 결론을 고른다.'
    ]},
    {'title': '05 NOT/EXCEPT에서 세 근거를 확인하는 법', 'paragraphs': [
        'NOT 또는 EXCEPT를 발견하면 질문 옆에 부정 표시를 한다. 보기마다 언급 여부를 확인하는 작은 표를 머릿속에 만들고 확인된 세 개를 제거한다. 지문과 비슷한 표현이 있다는 사실만으로 제거하지 말고, 실제 대상과 조건도 같은지 비교한다. 예약에 필요한 정보와 행사 당일 가져올 물건은 별개의 목록이다.',
        '예를 들어 신청 안내가 name, preferred session, dietary requirements를 요구하면 소속 회사가 필수라고 판단할 수 없다. 일반적으로 신청서에 회사명이 쓰인다는 상식은 근거가 되지 않는다. 질문이 NOT mentioned이면 부재를, NOT true이면 지문과의 모순 또는 성립하지 않는 내용을 확인한다. 이 차이를 검토하지 않으면 지문에 명시되지 않은 사실을 거짓이라고 단정하게 된다.'
    ]},
    {'title': '06 문맥상 의미와 지칭 대상', 'paragraphs': [
        '의미 문제에서는 해당 단어가 포함된 문장과 앞뒤 한 문장을 읽는다. Please hold the shipment until the address is confirmed에서 hold는 물건을 손으로 잡는 행동이 아니라 발송을 보류하는 행동이다. 대체 표현을 넣었을 때 목적어와 조건이 유지되는지 검증한다. 이 과정은 단어 뜻 목록을 암기하는 훈련이 아니라 문맥의 행동을 정확히 읽는 훈련이다.',
        '대명사는 수 일치만으로 결정하지 않는다. The sample labels were removed from the boxes because they contained outdated prices에서 they는 가격 정보를 담을 수 있는 labels를 가리킨다. 가까운 boxes만 보고 답을 정하면 안 된다. this나 that은 앞 명사 하나뿐 아니라 앞 문장의 사건 전체를 받을 수 있으므로 지시어에 실제 행동을 대입해 본다.'
    ]},
    {'title': '07 문장 삽입: 앞뒤 두 방향 연결', 'paragraphs': [
        '삽입 문장의 however, this change, these items, also와 같은 연결 단서를 먼저 표시한다. this change 앞에는 구체적 변경이 있어야 하고, these items 앞에는 복수 항목이 소개되어야 한다. 뒤 문장에서는 삽입 문장의 새 정보가 자연스럽게 이어지는지 본다. 같은 주제라는 이유만으로 위치를 정하지 않는다.',
        '예시: The workshop has moved to Room 204. [1] It now begins at 10:00 a.m. instead of 9:00 a.m. [2] These commuters should still register before Friday. [3] Please contact us with questions. [4] 삽입 문장 This later start will give commuters more time to arrive.는 [2]에 들어간다. 앞 문장의 9시에서 10시로 변경이 later start를 설명하고, 삽입 문장의 commuters가 뒤 문장 These commuters의 선행 대상이 된다. [1]에서는 변경 시간이 아직 없고 [3]·[4]에서는 These commuters가 선행 소개 없이 남는다. 실제 문제에서도 양옆의 연결을 모두 확인한다.'
    ]},
    {'title': '08 이중·삼중 지문: 동일 대상과 갱신 정보', 'paragraphs': [
        '문서를 읽으며 날짜, 주문 번호, 신청자 이름, 행사 이름을 연결 표식으로 삼는다. 광고의 일반 조건 → 신청 양식의 개인 선택 → 확인 이메일의 최종 배정처럼 각 문서의 기능을 나눈다. 두 문서에 등장하는 비슷한 가격이 같은 상품과 기간에 적용되는지 먼저 확인하고, 변경 이메일이 앞 문서의 어떤 항목을 갱신하는지 표시한다.',
        '연계 문제의 근거는 최소 두 문서에 나누어 존재한다. 일정표의 Tuesday session과 이메일의 cannot attend on Tuesday를 합치면 가능한 다른 회차를 찾을 수 있다. 이메일만으로 장소를 추정하거나 일정표만으로 참석 확정을 단정하지 않는다. 삼중 지문에서는 셋을 전부 사용해야 한다는 강박 없이, 질문에 필요한 문서 조합을 먼저 정한다.'
    ]},
    {'title': '09 장르별 정보의 위치', 'paragraphs': [
        '이메일·편지는 발신자, 수신자, 첫 용건, 마지막 행동 지시를 우선 확인한다. 광고는 제공 내용과 제외 조건을, 공지문은 적용 대상·변경 시점·대체 절차를, 기사는 사건의 배경·현재 조치·향후 계획을 구분한다. 계획된 조치를 완료 사실로 바꾸지 않는다. 일정표와 양식은 열 제목, 선택 표시, 단위와 날짜가 본문 문장만큼 중요하다.',
        '채팅은 발언자의 교체가 논리 연결 역할을 한다. I can take it from here의 의도는 앞에서 누구의 어떤 업무가 남아 있었는지와 뒤의 응답으로 결정한다. Could we move it?의 it도 직전 일정인지 파일인지 확인한다. 짧은 지문이라고 전체 흐름을 생략하지 않고, 장르에 따라 반복해서 나타나는 정보 위치를 익혀 탐색 시간을 줄인다.'
    ]},
    {'title': '10 읽는 순서·시간 배분·근거 복습', 'paragraphs': [
        '목적·추론·문장 삽입이 포함되거나 글이 짧고 논리적 변화가 많으면 처음부터 끝까지 흐름을 읽는 편이 안전하다. 장소·시간·금액처럼 위치가 분명한 세부 정보는 질문의 대상부터 파악하고 해당 부분을 찾은 뒤 주변 조건까지 읽는다. 복수 지문은 문서 제목과 관계를 먼저 확인하고, 연계 질문의 표식을 찾는다. 필요한 부분만 보다가 목적과 변경 사항을 놓치지 않는다.',
        '실전에서는 Part 7을 단일 지문과 복수 지문으로 나누어 진행 상황을 확인한다. 한 문제에서 근거를 찾지 못하면 임시 답을 표시하고 이동하며, 검토 때 모든 지문을 다시 읽기보다 불확실했던 조건을 확인한다. 개인 훈련은 정답률과 실제 소요 시간을 함께 기록해 배분을 조정한다. 각 문제 풀이 후 근거 한 문장, 보기의 바꿔 말하기, 틀린 보기의 오류 지점을 말로 설명하면 우연한 정답도 복습 대상으로 잡힌다.'
    ]},
]

data['training'].append(S('훈련 1 | 예약 변경 이메일', [D('Email: Harbor Workshop', '''To: Registered participants
From: Elise Park, Harbor Workshop Coordinator
Subject: Updated arrangements for the May 18 workshop

Thank you for registering for our product-photography workshop. We expected to use the studio on the second floor, but repairs to its ventilation system will not be completed before May 18. The workshop will therefore take place in the training room on the ground floor. Please enter through the courtyard gate; the front entrance is reserved for the repair crew.

The start time remains 9:30 a.m. We have extended the lunch break by fifteen minutes so that participants who wish to visit the nearby market can do so without missing the afternoon demonstration. A light lunch is included in the registration fee, although you are welcome to bring your own food.

Please bring a fully charged camera. We will provide lamps, backgrounds, and sample products, so there is no need to carry those items. If you require a parking space, reply to this message by May 14 with your vehicle registration number. Spaces are limited and will be assigned in the order requests are received. Your original workshop confirmation remains valid; a new registration is not necessary.''')], [
 Q('P7-01', 'Why was this email sent?', ['To request payment for repairs', 'To announce changes to workshop arrangements', 'To cancel a photography workshop', 'To introduce a new market tour'], 'B', '목적', '기본', 'Email: Harbor Workshop의 "will therefore take place in the training room"', '수리 때문에 방과 출입구가 바뀌었고 점심 및 준비물 안내가 이어진다. 취소가 아니라 기존 참가자에게 변경된 운영 정보를 전달한다.', '장소 변경과 참가 지침 전체를 포괄하는 B가 글의 목적이다.', {'A':'수리비 지불을 참가자에게 요청하는 문장이 없다.', 'C':'workshop will take place라고 개최를 확인한다.', 'D':'시장 방문은 점심 중 선택 사항이며 새 투어 소개가 아니다.'}),
 Q('P7-02', 'What should participants bring?', ['Sample products', 'Portable lamps', 'A camera with a charged battery', 'A replacement confirmation letter'], 'C', '세부 정보', '기본', 'Email: Harbor Workshop의 "bring a fully charged camera"', 'bring의 목적어는 camera이고 fully charged가 그 상태를 한정한다. 나머지 장비는 주최 측이 제공하며 기존 확인서는 유효하다.', '충전된 카메라를 가져오라는 직접 지시와 C가 일치한다.', {'A':'sample products는 제공 품목이다.', 'B':'lamps도 주최 측이 제공한다.', 'D':'새 등록이 필요 없으며 대체 확인서를 가져오라는 지시가 없다.'}),
 Q('P7-03', 'What is suggested about the parking spaces?', ['They are available to every participant automatically.', 'They are located inside the market.', 'They can be reserved after the workshop starts.', 'Earlier requests have an advantage.'], 'D', '추론', '중급', 'Email: Harbor Workshop의 "assigned in the order requests are received"', '공간 수가 제한되고 접수 순서대로 배정된다. 따라서 같은 조건에서 먼저 요청한 사람이 배정받는 데 유리하다.', '접수 순서가 우선순위라는 규칙을 바꿔 표현한 D가 타당하다.', {'A':'Spaces are limited이므로 자동 전원 배정이 아니다.', 'B':'주차 공간의 위치는 제시되지 않았다.', 'C':'신청 기한은 May 14이며 행사 시작 후 예약 근거는 없다.'}),
]))

data['training'].append(S('훈련 2 | 사무실 공지의 조건 읽기', [D('Notice: Riverside Offices', '''Temporary access arrangements

From June 3 through June 7, the west staircase at Riverside Offices will be closed while its handrails are replaced. [1] Employees who normally use that staircase should use the central stairs or the passenger elevator. The elevator will continue to serve all floors during normal business hours.

Deliveries of bulky furniture must be scheduled for the morning. The freight elevator will be available from 7:00 to 10:00 a.m., and a member of the facilities team must accompany each delivery. [2] Suppliers should send their expected arrival time and the dimensions of the largest item to facilities@riverside.example at least one working day in advance. This information will help the team determine whether additional assistance is necessary.

The bicycle storage area beside the west staircase will remain open, but its indoor doorway will be blocked. Cyclists should reach it from the garden path. [3] Please do not leave bicycles near the central stairs, as that route must be kept clear.

We expect to reopen the staircase on June 10 following a safety inspection. [4] An updated notice will be posted if the inspection results require further work.''')], [
 Q('P7-04', 'What is NOT mentioned as a requirement for furniture deliveries?', ['Payment of an access fee', 'A morning arrival time', 'Advance notification', 'A facilities team escort'], 'A', 'NOT/EXCEPT', '중급', 'Notice: Riverside Offices의 "morning", "at least one working day in advance", "must accompany"', '본문은 오전 배송, 하루 전 정보 전달, 시설팀 동행을 요구한다. 요금 지불은 어떤 문장에도 요구되지 않는다.', '언급된 세 조건을 제거하면 출입 요금인 A만 남는다.', {'B':'첫 문장에서 must be scheduled for the morning이라고 명시한다.', 'C':'공급업체는 적어도 하루 전 도착 정보를 보내야 한다.', 'D':'시설팀 직원이 각 배송에 동행해야 한다.'}),
 Q('P7-05', 'What does "This information" refer to?', ['The elevator operating hours', 'The arrival time and item dimensions', 'The safety inspection results', 'The number of stored bicycles'], 'B', '지칭', '중급', 'Notice: Riverside Offices의 "their expected arrival time and the dimensions"', 'This information은 직전 문장에서 제출하라고 한 두 정보를 받는다. 그 정보로 추가 도움이 필요한지 판단한다는 뒤 문장도 크기·도착 정보와 연결된다.', '예상 도착 시각과 최대 물품 치수를 함께 제시한 B가 선행 내용이다.', {'A':'운영 시간은 업체가 제출하는 정보가 아니다.', 'C':'검사 결과는 마지막 문단에서 나중에 소개된다.', 'D':'자전거 수량 제출은 요구되지 않았다.'}),
 Q('P7-06', 'Where does the following sentence best belong? "This outdoor route will be marked with temporary signs."', ['[1]', '[2]', '[3]', '[4]'], 'C', '문장 삽입', '고급', 'Notice: Riverside Offices의 "reach it from the garden path"와 [3]', 'This outdoor route는 garden path라는 외부 접근로를 받는다. [3] 뒤의 자전거 주차 금지 지침도 같은 이용자에게 이어지는 안내다.', '정원 길을 소개한 직후인 [3]에 삽입해야 선행 대상과 안내 흐름이 모두 맞는다.', {'A':'[1] 앞에는 계단 폐쇄만 있고 외부 경로가 소개되지 않았다.', 'B':'[2] 앞의 화물 엘리베이터와 동행 조건은 outdoor route가 아니다.', 'D':'[4] 앞의 재개방·검사는 야외 경로 소개와 연결되지 않는다.'}),
]))

data['training'].append(S('훈련 3 | 기사에서 현재와 계획 구분', [D('Article: Linden Library', '''Linden Library Tests a New Collection Service

Linden Library has begun a three-month trial allowing readers to collect reserved books from lockers outside its main building. The service was developed after a survey showed that many members could not visit during the library's regular opening hours. Members can request locker collection through their online accounts at no extra charge.

Library employees place each order in a locker and send the member an access code. The code remains active for forty-eight hours. If the order has not been collected by then, the books are returned to the indoor reservation shelf and can be collected during opening hours for another five days. Staff will not automatically generate a second locker code.

The trial uses twelve lockers, including two large compartments intended for oversized books. During its first week, the service handled eighty-three orders. Library director Helen Ross said that the figure was encouraging but too early to establish a lasting pattern.

The library will collect feedback throughout the trial and review the results in September. If demand remains strong, it may add lockers at the north branch next year. There are currently no plans to use the lockers for returning books; the existing return slot beside the main entrance will remain available.''')], [
 Q('P7-07', 'Why did the library introduce the collection service?', ['To reduce its collection of large books', 'To allow members to return books electronically', 'To help readers who cannot visit during opening hours', 'To replace all indoor reservation shelves'], 'C', '목적', '기본', 'Article: Linden Library의 "could not visit during"와 "regular opening hours"', '조사에서 이용 시간의 어려움이 확인되어 외부 보관함 수령을 도입했다. 수령과 반납은 구분된다.', '개관 시간에 방문하기 어려운 독자를 돕는다는 C가 도입 이유와 일치한다.', {'A':'대형 칸은 큰 책 수령용이지 장서 축소 목적이 아니다.', 'B':'반납 보관함 계획은 없고 전자 반납도 언급되지 않는다.', 'D':'실내 예약 선반은 미수령 도서를 보관하는 데 계속 사용된다.'}),
 Q('P7-08', 'What happens when a locker access code expires?', ['The books are moved to an indoor shelf.', 'The membership is suspended.', 'A new code is sent automatically.', 'The order is transferred to the north branch.'], 'A', '세부 정보', '중급', 'Article: Linden Library의 "returned to the indoor reservation shelf"', 'forty-eight hours 후 미수령 주문은 실내 선반으로 이동하고 5일 더 수령할 수 있다. 자동 재발급은 명시적으로 부정된다.', '코드 만료 뒤 도서의 위치 변화가 A에 정확히 반영된다.', {'B':'회원 정지라는 조치는 제시되지 않았다.', 'C':'will not automatically generate라고 반대 사실을 명시한다.', 'D':'북부 지점 추가 설치는 향후 가능성일 뿐 주문 이전이 아니다.'}),
 Q('P7-09', 'What can be inferred about the north branch?', ['It already operates twelve collection lockers.', 'It will certainly close next year.', 'It accepts all book returns through lockers.', 'Its participation in the service has not been decided.'], 'D', '추론', '고급', 'Article: Linden Library의 "If demand remains strong, it may add lockers"', '조건절과 may가 설치를 수요에 달린 가능성으로 표현한다. 현재 시행되는 본관 시험과 북부 지점의 장래 검토를 나눈다.', '아직 확정되지 않은 확대 계획이라는 D가 조건부 진술의 범위를 지킨다.', {'A':'12개는 현재 본관 시험 수량이다.', 'B':'지점 폐쇄는 언급되지 않는다.', 'C':'보관함 반납 계획 자체가 없다고 한다.'}),
]))

data['training'].append(S('훈련 4 | 채팅의 간접 의도', [D('Chat: Exhibit Team', '''9:05 Mina: The display panels arrived, but two stands are missing. Has the supplier confirmed when they will come?
9:07 Joel: They can deliver the stands tomorrow morning. Our installation is scheduled for this afternoon, though.
9:09 Mina: We cannot leave the panels leaning against the walls overnight. Could we borrow stands from the training room?
9:11 Joel: I checked. That room needs all of its stands for a seminar today.
9:13 Priya: We still have four spare stands in the basement store. I can bring them upstairs before noon.
9:15 Mina: That would keep us on schedule. Please use the service elevator; the visitor elevator is too small for them.
9:17 Joel: I will let the supplier know we can accept tomorrow's delivery. We can replace the borrowed stands after the installation.
9:19 Priya: Fine. I'll return our spare stands to the basement once the new ones are fitted.''')], [
 Q('P7-10', 'What problem is the team discussing?', ['A cancelled visitor seminar', 'Missing equipment needed for an installation', 'A damaged service elevator', 'An incorrect exhibition date'], 'B', '목적', '기본', 'Chat: Exhibit Team의 "two stands are missing"와 "installation ... this afternoon"', '패널을 설치할 받침대가 부족하지만 공급업체 배송은 다음 날이다. 대화는 오늘 설치를 유지할 대안을 찾는 흐름이다.', '설치에 필요한 장비 누락을 해결하는 대화라는 B가 중심 상황이다.', {'A':'세미나는 취소되지 않았고 받침대를 사용 중이다.', 'C':'서비스 엘리베이터 고장은 없으며 오히려 사용하라고 한다.', 'D':'전시 날짜 오류는 언급되지 않는다.'}),
 Q('P7-11', 'What does Mina mean when she writes, "That would keep us on schedule"?', ['Priya’s offer will allow the installation to proceed as planned.', 'The supplier must deliver the panels again.', 'The seminar should end before noon.', 'The team should postpone tomorrow’s delivery.'], 'A', '대화 의도', '중급', 'Chat: Exhibit Team의 "bring them upstairs before noon"와 "keep us on schedule"', 'That은 Priya가 지하 예비 받침대를 정오 전 가져오는 제안을 받는다. 오늘 오후 설치를 유지할 수 있다는 의미다.', '직전 제안이 당일 설치 일정 문제를 해결한다는 A가 발언 의도다.', {'B':'패널은 이미 도착했고 재배송 요구가 아니다.', 'C':'세미나 종료 시각을 바꾸는 제안이 없다.', 'D':'다음 날 배송은 그대로 수락할 계획이다.'}),
 Q('P7-12', 'What will Priya most likely do after the new stands are fitted?', ['Move the seminar to the basement', 'Cancel the supplier’s invoice', 'Return the spare stands to storage', 'Use the visitor elevator for the panels'], 'C', '세부 정보', '중급', 'Chat: Exhibit Team의 "return our spare stands to the basement"', 'once절은 새 받침대 설치가 끝난 뒤의 시점을 표시한다. 돌려놓는 대상은 빌려 쓴 예비 받침대다.', '지하 보관 공간으로 예비 받침대를 반환하는 C가 마지막 발언의 약속이다.', {'A':'세미나 장소 변경은 언급되지 않았다.', 'B':'청구서 취소는 대화에 없다.', 'D':'방문자 엘리베이터는 크기가 부족하다고 명시한다.'}),
]))

data['training'].append(S('훈련 5 | 광고와 예약 이메일 연계', [D('Advertisement: Oakfield Meeting Rooms', '''Oakfield Meeting Rooms
Flexible space for your next team event

Our Cedar Room seats up to twenty-four people in a classroom arrangement and includes a projector, wireless internet, and two whiteboards. The Birch Room seats up to sixteen and has the same standard equipment. Rooms may be booked for a morning session, from 9:00 a.m. to noon, or an afternoon session, from 1:00 to 5:00 p.m. A full-day reservation combines both sessions and includes access during the lunch break.

The Cedar Room costs $180 per session; the Birch Room costs $120. A full-day reservation receives a ten-percent reduction on the combined session price. Coffee and tea are included. Lunch can be ordered separately for $18 per person and must be requested at least three working days before the event. Outside catering is permitted, but a $25 cleaning charge applies.

Bookings are confirmed only after a deposit equal to half the room charge has been received. The balance is due on the event date. Changes to the participant count do not affect the room charge, provided the room capacity is not exceeded. Contact our booking team if your event requires additional equipment.'''), D('Email: Oakfield Booking Request', '''To: Oakfield booking team
From: Noah Lim, Bridgewell Design
Subject: July 12 reservation

I would like to reserve a room for our twenty-person planning meeting on July 12. We will need access from 9:00 a.m. until 5:00 p.m., including the lunch break, because we plan to leave our materials set up between sessions. We will use the standard projector and whiteboards. Please confirm that no extra equipment charge will apply.

Our office kitchen will prepare sandwiches, which a colleague will deliver at 11:45 a.m. We therefore do not need your lunch service. Once you send the room-charge total and deposit instructions, our accounts team will arrange payment. There is a chance that two more colleagues will attend, but the total will not exceed twenty-two. Please let me know whether that would require a different room or a revised room charge.''')], [
 Q('P7-13', 'Which room meets Mr. Lim’s needs?', ['The Birch Room for one morning', 'The Cedar Room for a full day', 'The Birch Room for a full day', 'The Cedar Room for one afternoon'], 'B', '복수 지문 연계', '고급', 'Advertisement: Oakfield Meeting Rooms의 "Cedar Room seats up to twenty-four"; Email: Oakfield Booking Request의 "twenty-person"와 "9:00 a.m. until 5:00 p.m."', '예약자는 20명에 점심을 포함한 종일 사용을 원한다. 광고에서 수용 인원 24명인 Cedar와 점심 시간 접근을 포함하는 full-day를 결합한다.', 'Cedar 종일 예약만 인원과 사용 시간 두 조건을 모두 충족한다.', {'A':'Birch의 최대 16명과 오전만의 사용이 둘 다 부족하다.', 'C':'종일 시간은 맞지만 Birch는 20명을 수용하지 못한다.', 'D':'Cedar 인원은 맞지만 오후만으로 오전 이용을 충족하지 못한다.'}),
 Q('P7-14', 'What room-charge total should be quoted, excluding the cleaning charge?', ['$180', '$216', '$300', '$324'], 'D', '복수 지문 연계', '고급', 'Advertisement: Oakfield Meeting Rooms의 "$180 per session"와 "ten-percent reduction"; Email: Oakfield Booking Request의 "9:00 a.m. until 5:00 p.m."', 'Cedar 두 회차 합계는 180 × 2 = 360달러다. 종일 예약의 10% 감액 36달러를 빼면 객실 요금은 324달러다.', '종일 감액을 정확히 적용한 324달러가 D다.', {'A':'180달러는 Cedar 한 회차 가격이다.', 'B':'216달러는 Birch 종일 가격이며 인원 조건이 맞지 않는다.', 'C':'300달러가 되는 요금 규칙은 광고에 없다.'}),
 Q('P7-15', 'Why will a cleaning charge apply?', ['The group will use outside catering.', 'The group requested two whiteboards.', 'The event will exceed room capacity.', 'The deposit will be paid late.'], 'A', '복수 지문 연계', '중급', 'Advertisement: Oakfield Meeting Rooms의 "Outside catering is permitted"와 "a $25 cleaning charge applies"; Email: Oakfield Booking Request의 "Our office kitchen will prepare sandwiches"', '회사 주방 음식이 회의장으로 배달되므로 외부 제공 음식에 해당한다. 광고의 외부 케이터링 청소비 규칙을 이 예약에 적용한다.', '외부 음식 반입이라는 요금 적용 이유가 A다.', {'B':'화이트보드는 기본 제공 장비이므로 청소비 이유가 아니다.', 'C':'최대 22명은 Cedar의 24명 한도를 넘지 않는다.', 'D':'지연 납부는 언급되지 않았고 청소비 조건도 아니다.'}),
 Q('P7-16', 'What must happen before the booking is confirmed?', ['The participant list must be printed.', 'The meeting must begin.', 'A deposit must be received.', 'The lunch menu must be approved.'], 'C', '세부 정보', '기본', 'Advertisement: Oakfield Meeting Rooms의 "only after a deposit"와 "has been received"', 'only after는 확정 전 필요한 조건을 표시한다. 보증금은 객실 요금 절반이며 잔금 납부일과 구분된다.', '보증금 수령이 선행되어야 한다는 C가 명시된 확정 조건이다.', {'A':'참가자 목록 인쇄는 요구되지 않는다.', 'B':'행사 시작이 예약 확정 조건일 수 없으며 글에도 없다.', 'D':'주최 측 점심을 주문하지 않으므로 메뉴 승인 근거가 없다.'}),
 Q('P7-17', 'What is suggested about adding two colleagues?', ['It would make lunch service compulsory.', 'It would not change the Cedar Room charge.', 'It would require an afternoon-only booking.', 'It would remove the full-day reduction.'], 'B', '복수 지문 연계', '고급', 'Advertisement: Oakfield Meeting Rooms의 "do not affect the room charge"와 "capacity is not exceeded"; Email: Oakfield Booking Request의 "will not exceed twenty-two"', 'Cedar 한도는 24명이고 변경 후 인원은 최대 22명이다. 따라서 인원 변경이 객실 요금을 바꾸지 않는 조건이 계속 충족된다.', '추가 두 명으로도 한도 이내이므로 B가 성립한다.', {'A':'인원 증가와 점심 주문 의무는 연결되지 않는다.', 'C':'인원 변화는 오전 이용을 제거하지 않는다.', 'D':'종일 감액은 예약 시간에 대한 규칙이며 인원 증가로 취소되지 않는다.'}),
]))

data['training'].append(S('훈련 6 | 삼중 지문의 마감·배정 연결', [D('Notice: City Market Stalls', '''City Market: August 24 Vendor Information

The city market will run from 10:00 a.m. to 4:00 p.m. on August 24 in Wellington Square. Standard stalls measure three meters by two meters and cost $45. Corner stalls measure three meters by three meters and cost $65. Electricity is available only at corner stalls and must be requested on the application form. Vendors must supply their own tables and extension cables.

Applications received by August 5 will be considered in the first allocation round. Later applications will be placed on a waiting list. The organizers will email stall assignments on August 8, and payment is due by August 12. Unpaid assignments will then be offered to vendors on the waiting list.

Vehicles may enter the square between 8:00 and 9:30 a.m. for unloading. They must leave before customers are admitted. During market hours, parking is available at the public garage on King Street. Vendors may return with vehicles for loading after 4:15 p.m. Please keep all products within your assigned stall boundary.'''), D('Application: Maren Ceramics', '''Vendor: Maren Ceramics
Contact: Sofia Hale
Application received: August 4
Products: Handmade cups and small planters
Requested stall: Corner
Electricity required: Yes
Additional notes: We will demonstrate a small electric pottery wheel. Our table measures two meters by one meter. We will bring a suitable extension cable and two display racks. We prefer a stall near a water point, if one is available. Our assistant will help unload equipment but will not stay for the entire event.'''), D('Email: Market Assignment', '''To: Sofia Hale
From: City Market Office
Date: August 8
Subject: Your stall assignment

We are pleased to offer Maren Ceramics corner stall C7. It is beside the fountain and has an electrical socket on the rear post. Please keep the cable inside the stall boundary so that it does not cross the public walkway.

Your payment must reach us by the date specified in the vendor notice. If you decide not to accept the assignment, please notify us promptly so another vendor can use it. Staff will be at the square from 8:00 a.m. to direct unloading vehicles. A printed copy of this message will help them identify your stall.''')], [
 Q('P7-18', 'Why was Maren Ceramics eligible for the first allocation round?', ['Its application arrived before the deadline.', 'It had already paid for two stalls.', 'Its assistant would work all day.', 'It had participated in the market before.'], 'A', '복수 지문 연계', '고급', 'Notice: City Market Stalls의 "by August 5"; Application: Maren Ceramics의 "received: August 4"', '첫 배정 심사는 8월 5일까지 접수된 신청서에 적용되고 Maren은 8월 4일 접수되었다. 전기나 과거 참여 여부가 이 자격의 기준은 아니다.', '마감 이전 접수라는 두 문서의 날짜 관계가 A를 뒷받침한다.', {'B':'두 자리 예약이나 사전 납부는 명시되지 않았다.', 'C':'보조자는 하루 종일 머무르지 않는다고 한다.', 'D':'과거 참가 경험은 제시되지 않았다.'}),
 Q('P7-19', 'How much must Ms. Hale pay for the assigned stall?', ['$45', '$50', '$65', '$110'], 'C', '복수 지문 연계', '중급', 'Notice: City Market Stalls의 "cost $65"; Email: Market Assignment의 "corner stall C7"', '최종 배정 이메일이 C7을 corner stall로 지정한다. 해당 유형의 공지 요금을 적용하면 65달러다.', '배정 유형과 요금표를 연결한 C가 정답이다.', {'A':'45달러는 standard stall 가격이다.', 'B':'50달러 요금은 안내에 없다.', 'D':'110달러는 두 유형 가격 합계이나 한 자리만 배정되었다.'}),
 Q('P7-20', 'What must Ms. Hale do by August 12?', ['Finish selling all of her products', 'Submit a second application', 'Move her table to King Street', 'Ensure that the payment reaches the organizers'], 'D', '복수 지문 연계', '고급', 'Notice: City Market Stalls의 "payment is due by August 12"; Email: Market Assignment의 "must reach us by the date specified"', '이메일은 납부 마감 날짜를 공지로 되돌려 연결한다. 공지에서 그 날짜는 8월 12일이며 송금 실행만 아니라 도착이 요구된다.', '납부금이 주최 측에 도달해야 한다는 D가 날짜와 행동을 모두 맞춘다.', {'A':'판매 행사는 8월 24일이다.', 'B':'새 신청서 제출 요구는 없다.', 'C':'King Street는 차량 주차장 위치이며 판매 테이블 이동 장소가 아니다.'}),
 Q('P7-21', 'Which request in the application appears to have been accommodated?', ['An assistant’s full-day admission', 'A location near water', 'A table supplied by the organizers', 'Two separate unloading periods before opening'], 'B', '복수 지문 연계', '고급', 'Application: Maren Ceramics의 "near a water point"; Email: Market Assignment의 "beside the fountain"', '신청서의 물 가까운 위치 선호와 배정 이메일의 분수 옆 위치를 연결한다. 수돗물 사용 가능 여부까지는 주장하지 않는다.', '물 주변 위치라는 범위에서 B가 수용된 요청으로 판단된다.', {'A':'보조자 종일 입장 요청은 신청서에 없다.', 'C':'테이블은 업체가 직접 준비해야 한다.', 'D':'개장 전 하역 시간은 한 구간으로 안내되며 별도 두 구간 요청이 없다.'}),
 Q('P7-22', 'What should Ms. Hale bring to help staff locate her stall?', ['A photograph of her pottery wheel', 'A parking ticket', 'A printed copy of the assignment email', 'An extra application fee'], 'C', '세부 정보', '기본', 'Email: Market Assignment의 "A printed copy of this message"', 'this message는 현재 배정 이메일이며 출력본이 직원의 자리 확인을 돕는다고 명시한다.', '배정 이메일 출력본이라는 C가 마지막 안내의 대상이다.', {'A':'물레 사진은 요청하지 않는다.', 'B':'주차권이 자리 확인에 필요하다는 근거가 없다.', 'D':'추가 신청 수수료는 안내에 없다.'}),
]))

data['mock'].append(S('실전 단일 지문 1 | 배송 조정 이메일', [D('Email: Calton Supplies', '''To: Grace Wu, Westbridge Studio
From: Daniel Ames, Calton Supplies
Date: March 6
Subject: Order WS-418

Thank you for your order of twelve adjustable desk lamps. Ten are ready to leave our warehouse today, but the remaining two are awaiting a replacement component. We expect the component to arrive on March 9, and the two lamps should then be ready for shipment on March 10.

We can send the ten available lamps now and ship the others separately, with no additional delivery charge. Alternatively, we can hold the entire order and send all twelve together on March 10. Please let us know which arrangement you prefer by 2:00 p.m. today. If we do not hear from you, we will use the first option because your order notes indicated that the lamps were needed for a studio opening.

Your existing invoice remains correct. It already includes the discount agreed upon when you placed the order, so no revised invoice is required for a split shipment. I have attached the tracking instructions that apply to either arrangement. The tracking link will become active after the first parcel leaves our warehouse. Thank you for your patience while we complete the order.''')], [
 Q('147', 'What is the main purpose of the email?', ['To request an increase in the order quantity', 'To explain delivery options for an incomplete order', 'To offer a new discount on desk lamps', 'To confirm that all items have already been delivered'], 'B', '목적', '중급', 'Email: Calton Supplies의 "send the ten available lamps now"와 "all twelve together"', '12개 중 10개만 준비되어 두 가지 발송 방안을 제시하고 당일 응답을 요청한다. 할인은 기존 내용의 확인이다.', '부분 준비된 주문의 배송 선택지를 설명하는 B가 전체 용건이다.', {'A':'수량 증가 요청은 없고 원래 12개를 완성하려 한다.', 'C':'할인은 주문 시 합의된 기존 할인이며 새로운 제안이 아니다.', 'D':'두 개는 아직 준비되지 않았고 배송 완료도 아니다.'}),
 Q('148', 'What will the supplier do if Ms. Wu does not reply by 2:00 p.m.?', ['Cancel the twelve-lamp order', 'Wait until all lamps are ready', 'Issue an additional shipping invoice', 'Send the ten available lamps first'], 'D', '세부 정보', '중급', 'Email: Calton Supplies의 "we will use the first option"', '첫 번째 옵션은 준비된 10개를 지금 발송하고 두 개를 나중에 별도 발송하는 것이다. 무응답 조건이 이 옵션을 선택하게 한다.', '대명사적 표현 first option을 앞 문장과 연결한 D가 기본 조치다.', {'A':'무응답 때 취소한다는 규칙은 없다.', 'B':'전체를 기다리는 것은 second option이다.', 'C':'별도 배송에도 추가 배송 요금이 없다고 한다.'}),
]))

data['mock'].append(S('실전 단일 지문 2 | 고객에게 보내는 편지', [D('Letter: Ellery Theater', '''Dear Ms. Baker,

Thank you for contacting Ellery Theater about your tickets for the April 16 evening performance. I understand that the change in the performance time makes it difficult for you to attend. The production team moved the start from 7:30 p.m. to 6:00 p.m. to accommodate an additional afternoon rehearsal.

Because this adjustment was announced after your purchase, we can exchange your two tickets for any performance of the same production during April, subject to seat availability. We will waive the usual exchange fee. If the new seats are in a higher-priced section, however, you will need to pay the difference. A move to a lower-priced section will result in a credit to your theater account.

If you prefer a refund, please return the original tickets to the box office by April 12. A photograph or digital copy cannot be accepted for this procedure. The refund will be issued to the card used for the original purchase within five working days of receipt.

Our box office is open from noon to 6:00 p.m. Tuesday through Saturday. Please contact me if you would like me to check availability for another date before you decide.

Sincerely,
Marco Ellis
Customer Services Manager''')], [
 Q('149', 'Why is Mr. Ellis offering an exchange without the usual fee?', ['The theater changed the starting time after the purchase.', 'Ms. Baker bought tickets for a cancelled production.', 'The theater sold more seats than it could provide.', 'Ms. Baker is a member of the production team.'], 'A', '세부 정보', '중급', 'Letter: Ellery Theater의 "adjustment was announced after your purchase"', 'Because절이 무료 교환의 이유를 직접 제시한다. 공연은 취소되지 않고 시작 시각이 앞당겨졌다.', '구매 후 시간 변경이라는 A가 요금 면제의 명시된 이유다.', {'B':'공연 취소가 아니라 7:30에서 6:00으로 시각 조정이다.', 'C':'초과 판매 사실은 없다.', 'D':'수신자가 제작팀 구성원이라는 근거가 없다.'}),
 Q('150', 'What is required for Ms. Baker to receive a refund?', ['Selecting seats in a higher-priced section', 'Sending a digital copy of the tickets', 'Returning the original tickets by April 12', 'Visiting the box office on a Monday'], 'C', '세부 정보', '기본', 'Letter: Ellery Theater의 "return the original tickets ... by April 12"', '환불 절차는 원본과 기한을 요구한다. 디지털 사본 불가라는 다음 문장이 이 조건을 강화한다.', '원본 반환과 4월 12일 마감을 모두 유지한 C가 맞다.', {'A':'비싼 좌석 선택은 교환의 추가금 조건이다.', 'B':'digital copy cannot be accepted라고 명시한다.', 'D':'매표소는 화요일부터 토요일까지 운영한다.'}),
]))

data['mock'].append(S('실전 단일 지문 3 | 서비스 광고', [D('Advertisement: Meridian Print', '''Meridian Print: A Practical Plan for Small Offices

Our Office Care plan is designed for businesses that want predictable costs for maintaining their printers. For a monthly fee of $35 per printer, the plan covers an annual inspection, replacement of worn rollers, and telephone support during weekday business hours. Ink cartridges, paper, and damage caused by improper use are not covered.

Customers can enroll printers from any manufacturer, provided the equipment is less than six years old. Before enrollment, one of our technicians will inspect each printer free of charge. Equipment that requires major repairs must be repaired before it can enter the plan; customers will receive a separate estimate for that work.

Enrollment remains open throughout the year, and contracts run for twelve months from the first day of the following month. The plan can be transferred to another eligible printer if a customer replaces the original equipment during the contract period. There is no transfer fee, but the replacement printer must pass the initial inspection.

For offices with five or more enrolled printers, Meridian Print provides a single consolidated invoice. This simplifies administration without changing the monthly rate. To arrange an inspection, complete the request form on our website or call our service desk.''')], [
 Q('151', 'What is NOT included in the Office Care plan?', ['An annual inspection', 'Replacement of worn rollers', 'Weekday telephone support', 'Ink cartridges'], 'D', 'NOT/EXCEPT', '중급', 'Advertisement: Meridian Print의 "Ink cartridges ... are not covered"', '첫 문단은 포함되는 세 서비스와 제외되는 소모품·오용 손상을 구분한다. 선택지 세 개는 모두 포함 항목이다.', '명시적으로 제외된 잉크 카트리지를 제시한 D가 정답이다.', {'A':'annual inspection은 covers 뒤 포함 목록에 있다.', 'B':'worn rollers의 교체도 포함된다.', 'C':'weekday business hours의 전화 지원도 포함된다.'}),
 Q('152', 'What can be inferred about a four-year-old printer from another manufacturer?', ['It qualifies without any inspection.', 'It may enter the plan if it passes the required inspection and needs no major repairs.', 'It can be enrolled only when five other printers are enrolled.', 'Its monthly fee will be lower than $35.'], 'B', '추론', '고급', 'Advertisement: Meridian Print의 "any manufacturer", "less than six years old", "Before enrollment ... inspect"', '타사 제품과 4년 사용이라는 조건은 허용 범위다. 다만 가입 전 검사 및 큰 수리 해결 조건은 그대로 적용된다.', '제조사·연식·검사 조건을 모두 보존한 조건부 진술 B가 가능하다.', {'A':'모든 장비는 사전 검사 대상이다.', 'C':'5대 조건은 통합 청구서에만 적용되며 가입 최소 수량이 아니다.', 'D':'대수와 관계없이 월 요금은 바뀌지 않는다고 한다.'}),
]))

data['mock'].append(S('실전 단일 지문 4 | 반품 절차 공지', [D('Notice: Norland Returns', '''New Procedure for Returning Office Equipment

Beginning September 2, Norland Supplies will process returns through its online customer portal. [1] This change applies to equipment purchased directly from Norland; products bought through independent retailers must be returned to those retailers instead.

To begin a return, enter your invoice number and select the relevant item in the portal. You will then be asked to describe the reason for the return and upload a photograph if the item is damaged. [2] A service representative will review the request and send a return authorization number, usually within two working days. Please wait for that number before sending any equipment.

Customers should retain the original packaging until their request has been reviewed. [3] If the packaging is unavailable, the representative will advise on a suitable alternative. Items must be packed securely to prevent damage during transport. An authorization number approves the shipment for inspection; it does not guarantee a refund.

After the equipment arrives, a technician will examine it and contact the customer with the result. [4] Refunds for approved returns will be issued to the original payment method. Our support desk can assist customers who cannot access the portal.''')], [
 Q('153', 'What is the purpose of the notice?', ['To explain how customers should request equipment returns', 'To advertise discounted office equipment', 'To announce the closure of independent retailers', 'To require customers to replace all old packaging'], 'A', '목적', '기본', 'Notice: Norland Returns의 "process returns through its online customer portal"', '공지의 중심은 새 반품 접수와 승인·검사·환불 순서다. 대상 및 예외 조건을 함께 설명한다.', '온라인 반품 요청 절차를 설명하는 A가 글 전체를 포괄한다.', {'B':'가격 할인 광고가 아니다.', 'C':'판매점 폐쇄 내용은 없고 해당 판매점 반품을 안내한다.', 'D':'원래 포장 보관을 권하며 대체 포장도 허용한다.'}),
 Q('154', 'The word "retain" is closest in meaning to', ['purchase', 'deliver', 'keep', 'repair'], 'C', '문맥상 의미', '중급', 'Notice: Norland Returns의 "retain the original packaging until ... reviewed"', 'until절이 포장을 검토 때까지 갖고 있어야 하는 기간을 한정한다. 뒤 문장의 unavailable일 때 대안 안내도 보관의 의미와 연결된다.', '원래 포장을 계속 가지고 있다는 keep이 문맥상 적절하다.', {'A':'이미 원래 포장을 갖고 있는 상황이며 새 구매가 아니다.', 'B':'승인 전 장비를 보내지 말라고 하므로 포장 배송을 뜻하지 않는다.', 'D':'손상된 장비 검사는 기술자가 하며 포장 수리가 아니다.'}),
 Q('155', 'Where does the following sentence best belong? "The next step depends on what the technician finds."', ['[1]', '[2]', '[3]', '[4]'], 'D', '문장 삽입', '고급', 'Notice: Norland Returns의 "a technician will examine it"와 [4]', 'the technician은 직전 도입된 검사자를 받고, 다음 문장은 승인 반품의 환불 방법을 제시한다. 검사 결과가 후속 조치를 좌우하는 흐름이다.', '기술자 검사 뒤이며 환불 안내 앞인 [4]가 양쪽 연결을 충족한다.', {'A':'기술자가 아직 소개되지 않았고 온라인 접수 설명이 이어진다.', 'B':'사진 제출 단계에는 기술자의 검사 결과가 아직 없다.', 'C':'포장 보관 안내 사이에 검사 결과를 넣으면 절차 순서가 끊긴다.'}),
]))

data['mock'].append(S('실전 단일 지문 5 | 지역 기업 기사', [D('Article: Brindle Foods', '''Brindle Foods Extends Reusable-Container Trial

Brindle Foods will continue its reusable lunch-container trial for another six months after reporting a strong response from customers at its two downtown shops. Since January, customers have been able to borrow a container by paying a $4 deposit and recover the deposit when they return it to either participating shop. No purchase is required at the time of return.

The company originally intended to assess the project in April. However, a temporary closure of one shop in February reduced the amount of data available. Managing director Ravi Desai said that an extended trial would provide a more reliable picture of how frequently containers were reused.

Staff clean and inspect returned containers before placing them back into circulation. Containers with damaged lids are removed, even if their lower sections remain usable. Customers are asked to return all parts together, although a missing lid does not prevent them from receiving their deposit back.

The company plans to publish the trial results in October. It has not yet decided whether to introduce the scheme at its suburban shops. Desai noted that those locations have different patterns of customer visits, and the company would need to consider those differences before expanding the program.''')], [
 Q('156', 'Why is the company extending the trial?', ['To avoid returning customer deposits', 'To gather more reliable information', 'To introduce a higher lunch price', 'To replace all suburban shop employees'], 'B', '세부 정보', '중급', 'Article: Brindle Foods의 "provide a more reliable picture"', '2월 한 점포의 임시 폐점으로 데이터가 줄었다. 기간 연장은 재사용 빈도를 더 신뢰할 만하게 평가하기 위한 조치다.', '정보의 충분성과 신뢰도를 보완한다는 B가 직접 설명된 이유다.', {'A':'보증금 반환 중단은 없고 반환 조건을 계속 안내한다.', 'C':'식사 가격 인상은 언급되지 않는다.', 'D':'직원 교체 계획은 없다.'}),
 Q('157', 'What happens to a container with a damaged lid?', ['It is removed from circulation.', 'It is sold to the customer.', 'It is accepted only with a new purchase.', 'It is immediately sent to a suburban shop.'], 'A', '세부 정보', '기본', 'Article: Brindle Foods의 "Containers with damaged lids are removed"', '뚜껑 손상이 있으면 아래 부분이 쓸 만해도 사용 순환에서 제외한다. 고객 보증금 지급과 회사의 용기 재사용은 별개 조건이다.', '재사용 대상에서 제거한다는 A가 명시된 처리다.', {'B':'고객에게 판매한다는 내용은 없다.', 'C':'반환 때 구매는 필요 없다고 한다.', 'D':'교외 도입은 아직 결정되지 않았고 손상품 이전도 없다.'}),
 Q('158', 'What is suggested about the suburban shops?', ['They have refused to accept any returns.', 'They are closing permanently in October.', 'They may require a separate assessment before joining the program.', 'They currently use more containers than the downtown shops.'], 'C', '추론', '고급', 'Article: Brindle Foods의 "different patterns of customer visits"와 "consider those differences"', '교외 점포의 고객 방문 양상이 달라 확대 전 차이를 고려해야 한다. 아직 도입 여부도 미정이다.', '별도 특성 평가가 필요할 수 있다는 C는 문장의 제한적 계획을 보존한다.', {'A':'참여 여부 미정이지 반환 거부 사실이 아니다.', 'B':'10월은 결과 발표 시점이며 영구 폐점 시점이 아니다.', 'D':'현재 교외 사용량을 비교하는 수치는 없다.'}),
]))

data['mock'].append(S('실전 단일 지문 6 | 일정표와 조건', [D('Schedule: Easton Skills Center', '''Easton Skills Center: Thursday, November 14

Room 1
9:00-10:30: Budget Planning Basics, instructor Ada Mills
11:00-12:30: Spreadsheet Reporting, instructor Leon Grant
2:00-4:00: Project Review Clinic, instructor Ada Mills

Room 2
9:30-11:00: Workplace Presentations, instructor Nia Cole
11:30-1:00: Meeting Facilitation, instructor Nia Cole
2:00-3:30: Customer Feedback Analysis, instructor Leon Grant

Participation notes
All morning sessions require advance registration. Afternoon sessions accept walk-in participants if seats remain, but registered participants have priority. Please arrive ten minutes before your session. The reception desk will check registration confirmations; a digital copy is sufficient.

The Project Review Clinic is intended for participants who bring a current project outline. An outline may be printed or stored on a personal device. The clinic does not provide introductory instruction, and participants should already be familiar with basic planning methods.

The center will provide drinking water, but there is no food service on site. Participants may use the lounge between sessions. A café across the street offers takeaway lunches. Anyone leaving a device in a classroom during lunch must arrange this with the instructor; classrooms will otherwise be locked when sessions end.''')], [
 Q('159', 'Which session begins at 11:30 a.m.?', ['Spreadsheet Reporting', 'Budget Planning Basics', 'Meeting Facilitation', 'Project Review Clinic'], 'C', '세부 정보', '기본', 'Schedule: Easton Skills Center의 "11:30-1:00: Meeting Facilitation"', '시간표 Room 2의 시작 시각을 확인한다. 11:00 시작 회차와 11:30 회차를 구분한다.', '11:30 시작 회차 이름과 일치하는 C가 맞다.', {'A':'Spreadsheet Reporting은 11:00에 시작한다.', 'B':'Budget Planning Basics는 9:00에 시작한다.', 'D':'Project Review Clinic은 2:00에 시작한다.'}),
 Q('160', 'Who would be most suited to attend the Project Review Clinic?', ['A participant with a project outline and basic planning experience', 'A participant seeking an introduction to planning', 'A participant who can attend only before noon', 'A participant who needs the center to supply a project topic'], 'A', '추론', '중급', 'Schedule: Easton Skills Center의 "bring a current project outline"와 "already be familiar"', '클리닉은 현재 개요를 가져오고 기본 계획법을 아는 사람을 전제로 한다. 두 조건과 오후 시간을 함께 확인한다.', '개요와 기본 경험을 모두 갖춘 A가 대상 조건에 부합한다.', {'B':'does not provide introductory instruction이라고 명시한다.', 'C':'클리닉은 오후 2시부터라 오전만 가능한 사람에게 맞지 않는다.', 'D':'센터가 주제를 제공한다고 하지 않고 본인의 개요를 요구한다.'}),
 Q('161', 'What is NOT indicated in the participation notes?', ['A digital confirmation is acceptable.', 'Registered participants have priority in the afternoon.', 'Drinking water will be provided.', 'Lunch is included in the session fee.'], 'D', 'NOT/EXCEPT', '중급', 'Schedule: Easton Skills Center의 "no food service on site"', '안내에는 디지털 확인, 오후 우선권, 식수 제공이 각각 명시된다. 점심 포함은 없으며 현장 식사 서비스 자체가 없다.', '언급되지 않고 식사 안내와도 맞지 않는 D가 남는다.', {'A':'a digital copy is sufficient이라고 직접 말한다.', 'B':'registered participants have priority라고 명시한다.', 'C':'provide drinking water라고 명시한다.'}),
]))

data['mock'].append(S('실전 단일 지문 7 | 수리 접수 양식', [D('Form: Aster Equipment Service', '''Aster Equipment: Service Request Record

Request number: SR-306
Customer: Hillside Surveying
Contact person: Lena Ortiz
Equipment: Portable measuring unit, model M8
Serial number: M8-77214
Date received: February 7
Warranty purchase date: August 19 of the previous year

Reported issue: The screen becomes blank after approximately twenty minutes of use. Restarting the unit restores the display temporarily. The customer reports no visible damage and no exposure to water.

Requested service: Diagnosis and repair
Return method selected: Courier delivery
Return address: Hillside Surveying, 8 Birch Avenue
Loan unit requested: No

Technician’s preliminary note: The unit operated normally during a ten-minute initial check. A longer test is required before a repair estimate can be prepared. Please do not replace any components until the fault has been reproduced.

Customer instructions: If the estimated repair cost exceeds $120, contact Ms. Ortiz for authorization before proceeding. Diagnosis is covered under the warranty, but coverage of replacement components will depend on the cause of the fault. Send the estimate by email. Ms. Ortiz will collect the unit herself only if courier delivery cannot be arranged.''')], [
 Q('162', 'What problem did the customer report?', ['The equipment was damaged during delivery.', 'The display stops working after a period of use.', 'The serial number cannot be found.', 'The unit fails to restart under any circumstances.'], 'B', '세부 정보', '기본', 'Form: Aster Equipment Service의 "screen becomes blank after approximately twenty minutes"', '고객이 보고한 문제는 사용 후 약 20분에 화면이 꺼지는 것이다. 재시작하면 잠시 복구된다는 제한도 있다.', '일정 시간 사용 뒤 표시 문제가 생긴다는 B가 정확하다.', {'A':'visible damage는 없다고 보고되며 배송 중 손상은 아니다.', 'C':'일련번호가 양식에 기재되어 있다.', 'D':'재시작은 일시적으로 화면을 복구한다고 한다.'}),
 Q('163', 'Why is a longer test needed?', ['The customer requested a loan unit.', 'The warranty has already expired.', 'The technician has replaced all components.', 'The initial check did not reproduce the reported problem.'], 'D', '추론', '고급', 'Form: Aster Equipment Service의 "operated normally during a ten-minute initial check"', '신고 문제는 약 20분 사용 후 발생하지만 초기 검사는 10분 동안 정상 작동했다. 아직 고장이 재현되지 않아 긴 시험이 필요하다.', '검사 길이와 증상 발생 시점을 연결하면 D가 필요한 이유다.', {'A':'Loan unit requested는 No다.', 'B':'보증 만료일은 제시되지 않았고 진단은 보증 대상이라고 한다.', 'C':'재현 전 부품을 교체하지 말라는 지시가 있다.'}),
 Q('164', 'When must the service team obtain Ms. Ortiz’s authorization?', ['When the estimated repair cost is over $120', 'Before sending any email', 'Whenever a diagnosis is performed', 'Only after courier delivery has failed'], 'A', '세부 정보', '중급', 'Form: Aster Equipment Service의 "exceeds $120 ... authorization before proceeding"', '허가는 견적이 120달러를 넘을 때 수리 진행 전에 필요하다. 진단 보장과 수리 부품 보장은 분리된다.', '금액 경계 exceeds와 사전 승인 조건을 유지한 A가 맞다.', {'B':'견적 이메일 발송 자체에 사전 승인을 요구하지 않는다.', 'C':'모든 진단에 승인 요구가 아니라 비용 초과 조건이다.', 'D':'배송 실패는 본인 수령의 조건으로 수리 승인과 무관하다.'}),
]))

data['mock'].append(S('실전 단일 지문 8 | 팀 채팅', [D('Chat: Solace Publishing', '''10:02 Hana: The author approved the cover, but the printer needs the final file by noon. Is the barcode layer ready?
10:04 Ben: Yes. I added it last night. I still need the updated price from sales before I export the file.
10:06 Ravi: The paperback price is now $19.50. I sent a confirmation email at 9:40, but you may have been looking at the earlier message.
10:08 Ben: That explains it. I'll update the price now. The export should take about twenty minutes.
10:10 Hana: I have a client call at 11:30. Can you send the finished file directly to Mara at the printing company?
10:12 Ben: I can take it from here. Please forward her address and the job reference.
10:14 Hana: Done. The reference is SP-204. Ask her to confirm receipt, and copy me on the message.
10:16 Ravi: Do we need another author approval after the price change?
10:18 Hana: No. The contract allows us to set the retail price. The author only needed to approve the cover design.''')], [
 Q('165', 'What does Ben mean when he writes, "I can take it from here"?', ['He will attend Hana’s client call.', 'He will choose a new cover design.', 'He will handle the file submission.', 'He will ask the author to set the price.'], 'C', '대화 의도', '중급', 'Chat: Solace Publishing의 "send the finished file directly to Mara"와 "forward her address"', 'Hana가 파일을 직접 보내 달라고 부탁한 데 Ben이 업무 인수를 수락한다. 이어 주소와 작업 번호를 요청한다.', '최종 파일 전송을 맡겠다는 C가 앞 요청과 뒤 행동을 연결한다.', {'A':'고객 통화는 Hana의 일정이며 Ben이 대신한다는 말이 없다.', 'B':'표지 디자인은 이미 승인되었다.', 'D':'판매팀이 가격을 제공했고 계약상 출판사가 결정한다.'}),
 Q('166', 'What was preventing Ben from exporting the file?', ['He had not confirmed the updated price.', 'The barcode had not been created.', 'Mara had rejected the job reference.', 'The author had withdrawn design approval.'], 'A', '세부 정보', '중급', 'Chat: Solace Publishing의 "still need the updated price from sales"', '바코드는 전날 추가했고 남은 정보는 새 가격이다. Ravi의 최신 이메일 대신 앞 이메일을 보았던 정황도 설명한다.', '가격 확인 미완료라는 A가 실제 지연 원인이다.', {'B':'I added it last night라고 바코드 작업 완료를 말한다.', 'C':'Mara가 작업 번호를 거부한 내용이 없다.', 'D':'저자는 표지를 승인했고 철회한 적이 없다.'}),
 Q('167', 'What is suggested about the author’s approval?', ['It must be renewed every morning.', 'It includes a final decision on the retail price.', 'It cannot be sent by email.', 'It concerns the design rather than the retail price.'], 'D', '추론', '고급', 'Chat: Solace Publishing의 "only needed to approve the cover design"', 'only가 승인 범위를 디자인에 한정하고 계약은 출판사에 판매가 결정 권한을 준다. 가격 변경 때문에 새 승인이 필요하지 않다.', '승인의 대상 범위를 정확히 표현한 D가 성립한다.', {'A':'매일 갱신 조건은 없다.', 'B':'가격 결정 권한은 계약상 출판사에 있다.', 'C':'승인 전달 수단의 제한은 제시되지 않는다.'}),
]))

data['mock'].append(S('실전 단일 지문 9 | 교육 등록 이메일', [D('Email: Luma Training', '''To: Department coordinators
From: Yuki Mori, Luma Training
Subject: Final arrangements for the data-review course

We have received more registrations than expected for the data-review course. The original session on December 6 is now full. [1] We have added a second session on December 13 with the same instructor and course content. Both sessions will run from 9:00 a.m. to 3:00 p.m. in Room 402. [2]

Employees currently on the waiting list will be offered places in the new session first. Please ask them to respond to their individual invitations by November 28. Any places remaining after that date will be released to other employees. A waiting-list entry is not a confirmed reservation.

Participants should bring a laptop with the current reporting software installed. The practice files will be sent two days before each session. [3] These should be downloaded in advance because the classroom internet connection may be slow when everyone connects at once.

We will hold a small number of spare laptops for participants whose devices fail on the day. They are intended for unexpected problems, so please do not rely on them instead of bringing your own device. [4] Contact the training desk if you need help checking the software version before the course.''')], [
 Q('168', 'Where does the following sentence best belong? "The additional date will allow more employees to attend without enlarging the classes."', ['[1]', '[2]', '[3]', '[4]'], 'B', '문장 삽입', '고급', 'Email: Luma Training의 "added a second session on December 13"와 [2]', 'The additional date는 추가된 12월 13일 회차를 받는다. [2] 앞에는 두 회차의 날짜·시간·장소가 소개되었고 뒤에는 새 회차의 우선 배정 절차가 이어진다. [1]에서는 추가 날짜가 아직 나오지 않는다.', '회차 추가의 효과를 설명하고 등록 절차로 넘어가는 [2]가 앞뒤 전개를 모두 연결한다.', {'A':'[1] 앞에는 기존 회차가 가득 찼다는 정보만 있어 additional date의 선행 대상이 없다.', 'C':'[3]은 연습 파일 소개와 These의 지칭 연결을 갈라놓는다.', 'D':'[4]는 예비 노트북과 소프트웨어 도움 안내 사이로 새 날짜의 효과와 멀다.'}),
 Q('169', 'What does "These" refer to?', ['The course invitations', 'The classroom laptops', 'The practice files', 'The software versions'], 'C', '지칭', '중급', 'Email: Luma Training의 "The practice files will be sent"와 "These should be downloaded"', '복수 지시어 These와 downloaded라는 행동은 직전 소개한 연습 파일에 맞는다. 노트북은 내려받는 대상이 아니다.', '연습 파일을 미리 다운로드하라는 연결이므로 C다.', {'A':'초대장은 이전 문단의 등록 수락 대상이며 연습용 다운로드 안내가 아니다.', 'B':'노트북 자체는 다운로드할 수 없다.', 'D':'이 문단의 직전 명사는 파일이며 버전은 마지막 도움 안내에서 언급된다.'}),
 Q('170', 'The word "hold" is closest in meaning to', ['reserve', 'repair', 'examine', 'purchase'], 'A', '문맥상 의미', '중급', 'Email: Luma Training의 "hold a small number of spare laptops"', '예기치 않은 장비 고장을 대비해 소수의 예비 노트북을 확보해 두는 상황이다. 물리적으로 손에 쥐거나 새 구매한다는 뜻은 아니다.', '필요할 때 쓰도록 마련해 둔다는 reserve가 문맥에 맞는다.', {'B':'대상은 고장 난 노트북의 수리가 아니라 정상 예비 장비다.', 'C':'검사 행위가 아니라 비상 사용을 위해 남겨 두는 행동이다.', 'D':'새 구매 여부는 명시되지 않으며 목적은 예비분 확보다.'}),
 Q('171', 'What must waiting-list employees do to secure a place in the new session?', ['Attend both December sessions', 'Pay for a spare laptop', 'Download the files by November 28', 'Respond to their invitations by November 28'], 'D', '세부 정보', '중급', 'Email: Luma Training의 "respond to their individual invitations by November 28"', '대기 명단 등록만으로 확정되지 않으므로 개별 초대에 기한 내 응답해야 한다. 파일 발송은 각 회차 이틀 전이다.', '수락 응답과 마감일을 모두 유지한 D가 필요한 행동이다.', {'A':'두 회차 참석 요구는 없다.', 'B':'예비 노트북 구매·대금 납부는 언급되지 않는다.', 'C':'11월 28일은 초대 응답 마감이지 연습 파일 다운로드일이 아니다.'}),
]))

data['mock'].append(S('실전 단일 지문 10 | 시범 운영 보고서', [D('Report: Northgate Shuttle', '''Northgate Business Park Shuttle: Trial Review

The four-week shuttle trial between Northgate Station and the business park ended on June 28. The service carried 1,240 passengers in total. Use was highest between 7:30 and 9:00 a.m., while the final evening departure at 7:00 p.m. attracted an average of only three passengers.

The passenger survey drew 186 responses. Most respondents valued the direct route, but several requested a stop at the medical center. Adding that stop would increase the journey by approximately eight minutes and require a change to the published timetable. We recommend keeping the direct route for the next phase and investigating a separate midday service to the medical center.

Operating costs were within the approved trial budget. However, one driver’s absence required a replacement bus from a contractor on two days. The contractor’s vehicle had fewer seats, and passengers on one morning departure had to wait for the next bus. A reserve-driver arrangement should be established before regular service begins.

The report does not recommend committing to a year-round contract yet. Instead, a second trial during the autumn would help determine whether passenger demand is affected by seasonal working patterns. The business park committee will review this recommendation at its July meeting.''')], [
 Q('172', 'What is the purpose of the report?', ['To announce a year-round shuttle contract', 'To evaluate a trial and recommend further steps', 'To advertise a new medical center', 'To request refunds from all passengers'], 'B', '목적', '중급', 'Report: Northgate Shuttle의 "Trial Review"와 "a second trial during the autumn"', '이용·조사·비용·인력 문제를 평가하고 경로 유지, 예비 기사, 가을 재시험을 권고한다. 연중 계약은 권고하지 않는다.', '시범 운영 평가와 후속 조치를 포괄하는 B가 목적이다.', {'A':'does not recommend ... year-round contract라고 반대된다.', 'C':'의료센터는 경유 요청 대상으로 등장할 뿐 광고가 아니다.', 'D':'환불 요청은 제시되지 않는다.'}),
 Q('173', 'Which action is NOT recommended in the report?', ['Keeping the direct route for the next phase', 'Establishing a reserve-driver arrangement', 'Conducting a second trial in autumn', 'Adding the medical-center stop to the existing route immediately'], 'D', 'NOT/EXCEPT', '고급', 'Report: Northgate Shuttle의 "keeping the direct route"와 "separate midday service"', '기존 직행 유지와 의료센터 별도 낮 서비스 검토가 권고된다. 기존 노선에 즉시 정류장을 추가하는 것은 그 권고와 다르다.', '별도 검토를 즉시 기존 경로 변경으로 바꾼 D가 권고되지 않은 행동이다.', {'A':'직행 경로 유지는 명시적 권고다.', 'B':'정기 운영 전 예비 기사 체계를 마련하라고 한다.', 'C':'계절 수요 확인을 위한 가을 재시험을 권고한다.'}),
 Q('174', 'What can be inferred about one morning during the trial?', ['The replacement bus could not carry everyone on one departure.', 'No passengers arrived at the station.', 'The direct route was permanently removed.', 'The contractor exceeded the full trial budget.'], 'A', '추론', '고급', 'Report: Northgate Shuttle의 "fewer seats"와 "had to wait for the next bus"', '대체 차량 좌석이 적었고 일부가 다음 차량을 기다렸다. 해당 회차의 수용 능력이 모든 대기 승객을 태우기에 부족했다는 최소 결론이 성립한다.', '좌석 수와 대기 결과를 연결한 A가 타당하다.', {'B':'다음 차량을 기다린 승객이 있으므로 아무도 오지 않았다는 말은 틀리다.', 'C':'직행은 유지 권고 대상이며 영구 제거되지 않았다.', 'D':'총 운영비는 승인 예산 이내였다고 한다.'}),
 Q('175', 'The word "drew" is closest in meaning to', ['illustrated', 'transported', 'received', 'withdrew'], 'C', '문맥상 의미', '중급', 'Report: Northgate Shuttle의 "survey drew 186 responses"', '주어는 survey이고 목적어는 응답 수다. 설문이 응답을 얻었다는 참여 결과를 표현한다.', '응답을 받았다는 received가 문장 의미를 유지한다.', {'A':'설문이 그림을 그렸다는 뜻으로 responses와 결합할 수 없다.', 'B':'승객 운송은 서비스의 행동이며 설문 응답을 운반했다는 의미가 아니다.', 'D':'응답을 철회했다는 뜻은 긍정적으로 수집한 응답 수와 반대다.'}),
]))

training_ids = [q['id'] for s in data['training'] for q in s['questions']]
mock_ids = [q['id'] for s in data['mock'] for q in s['questions']]
assert training_ids == [f'P7-{n:02}' for n in range(1,23)], training_ids
assert mock_ids == [str(n) for n in range(147,176)], mock_ids
assert [len(s['questions']) for s in data['mock']] == [2,2,2,3,3,3,3,3,4,4]
assert len(data['sections']) == 10
assert len(data['training']) == 6
assert len(data['mock']) == 10
assert '\u2014' not in json.dumps(data, ensure_ascii=False)
target = ROOT / 'part7.json'
target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
for group in ('training', 'mock'):
    for s in data[group]:
        count = sum(len(re.findall(r"[A-Za-z0-9]+(?:[-'’][A-Za-z0-9]+)*", d['text'])) for d in s['documents'])
        print(group, s['title'], 'documents=',len(s['documents']), 'words=',count, 'questions=',len(s['questions']))
print('Saved', target, '| Training:', len(training_ids), '| Mock singles:',len(mock_ids))

