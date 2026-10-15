# Content contract
All content must come ONLY from local source PDF C:/Users/user/Desktop/책/sql전문가가이드.pdf (786 scanned pages). No internet SQL references. OCR may have errors; source images in images/NNNN.jpg and OCR in ocr/NNNN.txt. Cite absolute PDF page numbers, not printed book pages, explicitly. Use Korean clear paraphrases with enough details, principles, conditions, exceptions. Important SQL examples must be transcribed faithfully (formatting only), verified against original images. Do not fix an apparent source SQL error silently; explain source context. No invented queries, results, problems, theories.

One UTF-8 JSON file per chapter in chapters/ sorted by order. Schema:
{
 "id":"I-1", "order":1, "part":"과목 I. 데이터 모델링의 이해", "title":"제1장 데이터 모델링의 이해", "source_range":"원문 PDF 9-78쪽", 
 "overview":{"topics":["핵심 주제/반드시 이해할 개념"],"flow":["개념→과정 등 논리 흐름"],"focus":["학습 집중사항"]},
 "sections":[{"title":"제1절 데이터 모델의 이해", "source_pages":"원문 PDF 10-32쪽", "blocks":[{"type":"p","text":"설명"},{"type":"bullets","items":["한 항목"]},{"type":"table","headers":["열1","열2"],"rows":[["셀","셀"]]}]}],
 "key_points":["반드시 기억할 사항"], "final_summary":["장 최종 요약을 읽고 관계까지 회상할 수 있게"],
 "codes":[{"id":"I1-C01", "title":"원문 코드가 보여주는 개념", "source_pdf_pages":[100], "sql":"원문 쿼리", "purpose":"수행 작업", "keywords":[{"term":"SELECT","role":"역할"}],"process":["원문에 제시된 처리 설명"],"result":"원문에서 확인되는 결과/설명만. 수치결과 미제공시 그 사실을 간단히", "learn":["반드시 이해할 내용"]}],
 "comparisons":[{"title":"개념 비교","headers":["기준","A","B"],"rows":[["역할","내용","내용"]]}],
 "checklist":["핵심개념을 이해했는지 확인할 항목. 새 문제 생성 금지"],
 "coverage":[{"section":"원문 절명","source_pdf_pages":"range","covered_topics":["실제 읽은 하위주제"]}]
}

Use multiple short paragraphs and specific subheadings as block type p with bold-like leading words if needed, but avoid raw Markdown. Tables are plain text. For detailed notes target approximately 100-180 final PDF pages total across all12 chapters: sufficiently detailed summaries, NOT short outlines. Keep every original numbered section, and within section cover all major subheadings/concepts including conditions/exceptions/important cases. Remove repetitive explanations. Each chapter roughly 5,000-12,000 Korean characters of detailed prose depending size, SQL-heavy chapters may be larger. A large 140-page source chapter should get 12k-20k characters or more if needed. Minimum 1 good explanatory paragraph per distinct core concept; avoid telegraphic noun strings. SQL examples ~4-12 per SQL-heavy chapter, prioritizing distinct syntax/concepts over repetition. No need to recreate all exercise problems. Incorporate their topic emphasis only when grounded in explanatory body. No cover matter/author/publication details. Scope excludes appendices absent from source file.

Chapter order:
1 I-1 데이터 모델링의 이해
2 I-2 데이터 모델과 SQL
3 II-1 SQL 기본
4 II-2 SQL 활용
5 II-3 관리 구문
6 III-1 SQL 수행 구조
7 III-2 SQL 분석 도구
8 III-3 인덱스 튜닝
9 III-4 조인 튜닝
10 III-5 SQL 옵티마이저
11 III-6 고급 SQL 튜닝
12 III-7 Lock과 트랜잭션 동시성 제어
