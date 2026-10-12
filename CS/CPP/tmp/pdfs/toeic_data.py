Q = []
P6 = []
P7 = []

def add(n, stem, opts, answer, level, tag, point, explanation, analyses, caution, remember, evidence=None):
    assert len(opts) == len(analyses) == 4
    Q.append(dict(n=n, stem=stem, opts=opts, answer=answer, level=level, tag=tag,
                  point=point, explanation=explanation, analyses=analyses,
                  caution=caution, remember=remember, evidence=evidence))

add(1, 'The updated expense policy was ------- posted on the company intranet.',
    ['recent', 'recently', 'recency', 'more recent'], 'B', 1, 'PART 5 - WORD FORM',
    '수동태 동사구를 수식하는 자리에는 부사가 필요하다.',
    '주어는 policy, 동사구는 was posted이다. 빈칸은 게시된 시점을 보충하므로 부사 recently가 들어간다.',
    ['형용사이므로 posted를 직접 수식할 수 없다.', '최근에 게시되었다는 뜻의 부사로 동사구를 수식한다.', '명사이며 이 자리에 명사구를 요구하는 구조가 없다.', '비교급 형용사이며 수식할 명사도 비교 기준도 없다.'],
    '빈칸 뒤 단어만 보지 말고 was posted를 하나의 동사구로 읽는다.', '문장 뼈대가 완성되면 수식어의 품사를 확인한다.')

add(2, 'Each of the replacement filters ------- a label showing its installation date.',
    ['have', 'are having', 'has', 'were having'], 'C', 1, 'PART 5 - AGREEMENT',
    'Each of + 복수명사의 핵심 주어 each는 단수 취급한다.',
    'filters는 of의 목적어이다. 핵심 주어 Each에 맞는 단수 현재 동사 has가 필요하며, have는 여기서 소유를 나타낸다.',
    ['복수형 동사라 단수 주어와 맞지 않는다.', '복수 동사이며 소유 의미에 진행형도 부적절하다.', '단수 주어와 일치하고 라벨을 지니고 있다는 의미도 맞다.', '복수 과거 진행형으로 수와 소유 의미 모두 맞지 않는다.'],
    '동사와 가까운 filters를 주어로 착각하지 않는다.', '수일치는 전치사구를 제외한 핵심 주어로 판단한다.')

add(3, 'By the time the new branch opens next month, all employees ------- the required safety training.',
    ['completed', 'have completed', 'are completing', 'will have completed'], 'D', 3, 'PART 5 - TENSE',
    '미래의 기준 시점보다 먼저 끝날 일에는 미래완료가 적절하다.',
    'next month의 개점이 미래 기준점이다. 그때까지 전 직원이 교육을 끝낸 상태를 나타내므로 will have completed를 고른다.',
    ['과거 시점이 제시되지 않았고 미래 기준점과 맞지 않는다.', '현재까지의 완료만 나타내어 미래 기준점까지의 완료를 표현하지 못한다.', '진행 중이라는 뜻으로 기준 시점까지 끝난 상태와 다르다.', '미래 기준점까지의 완료를 정확하게 나타낸다.'],
    'by the time 뒤 opens가 현재형이어도 시간 부사절은 미래를 나타낼 수 있다.', '미래 시점 + 그 전에 완료: will have + 과거분사.')

add(4, 'No refund can ------- until the returned item has been inspected.',
    ['be issued', 'issue', 'issuing', 'have issuing'], 'A', 2, 'PART 5 - VOICE',
    '환불은 발행되는 대상이므로 조동사 뒤 수동태가 필요하다.',
    'refund가 환불을 발행하는 주체가 아니다. can 뒤에 동사원형 be와 과거분사 issued를 두어 수동 의미를 만든다.',
    ['can be issued는 환불이 처리될 수 있다는 수동태이다.', '능동태라 환불이 발행하는 주체가 되는 문제가 있다.', '조동사 can 뒤에 동명사만 올 수 없다.', 'have 뒤 issuing은 완료형도 수동태도 아니다.'],
    '조동사 뒤라는 이유로 issue만 고르지 말고 능동·수동도 확인한다.', '주어가 받는 행위라면 modal + be + p.p.')

add(5, 'The supervisor lets team members ------- their shifts through the scheduling app.',
    ['swapping', 'to swap', 'swapped', 'swap'], 'D', 1, 'PART 5 - NONFINITE VERB',
    '사역동사 let의 목적격 보어에는 동사원형을 쓴다.',
    'lets + team members + swap 구조이다. 직원들이 교대 시간을 바꾸도록 허용한다는 뜻이다.',
    ['let의 목적격 보어로 동명사를 쓰지 않는다.', 'allow와 달리 let은 이 구조에서 to부정사를 취하지 않는다.', '직원들이 바꾸는 능동 행위이므로 과거분사가 아니다.', 'let + 목적어 + 동사원형 구조에 맞는다.'],
    'allow someone to do와 let someone do를 혼동하지 않는다.', 'let + 사람 + 동사원형.')

add(6, '------- the short notice, nearly all department heads attended the briefing.',
    ['Although', 'Despite', 'Even if', 'Because'], 'B', 1, 'PART 5 - PREPOSITION',
    '양보 의미 뒤에 명사구가 오면 despite를 쓴다.',
    'the short notice는 주어·동사가 없는 명사구이다. 촉박한 통보에도 거의 모두 참석했다는 양보 관계이다.',
    ['접속사이므로 뒤에 절이 필요하다.', '명사구를 목적어로 취하는 양보 전치사이다.', '접속사이며 조건 의미도 문맥과 맞지 않는다.', '절을 이끄는 접속사이며 양보 관계도 나타내지 않는다.'],
    '의미만 비슷한 although를 고르기 전에 뒤가 절인지 확인한다.', 'despite + 명사구 / although + 절.')

add(7, 'The supplier will keep the order on hold ------- it receives a revised purchase order.',
    ['during', 'by', 'until', 'within'], 'C', 2, 'PART 5 - CONJUNCTION',
    '절을 연결하면서 지속의 끝점을 나타내는 until을 찾는다.',
    '빈칸 뒤 it receives는 절이다. 수정 주문서를 받을 때까지 보류 상태가 계속된다는 뜻이다.',
    ['전치사이므로 절을 직접 목적어로 받을 수 없다.', '기한을 나타내는 전치사이며 이 절을 직접 연결하지 못한다.', '절을 연결하고 보류 상태의 끝점을 나타낸다.', '기간 명사구와 쓰는 전치사이며 절을 연결하지 못한다.'],
    '기한을 떠올려 by를 고르기 쉽지만 hold는 지속 상태이다.', '지속 상태 + 종료 조건의 절: until.')

add(8, 'Applicants ------- portfolios demonstrate experience in packaging design will receive priority.',
    ['whose', 'who', 'whom', 'which'], 'A', 2, 'PART 5 - RELATIVE PRONOUN',
    '선행사와 뒤 명사의 소유 관계는 whose로 연결한다.',
    '지원자들의 포트폴리오라는 관계이다. whose portfolios 전체가 관계절의 주어이고 demonstrate가 그 동사이다.',
    ['지원자들의 portfolios라는 소유 관계를 표시한다.', '주격이므로 뒤 명사 portfolios와 직접 이어지지 않는다.', '목적격이며 뒤 명사를 소유 형태로 수식하지 못한다.', '사물 관계대명사이며 필요한 소유 관계를 만들지 못한다.'],
    '사람 선행사만 보고 who를 고르지 않는다.', '빈칸 + 명사 + 동사이면 소유격 관계사를 검토한다.')

add(9, 'The orientation is open to all employees, including ------- who joined the company last month.',
    ['these', 'them', 'theirs', 'those'], 'D', 2, 'PART 5 - PRONOUN',
    'those who는 특정 조건에 해당하는 사람들을 나타낸다.',
    'including 뒤에는 명사 역할이 필요하다. those가 사람들을 가리키고 who절이 그 대상을 한정한다.',
    ['these who는 이 문장에서 사람들을 일반적으로 한정하는 자연스러운 표현이 아니다.', '인칭대명사 them을 이처럼 한정적 who절의 선행사로 쓰지 않는다.', '소유대명사라 사람들을 나타내는 문맥에 맞지 않는다.', 'those who joined는 지난달 입사한 사람들이라는 뜻이다.'],
    'including 뒤 목적격 자리라는 이유로 them만 고르지 않는다.', '조건에 해당하는 사람들: those who + 동사.')

add(10, 'The redesigned checkout page is ------- than the previous version.',
    ['easy to navigate', 'easier to navigate', 'easiest to navigate', 'easily navigated'], 'B', 1, 'PART 5 - COMPARISON',
    'than으로 두 대상을 비교하면 비교급을 사용한다.',
    '새 결제 페이지와 이전 버전을 비교하므로 easier가 필요하다. easy to navigate는 탐색하기 쉽다는 뜻이다.',
    ['원급이어서 than과 직접 비교 구조를 만들지 못한다.', '비교급 easier와 than이 자연스럽게 연결된다.', '최상급이며 두 버전의 비교 구조와 맞지 않는다.', '부사와 분사 조합이며 than 앞 비교급이 없다.'],
    'navigate의 형태보다 than이라는 구조 단서를 먼저 본다.', 'than이 보이면 비교급 형태를 확인한다.')

add(11, 'The conference room can ------- up to 120 guests without additional seating.',
    ['accompany', 'accomplish', 'accommodate', 'accumulate'], 'C', 2, 'PART 5 - VOCABULARY',
    '공간이 사람을 수용한다는 뜻에는 accommodate를 쓴다.',
    '방의 수용 인원을 설명하므로 accommodate guests가 맞다. 네 선택지는 모두 동사원형이므로 의미로 구별한다.',
    ['동행하다라는 뜻으로 방의 수용 능력을 나타내지 못한다.', '과업을 완수하다라는 뜻이며 guests를 목적어로 쓰기 부적절하다.', '사람을 수용하다라는 뜻으로 정원 설명에 맞는다.', '물건이나 양을 축적하다라는 뜻이며 손님 수용과 다르다.'],
    '철자가 비슷한 동사들을 품사 문제처럼 처리하지 않는다.', '장소 + accommodate + 인원 = 수용하다.')

