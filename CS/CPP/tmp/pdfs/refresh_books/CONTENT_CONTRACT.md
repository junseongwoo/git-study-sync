# Tour C++ · 운영체제 보완 편집

기존 상세 원고는 유지한다. chapters 원본 JSON 수정 금지. 본문은 main이 문장·목록·표·코드별로 근거 ID와 절·인쇄쪽수를 연결하여 새 공통 레이아웃으로 변환한다. 담당자는 보강 overlay만 작성한다. 새내용은 원본 스캔 및 원문 OCR만 사용하고 외부지식·현재 표준·새 예제·실행결과·오류 임의교정 금지.

T 원문: C:/Users/user/Desktop/책/A_Tour_Of_C++.pdf (351면). 원본자료 tmp/pdfs/cpp_tour/{chapters,images,ocr_tesseract,source_map.json}.
O 원문: C:/Users/user/Downloads/ocs.pdf (615면). 원본자료 tmp/pdfs/os_notes/{chapters,images,ocr_tesseract,source_map.json}.
PDF면→인쇄쪽수는 원본 source_map의 개별 대응표를 사용한다. 고정오프셋금지.

담당출력: tmp/pdfs/refresh_books/tour/overlays/NN.json 또는 os/overlays/NN.json.
NN은 기존 chapters 파일번호와 동일. OS02는 실제본문없음,OS16은 진짜16장이 아닌 제7부도입임을 보존.

스키마:
{
 "chapter":1,"title":"기존 장 제목", "source_code":"T 또는 O",
 "learning":[FACT 2~3개],
 "terms":[{"term":"원문 용어","definition":FACT} 6~10개],
 "summary_basis":"원문 요약/조언 절 번호와 제목 또는 편집 요약",
 "summary":[FACT 3~5개],
 "review":[{"question":"원문 개념 확인 질문","answer":FACT} 4개],
 "cheat":{"definitions":[{"term":"원문 용어","definition":FACT} 3개],"comparison_title":"비교","comparison_headers":["구분","책의 설명"],"comparison_rows":[[FACT,FACT] 2~4행],"formulas":[FORMULA 0~2개]},
 "checked_images":[원문PDF면번호],"editor_notes":[],"corrections":[]
}
FACT={"text":"원문에 직접 근거한 한 문장/명제","refs":[{"source":"T 또는 O","section":"실제 원문 절 번호와 제목","pages":[원문PDF면1기준]}],"evidence":"이미지와 대조한 짧은 원문 문구"}
FORMULA={"label":"이름","expression":"원문 수식","note":"원문 조건·기호","refs":[...],"evidence":"원문 문구"}.

새 용어/정의/학습범위/요약/복습/치트의 인용면은 모두 원본 이미지를 직접 확인하고 checked_images에 기록한다. 다른항목에서 FACT를 재사용한다. 범위가짧은장과도입은 항목수를줄여도된다. OS02는 미제공안내: 신규지식추가없이 learning/terms/summary/review/cheat비워두고 본문없음 editor_notes에기록한다.

치트시트는 단원당 A4세로1쪽, 10pt/15pt·21mm여백이므로 과밀하게작성하지않는다. 정의3개(짧게), 비교2~3행, 수식1개가 기본. 코드·별도해설·새예제는치트에넣지않는다. 공식이원문에없으면생략가능. 장말요약이있으면그내용기준, Tour는 조언 절을우선한다. 미제공요약을꾸며내지않는다.

보완검토: 담당기존장JSON의 모든본문을 읽고 대응원문 OCR와대조해 의미/조건/숫자/원문절번호의 명확한문제가있으면 corrections에 기록. 형식은 {"path":["sections",0,"blocks",0,"text"],"before":"기존값","after":"수정값","refs":[...],"reason":"원문위치와수정이유"}. main이복사본에적용한다. 원문내부불일치를외부지식으로고치지않는다. 원문기호·코드·원문의미심장표기는그대로보존또는판독한계표시.

장말요약/조언의 새문장과 정의는 좁은 PDF면 근거를우선한다. 각장완료후파일저장·페이지확인보고, 마지막에담당전체검토보고 JSON 저장. 기존 그림/코드/상세본문은 main이유지한다.
