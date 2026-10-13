from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parents[3]
TMP=ROOT/'tmp'/'pdfs'; EXTRA=TMP/'split_enhanced'; OUT=ROOT/'output'/'pdf'
sys.path.insert(0,str(TMP))
import build_book as b
from reportlab.platypus import PageBreak,Spacer,CondPageBreak,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader

class Volume(b.Book):
    def __init__(self,path,label):
        self.label=label
        super().__init__(path)
    def beforeDocument(self):
        super().beforeDocument()
        self.running=self.label
        self.canv.setSubject(self.label+' | 강화판 | 독립 학습 PDF')

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def topic(s):return re.sub(r'^\d+[.\s]+','',s)
def begin(label,subtitle,count,contents):
    b.story=[];b.seq=0
    b.story.extend([Spacer(1,46),b.p('Toeic RC','h1'),b.p(label,'h2'),Spacer(1,10)])
    b.para(subtitle)
    b.para(f'수록 문항 {count}개 | 문제·정답표·전체 해설 포함')
    b.story.append(Spacer(1,18))
    b.table([['학습 구성','이 파일에서 할 일']]+contents,[100,b.WIDTH-100],True)
    b.story.append(Spacer(1,12))
    b.para('총점 700점대에서 950점 이상을 목표로 하는 학습자를 위한 RC 교재입니다. RC 자체는 495점 만점이며, 이 파일은 해당 파트의 판단 능력을 기르는 독립 교재입니다.')
    b.para('강화판: 기존 학습 내용을 유지하면서 실제 풀이 예시·규칙의 경계·새 문제·오답 교정을 보강했습니다. 단어장과 암기용 단어 목록은 제외했습니다.')
    b.story.append(b.p('A4 세로 · 본문 10.4pt · 한글 글꼴 포함 · 파일별 목차와 페이지 번호','small'))
    b.story.append(PageBreak());b.heading('목차',1,False)
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('vTOC0',fontName='MalgunBold',fontSize=11,leading=16,textColor=b.NAVY,spaceBefore=6,spaceAfter=0,wordWrap='CJK'),ParagraphStyle('vTOC1',fontName='Malgun',fontSize=10,leading=14,leftIndent=9,spaceBefore=0,spaceAfter=0,wordWrap='CJK')]
    b.story.append(toc);b.story.append(PageBreak())
def usage(label,paragraphs):
    b.heading(label,0)
    b.heading('학습 순서와 근거 기록')
    for t in paragraphs:b.para(t)
    b.table([['단계','완료 기준'],['개념','규칙뿐 아니라 적용 조건과 예외를 설명한다.'],['예제','문장 성분 또는 문장 간 연결을 표시한다.'],['문제','해설을 가리고 정답과 근거를 고른다.'],['복습','오답 세 개를 제거한 이유까지 설명한다.']],[70,b.WIDTH-70],True)
    b.para('난도는 기본·중급·고급·실전 최상급으로 표기합니다. 문제 번호의 B는 강화판에서 추가한 문항을 뜻합니다. 정확한 근거를 확보한 뒤 제한 시간을 줄여 갑니다.')
def key(questions,label='정답표'):
    b.heading(label)
    vals=[f"{q['id']}  {q['answer']}" for q in questions]
    cols=5 if len(questions)>=100 else 4
    rows=[vals[i:i+cols]+['']*(cols-len(vals[i:i+cols])) for i in range(0,len(vals),cols)]
    b.table(rows,[b.WIDTH/cols]*cols)
def reviews(sections):
    for s in sections:
        b.heading(s['title'])
        for t in s['paragraphs']:b.para(t)
def finish(label,filename,questions,parts):
    for q in questions:b.validate_question(q)
    assert len({q['id'] for q in questions})==len(questions)
    path=OUT/filename
    doc=Volume(path,label);doc.multiBuild(b.story,maxPasses=5)
    reader=PdfReader(path)
    item=dict(label=label,file=str(path),pages=len(reader.pages),questions=len(questions),contents=parts,toc=doc.entries)
    stem='part5' if label=='Part 5' else 'part6' if label=='Part 6' else 'part7' if label=='Part 7' else 'mock'
    (EXTRA/(stem+'_questions.json')).write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{label}: {len(reader.pages)} pages, {len(questions)} questions',flush=True)
    return item

