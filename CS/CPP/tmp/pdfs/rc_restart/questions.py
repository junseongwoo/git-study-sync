import re,random
from content import CH

# Rule / decision cue. Every item also carries a sentence-specific reason.
RULES={
 'N':('명사 자리','관사·소유격 뒤 또는 동사·전치사의 목적어에는 명사 역할이 필요하다.','빈칸이 대상인지 확인하고 명사형을 고른다.'),
 'A':('형용사 자리','명사 수식과 주어·목적어의 상태 보어에는 형용사가 필요하다.','명사를 꾸미거나 상태를 설명하면 형용사를 검토한다.'),
 'D':('부사 자리','동사·형용사·분사·다른 부사를 수식할 때는 부사를 쓴다.','문장 뼈대가 완성되었는지 보고 수식 대상을 찾는다.'),
 'SG':('단수 수일치','일반 현재형은 핵심 단수 주어에 맞춘다.','전치사구·관계절을 빼고 핵심 주어의 수를 확인한다.'),
 'PL':('복수 수일치','일반 현재형은 핵심 복수 주어에 맞춘다.','가까운 명사가 아니라 핵심 주어에 일치시킨다.'),
 'MOD':('조동사 뒤 원형','조동사 뒤에는 주어의 수와 무관하게 동사원형이 온다.','빈칸 앞 조동사를 확인한 뒤 원형을 고른다.'),
 'FIN':('정형 동사','절의 서술어에는 시제·수에 맞는 정형 동사가 필요하다.','수식 분사를 제외하고 주절에 동사가 있는지 확인한다.'),
 'PASS':('수동태','주어가 행위를 받으면 be+p.p. 구조가 필요하다.','주어가 하는가 받는가를 정하고 수동 동사구를 완성한다.'),
 'PP':('과거분사 형태','완료 have 또는 수동 be 뒤의 과거분사 형태를 확인한다.','앞 조동사·have·be와 뒤 형태를 한 덩어리로 읽는다.'),
 'PAST':('단순과거','끝난 특정 과거 시점의 사건은 과거형으로 표현한다.','yesterday/last ... 같은 과거 시점과 문맥을 확인한다.'),
 'PERF':('현재완료','과거부터 현재까지의 계속·경험·결과는 현재완료로 연결한다.','현재까지 이어지는 상태인지 끝난 과거인지 구분한다.'),
 'PASTPERF':('과거완료','다른 과거 기준점 이전의 완료는 had+p.p.로 표현한다.','과거 기준점과 그보다 먼저 끝난 사건을 나눈다.'),
 'FUTPERF':('미래완료','미래 기준 시점까지의 완료는 will have+p.p.로 표현한다.','미래 기준점과 그전에 완료될 일을 찾는다.'),
 'TIME':('미래 시간 부사절','미래 의미의 시간 부사절에는 보통 현재형을 쓴다.','when/as soon as절이 시간을 나타내는 부사절인지 확인한다.'),
 'GER':('동명사 결합','전치사 또는 해당 동사가 요구하는 목적어에는 동명사를 쓴다.','앞 전치사·동사의 결합을 확인한다.'),
 'INF':('to부정사 결합','계획·결정 등 해당 동사나 목적 표현은 to+원형을 쓴다.','앞 동사가 to부정사를 요구하는지, 목적 의미인지 확인한다.'),
 'BARE':('원형부정사','능동 let/make+목적어 뒤에는 동사원형을 쓴다.','let/make와 목적어를 확인하고 뒤를 원형으로 고른다.'),
 'ED':('과거분사 수식','수식받는 명사가 행위를 받으면 과거분사를 검토한다.','수식 대상과 능동·수동 관계를 판단한다.'),
 'ING':('현재분사 수식','수식받는 명사가 행위하면 현재분사를 검토한다.','명사가 직접 하는 행동인지 확인한다.'),
 'EMO':('감정 분사','감정을 느끼는 상태인지 감정을 유발하는 성질인지 구별한다.','사람·사물 기준 대신 감정의 방향을 읽는다.'),
 'HAVING':('완료 분사구문','앞선 완료 행동의 행위자가 주절 주어와 일치해야 한다.','주절 주어가 분사 행동을 했는지 먼저 확인한다.'),
 'WHO':('사람 주격 관계사','사람 선행사를 받고 관계절의 주어가 빠지면 who를 쓴다.','선행사 종류와 관계절의 빠진 성분을 동시에 본다.'),
 'WHICH':('사물 관계대명사','사물 선행사의 주어·목적어 역할은 which 등으로 연결한다.','쉼표·전치사와 관계절의 빈 역할을 확인한다.'),
 'WHOSE':('소유격 관계사','선행사와 뒤 명사의 소유 관계에는 whose+명사를 쓴다.','빈칸 바로 뒤 명사와 선행사의 소유 관계를 본다.'),
 'WHOM':('전치사 뒤 사람 관계사','전치사 바로 뒤 사람 목적격 관계사는 whom이다.','전치사+관계사 덩어리와 사람 선행사를 확인한다.'),
 'WHERE':('관계부사 where','뒤 절의 핵심 구조가 갖추어지고 장소 관계가 필요하면 where를 쓴다.','장소 명사만 보지 말고 뒤 절의 목적어 유무를 확인한다.'),
 'WHEN':('관계부사 when','시간 선행사 뒤 시간 관계를 보충하는 절에는 when을 쓴다.','시간 선행사와 뒤 절의 완결 구조를 확인한다.'),
 'WHY':('관계부사 why','reason 뒤 이유 관계를 보충할 때 why를 쓸 수 있다.','이유 선행사와 뒤 절의 구조를 함께 본다.'),
 'CONJ':('접속사와 문맥','절의 구조와 이유·양보·조건·시간 관계를 함께 확인한다.','뒤가 절인지 본 뒤 앞뒤 주장 관계를 정한다.'),
 'PREP':('전치사와 결합','전치사는 뒤 명사 역할과 앞 단어의 결합을 함께 확인한다.','뒤가 명사구인지 보고 고정 결합·시간 의미를 맞춘다.'),
 'OBJ':('목적격 대명사','동사·전치사의 목적어에는 목적격을 사용한다.','주어와 지칭 대상이 다른지 보고 목적격을 고른다.'),
 'POSS':('소유격','명사 앞 소유 표현은 소유격 형태를 쓴다.','빈칸 바로 뒤 명사가 있는지 확인한다.'),
 'POSSPRO':('소유대명사','소유대명사는 소유격+명사를 대신하여 단독으로 쓴다.','뒤 명사가 생략되었는지 확인한다.'),
 'SELF':('재귀대명사','주어와 같은 대상을 목적어로 받거나 직접 했음을 강조한다.','지칭 대상과 목적어 유무를 확인한다.'),
 'OTHER':('다른 대상 지칭','단수·복수와 정해진 범위, 뒤 명사 유무를 확인한다.','another/other/others/the other의 수와 범위를 맞춘다.'),
 'COMP':('비교급','두 대상의 차이를 than과 비교하면 비교급을 쓴다.','than과 비교 대상의 범주를 확인한다.'),
 'SUPER':('최상급','정해진 범위 안의 최고·최저 수준에는 최상급을 쓴다.','the와 of/in 범위를 확인한다.'),
 'AS':('원급 비교','as+형용사·부사 원급+as로 동등 비교를 만든다.','두 as 사이에 비교급을 넣지 않는다.'),
 'EMPH':('비교급 강조','much/far/even/considerably 등은 비교급을 강조한다.','뒤가 비교급이면 very 대신 비교급 강조어를 검토한다.'),
 'IFPAST':('현재 반대 가정','현재 사실과 다른 가정은 if+과거형, would+원형을 쓴다.','현재 사실을 읽고 과거형의 가정 의미를 확인한다.'),
 'IFPERF':('과거 반대 가정','과거 사실 반대의 조건절에는 had+p.p.를 쓴다.','이미 끝난 사건인지 보고 조건절을 과거완료로 만든다.'),
 'IFRESULT':('과거 가정의 결과','과거 반대 가정의 결과에는 would have+p.p.를 쓴다.','if절과 결과절을 구분하고 완료형 조동사를 확인한다.'),
 'INV':('if 생략 도치','if가 생략되면 had/should/were 등이 주어 앞으로 이동한다.','문두 조동사와 뒤 주어·본동사의 형태를 확인한다.'),
 'MAND':('요구·권고절','요구·권고의 that절은 동사원형을 쓰며 수동은 be+p.p.이다.','요구 동사와 that절을 보고 태를 확인한다.'),
 'UNC':('불가산명사','information/equipment/advice 등은 이 의미에서 불가산명사이다.','a/an·복수형을 피하고 단위 표현을 확인한다.'),
 'ART':('관사','특정성·가산 단수 여부와 다음 단어의 소리로 관사를 고른다.','첫 소개인지 재언급인지 보고 a/an은 발음으로 정한다.'),
 'QUANT':('수량 표현','many/few는 가산 복수, much/little은 불가산명사와 쓴다.','뒤 명사의 가산성과 긍정·부정 방향을 확인한다.'),
 'VOC':('어휘와 콜로케이션','품사뿐 아니라 목적어·전치사·상황에 맞는 단어를 고른다.','문법이 맞는 후보는 문장 끝까지 읽고 결합으로 구별한다.'),
 'LOGIC':('문맥 연결','문장 사이의 대조·결과·대안·불이행 결과를 구분한다.','앞뒤 주장을 요약한 뒤 연결 표현을 대입한다.')
}
DESC={'n':'명사형이다.','a':'형용사형이다.','d':'부사형이다.','v':'동사형이다.','ing':'-ing 준동사형이다.','to':'to부정사형이다.','pp':'과거분사형이다.','sg':'단수 현재 동사형이다.','pl':'복수 현재 동사형이다.','past':'단순과거형이다.','perf':'현재완료형이다.','future':'미래형이다.','subj':'주격 대명사이다.','obj':'목적격 대명사이다.','poss':'명사 앞 소유격이다.','posspro':'소유대명사이다.','self':'재귀대명사이다.','comp':'비교급이다.','super':'최상급이다.','base':'원형이다.','prep':'명사 역할을 취하는 전치사이다.','conj':'절을 이끄는 접속사이다.'}

def q(kind,marked,forms,why):
    opts=[];analyses=[]
    need,core,exam=RULES[kind]
    for i,f in enumerate(forms.split('|')):
        text,sep,code=f.partition('~')
        opts.append(text)
        if i==0:analyses.append('정답. '+why)
        elif code.startswith('$'):analyses.append(code[1:])
        else:
            short={
             'N':'이 자리에는 대상을 나타내는 명사 역할이 필요하다.',
             'A':'이 자리는 명사 수식 또는 상태 보어인 형용사 자리이다.',
             'D':'여기서는 동작·형용사·분사를 꾸미는 부사가 필요하다.',
             'SG':'핵심 단수 주어에 맞는 정형 동사가 필요하다.',
             'PL':'핵심 복수 주어에 맞는 정형 동사가 필요하다.',
             'MOD':'조동사 바로 뒤에는 to나 -s 없이 원형을 쓴다.',
             'FIN':'이 형태로는 주절의 정형 동사 자리가 완성되지 않는다.',
             'PASS':'수동 동사구의 마지막에는 과거분사가 필요하다.',
             'PP':'앞 have/be가 요구하는 과거분사가 아니다.',
             'PAST':'끝난 특정 과거 시점의 서술에 맞지 않는다.',
             'PERF':'과거부터 현재까지 이어진 내용과 형태가 맞지 않는다.',
             'PASTPERF':'과거 기준점 이전의 완료를 나타내지 못한다.',
             'FUTPERF':'미래 기준점까지의 완료를 표현하지 못한다.',
             'TIME':'미래 시간 부사절에는 현재형 서술이 필요하다.',
             'GER':'앞 전치사·동사의 결합에는 동명사가 필요하다.',
             'INF':'이 결합에는 to+동사원형이 필요하다.',
             'BARE':'능동 let+목적어 뒤에는 원형을 쓴다.',
             'ED':'명사가 받는 행동을 나타내는 수식 형태가 아니다.',
             'ING':'명사가 직접 하는 행동의 수식 형태가 아니다.',
             'EMO':'여기서 필요한 감정의 방향 또는 형용사 자리에 맞지 않는다.',
             'OBJ':'이 자리는 주어와 다른 대상을 받는 목적격 자리이다.',
             'POSS':'뒤 명사를 꾸미는 소유격이 필요하다.',
             'POSSPRO':'명사를 대신하여 단독으로 쓰는 소유대명사가 필요하다.',
             'SELF':'주어와 같은 대상을 받거나 주어를 강조해야 한다.',
             'COMP':'이 비교에는 비교급 형태가 필요하다.',
             'SUPER':'정해진 범위 안에서 최상급이 필요하다.',
             'AS':'as ... as 사이에는 필요한 품사의 원급을 쓴다.',
             'IFPAST':'현재 반대 가정의 조건절 형태가 아니다.',
             'IFPERF':'과거 반대 가정의 조건절 형태가 아니다.',
             'IFRESULT':'과거 가정 결과의 would have+p.p.가 아니다.',
             'MAND':'요구·권고절의 동사원형을 완성하지 못한다.',
             'CONJ':'뒤에 있는 완전한 절을 이 구조로 연결하지 못한다.',
             'PREP':'뒤 명사구를 필요한 의미로 연결하지 못한다.',
            }.get(kind,core)
            analyses.append(DESC.get(code,'이 형태·의미는 적절하지 않다.')+' '+short)
    assert len(opts)==4 and len(set(opts))==4,(marked,forms)
    completed=marked.replace('-------',opts[0])
    stem=re.sub(r'\{[SVOCM]+\}','',marked).replace(' / ',' ')
    assert '-------' in stem and all(re.search(r'\{[SVOCM]+\}',x) for x in marked.split(' / ')),marked
    return dict(kind=kind,stem=stem,marked=marked,structure=completed,opts=opts,analyses=analyses,
                why=why,core=core,exam=exam,need=need,answer='A')

