# ConfigWindow - Light / Pattern 탭 사용자 매뉴얼

## 화면 용도

이 화면은 EEC-P725R2 PG 장비의 통신 대상과 패턴별 전압 채널을 설정합니다. 설정이 틀리면 패턴이 점등되지 않거나 R/G/B가 다른 채널에 적용되어 검사와 CA410 결과가 잘못될 수 있습니다.

검사·Aging이 실행 중인 상태에서는 변경하거나 저장하지 마십시오.

## 1. EEC-P725R2 공통 설정

| 항목 | 사용 방법 | 주의사항 |
|---|---|---|
| Display Count | 실제 사용할 PG display 수를 입력합니다. | 수를 늘린 후에는 새로 나타난 endpoint 행의 Host/Port를 반드시 설정합니다. |
| Simulation Port Base | PG simulator의 시작 포트입니다. | simulator는 `127.0.0.1:(Base + Index)`를 사용합니다. 실 장비 포트와 충돌시키지 마십시오. |
| Pattern On Delay | 패턴·전압 적용 후 촬영 또는 측정 전까지 기다릴 시간을 ms로 입력합니다. | 짧으면 점등 안정 전 촬영될 수 있고, 길면 검사 시간이 증가합니다. |
| Connect Timeout | PG 연결 대기 시간을 입력합니다. | 단순 timeout 증가는 통신 장애 해결 방법이 아닙니다. 주소·케이블·PG 상태를 먼저 확인합니다. |
| Response Timeout | PG 명령 응답 대기 시간을 입력합니다. | 너무 짧으면 정상 통신도 실패할 수 있습니다. |

## 2. Display endpoint 설정

| 항목 | 사용 방법 |
|---|---|
| Index | 자동으로 부여되는 PG 번호입니다. 수정할 수 없습니다. |
| Host | 해당 PG 장비의 IP 주소 또는 hostname을 입력합니다. |
| Port | 해당 PG 장비의 TCP 포트를 입력합니다. |

Display 행은 직접 추가하지 않습니다. `Display Count`를 늘리면 필요한 행이 자동으로 나타납니다.

## 3. Pattern 설정

| 항목 | 사용 방법 | 주의사항 |
|---|---|---|
| Pattern Name | R, G, B 등 패턴 역할 이름을 입력합니다. | R/G/B 명칭을 임의로 바꾸면 기본 채널 보정 규칙과 운영자의 이해가 달라질 수 있습니다. |
| Voltage Ch | 실제 PG의 전압 채널 번호를 입력합니다. | R/G/B 기본은 67/68/69입니다. 반드시 PG 배선/사양과 대조하십시오. Recipe별 값이 아닙니다. |
| Display Black V | 화면에서 꺼진 상태를 계산하는 기준 전압입니다. | 실제 Recipe 전압을 변경하는 값이 아니라 UI 표시 기준입니다. |
| Display White V | 화면에서 켜진 상태를 계산하는 기준 전압입니다. | Black V보다 작게 유지하십시오. |

## 4. 설정·검증 절차

1. 검사를 중지합니다.
2. 실제 PG 수와 각 장비의 IP/Port를 확인합니다.
3. Display Count를 맞추고 Display 목록의 Host/Port를 입력합니다.
4. PG 배선표를 기준으로 R/G/B Voltage Ch를 확인합니다.
5. 기존 Black/White V 기준은 확정된 극성·표시 기준이 아니면 변경하지 않습니다.
6. Save를 누르고 변경 목록을 검토합니다.
7. 저속 단일 셀에서 실제 R/G/B 패턴, 전압, 촬영 시점을 확인합니다.

## 5. Simulation Mode 주의사항

최신 운영 기준에서 PG simulator 사용 여부는 **전역 Simulation Mode**가 결정됩니다. Simulation Mode가 꺼져 있으면 실 PG에 연결해야 하며, 실 PG가 연결되지 않으면 검사도 실패해야 합니다.

화면에 Test Runner 기준 simulator 안내가 보일 수 있으나, 이는 최신 공식 기준과 다릅니다. 전역 Simulation Mode 기준으로 판단하십시오.

## 문제 발생 시 점검

| 현상 | 확인 항목 |
|---|---|
| 특정 셀/라인만 점등 실패 | 해당 PG Index의 Host/Port, Recipe PG 매핑 |
| R/G/B 색이 맞지 않음 | Voltage Ch, Pattern Name, PG 배선 |
| 이미지가 어둡거나 점등 직후 흔들림 | Pattern On Delay, PG 응답 상태 |
| PG 연결 timeout | Host/Port, 네트워크, PG 전원, Connect Timeout |
| 화면의 색 표시만 실제와 다름 | Display Black V, Display White V |
