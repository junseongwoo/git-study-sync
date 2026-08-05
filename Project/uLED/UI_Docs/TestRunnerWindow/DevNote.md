# TestRunnerWindow 인수인계 개발 노트

작성일: 2026-08-03

## 1. 분석 범위

### 직접 확인한 파일

- `uLedAoiConsole/Windows/Core/TestRunnerWindow.xaml`
- `uLedAoiConsole/Windows/Core/TestRunnerWindow.xaml.cs`
- `uLedAoiConsole/Models/TestRunnerModels.cs`
- `uLedAoiConsole/Windows/Core/MainWindow.xaml`
- `uLedAoiConsole/Windows/Core/MainWindow.xaml.cs`
- `uLedAoiConsole/ViewModels/MainWindowViewModel.cs`
- `uLedAoiConsole/Windows/Core/StandardMapOffsetWindow.xaml`
- `uLedAoiConsole/Windows/Core/StandardMapOffsetWindow.xaml.cs`
- `uLedAoiConsole/Services/Automation/AutomationApiHostService.cs`
- `uLedAoiConsole/Services/Export/ExportZipService.cs`
- `uLedAoiConsole/Helpers/Vars.cs`

### 적용한 공식 문서

- `docs/README.md`
- `docs/프로젝트 구조.md`
- `docs/전체 flow.md`
- `docs/main-glass-inspection-flow.md`
- `docs/automation-api.md`
- `docs/development/smoke-test-plan.md`
- `docs/표준맵사용검사-technical-manual.md`
- `docs/development/change-log.md`

`dist-lib/docs/README.md`는 저장소 지침상 우선 확인 대상이지만 현재 checkout의 `dist-lib`가 비어 있어 검증할 수 없었다.

## 2. 변경 시 가장 먼저 볼 지점

| 변경 목적 | 우선 확인 위치 |
|---|---|
| 작업 추가/삭제 | `TestRunnerTask`, `TestRunnerPolicy.Tasks` |
| 작업 설명 변경 | `TestRunnerPolicy.GetDescription` |
| 작업별 UI 표시 | `TestRunnerPolicy.Is*Visible` |
| Run 옵션 변경 | `TestRunnerPolicy.BuildRunOptions` |
| 하단 순서 요약 | `TestRunnerPolicy.BuildSummary` |
| 설정 필드 추가 | `TestRunnerTaskSettings`, Window load/commit/default |
| 실행 flow 변경 | `MainWindowViewModel.StartTestRunnerRunAsync`, `ExecuteGlassInspectionAsync` |
| 자동화와 일치 확인 | `AutomationApiHostService`의 `BuildRunOptions` 호출 |
| 결과/ZIP | Window export 상태 처리, `ExportZipService` |
| 표준맵 Offset | `BuildStandardMapOffsetComparisonRows`, `StandardMapOffsetWindow` |

작업별 분기를 XAML 또는 Window 이벤트에 새로 하드코딩하지 말고 `TestRunnerPolicy`를 확장하는 것이 공식 기준이다. Automation API도 같은 정책을 사용하므로 정책 변경은 UI뿐 아니라 외부 실행 계약에도 영향을 준다.

## 3. 모델 구조

### TestRunnerTask

```text
CaptureInspect
CaptureOnly
Ca410Only
Aging
ControlOnly
Replay
```

enum 문자열은 YAML의 `Tasks` dictionary key로 사용된다. 이름 변경은 기존 설정 파일과의 호환 문제를 만들 수 있다. 저장소의 fallback/migration 금지 지침 때문에 자동 변환을 추가하려면 먼저 사용자 확인이 필요하다.

### TestRunnerTaskSettings

주요 필드는 다음 범주로 나뉜다.

- 식별: `LotId`, `GlassId`
- 입력: `Source`, `InputFolder`, `BufferSourceFolderPath`
- timing: `CellIntervalSeconds`, `LineDelaySeconds`, `RepeatCount`
- flow: `UseAlign`, `UseGlassIdReading`, `UseContactFlow`, `UseContactCheck`, `UseAgingBeforeInspect`, `UseUnloadingFlow`
- 측정/결과: `UseCa410`, `SaveOriginalImages`, `ExportAfterInspect`

### TestRunnerSettingsData

- `LastTask`: 마지막 선택 작업
- `Tasks`: 작업 enum 문자열별 설정

설정 파일은 `Vars.TestRunnerSettingsPath`이며 실경로는 `{Vars.WorkDir}/Config/TestRunner.yaml`이다.

## 4. 정책 테이블의 핵심 불변 조건

`BuildRunOptions`는 UI 값을 그대로 통과시키지 않고 작업 종류에 따라 강제한다.

