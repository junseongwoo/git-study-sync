# SQL 실습 정답·해설

## SQL01 필터와 정렬

활성 직원 중 salary>=50의 id,name,salary를 salary 내림차순,id 오름차순으로 조회하라.

```sql
SELECT id,name,salary FROM employee WHERE active=1 AND salary>=50 ORDER BY salary DESC,id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [2, "누리", 60],
  [6, "바다", 60],
  [1, "가람", 50]
]
```

동률을 id로 정한다. ORDER BY가 없으면 반환 순서가 보장되지 않는다.

## SQL02 NULL 검사

score가 없는 직원의 id,name을 id순으로 조회하라.

```sql
SELECT id,name FROM employee WHERE score IS NULL ORDER BY id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [2, "누리"]
]
```

=NULL을 쓰면 TRUE가 되지 않는다.

## SQL03 집계 분모

전체 직원의 COUNT(*), COUNT(score), AVG(score)를 한 행으로 조회하라.

```sql
SELECT COUNT(*),COUNT(score),AVG(score) FROM employee;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [6, 5, 83.0]
]
```

90+80+70+85+90=415, 유효 score 5개이므로 평균83이다.

## SQL04 내부 조인

팀이 지정된 직원의 id,name,팀명을 id순으로 조회하라.

```sql
SELECT e.id,e.name,t.name FROM employee e JOIN team t ON e.team_id=t.id ORDER BY e.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, "가람", "개발"],
  [2, "누리", "개발"],
  [3, "다온", "운영"],
  [4, "라온", "운영"],
  [6, "바다", "데이터"]
]
```

team_id NULL인 마루는 매칭되지 않는다.

## SQL05 외부 조인

모든 직원 id,name,팀명을 출력하라. 미지정 팀은 문자열 미지정으로 대체하고 id순 정렬한다.

```sql
SELECT e.id,e.name,COALESCE(t.name,'미지정') FROM employee e LEFT JOIN team t ON e.team_id=t.id ORDER BY e.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, "가람", "개발"],
  [2, "누리", "개발"],
  [3, "다온", "운영"],
  [4, "라온", "운영"],
  [5, "마루", "미지정"],
  [6, "바다", "데이터"]
]
```

COALESCE는 출력 표현이다. 원본 NULL 데이터를 변경하는 것이 아니다.

## SQL06 빈 팀 포함 집계

모든 팀의 id,name,직원 수를 출력하라. 빈 팀도 0으로 출력하고 team.id순 정렬한다.

```sql
SELECT t.id,t.name,COUNT(e.id) FROM team t LEFT JOIN employee e ON e.team_id=t.id GROUP BY t.id,t.name ORDER BY t.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, "개발", 2],
  [2, "운영", 2],
  [3, "데이터", 1],
  [4, "보안", 0]
]
```

COUNT(*)는 빈 팀의 NULL 확장 행도1로 셀 수 있다. 오른쪽 non-null 키를 센다.

## SQL07 WHERE와 HAVING

활성 직원이 2명 이상인 지정 팀의 team_id,인원,평균 salary를 조회하라. team_id순 정렬한다.

```sql
SELECT team_id,COUNT(*),AVG(salary) FROM employee WHERE active=1 AND team_id IS NOT NULL GROUP BY team_id HAVING COUNT(*)>=2 ORDER BY team_id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, 2, 55.0]
]
```

운영팀은 비활성 라온이 제외되어1명이다. 필터 후 집계한다.

## SQL08 조건부 집계

각 지정 팀의 team_id,전체 인원,활성 인원을 team_id순 출력하라.

```sql
SELECT team_id,COUNT(*),SUM(CASE WHEN active=1 THEN 1 ELSE 0 END) FROM employee WHERE team_id IS NOT NULL GROUP BY team_id ORDER BY team_id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, 2, 2],
  [2, 2, 1],
  [3, 1, 1]
]
```

전체 인원과 활성 인원을 같은 그룹에서 다른 조건으로 센다.

## SQL09 평균 초과

전체 평균 salary보다 큰 직원 id,salary를 id순 출력하라.

```sql
SELECT id,salary FROM employee WHERE salary>(SELECT AVG(salary) FROM employee) ORDER BY id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [2, 60],
  [4, 60],
  [6, 60]
]
```

