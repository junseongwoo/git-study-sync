---
note_type: "study-chapter"
chapter_id: "03-08"
subject: "DB·SQL: 관계 모델부터 트랜잭션·실행계획까지"
---

# 03-08 뷰·복구·SQL 종합 실습: 읽기와 쓰기를 한 흐름으로

[[GI-교재03 DB_SQL|과목 목차]] · [[GI-문제03 DB_SQL|문제]] · [[GI-해설03 DB_SQL|해설]]

## 학습 목표
기본 DDL·DML·권한·거래 명령을 구분한다. 장애 복구의 로그와 백업이 다른 역할임을 이해한다. 교재를 읽은 뒤 실행 없이 결과를 예측하고 공통 실습 DB에서 확인하는 능력을 만든다.

## 1. 명령 분류와 뷰
DDL은 CREATE·ALTER·DROP 같은 구조 정의, DML은 SELECT·INSERT·UPDATE·DELETE 같은 데이터 조회·조작으로 분류하는 관례가 있다. SELECT를 별도 DQL로 분류하는 자료도 있으므로 시험에서 사용하는 분류를 확인한다. DCL은 GRANT·REVOKE 같은 권한, TCL은 COMMIT·ROLLBACK·SAVEPOINT 같은 거래 제어다. 특정 제품에서 DDL이 암묵적으로 커밋하는 경우가 있어 모두 동일한 롤백 동작으로 가정하지 않는다.

일반 뷰는 질의 정의로 논리적인 테이블을 제공한다. 보통 매 조회 시 해당 정의에 따라 결과를 얻으며 독립적인 전체 결과 저장 본이라는 뜻은 아니다. 물리화 뷰는 결과를 저장하여 조회에 활용하지만 갱신 시점·신선도·갱신 비용을 관리한다. 조인·집계·DISTINCT 등이 있는 뷰는 갱신이 제한될 수 있다. 모든 뷰가 갱신 가능하거나 모두 불가능하다는 명제는 틀리다.

```sql
CREATE VIEW done_txn AS
SELECT id,customer_id,region,amt FROM txn WHERE status='완료';
SELECT region,SUM(amt) FROM done_txn GROUP BY region;
```

뷰는 열·행 접근을 제한하는 수단이 될 수 있지만 기반 테이블 권한, 제품의 보안 실행 규칙과 함께 설계해야 한다. 뷰를 만들었다는 사실만으로 보안이 자동 완성되지 않는다. 저장 프로시저는 DB에 저장된 처리 로직이고 트리거는 지정된 데이터 사건 등에 반응하여 실행되는 로직이다. 숨은 변경·재귀·거래 경계를 읽을 수 있어야한다.

## 2. 로그·WAL·체크포인트·백업
장애 전 변경 기록을 로그에 남기고 필요한 로그가 데이터 페이지의 영구 반영보다 앞서 안정 저장되는 WAL 원칙을 이용하면 복구 판단을 할 수 있다. REDO는 커밋된 변경을 필요한 경우 다시 반영하고 UNDO는 미완료 변경의 영향을 취소하는 대표 개념이다. DBMS의 회복 알고리즘·steal/no-force 정책에 따라 필요한 조합과 기록 세부가 다르다.

### 손풀이 예제 17: 단순 복구 판정
문제에서 '커밋된 로그 변경은 REDO, 커밋되지 않은 변경은 UNDO하는 단순 복구 모델'이라고 명시한다. 로그는 T1 A100->90, T1 COMMIT, T2 B200->250, 장애다. T1의 A90은 지속되어야하므로 필요 시 REDO하고 T2의 B 변경은 UNDO하여 200으로 만든다. 이 예에서 체크포인트 유무나 페이지 반영 상태가 주어지지 않았다면 실제 필요한 I/O 횟수까지 추측하지 않는다.

