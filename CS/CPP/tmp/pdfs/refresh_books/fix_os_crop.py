from pathlib import Path
import json
from PIL import Image

root=Path(__file__).resolve().parent
book=root/'os'
chapter=json.loads((book/'chapters/11.json').read_text('utf-8-sig'))
index=next(i for i,f in enumerate(chapter['figures']) if f['id']=='O11-F04')
figure=chapter['figures'][index]
out=book/'assets/O11-F04.png'
out.parent.mkdir(exist_ok=True)
bbox=[350,189,1340,1281]
Image.open(figure['crop']['image']).crop(bbox).save(out)
path=book/'overlays/11.json'
overlay=json.loads(path.read_text('utf-8-sig'))
overlay.setdefault('corrections',[])
for field,before,after in [('file',figure['file'],str(out)),('crop',figure['crop'],dict(image=figure['crop']['image'],bbox=bbox))]:
    correction={'path':['figures',index,field],'before':before,'after':after,'refs':[{'source':'O','section':'11.8.4 RAID 수준','pages':[463]}],'reason':'원문 그림 오른쪽 mirror와 캡션 1+0을 보존하도록 발췌 범위를 확장했다.'}
    if correction not in overlay['corrections']:overlay['corrections'].append(correction)
path.write_text(json.dumps(overlay,ensure_ascii=False,indent=2),'utf-8')
print(out)
