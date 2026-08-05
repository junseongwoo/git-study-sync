# TestRunnerWindow 개발자 분석

작성일: 2026-08-03  
분석 대상: `Main > Test > Test Runner...`로 여는 `TestRunnerWindow`

## 1. 핵심 결론

`TestRunnerWindow`는 독립된 검사 엔진이 아니라, `MainWindowViewModel`이 가진 **공식 Glass 검사 실행 파이프라인을 작업 목적별 옵션으로 조립해 호출하는 운영·시험용 런처**다.

공식 문서와 현재 코드에서 확인되는 핵심 원칙은 다음과 같다.

- 작업별 표시 항목과 `GlassInspectionRunOptions` 변환은 `TestRunnerPolicy`가 단일 기준이다.
- 작업별 입력값은 `Config/TestRunner.yaml`에 별도로 저장·복원한다.
- Capture + Inspect의 IP 실행은 현재 공식 흐름인 `StartJob -> InputStep 반복 -> EndJob ACK -> EvtJobCompleted`를 따른다.
- 촬영/입력은 동기 step이고 검사는 IP 단일 worker의 비동기 작업이므로, `EndJob ACK` 뒤 다음 셀 준비가 진행될 수 있다.
- Control, PG, CA410 Simulation은 서로 다른 모드다. Control Simulation만 켜서 Align 또는 CA410 성공을 가장하지 않는다.
- 검사 기본 결과 위치는 사용자가 이 창에서 지정하지 않으며 `Data/InspectionResults/Glass`로 고정된다.
- 검사 완료 후 Export 폴더 열기·ZIP 생성은 실행과 분리된 후처리 기능이다.

가장 중요한 구조는 다음과 같다.

```text
Main > Test > Test Runner...
    -> TestRunnerWindow
    -> 작업별 TestRunnerTaskSettings
    -> TestRunnerPolicy.BuildRunOptions(...)
    -> MainWindowViewModel.StartTestRunnerRunAsync(...)
    -> ExecuteGlassInspectionAsync(...)
    -> 공통 Glass 검사 / 제어 / Replay 파이프라인
```

## 2. 분석 기준과 사실 우선순위

### 2.1 우선 적용한 공식 문서

1. `docs/README.md`
2. `docs/프로젝트 구조.md`
3. `docs/전체 flow.md`
4. `docs/main-glass-inspection-flow.md`
5. `docs/automation-api.md`
6. `docs/development/smoke-test-plan.md`
7. `docs/표준맵사용검사-technical-manual.md`
8. `docs/development/change-log.md`

저장소 지침이 먼저 확인하도록 요구한 `dist-lib/docs/README.md`는 현재 checkout에서 `dist-lib`가 비어 있어 열 수 없었다. 따라서 이번 분석은 로컬 `docs`의 공식 문서와 현재 소스의 교차 검증 결과를 사용했다.

### 2.2 2차 검증 방법

1차 검증에서는 XAML의 컨트롤과 Code-behind 이벤트를 연결했다. 2차 검증에서는 다음 연결이 실제로 이어지는지 다시 확인했다.

```text
Main 메뉴 이벤트
  -> Window 생성/재활성화
  -> TestRunnerPolicy의 작업별 옵션 강제
  -> MainWindowViewModel의 실행 진입
  -> 공통 검사 flow
  -> 결과 폴더/Export 상태 반영
```

또한 공식 문서와 코드가 다른 부분은 별도 절에서 분리했다.

## 3. MainWindow에서의 진입

`MainWindow.xaml`의 메뉴는 다음 이벤트에 연결된다.

```xml
<MenuItem Header="Test Runner..."
          Click="OpenTestRunnerMenuItem_Click"/>
```

`OpenTestRunnerMenuItem_Click`의 실제 동작은 다음과 같다.

```text
기존 창이 없거나 닫힘
  -> TestRunnerWindow 생성
  -> Owner = MainWindow
  -> Main의 최근 Glass 실행 옵션을 기본값으로 전달
  -> 비모달 Show()

기존 창이 Loaded 상태
  -> 숨겨져 있으면 Show()
  -> 최소화되어 있으면 Normal 복원
  -> Activate()
```

