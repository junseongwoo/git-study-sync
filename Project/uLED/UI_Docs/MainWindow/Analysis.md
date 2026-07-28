# MainWindow 분석

## 1. 화면 목적

### 공식 문서 기준

`uLedAoiConsole`은 전체 오케스트레이션의 중심이며, MainWindow는 다음을 제공하는 메인 진입 화면이다.

- 현재 레시피 기준의 Glass Map 표시
- IP 연결 상태 요약 및 백그라운드 모니터링
- Glass Size, Recipe, Config 등 편집 화면과 테스트 화면의 진입점

앱은 마지막 사용 레시피를 자동으로 열며, 없으면 기본 레시피를 연다. 메인 창이 준비되었을 때 연결된 IP가 있으면 현재 레시피를 자동 업로드한다.

근거: `docs/프로젝트 구조.md` 6.1, `docs/전체 flow.md` 2~3, `docs/시작 가이드.md` 3 및 16.

### 코드 차이

공식 문서의 MainWindow 설명은 진입·상태 요약 중심이다. 현재 XAML과 ViewModel에는 다음의 검사 운영 기능도 구현되어 있다.

- 글래스 검사 시작/중지와 AutoRun 선택
- 저장된 검사 결과 로드, 재생(Debug), 결과 초기화
- 검사 진행률, IP lane별 진행 상태, 셀 판정, 불량 목록·Crop·Mapping 이미지 표시
- 결과 Export, 알람·장비 변수·컨택 유니트 관리, Simulation 설정

따라서 이 문서는 화면의 **업무 목적은 공식 문서**, 세부 동작은 **코드 확인 결과**로 구분한다.

## 2. 화면 구성

| 영역 | XAML 구성 | 표시/역할 |
|---|---|---|
| 상단 상태/메뉴 | `DockPanel`, `Menu`, `ComboBox`, 알람 버튼·상태 배지 | 알람 요약, IP·Control 연결 상태, Simulation 표시, 메뉴와 Map 확대율 선택 |
| 좌상단 | `ScrollViewer` + `GlassMapControl` | 현재 레시피의 Glass Map, 선택 셀, 글래스 존재 상태, 검사 상태 및 불량 오버레이 표시 |
| 좌하단 | `TabControl` | Log, Inspection State, Cell Summary, 패턴별 통계, CA410 결과 표시 |
| 우상단 | `ToggleButton`, `Button`, 상태 `Border` | AutoRun, 검사 시작/중지, Recipe 편집 진입, 현재 검사 상태 |
| 우중단 | Recipe 정보 `GroupBox` | 현재 Recipe, LOT ID, Glass ID 표시 및 Recipe 로드 |
| 우중단 | 셀 판정 `GroupBox` | 선택 셀의 합격/불량 판정과 Black/Dark/Cluster/White/선 불량·점등 관련 수량 |
| 우하단 | `DataGrid`, `Image`, `TabControl` | 선택 셀의 불량 상세, Crop 이미지, 패턴별 Mapping Image |

좌측 내부와 좌·우 패널 사이는 `GridSplitter`로 크기를 조절할 수 있다. ViewModel은 마지막 화면 분할 크기를 변수 저장소에 보관한다.

## 3. 주요 컨트롤 및 바인딩

| 컨트롤/메뉴 | 종류 | 기능 | 연결 |
|---|---|---|---|
| Active Alarm | Button | 현재 활성 알람 요약을 열기 | `OpenAlarmManagerCommand` |
| IP / Control 상태 | Border + TextBlock | 연결/해제 상태와 요약 표시 | `IpConnection*`, `ControlConnection*` |
| Map 확대율 | ComboBox | Glass Map 확대율 선택 | `ZoomOptions`, `SelectedZoomOption` |
| Tool > Load Recipe | MenuItem/Button | 현재 레시피를 파일에서 변경 | `LoadRecipeCommand` |
| Tool > Glass Size Model / Recipe / Config | MenuItem | 각 설정·편집 창 열기 | `OpenGlassSizeCommand`, `OpenRecipeCommand`, `OpenConfigCommand` |
| Tool > Simulation | Checkable MenuItem | Control·PG·CA410 Simulation 모드 설정 | `IsSimulationMode`, `IsPgSimulationMode`, `IsCa410SimulationMode` |
| View > Refresh Map | MenuItem | 현재 레시피 기반 Map 재생성 | `RefreshGlassMapCommand` |
| Test > Inspect | MenuItem | 저장 결과 로드, 검사 실행, Debug 재생, 화면 상태 초기화 | 관련 Inspect/Load/Clear Command |
| INSPECT / STOP | Button | 글래스 검사 시작 또는 중지 요청 | `InspectGlassReleaseCommand`, `StopGlassReplayCommand` |
| SET UP | Button | Recipe Editor 열기 | `OpenRecipeCommand` |
| Glass Map | `GlassMapControl` | 셀 선택 및 검사 상태/불량 오버레이 시각화 | `MapInfo`, `SelectedCellId`, `InspectionCellStates`, `CellReplayOverlays` |
| Inspection State | KPI + DataGrid | 전체/완료/양품/불량/총 불량, 진행률, IP lane별 현재·완료 상태 | `GlassReplay*`, `GlassReplayLaneSummaries` |
| Cell Summary / 패턴별 통계 / CA410 | DataGrid | 셀 판정, 패턴 검사 통계, CA410 측정값 | 각각의 결과 컬렉션 |
| 선택 셀 불량 목록 | DataGrid | 채널, 불량 코드, Row/Column, 영역, Level, Camera 좌표 | `CellReplayDefects`, `SelectedCellReplayDefect` |
| Crop / Mapping Image | Image + TabControl | 선택 불량 Crop과 패턴별 결과 이미지 표시 | `SelectedDefectCropImage`, `SelectedMappingImageTabs` |

