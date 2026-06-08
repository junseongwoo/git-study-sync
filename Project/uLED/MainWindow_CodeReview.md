# MainWindow + MainWindowViewModel 코드 리뷰

> **파일 범위**: `MainWindow.xaml` / `MainWindow.xaml.cs` / `MainWindowViewModel.cs` (3,822줄)
> **리뷰 목적**: 핵심 목적·기능, 함수/클래스 문서, 알고리즘 설명, 가정 및 제한 사항

---

## 목차

1. [핵심 목적 및 주요 기능](#1-핵심-목적-및-주요-기능)
2. [아키텍처 결정 사항](#2-아키텍처-결정-사항)
3. [MainWindow.xaml — 레이아웃 문서](#3-mainwindowxaml--레이아웃-문서)
4. [MainWindow.xaml.cs — 클래스 문서](#4-mainwindowxamlcs--클래스-문서)
5. [MainWindowViewModel — 클래스 문서](#5-mainwindowviewmodel--클래스-문서)
   - 5-1. 생성자 및 의존성
   - 5-2. 주요 프로퍼티
   - 5-3. 커맨드 목록
   - 5-4. 핵심 메서드 상세
6. [핵심 알고리즘 상세](#6-핵심-알고리즘-상세)
   - 6-1. Glass 검사 실행 루프
   - 6-2. 셀 1개 라이프사이클 (ProcessGlassReplayAssignmentAsync)
   - 6-3. BuildGlassReplayRowPlans — 배치 계획 알고리즘
   - 6-4. WaitForProviderEventAsync — 이벤트→Task 패턴
   - 6-5. UpdateGlassMapViewport — 줌 모드 전환
7. [가정 및 제한 사항](#7-가정-및-제한-사항)
8. [다음 분석 대상](#8-다음-분석-대상)

---

## 1. 핵심 목적 및 주요 기능

### 핵심 목적

`MainWindow`는 **uLED 점등 검사기의 운영 제어 중심 화면**이다.
`MainWindowViewModel`은 **Glass 검사 전체 오케스트레이션 엔진**으로, 단순 UI 바인딩 계층이 아니라 검사 시퀀스 스케줄러·상태 머신·알람 관리자를 동시에 수행한다.

### 주요 기능 목록

| 기능 분류 | 세부 기능 |
|---|---|
| **GlassMap 시각화** | 셀 배치 렌더링, 실시간 검사 상태(색상), 불량 오버레이, 줌/회전 |
| **Glass 검사 실행** | Row/Step/Batch 계획화 → IP1·IP2 병렬 실행 → Checkpoint |
| **연결 모니터링** | IP 3초 폴링 자동 재연결, Control EventNotification Push 수신 |
| **알람 관리** | Heavy/Light 분류, 상태별 억제, Control 알람 통합 |
| **결과 조회** | 셀 클릭 → 불량 목록, Crop 이미지, Mapping 이미지 표시 |
| **레시피 관리** | 로드/교체 → IP 자동 동기화, GlassMap 즉시 재생성 |
| **테스트 도구** | FlowTest, PG Test, CA-410, Console API, Control API |

---

## 2. 아키텍처 결정 사항

### 결정 1: ViewModel이 WPF를 직접 참조하지 않는다

**이유**: ViewModel을 순수 C# 로직으로 유지하여 단위 테스트 가능성 확보.

**구현 방식**: View가 생성 시 모든 UI 조작 함수를 `Action` / `Func` 콜백으로 주입한다.

```csharp
// MainWindow.xaml.cs 생성자 — 콜백 주입
_viewModel = new MainWindowViewModel(
    OpenGlassMapDesignWindow,       // Action — 모달 창 열기
    ShowGlassInspectionRunDialog,   // Func<GlassInspectionRunOptions?> — 다이얼로그
    ...
);
```

> **제한**: ViewModel 내부에서 `Application.Current.Dispatcher`를 직접 사용하는 구간이 존재한다.
> 이는 비동기 검사 루프에서 UI 스레드 마샬링이 필요하기 때문이며, 완전한 WPF 분리가 이루어지지 않은 부분이다.

---

### 결정 2: 창 열기 방식을 ShowDialog / Show로 엄격히 구분한다

**이유**: 편집 중(RecipeWindow, GlassSizeWindow 열린 상태) 검사 명령이 들어오는 것을 구조적으로 차단.

| 창 종류 | 방식 | 이유 |
|---|---|---|
| GlassMapDesignWindow, RecipeWindow, GlassSizeWindow, ConfigWindow | `ShowDialog()` | 블로킹 모달 — 편집 중 명령 차단 |
| FlowTestWindow, EecP725R2LightTestWindow, Ca410TestWindow | `Show()` | 비모달 — MainWindow와 병렬 사용 |
| AlarmManagerWindow | `Show()` + 싱글턴 관리 | 이미 열려 있으면 `Activate()` |

---

### 결정 3: 검사 중단을 "즉시 종료"가 아닌 "협조적 중단"으로 구현한다

**이유**: 진행 중인 셀의 EndJob ACK를 받기 전에 끊으면 IP 상태가 불일치 발생.

```csharp
// StopGlassReplay() — CancellationToken을 쓰지 않고 플래그만 세운다
private void StopGlassReplay()
{
    if (!_glassReplayStopRequested)
    {
        _glassReplayStopRequested = true;   // 플래그: 현재 Step 완료 후 중단
        IsGlassReplayStopping = true;       // UI: GlassInspectionStoppingWindow 팝업
    }
}

// CancelStopGlassReplay() — 중단 취소
private void CancelStopGlassReplay()
{
    _glassReplayStopRequested = false;
    IsGlassReplayStopping = false;
}
```

**중단 체크 위치**: Step 루프 시작 직전에만 `_glassReplayStopRequested`를 확인한다.
즉, **현재 Step 배치의 EndJob ACK가 완료된 후에만** 중단된다.

---

## 3. MainWindow.xaml — 레이아웃 문서

### 전체 구조

```
Window [Title="MacroAoi Console", 1920×1080, Maximized]
└─ Grid (2 Row)
   ├─ Row 0: DockPanel (메뉴 바)
   │   ├─ Right: 알람 버튼 · IP 상태 · Control 상태
   │   └─ Left: Menu (Tool/Data/View/Test/ETC) · ZoomComboBox · TextBox
   └─ Row 1: Grid (3 Column)
       ├─ Col 0: Grid (Left)
       │   ├─ Row 0: ScrollViewer > GlassMapControl (커스텀)
       │   └─ Row 1: TabControl [Height=240]
       │       ├─ Tab: Log (LogViewer)
       │       ├─ Tab: Inspection State (통계 카드 + Lane DataGrid)
       │       ├─ Tab: Grade (등급 집계)
       │       └─ Tab: Code Top 10 (불량 코드 빈도)
       ├─ Col 1: GridSplitter [Width=6]
       └─ Col 2: Grid (Right, Width=800)
           ├─ Row 0: UniformGrid [4 버튼, Height=60]
           ├─ Row 1: Border [상태 바, Height=60]
           ├─ Row 2: GroupBox [레시피 정보]
           ├─ Row 3: DataGrid [불량 목록, Height=220]
           └─ Row 4: Grid [불량 이미지 (Crop + Mapping)]
```

---

### 바인딩 목록 (GlassMapControl)

```xml
<local:GlassMapControl
    MapInfo="{Binding MapInfo}"
    RotationAngle="{Binding RotationAngle}"
    ZoomFactor="{Binding ZoomFactor}"
    ShowPartitionNameOverlay="{Binding Source={x:Static local:Vars.EMRConfig},
                               Path=ShowGlassMapPartitionNameOverlay}"
    CellOrigin="{Binding SelectedCellOrigin}"
    SelectedCellId="{Binding SelectedCellId}"
    InspectionCellStates="{Binding InspectionCellStates}"
    ReplayDefectOverlays="{Binding CellReplayOverlays}"
    DefectInfos="{Binding DefectInfos}"/>
```

| 프로퍼티 | 타입 | 방향 | 의미 |
|---|---|---|---|
| `MapInfo` | `GlassMapInfo?` | OneWay | 셀 전체 좌표·크기·이름 |
| `RotationAngle` | `int` | OneWay | PanelAngleDeg 기반 회전 (0/90/180/270) |
| `ZoomFactor` | `double` | OneWay | 배율 (1.0/2.0/5.0) |
| `ShowPartitionNameOverlay` | `bool` | OneWay | 셀 이름 오버레이 표시 |
| `SelectedCellId` | `int?` | 직접 할당 | 선택된 셀 강조 표시 |
| `InspectionCellStates` | `ObservableCollection<GlassMapInspectionCellState>` | OneWay | 실시간 셀 색상 |
| `ReplayDefectOverlays` | `ObservableCollection<GlassMapReplayDefectOverlay>` | OneWay | 불량 위치 오버레이 |

---

### 셀 색상 의미

| 색상 | `GlassInspectionCellVisualStatus` | 발생 시점 |
|---|---|---|
| 회색 | `Pending` | 검사 대기 |
| 노란색 | `Inspecting` | PatternActivated 이벤트 수신 |
| 보라색 | `Queued` | EndJob ACK 완료, worker 검사 대기 중 |
| 초록색 | `Completed` (OK) | Completed 이벤트 + 불량 없음 |
| 빨간색 | `Completed` (NG) | Completed 이벤트 + 불량 있음 |
| 어두운 빨강 | `Failed` | 에러 발생 |

> **⚠️ 주의**: `Queued` (보라색)는 Accept 상태가 아니라 EndJob 이후 worker 검사 대기 상태다.
> 코드 주석에 명시: `// Note: "Queued" here means the job is queued in the IP inspector worker`

---

### Inspection State 탭 바인딩

```
[전체 셀]          GlassReplayTotalCells
[완료 셀]          GlassReplayCompletedCells
[총 불량]          GlassReplayTotalDefects
[불량 셀]          GlassReplayDefectCellCount
진행률: {0:F1}%    GlassReplayProgressPercent   ← CompletedCells / TotalCells × 100
현재 Row: {0}      GlassReplayCurrentRow
현재 Step: {0}     GlassReplayCurrentStep
남은 셀: {0}       GlassReplayRemainingCells     ← Max(0, Total - Completed)
시작: {0}          GlassReplayStartedAtText
경과: {0}          GlassReplayElapsedText        ← DateTime.Now - StartedAt
양품 셀: {0}       GlassReplayGoodCellCount      ← Max(0, Completed - DefectCellCount)
활성 IP: {0}       GlassReplayLaneSummaries.Count

Lane DataGrid:
  IP   = LaneNo
  상태  = Status
  현재 셀 = CurrentCellName
  마지막 셀 = LastCellName
  완료  = CompletedCells
  불량  = TotalDefects
```

---

### 불량 목록 DataGrid 바인딩

```xml
ItemsSource="{Binding CellReplayDefects}"
SelectedItem="{Binding SelectedCellReplayDefect}"
VirtualizingPanel.IsVirtualizing="True"
VirtualizingPanel.VirtualizationMode="Recycling"
```

| 컬럼 | 바인딩 경로 | 의미 |
|---|---|---|
| `#` | `Order` | 불량 순번 (Score 내림차순 정렬) |
| `Code` | `Code` | 불량 코드 |
| `Grade` | `Grade` | 불량 등급 (A/B/C) |
| `Score` | `Score` (F2) | 불량 점수 |
| `P` | `PatternIndex` | 패턴 인덱스 |
| `PT` | `PointIndex` | 포인트 인덱스 |
| `Shot` | `ShotName` | 촬영 Shot 이름 |
| `Desc` | `Message` | 불량 설명 |

> **가상화**: `EnableRowVirtualization=True` + `Recycling` 모드로 대량 불량에서도 성능 저하 없음.

---

### 미구현 항목 (주의)

```xml
<!-- LOT ID TextBox — 바인딩 없음 (입력해도 저장 안 됨) -->
<TextBox Width="120" Height="25"/>

<!-- SET UP 버튼 — Command 없음 (현재 미구현) -->
<Button Content="SET UP" Background="Violet" Margin="2" FontWeight="Bold" FontSize="14"/>
```

---

## 4. MainWindow.xaml.cs — 클래스 문서

### 클래스 개요

```csharp
public partial class MainWindow : Window
```

- **목적**: View 레이어. UI 이벤트 처리, 창 생명주기 관리, 다이얼로그 표시.
- **ViewModel과의 관계**: `DataContext = _viewModel`로 바인딩. 콜백 주입으로 ViewModel이 WPF 의존성 없음.

---

### 필드

| 필드 | 타입 | 목적 |
|---|---|---|
| `_log` | `RatelLogger` | 창 전용 로거 (Source = "MainWindow") |
| `_viewModel` | `MainWindowViewModel` | DataContext. 생성자에서 콜백 주입 후 생성. |
| `_windowProcess` | `WindowProcessStateMachine` | 창 생명주기 상태 머신 |
| `_glassStoppingWindow` | `GlassInspectionStoppingWindow?` | STOP 중 팝업 (싱글 인스턴스) |
| `_alarmManagerWindow` | `AlarmManagerWindow?` | 알람 관리 창 (싱글 인스턴스) |

---

### WindowProcessStateMachine

```
TrySetInitializing()  ← 생성자 시작
SetReady()            ← Loaded 이벤트
TryEnterClosing()     ← Closing 이벤트 (중복 닫기 방지)
SetClosed()           ← Closed 이벤트
```

**목적**: 초기화 전 접근, 이중 닫기, Closing 중 이벤트 재진입을 방지.

---

### 창 열기 메서드

#### `OpenGlassMapDesignWindow()` — `void`

```
입력: 없음
출력: 없음
부작용: GlassMapDesignWindow를 ShowDialog() 후 UpdateGlassMapViewportAsync() 호출
```

#### `OpenRecipeWindow()` — `void`

```
입력: 없음
출력: 없음
부작용: RecipeWindow를 ShowDialog() 후 UpdateGlassMapViewportAsync() 호출
```

> 레시피가 변경되었을 수 있으므로 닫힌 후 GlassMap을 항상 갱신한다.

#### `OpenAlarmManagerWindow()` — `void`

```
입력: 없음
출력: 없음
부작용: 싱글 인스턴스 관리
  - _alarmManagerWindow == null 또는 !IsLoaded → 새로 생성 후 Show()
  - IsLoaded && !IsVisible → Show()
  - IsLoaded && IsVisible → Activate() (포커스만 이동)
```

---

### 핵심 이벤트 핸들러

#### `ViewModel_PropertyChanged` — `void`

```
입력: PropertyChangedEventArgs (PropertyName)
출력: 없음
```

```csharp
// 감시 대상 프로퍼티별 처리
if (ZoomFactor || MapInfo)        → UpdateGlassMapViewportAsync()
if (SelectedCellId)               → glassMap.SelectedCellId = _viewModel.SelectedCellId
if (IsGlassReplayStopping)        → UpdateGlassStoppingWindow()
```

#### `GlassMap_CellClicked` — `void`

```
입력: GlassMapCellClickedEventArgs (Cell: RoiInfo)
출력: 없음
부작용: ViewModel에 셀 선택 알림 + 성능 측정 (10ms 기준 경고 로그)
```

```csharp
// ⚠️ 성능 임계값 = 10ms
var stopwatch = Stopwatch.StartNew();
_viewModel.NotifyManualReplayCellSelection(e.Cell.Id);
glassMap.SelectedCellId = e.Cell.Id;
stopwatch.Stop();
if (stopwatch.ElapsedMilliseconds >= 10)
{
    _log.Info("Perf", $"GlassMap cell click handled in {elapsed} ms ...");
}
```

---

### UpdateGlassMapViewport() — 줌 모드 전환

```
입력: 없음 (내부적으로 glassMapScroll과 _viewModel.ZoomFactor 참조)
출력: 없음
호출 경로: UpdateGlassMapViewportAsync() → Dispatcher.BeginInvoke(Loaded 우선순위)
```

```csharp
double zoom = _viewModel.ZoomFactor;

if (zoom <= 1.0)
{
    // Stretch 모드: GlassMap이 ScrollViewer를 꽉 채움
    glassMap.Width = double.NaN;                        // 크기 제한 없음 (Stretch)
    glassMap.Height = double.NaN;
    glassMap.HorizontalAlignment = HorizontalAlignment.Stretch;
    glassMap.VerticalAlignment = VerticalAlignment.Stretch;
    glassMapScroll.HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled;  // 스크롤 비활성
    glassMapScroll.ScrollToHorizontalOffset(0);         // 스크롤 위치 초기화
    glassMapScroll.ScrollToVerticalOffset(0);
}
else
{
    // 고정 크기 모드: 스크롤바 활성
    glassMap.Width = baseWidth * zoom;                  // ViewportWidth × zoom
    glassMap.Height = baseHeight * zoom;
    glassMap.HorizontalAlignment = HorizontalAlignment.Left;
    glassMap.VerticalAlignment = VerticalAlignment.Top;
    glassMapScroll.HorizontalScrollBarVisibility = ScrollBarVisibility.Auto;
}
```

> **가정**: `baseWidth`는 `ViewportWidth`가 우선. 0이면 `ActualWidth` 폴백.
> **제한**: Dispatcher.BeginInvoke를 사용하므로 호출 즉시가 아닌 UI 큐에 등록된다.

---

### 다이얼로그 메서드

#### `ShowGlassInspectionRunDialog()` — `GlassInspectionRunOptions?`

```
입력: 없음
출력: 사용자가 OK 클릭 시 GlassInspectionRunOptions, 취소 시 null
```

**초기값 결정 로직**:

```csharp
// Vars.Variables에서 마지막으로 사용한 값을 복원
CellIntervalSeconds = Vars.Variables?.GlassInspectCellIntervalSeconds >= 0
    ? Vars.Variables.GlassInspectCellIntervalSeconds
    : 2.0;   // 기본값 2.0초

// UsePgSimulator 기본값 = true (실장비에 올릴 때 반드시 false로 변경!)
UsePgSimulator = Vars.Variables?.GlassInspectUsePgSimulator != false;
```

> **⚠️ 함정**: `UsePgSimulator`의 기본값이 `true`다.
> `Variables.yaml`에 명시적으로 `false`가 저장되지 않으면 PG 시뮬레이터 모드로 실행된다.

---

### GlassInspectionStoppingWindow 관리

```csharp
// STOP 버튼 → IsGlassReplayStopping = true → ViewModel_PropertyChanged → UpdateGlassStoppingWindow()
private void UpdateGlassStoppingWindow()
{
    if (_viewModel.IsGlassReplayStopping)
    {
        // 창이 없거나 닫혔으면 새로 생성
        if (_glassStoppingWindow == null || !_glassStoppingWindow.IsLoaded)
        {
            _glassStoppingWindow = new GlassInspectionStoppingWindow { Owner = this };
            _glassStoppingWindow.CancelRequested += GlassStoppingWindow_CancelRequested;  // 취소 클릭
            _glassStoppingWindow.Show();
        }
        return;
    }
    CloseGlassStoppingWindow();  // IsGlassReplayStopping = false → 창 닫기
}

// 취소 클릭 → CancelStopGlassReplayCommand 실행
private void GlassStoppingWindow_CancelRequested()
{
    if (_viewModel.CancelStopGlassReplayCommand.CanExecute(null))
    {
        _viewModel.CancelStopGlassReplayCommand.Execute(null);
    }
}
```

---

## 5. MainWindowViewModel — 클래스 문서

### 5-1. 생성자 및 의존성

```csharp
public MainWindowViewModel(
    Action? openGlassMapDesign = null,
    Action? openRecipe = null,
    Action? openConfig = null,
    Action? openGlassSize = null,
    Action? openFlowTest = null,
    Action? openEecP725R2LightTest = null,
    Action? openCa410Test = null,
    Action? openAlarmManager = null,
    Action? openConsoleApiTest = null,
    Action? openControlApiHostTest = null,
    Func<string?>? showOpenInspectCellFolderDialog = null,
    Func<string?>? showOpenSavedGlassDefectFolderDialog = null,
    Func<GlassInspectionRunOptions?>? showGlassInspectionRunDialog = null,
    Func<string?>? showOpenRecipeFileDialog = null,
    IRecipeStore? recipeStore = null,
    IGlassSizeStore? glassSizeStore = null)
```

**생성자 실행 순서**:

1. 콜백 전부 `?? 빈 구현`으로 null 안전 처리
2. `ZoomOptions` 초기화 (X1, X2, X5)
3. `CellOriginOptions` 초기화 (enum 전체)
4. `GradeItems` 초기화 (G1~G5 + ELA_Repeat)
5. 모든 `RelayCommand` / `AsyncRelayCommand` 생성
6. IP 연결 이벤트 구독 + `MonitorIpConnectionAsync` Task.Run 시작
7. Control 이벤트 구독 + `MonitorControlConnectionAsync` Task.Run 시작
8. `_alarmManager.PropertyChanged` 구독
9. `GenerateGlassMap()` 실행

---

### 주요 내부 필드

| 필드 | 타입 | 목적 |
|---|---|---|
| `_cellReplayStateByCellId` | `Dictionary<int, CellReplayCellState>` | 셀 ID → 검사 결과 캐시 |
| `_glassReplayCts` | `CancellationTokenSource?` | 현재 검사 실행 취소 토큰 |
| `_ipMonitorCts` | `CancellationTokenSource` | IP 모니터 루프 취소 토큰 (앱 종료 시) |
| `_controlMonitorCts` | `CancellationTokenSource` | Control 모니터 루프 취소 토큰 |
| `_glassReplayStopRequested` | `bool` | 협조적 중단 플래그 (CT와 별도) |
| `_lastInspectedCellId` | `int?` | AutoShowLatestInspectedCell 추적용 |
| `_suppressManualSelectionTracking` | `bool` | 코드에서 셀 선택 시 AutoFollow 억제 |
| `_alarmOccurrenceCountByKey` | `Dictionary<string, int>` | 알람 중복 발생 카운터 |
| `_suppressedAlarmLogKeys` | `HashSet<string>` | 동일 알람 반복 로그 억제 |

---

### 5-2. 주요 프로퍼티

#### `CurrentOperationState` — `ConsoleOperationState`

```csharp
// 우선순위 순서로 상태 결정
public ConsoleOperationState CurrentOperationState
{
    get
    {
        if (_alarmManager.HasActiveHeavyAlarm)   return AlarmStop;   // Heavy 알람 최우선
        if (IsGlassReplayRunning && IsAutoRunEnabled) return AutoRun;
        if (IsGlassReplayRunning)                return Inspect;
        if (IsAutoRunEnabled)                    return AutoRun;
        return Idle;
    }
}
```

**알람 정책**: `AlarmPolicyCatalog`이 `ConsoleOperationState`를 보고 알람 발생 여부를 결정.
Heavy 알람 발생 → `AlarmStop` → 알람 정책에 의해 추가 알람 억제.

---

#### `SelectedCellReplayDefect` — `CellReplayDefectRow?`

```csharp
set
{
    if (SetProperty(ref _selectedCellReplayDefect, value))
    {
        // 사용자가 직접 불량을 선택하면 자동 팔로우 해제
        if (!_suppressManualSelectionTracking && value != null)
        {
            AutoShowLatestInspectedCell = false;
        }

        // 이미지 로드 + 성능 측정 (임계 20ms)
        var stopwatch = Stopwatch.StartNew();
        SelectedDefectCropImage = LoadBitmapSource(value?.CropImagePath)
            ?? LoadBitmapSource(value?.CropImageBytes);    // 경로 없으면 바이트 배열 폴백
        SelectedMappingImage = LoadBitmapSource(value?.MappingImagePath);
        stopwatch.Stop();
        if (stopwatch.ElapsedMilliseconds >= 20)
        {
            _log.Info("Perf", $"Selected defect image load in {elapsed} ms ...");
        }
    }
}
```

> **가정**: `CropImagePath`가 존재하면 파일에서 로드. 없으면 `CropImageBytes`(메모리)에서 로드.
> 실시간 검사 결과는 바이트 배열로, 폴더 리플레이는 파일 경로로 전달된다.

---

#### `CurrentRecipeName` — `string`

```csharp
// 우선순위 순서로 이름 결정
get
{
    // 1순위: IpRecipe.Descriptor.RecipeName
    // 2순위: IpRecipe.Descriptor.RecipeId
    // 3순위: 파일 경로에서 파일명 추출
    // 4순위: 빈 문자열
}
```

---

### 5-3. 커맨드 목록

| 커맨드 | 타입 | CanExecute 조건 | 실행 내용 |
|---|---|---|---|
| `InspectGlassReplayCommand` | `AsyncRelayCommand` | `!IsGlassReplayRunning && MapInfo.CellInfo.Any(Use)` | Glass 검사 실행 |
| `StopGlassReplayCommand` | `RelayCommand` | `IsGlassReplayRunning && !stopRequested` | 중단 플래그 세팅 |
| `CancelStopGlassReplayCommand` | `RelayCommand` | `IsGlassReplayRunning && stopRequested` | 중단 취소 |
| `InspectCellReplayCommand` | `RelayCommand` | `SelectedCellId.HasValue` | 단일 셀 결과 폴더 로드 |
| `LoadSavedGlassDefectFolderCommand` | `RelayCommand` | 항상 | 저장된 Glass 결과 세션 로드 |
| `ClearInspectCellReplayCommand` | `RelayCommand` | `cellReplayState 존재` | 선택 셀 또는 전체 결과 초기화 |
| `LoadRecipeCommand` | `RelayCommand` | 항상 | 파일 선택 → 레시피 교체 + IP 동기화 |
| `OpenGlassMapDesignCommand` | `RelayCommand` | 항상 | 콜백 호출 |
| `OpenRecipeCommand` | `RelayCommand` | 항상 | 콜백 호출 + GlassMap 갱신 |
| `OpenAlarmManagerCommand` | `RelayCommand` | 항상 | 콜백 호출 |
| `RedrawCommand` | `RelayCommand` | 항상 | GenerateGlassMap() |
| `OpenFlowTestCommand` | `RelayCommand` | 항상 | 콜백 호출 |
| `OpenEecP725R2LightTestCommand` | `RelayCommand` | 항상 | 콜백 호출 |
| `OpenCa410TestCommand` | `RelayCommand` | 항상 | 콜백 호출 |
| `OpenConsoleApiTestCommand` | `RelayCommand` | 항상 | 콜백 호출 |
| `OpenControlApiHostTestCommand` | `RelayCommand` | 항상 | 콜백 호출 |

---

### 5-4. 핵심 메서드 상세

#### `InitializeAsync()` — `Task`

```
입력: 없음
출력: Task
부작용:
  - Vars.Variables.LastRecipeFilePath에서 마지막 레시피 복원
  - GenerateGlassMap() 재실행
  - TrySyncCurrentRecipeToConnectedIpsAsync() 실행
  - Checkpoint가 있으면 Resume 여부 물어봄
```

---

#### `GenerateGlassMap()` — `void`

```
입력: 없음
출력: 없음
부작용: MapInfo, RotationAngle, CurrentRecipeName 갱신
```

```csharp
// 분기 1: 레시피가 있는 경우
if (recipe != null)
{
    var glassSizeResult = RecipeService.LoadGlassSizeForRecipe(recipe, _glassSizeStore);
    RotationAngle = RecipeService.GetEffectivePanelAngleDeg(recipe, glassSizeResult.Model);
    MapInfo = RecipeService.BuildGlassMapInfoFromRecipe(recipe, glassSize, cutMarks);
    return;
}

// 분기 2: 레시피 없음 → GlassMapDesign에서 직접 생성
var coordinateModels = LoadCoordinateModelsFromDesign();
MapInfo = new GlassMapInfo
{
    GlassSize = glassSize,
    CellInfo = GlassInfoHelper.MakeCells(coordinateModels)
};
```

> **가정**: 레시피가 없을 때는 `GlassMapDesign`(설계 원본)으로 대체 렌더링.
> 이 상태에서는 IP 분배(IpNo) 정보가 없어 검사 실행이 불가능하다.

---

#### `LoadRecipe()` — `void`

```
입력: 없음 (내부적으로 _showOpenRecipeFileDialog 콜백 호출)
출력: 없음
부작용:
  1. RecipeFolderBrowserWindow 다이얼로그 표시
  2. RecipeStore.Open(recipePath) → Vars.RecipeStore 교체
  3. LastRecipeFilePath 저장
  4. GenerateGlassMap()
  5. TrySyncCurrentRecipeToConnectedIpsAsync() 비동기 실행 (fire-and-forget)
오류 처리:
  - 로드 실패 시 CommonErrorMessageBox.Show()
```

---

#### `MonitorIpConnectionAsync()` — `Task` (백그라운드)

```
입력: CancellationToken
출력: Task (종료되지 않는 루프)
목적: 3초 주기로 IP 연결 상태 확인 및 자동 재연결
```

```csharp
while (!cancellationToken.IsCancellationRequested)
{
    foreach (ULedIpConnection connection in Vars.IpRuntimes.Connections)
    {
        if (!connection.Enabled) continue;

        if (!connection.IsConnected)
        {
            // 연결 시도
            await connection.ConnectAsync(cancellationToken);
            // 연결 성공 → 레시피 동기화
            await TrySyncCurrentRecipeToConnectionAsync(connection, cancellationToken);
        }
        else
        {
            // 이미 연결됨 → 상태 폴링
            await connection.RequestRuntimeStatusAsync(cancellationToken);
        }
    }

    RaiseIpStateChanged();  // UI 바인딩 갱신
    await Task.Delay(3000, cancellationToken);
}
```

> **제한**: 연결 중 예외는 catch 후 로그만 남기고 루프를 계속한다.
> IP가 영구 다운이어도 루프가 멈추지 않으며, CancellationToken으로만 종료된다.

---

#### `MonitorControlConnectionAsync()` — `Task` (백그라운드)

```
입력: CancellationToken
출력: Task (종료되지 않는 루프)
목적: 3초 주기 Control 연결 유지 + EventNotification Push 처리
```

```csharp
while (!cancellationToken.IsCancellationRequested)
{
    if (Vars.ControlRuntime != null)
    {
        Vars.ControlRuntime.ApplyConfig(Vars.EMRConfig.Control);  // 최신 설정 반영
        await Vars.ControlRuntime.EnsureConnectedAsync(cancellationToken);
    }
    await Task.Delay(3000, cancellationToken);
}

// Push 방식 (루프와 별개)
void OnControlRuntimeGlobalEvent(object? sender, ControlEventArgs e)
{
    SyncControlAlarmStates(e);  // 알람 상태 동기화
}
```

> **IP vs Control 차이**:
> IP는 Polling 전용. Control은 3초 폴링(연결 유지) + EventNotification Push(알람·상태 실시간).

---

#### `TrySyncCurrentRecipeToConnectedIpsAsync()` — `Task`

```
입력: string caller (로그용)
출력: Task
목적: 현재 로드된 레시피를 연결된 모든 IP에 업로드·활성화
부작용: 실패 시 알람 발생 (IpUploadFail)
```

---

#### `LoadCellInspectionReplay()` — `void`

```
입력: string folderPath
출력: 없음
부작용:
  1. CellInspectionReplayLoader.LoadFromFolder(folderPath) → session
  2. BuildDefectRows(session) → 불량 DataGrid 행
  3. BuildCellReplayState(session) → _cellReplayStateByCellId[SelectedCellId]
  4. RebuildGlassReplayOverlays() → CellReplayOverlays 갱신
  5. RebuildDefectDistributionStats() → Grade/Code 집계
  6. SelectReplayCell(SelectedCellId.Value) → 화면 이동
성능 로그: 각 단계별 경과 시간 (10ms 기준)
오류 처리: SelectedCellId 없으면 InvalidOperationException
```

---

#### `NotifyManualReplayCellSelection()` — `void`

```
입력: int cellId
출력: 없음
부작용:
  - _suppressManualSelectionTracking = true (SelectedCellId setter에서 AutoFollow 억제)
  - SelectedCellId = cellId
  - _suppressManualSelectionTracking = false
```

> **⚠️ 중요 설계**: `_suppressManualSelectionTracking`이 없으면 코드에서 셀을 선택할 때도
> `SelectedCellReplayDefect` setter의 `AutoShowLatestInspectedCell = false` 가 실행된다.
> 이를 방지하기 위한 재진입 방지 패턴.

---

## 6. 핵심 알고리즘 상세

### 6-1. Glass 검사 실행 루프

#### 진입점: `InspectGlassReplayAsync()`

```
① Checkpoint 로드 → Resume / New / Cancel 결정
② options 결정 (Resume: checkpoint.Options, New: 다이얼로그)
③ _glassReplayCts 재생성
④ SetGlassReplayRunningAsync(true)
⑤ RunGlassInspectionReplayAsync(options, ct, checkpoint) 실행
⑥ 예외별 알람 분류:
   - IsLikelySaveFailure(ex) → ConSaveFail
   - IsLikelyControlFailure(ex) → CtlDown
   - 그 외 → ConRunException
⑦ finally: 상태 초기화, CTS Dispose, Command CanExecute 재평가
```

#### 본체: `RunGlassInspectionReplayAsync()`

```
① GetGlassReplayTargetCells() → 검사 대상 셀 목록 (Use=true 필터)
② BuildGlassReplayRowPlans() → Row/Step/Batch 계획 생성
③ EnsureControlReadyForGlassInspectionAsync() → Control 준비 확인
④ Provider 선택:
   - Folder/CurrentBuffer → IpLoadedBufferCellInspectionDataProvider
   - Replay → FolderCellInspectionDataProvider
⑤ GlassInspectionOutputWriter 생성 (결과 저장 담당)
⑥ RestoreSavedCellsFromCheckpoint() → Resume 시 이전 결과 복원
⑦ UI 초기화 (Dispatcher.InvokeAsync)
⑧ 초기 Checkpoint 저장
⑨ Row 루프:
   for each rowPlan (LineIndex 순):
     BeginRowAsync (Contact)
     for each stepPlan (StepIndex 순):
       DelayUntilNextStepStartAsync (CellIntervalSeconds)
       CaptureBatchStartCoordinator × 4 생성
       pendingAssignments.Select(Task.Run(ProcessGlassReplayAssignmentAsync)) 실행
       WhenAll(endJobAckTasks) → 배치 EndJob 전부 완료 대기
       _glassReplayStopRequested → Checkpoint 저장 후 break
     EndRowAsync (Uncontact + LineDelaySeconds)
⑩ WhenAll(inFlightTasks) → 미완료 셀 전부 대기
⑪ Stopped → 반환 / Completed → writer.SaveGlassResult() + DeleteCheckpoint()
```

---

### 6-2. 셀 1개 라이프사이클 — `ProcessGlassReplayAssignmentAsync()`

```
입력:
  - assignment: GlassReplayAssignment (CellId, LaneNo, LineIndex, StepIndex)
  - provider: ICellInspectionDataProvider
  - laneDispatchSlot: SemaphoreSlim (Lane당 1개)
  - laneBufferingSlot: SemaphoreSlim (Lane당 1개)
  - captureCoordinator: CaptureBatchStartCoordinator
  - acceptCoordinator: CaptureBatchStartCoordinator
  - bufferingCoordinator: CaptureBatchStartCoordinator
  - endCoordinator: CaptureBatchStartCoordinator
  - endJobAckTcs: TaskCompletionSource<bool>
  - onCompleted: Action<GlassReplayAssignment>

7단계 실행:
① laneDispatchSlot.WaitAsync     ← Lane 진입 허가
   captureCoordinator.SignalReadyAndWait ← 배치 전체 동시 출발
② StartCellJobAsync              ← IP에 StartJob 전송
   WaitForProviderEventAsync(acceptedTcs, failedTcs) ← Accepted 이벤트 대기
③ laneQueue.Enqueue(assignment)
   acceptCoordinator.SignalReadyAndWait  ← Accept 배치 완료 대기
   laneDispatchSlot.Release      ← 다음 셀 StartJob 가능
④ laneBufferingSlot.WaitAsync    ← Buffering 순서 제어
   bufferingCoordinator.SignalReadyAndWait
⑤ BufferCellJobAsync             ← Pattern × Point StartStep 수행
   (PatternActivated → 셀 색상: 노란색)
⑥ endCoordinator.SignalReadyAndWait
   EndCellJobAsync               ← EndJob 전송
   laneBufferingSlot.Release
   endJobAckTcs.TrySetResult(true)  ← 메인 루프 다음 Step 허용
   → 셀 색상: Queued (보라색)
⑦ WaitForProviderEventAsync(completedTcs, failedTcs) ← worker 검사 완료 대기
   writer.SaveCell() → 파일 저장
   ApplyCellInspectionReplayState() → _cellReplayStateByCellId 갱신
   → 셀 색상: OK 또는 NG

예외별 알람:
  currentStage = "StartJob" → IpStartJobFail
  currentStage = "StartStep" → IpStartStepFail (Control 실패면 CtlDown)
  currentStage = "EndJob"   → IpEndJobFail
  currentStage = "SaveCell" → ConSaveFail

finally:
  provider.JobEvent -= Provider_JobEvent (이벤트 누수 방지)
  bufferingSlotAcquired → laneBufferingSlot.Release
  dispatchSlotAcquired && !dispatchAccepted → laneDispatchSlot.Release
```

---

### 6-3. BuildGlassReplayRowPlans() — 배치 계획 알고리즘

```
입력: List<GlassReplayCellPlan> (XIndex/YIndex 기준 정렬), assignmentCount, laneNos
출력: List<GlassReplayRowPlan>
```

```
1. 셀을 XIndex(행) 기준으로 GroupBy
2. 각 행 안에서:
   a. laneNo별로 YIndex 정렬 분리
   b. maxLaneLength = 가장 긴 Lane의 셀 수
   c. for i in [0, maxLaneLength):
      - stepPlan 생성 (StepIndex = i+1)
      - 각 Lane에서 i번째 셀을 stepPlan에 추가

예: 2 Lane, 행당 [6열, 6열]
  Lane 1: [c1, c3, c5, c7, c9, c11]
  Lane 2: [c2, c4, c6, c8, c10, c12]

  → Step 1: [c1, c2]   ← IP1의 1번째 + IP2의 1번째
  → Step 2: [c3, c4]
  → Step 3: [c5, c6]
  ...

이 구조로 IP1과 IP2가 항상 같은 행 같은 시점에 촬영.
```

---

### 6-4. WaitForProviderEventAsync() — 이벤트→Task 패턴

```csharp
/// <summary>
/// provider의 성공/실패 이벤트 중 먼저 도착한 결과를 기다린다.
/// 취소가 먼저 도착하면 OperationCanceledException을 던진다.
/// </summary>
private static async Task<CellInspectionJobEventArgs> WaitForProviderEventAsync(
    Task<CellInspectionJobEventArgs> successTask,
    Task<CellInspectionJobEventArgs> failedTask,
    CancellationToken cancellationToken)
{
    // 성공/실패/취소 중 먼저 오는 것을 선택
    Task completed = await Task.WhenAny(
        successTask,
        failedTask,
        Task.Delay(Timeout.Infinite, cancellationToken));

    if (completed == successTask) return await successTask;
    if (completed == failedTask)
    {
        // 실패 이벤트를 예외로 변환
        CellInspectionJobEventArgs failed = await failedTask;
        throw new InvalidOperationException(failed.Message);
    }

    // CT가 먼저 → 취소 예외
    cancellationToken.ThrowIfCancellationRequested();
    throw new OperationCanceledException(cancellationToken);
}
```

> **설계 의도**: IP는 결과를 이벤트로 push한다. 이 함수는 이벤트를 `await` 가능한 Task로 변환하여
> 순차적 async/await 흐름 안에서 이벤트 기반 비동기를 처리한다.
> `Task.Delay(Timeout.Infinite, ct)`는 CancellationToken이 발생하면 즉시 완료되는 무한 대기 Task다.

---

### 6-5. UpdateGlassMapViewport() — 줌 모드 전환 알고리즘

```
조건: zoom <= 1.0
  GlassMap.Width = NaN (WPF: 제한 없음 → Stretch)
  GlassMap.HorizontalAlignment = Stretch
  ScrollBarVisibility = Disabled
  ScrollToOffset(0) (스크롤 초기화)

조건: zoom > 1.0
  GlassMap.Width = ViewportWidth × zoom
  GlassMap.HorizontalAlignment = Left
  ScrollBarVisibility = Auto

호출 경로 (비동기):
  UpdateGlassMapViewportAsync()
    → Dispatcher.BeginInvoke(UpdateGlassMapViewport, DispatcherPriority.Loaded)

트리거:
  - SizeChanged 이벤트
  - ZoomFactor 변경 (PropertyChanged)
  - MapInfo 변경 (PropertyChanged, 즉 레시피 교체)
  - GlassMapDesignWindow / RecipeWindow 닫힌 직후
```

---

## 7. 가정 및 제한 사항

### 가정

| # | 가정 | 근거 |
|---|---|---|
| G1 | IP는 최대 2대 (IP1, IP2) | `laneNos`가 IpNo 기준으로 결정되며, 기본 EMRConfig에 2개 Endpoint |
| G2 | 모든 셀은 Use=true가 기본 | `GlassInfoHelper.MakeCell()`에서 `Use = true`로 생성 |
| G3 | Checkpoint는 1개만 존재 | `_glassInspectionCheckpointStore`가 단일 파일 기반 |
| G4 | Recipe가 없으면 GlassMapDesign으로 대체 렌더링 | `GenerateGlassMap()` 분기 |
| G5 | CropImagePath 없으면 CropImageBytes 사용 | 실시간 검사는 바이트, 폴더 리플레이는 파일 경로 |

### 제한 사항

| # | 제한 | 영향 |
|---|---|---|
| L1 | `Camera` Source 미구현 | `GlassInspectionRunSource.Camera` 선택 시 예외 발생 |
| L2 | `SET UP` 버튼 미구현 | 클릭해도 아무 동작 없음 |
| L3 | LOT ID TextBox 바인딩 없음 | 입력해도 저장되지 않음 |
| L4 | ViewModel 내 `Application.Current.Dispatcher` 직접 사용 | MVVM 완전 분리 미달. 단위 테스트 시 UI 스레드 필요 |
| L5 | `UsePgSimulator` 기본값 = `true` | 실장비 적용 시 Variables.yaml에 false 명시 필수 |
| L6 | IP 모니터 루프는 CancellationToken으로만 종료 | 앱 종료 시 `Shutdown()`에서 `_ipMonitorCts.Cancel()` 필요 |
| L7 | `StartJob → StartStep 반복 → EndJob` 외 IP API 직접 호출 금지 | Provider 인터페이스 주석에 명시 |
| L8 | CELL_Y=15, BLOCK_COUNT_Y=2 실제 생성 셀 수 = 15 | 코드 주석의 "14개"와 불일치. 실제는 [8,7] 분배 → 15개 |

---

## 8. 다음 분석 대상

아래 순서로 분석을 이어가면 전체 Console 코드가 연결된다.

### P1 — 즉시 (검사 핵심 루프 완성)

| 파일 | 이유 |
|---|---|
| `Services/InspectionReplay/GlassInspectionOutputWriter.cs` | `writer.SaveCell()` / `writer.SaveGlassResult()` 의 실제 저장 형식과 Checkpoint 연동 전체 |
| `Services/InspectionReplay/GlassInspectionExecutionCheckpointStore.cs` | Resume 흐름의 기준. `SessionFolderPath`, `CompletedCellIds`, `CurrentRow/Step` |
| `Services/Ip/ULedIpConnection.cs` | `StartJobAsync`, `EndJobAsync`, `WaitForPanelCompletedAsync` 실제 TCP 구현 |

### P2 — 레시피·GlassMap 연결

| 파일 | 이유 |
|---|---|
| `Recipes/ConsoleRecipeDocument.cs` | `ConsoleCellPlan`, `AlignPlan`, `ControlPlan` 필드 전체 구조 |
| `Services/RecipeService.cs` | `BuildGlassMapInfoFromRecipe`, `LoadGlassSizeForRecipe`, `GetEffectivePanelAngleDeg` |
| `Services/GlassInspectionStepPreparationService.cs` | `BeginRowAsync` / `EndRowAsync`에서 호출 — PG Contact·스테이지 이동 제어 |

### P3 — 연결·알람

| 파일 | 이유 |
|---|---|
| `Services/Control/ULedControlConnection.cs` | `EnsureConnectedAsync`, `GlobalControlEventReceived` 구현 |
| `Alarms/ConsoleAlarmManager.cs` | `RaiseAlarm`, `ClearAlarm`, `AlarmPolicyCatalog` 전체 |
| `Alarms/AlarmCatalog.cs` | `ConSaveFail`, `IpStartJobFail`, `CtlDown` 등 알람 정의 |

### P4 — GlassMap 렌더링

| 파일 | 이유 |
|---|---|
| `Controls/GlassMapControl.xaml.cs` | RoiInfo → Canvas 렌더링. InspectionCellStates 색상 결정 실제 로직 |
| `Models/GlassMapInspectionCellState.cs` | 셀 색상 열거형 전체 정의 |
| `Models/GlassMapReplayDefectOverlay.cs` | 불량 오버레이 좌표 정규화 방식 |

---

*이 문서는 코드 직접 분석 기반이며, 코드 변경 시 해당 섹션을 업데이트하세요.*
