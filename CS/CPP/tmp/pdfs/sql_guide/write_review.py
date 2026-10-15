import json
from pathlib import Path
BASE=Path(__file__).parent
chs=sorted([json.loads(p.read_text(encoding='utf-8-sig')) for p in (BASE/'chapters').glob('*.json')],key=lambda x:x['order'])
def p(x):return dict(type='p',text=x)
def h(x):return dict(type='heading',text=x)
def b(x):return dict(type='bullets',items=x)
def sy(cat,name,form,role,src):return dict(category=cat,name=name,form=form,role=role,source=src)
review={'scope_note':'수록 범위는 제공된 786쪽 PDF에서 확인되는 본문 12장입니다. 목차에만 기재된 부록은 파일에 없어 포함하지 않았습니다. 책 소개·저자·출판 정보와 연습문제 재출제는 제외했습니다. 출처의 쪽수는 인쇄면 번호가 아닌 원문 PDF의 파일 쪽수입니다. DBMS 지원 범위와 동작 비교는 원문의 설명 기준이며, 코드는 원문 식별자·상수·조건을 보존하고 공백과 줄 배치만 정리했습니다. 원문에서 문장·코드가 어긋나는 부분은 해당 해설에서 구분했습니다.',
 'blocks':[p('데이터 모델은 저장할 대상·속성·관계·식별자를 정의한다. SQL은 그 모델의 데이터를 원하는 결과 집합으로 표현한다. 실행계획과 I/O 구조는 결과를 얻는 실제 비용을 설명하며, 튜닝은 불필요한 읽기·정렬·호출을 줄인다. 트랜잭션과 동시성 제어는 그 작업이 함께 수행될 때의 정확성을 지킨다.')], 'syntax':[], 'comparisons':[], 'code_groups':[], 'checklist':[]}
for ch in chs:
 review['blocks'] += [h(ch['part']+' / '+ch['title']),p(ch['source_range']),b(ch['final_summary'])]
 review['checklist'].append(dict(title=ch['part']+' / '+ch['title'],items=ch.get('checklist',[])))