## 4. 이벤트와 명령 처리

- `MainWindow.Loaded`: 화면 준비 후 ViewModel 초기화/연결 상태 처리 및 Glass Map viewport 갱신을 수행한다.
- `MainWindow.Closing`/`Closed`: 중복 종료를 막고, 자식 창·통신 호스트를 정리한 뒤 ViewModel `Shutdown()`을 호출한다.
- `GlassMap.CellClicked`: 클릭한 셀 ID를 ViewModel에 알리고, 선택 셀 결과 패널을 동기화한다.
- `GlassMapScroll.SizeChanged`, 창 `SizeChanged`: 확대율에 맞춰 Map 크기와 스크롤바 사용 여부를 갱신한다.
- `MainMenu.Click`: 실제 하위 메뉴 선택 경로를 로그에 기록한다.
- XAML Command: 메뉴와 버튼은 `RelayCommand`/`IAsyncRelayCommand`를 통해 ViewModel로 전달된다. UI 로직이 Code-behind에 직접 집중되지 않는 MVVM 구조다.

## 5. 데이터 흐름

1. 앱 시작 시 Config, Variables, Glass Map Design, GlassSize, Recipe 저장소와 IP 런타임이 준비된다.
2. MainWindowViewModel이 현재 `ConsoleRecipeDocument`를 읽어 `MapInfo`를 만들고 화면에 바인딩한다.
3. IP/Control 상태와 알람 상태가 ViewModel 속성으로 갱신되어 상단 배지에 반영된다.
4. 사용자가 Map의 셀을 선택하면 해당 셀의 판정, 불량 목록, Crop, Mapping Image가 우측 패널에 표시된다.
5. 검사/재생 결과가 도착하면 셀 상태, KPI, lane 상태, 표와 오버레이가 갱신된다.

[추론] `CellReplay*`라는 속성명과 저장 결과 로드/Debug 메뉴의 연결로 보아, 이 화면은 실시간 검사 결과와 저장된 검사 결과를 같은 표시 모델로 보여주도록 설계되어 있다.

## 6. 공식 문서와 구현의 차이

| 항목 | 공식 문서 | 현재 코드 |
|---|---|---|
| MainWindow 역할 | Glass Map, IP 상태 요약, 편집/테스트 창 진입 | 좌측 상태 탭과 우측 검사·결과 패널까지 포함 |
| 주요 Tool 메뉴 | Glass Map Design, Glass Size Model, Recipe, Config | XAML에는 Load Recipe, Glass Size, Recipe, Config 및 관리/Simulation/Export가 보이나 `Glass Map Design` 메뉴는 없음 |
| 검사 진입 | 문서는 Recipe Editor의 IP 명령과 Test 흐름을 주로 안내 | MainWindow에 `INSPECT`, `STOP`, 저장 결과/Debug 재생 메뉴가 직접 존재 |

문서와 코드가 다른 경우 본 문서에서는 공식 문서의 업무 정의를 우선하고, 코드 차이는 현재 구현 확인 사항으로만 표시한다.

## 7. 추가 확인이 필요한 부분

- `Data` 메뉴는 현재 XAML에 하위 항목이 없다.
- `Start Time` 표시는 레이블만 있고 값 바인딩이 없다.
- 공식 문서에 있는 `Tool > Glass Map Design` 메뉴가 현재 MainWindow XAML에는 없다. 해당 기능이 다른 창으로 이동했는지 확인이 필요하다.
- [추론] AutoRun의 실제 반복·자동 시작 조건은 `MainWindowViewModel`의 검사 실행 옵션 및 Test Runner 정책까지 함께 확인해야 정확히 문서화할 수 있다.

## 근거 파일

- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\docs\프로젝트 구조.md`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\docs\전체 flow.md`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\docs\시작 가이드.md`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\Windows\Core\MainWindow.xaml`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\Windows\Core\MainWindow.xaml.cs`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\ViewModels\MainWindowViewModel.cs`
