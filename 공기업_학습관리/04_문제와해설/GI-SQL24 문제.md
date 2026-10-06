# SQL 실습 24개

SQLite 기반, 전부 가상 데이터. 답을 보기 전에 행 수·NULL·순서를 예측한다.

테이블: team(id,name), employee(id,name,team_id,salary,score,active), device(id,name), batch(id,device_id,day,inspected,defect), bonus(id,employee_id,amount). salary·bonus 값은 가상 단위이며 연봉 정보가 아니다.

원본 데이터는 00_setup.sql에 모두 있다. 정답 검증기는 매번 새 메모리 DB를 만들며 training.db를 수정하지 않는다.

## SQL01 필터와 정렬

활성 직원 중 salary>=50의 id,name,salary를 salary 내림차순,id 오름차순으로 조회하라.

## SQL02 NULL 검사

score가 없는 직원의 id,name을 id순으로 조회하라.

## SQL03 집계 분모

전체 직원의 COUNT(*), COUNT(score), AVG(score)를 한 행으로 조회하라.

## SQL04 내부 조인

팀이 지정된 직원의 id,name,팀명을 id순으로 조회하라.

## SQL05 외부 조인

모든 직원 id,name,팀명을 출력하라. 미지정 팀은 문자열 미지정으로 대체하고 id순 정렬한다.

## SQL06 빈 팀 포함 집계

모든 팀의 id,name,직원 수를 출력하라. 빈 팀도 0으로 출력하고 team.id순 정렬한다.

## SQL07 WHERE와 HAVING

활성 직원이 2명 이상인 지정 팀의 team_id,인원,평균 salary를 조회하라. team_id순 정렬한다.

## SQL08 조건부 집계

각 지정 팀의 team_id,전체 인원,활성 인원을 team_id순 출력하라.

## SQL09 평균 초과

전체 평균 salary보다 큰 직원 id,salary를 id순 출력하라.

## SQL10 팀 평균 초과

지정 팀에서 자기 팀 평균 salary보다 큰 직원 id,team_id,salary를 id순 출력하라.

## SQL11 NOT EXISTS

직원이 전혀 없는 팀 id,name을 id순 출력하라.

## SQL12 NOT IN 함정 재현

SELECT id FROM team WHERE id NOT IN (SELECT team_id FROM employee) ORDER BY id;의 결과를 예측하라.

## SQL13 중복 제거

employee의 서로 다른 salary를 오름차순 출력하라.

## SQL14 팀별 최고 한 명

지정 팀마다 salary 최고 직원 한 명의 id,team_id,salary를 출력한다. 동률은 id 작은 사람. team_id순 정렬한다.

## SQL15 RANK와 DENSE_RANK

salary 내림차순으로 전체 직원 id,salary,RANK,DENSE_RANK를 출력하라. 최종 정렬 salary DESC,id.

## SQL16 전체 결함률

모든 batch의 총 검사 수,총 결함 수,결함률(%)을 소수2자리로 출력하라.

## SQL17 장비별 결함률

모든 장비 id,총 검사 수,결함률%를 출력하라. 분모0이면 NULL, 소수2자리. id순.

## SQL18 날짜별 누적

날짜별 검사 합계를 먼저 집계하고 day,당일 검사합,누적합을 날짜순 출력하라.

## SQL19 LAG 비교

날짜별 검사 합계의 day,n,전일 관측 합계,증감량을 출력한다. 첫날 이전 값과 증감은 NULL.

## SQL20 가장 최근 배치

장비마다 가장 최근 day의 배치 id,device_id,day를 출력한다. 같은 day면 큰id. device_id순.

## SQL21 ON과 WHERE 비교

모든 팀을 유지하면서 활성 직원만 연결한다. t.id와 활성 직원 id를 출력하고 t.id,e.id순 정렬하라.

## SQL22 반복 행의 조인 집계

보너스가 있는 직원의 id,salary,보너스 합을 한 직원당 한 행, id순 출력하라.

## SQL23 UNION ALL

SELECT salary FROM employee WHERE id=2 UNION ALL SELECT salary FROM employee WHERE id=4; 결과를 예측하라.

## SQL24 인덱스 동등 결과

team_id=1인 직원 id,name을 id순 조회한다. 인덱스 생성 전후에도 결과가 같은지 확인하라.
