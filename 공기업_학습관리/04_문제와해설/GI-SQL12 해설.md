# SQL12제 정답·해설

setup.sql은 가상 학습 DB를 만든다. 단일 결과표와 정렬 계약을 따른다. 고객·계좌·거래·이벤트·지표·대사·필수범주 표를 사용한다.

## 스키마
```sql
PRAGMA foreign_keys=ON;
CREATE TABLE customer(id INTEGER PRIMARY KEY,region TEXT NOT NULL);
CREATE TABLE account(id INTEGER PRIMARY KEY,cid INTEGER NOT NULL REFERENCES customer(id),state TEXT NOT NULL);
CREATE TABLE txn(id INTEGER PRIMARY KEY,aid INTEGER NOT NULL REFERENCES account(id),ts TEXT NOT NULL,amount INTEGER,state TEXT NOT NULL,category TEXT NOT NULL);
CREATE TABLE event(ingest_id INTEGER PRIMARY KEY,event_id TEXT NOT NULL,value INTEGER);
CREATE TABLE metric(region TEXT NOT NULL,total INTEGER NOT NULL,fail INTEGER NOT NULL);
CREATE TABLE requirement(category TEXT PRIMARY KEY);
CREATE TABLE book(aid INTEGER PRIMARY KEY,amount INTEGER);
CREATE TABLE report(aid INTEGER PRIMARY KEY,amount INTEGER);
```

# SX01 없는 고객까지 집계

모든 고객의 DONE 거래 수·알려진 금액 수·알려진 금액 합을 구한다. DONE 거래가 없거나 금액이 전부 NULL이면 알려진 합은0으로 표시하되 두 종류의 건수를 같이 표시한다. 계좌 상태는 필터하지 않는다. 출력:id,done_n,known_n,known_sum, id순.

## 정답 SQL
```sql
SELECT c.id,COUNT(t.id) AS done_n,COUNT(t.amount) AS known_n,
       COALESCE(SUM(t.amount),0) AS known_sum
FROM customer c
LEFT JOIN account a ON a.cid=c.id
LEFT JOIN txn t ON t.aid=a.id AND t.state='DONE'
GROUP BY c.id ORDER BY c.id;
```

## 기준 데이터 결과

| id | done_n | known_n | known_sum |
| --- | --- | --- | --- |
| 1 | 4 | 3 | 350 |
| 2 | 1 | 1 | 300 |
| 3 | 3 | 3 | 500 |
| 4 | 2 | 1 | 0 |
| 5 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 |

## 왜 이 결과인가

DONE 조건을 ON에 둬 거래 없는 고객도 남긴다. COUNT(t.id)는 금액 NULL인 거래도 세고 COUNT(t.amount)는 제외한다.

## 흔한 오해

COUNT(*)는 외부조인의 NULL 확장행도 센다. 합0만 출력하면 알려진0과 정보부재를 혼동한다.

# SX02 행 조건과 그룹 조건

DONE 거래가2개 이상이고 알려진 금액 합이300 이상인 고객을 찾는다. 출력:cid,done_n,known_sum, cid순.

## 정답 SQL
```sql
SELECT a.cid,COUNT(*) AS done_n,SUM(t.amount) AS known_sum
FROM account a JOIN txn t ON t.aid=a.id
WHERE t.state='DONE'
GROUP BY a.cid HAVING COUNT(*)>=2 AND SUM(t.amount)>=300
ORDER BY a.cid;
```

## 기준 데이터 결과

| cid | done_n | known_sum |
| --- | --- | --- |
| 1 | 4 | 350 |
| 3 | 3 | 500 |

## 왜 이 결과인가

먼저 완료 거래 행을 제한하고 고객별로 모은 후 집계 조건을 적용한다.

## 흔한 오해

집계 함수를 WHERE에 쓰거나 계좌별 그룹을 만들면 고객별 요구와 달라진다.

# SX03 금액 NULL과 존재 여부

알려진 양수 DONE 거래가 하나도 없는 모든 고객을 구한다. 금액 NULL·0·음수는 양수 거래가 아니다. 출력:id, id순.

## 정답 SQL
```sql
SELECT c.id FROM customer c
WHERE NOT EXISTS (
 SELECT 1 FROM account a JOIN txn t ON t.aid=a.id
 WHERE a.cid=c.id AND t.state='DONE' AND t.amount>0
) ORDER BY c.id;
```

