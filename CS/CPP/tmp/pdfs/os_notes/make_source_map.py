import json,re
from pathlib import Path
root=Path(__file__).parent
# Printed page labels below were transcribed from the five supplied contents scans.
toc='''1|서론|3|1.1 운영체제가 할 일=4;1.2 컴퓨터 시스템의 구성=7;1.3 컴퓨터 시스템 구조=16;1.4 운영체제의 작동=23;1.5 자원 관리=28;1.6 보안과 보호=35;1.7 가상화=36;1.8 분산 시스템=38;1.9 커널 자료구조=39;1.10 계산 환경=43;1.11 무료 및 공개 소스 운영체제=50;1.12 요약=56
2|운영체제 구조|61|2.1 운영체제 서비스=62;2.2 사용자와 운영체제 인터페이스=64;2.3 시스템 콜=68;2.4 시스템 서비스=82;2.5 링커와 로더=84;2.6 응용 프로그램이 운영체제마다 다른 이유=86;2.7 운영체제 설계 및 구현=88;2.8 운영체제 구조=90;2.9 운영체제 빌딩과 부팅=100;2.10 운영체제 디버깅=105;2.11 요약=110
3|프로세스|117|3.1 프로세스 개념=118;3.2 프로세스 스케줄링=123;3.3 프로세스에 대한 연산=128;3.4 프로세스 간 통신=137;3.5 공유 메모리 시스템에서의 프로세스 간 통신=139;3.6 메시지 전달 시스템에서의 프로세스 간 통신=141;3.7 IPC 시스템의 사례=146;3.8 클라이언트 서버 환경에서 통신=161;3.9 요약=169
4|스레드와 병행성|175|4.1 개요=176;4.2 다중 코어 프로그래밍=178;4.3 다중 스레드 모델=182;4.4 스레드 라이브러리=185;4.5 암묵적 스레딩=194;4.6 스레드와 관련된 문제들=206;4.7 운영체제 사례=213;4.8 요약=215
5|CPU 스케줄링|219|5.1 기본 개념=220;5.2 스케줄링 기준=225;5.3 스케줄링 알고리즘=226;5.4 스레드 스케줄링=239;5.5 다중 처리기 스케줄링=242;5.6 실시간 CPU 스케줄링=250;5.7 운영체제 사례들=259;5.8 알고리즘의 평가=268;5.9 요약=274
6|동기화 도구들|283|6.1 배경=283;6.2 임계구역 문제=286;6.3 Peterson의 해결안=288;6.4 동기화를 위한 하드웨어 지원=291;6.5 Mutex Locks=297;6.6 세마포=299;6.7 모니터=303;6.8 라이브니스=310;6.9 평가=312;6.10 요약=315
7|동기화 예제|319|7.1 고전적인 동기화 문제들=319;7.2 커널 안에서의 동기화=327;7.3 POSIX 동기화=330;7.4 Java에서의 동기화=334;7.5 대체 방안들=342;7.6 요약=345
8|교착 상태|349|8.1 시스템 모델=350;8.2 다중 스레드 응용에서의 교착 상태=351;8.3 교착 상태 특성=353;8.4 교착 상태 처리 방법=358;8.5 교착 상태 예방=360;8.6 교착 상태 회피=363;8.7 교착 상태 탐지=371;8.8 교착 상태로부터 회복=376;8.9 요약=378
9|메인 메모리|385|9.1 배경=385;9.2 연속 메모리 할당=393;9.3 페이징=397;9.4 페이지 테이블의 구조=409;9.5 스와핑=414;9.6 사례: Intel 32비트와 64비트 구조=417;9.7 사례: ARM 구조=421;9.8 요약=423
10|가상 메모리|427|10.1 배경=428;10.2 요구 페이징=431;10.3 쓰기 시 복사=438;10.4 페이지 교체=440;10.5 프레임의 할당=454;10.6 스래싱=461;10.7 메모리 압축=467;10.8 커널 메모리의 할당=469;10.9 기타 고려 사항=473;10.10 운영체제의 예=480;10.11 요약=483
11|대용량 저장장치 구조|491|11.1 대용량 저장장치 구조의 개관=491;11.2 디스크 스케줄링=500;11.3 NVM 스케줄링=504;11.4 오류 감지 및 수정=505;11.5 저장장치 관리=506;11.6 스왑 공간 관리=511;11.7 저장장치 연결=513;11.8 RAID 구조=517;11.9 요약=530
12|입출력 시스템|535|12.1 개관=535;12.2 입출력 하드웨어=536;12.3 응용 입출력 인터페이스=548;12.4 커널 입출력 서브시스템=556;12.5 입출력 요구를 하드웨어 연산으로 변환=566;12.6 STREAMS=568;12.7 성능=570;12.8 요약=574
13|파일 시스템 인터페이스|579|13.1 파일 개념=579;13.2 접근 방법=590;13.3 디렉터리 구조=593;13.4 보호=603;13.5 메모리 사상 파일=608;13.6 요약=613
14|파일 시스템 구현|617|14.1 파일 시스템 구조=618;14.2 파일 시스템 구현=620;14.3 디렉터리 구현=623;14.4 할당 방법=625;14.5 가용 공간의 관리=634;14.6 효율과 성능=637;14.7 복구=642;14.8 예: WAFL 파일 시스템=646;14.9 요약=650
15|파일 시스템 내부구조|655|15.1 파일 시스템=655;15.2 파일 시스템 마운팅=657;15.3 파티션과 마운팅=659;15.4 파일 공유=660;15.5 가상 파일 시스템=662;15.6 원격 파일 시스템=664;15.7 일관성의 의미=668;15.8 NFS=669;15.9 요약=676
16|보안|681|16.1 보안 문제=681;16.2 프로그램 위협=685;16.3 시스템과 네트워크 위협=696;16.4 보안 도구로서 암호 기법=699;16.5 사용자 인증=712;16.6 보안 방어의 구현=717;16.7 예: Windows 10=727;16.8 요약=730
17|보호|733|17.1 보호의 목표=733;17.2 보호의 원칙=734;17.3 보호 링=735;17.4 보호의 영역=738;17.5 접근 행렬=742;17.6 접근 행렬의 구현=746;17.7 접근 권한의 취소=749;17.8 역할 기반 액세스 제어=751;17.9 강제적 접근 제어=752;17.10 자격-기반 시스템=753;17.11 기타 보호 개선 방법=755;17.12 언어 기반의 보호=758;17.13 요약=764
18|가상 머신|769|18.1 개요=769;18.2 역사=771;18.3 장점 및 특징=772;18.4 빌딩 블록=775;18.5 VM 유형 및 구현=781;18.6 가상화와 운영체제 구성요소=789;18.7 사례=796;18.8 가상화 연구=798;18.9 요약=799
19|네트워크 및 분산 시스템|803|19.1 분산 시스템의 장점=803;19.2 네트워크 구조=805;19.3 통신 구조=808;19.4 네트워크 및 분산 운영체제=820;19.5 분산 시스템의 설계 문제=824;19.6 분산 파일 시스템=829;19.7 DFS 명명 및 투명성=833;19.8 원격 파일 액세스=836;19.9 분산 파일 시스템에 대한 최종 생각=840;19.10 요약=841
20|Linux 시스템|847|20.1 Linux 역사=847;20.2 설계 원칙=853;20.3 커널 모듈=856;20.4 프로세스 관리=860;20.5 스케줄링=864;20.6 메모리 관리=870;20.7 파일 시스템=880;20.8 입/출력=887;20.9 프로세스 간 통신=890;20.10 네트워크 구조=891;20.11 보안=894;20.12 요약=897
21|윈도우 10|901|21.1 역사=901;21.2 설계 원칙=906;21.3 시스템 구성요소=920;21.4 터미널 서비스와 빠른 사용자 교체=960;21.5 파일 시스템=961;21.6 네트워킹=968;21.7 프로그래머 인터페이스=973;21.8 요약=986'''
chapters=[]
for line in toc.splitlines():
 n,title,start,secs=line.split('|'); secs=[dict(number=a.split(' ',1)[0],title=a.split(' ',1)[1],printed_start=int(b)) for s in secs.split(';') for a,b in [s.rsplit('=',1)]]
 chapters.append(dict(number=int(n),title=title,printed_start=int(start),sections=secs))