def setq(n,practice,review):
    assert len(practice)==8 and len(review)==10,(n,len(practice),len(review))
    CH[n-1]['practice']=practice;CH[n-1]['review']=review

setq(1,[
 q('A','The lobby{S} / remains{V} / -------{C} / during the renovation{M}.','accessible|access~n|accessibly~d|accessing~ing','remains는 상태를 연결하며 accessible이 lobby의 상태를 설명한다.'),
 q('N','The manager{S} / approved{V} / the -------{O} / yesterday{M}.','proposal|propose~v|proposed~pp|proposing~ing','the 뒤에는 승인한 대상인 명사가 필요하다.'),
 q('MOD','The visitors{S} / will -------{V} / at noon{M}.','arrive|arriving~ing|arrival~n|to arrive~to','will 뒤 원형 arrive가 와서 주어의 도착을 서술한다.'),
 q('A','The new labels{S} / make{V} / each package{O} / -------{C}.','identifiable|identification~n|identifiably~d|identify~v','포장이 식별 가능한 상태가 된다는 SVOC 구조이다.'),
 q('N','The clerk{S} / gave{V} / each customer{O} / a -------{O}.','receipt|receive~v|receivable~a|receiving~ing','고객에게 준 물건을 나타내는 두 번째 목적어 receipt가 필요하다.'),
 q('A','Please keep{V} / the documents{O} / -------{C}.','confidential|confidence~n|confidentially~d|confide~v','documents를 기밀 상태로 유지하라는 목적격 보어이다.'),
 q('SG','The list of approved suppliers{S} / -------{V} / on the shared drive{M}.','is|are~pl|being~ing|to be~to','핵심 주어는 suppliers가 아니라 단수 list이다.'),
 q('A','We{S} / found{V} / the instructions{O} / -------{C}.','helpful|help~n|helpfully~d|helping~ing','설명이 도움이 된다고 판단했다는 구조로 instructions의 상태를 보충한다.')],[
 q('N','The director{S} / requested{V} / a -------{O} / of the contract{M}.','revision|revise~v|revised~pp|revising~ing','요청한 대상이므로 관사 a 뒤 명사 revision이 필요하다.'),
 q('A','The storage area{S} / is{V} / -------{C}.','secure|security~n|securely~d|securing~ing','주어 area가 안전하다는 상태 보어이다.'),
 q('MOD','Our courier{S} / can -------{V} / the parcel{O} / today{M}.','deliver|delivery~n|delivering~ing|to deliver~to','can 뒤 원형 deliver가 오고 parcel이 그 목적어이다.'),
 q('A','The extra signs{S} / made{V} / the route{O} / -------{C}.','clear|clarity~n|clearly~d|clarify~v','route가 명확해졌다는 상태를 형용사가 설명한다.'),
 q('N','The receptionist{S} / sent{V} / the guest{O} / a -------{O}.','confirmation|confirm~v|confirmed~pp|confirming~ing','손님에게 보낸 것은 확인서이므로 명사이다.'),
 q('PL','The folders on the top shelf{S} / -------{V} / empty{C}.','are|is~sg|being~ing|to be~to','핵심 주어 folders가 복수이고 empty는 보어이다.'),
 q('A','The technician{S} / left{V} / the machine{O} / -------{C}.','operational|operation~n|operationally~d|operate~v','기계를 작동 가능한 상태로 두었다는 목적격 보어이다.'),
 q('N','The office{S} / needs{V} / more -------{O}.','storage|store~v|stored~pp|storing~ing','needs가 필요로 하는 대상은 보관 공간을 뜻하는 storage이다.'),
 q('A','The schedule{S} / seems{V} / -------{C}.','reasonable|reason~n|reasonably~d|reasoning~ing','seems 뒤에는 일정의 상태를 설명하는 형용사가 필요하다.'),
 q('SG','The entrance near the elevators{S} / -------{V} / locked{C}.','is|are~pl|being~ing|to be~to','단수 entrance가 주어이며 elevators는 수식어 안에 있다.')])

setq(2,[
 q('N','Please provide{V} / a brief -------{O} / of the problem{M}.','description|describe~v|descriptive~a|descriptively~d','관사와 형용사 brief 뒤에 목적어 명사가 필요하다.'),
 q('A','We{S} / need{V} / a ------- supplier{O}.','reliable|reliability~n|reliably~d|rely~v','supplier를 꾸미는 명사 앞 형용사 자리이다.'),
 q('D','The assistant{S} / answered{V} / the question{O} / -------{M}.','politely|polite~a|politeness~n|politer~comp','answered라는 행동의 방식을 꾸미므로 부사이다.'),
 q('A','The revised plan{S} / is{V} / -------{C}.','acceptable|acceptance~n|acceptably~d|accept~v','is 뒤에서 plan의 상태를 설명한다.'),
 q('D','The policy{S} / is{V} / ------- effective{C}.','highly|high~a|height~n|higher~comp','빈칸은 형용사 effective의 정도를 꾸민다.'),
 q('N','The company{S} / values{V} / customer -------{O}.','satisfaction|satisfactory~a|satisfactorily~d|satisfy~v','customer가 앞에서 수식하고 satisfaction이 목적어 핵심 명사이다.'),
 q('PREP','The event{S} / was canceled{V} / ------- the storm{M}.','because of|because~conj|although~conj|unless~conj','the storm은 절이 아닌 명사구이므로 because of가 필요하다.'),
 q('D','The estimate{S} / has been ------- revised{V}.','substantially|substantial~a|substance~n|substantiate~v','완성된 수동 동사구 has been revised를 수식하는 부사이다.')],[
 q('A','The ------- instructions{S} / reduced{V} / confusion{O}.','clear|clarity~n|clearly~d|clarify~v','주어 명사 instructions 앞 수식어는 형용사이다.'),
 q('N','We{S} / received{V} / written -------{O}.','permission|permit~v|permissible~a|permissibly~d','written의 수식을 받는 목적어 명사가 필요하다.'),
 q('D','The consultant{S} / explained{V} / the changes{O} / -------{M}.','clearly|clear~a|clarity~n|clearest~super','설명한 방식을 꾸미는 부사이다.'),
 q('A','Please keep{V} / the corridor{O} / -------{C}.','clear|clarity~n|clearly~d|clarify~v','corridor를 비워 둔 상태로 유지하라는 보어이다.'),
 q('D','The proposal{S} / is{V} / ------- attractive{C}.','particularly|particular~a|particulars~n|particularize~v','형용사 attractive를 꾸미는 정도 부사이다.'),
 q('N','The office{S} / requires{V} / proof of -------{O}.','payment|pay~v|payable~a|paying~ing','전치사 of 뒤 명사 payment가 납부 증빙의 내용을 나타낸다.'),
 q('MOD','The team{S} / must -------{V} / the figures{O}.','verify|verification~n|verifying~ing|to verify~to','조동사 must 뒤 원형이 필요하다.'),
 q('SG','The schedule for the workshops{S} / -------{V} / flexible{C}.','is|are~pl|being~ing|to be~to','주어 schedule은 단수이고 workshops는 전치사구 안에 있다.'),
 q('CONJ','------- the office is closed{M}, / customers{S} / can use{V} / the website{O}.','Although|Despite~prep|During~prep|Because of~prep','뒤에 주어 office와 동사 is가 있는 절이며 폐점에도 웹을 쓴다는 양보이다.'),
 q('A','The brochure{S} / made{V} / the service{O} / -------{C}.','appealing|appeal~n|appealingly~d|appeals~sg','서비스를 매력적으로 보이게 했다는 목적격 보어이다.')])

setq(3,[
 q('MOD','The driver{S} / will -------{V} / the goods{O} / tomorrow{M}.','collect|collects~sg|collecting~ing|to collect~to','will 뒤 동사원형을 쓴다.'),
 q('FIN','The staff{S} / -------{V} / the visitors{O} / yesterday{M}.','welcomed|welcoming~ing|to welcome~to|welcome party~n','yesterday의 완료된 행동을 서술하는 과거형이 필요하다.'),
 q('PP','The package{S} / has -------{V} / safely{M}.','arrived|arriving~ing|arrive~base|to arrive~to','has 뒤 과거분사 arrived로 완료 동사구를 완성한다.'),
 q('FIN','The invoices sent this morning{S} / -------{V} / a new account number{O}.','include|including~ing|to include~to|inclusion~n','sent this morning은 수식어이며 복수 주어 invoices의 본동사 include가 필요하다.'),
 q('PASS','The entrance{S} / is being -------{V} / this week{M}.','repaired|repairing~ing|repair~base|to repair~to','is being 뒤 과거분사가 와서 진행 수동태를 만든다.'),
 q('FIN','Employees working overseas{S} / -------{V} / online support{O}.','receive|receiving~ing|to receive~to|receipt~n','working overseas는 수식어이고 직원들이 받는다는 주절 동사가 필요하다.'),
 q('MOD','The technician{S} / can -------{V} / the device{O} / before lunch{M}.','inspect|inspects~sg|inspecting~ing|to inspect~to','can 뒤 원형을 쓰며 technician 단수와 별도로 판단한다.'),
 q('PP','The forms{S} / have been -------{V} / by the supervisor{M}.','checked|checking~ing|check~base|to check~to','have been 뒤 과거분사로 완료 수동 동사구를 완성한다.')],[
 q('FIN','The message attached to the file{S} / -------{V} / the error{O}.','explains|explaining~ing|to explain~to|explanation~n','attached는 수식어이고 단수 message의 본동사는 explains이다.'),
 q('MOD','The operator{S} / should -------{V} / the meter{O}.','check|checks~sg|checking~ing|to check~to','should 뒤에는 원형이 온다.'),
 q('PP','The company{S} / has -------{V} / two offices{O}.','opened|opening~ing|open~base|to open~to','has 뒤 과거분사 opened가 완료형을 만든다.'),
 q('PASS','All requests{S} / must be -------{V} / in writing{M}.','submitted|submitting~ing|submit~base|to submit~to','requests가 제출되는 대상이므로 must be+p.p.이다.'),
 q('N','The team{S} / needs{V} / a written -------{O}.','agreement|agree~v|agreeable~a|agreeably~d','a written 뒤 목적어 명사 agreement가 필요하다.'),
 q('D','The manager{S} / reviewed{V} / the file{O} / -------{M}.','carefully|careful~a|care~n|caring~ing','reviewed의 방식을 꾸미는 부사이다.'),
 q('A','The new seats{S} / are{V} / -------{C}.','comfortable|comfort~n|comfortably~d|comforting~ing','좌석의 편안한 상태를 설명하는 형용사 보어이다.'),
 q('FIN','The brochures printed last week{S} / -------{V} / several errors{O}.','contain|containing~ing|to contain~to|container~n','printed는 수식어이고 복수 brochures에 맞는 본동사 contain이 필요하다.'),
 q('MOD','The receptionist{S} / may -------{V} / a visitor pass{O}.','issue|issues~sg|issuing~ing|to issue~to','may 뒤 원형 issue를 쓴다.'),
 q('PP','The meeting{S} / has been -------{V} / until Friday{M}.','postponed|postponing~ing|postpone~base|to postpone~to','has been 뒤 과거분사로 회의가 연기된 완료 수동태를 만든다.')])

