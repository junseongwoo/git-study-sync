---
note_type: "study-chapter"
chapter_id: "03-05"
subject: "DB·SQL: 관계 모델부터 트랜잭션·실행계획까지"
---

# 03-05 윈도 함수·순위·날짜·SQL 방언: 코딩시험으로 연결하기

[[GI-교재03 DB_SQL|과목 목차]] · [[GI-문제03 DB_SQL|문제]] · [[GI-해설03 DB_SQL|해설]]

## 학습 목표
GROUP BY는 행을 묶어 결과 행 수를 줄일 수 있지만 윈도 함수는 원래 행을 유지하며 그룹 내 계산을 붙인다. 순위의 동률, 정렬 기준, 누적 합 프레임을 구분한다. IBK SQL 문제 준비를 위한 응용 장이며 특정 시험의 실제 문제를 재현한 것이 아니다.

## 1. 실습 데이터와 OVER
score(id,branch,amount)에 다음 여섯 행이 있다. amount는 모두 비NULL이다.

| id | branch | amount |
| --- | --- | --- |
| 1 | 부산 | 300 |
| 2 | 부산 | 300 |
| 3 | 부산 | 200 |
| 4 | 경기 | 150 |
| 5 | 경기 | 100 |
| 6 | 경기 | 100 |

`SUM(amount) OVER (PARTITION BY branch)`는 각 지점의 합계를 각 행 옆에 붙인다. 부산 행에는 모두 800, 경기 행에는 모두 350이 붙고 여섯 행이 유지된다. 반면 GROUP BY branch 집계는 부산·경기의 두 행이 된다. OVER의 PARTITION BY는 윈도 계산 범위를 나누며 SELECT 결과 전체를 그룹 한 행으로 압축하지 않는다.

## 2. ROW_NUMBER·RANK·DENSE_RANK
### 손풀이 예제 10: 동률과 다음 순위
부산에서 amount DESC만 순위 기준으로 쓰면 300,300,200이다. RANK는 1,1,3, DENSE_RANK는 1,1,2다. ROW_NUMBER는 1,2,3의 서로 다른 번호를 붙이지만 두 300중 누가 1인지는 그 기준만으로 결정되지 않는다. ROW_NUMBER의 OVER에는 id 같은 결정적 보조 키를 넣는다.

```sql
SELECT id, branch, amount,
 ROW_NUMBER() OVER(PARTITION BY branch ORDER BY amount DESC,id) AS rn,
 RANK() OVER(PARTITION BY branch ORDER BY amount DESC) AS rnk,
 DENSE_RANK() OVER(PARTITION BY branch ORDER BY amount DESC) AS drnk
FROM score ORDER BY branch,id;
```

RANK의 ORDER BY에도 id를 넣으면 amount 동률이더라도 id가 달라 동률 그룹이 깨진다. 따라서 '안정적 정렬을 위해 모든 함수에 보조 키 추가'가 언제나 맞지는 않다. 번호를 결정하려는 목적과 금액 동률을 유지하려는 목적을 구분한다.

'지점별 최대 2명'은 ROW_NUMBER <=2로 표현할 수 있다. '지점별 상위 2개 금액 수준'은 DENSE_RANK <=2다. '통상 경쟁 순위 2위 이내'는 RANK <=2다. 부산 사례에서는 각각 2명,3명,2명이다. 실제 문제의 문장을 이 세 요구 중 하나로 번역한다.

## 3. 윈도 결과를 필터링하는 단계
윈도 계산보다 WHERE가 논리적으로 앞에 있다. 따라서 같은 SELECT의 WHERE에 ROW_NUMBER 결과를 직접 쓰는 방식은 일반 공통 SQL로 쓰지 않는다. 서브쿼리나 CTE로 한 단계 감싼다.

```sql
WITH ranked AS (
 SELECT id,branch,amount,
  ROW_NUMBER() OVER(PARTITION BY branch ORDER BY amount DESC,id) AS rn
 FROM score
)
SELECT id,branch,amount FROM ranked
WHERE rn<=2 ORDER BY branch,rn;
```

CTE는 질의를 읽기 좋게 나누는 표현이다. CTE라는 이유만으로 반드시 임시 테이블에 물리 저장하거나 항상 빠르다는 결론은 틀리다. DBMS 버전·최적화·재사용에 따라 실행 방식이 달라진다.

## 4. 누적 합과 프레임
누적 합은 어떤 이전 행들을 포함하는지를 정해야 한다. ROWS는 정렬된 행 위치를, RANGE는 정렬 값과 동률 집단 등 값 기준 범위를 다룬다. 기본 프레임은 DBMS·함수에 따라 확인해야하며 원하는 누적 합은 프레임을 명시하면 오해가 줄어든다.

### 손풀이 예제 11: 행별 누적 합
부산 을 amount DESC,id ASC로 정렬하고 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW를 적용하면 id1 누적 300,id2 누적 600,id3 누적 800이다.

```sql
SELECT id,amount,
 SUM(amount) OVER(
  PARTITION BY branch ORDER BY amount DESC,id
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
 ) AS running_amt
FROM score WHERE branch='부산' ORDER BY amount DESC,id;
```

