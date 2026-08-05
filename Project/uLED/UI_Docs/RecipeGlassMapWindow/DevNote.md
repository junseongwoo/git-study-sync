# RecipeGlassMapWindow 인수인계 개발 노트

작성일: 2026-08-03

## 1. 유지보수자가 먼저 알아야 할 구조

이 Window는 독립 ViewModel을 만들지 않는다. `RecipeWindow`와 같은 `RecipeEditorViewModel`을 공유하는 얇은 편집 View다.

```text
RecipeWindow
  ├─ DataContext: RecipeEditorViewModel
  ├─ _glassMapWindow: RecipeGlassMapWindow
  └─ OpenGlassMapWindow_Click
       └─ RecipeGlassMapWindow
            ├─ Owner = RecipeWindow
            └─ DataContext = RecipeWindow.DataContext
```

핵심 데이터 책임:

```text
ConsoleRecipeDocument
└─ GlassMap: ConsoleGlassMapPlan
   ├─ GlassSizeId
   ├─ GlassSizeSnapshot
   ├─ GlassMapDesignSnapshot       // 설계 원본
   │  ├─ GlassWidthUm
   │  ├─ GlassHeightUm
   │  └─ Coordinates
   │     └─ GlassCoordinateModel
   │        ├─ Name
   │        └─ Coordinate: SMDCoordInfo
   └─ Cells                        // 실행용 전개 결과
      └─ ConsoleCellPlan
```

공식 Docs의 가장 중요한 불변 조건은 `GlassMapDesignSnapshot`과 `Cells`의 역할을 혼합하지 않는 것이다.

## 2. 주요 파일과 역할

| 파일 | 역할 |
|---|---|
| `RecipeWindow.xaml` | `레시피 Glass Map` 메뉴 정의 |
| `RecipeWindow.xaml.cs` | 창 단일 인스턴스 생성/활성화와 소유 창 종료 처리 |
| `RecipeGlassMapWindow.xaml` | Preview, 명령, Coordinate Editor UI |
| `RecipeGlassMapWindow.xaml.cs` | Window 상태 머신만 관리 |
| `RecipeEditorViewModel.cs` | 모든 command, binding property, 동기화, import, preview, 셀 재생성 |
| `GlassCoordinateViewModel.cs` | `GlassCoordinateModel` 변경 알림 adapter |
| `GlassMapDesignModel.cs` | `GlassCoordinateModel`, `GlassMapDesign` 저장 모델 |
| `GlassMapInfo.cs` | `SMDCoordInfo`, `RoiInfo`, `GlassInfoHelper.MakeCells` |
| `RecipeService.cs` | 실행용 Cell 전개, 좌표 변환, 속성 병합, index/IP 처리, validation |
| `GlassMapControl.cs` | Glass/Cell 렌더링과 셀 hit test |

## 3. 메뉴와 Window 생명주기

### 3.1 열기

`OpenGlassMapWindow_Click`은 `ShowOrActivate`를 사용한다.

`[추론] (코드 확인)`

- 창이 없거나 `IsLoaded=false`: 새로 생성 후 `Show()`
- 열려 있음: 최소화 상태를 Normal로 복원 후 `Activate()`
- `ShowDialog()`가 아니므로 RecipeWindow와 병행 편집 가능
- 같은 VM을 공유하므로 양쪽 UI에서 동일 Document를 편집

### 3.2 닫기

`RecipeGlassMapWindow`는 표준 `WindowProcessStateMachine` 패턴을 따른다.

```text
Constructor -> Initializing
Loaded      -> Ready
Closing     -> Closing 진입 시도, 중복 닫기 차단
Closed      -> Closed
```

RecipeWindow가 닫힐 때 `_glassMapWindow`도 닫는다.

## 4. XAML 바인딩 지도

### 4.1 Preview

| Target | Source | Mode/특성 |
|---|---|---|
| `GlassMapControl.MapInfo` | `GlassMapEditPreviewMapInfo` | Snapshot 직접 Preview |
| `RotationAngle` | `GlassMapEditPreviewRotationAngle` | getter가 항상 0 |
| `ZoomFactor` | `PreviewZoomFactor` | 기본 1.0 |
| `ShowIngressDirection` | `False` | 상수 |
| `ShowPartitionNameOverlay` | `False` | 상수 |
| 상태 TextBox | `StatusMessage` | OneWay, ReadOnly |