setq(4,[
 q('SG','Every visitor{S} / -------{V} / a badge{O}.','needs|need~pl|needing~ing|to need~to','Every visitor는 단수이다.'),
 q('PL','The new employees{S} / -------{V} / access cards{O}.','have|has~sg|having~ing|to have~to','employees가 복수 주어이다.'),
 q('SG','Each of the invoices{S} / -------{V} / a reference number{O}.','has|have~pl|having~ing|to have~to','핵심 주어 each는 단수이다.'),
 q('SG','The number of cancellations{S} / -------{V} / low{C}.','is|are~pl|being~ing|to be~to','취소 건수 number가 단수 주어이다.'),
 q('PL','A number of customers{S} / -------{V} / assistance{O}.','require|requires~sg|requiring~ing|to require~to','a number of customers는 여러 고객을 뜻하는 복수 주어이다.'),
 q('SG','The equipment in both rooms{S} / -------{V} / regular maintenance{O}.','needs|need~pl|needing~ing|to need~to','equipment는 불가산명사로 단수 취급한다.'),
 q('SG','Neither the assistants nor the director{S} / -------{V} / free{C}.','is|are~pl|being~ing|to be~to','nor 뒤 가까운 director가 단수이다.'),
 q('PL','There{M} / -------{V} / two available appointments{S}.','are|is~sg|being~ing|to be~to','there 뒤 실제 주어 two appointments가 복수이다.')],[
 q('SG','The cost of replacement parts{S} / -------{V} / high{C}.','is|are~pl|being~ing|to be~to','주어 cost는 단수이다.'),
 q('PL','Both the invoice and the receipt{S} / -------{V} / required{C}.','are|is~sg|being~ing|to be~to','and로 연결된 두 문서가 복수 주어이다.'),
 q('SG','Each employee{S} / -------{V} / a locker{O}.','has|have~pl|having~ing|to have~to','Each employee는 단수이다.'),
 q('PL','The guidelines for new suppliers{S} / -------{V} / clear{C}.','are|is~sg|being~ing|to be~to','주어 guidelines는 복수이다.'),
 q('SG','Either the drivers or their supervisor{S} / -------{V} / the route{O}.','checks|check~pl|checking~ing|to check~to','가까운 supervisor가 단수이다.'),
 q('MOD','The supervisor{S} / must -------{V} / the delivery{O}.','confirm|confirms~sg|confirming~ing|to confirm~to','조동사 뒤 원형이며 단수 주어라고 -s를 붙이지 않는다.'),
 q('FIN','The file stored on the server{S} / -------{V} / the latest figures{O}.','contains|containing~ing|to contain~to|container~n','stored는 수식어, contains는 주절 동사이다.'),
 q('A','The instructions{S} / remain{V} / -------{C}.','valid|validity~n|validly~d|validate~v','remain 뒤 상태 보어가 필요하다.'),
 q('D','The assistant{S} / filed{V} / the reports{O} / -------{M}.','accurately|accurate~a|accuracy~n|accuracies~n','filed라는 행동을 수식한다.'),
 q('N','We{S} / need{V} / written -------{O} / before delivery{M}.','approval|approve~v|approving~ing|approvingly~d','written 뒤 승인이라는 명사 목적어가 필요하다.')])

setq(5,[
 q('PAST','The supplier{S} / -------{V} / the order{O} / yesterday{M}.','confirmed|confirms~sg|will confirm~future|confirming~ing','yesterday는 끝난 특정 과거 시점이다.'),
 q('SG','The branch{S} / -------{V} / at nine every morning{M}.','opens|open~pl|opening~ing|to open~to','반복 운영 시간이며 단수 branch에 opens를 쓴다.'),
 q('PERF','The company{S} / -------{V} / this office{O} / since 2020{M}.','has occupied|will occupy~future|occupying~ing|to occupy~to','2020년부터 현재까지 사용하는 사무실이다.'),
 q('PASTPERF','By the time the guests arrived{M}, / the staff{S} / -------{V} / the room{O}.','had prepared|will prepare~future|preparing~ing|to prepare~to','손님 도착이라는 과거 기준점 전에 준비가 완료되었다.'),
 q('FUTPERF','By the end of next month{M}, / we{S} / -------{V} / the move{O}.','will have completed|completed~past|completing~ing|to complete~to','다음 달 말이라는 미래 시점까지의 완료이다.'),
 q('TIME','We will send a receipt as soon as{M} / the payment{S} / -------{V}.','arrives|will arrive~future|arriving~ing|to arrive~to','as soon as의 미래 시간 부사절에서는 현재형을 쓴다.'),
 q('PERF','The engineers{S} / -------{V} / the system{O} / since Monday and are still testing it{M}.','have been testing|had tested~$과거 기준점 이전 완료로 현재도 진행 중인 내용과 맞지 않는다.|will test~future|testing~ing','since Monday와 are still testing이 현재까지 계속되는 활동을 확인한다.'),
 q('PAST','Ms. Han{S} / -------{V} / the report{O} / last Friday{M}.','submitted|has submitted~perf|submitting~ing|to submit~to','last Friday가 끝난 과거 시점을 지정한다.')],[
 q('PAST','The store{S} / -------{V} / its doors{O} / early yesterday{M}.','closed|closes~sg|will close~future|closing~ing','어제 일찍 문을 닫았다는 과거 사건이다.'),
 q('PERF','Our team{S} / -------{V} / at this location{M} / for six years and still works here{M}.','has worked|will work~future|working~ing|to work~to','현재도 같은 곳에서 일하므로 기간을 현재완료로 연결한다.'),
 q('TIME','Please wait until{M} / the technician{S} / -------{V}.','returns|will return~future|returning~ing|to return~to','미래의 복귀 시점을 나타내는 until절이다.'),
 q('FUTPERF','By the time the fair opens tomorrow{M}, / we{S} / -------{V} / all displays{O}.','will have installed|installed~past|installing~ing|to install~to','내일 개장 전까지 전시 설치가 완료될 것이다.'),
 q('PASTPERF','Before the auditor visited last week{M}, / the team{S} / -------{V} / the error{O}.','had corrected|will correct~future|correcting~ing|to correct~to','지난주 방문보다 앞서 수정한 완료를 나타낸다.'),
 q('SG','Every delivery{S} / -------{V} / a tracking code{O}.','includes|include~pl|including~ing|to include~to','every delivery가 단수이다.'),
 q('MOD','The driver{S} / should -------{V} / reception{O} / on arrival{M}.','call|calls~sg|calling~ing|to call~to','should 뒤 원형이다.'),
 q('A','The revised timetable{S} / seems{V} / -------{C}.','practical|practice~n|practically~d|practicing~ing','seems 뒤 주어 상태를 설명한다.'),
 q('D','The coordinator{S} / replied{V} / -------{M}.','promptly|prompt~a|promptness~n|prompting~ing','replied를 꾸미는 부사이다.'),
 q('N','The team{S} / requested{V} / an -------{O} / of the deadline{M}.','extension|extend~v|extensive~a|extensively~d','an 뒤 연장이라는 목적어 명사가 필요하다.')])

setq(6,[
 q('PASS','The certificates{S} / will be -------{V} / tomorrow{M}.','issued|issuing~ing|issue~base|to issue~to','증명서는 발급되는 대상이다.'),
 q('PASS','Each application{S} / must be -------{V} / online{M}.','submitted|submitting~ing|submit~base|to submit~to','신청서는 제출되는 대상이므로 조동사 수동태이다.'),
 q('PASS','The elevator{S} / is being -------{V} / at present{M}.','inspected|inspecting~ing|inspect~base|to inspect~to','현재 점검 중인 수동 동사구이다.'),
 q('PASS','The contract{S} / has been -------{V} / by both parties{M}.','signed|signing~ing|sign~base|to sign~to','계약서가 서명된 완료 수동태이다.'),
 q('PASS','Employees{S} / were -------{V} / new access cards{O}.','given|giving~ing|give~base|to give~to','직원이 카드를 받는 수여동사 수동태로 물건 목적어가 남는다.'),
 q('FIN','The shipment{S} / -------{V} / yesterday{M}.','arrived|was arrived~$arrive는 여기서 자동사이므로 이런 수동태를 만들지 않는다.|arriving~ing|to arrive~to','arrive는 목적어 없는 자동사이며 과거 도착을 능동형으로 쓴다.'),
 q('PREP','The laboratory{S} / is equipped{V} / ------- modern safety devices{M}.','with|by~$devices는 장비이며 장비를 제공하는 행위자가 아니다.|to~$be equipped to 뒤 원형이 필요한 용법과 달리 뒤는 장비 명사구이다.|for~$장비 목록을 연결하는 결합은 equipped with이다.','갖추어진 장비는 with로 연결한다.'),
 q('PASS','No refund{S} / can -------{V} / before inspection{M}.','be issued|issue~$refund가 발행하는 주체가 아니라 발행되는 대상이다.|issuing~ing|to issue~to','can 뒤 수동 be issued가 필요하다.')],[
 q('PASS','The new policy{S} / was -------{V} / last month{M}.','introduced|introducing~ing|introduce~base|to introduce~to','정책이 도입된 과거 수동태이다.'),
 q('PASS','All invoices{S} / have been -------{V}.','paid|paying~ing|pay~base|to pay~to','청구액이 지불된 완료 수동태이다.'),
 q('PASS','The printer{S} / is being -------{V}.','replaced|replacing~ing|replace~base|to replace~to','프린터가 교체되는 진행 수동태이다.'),
 q('PASS','The forms{S} / should be -------{V} / by noon{M}.','completed|completing~ing|complete~base|to complete~to','양식은 작성되는 대상으로 should be+p.p.이다.'),
 q('FIN','The incident{S} / -------{V} / last Tuesday{M}.','occurred|was occurred~$occur는 자동사로 여기서 수동태를 만들지 않는다.|occurring~ing|to occur~to','사건 발생은 자동사 occur의 과거형을 쓴다.'),
 q('PAST','The manager{S} / -------{V} / the request{O} / yesterday{M}.','approved|has approved~perf|approving~ing|to approve~to','yesterday의 과거 능동 사건이다.'),
 q('SG','The list of repairs{S} / -------{V} / on the noticeboard{M}.','is|are~pl|being~ing|to be~to','주어 list가 단수이다.'),
 q('MOD','The technician{S} / may -------{V} / the repair{O}.','delay|delays~sg|delaying~ing|to delay~to','may 뒤 원형이다.'),
 q('A','The replacement part{S} / is{V} / -------{C}.','available|availability~n|availably~d|availing~ing','부품의 이용 가능 상태를 설명하는 형용사가 필요하다.'),
 q('D','The door{S} / closes{V} / -------{M}.','automatically|automatic~a|automation~n|automate~v','closes의 방식을 꾸미는 부사이다.')])

setq(7,[
 q('GER','Please avoid{V} / ------- duplicate requests{O}.','sending|send~base|to send~to|sent~pp','avoid는 동명사 목적어를 취한다.'),
 q('INF','The team{S} / decided{V} / ------- the deadline{O}.','to extend|extending~ing|extend~base|extended~pp','decide 뒤에는 to부정사를 쓴다.'),
 q('GER','We{S} / are interested{V} / in ------- the service{M}.','using|use~base|to use~to|used~pp','전치사 in 뒤 동명사이다.'),
 q('INF','The supervisor{S} / encouraged{V} / staff{O} / ------- early{C}.','to apply|applying~ing|apply~base|applied~pp','encourage+목적어+to부정사 구조이다.'),
 q('GER','We{S} / look forward{V} / to ------- your team{M}.','meeting|meet~base|to meet~to|met~pp','look forward to의 to는 전치사이다.'),
 q('INF','Please remember{V} / ------- the lights before leaving{O}.','to switch off|switching off~$앞으로 해야 할 일을 잊지 말라는 요청이며 과거 기억이 아니다.|switch off~base|switched off~pp','퇴실 전 해야 할 행동이므로 remember to do이다.'),
 q('BARE','The manager{S} / let{V} / the staff{O} / ------- early{C}.','leave|to leave~to|leaving~ing|left~pp','능동 let+목적어 뒤 원형이다.'),
 q('GER','The company{S} / is committed{V} / to ------- waste{M}.','reducing|reduce~base|to reduce~to|reduced~pp','be committed to의 to는 전치사이다.')],[
 q('GER','We{S} / considered{V} / ------- the office{O}.','relocating|relocate~base|to relocate~to|relocated~pp','consider는 동명사 목적어를 취한다.'),
 q('INF','The supplier{S} / agreed{V} / ------- the damaged items{O}.','to replace|replacing~ing|replace~base|replaced~pp','agree 뒤 to부정사를 쓴다.'),
 q('GER','Thank you{M} / for ------- the issue{M}.','reporting|report~base|to report~to|reported~pp','전치사 for 뒤 동명사이다.'),
 q('INF','The driver{S} / stopped{V} / ------- the address before continuing{M}.','to check|checking~$주소 확인을 중단했다는 뜻이 되어 잠시 멈춘 목적과 다르다.|check~base|checked~pp','운전을 멈춘 목적이 주소 확인이므로 stop to do이다.'),
 q('SG','Completing the application{S} / -------{V} / only ten minutes{O}.','takes|take~pl|taking~ing|to take~to','동명사구 전체는 단수 주어이다.'),
 q('PASS','The survey{S} / must be -------{V} / anonymously{M}.','completed|completing~ing|complete~base|to complete~to','설문은 작성되는 대상이다.'),
 q('PAST','The team{S} / -------{V} / the design{O} / last week{M}.','revised|has revised~perf|revising~ing|to revise~to','last week의 끝난 과거이다.'),
 q('A','The online form{S} / is{V} / -------{C}.','convenient|convenience~n|conveniently~d|conveniences~n','주어의 편리한 상태를 설명한다.'),
 q('D','Please review{V} / the terms{O} / -------{M}.','carefully|careful~a|care~n|caring~ing','review라는 행동을 수식한다.'),
 q('MOD','Participants{S} / must -------{V} / their own devices{O}.','bring|brings~sg|bringing~ing|to bring~to','must 뒤 원형이다.')])

