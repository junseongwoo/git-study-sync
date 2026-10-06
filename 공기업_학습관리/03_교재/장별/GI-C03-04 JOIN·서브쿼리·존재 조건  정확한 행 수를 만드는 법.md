---
note_type: "study-chapter"
chapter_id: "03-04"
subject: "DB·SQL: 관계 모델부터 트랜잭션·실행계획까지"
---

# 03-04 JOIN·서브쿼리·존재 조건: 정확한 행 수를 만드는 법

[[GI-교재03 DB_SQL|과목 목차]] · [[GI-문제03 DB_SQL|문제]] · [[GI-해설03 DB_SQL|해설]]

## 학습 목표
JOIN은 열을 붙이는 기능이면서 행을 늘리는 연산이다. 고객 수와 거래 수를 혼동하지 않는다. 외부 조인, EXISTS, NOT IN을 같은 방식으로 외우지 말고 작은 데이터로 결과를 검증한다.

## 1. 연결 실습 데이터
이 장의 customer는 고객 1 가람,2 나래,3 다온,4 라 온,5 마루다. 03-03의 txn은 그대로 쓴다.

```sql
CREATE TABLE customer (
 customer_id INTEGER PRIMARY KEY, name VARCHAR(20) NOT NULL
);
INSERT INTO customer VALUES
 (1,'가람'),(2,'나래'),(3,'다온'),(4,'라온'),(5,'마루');
```

INNER JOIN은 매칭 행 쌍만 남긴다. LEFT JOIN은 왼쪽 행을 보존하고 매칭이 없으면 오른쪽 열을 NULL로 채운다. 왼쪽 한 행에 오른쪽 3 행이 매칭되면 결과 3 행이다. '왼쪽 5 행이면 LEFT JOIN 결과도 정확히 5 행'은 틀리다.

### 손풀이 예제 8: LEFT JOIN과 COUNT
고객별 전체 거래 수를 다음처럼 구한다.

```sql
SELECT c.customer_id, COUNT(t.id) AS txn_n
FROM customer c
LEFT JOIN txn t ON t.customer_id=c.customer_id
GROUP BY c.customer_id ORDER BY c.customer_id;
```

결과는 (1,2),(2,2),(3,1),(4,1),(5,0)이다. 집계 전 LEFT JOIN은 총 7 행이다. 고객 5에도 NULL로 채워진 한 행이 있기 때문이다. COUNT(*)로 바꾸면 고객 5의 거래 수를 1로 잘못 센다. 매칭된 오른쪽 행의 비NULL 키인 t.id를 센다.

## 2. ON 조건과 WHERE 조건
완료 거래만 연결하면서 거래 없는 고객도 보존하려면 조건을 ON에 넣는다.

```sql
SELECT c.customer_id, COUNT(t.id) AS done_n
FROM customer c LEFT JOIN txn t
 ON t.customer_id=c.customer_id AND t.status='완료'
GROUP BY c.customer_id ORDER BY c.customer_id;
```

고객별 done_n은 2,1,1,1,0이다. 동일 조건을 `WHERE t.status='완료'`로 옮기면 고객 5의 NULL 행은 UNKNOWN으로 제거된다. 결과 고객 5가 사라진다. 또 취소 거래만 있는 고객이 존재한다면 해당 고객도 사라진다. 조건은 텍스트 위치가 아니라 '매칭 단계에서 제한하는가, 보존 후 걸러 내는가'로 읽는다.

`WHERE t.id IS NULL`은 외부 조인에서 매칭이 없는 고객을 찾는 대표 패턴이다. 검사 대상 열은 매칭이 되면 NULL일 수 없는 열을 고른다. 금액처럼 실제 행에서도 NULL일 수 있는 열로 검사하면 거래가 있는 데도 없다고 판정할 수 있다.

## 3. 다대다 조인으로 합계가 부풀어 오르는 경우
고객 1에 거래 2개와 연락처 3개가 있다고 하자. 고객에 거래와 연락처를 동시에 조인하면 2×3 =6 행이 생긴다. 각 거래 금액이 3번 반복된다. 해결은 업무상 필요한 행 단위를 정하고, 거래 합계를 고객 단위로 먼저 집계한 뒤 연락처와 결합하거나 별도 질의를 쓰는 것이다. SUM(DISTINCT 금액)으로 고치면 실제 동일 금액 거래를 하나로 합쳐 버릴 수 있으므로 일반 해법이 아니다.

## 4. 비상관·상관 서브쿼리
비상관 서브쿼리는 바깥 행의 열을 참조하지 않는다. 상관 서브쿼리는 바깥 행 값에 따라 조건이 달라진다. '상관 서브쿼리는 언제나 실제로 행마다 물리 실행'이라고 단정하지 않는다. 옵티마이저가 동등한 조인 등으로 변환할 수 있다.

```sql
SELECT c.customer_id, c.name
FROM customer c
WHERE EXISTS (
 SELECT 1 FROM txn t
 WHERE t.customer_id=c.customer_id
   AND t.status='완료' AND t.amt>=200
)
ORDER BY c.customer_id;
```

