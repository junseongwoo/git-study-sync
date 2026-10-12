from pathlib import Path
import re,json,html
from collections import Counter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Table,TableStyle,Spacer,PageBreak,Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from questions import ALL,THINKING,CH,RULES

ROOT=Path(__file__).resolve().parents[3]
TMP=Path(__file__).resolve().parent
OUT=ROOT/'output/pdf/TOEIC_RC_Restart_Concepts_Practice_Explanations.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
for name,path in [('KR','malgun.ttf'),('KR-Bold','malgunbd.ttf'),('EN','arial.ttf'),('EN-Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+path))
for name in ['KR','EN']:pdfmetrics.registerFontFamily(name,normal=name,bold=name+'-Bold',italic=name,boldItalic=name+'-Bold')
NAVY=HexColor('#17334F');INK=HexColor('#242A31');GRAY=HexColor('#566475');LINE=HexColor('#C6D0DC');PALE=HexColor('#F3F6F9')
PW,PH=A4;M=19*mm;W=PW-2*M;TOP=26*mm;BOTTOM=23*mm;H=PH-TOP-BOTTOM

def st(name,font='KR',size=10.3,lead=15.3,**kw):
    return ParagraphStyle(name,fontName=font,fontSize=size,leading=lead,textColor=INK,wordWrap='CJK' if font.startswith('KR') else None,**kw)
S={'body':st('body'),'small':st('small',size=9.1,lead=13.1),'en':st('en','EN',11,15.1),
   'option':st('option','EN',10.7,14.4),'exp':st('exp',size=9.7,lead=14.1),
   'struct':st('struct','KR',9.7,14.1),'meta':st('meta','KR',9,13),
   'head':st('head','KR-Bold',12.5,18.3),'key':st('key','EN',10.5,14.5,alignment=TA_CENTER)}
S['title']=ParagraphStyle('title',fontName='KR-Bold',fontSize=22,leading=29,textColor=NAVY)
def p(t,s='body'):return Paragraph(t,S[s])
def g(h=8):return Spacer(1,h)
def title(t,sub=None,bookmark=None):
    head=p(t,'title')
    if bookmark:head.bookmark=bookmark;head.bookmark_title=t
    a=[head,g(8)]
    if sub:a += [p(sub,'small'),g(15)]
    return a
def box(items,pad=11,bg=None,border=True,width=W):
    t=Table([[items]],colWidths=[width],hAlign='LEFT');t.splitByRow=0
    rules=[('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('VALIGN',(0,0),(-1,-1),'TOP')]
    if border:rules += [('BOX',(0,0),(-1,-1),.6,LINE)]
    if bg:rules += [('BACKGROUND',(0,0),(-1,-1),bg)]
    t.setStyle(TableStyle(rules));return t
def h(items):return sum(x.wrap(W,H)[1] for x in items)
PAGES=[];CHSTART={};LOC={}
def page(section,items):
    used=h(items)
    if used>H+.1:raise ValueError(f'Overflow {section}: {used:.1f} > {H:.1f}')
    PAGES.append(dict(section=section,items=items,height=round(used,1)))
    return len(PAGES)
def heading(t):return [p(t,'head'),g(6)]

def conceptbox(c):
    return box([p(c['name'],'head'),g(6),p('<b>핵심 개념</b> &nbsp;'+c['body']),g(8),
        p(c['example'],'en'),g(4),p('<b>해석</b> &nbsp;'+c['translation'],'small'),g(7),
        p('<b>왜 중요한가?</b> &nbsp;'+c['why'],'small'),g(7),
        p('<b>시험장에서 이렇게 판단</b><br/>'+c['judge'],'small')])

def qblock(item):
    a=[p(f'<b>{item["n"]:02d}.</b> &nbsp; '+html.escape(item['stem']),'en'),g(7)]
    opts=[p(f'({chr(65+i)}) &nbsp; '+html.escape(v),'option') for i,v in enumerate(item['opts'])]
    if max(len(x) for x in item['opts'])<38:
        t=Table([opts[:2],opts[2:]],colWidths=[W/2]*2)
        t.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),2),('VALIGN',(0,0),(-1,-1),'TOP')]))
        a += [t]
    else:a += opts
    return box(a,pad=0,border=False)

