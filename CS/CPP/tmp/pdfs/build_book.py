from pathlib import Path
import re, json, random, collections, html, math
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
from review_data import WEEKLY, FINAL_PASSAGES

BASE=Path(__file__).resolve().parent
OUT=Path.cwd()/'output/pdf'
pdfmetrics.registerFont(TTFont('KR',str(BASE/'NanumGothic-Regular.ttf')))
pdfmetrics.registerFont(TTFont('KRB',str(BASE/'NanumGothic-Bold.ttf')))
pdfmetrics.registerFontFamily('KR',normal='KR',bold='KRB',italic='KR',boldItalic='KRB')
W,H=A4; LEFT=40; RIGHT=W-40; CW=W-80
NAVY=colors.HexColor('#15334F'); BLUE=colors.HexColor('#2463A3'); PALE=colors.HexColor('#EDF4FA'); GRAY=colors.HexColor('#596573'); RULE=colors.HexColor('#CCD8E3')
ST={}
for name,size,leading,col,font in [('body',10.5,16,NAVY,'KR'),('small',9,13,GRAY,'KR'),('cell',9.2,12.5,NAVY,'KR'),('en',9.5,13,NAVY,'KR'),('title',24,31,NAVY,'KRB'),('sub',14,20,BLUE,'KRB'),('tiny',8,11,GRAY,'KR')]:
    ST[name]=ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=col,wordWrap=None,spaceAfter=0)

def esc(x):return html.escape(str(x))
def P(x,style='body'):return Paragraph(x,ST[style])
def josa(s,a,b):
    ch=s[-1] if s else ''; n=ord(ch)-0xAC00
    return a if 0<=n<11172 and n%28 else b
def obj(s):return s+josa(s,'을','를')
def topic(s):return s+josa(s,'은','는')
def with_(s):return s+josa(s,'과','와')
def article(s):
    mass={'equipment','software','hardware','baggage','luggage','seating','packaging','parking','transportation','training','employment','housing','maintenance','cash','income','tax','information','data','research','advice','assistance','satisfaction','staff','merchandise','machinery','furniture','traffic','access','coverage','insurance','funding','financing','revenue','feedback','consent','compliance','evidence','progress','capacity','availability','reliability','efficiency','productivity','security','safety','quality','permission','construction','production','inventory','capital','interest','communication','work','waste','energy','water','electricity','power','food','bread','coffee','tea','milk','fuel','freight','labor','turnover','demand','supply','travel','accommodation','consumption','oversight','recruitment','retention','compensation','remuneration','copyright','goodwill','expertise','equipment','personnel','procurement','billing','workmanship','coordination','cooperation'}
    last=s.split()[-1].lower()
    if last in mass or (last.endswith('s') and last not in {'business','access','process','address','analysis','status'}):return s
    return ('an ' if s[0].lower() in 'aeiou' else 'a ')+s

SPECIAL_A={
'currently':('The service is currently available.','현재 서비스를 이용할 수 있다.'),
'responsible':('The assistant is responsible for scheduling.','일정 조정은 비서가 담당한다.'),
'available':('Printed copies are available on request.','요청하면 인쇄본을 받을 수 있다.'),
'previously':('The committee reviewed a previously approved proposal.','위원회는 이전에 승인된 제안을 검토했다.'),
'recently':('Please visit our recently updated website.','최근에 갱신된 당사 웹사이트를 방문해 주세요.'),
'approximately':('The presentation is approximately ten minutes long.','발표 길이는 약 10분이다.'),
'temporarily':('The ticket office is temporarily closed.','매표소는 일시적으로 운영을 중단했다.'),
'usually':('A meeting room is usually available.','보통 회의실을 이용할 수 있다.'),
'especially':('This model is especially popular with commuters.','이 모델은 특히 통근자에게 인기가 많다.'),
'fully':('The hotel is fully booked this weekend.','이번 주말 호텔 예약은 모두 찼다.'),
'eligible':('Full-time employees are eligible for benefits.','상근 직원은 복리후생을 받을 자격이 있다.'),
'accessible':('The exhibition hall is accessible to visitors.','방문객은 전시장에 접근할 수 있다.'),
'closed':('The lobby is closed for maintenance.','로비는 유지보수로 폐쇄되어 있다.'),
'normally':('The office is normally open on Saturdays.','사무실은 보통 토요일에 문을 연다.'),
}