add(12, 'All contractors must comply ------- the site\'s safety requirements.',
    ['with', 'to', 'for', 'at'], 'A', 2, 'PART 5 - COLLOCATION',
    '규정 준수는 comply with라는 결합으로 표현한다.',
    'comply는 여기서 자동사이며 준수 대상인 safety requirements를 with로 연결한다.',
    ['comply with requirements라는 올바른 결합이다.', 'conform to와 혼동하기 쉽지만 comply는 with를 쓴다.', '준수 대상을 나타내는 결합이 아니다.', '준수 대상을 연결하지 못한다.'],
    '동의어 동사들이 같은 전치사를 쓰는 것은 아니다.', 'comply with / conform to를 동사째로 묶어 외운다.')

add(13, 'Details of the proposed merger must remain ------- until an agreement is signed.',
    ['confidentially', 'confidence', 'confide', 'confidential'], 'D', 1, 'PART 5 - COMPLEMENT',
    '상태를 나타내는 remain 뒤에는 주격 보어인 형용사가 온다.',
    '합병 세부 정보가 기밀 상태로 유지되어야 한다. confidential이 Details의 상태를 설명한다.',
    ['부사는 여기서 주어의 상태를 보충하는 보어가 될 수 없다.', '자신감·신뢰를 뜻하는 명사로 Details의 상태와 맞지 않는다.', '동사이므로 remain 뒤 상태 보어가 될 수 없다.', '기밀인이라는 형용사로 주어의 상태를 나타낸다.'],
    '동사 뒤에는 항상 부사가 온다는 규칙을 적용하지 않는다.', 'remain / become / seem 뒤 상태는 형용사.')

add(14, 'Only after the technician replaced the sensor ------- normally.',
    ['the system operated', 'did the system operate', 'the system did operate', 'operated the system'], 'B', 3, 'PART 5 - INVERSION',
    'Only + 부사절이 문두에 오면 주절에 도치를 적용한다.',
    'Only after절 뒤 주절은 조동사 did + 주어 the system + 동사원형 operate 순서가 된다.',
    ['일반 어순으로 문두 Only after가 요구하는 주절 도치가 없다.', 'did가 주어 앞으로 이동했고 본동사도 원형이다.', 'did가 있어도 주어 뒤에 있어 도치가 이루어지지 않았다.', 'operate는 여기서 자동사이며 필요한 조동사 도치가 아니다.'],
    'after절 내부를 도치하거나 본동사를 과거형으로 남기지 않는다.', 'Only + 부사구/절 문두: 주절 조동사 + 주어 + 원형.')

add(15, '------- the final inspection, Ms. Chen authorized the building to reopen.',
    ['Having completed', 'Having been completed', 'To be completed', 'Completion of'], 'A', 3, 'PART 5 - PARTICIPLE CLAUSE',
    '분사구문의 행위자는 주절 주어와 일치해야 한다.',
    'Ms. Chen이 점검을 완료한 뒤 재개장을 승인했다. 능동 완료 분사구문 Having completed가 행위와 선후 관계를 모두 표현한다.',
    ['Ms. Chen이 점검을 완료했다는 능동 완료 관계이다.', 'Ms. Chen이 완료된 대상으로 해석되어 의미가 어긋난다.', '완료될 목적이나 대상을 나타내는 수동 부정사로 맞지 않는다.', '명사구만 남아 뒤 완전한 주절과 문법적으로 연결되지 않는다.'],
    'inspection이 완료된다는 생각만으로 수동을 고르지 않는다. 숨은 주어는 Ms. Chen이다.', '분사구문은 주절 주어가 무엇을 하는지부터 확인한다.')

add(16, 'The delivery fee will be waived ------- the order totals at least $200; smaller orders incur a $12 charge.',
    ['even though', 'whereas', 'provided that', 'now that'], 'C', 3, 'PART 5 - CONDITION',
    '혜택이 적용되는 조건과 반대 경우의 규정을 연결한다.',
    '200달러 이상이라는 조건을 충족할 때만 배송료가 면제되고, 더 작은 주문에는 비용이 발생한다. provided that은 ~라는 조건으로라는 뜻이다.',
    ['양보 접속사로 금액에 따라 달라지는 조건을 표현하지 못한다.', '대조 접속사로 면제 조건을 이끄는 자리에 맞지 않는다.', '최소 주문액이라는 면제 조건을 정확히 나타낸다.', '이미 확정된 사실에 따른 이유를 나타내어 일반 적용 조건과 다르다.'],
    '빈칸 앞뒤만 보지 말고 세미콜론 뒤 작은 주문의 비용까지 확인한다.', '혜택 + 기준 충족 여부: 조건 접속사를 찾는다.')

add(17, 'Please submit the signed contract ------- noon tomorrow so that processing can begin that afternoon.',
    ['until', 'by', 'during', 'within'], 'B', 2, 'PART 5 - DEADLINE',
    '제출 완료 기한에는 by를 사용한다.',
    '내일 정오까지 한 번 제출을 완료하라는 요청이다. by noon이 마감 시점을 나타낸다.',
    ['정오까지 제출 행위를 계속하라는 뜻이 되어 완료 기한과 다르다.', '정오를 제출 완료의 최종 기한으로 설정한다.', '기간을 목적어로 취하며 noon이라는 시점과 맞지 않는다.', 'within 뒤에는 보통 two hours 같은 기간이 온다.'],
    '한국어 ~까지만 보고 until로 옮기지 않는다.', '완료 마감은 by / 상태 지속은 until.')

add(18, 'Since the store introduced online pickup, the number of repeat orders ------- steadily.',
    ['has risen', 'has raised', 'have risen', 'have raised'], 'A', 3, 'PART 5 - VERB AND AGREEMENT',
    'the number of의 단수 일치와 rise의 자동사 성격을 함께 확인한다.',
    '핵심 주어는 단수 number이므로 has가 필요하다. 주문 수가 스스로 증가한 것이므로 목적어가 필요 없는 rise의 과거분사 risen을 쓴다.',
    ['단수 일치와 자동사 현재완료를 모두 충족한다.', 'raise는 타동사인데 증가시키는 목적어가 없다.', 'risen은 맞지만 핵심 주어 number와 수가 맞지 않는다.', '복수 일치와 목적어 없는 타동사라는 두 문제가 있다.'],
    'orders에 수일치를 맞추거나 rise와 raise를 철자만으로 혼동하지 않는다.', 'the number는 단수 / 수치 자체의 증가는 rise.')

add(19, 'The purchasing manager has not yet ------- payment for the additional equipment.',
    ['applied', 'arrived', 'occurred', 'authorized'], 'D', 2, 'PART 5 - VOCABULARY',
    '결제를 승인하다는 authorize payment로 표현한다.',
    'has not yet 뒤에는 과거분사가 필요하며 네 선택지 모두 형태는 가능하다. payment를 직접 목적어로 받아 승인을 뜻하는 authorized가 맞다.',
    ['신청하다 의미로는 apply for가 필요하며 결제 승인과 다르다.', '자동사로 payment를 직접 목적어로 취하지 못한다.', '발생하다라는 자동사로 payment를 목적어로 취하지 못한다.', 'payment를 직접 목적어로 받아 결제를 승인한다는 뜻이다.'],
    '형태가 모두 과거형처럼 보여도 목적어와의 결합을 확인한다.', '동사의 뜻과 목적어를 함께 읽는다.')

add(20, 'The consultant to ------- the report should be sent is currently attending a conference.',
    ['who', 'whose', 'whom', 'which'], 'C', 3, 'PART 5 - RELATIVE CLAUSE',
    '사람 선행사를 받는 전치사 뒤에는 목적격 whom을 쓴다.',
    'send the report to the consultant의 to가 관계대명사 앞으로 이동했다. the report should be sent는 수동태 관계절이다.',
    ['격식을 갖춘 전치사 바로 뒤 자리에는 주격 who가 맞지 않는다.', '소유격이며 뒤에 수식할 명사가 필요한 구조와 다르다.', '전치사 to의 목적격이면서 사람을 가리킨다.', '사물 선행사에 사용하므로 consultant와 맞지 않는다.'],
    'consultant 뒤 관계절이 길어도 to whom을 한 덩어리로 본다.', '전치사 + 사람 관계대명사: whom.')

add(21, 'The designers prepared the exhibition materials ------- instead of hiring an outside agency.',
    ['their', 'themselves', 'them', 'theirs'], 'B', 2, 'PART 5 - REFLEXIVE PRONOUN',
    '재귀대명사는 주어가 직접 했음을 강조할 수 있다.',
    'prepared의 목적어 materials는 이미 있다. themselves는 디자이너들이 외주 없이 직접 준비했다는 강조 용법이다.',
    ['소유격 뒤에 명사가 없고 필요한 강조 의미도 없다.', '주어 designers를 강조하며 직접 준비했다는 뜻이다.', '목적어가 이미 있어 별도의 목적격 대명사를 덧붙일 수 없다.', '소유대명사가 들어갈 명사 자리가 아니다.'],
    '빈칸 앞 목적어가 이미 있는지 먼저 확인한다.', '주어가 직접 수행했다는 강조는 재귀대명사.')

add(22, 'Each rental bicycle is equipped ------- a front light and a rear reflector.',
    ['by', 'for', 'to', 'with'], 'D', 2, 'PART 5 - COLLOCATION',
    '장비가 갖추어져 있다는 be equipped with로 표현한다.',
    '자전거가 전조등과 후방 반사판을 갖추었다는 뜻이다. with 뒤에 갖추어진 장비가 나온다.',
    ['장비를 갖추는 행위자를 나타낼 수 있지만 light와 reflector는 행위자가 아니다.', '용도를 나타내는 자리라면 가능하나 장비 목록을 연결하지 못한다.', '장비를 목적어로 연결하는 결합이 아니다.', 'be equipped with + 장비라는 올바른 표현이다.'],
    '수동태에 by가 온다는 규칙을 기계적으로 적용하지 않는다.', '장비 with / 행위자 by를 구별한다.')

