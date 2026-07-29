# ConfigWindow - Connections 탭 사용자 매뉴얼

## 화면 용도

Connections 탭에서 검사 서버(uLedIp), CA-410 색도계, Light On/Off 조명 제어기의 통신 정보를 설정합니다. 이 화면은 장비 설치·교체·네트워크 변경 시 사용하는 관리자 설정 화면입니다.

검사가 진행 중일 때는 연결 값을 변경하지 마십시오.

## 1. IP Endpoints 설정

Recipe 창이 검사 처리를 맡길 uLedIp 서버 목록입니다.

| 항목 | 입력 방법 | 주의사항 |
|---|---|---|
| No | IP 서버의 순번을 입력 | 중복하지 않도록 1부터 관리합니다. |
| Name | 역할을 알 수 있는 이름 입력 | 예: `IP-Y1`, `IP-Y2`. 주소와 혼동하지 않도록 합니다. |
| IP Address | uLedIp가 실행 중인 PC의 주소 입력 | 같은 PC가 아니면 `127.0.0.1`을 사용하면 안 됩니다. |
| Port | uLedIp 수신 포트 입력 | 기본 IP-1=5003, IP-2=5004입니다. 네트워크 담당자 또는 IP 실행 설정과 일치해야 합니다. |
| Enabled | 사용할 endpoint만 체크 | 점검 중인 IP는 해제할 수 있으나, 검사 할당에 필요한 IP를 해제하지 않았는지 확인합니다. |

행을 추가할 수 있지만, 실제 검사에서 몇 개의 IP를 어떤 헤드/셀에 배정하는지는 레시피와 실행 구성에 따라 달라질 수 있습니다. 장비 설계가 확인되지 않은 endpoint를 임의로 추가하지 마십시오.

## 2. CA-410 RS232C 설정

### 공통 옵션

| 항목 | 사용 방법 |
|---|---|
| Include XYZ | CA-410 결과에 XYZ 값을 함께 사용할 때 체크합니다. 측정 결과 형식 요구가 확실하지 않으면 기존 설정을 유지합니다. |
| Command ms | 일반 CA-410 명령의 최대 대기 시간입니다. 장치가 느리다고 바로 크게 바꾸지 말고 통신 로그·케이블·장치 상태를 먼저 확인합니다. |
| ZRC timeout ms | CA-410 보정의 최대 대기 시간입니다. 보정 동작이 일반 측정보다 오래 걸릴 수 있습니다. |
| RS232 idle ms | 응답 종료를 판정하기 위한 대기 시간입니다. 너무 짧으면 응답 일부를 놓칠 수 있고, 너무 길면 측정 시간이 늘어납니다. |

### 장치별 설정

| 항목 | 사용 방법 |
|---|---|
| Name | CA-410 장치 식별명입니다. 현장 라벨과 맞춥니다. |
| Align Camera | 해당 CA-410이 설치된 헤드의 Align 카메라 이름을 입력합니다. Heads 탭의 Y1/Y2 Align Camera와 같은 이름을 사용합니다. |
| COM Port | Windows 장치 관리자에서 확인한 COM 포트를 입력합니다. 다른 프로그램이 같은 COM 포트를 열고 있으면 사용할 수 없습니다. |
| Baud / Data Bits | CA-410 통신 사양에 맞춥니다. 화면 기본 안내는 38400 bps, 7 data bits입니다. |
| Enabled | 사용할 CA-410만 체크합니다. |

CA-410 기본 안내 사양은 `38400 bps / 7 data bits / even parity / 2 stop bits / RTS/CTS`입니다. 화면에는 parity·stop bits·flow control 입력칸이 없으므로 현장 장비가 이 기본 규격과 다르면 개발 담당자에게 먼저 확인하십시오.

## 3. LED RS232C 설정

이 영역은 Light Controller 1대의 Light On/Off 통신 설정입니다.

| 항목 | 사용 방법 |
|---|---|
| COM Port | 조명 컨트롤러가 연결된 Windows COM 포트 입력 |
| Baud | 컨트롤러 사양의 통신 속도 입력 |
| Data Bits | 컨트롤러 사양의 데이터 비트 수 입력(5~8) |

이 설정은 PG pattern 장비 설정과 다를 수 있습니다. RGB 패턴 점등 설정은 `Light / Pattern` 탭에서 별도로 관리합니다.

## 4. 저장 및 확인 절차

1. 검사를 중지합니다.
2. 장비 PC의 IP 주소, Windows 장치 관리자의 COM 번호, 장비 통신 사양을 확인합니다.
3. 각 항목을 입력합니다.
4. Config 창의 **Save**를 누르고 표시되는 변경 목록을 확인합니다.
5. 저장 후 IP 연결 상태를 확인합니다.
6. CA-410은 단발 측정으로, Light Controller는 안전한 조건에서 On/Off로 각각 확인합니다.
7. 모든 통신이 정상일 때만 검사 또는 CA410 공정을 실행합니다.

## 장애 시 점검 순서

| 증상 | 먼저 점검할 항목 |
|---|---|
| IP 연결 실패 | IP Address, Port, uLedIp 실행 여부, 방화벽, Enabled |
| CA-410 통신 실패 | COM Port, COM 포트 점유 여부, Baud/Data Bits, 케이블, 장치 전원 |
| CA-410 timeout | 장치 상태와 응답 로그, Command/ZRC timeout, RS232 idle |
| Light On/Off 실패 | Light COM Port, Baud/Data Bits, 컨트롤러 전원/케이블 |

설정을 바꾼 뒤 반복적으로 실패하면 timeout만 계속 늘리지 말고 Console 로그와 장비 연결 상태를 먼저 확인하십시오.