setq(8,[
 q('ED','The documents{S} / ------- to this message are confidential{M}.','attached|attaching~$문서는 첨부하는 주체가 아니라 첨부되는 대상이다.|attach~base|to attach~$앞으로 첨부할 대상이 아니라 이미 이 메시지에 첨부된 문서이다.','documents가 첨부되는 대상이며 are confidential이 주절 서술부이다.'),
 q('ING','Employees{S} / ------- the training should arrive by nine{M}.','attending|attended~$직원이 참석하는 능동 관계이며 참석되는 대상이 아니다.|attend~$주절 should arrive가 이미 있어 연결어 없이 독립 동사를 추가할 수 없다.|to attended~$to 뒤 과거형은 올 수 없다.','직원이 교육에 참석하는 능동 관계의 수식어이다.'),
 q('EMO','The audience{S} / was{V} / ------- in the demonstration{C}.','interested|interesting~$흥미를 유발하는 성질이 아니라 흥미를 느끼는 상태이다.|interest~n|interests~n','청중이 관심을 느끼는 상태이며 interested in으로 결합한다.'),
 q('ING','The ------- speaker{S} / kept{V} / everyone{O} / engaged{C}.','engaging|engaged~$연설자가 관여 중이라는 상태보다 청중의 관심을 끄는 성질을 말한다.|engage~base|engagement~n','연설자가 흥미를 유발하는 쪽이므로 engaging이다.'),
 q('ED','Please follow{V} / the ------- instructions{O}.','revised|revising~$설명서가 수정하는 주체가 아니라 수정된 대상이다.|revise~base|revision~n','instructions가 수정된 대상이다.'),
 q('HAVING','------- the figures{M}, / the analyst{S} / finalized{V} / the report{O}.','Having checked|Having been checked~$주절 주어 analyst가 점검을 받았다는 뜻이 되어 figures를 점검한 관계가 아니다.|Checks~$주어 없는 독립 동사를 쉼표로 연결할 수 없다.|To checked~$to 뒤에는 동사원형이 필요하다.','analyst가 수치를 먼저 확인한 뒤 보고서를 마무리했다.'),
 q('ED','The rooms{S} / ------- last month are now available{M}.','renovated|renovating~$방은 보수되는 대상이다.|renovate~$are available이 주절 동사이므로 별도 동사를 직접 추가하지 못한다.|to renovating~$부정사 to 뒤 -ing는 이 구조에서 맞지 않는다.','rooms가 지난달 보수된 대상이다.'),
 q('EMO','The ------- result{S} / prompted{V} / a review{O}.','disappointing|disappointed~$결과가 감정을 느끼는 쪽이 아니라 실망을 유발한다.|disappointment~n|disappoint~base','결과가 실망을 유발하는 성질이다.')],[
 q('ING','Customers{S} / ------- assistance should call reception{M}.','needing|needed~$고객들이 도움을 필요로 하는 능동 관계이다.|need~$should call이 주절 동사라 연결어 없이 need를 더할 수 없다.|to needed~$to 뒤 과거형은 불가하다.','customers가 assistance를 필요로 한다.'),
 q('ED','The items{S} / ------- online will arrive tomorrow{M}.','ordered|ordering~$물품은 주문되는 대상이다.|order~$will arrive 외에 독립 동사를 추가할 수 없다.|to ordering~$부정사 to 뒤 -ing는 맞지 않는다.','items가 온라인으로 주문된 대상이다.'),
 q('EMO','The clients{S} / were{V} / ------- with the service{C}.','satisfied|satisfying~$고객이 만족을 유발하는 성질보다 만족한 상태를 말한다.|satisfaction~n|satisfy~base','고객이 만족을 느끼며 satisfied with로 결합한다.'),
 q('HAVING','------- the final draft{M}, / Ms. Park{S} / sent{V} / it{O} / to the client{M}.','Having reviewed|Having been reviewed~$Park가 검토당한 것이 아니라 초안을 검토했다.|Reviews~$주어 없는 정형 동사가 되어 연결되지 않는다.|To reviewed~$to 뒤 과거형은 불가하다.','Park가 먼저 검토를 마친 뒤 전송했다.'),
 q('GER','Please avoid{V} / ------- the device near water{O}.','using|use~base|to use~to|used~pp','avoid는 동명사를 취한다.'),
 q('INF','We{S} / plan{V} / ------- the showroom{O}.','to expand|expanding~ing|expand~base|expanded~pp','plan 뒤 to부정사를 쓴다.'),
 q('PASS','The entrance{S} / is being -------{V}.','cleaned|cleaning~ing|clean~base|to clean~to','출입구가 청소되는 진행 수동태이다.'),
 q('SG','Each of the remaining seats{S} / -------{V} / a clear view{O}.','offers|offer~pl|offering~ing|to offer~to','핵심 주어 each는 단수이다.'),
 q('D','The receptionist{S} / spoke{V} / -------{M}.','quietly|quiet~a|quietness~n|quieter~comp','spoke의 방식을 꾸미는 부사이다.'),
 q('PAST','The team{S} / -------{V} / the equipment{O} / yesterday{M}.','tested|has tested~perf|testing~ing|to test~to','yesterday의 과거 사건이다.')])

setq(9,[
 q('WHO','The employee{S} / ------- manages the account is away today{M}.','who|whose~$뒤 명사 없이 소유격을 쓸 수 없다.|whom~$manages의 주어가 빠진 자리이므로 목적격이 아니다.|where~$장소 관계가 아니라 사람 주어 역할이 필요하다.','employee를 받으며 manages의 주어가 필요하다.'),
 q('WHOSE','The supplier{S} / ------- prices are lowest will receive the order{M}.','whose|who~$prices라는 명사 앞에 소유 관계가 필요하다.|whom~$목적격은 뒤 명사를 소유 형태로 꾸미지 못한다.|where~$장소 관계가 아니다.','공급업체의 가격이라는 소유 관계이며 whose prices가 관계절 주어이다.'),
 q('WHICH','The software,{S} / ------- was updated yesterday, is running smoothly{M}.','which|that~$쉼표로 구분한 비제한적 관계절에는 that을 쓰지 않는다.|whose~$소유격 뒤 명사가 없다.|whom~$사물 선행사와 주어 역할에 맞지 않는다.','software를 받는 쉼표 관계절의 주어이다.'),
 q('WHOM','The client to ------- we sent the estimate{S} / has requested{V} / a call{O}.','whom|who~$전치사 바로 뒤에는 격식 목적격 whom을 쓴다.|whose~$소유격이 들어갈 자리가 아니다.|which~$사물 관계사가 아니라 사람 client를 가리킨다.','to의 목적격이며 선행사는 사람 client이다.'),
 q('WHICH','The policy under ------- we operate{S} / is{V} / being reviewed{C}.','which|that~$전치사 바로 뒤에는 that을 쓰지 않는다.|who~$policy는 사람 선행사가 아니다.|whose~$소유격이 필요한 자리가 아니다.','under의 목적어인 사물 관계대명사이다.'),
 q('WHOSE','We{S} / chose{V} / a system ------- interface is easy to use{O}.','whose|who~$사물 선행사이고 interface 앞 소유 관계가 필요하다.|whom~$목적격으로 소유 관계를 만들지 못한다.|where~$인터페이스의 소유 관계가 아니다.','시스템의 인터페이스라는 관계이며 사물도 whose를 쓸 수 있다.'),
 q('SG','The employee who handles overseas orders{S} / -------{V} / on leave{M}.','is|are~pl|being~ing|to be~to','주절 주어 employee는 단수이며 orders는 관계절 안 목적어이다.'),
 q('WHO','Applicants{S} / ------- meet all requirements will be contacted{M}.','who|whose~$뒤 동사 앞에 주어가 필요하며 소유 명사가 없다.|whom~$목적격이 아니라 meet의 주어 자리이다.|where~$장소 관계가 아니다.','Applicants를 받는 관계절 주어가 필요하다.')],[
 q('WHOSE','The designer{S} / ------- work won the award will speak today{M}.','whose|who~$work 앞 소유 관계가 필요하다.|whom~$목적격으로 work를 꾸밀 수 없다.|where~$장소 관계가 아니다.','디자이너의 작품이라는 관계이다.'),
 q('WHICH','The invoice,{S} / ------- includes delivery, totals $240{M}.','which|that~$쉼표 관계절에는 that을 쓰지 않는다.|whom~$사물이면서 주어 역할이다.|whose~$뒤 소유 명사가 없다.','invoice를 가리키는 부가 설명의 주어이다.'),
 q('WHOM','The officer with ------- we spoke{S} / was{V} / helpful{C}.','whom|who~$전치사 바로 뒤 목적격이 필요하다.|which~$사람 officer를 가리킨다.|whose~$소유 관계가 아니다.','with의 목적격이며 officer는 사람이다.'),
 q('WHO','The technician{S} / ------- repaired the printer left a note{M}.','who|whom~$repaired의 주어 자리이다.|whose~$소유 명사가 없다.|where~$장소 관계가 아니다.','technician을 받는 관계절 주어이다.'),
 q('ING','Employees{S} / ------- remotely need secure access{M}.','working|worked~$직원이 일하는 능동 관계이다.|work~$주절 need가 이미 있어 독립 동사를 추가할 수 없다.|to worked~$to 뒤 과거형은 불가하다.','직원이 원격으로 일하는 현재분사 수식이다.'),
 q('GER','We{S} / are committed{V} / to ------- access{M}.','improving|improve~base|to improve~to|improved~pp','committed to의 to는 전치사이다.'),
 q('PASS','The request{S} / has been -------{V}.','approved|approving~ing|approve~base|to approve~to','요청이 승인된 완료 수동태이다.'),
 q('SG','The number of applicants{S} / -------{V} / rising{C}.','is|are~pl|being~ing|to be~to','핵심 주어 number에 단수 is를 맞춘다.'),
 q('D','The terms{S} / were ------- explained{V}.','clearly|clear~a|clarity~n|clarify~v','explained를 수식하는 부사이다.'),
 q('A','The report{S} / made{V} / the problem{O} / -------{C}.','obvious|obviously~d|obviousness~n|oblivious~$문제가 분명해졌다는 뜻이며 oblivious는 알아차리지 못하는 상태이다.','problem의 상태를 설명하는 보어이다.')])