add(23, '------- the increase in reservations, the restaurant will add a second dinner seating.',
    ['Given', 'Giving', 'Gives', 'To give'], 'A', 3, 'PART 5 - PREPOSITION AND CONTEXT',
    'Given은 명사구 앞에서 ~을 고려하면이라는 전치사로 쓰인다.',
    '예약 증가를 고려하여 저녁 운영 시간을 한 차례 더 마련한다. Given the increase가 원인 판단의 배경을 제시한다.',
    ['증가를 고려하면이라는 전치사구로 문장 전체를 수식한다.', '주어 restaurant가 증가를 주는 행위라는 부자연스러운 의미가 된다.', '독립된 동사가 되지만 주어도 연결 장치도 없다.', '증가를 주기 위해라는 목적 의미로 문맥에 맞지 않는다.'],
    '모든 -ing/-ed 선택지를 분사구문으로만 해석하지 않는다.', 'Given + 명사구 = ~을 고려하면.')

add(24, 'The support team ------- customer requests since the service was restored and is still working through the backlog.',
    ['processes', 'will process', 'has been processing', 'had processed'], 'C', 2, 'PART 5 - TENSE',
    '과거에 시작해 지금도 계속되는 활동에는 현재완료진행이 적절하다.',
    'since절이 과거 시작점을 주고 is still working이 현재 지속을 확인한다. has been processing이 두 시점을 잇는다.',
    ['일반 현재는 since로 제시된 과거부터 현재까지의 지속을 충분히 나타내지 못한다.', '미래형은 이미 시작되어 지금 진행 중이라는 내용과 충돌한다.', '과거 시작과 현재까지 지속 중인 처리 활동을 표현한다.', '과거완료는 과거 기준점 이전의 완료이며 현재 지속과 맞지 않는다.'],
    'since만 보고 완료형을 찾은 뒤에도 still이라는 지속 단서를 확인한다.', 'since + 과거 시작점, 지금도 활동 중: has been -ing.')

add(25, 'Neither the technicians nor the site supervisor ------- available to inspect the equipment this afternoon.',
    ['are', 'is', 'were', 'have been'], 'B', 3, 'PART 5 - AGREEMENT',
    'neither A nor B의 동사는 가까운 주어 B에 맞춘다.',
    '동사에 가까운 the site supervisor가 단수이고 this afternoon의 현재 가용 상태를 묻는다. is available이 맞다.',
    ['가까운 단수 주어 supervisor와 일치하지 않는다.', '가까운 단수 주어와 일치하는 현재 be동사이다.', '복수 과거형으로 단수 주어와 맞지 않는다.', '복수형 have가 가까운 단수 주어와 맞지 않는다.'],
    '앞의 technicians에만 끌려 복수 동사를 고르지 않는다.', 'neither A nor B: 동사 가까운 B의 수를 확인한다.')

add(26, 'Customers who purchase the printer this week will receive installation at no additional -------.',
    ['fare', 'salary', 'charge', 'rent'], 'C', 2, 'PART 5 - VOCABULARY',
    '추가 비용 없이는 at no additional charge라는 표현이다.',
    '설치 서비스에 대한 부과 비용이 없다는 뜻이다. charge가 서비스 비용을 나타낸다.',
    ['교통수단의 운임이며 설치 서비스 비용과 다르다.', '직원 급여로 고객이 내는 서비스 비용이 아니다.', '서비스에 부과하는 비용으로 표현 전체가 자연스럽다.', '주택·장비 등의 임대료이며 설치 비용과 다르다.'],
    '한국어 비용으로 번역되는 모든 명사를 서로 바꾸어 쓰지 않는다.', '서비스 무료 제공: at no additional charge.')

add(27, 'Participants must register at least two days in ------- to receive the workshop materials by e-mail.',
    ['progress', 'place', 'order', 'advance'], 'D', 2, 'PART 5 - EXPRESSION',
    '미리라는 의미의 고정 표현은 in advance이다.',
    '행사 자료를 받으려면 적어도 이틀 전에 등록해야 한다. two days in advance가 선행 기간을 나타낸다.',
    ['in progress는 진행 중이라는 뜻으로 등록 선행 기간과 맞지 않는다.', 'in place는 제자리에 또는 마련되어라는 뜻이다.', 'in order는 순서대로 등의 뜻이며 이 문맥의 미리와 다르다.', 'in advance가 미리라는 뜻으로 two days와 자연스럽게 결합한다.'],
    '익숙한 전치사구라는 이유만으로 선택하지 않는다.', '기간 + in advance = 그 기간만큼 미리.')

add(28, 'The auditor recommended that all travel receipts ------- attached to the monthly report.',
    ['be', 'are', 'being', 'to be'], 'A', 3, 'PART 5 - MANDATIVE SUBJUNCTIVE',
    '요구·권고의 that절은 동사원형을 쓰며 수동이면 be + p.p.가 된다.',
    '감사인이 영수증을 첨부하도록 권고했다. recommended that + 주어 + be attached라는 권고절의 수동 구조이다.',
    ['권고절의 동사원형이자 수동태 be attached를 만든다.', '권고 내용의 당위절에서는 원형 be가 요구된다.', '정형 동사가 없어 that절이 완성되지 않는다.', 'that절에는 주어 뒤 정형 서술 구조가 필요하며 to부정사만 올 수 없다.'],
    'receipts가 복수라는 이유만으로 are를 고르지 않는다.', 'recommend that S + 동사원형; 수동은 be + p.p.')

add(29, 'The new delivery route has produced a ------- reduction in fuel costs.',
    ['considerably', 'consideration', 'considering', 'considerable'], 'D', 2, 'PART 5 - WORD FORM',
    '관사와 명사 사이에서 명사를 꾸미는 형용사를 찾는다.',
    'a + 빈칸 + reduction 구조이므로 형용사 considerable이 필요하다. 상당한 연료비 절감이라는 뜻이다.',
    ['부사로 명사 reduction을 직접 수식할 수 없다.', '명사로 a consideration reduction이라는 자연스러운 결합이 되지 않는다.', '고려하는이라는 분사 의미는 절감 규모를 나타내지 못한다.', '상당한이라는 형용사로 reduction의 규모를 설명한다.'],
    'considering이 익숙해도 문맥에서 절감 규모를 말하는지 본다.', 'a/an + 형용사 + 명사 구조를 먼저 확인한다.')

add(30, 'Please save a copy of the confirmation page; -------, you may be unable to verify your booking later.',
    ['moreover', 'otherwise', 'similarly', 'instead'], 'B', 2, 'PART 5 - LOGICAL CONNECTOR',
    '앞의 지시를 따르지 않았을 때의 결과는 otherwise로 연결한다.',
    '확인 페이지를 저장하라는 지시 뒤에 저장하지 않으면 예약을 확인하기 어려울 수 있다는 결과가 나온다.',
    ['추가 정보를 연결하며 지시 불이행의 결과를 나타내지 못한다.', '그렇지 않으면이라는 조건적 결과를 연결한다.', '유사한 사례가 제시되지 않아 의미가 맞지 않는다.', '대신이라는 대안이 아니라 지시를 안 따를 때의 결과이다.'],
    '세미콜론 뒤 부사들은 문법적으로 들어갈 수 있어도 논리 관계가 다르다.', '명령·권고 + otherwise = 따르지 않으면 생기는 결과.')

P6.append(dict(title='NOTICE', meta='Eastbridge Offices | Building access | October 12', nums=[31,32,33,34], paras=[
    'The main entrance to Eastbridge Offices ------- [31] from October 19 through October 23 while the automatic doors are replaced. During this period, please use the ------- [32] entrance on River Street.',
    'The River Street entrance has a ramp and will remain open during normal business hours. ------- [33], the front steps on Oak Avenue will be completely blocked, so they cannot be used as a shortcut.',
    'Employees carrying large packages may ask a security officer for assistance. ------- [34] This will allow the officer to meet you at the River Street entrance at the requested time.',
    'The visitor registration desk will move to the River Street lobby for the duration of the work. All other building services will operate as usual.'
]))
add(31, 'Choose the best answer for blank [31].', ['has closed','will be closed','closing','to close'], 'B', 1, 'PART 6 - VOICE AND TENSE',
    '예정된 출입구 폐쇄는 미래 수동태로 나타낸다.', '공지일은 10월 12일이고 작업 기간은 19~23일이다. 출입구가 폐쇄되는 대상이므로 will be closed가 맞다.',
    ['현재완료 능동형으로 앞으로 예정된 폐쇄 안내와 맞지 않는다.','미래 기간과 수동 의미를 모두 충족한다.','주절의 정형 동사가 없어 문장이 완성되지 않는다.','to부정사만으로 주절의 동사를 대신할 수 없다.'],
    '날짜를 읽지 않고 closed만 보고 과거 사건으로 판단하지 않는다.', '공지 시점과 작업 시점을 비교한 뒤 시제·태를 고른다.')
add(32, 'Choose the best answer for blank [32].', ['alternative','approximate','consecutive','competitive'], 'A', 2, 'PART 6 - VOCABULARY',
    '주 출입구를 대신하는 출입구는 alternative entrance이다.', '주 출입구가 막히므로 River Street 출입구를 대안으로 안내한다. alternative가 임시로 사용할 대체 경로의 역할을 설명한다.',
    ['대체 출입구라는 기능을 정확히 나타낸다.','대략적인이라는 뜻으로 출입구의 기능과 다르다.','연속적인이라는 뜻으로 맞지 않는다.','경쟁력 있는이라는 뜻으로 출입구 대체 안내와 맞지 않는다.'],
    '직역이 가능한 형용사라도 지문이 실제로 제공한 정보인지 확인한다.', '기존 수단을 대신한다면 alternative.')