`[추론] (코드 확인)` Test Runner는 한 MainWindow에서 한 인스턴스만 유지된다. Run을 누르면 창이 숨겨지므로 다시 설정 화면을 보고 싶을 때 같은 메뉴를 선택하면 기존 인스턴스가 다시 표시된다.

## 4. 관련 클래스와 책임

| 구성 요소 | 책임 |
|---|---|
| `TestRunnerWindow.xaml` | 작업 목록, 입력 옵션, 상태, 실행·중지·Export UI |
| `TestRunnerWindow.xaml.cs` | 작업별 설정 로드/저장, 화면 표시 분기, 옵션 생성 호출, 버튼 이벤트 |
| `TestRunnerModels.cs` | 작업 enum, YAML 저장 모델, `TestRunnerPolicy` 정책 테이블 |
| `MainWindowViewModel` | 실제 Glass 검사 실행, 제어·IP·CA410·Aging·Export 오케스트레이션 |
| `GlassInspectionRunOptions` | 한 번의 Glass Job에 전달되는 실행 옵션 |
| `YamlFileStore<TestRunnerSettingsData>` | `Config/TestRunner.yaml` 영속화 |
| `StandardMapOffsetWindow` | 마지막 표준맵 정렬 실측 offset을 읽기 전용으로 표시 |
| `ExportZipService` | 선택한 Export 폴더를 배포용 ZIP으로 생성 |

이 창 자체에는 별도 ViewModel이 없다. `DataContext` 바인딩보다 Code-behind에서 컨트롤을 읽어 `TestRunnerTaskSettings`에 반영하고, 실제 실행은 생성자로 받은 `MainWindowViewModel`에 위임한다.

## 5. 화면 구조

Window 기본 크기는 `920 × 850`, 최소 크기는 `820 × 600`이며 MainWindow 중앙에 열린다.

```text
┌───────────────┬────────────────────────────────────────────┐
│ Task 목록     │ 선택 작업 설명                              │
│               ├────────────────────────────────────────────┤
│ Capture +     │ Source                                     │
│ Inspect       │ Glass                                      │
│ Capture Only  │ Folders                                    │
│ CA410 Only    │ Flow / 장비                                │
│ Aging         │ 측정 / 결과                                │
│ Control Only  │ 실행                                       │
│ Replay        │ Export 결과                                │
├───────────────┴────────────────────────────────────────────┤
│ Simulation/표준맵 배지 · 실행 요약 · 상태       Run / Stop │
└────────────────────────────────────────────────────────────┘
```

오른쪽은 `ScrollViewer`이므로 창 높이가 작아도 모든 설정을 스크롤해 접근할 수 있다. 선택한 작업에 맞지 않는 섹션은 `TestRunnerPolicy`에 따라 숨겨진다.

## 6. 작업 정책 분석

### 6.1 작업별 핵심 옵션

| 작업 | 실행 Source | 검사 | IP 사용 | 특징 |
|---|---|---:|---:|---|
| Capture + Inspect | Camera / Folder / Current Buffer 중 선택 | O | O | 촬영·입력 후 IP 검사, 선택 시 CA410·원본 저장·Export 수행 |
| Capture Only | Camera / Folder / Current Buffer 중 선택 | X | O 경로 | 촬영 또는 입력 수집 중심, IP 검사 결과 생성은 하지 않음 |
| CA410 Only | `ControlOnly`로 강제 | X | 건너뜀 | CA410 측정을 강제로 사용 |
| Aging | `Aging`으로 강제 | X | 실행 경로에서 사용하지 않음 | 레시피 AgingPlan 중심 실행 |
| Control Only | `ControlOnly`로 강제 | X | 건너뜀 | Loading/Align/Contact/이동/Unloading 같은 제어 flow 확인 |
| Replay | `Replay`로 강제 | O | 저장 결과 해석 경로 | Motion을 사용하지 않고 반복 횟수는 1로 강제 |

`Capture Only`의 `SkipIpConnectionForControlOnly` 값은 false지만 `WithInspect=false`다. 즉 입력 경로는 IP buffer 계층을 사용할 수 있으나 검사 알고리즘 실행을 요청하지 않는 구성이다.

