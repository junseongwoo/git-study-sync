from pathlib import Path
import json, re, html
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from toeic_data import Q, P6, P7

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/TOEIC_RC_Practice_Set_01.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
SCRATCH = ROOT / 'tmp/pdfs'
pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('Malgun-Bold', 'C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Malgun', normal='Malgun', bold='Malgun-Bold', italic='Malgun', boldItalic='Malgun-Bold')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')

NAVY = HexColor('#17334F')
INK = HexColor('#20252B')
GRAY = HexColor('#536171')
LINE = HexColor('#CCD5DF')
PALE = HexColor('#F4F6F8')
PW, PH = A4
M = 19 * mm
W = PW - 2*M
TOP = PH - 24*mm
BOTTOM = 23*mm
H = TOP - BOTTOM

def sty(name, font='Malgun', size=10.3, lead=15.1, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead, textColor=INK,
                          spaceAfter=0, wordWrap='CJK' if font.startswith('Malgun') else None, **kw)
S = {
    'body': sty('body'),
    'small': sty('small', size=9, lead=13),
    'en': sty('en', 'Arial', 10.8, 14.7),
    'question': sty('question', 'Arial', 10.8, 14.8),
    'option': sty('option', 'Arial', 10.5, 14.2),
    'title': sty('title', 'Malgun-Bold', 23, 30, textColor=NAVY) if False else None,
    'meta': sty('meta', 'Arial', 9, 12),
    'exp': sty('exp', size=9.6, lead=13.8),
    'evidence': sty('evidence', 'Arial', 9.5, 13.2),
}
S['title'] = ParagraphStyle('title', fontName='Malgun-Bold', fontSize=22, leading=29, textColor=NAVY)
S['subtitle'] = sty('subtitle', 'Malgun-Bold', 12, 17)
S['key'] = sty('key', 'Arial', 11.5, 16, alignment=TA_CENTER)
S['white'] = ParagraphStyle('white', fontName='Arial-Bold', fontSize=10, leading=14, textColor=white)

def p(text, style='body'):
    return Paragraph(text, S[style])

def gap(h=8): return Spacer(1,h)

def title(name, subtitle=None):
    a=[p(name, 'title'), gap(9)]
    if subtitle: a += [p(subtitle, 'small'), gap(15)]
    return a

def section_head(part, name, time, nums):
    return title(f'{part} | {name}', f'Recommended time: {time} minutes &nbsp; | &nbsp; Questions {nums}')

def line_table(content, width=W, padding=10, bg=None, border=True):
    t=Table([[content]], colWidths=[width], hAlign='LEFT')
    rules=[('LEFTPADDING',(0,0),(-1,-1),padding),('RIGHTPADDING',(0,0),(-1,-1),padding),
           ('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding),
           ('VALIGN',(0,0),(-1,-1),'TOP')]
    if bg: rules.append(('BACKGROUND',(0,0),(-1,-1),bg))
    if border: rules.append(('BOX',(0,0),(-1,-1),0.6,LINE))
    t.setStyle(TableStyle(rules)); t.splitByRow=0
    return t

def question(q, layout='vertical'):
    a=[p(f'<b>{q["n"]}.</b> &nbsp; {q["stem"]}', 'question'), gap(5)]
    if layout == 'grid':
        cells=[p(f'({chr(65+i)}) &nbsp; {v}', 'option') for i,v in enumerate(q['opts'])]
        t=Table([cells[:2],cells[2:]], colWidths=[(W-12)/2]*2, hAlign='LEFT')
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
                               ('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),1),
                               ('BOTTOMPADDING',(0,0),(-1,-1),1)]))
        a.append(t)
    else:
        for i,v in enumerate(q['opts']):
            a.append(p(f'({chr(65+i)}) &nbsp; {v}', 'option'))
    return line_table(a, padding=0, border=False)

def docbox(d, width=W):
    a=[p(f'<b>{d["label"]}</b>', 'meta'), gap(4), p(d['meta'], 'meta'), gap(9)]
    for j,t in enumerate(d['paras']):
        a.append(p(t, 'en'))
        if j<len(d['paras'])-1: a.append(gap(7))
    return line_table(a, width=width, padding=12)