| 옵션 | 강제 규칙 |
|---|---|
| `Source` | Replay/Aging/Control/CA410는 작업별 source 강제, Capture만 UI source 사용 |
| `WithInspect` | CaptureInspect와 Replay만 true |
| `UseMotion` | Replay만 false |
| `UseAlign` | motion 작업이면서 설정 true |
| `UseGlassIdReading` | Capture 계열이면서 설정 true |
| `UseContactFlow` | motion 작업이면서 설정 true |
| `UseContactCheck` | Contact가 true여야 true |
| `UseCa410` | CA410 Only는 무조건 true, Capture 계열은 설정값 |
| `UseAgingBeforeInspect` | CaptureInspect만 설정값 허용 |
| `SaveOriginalImages` | Capture 계열만 허용 |
| `ExportAfterInspect` | CaptureInspect만 허용 |
| `SkipIpConnectionForControlOnly` | CA410 Only와 Control Only에서 true |
| `RepeatCount` | Replay는 1, 나머지는 최소 1 |
| timing | 최소 0으로 clamp |
| output | 항상 `Vars.GlassInspectionResultsDir` |

새 작업을 추가할 때 최소한 다음을 한 번에 검토해야 한다.

1. enum
2. task definition/표시명/설명
3. 모든 `Is*Visible`
4. `BuildRunOptions`
5. `BuildSummary`
6. 설정 기본값/저장/복원
7. Main 실행 provider 선택
8. Automation API 허용 작업과 요청 검증
9. smoke test와 공식 문서

## 5. Window 상태와 이벤트 흐름

```text
생성자
  -> YAML store LoadOrDefault
  -> task definitions 바인딩
  -> LastTask 복원
  -> LoadSettingsToUi
  -> visibility/summary/run/export 갱신
  -> MainWindowViewModel.PropertyChanged 구독

작업 변경
  -> CommitUiToSettings(old)
  -> current task 변경
  -> LoadSettingsToUi(new)

Run
  -> commit/검증/save
  -> policy option 생성
  -> Hide
  -> StartTestRunnerRunAsync await

Closing
  -> commit/save
  -> PropertyChanged 구독 해제
```

`_loadingUi`는 programmatic UI 설정 중 `TextChanged`/`Checked`가 설정을 되써서 섞지 않도록 막는다. `_exportFolderEditedByUser`는 사용자가 직접 선택한 ZIP 대상 폴더를 run 상태 갱신이 덮지 않도록 한다.

## 6. MainWindowViewModel 연결

### 시작

`StartTestRunnerRunAsync`는 다음을 담당한다.

- 실행 가능 여부 확인
- checkpoint 발견 시 재개/새 실행/취소 선택
- 현재 옵션 보관
- `ExecuteGlassInspectionAsync` 호출

checkpoint 재개 시 현재 UI 옵션보다 checkpoint의 `Options`가 우선한다. 이 차이를 유지해야 재개 지점의 실행 계약이 바뀌지 않는다.

### 반복

일반 실행은 `RepeatCount`만큼 전체 Glass Job을 반복한다. 재개 실행은 checkpoint가 가진 상태를 이어야 하므로 반복 수를 1로 취급하는 현재 로직을 확인해야 한다.

### Stop

현재 Stop은 cancellation과 함께 Control Stop 및 IP ClearBuffer를 요청하는 빠른 중단 경로다. 공식 `docs/전체 flow.md`의 Stop 기준과 함께 수정해야 한다.

## 7. 검사 flow 변경 금지 지점

Test Runner가 호출하는 Main 검사 flow에는 다음 불변 조건이 적용된다.

- `StartJob`은 셀 준비이고 pattern/point step을 실행하지 않는다.
- Camera/Folder/CurrentBuffer의 실제 입력은 모두 `InputStep`이다.
- `InputStep`은 촬영 또는 입력 완료까지 동기 응답한다.
- 검사는 `EndJob` 이후 IP 단일 queue/worker가 비동기로 순차 처리한다.
- `EndJob`은 최종 결과를 기다리지 않고 ACK한다.
- 최종 결과는 `EvtJobCompleted(final_result)`로 받는다.
- 결과 저장/UI/Export 때문에 다음 셀의 motion/PG/input을 막지 않는다.
- PG 패턴과 셀 색상은 실제 step 직전 훅에 연결한다.
- `REQ_PTN_OFF`는 step마다가 아니라 셀 마지막에 보낸다.

`StartJob accepted`에서 pattern 전체를 선실행하는 변경, `EndJob`에서 결과를 기다리는 변경, Camera를 과거 `Grab` 경로로 되돌리는 변경은 금지된다.

## 8. Source와 provider 연결