TAGS={'S':'주어','V':'동사','O':'목적어','C':'보어','M':'수식어·연결 표현'}
TAKE={
 'N':['명사는 행동의 대상·내용을 나타낼 수 있다.','관사·형용사 뒤의 핵심 명사를 찾는다.','명사형 선택 후 뜻과 결합도 확인한다.'],
 'A':['형용사는 명사를 꾸미거나 상태를 설명한다.','주격 보어와 목적격 보어를 구별한다.','동사 뒤라고 항상 부사가 필요한 것은 아니다.'],
 'D':['부사는 동사·형용사·분사 등을 수식한다.','수식 대상을 먼저 정하고 형태를 고른다.','문장 뼈대가 완성되었는지 확인한다.'],
 'SG':['일반 현재의 단수 주어에는 단수 동사를 쓴다.','of구·관계절 안의 명사에 끌리지 않는다.','조동사 뒤 원형은 수일치와 별도로 판단한다.'],
 'PL':['복수 주어에는 맞는 복수 현재형을 쓴다.','주어의 수식어와 핵심어를 분리한다.','and와 or/nor의 연결 방식을 구별한다.'],
 'MOD':['조동사 뒤에는 동사원형이 온다.','단수 주어여도 뒤 원형에 -s를 붙이지 않는다.','수동 의미라면 be+p.p.까지 완성한다.'],
 'FIN':['절마다 정형 동사가 필요하다.','수식 분사를 본동사로 세지 않는다.','준동사만으로 주절 서술을 완성하지 못한다.'],
 'PASS':['주어가 행위를 받으면 수동태를 검토한다.','수동 동사구의 끝은 과거분사이다.','완료 been과 진행 being을 구별한다.'],
 'PP':['have/be 뒤 형태를 한 덩어리로 읽는다.','완료·수동의 과거분사를 확인한다.','과거분사와 단순과거의 역할을 구분한다.'],
 'PAST':['끝난 특정 과거 사건에는 과거형을 쓴다.','yesterday·last week의 기준점을 읽는다.','현재완료의 현재 연결 의미와 구별한다.'],
 'PERF':['현재완료는 과거와 현재를 연결한다.','since는 시작점, for는 기간이다.','지금도 활동 중이면 완료진행도 검토한다.'],
 'PASTPERF':['과거완료는 과거 기준점보다 앞선다.','두 과거 사건의 선후를 먼저 확인한다.','오래된 일이라는 이유만으로 had를 쓰지 않는다.'],
 'FUTPERF':['미래완료는 미래 기준점까지의 완료이다.','will have+p.p. 형태를 확인한다.','by the time절의 현재형도 미래일 수 있다.'],
 'TIME':['미래 시간 부사절은 현재형을 쓴다.','주절의 미래와 부사절 형태를 따로 본다.','같은 when이라도 명사절 용법과 구별한다.'],
 'GER':['전치사 뒤에는 동명사가 올 수 있다.','avoid/consider/finish의 결합을 기억한다.','전치사 to와 부정사 to를 구별한다.'],
 'INF':['to부정사는 to+동사원형이다.','앞 동사가 요구하는 목적어 형태를 확인한다.','목적 표현과 이미 한 행동의 기억을 구별한다.'],
 'BARE':['능동 let/make+목적어 뒤에는 원형이다.','allow/encourage의 to부정사 구조와 구별한다.','목적어가 실제 행동하는지 확인한다.'],
 'ED':['명사가 받는 행동에는 과거분사를 검토한다.','수식 분사와 주절 동사를 구분한다.','분사의 시간·능동·수동 관계를 확인한다.'],
 'ING':['명사가 하는 행동에는 현재분사를 검토한다.','분사구를 포함한 전체 주어를 찾는다.','본동사가 이미 있는지 확인한다.'],
 'EMO':['감정을 느끼는지 유발하는지 구분한다.','사람이라고 무조건 -ed가 아니다.','interested in·satisfied with의 전치사도 기억한다.'],
 'HAVING':['분사구문의 행위자는 기본적으로 주절 주어이다.','Having+p.p.는 앞선 완료를 나타낸다.','주어가 하는가 받는가로 태를 정한다.'],
 'WHO':['who는 사람 관계절의 주어가 될 수 있다.','선행사뿐 아니라 절의 빈 역할을 본다.','whose+명사 구조와 구별한다.'],
 'WHICH':['which는 사물의 주어·목적어 역할을 한다.','쉼표 관계절과 전치사 뒤에는 that을 쓰지 않는다.','장소 명사라도 목적어 역할이면 which가 가능하다.'],
 'WHOSE':['whose+명사는 소유 관계를 만든다.','뒤 명사와 선행사를 소유 관계로 연결한다.','사물 선행사에도 whose를 쓸 수 있다.'],
 'WHOM':['전치사 바로 뒤 사람 목적격은 whom이다.','전치사와 관계사를 한 덩어리로 본다.','who·whose의 다른 역할과 구별한다.'],
 'WHERE':['where는 장소 관계를 보충한다.','뒤 절에 필요한 목적어가 이미 있는지 본다.','장소 명사라는 이유만으로 답을 고르지 않는다.'],
 'WHEN':['when은 시간 선행사의 관계절을 이끈다.','뒤 절의 핵심 구조가 갖추어져 있는지 본다.','날짜의 on which 같은 표현으로 확인한다.'],
 'WHY':['reason 뒤에는 이유 관계를 확인한다.','why가 절의 주어·목적어를 대신하지는 않는다.','뒤 절의 기본 구조가 갖추어져 있는지 본다.'],
 'CONJ':['접속사는 뒤 절의 구조를 확인한다.','이유·양보·조건·시간의 방향을 읽는다.','접속부사와 전치사의 연결 방식은 다르다.'],
 'PREP':['전치사는 명사 역할의 덩어리를 취한다.','앞 단어와의 결합·시간 단위를 확인한다.','완료 기한 by와 지속 until을 구별한다.'],
 'OBJ':['동사·전치사 목적어에는 목적격을 쓴다.','주어와 다른 사람인지 확인한다.','소유격은 뒤 명사가 필요한 별도 형태이다.'],
 'POSS':['소유격은 뒤 명사를 꾸민다.','소유대명사는 명사를 포함하여 대신한다.','지칭 대상의 인칭과 수를 맞춘다.'],
 'POSSPRO':['소유대명사는 소유격+명사를 대신한다.','뒤에 명사가 없는지 먼저 확인한다.','비교 대상의 명사 범주를 맞춘다.'],
 'SELF':['주어와 같은 대상 또는 직접 수행의 강조이다.','목적어가 이미 있는지 확인한다.','주어의 인칭·수에 맞는 재귀형을 쓴다.'],
 'OTHER':['단수·복수와 뒤 명사 유무를 본다.','another는 다른 하나, others는 다른 여럿이다.','정해진 나머지에는 the를 확인한다.'],
 'COMP':['than과 두 대상의 차이를 확인한다.','비교급 형태와 수식 품사를 맞춘다.','같은 범주의 대상을 비교한다.'],
 'SUPER':['비교 범위 안의 최고·최저를 나타낸다.','the와 of/in 범위를 함께 확인한다.','비교급과 최상급을 혼동하지 않는다.'],
 'AS':['as ... as 사이에는 원급이 온다.','동사 수식이면 부사 원급을 쓴다.','동등 비교를 더 크거나 작다는 뜻으로 읽지 않는다.'],
 'EMPH':['much/far/even 등은 비교급을 강조한다.','very를 비교급 앞에 기계적으로 넣지 않는다.','강조어와 비교 형태를 함께 확인한다.'],
 'IFPAST':['현재 반대 가정에는 과거형을 쓴다.','결과절 would+원형과 짝을 맞춘다.','과거형이 반드시 과거 시간을 뜻하지 않는다.'],
 'IFPERF':['과거 반대 가정의 if절은 had+p.p.이다.','실제 과거 사실을 먼저 파악한다.','결과절 would have+p.p.와 연결한다.'],
 'IFRESULT':['과거 가정 결과는 would have+p.p.이다.','if절과 결과절의 역할을 구분한다.','단순 미래 예측과 구별한다.'],
 'INV':['if 생략 시 had/should 등이 주어 앞으로 온다.','일반 if절 어순으로 복원해 본다.','조동사 뒤 본동사의 형태를 확인한다.'],
 'MAND':['요구·권고 that절은 원형을 쓴다.','수동이면 be+p.p.가 된다.','수일치 규칙만으로 are/is를 고르지 않는다.'],
 'UNC':['해당 뜻이 불가산이면 -s와 a/an을 피한다.','개수를 셀 때 piece 같은 단위를 쓴다.','명사 뜻에 따라 가산성이 달라질 수 있다.'],
 'ART':['가산 단수의 한정사를 확인한다.','a/an은 철자보다 발음이 기준이다.','이미 특정된 대상이면 the를 검토한다.'],
 'QUANT':['가산 복수와 불가산 수량 표현을 구별한다.','many/few와 much/little을 맞춘다.','a few와 few의 의미 방향도 확인한다.'],
 'VOC':['단어를 목적어·전치사와 묶어 기억한다.','같은 품사라면 문맥으로 후보를 좁힌다.','연기·취소·교체처럼 실제 행동을 구별한다.'],
 'LOGIC':['앞뒤 주장을 짧게 요약한다.','대조·결과·지시 불이행 결과를 구별한다.','연결 표현의 뜻과 문장부호를 함께 본다.']}