def expbox(q):
    level=['','★ Basic','★★ Intermediate','★★★ Advanced'][q['level']]
    flag=' &nbsp; | &nbsp; 700+ Trap' if q['level']==3 else ''
    a=[p(f'<b>{q["n"]}. 정답: ({q["answer"]})</b> &nbsp; | &nbsp; {level}{flag}', 'exp'),gap(4),
       p(f'<font color="#17334F">[{q["tag"]}]</font>', 'small'), gap(6),
       p(f'<b>핵심 포인트:</b> {q["point"]}', 'exp'),gap(4),
       p(f'<b>해설:</b> {q["explanation"]}', 'exp')]
    if q['evidence']:
        a += [gap(6)]
        for loc,txt in q['evidence']:
            a += [p(f'<b>Evidence | {html.escape(loc)}</b>', 'evidence'),
                  p('&quot;'+html.escape(txt)+'&quot;', 'evidence'),gap(3)]
    a += [gap(5),p('<b>오답 분석:</b>', 'exp')]
    for i,(opt,why) in enumerate(zip(q['opts'],q['analyses'])):
        label = chr(65+i)
        a.append(p(f'<b>({label})</b> {why}', 'exp'))
    a += [gap(5),p(f'<b>700점대 학습자 주의점:</b> {q["caution"]}', 'exp'),gap(4),
          p(f'<b>기억할 것:</b> {q["remember"]}', 'exp')]
    return line_table(a, padding=11)

pages=[]
def height_of(items):
    return sum(f.wrap(W,H)[1] for f in items)

def page(section,items,allow_sparse=False):
    used=height_of(items)
    if used>H+0.1: raise ValueError(f'Page too tall: {section}: {used:.1f} > {H:.1f}')
    pages.append(dict(section=section,items=items,height=round(used,1)))

# Cover: quiet typography and practical fields, with no page number.
cover=[gap(46),p('TOEIC RC', 'title'),gap(12)]
cover.append(Paragraph('PRACTICE BOOK',ParagraphStyle('coverbig',fontName='Arial-Bold',fontSize=34,leading=41,textColor=NAVY)))
cover += [gap(30),Paragraph('700 → 800',ParagraphStyle('covergoal',fontName='Malgun-Bold',fontSize=32,leading=43,textColor=NAVY)),
          gap(10),p('총점 700점대 학습자를 위한 RC 집중 훈련', 'subtitle'),gap(36),
          line_table([p('<b>Practice Set 01</b>', 'en'),gap(10),p('70 original questions', 'en'),gap(6),
                      p('PART 5 · 30 &nbsp; / &nbsp; PART 6 · 16 &nbsp; / &nbsp; PART 7 · 24', 'en'),gap(10),
                      p('권장 풀이 55분 + 정답 근거 중심 복습', 'body')],padding=16,bg=PALE),
          gap(48),p('이름: ________________________ &nbsp; 날짜: ________________________','body'),gap(20),
          p('A4 인쇄용 · 영어 문제 / 한국어 해설', 'small'),gap(8),
          p('독립 제작 학습 자료입니다. ETS의 공식 문제 또는 기출문제를 사용하지 않았습니다.', 'small')]
page('Cover',cover)

guide=title('Study Guide', '먼저 풀고, 근거를 설명하고, 같은 실수를 다시 확인하세요.')
guide += [p('<b>목표와 범위</b>','subtitle'),gap(6),
          p('이 교재는 TOEIC 총점 700점대에서 800점 이상을 목표로 하는 학습자의 RC 훈련용입니다. RC 단독 점수는 5~495점입니다. 실제 RC는 100문항·75분이며, 이 교재는 70문항의 집중 연습 세트이므로 공식 점수로 환산하지 않습니다.'),gap(12)]
timing=[[p('<b>구간</b>','small'),p('<b>문항</b>','small'),p('<b>권장 시간</b>','small'),p('<b>누적 경과</b>','small')],
        [p('PART 5','small'),p('1-30 / 30문항','small'),p('10분','small'),p('10분','small')],
        [p('PART 6','small'),p('31-46 / 16문항','small'),p('8분','small'),p('18분','small')],
        [p('PART 7','small'),p('47-70 / 24문항','small'),p('32분','small'),p('50분','small')],
        [p('검토','small'),p('미응답·답 표시 확인','small'),p('5분','small'),p('55분','small')]]
