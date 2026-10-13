from pathlib import Path
import json, re, html, unicodedata
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents

ROOT=Path(__file__).resolve().parents[2]
TMP=ROOT/'tmp'/'pdfs'
OUT=ROOT/'output'/'pdf'/'Toeic RC.pdf'
pdfmetrics.registerFont(TTFont('Malgun','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('MalgunBold','C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Malgun',normal='Malgun',bold='MalgunBold',italic='Malgun',boldItalic='MalgunBold')
NAVY=colors.HexColor('#17345a'); INK=colors.HexColor('#20252b'); PALE=colors.HexColor('#f2f4f7'); GRAY=colors.HexColor('#66707c')
W,H=A4; M=20*mm; WIDTH=W-2*M
ST={
 'body':ParagraphStyle('body',fontName='Malgun',fontSize=10.4,leading=14.8,textColor=INK,spaceAfter=6,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'english':ParagraphStyle('english',fontName='Malgun',fontSize=10.4,leading=14.8,textColor=INK,spaceAfter=7,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'h1':ParagraphStyle('h1',fontName='MalgunBold',fontSize=23,leading=31,textColor=NAVY,spaceBefore=7,spaceAfter=14,keepWithNext=True,wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='MalgunBold',fontSize=15,leading=21,textColor=NAVY,spaceBefore=14,spaceAfter=9,keepWithNext=True,wordWrap='CJK'),
 'h3':ParagraphStyle('h3',fontName='MalgunBold',fontSize=11.3,leading=16,textColor=INK,spaceBefore=9,spaceAfter=4,keepWithNext=True,wordWrap='CJK'),
 'label':ParagraphStyle('label',fontName='MalgunBold',fontSize=10.4,leading=14.8,textColor=NAVY,spaceBefore=5,spaceAfter=2,keepWithNext=True,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='Malgun',fontSize=9,leading=12.6,textColor=GRAY,spaceAfter=5,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='Malgun',fontSize=10,leading=14,textColor=INK,wordWrap='CJK'),
 'q':ParagraphStyle('q',fontName='Malgun',fontSize=10.4,leading=14.8,textColor=INK,spaceAfter=5,wordWrap='CJK'),
 'options':ParagraphStyle('options',fontName='Malgun',fontSize=10.4,leading=14.8,textColor=INK,leftIndent=11,spaceAfter=8,wordWrap='CJK'),
}

def clean(t):
    t=str(t).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    return unicodedata.normalize('NFC',t)
def esc(t): return html.escape(clean(t)).replace('\n','<br/>')
def p(t,style='body'): return Paragraph(esc(t),ST[style])
def rich(t,style='body'): return Paragraph(t,ST[style])

class Book(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=22*mm,bottomMargin=20*mm,title='Toeic RC',author='Original study material',pageCompression=1)
        self.running='Toeic RC'; self.entries=[]
        frame=Frame(M,20*mm,WIDTH,H-42*mm,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id='main')
        self.addPageTemplates(PageTemplate(id='normal',frames=[frame],onPageEnd=self.page))
    def beforeDocument(self): self.running='Toeic RC'; self.entries=[]
    def page(self,c,doc):
        c.saveState()
        if doc.page>1:
            c.setFont('Malgun',8.3); c.setFillColor(GRAY)
            c.drawString(M,H-14*mm,'Toeic RC')
            c.drawRightString(W-M,H-14*mm,self.running)
            c.setStrokeColor(colors.HexColor('#cbd1d9')); c.setLineWidth(.4); c.line(M,H-17*mm,W-M,H-17*mm)
        c.setFont('Malgun',9); c.setFillColor(GRAY); c.drawCentredString(W/2,11*mm,str(doc.page))
        c.restoreState()
    def afterFlowable(self,f):
        if hasattr(f,'toc_level'):
            self.canv.bookmarkPage(f.bookmark)
            self.canv.addOutlineEntry(f.toc_text,f.bookmark,level=f.toc_level,closed=True)
            self.notify('TOCEntry',(f.toc_level,f.toc_text,self.page,f.bookmark))
            self.entries.append({'title':f.toc_text,'page':self.page,'level':f.toc_level})
            if f.toc_level==0:self.running=f.toc_text

story=[]; seq=0
def heading(t,level=1,toc=True):
    global seq
    flow=p(t,'h1' if level==0 else 'h2')
    if toc:
        seq+=1; flow.bookmark=f'anchor{seq}';flow.toc_text=clean(t);flow.toc_level=level
    story.append(flow)
def para(t):story.append(p(t))
def block(label,text):story.extend([p(label,'label'),p(text)])
def table(rows,widths,header=False):
    data=[[p(x,'cell') for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    rules=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cbd1d9'))]
    if header:rules.append(('BACKGROUND',(0,0),(-1,0),PALE))
    t.setStyle(TableStyle(rules));story.extend([t,Spacer(1,8)])
def question(q,training=False):
    label=f"{q['id']}. "
    if training:label+=f"[{q['level']}] "
    opts='<br/>'.join(f"({letter}) {esc(s)}" for letter,s in zip('ABCD',q['options']))
    story.append(KeepTogether([p(label+q['prompt'],'q'),rich(opts,'options')]))
def explanation(q):
    story.append(CondPageBreak(90))
    story.append(p(f"{q['id']} 해설 | 정답 ({q['answer']})",'h3'))
    block('1. 정답',f"({q['answer']}) {q['options']['ABCD'.index(q['answer'])]}")
    block('2. 문제 유형',q['type'])
    block('3. 핵심 단서',q['clue'])
    block('4. 문장 구조 또는 문맥 분석',q['analysis'])
    block('5. 정답이 성립하는 이유',q['why'])
    block('6. 오답 선택지 분석','\n'.join(f"({a}) {q['wrong'][a]}" for a in 'ABCD' if a!=q['answer']))
    block('7. 실전 풀이 순서',q['order'])
    block('8. 다른 문제에 적용할 규칙',q['rule'])
    story.append(Spacer(1,5))
def passage_set(s,training=False):
    start=len(story)
    story.append(p(s['title'],'h3'))
    story.append(p(f"Questions {s['questions'][0]['id']}-{s['questions'][-1]['id']}",'small'))
    for d in s['documents']:
        story.append(p(d['title'],'label'))
        paragraphs=re.split(r'\n\s*\n',d['text'].strip())
        for t in paragraphs:story.append(p(t,'english'))
    for q in s['questions']:question(q,training)
    story.append(Spacer(1,8))
    flows=story[start:]
    flat=[]
    for f in flows:
        flat.extend(f._content if isinstance(f,KeepTogether) else [f])
    estimate=sum(f.wrap(WIDTH,100000)[1]+f.getSpaceBefore()+f.getSpaceAfter() for f in flat)
    del story[start:]
    if estimate<=H-42*mm-12:
        story.append(KeepTogether(flat))
    else:
        story.append(CondPageBreak(330))
        story.extend(flows)

def validate_question(q):
    required=['id','prompt','options','answer','type','level','clue','analysis','why','wrong','order','rule']
    assert all(k in q for k in required),(q.get('id'),set(required)-set(q))
    q['id']=str(q['id'])
    assert len(q['options'])==4 and len(set(q['options']))==4,q['id']
    assert q['answer'] in 'ABCD',q['id']
    assert set(q['wrong'])==set('ABCD')-{q['answer']},q['id']
    for k in ['prompt','type','clue','analysis','why','order','rule']:assert isinstance(q[k],str) and len(q[k])>=2,(q['id'],k)
    for v in q['wrong'].values():assert isinstance(v,str) and len(v)>5,q['id']
    return q

def main():
    g=json.loads((TMP/'content'/'part5.json').read_text(encoding='utf-8-sig'))
    s=json.loads((TMP/'content'/'part6_mock5.json').read_text(encoding='utf-8-sig'))
    r=json.loads((TMP/'content'/'part7.json').read_text(encoding='utf-8-sig'))
    multi_path=TMP/'content'/'part7_mock_multi.json'
    if multi_path.exists() and len(r['mock'])==10:
        r['mock'].extend(json.loads(multi_path.read_text(encoding='utf-8-sig')))
    train5=[q for ch in g['chapters'] for q in ch['questions']]
    assert len(g['chapters'])==20 and len(train5)==40
    train6=[q for x in s['part6']['sets'] for q in x['questions']]
    train7=[q for x in r['training'] for q in x['questions']]
    mock=s['mock5']+[q for x in s['mock6'] for q in x['questions']]+[q for x in r['mock'] for q in x['questions']]
    allq=train5+train6+train7+mock
    for q in allq:validate_question(q)
    assert len({q['id'] for q in allq})==len(allq)
    assert [q['id'] for q in mock]==[str(n) for n in range(101,201)]
    assert len(s['mock5'])==30 and len(s['mock6'])==4 and all(len(x['questions'])==4 for x in s['mock6'])
    assert len(r['mock'])==15 and sum(len(x['questions']) for x in r['mock'][:10])==29
    assert all(len(x['questions'])==5 for x in r['mock'][10:])
    for x in s['part6']['sets']+s['mock6']:
        text=' '.join(d['text'] for d in x['documents'])
        for q in x['questions']:assert f"[{q['id']}]" in text,q['id']
    OUT.parent.mkdir(parents=True,exist_ok=True)

    story.extend([Spacer(1,65),p('Toeic RC','h1'),Spacer(1,14)])
    para('총점 700점대에서 950점 이상을 목표로 하는 학습자를 위한 RC 학습 교재')
    para('문법과 구조 → 문맥과 논리 → 독해 근거 → 75분 실전 적용')
    story.append(Spacer(1,26))
    table([['01','Part 5','문법·문장 구조·난도별 문제'],['02','Part 6','문맥 완성·문장 삽입·연결'],['03','Part 7','단일·이중·삼중 지문 독해'],['04','실전 모의고사','100문항·정답표·전체 해설']],[35,105,WIDTH-140])
    story.append(Spacer(1,20))
    para(f"창작 연습 {len(train5)+len(train6)+len(train7)}문항 + 창작 실전 모의고사 100문항")
    para('단어장 및 암기용 단어 목록을 제외하고, 정답의 근거와 오답 제거 과정을 설명합니다.')
    story.append(p('A4 세로 · 본문 10.4pt · 한글 글꼴 포함 · 2026년 10월 제작','small'))
    story.append(PageBreak())
    heading('목차',1,False)
    para('페이지 번호와 PDF 책갈피를 이용해 각 파트, 단원, 문제 및 해설로 이동할 수 있습니다.')
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',fontName='MalgunBold',fontSize=11.2,leading=17,textColor=NAVY,spaceBefore=9,wordWrap='CJK'),ParagraphStyle('toc1',fontName='Malgun',fontSize=10,leading=15,leftIndent=11,firstLineIndent=0,spaceBefore=2,wordWrap='CJK')]
    story.append(toc)
    story.append(PageBreak())
    heading('이 교재의 사용법',1,False)
    para('목표 점수의 의미: TOEIC Listening & Reading의 각 영역은 5-495점이며 총점은 10-990점입니다. 따라서 지침의 700점→950점은 총점 목표로 해석합니다. 이 교재는 그 목표를 뒷받침하는 RC 역량을 훈련하며, LC 학습과 점수 향상 보장은 포함하지 않습니다.')
    para('공식 형식: RC 100문항, 75분. Part 5는 30문항, Part 6는 16문항, Part 7은 54문항입니다. Part 7 모의고사는 단일 지문 10세트·29문항, 복수 지문 5세트·25문항으로 구성했습니다. 아래 시간 배분과 학습 목표는 교재의 훈련 제안이며 시험의 공식 규정이 아닙니다.')
    para('ETS 형식·점수 확인 자료: TOEIC Listening & Reading Score User Guide, https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf (2026-10-13 확인). 실제 문제는 모두 새로 작성했습니다. ETS 공식 교재가 아니며 공식 환산표를 제공하지 않습니다.')
    block('학습 순서','단원 개념을 읽고 예문의 주어·동사와 빈칸 자리를 표시합니다. 해설을 가린 채 문제를 풀고 정답 근거를 한 문장으로 기록합니다. 채점 뒤 맞힌 문제도 근거가 틀리거나 추측했다면 복습 대상으로 분류합니다. 24시간 후, 3일 후, 7일 후에 같은 규칙을 설명하고 다시 풉니다.')
    table([['난도','학습 목표'],['기본','한 문장 안에서 한 가지 직접 단서를 확인한다.'],['중급','구조 분석과 규칙을 함께 적용한다.'],['고급','수식어·예외·문맥 중 복수 단서를 결합한다.'],['실전 최상급','앞뒤 문장 또는 여러 문서를 연결하고 시간 제한에서 근거를 설명한다.']],[78,WIDTH-78],True)
    block('700점대에서 점검할 핵심 역량','품사 이름만 아는 상태에서 벗어나 빈칸의 기능을 먼저 결정합니다. 긴 수식어를 괄호로 묶어 주절을 복구하고, 문장 사이의 시간·인과·대조를 표시합니다. 독해에서는 지문 단어와 보기가 비슷하다는 이유 대신, 주체·조건·시점까지 일치하는 근거를 찾습니다.')
    story.append(PageBreak())
    heading('시간 관리와 오답 분석',1,False)
    table([['구간','훈련용 배분','누적 경과 시간'],['Part 5','10분','10분'],['Part 6','8분','18분'],['Part 7 단일 지문','25분','43분'],['Part 7 복수 지문','29분','72분'],['표시 문제·답안 확인','3분','75분']],[135,115,WIDTH-250],True)
    para('처음부터 이 속도를 강제하지 않습니다. 첫 회는 시간 없이 근거 정확성을 확인하고, 다음 회부터 실제 소요 시간을 기록합니다. Part 5에서 약 25초 동안 구조상 단서를 찾지 못하면 임시 답을 남기고 진행합니다. Part 7은 한 세트의 근거 위치를 찾지 못한 문항을 표시하고 다른 문항을 푼 뒤 돌아옵니다. 종이에 답을 옮기는 시간도 포함합니다.')
    table([['오답 원인','확인 질문','다음 행동'],['문법 지식 부족','빈칸의 기능은 알지만 규칙을 말하지 못했는가?','규칙·예외와 대비 예문 1쌍을 다시 설명한다.'],['문장 구조 분석 실패','수식어를 주어나 동사로 잘못 읽었는가?','주절 S/V/O/C를 표시하고 수식 범위를 묶는다.'],['문맥 이해 부족','조건·시점·주체 또는 논리 연결을 놓쳤는가?','앞뒤 문장과 보기의 차이를 근거와 함께 기록한다.'],['시간 부족','시간 없이 다시 풀면 정확한 근거를 찾는가?','위치 찾기와 판단 시간을 나누어 같은 유형을 제한 시간으로 푼다.']],[100,165,WIDTH-265],True)
    block('맞힌 문제도 다시 보는 기준','정답을 맞혔어도 나머지 세 선택지를 제거한 이유를 말하지 못하면 미완료입니다. 근거 없는 정답은 G(추측), 근거가 분명한 정답은 E(확인)로 표시합니다. 정답률과 함께 E 비율, 무제한 재풀이 정답률, 시간 초과 문항 수를 기록하면 지식과 속도 문제를 분리할 수 있습니다.')
    block('근거 교정 예시','The report, along with its appendices, is ready. 이 문장의 is를 appendices가 가까우므로 선택했다고 설명했다면 답은 맞아도 근거는 틀렸습니다. 주어의 중심어는 report이며 along with its appendices는 추가 수식어입니다. 복습에는 정답 대신 “수식어를 제외하고 주어 중심어와 일치시킨다”를 적습니다.')

    story.append(PageBreak());heading('Part 5',0)
    for t in g['intro']:para(t)
    for i,ch in enumerate(g['chapters'],1):
        topic=re.sub(r'^\d+[.\s]+','',ch['title'])
        story.append(CondPageBreak(150));heading(f"5.{i:02d} {topic}")
        for b in ch['sections']:block(b['label'],b['text'])
        story.append(p('난도별 연습 | 먼저 풀고 아래 해설 확인','h3'))
        for q in ch['questions']:question(q,True)
        for q in ch['questions']:explanation(q)
    story.append(PageBreak());heading('Part 6',0)
    for t in s['part6']['intro']:para(t)
    for i,b in enumerate(s['part6']['sections'],1):
        topic=re.sub(r'^\d+[.\s]+','',b['title'])
        heading(f"6.{i:02d} {topic}")
        for t in b['paragraphs']:para(t)
    heading('Part 6 문맥 완성 연습')
    para('각 지문의 전체 목적을 확인한 후 네 빈칸을 풉니다. 문장 삽입은 앞 문장과 뒤 문장 모두 연결되는지 확인합니다. 해설은 모든 연습 지문 뒤에 있습니다.')
    for x in s['part6']['sets']:passage_set(x,True)
    story.append(PageBreak());heading('Part 6 연습 정답과 해설')
    for q in train6:explanation(q)
    story.append(PageBreak());heading('Part 7',0)
    for t in r['intro']:para(t)
    for i,b in enumerate(r['sections'],1):
        topic=re.sub(r'^\d+[.\s]+','',b['title'])
        heading(f"7.{i:02d} {topic}")
        for t in b['paragraphs']:para(t)
    heading('Part 7 단일·복수 지문 연습')
    para('문항별 근거를 문서 제목과 표현으로 기록합니다. 연계 문제는 문서 A의 조건과 문서 B 또는 C의 사실을 결합합니다. 단순한 업무 상식으로 내용을 추가하지 않습니다.')
    for x in r['training']:passage_set(x,True)
    story.append(PageBreak());heading('Part 7 연습 정답과 해설')
    for q in train7:explanation(q)
    story.append(PageBreak());heading('실전 모의고사',0)
    para('제한 시간 75분 | 총 100문항 | 번호 101-200 | 모든 문항은 창작 문제입니다.')
    para('문제와 정답표·해설을 분리했습니다. 시작 시각과 각 파트의 종료 시각을 기록하고, 문제마다 가장 적절한 답 하나를 고릅니다. 답이 불확실하면 임시 답과 표시를 남기고 진행합니다. 원점수는 학습 진단에만 사용하며 공식 점수로 환산하지 않습니다.')
    table([['시작 시각','Part 5 종료','Part 6 종료','전체 종료'],['________________','________________','________________','________________']],[WIDTH/4]*4,True)
    heading('모의고사 답안 기록표')
    table([[f'{n}  _____' for n in range(k,k+5)] for k in range(101,201,5)],[WIDTH/5]*5)
    story.append(PageBreak());heading('모의고사 Part 5 | 101-130')
    para('Directions: Choose the best word or phrase to complete each sentence.')
    for q in s['mock5']:question(q)
    story.append(PageBreak());heading('모의고사 Part 6 | 131-146')
    para('Directions: Read each text and choose the best word, phrase, or sentence for each blank.')
    for x in s['mock6']:passage_set(x)
    story.append(PageBreak());heading('모의고사 Part 7 | 147-200')
    para('Directions: Read each text or set of texts and choose the best answer to each question.')
    for x in r['mock']:passage_set(x)
    story.append(PageBreak());heading('모의고사 정답표')
    table([[f"{q['id']}  {q['answer']}" for q in mock[k:k+5]] for k in range(0,100,5)],[WIDTH/5]*5)
    para('정답 수: Part 5 ____/30 · Part 6 ____/16 · Part 7 ____/54 · 전체 ____/100')
    para('시간 초과 ____문항 · 추측 정답(G) ____문항 · 근거 확인 정답(E) ____문항')
    story.append(PageBreak());heading('모의고사 Part 5 상세 해설')
    for q in s['mock5']:explanation(q)
    story.append(PageBreak());heading('모의고사 Part 6 상세 해설')
    for q in mock[30:46]:explanation(q)
    story.append(PageBreak());heading('모의고사 Part 7 상세 해설')
    for q in mock[46:]:explanation(q)
    story.append(PageBreak());heading('모의고사 복습과 재훈련')
    block('채점 직후','정답표만 보고 종료하지 않습니다. 맞힌 문제를 포함해 각 문항에 E 또는 G를 표시하고 오답 원인을 네 분류 중 하나로 기록합니다. 시간이 부족했다면 제한 없이 다시 풀어 지식 부족과 속도 부족을 구분합니다. 무제한 재풀이도 틀린 문제는 먼저 개념·구조·문맥을 보완합니다.')
    table([['번호','내 답 / 정답','원인','놓친 단서 / 재풀이 규칙'],['________','____________','________','________________________________'],['________','____________','________','________________________________'],['________','____________','________','________________________________'],['________','____________','________','________________________________'],['________','____________','________','________________________________']],[55,90,75,WIDTH-220],True)
    block('24시간 후','해설을 가리고 정답 근거 한 문장과 오답 세 개의 오류를 설명합니다. Part 5는 빈칸의 기능→구조→수일치·시제·태 순서로 재현합니다. Part 6는 앞뒤 문장의 관계와 지칭 대상을 표시합니다. Part 7은 정확한 근거 문서·문장과 보기의 차이를 적습니다.')
    block('3일·7일 후','같은 문항을 외워 맞히는 데 그치지 않고, 조건 하나를 바꾸면 어떤 선택지가 가능해지는지 설명합니다. 이후 다른 연습 지문에서 같은 규칙을 찾아 적용합니다. 제한 시간에서는 정확한 근거를 확보한 문항의 수와 걸린 시간을 함께 측정합니다.')
    block('다음 모의고사 전 체크','Part 5에서 수식어를 제외한 핵심 주어와 정동사를 찾았는가? Part 6에서 시제의 기준 시점과 삽입문 앞뒤 연결을 확인했는가? Part 7에서 주체·날짜·조건·수량을 대조했는가? NOT/EXCEPT는 세 개의 참 근거를 확인했는가? 답안 번호를 확인하고 마지막 3분을 확보했는가?')
    para('학습 목표는 정답률과 근거 확인 비율을 함께 높이는 것입니다. 고득점 목표를 위해서는 LC도 별도로 준비하고, 공식 시험의 영역별 성적표를 이용해 실제 약점을 확인합니다.')
    doc=Book(OUT);doc.multiBuild(story,maxPasses=5)
    from pypdf import PdfReader
    reader=PdfReader(OUT)
    manifest={'file':str(OUT),'pages':len(reader.pages),'training':{'part5':len(train5),'part6':len(train6),'part7':len(train7)},'mock':{'part5':30,'part6':16,'part7':54},'total_questions':len(allq),'toc':doc.entries}
    (TMP/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (TMP/'questions.json').write_text(json.dumps(allq,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
