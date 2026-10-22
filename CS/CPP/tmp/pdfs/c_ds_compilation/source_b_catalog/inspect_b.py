import fitz,pathlib
from PIL import Image,ImageOps,ImageDraw
d=fitz.open(r'C:\Users\user\Downloads\C언어_자료구조_알고리즘.pdf')
out=pathlib.Path(__file__).parent
nums=[12,14,26,27,28,29,31,76,77,78,80,119,120,121,123,147,148,149,151,203,204,205,206,208,238,239,240,242,307,308,309,310,311,312,331,332,333,334,335,336,337,338,339,340,375,376,377,378,379,380,381,382,451,452,453,454,455,456,457,458,491,492,493,494,495,496,497,498,499,500,519,520,521,522,523,524,544,545,546,547,548,549,550,551,568,569,570,571,572,573,574,599,600,601,602,603,604,605,606,636]
can=Image.new('RGB',(1600,((len(nums)+3)//4)*110),'white')
dr=ImageDraw.Draw(can)
for j,n in enumerate(nums):
    p=d[n-1]
    px=p.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(0,p.rect.height-65,p.rect.width,p.rect.height))
    im=Image.frombytes('RGB',[px.width,px.height],px.samples)
    can.paste(ImageOps.contain(im,(390,90)),((j%4)*400,(j//4)*110+20))
    dr.text(((j%4)*400,(j//4)*110),str(n),fill='black')
can.save(out/'footers.jpg')
print('done')
