from pathlib import Path
import collections
import html
import json
import re
import unicodedata

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parents[2]/'output'/'pdf'
OUT.mkdir(parents=True,exist_ok=True)
FILES = {
 'notes': OUT/'컴퓨터_네트워킹_1-6장_학습노트.pdf',
 'cheat': OUT/'컴퓨터_네트워킹_1-6장_치트시트.pdf',
 'audit': OUT/'컴퓨터_네트워킹_1-6장_근거검증_인쇄점검.pdf'
}
W,H = A4
M = 21*mm
WIDTH = W-2*M
TOP = 31*mm
BOTTOM = 28*mm
BODY_H = H-TOP-BOTTOM
INK = colors.HexColor('#171717')
GRAY = colors.HexColor('#555555')
RULE = colors.HexColor('#8c8c8c')
PALE = colors.HexColor('#f3f3f3')
FONT_ROOT = ROOT.parent
pdfmetrics.registerFont(TTFont('Nanum',str(FONT_ROOT/'NanumGothic-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NanumBold',str(FONT_ROOT/'NanumGothic-Bold.ttf')))
pdfmetrics.registerFont(TTFont('MathSymbols','C:/Windows/Fonts/seguisym.ttf'))
pdfmetrics.registerFontFamily('Nanum',normal='Nanum',bold='NanumBold',italic='Nanum',boldItalic='NanumBold')

ST = {
 'body': ParagraphStyle('body',fontName='Nanum',fontSize=10.2,leading=15.3,textColor=INK,spaceAfter=6,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'small': ParagraphStyle('small',fontName='Nanum',fontSize=9,leading=13.5,textColor=GRAY,spaceAfter=5,wordWrap='CJK'),
 'h0': ParagraphStyle('h0',fontName='NanumBold',fontSize=23,leading=33,textColor=INK,spaceAfter=16,keepWithNext=True,wordWrap='CJK'),
 'h1': ParagraphStyle('h1',fontName='NanumBold',fontSize=15,leading=23,textColor=INK,spaceBefore=13,spaceAfter=8,keepWithNext=True,wordWrap='CJK'),
 'h2': ParagraphStyle('h2',fontName='NanumBold',fontSize=11.5,leading=17.5,textColor=INK,spaceBefore=10,spaceAfter=5,keepWithNext=True,wordWrap='CJK'),
 'cell': ParagraphStyle('cell',fontName='Nanum',fontSize=10,leading=15,textColor=INK,wordWrap='CJK',spaceAfter=0,allowWidows=0,allowOrphans=0),
 'cheat': ParagraphStyle('cheat',fontName='Nanum',fontSize=10,leading=15,textColor=INK,spaceAfter=4,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'cheathead': ParagraphStyle('cheathead',fontName='NanumBold',fontSize=11,leading=16.5,textColor=INK,spaceBefore=7,spaceAfter=4,keepWithNext=True,wordWrap='CJK'),
 'center': ParagraphStyle('center',fontName='NanumBold',fontSize=16,leading=24,alignment=TA_CENTER,textColor=INK,spaceAfter=10,wordWrap='CJK'),
}

CHAPTER_RANGES = {1:(1,74,9,82),2:(75,169,83,177),3:(171,279,178,286),4:(281,340,287,346),5:(341,402,347,408),6:(403,475,409,481)}
REGISTRY = []
INDEX = {}
COUNTS = collections.Counter()
CONTENT_CHARS = set()
BOLD_PATTERN = None
ALL_LAYOUT = {}

def norm(value):
    text=unicodedata.normalize('NFC',str(value)).replace('\u2011','-').replace('\u00a0',' ')
    subs='₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ'
    plain='0123456789+-=()aehijklmnoprstuvx'
    trans=str.maketrans(subs,plain)
    text=re.sub('['+re.escape(subs)+']+',lambda m:'_{'+m.group().translate(trans)+'}',text)
    sup={'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁺':'+','⁻':'-','⁼':'=','⁽':'(','⁾':')','ⁿ':'n','ⁱ':'i','ʳ':'r','ᴺ':'N'}
    return re.sub('['+re.escape(''.join(sup))+']+',lambda m:'^{'+''.join(sup[c] for c in m.group())+'}',text)

def esc(value):
    value=norm(value)
    CONTENT_CHARS.update(value)
    cmap=pdfmetrics.getFont('Nanum').face.charToGlyph
    mathmap=pdfmetrics.getFont('MathSymbols').face.charToGlyph
    result=[]
    for ch in value:
        if ch=='\n':
            result.append('<br/>')
        elif ord(ch) not in cmap and ord(ch) in mathmap:
            result.append(f'<font name="MathSymbols">{html.escape(ch)}</font>')
        else:
            result.append(html.escape(ch))
    return ''.join(result)

def para(value,style='body',rich=False):
    f=Paragraph(value if rich else esc(value),ST[style])
    f.audit_kind='text'
    return f

def math_markup(value):
    value=str(value).replace('d_종단간 지연','d_{종단간 지연}').replace('d_end-end','d_{end-end}')
    value=re.sub(r'_\(([^()]+)\)',r'_{\1}',value)
    text=esc(value)
    text=text.replace('client_isn','client@@ISN@@').replace('server_isn','server@@ISN@@')
    text=re.sub(r'_\{([^{}]+)\}',r'<sub>\1</sub>',text)
    text=re.sub(r'_([A-Za-z0-9]+)',r'<sub>\1</sub>',text)
    text=re.sub(r'\^\{([^{}]+)\}',r'<super>\1</super>',text)
    text=re.sub(r'\^([A-Za-z0-9]+)',r'<super>\1</super>',text)
    return text.replace('client@@ISN@@','client_isn').replace('server@@ISN@@','server_isn')

def body_markup(value):
    value=norm(value)
    if BOLD_PATTERN is None:
        return math_markup(value)
    result=[]
    start=0
    for match in BOLD_PATTERN.finditer(value):
        result.append(math_markup(value[start:match.start()]))
        result.append('<b>'+math_markup(match.group())+'</b>')
        start=match.end()
    result.append(math_markup(value[start:]))
    return ''.join(result)

def page_text(pages):
    values=sorted(set(int(v) for v in pages))
    groups=[]
    for v in values:
        if groups and v==groups[-1][-1]+1:
            groups[-1].append(v)
        else:
            groups.append([v])
    return ', '.join(str(g[0]) if len(g)==1 else f'{g[0]}-{g[-1]}' for g in groups)

def ref(f):
    section=str(f['section']).removesuffix('절')
    suffix='' if '장' in section else '절'
    return f'({section}{suffix}, p.{page_text(f["pages"])})'

def add_fact(f,chapter,kind='본문'):
    assert isinstance(f,dict) and f.get('text') and f.get('section') and f.get('pages') and f.get('evidence'),(chapter,kind,f)
    assert f['section'].split('.')[0]==str(chapter) or f['section'].startswith(f'{chapter}장'),(chapter,f)
    lo,hi,_,_=CHAPTER_RANGES[chapter]
    assert all(lo<=int(p)<=hi for p in f['pages']),(chapter,f)
    key=(norm(f['text']),str(f['section']),tuple(sorted(set(f['pages']))))
    if key not in INDEX:
        COUNTS[chapter]+=1
        ident=f'{chapter}-{COUNTS[chapter]:03d}'
        record={**f,'id':ident,'chapter':chapter,'kind':kind}
        INDEX[key]=record
        REGISTRY.append(record)
    return INDEX[key]

def fact_html(f,chapter,kind='본문',number=None,bold_term=None):
    r=add_fact(f,chapter,kind)
    body=body_markup(f['text'])
    if bold_term:
        body=f'<b>{esc(bold_term)}</b>: '+body
    if number is not None:
        body=f'<b>{number}.</b> '+body
    return f'{body} <font color="#555555">[{r["id"]}] {esc(ref(f))}</font>'

def fact_para(f,ch,kind='본문',style='body',**kwargs):
    return para(fact_html(f,ch,kind,**kwargs),style,True)

def formula_fact(f):
    text=f'{f["label"]}: {f["expression"]}'
    if f.get('note'):
        text+='; '+f['note']
    return {'text':text,'section':f['section'],'pages':f['pages'],'evidence':f['evidence']}

def box(flows):
    tab=Table([[flows]],colWidths=[WIDTH],hAlign='LEFT',splitByRow=0)
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),.6,RULE),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    tab.audit_kind='box'
    return tab

def table(header,rows,widths,max_height=500,style='cell'):
    def make(part):
        data=[[para(f'<b>{esc(x)}</b>',style,True) for x in header]]+part
        t=Table(data,colWidths=widths,hAlign='LEFT',splitByRow=0)
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.45,RULE),('LINEBELOW',(0,0),(-1,0),.8,INK),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        t.audit_kind='table'
        return t
    result=[]
    chunk=[]
    for row in rows:
        cooked=[x if isinstance(x,Paragraph) else para(x,style) for x in row]
        trial=make(chunk+[cooked])
        h=trial.wrap(WIDTH,BODY_H)[1]
        if h>max_height and chunk:
            result.extend([make(chunk),Spacer(1,9)])
            chunk=[cooked]
        else:
            chunk.append(cooked)
        assert make(chunk).wrap(WIDTH,BODY_H)[1]<=BODY_H-30,('oversized table row',header)
    if chunk:
        result.extend([make(chunk),Spacer(1,9)])
    return result