def struct(item):
    t=html.escape(item['structure'].rstrip('.'))
    for code,name in TAGS.items():t=t.replace('{'+code+'}',f' <font color="#536171">[{code}]</font>')
    return t.replace(' / ',' / ')

def expbox(item,thinking=False):
    a=[p(f'<b>{item["n"]:02d}. 정답: ({item["answer"]}) {html.escape(item["correct"])}</b>','exp'),g(6),
       p('<b>문장 구조</b> &nbsp; '+struct(item),'struct'),g(6),
       p('<b>풀이</b> &nbsp; ① 빈칸의 역할을 '+item['need']+' 기준으로 확인한다. ② '+item['why'],'exp'),g(5),p('<b>오답</b>','exp')]
    for i,why in enumerate(item['analyses']):
        a.append(p(f'<b>({chr(65+i)}) {html.escape(item["opts"][i])}</b>: {why}','exp'))
    a += [g(5),p('<b>핵심 문법</b> &nbsp;'+item['core'],'exp'),g(4),
          p('<b>시험장에서는</b> &nbsp;'+item['exam'],'exp'),g(5),
          p('<b>이 문제에서 가져가야 할 것</b>','exp'),
          *[p(f'{i}. '+x,'exp') for i,x in enumerate(TAKE[item['kind']],1)]]
    if thinking:
        before,after=item['stem'].split('-------')
        cue=' '.join(before.split()[-4:])+' ------- '+' '.join(after.split()[:5])
        a += [g(6),p('<b>7단계 적용 기록</b>','exp'),
              p('Step 1. 주변: '+html.escape(cue),'exp'),
              p('Step 2. 구조: 위 S/V/O/C/M 표시에서 빈칸의 역할을 찾는다.','exp'),
              p('Step 3. 필요한 기준: '+item['need']+'이다.','exp'),
              p('Step 4. '+('어휘·문맥을 비교한다.' if item['kind'] in ['VOC','LOGIC'] else '문법 구조로 가능한 형태를 좁힌다.'),'exp'),
              p('Step 5. 위 오답 분석의 세 후보를 각각 제거한다.','exp'),
              p('Step 6. 문맥 확인: '+item['why'],'exp'),
              p(f'Step 7. ({item["answer"]}) {html.escape(item["correct"])}로 결정한다.','exp')]
    return box(a,pad=10)

