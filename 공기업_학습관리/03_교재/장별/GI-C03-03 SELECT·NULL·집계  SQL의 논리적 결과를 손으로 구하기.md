---
note_type: "study-chapter"
chapter_id: "03-03"
subject: "DB·SQL: 관계 모델부터 트랜잭션·실행계획까지"
---

# 03-03 SELECT·NULL·집계: SQL의 논리적 결과를 손으로 구하기

[[GI-교재03 DB_SQL|과목 목차]] · [[GI-문제03 DB_SQL|문제]] · [[GI-해설03 DB_SQL|해설]]

## 학습 목표
SQL 코딩 문제에서 문법이 맞는 것과 요구 결과가 맞는 것은 다르다. NULL, 중복, 조건 적용 단계, 정렬을 확인해야 한다. 본 장 예제는 SQLite 공통 문법으로도 실습할 수 있도록 구성했다. 자료형과 제품별 옵션까지 완전히 같다는 뜻은 아니다.

## 1. 공통 실습 데이터
각 예제는 아래 초기 상태를 사용한다. amt의 NULL은 금액을 모르는 상태다. 0원과 구별한다.

```sql
CREATE TABLE txn (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  region VARCHAR(10) NOT NULL,
  amt INTEGER,
  status VARCHAR(10) NOT NULL
);
INSERT INTO txn VALUES
 (1,1,'부산',100,'완료'),
 (2,1,'부산',NULL,'완료'),
 (3,2,'경기',200,'완료'),
 (4,2,'경기',50,'취소'),
 (5,3,'부산',300,'완료'),
 (6,4,'경기',0,'완료');
```

FROM과 JOIN으로 후보 행을 만들고 WHERE로 개별 행을 거른 다음 GROUP BY로 그룹을 만들고 HAVING으로 그룹을 거른다. 이후 SELECT 결과와 DISTINCT, ORDER BY, 행 수 제한을 생각한다. 이는 결과 의미를 이해하는 논리 순서다. 옵티마이저의 실제 물리 실행 순서가 항상 그대로라는 뜻은 아니다. SELECT 별칭을 같은 질의의 WHERE에 쓸 수 있다고 일반화하지 않는다.

## 2. NULL과 3 값 논리
NULL은 미지·부재 등을 표현하는 표지로, `NULL = NULL`은 TRUE가 아니라 UNKNOWN이다. NULL인지 검사 하려면 `IS NULL`을 쓴다. WHERE는 TRUE인 행만 남기며 FALSE와 UNKNOWN은 제외한다.

| 식 | 결과 | WHERE에서 채택 |
| --- | --- | --- |
| NULL = 0 | UNKNOWN | 아니오 |
| NULL IS NULL | TRUE | 예 |
| TRUE AND UNKNOWN | UNKNOWN | 아니오 |
| FALSE AND UNKNOWN | FALSE | 아니오 |
| TRUE OR UNKNOWN | TRUE | 예 |
| NOT UNKNOWN | UNKNOWN | 아니오 |

`COALESCE(amt,0)`는 NULL을 0으로 바꿔 계산하지만 '모르는 금액을 0으로 간주해도 되는가'라는 업무 판단이 필요하다. SQL을 쉽게 쓰기 위해 사실의 의미를 바꾸지 않는다.

### 손풀이 예제 7: NULL이 포함된 COUNT
완료 상태는 ID 1,2,3,5,6의 5 행이다. `COUNT(*)`는 5, `COUNT(amt)`는 NULL 하나를 제외해 4, `SUM(amt)`는 100 +200 +300 +0 =600, `AVG(amt)`는 600/4=150이다. `AVG(COALESCE(amt,0))`는 600/5=120이다. 평균의 분모가 왜 달라지는지 설명할 수 있어야한다.

```sql
SELECT COUNT(*) AS rows_n, COUNT(amt) AS known_n,
       SUM(amt) AS total_amt, AVG(amt) AS mean_amt
FROM txn WHERE status = '완료';
```

빈 입력 집합에서 COUNT는 0, SUM·AVG는 보통 NULL을 반환한다. 합계가 0이어야하면 `COALESCE(SUM(amt),0)`처럼 집계 결과를 감싼다. 모든 NULL을 입력에서 0으로 치환하는 식과 빈 집합 처리는 같은 문제가 아니다.

## 3. 행 조건과 그룹 조건
완료된 거래만 합친 지역 중 합계 400 이상인 지역을 찾는다.

```sql
SELECT region, COUNT(*) AS rows_n, SUM(amt) AS total_amt
FROM txn
WHERE status = '완료'
GROUP BY region
HAVING SUM(amt) >= 400
ORDER BY total_amt DESC, region ASC;
```

부산은 완료 3행, 알려진 금액 합계 400, 경기는 완료 2 행 합계 200다. 부산만 남는다. 취소 거래를 WHERE에서 먼저 배제하지 않으면 경기는 250으로 바뀐다. HAVING은 그룹의 결과를 조건으로 평가한다. 일반적으로 집계 함수를 WHERE에 직접 쓰면 안 된다. 반면 GROUP BY에 포함된 열의 조건은 WHERE로 옮길 수 있는 경우가 있지만 의미와 옵티마이저 최적화를 섞지 않는다.