setq(10,[
 q('WHERE','This{S} / is{V} / the room ------- we hold interviews{C}.','where|which~$hold의 목적어 interviews가 이미 있어 장소 관계가 필요하다.|who~$사람 주어 역할이 아니다.|whose~$소유 명사를 이끄는 구조가 아니다.','we hold interviews는 목적어까지 있고 장소 관계가 필요하다.'),
 q('WHEN','We{S} / remember{V} / the day ------- the store opened{O}.','when|where~$day는 시간 선행사이다.|who~$사람 주어 역할이 아니다.|whose~$소유 관계가 아니다.','the store opened 뒤 시간 관계를 보충한다.'),
 q('WHY','We{S} / understand{V} / the reason ------- the delivery was delayed{O}.','why|where~$장소 관계가 아니다.|who~$사람 주어 역할이 아니다.|whose~$소유 명사를 이끌지 않는다.','reason과 완성된 수동절의 이유 관계이다.'),
 q('WHICH','The building ------- we purchased{S} / needs{V} / repairs{O}.','which|where~$purchased의 목적어가 빠져 있어 장소 부사로 채울 수 없다.|who~$building은 사람 선행사가 아니다.|whose~$뒤 명사의 소유 관계가 아니다.','purchased의 목적어는 building이다.'),
 q('WHERE','The hotel ------- we stayed{S} / was{V} / near the station{M}.','where|which~$stay는 여기서 자동사라 직접 목적격 which를 받지 않는다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','we stayed의 장소 관계이며 at which로 바꿀 수 있다.'),
 q('PREP','The date ------- which payment is due{S} / appears{V} / on the invoice{M}.','on|with~$날짜의 시간 관계는 on을 쓴다.|by~$payment is due는 특정 납기일의 상태를 말하므로 여기서는 on which가 자연스럽다.|of~$due와 날짜를 연결하는 시간 전치사가 아니다.','on which가 the date의 시간 관계를 나타낸다.'),
 q('WHICH','The office ------- she manages{S} / has{V} / twenty employees{O}.','which|where~$manages의 목적어가 빠졌으므로 관계대명사가 필요하다.|who~$office는 사람이 아니다.|whose~$소유 명사가 뒤에 없다.','사무실은 장소이지만 manages의 직접 목적어이다.'),
 q('WHERE','Please visit{V} / the page ------- the instructions are displayed{O}.','where|who~$사람 주어 역할이 아니다.|whose~$소유 관계가 아니다.|whom~$사람 목적격이 아니다.','the instructions are displayed는 완성된 절이고 표시되는 위치 관계가 필요하다.')],[
 q('WHERE','The warehouse ------- we store spare parts{S} / will close{V} / next week{M}.','where|which~$store의 목적어 spare parts가 이미 있다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','창고에서 보관한다는 장소 관계이다.'),
 q('WHEN','July is the month{S} / ------- most staff take leave{M}.','when|where~$month는 시간 선행사이다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','most staff take leave의 시간 관계이다.'),
 q('WHICH','The room ------- we booked{S} / has{V} / a screen{O}.','which|where~$booked의 목적어가 필요하다.|who~$room은 사람이 아니다.|whose~$소유 명사가 없다.','room이 booked의 목적어이다.'),
 q('WHY','The notice{S} / explains{V} / the reason ------- access is restricted{O}.','why|where~$장소 관계가 아니다.|who~$사람 주어 관계가 아니다.|whose~$소유 관계가 아니다.','제한 이유를 설명하는 reason의 관계절이다.'),
 q('WHOSE','The client ------- order was lost{S} / requested{V} / a refund{O}.','whose|who~$order 앞 소유 관계가 필요하다.|whom~$목적격으로 order를 꾸밀 수 없다.|where~$장소 관계가 아니다.','고객의 주문이라는 소유 관계이다.'),
 q('WHOM','The person to ------- you should speak{S} / is{V} / Ms. Lee{C}.','whom|who~$전치사 바로 뒤 목적격이 필요하다.|which~$사람 선행사이다.|whose~$소유 관계가 아니다.','to의 목적격 사람 관계사이다.'),
 q('GER','We{S} / look forward{V} / to ------- you{M}.','welcoming|welcome~base|to welcome~to|welcomed~pp','전치사 to 뒤 동명사이다.'),
 q('PASS','All appointments{S} / have been -------{V}.','confirmed|confirming~ing|confirm~base|to confirm~to','예약이 확인된 완료 수동태이다.'),
 q('PL','The directions on the website{S} / -------{V} / accurate{C}.','are|is~sg|being~ing|to be~to','핵심 주어 directions는 복수이다.'),
 q('D','The location{S} / is ------- marked{V} / on the map{M}.','clearly|clear~a|clarity~n|clarify~v','수동 분사 marked를 꾸미는 부사이다.')])

setq(11,[
 q('CONJ','------- the truck arrived late{M}, / the event{S} / started{V} / on time{M}.','Although|Despite~prep|During~prep|Because of~prep','뒤가 절이고 지연에도 정시 시작했다는 양보이다.'),
 q('CONJ','The office{S} / closed{V} / ------- the power supply failed{M}.','because|because of~prep|despite~prep|during~prep','뒤가 절이며 전력 장애가 폐점 이유이다.'),
 q('CONJ','The order{S} / will remain{V} / on hold{C} / ------- payment arrives{M}.','until|during~prep|within~prep|by~prep','보류 상태가 대금 도착 때까지 지속된다.'),
 q('CONJ','The discount{S} / applies{V} / ------- the order exceeds $300; smaller orders pay the regular price{M}.','provided that|even though~$양보가 아니라 할인 적용 조건이다.|whereas~$대조 절이 아니라 할인 적용 조건이 필요하다.|now that~$이미 확정된 이유가 아니라 일반 조건 규정이다.','300달러 초과라는 조건이며 작은 주문은 정상가이다.'),
 q('CONJ','The store{S} / will not accept{V} / a return{O} / ------- you provide a receipt{M}.','unless|although~$영수증 제공은 양보가 아니라 수락에 필요한 조건이다.|whereas~$대조가 아니라 조건이다.|because~$영수증을 제공해서 거절한다는 반대 의미가 된다.','영수증을 제시하지 않으면 반품을 받지 않는다는 조건이다.'),
 q('LOGIC','Save the confirmation code{M}; / -------, you may be unable to track the order{M}.','otherwise|moreover~$추가 정보가 아니라 지시를 안 따랐을 때의 결과이다.|similarly~$유사 사례를 비교하지 않는다.|instead~$대안 행동이 아니다.','코드를 저장하지 않았을 때 추적이 어려울 수 있다.'),
 q('LOGIC','The train was canceled{M}; / -------, we booked a bus{M}.','therefore|nevertheless~$대조가 아니라 취소 때문에 취한 후속 조치이다.|similarly~$유사 사례가 아니다.|otherwise~$지시 불이행의 가정 결과가 아니다.','열차 취소로 버스를 예약한 결과 관계이다.'),
 q('CONJ','The new process{S} / is{V} / both efficient ------- reliable{C}.','and|or~$both와 짝을 이루는 접속사는 and이다.|nor~$neither와 결합하는 형태이다.|but~$both의 병렬 짝이 아니다.','both A and B로 두 형용사를 병렬 연결한다.')],[
 q('CONJ','------- demand increased{M}, / we{S} / hired{V} / two assistants{O}.','Because|Because of~prep|Despite~prep|During~prep','완전한 절을 이유로 연결한다.'),
 q('LOGIC','The design is attractive{M}; / -------, it is too costly for this project{M}.','however|therefore~$매력적이어서 비싸다는 인과관계가 제시되지 않았다.|similarly~$장점과 예산 제약을 유사 관계로 연결할 수 없다.|otherwise~$지시 불이행 결과가 아니다.','매력적이라는 장점과 비용 제약을 대조한다.'),
 q('CONJ','Please wait until{M} / the light{S} / turns{V} / green{C} / ------- opening the door{M}.','before|because~$뒤 동명사구를 절처럼 직접 이끌지 못한다.|although~$뒤 동명사구를 직접 이끌지 못한다.|unless~$조건절이 아니라 동명사구 앞 시간 전치사이다.','문을 열기 전까지 기다리라는 시간 관계이며 before 뒤 동명사이다.'),
 q('CONJ','You{S} / may register{V} / either online ------- by mail{M}.','or|and~$either의 짝은 or이다.|nor~$neither의 짝이다.|but~$either의 짝이 아니다.','either A or B로 등록 대안을 연결한다.'),
 q('WHERE','The room ------- we meet{S} / is{V} / upstairs{M}.','where|which~$meet가 여기서 목적어 없이 쓰이고 장소 관계가 필요하다.|who~$사람 주어 관계가 아니다.|whose~$소유 관계가 아니다.','회의하는 장소 관계이다.'),
 q('WHOSE','The applicant ------- résumé impressed us{S} / was invited{V} / for an interview{M}.','whose|who~$résumé 앞 소유 관계가 필요하다.|whom~$소유 명사를 꾸미지 못한다.|where~$장소 관계가 아니다.','지원자의 이력서라는 관계이다.'),
 q('GER','Please avoid{V} / ------- large files{O}.','uploading|upload~base|to upload~to|uploaded~pp','avoid 뒤 동명사이다.'),
 q('PASS','The venue{S} / has been -------{V}.','reserved|reserving~ing|reserve~base|to reserve~to','행사장이 예약된 완료 수동태이다.'),
 q('SG','Each of the options{S} / -------{V} / a separate fee{O}.','has|have~pl|having~ing|to have~to','Each는 단수 주어이다.'),
 q('D','The staff{S} / responded{V} / -------{M}.','efficiently|efficient~a|efficiency~n|efficiencies~n','응답 행동을 수식하는 부사이다.')])

setq(12,[
 q('PREP','Please submit{V} / the application{O} / ------- noon tomorrow{M}.','by|until~$제출을 계속하는 것이 아니라 정오까지 완료하라는 마감이다.|within~$within 뒤에는 시점이 아니라 기간이 필요하다.|during~$noon은 지속 기간이 아니라 시점이다.','제출 완료의 마감 시점이다.'),
 q('PREP','The reception desk{S} / will remain{V} / open{C} / ------- six{M}.','until|by~$개방 상태가 지속되는 끝점을 나타내야 한다.|within~$시각 six는 기간이 아니다.|during~$시각을 기간처럼 취하지 않는다.','열린 상태가 6시까지 지속된다.'),
 q('PREP','We{S} / will respond{V} / ------- three business days{M}.','within|during~$3영업일 이내라는 응답 기한 범위에는 within이 적절하다.|at~$시각 전치사이며 기간 범위를 나타내지 않는다.|on~$날짜가 아니라 기간이다.','응답에 걸리는 최대 기간 안을 나타낸다.'),
 q('PREP','The seminar{S} / starts{V} / ------- 10 a.m.{M}.','at|on~$날짜·요일이 아니라 시각이다.|in~$월·연도가 아니라 시각이다.|within~$기간이 아닌 시각이다.','정확한 시각 앞에는 at을 쓴다.'),
 q('PREP','All contractors{S} / must comply{V} / ------- the rules{M}.','with|to~$comply는 with와 결합한다.|for~$준수 대상을 연결하는 결합이 아니다.|at~$규정 준수의 결합이 아니다.','comply with rules라는 결합이다.'),
 q('GER','In addition to ------- the form{M}, / staff{S} / must attach{V} / a receipt{O}.','completing|complete~base|to complete~to|completed~pp','in addition to의 to는 전치사이다.'),
 q('PREP','------- the short notice{M}, / most employees{S} / attended{V}.','Despite|Although~conj|Even though~conj|Because~conj','명사구를 취하면서 촉박한 통보에도 참석했다는 양보이다.'),
 q('PREP','The discount{S} / is available{V} / ------- members only{M}.','to|by~$이용 가능한 대상은 available to로 연결한다.|of~$혜택 대상을 연결하는 결합이 아니다.|at~$회원이라는 수혜 대상을 장소로 연결하지 않는다.','혜택을 이용할 수 있는 대상은 available to로 쓴다.')],[
 q('PREP','The workshop{S} / will be held{V} / ------- September 8{M}.','on|at~$날짜 앞에는 on이다.|in~$월 전체가 아니라 구체적 날짜이다.|within~$기간이 아니라 날짜이다.','구체적인 날짜 앞에는 on이다.'),
 q('PREP','The branch{S} / opened{V} / ------- 2022{M}.','in|on~$연도에는 in이다.|at~$시각이 아니라 연도이다.|within~$기간 범위가 아니라 연도이다.','연도 앞에는 in이다.'),
 q('PREP','Our decision{S} / depends{V} / ------- the results{M}.','on|to~$depend는 on과 결합한다.|for~$판단 근거를 연결하는 결합이 아니다.|with~$depend with는 이 의미의 결합이 아니다.','depend on으로 의존 대상을 연결한다.'),
 q('PREP','The fee{S} / was waived{V} / ------- the delay{M}.','because of|because~conj|although~conj|unless~conj','the delay는 명사구이며 지연이 면제 이유이다.'),
 q('WHEN','We{S} / remember{V} / the year ------- the center opened{O}.','when|where~$시간 선행사 year이다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','개장한 연도의 시간 관계이다.'),
 q('WHOSE','The supplier ------- delivery was late{S} / apologized{V}.','whose|who~$delivery 앞 소유 관계가 필요하다.|whom~$소유 관계를 나타내지 못한다.|where~$장소 관계가 아니다.','공급업체의 배송이라는 소유 관계이다.'),
 q('GER','We{S} / finished{V} / ------- the files{O}.','organizing|organize~base|to organize~to|organized~pp','finish 뒤 동명사이다.'),
 q('PASS','The room{S} / is being -------{V}.','prepared|preparing~ing|prepare~base|to prepare~to','방이 준비되는 진행 수동태이다.'),
 q('PL','The copies in this folder{S} / -------{V} / current{C}.','are|is~sg|being~ing|to be~to','주어 copies가 복수이다.'),
 q('A','The procedure{S} / is{V} / -------{C}.','simple|simply~d|simplicity~n|simplify~v','절차의 상태를 설명하는 형용사이다.')])