| Source/작업 | provider/입력 개념 |
|---|---|
| Camera | IP loaded-buffer 계층 + Camera `InputStep` |
| Folder | IP loaded-buffer 계층 + 셀 폴더 이미지 `InputStep` |
| CurrentBuffer | IP buffer 0 입력 |
| ControlOnly | 이미지 없이 제어/CA410 중심 provider |
| Aging | 이미지 없이 Aging 중심 실행 경로 |
| Replay | 저장 결과 폴더를 읽는 replay provider |

`CA410Only`의 source는 `ControlOnly`다. provider 선택 분기에서 작업 enum이 아니라 최종 `Source`와 `UseCa410` 조합이 어떤 경로를 타는지 함께 봐야 한다.

## 9. 데이터 바인딩 특성

Task List만 `ItemsSource`와 DataTemplate을 사용한다. 나머지 화면은 WPF Binding 대신 Code-behind가 직접 값을 넣고 읽는다.

장점:

- 정책 객체와 빠르게 연결하기 쉽다.
- 별도 TestRunnerViewModel 없이 MainWindowViewModel을 재사용한다.

주의:

- 설정 필드를 추가할 때 model만 추가하면 안 된다.
- `CreateDefaultSettings`, `LoadSettingsToUi`, `CommitUiToSettings`, summary/visibility를 모두 수정해야 한다.
- 누락되어도 컴파일 오류가 나지 않고 기본값 false/0으로 실행될 수 있다.

## 10. 확인된 코드 위험과 개선 후보

### 10.1 Offset ToolTip 오류

XAML ToolTip은 “recipe 기존값을 비교해서 업데이트”한다고 하지만 실제 보조 창은 읽기 전용이며 공식 문서도 자동 write-back 금지다.

권장 방향: ToolTip을 “마지막 검사의 실측 offset을 읽기 전용으로 확인합니다”로 변경한다.

### 10.2 Window 생명주기 지침 미준수

`TestRunnerWindow`에는 `WindowProcessStateMachine`이 없다. 신규 지침에 맞추려면 생성/Loaded/Closing/Closed 전이를 추가해야 한다. 단, 실제 수정은 이번 분석 범위에 포함하지 않았다.

### 10.3 전용 로그 부재

창에서 YAML 저장 실패를 포함한 로컬 오류를 추적하기 어렵다. 공식 logging 지침에 맞추려면 unique Caller, `RatelLog.ForWindow`, 필요한 경우 LogViewer 연결을 검토한다.

### 10.4 SaveStore 예외 무시

`SaveStore()`가 모든 예외를 삼킨다. 적어도 caller log에 파일 경로와 예외를 남겨야 작업별 설정 복원 문제를 진단할 수 있다.

### 10.5 숫자 입력 UX

invalid 입력은 메시지나 validation 표시 없이 기존 값이 유지된다. 화면의 문자열과 실제 실행값이 다를 수 있다. ValidationRule 또는 실행 전 명시적 오류 표시를 검토한다.

### 10.6 Glass ID 옵션의 UI 범위

Glass ID 자동 인식은 모든 task UI에서 편집 가능하지만 실제 정책은 Capture 계열만 허용한다. non-capture task에서는 숨기거나 비활성화하는 편이 실제 옵션과 일치한다. `BuildSummary`도 동일 조건을 적용해야 한다.

### 10.7 새 설정 생성 시 ContactCheck 누락

`CreateDefaultSettings`는 전달받은 기본 options의 여러 필드를 복사하지만 `UseContactCheck`를 복사하지 않는다. 의도된 안전 기본값인지 누락인지 공식 결정이 필요하다.

### 10.8 Folder 검증 문구와 검사 수준

오류 문구는 valid folder를 요구하지만 Capture Folder는 빈 값만 선검증한다. IP 원격 경로 때문에 로컬 `Directory.Exists`를 쓰지 않는 의도라면 “IP가 접근 가능한 경로” 검증 또는 명확한 문구가 필요하다.

### 10.9 BuildSummary 순서 오류

현재 `BuildSummary`는 Contact/Contact Check를 Align보다 먼저 추가한다. 실제 `ExecuteGlassInspectionAsync`는 Loading과 Glass ID 인식 후 Align을 완료하고, provider의 `BeginRowAsync`에서 행 Contact를 수행한다.

권장 방향: summary 조립 순서를 `Loading -> Glass ID -> Align -> Contact -> Contact Check -> Aging/작업`으로 맞춘다. 실제 flow가 바뀐 것이 아니므로 summary만 공식 flow에 맞춰야 한다.

### 10.10 작업 설명의 Simulation/선택 표현

- CA410 Only의 “Simulation Mode”를 `CA410 Simulation`으로 명확히 해야 한다.
- Control Only의 “Motion/PG를 선택” 문구는 현재 UI와 맞지 않는다. Motion은 정책상 항상 사용되고, 실제/모의 여부는 별도 Simulation 메뉴가 결정한다.

## 11. StandardMapOffsetWindow 인수인계