add(33, 'Choose the best answer for blank [33].', ['For example','Therefore','Similarly','However'], 'D', 2, 'PART 6 - CONTEXT',
    '열린 출입구와 완전히 막힌 계단의 대비를 읽는다.', 'River Street 출입구는 이용 가능하지만 Oak Avenue 계단은 이용할 수 없다. 두 시설의 상반된 접근 가능성을 However로 연결한다.',
    ['뒤 내용은 열린 출입구의 예시가 아니다.','계단 차단이 앞 출입구 개방 때문에 생기는 결과가 아니다.','이용 가능 여부가 반대이므로 유사 관계가 아니다.','열린 경로와 막힌 경로를 대조한다.'],
    '같은 공사 주제라는 이유로 Similarly를 선택하지 않는다.', '연결어는 주제가 아니라 두 문장의 주장 관계로 판단한다.')
add(34, 'Choose the sentence that best fits blank [34].', [
    'The registration desk normally closes at six.',
    'Please call the security desk at least 15 minutes before you arrive.',
    'The new doors will reduce energy consumption.',
    'Packages left in the lobby will be returned to the sender.'], 'B', 3, 'PART 6 - SENTENCE INSERTION',
    '다음 문장의 This가 가리킬 구체적인 행동을 채운다.', '앞은 짐 운반 지원이고 뒤는 보안 직원이 요청 시각에 맞춰 만난다는 설명이다. 미리 전화하라는 문장이 This와 requested time의 선행 정보를 제공한다.',
    ['등록 창구 폐점 시각은 보안 직원과의 약속을 설정하지 못한다.','사전 전화가 요청 시각을 알려 주어 뒤 문장과 연결된다.','문 교체 효과는 짐 운반 지원과 인과적으로 이어지지 않는다.','짐 반송 규정은 직원이 도착 시각에 맞춰 만나는 이유가 되지 못한다.'],
    '앞 문장의 packages만 일치하는 선택지보다 뒤의 This와 time을 확인한다.', '문장 삽입은 앞의 주제 + 뒤의 지시어를 모두 연결한다.')

P6.append(dict(title='E-MAIL', meta='To: Lena Ortiz | From: Westhaven Supply | Subject: Order WS-284', nums=[35,36,37,38], paras=[
    'Dear Ms. Ortiz,',
    'Thank you for ordering 40 desk lamps for your new office. The arrival of our latest shipment ------- [35] by a customs inspection last week. As a result, we currently have only 25 of the lamps in stock.',
    'We can make a ------- [36] delivery of those 25 lamps on November 6 and send the remaining 15 on November 10. ------- [37] your staff orientation is scheduled for November 7, this arrangement would allow you to set up most of the workstations in time.',
    'You would pay only the delivery fee listed in your original order. ------- [38] Please reply by November 3 if you would like us to proceed with the two deliveries.',
    'Sincerely,<br/>Daniel Cho<br/>Customer Service, Westhaven Supply'
]))
add(35, 'Choose the best answer for blank [35].', ['was delayed','has delaying','delays','will delay'], 'A', 1, 'PART 6 - VERB FORM',
    '지난주 발생한 지연은 과거 수동태로 표현한다.', '주어 arrival은 검사를 하는 주체가 아니며 by a customs inspection이 지연 원인을 나타낸다. last week에 맞는 was delayed를 쓴다.',
    ['과거 시점과 지연을 당한 의미에 맞는다.','has 뒤 현재분사는 올바른 완료형이 아니다.','현재 능동형으로 과거 지연 상황과 맞지 않는다.','미래 능동형으로 last week와 맞지 않는다.'],
    'by 뒤가 사람이 아니어도 수동태의 원인이 될 수 있다.', '과거 시점 + 영향을 받은 주어: was/were + p.p.')
add(36, 'Choose the best answer for blank [36].', ['mutual','former','partial','annual'], 'C', 2, 'PART 6 - VOCABULARY AND NUMBERS',
    '전체 40개 중 25개를 먼저 보내는 것은 부분 배송이다.', '25개 선배송과 15개 후배송을 합치면 원래 주문 40개가 된다. partial은 전체 중 일부라는 뜻이다.',
    ['상호의라는 뜻으로 배송 수량을 설명하지 못한다.','이전의라는 뜻이며 예정된 배송을 나타내지 못한다.','주문 수량 일부의 배송이라는 의미이다.','연례의라는 뜻이며 배송 분할과 무관하다.'],
    'delivery만 보고 익숙한 수식어를 고르기 전에 수량 관계를 읽는다.', '전체와 첫 배송 수량을 비교한다.')
add(37, 'Choose the best answer for blank [37].', ['Unless','Even though','Whereas','Because'], 'D', 2, 'PART 6 - LOGIC',
    '오리엔테이션 날짜가 앞선 배송을 제안하는 이유가 된다.', '11월 7일 행사 전에 6일에 일부를 받으면 대부분의 자리를 준비할 수 있다. 행사 일정이 이 방안의 유용성을 설명하므로 Because가 맞다.',
    ['행사가 잡혀 있지 않으면이라는 조건은 실제 행사 일정과 충돌한다.','양보가 아니라 일정상 이점의 이유를 설명한다.','두 사실은 서로 대조되지 않으며 행사 일정이 선배송의 이점을 설명한다.','행사 날짜가 선배송의 실용적인 이유임을 나타낸다.'],
    '7일과 6일이 다르다는 표면적 차이를 대조 관계로 오해하지 않는다.', '연결어는 제안의 이유인지, 반대 조건인지 구분한다.')
add(38, 'Choose the sentence that best fits blank [38].', [
    'Our office will be closed throughout November.',
    'You may select a different lamp color after delivery.',
    'We will cover the shipping cost of the second delivery.',
    'A new invoice will double the original delivery fee.'], 'C', 3, 'PART 6 - SENTENCE INSERTION',
    '기존 배송료만 낸다는 약속을 구체적으로 뒷받침한다.', '첫 문장은 고객이 원래 배송료만 낸다고 한다. 업체가 두 번째 운송비를 부담한다는 문장이 분할 배송에 추가 비용이 없는 이유를 설명한다.',
    ['11월 배송 예정과 충돌하고 비용 설명을 잇지 못한다.','색상 변경은 앞의 배송료 설명과 관련 없다.','두 번째 배송비를 업체가 부담하여 원래 배송료만 청구된다.','배송료가 두 배라는 내용은 앞 문장과 모순된다.'],
    '추가 배송이 있다고 고객에게 추가 배송료가 생긴다고 추측하지 않는다.', '문장 삽입에서 비용·수량 약속의 일관성을 확인한다.')

P6.append(dict(title='STAFF MEMO', meta='From: Human Resources | Subject: Revised onboarding workshop', nums=[39,40,41,42], paras=[
    'All employees hired this quarter ------- [39] to attend the onboarding workshop on December 4. This session replaces the two shorter sessions previously offered each month.',
    'Please complete the online registration form ------- [40] to November 27. Registration gives the training team time to create your individual account. Employees who miss the deadline cannot attend the December 4 session. ------- [41], late registrants will need to wait for the next workshop in January.',
    'The morning activities include logging in to a practice account and submitting a sample expense claim. ------- [42] A limited number of loan devices are available, but they must be reserved on the registration form.',
    'Lunch will be provided. If you have dietary requirements, include them when you register.'
]))
add(39, 'Choose the best answer for blank [39].', ['requires','requiring','has required','are required'], 'D', 1, 'PART 6 - AGREEMENT AND VOICE',
    '복수 직원에게 참석 의무가 부과되므로 복수 수동태가 필요하다.', 'All employees가 주어이고 hired this quarter는 직원을 수식한다. be required to attend 구조에서 are required를 쓴다.',
    ['단수 능동형이며 직원들이 의무를 부과하는 뜻이 된다.','주절의 정형 동사가 없어진다.','단수 현재완료 능동으로 수와 태가 맞지 않는다.','복수 주어와 일치하고 참석 의무를 나타내는 수동 구조이다.'],
    'hired를 주절 동사로 착각하지 않는다.', '주어 뒤 과거분사 수식어를 걷어 내고 주절 동사를 찾는다.')
add(40, 'Choose the best answer for blank [40].', ['prior','preceding','ahead','advance'], 'A', 2, 'PART 6 - FIXED EXPRESSION',
    'to가 뒤에 주어졌다면 prior to라는 표현을 완성한다.', 'prior to November 27은 11월 27일 이전에라는 뜻이다. 다른 선택지는 이 의미로 to와 결합하지 않는다.',
    ['prior to가 ~이전에라는 고정 표현이다.','preceding은 이 의미로 명사구 앞에 직접 쓰며 to와 결합하지 않는다.','미리라는 뜻의 ahead는 of와 결합한다.','advance는 in advance of 등의 형태가 필요하다.'],
    '비슷한 의미의 시간 표현들이 같은 전치사와 결합한다고 생각하지 않는다.', '빈칸 뒤 전치사가 이미 있다면 표현 전체로 확인한다.')
add(41, 'Choose the best answer for blank [41].', ['Nevertheless','Consequently','In contrast','For instance'], 'B', 2, 'PART 6 - CONSEQUENCE',
    '등록 마감 초과와 다음 회차 대기는 원인·결과 관계이다.', '마감을 놓친 직원은 12월 회차에 참석하지 못한다. 따라서 1월 회차까지 기다려야 한다는 결과가 이어진다.',
    ['그럼에도 불구하고라는 양보가 아니라 규정의 직접 결과이다.','앞의 참석 불가 규정에서 생기는 결과를 연결한다.','서로 다른 대상을 대조하는 내용이 아니다.','일부 사례가 아니라 해당 직원 전체에게 적용되는 결과이다.'],
    'December와 January라는 다른 달이 나와도 대조가 되는 것은 아니다.', '앞 규칙 때문에 뒤 조치가 필요하면 결과 연결어.')
add(42, 'Choose the sentence that best fits blank [42].', [
    'The catering service offers several vegetarian dishes.',
    'Attendance certificates will be mailed in January.',
    'The workshop was first held more than ten years ago.',
    'For these activities, please bring a laptop with a wireless connection.'], 'D', 3, 'PART 6 - SENTENCE INSERTION',
    '온라인 실습과 대여 기기 안내 사이에 준비물 문장을 넣는다.', 'practice account와 expense claim 실습에는 접속 기기가 필요하다. 노트북을 지참하라는 문장 뒤에 loan devices 예외가 자연스럽게 이어진다.',
    ['식단은 다음 문단 주제이며 기기 대여를 설명하지 못한다.','수료증 발송은 실습 준비물과 연결되지 않는다.','행사의 역사는 앞뒤 실무 안내와 무관하다.','실습 준비물 안내가 뒤의 대여 기기 예외로 이어진다.'],
    '뒤 문장의 devices가 무엇을 대신하는지 확인한다.', '준비물 안내 뒤 대여·예외 규정이 이어지는지 본다.')