## 기준 데이터 결과

| id |
| --- |
| 4 |
| 5 |
| 6 |

## 왜 이 결과인가

존재 여부는 행을 찾는 조건에 직접 표현한다. NULL 금액은 >0의 TRUE가 되지 않는다.

## 흔한 오해

거래 금액을0으로 바꾼 뒤 고객을 삭제하는 접근이나 NOT IN의 NULL 문제를 피한다.

# SX04 최근 거래와 동률

거래가 있는 계좌마다 상태를 구분하지 않고 가장 최근 거래1개를 고른다. ts가 같으면 id가 큰 거래가 최근이다. 출력:aid,id,state, aid순.

## 정답 SQL
```sql
WITH ranked AS (
 SELECT aid,id,state,ROW_NUMBER() OVER(PARTITION BY aid ORDER BY ts DESC,id DESC) AS rn
 FROM txn
)
SELECT aid,id,state FROM ranked WHERE rn=1 ORDER BY aid;
```

## 기준 데이터 결과

| aid | id | state |
| --- | --- | --- |
| 101 | 10 | DONE |
| 102 | 3 | DONE |
| 201 | 4 | DONE |
| 301 | 12 | DONE |
| 401 | 11 | DONE |
| 501 | 9 | PENDING |

## 왜 이 결과인가

정렬의 동률 보조 키를 명시한다. 윈도 결과는 바깥 질의에서 필터한다.

## 흔한 오해

MAX(ts)와 임의 id를 함께 뽑으면 두 열이 같은 거래에서 온다는 보장이 없다.

# SX05 월별 집계와 알려진 값

ts는 고정 길이 ISO 형식 TEXT다. 월별 DONE 거래 수·알려진 금액 합을 출력한다. 출력:month,done_n,known_sum, 월순.

## 정답 SQL
```sql
SELECT SUBSTR(ts,1,7) AS month,COUNT(*) AS done_n,
       COALESCE(SUM(amount),0) AS known_sum
FROM txn WHERE state='DONE'
GROUP BY SUBSTR(ts,1,7) ORDER BY month;
```

## 기준 데이터 결과

| month | done_n | known_sum |
| --- | --- | --- |
| 2026-01 | 6 | 950 |
| 2026-02 | 4 | 200 |

## 왜 이 결과인가

고정된 TEXT 계약에서는 앞7자가 연월이다. DATE/TIMESTAMP 자료형에서는 제품별 날짜 함수를 사용한다.

## 흔한 오해

금액 NULL을 거래 부재로 오해하지 않는다. 문자열 계약을 모든 날짜 자료형에 일반화하지 않는다.

# SX06 동률을 깨는 누적 합

DONE 거래만 대상으로 계좌별 ts,id순 알려진 금액 누적합과 알려진 금액 누적 건수를 구한다. 초기 알려진 금액이 없으면 합0. 출력:aid,id,running_sum,known_n, aid·ts·id순.

## 정답 SQL
```sql
SELECT aid,id,
 COALESCE(SUM(amount) OVER(PARTITION BY aid ORDER BY ts,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),0) AS running_sum,
 COUNT(amount) OVER(PARTITION BY aid ORDER BY ts,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS known_n
FROM txn WHERE state='DONE' ORDER BY aid,ts,id;
```

## 기준 데이터 결과

| aid | id | running_sum | known_n |
| --- | --- | --- | --- |
| 101 | 1 | 100 | 1 |
| 101 | 2 | 300 | 2 |
| 101 | 10 | 350 | 3 |
| 102 | 3 | 0 | 0 |
| 201 | 4 | 300 | 1 |
| 301 | 5 | 400 | 1 |
| 301 | 6 | 350 | 2 |
| 301 | 12 | 500 | 3 |
| 401 | 8 | 0 | 1 |
| 401 | 11 | 0 | 1 |

## 왜 이 결과인가

ROWS와 고유 id로 행별 누적 프레임을 정한다. SUM의 NULL 결과만0으로 표시하고 건수를 병행한다.

## 흔한 오해

ORDER BY ts만 둔 기본 RANGE 프레임은 같은 시각의 여러 행을 한꺼번에 포함할 수 있다.

# SX07 지점별 상위 두 금액 수준

