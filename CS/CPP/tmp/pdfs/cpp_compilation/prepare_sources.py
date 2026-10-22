from pathlib import Path
import json
import pymupdf as fitz

ROOT=Path(__file__).resolve().parent
SOURCES={
 'B':Path('C:/Users/user/Downloads/cpp.pdf'),
 'K':Path('C:/Users/user/Downloads/Cpp코테.pdf')
}
LECTURES=Path('C:/Users/user/Downloads/drive-download-20261019T123347Z-1-001')

def main():
    textdir=ROOT/'sources'
    textdir.mkdir(parents=True,exist_ok=True)
    registry={}
    for p in sorted(LECTURES.glob('*.pdf')):
        sid='L02D' if 'Additional' in p.name else p.name.split('_')[0].replace('Lec','L')
        if 'Part1' in p.name: sid='L05A'
        if 'Part2' in p.name: sid='L05B'
        SOURCES[sid]=p
    for sid,path in SOURCES.items():
        d=fitz.open(path)
        registry[sid]={'id':sid,'path':str(path),'filename':path.name,'pdf_pages':len(d),'printed_offset':-5 if sid=='B' else 0 if sid!='K' else None}
        if sid=='K':
            dest=ROOT/'kote_images'
            dest.mkdir(exist_ok=True)
            for i,page in enumerate(d,1):
                out=dest/f'{i:04d}.jpg'
                if out.exists():continue
                imgs=page.get_images(full=True)
                if len(imgs)==1:
                    image=d.extract_image(imgs[0][0])
                    if image['ext'] in ['jpg','jpeg']:
                        out.write_bytes(image['image'])
                    else:
                        page.get_pixmap(matrix=fitz.Matrix(2000/page.rect.width,2000/page.rect.width)).save(out)
                else:
                    page.get_pixmap(matrix=fitz.Matrix(2000/page.rect.width,2000/page.rect.width)).save(out)
            print('K: extracted 530 source images',flush=True)
            continue
        records=[{'source':sid,'pdf_page':i+1,'printed_page':i-4 if sid=='B' and i>=5 else i+1 if sid!='B' and i>0 else None,'text':page.get_text(sort=True)} for i,page in enumerate(d)]
        (textdir/f'{sid}_pages.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        (textdir/f'{sid}_all.txt').write_text(''.join(f'\n=== {sid} | PDF p.{r["pdf_page"]} | 印刷 p.{r["printed_page"]} ===\n{r["text"]}\n' for r in records),encoding='utf-8')
        print(f'{sid}: {len(d)} text pages',flush=True)
    (ROOT/'source_registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
