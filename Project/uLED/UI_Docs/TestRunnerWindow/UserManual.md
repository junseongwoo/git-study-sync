# Test Runner 사용자 매뉴얼

작성일: 2026-08-03  
대상 화면: `Main > Test > Test Runner...`

## 1. 화면 목적

Test Runner는 Main 검사 기능을 작업 목적별로 실행하는 화면이다. 한 화면에서 다음 시험을 선택할 수 있다.

- 촬영·이미지 입력과 IP 검사
- 촬영·이미지 입력만 수행
- CA410 측정만 수행
- Aging 실행
- Motion/Contact/Align 등 Control flow만 실행
- 저장된 검사 결과 Replay

이 화면에서 선택한 옵션은 실제 Main Glass 검사 흐름을 사용하므로, 실행 전에 현재 Recipe, 사용 셀, 장비 연결, Simulation 상태를 반드시 확인해야 한다.

## 2. 화면 열기

1. MainWindow 상단에서 `Test` 메뉴를 연다.
2. `Test Runner...`를 선택한다.
3. 이미 Test Runner가 열려 있으면 새 창을 만들지 않고 기존 창을 표시한다.

Run을 누르면 Test Runner 창이 숨겨질 수 있다. 검사 중 상태를 다시 확인하려면 `Test > Test Runner...`를 다시 선택한다.

## 3. 실행 전 공통 확인

1. Main 화면의 현재 Recipe가 시험 대상과 맞는지 확인한다.
2. Recipe 셀 맵에서 `Use` 셀이 하나 이상 있는지 확인한다.
3. 실제 장비 시험이면 Control, IP, PG, Camera, CA410 연결 상태를 확인한다.
4. 모의 시험이면 Main의 `Tool > Simulation`에서 필요한 모드만 켠다.
5. Test Runner 하단의 `SIM:` 배지로 실제 활성화된 Simulation 조합을 확인한다.
6. LotId, GlassId, 입력 폴더 및 flow 옵션을 확인한다.

주의: Simulation 설정은 Test Runner 설정 파일에 저장되지 않는다. 프로그램을 다시 실행한 뒤에는 Main 메뉴에서 다시 확인해야 한다.

## 4. 작업 선택

### 4.1 Capture + Inspect

Camera, Folder 또는 Current Buffer에서 Pattern × Point 입력을 만들고 IP 검사를 수행한다.

사용 순서:

1. Source를 선택한다.
2. LotId/GlassId를 입력한다.
3. Folder를 선택했다면 Glass Folder를 지정한다.
4. Align, Contact, CA410, 원본 저장, Export 등 필요한 옵션을 선택한다.
5. 간격과 반복 횟수를 입력한다.
6. 하단 요약에서 포함된 옵션을 확인한 뒤 `Run`을 누른다.

### 4.2 Capture Only

입력 이미지를 촬영하거나 로드하지만 검사 알고리즘 결과는 만들지 않는 작업이다. Camera/Folder/Current Buffer source와 원본 저장 옵션을 시험할 때 사용한다.

### 4.3 CA410 Only

IP 검사를 건너뛰고 셀 순회와 CA410 측정을 수행한다. `Use CA410` 체크박스는 표시되지 않지만 내부적으로 항상 사용된다.

장비 없이 시험하려면 Main의 별도 `CA410 Simulation`을 켜야 한다. Control 동작도 모의하려면 `Control Simulation`, PG도 모의하려면 `PG Simulation`을 각각 켠다.

### 4.4 Aging

현재 Recipe의 AgingPlan을 기준으로 Aging flow를 실행한다. Recipe의 Aging 시간·패턴과 PG 매핑을 먼저 확인한다.

### 4.5 Control Only

IP 검사를 건너뛰고 Loading, Align, Contact/Release, 셀 이동, Unloading 같은 제어 흐름을 확인한다. 실제 Motion이 불필요한 시험이면 Control Simulation을 켠다.

### 4.6 Replay

이미 저장된 검사 결과를 불러와 화면 결과를 재구성한다. Motion, Loading, Contact, Align, CA410를 실행하지 않는다.

Replay 폴더는 반드시 존재해야 하며 현재 Recipe의 사용 셀과 저장 결과 폴더 구조가 맞아야 한다. Repeat는 1회로 고정된다.

## 5. 각 컨트롤 사용법

### 5.1 Source

| 선택 | 언제 사용 | 준비 사항 |
|---|---|---|
| Camera | 실제 카메라 촬영 시험 | Camera/Control/IP/PG 연결과 Recipe Point 확인 |
| Folder | 준비된 셀 이미지를 IP에 입력 | IP가 접근할 수 있는 Glass Folder 경로 |
| Current Buffer | IP에 이미 적재된 buffer 재사용 | buffer 0의 데이터와 현재 Recipe 일치 확인 |

