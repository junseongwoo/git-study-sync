
---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [솔루션 구성](#2-솔루션-구성)
3. [기술 스택](#3-기술-스택)
4. [전체 아키텍처](#4-전체-아키텍처)
5. [레시피 계층 구조](#5-레시피-계층-구조)
6. [데이터 저장 구조](#7-데이터-저장-구조)
7. [주요 클래스 분석](#7-주요-클래스-분석)
   - 7-1. MainWindow (View)
   - 7-2. MainWindowViewModel
   - 7-3. GlassMapDesign / GlassMapInfo / GlassInfoHelper
   - 7-4. ICellInspectionDataProvider (인터페이스 + 2개 구현체)
   - 7-5. CellInspectionReplayLoader / Models
   - 7-6. GlassInspectionRunOptions
8. [핵심 시퀀스 분석](#8-핵심-시퀀스-분석)
   - 8-1. 앱 시작 흐름
   - 8-2. Glass 검사 실행 시퀀스
   - 8-3. 셀 1개 라이프사이클 (7단계)
   - 8-4. IP / Control 백그라운드 모니터링
9. [GlassMap 셀 좌표 계산 알고리즘](#9-glassmap-셀-좌표-계산-알고리즘)
10. [현재 구현 범위 vs 확장 예정](#10-현재-구현-범위-vs-확장-예정)
11. [Console 담당자 중점 확인 항목](#11-console-담당자-중점-확인-항목)
12. [다음 탐색 우선순위 로드맵](#12-다음-탐색-우선순위-로드맵)
13. [자주 실수하는 함정 목록](#13-자주-실수하는-함정-목록)

---

## 1. 프로젝트 개요

**uLedAoiConsole**은 uLED 디스플레이 패널의 **점등 검사기(AOI: Automated Optical Inspection)** 운영 소프트웨어다.

### 설비 구성

| 구성 요소                | 설명                                |
| -------------------- | --------------------------------- |
| Glass 모델             | 3가지 크기, 설비에 순차 투입                 |
| Align                | 투입된 Glass를 정밀 정렬                  |
| PG (Probe Generator) | Glass와 Contact하여 셀에 전압 인가 (점등)    |
| 검사 카메라 (IP)          | Area 카메라 × 2대, 각 열(Lane)을 분담하여 촬영 |
| Control              | 스테이지·인터락·Contact 제어               |
| CIM                  | 상위 MES/호스트 통신                     |

### 검사 흐름 요약

```
Glass 투입 → Align → PG Contact → 열(Row) 단위 이동
→ 각 셀을 IP1/IP2가 병렬 촬영·검사 → 결과 수집 → Uncontact → Unload
```

---

## 2. 솔루션 구성

```
uLedAoiConsole.sln
├── uLedAoiConsole          ← 메인 WPF 앱 (Console) ★ 담당 영역
├── uLed.Contracts          ← Console/IP 공용 계약 모델
├── uLedIp                  ← IP 런타임 (촬영·검사 수행)
├── uLedControl             ← 제어기 샘플
├── uLedCim                 ← CIM 통신
├── uLed.Common             ← 공용 유틸·레시피 편집 코어
└── Ratel.WPF.Utils         ← 로깅·뷰어 등 공용 UI 유틸
```

### 책임 경계

```
uLedAoiConsole  ──→  uLed.Contracts  ←──  uLedIp
       │                                      ↑
       ├──→  uLedControl                      │ RecipeModel 전달
       └──→  uLedCim                          │
                                       (촬영·검사·결과 반환)
```

- **Console**: 전체 오케스트레이션 중심. 데이터 소유자.
- **uLedIp**: `RecipeModel`만 소비. 촬영·검사·결과 반환만 담당.
- **Contracts**: 공용 계약 모델 (RecipeModel, PanelResultModel 등).

---

## 3. 기술 스택

### 프레임워크 / UI

| 기술 | 용도 |
|---|---|
| WPF (.NET) | 메인 UI 프레임워크 |
| CommunityToolkit.Mvvm | ObservableObject, RelayCommand, AsyncRelayCommand |
| XAML DataBinding (TwoWay) | ViewModel ↔ View 자동 동기화 |

### 비동기 / 동시성

| 기술                                       | 용도                                              |
| ---------------------------------------- | ----------------------------------------------- |
| `async/await` + `Task`                   | 검사 실행 전체 비동기 처리                                 |
| `CancellationTokenSource`                | 3개 운용 (IP모니터·Control모니터·검사실행)                   |
| `SemaphoreSlim`                          | Lane별 Dispatch/Buffering 동시성 제어                 |
| `TaskCompletionSource<T>`                | IP 이벤트(Accepted/Completed)를 `await` 가능 Task로 변환 |
| `CaptureBatchStartCoordinator`           | 커스텀 Barrier — IP1·IP2 Task를 4개 지점에서 동시 통과       |
| `Task.Run`                               | 백그라운드 모니터링 루프                                   |
| `Dispatcher.BeginInvoke` / `InvokeAsync` | 백그라운드 → UI 스레드 마샬링                              |

### 데이터 / 직렬화

| 기술 | 용도 |
|---|---|
| `System.Text.Json` | YAML/JSON 파일 읽기·쓰기 |
| YAML (config.yaml) | 장비 설정 저장 |
| `System.Drawing.Rectangle` | 셀 좌표(um 단위) 표현 |
| `ObservableCollection<T>` | UI 바인딩 컬렉션 |

### 로깅

| 기술 | 용도 |
|---|---|
| `RatelSoft.Utils.Wpf.Logging` | 외부 LogViewer 컴포넌트 |
| `RatelLogger` / `RatelLog.ForSource()` | 구조화 로그 (Source 태그 + 메시지) |
| `logs/app_yyyyMMdd.log` | 일별 파일 로그 |
| `Stopwatch` | 성능 측정 (10ms 기준 경고) |

---

## 4. 전체 아키텍처

### 레이어 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                    View Layer (XAML)                      │
│  MainWindow · RecipeWindow · GlassSizeWindow · FlowTest  │
└──────────────────────┬──────────────────────────────────┘
                       │ DataContext (양방향 바인딩)
┌──────────────────────▼──────────────────────────────────┐
│              ViewModel Layer                              │
│  MainWindowViewModel (3,822줄)                           │
│  ├─ GlassMap 관리          ├─ Glass 검사 실행 엔진        │
│  ├─ IP 연결 모니터          ├─ 알람 관리                  │
│  ├─ Control 모니터          └─ 검사 결과·리플레이 관리     │
│  └─ Recipe 동기화                                         │
└──────┬───────────┬──────────────────┬───────────────────┘
       │           │                  │
┌──────▼──┐  ┌────▼──────┐  ┌────────▼──────────────────┐
│ Vars    │  │ Recipe    │  │ Services                    │
│ WorkDir │  │ Store     │  │ ├─ ICellInspectionData      │
│ IpRunt  │  │ Console   │  │ │    Provider               │
│ Control │  │ Recipe    │  │ ├─ CellInspectionReplay     │
│ Runtime │  │ Document  │  │ │    Loader                 │
└─────────┘  └───────────┘  │ ├─ GlassInspectionOutput   │
                             │ │    Writer                 │
                             │ └─ ConsoleAlarmManager      │
                             └────────────┬───────────────┘
                                          │
              ┌───────────────────────────▼────────────────┐
              │         External Connections                 │
              │  ULedIpConnection × 2  ·  ULedControl       │
              │  CIM Client  ·  GlassInspectionStepPrep     │
              └────────────────────────────────────────────┘
```

### 핵심 설계 원칙

1. **Console이 데이터 소유자**: `ConsoleRecipeDocument`, `GlassMap`, `Cells`, `AlignPlan`, `ControlPlan` 전부 Console 소유.
2. **IP는 RecipeModel만 소비**: IP에게 전달되는 것은 `IpRecipe(RecipeModel)` 하나뿐.
3. **ViewModel은 WPF를 모른다**: UI 조작(창 열기, 다이얼로그)은 `Action/Func` 콜백으로 주입받음.
4. **검사 흐름은 단방향 이벤트**: IP → `JobEvent` → TCS → `await` 순차 처리.

---

## 5. 레시피 계층 구조

```
ConsoleRecipeDocument           ← Console 상위 레시피 (전체 포함)
├── IpRecipe: RecipeModel       ← IP 실행 레시피 (하위)
│   ├── Patterns: List<PatternPlanModel>
│   │     └── PatternIndex · PatternType · ExposureUs · Threshold
│   └── Points: List<CapturePointPlanModel>
│         └── PointIndex · StageX · StageY · FocusZ · ROI
├── GlassMap
│   ├── GlassSizeId             ← 핵심! 틀리면 전부 어긋남
│   ├── GlassSizeSnapshot       ← 외부 파일 변경과 무관하게 이 값이 실행 기준
│   ├── IpSplitColumn           ← IP 분배 기준 열 번호
│   ├── GlassMapDesignSnapshot  ← 설계 원본 스냅샷
│   └── Cells: List<ConsoleCellPlan>
│         └── CellId · IpNo · XIndex · YIndex · CellRectGlassUm
├── AlignPlan
│   └── Left/Right Override (없으면 GlassSize 기본값 사용)
└── ControlPlan
      └── ForbidYMoveWhileContact = true 반드시 유지

※ 실행 단위: Pattern × Point (Point는 Pattern에 종속되지 않음)
```

---

## 6. 데이터 저장 구조

```
{Vars.WorkDir}/
├── Config/
│   ├── config.yaml             ← Vars.EMRConfig (장비 공통 설정)
│   └── Variables.yaml          ← 가변 런타임 설정
├── Data/
│   ├── GlassMaps/
│   │   └── glass_map_design.json
│   ├── GlassSizes/
│   │   └── {glassSizeId}.json
│   ├── Recipes/
│   │   └── {glassSizeId}/{recipeId}/
│   │       └── recipe.json     ← ConsoleRecipeDocument
│   ├── Calibrations/
│   │   └── {glassSizeId}/axis_hardware.json
│   └── Runtime/
│       └── align_result.json
└── logs/
    └── app_yyyyMMdd.log
```

---

## 7. 주요 클래스 분석

### 7-1. MainWindow (View)

**파일**: `Windows/Core/MainWindow.xaml` / `.xaml.cs`
**크기**: 1920×1080, Maximized

#### 레이아웃 구조

```
Root Grid (2 Row)
├── Row 0: Menu Bar (DockPanel)
│   ├── 왼쪽: Tool · Data · View · Test · ETC 메뉴
│   │   ├── Tool → ShowDialog() 모달 (편집 중 검사 방지)
│   │   └── Test → Show() 비모달 (동시 사용 가능)
│   └── 오른쪽: Alarm 버튼 · IP 상태 · Control 상태
└── Row 1: Content (Grid, 3 Col)
    ├── Col 0: 왼쪽 컬럼
    │   ├── GlassMapControl (커스텀, ScrollViewer)
    │   └── TabControl (Height=240)
    │       ├── Log: LogViewer
    │       ├── Inspection State: 4카드 + Lane 요약 DataGrid
    │       ├── Grade: 등급별 집계
    │       └── Code Top 10: 불량 코드 빈도
    ├── Col 1: GridSplitter
    └── Col 2: 오른쪽 컨트롤 패널 (Width=800)
        ├── 조작 버튼 (AUTORUN · INSPECT · STOP · SET UP)
        ├── 상태 바 (FontSize=30, 색상 변화)
        ├── 레시피 정보 (Recipe · LOT ID · GlassID · Start)
        ├── 불량 목록 DataGrid (가상화, Height=220)
        └── 불량 이미지 (Crop + Mapping Image)
```

#### Code-behind 핵심

| 구조 | 역할 |
|---|---|
| `WindowProcessStateMachine` | 창 생명주기 (Initializing→Ready→Closing→Closed) |
| `MainWindowViewModel` 생성자 주입 | Action/Func 콜백 7개+ 주입 → ViewModel WPF 의존성 없음 |
| `UpdateGlassMapViewport()` | Zoom ≤ 1.0 → Stretch, > 1.0 → 고정크기+스크롤 |
| `GlassInspectionStoppingWindow` | STOP 버튼 시 팝업, MainWindow가 직접 관리 |
| `GlassInspectionRunOptions` 다이얼로그 | INSPECT 클릭 시 Source/Interval/PG옵션 선택 |

---

### 7-2. MainWindowViewModel

**파일**: `ViewModels/MainWindowViewModel.cs`
**코드 라인**: 3,822줄

#### 6대 책임 영역

| 영역 | 핵심 메서드 | 기술 |
|---|---|---|
| GlassMap 관리 | `GenerateGlassMap()` | RecipeService 호출, RotationAngle 계산 |
| IP 연결 모니터 | `MonitorIpConnectionAsync()` | Task.Run + 3초 루프 + CTS |
| Control 모니터 | `MonitorControlConnectionAsync()` | 3초 폴링 + EventNotification Push |
| Glass 검사 엔진 | `InspectGlassReplayAsync()` | 4중 배리어 + Lane 병렬 처리 |
| 알람 관리 | `ConsoleAlarmManager.Current` | 싱글턴, PolicyCatalog 기반 |
| 결과·리플레이 | `CellReplayStateByCellId` | Checkpoint·Resume 관리 |

#### Commands

```
InspectGlassReplayCommand   (AsyncRelayCommand) → InspectGlassReplayAsync
StopGlassReplayCommand      (RelayCommand)      → IsGlassReplayStopping = true
CancelStopGlassReplayCommand(RelayCommand)      → IsGlassReplayStopping = false
LoadRecipeCommand            (AsyncRelayCommand) → 파일 선택 다이얼로그 → 레시피 교체
OpenGlassMapDesignCommand    (RelayCommand)      → 콜백 → GlassMapDesignWindow
OpenRecipeCommand            (RelayCommand)      → 콜백 → RecipeWindow
```

#### 내부 보조 클래스

```csharp
// 검사 계획 계층
GlassReplayRowPlan           // Row 1개 = 여러 Step
  └─ GlassReplayStepPlan     // Step 1개 = 배치 단위 셀들
       └─ GlassReplayAssignment  // 셀 1개 배정 (CellId, IpNo, LineIndex, StepIndex)

// IP 배치 동기화 (커스텀 Barrier)
CaptureBatchStartCoordinator // SignalReadyAndWait × 4 지점

// 상태 추적
GlassReplayLaneSummary       // IP별 현재 상태 (Inspection State 탭 표시)
CellReplayCellState          // 셀별 결과 캐시
DefectStatItem               // Grade/Code 집계
```

---

### 7-3. GlassMapDesign / GlassMapInfo / GlassInfoHelper

#### 데이터 흐름

```
glass_map_design.json
  └─ GlassMapDesign
       └─ List<GlassCoordinateModel>   (모델별 A, B, C…)
            └─ SMDCoordInfo            (좌표 파라미터, 단위=μm)
                    │
                    │ GlassInfoHelper.MakeCells()
                    ▼
             List<RoiInfo>             (셀 1개 = Rect + Name + Id + IPNo)
                    │
                    ▼
             GlassMapInfo              (GlassMapControl 바인딩 대상)
```

#### SMDCoordInfo 핵심 필드 (기본값 = 750×650mm Glass 기준)

| 필드 | 기본값 (μm) | 의미 |
|---|---|---|
| CELL_X | 12 | X 방향 전체 셀 수 |
| CELL_Y | 15 | Y 방향 전체 셀 수 |
| BLOCK_COUNT_X | 2 | X 블록 수 |
| BLOCK_COUNT_Y | 2 | Y 블록 수 |
| OFFSET_E_X | 24,998 | 좌상단 → 첫 셀 X 거리 |
| OFFSET_E_Y | 25,003 | 좌상단 → 첫 셀 Y 거리 |
| CELL_DIST_X | 59,167 | 셀 간격 X (center-to-center) |
| CELL_DIST_Y | 43,571 | 셀 간격 Y |
| CELL_SIZE_X | 54,167 | 셀 너비 (= DIST − 5000) |
| CELL_SIZE_Y | 38,571 | 셀 높이 (= DIST − 5000) |

#### GlassInfoHelper.MakeCell() 알고리즘

```csharp
// 4중 루프 (순서 중요!)
for (bY = 0; bY < blockCountY; bY++)          // Y 블록
  for (localY = 0; localY < rowsInBlock; localY++)  // 블록 내 행
    for (bX = 0; bX < blockCountX; bX++)      // X 블록
      for (localX = 0; localX < colsInBlock; localX++)  // 블록 내 열

// 좌표 계산
blockBaseX = OFFSET_E_X + bX × BLOCK_DIST_X
cellX      = blockBaseX + localX × CELL_DIST_X
Rect       = (Round(cellX), Round(cellY), CELL_SIZE_X, CELL_SIZE_Y)

// 이름 조합
name = prefix + GetColumnChar(globalColumnIndex) + rowNum(2자리)
// 예: Coordinate.Name="A", 3열 5행 → "AD05"
```

#### ⚠️ 주의: CELL_Y=15, BLOCK_COUNT_Y=2

```csharp
BuildBlockCellCounts(15, 2) → [8, 7]  // 총 15개 생성
// 주석에 "14개 생성"이라 쓰여 있으나 코드 결과는 15개 — 실제 확인 필요
```

---

### 7-4. ICellInspectionDataProvider

**파일**: `Services/InspectionReplay/CellInspectionDataProvider.cs`

#### 인터페이스 계약

```csharp
/// StartJob → StartStep 반복 → EndJob → EvtJobCompleted 흐름만 허용
/// TryInspectPoint, TryInspectPanelFolder 등 직접 API 호출 금지
public interface ICellInspectionDataProvider
{
    int AvailableCellCount { get; }
    event EventHandler<CellInspectionJobEventArgs>? JobEvent;
    Task BeginRowAsync(int lineIndex, IReadOnlyList<CellInspectionRowTarget> rowTargets, CancellationToken ct);
    Task EndRowAsync(int lineIndex, CancellationToken ct);
    Task StartCellJobAsync(int ipNo, int cellId, string cellName, CancellationToken ct);
    Task BufferCellJobAsync(int ipNo, int cellId, string cellName, int lineIndex, int stepIndex, int batchParticipantCount, CancellationToken ct);
    Task EndCellJobAsync(int ipNo, int cellId, string cellName, CancellationToken ct);
}
```

#### JobEvent 종류

| Kind | 발생 시점 | UI 반영 |
|---|---|---|
| Accepted(0) | StartJob 승인 | 셀 상태: Pending |
| BufferWaiting(1) | IP 버퍼 가득 찼을 때 | 5초 대기 로그 |
| PatternActivated(2) | 패턴 검사 시작 | 셀 상태: Inspecting + PatternType |
| StepBuffered(3) | StartStep 완료 | — |
| Completed(4) | 검사 완료 | 셀 상태: OK or NG |
| Failed(5) | 에러 발생 | 셀 상태: Failed |

#### 구현체 비교

| 항목 | FolderCellInspection DataProvider | IpLoadedBufferCellInspection DataProvider |
|---|---|---|
| 소스 | 미리 저장된 결과 폴더 | 실제 ULedIpConnection |
| AvailableCellCount | 폴더 개수 | int.MaxValue |
| StartCellJob | 랜덤 폴더 선택 → 즉시 Accepted | IP StartJob → 버퍼 재시도 루프 |
| BufferCellJob | Task.Yield() (no-op) | Pattern×Point StartStep 병렬 수행 |
| EndCellJob | 즉시 Completed | EndJob → FinalResult 수신 |
| BeginRow/EndRow | 취소만 확인 (no-op) | GlassInspectionStepPreparationService |
| IDisposable | ✗ | ✓ (StepPreparationService 해제) |
| 용도 | 오프라인 테스트·리플레이 | 실 장비 검사 |

#### IpLoadedBufferCellInspectionDataProvider 핵심 로직

**StartJob 버퍼 재시도**

```csharp
// StartJobWithBufferRetryAsync
while (true)
{
    var started = await connection.StartJobAsync(...);
    if (started.Ok) return started;
    if (started.ErrorCode != IpErrorCode.ErrBufferFull) throw;
    
    // 버퍼 가득 찼을 때 → 5초 대기 후 재시도
    OnJobEvent(BufferWaiting, 버퍼 현황...);
    await Task.Delay(5초, ct);
    await connection.RequestRuntimeStatusAsync(ct);
}
```

**BufferBatchContext — 배치 내 동기화**

```csharp
// 배치 키: "lineIndex:stepIndex"
// 마지막 참여자가 Leader가 되어 ProcessBufferedBatchAsync 실행
// 나머지는 batchContext.Completion.Task를 await

if (batchContext.Participants.Count == batchContext.ParticipantCount && !batchContext.Started)
{
    batchContext.Started = true;
    isLeader = true;
}
if (isLeader)
    _ = Task.Run(() => ProcessBufferedBatchAsync(batchKey, batchContext, ct));

await batchContext.Completion.Task;   // 모든 참여자가 여기서 대기
```

**LoadWithInspect 특수 경로**

```csharp
// EndCellJobAsync에서 분기
if (_runMode == StepRunMode.LoadWithInspect)
{
    // EndJob → 즉시 반환 (검사는 worker가 비동기로)
    _ = Task.Run(async () =>
    {
        var completed = await connection.WaitForPanelCompletedAsync(jobId, CancellationToken.None);
        // 완료 시 Completed 이벤트 발생
    });
    return;  // 호출자는 즉시 반환됨
}
// GrabWithInspect/Inspect → EndJob 응답에 FinalResult 포함
```

---

### 7-5. CellInspectionReplayLoader / Models

#### 폴더 구조 (셀 결과 1개)

```
{cellResultFolder}/
├── panel_result.json          ← 검사 결과 전체 (Pattern→Point→Shot→Defect)
├── defect_crops/
│   └── {DefectId}.jpg         ← 불량 부위 크롭 이미지
├── mapping_images/
│   └── {patternIdx:00}_{channelName}.png  ← 맵핑 이미지
└── mapping_images_raw/
    └── {patternIdx:00}_mapping.raw
```

#### LoadFromFolder() 처리 흐름

```
panel_result.json 파싱 (System.Text.Json, CaseInsensitive)
    │
    ├── Pattern 순서 정렬 → Point 순서 정렬 → Shot 순서 정렬
    │      └── Shot마다 ResolveMappingImagePath() (3단계 퍼지 매칭)
    │
    └── Defect마다 ResolveCropPath() (DefectId 기반 파일명 매칭)
                    │
                    ▼
             CellInspectionReplaySession
             ├── Shots: List<CellInspectionReplayShot>
             └── Defects: List<CellInspectionReplayDefect>
```

#### 맵핑 이미지 해석 우선순위 (ResolveMappingImagePath)

```
1순위: 파일명 == "{pattern:00}_{channelName}" 정확히 일치
2순위: 파일명 == "{pattern:00}_{shotName}" 정확히 일치
3순위: 파일명 == "{pattern:00}_mapping" 정확히 일치
4순위: 파일명이 "{pattern:00}_"로 시작 + channel/shot/mapping 포함 (부분 매칭)
5순위: 파일명이 "{pattern:00}_"로 시작하는 첫 번째 파일
```

#### 모델 구조

```csharp
CellInspectionReplaySession
├── PanelId / JobId / OverallJudgment / TotalDefectCount
├── FinalPanelResultModel?          // IP 직접 검사 시 채워짐
├── List<CellInspectionReplayShot>
│   └── PatternIndex · PointIndex · ShotId · ShotName · ChannelName
│       MappingImageBytes / MappingImageRawBytes (byte[])
└── List<CellInspectionReplayDefect>
    └── DefectModel · ShotName · ChannelName · CropImagePath
```

---

### 7-6. GlassInspectionRunOptions

**파일**: `Models/GlassInspectionRunOptions.cs`

```csharp
public sealed class GlassInspectionRunOptions
{
    public string InputFolderPath { get; set; }          // 소스 이미지 폴더
    public string BufferSourceFolderPath { get; set; }   // IP 버퍼 소스
    public string OutputFolderPath { get; set; }         // 결과 저장 폴더
    public double CellIntervalSeconds { get; set; } = 2.0;  // 셀 간격
    public double LineDelaySeconds { get; set; } = 2.0;     // Row 간격
    public GlassInspectionRunSource Source { get; set; } = Folder;
    public bool WithInspect { get; set; } = true;
    public bool UseMotion { get; set; }                  // false = 스테이지 이동 없음
    public bool UsePgSimulator { get; set; } = true;     // ⚠️ 기본값 true = 실장비 연결 불필요
}
```

#### Source × WithInspect → RunMode 결정

| Source | WithInspect | RunMode | 설명 |
|---|---|---|---|
| Replay/Camera | — | GrabWithInspect | 카메라 촬영 + 검사 동시 |
| Folder | true | LoadWithInspect | 폴더 이미지 적재 → 검사 |
| Folder | false | NoOp | 적재만 (검사 없음) |
| CurrentBuffer | true | Inspect | 버퍼 내 검사만 |
| CurrentBuffer | false | NoOp | 동작 없음 |

#### Checkpoint와의 관계

```
검사 실행 중 셀 완료마다
    └─ GlassInspectionExecutionCheckpoint에 RunOptions 통째로 저장
앱 재시작 후 이어하기
    └─ Checkpoint에서 RunOptions 복원 → 동일 소스/경로/모드로 재실행
```

---

## 8. 핵심 시퀀스 분석

### 8-1. 앱 시작 흐름

```
App.xaml.cs
  ├─ 1. 설정·로그 시스템 초기화
  ├─ 2. Config/config.yaml → Vars.EMRConfig
  ├─ 3. Variables.yaml → Vars.RuntimeConfig
  ├─ 4. Data/GlassMaps/glass_map_design.json → GlassMapDesignStore
  ├─ 5. Data/GlassSizes/ → GlassSizeStore
  ├─ 6. Vars.EMRConfig.IpEndpoints → IpRuntimeRegistry (ULedIpConnection × 2)
  ├─ 7. Data/Recipes/Default/Default/recipe.json → RecipeStore
  │       (없으면 기본 ConsoleRecipeDocument 자동 생성)
  └─ 8. MainWindow 실행
          └─ 마지막 레시피 자동 로드 (없으면 Default)
```

### 8-2. Glass 검사 실행 시퀀스

```
INSPECT 버튼 클릭
  │
  ├─ Checkpoint 확인 → Resume / New / Cancel 선택
  ├─ GlassInspectionRunOptions 다이얼로그
  ├─ EnsureControlReadyForGlassInspectionAsync
  │     (UseMotion=false면 Control 연결 체크 건너뜀)
  ├─ IP 연결 확인 + 레시피 동기화
  ├─ BuildGlassReplayRowPlans()  ← 셀을 Row/Step/Batch로 계획화
  │
  └─ [Row 루프]
       ├─ BeginRowAsync (Contact / PG 전원 ON)
       │
       ├─ [Step 루프]
       │   ├─ CaptureBatchStartCoordinator × 4 생성
       │   ├─ Task.Run (IP1) ‖ Task.Run (IP2)  ← 병렬
       │   │   └─ ProcessGlassReplayAssignmentAsync (7단계)
       │   ├─ WhenAll(endJobAckTasks)  ← 배치 EndJob 전부 완료 대기
       │   ├─ DelayUntilNextStepStartAsync  ← CellIntervalSeconds 준수
       │   └─ StopRequested? → break
       │
       └─ EndRowAsync (Uncontact + LineDelaySeconds 대기)
```

### 8-3. 셀 1개 라이프사이클 (7단계)

```
①  laneDispatchSlot.Wait         ← Lane 진입 허가 (SemaphoreSlim)
          ↓
    captureCoordinator.SignalReadyAndWait  ← 배치 전체 동시 출발 대기
          ↓
②  StartCellJobAsync             ← IP에 StartJob 전송
          ↓
    Accepted TCS await            ← IP Accepted 이벤트 수신 대기
          ↓
③  laneDispatchSlot.Release       ← 다음 셀이 진입 가능
    acceptCoordinator.SignalReadyAndWait
          ↓
④  laneBufferingSlot.Wait         ← Buffering 순서 제어
    bufferingCoordinator.SignalReadyAndWait
          ↓
⑤  BufferCellJobAsync             ← Pattern × Point StartStep 수행
    (PatternActivated 이벤트 → 셀 색상: 노란색)
          ↓
⑥  endCoordinator.SignalReadyAndWait
    EndCellJobAsync               ← EndJob 전송
    laneBufferingSlot.Release
    endJobAckTcs.SetResult        ← 메인 루프 진행 허용
          ↓
⑦  Completed TCS await           ← IP worker 검사 완료 대기
    결과 저장 + Checkpoint 업데이트
    셀 색상: OK(초록) or NG(빨강)
```

### 8-4. IP / Control 백그라운드 모니터링

```
[IP Monitor — 3초 주기]
  연결 없음 → ConnectAsync → TrySyncCurrentRecipeToConnectionAsync
  연결 있음 → RequestRuntimeStatusAsync
  상태 변경 → RaiseIpStateChanged → 알람 판정

[Control Monitor — 3초 주기]
  ApplyConfig → EnsureConnectedAsync
  연결 실패 → MarkFailure → 알람 발생
  EventNotification Push → SyncControlAlarmStates

[알람 시스템]
  ConsoleAlarmManager.Current (싱글턴)
  AlarmPolicyCatalog: ConsoleOperationState 기준 발생 억제
  Heavy 알람 → ConsoleOperationState.AlarmStop 전환
```

---

## 9. GlassMap 셀 좌표 계산 알고리즘

```
Glass 좌상단 (0, 0)
│
├── OFFSET_E_X, OFFSET_E_Y  → 첫 번째 셀까지의 거리
│
└── Block 구조 (BLOCK_COUNT_X × BLOCK_COUNT_Y)
     ├── 블록 기준점: OFFSET_E + bIndex × BLOCK_DIST
     └── 셀 위치: blockBase + localIndex × CELL_DIST

CELL_SIZE = CELL_DIST − 5000  → 셀 사이 5mm 갭 유지
BLOCK_DIST = (셀수/블록) × CELL_DIST − 5000  → 블록 경계도 5mm gap

셀 이름: {coordinatePrefix}{columnChar}{rowNum:00}
  예) Name="A", 3번째 열, 5번째 행 → "AD05"
      Name="B", 0번째 열, 14번째 행 → "BA14"
```

---

## 10. 현재 구현 범위 vs 확장 예정

### 현재 구현 완료 ✅

- Recipe / GlassSize / GlassMap 편집 (RecipeWindow, GlassSizeWindow)
- IP 업로드 / 활성화 / 단건 셀 검사
- FlowTestWindow 기반 Control·CIM·IP 통신 검증
- 오프라인 폴더 리플레이 (FolderCellInspectionDataProvider)
- Checkpoint / Resume 이어하기
- 실시간 GlassMap 셀 상태 표시
- 알람 시스템 (ConsoleAlarmManager)
- 다중 IP (IP1·IP2) 병렬 처리

### 확장 예정 🔧

- 생산 자동화 시퀀스 (Load → Align → Process → Unload 완전 자동)
- Control 주도 실제 축/인터락 연동
- CIM 실설비 연동 상태 머신
- Recipe 선택 / Job 관리 UI
- `SET UP` 버튼 기능 (현재 미구현)
- LOT ID TextBox 바인딩 (현재 빈 상태)

---

## 11. Console 담당자 중점 확인 항목

### 처음 실행 전 필수 체크리스트

```
□ Vars.WorkDir가 올바른 작업 폴더를 가리키는가
□ Config/config.yaml → IP endpoint가 실제 장비 주소와 맞는가
□ GlassSize → GlassSizeId 존재 확인
□ GlassSize → PanelAngleDeg가 현재 투입 방향과 맞는가
□ GlassSize → AlignCam1Calibration 3점 + AlignCam2Reference 1점 입력됐는가
□ Recipe → GlassMap.GlassSizeId 올바른가 (틀리면 전부 어긋남)
□ Recipe → GlassSizeSnapshot 최신 반영됐는가
□ Recipe → Cells 재생성 + IpNo Auto Assign 결과 확인
□ Recipe → IpRecipe.Points.ROI 크기 > 0 확인
□ ControlPlan.ForbidYMoveWhileContact = true 유지 확인
□ GlassInspectionRunOptions.UsePgSimulator = false (실장비 연결 시)
```

### 코드 읽을 때 집중해야 할 포인트

1. **GlassSizeSnapshot** — 외부 파일이 바뀌어도 레시피 내 스냅샷이 실행 기준.
2. **CaptureBatchStartCoordinator** — 4개 배리어 중 하나라도 Release 안 되면 데드락.
3. **LoadWithInspect 분기** — EndCellJobAsync가 즉시 반환되고 Completed는 나중에 비동기로 옴.
4. **ErrBufferFull 재시도 루프** — IP 버퍼가 찰 때 5초 대기 무한 루프. CancellationToken으로만 탈출.
5. **PanelAngleDeg 180/270** — Column 해석 방향이 반전됨. IP 분배 결과가 달라짐.

---

## 12. 다음 탐색 우선순위 로드맵

### P1 — 검사 핵심 루프 직결 (즉시)

| 클래스 | 파일 | 이유 |
|---|---|---|
| `ICellInspectionDataProvider` 구현 내부 | `CellInspectionDataProvider.cs` | 셀 7단계 라이프사이클 실제 구현 |
| `GlassInspectionOutputWriter` | `Services/InspectionReplay/` | 결과 저장 형식·Checkpoint 연동 |
| `GlassInspectionExecutionCheckpoint` | `Services/InspectionReplay/` | Resume 흐름 전체 기준 |
| `ULedIpConnection` | `Services/Ip/` | StartJob/EndJob/WaitForPanelCompleted 실제 TCP 구현 |

### P2 — 레시피·GlassMap 연결

| 클래스 | 파일 | 이유 |
|---|---|---|
| `ConsoleCellPlan` | `Recipes/ConsoleRecipeDocument.cs` | RoiInfo ↔ Recipe 셀 브릿지 |
| `RecipeService` | `Services/RecipeService.cs` | Recipe → GlassMapInfo 변환 전체 |
| `GlassInspectionStepPreparationService` | `Services/` | PG Contact / 스테이지 이동 제어 |

### P3 — 연결 레이어

| 클래스 | 파일 | 이유 |
|---|---|---|
| `ULedControlConnection` | `Services/Control/` | Align/Contact/Inspect 상태 제어 |
| `ConsoleAlarmManager` + `AlarmCatalog` | `Alarms/` | 알람 정책·억제 조건 전체 |

### P4 — GlassMap 렌더링

| 클래스 | 파일 | 이유 |
|---|---|---|
| `GlassMapControl` | `Controls/GlassMapControl.xaml(.cs)` | RoiInfo → Canvas 렌더링 |
| `GlassMapInspectionCellState` | `Models/` | 실시간 셀 색상 결정 모델 |

---

## 13. 자주 실수하는 함정 목록

| # | 함정 | 결과 | 대책 |
|---|---|---|---|
| 1 | `GlassMap.GlassSizeId` 잘못 설정 | 셀 좌표·회전·Align 기준 전부 어긋남 | 레시피 열 때마다 최우선 확인 |
| 2 | `GlassSizeSnapshot` 미갱신 | 외부 GlassSize 수정해도 레시피가 옛날 값 사용 | GlassSize 수정 후 반드시 레시피에 스냅샷 반영 |
| 3 | `UsePgSimulator = true` 실장비에 올림 | PG 실제로 동작 안 함 | 기본값이 true이므로 실장비 시 false 강제 |
| 4 | CELL_Y=15, BLOCK_COUNT_Y=2 | 코드는 15개 생성, 주석은 14개 — 혼동 | 실제 셀 수는 코드(15개) 기준 |
| 5 | `IpSplitColumn` Auto Assign 후 미확인 | IP 분배가 의도와 다를 수 있음 | Auto Assign 후 반드시 Cells 탭에서 눈으로 확인 |
| 6 | `AlignPlan Override` 값 있을 때 | GlassSize 기본 Align이 아닌 레시피 Override 우선 | 레시피마다 Override 값 존재 여부 확인 |
| 7 | `SET UP` 버튼 클릭 | 현재 미구현 — 아무 동작 없음 | 구현 전 사용 금지 |
| 8 | `LOT ID` TextBox | 바인딩 없음 — 입력해도 저장 안 됨 | 현재 표시용만, 구현 필요 |
| 9 | ErrBufferFull 상황 | 5초 루프 무한 재시도 — CT만 탈출 가능 | STOP 버튼이 정상 동작하는지 확인 필수 |
| 10 | LoadWithInspect EndCellJob | 즉시 반환되므로 Completed가 늦게 옴 | inFlightTasks WhenAll 대기 구조 이해 필수 |
