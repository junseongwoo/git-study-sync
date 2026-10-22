import pathlib,sys
from PIL import Image,ImageOps,ImageDraw
root=pathlib.Path(__file__).parent.parent
label=sys.argv[1]; src=sys.argv[2]; nums=[int(s) for s in sys.argv[3].split(',')]
out=root/'checked_contacts';out.mkdir(exist_ok=True)
for a in range(0,len(nums),4):
    can=Image.new('RGB',(1640,2340),'#ddd');dr=ImageDraw.Draw(can)
    for j,n in enumerate(nums[a:a+4]):
        im=Image.open(root/f'{src}_images'/f'{n:04}.jpg').convert('RGB')
        im=ImageOps.contain(im,(800,1120))
        can.paste(im,((j%2)*820,(j//2)*1170+35))
        dr.text(((j%2)*820+10,(j//2)*1170+10),f'{src} PDF {n}',fill='black')
    path=out/f'{label}_{src}_{a//4+1:02}.jpg';can.save(path,quality=92)
    print(path)