`CA410 Only`는 이름과 달리 Control flow가 완전히 제거된 작업이 아니다. 정책상 `Source=ControlOnly`, `UseMotion=true`, `UseCa410=true`, `SkipIpConnectionForControlOnly=true`이므로 선택된 Contact/Align/Unloading 옵션과 셀 순회 속에서 CA410 측정을 수행한다.

### 6.2 작업별 화면 표시

| UI 영역 | 표시되는 작업 |
|---|---|
| Source | Capture + Inspect, Capture Only |
| Replay 폴더 | Replay |
| Glass Folder | Capture 계열에서 Source=Folder일 때 |
| Flow / 장비 | Replay를 제외한 모든 작업 |
| Use CA410 | Capture + Inspect, Capture Only |
| Save Original Images | Capture + Inspect, Capture Only |
| Export after Inspect | Capture + Inspect만 |
| Aging before Inspect | Capture + Inspect만 |
| 실행 간격·반복 | Replay를 제외한 모든 작업 |

CA410 Only에서는 `Use CA410` 체크박스가 보이지 않지만 정책에서 true로 강제한다. Replay는 반복 입력이 보이지 않고 실제 옵션도 1회로 고정된다.

## 7. 컨트롤과 값의 영향

### 7.1 Source

| 값 | 의미 | 실행 영향 |
|---|---|---|
| Camera | 실제 카메라 입력 | 각 Pattern × Point에서 Camera source의 `InputStep` 수행 |
| Folder | 글래스 폴더 입력 | IP가 접근할 수 있는 셀별 폴더의 이미지를 step 단위로 로드 |
| Current Buffer | 현재 IP buffer | 새 폴더 로드 없이 IP의 buffer 0 데이터를 입력으로 사용 |

공식 최신 흐름에서는 Camera도 별도 `Grab` 계약이 아니라 `InputStep(Source=Camera)`로 정리되어 있다. 과거 문서나 주석에 남은 `Grab` 표현은 현재 기준으로 사용하지 않는다.

### 7.2 Glass

| 컨트롤 | 저장값 | 영향 |
|---|---|---|
| LotId | `LotId` | Glass Job의 lot 식별 메타데이터 |
| GlassId | `GlassId` | 실행·결과·Export의 glass 식별자 |
| 자동 인식 | `UseGlassIdReading` | Loading 직후 teach 위치에서 Glass ID 촬영·인식, 성공 시 입력 GlassId 대체 |

자동 인식 실패 시 사용자가 입력한 GlassId를 유지한다. 정책상 이 기능은 Capture 계열에서만 실행 옵션으로 반영된다.

### 7.3 Folders

| 컨트롤 | 사용 시점 | 의미 |
|---|---|---|
| Replay | Replay | 저장된 검사 결과를 읽을 루트 폴더 |
| Glass Folder | Capture 계열 + Folder | 셀별 이미지가 있는 입력 글래스 폴더 |
| Browse... | 각 경로 | Windows 폴더 선택 창으로 경로 입력 |

Folder source는 Control PC와 Console에서 보이는 경로가 아니라 **IP 프로세스가 접근 가능한 경로 구조**여야 한다. Replay 폴더는 저장 결과의 셀 폴더와 결과 파일 구조가 맞아야 한다.

### 7.4 Flow / 장비

| 컨트롤 | 조건/순서 | 프로그램 전체 영향 |
|---|---|---|
| Use Align | Loading 후 | 레시피 AlignPlan으로 좌표 보정 후 셀 이동 기준에 반영 |
| Contact / Release | 행 검사 전/후 | 행 단위 contact를 수행하고 검사 후 release |
| Contact 확인(CAM3) | Contact 성공 직후 | Recipe point를 CAM3로 촬영해 세션의 `contactimages`에 저장 |
| Aging before Inspect | Capture + Inspect, Contact 후 | 각 행의 전체 PG에 AgingPlan을 동시 실행한 뒤 검사 시작 |
| Unloading Flow | 전체 처리 후 | 글래스 unload 제어 flow 실행 |

`Contact 확인(CAM3)`은 Contact / Release가 켜져 있어야 실제 옵션이 true가 된다. `Aging before Inspect`는 독립 Aging 작업과 다르며 Capture + Inspect의 각 행 검사 직전에 삽입되는 전처리다.

### 7.5 측정 / 결과