setq(13,[
 q('POSS','Please attach{V} / ------- résumé{O}.','your|you~subj|yours~posspro|yourself~self','뒤 명사 résumé를 꾸미는 소유격이 필요하다.'),
 q('OBJ','The receptionist{S} / will call{V} / -------{O} / when your room is ready{M}.','you|your~poss|yours~posspro|yourself~$주어 receptionist와 상대방 you는 다른 사람이므로 재귀대명사가 아니다.','call의 대상인 상대방을 목적격으로 쓴다.'),
 q('POSSPRO','Our office{S} / is{V} / smaller than -------{C}.','theirs|their~poss|them~obj|they~subj','비교 대상은 their office이며 명사를 생략한 소유대명사이다.'),
 q('SELF','Ms. Lee{S} / introduced{V} / -------{O} / to the new staff{M}.','herself|her~$소개하는 주체와 소개되는 대상이 같은 Ms. Lee이다.|hers~posspro|she~subj','주어와 목적어가 같은 인물이므로 재귀대명사이다.'),
 q('SELF','The designers{S} / prepared{V} / the display{O} / -------{M}.','themselves|their~poss|theirs~posspro|they~subj','목적어 display가 이미 있고 직접 준비했다는 강조이다.'),
 q('OTHER','This printer is unavailable{M}; / please use{V} / ------- one{O}.','another|others~$others는 자체 복수 대명사라 one 앞 수식어로 쓰지 못한다.|the others~$정해진 나머지 전부를 가리키는 복수 대명사이다.|each other~$서로라는 관계를 나타낸다.','대신 사용할 불특정 다른 프린터 하나이다.'),
 q('OTHER','Some customers prefer e-mail{M}; / -------{S} / prefer{V} / telephone calls{O}.','others|other~$뒤 복수 명사가 필요하다.|another~$단수 대명사이므로 복수 동사 prefer와 맞지 않는다.|the other~$정해진 둘 중 나머지 하나라는 문맥이 아니며 수도 맞지 않는다.','불특정 다른 여러 고객들이므로 others이다.'),
 q('OTHER','The workshop{S} / is{V} / open to ------- who registered online{C}.','those|them~$제한적 who절을 받는 일반적 표현은 those who이다.|their~poss|theirs~posspro','those who registered는 온라인으로 등록한 사람들이다.')],[
 q('POSS','The visitors{S} / left{V} / ------- bags{O} / at reception{M}.','their|they~subj|them~obj|theirs~posspro','bags 앞 소유격이다.'),
 q('OBJ','Please send{V} / the file{O} / to -------{M}.','me|I~subj|my~poss|mine~posspro','전치사 to의 목적어로 목적격 me를 쓴다.'),
 q('SELF','The manager{S} / completed{V} / the audit{O} / -------{M}.','herself|her~obj|hers~posspro|she~subj','목적어 audit가 이미 있고 관리자가 직접 했다는 강조이다.'),
 q('OTHER','We ordered two lamps{M}; / one is blue and ------- is gray{M}.','the other|another~$두 개 중 정해진 나머지 하나이므로 the other이다.|others~$복수이며 동사 is와 맞지 않는다.|other~$단독 단수 대명사 형태로 정해진 나머지를 나타내지 못한다.','두 램프 중 하나를 제외한 나머지 하나이다.'),
 q('PREP','Please reply{V} / ------- Friday{M}.','by|until~$한 번의 회신 완료 마감이다.|within~$기간이 아니라 요일이다.|during~$요일 하나를 완료 기한으로 연결하지 못한다.','금요일까지 회신을 완료하라는 기한이다.'),
 q('CONJ','------- the item was damaged{M}, / the store{S} / issued{V} / a refund{O}.','Because|Because of~prep|Despite~prep|During~prep','뒤가 완전한 절이며 손상이 환불 이유이다.'),
 q('WHERE','The desk ------- visitors check in{S} / has moved{V}.','where|which~$check in은 여기서 목적어 없는 구동사라 장소 관계가 필요하다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','방문자가 접수하는 장소 관계이다.'),
 q('GER','We{S} / are considering{V} / ------- a new system{O}.','buying|buy~base|to buy~to|bought~pp','consider 뒤 동명사를 쓴다.'),
 q('PASS','The room{S} / has been -------{V}.','cleaned|cleaning~ing|clean~base|to clean~to','청소가 끝난 완료 수동태이다.'),
 q('SG','Each of the branches{S} / -------{V} / a separate account{O}.','has|have~pl|having~ing|to have~to','주어 Each는 단수이다.')])

setq(14,[
 q('COMP','The new route{S} / is{V} / ------- than the old one{C}.','shorter|shortest~super|short~a|shortly~d','than으로 두 경로를 비교한다.'),
 q('SUPER','This{S} / is{V} / the ------- option of the three{C}.','cheapest|cheaper~comp|cheap~a|cheaply~d','세 선택지 범위 안에서 최저 가격을 나타낸다.'),
 q('AS','The new device{S} / is{V} / as ------- as the earlier model{C}.','reliable|more reliable~comp|most reliable~super|reliably~d','as와 as 사이에 형용사 원급을 쓴다.'),
 q('EMPH','The revised process{S} / is{V} / ------- more efficient{C}.','much|very~$very는 보통 비교급을 직접 강조하지 않는다.|many~$가산 복수명사를 수식하는 수량 표현이다.|most~$more와 최상급 강조를 겹쳐 쓰지 않는다.','much는 비교급 more efficient를 강조한다.'),
 q('OTHER','Our rates{S} / are{V} / lower than ------- of nearby hotels{C}.','those|that~$앞 복수명사 rates를 대신하므로 those이다.|this~$단수 지시어이며 rates와 수가 다르다.|them~$비교에서 앞 복수명사를 those of로 대신한다.','rates와 다른 호텔의 rates를 비교하며 복수 those가 필요하다.'),
 q('COMP','The sooner we receive the file{M}, / the ------- we can finish{M}.','earlier|earliest~super|early~a|earliness~n','the+비교급, the+비교급의 비례 변화 구조이다.'),
 q('COMP','The office{S} / is{V} / ------- than we expected{C}.','larger|largest~super|large~a|largely~d','기대했던 크기와 비교하므로 larger이다.'),
 q('SUPER','This model{S} / has{V} / the ------- maintenance costs in the series{O}.','lowest|lower~comp|low~a|lowly~a','시리즈 전체 범위에서 최저 유지비이다.')],[
 q('COMP','The express service{S} / is{V} / ------- than standard delivery{C}.','faster|fastest~super|fast~a|fasting~ing','than이 비교급을 요구한다.'),
 q('AS','The assistant{S} / works{V} / as ------- as the supervisor{M}.','quickly|more quickly~comp|most quickly~super|quick~a','works를 꾸미는 부사 원급이 as ... as 사이에 필요하다.'),
 q('SUPER','It{S} / is{V} / the ------- room in the building{C}.','quietest|quieter~comp|quiet~a|quietly~d','건물 안의 전체 방 중 최상급이다.'),
 q('OTHER','The price of this model{S} / is{V} / higher than ------- of the older model{C}.','that|those~$단수 price를 대신하므로 that이다.|these~$복수 지시어이다.|them~$비교에서 단수 명사를 대신하는 that of가 필요하다.','price와 price를 비교하며 단수 that을 쓴다.'),
 q('POSS','Please verify{V} / ------- contact details{O}.','your|you~subj|yours~posspro|yourself~self','명사 contact details 앞 소유격이다.'),
 q('PREP','The offer{S} / remains{V} / valid{C} / ------- Monday{M}.','until|within~$Monday는 기간이 아니라 시점이다.|during~$유효 상태의 끝점을 나타내야 한다.|at~$요일의 지속 끝점 전치사가 아니다.','유효 상태가 월요일까지 지속된다.'),
 q('WHOSE','The company ------- products we sell{S} / has expanded{V}.','whose|who~$products 앞 소유 관계가 필요하다.|whom~$소유 명사를 꾸미지 못한다.|where~$장소 관계가 아니다.','회사의 제품이라는 소유 관계이다.'),
 q('GER','The supplier{S} / avoided{V} / ------- extra fees{O}.','charging|charge~base|to charge~to|charged~pp','avoid 뒤 동명사이다.'),
 q('PASS','The estimate{S} / has been -------{V}.','revised|revising~ing|revise~base|to revise~to','견적이 수정된 완료 수동태이다.'),
 q('D','The new printer{S} / runs{V} / -------{M}.','quietly|quiet~a|quietness~n|quieter~comp','runs의 방식을 꾸미는 부사이다.')])

setq(15,[
 q('IFPAST','If we ------- more storage space{M}, / we{S} / would order{V} / extra stock{O}.','had|have~$현재 반대 가정이므로 단순현재 조건형이 아니다.|will have~$if절 현재 반대 가정에 미래형을 쓰지 않는다.|having~ing','would order의 현재 가정 조건절이므로 had이다.'),
 q('IFPAST','If I ------- available today{M}, / I{S} / would attend{V} / the meeting{O}.','were|am~$현재 사실 반대 가정의 격식 형태가 필요하다.|will be~future|being~ing','오늘 시간이 없다는 현재 가정으로 were를 쓴다.'),
 q('IFPERF','If we ------- the address last week{M}, / the parcel{S} / would have arrived{V} / on time{M}.','had checked|check~base|will check~future|checking~ing','지난주 행동의 반대를 가정하는 if절이다.'),
 q('IFRESULT','If the team had left earlier{M}, / it{S} / ------- the train{V}.','would have caught|will catch~future|catching~ing|to catch~to','과거에 늦게 출발해 놓친 결과의 반대 가정이다.'),
 q('INV','------- you need assistance{M}, / please call{V} / the front desk{O}.','Should|Would~$이 조건 도치는 If you should need의 should를 앞으로 옮긴 형태이다.|Had~$had 뒤에는 need 원형이 아니라 과거분사가 필요한 다른 구조이다.|Were~$were need라는 동사구를 만들지 못한다.','If you should need에서 if를 생략한 조건 도치이다.'),
 q('INV','------- we known about the delay{M}, / we{S} / would have changed{V} / the schedule{O}.','Had|Have~$과거 반대 가정의 도치이므로 had이다.|Did~$did 뒤 과거분사 known을 쓸 수 없다.|Will~$will 뒤 과거분사 known을 쓸 수 없다.','If we had known의 if 생략 도치이다.'),
 q('MAND','The auditor{S} / requested{V} / that all receipts ------- attached{O}.','be|being~ing|been~pp|to be~to','요구 내용의 that절은 원형을 쓰며 영수증은 첨부되는 대상이다.'),
 q('MAND','The manager{S} / recommended{V} / that the supplier ------- contacted{O}.','be|being~ing|been~pp|to be~to','권고절의 수동 구조 be contacted이다.')],[
 q('IFPERF','If the driver ------- earlier yesterday{M}, / we{S} / would have received{V} / the goods{O}.','had called|calls~sg|will call~future|calling~ing','이미 끝난 어제 상황의 반대 가정이다.'),
 q('IFRESULT','If we had reserved a room{M}, / we{S} / ------- a place to meet{V}.','would have had|will have~future|having~ing|to have~to','과거 예약 실패 결과의 반대를 나타낸다.'),
 q('IFPAST','If the office ------- larger{M}, / we{S} / would hire{V} / more staff{O}.','were|is~$현재 사실 반대 가정이므로 were이다.|will be~future|being~ing','현재 공간이 작다는 반대 가정이다.'),
 q('MAND','The director{S} / required{V} / that the report ------- submitted today{O}.','be|being~ing|been~pp|to be~to','요구절에서 수동 be submitted를 쓴다.'),
 q('COMP','The new route{S} / is{V} / ------- than the previous one{C}.','safer|safest~super|safe~a|safely~d','두 경로 비교이므로 safer이다.'),
 q('POSSPRO','Their schedule{S} / is{V} / similar to -------{C}.','ours|our~poss|us~obj|we~subj','our schedule을 대신하는 소유대명사이다.'),
 q('PREP','Please finish{V} / the work{O} / ------- Friday{M}.','by|until~$작업을 마치는 완료 기한이다.|within~$요일은 기간이 아니다.|during~$요일을 완료 기한으로 연결하지 못한다.','금요일까지 완료하라는 뜻이다.'),
 q('WHERE','The venue ------- we held the seminar{S} / has closed{V}.','where|which~$held의 목적어 the seminar가 이미 있다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','행사를 개최한 장소 관계이다.'),
 q('GER','We{S} / considered{V} / ------- the session{O}.','postponing|postpone~base|to postpone~to|postponed~pp','consider 뒤 동명사이다.'),
 q('SG','The number of vacant rooms{S} / -------{V} / small{C}.','is|are~pl|being~ing|to be~to','수치 number가 단수이다.')])

