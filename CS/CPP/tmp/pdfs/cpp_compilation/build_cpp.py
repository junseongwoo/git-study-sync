from pathlib import Path
import collections, html, json, re, unicodedata, sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,KeepTogether,Table,TableStyle
from reportlab.platypus.tableofcontents import TableOfContents

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[2]/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
FILES={k:OUT/f'C++_프로그래밍과_코딩테스트_{v}.pdf' for k,v in [('notes','정리_및_요약'),('cheat','확인_및_시험'),('audit','근거_및_인쇄점검표')]}
SOURCES=json.loads((ROOT/'source_registry.json').read_text('utf-8'))
W,H=A4; M=21*mm; TOP=31*mm; BOTTOM=28*mm; WIDTH=W-2*M; BODY_H=H-TOP-BOTTOM
INK=colors.HexColor('#191919'); GRAY=colors.HexColor('#535353'); RULE=colors.HexColor('#8a8a8a'); PALE=colors.HexColor('#f3f3f3')
for n,p in [('Nanum',ROOT.parent/'NanumGothic-Regular.ttf'),('NanumBold',ROOT.parent/'NanumGothic-Bold.ttf'),('MathSymbols',Path('C:/Windows/Fonts/seguisym.ttf')),('Mono',Path('C:/Windows/Fonts/consola.ttf'))]: pdfmetrics.registerFont(TTFont(n,str(p)))
pdfmetrics.registerFontFamily('Nanum',normal='Nanum',bold='NanumBold',italic='Nanum',boldItalic='NanumBold')
ST={
 'body':ParagraphStyle('body',fontName='Nanum',fontSize=10.2,leading=15.3,textColor=INK,spaceAfter=6,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'small':ParagraphStyle('small',fontName='Nanum',fontSize=9,leading=13.5,textColor=GRAY,spaceAfter=5,wordWrap='CJK'),
 'h0':ParagraphStyle('h0',fontName='NanumBold',fontSize=22,leading=31,textColor=INK,spaceAfter=13,wordWrap='CJK',keepWithNext=True),
 'h1':ParagraphStyle('h1',fontName='NanumBold',fontSize=14.5,leading=22,textColor=INK,spaceBefore=12,spaceAfter=7,wordWrap='CJK',keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='NanumBold',fontSize=11.4,leading=17.1,textColor=INK,spaceBefore=9,spaceAfter=5,wordWrap='CJK',keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='Nanum',fontSize=10,leading=15,textColor=INK,wordWrap='CJK',spaceAfter=0,allowWidows=0,allowOrphans=0),
 'cheat':ParagraphStyle('cheat',fontName='Nanum',fontSize=10,leading=15,textColor=INK,spaceAfter=4,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'ch':ParagraphStyle('ch',fontName='NanumBold',fontSize=11,leading=16.5,textColor=INK,spaceBefore=7,spaceAfter=4,wordWrap='CJK',keepWithNext=True),
 'code':ParagraphStyle('code',fontName='Mono',fontSize=9.5,leading=14.3,textColor=INK,wordWrap='CJK',spaceAfter=0),
}
REGISTRY=[]; INDEX={}; COUNTS=collections.Counter(); ALL_LAYOUT={}; CHARS=set(); BOLD_PATTERN=None; SEQ=0
def norm(x): return unicodedata.normalize('NFC',str(x)).replace('\u2011','-').replace('\xa0',' ').replace('\uf0e0','→')
def esc(x):
    s=norm(x); CHARS.update(s); cm=pdfmetrics.getFont('Nanum').face.charToGlyph; mmc=pdfmetrics.getFont('MathSymbols').face.charToGlyph
    return ''.join('<br/>' if c=='\n' else f'<font name="MathSymbols">{html.escape(c)}</font>' if ord(c) not in cm and ord(c) in mmc else html.escape(c) for c in s)
def body_html(x):
    s=norm(x)
    if not BOLD_PATTERN: return esc(s)
    out=[]; start=0
    for m in BOLD_PATTERN.finditer(s): out.extend([esc(s[start:m.start()]),'<b>'+esc(m.group())+'</b>']);start=m.end()
    out.append(esc(s[start:]));return ''.join(out)
def para(x,style='body',rich=False):
    p=Paragraph(x if rich else esc(x),ST[style]);p.audit_kind='text';return p
def pages_text(pages):
    groups=[]
    for p in sorted(set(int(n) for n in pages)):
        if groups and p==groups[-1][-1]+1: groups[-1].append(p)
        else: groups.append([p])
    return ','.join(str(g[0]) if len(g)==1 else f'{g[0]}-{g[-1]}' for g in groups)
def ref_text(refs,compact=False):
    result=[]
    for r in refs:
        s=r['source'];p=r['pages'];sec=r['section']
        if s=='B': loc='인쇄 p.'+pages_text([int(n)-5 for n in p])
        elif s=='K': loc='PDF p.'+pages_text(p)
        else: loc='슬라이드 '+pages_text(p)
        result.append(f'{s} {sec}, {loc}')
    return '('+'; '.join(result)+')'
def add_fact(f,u,kind='본문'):
    assert f.get('text') and f.get('refs') and f.get('evidence'),(u,kind,f)
    for r in f['refs']:
        assert r['source'] in SOURCES and r.get('section') and r.get('pages'),(u,r)
        assert all(1<=int(n)<=SOURCES[r['source']]['pdf_pages'] for n in r['pages']),(u,r)
    key=(norm(f['text']),json.dumps(f['refs'],ensure_ascii=False,sort_keys=True))
    if key not in INDEX:
        COUNTS[u]+=1;r={**f,'unit':u,'kind':kind,'id':f'U{u:02}-{COUNTS[u]:03}'};REGISTRY.append(r);INDEX[key]=r
    return INDEX[key]
def fact_html(f,u,kind='본문',number=None,term=None,compact=False):
    r=add_fact(f,u,kind);s=body_html(f['text'])
    if term: s='<b>'+esc(term)+'</b>: '+s
    if number is not None:s='<b>'+str(number)+'.</b> '+s
    return s+f' <font color="#555555">[{r["id"]}] {esc(ref_text(f["refs"],compact))}</font>'
def fp(f,u,kind='본문',style='body',**kwargs): return para(fact_html(f,u,kind,**kwargs),style,True)
def form_fact(f):
    supers=str.maketrans('0123456789n','⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ')
    expression=re.sub(r'\^([0-9]+|n)(?![A-Za-z0-9])',lambda m:m[1].translate(supers),f['expression'])
    return dict(text=f['label']+': '+expression+('; '+f['note'] if f.get('note') else ''),refs=f['refs'],evidence=f['evidence'])
def code_fact(c):return dict(text=c['label']+' (원문 코드 발췌)\n'+c['code'],refs=c['refs'],evidence=c['evidence'])
def heading(s,level=1,toc=False,style=None):
    global SEQ
    p=Paragraph(esc(s),style) if style else para(s,'h0' if level==0 else 'h1' if level==1 else 'h2');p.audit_kind='heading';p.heading_text=s
    if toc: SEQ+=1;p.toc_level=0;p.toc_text=s;p.anchor='a'+str(SEQ)
    return p
def box(flows):
    t=Table([[flows]],colWidths=[WIDTH],hAlign='LEFT',splitByRow=0);t.audit_kind='box'
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),.6,RULE),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));return t
def table(header,rows,widths=None,max_height=500):
    widths=widths or [WIDTH/len(header)]*len(header)
    def make(part):
        data=[[para('<b>'+esc(s)+'</b>','cell',True) for s in header]]+part
        t=Table(data,colWidths=widths,hAlign='LEFT',splitByRow=0);t.audit_kind='table'
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.45,RULE),('LINEBELOW',(0,0),(-1,0),.8,INK),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));return t
    out=[];chunk=[]
    for row in rows:
        cooked=[x if isinstance(x,(Paragraph,list)) else para(x,'cell') for x in row]
        if make(chunk+[cooked]).wrap(WIDTH,BODY_H)[1]>max_height and chunk:out.extend([make(chunk),Spacer(1,8)]);chunk=[]
        chunk.append(cooked)
        assert make(chunk).wrap(WIDTH,BODY_H)[1]<BODY_H-20,('oversize table',header)
    if chunk:out.extend([make(chunk),Spacer(1,8)])
    return out