SPECIAL_EX={
'mean':('A higher fee could mean a change in policy.','요금 인상은 정책 변경을 의미할 수 있다.'),
'owe':('Our records show that we owe money to a supplier.','기록에 따르면 우리는 공급업체에 지급할 돈이 있다.'),
'fluctuate':('Prices may fluctuate within a narrow range.','가격은 좁은 범위 안에서 변동할 수 있다.'),
'carelessly':('The device was handled carelessly during delivery.','배송 중 기기가 부주의하게 취급되었다.'),
'illegally':('The contractor was fined for dumping waste illegally.','시공업체는 폐기물을 불법 투기해 벌금을 부과받았다.'),
'negligently':('The equipment had been handled negligently.','장비가 부주의하게 취급되어 있었다.'),
'conceal':('Employees must not conceal a material fact when filing a claim.','직원은 보험금을 청구할 때 중요한 사실을 숨기면 안 된다.'),
'inflate':('Do not inflate expense claims.','경비 청구액을 부풀리지 마세요.'),
'overcharge':('Please check that we do not overcharge customers.','고객에게 과다 청구하지 않는지 확인해 주세요.'),
'undercharge':('An error may cause the store to undercharge for shipping.','오류로 매장이 배송료를 적게 청구할 수 있다.'),
'underpay':('Employers must not underpay temporary workers.','고용주는 임시 근로자에게 적정액보다 적게 지급하면 안 된다.'),
'discriminate':('It is unlawful to discriminate against job applicants.','입사 지원자를 차별하는 것은 위법이다.'),
'frustrate':('Unexpected delays can frustrate customers.','예상치 못한 지연은 고객을 답답하게 만들 수 있다.'),
'disappoint':('Delays may disappoint our customers.','지연은 고객을 실망시킬 수 있다.'),
'exhaust':('Unexpected repairs could exhaust the budget.','예상치 못한 수리로 예산이 소진될 수 있다.'),
'jeopardize':('A late delivery could jeopardize project success.','늦은 배송은 프로젝트 성공을 위태롭게 할 수 있다.'),
'obstruct':('Do not obstruct the entrance.','입구를 막지 마세요.'),
'disrupt':('Construction may disrupt normal operations.','공사로 정상 운영에 차질이 생길 수 있다.'),
'default':('The company could default on payment if revenue falls.','매출이 감소하면 회사가 대금 지급 의무를 이행하지 못할 수 있다.'),
'forfeit':('Guests who cancel after Friday forfeit the deposit.','금요일 이후 취소하는 투숙객은 보증금 반환 권리를 잃는다.'),
'accrue':('The account will accrue interest monthly.','해당 계좌에는 매월 이자가 쌓인다.'),
'adversely':('The delay could affect sales adversely.','지연은 매출에 부정적인 영향을 줄 수 있다.'),
'respectively':('Rooms 201 and 202 were assigned to Lee and Park, respectively.','201호와 202호는 각각 이 씨와 박 씨에게 배정되었다.'),
'nevertheless':('Costs rose; nevertheless, the company remained profitable.','비용이 올랐지만 회사는 여전히 수익을 냈다.'),
'nonetheless':('The schedule is tight; nonetheless, the team can finish on time.','일정이 빠듯하지만 팀은 제시간에 끝낼 수 있다.'),
'however':('The hotel is small; however, its meeting rooms are spacious.','호텔은 작지만 회의실은 넓다.'),
'therefore':('Demand increased; therefore, we hired more staff.','수요가 늘어 직원들을 더 채용했다.'),
'thus':('The new process reduces waste, thus lowering costs.','새 공정은 낭비를 줄여 비용을 낮춘다.'),
'consequently':('The flight was canceled; consequently, the meeting was postponed.','항공편이 취소되어 그 결과 회의가 연기되었다.'),
'moreover':('The printer is reliable; moreover, it is inexpensive to maintain.','프린터는 믿을 만하며 유지 비용도 저렴하다.'),
'furthermore':('We offer free delivery. Furthermore, installation is included.','무료 배송을 제공하며 설치도 포함되어 있다.'),
'meanwhile':('The technicians are repairing the system. Meanwhile, we accept phone orders.','기술자들이 시스템을 수리하고 있다. 그동안 전화 주문을 받는다.'),
'alternatively':('You may call our office. Alternatively, send us an email.','사무실로 전화하거나 대안으로 이메일을 보내도 된다.'),
'instead':('The model is unavailable, so we will send a replacement instead.','그 기종을 제공할 수 없어 대신 대체품을 보낼 예정이다.'),
'indeed':('The new process is indeed more efficient.','새 공정은 실제로 더 효율적이다.'),
'likewise':('The main office is closed. Likewise, all branches are closed today.','본사는 닫혀 있다. 마찬가지로 오늘 모든 지점도 닫혀 있다.'),
'additionally':('The hotel provides breakfast. Additionally, guests can use the gym.','호텔은 아침 식사를 제공하며 투숙객은 체육관도 이용할 수 있다.'),
'regardless':('The event will proceed regardless of the weather.','행사는 날씨에 상관없이 진행된다.'),
}