### 4.2 Snapshot 명령/정보

| Target | Source |
|---|---|
| Add Copy | `AddCoordinateModelCommand` |
| Remove | `RemoveCoordinateModelCommand` |
| Import From Recipe | `ImportGlassMapFromRecipeCommand` |
| Generate Cells | `RegenerateCellsFromCoordinatesCommand` |
| Refresh Preview | `RefreshPreviewCommand` |
| Recipe | `RecipeId` |
| Glass Size | `GlassSizeModelInfo` |
| Snapshot Summary | `CoordinateSummary` |
| ListBox Items | `CoordinateModels` |
| ListBox SelectedItem | `SelectedCoordinateModel` |

### 4.3 Editor

모든 Text 입력은 `UpdateSourceTrigger=PropertyChanged`다.

| UI | VM 속성 | 모델 필드 |
|---|---|---|
| Name | `SelectedCoordinateModel.Name` | `GlassCoordinateModel.Name` |
| CELL_SIZE_X | `CellSizeX` | `SMDCoordInfo.CELL_SIZE_X` |
| CELL_SIZE_Y | `CellSizeY` | `SMDCoordInfo.CELL_SIZE_Y` |
| CELL_X_COUNT | `CellX` | `SMDCoordInfo.CELL_X` |
| CELL_Y_COUNT | `CellY` | `SMDCoordInfo.CELL_Y` |
| OFFSET_E_X | `OffsetEX` | `SMDCoordInfo.OFFSET_E_X` |
| OFFSET_E_Y | `OffsetEY` | `SMDCoordInfo.OFFSET_E_Y` |
| CELL_DIST_X | `CellDistX` | `SMDCoordInfo.CELL_DIST_X` |
| CELL_DIST_Y | `CellDistY` | `SMDCoordInfo.CELL_DIST_Y` |
| BLOCK_DIST_X | `BlockDistX` | `SMDCoordInfo.BLOCK_DIST_X` |
| BLOCK_DIST_Y | `BlockDistY` | `SMDCoordInfo.BLOCK_DIST_Y` |
| BLOCK_COUNT_X | `BlockCountX` | `SMDCoordInfo.BLOCK_COUNT_X` |
| BLOCK_COUNT_Y | `BlockCountY` | `SMDCoordInfo.BLOCK_COUNT_Y` |

`GlassCoordinateViewModel`은 모델을 clone하지 않고 직접 감싼다. float setter는 `0.0001f` epsilon으로 동일값 판단을 하고 나머지는 `EqualityComparer<T>.Default`를 사용한다.

## 5. Command 초기화 위치

`RecipeEditorViewModel` 생성자에서 다음 command가 만들어진다.

```csharp
ImportGlassMapFromRecipeCommand = new RelayCommand(ImportGlassMapFromRecipe);
RefreshPreviewCommand = new RelayCommand(RefreshPreview);
AddCoordinateModelCommand = new RelayCommand(AddCoordinateModel);
RemoveCoordinateModelCommand = new RelayCommand(
    RemoveSelectedCoordinateModel,
    CanRemoveSelectedCoordinateModel);
RegenerateCellsFromCoordinatesCommand = new RelayCommand(RegenerateCellsFromCoordinates);
```

`RemoveCoordinateModelCommand`만 선택 유무 기반 `CanExecute`를 가진다. Import/Generate/Refresh에는 별도 사전 CanExecute가 없고 실행 중 예외를 catch하여 `StatusMessage`에 표시한다.

## 6. Coordinate 바인딩 초기화

`RebindCoordinateModels()` 진행:

```text
기존 CollectionChanged 해제
  -> 기존 item PropertyChanged 해제
  -> UI collection Clear
  -> Document.GlassMap/Snapshot/Coordinates null 방어
  -> 모델별 GlassCoordinateViewModel 생성
  -> item PropertyChanged 연결
  -> 비어 있으면 기본 Name=A 모델 추가
  -> CollectionChanged 연결
  -> SyncCoordinateModelsToDocument
  -> 첫 항목 선택
  -> RefreshGlassMapEditPreview
  -> CoordinateSummary 알림
```

