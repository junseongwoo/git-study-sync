# MainWindow 인수인계 노트

## 구성 파일과 책임

| 파일 | 책임 |
|---|---|
| `Windows/Core/MainWindow.xaml` | 화면 레이아웃, 바인딩, 메뉴, 결과 표와 이미지 영역 정의 |
| `Windows/Core/MainWindow.xaml.cs` | 창 생명주기, 자식 창 생성/재사용, GlassMap 클릭·크기 이벤트, 대화상자 표시 |
| `ViewModels/MainWindowViewModel.cs` | 화면 상태, Command, 레시피 로드, Map 생성, 연결 상태, 검사/재생/Export 결과 처리 |

## 핵심 ViewModel 상태

- Map/선택: `MapInfo`, `SelectedCellId`, `SelectedCellName`, `ZoomOptions`, `SelectedZoomOption`
- 연결/알람: `IpConnectionStateText`, `ControlConnectionStateText`, `ActiveAlarmSummary`, 각 Brush 속성
- 현재 작업: `CurrentRecipeName`, `CurrentLotId`, `CurrentGlassId`
- 검사 상태: `GlassInspectionStatusText`, `GlassReplayTotalCells`, `GlassReplayCompletedCells`, `GlassReplayTotalDefects`, `GlassReplayLaneSummaries`
- 선택 결과: `SelectedCellJudgment`, `CellReplayDefects`, `SelectedCellReplayDefect`, `SelectedDefectCropImage`, `SelectedMappingImageTabs`

## Command 연결

- 창 열기: `OpenRecipeCommand`, `OpenConfigCommand`, `OpenGlassSizeCommand`, `OpenFlowTestCommand`, `OpenCa410TestCommand` 등
- 레시피/Map: `LoadRecipeCommand`, `RefreshGlassMapCommand`
- 검사: `InspectGlassReleaseCommand`, `InspectGlassReplayCommand`, `StopGlassReplayCommand`, `ClearInspectCellReplayCommand`
- 운영 보조: `RunLoadReadyFlowCommand`, `RunUnloadReadyFlowCommand`, `ExportGlassInspectionResultCommand`, `LoadSavedGlassDefectFolderCommand`

## 이벤트 및 생명주기

- 생성자에서 Window process 상태를 initializing으로 설정하고 `DataContext`에 MainWindowViewModel을 배정한다.
- Loaded에서 준비 상태 전환, 초기 viewport 처리, 자동화 호스트 준비를 수행한다.
- Closing에서 `TryEnterClosing()` 성공 경로에서만 자식 창·PG DLL·Automation host·ViewModel을 정리한다.
- Closed에서 window process 상태를 closed로 전환한다.
- `GlassMap_CellClicked`는 `NotifyManualReplayCellSelection()`을 호출하므로 Map 선택 변경은 결과 패널 갱신의 출발점이다.

## 공식 문서 우선 사항

- Console은 전체 오케스트레이션 중심이고, MainWindow는 현재 Recipe의 Map·IP 상태·편집/테스트 진입을 제공한다.
- 메인 글래스 검사 flow의 기준은 `docs/main-glass-inspection-flow.md`이며, 화면 코드만 보고 검사 프로토콜을 재정의하면 안 된다.
- 레시피의 상위 기준은 `ConsoleRecipeDocument`, IP 실행 레시피 기준은 `RecipeModel`이다.

## 코드와 문서의 차이

- 공식 문서는 MainWindow의 주요 메뉴로 `Tool > Glass Map Design`을 열거하지만, 현재 XAML의 Tool 메뉴에는 이 항목이 없다.
- 공식 문서의 단순한 진입/상태 요약 범위보다 현재 구현의 검사 실행·재생·Export·결과 시각화 범위가 넓다.

## 유지보수 시 주의

- XAML 바인딩 이름을 변경하면 ViewModel의 PropertyChanged/Command와 함께 확인한다.
- 셀 선택 처리 변경 시 GlassMap 선택, 선택 셀 판정, 불량 목록, Crop/Mapping Image가 함께 갱신되는지 확인한다.
- 창 종료 정리는 Closing의 단일 진입 경로를 유지한다.
- 검사 flow 변경은 `docs/main-glass-inspection-flow.md`의 StartJob/StartStep/EndJob 및 async worker 불변 조건을 먼저 확인한다.
- 상태 확인은 UI만 보지 말고 Console 로그(`c:\elp\uLed\uLedAoi\logs\yyyyMM\`)에서 MainWindow/관련 Caller 로그를 함께 확인한다.

## 추가 확인 대상

- `TestRunnerPolicy` 및 `Config/TestRunner.yaml`: AutoRun·검사 옵션의 실제 정책 확인
- `GlassMapControl`: 셀 상태 색상, 오버레이, 회전/확대 처리 확인
- `GlassInspectionRunWindow`, `GlassInspectionStartWindow`: INSPECT 실행 전 사용자 입력과 검증 확인
- `CellInspectionReplayLoader`, `GlassInspectionReplayBatchLoader`: 저장 결과를 화면 모델로 변환하는 기준 확인
- `ConsoleFlowCoordinator`, `docs/main-glass-inspection-flow.md`: 실제 검사·통신 flow 확인

[추론] MainWindowViewModel은 화면 표시뿐 아니라 검사 실행과 결과 export를 직접 조정하는 조정자 역할도 가진다. 이 범위가 더 커질 경우 검사 실행 서비스를 별도 계층으로 분리할 필요성을 검토할 수 있으나, 현재 변경 요구는 아니다.