체크포인트는 복구 시작 범위를 줄이는 데 도움을 준다. 체크포인트 직전에 모든 거래가 반드시 커밋하거나 이후 장애에 복구가 필요 없다는 뜻은 아니다. 백업은 복구에 사용할 별도 저장 본이고 로그 아카이브와 결합하면 특정 시점 복구를 제공할 수 있다. RAID는 저장 장치 장애 내 성 수단이며 잘못된 삭제·논리 손상·랜섬웨어까지 해결하는 독립 백업과 동일하지 않다.

복제는 데이터 사본을 유지하는 방식이다. 비동기 복제는 지연과 최신 변경 손실 가능성, 동기 복제는 응답 지연·가용성과 관련된 선택을 갖는다. 복제도 사용자의 잘못된 DELETE를 다른 사본에 전달할 수 있어 백업의 대체물로 단정하지 않는다. 이 책은 원리 수준이며 실제 금융 업무 복구 목표는 조직의 RPO·RTO 정책과 검증된 운영 절차를 따른다.

## 3. 60분 종합 실습: 초기 상태를 매번 복구
시간 60분은 자체 학습 권장량이고 공식 시험 시간은 아니다. 03-03의 txn과03-04의 customer 초기 데이터를 다시 만든다. 먼저 예상 결과를 적고 질의를 실행한다. 정렬이 필요한 답안은 ORDER BY를 명시한다.

### 실습 A: 고객별 완료 거래 집계
요구: 모든 고객을 표시하고 완료 거래 수와 알려진 금액 합계를 구한다. 거래가 없거나 완료 금액이 전부 NULL이면 합계 0. 고객 ID 오름차순.

```sql
SELECT c.customer_id,c.name,COUNT(t.id) AS done_n,
 COALESCE(SUM(t.amt),0) AS done_amt
FROM customer c LEFT JOIN txn t
 ON c.customer_id=t.customer_id AND t.status='완료'
GROUP BY c.customer_id,c.name ORDER BY c.customer_id;
```

예상 결과는 1 가람 2건 100,2 나래 1건 200,3 다온 1건 300,4 라 온 1건 0,5 마루 0건 0이다. COUNT(t.amt)를 쓰면 가람의 NULL 금액 거래를 제외해 1건이 되므로 '거래 수' 요구를 충족하지 못한다. 합계 0과 알려진 0원 거래 존재 여부도 구분할 수 있어야한다.

### 실습 B: 완료 거래 평균보다 큰 알려진 거래
완료 amt의 평균은 150이다. amt>150 인 완료 거래는 ID3과 5다.

```sql
SELECT id,customer_id,amt FROM txn
WHERE status='완료' AND amt>(
 SELECT AVG(amt) FROM txn WHERE status='완료'
)
ORDER BY amt DESC,id;
```

정렬 결과는 ID5 금액 300,ID3 금액 200이다. 평균을 구할 때 취소 50을 넣으면 평균 130으로 바뀌므로 바깥·안쪽 조건 모두 확인한다. NULL을 0으로 치환하는 평균 120도 요구에 따라 다른 통계다.

### 실습 C: 알려진 완료 금액이 없는 고객
요구는 '거래가 없음'이 아니라 'amt가 비NULL인 완료 거래가 없음'이다. 초기 데이터에서 고객 5 만 해당하지만, 고객 1의 100 거래를 삭제하면 고객 1도 해당한다. NULL 거래가 남는다는 사실 때문에 일반 거래 없음 질의와 다르다.

```sql
SELECT c.customer_id FROM customer c
WHERE NOT EXISTS (
 SELECT 1 FROM txn t WHERE t.customer_id=c.customer_id
  AND t.status='완료' AND t.amt IS NOT NULL
)
ORDER BY c.customer_id;
```

### 실습 D: 취소 기록이 있고 완료 기록도 있는 고객
EXISTS 두 개를 AND로 연결한다. 초기 상태에서는 고객 2다. 고객별 거래 원본을 두 번 직접 조인하면 완료 × 취소 조합 수만큼 중복될 수 있다.