raw=json.loads((root/'footer_candidates.json').read_text(encoding='utf-8'))
pages=[]
manual={6:1,7:3,226:281,244:300,324:383,346:406,429:489,516:577,615:679}
part_pages={6:1,226:3,324:4,429:5,516:6,615:7}
for d in raw:
 p=d['pdf']; top=[x['n'] for x in d['candidate'] if x['y']<500]
 lower=[x['n'] for x in d['candidate'] if x['y']>2000 and x['n']>20]
 num=manual.get(p, max(top) if top else max(lower) if lower else None)
 if p<=5:num=None
 ch=next((x['number'] for i,x in enumerate(chapters) if num and x['printed_start']<=num<(chapters[i+1]['printed_start'] if i+1<len(chapters) else 989)),None)
 if p in part_pages:ch=None
 pages.append(dict(pdf=p,printed=num,chapter=ch,part=part_pages.get(p),kind='contents' if p<=5 else 'part_intro' if p in part_pages else 'chapter',head=d['head'],method='image_checked_manual' if p in manual else 'scan_page_number_ocr'))
for i,p in enumerate(pages):
 if p['pdf']<=6:continue
 prev=pages[i-1]
 if p['printed'] and prev['printed'] and (p['printed']-prev['printed']!=1):print('GAP',prev['pdf'],prev['printed'],'->',p['pdf'],p['printed'])