`[추론] (코드 확인)` 빈 snapshot을 로드해도 이 메서드가 기본 Coordinate를 만들고 즉시 snapshot에 기록한다. 따라서 UI에서 열린 이후 in-memory snapshot이 완전히 빈 Coordinates 상태로 유지되지 않는다.

## 7. 변경 알림과 자동 동기화

### 7.1 Item 속성 변경

```text
CalcTextBox/TextBox
 -> GlassCoordinateViewModel setter
 -> PropertyChanged
 -> CoordinateModel_PropertyChanged
 -> SyncCoordinateModelsToDocument
 -> RefreshGlassMapEditPreview
 -> SelectedCoordinateModelDisplay 알림
```

### 7.2 Collection 변경

```text
Add/Remove
 -> CoordinateModels_CollectionChanged
 -> item event 연결/해제
 -> SyncCoordinateModelsToDocument
 -> RefreshGlassMapEditPreview
 -> CoordinateSummary 알림
 -> Remove command CanExecute 갱신
```

### 7.3 Snapshot 동기화

`SyncCoordinateModelsToDocument()`는 다음 세 가지를 쓴다.

```csharp
snapshot.GlassWidthUm = currentGlassSize.Width;
snapshot.GlassHeightUm = currentGlassSize.Height;
snapshot.Coordinates = CoordinateModels.Select(x => x.Model).ToList();
```

`[추론] (코드 확인)` Snapshot 내부의 `GlassWidthUm/GlassHeightUm`은 사용자 입력값이 아니라 현재 Recipe GlassSize에서 매번 갱신된다.

## 8. Preview 경로

### 8.1 편집 Preview

```text
RefreshGlassMapEditPreview
  -> Snapshot/Coordinates null 방어
  -> ResolveCurrentGlassMapNamingPolicy
  -> GlassMapInfo
       GlassSize = GetCurrentGlassSize()
       CutMark = policy.CuttingMarkPosition
       CellInfo = GlassInfoHelper.MakeCells(
           Snapshot.Coordinates,
           policy,
           currentGlassSize)
  -> GlassMapEditPreviewMapInfo setter
  -> GlassMapControl render invalidation
```

편집 Preview는 `GlassMap.Cells`를 우회하여 Coordinate snapshot에서 직접 만들어진다. 최신 공식 change-log가 요구한 동작이다.

### 8.2 일반 RefreshPreview

```text
SyncCollectionsToDocument
 -> RefreshCellMotionTargets
 -> PreviewMapInfo = BuildGlassMapInfoFromRecipe(Cells 기반)
 -> PreviewRotationAngle = GetDisplayRotationAngleDeg
 -> RefreshGlassMapEditPreview(Snapshot 기반)
```

한 command에서 Cells 기반 Preview와 Snapshot 기반 Preview를 둘 다 갱신하지만 이 Window가 바인딩한 것은 후자다.

### 8.3 회전 정책

```csharp
public int GlassMapEditPreviewRotationAngle => 0;
```

이 상수 getter 때문에 `_previewRotationAngle` observable field와 무관하게 이 Window는 항상 0°다. 운영 Display와 편집 도면의 목적을 분리한 명시적 정책이다.

## 9. GlassMapControl 동작

`GlassMapControl`은 `FrameworkElement` 렌더링 기반 사용자 컨트롤이다.

주요 dependency property:

- `MapInfo`
- `RotationAngle`
- `ZoomFactor`
- `CellOrigin`
- `SelectedCellId`
- `IsUseToggleMode`
- `ShowPartitionNameOverlay`
- `ShowIngressDirection`
- `IngressDirection`
- `ReplayDefectOverlays`
- `InspectionCellStates`
- `GlassPresent`

이 Window에서는 앞의 3개와 두 show flag만 지정한다.

렌더링:

