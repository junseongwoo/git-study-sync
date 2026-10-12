from pathlib import Path
import subprocess,json
from PIL import Image, ImageDraw
from pypdf import PdfReader
import build_guides as bg
HERE=Path(__file__).resolve().parent
POPPLER=r'C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
for key,path in bg.OUTPUTS.items():
    target=HERE/key;target.mkdir(exist_ok=True)
    subprocess.run([POPPLER,'-r','95','-png',str(path),str(target/'page')],check=True,capture_output=True)
    count=len(PdfReader(str(path)).pages)
    files=sorted(target.glob('page-*.png'))[:count]
    for start in range(0,len(files),4):
        thumbs=[]
        for f in files[start:start+4]:
            im=Image.open(f).convert('RGB');im.thumbnail((650,920))
            thumbs.append((f,im.copy()))
        sheet=Image.new('RGB',(1340,1920),'#DCE3E9');draw=ImageDraw.Draw(sheet)
        for j,(f,im) in enumerate(thumbs):
            x=10+(j%2)*670;y=25+(j//2)*950
            draw.text((x,y-17),f'{key} / {f.stem}',fill='black')
            sheet.paste(im,(x,y))
        sheet.save(HERE/f'{key}-sheet-{start//4+1}.png')
    reader=PdfReader(str(path))
    assert all(len(page.extract_text() or '')>100 for page in reader.pages)
    print(key,len(files),'rendered')