for i,c in enumerate(chapters):
 cpages=[p for p in pages if p['chapter']==c['number']]; c['pdf']=[p['pdf'] for p in cpages];c['printed']=[p['printed'] for p in cpages];c['available']=bool(cpages)
 for j,s in enumerate(c['sections']):
  end=c['sections'][j+1]['printed_start'] if j+1<len(c['sections']) else (chapters[i+1]['printed_start'] if i+1<len(chapters) else 989)
  found=[p for p in cpages if s['printed_start']<=p['printed']<end]
  s['pdf']=[p['pdf'] for p in found];s['printed']=[p['printed'] for p in found];s['available']=bool(found)
 outdir=root/'chapters'/'ocr';outdir.mkdir(parents=True,exist_ok=True)
 for dirname,suffix in [('ocr',''),('ocr_tesseract','_tesseract')]:
  text='\n\n'.join(f"===== PDF {p['pdf']} / 인쇄 {p['printed']} =====\n"+(root/dirname/f"{p['pdf']:04d}.txt").read_text(encoding='utf-8-sig') for p in cpages if (root/dirname/f"{p['pdf']:04d}.txt").exists())
  (outdir/f"ch{c['number']:02d}{suffix}.txt").write_text(text,encoding='utf-8')
nums={p['printed'] for p in pages if p['printed']}
missing=[n for n in range(1,680) if n not in nums]
result=dict(total_pdf_pages=615,contents_pdf=[1,2,3,4,5],pages=pages,chapters=chapters,missing_printed_within_1_679=missing,notes=['표제지와 저자 정보 미제공','제2장 및 제16~21장과 부록 본문은 미제공','PDF615는 Part7 도입만 제공한다.'])
(root/'source_map.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('MAPPED',len(pages),'UNKNOWN',[(x['pdf'],x['head']) for x in pages if x['pdf']>5 and x['printed'] is None])
print('CHAPTERS',[(c['number'],min(c['pdf'],default=0),max(c['pdf'],default=0),min(c['printed'],default=0),max(c['printed'],default=0)) for c in chapters])
