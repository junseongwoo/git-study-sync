# uLedAoiConsole — MainWindow & MainWindowViewModel 완전 분석

> **프로젝트**: uLED(마이크로 LED) 점등 AOI(Automated Optical Inspection) 콘솔
> **분석 파일**: `MainWindow.xaml` / `MainWindow.xaml.cs` / `MainWindowViewModel.cs`
> **아키텍처**: WPF + MVVM (CommunityToolkit.Mvvm)
> **작성일**: 2025

---

## 목차

1. [코드의 핵심 목적과 주요 기능](#1-코드의-핵심-목적과-주요-기능)
2. [전체 아키텍처 구조](#2-전체-아키텍처-구조)
3. [UI 레이아웃 분석 (MainWindow.xaml)](#3-ui-레이아웃-분석-mainwindowxaml)
4. [MainWindow 코드-비하인드 분석](#4-mainwindow-코드-비하인드-분석)
5. [MainWindowViewModel 분석](#5-mainwindowviewmodel-분석)
6. [핵심 알고리즘 설명](#6-핵심-알고리즘-설명)
7. [데이터 모델 클래스 목록](#7-데이터-모델-클래스-목록)
8. [가정 및 제한 사항](#8-가정-및-제한-사항)
9. [다음으로 분석해야 할 코드](#9-다음으로-분석해야-할-코드)

---

## 1. 코드의 핵심 목적과 주요 기능

### 핵심 목적

이 프로그램은 **uLED(마이크로 LED) 패널 점등 검사 자동화 콘솔**이다.  
유리 기판(Glass) 위에 배치된 수십~수백 개의 마이크로 LED 셀(Cell)을 순차적으로 점등하고,  
각 셀의 이미지를 촬영·분석해 불량을 탐지하는 AOI 장비를 제어하는 운영 소프트웨어다.

### 주요 기능 요약

| 기능 카테고리             | 세부 내용                                   |
| ------------------- | --------------------------------------- |
| **글래스 맵 시각화**       | 유리 기판 위 셀 배치를 2D 맵으로 표시, 셀 클릭으로 선택      |
| **레시피 관리**          | 검사 조건 파일(레시피) 로드·동기화                    |
| **자동 검사(AUTORUN)**  | 전체 셀을 Row/Step/Batch 단위로 순차 검사          |
| **불량 결과 조회**        | 셀별 불량 목록, 조건 불량(점등불량), CA-410 측색 데이터 표시 |
| **IP 통신 모니터링**      | 다중 IP(Image Processor) 연결 상태 실시간 감시     |
| **Control 장비 연동**   | 이동/접촉(Contact) 제어 장비와의 연결 관리            |
| **알람 관리**           | IP·Control 이상 감지 시 알람 발생/해제             |
| **검사 이어하기(Resume)** | 프로그램 재시작 후 중단된 검사 복원                    |
| **결과 저장/로드**        | 검사 결과를 JSON 기반 세션 폴더에 저장, 이후 재로드        |

---

## 2. 전체 아키텍처 구조

```
┌─────────────────────────────────────────────┐
│              MainWindow.xaml                │  ← View (UI 정의)
│  GlassMapControl / DataGrid / LogViewer     │
└────────────────────┬────────────────────────┘
                     │ DataContext (MVVM Binding)
┌────────────────────▼────────────────────────┐
│         MainWindowViewModel.cs              │  ← ViewModel (상태·명령)
│  ObservableObject (CommunityToolkit.Mvvm)   │
└───────┬──────────────────────┬──────────────┘
        │                      │
┌───────▼──────┐    ┌──────────▼──────────────┐
│  IP Runtime  │    │   Control Runtime        │
│ (ULedIp)     │    │  (ULedControl)           │
│ 다중 연결 모니터│    │  이동/접촉 제어 장비      │
└──────────────┘    └─────────────────────────┘
        │
┌───────▼──────────────────────────────────────┐
│        GlassInspectionReplay 서비스           │
│  CellInspectionReplayLoader                  │
│  GlassInspectionOutputWriter                 │
│  ICellInspectionDataProvider                 │
│    ├─ FolderCellInspectionDataProvider       │  ← 폴더에서 재생
│    ├─ IpLoadedBufferCellInspectionDataProvider│  ← IP 버퍼에서 실행
│    └─ ControlOnlyCellInspectionDataProvider  │  ← Control 동작만
└──────────────────────────────────────────────┘
```

### MVVM 패턴 적용 방식

- **View → ViewModel**: `{Binding}` 으로 속성·명령 바인딩
- **ViewModel → View**: `INotifyPropertyChanged` (`ObservableObject` 상속)
- **View → ViewModel (UI 이벤트)**: `Command` 바인딩 또는 Code-behind에서 ViewModel 메서드 호출
- **창(Window) 열기**: ViewModel이 `Action` 콜백을 주입받아 호출 → View가 실제 창 생성

---

## 3. UI 레이아웃 분석 (MainWindow.xaml)

### 3-1. 전체 레이아웃 구조

```
Window (1920×1080, Maximized)
 └─ Grid
     ├─ Row 0: 상단 메뉴바 (DockPanel)
     │    ├─ 알람 버튼 (ActiveAlarmBrush 색상)
     │    ├─ IP 연결 상태 표시
     │    ├─ Control 연결 상태 표시
     │    ├─ Menu (Tool / Data / View / Test / ETC)
     │    └─ Zoom 선택 ComboBox
     │
     └─ Row 1: 메인 콘텐츠 (Grid 3열)
          ├─ Column 0: 좌측 — 글래스 맵 + 탭 패널
          │    ├─ ScrollViewer > GlassMapControl
          │    └─ TabControl
          │         ├─ Tab: Log (로그 뷰어)
          │         ├─ Tab: Inspection State (검사 진행 현황)
          │         ├─ Tab: Grade (등급별 불량 통계)
          │         └─ Tab: Code Top 10 (코드별 불량 통계)
          │
          ├─ Column 1: GridSplitter (6px 분할 드래그)
          │
          └─ Column 2: 우측 — 제어 패널 (800px)
               ├─ AUTORUN / INSPECT / STOP / SET UP 버튼
               ├─ 검사 상태 표시 (INSPECT / STOP 대형 배너)
               ├─ Recipe 정보 (이름, LOT ID, Glass ID)
               ├─ Condition Issue 목록 (점등 불량 DataGrid)
               ├─ CA-410 측색 목록 (DataGrid)
               ├─ Defect 목록 (DataGrid)
               └─ Defect 이미지 (Crop / Mapping Image)
```

### 3-2. 주요 바인딩 속성 목록

| UI 요소 | 바인딩 속성 | 설명 |
|---|---|---|
| 알람 버튼 색상 | `ActiveAlarmBrush` | Heavy=빨강, Light=주황, 정상=파랑 |
| 알람 버튼 텍스트 | `ActiveAlarmSummary` | 현재 알람 요약 텍스트 |
| IP 연결 배지 색상 | `IpConnectionBrush` | 연결=초록, 끊김=빨강 |
| Control 연결 배지 | `ControlConnectionBrush` | 연결=초록, 끊김=빨강 |
| 글래스 맵 | `MapInfo`, `ZoomFactor`, `RotationAngle` | 맵 데이터·줌·회전 |
| 검사 상태 배너 | `GlassInspectionStatusText`, `GlassInspectionStatusBrush` | INSPECT/STOP 표시 |
| 현재 레시피명 | `CurrentRecipeName` | 로드된 레시피 이름 |
| Condition 목록 | `CellReplayConditionIssues` | 점등 조건 불량 리스트 |
| CA-410 목록 | `CellReplayCa410Measurements` | 측색 데이터 리스트 |
| Defect 목록 | `CellReplayDefects` | 불량 리스트 |
| Crop 이미지 | `SelectedDefectCropImage` | 선택된 불량의 크롭 이미지 |
| Mapping 이미지 | `SelectedMappingImage` | 선택된 불량의 매핑 이미지 |

---

## 4. MainWindow 코드-비하인드 분석

### 4-1. 클래스 개요

```csharp
// 위치: uLedAoiConsole 네임스페이스
// 역할: View 계층 — UI 이벤트 처리 + 서브 창 관리
public partial class MainWindow : Window
```

**주요 필드:**

| 필드 | 타입 | 설명 |
|---|---|---|
| `_log` | `RatelLogger` | 윈도우 전용 로거 |
| `_viewModel` | `MainWindowViewModel` | 바인딩된 ViewModel |
| `_windowProcess` | `WindowProcessStateMachine` | 창 생명주기 상태 머신 |
| `_glassStoppingWindow` | `GlassInspectionStoppingWindow?` | 정지 진행 팝업 |
| `_alarmManagerWindow` | `AlarmManagerWindow?` | 알람 관리 창 |
| `_recipeWindow` | `RecipeWindow?` | 레시피 편집 창 |

---

### 4-2. 생성자 분석

```csharp
public MainWindow()
```

**실행 순서:**

```
1. _windowProcess.TrySetInitializing()   ← 상태: Initializing
2. InitializeComponent()                 ← XAML 요소 생성
3. LoggingHelper 설정
4. MainWindowViewModel 생성 (Action 콜백 16개 주입)
5. DataContext = _viewModel              ← 바인딩 시작
6. 이벤트 핸들러 등록
   - ViewModel.PropertyChanged
   - glassMap.CellClicked
   - Loaded (비동기 초기화)
   - SizeChanged
   - Closing
   - Closed
```

> **핵심 설계 결정**: ViewModel에 창 열기 Action을 주입하는 방식은  
> ViewModel이 WPF에 직접 의존하지 않도록 분리하기 위한 패턴이다.  
> 덕분에 ViewModel은 단위 테스트 가능한 순수 C# 클래스로 유지된다.

---

### 4-3. 주요 메서드

#### `UpdateGlassMapViewport()` / `UpdateGlassMapViewportAsync()`

```
목적: 줌 배율에 따라 GlassMapControl의 크기와 스크롤 동작을 조정
입력: ZoomFactor (ViewModel), ScrollViewer 뷰포트 크기
출력: glassMap.Width/Height 설정, 스크롤바 표시 여부 결정
```

**로직:**
- `ZoomFactor <= 1.0`: Stretch 모드 (스크롤바 숨김)
- `ZoomFactor > 1.0`: 픽셀 크기 고정 + 스크롤바 표시

```csharp
// 비동기 버전은 Dispatcher를 통해 UI 스레드에서 실행 보장
private void UpdateGlassMapViewportAsync()
{
    Dispatcher.BeginInvoke(UpdateGlassMapViewport, DispatcherPriority.Loaded);
}
```

---

#### `GlassMap_CellClicked()`

```
목적: 글래스 맵에서 셀 클릭 시 ViewModel에 선택 통보
입력: GlassMapCellClickedEventArgs (Cell.Id, Cell.Name)
출력: ViewModel.NotifyManualReplayCellSelection() 호출
      + 성능 로그 (10ms 이상 소요 시)
```

---

#### `ShowGlassInspectionRunDialog()`

```
목적: 글래스 검사 실행 옵션 다이얼로그 표시 후 결과 반환
입력: Vars.Variables (이전 설정값으로 기본값 세팅)
출력: GlassInspectionRunOptions? (취소 시 null)
```

기본값 로드 우선순위:
1. `Vars.Variables.LastGlass*` 계열 (마지막 실행값)
2. 코드 하드코딩 기본값 (CellIntervalSeconds=2.0, LineDelaySeconds=2.0)

---

#### 서브 창 관리 패턴

RecipeWindow, AlarmManagerWindow 등 재사용 창은 **싱글턴 패턴**으로 관리:

```csharp
// 이미 열려 있으면 포커스만 줌, 없으면 새로 생성
private void OpenRecipeWindow()
{
    if (_recipeWindow == null || !_recipeWindow.IsLoaded)
    {
        _recipeWindow = new RecipeWindow { Owner = this };
        _recipeWindow.Closed += RecipeWindow_Closed;
        _recipeWindow.Show();
        return;
    }
    if (_recipeWindow.WindowState == WindowState.Minimized)
        _recipeWindow.WindowState = WindowState.Normal;
    _recipeWindow.Activate();
}
```

GlassStoppingWindow는 `IsGlassReplayStopping` 속성 변화에 반응해 자동 표시/숨김된다.

---

#### `IsRecipeDirectoryOrChild()` (정적 메서드)

```
목적: 출력 폴더가 레시피 폴더 안에 포함되는지 검사 (실수 방지)
입력: folderPath (검사 대상 경로)
출력: true/false
제한: 경로 비교는 대소문자 무시(OrdinalIgnoreCase)
```

---

## 5. MainWindowViewModel 분석

### 5-1. 클래스 개요

```csharp
// 위치: uLedAoiConsole.ViewModels 네임스페이스
// 상속: ObservableObject (CommunityToolkit.Mvvm)
// 역할: 전체 애플리케이션 상태와 비즈니스 로직의 중심
public class MainWindowViewModel : ObservableObject
```

**중요 상수:**
```csharp
// 레시피 없을 때 기본 글래스 크기 (단위: 마이크로미터)
private static readonly DrawingSize DefaultGlassSize = new DrawingSize(470000, 370000);
// → 470mm × 370mm
```

---

### 5-2. 생성자 파라미터

```csharp
public MainWindowViewModel(
    Action? openGlassMapDesign,    // 글래스 맵 디자인 창 열기
    Action? openRecipe,            // 레시피 창 열기
    Action? openConfig,            // 설정 창 열기
    Action? openGlassSize,         // 글래스 크기 창 열기
    Action? openFlowTest,          // Flow 테스트 창
    Action? openEecP725R2LightTest,// 광원 테스트 창
    Action? openCa410Test,         // CA-410 테스트 창
    Action? openAlarmManager,      // 알람 관리 창
    Action? openAxisGlassCoordinate,// 축-유리 좌표 변환 창
    Action? openConsoleApiTest,    // API 테스트 창
    Action? openControlApiHostTest,// Control API 테스트 창
    Func<string?>? showOpenInspectCellFolderDialog,       // 셀 결과 폴더 선택 다이얼로그
    Func<string?>? showOpenSavedGlassDefectFolderDialog,  // 저장된 글래스 세션 폴더 선택
    Func<GlassInspectionRunOptions?>? showGlassInspectionRunDialog, // 검사 실행 옵션 다이얼로그
    Func<string?>? showOpenRecipeFileDialog,              // 레시피 파일 선택 다이얼로그
    IRecipeStore? recipeStore,     // 레시피 저장소 (테스트용 주입)
    IGlassSizeStore? glassSizeStore// 글래스 크기 저장소 (테스트용 주입)
)
```

> **가정**: 모든 Action/Func 파라미터는 null 허용이며, null 시 빈 람다로 대체된다.  
> 이는 테스트 환경에서 UI 없이 ViewModel만 생성 가능하게 한다.

---

### 5-3. 주요 속성 목록

#### 연결 상태 속성

| 속성명 | 타입 | 설명 |
|---|---|---|
| `IsIpConnected` | `bool` | 활성화된 IP 중 하나 이상 연결 여부 |
| `IpConnectionStateText` | `string` | "IP Connected" / "IP Disconnected" |
| `IpConnectionSummary` | `string` | IP별 상태 요약 ("IP1:Connected \| IP2:Disconnected") |
| `IpConnectionBrush` | `Brush` | 연결=ForestGreen, 끊김=IndianRed |
| `IsControlConnected` | `bool` | Control 장비 연결 여부 |
| `ControlConnectionSummary` | `string` | Control 연결 상세 정보 |

#### 검사 진행 상태 속성

| 속성명 | 타입 | 설명 |
|---|---|---|
| `IsGlassReplayRunning` | `bool` | 검사 실행 중 여부 |
| `IsGlassReplayStopping` | `bool` | 정지 요청 후 완료 대기 중 |
| `GlassReplayTotalCells` | `int` | 전체 검사 대상 셀 수 |
| `GlassReplayCompletedCells` | `int` | 완료된 셀 수 |
| `GlassReplayRemainingCells` | `int` | 남은 셀 수 (계산 속성) |
| `GlassReplayProgressPercent` | `double` | 진행률 (%) |
| `GlassReplayTotalDefects` | `int` | 누적 불량 수 |
| `GlassReplayDefectCellCount` | `int` | 불량 있는 셀 수 |
| `GlassReplayGoodCellCount` | `int` | 양품 셀 수 (계산 속성) |
| `GlassReplayCurrentRow` | `int` | 현재 처리 중인 Row |
| `GlassReplayCurrentStep` | `int` | 현재 처리 중인 Step |

#### 셀 선택 및 결과 속성

| 속성명 | 타입 | 설명 |
|---|---|---|
| `SelectedCellId` | `int?` | 현재 선택된 셀 ID |
| `SelectedCellName` | `string` | 현재 선택된 셀 이름 |
| `SelectedCellReplaySummary` | `string` | 선택 셀 결과 요약 텍스트 |
| `CellReplayDefects` | `ObservableCollection<CellReplayDefectRow>` | 불량 목록 |
| `CellReplayConditionIssues` | `ObservableCollection<CellReplayConditionIssueRow>` | 점등 불량 목록 |
| `CellReplayCa410Measurements` | `ObservableCollection<CellReplayCa410MeasurementRow>` | CA-410 측정값 |
| `SelectedDefectCropImage` | `BitmapSource?` | 불량 크롭 이미지 |
| `SelectedMappingImage` | `BitmapSource?` | 불량 매핑 이미지 |

#### 알람 속성

| 속성명 | 설명 |
|---|---|
| `ActiveAlarmSummary` | 알람 요약 텍스트 |
| `ActiveAlarmBrush` | Heavy=IndianRed, Light=DarkOrange, 없음=SteelBlue |
| `CurrentOperationState` | AlarmStop / AutoRun / Inspect / Idle |

---

### 5-4. 명령(Command) 목록

| 명령명 | 타입 | 설명 | 실행 조건 |
|---|---|---|---|
| `InspectGlassReplayCommand` | `IAsyncRelayCommand` | 글래스 검사 시작 | !IsRunning && 셀 존재 |
| `StopGlassReplayCommand` | `RelayCommand` | 검사 정지 요청 | IsRunning && !StopRequested |
| `CancelStopGlassReplayCommand` | `RelayCommand` | 정지 요청 취소 | IsRunning && StopRequested |
| `InspectCellReplayCommand` | `RelayCommand` | 단일 셀 결과 로드 | SelectedCellId != null |
| `ClearInspectCellReplayCommand` | `RelayCommand` | 셀 결과 초기화 | 결과 존재 |
| `LoadSavedGlassDefectFolderCommand` | `RelayCommand` | 저장된 세션 로드 | 항상 |
| `LoadRecipeCommand` | `RelayCommand` | 레시피 파일 선택 로드 | 항상 |
| `OpenRecipeCommand` | `RelayCommand` | 레시피 편집 창 열기 | 항상 |
| `OpenConfigCommand` | `RelayCommand` | 설정 창 열기 | 항상 |

---

### 5-5. 주요 메서드

#### `InitializeAsync()`

```
목적: 창 로드 후 비동기 초기화
입력: 없음
출력: 없음
동작:
  1. ControlRuntime 설정 적용
  2. Control 상태 갱신
  3. 이전 미완료 검사 상태 복원 시도
  4. 연결된 IP에 현재 레시피 동기화
```

---

#### `GenerateGlassMap()`

```
목적: 현재 레시피 또는 디자인 템플릿으로 글래스 맵 정보 생성
입력: Vars.Recipe or _recipeStore
출력: MapInfo 속성 업데이트
분기:
  - 레시피 있음 → RecipeService.BuildGlassMapInfoFromRecipe()
  - 레시피 없음 → 디자인 템플릿 JSON에서 좌표 로드
```

---

#### `InspectGlassReplayAsync()` (핵심 메서드)

```
목적: 전체 글래스 검사 실행 (Resume/New/Cancel 분기 포함)
입력: GlassInspectionRunOptions (다이얼로그로부터)
출력: GlassInspectionRunOutcome (Completed / Stopped)
예외 처리:
  - OperationCanceledException → 사용자 취소 로그
  - 저장 실패 → ConSaveFail 알람
  - Control 실패 → CtlDown 알람
  - 기타 → ConRunException 알람
```

---

#### `LoadCellInspectionReplay(string folderPath)` (public)

```
목적: 단일 셀의 검사 결과 폴더를 로드해 UI에 반영
입력: folderPath — 셀 검사 결과가 있는 폴더 경로
출력: 없음 (ViewModel 상태 업데이트)
예외: SelectedCellId가 null이면 InvalidOperationException
성능 로그: 각 단계별 소요 시간 기록
```

---

#### `RaiseAlarm()` / `ClearAlarm()`

```
목적: 알람 발생 및 해제 (AlarmPolicy 정책 기반)
입력:
  - definition: AlarmDefinition (알람 정의)
  - sourceKey: 알람 출처 식별자 (예: "IP1", "CONTROL")
  - detail: 상세 메시지
동작:
  - CurrentOperationState에 따라 알람 억제 여부 결정
  - 발생 횟수 추적 (_alarmOccurrenceCountByKey)
```

---

#### `MonitorIpConnectionAsync()` / `MonitorControlConnectionAsync()`

```
목적: 백그라운드 연결 감시 루프 (3초 간격)
스레드: Task.Run으로 백그라운드 실행
동작(IP):
  - 끊기면 자동 재연결 시도
  - 연결되면 레시피 동기화
  - 상태 변화 시 RaiseAlarm/ClearAlarm
동작(Control):
  - 설정 재적용 후 EnsureConnectedAsync 호출
종료: CancellationToken으로 종료 (Shutdown() 호출 시)
```

---

## 6. 핵심 알고리즘 설명

### 6-1. 글래스 검사 스케줄링 알고리즘

**목적**: 다수의 셀을 Row/Step/Batch 단위로 최적화하여 순차 처리

```
입력: 셀 목록 (CellId, XIndex, YIndex, LaneNo)
출력: GlassReplayRowPlan 리스트

알고리즘:
1. XIndex 기준으로 그룹화 → Row (행) 단위
2. 각 Row 내에서 Lane(IP) 별로 셀 분리
3. 같은 Step 인덱스의 셀들을 하나의 Batch로 묶음
4. Batch 내 셀들은 병렬 처리, Batch 간에는 순차 처리

예시 (2 Lane 구조):
  Row 0: [Step1: Cell-A(IP1) + Cell-B(IP2)]
         [Step2: Cell-C(IP1) + Cell-D(IP2)]
  Row 1: [Step1: Cell-E(IP1) + Cell-F(IP2)]
```

---

### 6-2. 배치(Batch) 동기화 메커니즘 (`CaptureBatchStartCoordinator`)

한 배치의 셀들이 동시에 각 단계를 진행하도록 Barrier 패턴 구현:

```
단계별 Coordinator (4개):
  1. captureCoordinator  → 모든 셀이 StartJob 준비 완료 대기
  2. acceptCoordinator   → 모든 셀이 Accepted 수신 후 대기
  3. bufferingCoordinator→ 모든 셀이 버퍼링 준비 후 대기
  4. endCoordinator      → 모든 셀이 EndJob 전송 전 대기

흐름:
  각 셀(Task) ──→ SignalReadyAndWait()  ─→ 모두 준비되면 →  메인 루프가 Release()
                                                              ↓
                                               모든 셀이 다음 단계 진행
```

**핵심 제약 (코드 주석에서):**
- 한 배치의 셀들은 반드시 `StartJob`을 함께 시작하고 `EndJob`을 함께 완료해야 함
- `Cell Interval`은 검사 완료 간격이 아닌 다음 배치 버퍼링 시작 간격임
- `Line Delay`는 Row 경계에서만 적용됨

---

### 6-3. 이어하기(Resume) 알고리즘

```
시작 시 체크포인트 파일 탐색
  ↓ 발견 시
사용자에게 Yes/No/Cancel 프롬프트
  ↓ Yes (이어하기)
1. 저장된 세션 폴더에서 완료된 셀 결과 로드
2. IP 버퍼 전체 초기화 (ResetGlassReplayIpBuffersForResumeAsync)
3. 마지막 완료 셀 이후부터 재시작
4. completedCellIds로 이미 완료된 셀 Skip

중요: 재시작 시 이전 종료 원인을 신뢰하지 않고 IP 상태를 강제 초기화
```

---

### 6-4. 셀 클릭 → 결과 표시 흐름

```
glassMap.CellClicked 이벤트
  → MainWindow.GlassMap_CellClicked()
  → ViewModel.NotifyManualReplayCellSelection(cellId)
  → SelectReplayCell(cellId, disableAutoFollow: true)
    → AutoShowLatestInspectedCell = false  ← 자동 따라가기 OFF
    → SelectedCellId = cellId
      → (SelectedCellId setter)
        → SelectedCellName 업데이트
        → RebuildGlassReplayOverlays()      ← 불량 오버레이 갱신
        → UpdateSelectedCellReplayState()   ← 불량/조건/CA-410 목록 갱신
        → Command.NotifyCanExecuteChanged() ← 버튼 활성화 갱신
```

---

### 6-5. 불량 이미지 오버레이 정규화

```csharp
// 불량 좌표를 셀 내 상대 좌표(0.0~1.0)로 정규화
double normalizedX = (defect.X - minX) / spanX;
double normalizedY = (defect.Y - minY) / spanY;

// 최소 크기 0.01 보장 (너무 작으면 보이지 않음)
double normalizedWidth = Math.Max(0.01, defect.Width / spanX);

// 경계 범위 클램프 (0.0~0.99, 0.01~1.0)
NormalizedX = Math.Clamp(normalizedX, 0.0, 0.99);
```

---

## 7. 데이터 모델 클래스 목록

### 7-1. UI 표시용 Row 클래스

| 클래스명 | 용도 | 주요 속성 |
|---|---|---|
| `CellReplayDefectRow` | 불량 DataGrid 행 | Code, Grade, Score, PatternIndex, ShotName, CropImagePath |
| `CellReplayConditionIssueRow` | 점등 불량 DataGrid 행 | Name, PatternIndex, LitPixelCount, ExpectedPixelCount, LitRatioPercent |
| `CellReplayCa410MeasurementRow` | CA-410 DataGrid 행 | ProbeNumber, DisplayMode, Value1~3, Flicker |

### 7-2. 상태 추적 클래스

| 클래스명 | 용도 | 주요 속성 |
|---|---|---|
| `GlassMapInspectionCellState` | 셀별 시각적 상태 | CellId, Status, DefectCount, ActivePatternType |
| `GlassReplayLaneSummary` | Lane(IP)별 진행 요약 | LaneNo, Status, CurrentCellName, CompletedCells, TotalDefects |
| `CellReplayCellState` | 셀별 결과 캐시 (내부) | PanelId, Summary, Defects, Overlays |
| `GlassMapReplayDefectOverlay` | 불량 오버레이 좌표 | CellId, NormalizedX/Y/Width/Height |

### 7-3. 검사 계획 클래스 (내부)

| 클래스명 | 용도 |
|---|---|
| `GlassReplayCellPlan` | 개별 셀 검사 계획 (XIndex, YIndex, IpNo) |
| `GlassReplayRowPlan` | 행(Row) 단위 계획 |
| `GlassReplayStepPlan` | 스텝(Step) 단위 계획 |
| `GlassReplayAssignment` | 최종 할당 (LaneNo, LineIndex, StepIndex) |

### 7-4. 동기화 클래스 (내부)

| 클래스명 | 용도 |
|---|---|
| `CaptureBatchStartCoordinator` | 배치 내 셀 동기화 Barrier |

### 7-5. Enum

| Enum명 | 값 | 설명 |
|---|---|---|
| `GlassInspectionCellVisualStatus` | None, Pending, Queued, Inspecting, Completed, LightingFailure | 셀 시각적 상태 |
| `GlassInspectionRunOutcome` | Completed, Stopped | 검사 완료 결과 |
| `GlassInspectionResumeDecision` | Resume, New, Cancel | 이어하기 선택 |

---

## 8. 가정 및 제한 사항

### 가정

1. **`Vars` 전역 클래스**: `Vars.Recipe`, `Vars.IpRuntimes`, `Vars.ControlRuntime` 등 전역 상태를 가진 정적 클래스가 존재한다. 이 코드에서는 직접 구현을 볼 수 없으나, 시스템 부팅 시 초기화된다고 가정한다.

2. **IP 번호 연속성**: Lane(IP) 번호는 레시피 셀 계획에서 가져오며, 없으면 기본값 1번으로 처리된다.

3. **레시피 필수**: 글래스 검사를 실행하려면 레시피가 반드시 로드되어 있어야 한다. 레시피 없이는 `InvalidOperationException` 발생.

4. **UI 스레드 안전**: `Application.Current.Dispatcher.InvokeAsync()` 패턴으로 백그라운드 스레드에서 UI 업데이트가 가능하게 설계되어 있다.

### 제한 사항

1. **단일 검사 세션**: 동시에 하나의 검사만 실행 가능하다 (`_glassReplayCts` 단일 CTS).

2. **이미지 로딩 방식**: 불량 이미지는 선택 시 파일에서 즉시 로드(`BitmapCacheOption.OnLoad`). 파일이 없거나 손상되면 null 반환으로 조용히 실패한다.

3. **알람 정책 의존**: 알람 발생/억제는 `AlarmPolicyCatalog`에 정의된 정책에 의존한다. 이 클래스는 분석 파일 밖에 있다.

4. **체크포인트는 단일**: `Vars.Variables.LastGlassInspectCheckpointPath`에 하나의 체크포인트만 저장된다. 여러 세션을 동시에 이어하기할 수 없다.

5. **ZoomOption 고정**: X1, X2, X5 세 가지 줌 단계만 지원한다 (코드에서 하드코딩).

---

## 9. 다음으로 분석해야 할 코드

지금까지 MainWindow와 ViewModel의 전체 구조를 파악했다.  
이 코드가 참조하는 주변 클래스들을 분석하면 전체 시스템을 이해할 수 있다.

### 우선순위 1 — 핵심 서비스 계층

| 파일 / 클래스 | 이유 |
|---|---|
| **`ICellInspectionDataProvider`** 및 구현체 3개 | 검사 데이터 공급 방식 이해 (폴더/IP 버퍼/Camera) |
| **`GlassInspectionOutputWriter`** | 결과 저장 구조, `glass_result.json` 포맷 |
| **`CellInspectionReplayLoader`** | 셀 결과 폴더 파싱 로직 |
| **`RecipeService`** | 레시피에서 글래스 맵 생성, 유효성 검사 방법 |

### 우선순위 2 — 통신 계층

| 파일 / 클래스 | 이유 |
|---|---|
| **`ULedIpConnection`** | IP(Image Processor) 프로토콜, StartJob/BufferJob/EndJob 동작 |
| **`ULedControlConnection`** | Control 장비 프로토콜, Contact/Move/GlassPresent 상태 |

### 우선순위 3 — 설정 및 모델

| 파일 / 클래스 | 이유 |
|---|---|
| **`Vars`** (전역 변수 클래스) | 전체 시스템 부팅 흐름, 전역 상태 구조 |
| **`ConsoleRecipeDocument`** | 레시피의 데이터 구조 전체 파악 |
| **`GlassMapControl`** | UI 커스텀 컨트롤 내부 구현 |
| **`AlarmPolicyCatalog`** / **`ConsoleAlarmManager`** | 알람 정책 전체 이해 |

### 우선순위 4 — 서브 창

| 파일 / 클래스 | 이유 |
|---|---|
| **`RecipeWindow`** | 레시피 편집 UI와 저장 로직 |
| **`GlassInspectionRunWindow`** | 검사 옵션 다이얼로그 구조 |
| **`GlassInspectionStoppingWindow`** | 정지 대기 팝업과 CancelRequested 이벤트 |

---

> **추천 다음 분석**: `ULedIpConnection`부터 시작하는 것을 권장한다.  
> ViewModel의 가장 복잡한 로직인 `ProcessGlassReplayAssignmentAsync()`이  
> IP와 주고받는 프로토콜(`StartCellJobAsync`, `BufferCellJobAsync`, `EndCellJobAsync`)을  
> 이해해야 전체 검사 루프가 완전히 파악된다.
