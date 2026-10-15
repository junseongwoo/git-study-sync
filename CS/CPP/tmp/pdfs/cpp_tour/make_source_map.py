from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent
out=[]
for p in range(1,352):
    j=json.loads((ROOT/'ocr'/'lines'/f'{p:04d}.json').read_text(encoding='utf-8'))
    lines=[l['text'] for l in j['lines'] if min([w['y'] for w in l['words']],default=0)>j['height']*.89]
    out.append(f'{p:04d}: '+' | '.join(lines))
(ROOT/'footer_numbers.txt').write_text('\n'.join(out),encoding='utf-8')

def printed(p):
    if 1<=p<=12:return p+358
    if 13<=p<=17:return None
    if 18<=p<=88:return p+1
    if 89<=p<=137:return p+2
    if 138<=p<=284:return p+3
    if 285<=p<=320:return p+5
    if 321<=p<=339:return p+6
    if 340<=p<=351:return p+7

chapters=[
 (1,'기초',19,48,[(1,'소개',20),(2,'프로그램',20),(3,'함수',23),(4,'타입과 변수, 산술 연산',26),(5,'스코프와 수명',31),(6,'상수',32),(7,'포인터, 배열, 참조',34),(8,'조건 테스트',39),(9,'하드웨어 대응',42),(10,'조언',46)]),
 (2,'사용자 정의 타입',49,60,[(1,'소개',49),(2,'구조체',50),(3,'클래스',53),(4,'공용체',55),(5,'열거형',57),(6,'조언',59)]),
 (3,'모듈화',61,89,[(1,'소개',61),(2,'분할 컴파일',63),(3,'모듈(C++20)',66),(4,'네임스페이스',68),(5,'에러 처리',71),(6,'함수 인자와 반환 값',81),(7,'조언',88)]),
 (4,'클래스',91,118,[(1,'소개',91),(2,'구체 타입',93),(3,'추상 타입',102),(4,'가상 함수',107),(5,'클래스 계층 구조',108),(6,'조언',117)]),
 (5,'필수적인 연산',119,139,[(1,'소개',119),(2,'복사와 이동',124),(3,'자원 관리',131),(4,'관례적인 연산',133),(5,'조언',138)]),
 (6,'템플릿',141,162,[(1,'소개',141),(2,'파라미터화된 타입',142),(3,'파라미터화된 연산',149),(4,'템플릿 메커니즘',157),(5,'조언',161)]),
 (7,'컨셉과 제네릭 프로그래밍',163,182,[(1,'소개',163),(2,'컨셉(C++20)',164),(3,'제네릭 프로그래밍',172),(4,'가변 템플릿',176),(5,'템플릿 컴파일 모델',181),(6,'조언',182)]),
 (8,'라이브러리의 개요',183,188,[(1,'소개',183),(2,'표준 라이브러리 구성 요소',184),(3,'표준 라이브러리 헤더와 네임스페이스',186),(4,'조언',188)]),
 (9,'문자열과 정규 표현식',189,208,[(1,'소개',189),(2,'문자열',190),(3,'문자열 뷰',194),(4,'정규 표현식',197),(5,'조언',207)]),
 (10,'입력과 출력',209,232,[(1,'소개',210),(2,'출력',211),(3,'입력',213),(4,'입출력 상태',215),(5,'사용자 정의 타입의 입출력',217),(6,'형식화',219),(7,'파일 스트림',221),(8,'문자열 스트림',222),(9,'C 스타일 입출력',223),(10,'파일 시스템',224),(11,'조언',230)]),
 (11,'컨테이너',233,252,[(1,'소개',234),(2,'vector',234),(3,'list',241),(4,'map',244),(5,'unordered_map',245),(6,'컨테이너 개요',248),(7,'조언',251)]),
 (12,'알고리즘',253,274,[(1,'소개',254),(2,'반복자의 사용',255),(3,'반복자 타입',259),(4,'스트림 반복자',261),(5,'술어',263),(6,'알고리즘 요약',264),(7,'컨셉(C++20)',266),(8,'컨테이너 알고리즘',272),(9,'병렬 알고리즘',273),(10,'조언',274)]),
 (13,'유틸리티',275,314,[(1,'소개',276),(2,'자원 관리',276),(3,'구간 검사: gsl::span',284),(4,'특수한 컨테이너',287),(5,'선택지',295),(6,'할당자',300),(7,'시간',302),(8,'함수 어댑션',303),(9,'타입 함수',306),(10,'조언',312)]),
 (14,'수치',315,325,[(1,'소개',316),(2,'수학 함수',316),(3,'수치 알고리즘',318),(4,'복소수',320),(5,'난수',321),(6,'벡터 산술',323),(7,'수치 한계',324),(8,'조언',325)]),
 (15,'동시성',327,345,[(1,'소개',327),(2,'태스크와 thread',328),(3,'인자 전달',330),(4,'결과 반환',331),(5,'데이터 공유',333),(6,'이벤트 대기',335),(7,'태스크 간 통신',338),(8,'조언',343)]),
 (16,'역사와 호환성',347,370,[(1,'역사',347),(2,'C++ 기능의 진화',359),(3,'C/C++ 호환성',365),(4,'참고 자료',370),(5,'조언',376)]),
]
page_records=[]
for p in range(1,352):
    pn=printed(p)
    text=(ROOT/'ocr'/f'{p:04d}.txt').read_text(encoding='utf-8')
    candidates=[]
    for line in text.splitlines():
        if re.match(r'^\d{1,2}[.]\d{1,2}(?:[.]\d{1,2})*\s+[^0-9]',line):candidates.append(line)
    page_records.append({'pdf_page':p,'printed_page':pn,'type':'toc' if pn is None else 'body','chapter':next((ch[0] for ch in chapters if pn is not None and ch[2]<=pn<=ch[3]),None),'image':f'images/{p:04d}.jpg','winrt_ocr':f'ocr/{p:04d}.txt','tesseract_ocr':f'ocr_tesseract/{p:04d}.txt','ocr_heading_candidates':candidates,'winrt_chars':len(text)})