def qpages(ch,items,review=False):
    chunks=[items[i:i+(5 if review else 4)] for i in range(0,len(items),5 if review else 4)]
    for j,chunk in enumerate(chunks):
        label='Review Test' if review else 'Application Practice'
        a=title(f'Chapter {ch:02d} | {label}',f'Questions {chunk[0]["n"]:02d}-{chunk[-1]["n"]:02d} &nbsp; | &nbsp; 답을 고른 근거를 여백에 적어 보세요.')
        last=None
        for item in chunk:
            if not review and item['level']!=last:
                a += [p(f'Level {item["level"]}','meta'),g(6)];last=item['level']
            a += [qblock(item),g(24 if not review else 18)]
        pg=page(f'CH {ch:02d} | '+label,a)
        for item in chunk:LOC[item['id']]=dict(question_page=pg)

def keyrow(items):
    cells=[p(f'{x["n"]:02d} ({x["answer"]})','key') for x in items]
    t=Table([cells],colWidths=[W/len(cells)]*len(cells));t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('GRID',(0,0),(-1,-1),.4,LINE),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));return t

def explanations(ch,items,review=False,thinking=False):
    label='Review Answers' if review else 'Practice Answers'
    if thinking:label='Thinking Lab Answers'
    batch=[];first=True
    def head(first,n1,n2):
        t=f'Chapter {ch:02d} | {label}' if ch<=18 else label
        a=title(t,f'Questions {n1:02d}-{n2:02d} | 문장 성분: S 주어 · V 동사 · O 목적어 · C 보어 · M 수식어/연결 표현')
        if first:a += [keyrow(items),g(12)]
        return a
    def flush():
        nonlocal first
        if not batch:return
        a=head(first,batch[0][0]['n'],batch[-1][0]['n'])
        for item,b in batch:a += [b,g(12)]
        pg=page(f'CH {ch:02d} | '+label,a)
        for item,_ in batch:LOC.setdefault(item['id'],{})['explanation_page']=pg
        first=False
    for item in items:
        b=expbox(item,thinking)
        candidate=head(first,batch[0][0]['n'] if batch else item['n'],item['n'])
        for _,old in batch:candidate += [old,g(12)]
        candidate += [b,g(12)]
        if h(candidate)>H:
            flush();batch=[]
        if h(head(first,item['n'],item['n'])+[b,g(12)])>H:raise ValueError('Explanation too tall: '+item['id'])
        batch.append((item,b))
    flush()

def bullet(items,s='body'):return [p('• '+x,s) for x in items]

cover=[g(30),p('TOEIC RC','title'),g(11),Paragraph('다시 시작하기',ParagraphStyle('cover',fontName='KR-Bold',fontSize=35,leading=45,textColor=NAVY)),g(13),
       p('개념 → 예문 → 문제 적용 → 상세 해설 → 복습','head'),g(29),
       box([p('<b>총점 700점대 경험자를 위한 RC 복구 과정</b>'),g(9),p('18개 문법 Chapter · 단계별 적용 144문항 · 누적 복습 180문항', 'small'),g(5),p('PART 5 사고법 훈련 8문항 · 독해 연결 18개 · Chapter별 My Notes','small')],pad=17,bg=PALE),
       g(37),p('이름: _______________________ &nbsp; 시작일: _______________________'),g(17),
       p('문법을 떠올리는 데서 끝내지 않고, 답을 판단한 이유를 설명하는 교재입니다.'),g(35),
       p('A4 인쇄용 | 독립 제작 영어 예문·문제 / 한국어 개념·해설','small'),g(7),
       p('ETS 공식 교재가 아닙니다. 기존 기출문제를 복사하거나 변형하지 않았습니다.','small')]
page('Cover',cover)

a=title('Study Guide','기억이 돌아오는 속도에 맞춰, 설명할 수 있는 단위로 공부하세요.')
a += heading('이 교재의 출발점')+[p('과거 총점 700점대의 학습 경험이 있어도 지금의 문법 회상 속도는 다를 수 있습니다. RC는 단독으로 5~495점이므로 요청문의 700→800 목표는 총점 기준으로 정리했습니다. 이 교재의 정답률은 복습 진단용이며 공인 점수로 환산하지 않습니다.'),g(13)]
a += heading('한 Chapter를 공부하는 순서')+bullet(['개념·예문: 문장 성분을 펜으로 표시하며 읽습니다. 판단 순서를 자기 말로 바꾸어 봅니다.','적용 8문항: Level 1(1-3번), Level 2(4-6번), Level 3(7-8번) 순서로 풉니다. 처음에는 시간을 재지 않습니다.','해설·정리: 정답뿐 아니라 오답이 왜 안 되는지 확인합니다. 맞혔어도 근거가 없으면 복습 대상으로 남깁니다.','Review 10문항: 현재 단원과 앞 단원 내용을 섞었습니다. 문제 페이지에는 유형·난이도 힌트를 넣지 않았습니다.','독해·My Notes: 문법을 실제 문장에 적용하고, 잘못 알고 있던 규칙과 예외를 직접 적습니다.'])+[g(13)]
a += heading('권장 학습량과 다시 보기')+[p('한 Chapter를 2~3회로 나누세요. 첫 회는 개념과 적용, 둘째 회는 해설과 Summary, 셋째 회는 Review와 독해를 권합니다. 다음 날, 3일 뒤, 7일 뒤에 틀린 문제의 답을 가리고 다시 설명해 봅니다. 전 단원 정답을 외우기보다 같은 구조의 새로운 문장을 읽을 수 있는지가 목표입니다.'),g(13)]
a += heading('표시와 인쇄')+[p('★ 반드시 알아야 함 · ★★ 자주 출제됨 · ★★★ 700점대에서 자주 틀리는 판단. 이 표시는 개념 페이지에만 사용합니다. 문제 페이지에서는 문법 유형을 숨깁니다. A4 세로, 실제 크기 100%로 인쇄하세요. 모든 본문·표·쪽번호는 15mm 안전 영역 안에 배치합니다.','small'),g(8),
 p('시험 점수 체계 참고: <link href="https://www.eu.ets.org/toeic/about/listening-reading.html" color="#17334F">ETS TOEIC Listening and Reading Test</link>. 학습 순서, 문제, 해설과 학습 시간 제안은 독립 제작 내용입니다.','small')]