t=Table(timing,colWidths=[W*.20,W*.31,W*.23,W*.26]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.5,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
guide += [t,gap(13),p('<b>학습 순서</b>','subtitle'),gap(6),
          p('1. 55분 타이머를 켜고 해설을 보지 않은 채 풉니다. 답은 문제지에 표시하고, 확신이 없었던 번호에는 작은 동그라미를 남깁니다.'),gap(5),
          p('2. 채점 후 틀린 문제와 맞혔어도 설명할 수 없는 문제를 복습합니다. PART 7은 지문에서 근거를 먼저 찾아 밑줄을 긋습니다.'),gap(5),
          p('3. 오답 이유를 기록하고 1일·3일·7일 뒤 다시 풉니다. 답의 위치보다 정답 근거와 오답 배제 이유를 말할 수 있는지 확인합니다.'),gap(12),
          p('<b>구성 안내</b>','subtitle'),gap(6),
          p('PART 7은 단일 지문 2개 × 3문항, 이중 지문 2세트 × 3문항, 삼중 지문 2세트 × 4문항을 수록했습니다. 요청문의 총 24문항에 맞추기 위해 짧은 단일 지문 2개 × 2문항을 추가했습니다.'),gap(6),
          p('난이도는 Basic 14문항(20%), Intermediate 35문항(50%), Advanced 21문항(30%)입니다. 유형·난이도·700+ Trap 표시는 해설에서만 확인할 수 있습니다.'),gap(12),
          p('<b>인쇄 및 참고</b>','subtitle'),gap(6),
          p('A4 세로, 실제 크기(100%)로 인쇄합니다. 모든 본문과 쪽번호는 가장자리에서 15mm 이상 안쪽에 있습니다. 글자와 선은 벡터로 제작하여 인쇄 시 선명하게 유지됩니다.', 'small'),gap(5),
          p('시험 형식·점수 확인: <link href="https://www.eu.ets.org/toeic/about/listening-reading.html" color="#17334F">ETS: TOEIC Listening and Reading Test</link> (확인일: 2026-10-07). 문제·해설·시간 배분은 이 교재의 독자 제작 내용입니다.', 'small')]
page('Study Guide',guide)

# Practice pages: each question and every choice remain in one indivisible block.
for start in range(1,31,6):
    a=section_head('PART 5','Incomplete Sentences',10,'1-30') if start==1 else title('PART 5 | Incomplete Sentences',f'Questions {start}-{start+5}')
    for n in range(start,start+6): a += [question(Q[n-1], 'grid'),gap(18)]
    page('PART 5',a)

for i,s in enumerate(P6):
    a=section_head('PART 6','Text Completion',8,'31-46') if i==0 else title('PART 6 | Text Completion',f'Questions {s["nums"][0]}-{s["nums"][-1]}')
    a += [docbox(dict(label=s['title'],meta=s['meta'],paras=s['paras'])),gap(14)]
    for n in s['nums']:
        q=Q[n-1]; a += [question(q,'vertical' if n in [34,38,42,46] else 'grid'),gap(11)]
    page('PART 6',a)

for i,s in enumerate(P7):
    ns=s['nums']; sub=f'{s["kind"]} | Questions {ns[0]}-{ns[-1]}'
    a=section_head('PART 7','Reading Comprehension',32,'47-70') if i==0 else title('PART 7 | Reading Comprehension',sub)
    if i==0: a += [p(sub,'meta'),gap(9)]
    if s.get('split'):
        for d in s['docs'][:2]: a += [docbox(d),gap(13)]
        a += [p('The third document and Questions '+str(ns[0])+'-'+str(ns[-1])+' are on the next page.','meta')]
        page('PART 7',a)
        a=title('PART 7 | Reading Comprehension',sub+' | continued')
        a += [p('Use all three documents to answer the questions. The first two documents are on the previous page.','meta'),gap(9),docbox(s['docs'][2]),gap(13)]
    else:
        for d in s['docs']: a += [docbox(d),gap(12)]
    for n in ns: a += [question(Q[n-1]),gap(12)]
    page('PART 7',a)

key=title('Answer Key', '채점 후에는 맞혔지만 확신이 없었던 문제도 복습하세요.')
for label,lo,hi in [('PART 5',1,30),('PART 6',31,46),('PART 7',47,70)]:
    key += [p(label,'subtitle'),gap(7)]
    cells=[]
    for n in range(lo,hi+1): cells.append(p(f'<b>{n}</b> &nbsp; ({Q[n-1]["answer"]})','key'))
    while len(cells)%6: cells.append('')
    t=Table([cells[j:j+6] for j in range(0,len(cells),6)],colWidths=[W/6]*6)
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,LINE),('BACKGROUND',(0,0),(-1,-1),white),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    key += [t,gap(17)]
key += [p('<b>채점 기록</b>','subtitle'),gap(7),p('PART 5: ____ / 30 &nbsp; PART 6: ____ / 16 &nbsp; PART 7: ____ / 24'),gap(8),
        p('합계: ____ / 70 &nbsp; 풀이 시간: ____분 &nbsp; 확신 없이 맞힌 문제: ____개'),gap(9),
        p('원점수는 이 세트 안에서의 진단용입니다. TOEIC 공인 점수 또는 예상 점수로 변환하지 않습니다.','small')]
