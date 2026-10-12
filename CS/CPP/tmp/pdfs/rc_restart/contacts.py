from pathlib import Path
import json
from PIL import Image,ImageDraw
base=Path(__file__).resolve().parent
manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
images=sorted((base/'render').glob('page-*.png'));assert len(images)==len(manifest)
for start in range(0,len(images),25):
    tw,th=245,347
    sheet=Image.new('RGB',(5*(tw+12)+12,5*(th+25)+12),'#d7dce2');draw=ImageDraw.Draw(sheet)
    for j,path in enumerate(images[start:start+25]):
        im=Image.open(path).convert('RGB');im.thumbnail((tw,th))
        x=12+(j%5)*(tw+12);y=12+(j//5)*(th+25)
        sheet.paste(im,(x,y));draw.text((x,y+th+3),f'{start+j+1} | {manifest[start+j]["section"]}',fill='black')
    sheet.save(base/f'contact-{start//25+1:02d}.jpg',quality=92)
print('Created', (len(images)+24)//25,'contact sheets')
