import json, heapq, itertools
from pathlib import Path
import pdfplumber
from pypdf import PdfReader
from reportlab.pdfbase.ttfonts import TTFont
import build_guides as bg

roots={'cpp':bg.VAULT/'CS/CPP','cv':bg.VAULT/'CV','coding':bg.VAULT/'코테준비'}
font=TTFont('final-font','C:/Windows/Fonts/malgun.ttf')
for key,path in bg.OUTPUTS.items():
    d=json.loads((bg.HERE/(key+'.json')).read_text(encoding='utf-8'))
    glyphs={c for c in bg.normalize(json.dumps(d,ensure_ascii=False)) if ord(c)>32}
    assert not [c for c in glyphs if ord(c) not in font.face.charToGlyph]
    for e in d['evidence']: assert (roots[key]/e['path']).is_file(),e['path']
    r=PdfReader(str(path))
    assert len(r.pages)=={'cpp':14,'cv':13,'coding':13}[key]
    links=sum(len(p.get('/Annots',[])) for p in r.pages)
    assert links>=len(d['sources'])
    with pdfplumber.open(path) as pdf:
        for i,p in enumerate(pdf.pages):
            assert p.chars
            assert not [x for x in p.chars if x['x0']<0 or x['x1']>p.width+.1 or x['top']<0 or x['bottom']>p.height+.1]
    print(key, len(r.pages), 'pages;', path.stat().st_size,'bytes; font, links, bounds OK')

g=[[(1,7),(2,2)],[],[(1,1)]]
dist=[10**9]*3;dist[0]=0;q=[(0,0)]
while q:
    du,u=heapq.heappop(q)
    if du!=dist[u]:continue
    for v,w in g[u]:
        if du+w<dist[v]:dist[v]=du+w;heapq.heappush(q,(dist[v],v))
assert dist==[0,3,2]
parent=list(range(4))
def find(a):
    while a!=parent[a]:a=parent[a]
    return a
cost=0;edges=0
for w,a,b in sorted([(1,0,1),(2,1,2),(5,0,2),(3,2,3)]):
    a=find(a);b=find(b)
    if a!=b:parent[b]=a;cost+=w;edges+=1
assert (cost,edges)==(6,3)
def partition(a,m):
    def feasible(c):
        used=1;s=0
        for x in a:
            if s+x>c:used+=1;s=0
            s+=x
        return used<=m
    lo=max(a);hi=sum(a)
    while lo<hi:
        mid=(lo+hi)//2
        if feasible(mid):hi=mid
        else:lo=mid+1
    return lo
for a,m,answer in [([4,2,3],2,5),([4,2,3],1,9),([4,2,3],3,4),([7],5,7),([2,2,2,2],3,4)]:
    assert partition(a,m)==answer
def knap(items,cap,unlimited=False):
    dp=[0]*(cap+1)
    for weight,value in items:
        for w in (range(weight,cap+1) if unlimited else range(cap,weight-1,-1)):
            dp[w]=max(dp[w],dp[w-weight]+value)
    return dp[cap]
assert knap([(2,3)],4)==3
assert knap([(2,3)],4,True)==6
assert knap([(2,3),(3,4)],5)==7
assert knap([(2,3),(3,4)],1)==0
print('Remaining graph, partition and DP examples verified via Python; no C++ compilation claimed.')