page('Answer Key',key)

# Pack complete explanation boxes, measuring before adding a page break.
for label,lo,hi in [('PART 5',1,30),('PART 6',31,46),('PART 7',47,70)]:
    batch=[]
    def flush():
        if not batch: return
        a=title('Detailed Explanations',f'{label} | Questions {batch[0][0]}-{batch[-1][0]}')
        for n,b in batch: a += [b,gap(12)]
        page('Explanations - '+label,a)
    for n in range(lo,hi+1):
        b=expbox(Q[n-1])
        test=title('Detailed Explanations',f'{label} | Questions {n}-{n}')
        for _,old in batch: test += [old,gap(12)]
        test += [b,gap(12)]
        if height_of(test)>H:
            flush();batch=[]
        batch.append((n,b))
    flush()

def strategy_block(heading,body):
    return [p(heading,'subtitle'),gap(6),p(body),gap(16)]

a=title('700 → 800 RC Strategy','01 | PART 5와 PART 6에서 읽을 곳을 정확히 고르기')
a += strategy_block('PART 5 시간 단축 방법','먼저 빈칸 주변에서 필요한 품사를 확인하고, 주어·동사·목적어를 찾습니다. 구조만으로 풀리는 문제는 짧게 끝내고, 어휘·접속사 문제는 문장 끝까지 읽습니다. 목표는 무조건 빨리 읽기가 아니라 구조 문제에 문장 전체 번역을 반복하지 않는 것입니다. 예를 들어 1번은 was posted가 완성되었으므로 부사 자리를 먼저 확인합니다.')
a += strategy_block('PART 5에서 일단 넘길 문제','보기 두 개 사이에서 근거 없이 고민하며 30~40초를 쓰고 있다면 임시 답을 표시하고 넘깁니다. 특히 모르는 어휘 네 개를 계속 읽는 일은 효율이 낮습니다. 문법 문제라면 주어·태·목적어를 한 번 더 확인한 뒤 결정합니다. 넘긴 문항은 복습 때 뜻과 결합을 학습하며, 시험 중에는 정해 둔 총시간을 지킵니다.')
a += strategy_block('PART 6 읽는 순서','문서 종류와 작성 목적을 확인한 뒤 첫 문장부터 순서대로 읽습니다. 형태 문제는 해당 문장에서 판단하되 시제·대명사·연결어는 앞뒤 문장을 함께 봅니다. 문장 삽입은 앞 문장의 화제와 뒤 문장의 This, these, 절차·결과를 동시에 연결합니다. 42번처럼 실습 → 준비 기기 → 대여 기기라는 흐름을 잡으면 단어만 반복하는 오답을 피할 수 있습니다.')
a += strategy_block('시간 배분은 개인 기록으로 조정','이 70문항 세트의 10분·8분·32분·검토 5분은 훈련용 시작 기준입니다. 공식 100문항 RC의 75분을 연습할 때는 예를 들어 PART 5 10분, PART 6 8분, PART 7 및 최종 확인 57분으로 시작해 보세요. 특정 PART에서 시간을 넘긴 이유를 적고, 근거가 분명한 문제의 풀이 시간을 먼저 줄입니다. 어려운 독해를 무조건 빠르게 읽어 해결하려 하지 않습니다.')
page('RC Strategy',a)