chapter_records=[]
for n,title,start,end,sections in chapters:
    pages=sorted([r for r in page_records if r['chapter']==n],key=lambda r:r['printed_page'])
    chapter_records.append({'chapter':n,'title':title,'printed_start':start,'printed_end_provided':end,'pdf_pages_in_reading_order':[r['pdf_page'] for r in pages],'sections':[{'section':f'{n}.{s}','title':t,'printed_page':p,'pdf_page':next((r['pdf_page'] for r in page_records if r['printed_page']==p),None),'status':'provided' if p<=370 else 'not_provided'} for s,t,p in sections]})
mapping={'source_pdf':'C:/Users/user/Desktop/책/A_Tour_Of_C++.pdf','pdf_pages':351,'verified_toc_images':[13,14,15,16,17],'source_title':None,'source_author':None,'metadata_note':'표지·표제지·판권지·지은이 소개가 없으므로 정확한 책 제목·저자명은 직접 확인 불가. 파일명으로 제목을 확정하지 않음.','printed_range_available':[19,370],'missing_printed_pages_within_range':[90,140,288,289,326,346],'missing_note':'90·140·326·346은 장 경계에 있으나 빈 페이지인지는 확인 불가. 288·289는 13.4 설명 중간에서 누락. 371 이후 참고 자료 나머지, 16.5 조언(목차376쪽), 찾아보기(목차378쪽)는 미제공.','chapters':chapter_records,'pages':page_records}
(ROOT/'source_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
for engine in ['ocr','ocr_tesseract']:
    dest=ROOT/'chapters'/engine;dest.mkdir(parents=True,exist_ok=True)
    full=[]
    for ch in chapter_records:
        parts=[]
        for p in ch['pdf_pages_in_reading_order']:
            f=ROOT/engine/f'{p:04d}.txt'
            if not f.exists():continue
            parts.append(f'\n\n===== 인쇄 {printed(p)}쪽 / PDF {p}쪽 =====\n'+f.read_text(encoding='utf-8'))
        (dest/f'ch{ch["chapter"]:02d}.txt').write_text(''.join(parts),encoding='utf-8')
        full.extend(parts)
    (ROOT/f'{engine}_all_in_book_order.txt').write_text(''.join(full),encoding='utf-8')
print(json.dumps({'winrt_pages':len(list((ROOT/'ocr').glob('*.txt'))),'tesseract_pages':len(list((ROOT/'ocr_tesseract').glob('*.txt'))),'chapters':len(chapter_records),'mapping':str(ROOT/'source_map.json')},ensure_ascii=False))