setq(16,[
 q('UNC','Please send{V} / additional -------{O} / about the course{M}.','information|informations~$information은 이 의미에서 불가산으로 복수형을 쓰지 않는다.|an information~$불가산 information 앞에 an을 붙이지 않는다.|inform~v','추가 정보는 불가산명사 information이다.'),
 q('ART','The inspection{S} / takes{V} / about ------- hour{O}.','an|a~$hour는 h가 묵음이고 모음 소리로 시작한다.|these~$복수 한정사가 단수 hour와 맞지 않는다.|many~$many 뒤에는 가산 복수명사가 필요하다.','hour의 발음이 모음 소리로 시작하므로 an이다.'),
 q('ART','She{S} / works{V} / at ------- university{M}.','a|an~$university는 /juː/의 자음 소리로 시작한다.|these~$단수 university와 맞지 않는다.|many~$단수 university와 맞지 않는다.','university는 철자 u가 아니라 첫소리 /j/에 따라 a이다.'),
 q('QUANT','We{S} / have{V} / too ------- applications to review today{O}.','many|much~$applications는 가산 복수명사이다.|little~$불가산명사에 쓰며 너무 많다는 문맥과 다르다.|a little~$불가산 수량 표현이며 too와도 맞지 않는다.','applications는 가산 복수이므로 many이다.'),
 q('QUANT','We{S} / have{V} / very ------- time before the deadline{O}.','little|few~$time은 여기서 불가산명사이다.|many~$many는 가산 복수에 쓴다.|a few~$time은 셀 수 있는 복수 의미가 아니다.','시간은 여기서 불가산이며 very little로 거의 없음을 나타낸다.'),
 q('ART','I found a folder{M}; / ------- folder{S} / contains{V} / your forms{O}.','the|an~$folder는 자음 소리로 시작하고 이미 특정되었다.|many~$단수 folder와 맞지 않는다.|these~$복수 한정사로 단수 folder와 맞지 않는다.','앞서 소개된 특정 폴더를 다시 가리킨다.'),
 q('UNC','We{S} / purchased{V} / three ------- for the workshop{O}.','pieces of equipment|equipments~$equipment는 이 의미에서 복수형을 쓰지 않는다.|equipment~$three 뒤에 단위 없는 불가산명사를 둘 수 없다.|a piece of equipment~$three와 단수 관사를 함께 쓸 수 없다.','불가산 equipment를 pieces라는 가산 단위로 센다.'),
 q('QUANT','Only ------- seats{S} / remain{V}, so register now{M}.','a few|a little~$seats는 가산 복수명사이다.|much~$가산 복수에 쓸 수 없다.|an~$단수 관사는 복수 seats 앞에 맞지 않는다.','복수 seats에 a few를 써서 소수나마 남았음을 나타낸다.')],[
 q('UNC','The consultant{S} / gave{V} / us{O} / useful -------{O}.','advice|advices~$이 의미의 advice는 불가산으로 복수형을 쓰지 않는다.|an advice~$불가산 advice에 an을 붙이지 않는다.|advise~v','조언은 불가산명사 advice이고 advise는 동사이다.'),
 q('ART','The session{S} / begins{V} / in ------- hour{M}.','an|a~$hour의 첫소리는 모음이다.|many~$단수 hour와 맞지 않는다.|these~$복수 한정사로 단수 hour와 맞지 않는다.','hour의 h는 묵음이다.'),
 q('QUANT','The project{S} / has made{V} / ------- progress{O}.','much|many~$progress는 불가산명사이다.|a few~$가산 복수 수량 표현이다.|an~$progress는 불가산이고 모음 소리도 아니다.','progress는 불가산명사이다.'),
 q('UNC','All -------{S} / is provided{V} / by the center{M}.','furniture|furnitures~$가구 의미의 furniture는 불가산명사이다.|a furniture~$all과 관사 a를 이처럼 함께 쓰지 않는다.|furnish~v','furniture는 불가산으로 단수 동사 is와 맞는다.'),
 q('MAND','The manager{S} / requested{V} / that the invoice ------- corrected{O}.','be|being~ing|been~pp|to be~to','요구절의 수동은 be+p.p.이다.'),
 q('COMP','This guide{S} / is{V} / ------- than the old one{C}.','clearer|clearest~super|clear~a|clearly~d','than과 두 지침을 비교한다.'),
 q('POSS','Please bring{V} / ------- identification{O}.','your|you~subj|yours~posspro|yourself~self','명사 identification 앞 소유격이다.'),
 q('PREP','The office{S} / is closed{V} / ------- Sundays{M}.','on|at~$요일 앞에는 on이다.|in~$요일 앞에는 on이다.|within~$기간 범위가 아니라 반복 요일이다.','요일 앞 전치사는 on이다.'),
 q('WHERE','The cabinet ------- we keep the files{S} / is{V} / locked{C}.','where|which~$keep의 목적어 the files가 이미 있다.|who~$사람 관계사가 아니다.|whose~$소유 관계가 아니다.','파일을 보관하는 장소 관계이다.'),
 q('GER','The team{S} / finished{V} / ------- the schedule{O}.','updating|update~base|to update~to|updated~pp','finish 뒤 동명사를 쓴다.')])

setq(17,[
 q('A','The estimate{S} / seems{V} / -------{C}.','reasonable|reason~n|reasonably~d|reasoning~ing','seems 뒤 주어의 상태를 나타내는 보어이다.'),
 q('D','The assistant{S} / organized{V} / the files{O} / -------{M}.','neatly|neat~a|neatness~n|neater~comp','organized의 방식을 꾸미는 부사이다.'),
 q('A','Please keep{V} / your password{O} / -------{C}.','secure|security~n|securely~d|securing~ing','password의 상태를 설명하는 목적격 보어이다.'),
 q('D','The advice{S} / was{V} / ------- useful{C}.','extremely|extreme~a|extremes~n|extremity~n','형용사 useful의 정도를 수식한다.'),
 q('VOC','The technicians{S} / worked{V} / ------- to restore service{M}.','hard|hardly~$거의 일하지 않았다는 뜻으로 복구 노력 문맥과 다르다.|hardness~n|harder than~$than 뒤 비교 대상이 없어 문장이 완성되지 않는다.','서비스 복구를 위해 열심히 일했다는 뜻이다.'),
 q('VOC','We{S} / have{V} / ------- any spare parts left, so we must order more{O}.','hardly|hard~$열심히·단단하게라는 뜻으로 수량 부정 표현이 아니다.|high~$수량이 거의 없다는 의미가 아니다.|late~$늦게라는 뜻으로 수량을 한정하지 못한다.','hardly any는 거의 없다는 뜻으로 추가 주문 이유와 맞는다.'),
 q('D','The revised service{S} / is{V} / ------- more reliable{C}.','considerably|considerable~a|consideration~n|consider~v','비교급 more reliable의 정도를 꾸미는 부사이다.'),
 q('VOC','The train{S} / arrived{V} / -------, and we missed the connection{M}.','late|lately~$최근에라는 뜻으로 지연 도착의 의미가 아니다.|latest~super|lateness~n','연결편을 놓친 원인이므로 늦게 도착했다는 late이다.')],[
 q('A','The response{S} / was{V} / -------{C}.','helpful|help~n|helpfully~d|helping~ing','응답의 상태를 설명하는 형용사 보어이다.'),
 q('D','The contract{S} / was ------- reviewed{V}.','thoroughly|thorough~a|thoroughness~n|through~$통과·~을 통해라는 뜻으로 검토 방식을 나타내지 않는다.','reviewed를 꾸미는 부사이다.'),
 q('D','The new software{S} / is{V} / ------- easy to use{C}.','remarkably|remarkable~a|remark~n|remarks~n','형용사 easy의 정도를 꾸민다.'),
 q('A','Please leave{V} / the reception area{O} / -------{C}.','tidy|tidily~d|tidiness~n|tidying~ing','area의 정돈된 상태를 보충한다.'),
 q('UNC','We{S} / need{V} / more -------{O}.','equipment|equipments~$불가산명사로 복수형을 쓰지 않는다.|an equipment~$불가산명사에 an을 붙이지 않는다.|equip~v','equipment는 불가산명사이다.'),
 q('IFPERF','If we ------- the warning{M}, / we{S} / would have avoided{V} / the error{O}.','had noticed|notice~base|will notice~future|noticing~ing','과거 사실 반대의 조건절이다.'),
 q('AS','The second room{S} / is{V} / as ------- as the first{C}.','spacious|more spacious~comp|most spacious~super|spaciously~d','as ... as 사이 형용사 원급이다.'),
 q('OBJ','The clerk{S} / handed{V} / -------{O} / a receipt{O}.','us|we~subj|our~poss|ours~posspro','물건을 받은 사람을 간접목적어 목적격으로 쓴다.'),
 q('CONJ','------- the printer is old{M}, / it{S} / works{V} / well{M}.','Although|Despite~prep|During~prep|Because of~prep','뒤 절과 양보 관계를 만드는 접속사이다.'),
 q('WHOSE','The employee ------- desk is near the door{S} / handles{V} / deliveries{O}.','whose|who~$desk 앞 소유 관계가 필요하다.|whom~$소유 명사를 꾸미지 못한다.|where~$장소 관계가 아니다.','직원의 책상이라는 소유 관계이다.')])

setq(18,[
 q('VOC','The manager{S} / will -------{V} / the concern{O} / at the briefing{M}.','address|mail~$우려를 우편으로 보낸다는 뜻이 되어 문제를 다룬다는 문맥과 다르다.|locate~$위치를 찾는 뜻으로 우려를 논의하는 행동과 다르다.|deliver~$우려를 전달하는 것이 아니라 해결 대상으로 다룬다.','address a concern은 우려를 다루다는 결합이다.'),
 q('VOC','Please -------{V} / an order{O} / through the website{M}.','place|do~$주문하다의 자연스러운 결합은 place an order이다.|perform~$과업을 수행하다의 뜻으로 order와 결합하지 않는다.|attend~$참석하다라는 뜻이다.','주문하다는 place an order이다.'),
 q('VOC','The store{S} / agreed{V} / to ------- a refund{O}.','issue|attend~$참석하다라는 뜻으로 refund와 맞지 않는다.|arise~$발생하다라는 자동사로 refund를 목적어로 취하지 못한다.|arrive~$도착하다라는 자동사이다.','환불을 처리하다는 issue a refund이다.'),
 q('VOC','We{S} / must -------{V} / the deadline{O}.','meet|attend~$행사에 참석하다는 뜻으로 기한을 지킨다는 결합이 아니다.|arrive~$자동사로 deadline을 직접 목적어로 취하지 못한다.|occur~$발생하다라는 자동사이다.','기한을 지키다는 meet a deadline이다.'),
 q('VOC','The charity{S} / hopes{V} / to ------- funds for the project{O}.','raise|rise~$rise는 자동사이고 funds를 직접 목적어로 취하지 못한다.|arise~$발생하다라는 자동사이다.|arrive~$도착하다라는 자동사이다.','자금을 모으다는 타동사 raise funds이다.'),
 q('PREP','All employees{S} / may participate{V} / ------- the workshop{M}.','in|to~$participate는 in과 결합한다.|at~$이 참여 대상을 연결하는 결합은 in이다.|for~$참여 대상을 연결하지 못한다.','participate in과 attend+행사를 구별한다.'),
 q('VOC','The event{S} / was -------{V} / until August because the venue needed repairs{M}.','postponed|canceled~$until August는 나중으로 옮긴 시점을 나타내며 영구 취소가 아니다.|replaced~$대상 교체가 아니라 일정 연기이다.|renewed~$유효기간 갱신이 아니라 일정 연기이다.','until August라는 새 시점으로 연기되었다.'),
 q('VOC','The meeting room{S} / can -------{V} / forty people{O}.','accommodate|accompany~$동행하다라는 뜻이며 방이 사람을 수용하는 의미가 아니다.|accomplish~$과업을 완수하다는 뜻이다.|accumulate~$축적하다라는 뜻으로 손님 수용과 다르다.','장소의 수용 능력은 accommodate people이다.')],[
 q('VOC','Please check{V} / your mailing -------{O} / before ordering{M}.','address|issue~$문제·발행이라는 뜻으로 우편 목적지와 다르다.|concern~$우려라는 뜻이다.|speech~$연설이라는 뜻이며 mailing과 맞지 않는다.','mailing address는 우편 주소이다.'),
 q('VOC','The company{S} / will -------{V} / its subscription{O} / before it expires{M}.','renew|attend~$참석하다라는 뜻이다.|arise~$발생하다라는 자동사이다.|accommodate~$수용하다라는 뜻으로 구독 연장과 다르다.','만료 전 구독을 갱신하다는 renew a subscription이다.'),
 q('VOC','Sales{S} / have -------{V} / steadily this quarter{M}.','risen|raised~$raise는 타동사인데 증가시키는 목적어가 없다.|arisen~$발생하다보다 수치 증가를 나타내는 rise가 맞다.|arrived~$도착하다는 뜻이다.','매출 수치 자체의 증가는 자동사 rise의 과거분사 risen이다.'),
 q('LOGIC','The item is out of stock{M}; / -------, delivery will take longer{M}.','therefore|nevertheless~$재고 부족과 배송 지연은 양보가 아니라 결과 관계이다.|similarly~$유사 사례가 아니다.|otherwise~$지시 불이행의 가정 결과가 아니다.','재고 부족이 배송 지연의 이유이다.'),
 q('D','The revised manual{S} / explains{V} / the process{O} / -------{M}.','clearly|clear~a|clarity~n|clarify~v','explains를 꾸미는 부사이다.'),
 q('UNC','Please provide{V} / accurate -------{O}.','information|informations~$불가산명사로 복수형을 쓰지 않는다.|an information~$불가산명사에 an을 붙이지 않는다.|inform~v','information은 불가산명사이다.'),
 q('MAND','The supervisor{S} / requested{V} / that all copies ------- checked{O}.','be|being~ing|been~pp|to be~to','요구절의 수동은 be checked이다.'),
 q('COMP','The new plan{S} / is{V} / ------- than the earlier proposal{C}.','simpler|simplest~super|simple~a|simply~d','than과 두 계획을 비교하므로 비교급이다.'),
 q('POSS','Participants{S} / should bring{V} / ------- own devices{O}.','their|they~subj|them~obj|theirs~posspro','own devices 앞 소유격이다.'),
 q('PREP','The supplier{S} / must comply{V} / ------- our policy{M}.','with|to~$comply with가 올바른 결합이다.|for~$준수 대상을 연결하지 못한다.|at~$규정 준수 결합이 아니다.','규정 준수는 comply with이다.')])