```sql
SELECT c.customer_id FROM customer c
WHERE EXISTS (SELECT 1 FROM txn t
 WHERE t.customer_id=c.customer_id AND t.status='취소')
AND EXISTS (SELECT 1 FROM txn t
 WHERE t.customer_id=c.customer_id AND t.status='완료')
ORDER BY c.customer_id;
```

## 4. 쓰기 실습은 조회와 분리
읽기 실습이 끝난 뒤 별도 복사 DB에서 거래를 시작한다. 완료 금액을 +10한 뒤 해당 행을 조회하고 ROLLBACK한다. SQLite에서는 BEGIN,ROLLBACK으로 확인 가능하다. 원본 사용자 DB를 쓰지 않는다. UPDATE의 WHERE를 빼면 대상 범위가 달라짐을 먼저 예상한다. DELETE와 DROP은 행 삭제와 구조 제거의 차이다.

## 5. 시험용 오답 점검 순서
1. 결과 행의 단위는 고객·거래·지점 중 무엇인가?
2. 같은 키가 여러 번 나올 수 있는가? 조인 증 폭은 없는 가?
3. NULL은 제외·0대 체·별도 분류 중 어느 요구인가?
4. WHERE와 HAVING·ON의 위치가 결과를 바꾸는가?
5. 순위의 동률과 정렬은 결정되었는가?
6. 함수·행 제한·날짜가 허용 DBMS 문법에 맞는가?

### 완료 기준
24 문항에서 정답만 맞히지 말고 오답을 최소 한 가지 반례로 반박한다. A-D 실습은 실행 전 결과를 쓰고 질의를 독립 작성한다. 실패한 문제는 정의를 그대로 베끼지 말고 '내가 잘못 가정 한 행·NULL·순서'를 한 문장으로 적는다. 1일·3일·7일 뒤 초기 데이터를 다시 만들어 같은 요구를 재작성한다.

참고: [SQLite 트랜잭션](https://www.sqlite.org/lang_transaction.html), [PostgreSQL WAL 소개](https://www.postgresql.org/docs/current/wal-intro.html), [PostgreSQL 백업](https://www.postgresql.org/docs/current/backup.html). 복구 모델·SQL 실습·권장 시간은 자체 제작이다.

## 강화 실습: 파일 대신 메모리 DB에서 NULL·집계·롤백을 검증한다
아래 Python 예제는 :memory: DB만 사용한다. 실행할 때 기존 파일이나 실제 업무 DB를 연결하지 않는다. 값은 매개변수로 바인딩하며 테이블 이름을 사용자 입력으로 조합하지 않는다.

```python
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v INTEGER)")
con.executemany("INSERT INTO t VALUES (?, ?)",
                [(1, 10), (2, 10), (3, None), (4, 20)])
con.commit()
row = con.execute("SELECT COUNT(*), COUNT(v), SUM(v) FROM t").fetchone()
assert row == (4, 3, 40)
con.execute("UPDATE t SET v = ? WHERE id = ?", (99, 1))
con.rollback()
assert con.execute("SELECT v FROM t WHERE id = 1").fetchone()[0] == 10
con.close()
```

INSERT 후 commit이 있는 이유는 기존 샘플을 확정해 UPDATE만 롤백하기 위해서다. SQLite의 트랜잭션 기본 설정과 Python 버전에 따라 명시적 설정을 검토하며, 이 예제의 검증 결과를 Oracle/MySQL의 전체 동작 보장으로 확대하지 않는다.

**복구 반례:** 마지막 백업 뒤의 로그가 일부 없으면 백업 시점 이후 원하는 모든 거래를 복원할 수 없다. 복제본에도 잘못된 DELETE가 전달될 수 있다. 복구 시험에서는 백업 파일 존재 외에 복원 가능성·로그 연속성·복구 시점·검증 절차를 기록한다.