def comparison(comp,u,compact=False):
    rows=[[fp(f,u,'비교표','cell',compact=compact) if isinstance(f,dict) else para(str(f),'cell') for f in row] for row in comp['rows']]
    widths=[WIDTH/len(comp['headers'])]*len(comp['headers'])
    if len(widths)==2:widths=[112,WIDTH-112]
    return table(comp['headers'],rows,widths,max_height=490)
def code_block(c,u,compact=False):
    r=add_fact(code_fact(c),u,'원문 코드'); flows=[para('<b>'+esc(c['label'])+'</b> (원문 발췌)','small',True)]
    for line in c['code'].expandtabs(4).splitlines():
        out=[]
        for ch in line:
            CHARS.add(ch);t=html.escape(ch)
            out.append('&#160;' if ch==' ' else f'<font name="Nanum">{t}</font>' if ord(ch)>127 else t)
        flows.append(para(''.join(out) or '&#160;','code',True))
    flows.append(para(f'[{r["id"]}] '+ref_text(c['refs'],compact),'small'))
    if c.get('note'):flows.append(fp(c['note'],u,'코드 주석','cheat' if compact else 'body',compact=compact))
    return box(flows)
class Document(BaseDocTemplate):
    def __init__(self,path,title,key):
        super().__init__(str(path),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=TOP,bottomMargin=BOTTOM,title=title,author='첨부 원문 기반 학습 노트',pageCompression=1,allowSplitting=1)
        self.key=key;self.positions=[];self.entries=[]
        self.addPageTemplates(PageTemplate('normal',[Frame(M,BOTTOM,WIDTH,BODY_H,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.draw_page))
    def beforeDocument(self):self.positions=[];self.entries=[]
    def draw_page(self,c,doc):
        c.saveState();c.setFillColor(GRAY)
        if self.page>1:
            c.setFont('Nanum',8.2);c.drawString(M,H-23*mm,'C++ 프로그래밍과 코딩 테스트');c.drawRightString(W-M,H-23*mm,{'notes':'정리 및 요약','cheat':'확인 및 시험','audit':'문장별 근거 · 인쇄 점검'}[self.key]);c.setLineWidth(.45);c.setStrokeColor(RULE);c.line(M,H-26*mm,W-M,H-26*mm)
        c.setFont('Nanum',9);c.drawCentredString(W/2,22*mm,str(self.page));c.restoreState()
    def afterFlowable(self,f):
        kind=getattr(f,'audit_kind',None)
        if kind is None and isinstance(f,(Paragraph,Table,TableOfContents)):kind='text'
        if kind:self.positions.append(dict(page=self.page,kind=kind,bottom=float(self.frame._y),height=float(getattr(f,'height',getattr(f,'_height',0))),title=getattr(f,'heading_text','')))
        if hasattr(f,'toc_level'):
            self.canv.bookmarkPage(f.anchor);self.canv.addOutlineEntry(f.toc_text,f.anchor,level=0,closed=True);self.notify('TOCEntry',(0,f.toc_text,self.page,f.anchor));self.entries.append(dict(title=f.toc_text,page=self.page,level=0))
    def save_layout(self):ALL_LAYOUT[self.key]=dict(entries=self.entries,positions=self.positions,page_count=self.page)
def scope_text(u):
    return ' | '.join(s['source']+' PDF '+pages_text(range(s['start'],s['end']+1)) for s in u['scope'])
def cover(subtitle):return [Spacer(1,57*mm),para('C++ 프로그래밍','h0'),para('코딩 테스트','h0'),Spacer(1,10*mm),para('- '+subtitle,'h1'),PageBreak()]
def make_notes(units):
    story=cover('정리 및 요약');story.append(heading('목차'))
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Nanum',fontSize=10.2,leading=15.3,spaceBefore=5,wordWrap='CJK')];story.extend([toc,PageBreak(),heading('원문 범위와 출처 읽는 법',0,True)])
    for text in [
      '첨부한 C++ 책 2개와 강의 자료 13개만을 사용했습니다. 주제가 겹치는 내용은 25개 통합 단원으로 묶었습니다. 통합 단원 번호는 편집 번호이며 원문의 장 번호와 다릅니다.',
      '각 항목 끝에는 [문장 번호]와 원본 파일 코드·절·쪽수를 표시했습니다. B는 책의 인쇄 쪽수이며 원본 PDF 면 번호에서 5를 뺀 값입니다. K는 PDF 면 번호, L로 시작하는 코드는 강의 슬라이드 번호입니다. 별도 근거 검증표의 같은 번호로 문장을 찾을 수 있습니다.',
      '다루는 내용은 원문 도입부와 본문의 학습 범위입니다. 원문에 요약 절이 있는 경우 이를 우선했으며, 본문을 재압축한 단원은 편집 요약으로 표시했습니다. 코드와 수식은 원문 발췌이며, 책에 없는 예시나 보충 설명을 덧붙이지 않았습니다.',
      'K는 목차부터 시작하는 스캔 자료입니다. 책의 표지·서지 정보는 원문에서 확인 불가이며, 마지막 PDF 530면은 찾아보기 첫 면입니다. 찾아보기의 나머지 면은 첨부에서 확인 불가입니다. 부록 A.2.2의 제목·도입 일부도 수록 면 사이에서 확인 불가이므로 확인되는 풀이만 정리했습니다. 본문·부록 중 수록된 면만 사용했습니다. (K PDF p.444-446, 530)',
      '별도 「확인 및 시험」은 단원마다 한 페이지입니다. 출처는 파일 코드와 절·쪽수로 표시하며, 같은 문장 번호의 근거 검증표에서도 확인할 수 있습니다. 자세한 복습 질문과 정답 근거는 이 노트 뒤에 있습니다.'
    ]:story.append(para(text))
    story.append(heading('원본 파일 코드',1))
    rows=[[s['id'],s['filename'],str(s['pdf_pages'])] for s in SOURCES.values()]
    story.extend(table(['코드','첨부 파일명','총 PDF 면'],rows,[47,WIDTH-110,63],max_height=550))
    story.append(heading('통합 단원과 원문 범위',1))
    rows=[[f'{u["unit"]:02}',u['title'],scope_text(u)] for u in units]
    story.extend(table(['단원','제목','원본 PDF 면 범위'],rows,[38,WIDTH*.44,WIDTH*.56-38],max_height=530))
    for u in units:
        n=u['unit'];story.extend([PageBreak(),heading(f'{n:02} {u["title"]}',0,True),para(scope_text(u),'small')])
        if n==25:
            story.extend([heading('첨부 수록 범위 확인',2),para('K PDF444-446에서 인쇄 쪽수는 455쪽에서 459쪽으로 이어집니다. PDF445 하단 쪽수는 왼쪽이 잘려 전체 숫자를 확인할 수 없습니다. A.2.2 제목·도입 일부는 원문에서 확인 불가이며, 수록된 최소 힙 병합 절차만 정리했습니다. (K 부록 A.2.2, PDF p.444-446)')])
        story.append(heading('다루는 내용',1))
        story.extend(fp(f,n,'학습 범위') for f in u['learning'])
        story.append(heading('핵심 개념',1))
        for c in u['concepts']:
            flows=[fp(f,n,'핵심 개념') for f in c['items']]
            # Small groups keep definitions visually distinct without split boxes.
            chunks=[];chunk=[]
            for p in flows:
                trial=box(chunk+[p])
                if trial.wrap(WIDTH,BODY_H)[1]>430 and chunk:chunks.append(chunk);chunk=[]
                chunk.append(p)
            if chunk:chunks.append(chunk)
            for j,chunk in enumerate(chunks):
                story.extend([heading(c['title']+(' (계속)' if j else ''),2),box(chunk),Spacer(1,7)])
        if u['procedures']:
            for j,p in enumerate(u['procedures']):
                flows=([heading('동작 방식·절차',1)] if j==0 else [])+[heading(p['title'],2)]+[fp(f,n,'동작 절차',number=i+1) for i,f in enumerate(p['steps'])]
                height=sum(f.wrap(WIDTH,BODY_H)[1]+f.getSpaceAfter()+f.getSpaceBefore() for f in flows)
                if height<BODY_H-15:story.append(KeepTogether(flows))
                else:story.extend(flows)
        story.append(heading('주요 문법·표·수식',1))
        for c in u.get('syntax',[]):story.extend([code_block(c,n),Spacer(1,8)])
        for f in u.get('formulas',[]):story.extend([box([fp(form_fact(f),n,'수식·복잡도')]),Spacer(1,8)])
        for comp in u.get('comparisons',[]):story.append(heading(comp['title'],2));story.extend(comparison(comp,n))
        story.append(heading('핵심 용어 표',1))
        rows=[[para('<b>'+esc(t['term'])+'</b>','cell',True),fp(t['definition'],n,'핵심 용어','cell')] for t in u['terms']]
        story.extend(table(['용어','원문에 나온 정의·설명'],rows,[108,WIDTH-108],max_height=500))
        summary=[fp(f,n,'단원 요약') for f in u['summary']]
        story.append(KeepTogether([heading('단원 요약',1),para('요약 기준: '+u['summary_basis'],'small'),summary[0]]))
        story.extend(summary[1:])
    story.extend([PageBreak(),heading('원문 기반 복습 질문과 정답',0,True)])
    for j,u in enumerate(units):
        n=u['unit']
        if j:story.append(PageBreak())
        story.append(heading(f'{n:02} {u["title"]}',1,True))
        for i,q in enumerate(u['review'],1):story.append(para(f'<b>{n:02}-{i}.</b> '+esc(q['question'])+' '+esc(ref_text(q['answer']['refs'])),'body',True))
        story.append(heading('정답과 원문 근거',1));story.extend(fp(q['answer'],n,'복습 정답',number=i) for i,q in enumerate(u['review'],1))
    d=Document(FILES['notes'],'C++ 프로그래밍과 코딩 테스트 - 정리 및 요약','notes');d.multiBuild(story);d.save_layout();print('NOTES',d.page,flush=True)
def cheat_story(u,first=False):
    n=u['unit'];story=[]
    if first:
        s=ParagraphStyle('ctitle',parent=ST['h0'],fontSize=18,leading=24,spaceAfter=3)
        story.extend([Paragraph('C++ 프로그래밍 · 코딩 테스트',s),para('- 확인 및 시험','ch'),Spacer(1,5)])
    s=ParagraphStyle('utitle',parent=ST['h0'],fontSize=15.5,leading=23,spaceAfter=6)
    story.append(heading(f'{n:02} {u["title"]}',0,True,s));story.append(para('핵심 정의','ch'))
    for t in u['cheat']['definitions']:story.append(fp(t['definition'],n,'치트 정의','cheat',term=t['term'],compact=True))
    c=u['cheat']
    if c.get('comparison_rows'):
        story.append(para(c['comparison_title'],'ch'));story.extend(comparison(dict(headers=c['comparison_headers'],rows=c['comparison_rows']),n,True))
    if c.get('formulas'):
        story.append(para('주요 수식·복잡도','ch'));story.extend(fp(form_fact(f),n,'치트 수식','cheat',compact=True) for f in c['formulas'])
    if c.get('syntax'):
        story.append(para('원문 문법 발췌','ch'));story.extend([code_block(x,n,True) for x in c['syntax']])
    return story
def make_cheats(units):
    story=[]
    for j,u in enumerate(units):
        if j:story.append(PageBreak())
        story.extend(cheat_story(u,j==0))
    d=Document(FILES['cheat'],'C++ 프로그래밍과 코딩 테스트 - 확인 및 시험','cheat');d.multiBuild(story);d.save_layout()
    assert d.page==len(units),('cheat overflow',d.page,d.entries)
    assert [x['page'] for x in d.entries]==list(range(1,len(units)+1)),d.entries
    print('CHEAT',d.page,flush=True)
def make_audit(units):
    story=cover('문장별 근거 · 인쇄 점검');story.extend([heading('검증 범위',0,True),para(f'중복을 합친 {len(REGISTRY)}개 항목의 문장·코드·수식과 원문 근거를 대조할 수 있습니다. 번호는 학습 노트·치트시트와 같습니다. 출처는 파일 코드와 원문 절·쪽수를 구분해 표시했습니다.'),para('B의 쪽수는 인쇄 쪽수이며 PDF 면 번호에서 5를 뺀 값입니다. K는 PDF 면 번호, L은 강의 슬라이드 번호입니다. 근거 대조 문구는 원문 발췌 또는 원문을 줄인 확인 문구입니다. 인용된 관련 페이지의 문맥과 대조했으며, OCR 자료의 코드·수식과 주요 표는 원본 이미지로 확인했습니다.')])
    story.append(heading('인쇄 품질 점검',1));qp=ROOT/'quality_report.json';q=json.loads(qp.read_text('utf-8')) if qp.exists() else None
    if q:
        rows=[]
        for k in ['notes','cheat','audit']:
            x=q['files'].get(k)
            if x:rows.append([{'notes':'학습 노트','cheat':'확인·시험','audit':'근거·점검'}[k],f'1-{x["pages"]}',x['clipping_status'],x['font_status'],x['orphan_status'],x['table_status']])
        story.extend(table(['파일','점검 면','잘림·넘침','폰트','제목 고립','표 분리'],rows,[65,47,95,70,85,WIDTH-362],max_height=400))
        story.append(para('최종 PDF의 모든 페이지를 이미지로 변환해 확인했습니다. 좌표·글꼴 포함·대체 글리프·제목·표 배치 검사 결과를 함께 대조했습니다.'))
    else:story.append(para('최종 렌더링 점검 후 결과를 반영합니다.'))
    for u in units:
        n=u['unit'];story.extend([PageBreak(),heading(f'{n:02} {u["title"]}',0,True)])
        rows=[]
        for r in REGISTRY:
            if r['unit']!=n:continue
            ev='근거 대조 문구: '+r['evidence']
            rows.append([r['id'],[para(r['text'],'cell'),Spacer(1,4),para(ev,'small')],ref_text(r['refs'])])
        story.extend(table(['번호','문장·원문 코드 / 근거 대조 문구','원문 위치'],rows,[54,WIDTH-177,123],max_height=570))
    d=Document(FILES['audit'],'C++ 프로그래밍과 코딩 테스트 - 문장별 근거 검증','audit');d.multiBuild(story);d.save_layout();print('AUDIT',d.page,flush=True)
def main():
    global BOLD_PATTERN
    units=[json.loads(p.read_text('utf-8-sig')) for p in sorted(ROOT.glob('unit_??.json'))]
    assert len(units)==25 or '--partial' in sys.argv,('missing units',len(units))
    assert [u['unit'] for u in units]==list(range(1,len(units)+1)), 'unit ordering'
    terms={t['term'].split('(')[0].strip() for u in units for t in u['terms']};patterns=[]
    for t in sorted(terms,key=len,reverse=True):
        if len(t)<2:continue
        patterns.append(r'(?<![A-Za-z0-9_])'+re.escape(t)+r'(?![A-Za-z0-9_])' if re.fullmatch(r'[A-Za-z0-9_ :<>-]+',t) else re.escape(t))
    BOLD_PATTERN=re.compile('|'.join(patterns))
    if '--audit-only' in sys.argv:
        REGISTRY.extend(json.loads((ROOT/'registry.json').read_text('utf-8')));ALL_LAYOUT.update(json.loads((ROOT/'layout.json').read_text('utf-8')));make_audit(units)
    else:
        make_notes(units);make_cheats(units);make_audit(units)
        (ROOT/'registry.json').write_text(json.dumps(REGISTRY,ensure_ascii=False,indent=2),'utf-8')
    maps=[pdfmetrics.getFont(n).face.charToGlyph for n in ['Nanum','MathSymbols','Mono']]
    missing=sorted(c for c in CHARS if c not in '\n\r\t' and not any(ord(c) in m for m in maps));assert not missing,missing
    (ROOT/'layout.json').write_text(json.dumps(ALL_LAYOUT,ensure_ascii=False,indent=2),'utf-8')
    (ROOT/'deliverables.json').write_text(json.dumps({k:str(v) for k,v in FILES.items()},ensure_ascii=False,indent=2),'utf-8')
    print('BUILD COMPLETE',flush=True)
if __name__=='__main__':main()
