# 원문 충실 학습 노트 편집 계약

원본: C:/Users/user/Downloads/네트워크_하향식.pdf
범위: 1~6장. 외부 지식, 추론, 보충 해설, 새로운 예시 금지.
인쇄 p.170 및 p.280은 첨부에 없음. 6장은 p.475까지.
OCR는 읽기 보조 수단. 오인식된 용어·수식·숫자는 반드시 원문 페이지 이미지에서 확인하고, 확정할 수 없으면 해당 사실 제외 또는 '원문에서 확인 불가'로 처리.

각 담당자는 chapter_N.json 을 현재 폴더에 UTF-8 JSON으로 작성한다. 다음 스키마를 사용한다.

```json
{
  "chapter": 1,
  "title": "원문 장 제목",
  "learning": [FACT],
  "concepts": [{"section":"1.1", "title":"원문 절 제목", "items":[FACT]}],
  "procedures": [{"title":"절차 제목", "section":"1.1", "steps":[FACT]}],
  "formulas": [{"label":"원문 수식 이름", "expression":"원문과 동일한 수식", "section":"1.1", "pages":[1], "evidence":"원문 근거 문구", "note":"원문에 있는 기호 정의만"}],
  "terms": [{"term":"핵심 용어", "definition":FACT}],
  "summary": [FACT],
  "protocols": [{"name":"프로토콜", "layer":FACT_OR_NULL, "role":FACT_OR_NULL, "features":FACT_OR_NULL, "header":FACT_OR_NULL}],
  "review": [{"question":"본문 또는 연습문제 기반 질문", "answer":FACT}],
  "cheat": {"definitions":[{"term":"용어", "definition":FACT}], "comparison_title":"원문 비교 기준", "comparison_headers":["항목","원문 내용"], "comparison_rows":[[FACT,FACT]], "formulas":[{"label":"이름", "expression":"수식", "section":"1.1", "pages":[1], "evidence":"원문 근거", "note":"기호 정의"}]},
  "checked_images":[9,10],
  "editor_notes": ["원문 확인의 한계 또는 실제 생략 여부"]
}
```

FACT 형식: {"text":"한 문장 또는 한 가지 명제", "section":"1.1.1", "pages":[2,3], "evidence":"그 문장을 직접 뒷받침하는 짧은 원문 문구"}.
pages는 항상 책 인쇄 쪽수이다. evidence는 OCR를 교정한 원문 근거 문구이며 각 FACT마다 필수이다. 한 항목에 여러 문장을 섞지 말 것. 층·역할 등 책에 확인되지 않은 프로토콜 셀은 null로 둔다.

장당 권장: learning 2~3개, concepts 각 주요 절 2~5개로 모든 절을 포괄(역사는 시대별 1개), procedures 4~7개(각 2~5단계), formulas 실제 핵심 수식만 4~10개(없는 장은 없음), terms 12~18개, summary 책의 요약 절 근거 4~7개, review 5~7개.
문장을 원문 취지에 충실하게 줄이고 핵심 용어·정의·수식·수치는 그대로 유지한다. 원문에 있는 예시라도 장황한 해설은 제외.
학습 목표는 장 도입부에서 밝힌 범위로만 작성한다. 책이 학습 목표 목록을 따로 제시한다고 주장하지 말 것.
장 요약은 반드시 책의 요약 절에서 확인한 내용에만 근거할 것.
치트시트는 A4 1페이지, 본문 10pt/줄간격 15pt에 맞게 definitions 4~5개, comparison_rows 2~3개, formulas 1~3개로 간결하게 작성한다. 추가 해설 금지.
원문 프로토콜 비교용 데이터는 담당 장의 설명만으로 작성: 1장은 꼭 필요할 때만, 2장은 HTTP/DNS/SMTP/POP3/IMAP, 3장은 UDP/TCP, 4장은 IPv4/IPv6/OpenFlow, 5장은 OSPF/BGP/OpenFlow/ICMP/SNMP, 6장은 Ethernet/ARP/DHCP 등 해당 본문에서 확인된 것만.
모든 내용은 근거 페이지를 직접 확인한다. 특히 정의·수식·숫자·프로토콜 헤더는 이미지로 교차 확인하고 checked_images에 실제 열어 본 PDF 페이지 번호를 기록한다.

입력 chapter_N_ocr.txt 및 chapter_N_pages.json은 OCR 작업 완료 후 생성된다. 원본 페이지 이미지는 images/NNNN.jpg (PDF 1기준 번호), OCR 줄 좌표는 ocr/lines/NNNN.json 이다.
인쇄→PDF 변환: 1~2장 +8, 3장 +7, 4~6장 +6.
편집은 본인이 맡은 chapter_N.json에 한정한다. 최종 PDF 제작은 메인에서 한다.
