import json, math, itertools, random, subprocess
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from pypdf import PdfReader
from reportlab.pdfbase.ttfonts import TTFont
import build_guides as bg
HERE=Path(__file__).resolve().parent

# Clarify paths, API snippets and section references before final rendering.
d=json.loads((HERE/'cv.json').read_text(encoding='utf-8'))
d['folder']='CV'
d['audience']='C++ 검사 장비 SW 경험을 비전 알고리즘 검증으로 확장하는 개발자'
(HERE/'cv.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
d=json.loads((HERE/'cpp.json').read_text(encoding='utf-8'))
d['audience']='C++ 기반 장비·머신비전 소프트웨어 개발자'
for s in d['sources']:
    import re
    s['use']=re.sub(r'(\d+)쪽',r'학습단원 \1',s['use'])
for block in d['pages'][2]['blocks']:
    if block['type']=='code' and '#include' not in block['text']:
        block['text']='#include <cstdint>\n#include <variant>\n'+block['text']
(HERE/'cpp.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

assert round(393000*math.tan(math.radians(.001)),2)==6.86
assert round(math.degrees(math.sqrt(2)*5/393000),5)==.00103
assert round(math.sqrt(36-4/3),2)==5.89
assert round(math.sqrt(14)*2,2)==7.48
assert math.ceil(math.log(.05)/math.log(.999))==2995
assert round(-math.expm1(math.log(.05)/100)*100,3)==2.951
assert round(-math.expm1(math.log(.05)/300)*100,3)==.994
assert round(-math.expm1(math.log(.05)/2995)*100,5)==.09997
assert .1*1000*.020==2
assert 2048*2048/1024**2==4
assert (8+2+1)*4==44

def count_hash(a,k):
    freq={0:1};s=ans=0
    for x in a:
        s+=x;ans+=freq.get(s-k,0);freq[s]=freq.get(s,0)+1
    return ans
def brute_count(a,k):
    return sum(sum(a[i:j])==k for i in range(len(a)) for j in range(i+1,len(a)+1))
def shortest(a,k):
    left=s=0;best=len(a)+1
    for right,x in enumerate(a):
        s+=x
        while left<=right and s>=k:
            best=min(best,right-left+1);s-=a[left];left+=1
    return best if best<=len(a) else 0
def brute_short(a,k):
    return min([j-i for i in range(len(a)) for j in range(i+1,len(a)+1) if sum(a[i:j])>=k] or [0])
rng=random.Random(260926)
for _ in range(300):
    arr=[rng.randint(-3,3) for _ in range(rng.randrange(9))];k=rng.randint(-5,5)
    assert count_hash(arr,k)==brute_count(arr,k)
    arr=[rng.randint(1,7) for _ in range(rng.randrange(9))];k=rng.randint(1,25)
    assert shortest(arr,k)==brute_short(arr,k)
assert count_hash([1,-1,3,0],3)==4
assert count_hash([0,0,0],0)==6
assert shortest([2,1,3,2,4],6)==2
assert shortest([1,-1,5],5)==3
assert brute_short([1,-1,5],5)==1
assert [sum(v for l,r,v in [(1,3,2),(2,4,-1)] if l<=i<=r) for i in range(5)]==[0,2,1,1,-1]

font=TTFont('font-audit','C:/Windows/Fonts/malgun.ttf')
cmap=font.face.charToGlyph
for key in ['cpp','cv','coding']:
    d=json.loads((HERE/(key+'.json')).read_text(encoding='utf-8'))
    s=bg.normalize(json.dumps(d,ensure_ascii=False))
    missing=sorted({c for c in s if ord(c)>32 and ord(c) not in cmap})
    if missing: print('MISSING_GLYPHS',key,repr(missing))
print('Numeric examples and 600 algorithm cross-checks passed; C++ not compiled.')
