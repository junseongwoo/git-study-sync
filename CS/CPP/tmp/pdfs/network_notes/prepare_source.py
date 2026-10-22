from pathlib import Path
import json
import pymupdf as fitz

ROOT = Path(__file__).resolve().parent
SOURCE = Path('C:/Users/user/Downloads/네트워크_하향식.pdf')
CHAPTERS = [(1, 9, 82, 1, 74), (2, 83, 177, 75, 169), (3, 178, 286, 171, 279), (4, 287, 346, 281, 340), (5, 347, 408, 341, 402), (6, 409, 481, 403, 475)]

def render():
    doc = fitz.open(SOURCE)
    folder = ROOT/'images'
    folder.mkdir(parents=True, exist_ok=True)
    for number in range(9, 482):
        dest = folder/f'{number:04d}.jpg'
        if dest.exists():
            continue
        page = doc[number-1]
        page.get_pixmap(matrix=fitz.Matrix(2000/page.rect.width, 2000/page.rect.width)).save(dest, jpg_quality=91)
        if number % 50 == 0:
            print(f'render {number}/481', flush=True)
    print('RENDER COMPLETE', flush=True)

def combine():
    for chapter, start, end, first, last in CHAPTERS:
        if not all((ROOT/'ocr'/f'{page:04d}.txt').exists() for page in range(start,end+1)):
            print(f'chapter {chapter}: OCR pending',flush=True)
            continue
        records = []
        chunks = []
        for page in range(start, end+1):
            printed = first+page-start
            path = ROOT/'ocr'/f'{page:04d}.txt'
            text = path.read_text(encoding='utf-8')
            records.append({'chapter':chapter, 'pdf_page':page, 'printed_page':printed, 'text':text})
            chunks.append(f'\n=== 인쇄 p.{printed} | PDF {page} ===\n{text}\n')
        (ROOT/f'chapter_{chapter}_ocr.txt').write_text(''.join(chunks),encoding='utf-8')
        (ROOT/f'chapter_{chapter}_pages.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'chapter {chapter}: {len(records)} pages',flush=True)

if __name__ == '__main__':
    import sys
    render() if sys.argv[1] == 'render' else combine()