```text
OnRender
  -> content/glass drawing rect 계산
  -> cached base map drawing
       background
       glass outline + cut mark
       cells
       partition overlays (현재 off)
       ingress (현재 off)
  -> glass presence overlay (미바인딩)
  -> inspection state overlay (미바인딩)
  -> selected cell overlay
  -> replay defect overlay (미바인딩)
```

클릭:

```text
OnMouseLeftButtonDown
  -> HitTestCell
  -> IsUseToggleMode면 toggle event
  -> 아니면 SelectedCellId 설정 + CellClicked event
```

`[추론] (코드 확인)` 이 Window는 event와 `SelectedCellId`를 VM에 바인딩하지 않으므로 클릭 선택은 컨트롤 내부 시각 상태로 끝난다.

## 10. 셀 생성 알고리즘

### 10.1 MakeCells 구조

```text
Coordinates 순회
  -> 각 Coordinate MakeCell
  -> RoiInfo.Id를 전체 목록 기준 1부터 순차 부여
  -> merged list 반환
```

각 Coordinate의 `Group`은 `coordinateIndex + 1`이다. `MapColumnIndex`, `MapRowIndex`는 Coordinate 내부 전역 0-base index다.

### 10.2 Block 분배

```csharp
blockCount = Math.Max(1, BLOCK_COUNT);
totalCount = Math.Max(0, CELL_COUNT);
baseCount = totalCount / blockCount;
remainder = totalCount % blockCount;
count[i] = baseCount + (i < remainder ? 1 : 0);
```

따라서 block 수는 총 Cell 수를 증가시키지 않는다. 총 셀 수는 Coordinate별 `max(0, CELL_X) × max(0, CELL_Y)`다.

### 10.3 위치식

```text
blockBaseX = OFFSET_E_X + blockX × BLOCK_DIST_X
blockBaseY = OFFSET_E_Y + blockY × BLOCK_DIST_Y

naturalX = blockBaseX + localX × CELL_DIST_X
naturalY = blockBaseY + localY × CELL_DIST_Y
```

FirstCellPosition mirror:

```text
startsOnRight: X = glassWidth  - naturalX - cellWidth
otherwise:     X = naturalX

startsOnBottom:Y = glassHeight - naturalY - cellHeight
otherwise:     Y = naturalY
```

`RectangleF`를 만든 후 `Rectangle.Round`으로 정수 µm 사각형이 된다.

### 10.4 이름 생성

```text
coordinate.Name의 첫 letter/digit -> uppercase partition prefix
없음 -> coordinate index 기반 A..Z, 0..9, 이후 ?

X label -> GlassSize XRule
Y label -> GlassSize YRule
tokens  -> GlassSize TokenOrder
partition 포함 -> UsePartitionName
```

이름 규칙을 변경할 때 `docs/glass-map.md`의 고정 4문자 설명을 그대로 구현 기준으로 사용하지 말아야 한다. 최신 기준은 `GlassMapNamingPolicy`다.

## 11. Generate Cells 세부 흐름

```text
RegenerateCellsFromCoordinates
  -> SyncCoordinateModelsToDocument
  -> RecipeService.RegenerateCellsFromSnapshot(
       Document,
       GetCurrentGlassSize(),
       preserveExistingValues: true)
       -> previous Cells clone
       -> BuildCellsFromGlassMapDesign
            -> MakeCells
            -> RoiInfo -> ConsoleCellPlan
            -> Y desc, X asc 정렬
       -> MergeCellAttributes
       -> AssignCellIndexesFromCellMap
       -> EnsureIpAssignment
       -> Document.GlassMap.Cells 교체
  -> RebindCollections
  -> RefreshPreview
```

### 11.1 RoiInfo → ConsoleCellPlan

`Coord.CellCornerToGlassCentered`로 좌상단/+Y down 좌표를 글래스 중심/+Y up 좌표로 변환한다.

복사 필드:

- `Id` → `CellId`
- `Name`
- `Use`
- `IPNo` → `IpNo`
- `RoundCell`
- `Group` → `MapGroupIndex`
- `MapColumnIndex`
- `MapRowIndex`
- 변환 Rect → `CellRectGlassUm`

