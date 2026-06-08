# uLedAoiConsole — RecipeWindow & RecipeEditorViewModel 완전 분석

> **프로젝트**: uLED(마이크로 LED) 점등 AOI 콘솔
> **분석 파일**: `RecipeWindow.xaml` / `RecipeWindow.xaml.cs` / `RecipeEditorViewModel.cs`
> **진입점**: MainWindow에서 `OpenRecipeWindow()` 호출 시 생성
> **아키텍처**: WPF + MVVM (CommunityToolkit.Mvvm) + OpenCvSharp

---

## 목차

1. [핵심 목적과 주요 기능](#1-핵심-목적과-주요-기능)
2. [전체 아키텍처 구조](#2-전체-아키텍처-구조)
3. [UI 레이아웃 분석 (RecipeWindow.xaml)](#3-ui-레이아웃-분석)
4. [RecipeWindow 코드-비하인드 분석](#4-recipewindow-코드-비하인드-분석)
5. [RecipeEditorViewModel 분석](#5-recipeeditorviewmodel-분석)
6. [핵심 알고리즘 설명](#6-핵심-알고리즘-설명)
7. [데이터 흐름 다이어그램](#7-데이터-흐름-다이어그램)
8. [가정 및 제한 사항](#8-가정-및-제한-사항)
9. [다음으로 분석해야 할 코드](#9-다음으로-분석해야-할-코드)

---

## 1. 핵심 목적과 주요 기능

### 핵심 목적

**Recipe Editor는 uLED AOI 검사 시스템의 핵심 설정 도구**다.  
레시피(검사 조건 파일)를 편집하고, IP(Image Processor) 장비에 업로드하고,  
물리적 장비(Stage, Contact, PG 광원, CA-410 색도계)를 실시간으로 제어하며  
설정값이 올바른지 검증하는 통합 편집 환경이다.

### 주요 기능 6가지

| 기능 | 설명 |
|---|---|
| **레시피 편집** | Pattern(검사 조건), Point(ROI), Cell(유리 기판 셀) 목록 관리 |
| **변경 추적** | 저장 전/후 변경 사항을 Diff로 표시, 미저장 시 경고 |
| **장비 제어** | Stage 이동, Contact On/Off, PG 광원 점등, CA-410 측색 |
| **IP 연동** | IP 연결, 레시피 업로드, 점검(Inspect), 이미지 수신 |
| **글래스 맵 미리보기** | 편집 중인 셀 배치를 GlassMapControl로 시각화 |
| **불량 결과 표시** | 검사 결과 불량 이미지를 DefectWindow로 자동 팝업 |

---

## 2. 전체 아키텍처 구조

```
RecipeWindow (View)
  ├── RecipeEditorViewModel (DataContext / ViewModel)
  │    ├── ConsoleRecipeDocument (데이터 모델)
  │    │    ├── IpRecipe.Patterns    ← PatternPlanModel 목록
  │    │    ├── IpRecipe.Points      ← CapturePointPlanModel 목록
  │    │    ├── GlassMap.Cells       ← ConsoleCellPlan 목록
  │    │    ├── GlassMap.GlassSizeId ← Glass Size 링크
  │    │    ├── AlignPlan            ← 얼라인 설정
  │    │    └── ControlPlan          ← Contact/PG 제어 설정
  │    │
  │    ├── DataStore<ConsoleRecipeDocument>  ← JSON 파일 I/O
  │    ├── ObjectChangeTracker              ← 변경 추적
  │    ├── ICoordinateTransformService      ← 좌표 변환
  │    ├── ULedIpConnection                 ← IP 통신
  │    └── EecP725R2LightCluster            ← PG 광원 제어
  │
  ├── 서브 창들 (모두 RecipeWindow DataContext 공유)
  │    ├── RecipeGlassMapWindow    ← 글래스 맵 전용 창
  │    ├── RecipeImageWindow       ← 이미지 뷰어
  │    ├── AlignTestWindow         ← 얼라인 테스트
  │    ├── PatternTableWindow      ← 패턴 테이블
  │    └── DefectWindow            ← 불량 이미지 팝업
  │
  └── GlassMapControl (mapPreviewControl) ← Cell Map 탭 내장
```

### 특징적인 설계 결정

> **DataContext 공유**: 모든 서브 창은 `DataContext = DataContext` 로 RecipeWindow와 ViewModel을 공유한다.  
> 이 덕분에 메인 창에서 Pattern을 선택하면 이미지 창에도 즉시 반영된다.

---

## 3. UI 레이아웃 분석

### 3-1. 창 전체 구조

```
RecipeWindow (1480×900, CenterOwner)
 ├── Menu Bar (File / Window / IP)
 └── Grid (2컬럼)
      ├── Col 0 (340px): 좌측 패널
      │    ├── GroupBox: Workspace
      │    │    └── 레시피명, 파일경로, New/Load/Save/Validate 버튼
      │    ├── GroupBox: Selected Cell
      │    │    └── IP 선택, 셀 표시, Pattern/Point, Contact 요약
      │    │    └── [Move Selected IP To Cell] 버튼
      │    ├── GroupBox: Manual Operation
      │    │    ├── Pattern ON / OFF
      │    │    ├── Contact On / Off / Read / Move
      │    │    ├── Refresh / Glass Map / Align Test / Align Flow / Read Axis
      │    │    └── Move CA410 / Read CA410
      │    └── GroupBox: Validation / Status
      │         └── ValidationSummary + StatusMessage 텍스트박스
      │
      └── Col 2 (*): 우측 탭 패널
           ├── TabControl (상단, *)
           │    ├── Tab: General      ← 레시피 기본 정보, Glass Size
           │    ├── Tab: Patterns     ← Pattern 목록 + 상세 편집
           │    ├── Tab: PG Mapping   ← Y Index ↔ PG Index 매핑
           │    ├── Tab: Cells        ← Cell 목록 + IP 자동 배분
           │    ├── Tab: Cell Map     ← GlassMapControl 미리보기
           │    └── Tab: Align/Control ← Align 좌표 + Contact 위치
           │
           ├── GridSplitter (8px)
           │
           └── GroupBox: Logs
                └── LogViewer
```

### 3-2. 주요 바인딩 속성

| 탭/영역 | UI 요소 | 바인딩 속성 |
|---|---|---|
| Workspace | 레시피명 | `Document.IpRecipe.Descriptor.RecipeName` |
| Workspace | 파일경로 | `CurrentFilePath` |
| Selected Cell | IP 선택 | `SelectedIp` ↔ `IpOptions` |
| Selected Cell | 셀 이름 | `SelectedCellDisplay` (읽기전용) |
| Selected Cell | Contact 요약 | `EffectiveContactPositionSummary` |
| Manual Operation | Pattern 상태 | `PatternLightSummary` |
| Manual Operation | CA-410 결과 | `Ca410Summary` |
| Validation | 검증 결과 | `ValidationSummary` |
| Validation | 상태 메시지 | `StatusMessage` |
| General | Pixel Count W/H | `Document.IpRecipe.DisplayPixelWidthCount/HeightCount` |
| General | Pixel Size W/H | `Document.IpRecipe.DisplayPixelWidthUm/HeightUm` |
| Patterns | 패턴 목록 | `Patterns` (ObservableCollection) |
| Patterns | ROI X/Y/W/H | `PrimaryPoint.RoiX/Y/Width/Height` |
| Cells | 셀 목록 | `Cells` (ObservableCollection) |
| Cell Map | 맵 미리보기 | `PreviewMapInfo`, `PreviewRotationAngle` |
| Align | Align 활성화 | `Document.AlignPlan.Enabled` |
| Align | Tolerance X/Y/T | `Document.AlignPlan.ToleranceXUm/YUm/ThetaDeg` |
| Align/Contact | Align Ref StageX | `AlignReferenceStageX` |
| Align/Contact | ContactX | `ContactX` |

---

## 4. RecipeWindow 코드-비하인드 분석

### 4-1. 클래스 개요

```csharp
public partial class RecipeWindow : System.Windows.Window
```

**주요 필드:**

| 필드 | 타입 | 설명 |
|---|---|---|
| `_glassMapWindow` | `RecipeGlassMapWindow?` | 글래스 맵 전용 창 (싱글턴) |
| `_imageWindow` | `RecipeImageWindow?` | 이미지 뷰어 창 (싱글턴) |
| `_alignTestWindow` | `AlignTestWindow?` | 얼라인 테스트 창 (싱글턴) |
| `_patternTableWindow` | `PatternTableWindow?` | 패턴 테이블 창 (싱글턴) |
| `_defectWindow` | `DefectWindow?` | 불량 이미지 팝업 (싱글턴) |
| `_defectAutoOpenTimer` | `DispatcherTimer` | 불량 발생 시 150ms 딜레이 자동 팝업 타이머 |

---

### 4-2. 생성자 주요 순서

```
1. InitializeComponent()
2. 로거 설정 (LoggingHelper.AssignUniqueCaller)
3. DefectAutoOpenTimer 초기화 (150ms)
4. RecipeEditorViewModel 생성 (6개 Func 콜백 주입)
5. DataContext = viewModel
6. viewModel.PropertyChanged 구독
7. viewModel.CurrentDefects.CollectionChanged 구독
8. mapPreviewControl.CellClicked 구독
```

---

### 4-3. 주요 메서드

#### `ShowOrActivate<T>()` (정적 제네릭 헬퍼)

```
목적: 서브 창 싱글턴 관리 패턴
입력: 기존 창 인스턴스?, 창 생성 factory Func
출력: 창 인스턴스 (새로 만들거나 기존 것 활성화)

로직:
  1. window == null 또는 !IsLoaded → factory() 호출 후 Show()
  2. 최소화 상태 → WindowState = Normal
  3. 이미 열림 → Activate()
```

---

#### `RunManualAlignFlow_Click()` (async void)

```
목적: Align Flow 실행 — 이동 → AlignTestWindow 열기 → Live 모드 시작
입력: 사용자 확인 (NoDefault 팝업)
동작:
  1. 사용자 확인
  2. MoveAlignReferencePositionOrThrowAsync() 호출 (실제 Stage 이동)
  3. AlignTestWindow 열기
  4. StartLiveModeAsync() 호출 (카메라 라이브 시작)
예외: 실패 시 StatusMessage에 에러 표시
```

> **주의**: `async void`는 예외가 호출자로 전파되지 않는다.  
> 이 메서드 내부에서 모든 예외를 `try-catch`로 처리하고 있어 안전하다.

---

#### `BuildDefectItems()` (정적)

```
목적: DefectModel 리스트를 DefectDisplayItem UI 모델로 변환
입력:
  - sourceMat: Mat? (OpenCV 이미지, 있으면 크롭 이미지 직접 추출)
  - defects: IEnumerable<DefectModel>
  - patternIndex/pointIndex: 폴백 인덱스
출력: List<DefectDisplayItem>

이미지 크롭 우선순위:
  1. defect.CropImageBytes 있으면 → ImDecode
  2. 없고 sourceMat 있으면 → BuildCropRect()로 잘라서 추출
  3. 둘 다 없으면 CropImage = null
```

---

#### `BuildCropRect()` (정적)

```
목적: 불량 좌표 기반 크롭 영역 계산 (패딩 포함)
입력: DefectModel (CameraX/Y/Width/Height), 이미지 크기
출력: OpenCvSharp.Rect

알고리즘:
  padding = Max(12, 불량 크기)
  left   = floor(CameraX - CameraWidth/2) - padding
  top    = floor(CameraY - CameraHeight/2) - padding
  right  = ceil(CameraX + CameraWidth/2) + padding
  bottom = ceil(CameraY + CameraHeight/2) + padding
  → Clamp으로 이미지 경계 내 제한
```

> **설계 의도**: 불량 주변 컨텍스트를 최소 12픽셀 확보하되,  
> 불량이 크면 불량 크기만큼 더 넓게 잘라 전체를 볼 수 있게 한다.

---

#### `ToBitmapSource()` / `NormalizeForDisplay()` (정적)

```
목적: OpenCV Mat → WPF BitmapSource 변환
지원 포맷:
  - CV_8U (1ch) → Gray8
  - CV_8U (3ch) → Bgr24
  - CV_8U (4ch) → Bgra32
  - CV_16U → 8비트 스케일 (÷256)
주의: Freeze()로 UI 스레드 외에서도 안전하게 사용 가능
```

---

#### 불량 자동 팝업 메커니즘

```
CurrentDefects.CollectionChanged 이벤트
  → OnCurrentDefectsCollectionChanged()
  → ScheduleAutoOpenDefectWindow()  ← 타이머 리셋/재시작
     ↓ (150ms 후)
  DefectAutoOpenTimer_Tick()
  → TryAutoOpenDefectWindow()
  → ShowDefectWindow(autoOpen: true)
```

> **150ms 딜레이 이유**: 불량이 여러 건 연속 추가될 때 매번 팝업이 열리지 않도록  
> 마지막 추가 후 150ms가 지난 뒤 한 번만 열리게 한다 (디바운스 패턴).

---

## 5. RecipeEditorViewModel 분석

### 5-1. 클래스 개요

```csharp
public partial class RecipeEditorViewModel : ObservableObject
```

**주요 상수:**
```csharp
// 이미지 청크 크기: 4MB 단위로 IP에서 이미지를 분할 수신
private const int DefaultImageChunkSize = 4 * 1024 * 1024;

// 미사용 Y 축 포지션 (0.0이면 해당 유닛 사용 안 함)
private const double UnusedInspectionYPositionUm = 0.0;

// 이동 완료 검증 허용 오차: 10μm
private const double MotionVerifyToleranceUm = 10.0;
```

---

### 5-2. 생성자 - 스토어 초기화 흐름

```
Vars.RecipeStore 있음?
  ├─ 예 → 그대로 사용
  └─ 아니오 → LastRecipeFilePath로 경로 결정
       ├─ 경로 있음 → RecipeStore.Open(path, autoLoad: true)
       └─ 없음   → Vars.GetRecipePath(glassSizeId, recipeId)로 기본 경로 생성

→ Vars.RecipeStore = _store (전역에 등록)
→ LoadFromStore(_store) 호출
```

---

### 5-3. 주요 ObservableProperty 목록

#### 선택 상태 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `SelectedPattern` | `PatternPlanModel?` | 현재 선택된 패턴 |
| `SelectedPoint` | `CapturePointPlanModel?` | 현재 선택된 포인트(ROI) |
| `SelectedCell` | `ConsoleCellPlan?` | 현재 선택된 셀 |
| `SelectedIp` | `int` | 현재 선택된 IP 번호 (1 또는 2) |

#### 현재 축 위치 속성

| 속성 | 설명 |
|---|---|
| `CurrentX1` | IP1(Left Bridge) X축 위치 |
| `CurrentX2` | IP2(Right Bridge) X축 위치 |
| `CurrentA1/A2` | Align 헤드 위치 |
| `CurrentY/Y2` | Stage Y축 위치 |
| `CurrentFocusZ` | Z(초점) 축 위치 |

> `PositionSummary` 속성이 위 6개를 하나의 문자열로 포매팅한다.  
> 각 축 값이 변경될 때마다 `partial void OnCurrent*Changed()` 후크로 자동 갱신된다.

#### 상태 속성

| 속성 | 설명 |
|---|---|
| `IsContactActive` | 현재 Contact(접촉) 활성 여부 |
| `CurrentImageMat` | 현재 표시 중인 OpenCV Mat 이미지 |
| `StatusMessage` | 하단 상태 메시지 (최근 동작 결과) |
| `ValidationSummary` | 레시피 검증 결과 요약 |
| `PatternLightSummary` | PG 광원 ON/OFF 상태 |
| `Ca410Summary` | CA-410 측색 결과 |

---

### 5-4. 명령(Command) 전체 목록

#### 파일 관리

| 명령 | 설명 |
|---|---|
| `NewCommand` | 새 레시피 생성 (GlassSize 선택 → 기본 문서 생성) |
| `LoadCommand` | 레시피 파일 열기 |
| `ReloadCommand` | 현재 파일 재로드 |
| `SaveCommand` | 저장 (변경 Diff 표시 후 확인) |
| `SaveAsCommand` | 다른 이름으로 저장 |
| `ValidateCommand` | 레시피 유효성 검사 |

#### 데이터 편집

| 명령 | 설명 |
|---|---|
| `AddPatternCommand` / `RemovePatternCommand` | 패턴 추가/삭제 |
| `AddCellCommand` / `RemoveCellCommand` | 셀 추가/삭제 |
| `AutoAssignIpToCellsCommand` | Stage 컬럼 기준 IP 자동 배분 |
| `ApplyIpSplitColumnCommand` | Split Y 기준 IP 배분 |
| `UseAllCellsCommand` | 모든 셀 Use=true 설정 |
| `SyncPgMappingsFromCellsCommand` | Y Index 기준 PG Mapping 동기화 |
| `LoadGlassSizeSnapshotCommand` | Glass Size Model 적용 |
| `RefreshPreviewCommand` | Cell Map 미리보기 갱신 |

#### 장비 제어 (비동기)

| 명령 | 설명 |
|---|---|
| `MoveSelectedIpToSelectedCellCommand` | 선택 셀 위치로 Stage 이동 |
| `ContactOnCommand` / `ContactOffCommand` | 접촉 On/Off |
| `TurnPatternOnCommand` / `TurnPatternOffCommand` | PG 광원 점등/소등 |
| `MoveCa410ToSelectedCellCommand` | CA-410을 선택 셀 위치로 이동 |
| `MeasureCa410Command` | CA-410 측색 실행 |
| `MoveAlignReferencePositionCommand` | Align 기준 위치로 Stage 이동 |
| `ApplyCurrentPositionToAlignCommand` | 현재 축값을 Align 위치로 저장 |
| `ApplyCurrentPositionToContactCommand` | 현재 ContactX값 저장 |

#### IP 연동 (비동기)

| 명령 | 설명 |
|---|---|
| `ConnectIpCommand` | IP 연결 (+ 자동 레시피 업로드) |
| `RefreshIpStatusCommand` | IP 상태 갱신 |
| `UploadRecipeToIpCommand` | 현재 레시피 IP에 업로드 |
| `InspectPointOnIpCommand` | 선택 Pattern/Point 단건 검사 |
| `InspectPanelOnIpCommand` | 전체 Pattern×Point 패널 검사 |
| `ClearDefectsCommand` | 불량 결과 초기화 |

---

### 5-5. 주요 메서드 상세

#### `LoadFromStore()` (핵심 초기화)

```
목적: 레시피 스토어를 로드해 전체 UI 상태를 초기화
입력: DataStore<ConsoleRecipeDocument>, 선택적 경로 오버라이드
동작:
  1. _store = store → Vars.RecipeStore 전역 등록
  2. Document = 스토어 데이터 (없으면 기본 문서 생성)
  3. _requiresSaveAs = isNewDocument 플래그
  4. RebindCoordinateModels() → CoordinateModels 컬렉션 재구성
  5. RebindCollections() → Patterns, Points, Cells 재구성
  6. SeedWorkingState() → 현재 선택 상태 초기화
  7. RefreshPreview() → Cell Map 미리보기 갱신
  8. RefreshGlassSizeInfo() → Glass Size 링크 상태 갱신
  9. _changeTracker.Reset(Document) → 변경 추적 기준선 리셋
  10. TryAutoSyncRecipeToCurrentIpAsync("load") → IP에 자동 업로드 시도
```

---

#### `SaveInternal()` (핵심 저장 로직)

```
목적: 레시피 저장 (변경 Diff 표시 포함)
입력: owner 창, showChangeConfirmation 플래그
출력: bool (저장 성공 여부)
동작:
  1. _requiresSaveAs면 SaveAsInternal()로 위임
  2. SyncCollectionsToDocument() → UI 컬렉션 → Document 동기화
  3. _changeTracker.GetChanges() → 변경 목록 계산
  4. changes.Count == 0이면 "저장할 것 없음" 반환
  5. showChangeConfirmation이면 Diff 텍스트 표시 + 확인
  6. Document.UpdatedAt = UtcNow 갱신
  7. RecipeService.ValidateOrThrow() 검증
  8. _store.Save() 파일에 쓰기
  9. _changeTracker.Reset() 기준선 리셋
```

---

#### `ConfirmClose()` (창 닫기 전 확인)

```
목적: 미저장 변경 있을 때 Yes/No/Cancel 팝업
입력: owner 창
출력: true = 닫아도 됨 / false = 닫기 취소
분기:
  - HasUnsavedChanges = false → 즉시 true
  - [예] 선택 → SaveWithoutChangeConfirmation() 후 결과 반환
  - [아니오] 선택 → true (저장 없이 닫기)
  - [취소] 선택 → false (닫기 취소)
```

---

#### `MoveSelectedIpToSelectedCellAsync()`

```
목적: 선택 셀 위치로 Stage 물리 이동
입력: SelectedCell (ConsoleCellPlan)
동작:
  1. TryResolveCellMotionTarget() → 글래스 좌표 → Stage 축 좌표 변환
  2. 사용자 확인 (StageX, Y1, Y2 표시)
  3. ConfirmAndReleaseForRowChangeAsync() → Row 변경 시 Contact Off 필요 여부 확인
  4. ControlRuntime에 3축 이동 명령 (StageX, Unit1Y, Unit2Y)
  5. 이동 응답 확인 (OK 체크)
  6. ApplyCellMotionTargetToCurrentPosition() → 현재 위치 속성 업데이트
```

---

#### `ContactOnAsync()` / `ContactOffCoreAsync()`

```
ContactOn 순서:
  1. 선택 셀 확인
  2. IsContactActive 중복 확인
  3. ContactX 설정 확인
  4. 사용자 확인
  5. ContactorX 위치로 이동 (SendControlMoveAsync)
  6. 이동 검증 (VerifyControlMoveReachedAsync, 허용 오차 10μm)
  7. FlowContact 명령 (SendControlFlowAsync)
  8. 다시 ContactX 도달 검증
  9. IsContactActive = true, _contactedRowIndex = 선택 셀.YIndex

ContactOff 순서:
  1. 사용자 확인
  2. TurnPatternOffCoreAsync() → PG 광원 OFF
  3. FlowRelease 명령
  4. IsContactActive = false, _contactedRowIndex = null
```

---

#### `InspectPanelOnIpAsync()` (수동 패널 검사)

```
목적: 편집 창에서 전체 Pattern×Point 조합을 수동 검사
경고: 메인 검사 flow와 다름 (주석으로 명시)

순서:
  1. 사용자 확인 (Steps = Patterns.Count × Points.Count 표시)
  2. SyncCollectionsToDocument()
  3. IP 연결 확인
  4. 불량 결과 초기화
  5. connection.CreateInspectionJob() → Job 생성
  6. PrepareJobAsync() → IP에 Job 준비 요청
  7. Pattern × Point 이중 반복:
     a. RunInspectionStepAsync() 실행
     b. UI 진행률 갱신 (SelectedPattern, SelectedPoint 업데이트)
  8. EndJobAsync(includeFinalResult: true) → 최종 결과 수신
  9. 불량 목록 반영
  10. 마지막 선택 Pattern/Point 이미지 로드
```

---

#### `FetchImageFromIpAsync()`

```
목적: IP에서 이미지를 청크 단위로 받아 Mat으로 변환
입력: IpImageVariant (Full / Preview / Annotated / Roi)
이미지 변종:
  - Full     → 원본 이미지, Downsample=1
  - Preview  → 미리보기, Downsample=4 (1/4 크기)
  - Annotated → 불량 마크 표시 이미지
  - Roi      → 선택 Point ROI 영역만

디코딩 경로:
  1. PixelFormat이 BMP/PNG/JPG/TIF → Cv2.ImDecode (인코딩된 포맷)
  2. MONO8/16, BGR24/48, BGRA32 → Marshal.Copy로 직접 Mat 생성
  3. 그 외 → InvalidOperationException
```

---

#### `InspectGlassReplayAsync()` ← 주석 "Manual/Test only"

```
목적: 선택 Pattern/Point 단건 수동 점검 (Grab / Inspect / GrabWithInspect)
경고: "메인 glass 검사 flow와 동일 경로로 오해하면 안 된다"(코드 주석)
      실제 glass 검사는 MainWindowViewModel.InspectGlassReplayAsync() 에서 처리함
```

---

#### `VerifyControlMoveReachedAsync()` (이동 검증)

```
목적: Stage 이동 후 실제 도달 여부 확인 (허용 오차 10μm)
입력: 이동 명령 목록, context 문자열
동작:
  1. Abs 모드 이동만 검증
  2. ReadControlStatusAsync()로 현재 축 값 수신
  3. 목표값과 실제값 차이 > 10μm → InvalidOperationException
사용처: ContactX 이동, CA-410 이동 등 정밀 위치 확인 필요 시
```

---

#### `ResolveEffectiveAlignReferencePose()`

```
목적: Align 기준 위치를 결정 (Recipe 설정 우선, 없으면 Glass Model 기본값)
반환 AlignReferencePose:
  StageX = ControlPlan.AlignReferenceStageX ?? GlassModel.AlignStageSharedPose.StageX
  LeftUnitY  = ControlPlan.AlignReferenceLeftUnitY ?? GlassModel.AlignBridgeReferencePose.LeftAlignUnitY
  RightUnitY = ControlPlan.AlignReferenceRightUnitY ?? GlassModel.AlignBridgeReferencePose.RightAlignUnitY
  StageU/V/W = ControlPlan 값 ?? GlassModel 값

설계 의도: Recipe에 명시적 override가 있으면 그것을 쓰고,
           없으면 Glass Size Model의 공장 기준 위치를 사용한다.
```

---

## 6. 핵심 알고리즘 설명

### 6-1. 변경 추적 (Change Tracking)

```csharp
// 추적 제외 속성 선언 (UI 전용이거나 자동 계산되는 값)
private readonly ObjectDiffOptions _changeDiffOptions = new ObjectDiffOptions()
    .IgnoreProperty(
        nameof(ConsoleRecipeDocument.UpdatedAt),   // 저장 시 자동 갱신
        nameof(ConsoleCellPlan.MotionStageX),       // 좌표 변환 계산값
        nameof(ConsoleCellPlan.MotionY1),           // 좌표 변환 계산값
        nameof(ConsoleCellPlan.MotionY2));          // 좌표 변환 계산값
```

**저장 플로우:**
```
편집 시작
  → _changeTracker.Reset(Document)  ← 기준선 스냅샷
편집 중
  → _changeTracker.GetChanges()     ← 실시간 Diff 계산 (HasUnsavedChanges 등)
저장 시
  → GetChanges()로 Diff 텍스트 표시
  → 확인 후 Save()
  → _changeTracker.Reset()          ← 기준선 갱신
```

---

### 6-2. 셀 → Stage 좌표 변환 알고리즘

```
입력: ConsoleCellPlan (CellRectGlassUm.X, Y, Width, Height)
      IpNo (1 = Left Bridge, 2 = Right Bridge)

1. 셀 중심 유리 좌표 계산
   glassCenter = (X + Width/2, Y - Height/2)  ← Y축 방향 주의

2. Inspect 카메라 오프셋 보정
   alignTarget = CoordinateTransformService.ResolveAlignTarget(
       glassCenter, EMRConfig.HeadOffsets.InspectCameraFromAlignUm)

3. Bridge 보정 행렬 적용 (AffineAxisTransform)
   axisTarget = CoordinateTransformService.ToBridgeAxes(alignTarget, transform)
   → axisTarget.X = Bridge 이동 축 값
   → axisTarget.Y = Stage 이동 축 값

4. IP 번호에 따른 Y1/Y2 분배
   IP1 (Left):  StageX=axisTarget.Y, Y1=axisTarget.X, Y2=0 (미사용)
   IP2 (Right): StageX=axisTarget.Y, Y1=0 (미사용), Y2=axisTarget.X
```

---

### 6-3. PG Mapping 동기화 알고리즘

```
목적: YIndex별 사용할 PG(Pattern Generator) 장치 인덱스 결정

기존 PgMappings (이전 설정값)
  ↓
현재 Cells에서 사용 중인 YIndex 목록 추출 (중복 제거, 정렬)
  ↓
각 YIndex에 대해:
  기존 매핑 있음? → 기존 PgIndex 사용 (사용자 설정 보존)
  없음?           → YIndex == PgIndex (기본 1:1 매핑)
  ↓
PgMappings 컬렉션 갱신 → Document.ControlPlan.PgMappings 저장
```

---

### 6-4. IP 자동 배분 알고리즘 (`AutoAssignIpToCells`)

```
RecipeService.AutoAssignIpNumbers(Document) 호출
  ↓
내부 로직 (RecipeService):
  XIndex(행 번호)와 IpSplitColumn을 기준으로
  YIndex가 SplitColumn 미만 → IP1
  YIndex가 SplitColumn 이상 → IP2
  (실제 구현은 RecipeService에 있음, 이 파일에서는 호출만)
```

---

### 6-5. 이미지 디코딩 전략

```
IP에서 수신한 이미지 bytes
  ↓
PixelFormat 확인
  ├─ BMP/PNG/JPG/TIF → Cv2.ImDecode() (표준 압축 포맷)
  └─ RAW 포맷
       ├─ MONO8  → CV_8UC1  (1ch 8bit, 1 byte/px)
       ├─ MONO16 → CV_16UC1 (1ch 16bit, 2 bytes/px)
       ├─ BGR24  → CV_8UC3  (3ch 8bit, 3 bytes/px)
       ├─ BGR48  → CV_16UC3 (3ch 16bit, 6 bytes/px)
       └─ BGRA32 → CV_8UC4  (4ch 8bit, 4 bytes/px)
  ↓
RAW의 경우: 예상 바이트 수 = Width × Height × BPP
  → 실제 길이 불일치 시 InvalidOperationException
  → Marshal.Copy로 bytes → Mat.Data 직접 복사
  ↓
WPF 표시용: NormalizeForDisplay()
  → CV_8U면 Clone 반환
  → CV_16U면 ÷256 하여 8비트 변환
```

---

## 7. 데이터 흐름 다이어그램

### 레시피 저장 플로우

```
사용자 [Save] 클릭
  → SaveCommand → SaveWithChangeReport()
  → SyncCollectionsToDocument()          ← UI → Document 동기화
       ├─ Patterns → Document.IpRecipe.Patterns
       ├─ Points   → Document.IpRecipe.Points
       └─ Cells    → Document.GlassMap.Cells
  → _changeTracker.GetChanges()          ← 변경 목록 계산
  → Diff 팝업 표시
  → RecipeService.ValidateOrThrow()      ← 유효성 검사
  → _store.Save()                        ← 파일 쓰기
  → _changeTracker.Reset()               ← 기준선 리셋
  → TryAutoSyncRecipeToCurrentIpAsync()  ← IP에 자동 업로드
```

### IP 검사 플로우 (단건)

```
사용자 [Inspect Selected Point] 클릭
  → InspectPointOnIpAsync()
  → ExecuteManualPointOnIpAsync(GrabWithInspect, Annotated)
       → connection.GrabWithInspectPointAsync(Pattern, Point, ...)
       → FetchImageFromIpAsync(Annotated)   ← 이미지 수신
       → CurrentImageMat = 수신된 Mat
       → UpsertDefectsForImage()            ← 불량 목록 갱신
       → CurrentDefects 갱신
  ← CollectionChanged 이벤트
  → ScheduleAutoOpenDefectWindow()          ← 150ms 후 DefectWindow 열기
```

---

## 8. 가정 및 제한 사항

### 가정

1. **IP 번호는 1 또는 2**: IP1 = Left Bridge, IP2 = Right Bridge로 하드코딩된 가정이 있다. `SelectedIp == 1` 조건이 곳곳에 사용된다.

2. **ContactX 단일값**: Contact 위치는 X축 하나의 값으로 결정된다. Y축이나 Z축은 Flow 명령(FlowContact)이 자동 처리한다고 가정한다.

3. **이동 검증 허용 오차**: `MotionVerifyToleranceUm = 10.0μm`. 이 값이 너무 엄격하면 정상 이동에서도 예외가 발생할 수 있다.

4. **PG 인덱스가 0부터**: `pgNo < 0 || pgNo >= endpoints.Count` 체크를 보면 PG 인덱스가 0-based라고 가정한다.

5. **Glass Size Model 외부 파일**: `Vars.WorkDir` 아래의 파일에서 Glass Size 정보를 로드한다. 파일이 없으면 링크 상태가 "찾을 수 없음"으로 표시된다.

### 제한 사항

1. **수동 검사만 지원**: `InspectPointOnIpCommand`, `InspectPanelOnIpCommand`는 편집 창 전용 수동 경로다. 실제 자동 검사는 `MainWindowViewModel`에서 별도 경로로 실행된다.

2. **단일 IP 동시 제어**: Recipe Editor에서는 `SelectedIp` 한 개만 제어한다. 메인 검사에서처럼 다중 IP 병렬 처리를 지원하지 않는다.

3. **이미지 메모리 관리**: `CurrentImageMat`은 `IDisposable`인 `Mat` 타입이지만, 명시적 Dispose가 없다. 새 이미지가 할당될 때 이전 것이 GC에 의존한다.

4. **좌표 변환 의존**: `ICoordinateTransformService`와 `GlassSizeModel`의 캘리브레이션 데이터가 없으면 Stage 이동 계산이 실패한다.

5. **`async void` 사용**: `RunManualAlignFlow_Click`이 `async void`다. WPF 이벤트 핸들러에서 불가피하지만, 예외를 `try-catch`로 처리하고 있어 무한 대기나 앱 크래시는 없다.

---

## 9. 다음으로 분석해야 할 코드

지금까지 Recipe Editor의 전체 구조와 동작을 파악했다.  
이 코드가 의존하는 핵심 서비스들을 순서대로 분석하면 된다.

### 우선순위 1 — RecipeService (최우선)

| 파일/클래스 | 이유 |
|---|---|
| **`RecipeService`** | Recipe Editor의 모든 데이터 변환이 여기서 일어남. `BuildGlassMapInfoFromRecipe`, `RegenerateCellsFromSnapshot`, `AutoAssignIpNumbers`, `ValidateOrThrow` 등 핵심 로직 전부 |

### 우선순위 2 — 좌표 변환 계층

| 파일/클래스 | 이유 |
|---|---|
| **`ICoordinateTransformService` / `CoordinateTransformService`** | `TryResolveCellMotionTarget`의 실체. 유리 좌표 → Stage 축 좌표 변환 핵심 알고리즘 |
| **`GlassSizeModel` / `GlassSizeStore`** | Align 캘리브레이션 데이터 구조와 로드 방식 |

### 우선순위 3 — IP 통신 계층

| 파일/클래스 | 이유 |
|---|---|
| **`ULedIpConnection`** | `CreateInspectionJob`, `PrepareJobAsync`, `RunInspectionStepAsync`, `EndJobAsync`, `FetchImageAsync` 등 IP 프로토콜 전체 |
| **`PanelInspectionJob`** | 검사 Job의 데이터 구조 (JobId, Pattern, Point 조합) |

### 우선순위 4 — 데이터 인프라

| 파일/클래스 | 이유 |
|---|---|
| **`ObjectChangeTracker<T>` / `ObjectDiffFormatter`** | 변경 추적과 Diff 표시 방식. 어떤 기준으로 변경을 감지하는지 |
| **`DataStore<T>`** | 레시피 파일을 JSON으로 읽고 쓰는 방식, `RecipeStore.Open/CreateNew` |
| **`ConsoleRecipeDocument`** | Recipe의 전체 데이터 모델 구조 파악 |

### 우선순위 5 — 하드웨어 제어

| 파일/클래스 | 이유 |
|---|---|
| **`ULedControlConnection`** | `SendMoveAsync`, `SendFlowAsync`, `RefreshStatusAsync` 등 Stage 제어 프로토콜 |
| **`EecP725R2LightCluster`** | PG(Pattern Generator) 광원 제어 프로토콜 |
| **`Ca410MeasurementClient`** | CA-410 색도계 측정 프로토콜 |

---

> **추천 다음 분석**: `RecipeService`부터 시작하는 것을 강력히 권장한다.  
> Recipe Editor의 "Save" 버튼 하나가 내부적으로 `RecipeService.ValidateOrThrow()` →  
> `RegenerateCellsFromSnapshot()` → `RefreshCellIndexesForPanelAngle()` 등  
> 여러 서비스를 순서대로 호출하기 때문에, 이 서비스를 이해하면  
> Recipe가 어떻게 만들어지고 검증되는지 전체 그림이 완성된다.