Folder source에서 Browse로 선택한 경로가 Console에는 보여도 IP PC에서 접근할 수 없을 수 있다. 네트워크 공유 경로와 권한을 함께 확인한다.

### 5.2 LotId / GlassId

- `LotId`: lot 식별값이다.
- `GlassId`: 현재 한 장의 Glass Job과 결과 폴더를 식별하는 핵심 값이다.
- `자동 인식`: Loading 직후 teach 위치에서 Glass ID를 촬영·인식한다. 실패하면 입력한 GlassId를 유지한다.

자동 인식은 Capture + Inspect와 Capture Only에서만 실제 실행 옵션으로 사용한다. 다른 작업에서는 체크하지 않는 것이 좋다.

### 5.3 Replay / Glass Folder

- `Replay`: Replay 작업이 읽을 저장 결과 루트다.
- `Glass Folder`: Folder source가 읽을 입력 이미지 루트다.
- `Browse...`: Windows 폴더 선택 창을 연다.

입력 폴더와 결과 폴더는 용도가 다르므로 서로 바꾸어 지정하지 않는다.

### 5.4 Flow / 장비

#### Use Align

Loading 후 Recipe AlignPlan에 따라 좌표를 보정한다. Align 장치가 없으면 Control Simulation만으로 성공 처리되지 않으므로 옵션을 끄거나 실제 장치를 준비한다.

#### Contact / Release

행 검사 전에 Contact하고 행 작업 후 Release한다. Probe/contact가 필요 없는 시험은 끈다.

#### Contact 확인(CAM3)

Contact 성공 직후 Recipe point를 CAM3로 촬영하여 세션의 `contactimages` 폴더에 저장한다. 반드시 `Contact / Release`도 함께 켜야 한다.

#### Aging before Inspect

Capture + Inspect에서 각 행 Contact 직후, 셀 검사 전에 해당 행 전체 PG에 Recipe AgingPlan을 동시 실행한다.

```text
Contact -> 행 Aging -> 셀 검사/측정 -> Release
```

왼쪽 작업 목록의 `Aging`은 Aging만 실행하는 별도 작업이고, 이 체크박스는 Capture + Inspect 안에 Aging을 삽입하는 옵션이다.

#### Unloading Flow

전체 셀 처리가 끝난 뒤 글래스를 Unload한다. 장비에서 글래스를 그대로 유지해야 하는 시험이면 끈다.

### 5.5 측정 / 결과

#### Use CA410

Capture 계열 검사에 CA410 측정을 추가한다. 실제 CA410 연결 또는 Main의 CA410 Simulation이 필요하다.

#### Save Original Images

원본 이미지 저장을 요청한다. 장비 Config의 원본 이미지 출력 루트가 비어 있으면 실행이 실패할 수 있으므로 먼저 설정을 확인한다.

#### Export after Inspect

Capture + Inspect가 완료한 셀 결과를 공식 Export 형식으로 저장한다. Export 작업이 비동기로 마무리될 수 있으므로 하단 상태가 `진행 중` 또는 `마무리 중`이면 프로그램을 종료하거나 ZIP 생성을 시작하지 않는다.

### 5.6 실행 값

| 입력 | 사용법 | 주의 |
|---|---|---|
| Cell Interval (s) | 다음 셀 시작 전 대기 초 | 0 이상 입력 |
| Line Delay (s) | 다음 행 시작 전 추가 대기 초 | 0 이상 입력 |
| Repeat | 전체 작업 반복 횟수 | 1 이상 입력, Replay는 1회 |

잘못된 문자나 범위 밖 숫자를 입력하면 오류가 바로 표시되지 않고 이전 유효값이 유지될 수 있다. Run 전에 하단 실행 요약과 표시값을 다시 확인한다.

## 6. Run과 Stop

### Run

1. 입력값을 확인한다.
2. 하단 요약에서 포함된 옵션을 확인한다.
3. Simulation과 표준맵 모드 배지를 확인한다.
4. `Run`을 누른다.
5. checkpoint가 발견되면 다음 중 하나를 선택한다.
   - 재개: 저장된 checkpoint 옵션으로 이어서 실행
   - 새 실행: checkpoint를 삭제하고 현재 설정으로 시작
   - 취소: 실행하지 않음

Run 후 창이 숨겨지는 것은 정상 동작이다. Main에서 같은 메뉴를 선택하면 다시 볼 수 있다.

주의: 현재 하단 요약은 Contact를 Align보다 먼저 표시할 수 있지만 실제 flow는 `Loading -> Glass ID 인식 -> Align -> 행 Contact` 순서다. 정확한 장비 순서는 실제 상태와 Main 로그를 기준으로 확인한다.