GROUP BY 없이 SELECT에 집계와 일반 열을 섞거나, 그룹 기준에 없는 일반 열을 임의 출력하면 표준 의미상 문제가 생긴다. SQLite의 유연한 허용이나 MySQL 설정에 따른 동작을 '어느 DB에서도 정답'으로 취급하지 않는다. 시험에 DBMS와 모드가 있으면 그 조건을 따른다.

## 4. DISTINCT·집합 연산·정렬
`SELECT customer_id FROM txn`에는 1,1,2,2,3,4가 있다. DISTINCT를 쓰면 1,2,3,4 네 값이다. 정렬을 지정하지 않은 출력 순서는 보장하지 않는다. UNION은 중복을 제거하고 UNION ALL은 유지한다. 둘은 결과 행 수도 성능 특성도 다를 수 있다. 중복을 제거해야할 업무 조건이 없다면 무작정 UNION을 쓰지 않는다.

NULL의 기본 정렬 위치는 DBMS별로 다르다. Oracle·PostgreSQL과 MySQL의 기본 값을 같은 것으로 외우면 틀릴 수 있다. 이식 가능한 학습 예에서는 정렬 방향과 NULL 처리 요구를 명시한다. 제품이 `NULLS FIRST/LAST`를 지원하지 않으면 CASE 정렬 키로 표현할 수 있다.

```sql
SELECT id, amt FROM txn
ORDER BY CASE WHEN amt IS NULL THEN 1 ELSE 0 END,
         amt DESC, id ASC;
```

위 결과의 ID 순서는 5,3,1,4,6,2다. NULL은 마지막이고 같은 금액이 생기면 id로 결정한다. 데이터 조회의 '상위 N 개' 요구는 순위 기준과 동률 처리 방식을 반드시 읽는다.

## 5. CASE와 조건부 집계
여러 조건의 합계를 한 번에 구할 때 CASE를 사용할 수 있다.

```sql
SELECT region,
 SUM(CASE WHEN status='완료' THEN COALESCE(amt,0) ELSE 0 END) AS done_amt,
 SUM(CASE WHEN status='취소' THEN 1 ELSE 0 END) AS cancel_n
FROM txn GROUP BY region ORDER BY region;
```

부산은 done_amt400,cancel_n0, 경기는 200,1이다. `COUNT(CASE WHEN ... THEN 1 ELSE 0 END)`는 0도 비 NULL이라 모든 행을 센다. 조건부 COUNT를 쓸 때 ELSE NULL 또는 ELSE 생략과 `COUNT`의 NULL 제외를 함께 이해한다.

### 직접 풀기
초기 데이터에서 `WHERE amt <> 0`으로 남는 ID, `COUNT(amt)`, SUM은? 남는 ID는 1,3,4,5이고 개수 4, 합계 650이다. ID2는 UNKNOWN, ID6은 FALSE라 제외된다. NULL을 '<>0이면 남겠지'라고 해석하면 틀린다.

완료: 작은 표의 결과를 실행 전에 쓰고 DB 실행 결과와 비교한다. 틀린 이유를 행 수·NULL·적용 단계 중 하나로 설명한다. 참고: [PostgreSQL 테이블 표현식](https://www.postgresql.org/docs/current/queries-table-expressions.html), [SQLite SELECT](https://www.sqlite.org/lang_select.html). 표·질의·예상 결과는 자체 제작이다.

## 강화 손풀이: NULL이 있는 빈 집계와 중복을 분리한다
T(v)의 행이 10,10,NULL,20이라고 하자. COUNT(*)=4, COUNT(v)=3, COUNT(DISTINCT v)=2, SUM(v)=40, AVG(v)=40/3이다. AVG의 분모에 NULL 행을 넣어 10이라고 계산하면 틀린다. DISTINCT는 값의 중복을 제거하며, 집계 함수별 NULL 처리와 결합해 판단한다.

WHERE v<>10은 20만 남긴다. NULL<>10은 TRUE가 아니라 UNKNOWN이라 WHERE에서 제외된다. WHERE v<>10 OR v IS NULL이면 20과 NULL이 남는다. AND·OR를 보기 전에 각 비교가 TRUE/FALSE/UNKNOWN 중 무엇인지 표시한다.

**빈 입력 반례:** WHERE v>100 뒤 GROUP BY 없이 집계하면 COUNT(*)는 0, SUM(v)는 NULL이다. GROUP BY v를 쓰면 입력 행이 없으므로 그룹 행 자체가 없을 수 있다. '집계하면 반드시 0인 행이 나온다'는 일반화는 틀리다.

금액 결과의 NULL을 0으로 바꾸라는 요구가 있을 때만 COALESCE(SUM(v),0)를 사용한다. 결측을 0으로 취급하는 것이 업무상 타당한지 먼저 정한다.