| 컨트롤 | 적용 작업 | 영향/선행 조건 |
|---|---|---|
| Use CA410 | Capture 계열 | 셀 검사 flow에 CA410 측정을 추가. 실제 장비 또는 별도 CA410 Simulation 필요 |
| Save Original Images | Capture 계열 | IP 원본 이미지 저장 요청. 원본 출력 루트 설정이 비어 있으면 실행 실패 가능 |
| Export after Inspect | Capture + Inspect | 완료 셀 결과를 공식 Export 구조로 비동기 저장 |

Export의 thumbnail·overlay·crop 원본은 IP가 만든 완성된 `FinalPanelResultModel`이다. Console이 임의로 thumbnail을 다시 만들지 않는다.

### 7.6 실행 값

| 값 | 허용/보정 | 실제 의미 |
|---|---|---|
| Cell Interval (s) | 0 이상, 음수는 0으로 보정 | 다음 셀 작업 시작 전 대기. 앞 batch의 `EndJob ACK` 이후 적용 |
| Line Delay (s) | 0 이상, 음수는 0으로 보정 | 행 경계에서 다음 행 시작 전 추가 대기 |
| Repeat | 1 이상, Replay는 1 강제 | 동일 설정의 Glass Job 반복 횟수 |

화면 입력은 현재 문화권 형식의 `double.TryParse`와 `int.TryParse`를 사용한다. 잘못된 문자열이나 범위 밖 값을 입력하면 오류 표시 없이 마지막 유효값이 유지된다.

## 8. 설정 저장과 복원

공식 기준에 따라 작업별 설정은 다음 파일에 저장된다.

```text
{Vars.WorkDir}\Config\TestRunner.yaml
```

저장 모델은 다음 구조다.

```text
TestRunnerSettingsData
  LastTask
  TaskSettings
    CaptureInspect -> TestRunnerTaskSettings
    CaptureOnly    -> TestRunnerTaskSettings
    Ca410Only      -> TestRunnerTaskSettings
    Aging          -> TestRunnerTaskSettings
    ControlOnly    -> TestRunnerTaskSettings
    Replay         -> TestRunnerTaskSettings
```

작업을 바꾸면 이전 작업의 현재 UI 값을 메모리 설정에 반영한 뒤 새 작업 값을 불러온다. Run과 창 닫기 시 YAML을 저장한다.

Simulation 상태는 안전을 위해 Test Runner 작업 설정에 저장하지 않는다. 프로그램 재시작 후 실제 장비 모드인지 Main의 `Tool > Simulation` 메뉴에서 다시 확인해야 한다.

## 9. Run 이벤트의 코드 진행

```text
Run 클릭
  1. 현재 UI -> 현재 작업 설정 반영
  2. Replay이면 입력 폴더 존재 여부 검증
  3. Capture + Folder이면 Glass Folder가 비어 있는지 검증
  4. TestRunner.yaml 저장
  5. TestRunnerPolicy.BuildRunOptions(...)
  6. 기본 결과 루트 생성
  7. TestRunnerWindow.Hide()
  8. MainWindowViewModel.StartTestRunnerRunAsync(options)
  9. 시작 거절/취소이면 창 재표시
```

기본 결과 루트는 다음과 같다.

```text
{Vars.WorkDir}\Data\InspectionResults\Glass
```

`StartTestRunnerRunAsync`는 기존 checkpoint가 있으면 재개/새 실행/취소를 묻는다. 재개를 선택하면 현재 화면 옵션이 아니라 checkpoint에 저장된 옵션으로 이어서 실행한다.

`[추론] (코드 확인)` 정상적으로 실행이 시작된 뒤 메서드가 끝나도 창을 자동으로 다시 표시하지 않는다. 사용자는 Main의 `Test > Test Runner...`를 눌러 숨겨진 기존 창을 다시 열 수 있다.

## 10. 공통 검사 흐름과 연결

### 10.1 비 Replay 실행

공식 문서 기준의 상위 흐름은 다음과 같다.

```text
사전 조건 확인
  -> 사용 셀/행/IP 배정 구성
  -> Control Release / Loading
  -> Glass 존재 확인
  -> 선택 시 Glass ID 인식
  -> 선택 시 Align
  -> 행 반복
       -> 선택 시 Contact
       -> 선택 시 Contact 확인(CAM3)
       -> 선택 시 Aging before Inspect
       -> 셀/step 실행
       -> 행 Release
       -> Line Delay
  -> 선택 시 Unloading
  -> 결과 저장/Export 완료 처리
```