a=title('700 → 800 RC Strategy','02 | PART 7의 질문과 지문을 왕복하는 방법')
a += strategy_block('PART 7 지문 읽는 방법','제목·발신자·수신자·날짜로 상황을 잡고, 각 문단이 하는 일을 한 줄로 생각합니다. 첫 문단은 목적, 중간은 조건·변경·예외, 마지막은 요청이나 다음 행동인 경우가 많습니다. 모든 문장을 번역해 외우기보다, 필요한 정보를 다시 찾을 수 있게 위치를 기억합니다. 질문의 답을 찾으면 선택지의 동의 표현이 원문 의미를 유지하는지 확인합니다.')
a += strategy_block('문제 먼저 읽는 경우','이름·날짜·금액·장소처럼 찾을 대상이 분명한 세부 문제는 질문을 먼저 읽으면 탐색 기준을 잡기 쉽습니다. 보기 네 개까지 전부 외우려 하지 말고 무엇을 찾아야 하는지만 정합니다. NOT 문제는 보기의 핵심어도 간단히 확인하고 각 항목의 근거를 찾습니다. 근거를 발견한 문장만 읽고 조건이나 예외가 담긴 다음 문장을 건너뛰지 않습니다.')
a += strategy_block('지문 먼저 읽는 경우','목적, 문맥상 발언 의미, 문장 위치, 글 전체 추론은 흐름을 먼저 잡는 편이 유리합니다. 특히 짧은 공지나 채팅은 처음부터 한 번 읽어 누가 무엇을 요청하고 어떻게 응답했는지 파악합니다. 51번의 breathing room은 직전의 제출 기한 안내가 있어야 시간적 여유로 해석할 수 있습니다. 익숙한 단어의 문자 뜻만 대입하지 않습니다.')
a += strategy_block('Double / Triple Passage 접근법','각 문서의 역할을 구분합니다. 예: 카탈로그는 규정·단가, 고객 메일은 수량·기한·예산, 확인서는 실제 재고·배송 방식입니다. 같은 인물·주문 번호·행사 이름을 연결하고, 기본 규정과 개별 변경을 구분합니다. 날짜는 지원일·회신일·참석일처럼 사건 이름을 붙여 적습니다. 세 문서를 합치는 질문은 한 문서의 문장 하나만으로 답을 확정하지 않습니다.')
page('RC Strategy',a)

a=title('700 → 800 RC Strategy','03 | 함정을 줄이고 마지막 시간을 회수하기')
a += strategy_block('NOT 문제 처리법','네 선택지마다 지문 근거를 확인해 세 개를 지웁니다. 직접 언급, 동의 표현, 조건을 충족한 정보가 모두 근거가 될 수 있습니다. 현실에서 그럴듯한 정보는 지문 근거가 아닙니다. 질문이 NOT mentioned인지 NOT included인지 구분하고, 무료·추가 요금처럼 범주가 다른 정보를 섞지 않습니다.')
a += strategy_block('추론 문제 접근법','반드시 참이라고 볼 수 있는 최소 결론을 고릅니다. 인물이 초안을 수정한다고 해서 인쇄소를 운영한다고 확대하지 않습니다. 가능 날짜를 밝혔다고 면접이 확정된 것도 아닙니다. 조건과 다음 행동이 제시되면 그 조건이 발생했는지 확인한 후 행동을 고릅니다. 상식이나 경험보다 명시된 제약을 우선합니다.')
a += strategy_block('동의어 문제 접근법','해당 문장의 앞뒤를 읽고 선택지를 실제 자리에 대입합니다. 품사, 긍정·부정 방향, 행동의 강도와 대상이 유지되는지 봅니다. 사전의 첫 뜻이 아니라 문맥의 뜻을 고릅니다. 69번의 prorated는 뒤에 남은 날짜 수라는 기준이 있으므로 기간에 비례한 조정으로 이해합니다.')
a += strategy_block('시간 부족 시 우선순위','이름·수치 등 근거 위치를 빨리 찾을 수 있는 세부 문제부터 해결합니다. 모르는 단어 하나에 오래 머무르지 않습니다. 다중 지문이 항상 더 어렵다고 가정하지 말고 정보 위치와 이미 읽은 범위를 기준으로 판단합니다. 긴 계산이나 문장 위치 문제에 막히면 임시 답을 남기고 다음 문제의 근거를 확보합니다.')
a += strategy_block('마지막 10분 활용법','남은 지문 수와 미응답 수부터 확인합니다. 앞부분의 애매한 한 문제로 즉시 돌아가기보다 읽지 않은 지문에서 풀 수 있는 문제를 확보합니다. 마지막 2분은 미응답과 답 표시 위치를 확인하도록 남겨 둡니다. 이미 고른 답은 새 근거가 생겼을 때 바꾸고, 단순히 불안하다는 이유로 바꾸지 않습니다. 이 교재의 55분 연습에서는 종료 10분 전부터 같은 절차를 적용합니다.')
page('RC Strategy',a)

