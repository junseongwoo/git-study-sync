import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
fixes={
'빅오메가 표기법은 함수의 하한을 나타내며, 모든 n>n₀에 대해 |f(n)|≥c|g(n)|이면 f(n)=Ω(g(n))이다.':
'빅오메가 표기법은 함수의 하한을 나타내며, 모든 n>n₀에 대해 |f(n)|≥c|g(n)|을 만족하는 상수 c와 n₀가 존재하면 f(n)=Ω(g(n))이다.',
'빅세타 표기법은 함수의 상한과 하한을 동시에 나타내며, 모든 n>n₀에 대해 c₁|g(n)|≤|f(n)|≤c₂|g(n)|이면 f(n)=Θ(g(n))이다.':
'빅세타 표기법은 함수의 상한과 하한을 동시에 나타내며, 모든 n>n₀에 대해 c₁|g(n)|≤|f(n)|≤c₂|g(n)|을 만족하는 상수 c₁, c₂, n₀가 존재하면 f(n)=Θ(g(n))이다.',
'RecurrenceSum()의 수행 시간은 T(n)=T(n−1)+c로 나타내고, 이를 전개하여 T(n)=cn, O(n)을 얻는다.':
'RecurrenceSum()의 수행 시간은 T(n)=T(n−1)+c로 나타내고, 이를 전개하여 T(n)≤cn이라는 상한과 O(n)을 얻는다.',
'어떤 상수 ε>0에 대해 f(n)=Ω(n^(log_b a+ε))이고, 상수 C(<1)와 충분히 큰 n에 대해 af(n/b)≤Cf(n)이 성립하면 T(n)=Θ(f(n))이다.':
'어떤 상수 ε>0에 대해 f(n)=Ω(n^(log_b a+ε))이고, 상수 C(<1)와 충분히 큰 n에 대해 af(n/b)≤cf(n)이 성립하면 T(n)=Θ(f(n))이다.'
}
checked={3:{'A':[17,18,19,20,23,24,25,27,28,29,30],'B':[499,500,507,508,509,510,511,512,514,515,517]},4:{'A':[34,35,36,38,40,41,42,43,44,45,46,47,48,49,50,51,52,53,56]}}
report={'reviewer':'c_ds_algorithms','method':'모든 refs의 원본 스캔 이미지 직접 대조. OCR는 보조만 사용. 수식의 부등호·정의의 상수 존재 조건·원문 코드의 함수명/연산/분기 조건 확인.','units':[],'modifications':[]}
for n in [3,4]:
 p=R/f'unit_{n:02d}.json';u=json.loads(p.read_text(encoding='utf-8')); changed=[]; seen=set();refs=set()
 def walk(x):
  if isinstance(x,dict):
   if 'text' in x and x['text'] in fixes:
    old=x['text'];x['text']=fixes[old];changed.append((old,x['text']))
   if 'refs' in x:
    seen.add((x.get('text',x.get('code',x.get('expression',''))),json.dumps(x['refs'],sort_keys=True)))
    for rr in x['refs']:
     for pp in rr['pages']:
      assert pp in checked[n][rr['source']],(n,rr)
      refs.add((rr['source'],pp))
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(u)
 u['checked_images']=[{'source':s,'pages':ps} for s,ps in checked[n].items()]
 if n==3:
  u['editor_notes'].append('B PDF517의 마스터 정리 ③은 상수를 C(<1)로 쓰고 부등식 우변은 cf(n)으로 표기한다. 원문의 대소문자 혼용을 임의로 교정하지 않고 그대로 수록했다.')
  report['modifications']=[{'unit':3,'before':old,'after':new} for old,new in dict(changed).items()]
 p.write_text(json.dumps(u,ensure_ascii=False,indent=2),encoding='utf-8')
 report['units'].append({'unit':n,'distinct_cited_items':len(seen),'cited_page_count':len(refs),'checked_images':u['checked_images'],'all_refs_visually_verified':True,'code_status':'unit04의 A 프로그램2.1(PDF35), 프로그램2.5(PDF46)의 연산·함수명·기저 조건 모두 일치.' if n==4 else '코드 발췌 없음.','formula_status':'팩토리얼 정의, 피보나치 점화식, O(2ⁿ) 상한, 순환 거듭제곱 O(log₂n) 및 하노이 탑 이동 순서 일치.' if n==4 else 'A PDF23/27의 절댓값·부등호·n>n₀ 확인. Ω/Θ 본문에서 상수 존재 조건 보완. B PDF517 마스터 정리 세 조건 확인. B PDF510 RecurrenceSum의 상한 ≤를 복원.'})
report['notes']=['원문의 표기나 설명을 외부 지식으로 교정하지 않았다.','수정 내용은 본문뿐 아니라 같은 FACT를 재사용한 용어·요약·복습 정답·치트에도 재귀적으로 적용했다.','unit04의 코드 두 개는 수정할 필요가 없었다. checked_images만 보완했다.']
(R/'root_03_04_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verified':[(x['unit'],x['cited_page_count'],x['distinct_cited_items']) for x in report['units']],'distinct_corrections':len(report['modifications'])},ensure_ascii=False))