Loading은 Replay를 제외한 작업에서 기본 flow다. `UseMotion`도 Replay를 제외하면 true로 구성되며, UI에서 별도 Motion 체크박스를 제공하지 않는다. Motion 없이 확인하려면 Control Simulation을 명시적으로 켜는 현재 정책을 따른다.

### 10.2 Capture + Inspect의 셀 실행

```text
Cell Job 시작
  -> StartJob: 셀 준비와 buffer 적재 준비
  -> Pattern × Point 반복
       검사 카메라 이동
       -> PG REQ_PTN_SEL
       -> PatternOnDelay
       -> InputStep(Source=Camera/Folder/CurrentBuffer)
  -> 마지막에 REQ_PTN_OFF
  -> EndJob: 새 step 입력 종료 선언, queueing 후 ACK
  -> Console은 다음 셀 준비 가능

별도 IP inspection worker
  -> 셀 순차 검사
  -> EvtJobCompleted(final_result)
  -> 결과 수신 task가 저장/UI/Export 처리
```

`StartJob`은 pattern 실행 명령이 아니며, `EndJob`은 결과 조회 명령이 아니다. 최종 판정은 반드시 `EvtJobCompleted(final_result)`를 기준으로 한다.

### 10.3 Replay

Replay는 Motion·Loading·Contact·Align·CA410를 사용하지 않고 저장 결과 폴더를 해석해 검사 결과 표시 모델을 복원한다. 현재 셀 맵에 사용 셀이 하나 이상 있어야 실행 가능하며, 저장 폴더의 셀 식별과 파일 구조가 현재 레시피와 맞아야 한다.

## 11. Stop 동작

Stop 버튼은 MainWindowViewModel의 `StopGlassReplayCommand`를 실행한다. 현재 공식 흐름과 코드에서 Stop은 다음을 요청한다.

- 실행 Cancellation 요청
- Control Stop 전송
- IP buffer/queue 정리 요청
- 이미 최종 완료된 셀만 확정 결과로 유지

Stop은 UI 스레드에서 모든 장비가 즉시 정지했다는 뜻이 아니라, 실행 파이프라인에 빠른 중단과 정리 명령을 전달한 상태다. 장비·통신 상태는 Main 로그와 alarm을 함께 확인해야 한다.

## 12. Simulation 모드 영향

하단 배지는 Main 설정 중 하나라도 켜지면 조합을 표시한다.

```text
SIM: CONTROL
SIM: PG
SIM: CA410
SIM: CONTROL+PG+CA410
```

| 모드 | 대체 범위 | 대체하지 않는 것 |
|---|---|---|
| Control Simulation | ControlRuntime을 내장 Control Simulator로 연결, 기본 포트 5002 | 실제 Align 장치와 CA410 |
| PG Simulation | PG 통신/패턴 제어 | Control, CA410 |
| CA410 Simulation | CA410 측정기 동작 | Control, PG, Align |

Simulation 전환은 Main의 `Tool > Simulation`에서 수행하며 검사 중에는 전환하지 않는 것이 기준이다. Align은 별도 성공 모사가 없으므로 실제 의존 장치가 없으면 꺼야 한다.

## 13. Export 결과 영역

### 13.1 상태와 폴더

검사 pipeline이 마지막 Export 폴더와 상태를 MainWindowViewModel에 반영하면 이 창이 `PropertyChanged`를 받아 화면을 갱신한다.

- 사용자가 경로를 직접 편집하지 않았다면 최근 실행 폴더로 자동 갱신한다.
- 사용자가 키보드로 경로를 수정한 뒤에는 실행 상태가 해당 값을 덮어쓰지 않는다.
- 실제로 존재하는 폴더일 때만 `Export 폴더 열기`와 `압축 생성`이 활성화된다.
- Export가 진행 중이거나 마무리 중이면 같은 폴더의 ZIP 생성을 막는다.

### 13.2 ZIP Prefix

비어 있으면 다음 형식을 기본으로 사용한다.

```text
[ELP]검사결과_{glass 폴더명}
```