Test Runner의 Offset 버튼으로 열리는 모달 창이다.

- `BuildStandardMapOffsetComparisonRows()`에서 마지막 replay/검사 상태를 row로 만든다.
- R 채널 첫 point alignment를 우선하고 없으면 첫 alignment를 사용한다.
- `PanelId`를 Cell 표시명으로 사용한다.
- X/Y translation, pair count, residual을 표시한다.
- `abs(X)>3.0 || abs(Y)>3.0`이면 행을 강조한다.
- items는 read-only이고 recipe write-back command가 없다.
- 이 보조 창은 `WindowProcessStateMachine`과 window caller logging을 적용하고 있다.

`[추론]` TestRunnerWindow가 생명주기/로깅 지침을 적용할 때 이 창의 패턴을 가까운 참고 구현으로 사용할 수 있다.

## 12. Export 인수인계

- 표준 검사 결과 루트: `Vars.GlassInspectionResultsDir`
- Export run 폴더는 `ExportNaming`이 단일 소유한다.
- 마지막 Export 경로/상태는 MainWindowViewModel property로 전달된다.
- user-edited Export 경로는 자동 상태 갱신이 덮어쓰지 않는다.
- Export 진행/마무리 중 같은 폴더의 ZIP 버튼을 비활성화한다.
- ZIP prefix 공백 시 `[ELP]검사결과_{folder name}`을 사용한다.

Export 파일명이나 폴더명을 TestRunnerWindow에 새로 조립하지 않는다. 공식 규칙은 `ULed.Contracts.Naming.ExportNaming`과 manifest 계약에 유지한다.

## 13. Simulation 인수인계

세 모드는 독립적이다.

- Control Simulation endpoint 적용은 `MainWindowViewModel.ApplyControlEndpointForCurrentMode`만 사용한다.
- 전역 Control Simulator 포트는 5002다.
- PG Simulation은 PG만 대체한다.
- CA410 Simulation은 CA410만 대체한다.
- Align은 장비가 없을 때 성공을 모사하지 않는다.

Test Runner에 임의의 “Skip IP”, “Use Motion”, “Confirm Motion Step” 옵션을 다시 추가하지 않는다. 현재 정책은 작업 종류와 Simulation을 통해 실행 역할을 분리한다.

## 14. 테스트 체크리스트

### UI/저장

- [ ] 6개 task 순서와 설명 확인
- [ ] task 전환 시 각 작업 값이 서로 섞이지 않는지 확인
- [ ] 창 닫기/재열기 후 `TestRunner.yaml` 복원 확인
- [ ] Simulation 상태가 YAML에 저장되지 않는지 확인
- [ ] invalid 숫자 입력 시 실제 실행값 확인

### 실행 정책

- [ ] Capture + Inspect의 세 source별 `InputStep` 확인
- [ ] Capture Only에서 검사 결과를 기다리지 않는지 확인
- [ ] CA410 Only에서 IP 검사 건너뜀과 CA410 강제 확인
- [ ] Aging에서 AgingPlan 실행 확인
- [ ] Control Only에서 IP 미사용 확인
- [ ] Replay에서 Motion 미사용 및 1회 강제 확인

### Flow

- [ ] Loading -> Glass ID -> Align 순서 확인
- [ ] Contact -> Contact Check -> Aging before Inspect -> 검사 순서 확인
- [ ] `EndJob ACK` 후 다음 셀 진행과 `EvtJobCompleted` 비동기 수신 확인
- [ ] Stop 시 Control Stop/IP ClearBuffer 로그 확인

### 결과

- [ ] 표준 결과 루트 확인
- [ ] Save Original Images root 누락 오류 확인
- [ ] Export progress/finalize 상태 확인
- [ ] Export 중 ZIP 비활성 확인
- [ ] user-edited Export 경로 유지 확인
- [ ] Offset 창 read-only 및 3 px 초과 강조 확인

## 15. 2차 검증 결론

Test Runner의 핵심 설계인 정책 단일화, 작업별 YAML, 공통 Main 검사 flow 재사용, Simulation 분리, 표준 결과 경로는 공식 문서와 코드가 일치한다.

인수인계 시 우선 처리할 불일치는 다음 여섯 가지다.

1. Offset ToolTip의 “업데이트” 표현
2. TestRunnerWindow의 WindowProcessStateMachine 미적용
3. 창 전용 logging/저장 실패 진단 부재
4. non-capture 작업의 Glass ID 자동 인식 UI·summary와 실제 옵션 불일치
5. 하단 summary의 Contact/Align 순서와 실제 flow 불일치
6. 작업 설명의 일반 Simulation 및 Motion/PG 선택 표현

이번 작업은 분석 및 문서 작성만 수행했으며 소스 코드는 수정하지 않았다.