basic=BASE/'syntax_basic.json'
if basic.exists(): review['syntax']+=json.loads(basic.read_text(encoding='utf-8-sig'))
S=review['syntax']
S += [
sy('서브쿼리·집합 결합','단일·다중 행 비교','칼럼 = (서브 쿼리)\n칼럼 IN (서브 쿼리)','반환 행 수에 맞게 단일·다중 행 연산자를 대응한다.','273-278쪽'),
sy('서브쿼리·집합 결합','ALL / ANY / SOME','비교연산자 ALL(서브 쿼리)\n비교연산자 ANY(서브 쿼리)','모든 값 / 하나 이상의 값 만족 여부. SOME은 ANY와 같다.','277쪽'),
sy('서브쿼리·집합 결합','EXISTS','EXISTS (SELECT 1 ... )','조건을 만족하는 행의 존재만 확인한다.','281쪽'),
sy('서브쿼리·집합 결합','다중 칼럼 비교','(TEAM_ID, HEIGHT) IN (SELECT TEAM_ID, MIN(HEIGHT) ... )','같은 위치의 칼럼 쌍을 동시에 비교한다.','279쪽'),
sy('서브쿼리·집합 결합','스칼라·인라인 뷰','SELECT ... (SELECT ...) ...\nFROM (SELECT ...) 별칭','한 값을 제공하는 서브쿼리와 중간 집합을 제공하는 서브쿼리를 구별한다.','281-284쪽'),
sy('서브쿼리·집합 결합','CREATE / DROP VIEW','CREATE VIEW 뷰명 AS SELECT ...\nDROP VIEW 뷰명;','SELECT 정의를 저장·제거한다.','286-287쪽'),
sy('서브쿼리·집합 결합','집합 연산','SELECT ... UNION [ALL] SELECT ...\nINTERSECT / MINUS / EXCEPT','합집합·교집합·차집합. UNION ALL은 중복을 유지한다. 최종 ORDER BY는 마지막이다.','288-300쪽'),
sy('다중 수준 집계','ROLLUP','GROUP BY ROLLUP(B.DNAME, A.JOB)','계층적 소계와 총계. 인수 순서가 중요하다.','302-309쪽'),
sy('다중 수준 집계','CUBE','GROUP BY CUBE(B.DNAME, A.JOB)','그룹 항목의 모든 조합을 집계한다.','310-312쪽'),
sy('다중 수준 집계','GROUPING SETS','GROUP BY GROUPING SETS(B.DNAME, A.JOB)','명시한 집계 집합을 결합한다.','312-316쪽'),
sy('다중 수준 집계','GROUPING','GROUPING(표현식)','소계로 묶인 항목을 1, 그 외를 0으로 구별한다.','305-307쪽'),
sy('윈도우 분석','OVER','함수(인수) OVER ([PARTITION BY 칼럼] [ORDER BY ...] [WINDOWING ...])','파티션·분석 순서·프레임을 정한다. 함수별 사용 조건을 따른다.','317-318쪽'),
sy('윈도우 분석','순위 함수','RANK() / DENSE_RANK() / ROW_NUMBER() OVER (...)','동률 뒤 건너뛰기 / 연속 등수 / 고유 행 번호.','319-322쪽'),
sy('윈도우 분석','집계 함수와 OVER','SUM(SAL) OVER (PARTITION BY MGR)\nMAX / MIN / AVG / COUNT ... OVER (...)','개별 행을 유지하면서 파티션·프레임 집계를 표시한다.','323-329쪽'),
sy('윈도우 분석','ROWS / RANGE','ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING\nRANGE BETWEEN 50 PRECEDING AND 150 FOLLOWING','물리적 이웃 행 수 / 정렬 값 범위. 파티션 경계와 동률 포함을 주의한다.','327-329쪽'),
sy('윈도우 분석','첫 값·마지막 값','FIRST_VALUE(칼럼) OVER (...)\nLAST_VALUE(칼럼) OVER (...)','지정 윈도우의 첫·끝 값을 선택한다. 동률의 세부 정렬과 프레임이 중요하다.','330-332쪽'),
sy('윈도우 분석','이전·이후 값','LAG(SAL, 2, 0) OVER (ORDER BY HIREDATE)\nLEAD(HIREDATE, 1) OVER (...)','앞·뒤 행 값. 이동 거리와 행이 없을 때의 대체값을 인수로 정한다.','333-334쪽'),
sy('윈도우 분석','비율·분할','RATIO_TO_REPORT / PERCENT_RANK / CUME_DIST / NTILE(N) ... OVER (...)','합계 대비 비율, 상대 순위, 누적 비율, N개 그룹 분배를 구별한다.','335-338쪽'),
sy('Top N·계층','Oracle ROWNUM','SELECT ... FROM (SELECT ... ORDER BY ...) WHERE ROWNUM <= N','먼저 정렬한 집합에 행 제한을 적용한다.','339-340쪽'),
sy('Top N·계층','SQL Server TOP','TOP(Expression) [PERCENT] [WITH TIES]','행 수·비율 제한. WITH TIES는 마지막 동순위까지 포함한다.','341-342쪽'),
sy('Top N·계층','ROW LIMITING','[OFFSET offset ROWS]\n[FETCH FIRST rowcount ROWS ONLY]','정렬 결과에서 건너뛰기·반환 수 제한. 원문은 NEXT·PERCENT·WITH TIES도 설명한다.','342-343쪽'),
sy('Top N·계층','셀프 조인','FROM EMP WORKER, EMP MANAGER\nWHERE MANAGER.EMPNO = WORKER.MGR','동일 테이블을 역할별 별칭으로 구분해 연결한다.','344-347쪽'),
sy('Top N·계층','Oracle 계층 전개','START WITH MGR IS NULL\nCONNECT BY MGR = PRIOR EMPNO','시작점과 부모·자식 연결 방향을 정한다.','348-352쪽'),
sy('Top N·계층','계층 표시·경로','LEVEL / CONNECT_BY_ISLEAF\nSYS_CONNECT_BY_PATH(칼럼, 구분자)\nCONNECT_BY_ROOT 칼럼','깊이·리프·경로·루트 표시. NOCYCLE과 형제 정렬도 문맥에 맞게 사용한다.','348-352쪽'),
sy('Top N·계층','재귀 CTE','WITH CTE AS (앵커 SELECT UNION ALL 재귀 SELECT) SELECT ... FROM CTE','앵커부터 이전 결과를 입력으로 반복하고 전체 결과를 합친다.','353-357쪽'),
sy('행·열 변환·패턴','PIVOT','PIVOT (SUM(SAL) FOR DEPTNO IN (10, 20, 30))','행 값을 열로 펼쳐 집계한다. 대상 밖 열은 집계 기준이다.','358-362쪽'),
sy('행·열 변환·패턴','UNPIVOT','UNPIVOT [INCLUDE NULLS] (SAL FOR DEPTNO IN (D10_SAL AS 10, D20_SAL AS 20))','열을 행으로 전환한다. NULL 포함 여부를 선택한다.','362-367쪽'),
sy('행·열 변환·패턴','정규 표현식 조건','REGEXP_LIKE(source_char, pattern [, match_param])','패턴 일치 여부로 행을 제한한다.','379-380쪽'),
sy('행·열 변환·패턴','정규 표현식 함수','REGEXP_REPLACE / REGEXP_SUBSTR / REGEXP_INSTR / REGEXP_COUNT','치환 문자열 / 일치 문자열 / 위치 / 횟수 반환. 선택 인수는 함수별로 확인한다.','380-383쪽'),
sy('행 변경','INSERT VALUES','INSERT INTO 테이블명 [(칼럼1, 칼럼2, ...)] VALUES (값1, 값2, ...);','한 행 입력. 칼럼과 값을 같은 순서로 대응한다.','391-392쪽'),
sy('행 변경','INSERT SELECT','INSERT INTO 테이블명 [(칼럼1, 칼럼2, ...)] 서브 쿼리;','조회된 여러 행을 입력한다.','393쪽'),
sy('행 변경','UPDATE','UPDATE 테이블명 SET 칼럼 = 값 [, ...] [WHERE 조건];','조건 대상 행을 수정한다. WHERE가 없으면 전체다.','394-396쪽'),
sy('행 변경','DELETE','DELETE [FROM] 테이블명 [WHERE 조건];','조건 대상 행을 삭제한다. 구조는 유지한다.','396-397쪽'),
sy('행 변경','MERGE','MERGE INTO 타깃 USING 소스 ON (조건)\nWHEN MATCHED THEN UPDATE ...\nWHEN NOT MATCHED THEN INSERT ...','소스와 타깃의 일치 여부로 수정·입력을 나눈다.','398-401쪽'),
sy('트랜잭션','확정·전체 취소','COMMIT;\nROLLBACK;','미확정 변경을 확정하거나 시작 전으로 취소한다.','403-409쪽'),
sy('트랜잭션','Oracle 저장점','SAVEPOINT 저장점명;\nROLLBACK TO 저장점명;','지정 시점 이후 변경만 취소한다.','410-416쪽'),
sy('트랜잭션','SQL Server 저장점','BEGIN TRAN\nSAVE TRAN 저장점명;\nROLLBACK TRAN 저장점명;','명시적 트랜잭션 안에서 부분 취소한다.','407-413쪽'),
sy('테이블·제약 정의','CREATE TABLE','CREATE TABLE 테이블명 (칼럼명 데이터유형 [기본값] [NOT NULL], ...);','칼럼·유형·기본값·제약조건을 정의한다.','418-424쪽'),
sy('테이블·제약 정의','키·무결성 제약','PRIMARY KEY / UNIQUE / NOT NULL / CHECK / FOREIGN KEY ... REFERENCES ...','유일성·필수값·값 조건·참조 관계를 제한한다.','423-424쪽'),
sy('테이블·제약 정의','조회 결과로 생성','CREATE TABLE TEAM_TEMP AS SELECT * FROM TEAM;\nSELECT * INTO TEAM_TEMP FROM TEAM;','Oracle CTAS / SQL Server SELECT INTO. 원문의 제약 복사 제한을 함께 확인한다.','426-427쪽'),
sy('테이블·제약 정의','칼럼 추가·삭제','ALTER TABLE ... ADD ...\nALTER TABLE ... DROP COLUMN ...','칼럼 추가·삭제. DBMS별 괄호·키워드 차이는 상세 노트 참고.','428-430쪽'),
sy('테이블·제약 정의','칼럼 변경·이름 변경','ALTER TABLE ... MODIFY (...)\nALTER TABLE ... ALTER COLUMN ...\nRENAME COLUMN ... TO ...','유형·기본값·필수 여부·이름 변경. 기존 자료와의 양립 조건을 확인한다.','431-435쪽'),
sy('테이블·제약 정의','제약 추가·제거','ALTER TABLE ... ADD CONSTRAINT ...\nALTER TABLE ... DROP CONSTRAINT ...','기존 테이블의 무결성 제약을 관리한다.','435-437쪽'),
sy('테이블·제약 정의','이름·전체 제거','RENAME ... TO ...\nTRUNCATE TABLE ...\nDROP TABLE ...','이름 변경 / 구조 유지 전체 행 제거 / 구조·데이터 제거.','438-442쪽'),
sy('사용자·권한','사용자 생성·삭제','CREATE USER ... IDENTIFIED BY ...\nDROP USER ... [CASCADE]','Oracle 사용자·객체 관리. SQL Server 로그인·사용자 매핑과 구별한다.','445-446,457쪽'),
sy('사용자·권한','시스템·객체 권한','GRANT CREATE TABLE TO SQLD;\nGRANT SELECT ON MENU TO SCOTT;\nREVOKE ... FROM ...','종류별 작업과 특정 객체의 작업 권한을 부여·회수한다.','445-455쪽'),
sy('사용자·권한','ROLE','CREATE ROLE LOGIN_TABLE;\nGRANT ... TO LOGIN_TABLE;\nGRANT LOGIN_TABLE TO SQLD;','권한을 ROLE에 묶어 사용자에게 부여한다.','454-458쪽')]