def predicate(k):
    pairs=[('위치함','위치해 있다'),('힘듦','힘들다'),('같음','같다'),('높음','높다'),('느림','느리다'),('많음','많다'),('없음','없다'),('있음','있다'),('않음','않다'),('됨','되어 있다'),('임','이다'),('함','하다'),('불가','불가능하다'),('가능','가능하다')]
    for a,z in pairs:
        if k.endswith(a):return k[:-len(a)]+z
    if k.endswith('담당'):return k+'한다'
    if k.endswith('다'):return k
    return k+' 상태이다'

def a_subject(c):
    rules=[(['entitled','eligible','insured'],'The employees','직원들'),(['liable','responsible','obligated'],'The company','회사'),(['priced'],'The product','제품'),(['located','renovated','open','closed','accessible'],'The office','사무실'),(['damaged','stored','produced'],'The goods','물품'),(['billed'],'The customer','고객'),(['equal','higher'],'The prices','가격'),(['complete','approved','scheduled','unchanged'],'The schedule','일정'),(['sound','insulated','cleaner'],'The building','건물'),(['demanding'],'The work','업무'),(['independent','profitable','viable','stable','successful','recognized','renowned'],'The company','회사'),(['clear'],'The instructions','지시 사항'),(['significant'],'The result','결과'),(['prepared'],'The team','팀'),(['noticeable'],'The change','변화'),(['covered'],'The loss','손해'),(['digital','advertised','designed'],'The product','제품'),(['contingent'],'The offer','제안'),(['friendly','complex'],'The process','절차')]
    for keys,en,ko in rules:
        if any(k in c for k in keys):return en,ko
    return 'The service','서비스'

