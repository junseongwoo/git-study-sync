from pathlib import Path
import json, re, html, math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Preformatted
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
VAULT = HERE.parents[4]
W, H = 595.2756, 841.8898
M = 43
CW = W - 2*M
NAVY = colors.HexColor('#152C46')
INK = colors.HexColor('#213449')
MUTED = colors.HexColor('#586B7D')
LINE = colors.HexColor('#D7E0E8')
LIGHT = colors.HexColor('#F1F5F8')
WHITE = colors.white
ACCENTS = {'cpp':'#2162A2','cv':'#087B73','coding':'#7751A6'}
COUNTS = {'cpp':'Markdown 9개 · 기존 PDF 3개', 'cv':'Markdown 32개 · 기존 PDF 5개', 'coding':'Markdown 6개'}
OUTPUTS = {
 'cpp': VAULT/'CS/CPP/output/pdf/CPP_이직준비_추가학습_검증과제품화.pdf',
 'cv': VAULT/'CV/output/pdf/CV_이직준비_추가학습_측정과검증.pdf',
 'coding': VAULT/'코테준비/output/pdf/코테_이직준비_추가학습_6일차이후.pdf',
}
pdfmetrics.registerFont(TTFont('Malgun','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('Malgun-Bold','C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFontFamily('Malgun',normal='Malgun',bold='Malgun-Bold',italic='Malgun',boldItalic='Malgun-Bold')
pdfmetrics.registerFont(TTFont('Code','C:/Windows/Fonts/consola.ttf'))

def normalize(s):
    return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u00a0',' ')

def rich(s):
    s = html.escape(normalize(s))
    s = re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    s = re.sub(r'`([^`]+)`',r'<font color="#2162A2">\1</font>',s)
    return s.replace('\n','<br/>')

def para(s, size=10.6, color=INK, bold=False, leading=None, raw=False):
    st = ParagraphStyle('p',fontName='Malgun-Bold' if bold else 'Malgun',fontSize=size,
                        leading=leading or size*1.52,textColor=color,wordWrap='CJK',
                        splitLongWords=True,allowWidows=0,allowOrphans=0)
    return Paragraph(s if raw else rich(s), st)

def measured(flow, width=CW):
    return flow.wrap(width, 10000)[1]

def boxed(content, width=CW, bg=LIGHT, accent=None, padding=11):
    t = Table([[content]],colWidths=[width])
    cmds=[('BACKGROUND',(0,0),(-1,-1),bg),('LEFTPADDING',(0,0),(-1,-1),padding),
          ('RIGHTPADDING',(0,0),(-1,-1),padding),('TOPPADDING',(0,0),(-1,-1),padding),
          ('BOTTOMPADDING',(0,0),(-1,-1),padding)]
    if accent: cmds += [('LINEBEFORE',(0,0),(0,-1),2.5,accent)]
    t.setStyle(TableStyle(cmds))
    return t

def block_flows(block, scale, accent):
    typ = block['type']; fs=10.6*scale
    if typ=='p': return [(para(block['text'],fs),7*scale)]
    if typ=='h3': return [(para(block['text'],12.2*scale,accent,True),6*scale)]
    if typ=='bullets':
        rows=[[para('-',fs,accent,True),para(it,fs)] for it in block['items']]
        t=Table(rows,colWidths=[13,CW-13]); t.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
            ('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),
            ('BOTTOMPADDING',(0,0),(-1,-1),4*scale)]))
        return [(t,5*scale)]
    if typ=='code':
        code=normalize(block['text']).expandtabs(4)
        code_font='Code' if code.isascii() else 'Malgun'
        longest=max([pdfmetrics.stringWidth(x,code_font,8.5*scale) for x in code.splitlines()] or [0])
        code_size=8.5*scale*min(1,(CW-24)/max(1,longest))
        if code_size<7: raise ValueError(f'Code too small: {code_size}')
        p=Preformatted(code,ParagraphStyle('code',fontName=code_font,fontSize=code_size,
                           leading=code_size*1.42,textColor=INK))
        return [(boxed(p,padding=10),10*scale)]
    if typ=='callout':
        ps=[para(block.get('title','학습 포인트'),10.3*scale,accent,True),
            para(block['text'],10.1*scale)]
        return [(boxed(ps,bg=colors.HexColor('#F0F5FA'),accent=accent,padding=10),10*scale)]
    if typ=='table':
        heads=block['headers']; ratios=block.get('widths',[1/len(heads)]*len(heads))
        sw=sum(ratios); widths=[CW*r/sw for r in ratios]
        rows=[[para(x,9.2*scale,WHITE,True) for x in heads]]
        rows += [[para(x,9.5*scale) for x in row] for row in block['rows']]
        t=Table(rows,colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),accent),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
            ('TOPPADDING',(0,0),(-1,-1),7*scale),('BOTTOMPADDING',(0,0),(-1,-1),7*scale),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,LIGHT]),
            ('LINEBELOW',(0,0),(-1,0),.5,accent),('LINEBELOW',(0,1),(-1,-1),.4,LINE)]))
        return [(t,10*scale)]
    raise ValueError(typ)