P6.append(dict(title='SERVICE UPDATE', meta='ClearDesk Online | Account dashboard | June 8', nums=[43,44,45,46], paras=[
    'Since last Monday, our development team ------- [43] a redesigned account dashboard with a group of volunteer customers. Testing is still in progress, and the update will be released to all users on June 15.',
    'The new design provides quicker ------- [44] to invoices and subscription settings. Most test users have reported that routine tasks take less time. ------- [45], older activity records will no longer appear on the main dashboard after the update.',
    'Records dated before January 1 will remain available through a separate archive page. ------- [46] To save a copy, open the archive page, choose a date range, and click Download.',
    'Your current subscription and payment settings will not change. Contact our support team if you need help locating a record.'
]))
add(43, 'Choose the best answer for blank [43].', ['had tested','has been testing','will be tested','testing'], 'B', 2, 'PART 6 - TENSE IN CONTEXT',
    'Since와 still in progress를 함께 읽어 진행 중인 시험을 판단한다.', '지난 월요일 시작한 테스트가 지금도 진행 중이다. 개발팀이 시험하는 주체이므로 능동 현재완료진행이 맞다.',
    ['과거 기준점 이전 완료를 나타내며 현재도 진행 중이라는 내용과 다르다.','과거 시작부터 현재까지 계속되는 테스트를 나타낸다.','미래 수동형으로 팀이 시험당하는 뜻이 되고 since와도 맞지 않는다.','정형 동사가 없어 문장이 완성되지 않는다.'],
    '출시 예정 날짜만 보고 테스트까지 미래형으로 고르지 않는다.', '테스트 진행 시점과 출시 시점을 분리한다.')
add(44, 'Choose the best answer for blank [44].', ['accessed','accessible','access','accessibly'], 'C', 1, 'PART 6 - WORD FORM',
    '형용사 quicker의 수식을 받는 명사 access가 필요하다.', 'provides의 목적어는 quicker access이고 to invoices가 접근 대상을 덧붙인다. access는 이 용법에서 불가산명사이다.',
    ['과거분사로 quicker의 수식을 받는 목적어 명사를 만들지 못한다.','형용사이므로 목적어가 되는 명사 자리를 채우지 못한다.','quicker access to라는 명사구를 완성한다.','부사이므로 목적어 명사 자리에 올 수 없다.'],
    'to만 보고 부정사를 떠올리지 말고 access to라는 명사 결합을 본다.', 'provide + 형용사 + 명사 + to 대상.')
add(45, 'Choose the best answer for blank [45].', ['However','Likewise','As a result','For this reason'], 'A', 2, 'PART 6 - CONTRAST',
    '편의성 개선 뒤 사용자가 알아야 할 제한이 나온다.', '일상 작업은 빨라졌지만 오래된 기록은 메인 화면에서 사라진다. 전반적 장점과 제한 사항을 대조하는 However가 적절하다.',
    ['개선 효과와 기록 표시 제한을 대조한다.','유사한 장점을 덧붙이는 내용이 아니다.','사용자 보고 때문에 기록을 숨기는 인과관계가 제시되지 않았다.','앞 사실을 이유로 기록 표시를 바꾼다고 말하지 않는다.'],
    '시간 순서상 업데이트 뒤 생기는 일이라고 모두 인과 연결어를 쓰지 않는다.', '장점 뒤 제한·주의사항이면 대조를 검토한다.')
add(46, 'Choose the sentence that best fits blank [46].', [
    'These records can also be exported as a file.',
    'All archived records will be permanently deleted on June 15.',
    'The volunteers must create a new paid subscription.',
    'No changes have been made to the dashboard layout.'], 'A', 3, 'PART 6 - SENTENCE INSERTION',
    '기록 보관 설명과 Download 절차 사이에 파일 내보내기 기능을 소개한다.', 'These records는 1월 1일 이전 기록을 가리킨다. 파일로 내보낼 수 있다는 문장이 뒤의 사본 저장 절차를 소개한다.',
    ['보관 기록을 파일로 저장할 수 있다는 소개 뒤에 다운로드 방법이 이어진다.','기록이 별도 보관 페이지에 남는다는 앞 문장과 모순된다.','지원자 유료 구독은 기록 저장 절차와 무관하다.','새 디자인을 시험·출시한다는 공지와 충돌한다.'],
    '앞 문장만 그럴듯한 선택지보다 뒤의 To save a copy와 이어지는지 본다.', '기능 소개 → 조작 절차라는 흐름을 확인한다.')

P7.append(dict(kind='Single Passage', title='Riverton Library', nums=[47,48,49], docs=[dict(label='NOTICE', meta='Riverton Library | Room reservations', paras=[
    '[1] Starting September 1, library members may reserve a study room up to seven days ahead through the library website. Each reservation is limited to two hours. Members may hold only one future reservation at a time.',
    '[2] If you arrive more than 15 minutes late, your booking will be released to other users. A reservation can be canceled online at any time before its start time. No payment is required to use a room.',
    '[3] The second-floor study rooms are being repainted and will remain closed through September 12. During this period, all reservations will be assigned to rooms on the ground floor.',
    '[4] Please ask at the service desk if you need help making a reservation.'
])]))
add(47, 'What is the main purpose of the notice?', [
    'To announce a change in library membership fees', 'To explain study-room reservation procedures',
    'To recruit volunteers for a painting project', 'To advertise a new branch of the library'], 'B', 1, 'PART 7 - PURPOSE',
    '첫 문장의 예약 안내를 나머지 규정과 묶어 목적을 판단한다.', '예약 방법, 시간 제한, 지각·취소 규정, 임시 배정 장소를 안내하는 글이다. 도색은 예약 운영에 영향을 주는 부수 정보이다.',
    ['회비 변경은 없다.', '예약 이용 절차를 안내하는 전체 내용과 일치한다.', '도색 인력 모집은 없다.', '새 지점 홍보가 아니다.'],
    '눈에 띄는 도색 정보 하나를 글 전체의 목적으로 확대하지 않는다.', '목적은 여러 문단을 포괄하는 선택지를 고른다.',
    evidence=[('Notice, paragraph 1', 'Starting September 1, library members may reserve a study room up to seven days ahead through the library website.')])
add(48, 'What is NOT mentioned as a condition for using a study room?', [
    'A limit on the length of a reservation', 'A limit on future reservations',
    'Loss of a booking after a late arrival', 'A requirement to leave a refundable deposit'], 'D', 2, 'PART 7 - NOT',
    'NOT 문제는 세 선택지의 근거를 확인하고 남은 하나를 고른다.', '2시간 제한, 미래 예약 1건 제한, 15분 초과 지각 시 예약 해제는 모두 명시되어 있다. 보증금 요구는 없고 오히려 무료라고 한다.',
    ['1문단에 2시간 제한이 있다.', '1문단에 미래 예약 1건 제한이 있다.', '2문단에 15분 초과 지각 시 해제가 있다.', '보증금 요구는 없으며 무료 이용 규정과도 어긋난다.'],
    '현실의 일반적인 예약 관행을 지문 규정에 덧붙이지 않는다.', 'NOT은 선택지마다 근거를 표시해 소거한다.',
    evidence=[('Notice, paragraphs 1-2', 'Each reservation is limited to two hours.'), ('Notice, paragraph 2', 'No payment is required to use a room.')])
add(49, 'In which position marked [1], [2], [3], and [4] does the following sentence best belong? "These rooms can be reached without using the stairs or the elevator."',
    ['[1]', '[2]', '[3]', '[4]'], 'D', 3, 'PART 7 - SENTENCE POSITION',
    'These rooms의 지시 대상과 접근 경로가 함께 맞는 위치를 찾는다.', '3문단 마지막에서 ground floor의 방을 소개한다. 바로 뒤 [4]에 넣으면 These rooms가 지상층 방을 가리키고 계단·엘리베이터가 불필요한 이유도 설명된다.',
    ['앞에 These rooms가 가리킬 방 정보가 없다.', '예약 제한 뒤에는 지상층 방이라는 접근 경로 근거가 없다.', '바로 뒤에 2층 방이 나와 계단·엘리베이터가 필요 없다는 설명과 맞지 않는다.', '바로 앞 ground-floor rooms를 받아 접근성을 설명한다.'],
    'rooms라는 명사 반복만 보지 말고 위치 정보까지 연결한다.', '지시어의 선행사 + 공간·시간 논리를 함께 확인한다.',
    evidence=[('Notice, paragraph 3, final sentence', 'During this period, all reservations will be assigned to rooms on the ground floor.')])

P7.append(dict(kind='Single Passage', title='Project chat', nums=[50,51,52], docs=[dict(label='ONLINE CHAT', meta='Harbor Design | June 3', paras=[
    '<b>9:05 | Maya:</b> The client likes the brochure layout, but they want the price chart enlarged. Can you send a revised file before noon?',
    '<b>9:08 | Leo:</b> Yes. I will need to move the product photos to the back page. Has the print shop confirmed its deadline?',
    '<b>9:10 | Maya:</b> They can accept the file by 3 p.m. tomorrow and still have the brochures ready for Friday\'s event.',
    '<b>9:11 | Leo:</b> That gives us some breathing room. I can send you a draft at 11 today, but I would prefer not to release the final file until the client checks the new chart.',
    '<b>9:14 | Maya:</b> Agreed. I will call the client as soon as your draft arrives. Please leave the cover exactly as it is.'
])]))
add(50, 'What is suggested about Leo?', [
    'He is responsible for revising a brochure.', 'He operates the printing equipment.',
    'He has postponed the client\'s event.', 'He has already received final approval.'], 'A', 2, 'PART 7 - INFERENCE',
    '인물의 실제 작업 발언에서 담당 업무를 추론한다.', 'Leo는 사진을 옮기고 수정 초안을 보낼 수 있다고 한다. 이를 통해 브로슈어 수정 담당임을 알 수 있으며 직책이나 소속까지 확대할 필요는 없다.',
    ['사진 이동과 초안 전송 발언이 수정 담당임을 뒷받침한다.', '인쇄소는 별도로 언급되며 Leo의 장비 운영 근거는 없다.', '행사 연기는 없다.', '고객의 새 차트 검토를 기다려야 한다.'],
    'print shop이 등장해도 화자가 인쇄소 직원이라고 단정하지 않는다.', '추론은 발언이 직접 뒷받침하는 최소 범위만 고른다.',
    evidence=[('Chat, Leo at 9:08', 'I will need to move the product photos to the back page.'), ('Chat, Leo at 9:11', 'I can send you a draft at 11 today')])