def example(e,i):
    w,pos,m,code,c,k=e['word'],e['pos'],e['meaning'],e['code'],e['colloc'],e['kr']
    if w in SPECIAL_EX:return SPECIAL_EX[w]
    if code=='S':return c,k
    if code=='A' and w in SPECIAL_A:return SPECIAL_A[w]
    if code=='A':
        sub,sk=a_subject(c);be='are' if sub in ['The employees','The goods','The prices','The instructions'] else 'is'
        return (sub+' '+be+' '+c+'.',topic(sk)+' '+predicate(k)+'.')
    if code=='V':
        templates=[('Our staff will {c} this week.','직원들은 이번 주에 {k}할 예정이다.'),('We need to {c} before Friday.','금요일 전까지 {k}해야 한다.'),('The team plans to {c} soon.','팀은 곧 {k}할 계획이다.'),('Please {c} as soon as possible.','가능한 한 빨리 {k}해 주세요.'),('The company has decided to {c}.','회사는 {k}하기로 결정했다.')]
    elif code=='L':
        templates=[('Visitors should go to the {c}.','방문객은 {k}(으)로 가야 한다.'),('The meeting will be held at the {c}.','회의는 {k}에서 열린다.'),('Please meet us at the {c}.','{k}에서 만나 주세요.')]
    elif code=='H':
        templates=[('The manager spoke with the {c}.','관리자는 {withk} 이야기를 나눴다.'),('Please contact the {c} for details.','자세한 내용은 {k}에게 문의해 주세요.')]
    elif code=='E':
        templates=[('The notice confirms the date of the {c}.','공지에서 {k}의 날짜를 확인할 수 있다.'),('We are preparing for the {c}.','우리는 {objk} 준비하고 있다.')]
    elif code=='R':templates=[('We need {c} for the new project.','새 프로젝트에는 {k}이 필요하다.')]
    elif code=='C':templates=[('The delivery contained {ac}.','배송 물품에는 {k}이 포함되어 있었다.'),('Please inspect the {c} carefully.','{objk} 주의 깊게 점검해 주세요.')]
    else:
        templates=[('The email includes details about the {c}.','이메일에는 {k}에 대한 자세한 정보가 있다.'),('We discussed the {c} at the meeting.','회의에서 {k}에 대해 논의했다.'),('Please review the information about the {c}.','{k}에 관한 정보를 검토해 주세요.'),('Contact our office for details about the {c}.','{k}에 관한 자세한 사항은 사무실로 문의해 주세요.'),('The report contains a section on the {c}.','보고서에는 {k}에 관한 부분이 있다.')]
    en,kr=templates[i%len(templates)]
    kr=kr.format(k=k,objk=obj(k),withk=with_(k)).replace('(으)로',josa(k,'으로','로')).replace(k+'이 필요',k+josa(k,'이','가')+' 필요').replace(k+'이 포함',k+josa(k,'이','가')+' 포함')
    return en.format(c=c,ac=article(c)),kr

def wordpattern(w):
    forms=[w,w+'s',w+'es']
    if w.endswith('y'):forms.append(w[:-1]+'ies')
    if w.endswith('is'):forms.append(w[:-2]+'es')
    return r'(?<![A-Za-z])(?:'+'|'.join(re.escape(x) for x in sorted(forms,key=len,reverse=True))+r')(?![A-Za-z])'

