import json
from pathlib import Path
H=Path(__file__).resolve().parent
chapters=[json.loads(p.read_text(encoding='utf-8-sig')) for p in sorted((H/'chapters').glob('*.json'))]
old=json.loads((H/'book_info.json').read_text(encoding='utf-8')) if (H/'book_info.json').exists() else {}
info={
 'confirmed_title':old.get('confirmed_title','[원문에서 확인할 수 없음]'),
 'title_note':old.get('title_note',''),
 'author':'[원문에서 확인할 수 없음]',
 'scope_note':'제공된 351쪽 스캔 PDF에서 실제로 확인한 1~16장의 내용을 원래 장·절 순서로 재구성한 학습 교재다. 원본 책 전체의 완전한 요약이라고 표시하지 않는다. 원문만을 내용 출처로 삼았으며, 원문 속 인용 자료나 인터넷 자료로 설명을 보충하지 않았다.',
 'source_pages':351,
 'available_range':'원문 목차 5쪽과 인쇄 19~370쪽 중 제공된 346쪽. 중간 누락과 마지막 미제공 부분은 아래에 구별한다.',
 'limitations':[
  ('표지·표제지·판권지·지은이 소개가 제공되지 않았다. 책 제목은 사용자가 확인한 A Tour of C++를 반영했다. 저자명은 원문에서 확인할 수 없어 기재하지 않았다.' if old.get('confirmed_title') == 'A Tour of C++' else '표지·표제지·판권지·지은이 소개가 제공되지 않았다. 정확한 책 제목과 저자명은 원문에서 확인할 수 없다. 파일명이나 일반 지식으로 확정하지 않았다. 표지의 확인 불가 표시는 이 제한을 나타낸다.'),
  '인쇄 90·140·288·289·326·346쪽은 제공 파일에 없다. 장 경계에 있는 쪽도 빈 페이지라고 추정하지 않았다.',
  '인쇄 288~289쪽은 13.4 특수 컨테이너 설명 중간에서 누락됐다. 해당 부분의 코드·정의·결과를 임의 복원하지 않았다.',
  '인쇄 371쪽 이후는 제공되지 않았다. 16.4 참고 자료의 나머지, 16.5 조언 본문(목차상 376쪽), 원본 찾아보기(목차상 378쪽)를 읽거나 요약한 것으로 표시하지 않는다.',
  '제공 PDF 1~12쪽은 원문 인쇄 359~370쪽이다. 이 부분을 인쇄 347~358쪽 뒤에 배치해 원래 16장의 흐름을 복원했다.',
  'OCR은 독서 보조로 사용했다. 수록한 대표 코드는 원문 이미지와 대조했으며, 의심되는 원문 표기와 판독 한계는 해당 위치에 표시했다. 나머지 모든 문자에 대해 완전한 전사 정확성을 보증하는 것은 아니다.',
  '원문의 C++11·14·17 관련 설명과 C++20·모듈·컨셉·Ranges TS 등에 대한 당시의 예정·실험적 상태를 그대로 유지했다. 현재 표준이나 최신 자료로 수정하지 않았다.',
  '중요한 원문 코드 중 학습 목적에 맞는 대표 예제를 선별했다. 발췌와 원문의 생략 표시는 구별해 알렸으며, 모든 코드를 전재한 자료는 아니다.',
  '실행 결과가 제시되지 않은 예제에는 [원문에 실행 결과 미제시]를 표시했다. 코드를 실행·수정해 새 결과를 생성하지 않았다.'
 ],
 'pagination_note':'출처의 “인쇄”는 스캔 이미지에서 확인한 원본 쪽수이고 “제공 PDF”는 첨부 파일의 첫 쪽을 1로 세는 위치다. 이 학습 교재의 목차·쪽번호·색인은 새 교재의 실제 PDF 쪽수를 사용한다. 원문의 번호와 교재 번호는 서로 다르다.',
 'overview':[], 'syntax':[], 'code_collection':[]
}
for ch in chapters:
 info['overview'].append({'type':'heading','text':ch['title']})
 info['overview'].append({'type':'bullets','items':ch.get('overview',[]),'source':ch['source']})
# The syntax collection quotes only actual lines already transcribed and checked
# for the chapter notes. This never synthesizes a new generic example.
for ch in chapters:
 codes=ch.get('codes',[])
 if not codes: continue
 # Select the shortest original example, keeping its complete transcription.
 c=min(codes,key=lambda c:len(c.get('code','')))
 info['syntax'].append({'title':ch['title']+' — '+c['title'],
   'source':c['source'],'form':c['code'],
   'meaning':c['meaning']+(' '+c.get('excerpt_note','') if c.get('excerpt') else '')+
       ' 상세 동작·주의 사항과 실행 결과 제시 여부는 해당 장의 같은 제목 코드 해설에서 확인한다.'})
(H/'book_info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
print('info prepared for',len(chapters),'chapters')