page('Study Guide',a)
toc_slots=[]
for _ in range(2):toc_slots.append(len(PAGES));page('Contents',[g(1)])

VOCAB=[
 ('address','주소(n.) / 문제를 다루다(v.) / 청중에게 연설하다(v.)','mailing address / address an issue / address the audience','The director will address the audience after the team addresses the technical issue.','팀이 기술 문제를 다룬 뒤 책임자가 청중에게 연설할 것이다.','목적어가 issue인지 audience인지, 명사 자리인지 먼저 확인한다.'),
 ('issue','사안·문제(n.) / 발급·발행하다(v.)','raise an issue / issue a refund / issue a permit','Reception can issue a temporary pass while your new card is being prepared.','새 카드가 준비되는 동안 접수처에서 임시 출입증을 발급할 수 있다.','목적어가 pass/refund이면 발급·처리의 동사 뜻을 검토한다.'),
 ('charge','요금(n.) / 비용을 청구하다(v.) / 책임(n.)','delivery charge / charge a fee / in charge of','There is no delivery charge, but the store charges a fee for installation.','배송료는 없지만 매장은 설치 비용을 청구한다.','무료 항목과 유료 항목을 목적어 단위로 분리한다.'),
 ('meet','만나다 / 기준·기한을 충족하다','meet a client / meet requirements / meet a deadline','Suppliers must meet all safety requirements before delivery.','공급업체는 배송 전에 모든 안전 요건을 충족해야 한다.','사람이 아닌 requirements가 목적어이면 충족하다이다.'),
 ('place','장소(n.) / 놓다·주문하다(v.)','place an order / take place / in place','Orders placed before noon will be dispatched the same day.','정오 전에 접수된 주문은 당일 발송된다.','place an order와 행사가 열리다는 take place를 구별한다.'),
 ('raise / rise','raise: ~을 올리다·모으다 / rise: 오르다','raise prices / raise funds / prices rise','The store raised its prices after transport costs rose.','운송비가 오른 뒤 매장이 가격을 인상했다.','직접 목적어가 있으면 raise, 수치 자체가 오르면 rise를 본다.'),
 ('accommodate','수용하다 / 요구·일정에 맞추다','accommodate guests / accommodate a request','The larger room can accommodate all sixty participants.','더 큰 방은 참가자 60명을 모두 수용할 수 있다.','accompany(동행)·accomplish(완수)와 철자만으로 혼동하지 않는다.'),
 ('confirm','확인하다 / 확정하다','confirm a booking / confirm receipt / confirmation e-mail','Please confirm receipt of the revised contract by tomorrow.','내일까지 수정 계약서를 받았는지 확인해 주세요.','receipt가 영수증뿐 아니라 수령이라는 뜻도 된다는 점을 확인한다.'),
 ('renew','갱신하다 / 연장하다','renew a subscription / renew a license','You can renew your subscription online before it expires.','구독이 만료되기 전에 온라인으로 갱신할 수 있다.','처음 등록과 기존 계약 갱신을 구분한다.'),
 ('postpone','나중으로 미루다 / 연기하다','postpone a meeting / postpone until Friday','The meeting has been postponed until Friday, and the location is unchanged.','회의는 금요일로 연기되었고 장소는 그대로이다.','연기를 취소로 읽지 말고 바뀐 날짜와 유지된 장소를 분리한다.')]