평균은315/6=52.5다. 비활성도 전체 평균에 포함한다는 조건이다.

## SQL10 팀 평균 초과

지정 팀에서 자기 팀 평균 salary보다 큰 직원 id,team_id,salary를 id순 출력하라.

```sql
SELECT e.id,e.team_id,e.salary FROM employee e WHERE e.team_id IS NOT NULL AND e.salary>(SELECT AVG(x.salary) FROM employee x WHERE x.team_id=e.team_id) ORDER BY e.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [2, 1, 60],
  [4, 2, 60]
]
```

팀 평균은 개발55,운영50,데이터60이다. 평균과 같은 바다는 제외된다.

## SQL11 NOT EXISTS

직원이 전혀 없는 팀 id,name을 id순 출력하라.

```sql
SELECT t.id,t.name FROM team t WHERE NOT EXISTS(SELECT 1 FROM employee e WHERE e.team_id=t.id) ORDER BY t.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [4, "보안"]
]
```

employee.team_id에 NULL이 있으므로 NOT IN을 무심코 쓰면 보안팀도 사라질 수 있다.

## SQL12 NOT IN 함정 재현

SELECT id FROM team WHERE id NOT IN (SELECT team_id FROM employee) ORDER BY id;의 결과를 예측하라.

```sql
SELECT id FROM team WHERE id NOT IN (SELECT team_id FROM employee) ORDER BY id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[]
```

후보에 NULL이 포함된다. 일치하지 않는4조차 UNKNOWN으로 걸러져 결과0행이다.

## SQL13 중복 제거

employee의 서로 다른 salary를 오름차순 출력하라.

```sql
SELECT DISTINCT salary FROM employee ORDER BY salary;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [40],
  [45],
  [50],
  [60]
]
```

60은3명이어도 DISTINCT 결과에서는 한 번이다.

## SQL14 팀별 최고 한 명

지정 팀마다 salary 최고 직원 한 명의 id,team_id,salary를 출력한다. 동률은 id 작은 사람. team_id순 정렬한다.

```sql
WITH r AS (SELECT id,team_id,salary,ROW_NUMBER() OVER(PARTITION BY team_id ORDER BY salary DESC,id) rn FROM employee WHERE team_id IS NOT NULL) SELECT id,team_id,salary FROM r WHERE rn=1 ORDER BY team_id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [2, 1, 60],
  [4, 2, 60],
  [6, 3, 60]
]
```

행 유지 상태에서 팀별 순번을 붙이고 바깥에서 rn=1을 고른다.

## SQL15 RANK와 DENSE_RANK

salary 내림차순으로 전체 직원 id,salary,RANK,DENSE_RANK를 출력하라. 최종 정렬 salary DESC,id.

```sql
SELECT id,salary,RANK() OVER(ORDER BY salary DESC),DENSE_RANK() OVER(ORDER BY salary DESC) FROM employee ORDER BY salary DESC,id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [2, 60, 1, 1],
  [4, 60, 1, 1],
  [6, 60, 1, 1],
  [1, 50, 4, 2],
  [5, 45, 5, 3],
  [3, 40, 6, 4]
]
```

윈도우 ORDER BY에 id까지 넣으면 salary 동률이 깨진다. 출력 정렬과 순위 기준을 나눈다.

## SQL16 전체 결함률

모든 batch의 총 검사 수,총 결함 수,결함률(%)을 소수2자리로 출력하라.

```sql
SELECT SUM(inspected),SUM(defect),ROUND(100.0*SUM(defect)/NULLIF(SUM(inspected),0),2) FROM batch;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [550, 8, 1.45]
]
```

8/550×100≈1.4545%. 배치별 결함률의 단순 평균과 다르다.

## SQL17 장비별 결함률

모든 장비 id,총 검사 수,결함률%를 출력하라. 분모0이면 NULL, 소수2자리. id순.

```sql
SELECT d.id,COALESCE(SUM(b.inspected),0),ROUND(100.0*SUM(b.defect)/NULLIF(SUM(b.inspected),0),2) FROM device d LEFT JOIN batch b ON b.device_id=d.id GROUP BY d.id ORDER BY d.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, 250, 2.4],
  [2, 300, 0.67],
  [3, 0, null]
]
```

0/0을 정상 결함률0으로 단정하지 않는다. NULLIF로 분모0을 결측 처리한다.