고객 2와 3이 결과다. EXISTS는 조건을 만족하는 행이 하나라도 있는지를 평가하므로 해당 고객에게 고액 거래가 여러 개 있어도 바깥 고객 행은 한 번만 나온다. SELECT 1은 '항상 1 행'이라는 뜻이 아니라 검색 결과의 내용보다 존재 여부가 중요하다는 표기다.

### 손풀이 예제 9: NOT IN과 NULL
차단 목록 blocked(customer_id)에 2와 NULL이 있다고 하자. `customer_id NOT IN (2,NULL)`은 1에 대해 `(1<>2) AND (1<>NULL)` = TRUE AND UNKNOWN = UNKNOWN이다. 2는 FALSE, 나머지도 UNKNOWN이라 WHERE에는 아무 행도 남지 않는다.

```sql
SELECT c.customer_id FROM customer c
WHERE NOT EXISTS (
 SELECT 1 FROM blocked b WHERE b.customer_id=c.customer_id
)
ORDER BY c.customer_id;
```

이 질의는 고객 1,3,4,5를 반환한다. blocked의 NULL은 등호 비교에서 어떤 비NULL 고객과도 TRUE 매칭을 만들지 않는다. NOT EXISTS가 모든 업무에서 무조건 맞다는 뜻은 아니다. 'NULL 차단 기록을 어떻게 해석할 것인가'라는 요구를 먼저 결정한다.

## 5. 전체 대상 충족을 찾는 나눗셈 질의
필수 과목 required(course)에 DB,OS가 있고 수강 taken(student,course)에 가람-DB, 가람-OS, 나래-DB가 있다. 모든 필수 과목을 수강한 학생을 찾는 이중 부정은 '아직 수강하지 않은 필수 과목이 존재하지 않는다'다.

```sql
SELECT s.student FROM student s
WHERE NOT EXISTS (
 SELECT 1 FROM required r
 WHERE NOT EXISTS (
  SELECT 1 FROM taken t
  WHERE t.student=s.student AND t.course=r.course
 )
);
```

required가 비어 있으면 어떤 학생도 미충족 과목을 갖지 않으므로 모든 학생이 통과한다. 이를 원하지 않는 업무라면 required가 비어 있지 않다는 조건을 따로 넣는다. 집계 대안은 중복 수강 행과 필수 외 과목의 영향을 제거해야 한다. SQL 문제의 예외 조건을 읽는 연습이 된다.

## 6. DBMS 문법 주의
공통 INNER/LEFT JOIN과 EXISTS는 널리 쓸 수 있다. MySQL8.0에는 FULL OUTER JOIN 직접 문법이 없으므로 UNION 등을 이용한 별도 구현이 필요하다. Oracle19c는 테이블 별칭에 AS를 쓰지 않는 형태로 작성한다. 오래된 Oracle `(+)` 외부 조인 표기는 기본 개념을 배운 뒤 별도로 읽고, 새로운 학습 질의는 ANSI JOIN을 우선한다. 테이블·열의 따옴표와 대소문자 규칙도 제품별로 다르다.

### 직접 풀기와 확인
고객 1의 금액이 100과 100, 연락처가 3개이면 조인 후 SUM(amt)는 600이다. 실제 합계 200과 다르다. SUM(DISTINCT amt)는 100이므로 역시 틀리다. 먼저 고객별 SUM을 만들어 200으로 집계한 뒤 연결해야 한다.

완료: JOIN 전후 각 행의 개수를 적고, 거래 없는 고객·NULL·중복 금액을 포함한 최소 반례를 만든다. 참고: [PostgreSQL JOIN 의미](https://www.postgresql.org/docs/current/queries-table-expressions.html), [Oracle SELECT 문법](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html). 예제 데이터는 자체 제작이다.

## 강화 손풀이: 두 1:N 조인의 곱셈 중복을 막는다
고객 1에게 계좌 두 개(잔액 100,200), 문의 세 개가 있다. 고객-계좌-문의를 customer_id로 함께 조인하면 2×3=6행이 된다. 이 결과에서 SUM(balance)는 (100+200)×3=900이며 실제 계좌 총액 300이 아니다.

**안전한 풀이:** 계좌를 고객별로 먼저 SUM하고, 문의를 고객별로 먼저 COUNT한 뒤 각각 고객에 연결한다. 또는 계좌와 문의 요구를 독립적인 상관 서브쿼리로 계산한다. SUM(DISTINCT balance)는 정당한 해결책이 아니다. 서로 다른 두 계좌의 잔액이 모두 100이면 실제 200인데 DISTINCT는 100만 더한다.

**존재 조건:** '계좌가 하나 이상 있는 고객'이면 EXISTS는 고객 한 행을 유지한다. INNER JOIN 뒤 DISTINCT로 고객을 다시 줄이는 방법과 결과가 같을 수 있어도 요구를 직접 표현하는 EXISTS의 논리를 먼저 이해한다.

**반례:** NOT IN의 내부 결과가 (2,NULL)이면 고객 ID 1에 대해 1<>2 AND 1<>NULL은 UNKNOWN이다. NOT EXISTS를 고객별 동등 비교로 구성하면 참조 NULL 행이 고객 1을 가로막지 않는다. 다만 외부 ID가 NULL일 때 업무 요구는 별도로 정해야 한다.