THINKING=[
 q('A','The revised instructions{S} / are{V} / -------{C}.','clear|clarity~n|clearly~d|clarify~v','문장의 뼈대는 S+V+C이며 상태 보어가 필요하다.'),
 q('D','The package{S} / was ------- labeled{V}.','incorrectly|incorrect~a|incorrectness~n|correction~n','labeled를 꾸미는 부사가 필요하다.'),
 q('SG','The number of pending requests{S} / -------{V} / small{C}.','is|are~pl|being~ing|to be~to','전치사구를 제외하면 핵심 주어는 number이다.'),
 q('GER','We{S} / are committed{V} / to ------- delays{M}.','reducing|reduce~base|to reduce~to|reduced~pp','전치사 to 뒤 명사 역할인 동명사가 필요하다.'),
 q('WHOSE','The supplier ------- quotation we accepted{S} / will deliver{V} / the chairs{O}.','whose|who~$quotation 앞 소유 관계가 필요하다.|whom~$소유 관계를 나타내지 못한다.|where~$장소 관계가 아니다.','supplier의 quotation이라는 소유 관계이다.'),
 q('PREP','Please complete{V} / the inspection{O} / ------- Friday{M}.','by|until~$완료 마감이며 검사 상태의 지속이 아니다.|within~$요일은 기간이 아니다.|during~$완료 기한을 나타내지 못한다.','완료 기한이므로 by를 고른다.'),
 q('VOC','The hotel{S} / can -------{V} / eighty guests{O}.','accommodate|accompany~$손님과 동행하는 의미가 아니다.|accomplish~$과업을 완수하는 의미이다.|accumulate~$손님 수용이 아니라 축적의 의미이다.','문법적으로 모두 원형이지만 수용하다의 결합만 맞는다.'),
 q('LOGIC','Keep a copy of the receipt{M}; / -------, you may not be able to request a refund{M}.','otherwise|moreover~$추가 사실이 아니라 지시를 따르지 않았을 때의 결과이다.|similarly~$유사 관계가 아니다.|instead~$대안 행동이 아니다.','영수증을 보관하지 않을 경우 생기는 결과이다.')]

def finalize():
    allq=[]
    for c in CH:
        for section in ['practice','review']:
            for i,item in enumerate(c[section],1):
                item.update(id=f'C{c["n"]:02d}-'+('P' if section=='practice' else 'R')+f'{i:02d}',n=i,chapter=c['n'],section=section,
                            level=1 if i<=3 else 2 if i<=6 else 3)
                allq.append(item)
    for i,item in enumerate(THINKING,1):
        item.update(id=f'T-{i:02d}',n=i,chapter=19,section='thinking',level=2);allq.append(item)
    rng=random.Random(20261008)
    positions=[0,1,2,3]*(len(allq)//4)
    positions += list(range(len(allq)%4));rng.shuffle(positions)
    for item,pos in zip(allq,positions):
        correct=item['opts'][0];correctreason=item['analyses'][0]
        wrong=list(zip(item['opts'][1:],item['analyses'][1:]));rng.shuffle(wrong)
        pairs=wrong[:pos]+[(correct,correctreason)]+wrong[pos:]
        item['opts']=[x[0] for x in pairs];item['analyses']=[x[1] for x in pairs]
        item['answer']=chr(65+pos);item['correct']=correct
    return allq

# Explicit structure checks: entire relative clauses stay inside the subject;
# main verbs and the verbs of independent clauses are always visible.
REPAIRS={
 'Thank you{M} / for ------- the issue{M}.':'Thank{V} / you{O} / for ------- the issue{M}.',
 'The documents{S} / ------- to this message are confidential{M}.':'The documents ------- to this message{S} / are{V} / confidential{C}.',
 'Employees{S} / ------- the training should arrive by nine{M}.':'Employees ------- the training{S} / should arrive{V} / by nine{M}.',
 'The rooms{S} / ------- last month are now available{M}.':'The rooms ------- last month{S} / are{V} / now available{C}.',
 'Customers{S} / ------- assistance should call reception{M}.':'Customers ------- assistance{S} / should call{V} / reception{O}.',
 'The items{S} / ------- online will arrive tomorrow{M}.':'The items ------- online{S} / will arrive{V} / tomorrow{M}.',
 'The employee{S} / ------- manages the account is away today{M}.':'The employee ------- manages the account{S} / is{V} / away today{C}.',
 'The supplier{S} / ------- prices are lowest will receive the order{M}.':'The supplier ------- prices are lowest{S} / will receive{V} / the order{O}.',
 'The software,{S} / ------- was updated yesterday, is running smoothly{M}.':'The software, ------- was updated yesterday,{S} / is running{V} / smoothly{M}.',
 'Applicants{S} / ------- meet all requirements will be contacted{M}.':'Applicants ------- meet all requirements{S} / will be contacted{V}.',
 'The designer{S} / ------- work won the award will speak today{M}.':'The designer ------- work won the award{S} / will speak{V} / today{M}.',
 'The invoice,{S} / ------- includes delivery, totals $240{M}.':'The invoice, ------- includes delivery,{S} / totals{V} / $240{O}.',
 'The technician{S} / ------- repaired the printer left a note{M}.':'The technician ------- repaired the printer{S} / left{V} / a note{O}.',
 'Employees{S} / ------- remotely need secure access{M}.':'Employees ------- remotely{S} / need{V} / secure access{O}.',
 'July is the month{S} / ------- most staff take leave{M}.':'July{S} / is{V} / the month ------- most staff take leave{C}.',
 'Save the confirmation code{M}; / -------, you may be unable to track the order{M}.':'Save{V} / the confirmation code{O}; / -------{M}, / you{S} / may be{V} / unable to track the order{C}.',
 'The train was canceled{M}; / -------, we booked a bus{M}.':'The train{S} / was canceled{V}; / -------{M}, / we{S} / booked{V} / a bus{O}.',
 'The design is attractive{M}; / -------, it is too costly for this project{M}.':'The design{S} / is{V} / attractive{C}; / -------{M}, / it{S} / is{V} / too costly for this project{C}.',
 'We ordered two lamps{M}; / one is blue and ------- is gray{M}.':'We{S} / ordered{V} / two lamps{O}; / one{S} / is{V} / blue{C} / and{M} / -------{S} / is{V} / gray{C}.',
 'The sooner we receive the file{M}, / the ------- we can finish{M}.':'The sooner{M} / we{S} / receive{V} / the file{O}, / the -------{M} / we{S} / can finish{V}.',
 'The item is out of stock{M}; / -------, delivery will take longer{M}.':'The item{S} / is{V} / out of stock{C}; / -------{M}, / delivery{S} / will take{V} / longer{M}.',
 'Keep a copy of the receipt{M}; / -------, you may not be able to request a refund{M}.':'Keep{V} / a copy of the receipt{O}; / -------{M}, / you{S} / may not be{V} / able to request a refund{C}.',
 'This printer is unavailable{M}; / please use{V} / ------- one{O}.':'This printer{S} / is{V} / unavailable{C}; / please use{V} / ------- one{O}.',
 'Some customers prefer e-mail{M}; / -------{S} / prefer{V} / telephone calls{O}.':'Some customers{S} / prefer{V} / e-mail{O}; / -------{S} / prefer{V} / telephone calls{O}.',
 'I found a folder{M}; / ------- folder{S} / contains{V} / your forms{O}.':'I{S} / found{V} / a folder{O}; / ------- folder{S} / contains{V} / your forms{O}.',
 'If the team had left earlier{M}, / it{S} / ------- the train{V}.':'If the team had left earlier{M}, / it{S} / -------{V} / the train{O}.',
 'If we had reserved a room{M}, / we{S} / ------- a place to meet{V}.':'If we had reserved a room{M}, / we{S} / -------{V} / a place to meet{O}.',
 'The number of applicants{S} / -------{V} / rising{C}.':'The number of applicants{S} / ------- rising{V}.',
 'The policy under ------- we operate{S} / is{V} / being reviewed{C}.':'The policy under ------- we operate{S} / is being reviewed{V}.',
}
for item in [x for c in CH for sec in ['practice','review'] for x in c[sec]]+THINKING:
    if item['marked'] in REPAIRS:
        item['marked']=REPAIRS[item['marked']]
        item['stem']=re.sub(r'\{[SVOCM]+\}','',item['marked']).replace(' / ',' ')
        item['structure']=item['marked'].replace('-------',item['opts'][0])
    if item['opts']==['engaging','engaged','engage','engagement']:
        item['opts']=['engaging','engages','engage','engagement']
        item['analyses'][1]='정형 동사 engages는 명사 speaker 앞 수식어가 될 수 없다.'
    if item['opts']==['on','with','by','of']:
        item['opts'][2]='from';item['analyses'][2]='날짜에 납기가 도래하는 관계는 on which이며 from은 시작 관계를 나타낸다.'
    if 'availably' in item['opts']:
        k=item['opts'].index('availably');item['opts'][k]='avail';item['analyses'][k]='동사 avail은 주어의 이용 가능 상태를 설명하는 형용사 보어가 아니다.'
    replacements={'to attended':('attendance','명사 attendance는 Employees 뒤에서 참석하는 행동을 수식하지 못한다.'),
                  'To checked':('Check','원형 Check만으로는 주절 앞의 분사구문을 만들지 못한다.'),
                  'to renovating':('renovation','명사 renovation은 rooms 뒤에서 보수된 관계를 수식하지 못한다.'),
                  'to needed':('needs','정형 동사 needs는 복수 Customers와 맞지 않고 주절 should call과도 연결되지 않는다.'),
                  'to ordering':('orders','orders는 이 자리에 필요한 과거분사 수식어가 아니다.'),
                  'To reviewed':('Review','원형 Review만으로 앞선 검토를 나타내는 분사구문을 만들지 못한다.'),
                  'to worked':('works','정형 동사 works는 복수 Employees와 맞지 않고 주절 need와도 연결되지 않는다.')}
    for bad,(good,reason) in replacements.items():
        if bad in item['opts']:
            k=item['opts'].index(bad);item['opts'][k]=good;item['analyses'][k]=reason
    if item['marked'].startswith('The documents ------- to this message') and 'to attach' in item['opts']:
        k=item['opts'].index('to attach');item['opts'][k]='attachment';item['analyses'][k]='명사 attachment는 뒤 전치사구와 함께 documents의 과거분사 수식어를 대신하지 못한다.'
    if item['opts'][0]=='provided that' and 'now that' in item['opts']:
        k=item['opts'].index('now that');item['opts'][k]='because of';item['analyses'][k]='because of는 뒤에 명사구를 취하며 the order exceeds라는 완전한 절을 직접 이끌지 못한다.'
    assert '{V}' in item['marked'],item['marked']
ALL=finalize()