class Document(BaseDocTemplate):
    def __init__(self,path,title,key):
        super().__init__(str(path),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=TOP,bottomMargin=BOTTOM,title=title,author='첨부 원문 기반 학습 노트',pageCompression=1,allowSplitting=1)
        self.doc_title=title
        self.key=key
        self.running=''
        self.positions=[]
        self.entries=[]
        self.addPageTemplates(PageTemplate('normal',[Frame(M,BOTTOM,WIDTH,BODY_H,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.draw_page))
    def beforeDocument(self):
        self.positions=[]
        self.entries=[]
        self.running=''
    def draw_page(self,c,doc):
        c.saveState()
        if self.page>1:
            c.setFont('Nanum',8.2)
            c.setFillColor(GRAY)
            c.drawString(M,H-23*mm,'컴퓨터 네트워킹 | 1-6장')
            c.drawRightString(W-M,H-23*mm,{'notes':'학습 노트','cheat':'장별 치트시트','audit':'근거 검증 · 인쇄 점검'}[self.key])
            c.setLineWidth(.45)
            c.setStrokeColor(RULE)
            c.line(M,H-26*mm,W-M,H-26*mm)
        c.setFont('Nanum',9)
        c.setFillColor(GRAY)
        c.drawCentredString(W/2,22*mm,str(doc.page))
        c.restoreState()
    def afterFlowable(self,f):
        kind=getattr(f,'audit_kind',None)
        if kind is None and isinstance(f,(Paragraph,Table,TableOfContents)):
            kind='text'
        if kind:
            self.positions.append({'page':self.page,'kind':kind,'bottom':float(self.frame._y),'height':float(getattr(f,'height',getattr(f,'_height',0))),'title':getattr(f,'heading_text','')})
        if hasattr(f,'toc_level'):
            self.canv.bookmarkPage(f.anchor)
            self.canv.addOutlineEntry(f.toc_text,f.anchor,level=f.toc_level,closed=True)
            self.notify('TOCEntry',(f.toc_level,f.toc_text,self.page,f.anchor))
            self.entries.append({'title':f.toc_text,'page':self.page,'level':f.toc_level})
            if f.toc_level==0:
                self.running=f.toc_text
    def save_layout(self):
        ALL_LAYOUT[self.key]={'entries':self.entries,'positions':self.positions,'page_count':self.page}

SEQ=0
def heading(text,level=1,toc=False,style_override=None):
    global SEQ
    f=Paragraph(esc(text),style_override) if style_override else para(text,'h0' if level==0 else 'h1' if level==1 else 'h2')
    f.audit_kind='heading'
    f.heading_text=text
    if toc:
        SEQ+=1
        f.toc_level=level
        f.toc_text=text
        f.anchor=f'anchor_{SEQ}'
    return f

def cover(title,subtitle,description):
    return [Spacer(1,57*mm),para('컴퓨터 네트워킹','h0'),para('하향식 접근','h0'),Spacer(1,10*mm),para(title,'h1'),para(subtitle,'body'),Spacer(1,10*mm),para(description,'body'),Spacer(1,12*mm),para('범위: 1-6장 · 첨부 인쇄 p.1-475 중 수록된 면','small'),para('A4 세로 · 여백 21mm 이상 · 나눔고딕 포함','small'),PageBreak()]

def study_cover():
    return [Spacer(1,57*mm),para('컴퓨터 네트워킹','h0'),para('하향식 접근','h0'),Spacer(1,10*mm),para('- 정리 및 요약','h1'),PageBreak()]

def make_notes(chapters):
    story=study_cover()
    story.append(heading('목차',1))
    toc=TableOfContents()
    toc.levelStyles=[ParagraphStyle('toc0',fontName='NanumBold',fontSize=11,leading=18,spaceBefore=9,wordWrap='CJK'),ParagraphStyle('toc1',fontName='Nanum',fontSize=10,leading=15,leftIndent=10,spaceBefore=2,wordWrap='CJK')]
    story.extend([toc,PageBreak(),heading('원문 범위와 출처 읽는 법',1)])
    story.append(para('본문 10.2pt, 줄간격 15.3pt로 편집했습니다. 학습 목표는 각 장 도입부에서 밝힌 학습 범위를 줄여 정리했습니다. 장 요약은 책의 요약 절을 기준으로 작성했습니다.'))
    source_rows=[]
    for c in chapters:
        lo,hi,a,b=CHAPTER_RANGES[c['chapter']]
        source_rows.append([f'{c["chapter"]}장',c['title'],f'p.{lo}-{hi}',f'{a}-{b}'])
    story.extend(table(['장','원문 장 제목','인쇄 쪽수','PDF 페이지'],source_rows,[35,WIDTH-195,80,80],max_height=450))
    story.append(para('첨부에는 인쇄 p.170·280에 해당하는 면이 없으며, 본문은 6장 인쇄 p.475에서 끝납니다. 누락된 두 면의 내용은 원문에서 확인 불가입니다.'))
    story.append(para('프로토콜 비교표의 빈칸은 해당 항목의 서술을 확인하지 못한 경우입니다. 별도 치트시트는 장마다 한 면으로 구성했으며, 별도 검증표에는 문장별 근거 위치와 인쇄 점검 결과를 실었습니다.'))
    for c in chapters:
        ch=c['chapter']
        lo,hi,a,b=CHAPTER_RANGES[ch]
        story.extend([PageBreak(),heading(f'{ch}장 {c["title"]}',0,True),para(f'원문 인쇄 p.{lo}-{hi} | PDF {a}-{b}페이지','small'),heading('학습 목표',1,True)])
        story.extend(fact_para(f,ch,'학습 목표') for f in c['learning'])
        story.append(heading('핵심 개념',1,True))
        for section in c['concepts']:
            story.append(heading(f'{section["section"]} {section["title"]}',2))
            if section['items']:
                story.extend([box([fact_para(f,ch,'핵심 개념') for f in section['items']]),Spacer(1,7)])
        for procedure_index,procedure in enumerate(c['procedures']):
            flows=([heading('동작 방식·절차',1,True)] if procedure_index==0 else [])+[heading(procedure['title'],2)]
            flows.extend(fact_para(f,ch,'동작 절차',number=i+1) for i,f in enumerate(procedure['steps']))
            # Keep the title and its entire short procedure in one unit.
            height=sum(f.wrap(WIDTH,BODY_H)[1]+f.getSpaceAfter()+f.getSpaceBefore() for f in flows)
            story.append(KeepTogether(flows)) if height<BODY_H-15 else story.extend(flows)
        story.append(heading('주요 프로토콜·표·수식',1,True))
        if c.get('formulas'):
            for f in c['formulas']:
                story.extend([box([fact_para(formula_fact(f),ch,'수식')]),Spacer(1,7)])
        if c.get('protocols'):
            rows=[]
            for protocol in c['protocols']:
                refs=[protocol.get(k) for k in ['role','features'] if protocol.get(k)]
                rows.append([para(f'<b>{esc(protocol["name"])}</b>','cell',True),[fact_para(f,ch,'프로토콜','cell') for f in refs]])
            # Lists of paragraphs are valid table cells and preserve wrapping.
            # Render protocol rows individually so their boxes never split.
            for name,items in rows:
                t=Table([[name,items]],colWidths=[80,WIDTH-80],hAlign='LEFT',splitByRow=0)
                t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.45,RULE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                t.audit_kind='table'
                story.extend([t,Spacer(1,7)])
        story.append(heading('핵심 용어 표',1,True))
        termrows=[[para(f'<b>{esc(t["term"])}</b>','cell',True),fact_para(t['definition'],ch,'핵심 용어','cell')] for t in c['terms']]
        story.extend(table(['용어','책에 나온 정의'],termrows,[108,WIDTH-108],max_height=490))
        story.append(heading('장 요약',1,True))
        story.extend(fact_para(f,ch,'장 요약') for f in c['summary'])
    story.extend([PageBreak(),heading('프로토콜·계층 비교표',0,True)])
    merged=collections.OrderedDict()
    for c in chapters:
        for p in c.get('protocols',[]):
            key=p['name'].lower()
            target=merged.setdefault(key,{'name':p['name'],'layer':[],'role':[],'features':[],'header':[]})
            for field in ['layer','role','features','header']:
                if p.get(field):
                    marker=(norm(p[field]['text']),p[field]['section'],tuple(p[field]['pages']))
                    if not any((norm(f['text']),f['section'],tuple(f['pages']))==marker for _,f in target[field]):
                        target[field].append((c['chapter'],p[field]))
    protocols=list(merged.values())
    def protocol_cell(p,key):
        return para('<br/>'.join(fact_html(f,ch,'프로토콜 비교') for ch,f in p[key]),'cell',True) if p[key] else ''
    for start in range(0,len(protocols),3):
        group=protocols[start:start+3]
        story.append(heading(f'계층·역할 비교 {start//3+1}',1))
        rows=[]
        for p in group:
            rows.append([para(f'<b>{esc(p["name"])}</b>','cell',True)]+[protocol_cell(p,k) for k in ['layer','role']])
        story.extend(table(['프로토콜','계층','역할'],rows,[78,106,WIDTH-184],max_height=500))
        story.append(heading(f'특징·헤더 필드 비교 {start//3+1}',1))
        rows=[]
        for p in group:
            rows.append([para(f'<b>{esc(p["name"])}</b>','cell',True)]+[protocol_cell(p,k) for k in ['features','header']])
        story.extend(table(['프로토콜','특징','헤더·프레임 필드'],rows,[78,(WIDTH-78)/2,(WIDTH-78)/2],max_height=530))
    story.extend([PageBreak(),heading('책 기반 복습 문제',0,True)])
    for c in chapters:
        ch=c['chapter']
        if ch>1:
            story.append(PageBreak())
        story.append(heading(f'{ch}장 복습 질문',1,True))
        for i,q in enumerate(c['review'],1):
            answer=q['answer']
            story.append(para(f'<b>{ch}-{i}.</b> {esc(q["question"])} <font color="#555555">{esc(ref(answer))}</font>','body',True))
        story.append(heading('정답과 원문 근거',1))
        for i,q in enumerate(c['review'],1):
            story.append(fact_para(q['answer'],ch,'복습 정답',number=i))
    doc=Document(FILES['notes'],'컴퓨터 네트워킹 하향식 접근 - 정리 및 요약','notes')
    doc.multiBuild(story)
    doc.save_layout()
    print(f'NOTES {doc.page} pages',flush=True)

def make_cheats(chapters):
    story=[]
    for c in chapters:
        ch=c['chapter']
        if story:
            story.append(PageBreak())
        if ch==1:
            title_style=ParagraphStyle('cheatbooktitle',parent=ST['h0'],fontSize=21,leading=29,spaceAfter=4)
            subtitle_style=ParagraphStyle('cheatbooksubtitle',parent=ST['cheathead'],fontSize=14,leading=21,spaceAfter=8)
            story.extend([Paragraph('컴퓨터 네트워킹',title_style),Paragraph('하향식 접근',title_style),Paragraph('- 확인 및 시험',subtitle_style),Spacer(1,7)])
        if ch==1:
            chapter_style=ParagraphStyle('cheatfirstchapter',parent=ST['h0'],fontSize=14,leading=21,spaceAfter=7)
            h=heading(f'{ch}장 {c["title"]}',0,True,style_override=chapter_style)
        else:
            h=heading(f'{ch}장 {c["title"]}',0,True)
            h.style=ParagraphStyle(f'cheattitle{ch}',parent=ST['h0'],fontSize=17,leading=25,spaceAfter=7)
        story.append(h)
        if ch!=1:
            story.append(para('1페이지 치트시트 | 핵심 정의 · 비교표 · 주요 수식','small'))
        story.append(para('핵심 정의','cheathead'))
        for item in c['cheat']['definitions']:
            story.append(fact_para(item['definition'],ch,'치트시트','cheat',bold_term=item['term']))
        rows=c['cheat'].get('comparison_rows',[])
        if rows:
            story.append(para(c['cheat']['comparison_title'],'cheathead'))
            header=c['cheat']['comparison_headers']
            cooked=[[fact_para(f,ch,'치트시트 비교','cell') if isinstance(f,dict) else para(str(f),'cell') for f in r] for r in rows]
            widths=[WIDTH/len(header)]*len(header)
            if len(header)==2:
                widths=[105,WIDTH-105]
            story.extend(table(header,cooked,widths,max_height=300))
        if c['cheat'].get('formulas'):
            story.append(para('주요 수식','cheathead'))
            for f in c['cheat']['formulas']:
                story.append(fact_para(formula_fact(f),ch,'치트시트 수식','cheat'))
    doc=Document(FILES['cheat'],'컴퓨터 네트워킹 하향식 접근 - 확인 및 시험','cheat')
    doc.multiBuild(story)
    doc.save_layout()
    assert doc.page==len(chapters),('cheatsheet must be exactly one page per chapter',doc.page,len(chapters))
    assert [x['page'] for x in doc.entries]==list(range(1,len(chapters)+1)),doc.entries
    print(f'CHEAT {doc.page} pages',flush=True)

def make_audit(chapters):
    story=cover('문장별 근거 검증 · 인쇄 점검','학습 노트와 치트시트의 출처 대조표','각 대괄호 번호는 학습 노트 또는 치트시트의 동일 문장을 가리킵니다. 책에서 직접 확인한 절·인쇄 쪽수를 함께 표기했습니다.')
    story.append(heading('검증 범위',1))
    story.append(para(f'중복 문장을 합쳐 {len(REGISTRY)}개 항목의 출처를 정리했습니다. 학습 목표, 핵심 개념, 절차, 수식, 용어 정의, 장 요약, 프로토콜 비교, 복습 정답, 치트시트를 포함합니다.'))
    story.append(para('복습 질문의 정답 근거는 질문 끝과 정답 문장 끝에 표시했습니다. 원문 근거가 확정되지 않은 설명을 보충하지 않았습니다. 원문 근거 문구와 확인한 페이지 목록은 편집용 대조 기록에 보관했습니다.'))
    quality_path=ROOT/'quality_report.json'
    report=json.loads(quality_path.read_text(encoding='utf-8')) if quality_path.exists() else None
    story.append(heading('인쇄 품질 점검',1))
    if report:
        rows=[]
        for key in ['notes','cheat','audit']:
            r=report['files'][key]
            rows.append([{'notes':'학습 노트','cheat':'치트시트','audit':'근거·점검표'}[key],f'1-{r["pages"]}',r['clipping_status'],r['font_status'],r['orphan_status'],r['table_status']])
        story.extend(table(['파일','점검 면','잘림·넘침','폰트','제목 고립','표 분리'],rows,[70,53,95,75,85,WIDTH-378],max_height=400))
        story.append(para('최종 페이지 이미지로 여백·줄바꿈·표·제목 배치를 직접 확인했습니다. 좌표 검사, 포함 글꼴 검사, 제목과 표의 배치 기록을 함께 대조했습니다.'))
    else:
        story.append(para('점검표는 최종 렌더링 검사 후 반영합니다.'))
    for c in chapters:
        ch=c['chapter']
        rows=[]
        for r in REGISTRY:
            if r['chapter']==ch:
                rows.append([r['id'],para(math_markup(r['text']),'cell',True),ref(r)])
        story.extend([PageBreak(),heading(f'{ch}장 문장별 근거',0,True)])
        story.extend(table(['번호','학습 노트·치트시트 문장','책의 근거 위치'],rows,[48,WIDTH-165,117],max_height=565))
    doc=Document(FILES['audit'],'컴퓨터 네트워킹 1-6장 문장별 근거 검증','audit')
    doc.multiBuild(story)
    doc.save_layout()
    print(f'AUDIT {doc.page} pages',flush=True)

def verify_glyphs():
    allowed={'\n','\r','\t'}
    failures=[]
    for name in ['Nanum','NanumBold']:
        cmap=pdfmetrics.getFont(name).face.charToGlyph
        mathmap=pdfmetrics.getFont('MathSymbols').face.charToGlyph
        missing=sorted(c for c in CONTENT_CHARS if c not in allowed and ord(c) not in cmap and ord(c) not in mathmap)
        if missing:
            failures.append({'font':name,'characters':missing})
    assert not failures,failures

def main():
    global BOLD_PATTERN
    import sys
    study_only='--study-only' in sys.argv
    if study_only and (ROOT/'layout.json').exists():
        ALL_LAYOUT.update(json.loads((ROOT/'layout.json').read_text(encoding='utf-8')))
    chapters=[json.loads((ROOT/f'chapter_{n}.json').read_text(encoding='utf-8-sig')) for n in range(1,7)]
    terms=set(t['term'].split('(')[0].strip() for c in chapters for t in c['terms'])
    patterns=[]
    for t in sorted(terms,key=len,reverse=True):
        if len(t)<2:
            continue
        patterns.append(r'(?<![A-Za-z0-9_])'+re.escape(t)+r'(?![A-Za-z0-9_])' if re.fullmatch(r'[A-Za-z0-9_ -]+',t) else re.escape(t))
    BOLD_PATTERN=re.compile('|'.join(patterns))
    for c in chapters:
        assert c['chapter'] in CHAPTER_RANGES
        assert len(c['learning']) and len(c['concepts']) and len(c['terms']) and len(c['summary'])
    make_notes(chapters)
    make_cheats(chapters)
    if not study_only:
        make_audit(chapters)
    verify_glyphs()
    (ROOT/'registry.json').write_text(json.dumps(REGISTRY,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'layout.json').write_text(json.dumps(ALL_LAYOUT,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'deliverables.json').write_text(json.dumps({k:str(v) for k,v in FILES.items()},ensure_ascii=False,indent=2),encoding='utf-8')
    print('BUILD COMPLETE',flush=True)

if __name__=='__main__':
    import sys
    if '--audit-only' in sys.argv:
        chapters=[json.loads((ROOT/f'chapter_{n}.json').read_text(encoding='utf-8-sig')) for n in range(1,7)]
        REGISTRY.extend(json.loads((ROOT/'registry.json').read_text(encoding='utf-8')))
        ALL_LAYOUT.update(json.loads((ROOT/'layout.json').read_text(encoding='utf-8')))
        make_audit(chapters)
        verify_glyphs()
        (ROOT/'layout.json').write_text(json.dumps(ALL_LAYOUT,ensure_ascii=False,indent=2),encoding='utf-8')
    else:
        main()