amount만 정렬하고 동률을 함께 포함하는 RANGE 프레임이면 처음 두 300 행의 누적 합이 둘 다 600이 될 수 있다. '누적 합이 갑자기 600부터 시작'하는 것은 반드시 버그가 아니라 프레임의 의미다. LAST_VALUE 역시 전체 파티션 마지막 값과 현재 프레임 마지막 값이 다를 수 있다. 함수 이름만 보고 결과를 결정하지 않는다.

## 5. LAG·LEAD와 전후 비교
`LAG(amount) OVER(PARTITION BY branch ORDER BY id)`는 같은 지점의 이전행 금액을 가져온다. 부산 id1은 이전 행이 없어 NULL,id2는 300,id3은 300이다. 현재-이전 계산은 NULL에 대한 처리 규칙을 정한다. 지점별 전일 대비 변화처럼 기간 단위 문제는 먼저 날짜별로 집계한 뒤 전일 행을 찾는다. 중간 날짜가 없으면 LAG의 '이전 행'이 '정확히 전날'이라는 뜻은 아니다.

## 6. 날짜와 행 제한의 방언
| 요구 | MySQL8.0 | Oracle19c | 학습 주의 |
| --- | --- | --- | --- |
| 정렬 후 상위 5 행 | LIMIT 5 | FETCH FIRST 5 ROWS ONLY | ORDER BY를 함께 명시 |
| NULL 대체 | COALESCE,IFNULL | COALESCE,NVL | COALESCE가 공통 선택 |
| 오늘 날짜 | CURRENT_DATE 등 | CURRENT_DATE 등 | 시간대·시간 포함 차이 검토 |
| 문자열 날짜 변환 | STR_TO_DATE | TO_DATE | 포맷 문자열과 함수가 다름 |
| 테이블 별칭 | AS 허용 | AS 없이 별칭 | SELECT 열 별칭과 혼동 금지 |

Oracle은 현재 빈 문자열을 NULL로 취급한다. MySQL에서 빈 문자열과 NULL은 별개다. 그러므로 `name=''` 조건을 어느 제품에서도 같은 의미로 생각하지 않는다. Oracle의 ROWNUM은 질의 블록에서 행이 선택될 때 매겨지므로 동일 블록에서 ROWNUM 제한 뒤 ORDER BY를 쓰면 정렬 전 일부 행을 제한하는 의미가 될 수 있다. 정렬 후 외부 블록에서 제한하거나 row_limiting_clause를 쓴다.

SQLite는 학습용 공통 SQL의 결과를 확인하는 수단이다. 동적 자료형과 일부 문법 허용이 Oracle/MySQL보다 유연하므로 SQLite에서 실행된다는 사실만으로 지원 DBMS에서의 정답을 보장하지 않는다. 윈도 함수는 SQLite3.25.0 이상에서 지원한다. 이 책의 검증 환경과 실제 시험의 허용 SQL 엔진은 구분한다.

### 직접 풀기와 확인
경기 150,100,100에서 금액 DESC RANK는 1,2,2이고 DENSE_RANK도 1,2,2다. ROW_NUMBER <=2는 두 행만, RANK <=2는 세 행 모두를 선택한다. 금액만 기준인 ROW_NUMBER의 두 100 중 선택 행은 미정이다. id 보조 키를 주면 하나로 결정된다.

완료: 문제마다 동률 포함·최대 인원·정렬을 한 문장으로 적고 함수·프레임을 선택한다. 참고: [PostgreSQL 윈도 함수](https://www.postgresql.org/docs/current/functions-window.html), [MySQL8.0 윈도 문법](https://dev.mysql.com/doc/refman/8.0/en/window-functions-usage.html), [Oracle SELECT](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/SELECT.html), [Oracle NULL](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Nulls.html).

## 강화 손풀이: 같은 정렬 값과 프레임의 경계를 나눠 본다
T(id,v)={(1,10),(2,10),(3,20)}이고 결과 표시만 id순이라고 하자. SUM(v) OVER(ORDER BY v RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)는 첫 두 동률 행에 20,20을 주고 마지막에 40을 준다. 동률을 함께 포함하기 때문이다.

SUM(v) OVER(ORDER BY v,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)는 정렬을 유일하게 만들고 행 위치대로 10,20,40을 준다. ROWS만 바꾸고 동률의 보조 정렬을 생략하면 같은 값의 어느 id가 먼저 계산되는지 확정할 수 없다.

LAST_VALUE(v) OVER(ORDER BY v,id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)는 10,10,20이다. 전체 파티션의 마지막 값 20을 모든 행에 얻으려면 끝 경계를 UNBOUNDED FOLLOWING으로 명시한다.

**시간 반례:** 10월 1일 매출 100,10월 3일 매출 300만 있으면 3일의 LAG는 1일 행 100을 가져온다. 이것을 전날 매출이라고 부르면 틀리다. 달력 테이블과 LEFT JOIN으로 빠진 날짜를 채우거나, 실제 전일 존재 조건을 직접 검사해야 한다. SQL 방언별 날짜 더하기 문법은 따로 확인한다.
