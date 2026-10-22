from pathlib import Path
import json
import re
import pymupdf as fitz
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
MM=72/25.4

def check_render(only=None):
    files=json.loads((ROOT/'deliverables.json').read_text(encoding='utf-8'))
    layouts=json.loads((ROOT/'layout.json').read_text(encoding='utf-8'))
    old=ROOT/'quality_report.json'
    result=json.loads(old.read_text(encoding='utf-8')) if old.exists() else {'files':{},'visual_review_complete':False}
    for key,path in files.items():
        if only and key not in only:
            continue
        d=fitz.open(path)
        folder=ROOT/'render'/key
        folder.mkdir(parents=True,exist_ok=True)
        boundary=[]
        glyphs=[]
        empty=[]
        font_names=set()
        for i,page in enumerate(d):
            text=page.get_text()
            if len(text.strip())<10:
                empty.append(i+1)
            if '\ufffd' in text or '\u25a1' in text or '\x00' in text:
                glyphs.append(i+1)
            for block in page.get_text('dict')['blocks']:
                if 'lines' not in block:
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        font_names.add(span['font'])
                        x0,y0,x1,y1=span['bbox']
                        if x0<20*MM-.5 or x1>page.rect.width-20*MM+.5 or y0<20*MM-.5 or y1>page.rect.height-20*MM+.5:
                            boundary.append({'page':i+1,'text':span['text'],'bbox':[round(x,2) for x in span['bbox']]})
            page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(folder/f'{i+1:03d}.png')
        positions=layouts[key]['positions']
        orphans=[]
        for i,p in enumerate(positions):
            if p['kind']=='heading':
                following=next((x for x in positions[i+1:] if x['kind']!='heading'),None)
                if following and following['page']!=p['page']:
                    orphans.append({'page':p['page'],'heading':p['title']})
        tables=[p for p in positions if p['kind'] in ['table','box']]
        table_errors=[p for p in tables if p['bottom']<28*MM-.5]
        # Every table and definition box is a single non-splitting flowable.
        for start in range(0,len(d),4):
            thumbs=[]
            for i in range(start,min(start+4,len(d))):
                im=Image.open(folder/f'{i+1:03d}.png').convert('RGB')
                im.thumbnail((800,1132))
                thumbs.append((i+1,im))
            sheet=Image.new('RGB',(1640,2*1170),'#dedede')
            draw=ImageDraw.Draw(sheet)
            for j,(num,im) in enumerate(thumbs):
                x=10+(j%2)*820
                y=25+(j//2)*1170
                draw.text((x,y-19),f'{key} PDF {num}',fill='black')
                sheet.paste(im,(x,y))
            sheet.save(folder/f'contact_{start+1:03d}_{min(start+4,len(d)):03d}.jpg',quality=94)
        font_embedded=all(any(z[1] and z[1] not in ['n/a',''] for z in d.get_page_fonts(i)) for i in range(len(d)))
        result['files'][key]={'path':path,'pages':len(d),'boundary_issues':boundary,'replacement_glyph_pages':glyphs,'empty_pages':empty,'orphan_headings':orphans,'table_errors':table_errors,'fonts':sorted(font_names),'font_embedded':font_embedded,'clipping_status':'이상 없음' if not boundary else f'{len(boundary)}건 확인 필요','font_status':'이상 없음' if not glyphs and font_embedded else '확인 필요','orphan_status':'이상 없음' if not orphans else f'{len(orphans)}건 확인 필요','table_status':'분리 없음' if not table_errors else '확인 필요'}
        print(key,len(d),'pages; boundary',len(boundary),'glyph',glyphs,'orphan',len(orphans),'table',len(table_errors),flush=True)
    (ROOT/'quality_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    import sys
    check_render(sys.argv[1:] or None)