OPEN 계좌의 알려진 DONE 금액 합(없으면0)을 구해 지역별 상위 두 개의 서로 다른 합계 수준을 모두 고른다. 동률 계좌는 전부 포함. 출력:region,aid,total,rank_n, 지역·순위·aid순.

## 정답 SQL
```sql
WITH totals AS (
 SELECT c.region,a.id AS aid,COALESCE(SUM(t.amount),0) AS total
 FROM account a JOIN customer c ON c.id=a.cid
 LEFT JOIN txn t ON t.aid=a.id AND t.state='DONE'
 WHERE a.state='OPEN' GROUP BY c.region,a.id
), ranks AS (
 SELECT region,aid,total,DENSE_RANK() OVER(PARTITION BY region ORDER BY total DESC) AS rank_n FROM totals
)
SELECT region,aid,total,rank_n FROM ranks WHERE rank_n<=2 ORDER BY region,rank_n,aid;
```

## 기준 데이터 결과

| region | aid | total | rank_n |
| --- | --- | --- | --- |
| 경기 | 301 | 500 | 1 |
| 경기 | 401 | 0 | 2 |
| 부산 | 101 | 350 | 1 |
| 부산 | 102 | 0 | 2 |
| 부산 | 501 | 0 | 2 |

## 왜 이 결과인가

요구가 두 행이 아니라 두 금액 수준이므로 DENSE_RANK다.

## 흔한 오해

ROW_NUMBER는 동률 중 일부만 남기고 RANK는 동률 개수 때문에 다음 금액의 순위가 건너뛴다.

# SX08 중복 이벤트의 최신 수신

event_id별 ingest_id가 가장 큰 행을 남긴다. 최신 value가 NULL이어도 이전 비NULL값으로 대신하지 않는다. 출력:event_id,ingest_id,value, event_id순.

## 정답 SQL
```sql
WITH ranked AS (
 SELECT event_id,ingest_id,value,ROW_NUMBER() OVER(PARTITION BY event_id ORDER BY ingest_id DESC) AS rn FROM event
)
SELECT event_id,ingest_id,value FROM ranked WHERE rn=1 ORDER BY event_id;
```

## 기준 데이터 결과

| event_id | ingest_id | value |
| --- | --- | --- |
| E1 | 3 | 12 |
| E2 | 5 | NULL |
| E3 | 4 | 30 |

## 왜 이 결과인가

수신 순서가 최신 판단 기준이며 value 크기는 기준이 아니다.

## 흔한 오해

MAX(value)와 MAX(ingest_id)를 따로 집계하면 서로 다른 행의 값을 붙일 수 있다.

# SX09 모든 필수 항목 충족

requirement의 모든 category에 대해 DONE 거래가 한 번 이상 있는 고객을 찾는다. 금액은 조건이 아니다. 필수항목 집합이 비어 있으면 모든 고객을 반환한다. 출력:id, id순.

## 정답 SQL
```sql
SELECT c.id FROM customer c WHERE NOT EXISTS (
 SELECT 1 FROM requirement r WHERE NOT EXISTS (
  SELECT 1 FROM account a JOIN txn t ON t.aid=a.id
  WHERE a.cid=c.id AND t.state='DONE' AND t.category=r.category
 )
) ORDER BY c.id;
```

## 기준 데이터 결과

| id |
| --- |
| 1 |
| 3 |

## 왜 이 결과인가

충족하지 못한 필수항목이 존재하지 않는다는 전칭 조건을 이중 NOT EXISTS로 표현한다.

## 흔한 오해

단순 거래 COUNT와 필수항목 개수를 비교하면 중복거래와 다른 항목 때문에 틀린다.

# SX10 비율의 가중 평균

metric의 지역별 전체 오류율을 백분율로 소수셋째자리까지 출력한다. 전체 건수0이면 NULL. 출력:region,error_pct, 지역순.

## 정답 SQL
```sql
SELECT region,ROUND(100.0*SUM(fail)/NULLIF(SUM(total),0),3) AS error_pct
FROM metric GROUP BY region ORDER BY region;
```

## 기준 데이터 결과

| region | error_pct |
| --- | --- |
| 경기 | 20.0 |
| 부산 | 19.091 |
| 전국 | NULL |

## 왜 이 결과인가

각 부분의 비율을 같은 가중치로 평균하지 않고 전체 오류 건수/전체 처리 건수를 계산한다.

## 흔한 오해

