import pathlib,json
R=pathlib.Path(__file__).parent
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
samples={
5:[('A',[184],'insert_first의 할당→data→link→head→반환 순서'),('A',[214],'head가 마지막 노드를 가리키는 조건에서 처음·끝 상수시간 삽입'),('B',[35],'노드 삭제와 소멸의 구분')],
6:[('A',[118],'후위식 계산의 second 먼저 pop, first op second 순서'),('A',[129],'미로의 위·아래·왼쪽·오른쪽 push와 공백 실패 조건'),('B',[92],'A와 다른 List=head, Top=tail의 연결스택 구현')],
7:[('A',[146],'원형큐 front가 첫 요소 직전, rear가 마지막인 전제'),('A',[150],'한 칸 비우는 구현의 공백·포화 수식'),('B',[132,133],'B의 Front는 실제전단, Rear는 다음삽입위치이며 wrap처리 확인')],
8:[('A',[252],'루트레벨1 기준 최소·최대 노드수와 높이 올림식'),('B',[154],'B의 깊이0·레벨집합·높이최대깊이 정의'),('A',[283],'스레드 포인터·자식 포인터 구분 태그 필요')],
9:[('A',[502],'AVL 정의·균형인수 부호·O(logn) 조건'),('B',[281],'부모가 왼쪽자식인 삽입복구의 좌회전과 우회전 분기'),('B',[289],'왼쪽 이중흑색의 형제 오른쪽 빨간자식 경우 및 루트종료')],
10:[('A',[321],'루트 인덱스1의 자식2i/2i+1·부모i/2'),('B',[318],'루트 인덱스0의 자식2k+1/2k+2·부모몫'),('A',[342],'A 허프만 간선은 왼쪽1·오른쪽0임을 그대로 보존')],
16:[('B',[466],'카프–라빈 최초·롤링 해시식의 제곱·괄호·mod q'),('B',[476],'KMP 이동거리=일치접두길이−최대경계너비'),('B',[481],'보이어–무어 비교방향과 이동방향 및 큰 이동 선택')],
17:[('B',[534],'거듭제곱 짝수·홀수 분기와 O(log₂n)'),('B',[539],'피보나치 행렬 항의 위치·거듭제곱과 Θ(2ⁿ)/Θ(log₂n)')],
18:[('B',[549],'최적부분구조·부분문제 의존·Bottom-Up 및 저장'),('B',[556],'LCS 빈 행열·점화식3경우·(i+1)×(j+1)'),('B',[560],'왼쪽위→오른쪽아래 채우기와 최악 O(nm)')],
19:[('B',[571],'탐욕의 최적해 비보장·최적부분구조 전제·3단계'),('B',[585],'B 허프만 간선은 왼쪽0·오른쪽1로 A와 구분'),('B',[589],'aaabaacdd의 72비트→15비트 및 압축해제 비트방향')],
20:[('B',[614],'미로 북→남→동→서 시도 순서'),('B',[623],'64C8 후보해·실제92해·N크기 설명'),('B',[630],'퀸 열검사·대각선 절댓값식·수평검사 제외 조건')]
}
items=[];errors=[];all_pages=set()
for n,checks in samples.items():
    j=json.loads((R/f'unit_{n:02}.json').read_text('utf8'))
    declared={c['source']:set(c['pages']) for c in j['checked_images']}
    refs=0;core=sum(len(c['items']) for c in j['concepts'])
    for x in walk(j):
        if 'refs' not in x:continue
        refs+=1
        if not x.get('evidence'):errors.append({'unit':n,'kind':'empty evidence'})
        for ref in x['refs']:
            if not ref.get('section'):errors.append({'unit':n,'kind':'empty section'})
            for p in ref['pages']:
                if not isinstance(p,int) or p<1 or p>dict(A=562,B=636)[ref['source']]:errors.append({'unit':n,'kind':'invalid PDF page','ref':ref})
                if p not in declared.get(ref['source'],set()):errors.append({'unit':n,'kind':'undeclared visual check','ref':ref})
                if not (R/f"{ref['source']}_images"/f'{p:04}.jpg').exists():errors.append({'unit':n,'kind':'missing source image','ref':ref})
    samples_out=[]
    for s,ps,topic in checks:
        for p in ps:all_pages.add((s,p))
        samples_out.append({'source':s,'pdf_pages':ps,'check':topic,'result':'원본 스캔 이미지와 일치','correction':None})
    items.append({'unit':n,'title':j['title'],'core_statements_reviewed_for_scope':core,'reference_objects_checked':refs,'all_topic_reference_structure':'절·PDF면·원본이미지 존재 및 작성자의 이미지확인 기록 검증','independent_image_samples':samples_out})
report={'reviewer':'independent content review','units':list(samples),'method':'각 단원의 모든 핵심 주제 목록과 출처 위치·전제 보존 여부를 읽고, 까다로운 정의·수식·절차를 단원당 2~3개 골라 원본 스캔 이미지로 독립 대조했다. 전체 참조 객체의 원본면·절·근거 구절·이미지확인 기록 존재를 검사했다. 모든 문장을 새로 독립 검증했다는 의미는 아니다.','sample_count':sum(len(v) for v in samples.values()),'source_image_page_count':len(all_pages),'sample_images':[{'source':s,'pdf_page':p} for s,p in sorted(all_pages)],'units_reviewed':items,'reference_structure_errors':errors,'substantive_errors_found':[],'direct_json_corrections':[],'result':'검토한 원고와 독립 이미지 표본에서 수정이 필요한 오류를 발견하지 못함','preserved_distinctions':['A/B 원형큐의 Front/Rear 정의가 다름','A/B 트리의 레벨·깊이·높이 정의가 다름','A/B 히프의 루트 배열 인덱스가 다름','A 허프만 왼쪽1·오른쪽0, B 허프만 왼쪽0·오른쪽1을 각각 보존','레드 블랙 회전·색 복구는 부모·형제의 방향 전제 포함']}
(R/'independent_content_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('samples',report['sample_count'],'pages',len(all_pages),'errors',errors)
assert not errors