### Stop

`Stop`은 현재 실행의 cancellation, Control Stop, IP buffer/queue 정리를 요청한다. Stop을 눌렀다고 모든 장치가 같은 순간에 물리 정지했다는 의미는 아니다.

중지 후에는 다음을 확인한다.

- Main 화면의 실행 상태
- Control/IP 연결 상태
- 활성 Alarm
- Main Log의 Stop 및 ClearBuffer 결과
- Contact 상태와 장비 안전 상태

## 7. 하단 상태 읽기

| 표시 | 의미 |
|---|---|
| `SIM: ...` | 현재 켜진 Control/PG/CA410 Simulation 조합 |
| 표준맵 배지 | 현재 Recipe의 표준맵 사용 및 정합 모드 |
| 실행 요약 | 이번 실행에 포함된 Loading·Align·Contact·작업·Unloading 옵션 요약 |
| Running `(n/N)` | 현재 repeat 진행 |
| Idle — 결과 경로 | 대기 상태와 표준 결과 루트 |

표준맵 배지에 미검증·경고 성격의 문구가 있으면 Recipe의 표준맵 설정과 마지막 정합 결과를 확인한 뒤 실행한다.

## 8. Export 결과 사용법

### Export 폴더 열기

1. Export 상태가 완료됐는지 확인한다.
2. 경로가 실제로 존재하면 버튼이 활성화된다.
3. `Export 폴더 열기`를 눌러 탐색기에서 결과를 확인한다.

경로는 최근 실행이 자동으로 채울 수 있다. 직접 다른 결과 폴더를 입력하면 그 폴더를 열거나 ZIP만 별도로 생성할 수 있다.

### 압축 생성

1. Export 상태가 진행/마무리 중이 아닌지 확인한다.
2. 필요한 경우 `Zip Prefix`를 입력한다.
3. 비워 두면 `[ELP]검사결과_{glass 폴더명}`이 사용된다.
4. `압축 생성`을 누른다.
5. 완료 또는 실패 메시지를 확인한다.

### Offset

`Offset`은 마지막 표준맵 검사의 실측 X/Y translation을 표시하는 읽기 전용 창을 연다.

- 단위는 pixel이다.
- 절대값이 3 px를 넘는 행은 강조된다.
- 이 창은 Recipe를 자동 수정하지 않는다.
- 물리 좌표 보정은 설치 환경의 px→µm 값을 확인한 뒤 Recipe CellMap 값을 수동으로 수정한다.

화면 ToolTip에 “업데이트”라는 표현이 있지만 현재 구현은 조회 전용이다.

## 9. 권장 실행 예시

### Folder 이미지로 IP 검사

```text
Task: Capture + Inspect
Source: Folder
Glass Folder: IP가 접근 가능한 입력 경로
Use Align: 필요할 때만
Contact / CA410: 시험 범위에 따라 선택
Export after Inspect: 결과 납품 구조가 필요하면 선택
Run
```

### 장비 없이 Control 순서 확인

```text
Main > Tool > Simulation > Control Simulation ON
Task: Control Only
필요한 Contact / Unloading 옵션 선택
하단 SIM: CONTROL 확인
Run
```

Align은 Control Simulation이 성공을 모사하지 않으므로 실제 Align 장치가 없다면 끈다.

### CA410 연결 없이 측정 flow 확인

```text
Main > Tool > Simulation > CA410 Simulation ON
필요하면 Control/PG Simulation도 각각 ON
Task: CA410 Only
하단 Simulation 조합 확인
Run
```

## 10. 문제 발생 시 확인

| 증상 | 확인 항목 |
|---|---|
| Run이 시작되지 않음 | 사용 셀, 입력 폴더, 기존 실행 상태, checkpoint 선택 |
| Folder 입력 실패 | IP에서 보이는 경로, 공유 권한, 셀/패턴 파일 구조 |
| Align 실패 | 실제 Align 장치 연결, AlignPlan, Simulation 범위 |
| CA410 실패 | CA410 연결 또는 CA410 Simulation, Recipe 측정 설정 |
| 원본 저장 실패 | Original Image Output Root 설정 |
| Export 버튼 비활성 | 폴더 존재 여부, Export 진행/마무리 상태 |
| 설정이 다음 실행에 사라짐 | `Config/TestRunner.yaml` 쓰기 권한과 파일 상태 |
| Stop 후 상태가 남음 | Control/IP 로그, Alarm, Contact/Release 상태 |

운영 로그는 기본적으로 다음 위치를 확인한다.

```text
Console: c:\elp\uLedAoi\logs\yyyyMM\
IP:      c:\elp\uLed\uLedIp\logs\yyyyMM\
```