add(51, 'At 9:11, what does Leo mean when he writes, "That gives us some breathing room"?', [
    'The brochure needs more empty space.', 'The team should take a lunch break.',
    'There is additional time to complete the revisions.', 'The event venue can hold more people.'], 'C', 2, 'PART 7 - IMPLIED MEANING',
    '관용 표현은 직전 발언이 제공한 상황으로 해석한다.', '직전 발언에서 인쇄소가 내일 오후 3시까지 파일을 받는다고 한다. breathing room은 수정과 고객 검토를 할 시간적 여유를 뜻한다.',
    ['레이아웃 여백의 문자적 의미가 아니다.', '휴식 제안이 없다.', '내일까지 제출할 수 있어 수정 시간을 확보했다는 뜻이다.', '행사장 정원에 관한 내용은 없다.'],
    '디자인 주제라는 이유로 room을 지면의 빈 공간으로만 해석하지 않는다.', '표현 의미는 직전 질문·답변의 기능으로 확인한다.',
    evidence=[('Chat, Maya at 9:10', 'They can accept the file by 3 p.m. tomorrow and still have the brochures ready for Friday\'s event.')])
add(52, 'What does Maya ask Leo to keep unchanged?', [
    'The size of the price chart', 'The brochure cover', 'The placement of the product photos', 'The print shop\'s delivery address'], 'B', 1, 'PART 7 - DETAIL',
    'leave ... exactly as it is를 unchanged로 바꿔 읽는다.', 'Maya의 마지막 메시지에서 cover를 그대로 두라고 한다. 차트와 제품 사진은 수정 대상이다.',
    ['차트는 확대 요청 대상이다.', '마지막 메시지에서 표지를 그대로 두라고 한다.', '사진은 뒷면으로 이동할 예정이다.', '배송 주소는 언급되지 않는다.'],
    '앞에서 수정한 요소를 그대로 유지할 요소와 혼동하지 않는다.', 'change / keep unchanged처럼 질문의 방향을 확인한다.',
    evidence=[('Chat, Maya at 9:14', 'Please leave the cover exactly as it is.')])

P7.append(dict(kind='Double Passage', title='Hotel booking', nums=[53,54,55], docs=[
    dict(label='HOTEL OFFER', meta='Lakeview Hotel | Autumn Business Package', paras=[
        'The Autumn Business Package costs $180 per room per night for stays from October 1 through November 30. The rate includes breakfast and a meeting room for up to eight people for two hours during the stay. Additional meeting-room time costs $35 per hour.',
        'A booking deposit equal to one night\'s room rate is required. Cancel at least 48 hours before the scheduled 3 p.m. arrival time for a full deposit refund. Later cancellations receive a 50 percent deposit refund. Parking costs $15 per day and is not included.'
    ]),
    dict(label='E-MAIL', meta='To: Lakeview Hotel | From: Priya Shah | Sent: October 14, 10 a.m.', paras=[
        'I booked two package rooms for one night, with arrival on October 15 at 3 p.m., and paid both deposits. Please cancel one room because a colleague can no longer travel. Keep the other room for me.',
        'I will still host a meeting for six people from 10 a.m. to 1 p.m. on October 16. Please reserve the meeting room for all three hours. I will arrive by train and will not need parking.'
    ])
]))
add(53, 'What will Ms. Shah have to pay in addition to the package room rate?', [
    'Breakfast for one guest', 'Parking for one day', 'A fee for six meeting participants', 'One additional hour of meeting-room use'], 'D', 2, 'PART 7 - CROSS-REFERENCE',
    '포함 시간과 실제 예약 시간을 비교한다.', '상품은 회의실 2시간을 포함하지만 Shah는 10시~13시의 3시간을 요청했다. 1시간 추가 요금이 필요하다. 인원 6명은 정원 8명 이내이다.',
    ['조식은 상품에 포함된다.', '기차로 와 주차가 필요 없다고 했다.', '6명은 포함 정원 8명 이내이다.', '요청 3시간에서 포함 2시간을 빼면 1시간이 추가된다.'],
    '투숙일과 회의일이 다르다는 이유만으로 회의실 혜택을 부정하지 않는다. 1박 체류 중이다.', '포함 범위와 실제 이용량을 같은 단위로 비교한다.',
    evidence=[('Offer, paragraph 1', 'a meeting room for up to eight people for two hours during the stay'), ('E-mail, paragraph 2', 'from 10 a.m. to 1 p.m. on October 16')])
add(54, 'How much of the deposit for the canceled room will Ms. Shah receive back?', ['$90', '$180', '$35', '$360'], 'A', 3, 'PART 7 - DATE AND AMOUNT',
    '취소 시차를 계산한 뒤 취소 객실 1개의 보증금에만 비율을 적용한다.', '10월 14일 오전 10시에서 15일 오후 3시까지는 29시간으로 48시간 미만이다. 취소 객실 보증금 180달러의 50%인 90달러를 돌려받는다.',
    ['늦은 취소의 50% × 취소 객실 보증금 $180 = $90이다.', '48시간 이상 앞선 취소에만 전액 환불된다.', '회의실 추가 1시간 요금이며 보증금 환불액이 아니다.', '두 객실 보증금 합계이며 두 객실을 모두 취소하지 않았다.'],
    '총 보증금 360달러에 50%를 적용하지 않는다. 취소 대상은 1객실이다.', '조건 판단 → 적용 대상 확정 → 금액 계산 순서로 푼다.',
    evidence=[('Offer, paragraph 2', 'Later cancellations receive a 50 percent deposit refund.'), ('E-mail, paragraph 1', 'Please cancel one room because a colleague can no longer travel.')])
add(55, 'What is suggested about Ms. Shah\'s original reservation?', [
    'It included a discounted parking space.', 'It was for two nights in one room.',
    'It included a room intended for another traveler.', 'It was made after the cancellation deadline.'], 'C', 3, 'PART 7 - INFERENCE',
    '두 객실 예약과 동료 불참이라는 취소 이유를 연결한다.', '한 객실은 자신을 위해 유지하고 동료가 여행하지 못해 다른 객실을 취소한다. 원래 예약에 다른 여행자용 객실이 있었다는 최소 추론이 성립한다.',
    ['주차 할인은 없다.', '두 객실 1박이라고 명시했다.', '동료 불참으로 한 객실을 취소하고 다른 객실은 본인이 사용한다.', '메일 날짜는 취소 요청일이며 최초 예약일은 알 수 없다.'],
    '메일을 보낸 날짜를 원래 예약한 날짜로 바꾸어 읽지 않는다.', '최초 예약·변경 요청·이용 날짜를 구분한다.',
    evidence=[('E-mail, paragraph 1', 'I booked two package rooms for one night'), ('E-mail, paragraph 1', 'Please cancel one room because a colleague can no longer travel. Keep the other room for me.')])

P7.append(dict(kind='Double Passage', title='Small-business forum', nums=[56,57,58], docs=[
    dict(label='EVENT PROGRAM', meta='Northbank Small-Business Forum | May 22 | Civic Hall', paras=[
        '<b>9:00-9:45 | Opening keynote:</b> Building Customer Trust. Main Auditorium.',
        '<b>10:00-11:00 | Workshop A:</b> Photographing Products with a Phone. Studio 1. Participants should bring a smartphone.',
        '<b>10:00-11:00 | Workshop B:</b> Managing Seasonal Cash Flow. Room 204. No equipment is required.',
        '<b>11:15-12:15 | Workshop C:</b> Writing Effective Online Listings. Room 204.',
        'The $60 admission fee includes one morning workshop and lunch. An additional workshop costs $15. Register online by May 18.'
    ]),
    dict(label='E-MAIL', meta='To: Forum registrations | From: Owen Price | Sent: May 16', paras=[
        'I registered for Workshop B and paid the $60 fee. My business partner will handle our finances this year, so I would like to switch to the workshop on product photography. I can bring my phone.',
        'I also want to attend Workshop C after that. Please let me know how to pay the additional fee. My partner will not attend the forum. Please confirm the change before I book my train ticket.'
    ])
]))
add(56, 'Which workshop does Mr. Price want to attend at 10 a.m.?', [
    'Building Customer Trust', 'Photographing Products with a Phone', 'Managing Seasonal Cash Flow', 'Writing Effective Online Listings'], 'B', 2, 'PART 7 - CROSS-REFERENCE',
    '변경 전 등록 내역과 변경 후 희망 내역을 분리한다.', '이메일에서 B를 사진 촬영 워크숍으로 바꾸고 싶다고 한다. 프로그램에서 해당 워크숍은 10시의 A이다.',
    ['9시 기조연설이다.', '변경 요청 대상인 10시 Workshop A이다.', '처음 등록한 B이며 지금은 변경을 요청한다.', '11시 15분의 C이며 추가로 듣고 싶어 한다.'],
    'registered라는 과거 정보만 보고 최종 희망을 놓치지 않는다.', '현재 질문이 최초 등록인지 변경 희망인지 확인한다.',
    evidence=[('E-mail, paragraph 1', 'I would like to switch to the workshop on product photography.'), ('Program, Workshop A', '10:00-11:00 | Workshop A: Photographing Products with a Phone.')])
