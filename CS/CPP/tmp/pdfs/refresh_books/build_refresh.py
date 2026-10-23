from pathlib import Path
import json,sys,re,copy,importlib.util,html
from reportlab.platypus import Image as RLImage
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('layout',BASE.parent/'c_ds_compilation/build_c_ds.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=m.para;H=m.heading;FP=m.fp;SP=m.Spacer;PB=m.PageBreak;KT=m.KeepTogether
CFG={};CHAPTERS=[];OVERLAYS={};SRC='';ROOT=None

def source_ref(src,section):
    assert src and src.get('pdf'),(section,src)
    return [dict(source=SRC,section=section,pages=src['pdf'])]
def fact(text,src,section,evidence='원문 해당 절·면의 본문과 대조하는 재구성 문장'):
    return dict(text=clean(text),refs=source_ref(src,section),evidence=evidence)
def clean(s):return m.norm(str(s)).replace('**','').replace('[원문에서 확인할 수 없음]','원문에서 확인 불가').replace('원문에서 확인되지 않음','원문에서 확인 불가')
def sentences(s):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[가-힣A-Za-z<\[])',clean(s)) if x.strip()]
def ref_text(refs,compact=False,include_pdf=False):
    out=[]
    for r in refs:
        nums=[CFG['page_map'].get(str(p)) for p in r['pages']];sec=r['section']
        if compact:
            prefix=sec.split(' ')[0]
            if re.fullmatch(r'[0-9.·~–-]+',prefix):sec=prefix
        loc=('p.' if compact else '인쇄 p.')+m.pages_text(nums) if all(x is not None for x in nums) else 'PDF p.'+m.pages_text(r['pages'])
        if include_pdf and all(x is not None for x in nums):loc+=' / PDF p.'+m.pages_text(r['pages'])
        out.append(sec+', '+loc)
    return '('+'; '.join(out)+')'
class Document(m.Document):
    def draw_page(self,c,doc):
        c.saveState();c.setFillColor(m.GRAY)
        if self.page>1:
            c.setFont('Nanum',8.2);c.drawString(m.M,m.H-23*m.mm,CFG['title']);c.drawRightString(m.W-m.M,m.H-23*m.mm,{'notes':'정리 및 요약','cheat':'확인 및 시험','audit':'문장별 근거 · 인쇄 점검'}[self.key]);c.setLineWidth(.45);c.setStrokeColor(m.RULE);c.line(m.M,m.H-26*m.mm,m.W-m.M,m.H-26*m.mm)
        c.setFont('Nanum',9);c.drawCentredString(m.W/2,22*m.mm,str(self.page));c.restoreState()
def cover(subtitle):return [SP(1,57*m.mm),P(CFG['title'],'h0'),SP(1,10*m.mm),P('- '+subtitle,'h1'),PB()]
def contents():
    toc=m.TableOfContents();toc.levelStyles=[m.ParagraphStyle('refresh_toc',fontName='Nanum',fontSize=10.2,leading=14,spaceBefore=0,spaceAfter=0,wordWrap='CJK')]
    return [H('목차'),toc,PB()]
def text_facts(text,src,sec,u,kind='상세 본문',style='body'):
    return [FP(fact(s,src,sec),u,kind,style) for s in sentences(text)]
def source_line(src,sec):return P(ref_text(source_ref(src,sec)),'small')
def compare(table,u,src,sec,kind='원문 비교표'):
    rows=[]
    for row in table['rows']:
        rows.append([FP(fact(cell,src,sec),u,kind,'cell') for cell in row])
    widths=table.get('widths')
    if widths and (len(widths)!=len(table['headers']) or sum(widths)>m.WIDTH+1):widths=None
    if widths is None and len(table['headers'])==2:widths=[m.WIDTH*.26,m.WIDTH*.74]
    return m.table(table['headers'],rows,widths,max_height=500)
def code_flows(code,u,sec):
    refs=source_ref(code['source'],sec);lines=code['code'].splitlines();chunks=[];chunk=[]
    for line in lines:
        tentative=dict(label=code['title'],code='\n'.join(chunk+[line]),refs=refs,evidence='원문 코드 발췌',note=None)
        # Trial uses an isolated paragraph-only estimate; no registry side effects.
        height=65+sum(P(html.escape(l.expandtabs(4)).replace(' ','&#160;') or '&#160;','code',True).wrap(m.WIDTH-18,m.BODY_H)[1] for l in chunk+[line])
        if height>485 and chunk:chunks.append(chunk);chunk=[]
        chunk.append(line)
    if chunk:chunks.append(chunk)
    out=[]
    for j,part in enumerate(chunks):
        label=code['title']+(f' ({j+1}/{len(chunks)})' if len(chunks)>1 else '')
        c=dict(label=label,code='\n'.join(part),refs=refs,evidence='원문 코드: '+next((x.strip() for x in part if x.strip()),code['title']),note=None)
        out.extend([m.code_block(c,u),SP(1,8)])
    if code.get('excerpt_note'):out.append(P('발췌 범위: '+clean(code['excerpt_note']),'small'))
    return out
def figure_flows(fig,u,sec):
    file=Path(fig['file']);file=file if file.is_absolute() else Path(CFG['original_dir'])/file
    im=RLImage(str(file));scale=min(m.WIDTH/im.imageWidth,450/im.imageHeight,1.0);im.drawWidth=im.imageWidth*scale;im.drawHeight=im.imageHeight*scale;im.height=im.drawHeight;im.audit_kind='figure'
    label=fig.get('title',fig['id']);caption=FP(fact(fig.get('caption') or label,fig['source'],sec),u,'원문 그림','small')
    return [KT([H(label,2),im,SP(1,4),caption]),SP(1,7)]
def render_blocks(ch,u):
    out=[];codes={x['id']:x for x in ch.get('codes',[])};figs={x['id']:x for x in ch.get('figures',[])};used_c=set();used_f=set()
    for sec in ch['sections']:
        label=sec['number']+' '+sec['title'];src=sec.get('source',ch['source']);blocks=sec.get('blocks',[])
        if not blocks:continue
        out.append(H(label,2))
        for b in blocks:
            bs=b.get('source',src);typ=b['type']
            if typ=='p':out.extend(text_facts(b['text'],bs,label,u))
            elif typ in ['bullets','list']:
                for t in b['items']:out.extend(text_facts(t,bs,label,u))
            elif typ=='table':out.extend(compare(b,u,bs,label))
            elif typ in ['steps','flow']:
                if b.get('title'):out.append(H(b['title'],2))
                for i,t in enumerate(b.get('items',b.get('steps',[])),1):out.append(FP(fact(t,bs,label),u,'동작 절차',number=i))
            elif typ=='formula':
                f=dict(label=b.get('title','원문 수식'),expression=b['text'],note='; '.join(b.get('symbols',[]))+('; '+b['explanation'] if b.get('explanation') else ''),refs=source_ref(bs,label),evidence='원문 수식과 기호')
                out.extend([m.box([m.form_para(f,u)]),SP(1,8)])
            elif typ=='code_ref':out.extend(code_flows(codes[b['id']],u,label));used_c.add(b['id'])
            elif typ=='figure_ref':out.extend(figure_flows(figs[b['id']],u,label));used_f.add(b['id'])
            elif typ in ['heading','subheading']:out.append(H(b.get('text',b.get('title','')),2))
            else:raise ValueError((ch['id'],typ))
    for c in ch.get('codes',[]):
        if c['id'] not in used_c:out.extend(code_flows(c,u,ch['title']))
    for f in ch.get('figures',[]):
        if f['id'] not in used_f:out.extend(figure_flows(f,u,ch['title']))
    return out
def build_notes():
    story=cover('정리 및 요약')+contents()+[H('원문 범위와 출처 읽는 법',0,True)]
    for t in [CFG['original_info']['scope_note'],'기존 상세 내용을 원문 장·절 순서로 유지하면서 항목별 근거 번호, 정의 중심 용어 표, 원문 요약·조언에 근거한 장 요약과 복습 정답을 보강했습니다. 문장 끝의 인쇄 쪽수는 원본 스캔의 쪽수입니다. 별도 근거표에는 원본 PDF 면 번호도 병기했습니다.','같은 [U장-항목] 번호는 세 PDF에서 같은 내용을 가리킵니다. 원문에 없는 예시·해설·실행 결과를 보충하지 않았습니다. 당시의 표준·기능 상태와 원문 내부의 의심 표기는 원문 확인 메모와 함께 보존했습니다.']:
        story.append(P(clean(t)))
    story.append(H('수록 한계',1))
    story.extend(P(clean(t)) for t in CFG['original_info'].get('limitations',[]))
    story.append(H('장별 원문 범위',1));story.extend(m.table(['장','원문 위치'],[[c['title'],ref_text(source_ref(c['source'],c['title']),include_pdf=True)] for c in CHAPTERS],[m.WIDTH*.42,m.WIDTH*.58],max_height=540))
    # Preserve original part introductions where they have their own source page.
    for b in CFG['original_info'].get('overview',[]):
        if isinstance(b,dict) and b.get('type')=='p' and b.get('source'):story.extend(text_facts(b['text'],b['source'],'부 도입',0,'부 도입'))
    for c in CHAPTERS:
        u=int(c['order']);o=OVERLAYS[u];story.extend([PB(),H(c['title'],0,True),source_line(c['source'],c['title'])])
        if o['learning']:story.append(H('학습 목표·범위',1));story.extend(FP(f,u,'학습 범위') for f in o['learning'])
        story.append(H('핵심 개념·동작 절차·원문 예제',1));story.extend(render_blocks(c,u))
        if c.get('comparisons'):
            story.append(H('주요 비교표',1))
            for comp in c['comparisons']:
                story.append(H(comp['title'],2));story.extend(compare(comp,u,comp.get('source',c['source']),comp['title']))
        if o['terms']:
            story.append(H('핵심 용어 표',1));story.extend(m.table(['용어','원문 정의·설명'],[[P('<b>'+m.esc(t['term'])+'</b>','cell',True),FP(t['definition'],u,'핵심 용어','cell')] for t in o['terms']],[108,m.WIDTH-108],max_height=500))
        if o['summary']:
            fs=[FP(f,u,'장 요약') for f in o['summary']];story.append(KT([H('장 요약',1),P('요약 기준: '+o['summary_basis'],'small'),fs[0]]));story.extend(fs[1:])
        if c.get('limitations') or o.get('editor_notes'):
            story.append(H('원문 확인 메모',1));story.extend(P(clean(t),'small') for t in c.get('limitations',[])+o.get('editor_notes',[]))
    story.extend([PB(),H('원문 기반 복습 질문과 정답',0,True)])
    for c in CHAPTERS:
        u=int(c['order']);o=OVERLAYS[u]
        if not o['review']:continue
        story.extend([PB(),H(c['title'],1,True)])
        for i,q in enumerate(o['review'],1):story.append(P(f'{u:02}-{i}. '+q['question']+' '+ref_text(q['answer']['refs'])))
        story.append(H('정답과 원문 근거',1));story.extend(FP(q['answer'],u,'복습 정답',number=i) for i,q in enumerate(o['review'],1))
    d=Document(m.FILES['notes'],CFG['title']+' - 정리 및 요약','notes');d.multiBuild(story);d.save_layout();print(CFG['name'],'NOTES',d.page,flush=True)
def build_cheat():
    story=cover('확인 및 시험')+contents()
    for i,c in enumerate(CHAPTERS):
        u=int(c['order']);o=OVERLAYS[u]
        if i:story.append(PB())
        style=m.ParagraphStyle('cheat-title',parent=m.ST['h0'],fontSize=15.5,leading=23,spaceAfter=6)
        story.append(H(c['title'],0,True,style))
        cheat=o['cheat']
        if not cheat.get('definitions'):
            story.append(P('본문은 원문에서 확인 불가입니다. 이 면은 미제공 범위를 알리는 안내이며, 해당 장의 학습 내용을 요약하지 않았습니다. '+ref_text(source_ref(c['source'],'원문 목차'))));continue
        story.append(H('핵심 정의',2));story.extend(FP(t['definition'],u,'치트 정의','cheat',term=t['term'],compact=True) for t in cheat['definitions'])
        if cheat.get('comparison_rows'):
            story.append(H(cheat['comparison_title'],2));story.extend(m.comparison(dict(headers=cheat['comparison_headers'],rows=cheat['comparison_rows']),u,True))
        if cheat.get('formulas'):
            story.append(H('주요 수식·조건',2));story.extend(m.form_para(f,u,'치트 수식','cheat',True) for f in cheat['formulas'])
    d=Document(m.FILES['cheat'],CFG['title']+' - 확인 및 시험','cheat');d.multiBuild(story);d.save_layout()
    assert len(d.entries)==len(CHAPTERS)
    assert [e['page'] for e in d.entries]==list(range(d.entries[0]['page'],d.entries[0]['page']+len(CHAPTERS))),('cheat overflow',d.entries)
    print(CFG['name'],'CHEAT',d.page,flush=True)
def build_audit():
    story=cover('문장별 근거 · 인쇄 점검')+contents()+[H('검증 범위와 인쇄 점검',0,True),P(f'문장·목록·표의 항목·코드·수식 {len(m.REGISTRY)}개에 근거 번호와 원문의 절·인쇄 쪽수·PDF 면 번호를 연결했습니다. 문장의 원문 위치는 기존 상세 원고의 절별 근거를 유지했으며, 추가한 정의·요약·치트·복습 답은 원문과 다시 대조했습니다. 같은 번호는 세 PDF에서 재사용합니다.'),P('코드·수식·그림과 의심 표기는 원문 스캔을 우선했습니다. 의심스러운 내용을 외부 지식으로 교정하거나 미제공 부분을 채우지 않았습니다.')]
    qpath=ROOT/'quality_report.json'
    if qpath.exists():
        q=json.loads(qpath.read_text('utf-8'));rows=[]
        for k,label in [('notes','학습 노트'),('cheat','확인·시험'),('audit','근거·점검')]:
            x=q['files'][k];rows.append([label,'1-'+str(x['pages']),x['clipping_status'],x['font_status'],x['orphan_status'],x['table_status']])
        story.extend(m.table(['파일','점검 면','잘림·넘침','폰트','제목 고립','표 분리'],rows,[65,47,95,70,85,m.WIDTH-362],max_height=400));story.append(P('전체 페이지를 이미지로 변환해 직접 확인하고 좌표·글꼴·제목·표 배치 검사와 대조했습니다.'))
    else:story.append(P('전체 페이지 렌더링 점검 후 결과를 반영합니다.'))
    for u,label in [(0,'부 도입')]+[(int(c['order']),c['title']) for c in CHAPTERS]:
        entries=[r for r in m.REGISTRY if r['unit']==u]
        if not entries:continue
        story.extend([PB(),H(label,0,True)])
        rows=[[r['id'],P(r['text'],'cell'),ref_text(r['refs'],include_pdf=True)] for r in entries]
        story.extend(m.table(['번호','문장·표 항목·원문 코드·수식','원문 위치'],rows,[54,m.WIDTH-177,123],max_height=570))
    d=Document(m.FILES['audit'],CFG['title']+' - 근거 및 인쇄 점검표','audit');d.multiBuild(story);d.save_layout();print(CFG['name'],'AUDIT',d.page,flush=True)
def main():
    global CFG,CHAPTERS,OVERLAYS,SRC,ROOT
    name=sys.argv[1];ROOT=BASE/name;CFG=json.loads((ROOT/'config.json').read_text('utf-8'));SRC=CFG['source_code']
    CHAPTERS=[json.loads(p.read_text('utf-8-sig')) for p in sorted((ROOT/'chapters').glob('*.json'))]
    OVERLAYS={int(p.stem):json.loads(p.read_text('utf-8-sig')) for p in sorted((ROOT/'overlays').glob('??.json'))}
    assert len(OVERLAYS)==16 or '--partial' in sys.argv,('missing overlays',len(OVERLAYS))
    if '--partial' in sys.argv:CHAPTERS=[c for c in CHAPTERS if int(c['order']) in OVERLAYS]
    for c in CHAPTERS:
        for correction in OVERLAYS[int(c['order'])].get('corrections',[]):
            parent=c
            for key in correction['path'][:-1]:parent=parent[key]
            key=correction['path'][-1];assert parent[key]==correction['before'],correction;parent[key]=correction['after']
    m.ROOT=ROOT;m.SOURCES={SRC:dict(id=SRC,pdf_pages=CFG['pdf_pages'],filename=Path(CFG['source_pdf']).name)};m.ref_text=ref_text
    m.FILES={k:BASE.parents[2]/'output/pdf'/f'{CFG["output_prefix"]}_{label}.pdf' for k,label in [('notes','정리_및_요약'),('cheat','확인_및_시험'),('audit','근거_및_인쇄점검표')]}
    terms={t['term'].split('(')[0].strip() for o in OVERLAYS.values() for t in o['terms']}
    for c in CHAPTERS:
        for s in c['sections']:
            for b in s['blocks']:
                if b.get('text'):terms.update(re.findall(r'\*\*(.+?)\*\*',b['text']))
    pats=[re.escape(t) for t in sorted(terms,key=len,reverse=True) if len(t)>1];m.BOLD_PATTERN=re.compile('|'.join(pats)) if pats else None
    if '--audit-only' in sys.argv:
        m.REGISTRY.extend(json.loads((ROOT/'registry.json').read_text('utf-8')));m.ALL_LAYOUT.update(json.loads((ROOT/'layout.json').read_text('utf-8')));build_audit()
    else:
        build_notes();build_cheat();build_audit();(ROOT/'registry.json').write_text(json.dumps(m.REGISTRY,ensure_ascii=False,indent=2),'utf-8')
    maps=[m.pdfmetrics.getFont(n).face.charToGlyph for n in ['Nanum','MathSymbols','Mono']]
    missing=sorted(c for c in m.CHARS if c not in '\n\r\t' and not any(ord(c) in d for d in maps));assert not missing,missing
    (ROOT/'layout.json').write_text(json.dumps(m.ALL_LAYOUT,ensure_ascii=False,indent=2),'utf-8');(ROOT/'deliverables.json').write_text(json.dumps({k:str(v) for k,v in m.FILES.items()},ensure_ascii=False,indent=2),'utf-8')
if __name__=='__main__':main()