def draw_flow(c, f, y, x=M, width=CW):
    h=measured(f,width); f.drawOn(c,x,y-h); return y-h

def furniture(c,d,n,total,accent):
    c.setFillColor(accent); c.rect(0,H-7,W,7,fill=1,stroke=0)
    c.setFont('Malgun-Bold',8.5); c.setFillColor(accent)
    c.drawString(M,H-33,'FOLDER STUDY / '+d['folder'])
    c.setFillColor(MUTED); c.setFont('Malgun',8)
    c.drawRightString(W-M,H-33,'추가 학습 · 이직 준비')
    c.setStrokeColor(LINE); c.setLineWidth(.5); c.line(M,43,W-M,43)
    c.setFont('Malgun',7.5); c.setFillColor(MUTED)
    c.drawString(M,28,'2026.09.26  |  기존 자료를 잇는 실습과 검증')
    c.drawRightString(W-M,28,f'{n:02d} / {total:02d}')

def cover(c,d,total,accent):
    c.setFillColor(NAVY); c.rect(0,H-345,W,345,fill=1,stroke=0)
    c.setFillColor(accent); c.rect(M,H-80,42,5,fill=1,stroke=0)
    c.setFont('Malgun-Bold',10); c.setFillColor(colors.HexColor('#C5DAE9'))
    c.drawString(M,H-60,'CAREER STUDY / '+d['folder'])
    y=H-105
    y=draw_flow(c,para(d['title'],29,WHITE,True,leading=41),y)
    y-=17
    y=draw_flow(c,para(d['subtitle'],12,colors.HexColor('#DBE6EE'),leading=19),y)
    if y<H-321: raise ValueError('Cover title too long')
    y=H-373
    y=draw_flow(c,para('현재 자료 다음에, 무엇을 직접 해볼까',17,INK,True),y)-12
    y=draw_flow(c,para(d['summary'],11.2,INK),y)-17
    data=[['기준 폴더',d['folder']],['검토 자료',COUNTS[d['id']]],
          ['기준 직무',d['audience']],['권장 활용','주 6-8시간을 이 폴더에 배정하는 6주 집중 과정']]
    t=Table([[para(a,9.5,MUTED,True),para(b,10)] for a,b in data],colWidths=[85,CW-85])
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
         ('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),7),
         ('LINEBELOW',(0,0),(-1,-1),.4,LINE)]))
    y=draw_flow(c,t,y)-15
    y=draw_flow(c,para('읽기  →  구현·실험  →  결과 설명',11.5,accent,True),y)-7
    y=draw_flow(c,para('자료 보유와 학습 완료는 별개입니다. 각 장의 통과 기준으로 시작 위치를 정하세요. 세 폴더의 계획은 개별 집중 기준이며, 병행할 때는 총 가용 시간에 맞춰 기간을 늘립니다.',9.5,MUTED),y)
    if y<70: raise ValueError(f'Cover overflow {y}')
    c.setStrokeColor(LINE); c.line(M,43,W-M,43)
    c.setFillColor(MUTED); c.setFont('Malgun',7.5)
    c.drawString(M,28,'작성 기준 2026.09.26  |  학습 우선순위는 기존 자료와 직무 연결을 바탕으로 제안')
    c.drawRightString(W-M,28,f'01 / {total:02d}')
    c.bookmarkPage('cover'); c.addOutlineEntry('표지','cover',0)
    c.showPage()