### 11.2 기존 속성 병합

`MergeCellAttributes`는 다음 순서로 기존 Cell을 찾는다.

```text
1. CellId exact match
2. CellId match 실패 시 Name case-insensitive match
```

보존 필드:

- `Use`
- `IpNo`
- `RoundCell`
- `UserDefinedName`

`[추론]` geometry와 ID 순서가 크게 바뀌는 편집에서는 ID 우선 match가 물리적으로 다른 Cell에 속성을 이어 줄 수 있다. 위치 기반 match가 아니므로 UI/테스트에서 속성 재검토가 필요하다.

### 11.3 XIndex/YIndex

공식 기준과 코드가 일치한다.

1. GlassSize bridge calibration과 Unit1 inspect camera offset을 사용해 각 Cell center의 Unit1 기준 StageX/InspectionUnit1Y target 계산
2. `MapColumnIndex`, `MapRowIndex` 중 group 평균 StageX span이 더 큰 축을 XIndex group 축으로 선택
3. X group을 평균 StageX 오름차순으로 0-base 인덱싱
4. 같은 X group 안에서 남은 map 축을 평균 Unit1Y 오름차순으로 0-base YIndex 부여

PanelAngle은 XIndex/YIndex 계산 기준으로 사용하지 않는다.

## 12. Add/Remove 구현 메모

### AddCoordinateModel

- 선택이 있으면 `Model.Clone()`
- 없으면 `new GlassCoordinateModel()`
- 새 Name은 `GetNextCoordinateModelName()`
- A~Z 뒤에는 `Coord {index+1}`
- collection handler가 snapshot/preview 갱신

`SMDCoordInfo` 생성자 기본값은 750×650급 기본 배치를 전제로 한 값이 남아 있다.

```text
CELL_X/Y = 12 / 15
BLOCK_COUNT_X/Y = 2 / 2
OFFSET_E_X/Y = 24998 / 25003
CELL_DIST_X/Y = 59167 / 43571
CELL_SIZE_X/Y = 54167 / 38571
BLOCK_DIST_X/Y = 350002 / 299997
```

`[추론] (코드 확인)` 이 기본값은 현재 GlassSize 크기에 따라 자동 scaling되지 않는다. 새 Coordinate 생성 후 Preview로 적합성을 확인해야 한다.

### RemoveSelectedCoordinateModel

- 선택 없으면 command disabled
- No-default confirmation
- 제거 인덱스 기억
- 마지막 항목 삭제 시 `AddCoordinateModel()` 호출
- 아니면 인접 항목 선택

## 13. Import From Recipe 구현 메모

```text
_showOpenFileDialog
 -> RecipeStore.Open(path, autoLoad:true)
 -> source.GlassMap.GlassMapDesignSnapshot required
 -> CloneGlassMapDesign(JSON round-trip)
 -> current snapshot replace
 -> _currentGlassMapDesignFilePath = null
 -> RebindCoordinateModels
 -> RegenerateCellsFromSnapshot(current GlassSize, preserve=true)
 -> RebindCollections
 -> RefreshPreview
```

중요 책임 경계:

- source GlassSize는 적용하지 않음
- source Cells를 직접 복사하지 않음
- current GlassSize/naming policy로 새 Cells 생성
- current previous Cells 속성은 merge 가능

`[추론] (코드 확인)` JSON round-trip clone이므로 모델에 직렬화되지 않는 상태가 추가되면 Import에서 보존되지 않는다. 현재 모델은 단순 저장 속성으로 구성되어 문제없다.

## 14. Save/Validate의 중요 함정

`SyncCollectionsToDocument()`:

```text
SyncCoordinateModelsToDocument
Document.GlassMap.Cells = Cells.ToList()
RecipeService.RefreshCellIndexes
  -> 기존 Cell 이름 복원
  -> XIndex/YIndex 갱신
PG mapping sync
```

이 메서드에는 `RegenerateCellsFromSnapshot`이 없다.

따라서 Coordinate geometry 변경 후 Generate Cells를 누르지 않아도 다음과 같은 불일치 상태를 저장할 가능성이 있다.

