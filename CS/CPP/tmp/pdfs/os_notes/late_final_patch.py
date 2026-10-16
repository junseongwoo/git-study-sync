import json
from pathlib import Path
B=Path(__file__).resolve().parent
def load(n): return json.loads((B/'chapters'/f'{n:02}.json').read_text(encoding='utf8'))
def save(n,d): (B/'chapters'/f'{n:02}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def section(d,n): return next(s for s in d['sections'] if s['number']==n)
def para(s): return {'type':'p','text':s}

d=load(11)
d['verification']['visually_checked_pdf_pages']=sorted(set(d['verification']['visually_checked_pdf_pages']+[457,459]))
d['verification']['notes'].append('추가 이미지 대조: PDF457의100,000/100=1,000시간, PDF459의(i mod n)+1 스트라이핑식. 모든 원문 수식은 계산 결과를 새로 생성하지 않았다.')
save(11,d)

d=load(13)
section(d,'13.5.1')['blocks'].insert(2,para('원문의 기록 시점 설명에서는 일반적으로 파일을 닫을 때 메모리 이미지의 변경을 파일에 반영하고 가상 주소의 사상을 제거한다. 메모리 부족으로 공간을 확보할 때는 변경을 잃지 않도록 스왑 공간에 반영한다고 설명한다. 이 처리와 공유 프로세스가 같은 물리 페이지의 변경을 보는 시점은 별개의 관계이다.'))
section(d,'13.2.2')['blocks'].insert(2,{'type':'table','headers':['원문의 순차 연산','직접 접근으로의 구현'],'rows':[['reset','cp = 0;'],['read next','read cp; 이후 cp = cp+1'],['write next','write cp; 이후 cp = cp+1']]})
section(d,'13.2.2')['blocks'].insert(3,para('그림 13.5의 cp는 현재 위치이다. 직접 접근에 현재 위치 추적을 더하면 다음 레코드 순서로 처리할 수 있음을 보이는 원문의 표를 정리했다. 이는 별도의 새 알고리즘이 아니다.'))
d['verification']['visually_checked_pdf_pages']=sorted(set(d['verification']['visually_checked_pdf_pages']+[529]))
d['verification']['notes'].append('추가 대조: PDF529의고정레코드주소L×N식과0부터세는조건, PDF530의cp기반순차접근표를확인했다.')
save(13,d)

d=load(15)
section(d,'15.8.5')['blocks'].insert(1,para('원문의 수치 사례에서 속성 캐시는 기본 60초 뒤 버리며, 한 기계에서 만든 새 파일은 다른 기계에서 30초 동안 보이지 않을 수 있다고 설명한다. 이 수치는 본문의 NFS 구현·성능 조정 사례를 그대로 기록한 것이며 모든 버전과 설정의 공통값이라는 의미로 사용하지 않는다.'))
d['verification']['visually_checked_pdf_pages']=sorted(set(d['verification']['visually_checked_pdf_pages']+[611,612]))
d['verification']['notes'].append('추가 대조: PDF611의속성캐시60초와PDF612의새파일가시성30초를이미지로확인했다.')
save(15,d)

for n in range(11,16):
    d=load(n)
    for s in d['sections']:
        for b in s['blocks']:
            b.setdefault('source',s['source'])
    save(n,d)