100 대신100.0으로 실수 계산 의도를 명시한다. 분모0을 임의0%로 바꾸지 않는다.

# SX11 두 원장의 불일치 찾기

book/report는 aid별 한 행이며 금액 NULL은 미확인이다. 양쪽 존재하고 금액이 같은 행만 제외하고, 누락·미확인·금액 차이를 구분한다. 출력:aid,book_amt,report_amt,reason, aid순. 판정 우선순위는 book 행 부재 MISSING_BOOK, report 행 부재 MISSING_REPORT, 양쪽 존재하나 금액 하나라도 NULL이면 UNKNOWN, 양쪽 알려진 금액이 다르면 DIFF다. 양쪽 알려진 금액이 같으면 MATCH로 보되 출력에서 제외한다.

## 정답 SQL
```sql
WITH joined AS (
 SELECT b.aid,b.amount AS book_amt,r.amount AS report_amt,b.aid AS bid,r.aid AS rid
 FROM book b LEFT JOIN report r ON r.aid=b.aid
 UNION ALL
 SELECT r.aid,b.amount,r.amount,b.aid,r.aid
 FROM report r LEFT JOIN book b ON b.aid=r.aid WHERE b.aid IS NULL
), marked AS (
 SELECT aid,book_amt,report_amt,CASE
 WHEN bid IS NULL THEN 'MISSING_BOOK' WHEN rid IS NULL THEN 'MISSING_REPORT'
 WHEN book_amt IS NULL OR report_amt IS NULL THEN 'UNKNOWN'
 WHEN book_amt<>report_amt THEN 'DIFF' ELSE 'MATCH' END AS reason FROM joined
)
SELECT aid,book_amt,report_amt,reason FROM marked WHERE reason<>'MATCH' ORDER BY aid;
```

## 기준 데이터 결과

| aid | book_amt | report_amt | reason |
| --- | --- | --- | --- |
| 2 | 200 | 180 | DIFF |
| 3 | NULL | 0 | UNKNOWN |
| 4 | 300 | NULL | MISSING_REPORT |
| 5 | NULL | 500 | MISSING_BOOK |

## 왜 이 결과인가

두 방향 LEFT JOIN을 합치되 두 번째는 왼쪽 부재만 남겨 중복을 방지한다. 키의 존재와 금액의 NULL은 다르다.

## 흔한 오해

금액 NULL만 보고 원장 행이 없다고 판단하지 않는다. MySQL의 FULL OUTER JOIN 지원을 가정하지 않는다.

# SX12 30분 단위 이용 세션

DONE 거래를 계좌별 ts,id순으로 본다. 최초 거래 또는 직전 DONE 거래와30분 이상 차이 나면 새 세션이다. 출력:aid,id,session_n, aid·ts·id순. 이 답안은 SQLite 날짜 함수 기준이다.

## 정답 SQL
```sql
WITH prev AS (
 SELECT aid,id,ts,LAG(ts) OVER(PARTITION BY aid ORDER BY ts,id) AS prev_ts
 FROM txn WHERE state='DONE'
), flags AS (
 SELECT aid,id,ts,CASE WHEN prev_ts IS NULL OR
 CAST(strftime('%s',ts) AS INTEGER)-CAST(strftime('%s',prev_ts) AS INTEGER)>=1800
 THEN 1 ELSE 0 END AS new_session FROM prev
)
SELECT aid,id,SUM(new_session) OVER(PARTITION BY aid ORDER BY ts,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS session_n
FROM flags ORDER BY aid,ts,id;
```

## 기준 데이터 결과

| aid | id | session_n |
| --- | --- | --- |
| 101 | 1 | 1 |
| 101 | 2 | 2 |
| 101 | 10 | 3 |
| 102 | 3 | 1 |
| 201 | 4 | 1 |
| 301 | 5 | 1 |
| 301 | 6 | 1 |
| 301 | 12 | 2 |
| 401 | 8 | 1 |
| 401 | 11 | 2 |

## 왜 이 결과인가

LAG로 직전 시각을 만든 후 새 세션 표지를 누적한다. 윈도 함수를 한 표현식 안에 직접 중첩하지 않는다.

## 흔한 오해

정확히30분도 새 세션이다. MySQL은 TIMESTAMPDIFF, Oracle은 날짜/interval 계산을 해당 열 자료형에 맞춰 바꾼다.