## SQL18 날짜별 누적

날짜별 검사 합계를 먼저 집계하고 day,당일 검사합,누적합을 날짜순 출력하라.

```sql
WITH daily AS(SELECT day,SUM(inspected) n FROM batch GROUP BY day) SELECT day,n,SUM(n) OVER(ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) FROM daily ORDER BY day;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  ["2026-10-01", 300, 300],
  ["2026-10-02", 150, 450],
  ["2026-10-03", 100, 550]
]
```

동일 날짜 여러 배치를 먼저 합친다. ISO 날짜 문자열이라 정렬 순서가 날짜순과 일치한다.

## SQL19 LAG 비교

날짜별 검사 합계의 day,n,전일 관측 합계,증감량을 출력한다. 첫날 이전 값과 증감은 NULL.

```sql
WITH daily AS(SELECT day,SUM(inspected) n FROM batch GROUP BY day) SELECT day,n,LAG(n) OVER(ORDER BY day),n-LAG(n) OVER(ORDER BY day) FROM daily ORDER BY day;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  ["2026-10-01", 300, null, null],
  ["2026-10-02", 150, 300, -150],
  ["2026-10-03", 100, 150, -50]
]
```

LAG는 이전 관측 행이지 누락된 달력 날짜를 자동 생성하지 않는다. 이 데이터는 연속 날짜다.

## SQL20 가장 최근 배치

장비마다 가장 최근 day의 배치 id,device_id,day를 출력한다. 같은 day면 큰id. device_id순.

```sql
WITH r AS(SELECT id,device_id,day,ROW_NUMBER() OVER(PARTITION BY device_id ORDER BY day DESC,id DESC) rn FROM batch) SELECT id,device_id,day FROM r WHERE rn=1 ORDER BY device_id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [5, 1, "2026-10-03"],
  [4, 2, "2026-10-02"],
  [6, 3, "2026-10-02"]
]
```

MAX(day)와 아무 id를 같이 SELECT하는 방식은 목표 행의 id를 보증하지 않는다.

## SQL21 ON과 WHERE 비교

모든 팀을 유지하면서 활성 직원만 연결한다. t.id와 활성 직원 id를 출력하고 t.id,e.id순 정렬하라.

```sql
SELECT t.id,e.id FROM team t LEFT JOIN employee e ON e.team_id=t.id AND e.active=1 ORDER BY t.id,e.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, 1],
  [1, 2],
  [2, 3],
  [3, 6],
  [4, null]
]
```

활성 조건을 ON에 넣어 빈 보안팀을 유지한다. WHERE로 옮기면 보안팀이 제거된다.

## SQL22 반복 행의 조인 집계

보너스가 있는 직원의 id,salary,보너스 합을 한 직원당 한 행, id순 출력하라.

```sql
SELECT e.id,e.salary,b.total FROM employee e JOIN(SELECT employee_id,SUM(amount) total FROM bonus GROUP BY employee_id) b ON e.id=b.employee_id ORDER BY e.id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, 50, 30],
  [3, 40, 5]
]
```

가람의 salary50을 보너스2행과 조인한 뒤 SUM(salary)하면100으로 부풀 수 있다. 먼저 보너스를 직원 단위로 집계한다.

## SQL23 UNION ALL

SELECT salary FROM employee WHERE id=2 UNION ALL SELECT salary FROM employee WHERE id=4; 결과를 예측하라.

```sql
SELECT salary FROM employee WHERE id=2 UNION ALL SELECT salary FROM employee WHERE id=4;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [60],
  [60]
]
```

UNION ALL은 중복 유지한다. 두 값이 같아서 이 예의 행 순서 불확실성은 관찰 결과에 영향 없다.

## SQL24 인덱스 동등 결과

team_id=1인 직원 id,name을 id순 조회한다. 인덱스 생성 전후에도 결과가 같은지 확인하라.

```sql
SELECT id,name FROM employee WHERE team_id=1 ORDER BY id;
```

기대 결과(한 줄은 한 행, 열 순서 포함, JSON null은 SQL NULL):

```json
[
  [1, "가람"],
  [2, "누리"]
]
```

인덱스는 논리 결과를 바꾸지 않는다. 작은 샘플에서 속도 개선이나 특정 계획 선택을 보증하지 않는다.