```text
Snapshot.Coordinates = new design
Cells.CellRectGlassUm = old runtime geometry
```

`ValidateOrThrow`는 다음을 확인하지만 Snapshot과 Cells geometry 동일성은 비교하지 않는다.

- GlassSizeId 존재
- Cells가 비어 있지 않음
- 각 Cell Rect 존재
- Cell width/height > 0
- XIndex/YIndex >= 0
- 표시 이름 중복/유효성
- GlassSize model 유효성
- 그 밖의 Pattern/Point/검사 파라미터

유지보수 개선 후보:

- Snapshot에서 임시 Cells를 재생성하여 geometry/name/count hash를 현재 Cells와 비교하는 validator
- dirty flag: Coordinate 변경 후 `CellsNeedRegeneration=true`
- Save/Validate 전 명시적 warning

단, 자동 재생성은 기존 Use/IP/UserDefinedName 보존 정책과 운영 변경 범위를 동반하므로 사용자 확인 없이 fallback처럼 넣으면 안 된다.

## 15. 범위/검증 현황

| 값 | UI 제한 | 생성 처리 | Recipe validation |
|---|---|---|---|
| CELL_SIZE_X/Y | Minimum=0 | 그대로 사용 후 정수 round | 생성 Cell은 >0 필요 |
| CELL_X/Y | 없음 | `max(0, value)` | Coordinate 값 직접 검증 없음 |
| BLOCK_COUNT_X/Y | 없음 | `max(1, value)` | 직접 검증 없음 |
| OFFSET_E_X/Y | 없음 | 그대로 사용 | 글래스 범위 검증 없음 |
| CELL_DIST_X/Y | 없음 | 그대로 사용 | 중첩/역방향 검증 없음 |
| BLOCK_DIST_X/Y | 없음 | 그대로 사용 | 중첩/역방향 검증 없음 |
| Name | 없음 | 첫 영문/숫자를 prefix로 사용 | 최종 Cell 표시 이름 검증 영향 |

`[추론]` XAML이 size에 `Minimum=0`을 두었지만 validation은 positive를 요구하므로 UI와 저장 조건에 경계 차이가 있다. UI 최소값을 양수로 바꾸거나 validation 메시지를 사전 표시할 수 있으나 실제 최소 µm 정책은 공식 Docs에 정의되어 있지 않다.

## 16. 공식 Docs와 코드 차이/잔여물

### 16.1 과거 전역 Template 설명

`docs/glass-map.md` 일부는 `GlassMapDesignViewModel`과 전역 JSON을 현재 편집의 중심처럼 설명한다. 최신 change-log에서는 전역 편집 Window/VM을 삭제했고 현재 레시피 snapshot 구조를 기준으로 한다.

### 16.2 Snapshot Summary

`CoordinateSummary`는 `_currentGlassMapDesignFilePath`를 보여 준다. 현재 XAML에는 `SaveSnapshot`, `SaveSnapshotAs`, Template import/export 버튼이 없고 `Import From Recipe`는 해당 경로를 null로 만든다.

`[추론]` 이 문자열의 `파일 없음`은 사용자가 snapshot 부재로 오해할 가능성이 있다. `Coordinate N개 / Recipe embedded snapshot`처럼 현재 구조에 맞는 문구로 정리할 후보가 있다.

### 16.3 VM의 비노출 Template command

`RecipeEditorViewModel`에는 `SaveSnapshotCommand`, `SaveSnapshotAsCommand`와 관련 dialog delegate가 남아 있지만 현재 RecipeGlassMapWindow XAML에서 노출하지 않는다. 최신 공식 change-log의 “template import/export 버튼 제거”와 동작상 충돌하지 않으나 dead/legacy surface 여부를 후속 검토할 수 있다.

## 17. 전체 프로젝트 영향 경로