def load_days():
    days=[]
    for line in (BASE/'vocabulary.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        if line.startswith('@'):
            d,title,goal=line[1:].split('|');days.append(dict(day=int(d),title=title,goal=goal,entries=[]))
        else:
            w,pos,m,c,k=line.split('|');code,coll=c.split(':',1)
            e=dict(word=w,pos=pos,meaning=m,code=code,colloc=coll,kr=k)
            en,ko=example(e,len(days[-1]['entries'])+days[-1]['day']);e.update(en=en,ko=ko)
            if code=='S':e['colloc']={'although':'although + clause','unless':'unless + clause','provided':'provided (that) + clause','whereas':'whereas + clause','except':'except Sunday','thereof':'the costs thereof','whereby':'a system whereby'}[w]
            days[-1]['entries'].append(e)
    seen=collections.Counter(e['word'].lower() for d in days for e in d['entries'])
    dup=[w for w,n in seen.items() if n>1]
    assert not dup,('Duplicate headwords',dup)
    for d in days:
        assert len(d['entries'])==30,(d['day'],len(d['entries']))
        for e in d['entries']:
            assert re.search(wordpattern(e['word']),e['en'],re.I),(d['day'],e['word'],e['en'])
    return days

class Book:
    def __init__(self,path):
        self.path=path;self.c=canvas.Canvas(str(path),pagesize=A4,pageCompression=1);self.c.setTitle('TOEIC 900 Vocabulary - 60 Day Challenge');self.c.setAuthor('Personal Study Edition');self.p=0;self.toc=[];self.overflows=[];self.sections={};self.logs=[]
    def new(self,label,title=None,sub=None,key=None):
        if self.p:self.c.showPage()
        self.p+=1;self.y=H-86;self.c.setFillColor(NAVY);self.c.setFont('KRB',8.5);self.c.drawString(LEFT,H-32,'TOEIC 900  /  VOCABULARY');self.c.setFont('KR',8);self.c.drawRightString(RIGHT,H-32,label)
        self.c.setStrokeColor(RULE);self.c.line(LEFT,H-43,RIGHT,H-43);self.c.line(LEFT,34,RIGHT,34);self.c.setFont('KR',8);self.c.setFillColor(GRAY);self.c.drawString(LEFT,22,'60 DAY CHALLENGE  |  1,800 WORDS');self.c.drawRightString(RIGHT,22,f'{self.p:03d}')
        if title:self.para(title,'title',after=10)
        if sub:self.para(sub,'small',after=15)
        if key:self.sections[key]=self.p
        return self.p
    def para(self,text,style='body',after=8,x=None,width=None):
        p=P(text,style); ww,hh=p.wrap(width or CW,1000)
        if self.y-hh<49:self.overflows.append((self.p,'paragraph',text[:80],self.y-hh))
        p.drawOn(self.c,x or LEFT,self.y-hh);self.y-=hh+after
        self.logs.append((self.p,x or LEFT,self.y+after,ww,hh))
    def table(self,rows,widths,header=True,font='cell',rowpad=8):
        data=[[P(str(v),font) for v in row] for row in rows]
        t=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
        cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),rowpad),('BOTTOMPADDING',(0,0),(-1,-1),rowpad),('LINEBELOW',(0,0),(-1,0),.6,BLUE),('LINEBELOW',(0,1),(-1,-1),.35,RULE)]
        if header:cmds += [('BACKGROUND',(0,0),(-1,0),PALE)]
        for z in range(1,len(rows)):
            if z%2==0:cmds.append(('BACKGROUND',(0,z),(-1,z),colors.HexColor('#F7FAFC')))
        t.setStyle(TableStyle(cmds));ww,hh=t.wrap(CW,10000)
        if self.y-hh<49:self.overflows.append((self.p,'table',hh,self.y-hh))
        t.drawOn(self.c,LEFT,self.y-hh);self.y-=hh+12
        self.logs.append((self.p,LEFT,self.y+12,ww,hh))
    def box(self,label,body):
        self.para(label,'sub',after=5);self.para(body,'body',after=14)
    def finish(self):
        self.c.save();assert not self.overflows,self.overflows

def read_focus():
    out=collections.defaultdict(list)
    for line in (BASE/'daily_focus.txt').read_text(encoding='utf-8').splitlines():
        if line.strip():
            day,prompt,ops,answer,why=line.split('|');ops=ops.split(';')
            assert len(ops)==4 and answer in ops
            out[int(day)].append(dict(type='Part 5',prompt=prompt,options=ops,answer=ops.index(answer),word=answer,why=why))
    return out