def part5(g,e):
    assert len(g['chapters'])==len(e['chapters'])==20
    qs=[]
    for c,x in zip(g['chapters'],e['chapters']):
        assert len(x['questions'])==2 and len(x['blocks'])==3
        qs.extend([x['questions'][0],*c['questions'],x['questions'][1]])
    assert len(qs)==80
    begin('Part 5','품사·문장 구조·문법의 경계와 복합 단서를 단계별로 훈련합니다.',80,[['핵심 개념','20단원·필수 규칙·문장 구조·비교와 예외'],['풀이 예시','단원마다 최소 대립 예문·단계별 판단·고득점 예외'],['난도별 연습','단원당 4문항, 총80문항'],['해설과 복습','정답표·선택지별 근거·구조 분석 복습']])
    usage('Part 5',['주어와 정동사, 목적어·보어, 수식어를 먼저 구분합니다. 빈칸의 기능을 정한 뒤 규칙을 적용하고, 형태만으로 답이 하나로 정해지지 않으면 목적어·조건·문맥을 확인합니다.','각 단원에는 기존 중급·고급 문제에 새 기본·실전 최상급 문제를 더했습니다. 문제를 모두 푼 뒤 파일 뒤의 정답표와 해설을 확인합니다. 예제의 해설과 실제 연습문제 해설을 구분하여 답을 먼저 보지 않고 연습할 수 있게 구성했습니다.'])
    for t in g['intro']:b.para(t)
    for i,(c,x) in enumerate(zip(g['chapters'],e['chapters']),1):
        b.story.append(CondPageBreak(180));b.heading(f'5.{i:02} {topic(c["title"])}')
        for s in c['sections']:b.block(s['label'],s['text'])
        for s in x['blocks']:b.block(s['label'],s['text'])
        group=[x['questions'][0],*c['questions'],x['questions'][1]]
        lead=b.p('난도별 연습 | 해설은 파일 뒤에서 확인','h3')
        b.question(group[0],True)
        first=b.story.pop()
        b.story.append(KeepTogether([lead,*first._content]))
        for q in group[1:]:b.question(q,True)
    b.story.append(PageBreak());key(qs)
    b.story.append(PageBreak());b.heading('Part 5 전체 상세 해설')
    for i,(c,x) in enumerate(zip(g['chapters'],e['chapters']),1):
        b.story.append(CondPageBreak(150));b.story.append(b.p(f'5.{i:02} {topic(c["title"])}','h3'))
        for q in [x['questions'][0],*c['questions'],x['questions'][1]]:b.explanation(q)
    b.story.append(PageBreak());b.heading('구조 분석과 시간 훈련')
    reviews(e['review_sections'])
    b.table([['문항','빈칸의 기능 / 핵심 성분','놓친 단서 / 다음 행동'],['________','________________________','________________________'],['________','________________________','________________________'],['________','________________________','________________________']],[75,200,b.WIDTH-275],True)
    return finish('Part 5','Toeic RC - Part 5.pdf',qs,dict(chapters=20,worked_blocks=60,original_questions=40,new_questions=40))

