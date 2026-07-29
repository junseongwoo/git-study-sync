# MainWindow - 메뉴/상단 툴바 간략 기능 분석

## 1. 화면 목적

MainWindow 상단 메뉴는 레시피·장비 설정·검사 실행·진단 창으로 진입하는 허브다. 메뉴 항목은 `MainWindowViewModel` Command 또는 `MainWindow.xaml.cs` Click handler에 연결된다.

아래 상태는 소스 코드 기준이다. `구현`은 Command/Click handler가 실제 동작 또는 Window 열기를 수행하는 경우이고, `미구현`은 메뉴만 있고 하위 항목·Command·Click handler가 없는 경우다.

## 2. Tool 메뉴

| 항목 | 상태 | 간략 기능 |
|---|---|---|
| Load Recipe... | 구현 | 레시피 파일 선택 창을 열어 레시피를 로드한다. 검사 중에는 레시피 변경을 거부한다. 로드 후 Glass Map 갱신 및 연결된 IP로 레시피 동기화를 시도한다. |
| Glass Size Model | 구현 | Glass Size Model 선택/편집 창을 연다. 닫힌 후 Main Glass Map을 다시 생성한다. |
| Recipe | 구현 | RecipeWindow를 연다. |
| Config | 구현 | ConfigWindow를 연다. |
| 장비 변수 관리 | 구현 | EquipmentVariableWindow를 modeless로 열거나 이미 열린 창을 앞으로 가져온다. |
| 알람 관리 | 구현 | AlarmManagementWindow를 modeless로 연다. View 메뉴의 Alarm Manager와 목적이 유사하지만 서로 다른 진입 구현이다. **[추론]** 운영 알람 관리 설정용 창이다. |
| 컨택 유니트 관리 | 구현 | ContactUnitWindow를 modeless로 연다. |
| Simulation > Control Simulation | 구현 | `IsSimulationMode`를 전환한다. 공식 기준상 Control endpoint는 현재 mode에 따라 단일 적용 지점에서 결정된다. |
| Simulation > PG Simulation | 구현 | `IsPgSimulationMode`를 전환한다. 최신 공식 기준상 PG cluster의 simulator 사용 여부를 전역으로 전환한다. |
| Simulation > CA410 Simulation | 구현 | `IsCa410SimulationMode`를 전환한다. CA410 측정 client의 simulator 사용 여부에 반영된다. |
| Export... | 구현 | Glass 검사 결과 export 대화상자를 열고 선택한 입력 결과를 NAS/대상 경로로 export한다. |

## 3. Data 메뉴

| 항목 | 상태 | 간략 기능 |
|---|---|---|
| Data | **미구현** | XAML에 최상위 `MenuItem Header="Data"`만 있고 하위 메뉴, Command, Click handler가 없다. |

## 4. View 메뉴 및 상단 툴바

| 항목 | 상태 | 간략 기능 |
|---|---|---|
| Refresh Map | 구현 | 현재 레시피/Glass Size 기반으로 MainWindow Glass Map을 다시 생성한다. |
| Alarm Manager | 구현 | AlarmManagerWindow를 연다. 상단의 Active Alarm 요약 버튼도 같은 Command를 사용한다. |
| Axis → Glass Coordinate | 구현 | 축 좌표를 Glass 좌표로 확인하는 보조 창을 연다. |
| Zoom ComboBox | 구현 | `ZoomOptions`와 `SelectedZoomOption` 바인딩을 통해 Main Glass Map의 `ZoomFactor`를 바꾼다. **[추론]** 메뉴가 아닌 상단 툴바 성격의 표시 배율 선택기다. |
| IP/Control 상태 배지 | 구현 | IP 및 Control 연결 상태를 색상/문구로 표시한다. 조작 버튼이 아니라 상태 표시다. |
| SIMULATION 배지 | 구현 | Simulation Mode가 활성화됐을 때만 경고 배지를 표시한다. |

## 5. Test 메뉴

| 항목 | 상태 | 간략 기능 |
|---|---|---|
| Test Runner... | 구현 | task 기반 TestRunnerWindow를 열거나 실행 중 숨겨진 창을 다시 표시한다. 공식 문서 기준 Capture+Inspect, Capture Only, CA410 Only, Aging, Control Only, Replay task를 지원한다. |
| Inspect > Load Saved Glass... | 구현 | 저장된 Glass 결함/결과 session 폴더를 선택해 Main map과 결과 상태를 불러온다. |
| Inspect > Release Glass... | 구현 | GlassInspection 시작/이어하기 대화상자를 열고 실제 검사 실행을 시작한다. |
| Inspect > Debug Glass... | 구현 | 검사 실행/재생 설정 대화상자를 열고 Debug/Replay 성격의 Glass 검사 실행을 시작한다. |
| Inspect > Clear | 구현 | 선택 셀 또는 전체 replay 상태와 검사 checkpoint를 제거한다. 실제 장비의 검사 결과 파일을 삭제하는 기능으로 확인되지는 않았다. **[추론]** |
| Load Ready | 구현 | Control runtime에 Load Ready flow 명령을 비동기로 요청한다. 검사와 Control test flow가 동시에 실행 중이면 비활성화된다. |
| Unload Ready | 구현 | Control runtime에 Unload Ready flow 명령을 비동기로 요청한다. |
| PG Recipe | 구현 | PGRecipeControlWindow를 열거나 기존 창을 활성화한다. |
| Flow Test | 구현 | FlowTestWindow를 연다. |
| EEC-P725R2 PG Test | 구현 | EEC-P725R2 Light Test 창을 연다. |
| CA-410 Test | 구현 | CA-410 Test 창을 연다. |
| Console API Test | 구현 | Console API Test 창을 연다. |
| Control API Host Test | 구현 | Control API Host Test 창을 연다. |

Test 메뉴는 운영 검사보다 장비 검증·개발/시운전 성격이 강하므로, 권한 있는 사용자만 사용해야 한다. **[추론]**

## 6. ETC 메뉴

| 항목 | 상태 | 간략 기능 |
|---|---|---|
| 전체 불량 오버레이 표시 | 구현 | `ShowAllReplayDefectOverlays`를 전환해 Main Glass Map의 replay 결함 overlay 표시 범위를 바꾼다. **[추론]** 검사 판정이나 원본 결과를 바꾸지 않는 표시 옵션이다. |

## 7. 전체 흐름 요약

```text
Tool: 레시피·장비 기준값·시뮬레이션 설정
View: Main map/상태 확인
Test: 검사·Control·PG·CA410·API 시험 실행
ETC: 결함 overlay 표시 방식 변경
```

### 공식 문서와 화면의 주의점

`Light / Pattern` 탭의 과거 안내와 달리 최신 공식 문서 기준 PG simulator는 전역 Simulation Mode가 결정한다. MainWindow의 `PG Simulation` 메뉴가 그 전역 전환 진입점이다.

### 참조 근거

- UI: `uLedAoiConsole/Windows/Core/MainWindow.xaml`, `MainWindow.xaml.cs`
- ViewModel: `uLedAoiConsole/ViewModels/MainWindowViewModel.cs`
- 공식 문서: `docs/automation-api.md`, `docs/main-glass-inspection-flow.md`, `docs/development/change-log.md`
