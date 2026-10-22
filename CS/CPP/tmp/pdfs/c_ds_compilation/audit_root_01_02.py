import json
from pathlib import Path

ROOT=Path(__file__).parent
checked={
 1:{'A':[7,9,10,11,12,13,14,15],'B':[14,15,16,17]},
 2:{'A':[63,64,65,66,69,72,75,77,78,80,82,83,84,85,88],'B':[19,20,21,22,23,24,25]},
}
report={'reviewer':'c_ds_catalog_a','method':'모든 고유 인용 PDF 면의 원본 스캔 이미지를 직접 열어 문장·용어·표·코드·수식을 대조하였다. OCR는 위치 탐색 보조로만 사용하였다.','units':[], 'additional_checked_images':[{'source':'B','pages':[18]}]}

for n in [1,2]:
    path=ROOT/f'unit_{n:02d}.json'
    u=json.loads(path.read_text(encoding='utf8'))
    changes=[]
    if n==1:
        for f in u['formulas']+u['cheat']['formulas']:
            if f.get('label')=='그림 1-2·1-3의 프로그램 구성':
                f['label']='그림 1-3의 프로그램 구성'
        changes.append({'kind':'label','before':'그림 1-2·1-3의 프로그램 구성','after':'그림 1-3의 프로그램 구성','reason':'인용 면 A PDF9에서 직접 확인한 그림 번호는 1-3이다. 수식 내용은 변경하지 않았다.','refs':[{'source':'A','pages':[9]}]})
    else:
        old='배열의 첫 요소를 가리키는 포인터에 ++를 적용하면 기반 데이터 형식의 크기만큼 주소가 증가하여 다음 요소를 가리킨다.'
        new='원문의 int 배열에서 첫 요소를 가리키는 포인터 ptr에 ++를 적용하면 int의 크기만큼 주소가 증가하여 다음 요소를 가리킨다.'
        changes.append({'kind':'condition','before':old,'after':new,'reason':'인용 면 B PDF19의 직접 서술은 int 배열과 ptr의 예제이므로 그 조건을 문장에 복원했다.','refs':[{'source':'B','pages':[19]}]})
    evidence_fixes={
        '매개변숴 반환형':'매개 변수, 반환형',
        '자료구조가 갖취야 할 일련의 연산':'자료구조가 갖춰야 할 일련의 연산',
        '메모리의 당비':'메모리의 낭비',
        '각 항의 치수를 비교':'각 항의 차수를 비교',
    }
    unique={}
    used={}
    def walk(x,p='$'):
        if isinstance(x,dict):
            if n==2 and x.get('text')==old:
                x['text']=new
                x['evidence']='ptr은 int의 크기만큼 더해진 주소값'
            if x.get('evidence') in evidence_fixes:
                prev=x['evidence'];x['evidence']=evidence_fixes[prev]
                if not any(c.get('before')==prev for c in changes):
                    changes.append({'kind':'evidence_ocr_typo','before':prev,'after':x['evidence'],'reason':'원본 이미지에 보이는 문구로 OCR 오탈자만 수정했다. 본문 명제는 변경하지 않았다.','refs':x.get('refs',[])})
            if 'refs' in x:
                content=x.get('text',x.get('code',x.get('expression','')))
                key=json.dumps([content,x['refs']],ensure_ascii=False,sort_keys=True)
                e=unique.setdefault(key,{'content':content,'refs':x['refs'],'occurrences':[],'status':'원본 이미지 대조 확인'})
                e['occurrences'].append(p)
                for ref in x['refs']:
                    used.setdefault(ref['source'],set()).update(ref['pages'])
            for k,v in x.items():walk(v,f'{p}.{k}')
        elif isinstance(x,list):
            for i,v in enumerate(x):walk(v,f'{p}[{i}]')
    walk(u)
    for s,ps in used.items():
        assert ps<=set(checked[n][s]),(n,s,sorted(ps-set(checked[n][s])))
    u['checked_images']=[{'source':s,'pages':ps} for s,ps in checked[n].items()]
    if n==2:
        u['editor_notes'].append('B의 포인터 증감 설명은 원문의 int 배열 예제 조건을 유지하였다.')
    path.write_text(json.dumps(u,ensure_ascii=False,indent=2),encoding='utf8')
    report['units'].append({'unit':n,'file':path.name,'status':'전체 refs 원본 이미지 대조 완료','checked_images':u['checked_images'],'unique_cited_records':len(unique),'changes':changes,'records':list(unique.values())})

report['swap_check']={'source':'A','pdf_page':84,'printed_page':91,'status':'원문과 일치','detail':'프로그램 3.6의 void swap(int *px, int *py), int tmp, tmp = *px, *px = *py, *py = tmp를 원본 이미지로 확인했다. JSON 발췌의 차이는 들여쓰기뿐이며 식별자·포인터·대입 순서는 일치한다.','code':'void swap(int *px, int *py)\n{\n    int tmp;\n    tmp = *px;\n    *px = *py;\n    *py = tmp;\n}'}
report['remaining_unsupported_records']=[]
(ROOT/'root_01_02_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('saved unit_01.json, unit_02.json, root_01_02_review.json')