add(57, 'Why does Mr. Price mention his business partner?', [
    'To explain why he wants to change workshops', 'To request a second admission ticket',
    'To ask for a discount for two attendees', 'To arrange a shared train journey'], 'A', 3, 'PART 7 - PURPOSE OF A DETAIL',
    '인물 언급의 목적은 바로 뒤 요청과의 인과관계로 읽는다.', '동료가 올해 재무를 담당하므로 본인은 현금 흐름 수업 대신 제품 촬영 수업을 듣겠다는 이유를 설명한다. 동료는 행사에 참석하지 않는다.',
    ['재무 업무 분담이 워크숍 변경의 이유이다.', '동료가 불참하므로 두 번째 표를 요청하지 않는다.', '단체 할인은 요청하지 않는다.', '기차표는 본인의 변경 확인 이후 계획이다.'],
    'partner가 나오면 두 명 예약이라고 단정하지 않는다.', 'Why mention은 해당 정보가 뒷문장의 요청에 하는 역할을 본다.',
    evidence=[('E-mail, paragraph 1', 'My business partner will handle our finances this year, so I would like to switch to the workshop on product photography.')])
add(58, 'What is NOT included in the $60 admission fee?', ['Lunch', 'One morning workshop', 'A second workshop', 'Admission to the forum'], 'C', 2, 'PART 7 - NOT AND FEES',
    '기본 요금에 포함되는 것과 추가 요금 항목을 나눈다.', '60달러는 행사 입장과 오전 워크숍 1개, 점심을 포함한다. 두 번째 워크숍은 15달러 추가이다.',
    ['점심은 포함이라고 명시되어 있다.', '오전 워크숍 1개는 포함이다.', '추가 워크숍에는 $15를 별도로 낸다.', '60달러 자체가 행사 입장료이다.'],
    'morning workshop이라는 말이 오전 워크숍 전부를 뜻하지 않는다.', 'one, additional 같은 수량 한정어에 표시한다.',
    evidence=[('Program, final paragraph', 'The $60 admission fee includes one morning workshop and lunch. An additional workshop costs $15.')])

P7.append(dict(kind='Triple Passage', title='Office furniture order', nums=[59,60,61,62], split=True, docs=[
    dict(label='CATALOG', meta='Beacon Office Furniture | Compact Task Chair', paras=[
        'Our Compact Task Chair is designed for small work areas and includes adjustable seat height and a two-year warranty. It is available in gray or blue at $85 per chair. Both colors have the same specifications and price.',
        'Orders of six or more chairs qualify for a 5 percent discount on merchandise only. Standard delivery costs $30 per order. Express delivery adds $20 to the standard delivery fee. All listed prices include tax; no other charges apply.'
    ]),
    dict(label='CUSTOMER E-MAIL', meta='To: Beacon sales | From: Naomi Park | Sent: May 6', paras=[
        'Please supply eight gray Compact Task Chairs for our new training room. If gray is unavailable, blue is acceptable, provided the specifications and price are the same.',
        'The chairs must arrive no later than May 10 because staff training begins the following morning. Please choose the least expensive delivery service that meets this deadline. Our total budget, including delivery, is $700. Please confirm the color and expected arrival date before dispatch.'
    ]),
    dict(label='ORDER CONFIRMATION', meta='Beacon Office Furniture | Order B-614 | May 7', paras=[
        '<b>Customer:</b> Naomi Park<br/><b>Model:</b> Compact Task Chair<br/><b>Quantity:</b> 8<br/><b>Color:</b> Blue; gray is currently out of stock.',
        'The catalog\'s volume discount has been applied to the merchandise. Express delivery has been selected. The standard delivery fee and the express supplement will both be charged.',
        '<b>Expected arrival:</b> May 9. Standard delivery for this order would arrive on May 14. Please reply today if any details need correction.'
    ])
]))
add(59, 'Why does the confirmation list blue chairs?', [
    'Blue chairs are less expensive.', 'Blue chairs can be assembled more quickly.',
    'Ms. Park requested a different model.', 'Gray chairs are unavailable and Ms. Park allowed a substitute.'], 'D', 2, 'PART 7 - CROSS-REFERENCE',
    '고객의 대체 허용 조건과 공급업체의 재고 정보를 연결한다.', 'Park는 동일 사양·가격이면 파란색을 허용했고 확인서는 회색 품절을 알린다. 카탈로그는 두 색의 사양·가격이 같다고 확인해 준다.',
    ['두 색의 가격은 같다.', '조립 속도 차이는 없다.', '모델 변경을 요청하지 않았다.', '회색 품절과 파란색 대체 허용 조건이 모두 충족된다.'],
    '색상 변경을 모델 변경이나 가격 할인으로 확대하지 않는다.', '대체품은 허용 조건과 실제 공급 사유를 함께 확인한다.',
    evidence=[('Catalog, paragraph 1', 'Both colors have the same specifications and price.'), ('Customer e-mail, paragraph 1', 'If gray is unavailable, blue is acceptable'), ('Confirmation, item details', 'Blue; gray is currently out of stock.')])
add(60, 'What is the merchandise charge after the volume discount, before delivery fees?', ['$680', '$650', '$646', '$696'], 'C', 2, 'PART 7 - AMOUNT',
    '상품 금액에만 할인율을 적용하고 배송비는 제외한다.', '8개 × 85달러 = 680달러이다. 6개 이상이므로 5% 할인 34달러를 빼면 상품 금액은 646달러이다.',
    ['할인 전 상품 금액이다.', '배송비 $30를 할인액처럼 뺀 값이다.', '$680 × 0.95 = $646으로 상품 할인 후 금액이다.', '배송비 $50까지 더한 총액으로 질문 범위를 넘는다.'],
    'before delivery fees라는 질문 범위를 읽고 배송비를 합치지 않는다.', '상품 할인과 배송비를 별도로 계산한다.',
    evidence=[('Catalog, paragraph 1', '$85 per chair'), ('Catalog, paragraph 2', 'a 5 percent discount on merchandise only'), ('Confirmation, item details', 'Quantity: 8')])
add(61, 'Why was express delivery selected?', [
    'Standard delivery would miss Ms. Park\'s deadline.', 'The volume discount applies only to express orders.',
    'Ms. Park asked for delivery before May 7.', 'Express delivery avoids the standard delivery fee.'], 'A', 3, 'PART 7 - DATE CROSS-REFERENCE',
    '필수 도착일과 두 배송 방식의 예상 도착일을 비교한다.', '필수 도착일은 5월 10일이다. 일반 배송은 14일로 늦고 특급은 9일로 기한을 지킨다. 최소 비용 조건은 기한을 만족하는 방식들 중에서 적용한다.',
    ['일반은 14일 도착으로 10일 기한을 넘는다.', '수량 할인은 배송 방식과 무관하다.', '요청 기한은 10일이며 7일 전 도착이 아니다.', '특급은 일반 배송비에 추가 요금을 더하는 방식이다.'],
    'least expensive만 보고 기한을 못 지키는 일반 배송을 고르지 않는다.', '필수 조건을 먼저 걸러 낸 뒤 비용을 비교한다.',
    evidence=[('Customer e-mail, paragraph 2', 'The chairs must arrive no later than May 10'), ('Confirmation, final paragraph', 'Standard delivery for this order would arrive on May 14.')])
add(62, 'What is suggested about the confirmed order when all charges are included?', [
    'It exceeds the budget by $30.', 'It leaves $4 of Ms. Park\'s budget unused.',
    'It requires the volume discount to be applied to delivery.', 'It costs exactly $700.'], 'B', 3, 'PART 7 - THREE-TEXT INFERENCE',
    '세 자료의 단가·할인·배송 선택·예산을 한 계산에 합친다.', '카탈로그의 85달러와 5% 할인, 확인서의 8개 및 특급 선택으로 646 + 30 + 20 = 696달러이다. 이메일의 예산 700달러에서 4달러가 남는다.',
    ['총액은 $696으로 예산을 넘지 않는다.', '상품 $646 + 배송 $50 = $696, 예산에서 $4가 남는다.', '할인은 상품에만 적용되며 배송 할인 없이도 예산 안이다.', '예산 한도와 실제 청구액을 혼동한 값이다.'],
    '특급 20달러를 전체 배송비로 보거나 배송비에 5% 할인하지 않는다.', '각 금액의 적용 범위를 적고 마지막에 예산과 비교한다.',
    evidence=[('Catalog, paragraph 2', 'Express delivery adds $20 to the standard delivery fee.'), ('Customer e-mail, paragraph 2', 'Our total budget, including delivery, is $700.'), ('Confirmation, paragraph 2', 'The catalog\'s volume discount has been applied to the merchandise.')])

P7.append(dict(kind='Triple Passage', title='Recruitment schedule', nums=[63,64,65,66], split=True, docs=[
    dict(label='JOB NOTICE', meta='Meridian Arts Center | Visitor Services Coordinator', paras=[
        'Meridian Arts Center seeks a full-time visitor services coordinator to supervise the front desk and train volunteer guides. At least two years of customer service experience is required. Museum experience is welcome but not essential.',
        'The regular schedule is Tuesday through Saturday, 9 a.m. to 5 p.m. The center is closed on Mondays. Applications must be received by August 8. Selected applicants will be invited to an interview on August 14 or August 15. Please state any interview-date restrictions in your application.'
    ]),
    dict(label='APPLICATION E-MAIL', meta='To: Meridian recruitment | From: Alex Rivera | Sent: August 6', paras=[
        'I am applying for the visitor services coordinator position. I have worked at a hotel reception desk for three years and have trained new employees. Although I have not worked in a museum, I regularly volunteer at community events.',
        'I can work the advertised weekly schedule. I will be out of town from August 13 through August 14, but I am available all day on August 15. My résumé and references are attached.'
    ]),
    dict(label='RECRUITMENT E-MAIL', meta='To: Alex Rivera | From: Meridian recruitment | Sent: August 10', paras=[
        'Thank you for your application. We would like to interview you on August 14 at 10 a.m. The interview will last 45 minutes and will take place in our second-floor meeting room.',
        'Please confirm by August 11. If the proposed appointment conflicts with a restriction you previously reported, contact me directly rather than selecting a time through the online booking page. I can check the remaining appointments for the other interview day.',
        'Best regards,<br/>Tessa Lin<br/>Recruitment coordinator'
    ])
]))
add(63, 'What is required for the advertised position?', [
    'A degree in museum studies', 'Availability to work every Monday', 'Previous employment at an arts center', 'At least two years of customer service experience'], 'D', 1, 'PART 7 - DETAIL',
    '필수 조건과 우대 조건을 구분한다.', '공고는 고객 서비스 경력 2년 이상을 요구하고 박물관 경력은 필수는 아니라고 한다. 월요일에는 센터가 문을 닫는다.',
    ['전공·학위 조건은 없다.', '월요일은 휴관일이다.', '박물관 경력조차 필수가 아니다.', '공고에 명시된 필수 경력 조건이다.'],
    'welcome과 required를 같은 강도의 조건으로 읽지 않는다.', 'required / essential / welcome의 의무 수준을 구별한다.',
    evidence=[('Job notice, paragraph 1', 'At least two years of customer service experience is required.')])