for c in CH:
    n=c['n'];CHSTART[n]=len(PAGES)+1
    part='PART 1 | 문장 구조 복구' if n<=3 else 'PART 2 | TOEIC 필수 문법'
    a=title(f'Chapter {n:02d}. {c["title"]}',part,bookmark=f'ch{n:02d}')
    a += heading('오늘 배울 것')+bullet(c['goals'],'small')+[g(13),conceptbox(c['concepts'][0]),g(13),conceptbox(c['concepts'][1])]
    # Preserve each concept and its English/Korean example as a complete block.
    if h(a)>H:
        a=a[:-2];page(f'CH {n:02d} | Concepts',a)
        a=title(f'Chapter {n:02d} | 핵심 개념','개념과 예문을 같은 덩어리로 읽어 보세요.')+[conceptbox(c['concepts'][1]),g(13),conceptbox(c['concepts'][2])]
        page(f'CH {n:02d} | Concepts',a)
        a=title(f'Chapter {n:02d} | 구별과 암기')
    else:
        page(f'CH {n:02d} | Concepts',a)
        a=title(f'Chapter {n:02d} | 핵심 개념과 구별')+[conceptbox(c['concepts'][2]),g(13)]
    a += heading('자주 헷갈리는 것')
    for label,body in c['confusions']:a += [p('<b>'+label+'</b>','small'),p(body,'small'),g(8)]
    a += [g(3),box([p('MUST KNOW','head'),g(6)]+bullet(c['must'],'small'),bg=PALE)]
    page(f'CH {n:02d} | Concepts',a)
    if n==18:
        for vocab_group in [VOCAB[:3],VOCAB[3:6],VOCAB[6:8],VOCAB[8:]]:
            a=title('Vocabulary in Use','단어 → 주요 의미 → 콜로케이션 → 실제 문장')
            for word,meaning,coll,ex,tr,cue in vocab_group:
                a += [box([p(word,'head'),g(4),p('<b>주요 의미</b> '+meaning,'small'),g(5),p(coll,'en'),g(6),p(ex,'en'),p(tr,'small'),g(5),p('<b>시험장에서는</b> '+cue,'small')]),g(13)]
            page('Vocabulary in Use',a)
    qpages(n,c['practice']);explanations(n,c['practice'])
    a=title(f'Chapter {n:02d} | Summary',c['title'])
    for label,items in [('반드시 기억할 것',c['summary']),('자주 틀리는 것',c['pitfalls']),('시험장에서 확인할 것',c['checks'])]:
        a += heading(label)+bullet(items,'small')+[g(11)]
    a += heading('필수 표현')
    rows=[]
    for i in range(0,10,2):rows.append([p(c['expressions'][i],'small'),p(c['expressions'][i+1],'small')])
    t=Table(rows,colWidths=[W/2]*2);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    a += [t];page(f'CH {n:02d} | Summary',a)
    qpages(n,c['review'],True);explanations(n,c['review'],True)
    label,text,asks,answers=c['reading']
    a=title(f'Chapter {n:02d} | Reading Bridge','문법을 PART 6/7 읽기의 도구로 사용해 보세요.')
    a += [box([p(label,'meta'),g(8),p(text,'en')]),g(14)]+heading('직접 확인하기')
    for i,ask in enumerate(asks,1):a += [p(f'{i}. {ask}','small'),g(12)]
    a += [g(3)]+heading('근거와 구조 확인')
    for i,answer in enumerate(answers,1):a += [p(f'<b>{i}.</b> '+answer,'small'),g(8)]
    a += [g(5),p('독해에 연결: 주어·동사로 주장부터 잡고, 날짜·조건·예외를 수식어와 연결해 읽습니다.','small')]
    page(f'CH {n:02d} | Reading Bridge',a)
    a=title(f'Chapter {n:02d} | My Notes','틀린 답보다, 잘못 세운 규칙을 기록하세요.')
    a += [p('내가 잘못 알고 있던 규칙: __________________________________________________','small'),g(15),p('고쳐 쓴 판단 기준과 나만의 예문','head'),g(10)]
    for _ in range(13):
        t=Table([['']],colWidths=[W],rowHeights=[26]);t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),.4,LINE)]));a.append(t)
    a += [g(20),p('복습할 번호: ___________________ &nbsp; 다시 볼 날: ___________________','small'),g(12),p('1일 뒤 □ &nbsp; 3일 뒤 □ &nbsp; 7일 뒤 □ &nbsp; 근거를 설명할 수 있음 □','small')]
    page(f'CH {n:02d} | My Notes',a)

THINKSTART=len(PAGES)+1
a=title('PART 5 Thinking Lab','필수 문법을 문제 판단 과정으로 바꾸기',bookmark='thinking')
steps=[('Step 1. 빈칸 앞뒤를 본다','조동사, 관사, 전치사, than, 뒤 명사처럼 구조를 결정하는 표시를 먼저 봅니다. 앞뒤만으로 부족하면 문장 전체를 읽습니다.'),
       ('Step 2. 문장 구조를 파악한다','주어의 핵심어와 본동사를 찾습니다. 수식어를 괄호로 묶고 동사가 이미 있는지 확인합니다.'),
       ('Step 3. 빈칸의 품사·형태를 판단한다','명사 자리인지 상태 보어인지, 동사구의 어느 부분인지 정합니다. 관계사·접속사라면 절의 역할을 봅니다.'),
       ('Step 4. 문법 문제인지 어휘 문제인지 정한다','보기들이 같은 단어의 품사 변형이면 구조부터, 모두 같은 품사면 뜻·목적어·콜로케이션까지 읽습니다.'),
       ('Step 5. 선택지를 제거한다','수·태·동사 형태·결합이 맞지 않는 이유를 말하며 지웁니다. 처음 보는 단어라는 이유만으로 제거하지 않습니다.'),
       ('Step 6. 문맥을 확인한다','날짜·긍정과 부정·조건·원인과 결과가 맞는지 확인합니다. 문법적으로 가능하다는 것과 문맥 정답은 다릅니다.'),
       ('Step 7. 답을 결정한다','남은 답을 넣어 문장을 한 번 읽습니다. 새 근거 없이 계속 되돌아가지 않습니다. 초기에는 무제한으로, 익숙해진 구조 문제는 10~20초를 목표로 연습합니다.')]