def part6(s,e):
    sets=s['sets']+e['sets'];qs=[q for x in sets for q in x['questions']]
    assert len(e['sets'])==8 and len(qs)==48
    for x in sets:
        assert len(x['questions'])==4
        text=' '.join(d['text'] for d in x['documents'])
        for q in x['questions']:assert '['+q['id']+']' in text
    begin('Part 6','문법 자리를 정하고, 앞뒤 문맥과 지시어를 연결해 빈칸을 완성합니다.',48,[['핵심 전략','8가지 문맥 판단과 장르별 접근'],['풀이 사례','유형별 영문 사례·오답의 성립 조건·판단 순서'],['지문 훈련','기존4세트+새8세트, 총12세트·48문항'],['전체 해설','각 문항의 구조·문맥·오답3개·일반화 규칙']])
    usage('Part 6',['지문 목적→빈칸 문장 구조→앞뒤 문장의 시간과 지칭 대상→문장 삽입의 양쪽 연결 순서로 판단합니다. 문장 삽입은 앞 문장에만 어울리는 답을 경계합니다.','핵심 전략을 읽은 뒤 강화 사례에서 단서를 먼저 표시합니다.12개 지문을 풀고 정답표·해설을 확인합니다. 처음에는 근거 정확성을 우선하고, 이후에는 개인 기록을 바탕으로 지문당 목표시간을 정합니다.'])
    for t in s['intro']:b.para(t)
    for i,x in enumerate(s['sections'],1):
        b.heading(f'6.{i:02} {topic(x["title"])}')
        for t in x['paragraphs']:
            if i==8:b.story.append(KeepTogether([b.p(t)]))
            else:b.para(t)
    b.story.append(CondPageBreak(170));b.heading('유형별 판단을 재현하는 강화 사례')
    for s in e['sections']:
        b.heading(s['title'])
        for t in s['paragraphs']:b.story.append(KeepTogether([b.p(t)]))
    b.story.append(CondPageBreak(170));b.heading('연습 전: 네 빈칸의 근거를 기록하는 방법')
    b.para('아래12세트는 먼저 글의 목적을 확인하고 네 빈칸을 푼 뒤 문단을 다시 읽는 순서로 연습합니다. 각 빈칸 옆에 G(문법), C(문맥), I(문장 삽입)를 적어 어떤 단서로 결정했는지 분리합니다. 두 범주가 함께 필요하면 둘 다 표시합니다.')
    b.para('대명사·시제는 문장 내부 형태와 앞뒤 내용이 모두 맞는지 검사합니다. 문장 삽입은 “앞에서 해결할 내용”과 “뒤에서 되받는 대상”을 각각 한 줄로 적습니다. 정답을 고른 뒤에는 가장 그럴듯했던 오답이 어느 단서를 설명하지 못하는지 기록합니다.')
    b.table([['빈칸','문법 / 문맥 / 삽입','직접 단서와 제거 이유'],['1','________________','________________________'],['2','________________','________________________'],['3','________________','________________________'],['4','________________','________________________']],[60,140,b.WIDTH-200],True)
    b.story.append(PageBreak());b.heading('Part 6 지문별 연습 | 12세트')
    for x in sets:b.passage_set(x,True)
    b.story.append(PageBreak());key(qs)
    b.story.append(PageBreak());b.heading('Part 6 전체 상세 해설')
    for x in sets:
        b.story.append(CondPageBreak(150));b.story.append(b.p(x['title'],'h3'))
        for q in x['questions']:b.explanation(q)
    b.story.append(PageBreak());b.heading('문맥 연결과 오답 교정')
    reviews(e['review_sections'])
    b.table([['문항','앞→빈칸→뒤 연결','오답이 가능해지는 조건'],['________','________________________','________________________'],['________','________________________','________________________'],['________','________________________','________________________']],[75,200,b.WIDTH-275],True)
    return finish('Part 6','Toeic RC - Part 6.pdf',qs,dict(core_sections=8,worked_cases=8,sets=12,original_questions=16,new_questions=32))

def part7(r,e):
    sets=r['training']+e['sets'];qs=[q for x in sets for q in x['questions']]
    assert len(e['sets'])==6 and len(qs)==50
    begin('Part 7','문장 구조를 빠르게 복구하고, 지문과 선택지를 정확한 근거로 연결합니다.',50,[['핵심 독해','10가지 구조·논리·문제 유형별 전략'],['판단 사례','유형별 영문 사례·근거 범위·함정 교정'],['지문 연습','총12세트, 단일·이중·삼중 지문50문항'],['근거 해설','문서명·영문 근거·오답 오류·실전 판단 순서']])
    usage('Part 7',['목적·추론·삽입 문제는 글의 흐름을 읽고, 세부 정보는 질문의 인물·날짜·장소를 찾은 뒤 주변 조건을 확인합니다. 복수 지문은 문서의 기능과 동일 대상을 연결합니다.','새 지문은 조건·시점·역할을 동시에 비교하도록 만들었습니다. 어려운 단어를 외우는 대신 정확한 근거를 찾고, 보기의 결론과 이유가 모두 성립하는지 확인합니다. 읽기 후 정답 근거를 문서 제목과 짧은 표현으로 기록합니다.'])
    for t in r['intro']:b.para(t)
    for i,x in enumerate(r['sections'],1):
        b.heading(f'7.{i:02} {topic(x["title"])}')
        for t in x['paragraphs']:
            if i==10:b.story.append(KeepTogether([b.p(t)]))
            else:b.para(t)
    b.story.append(CondPageBreak(170));b.heading('근거 판단을 재현하는 강화 사례')
    reviews(e['sections'])
    b.story.append(PageBreak());b.heading('Part 7 단일·복수 지문 연습 | 12세트')
    for x in sets:
        if len(x['documents'])>1:b.story.append(PageBreak())
        b.passage_set(x,True)
    b.story.append(PageBreak());key(qs)
    b.story.append(PageBreak());b.heading('Part 7 전체 상세 해설')
    for x in sets:
        b.story.append(CondPageBreak(150));b.story.append(b.p(x['title'],'h3'))
        for q in x['questions']:b.explanation(q)
    b.story.append(PageBreak());b.heading('독해 근거와 제한 시간 훈련')
    reviews(e['review_sections'])
    b.table([['문항','문서명 / 직접 근거','보기와 다른 주체·조건·시점'],['________','________________________','________________________'],['________','________________________','________________________'],['________','________________________','________________________']],[75,200,b.WIDTH-275],True)
    return finish('Part 7','Toeic RC - Part 7.pdf',qs,dict(core_sections=10,worked_cases=10,sets=12,original_questions=22,new_questions=28))