add(64, 'What is indicated about Mr. Rivera\'s application?', [
    'It was sent before the application deadline.', 'It requested a part-time schedule.',
    'It was missing his references.', 'It stated that he had museum experience.'], 'A', 2, 'PART 7 - CROSS-REFERENCE',
    '공고 마감일과 지원 메일 발송일을 대조한다.', '공고 마감은 8월 8일이고 지원 메일은 6일에 발송되었다. 다른 선택지는 지원 내용과 반대이다.',
    ['8월 6일 발송으로 8일 마감 전이다.', '공고의 주간 근무 일정대로 일할 수 있다고 했다.', '추천인 정보가 첨부되었다고 했다.', '박물관에서 일한 적이 없다고 밝혔다.'],
    '지원 메일 6일, 채용팀 회신 10일, 확인 기한 11일을 섞지 않는다.', '날짜를 문서와 사건에 붙여 기록한다.',
    evidence=[('Job notice, paragraph 2', 'Applications must be received by August 8.'), ('Application e-mail, header', 'Sent: August 6')])
add(65, 'Which originally announced interview date matches Mr. Rivera\'s stated availability?', ['August 8', 'August 11', 'August 14', 'August 15'], 'D', 3, 'PART 7 - THREE-TEXT SCHEDULE',
    '공식 면접 날짜 중 지원자의 불가 기간을 제외한다.', '공고의 면접일은 14일 또는 15일이다. 지원자는 13~14일 외지에 있고 15일은 가능하다. 회신의 14일 예약은 이 제약과 충돌한다.',
    ['지원 마감일이며 면접일이 아니다.', '참석 확인 기한이며 면접일이 아니다.', '채용팀 제안일이지만 지원자가 외지에 있다.', '공고의 면접일이면서 지원자가 하루 종일 가능하다고 밝힌 날짜이다.'],
    '채용팀이 잡은 날짜라는 이유로 지원자 가능 날짜와 같다고 생각하지 않는다.', '예정된 일정과 개인 제약의 교집합을 찾는다.',
    evidence=[('Job notice, paragraph 2', 'an interview on August 14 or August 15'), ('Application e-mail, paragraph 2', 'I am available all day on August 15.'), ('Recruitment e-mail, paragraph 1', 'interview you on August 14 at 10 a.m.')])
add(66, 'What should Mr. Rivera most likely do next?', [
    'Submit a new application after August 11.', 'Select an August 14 appointment online.',
    'Contact Ms. Lin directly about changing the interview date.', 'Ask the center to create a Monday work schedule.'], 'C', 3, 'PART 7 - INFERENCE AND NEXT ACTION',
    '이전에 알린 제약과 충돌할 때 적용되는 연락 절차를 따른다.', '지원자는 14일 불가를 이미 알렸고 회신은 바로 그날 면접을 제안했다. 이런 경우 온라인 페이지 대신 담당자에게 직접 연락하라고 안내한다. 15일 잔여 시간은 확인이 필요하다.',
    ['새 지원서 제출 지시는 없으며 마감도 지난다.', '불가 날짜와 충돌하고 직접 연락 지시도 어긴다.', '기존 제약과 충돌할 때의 명시된 절차에 맞는다.', '근무 일정 변경 요청은 필요 없다.'],
    '15일 면접이 자동 확정되었다고 추론하지 않는다. 가능한 날짜와 예약 확정은 다르다.', '조건 발생 여부를 확인한 뒤 해당 행동 지시를 적용한다.',
    evidence=[('Recruitment e-mail, paragraph 2', 'If the proposed appointment conflicts with a restriction you previously reported, contact me directly rather than selecting a time through the online booking page.')])

P7.append(dict(kind='Single Passage', title='Restaurant reopening', nums=[67,68], docs=[dict(label='CUSTOMER NOTICE', meta='Juniper Kitchen | Reopening announcement', paras=[
    'Juniper Kitchen will reopen on April 18 after a three-week kitchen renovation. Lunch service will resume that day, but dinner service will not begin until April 25 while the new evening staff complete their training.',
    'To thank our regular customers, we are offering a complimentary dessert with every lunch entrée purchased from April 18 through April 24. The offer applies to meals eaten in the restaurant and cannot be used for takeaway orders.',
    'Our menu will feature several new vegetarian dishes alongside our usual favorites. Customers may book tables online now. Gift cards purchased before the renovation will remain valid after reopening.'
])]))
add(67, 'When will dinner service resume?', ['April 18', 'April 24', 'April 25', 'May 18'], 'C', 1, 'PART 7 - DETAIL AND DATE',
    '재개장일과 저녁 서비스 시작일을 분리한다.', '4월 18일에는 점심만 재개하고 저녁은 직원 교육이 끝난 뒤 25일부터 시작한다.',
    ['식당 재개장과 점심 서비스 시작일이다.', '디저트 행사 마지막 날이다.', '저녁 서비스 시작일로 명시되어 있다.', '이 날짜는 지문에 없다.'],
    'reopen 날짜를 모든 서비스의 재개일로 일반화하지 않는다.', '날짜마다 어떤 서비스가 시작·종료되는지 연결한다.',
    evidence=[('Notice, paragraph 1', 'dinner service will not begin until April 25')])
add(68, 'What is suggested about a customer who buys a takeaway lunch on April 20?', [
    'The customer will receive a free dessert.', 'The customer will not qualify for the dessert offer.',
    'The customer must use an old gift card.', 'The customer can order only vegetarian food.'], 'B', 2, 'PART 7 - INFERENCE AND EXCEPTION',
    '행사 기간을 충족해도 이용 방식의 예외를 적용한다.', '4월 20일은 행사 기간 안이지만 포장 주문은 제외된다. 날짜 조건과 매장 식사 조건을 모두 충족해야 한다.',
    ['기간 안이어도 takeaway 제외 규정이 적용된다.', '포장 주문은 행사 적용 대상이 아니다.', '기프트카드 사용 의무는 없다.', '기존 메뉴도 제공되므로 채식 메뉴만 가능한 것은 아니다.'],
    '날짜 하나만 맞으면 모든 혜택이 적용된다고 판단하지 않는다.', '할인·혜택은 기간, 대상, 이용 방식 조건을 모두 확인한다.',
    evidence=[('Notice, paragraph 2', 'The offer applies to meals eaten in the restaurant and cannot be used for takeaway orders.')])

P7.append(dict(kind='Single Passage', title='Online service plans', nums=[69,70], docs=[dict(label='SERVICE PLANS', meta='FileHarbor | Team storage', paras=[
    'The Starter plan costs $12 per month and supports up to three users. It includes 50 GB of shared storage and e-mail support. The Team plan costs $28 per month and supports up to ten users, with 200 GB of shared storage and telephone support during business hours.',
    'Customers may upgrade at any time. The additional charge for the rest of the current billing month will be prorated according to the number of days remaining. Downgrades take effect at the start of the next billing month.',
    'Both plans include automatic daily backups. A 14-day free trial is available to new customers; no payment card is required to begin the trial. Existing customers are not eligible for another free trial when changing plans.'
])]))
add(69, 'The word "prorated" in paragraph 2 is closest in meaning to', [
    'adjusted in proportion to the time covered', 'removed because of a complaint',
    'increased by a fixed penalty', 'divided equally among all customers'], 'A', 2, 'PART 7 - VOCABULARY IN CONTEXT',
    '낯선 단어는 뒤의 구체적 산정 기준으로 뜻을 추론한다.', 'according to the number of days remaining이 남은 날짜 수에 비례해 요금을 조정한다는 의미를 풀어 준다.',
    ['잔여 기간에 비례해 조정한다는 문맥상 의미이다.', '불만 제기나 요금 면제에 관한 설명이 없다.', '정액 벌금이 아니라 일수에 따른 산정이다.', '고객들 사이의 분담이 아니다.'],
    'pro- 같은 철자 일부로 뜻을 찍기보다 바로 뒤 기준을 읽는다.', '어휘 뒤 설명·예시·기준에서 뜻을 검증한다.',
    evidence=[('Plans, paragraph 2', 'according to the number of days remaining')])
add(70, 'What is mentioned about both service plans?', [
    'They include telephone support.', 'They support at least ten users.', 'They require a payment card for a trial.', 'They provide automatic daily backups.'], 'D', 2, 'PART 7 - SHARED DETAIL',
    '두 상품 공통 사항과 상위 상품 전용 기능을 구별한다.', '마지막 문단에서 Both plans include automatic daily backups라고 명시한다. 전화 지원과 사용자 10명은 Team만의 조건이다.',
    ['전화 지원은 Team에만 명시되어 있다.', 'Starter는 최대 3명이다.', '체험 시작에 결제 카드가 필요 없다고 했다.', 'Both plans라고 공통 제공 기능을 명시한다.'],
    '상위 요금제의 기능을 두 상품 공통 기능으로 옮기지 않는다.', 'both / only / up to 같은 범위 표현에 표시한다.',
    evidence=[('Plans, paragraph 3', 'Both plans include automatic daily backups.')])