for head,body in steps:a += [p(head,'head'),g(4),p(body,'small'),g(11)]
page('PART 5 Thinking Lab',a)

a=title('Worked Examples','7단계가 실제로 어떤 판단을 만드는지 확인하세요.')
a += [box([p('<b>Example A</b> The revised schedule is -------.','en'),g(6),p('(A) suitability  (B) suitable  (C) suitably  (D) suit','en'),g(9),
 p('1. is 뒤를 본다. 2. S(The revised schedule)+V(is)+C 구조이다. 3. 보어 형용사가 필요하다. 4. 품사 문제이다. 5. 명사 suitability, 부사 suitably, 동사 suit를 제거한다. 6. 일정이 적절하다는 의미가 맞다. 7. (B) suitable로 결정한다.','small'),g(8),p('가져갈 것: be 뒤 빈칸이 주어의 상태를 말하는지 확인한다. 동사 뒤라고 항상 부사가 아니다.','small')]),g(18),
 box([p('<b>Example B</b> The supplier will ------- the damaged chairs.','en'),g(6),p('(A) replace  (B) attend  (C) arise  (D) comply','en'),g(9),
 p('1. will 뒤와 chairs를 본다. 2. S+will V+O 구조이다. 3. 원형 동사가 필요하다. 4. 네 선택지 모두 원형이므로 어휘·결합 문제이다. 5. attend는 참석, arise는 자동사, comply는 with가 필요한 준수 표현이다. 6. 손상 의자를 교체한다는 문맥이 맞다. 7. (A) replace로 결정한다.','small'),g(8),p('가져갈 것: 형태가 모두 맞으면 목적어와 상황을 읽어야 답을 정할 수 있다.','small')]),g(18),
 p('이어서 8문항을 풀고, 각 문항에서 가장 먼저 확인한 단서를 여백에 적으세요. 해설에는 7단계 적용 기록을 따로 제공합니다.')]
page('PART 5 Thinking Lab',a)
qpages(19,THINKING);explanations(19,THINKING,thinking=True)

REVIEWSTART=len(PAGES)+1
a=title('Final Review System','틀린 답의 번호를 넘어, 판단 규칙을 점검하세요.',bookmark='finalreview')
a += heading('세 번의 복습에서 할 일')+bullet(['1일 뒤: 답을 가리고 같은 문제를 풉니다. 원래 선택했던 오답이 왜 틀리는지 말합니다.','3일 뒤: 예문의 명사·시점을 바꾸어 자신의 문장을 만듭니다. 바꾼 부분 때문에 수·시제·태가 달라지는지 확인합니다.','7일 뒤: Review 문제와 Reading Bridge를 다시 풉니다. 지문에서 핵심 S+V, 수식어, 조건·예외를 표시합니다.'],'small')+[g(15)]
a += heading('오답 원인 분류')+[p('문법 회상 / 품사 판단 / 주어·동사 찾기 / 수식 관계 / 시제 기준점 / 능동·수동 / 결합 어휘 / 문맥·부정 방향 / 문제 오독 / 시간 부족','small'),g(12),p('예: “4장 R01 - repairs를 주어로 보고 are를 선택함 → of구를 빼고 cost에 맞추기.” 답만 기록하지 말고 잘못 적용한 규칙과 다음 행동을 함께 적습니다.'),g(15)]
a += heading('완료 기준')+bullet(['정답을 골랐는가?','완성 문장에서 주어·동사와 빈칸의 역할을 표시할 수 있는가?','오답 세 개가 왜 안 되는지 설명할 수 있는가?','짧은 독해에서 같은 구조와 의미를 찾을 수 있는가?'],'small')+[g(20),p('다음 페이지에 학습 현황을 기록하고, 마지막 한 장 요약을 책상 옆에 두세요. 요약의 규칙이 떠오르지 않으면 해당 Chapter의 예문으로 돌아갑니다.')]
page('Final Review System',a)

a=title('Progress Tracker','모든 칸을 한 번에 채우기보다, 근거를 말할 수 있을 때 체크하세요.')
rows=[[p(x,'small') for x in ['CH','개념','적용  /8','Review /10','독해','1일·3일·7일']]]
for c in CH:rows.append([p(f'{c["n"]:02d}','small'),p('□','small'),p('___ / 8','small'),p('___ / 10','small'),p('□','small'),p('□  □  □','small')])
t=Table(rows,colWidths=[W*x for x in [.08,.12,.20,.23,.12,.25]],rowHeights=[29]+[27]*18)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.45,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)]))
a += [t,g(16),p('가장 다시 볼 Chapter: ________ &nbsp; 다음 학습일: __________________','small')]
page('Progress Tracker',a)

