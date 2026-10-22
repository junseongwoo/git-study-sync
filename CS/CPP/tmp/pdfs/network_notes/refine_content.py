from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
p=ROOT/'chapter_1.json'
c=json.loads(p.read_text(encoding='utf-8'))

def fact(text,evidence):
    return {'text':text,'section':'1.5.1','pages':[46],'evidence':evidence}

# The requested cheat sheet comparison is a protocol comparison.
# Both services are explicitly described on the same verified source page.
c['cheat']['comparison_title']='TCP와 UDP의 서비스'
c['cheat']['comparison_headers']=['프로토콜','책에 나온 서비스']
c['cheat']['comparison_rows']=[
    [fact('TCP','TCP'),fact('연결지향형 서비스로 메시지 전달 보장, 흐름제어와 혼잡제어를 제공한다.','TCP는 애플리케이션에게 연결지향형 서비스를 제공한다. / 전달 보장과 흐름제어 / 혼잡제어 기능을 제공하여')],
    [fact('UDP','UDP'),fact('비연결형 서비스로 신뢰성, 흐름제어, 혼잡제어를 제공하지 않는다.','UDP 프로토콜은 애플리케이션에 비연결형 서비스를 제공한다. / 신뢰성, 흐름제어, 혼잡제어를 제공하지 않는')]
]
if 54 not in c['checked_images']:
    c['checked_images'].append(54)
    c['checked_images'].sort()
p.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
print('Chapter 1 cheat protocol comparison verified against printed p.46.')