DAILY_FOCUS=read_focus()
def daily_questions(d):
    es=d['entries'];qs=[]
    for e in es[:5]:qs.append(dict(type='영어 → 한국어',prompt=e['word'],answer=e['meaning'],why=e['colloc']))
    for e in es[10:15]:qs.append(dict(type='한국어 → 영어',prompt=e['meaning']+' ('+e['pos']+'.)',answer=e['word'],why=e['colloc']))
    picked=[]
    for pos in ['n','v','adj','adv','n']:
        pool=[e for e in es if e['pos'].split('/')[0]==pos and e not in picked]
        e=pool[-1] if pool else next(e for e in es if e not in picked);picked.append(e)
        base=e['pos'].split('/')[0]
        distract={'n':['carefully','eligible','apologize'],'v':['equipment','reliable','promptly'],'adj':['equipment','apologize','carefully'],'adv':['equipment','reliable','apologize']}[base]
        target=re.search(wordpattern(e['word']),e['en'],re.I).group()
        options=[target]+distract;random.Random(d['day']*31+len(qs)).shuffle(options)
        question=re.sub(wordpattern(e['word']),'_______',e['en'],count=1,flags=re.I)
        qs.append(dict(type='Part 5',prompt=question,options=options,answer=options.index(target),word=target,why=f"{e['meaning']}. {e['colloc']}에서 {e['pos']}. 형태를 확인한다.",translation=e['ko']))
    for n,q in enumerate(DAILY_FOCUS.get(d['day'],[])[:2]):
        ops=q['options'][:];random.Random(d['day']*61+n).shuffle(ops)
        qq=q.copy();qq['options']=ops;qq['answer']=ops.index(q['word']);qs[10+n]=qq
    assert len(qs)==15
    return qs

FOCUS={
1:'employee 직원 / employer 고용주; staff는 직원 집단; colleague 동료 / supervisor 상사; responsible for + 명사; full-time / part-time 근무 형태',
2:'postpone 미루다 / cancel 취소하다; reserve 예약하다 / confirm 확정하다; discuss + 목적어(about 불필요); minutes 회의록 / minute 분; prompt 신속한 / promptly 신속히',
3:'invoice 청구서 / receipt 영수증; ship 발송 / deliver 배달; package 포장물 / packaging 포장; quantity 수량 / quality 품질; safely 안전히 / safety 안전',
4:'fare 운임 / fee 수수료; baggage·luggage는 불가산; board 탑승하다 / aboard 탑승하여; domestic 국내 / international 국제; depart from / arrive at',
5:'complimentary 무료의 / complementary 보완하는; reservation 예약 / reserve 예약하다; accommodation 숙박 시설; charge 요금 청구 / fee 요금; especially 특히 / specially 특별히',
6:'refund 환불 / exchange 교환; defective 결함 있는 / damaged 손상된; satisfied 사람 / satisfying 만족감을 주는; respond to + 문의; apologize for + 사유',
7:'applicant 지원자 / application 지원서; qualification 자격 / qualified 자격 있는; apply for 직위 / apply to 회사; experience 경력(불가산); eligible for + 혜택',
8:'equipment·software는 불가산; efficient 효율적인 / effective 효과적인; operate 작동 / operation 운영; compatible with + 기기; automatic 형용사 / automatically 부사',
9:'outstanding 미지급의·뛰어난; expense 비용 / expensive 비싼; deposit 예치 / withdraw 인출; profit 이익 / revenue 매출; due 지급 예정의 / overdue 연체된',
10:'maintenance 유지보수 / maintain 유지하다; accessible 접근 가능한 / access 접근; notice 공지·알아차리다; register for 행사; closed 상태 / close 동작',
}