def mock(s,r,e):
    multi=read(TMP/'content'/'part7_mock_multi.json')
    readsets=r['mock']+multi
    full=s['mock5']+[q for x in s['mock6'] for q in x['questions']]+[q for x in readsets for q in x['questions']]
    mini=e['grammar']+[q for x in e['sets'] for q in x['questions']]
    assert [q['id'] for q in full]==[str(n) for n in range(101,201)] and len(mini)==15
    begin('실전 모의고사','75분100문항 시험과 상세 해설, 시험 후 진단·15문항 보완 훈련을 담았습니다.',115,[['본시험','Part5 30문항·Part6 16문항·Part7 54문항'],['진행 기록','파트별 시간·100문항 답안 기록표'],['전체 해설','정답·문장 구조·문맥 근거·선택지별 오류'],['강화 콘텐츠','근거 확인율 진단·문항별 복습 경로·새15문항']])
    b.heading('실전 모의고사',0)
    b.heading('시험 안내와 시간 기록')
    b.para('본시험은75분100문항이며 번호는101-200입니다. 뒤의 M-B01-M-B15는 채점 후에 푸는 별도의 보완 훈련입니다. 본시험 시간과 점수에 보완 훈련을 합치지 않습니다. 각 문제에서 가장 적절한 답 하나를 고릅니다.')
    b.para('RC 공식 형식은100문항75분, Part5 30문항·Part6 16문항·Part7 54문항입니다. 모의고사는 단일 지문10세트29문항, 복수 지문5세트25문항으로 구성했습니다. 창작 학습자료이며 공식 환산점수는 제공하지 않습니다.')
    b.story.append(b.rich('<link href="https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf" color="#17345a"><u>시험 형식 참고: ETS TOEIC Listening &amp; Reading Score User Guide</u></link>','small'))
    b.table([['시작 시각','Part5 종료','Part6 종료','전체 종료'],['____________','____________','____________','____________']],[b.WIDTH/4]*4,True)
    b.table([['구간','훈련용 배분','누적 경과'],['Part5','10분','10분'],['Part6','8분','18분'],['Part7','54분','72분'],['답안·표시 검토','3분','75분']],[150,130,b.WIDTH-280],True)
    b.para('시간 배분은 훈련용 제안입니다. 자신의 정확도와 실제 소요 시간을 기록해 조정합니다. E는 근거 확인, G는 근거 불완전·추측, T는 시간 때문에 처리하지 못한 문항으로 표시합니다.')
    b.story.append(PageBreak());b.heading('본시험 답안 기록표 | 101-200')
    b.table([[f'{n} _____' for n in range(k,k+5)] for k in range(101,201,5)],[b.WIDTH/5]*5)
    b.story.append(PageBreak());b.heading('본시험 Part 5 | 101-130')
    b.para('Directions: Choose the best word or phrase to complete each sentence.')
    for q in s['mock5']:b.question(q)
    b.story.append(PageBreak());b.heading('본시험 Part 6 | 131-146')
    b.para('Directions: Read each text and choose the best word, phrase, or sentence for each blank.')
    for x in s['mock6']:b.passage_set(x)
    b.story.append(PageBreak());b.heading('본시험 Part 7 | 147-200')
    b.para('Directions: Read each text or set of texts and choose the best answer to each question.')
    for x in readsets:b.passage_set(x)
    b.story.append(PageBreak());key(full,'본시험 정답표')
    b.para('정답 수: Part5 ___/30 · Part6 ___/16 · Part7 ___/54 · 전체 ___/100')
    b.para('E 정답 ___개 · G 정답 ___개 · T 문항 ___개 · 무제한 재풀이 정답 ___개')
    for title,qs in [('본시험 Part 5 상세 해설',full[:30]),('본시험 Part 6 상세 해설',full[30:46]),('본시험 Part 7 상세 해설',full[46:])]:
        b.story.append(PageBreak());b.heading(title)
        for q in qs:b.explanation(q)
    b.story.append(PageBreak());b.heading('시험 후 진단과 근거 교정')
    reviews(e['sections'])
    b.heading('파트별 재훈련 경로')
    b.table([['오류','다음에 펼칠 파일과 단원'],['품사·주어·정동사','Part5 5.01-5.05, 5.10-5.11'],['시제·태·준동사','Part5 5.06-5.09, 5.17'],['절·관계사·병렬','Part5 5.12-5.15'],['비교·한정사·복합 단서','Part5 5.16, 5.19-5.20'],['문맥 시제·지칭·연결','Part6 6.02-6.05 및 해당 강화 사례'],['문장 삽입','Part6 6.01·6.07, Part7 7.07'],['주체·조건·추론','Part7 7.04-7.06'],['복수 지문 갱신·연계','Part7 7.08 및 새 이중·삼중 지문']],[150,b.WIDTH-150],True)
    b.heading('문항별 진단 기록표')
    for tag,qs in [('Part5',full[:30]),('Part6',full[30:46]),('Part7',full[46:])]:
        b.story.append(b.p(tag,'h3'))
        rows=[['문항','판단 유형','내가 놓친 단서 / 재훈련 번호']]
        rows += [[q['id'],q['type'],'________________________________'] for q in qs]
        b.table(rows,[55,170,b.WIDTH-225],True)
    b.story.append(PageBreak());b.heading('강화 보완 훈련 | 15문항')
    b.para('본시험 채점과 원인 분류를 마친 뒤 풉니다. 먼저 시간 제한 없이 근거를 확인하고, 이후 자신의 목표시간에 맞춰 재훈련합니다. 별도 번호 M-B01-M-B15를 사용합니다.')
    b.story.append(b.p('문장 완성 | M-B01-M-B05','h3'))
    for q in e['grammar']:b.question(q,True)
    for x in e['sets']:b.passage_set(x,True)
    b.story.append(PageBreak());key(mini,'보완 훈련 정답표')
    b.story.append(PageBreak());b.heading('보완 훈련 전체 상세 해설')
    for q in mini:b.explanation(q)
    b.story.append(PageBreak());b.heading('복습 기록과 다음 회차 점검')
    b.table([['번호','내 답 / 정답','원인','다음 행동'],['________','___________','________','________________________'],['________','___________','________','________________________'],['________','___________','________','________________________'],['________','___________','________','________________________']],[60,90,90,b.WIDTH-240],True)
    b.block('다음 회차 전 완료 기준','정답 근거와 오답3개의 오류를 말로 설명한다. 조건을 바꾸면 어떤 오답이 가능해지는지 설명한다. 각 파트 파일의 새로운 지문에서도 같은 규칙을 적용한다. 같은 시험의 답 기억으로 얻은 속도 향상과 처음 보는 자료에서의 판단 속도를 구분한다.')
    return finish('실전 모의고사','Toeic RC - 실전 모의고사.pdf',full+mini,dict(full_mock_questions=100,full_mock_minutes=75,supplemental_questions=15,diagnostic_sections=6))

def main():
    OUT.mkdir(exist_ok=True)
    g=read(TMP/'content'/'part5.json');s=read(TMP/'content'/'part6_mock5.json');r=read(TMP/'content'/'part7.json')
    builders={'part5':lambda:part5(g,read(EXTRA/'part5_extra.json')),'part6':lambda:part6(s['part6'],read(EXTRA/'part6_extra.json')),'part7':lambda:part7(r,read(EXTRA/'part7_extra.json')),'mock':lambda:mock(s,r,read(EXTRA/'mock_extra.json'))}
    selected=sys.argv[1:] or list(builders)
    records=read(EXTRA/'manifest.json')['files'] if (EXTRA/'manifest.json').exists() else []
    for name in selected:
        item=builders[name]();records=[x for x in records if x['label']!=item['label']]+[item]
    order={'Part 5':0,'Part 6':1,'Part 7':2,'실전 모의고사':3}
    records.sort(key=lambda x:order[x['label']])
    manifest=dict(files=records,total_pages=sum(x['pages'] for x in records),total_questions=sum(x['questions'] for x in records),new_questions=115)
    if len(records)==4:assert manifest['total_questions']==293
    (EXTRA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(records)} independent enhanced PDFs ready',flush=True)
if __name__=='__main__':main()