# 원문 코드의 식별자·형태를 그대로 재사용하는 튜닝·분석 문법 항목.
for cid,cat,name in [
 ('III1-C01','실행·분석·튜닝','Oracle 힌트'),('III1-C02','실행·분석·튜닝','SQL Server 힌트'),
 ('III2-C01','실행·분석·튜닝','예상 실행계획'),('III2-C02','실행·분석·튜닝','SQL 트레이스')]:
 entry=next(((ch,x) for ch in chs for x in ch.get('codes',[]) if x['id']==cid),None)
 if entry:
  ch,x=entry
  S.append(sy(cat,name,x['sql'],x['purpose'],','.join(map(str,x['source_pdf_pages']))+'쪽'))

for ch in chs:
 if ch.get('comparisons'):
  co=dict(ch['comparisons'][0]); co['title']=ch['id']+' / '+co['title'];review['comparisons'].append(co)

ids={x['id'] for ch in chs for x in ch.get('codes',[])}
groups=[('모델과 NULL의 의미',['I2-C01','I2-C03']),('기본 조회와 조건·조인',['II1-C01','II1-C06','II1-C10']),('서브쿼리·집합·집계',['II2-C02','II2-C04','II2-C05']),('행 분석과 상위 행 제한',['II2-C06','II2-C07','II2-C08','II2-C16']),('계층·행열 변환·패턴',['II2-C09','II2-C11','II2-C12','II2-C13']),('변경·트랜잭션·무결성',['II3-C04','II3-C05','II3-C08']),('권한 관리',['II3-C10'])]
for title,choices in groups:
 found=[i for i in choices if i in ids]
 if found:review['code_groups'].append(dict(title=title,code_ids=found))
for ch in chs:
 if ch['id'].startswith('III-') and ch.get('codes'):
  review['code_groups'].append(dict(title=ch['title'],code_ids=[ch['codes'][0]['id']]))

(BASE/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print('review prepared:',len(chs),'chapters,',len(S),'syntax entries')