```text
Coordinate edit
 -> GlassMapDesignSnapshot
 -> Generate Cells
 -> ConsoleCellPlan
    ├─ CellRectGlassUm
    │   └─ cell center
    │       └─ bridge calibration + tool offset
    │           └─ StageX / Unit1Y / Unit2Y target
    ├─ MapColumn/MapRow
    │   └─ XIndex / YIndex
    │       ├─ line/cell 실행 순서
    │       ├─ IP Auto Assign / Split
    │       └─ PG Mapping
    ├─ IpNo
    │   └─ IP1=Unit1, IP2=Unit2
    ├─ Use
    │   └─ 검사 대상 포함 여부
    └─ DisplayName
        ├─ Cell Job 이름
        ├─ 원본/결과 폴더와 파일명
        └─ 로그/UI 표시
```

Glass Map 변경은 UI 표시 변경에 그치지 않고 motion, IP job, PG, 결과 저장 이름까지 영향을 줄 수 있다.

## 18. 테스트 포인트

### 18.1 UI/바인딩

- 창을 두 번 열 때 단일 창이 활성화되는지
- RecipeWindow와 동일 RecipeId/GlassSize가 표시되는지
- 각 필드 입력 즉시 Preview가 갱신되는지
- Coordinate 선택 시 Editor 값이 바뀌는지
- 마지막 Coordinate 삭제 후 기본 항목이 생기는지

### 18.2 생성식

- `12 cells / 2 blocks` → `6+6`
- `15 cells / 2 blocks` → `8+7`
- FirstCellPosition 4방향별 X/Y mirror
- CELL_DIST와 BLOCK_DIST가 각각 intra-block / inter-block 시작점 간격으로 적용되는지
- 여러 Coordinate의 ID가 전체 기준 연속인지
- naming policy token 순서/label rule 반영

### 18.3 런타임 결과

- Generate 전후 `Cells.Count`
- CellRect 좌상단 설계좌표 → 중심 실행좌표 변환
- XIndex/YIndex와 모션 target
- IP 보존/자동 배정
- Use/RoundCell/UserDefinedName 보존
- PG mapping 동기화

### 18.4 위험 회귀

- Coordinate만 수정하고 Generate하지 않은 상태에서 Validate/Save 경고 부재
- ID 순서가 바뀌는 대규모 layout 변경 후 속성 오매칭
- 다른 GlassSize Recipe import 후 글래스 외곽 초과
- 0 size, 음수 count/distance, 0 block 입력
- 동일 partition prefix로 최종 Cell 이름 중복

## 19. 추가 확인이 필요한 항목

- 현장 공정별 Coordinate 입력 허용 범위와 최소 pitch
- 셀 중첩/글래스 외곽 초과를 오류로 볼지 경고로 볼지
- 대규모 재생성 시 기존 속성 보존 기준을 ID/이름/위치 중 무엇으로 확정할지
- Coordinate 변경 dirty 상태를 UI에 어떻게 표시할지
- `Snapshot Summary`의 legacy 파일 상태를 제거할지
- 비노출 Snapshot template command를 완전히 삭제할지

위 항목은 공식 Docs나 현재 UI에 확정 기준이 없으므로 임의 변경하지 말고 사용자/제작자 확인이 필요하다.

## 20. 2차 검증 결과

다음 구현 경로를 서로 교차 검증했다.

- 메뉴 이벤트 ↔ Window 생성/재활성화
- XAML command ↔ ViewModel command 초기화 ↔ 실제 private method
- XAML field ↔ `GlassCoordinateViewModel` ↔ `SMDCoordInfo`
- PropertyChanged ↔ Snapshot 동기화 ↔ 편집 Preview
- Generate command ↔ MakeCells ↔ 좌표 변환 ↔ 속성 병합 ↔ index/IP
- Preview binding ↔ GlassMapControl 렌더링/클릭
- Save/Validate ↔ SyncCollectionsToDocument ↔ Regenerate 호출 부재
- 공식 최신 change-log ↔ 회전/ingress/partition overlay/Import 동작

검증 결과, 현재 코드의 핵심 구조는 최신 공식 문서와 일치한다. 차이는 과거 전역 Template 설명과 현재 남아 있는 `CoordinateSummary`/비노출 command 같은 잔여 요소이며, 가장 큰 운영 위험은 Coordinate 변경 후 `Generate Cells`를 생략해도 설계와 실행 Cells 불일치가 자동 검출되지 않는 점이다.