SUMMARYSTART=len(PAGES)+1
a=title('RC 필수 문법 한 장 요약','규칙이 모호하면 괄호의 Chapter로 돌아가 예문을 읽으세요.',bookmark='onesheet')
rows=[[p('<b>문법</b>','small'),p('<b>시험장에서 기억할 기준</b>','small')]]
summary=[('문장 구조 (01)','S/V/O/C/M 구분. 목적어=대상, 보어=상태·정체.'),('품사 (02)','명사 자리·형용사 보어·부사 수식 대상을 먼저 확인.'),('동사 찾기 (03)','조동사+원형, have+p.p., be+-ing/p.p.를 묶기.'),('수일치 (04)','핵심 주어에 일치. each/the number 단수, a number 복수.'),('시제 (05)','기준 시점 확인. 완료=기준점과 연결, 진행=활동 중.'),('수동태 (06)','주어가 받는 행위: be+p.p.; 완료 been / 진행 being.'),('준동사 (07)','전치사+-ing; plan to do; avoid doing; let O do.'),('분사 (08)','명사가 하는가(-ing), 받는가(p.p.); 감정의 방향 확인.'),('관계대명사 (09)','절의 빈 역할 찾기. whose+명사; 전치사+whom/which.'),('관계부사 (10)','핵심 구조가 갖추어진 절의 장소 where·시간 when·이유 why.'),('접속사 (11)','절 구조와 이유·양보·조건 확인. 접속부사는 문장부호 확인.'),('전치사 (12)','명사 역할을 취함. by 완료 기한 / until 지속 / within 기간.'),('대명사 (13)','격·수·지칭 맞추기. 소유격+명사 / 소유대명사 단독.'),('비교 (14)','as 원급 as / 비교급 than / 최상급+범위. 같은 대상 비교.'),('가정법 (15)','현재: if 과거, would 원형. 과거: if had p.p., would have p.p.'),('명사·관사 (16)','가산 단수 한정사. information/equipment 불가산. a/an 발음.'),('형용사·부사 (17)','보어는 형용사, 수식 대상 보고 부사. hard≠hardly.'),('어휘·문맥 (18)','목적어·전치사까지 결합. raise O / rise. 연기≠취소.')]
for label,body in summary:rows.append([p(label,'small'),p(body,'small')])
t=Table(rows,colWidths=[W*.26,W*.74]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.4,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
a += [t];page('One-page Grammar Summary',a)

# Fill the table of contents after all destinations have definite pages.
for k,slot in enumerate(toc_slots):
    a=title('Contents',f'학습 순서 {k+1} / 2 | 항목을 누르면 해당 Chapter로 이동합니다.')
    for c in CH[k*9:(k+1)*9]:
        n=c['n'];text=f'<link href="#ch{n:02d}" color="#17334F"><b>{n:02d}. {c["title"]}</b></link>'
        t=Table([[p(text),p(str(CHSTART[n]),'small')]],colWidths=[W-40,40]);t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),.4,LINE),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),11)]));a += [t]
    a += [g(18)]
    if k==0:a += [p('<b>PART 1</b> Chapter 01-03: 문장을 읽는 뼈대 복구<br/><b>PART 2</b> Chapter 04-18: 필수 문법과 결합 어휘','small'),g(12),p('각 Chapter: 개념 → 적용 8문항 → 해설 → Summary → Review 10문항 → 해설 → Reading Bridge → My Notes','small')]
    else:
        for label,dest,pg in [('PART 5 Thinking Lab','thinking',THINKSTART),('Final Review System','finalreview',REVIEWSTART),('RC 필수 문법 한 장 요약','onesheet',SUMMARYSTART)]:
            a += [p(f'<link href="#{dest}" color="#17334F">{label}</link> &nbsp; {pg}','small'),g(7)]
    assert h(a)<=H
    PAGES[slot]=dict(section='Contents',items=a,height=round(h(a),1))

class Book(BaseDocTemplate):
    def afterFlowable(self,f):
        if hasattr(f,'bookmark'):
            self.canv.bookmarkPage(f.bookmark)
            self.canv.addOutlineEntry(f.bookmark_title,f.bookmark,0,False)

def footer(c,doc):
    if doc.page==1:return
    c.saveState();c.setFillColor(GRAY);c.setFont('EN',8)
    c.drawString(M,PH-17.8*mm,'TOEIC RC RESTART | CONCEPTS & PRACTICE')
    c.drawRightString(PW-M,PH-17.8*mm,PAGES[doc.page-1]['section'])
    c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(M,PH-20*mm,PW-M,PH-20*mm)
    c.drawCentredString(PW/2,16*mm,f'{doc.page} / {len(PAGES)}');c.restoreState()

assert len(CH)==18 and len(ALL)==332
assert len({x['stem'] for x in ALL})==332
assert all(len(c['practice'])==8 and len(c['review'])==10 and len(c['concepts'])==3 and len(c['expressions'])==10 for c in CH)
book=Book(str(OUT),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=TOP,bottomMargin=BOTTOM,
          pageCompression=1,title='TOEIC RC 다시 시작하기 - 개념·문제·해설',author='Independent study material',allowSplitting=0)
book.addPageTemplates(PageTemplate('main',[Frame(M,BOTTOM,W,H,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer))
story=[]
for i,pg in enumerate(PAGES):
    if i:story.append(PageBreak())
    story += pg['items']
book.build(story)
manifest=[dict(page=i+1,section=x['section'],content_height=x['height']) for i,x in enumerate(PAGES)]
(TMP/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(TMP/'all_questions.json').write_text(json.dumps(ALL,ensure_ascii=False,indent=2),encoding='utf-8')
(TMP/'locations.json').write_text(json.dumps(LOC,ensure_ascii=False,indent=2),encoding='utf-8')
(TMP/'chapter_starts.json').write_text(json.dumps(CHSTART,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(output=str(OUT),pages=len(PAGES),questions=len(ALL),chapter_starts=CHSTART,sections=dict(Counter(x['section'].split(' | ')[-1] for x in PAGES))),ensure_ascii=False))
