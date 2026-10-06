# SQL12제 문제만

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

## 데이터 customer

| id | region |
| --- | --- |
| 1 | 부산 |
| 2 | 부산 |
| 3 | 경기 |
| 4 | 경기 |
| 5 | 부산 |
| 6 | 경기 |

## 데이터 account

| id | cid | state |
| --- | --- | --- |
| 101 | 1 | OPEN |
| 102 | 1 | OPEN |
| 201 | 2 | CLOSED |
| 301 | 3 | OPEN |
| 401 | 4 | OPEN |
| 501 | 5 | OPEN |

## 데이터 txn

| id | aid | ts | amount | state | category |
| --- | --- | --- | --- | --- | --- |
| 1 | 101 | 2026-01-01 09:00:00 | 100 | DONE | A |
| 2 | 101 | 2026-01-01 10:00:00 | 200 | DONE | B |
| 3 | 102 | 2026-01-02 10:00:00 | NULL | DONE | A |
| 4 | 201 | 2026-01-03 10:00:00 | 300 | DONE | A |
| 5 | 301 | 2026-01-03 10:00:00 | 400 | DONE | A |
| 6 | 301 | 2026-01-03 10:00:00 | -50 | DONE | B |
| 7 | 301 | 2026-01-05 10:00:00 | 100 | CANCEL | C |
| 8 | 401 | 2026-02-01 10:00:00 | 0 | DONE | C |
| 9 | 501 | 2026-02-01 10:00:00 | 500 | PENDING | A |
| 10 | 101 | 2026-02-01 10:00:00 | 50 | DONE | C |
| 11 | 401 | 2026-02-01 12:00:00 | NULL | DONE | A |
| 12 | 301 | 2026-02-02 12:00:00 | 150 | DONE | C |

## 데이터 event

| ingest_id | event_id | value |
| --- | --- | --- |
| 1 | E1 | 10 |
| 2 | E2 | 20 |
| 3 | E1 | 12 |
| 4 | E3 | 30 |
| 5 | E2 | NULL |

## 데이터 metric

| region | total | fail |
| --- | --- | --- |
| 부산 | 10 | 1 |
| 부산 | 100 | 20 |
| 경기 | 2 | 1 |
| 경기 | 8 | 1 |
| 전국 | 0 | 0 |

## 데이터 book

| aid | amount |
| --- | --- |
| 1 | 100 |
| 2 | 200 |
| 3 | NULL |
| 4 | 300 |

## 데이터 report

| aid | amount |
| --- | --- |
| 1 | 100 |
| 2 | 180 |
| 3 | 0 |
| 5 | 500 |

## 데이터 requirement

| category |
| --- |
| A |
| B |
| C |

# SX01 없는 고객까지 집계

모든 고객의 DONE 거래 수·알려진 금액 수·알려진 금액 합을 구한다. DONE 거래가 없거나 금액이 전부 NULL이면 알려진 합은0으로 표시하되 두 종류의 건수를 같이 표시한다. 계좌 상태는 필터하지 않는다. 출력:id,done_n,known_n,known_sum, id순.

# SX02 행 조건과 그룹 조건

DONE 거래가2개 이상이고 알려진 금액 합이300 이상인 고객을 찾는다. 출력:cid,done_n,known_sum, cid순.

# SX03 금액 NULL과 존재 여부

알려진 양수 DONE 거래가 하나도 없는 모든 고객을 구한다. 금액 NULL·0·음수는 양수 거래가 아니다. 출력:id, id순.

# SX04 최근 거래와 동률

거래가 있는 계좌마다 상태를 구분하지 않고 가장 최근 거래1개를 고른다. ts가 같으면 id가 큰 거래가 최근이다. 출력:aid,id,state, aid순.

# SX05 월별 집계와 알려진 값

ts는 고정 길이 ISO 형식 TEXT다. 월별 DONE 거래 수·알려진 금액 합을 출력한다. 출력:month,done_n,known_sum, 월순.

# SX06 동률을 깨는 누적 합

DONE 거래만 대상으로 계좌별 ts,id순 알려진 금액 누적합과 알려진 금액 누적 건수를 구한다. 초기 알려진 금액이 없으면 합0. 출력:aid,id,running_sum,known_n, aid·ts·id순.

# SX07 지점별 상위 두 금액 수준

OPEN 계좌의 알려진 DONE 금액 합(없으면0)을 구해 지역별 상위 두 개의 서로 다른 합계 수준을 모두 고른다. 동률 계좌는 전부 포함. 출력:region,aid,total,rank_n, 지역·순위·aid순.

# SX08 중복 이벤트의 최신 수신

event_id별 ingest_id가 가장 큰 행을 남긴다. 최신 value가 NULL이어도 이전 비NULL값으로 대신하지 않는다. 출력:event_id,ingest_id,value, event_id순.

# SX09 모든 필수 항목 충족

requirement의 모든 category에 대해 DONE 거래가 한 번 이상 있는 고객을 찾는다. 금액은 조건이 아니다. 필수항목 집합이 비어 있으면 모든 고객을 반환한다. 출력:id, id순.

# SX10 비율의 가중 평균

metric의 지역별 전체 오류율을 백분율로 소수셋째자리까지 출력한다. 전체 건수0이면 NULL. 출력:region,error_pct, 지역순.

# SX11 두 원장의 불일치 찾기

book/report는 aid별 한 행이며 금액 NULL은 미확인이다. 양쪽 존재하고 금액이 같은 행만 제외하고, 누락·미확인·금액 차이를 구분한다. 출력:aid,book_amt,report_amt,reason, aid순. 판정 우선순위는 book 행 부재 MISSING_BOOK, report 행 부재 MISSING_REPORT, 양쪽 존재하나 금액 하나라도 NULL이면 UNKNOWN, 양쪽 알려진 금액이 다르면 DIFF다. 양쪽 알려진 금액이 같으면 MATCH로 보되 출력에서 제외한다.

# SX12 30분 단위 이용 세션

DONE 거래를 계좌별 ts,id순으로 본다. 최초 거래 또는 직전 DONE 거래와30분 이상 차이 나면 새 세션이다. 출력:aid,id,session_n, aid·ts·id순. 이 답안은 SQLite 날짜 함수 기준이다.