def render_page(c,d,page,n,total,accent):
    furniture(c,d,n,total,accent)
    y=H-68
    y=draw_flow(c,para(page.get('label',f'{n-1:02d}'),9.1,accent,True),y)-7
    y=draw_flow(c,para(page['title'],22,INK,True,leading=30),y)-12
    if page.get('lead'):
        y=draw_flow(c,para(page['lead'],10.8,MUTED),y)-14
    available=y-62
    scale=1.0
    while True:
        flows=[]
        for b in page['blocks']: flows+=block_flows(b,scale,accent)
        req=sum(measured(f)+g for f,g in flows)
        if req<=available: break
        scale=round(scale-.02,2)
        if scale<.86:
            raise ValueError(f"{d['id']} p{n} overflow: {page['title']} {req:.1f}/{available:.1f}")
    key='p'+str(n)
    c.bookmarkPage(key); c.addOutlineEntry(page['title'],key,0)
    for f,g in flows: y=draw_flow(c,f,y)-g
    c.showPage()
    return {'page':n,'title':page['title'],'scale':scale,'bottom':round(y,1)}

def supplement_pages(d):
    pages=[]
    ev=d.get('evidence',[])
    if ev:
        for i in range(0,len(ev),5):
            blocks=[]
            for e in ev[i:i+5]:
                blocks.extend([{'type':'h3','text':e['path']},{'type':'p','text':e['finding']}])
            if i==0: blocks.append({'type':'callout','title':'검토 기준','text':'기존 자료의 주제와 실습을 검토해 다음 과제를 골랐습니다. 문서에서 확인되지 않는 내용은 자료상의 빈칸으로 해석하며, 개인의 실제 경험이나 숙련도를 단정하지 않습니다.'})
            pages.append({'label':'APPENDIX / LOCAL NOTES','title':'어떤 자료에서 이어졌나'+(' · 계속' if i else ''),'lead':'경로는 표지의 기준 폴더 안에서 읽습니다. 기존 노트를 함께 펴놓고 이어서 학습하세요.','blocks':blocks})
    sources=d.get('sources',[])
    for i in range(0,len(sources),5):
        blocks=[]
        for s in sources[i:i+5]:
            url=s['url']
            blocks.extend([{'type':'h3','text':f"[{s['id']}] {s['title']}"},
                           {'type':'p','text':s['use']},
                           {'type':'source_link','url':url}])
        pages.append({'label':'REFERENCES / PRIMARY SOURCES','title':'참고 자료와 활용 범위'+(' · 계속' if i else ''),'lead':'본문의 [번호]에 대응하는 공식 문서·원문입니다. 확인일: 2026.09.26.','blocks':blocks})
    return pages

orig_block_flows=block_flows
def block_flows(block,scale,accent):
    if block['type']=='source_link':
        url=html.escape(block['url'],quote=True)
        return [(para(f'<link href="{url}" color="{accent.hexval()}">{url}</link>',8.4*scale,raw=True),12*scale)]
    return orig_block_flows(block,scale,accent)

def main():
    import sys
    selected=sys.argv[1:] or ['cpp','cv','coding']
    results=[]
    for key in selected:
        d=json.loads((HERE/(key+'.json')).read_text(encoding='utf-8-sig'))
        accent=colors.HexColor(ACCENTS[key])
        pages=d['pages']+supplement_pages(d)
        dest=OUTPUTS[key];dest.parent.mkdir(parents=True,exist_ok=True)
        c=canvas.Canvas(str(dest),pagesize=(W,H),pageCompression=1)
        c.setTitle(d['title']);c.setAuthor('학습 자료');c.setSubject(d['subtitle'])
        cover(c,d,len(pages)+1,accent)
        qa=[]
        for idx,p in enumerate(pages,start=2): qa.append(render_page(c,d,p,idx,len(pages)+1,accent))
        c.save()
        reader=PdfReader(str(dest))
        text='\n'.join(p.extract_text() or '' for p in reader.pages)
        if '\ufffd' in text or len(text)<5000: raise ValueError('PDF extraction anomaly')
        if len(reader.pages)!=len(pages)+1: raise ValueError('Page count mismatch')
        info={'id':key,'path':str(dest),'pages':len(reader.pages),'text_chars':len(text),'layout':qa}
        results.append(info)
        print(json.dumps({k:v for k,v in info.items() if k!='layout'},ensure_ascii=False))
    (HERE/'build-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