`압축 생성`은 UI가 멈추지 않도록 백그라운드에서 `ExportZipService`를 호출하며, 성공·실패 결과를 상태와 메시지로 표시한다.

### 13.3 Offset 보조 창

Offset 버튼은 마지막 검사 결과에서 표준맵 정렬 비교 row를 만들고, 데이터가 있으면 `StandardMapOffsetWindow`를 모달로 연다.

이 창의 값은 읽기 전용이다.

| 열 | 의미 |
|---|---|
| Cell | 결과에 저장된 panel/cell 식별자 |
| Mode | 표준맵 정렬 모드 |
| Measured X/Y (px) | 마지막 검사에서 측정한 translation |
| Pairs | 정합에 사용된 pair 수 |
| Residual P50 | residual 중앙값 계열 지표 |

X 또는 Y offset 절대값이 `3.0 px`를 넘으면 강조 표시한다. 물리 보정값은 자동으로 레시피에 쓰지 않으며, 설치 환경의 px→µm 관계를 확인해 Recipe의 CellMap `StageX/UnitY` 등을 수동 보정해야 한다.

## 14. 이벤트와 상태 갱신

| 이벤트 | 처리 |
|---|---|
| Task 선택 변경 | 기존 작업 값 commit -> 새 작업 값 load -> 섹션/요약 갱신 |
| 설정 TextChanged/Checked | 설정 commit -> 표시 조건/실행 요약 갱신 |
| Window Activated | 표준맵 모드 배지 재계산 |
| ViewModel PropertyChanged | 실행 상태 또는 Export 상태 갱신 |
| Run | 검증·저장·옵션 생성 후 공통 실행 호출 |
| Stop | 공통 Stop command 호출 |
| Closing | 현재 작업 저장, ViewModel 이벤트 구독 해제 |

Run 상태에서는 Run이 비활성화되고 Stop이 활성화된다. 상태 문구는 실행 중 repeat 진행 또는 Idle과 기본 결과 경로를 표시한다.

## 15. Docs-코드 차이 및 주의점

### 15.1 Offset ToolTip과 실제 동작 불일치

공식 표준맵 문서는 Offset 창을 **읽기 전용 참고 창**으로 정의하고 자동 recipe write-back을 하지 않는다고 명시한다. 코드도 읽기 전용 DataGrid와 Close 버튼만 제공한다.

그러나 XAML ToolTip은 “recipe 기존값을 비교해서 업데이트합니다”라고 표시한다. 실제 업데이트 기능은 없으므로 ToolTip 문구가 문서·코드와 다르다.

### 15.2 Window 생명주기 지침 미적용

공식 저장소 지침은 모든 WPF Window에 `WindowProcessStateMachine`의 Initializing/Ready/Closing/Closed 전이를 요구한다. 현재 `TestRunnerWindow`는 일반 `Closing` 이벤트만 사용하고 해당 상태 전이를 구현하지 않았다.

### 15.3 창 전용 로깅 미적용

공식 로깅 지침은 Window별 Caller와 `RatelLog`/`LogViewer`를 요구한다. 현재 TestRunnerWindow 자체에는 Caller 지정, 전용 logger, LogViewer가 없고 실행 로그는 주로 MainWindowViewModel에 의존한다.

### 15.4 폴더 선검증 차이

Replay는 Run 전에 `Directory.Exists`까지 확인한다. 반면 Capture + Folder의 Glass Folder는 빈 문자열만 검사하고 실제 존재 여부는 이 단계에서 확인하지 않는다.

`[추론]` IP가 접근하는 UNC/원격 경로를 Console의 로컬 `Directory.Exists`로 오판하지 않기 위한 가능성은 있으나, 코드에 그 의도가 명시되어 있지 않다.

### 15.5 Glass 자동 인식 표시 범위

Glass 영역은 모든 작업에 보이며 실행 요약도 설정값이 켜져 있으면 Glass ID 인식을 표시할 수 있다. 하지만 `BuildRunOptions`는 Capture 계열에서만 `UseGlassIdReading=true`를 전달한다. Aging/Control Only/CA410 Only 화면에서 체크해도 실제 실행에는 반영되지 않는다.

### 15.6 설정 저장 실패가 표시되지 않음