reasons='문법 / 어휘 / 구문 / 독해 / 시간 부족 / 문제 오독 / 함정에 걸림 / 근거를 잘못 찾음 / 추론 실패 / 단어를 몰랐음'
for i in range(1,4):
    a=title('Error Log',f'오답 기록표 {i} / 3 | 틀린 문제와 확신 없이 맞힌 문제를 기록하세요.')
    a += [p('<b>오답 이유 분류</b>','small'),gap(5),p(reasons,'small'),gap(7),
          p('틀린 이유 칸에는 분류와 구체적인 판단 오류를 함께 적습니다. 예: 근거를 잘못 찾음 - 회신 날짜를 면접 날짜로 읽음. 다시 볼 날짜는 1일·3일·7일 뒤를 적습니다.','small'),gap(13)]
    headers=['문제','정답','내가\n고른 답','유형','틀린 이유','다시 볼\n날짜']
    rows=[[p(h.replace('\n','<br/>'),'small') for h in headers]]
    rows += [['','','','','',''] for _ in range(10)]
    t=Table(rows,colWidths=[W*x for x in [.07,.07,.11,.15,.40,.20]],rowHeights=[36]+[43]*10)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.5,LINE),
                           ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),5)]))
    a += [t,gap(14),p('이번 복습에서 가장 많이 반복한 실수: __________________________________________','small'),gap(13),
          p('다음 풀이에서 바꿀 행동 한 가지: _____________________________________________','small')]
    page('Error Log',a)

assert len(Q)==70 and [q['n'] for q in Q]==list(range(1,71))
assert Counter(q['level'] for q in Q)=={1:14,2:35,3:21}
assert all(len(q['opts'])==4 and len(set(q['opts']))==4 and q['answer'] in 'ABCD' for q in Q)
assert [n for s in P6 for n in s['nums']]==list(range(31,47))
assert [n for s in P7 for n in s['nums']]==list(range(47,71))
assert all(q['evidence'] for q in Q if q['n']>=47)

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.saved=[]
    def showPage(self):
        self.saved.append(dict(self.__dict__));self._startPage()
    def save(self):
        count=len(self.saved)
        if count!=len(pages): raise ValueError(f'Unexpected pagination: {count} vs {len(pages)}')
        for state in self.saved:
            self.__dict__.update(state)
            pn=self._pageNumber
            if pn>1:
                self.setStrokeColor(LINE);self.setLineWidth(.5)
                self.line(M,PH-20*mm,PW-M,PH-20*mm)
                self.setFont('Arial',8);self.setFillColor(GRAY)
                self.drawString(M,PH-17.8*mm,'TOEIC RC PRACTICE | SET 01')
                self.drawRightString(PW-M,PH-17.8*mm,pages[pn-1]['section'])
                self.drawCentredString(PW/2,16*mm,f'{pn} / {count}')
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

story=[]
for i,pg in enumerate(pages):
    if i:story.append(PageBreak())
    story.extend(pg['items'])
doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=M,rightMargin=M,
                      topMargin=PH-TOP,bottomMargin=BOTTOM,pageCompression=1,
                      title='TOEIC RC Practice Book - 700 to 800 - Set 01',
                      author='Independent study material',allowSplitting=0)
# Remove default 6-point frame padding so measured widths and actual layout agree.
from reportlab.platypus import Frame, PageTemplate
def make_template():
    return PageTemplate('book',[Frame(M,BOTTOM,W,H,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)])
doc._firstPageTemplateIndex=0
doc.handle_pageBegin = doc.handle_pageBegin
doc.addPageTemplates(make_template())
doc.build(story,canvasmaker=NumberedCanvas)
manifest=[dict(page=i+1,section=x['section'],content_height=x['height']) for i,x in enumerate(pages)]
(SCRATCH/'page_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(SCRATCH/'questions.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pdf=str(OUT),pages=len(pages),questions=len(Q),difficulty=dict(Counter(q['level'] for q in Q)),sections=dict(Counter(x['section'] for x in pages))),ensure_ascii=False))