def day_pages(b,d):
    day=d['day'];es=d['entries'];phase=(day-1)//10+1
    for part in range(3):
        b.new(f'DAY {day:02d} / WORDS {part*10+1:02d}-{part*10+10:02d}',f'Day {day:02d}  |  {d["title"]}',f'Phase {phase}  ·  {d["goal"]}' if part==0 else '예문을 읽고 빈출 표현을 소리 내어 반복하세요.',key=f'day{day}' if part==0 else None)
        rows=[['번호','단어','품사','핵심 뜻','TOEIC 표현','예문 / 해석']]
        for i,e in enumerate(es[part*10:(part+1)*10],part*10+1):
            rows.append([f'{i:02d}',f'<b>{esc(e["word"])}</b>',e['pos']+'.',esc(e['meaning']),esc(e['colloc']),esc(e['en'])+'<br/><font color="#657080">'+esc(e['ko'])+'</font>'])
        b.table(rows,[28,78,35,65,108,CW-314],rowpad=7)
        b.para('인식 체크  [ ] 뜻이 바로 떠오름   [ ] 표현을 말할 수 있음   [ ] 예문을 이해함','small')
    qs=daily_questions(d)
    b.new(f'DAY {day:02d} / MINI TEST',f'Day {day:02d}  Mini Test','책을 덮고 8~10분 안에 풀어 보세요. 각 1점, 총 15점. 뜻은 핵심 의미가 맞으면 인정합니다.',key=f'mini{day}')
    b.para('01-05  영어 → 한국어','sub',after=7)
    rows=[]
    for i,q in enumerate(qs[:5],1):rows.append([f'{i:02d}. '+q['prompt'],'________________________________'])
    b.table(rows,[CW*.46,CW*.54],header=False,rowpad=6)
    b.para('06-10  한국어 → 영어','sub',after=7)
    rows=[]
    for i,q in enumerate(qs[5:10],6):rows.append([f'{i:02d}. '+q['prompt'],'________________________________'])
    b.table(rows,[CW*.46,CW*.54],header=False,rowpad=6)
    b.para('11-15  Part 5  빈칸에 가장 알맞은 답을 고르세요.','sub',after=6)
    for i,q in enumerate(qs[10:],11):
        b.para(f'<b>{i:02d}.</b> '+esc(q['prompt']),'en',after=4)
        b.para(' &nbsp; '.join(f'({chr(65+j)}) {esc(o)}' for j,o in enumerate(q['options'])),'small',after=9)
    b.new(f'DAY {day:02d} / ANSWERS & REVIEW',f'Day {day:02d}  Answers','채점 후 틀린 단어는 뜻·품사·연어 중 무엇을 놓쳤는지 표시하세요.',key=f'answer{day}')
    b.para('01-10  정답','sub',after=6)
    rows=[]
    for i in range(5):rows.append([f'{i+1:02d}. {esc(qs[i]["answer"])}',f'{i+6:02d}. <b>{qs[i+5]["answer"]}</b>'])
    b.table(rows,[CW/2,CW/2],header=False,rowpad=5)
    b.para('11-15  정답과 해설','sub',after=6)
    for i,q in enumerate(qs[10:],11):
        b.para(f'<b>{i}. ({chr(65+q["answer"])}) {q["word"]}</b>  -  {esc(q["why"])}','small',after=5)
    b.para("Today's Review",'sub',after=8)
    b.para('오늘 신규 단어: <b>30개</b>  /  점수: ____ / 15  /  재시험: ____ / 15','body')
    important=[es[i]['word'] for i in [0,4,10,12,22]]
    confusing=[es[i]['word'] for i in [1,8,15,23,26]]
    expressions=[es[i]['colloc'] for i in [10,13,19,22,28]]
    b.para('<b>가장 중요한 단어 5개</b><br/>'+ ' · '.join(important),'small')
    b.para('<b>헷갈리기 쉬운 단어 5개</b><br/>'+ ' · '.join(confusing),'small')
    b.para('<b>오늘 반드시 외울 표현 5개</b><br/>'+ ' / '.join(expressions),'small')
    focus=FOCUS.get(day,' / '.join(e['word']+' ('+e['pos']+'.)' for e in es[20:25]))
    b.para('<b>구분 포인트</b><br/>'+esc(focus),'small')
    b.para('복습 체크  [ ] 오늘 저녁  [ ] D+1  [ ] D+3  [ ] D+7  [ ] D+14<br/>취약 단어  ____________________  ____________________  ____________________','small')

def sample_build():
    days=load_days();b=Book(BASE/'stage_day01_10.pdf')
    for d in days[:10]:day_pages(b,d)
    b.finish(); print(json.dumps(dict(days=len(days),headwords=sum(len(d['entries']) for d in days),pages=b.p,duplicates=0,overflows=b.overflows),ensure_ascii=False))
    (BASE/'stage_audit.json').write_text(json.dumps(days,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':sample_build()