`SaveStore()`는 예외를 사용자에게 알리거나 로그로 남기지 않고 무시한다. 따라서 Run은 진행됐지만 다음 실행에서 설정이 복원되지 않는 상황을 화면만으로 구분하기 어렵다.

### 15.7 새 작업 기본값 일부 누락

`[추론] (코드 확인)` Main의 최근 실행 옵션으로 새 작업 설정을 만들 때 `UseContactCheck`는 복사하지 않는다. 다른 공통 옵션과 달리 CAM3 Contact 확인은 새 작업의 기본값이 false가 된다.

### 15.8 하단 실행 요약과 실제 Align 순서 불일치

`BuildSummary`는 `Loading -> Glass ID -> Contact -> Contact 확인 -> Align` 순으로 문자열을 만든다. 그러나 실제 Main 검사 flow는 Loading과 Glass ID 인식 후 **Align을 먼저 완료**하고, 각 행을 시작할 때 Contact와 Contact 확인을 수행한다.

따라서 하단 summary는 현재 옵션 포함 여부를 확인하는 용도로는 사용할 수 있지만 Align과 Contact의 정확한 실행 순서를 나타내지는 못한다. 공식 flow와 실제 실행 코드의 순서가 기준이다.

### 15.9 작업 설명의 Simulation 표현

CA410 Only 설명의 “Simulation Mode”는 어떤 Simulation인지 구분하지 않는다. 현재 구현에서는 별도 `CA410 Simulation`이 CA410를 대체하며 Control Simulation은 CA410 성공을 모사하지 않는다.

Control Only 설명도 Motion/PG를 “선택”한다고 표현하지만 현재 UI에는 Use Motion 또는 Use PG 체크박스가 없다. Motion은 non-Replay 작업에서 정책상 항상 true이며, 실제 장비 대신 실행할지는 Main의 Control/PG Simulation으로 결정한다.

## 16. 2차 검증 결과

| 검증 항목 | 공식 Docs | 현재 코드 | 판정 |
|---|---|---|---|
| Main Test 메뉴 진입 | Test Runner 제공 | 단일 modeless 창 생성/재활성화 | 일치 |
| 작업별 정책 단일화 | `TestRunnerPolicy` 단일 기준 | UI 표시와 RunOptions 모두 정책 사용 | 일치 |
| 작업별 설정 저장 | `Config/TestRunner.yaml` | task key별 YAML 저장/복원 | 일치 |
| 공통 검사 파이프라인 | StartJob/InputStep/EndJob/이벤트 결과 | MainWindowViewModel 공통 실행 호출 | 일치 |
| 출력 위치 | 표준 결과 루트 고정 | `Vars.GlassInspectionResultsDir` 사용 | 일치 |
| Simulation 분리 | Control/PG/CA410 별도 | 세 상태 및 배지 분리 | 일치 |
| Offset 적용 | 읽기 전용 참고, 자동 반영 없음 | 읽기 전용 창 | 일치 |
| Offset ToolTip | 읽기 전용이어야 함 | “업데이트”한다고 표기 | 불일치 |
| 실행 순서 요약 | Align 후 행 Contact | Contact를 Align보다 먼저 표시 | 불일치 |
| CA410 Simulation 안내 | CA410 전용 Simulation 필요 | 작업 설명은 일반 Simulation으로 표기 | 설명 보완 필요 |
| Window 상태 전이 | 상태 머신 강제 | 미적용 | 불일치 |
| Window별 로그 | Caller/LogViewer 요구 | 창 자체 미적용 | 불일치 |

## 17. 추가 확인이 필요한 부분

- 실제 장비별 Cell Interval/Line Delay의 권장 운영값은 코드와 공식 문서에 고정 범위가 없다. 장비 takt와 안정화 시간을 기준으로 현장 검증이 필요하다.
- Folder source의 정확한 셀 폴더·패턴 파일 규칙은 IP recipe, manifest, 실제 입력 데이터 세트를 함께 확인해야 한다.
- CA410 Only의 측정 위치·pattern 세부 순서는 현재 Recipe의 CA410Plan/Pattern/Point 설정에 따라 달라진다.
- 표준맵 `Measured X/Y(px)`를 Stage 보정 µm로 바꾸는 물리 변환 기준은 설치 교정값이 필요하며 이 창이 계산하지 않는다.
