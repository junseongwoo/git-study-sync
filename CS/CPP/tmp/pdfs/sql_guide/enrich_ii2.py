import json
from pathlib import Path
from write_ii2 import code
p=Path(__file__).parent/'chapters'/'04_II2.json'
c=json.loads(p.read_text(encoding='utf-8'))
c['codes'] += [
code(14,'RANGE로 급여 값 범위의 인원 계산',[329],"SELECT ENAME, SAL,\n       COUNT(*) OVER (ORDER BY SAL\n           RANGE BETWEEN 50 PRECEDING AND 150 FOLLOWING) AS EMP_CNT\nFROM EMP;",'현재 급여보다 50 적은 값부터 150 큰 값까지의 인원수를 센다.',[('RANGE','정렬 값 기준의 논리적 범위'),('COUNT(*) OVER','각 행에 해당 범위 인원수 표시')],['전체 행을 급여 기준으로 분석한다.','각 행의 급여 -50~+150에 포함되는 행 수를 계산한다.'],'원문 ADAMS의 급여 1100에 대해 1050~1250 범위의 ADAMS·WARD·MARTIN 3행이 포함된다.',['ROWS의 앞뒤 행 수와 달리 값의 범위다.']),
code(15,'LAG의 이동 거리와 대체값',[333,334],"SELECT ENAME, HIREDATE, SAL,\n       LAG(SAL, 2, 0) OVER (ORDER BY HIREDATE) AS LAG_SAL\nFROM EMP\nWHERE JOB = 'SALESMAN';",'판매사원을 입사일로 정렬하여 두 행 앞의 급여를 표시한다.',[('LAG(SAL, 2, 0)','두 행 앞 값이 없으면 0'),('ORDER BY HIREDATE','앞뒤를 판단하는 기준')],['SALESMAN 행을 대상으로 입사일 순서를 정한다.','두 행 앞 SAL을 읽고 해당 행이 없으면 0을 쓴다.'],'원문 첫 두 행의 LAG_SAL은 0이며 이후 두 행은 1600과 1250이다.',['행이 없는 경우의 대체값과 이동 행 수를 구분한다.']),
code(16,'SQL Server TOP WITH TIES',[342],"SELECT TOP(2) WITH TIES\n       ENAME, SAL\nFROM EMP\nORDER BY SAL DESC;",'급여 상위 2개 위치에 마지막 동순위까지 포함한다.',[('TOP(2)','상위 행 제한'),('WITH TIES','마지막 정렬 값의 동순위 포함')],['급여 내림차순을 기준으로 상위 행을 선택한다.','마지막 선택 급여와 같은 행을 추가로 포함한다.'],'원문은 KING 5000, SCOTT 3000, FORD 3000의 3행을 제시한다.',['N이라는 수가 최종 행 수의 상한은 아닐 수 있다.']),
code(17,'ROW LIMITING의 FETCH',[343],"SELECT EMPNO, SAL\nFROM EMP\nORDER BY SAL, EMPNO\nFETCH FIRST 5 ROWS ONLY;",'급여·사번 정렬에서 처음 5행을 반환한다.',[('FETCH FIRST 5 ROWS ONLY','정렬 결과의 처음 5행')],['급여, 사번 순서로 결과를 정렬한다.','처음 5행만 반환한다.'],'원문은 급여 800, 950, 1100, 1250, 1250의 5행을 표시한다.',['같은 쪽의 OFFSET 5 ROWS 예는 첫 5행을 건너뛰고 나머지 9행을 반환한다.'])]
c['codes'].sort(key=lambda x:min(x['source_pdf_pages']))
p.write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
print('enriched',len(c['codes']))
