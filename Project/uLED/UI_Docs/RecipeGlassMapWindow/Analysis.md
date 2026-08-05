# RecipeGlassMapWindow 개발자 분석

작성일: 2026-08-03  
분석 대상: `RecipeWindow > 레시피 Glass Map` 메뉴로 여는 `RecipeGlassMapWindow`

## 1. 핵심 결론

이 창은 현재 레시피의 `GlassMapDesignSnapshot.Coordinates`를 편집하는 **Glass Map 설계 입력 창**이다. 공식 문서가 정의한 데이터 책임은 다음과 같다.

- `GlassMapDesignSnapshot`: 셀 배치의 설계 원본
- `GlassSizeSnapshot`: 글래스 크기, 이름 정책, 첫 셀 위치 등의 패널 기준
- `GlassMap.Cells`: 실제 검사 순회에 사용하는 런타임 전개 결과

따라서 좌표 모델을 수정한 뒤에는 반드시 `Generate Cells`를 실행해 설계 원본을 런타임 셀로 전개해야 한다. 이 창의 왼쪽 `Recipe Preview`는 좌표 입력 변경을 즉시 보여 주지만, 미리보기 갱신과 런타임 `Cells` 재생성은 같은 동작이 아니다.

가장 중요한 운영상 주의점은 다음과 같다.

> 좌표 입력 → 미리보기 변화 → `Generate Cells` → RecipeWindow의 셀 목록/셀 맵 확인 → Validate → Save 순서로 작업해야 한다.

## 2. 분석 기준과 사실 우선순위

### 2.1 우선 적용한 공식 문서

1. `docs/프로젝트 구조.md`
2. `docs/전체 flow.md`
3. `docs/console-recipe-document.md`
4. `docs/glass-map.md`
5. `docs/development/change-log.md`
6. `docs/release-notes.md`

공식 문서의 공통 기준은 `GlassMapDesignSnapshot`을 설계 원본, `Cells`를 실행용 결과로 분리하는 것이다. 셀 생성 흐름은 다음과 같이 정의되어 있다.

```text
GlassMapDesignSnapshot.Coordinates
    -> GlassInfoHelper.MakeCells(...)
    -> RecipeService.BuildCellsFromGlassMapDesign(...)
    -> ConsoleCellPlan 목록
    -> XIndex / YIndex 계산
    -> IP 배정 유지 또는 자동 분배
```

### 2.2 문서 내 과거 설명 처리

`docs/glass-map.md` 일부에는 전역 `GlassMapDesignViewModel`, `Data/GlassMaps/glass_map_design.json`, `Tool > Glass Map Design`을 주 편집 경로로 설명한 내용이 남아 있다. 그러나 최신 공식 변경 기록은 전역 Template 편집기를 삭제하고 레시피의 `GlassMapDesignSnapshot`과 GlassSize 기반 셀 생성을 현재 구조로 확정했다.

따라서 본 문서는 최신 공식 변경 기록과 현재 코드를 기준으로 다음과 같이 해석한다.

- 전역 Template 편집기: 삭제됨
- 현재 편집 대상: 레시피 내부 `GlassMapDesignSnapshot`
- Template Import/Export 버튼: 현재 창에서 제거됨
- 현재 외부 가져오기: `Import From Recipe`
- 셀 이름: 고정 4문자 규칙이 아니라 GlassSize의 `GlassMapNamingPolicy`를 따름

## 3. 화면 진입과 Window 생명주기

### 3.1 메뉴 이벤트

`RecipeWindow.xaml`의 메뉴 항목은 다음 이벤트에 연결된다.

```xml
<MenuItem Header="레시피 Glass Map"
          Click="OpenGlassMapWindow_Click"/>
```

`OpenGlassMapWindow_Click`은 `ShowOrActivate`를 통해 창을 연다.

```text
메뉴 클릭
  -> 기존 RecipeGlassMapWindow가 없거나 닫혔으면 새 창 생성
  -> Owner = RecipeWindow
  -> DataContext = RecipeWindow.DataContext
  -> 비모달 Show()

기존 창이 열려 있으면
  -> 최소화 상태 복원
  -> Activate()
```

`[추론] (코드 확인)` 이 창은 RecipeWindow와 동일한 `RecipeEditorViewModel` 인스턴스를 공유한다. 그러므로 이 창에서 변경한 좌표 모델은 별도의 복사본이 아니라 현재 RecipeWindow가 편집 중인 in-memory 레시피에 즉시 반영된다.

### 3.2 중복 창과 소유 관계

`[추론] (코드 확인)` 같은 RecipeWindow에서 Recipe Glass Map 창은 한 개만 유지된다. 메뉴를 다시 눌러도 새 창을 계속 만들지 않고 기존 창을 활성화한다.

`[추론] (코드 확인)` RecipeWindow 종료 시 `CloseOwnedWindowsAsync()`가 이 창을 닫고 참조를 해제한다.

### 3.3 Window 상태 전이

`RecipeGlassMapWindow.xaml.cs`는 데이터 로직을 갖지 않고 창 상태만 관리한다.

| 시점 | 처리 |
|---|---|
| 생성자 | `TrySetInitializing()` 후 XAML 초기화 및 이벤트 등록 |
| `Loaded` | `SetReady()` |
| `Closing` | `TryEnterClosing()` 실패 시 닫기 취소 |
| `Closed` | `SetClosed()` |

이는 프로젝트의 Window 생명주기 지침에 맞는 구현이다.

## 4. 전체 화면 구조

Window 기본 크기는 `1220 × 820`, 시작 위치는 소유자인 RecipeWindow 중앙이다.

```text
┌──────────────────────────────────────┬────────────────────────────┐
│ Recipe Preview                       │ Recipe Snapshot            │
│                                      │ - 명령 버튼                 │
│ GlassMapControl                      │ - Recipe / Glass Size      │
│                                      │ - Snapshot Summary         │
│                                      │ - Coordinate model 목록    │
│                                      ├────────────────────────────┤
│ StatusMessage                        │ Snapshot Coordinate Editor │
│                                      │ - 좌표/크기/간격/Block 입력│
└──────────────────────────────────────┴────────────────────────────┘
```

왼쪽은 도면 입력 결과를 시각적으로 확인하는 영역이며, 오른쪽은 Snapshot 명령과 선택 Coordinate 편집 영역이다.

## 5. 컨트롤 분석

### 5.1 Recipe Preview 영역

| 컨트롤 | 바인딩/설정 | 역할 | 영향 |
|---|---|---|---|
| `GlassMapControl` | `MapInfo=GlassMapEditPreviewMapInfo` | Coordinate snapshot을 셀 사각형으로 표시 | 설계 입력 결과를 즉시 확인 |
| `RotationAngle` | `GlassMapEditPreviewRotationAngle` | 편집 화면 회전 | 현재 항상 `0°` |
| `ZoomFactor` | `PreviewZoomFactor` | 지도 표시 배율 | 같은 VM의 preview 배율 사용 |
| `ShowIngressDirection` | `False` | 인입 방향 화살표 표시 | 편집 창에서는 숨김 |
| `ShowPartitionNameOverlay` | `False` | 분판 이름 대형 오버레이 | 편집 창에서는 숨김 |
| 상태 TextBox | `StatusMessage`, OneWay | 명령 성공/실패 메시지 | 읽기 전용, 64px 높이 |

공식 변경 기록에 따라 이 Preview는 운영 화면의 패널 회전과 인입 방향을 의도적으로 적용하지 않는다. Coordinate snapshot과 GlassSize naming policy를 직접 사용해 `FirstCellPosition` 변경을 즉시 반영하는 도면 입력용 화면이다.

`[추론] (코드 확인)` `GlassMapControl` 자체는 클릭한 셀을 `SelectedCellId`로 표시할 수 있지만, 이 XAML은 `SelectedCellId`, `CellClicked`, `CellUseToggleRequested`를 VM에 연결하지 않았다. 따라서 이 창에서 셀 클릭은 선택 테두리를 보일 수 있을 뿐 Coordinate 편집 대상이나 런타임 Cell을 변경하지 않는다.

### 5.2 Recipe Snapshot 영역

| 표시/버튼 | 바인딩 | 기능 |
|---|---|---|
| `Add Copy` | `AddCoordinateModelCommand` | 선택 Coordinate를 복제해 새 Coordinate 추가 |
| `Remove` | `RemoveCoordinateModelCommand` | 선택 Coordinate 삭제 확인 후 제거 |
| `Import From Recipe` | `ImportGlassMapFromRecipeCommand` | 다른 Recipe의 Glass Map snapshot을 현재 Recipe로 가져옴 |
| `Generate Cells` | `RegenerateCellsFromCoordinatesCommand` | 현재 Coordinate 설계로 런타임 `Cells` 재생성 |
| `Refresh Preview` | `RefreshPreviewCommand` | 현재 문서 동기화, 셀 인덱스/모션 대상 및 미리보기 갱신 |
| `Recipe` | `RecipeId`, OneWay | 현재 편집 Recipe 식별자 |
| `Glass Size` | `GlassSizeModelInfo`, OneWay | 현재 GlassSize 모델 정보 및 상태 |
| `Snapshot Summary` | `CoordinateSummary`, OneWay | Coordinate 개수와 Template 파일 상태 표시 |
| Coordinate 목록 | `ItemsSource=CoordinateModels` | Snapshot 내 Coordinate 모델 목록 |
| 목록 선택 | `SelectedCoordinateModel` | 아래 Editor가 편집할 Coordinate 선택 |

`[추론] (코드 확인)` `CoordinateSummary`의 `파일 없음`은 레시피 snapshot이 없다는 뜻이 아니다. 현재 창에서 제거된 과거 Template 파일 경로인 `_currentGlassMapDesignFilePath`가 없다는 뜻이다. 이 때문에 정상적인 레시피 snapshot도 `Coordinate model N개 / 파일 없음`으로 표시될 수 있다.

### 5.3 Snapshot Coordinate Editor

모든 입력은 선택된 `GlassCoordinateViewModel`에 `UpdateSourceTrigger=PropertyChanged`로 연결된다. 입력이 바인딩 소스에 반영되는 즉시 snapshot 동기화와 편집 Preview 재생성이 수행된다.

공식 좌표 기준:

- 설계 입력 좌표 원점: 글래스 좌상단
- 설계 입력 `+X`: 오른쪽
- 설계 입력 `+Y`: 아래쪽
- 단위: µm
- 실행용 `CellRectGlassUm`: 글래스 중심 `(0,0)`, `+X` 오른쪽, `+Y` 위쪽으로 변환됨

| 입력값 | 의미 | 생성식/영향 | UI 범위 |
|---|---|---|---|
| `Name` | Coordinate/분판 식별 이름 | 이름 정책에서 Partition token의 prefix 후보 | 명시적 제한 없음 |
| `CELL_SIZE_X` | 셀 폭 | 생성 셀 사각형 `Width` | `Minimum=0` |
| `CELL_SIZE_Y` | 셀 높이 | 생성 셀 사각형 `Height` | `Minimum=0` |
| `CELL_X_COUNT` | 이 Coordinate 전체의 X방향 셀 수 | X block들에 나누어 배치 | 명시적 제한 없음 |
| `CELL_Y_COUNT` | 이 Coordinate 전체의 Y방향 셀 수 | Y block들에 나누어 배치 | 명시적 제한 없음 |
| `OFFSET_E_X` | 첫 X block의 첫 셀 좌상단 X | `blockBaseX`의 시작값 | 명시적 제한 없음 |
| `OFFSET_E_Y` | 첫 Y block의 첫 셀 좌상단 Y | `blockBaseY`의 시작값 | 명시적 제한 없음 |
| `CELL_DIST_X` | 같은 block 안 셀 시작점 간 X pitch | `localX × CELL_DIST_X` | 명시적 제한 없음 |
| `CELL_DIST_Y` | 같은 block 안 셀 시작점 간 Y pitch | `localY × CELL_DIST_Y` | 명시적 제한 없음 |
| `BLOCK_DIST_X` | X block 시작점 간 거리 | `blockX × BLOCK_DIST_X` | 명시적 제한 없음 |
| `BLOCK_DIST_Y` | Y block 시작점 간 거리 | `blockY × BLOCK_DIST_Y` | 명시적 제한 없음 |
| `BLOCK_COUNT_X` | X 방향 block 수 | `max(1, 입력값)`으로 생성 | 명시적 제한 없음 |
| `BLOCK_COUNT_Y` | Y 방향 block 수 | `max(1, 입력값)`으로 생성 | 명시적 제한 없음 |

`CELL_SIZE_X/Y`는 UI에서 0까지 허용하지만 Recipe 검증은 생성된 Cell의 폭과 높이가 모두 양수여야 통과한다. 따라서 실사용 값은 `0보다 큰 값`이어야 한다.

`[추론] (코드 확인)` 나머지 값에는 XAML/VM 차원의 최소·최대 검증이 없다. 음수 count는 생성 시 0으로 처리되고, block count가 0 이하이면 1로 처리되며, 음수 offset/distance는 글래스 밖 배치나 역방향/겹침을 만들 수 있다. 현재 Recipe 검증은 Coordinate 자체의 범위, 글래스 포함 여부, 셀 중첩을 검사하지 않는다.

## 6. 셀 배치 계산 로직

### 6.1 Block별 셀 수 배분

`CELL_X_COUNT`와 `CELL_Y_COUNT`는 **각 block당 셀 수가 아니라 해당 Coordinate 전체 셀 수**다.

각 축의 전체 셀 수 `T`를 block 수 `B`에 나눌 때:

```text
baseCount = T / B
remainder = T % B

앞쪽 remainder개 block: baseCount + 1개
나머지 block:          baseCount개
```

예: `CELL_X_COUNT=12`, `BLOCK_COUNT_X=2`이면 X block별 `6, 6`개다.  
예: `CELL_Y_COUNT=15`, `BLOCK_COUNT_Y=2`이면 Y block별 `8, 7`개다.

Coordinate 하나의 총 셀 수는 정상적인 양수 입력 기준으로 다음과 같다.

```text
총 셀 수 = CELL_X_COUNT × CELL_Y_COUNT
```

`BLOCK_COUNT_X/Y`는 총 셀 수를 곱하지 않고 셀을 block에 분할하는 역할만 한다.

### 6.2 기본 좌상단 시작 위치 계산

`bX`, `bY`는 0-base block index, `localX`, `localY`는 block 내부 0-base index다.

```text
blockBaseX = OFFSET_E_X + bX × BLOCK_DIST_X
blockBaseY = OFFSET_E_Y + bY × BLOCK_DIST_Y

naturalX = blockBaseX + localX × CELL_DIST_X
naturalY = blockBaseY + localY × CELL_DIST_Y
```

셀 사각형은 다음과 같다.

```text
Rect = (resolvedX, resolvedY, CELL_SIZE_X, CELL_SIZE_Y)
```

### 6.3 FirstCellPosition 반영

GlassSize의 `GlassMapNamingPolicy.FirstCellPosition`이 오른쪽 시작이면 X를 반전하고, 아래쪽 시작이면 Y를 반전한다.

```text
오른쪽 시작:
resolvedX = GlassWidth - naturalX - CELL_SIZE_X

왼쪽 시작:
resolvedX = naturalX

아래쪽 시작:
resolvedY = GlassHeight - naturalY - CELL_SIZE_Y

위쪽 시작:
resolvedY = naturalY
```

이 정책은 셀 이름뿐 아니라 실제 셀 배치 시작 위치에도 적용된다.

### 6.4 Coordinate 이름과 셀 이름

공식 최신 기준에서 셀 이름은 GlassSize의 naming policy에 따라 생성된다.

- Coordinate `Name`에서 첫 영문/숫자 문자를 찾아 대문자 Partition prefix로 사용
- 사용할 문자가 없으면 Coordinate 순서 기반 문자 사용
- `UsePartitionName`에 따라 Partition 포함 여부 결정
- `TokenOrder`에 따라 Partition/X/Y 순서 결정
- `XRule`, `YRule`에 따라 영문, 십진수, 2자리 십진수, 사용자 정의 label 적용

`docs/glass-map.md`의 고정 `AA01` 형태 설명은 기본 정책을 단순화한 과거 설명이며, 현재는 고정 규칙이 아니다.

### 6.5 실행 좌표로 변환

Preview 생성 시 `RoiInfo.Rect`는 좌상단 원점 좌표다. `Generate Cells`에서는 이를 `Coord.CellCornerToGlassCentered`로 변환해 `ConsoleCellPlan.CellRectGlassUm`에 저장한다.

개념 변환은 다음과 같다.

```text
glassX = cornerX - GlassWidth / 2
glassY = GlassHeight / 2 - cornerY
```

단, `CellRectGlassUm.Y`는 실행 모델에서 셀의 위쪽 기준을 유지하고 셀 중심은 `Y - Height/2`로 계산한다.

## 7. 데이터 바인딩과 변경 흐름

### 7.1 핵심 바인딩 객체

```text
RecipeGlassMapWindow.DataContext
  = RecipeWindow.DataContext
  = RecipeEditorViewModel

RecipeEditorViewModel.Document.GlassMap
  ├─ GlassSizeId
  ├─ GlassSizeSnapshot
  ├─ GlassMapDesignSnapshot
  │    └─ Coordinates: List<GlassCoordinateModel>
  └─ Cells: List<ConsoleCellPlan>

CoordinateModels: ObservableCollection<GlassCoordinateViewModel>
GlassMapEditPreviewMapInfo: GlassMapInfo
```

`GlassCoordinateViewModel`은 별도 데이터 복사본이 아니라 `GlassCoordinateModel`을 감싸서 `Name`과 `SMDCoordInfo` 속성 변경 알림을 제공한다.

### 7.2 값 입력 시 흐름

`[추론] (코드 확인)` 입력값이 변경되면 다음 순서로 처리된다.

```text
TextBox / CalcTextBox 입력
  -> SelectedCoordinateModel 속성 setter
  -> PropertyChanged
  -> CoordinateModel_PropertyChanged
  -> SyncCoordinateModelsToDocument
       - Snapshot GlassWidth/Height를 현재 GlassSize로 갱신
       - CoordinateModels를 Snapshot.Coordinates에 반영
  -> RefreshGlassMapEditPreview
  -> GlassMapControl 재렌더링
```

이 흐름에는 `RegenerateCellsFromSnapshot` 호출이 없다. 즉 입력 즉시 바뀌는 것은 설계 snapshot과 설계 Preview이며, 런타임 `Cells`는 기존 상태다.

### 7.3 목록 추가/삭제 시 흐름

`CoordinateModels.CollectionChanged`도 snapshot 동기화와 Preview 갱신을 수행한다. 삭제 후 목록이 비면 `AddCoordinateModel()`이 기본 Coordinate 하나를 다시 추가하므로 UI 작업으로는 Coordinate 목록을 완전히 빈 상태로 유지하지 않는다.

## 8. 버튼별 코드 진행과 영향

### 8.1 Add Copy

`[추론] (코드 확인)`

1. 선택 모델이 있으면 `GlassCoordinateModel.Clone()`으로 모든 `SMDCoordInfo` 값을 복사한다.
2. 선택 모델이 없으면 기본 `SMDCoordInfo`를 가진 새 모델을 만든다.
3. 중복되지 않는 이름을 `A`~`Z`, 이후 `Coord N` 형식으로 찾는다.
4. 컬렉션에 추가하고 새 항목을 선택한다.
5. snapshot과 Preview가 즉시 갱신된다.

런타임 `Cells`는 자동으로 재생성되지 않는다.

### 8.2 Remove

`[추론] (코드 확인)`

1. 선택 항목이 있을 때만 버튼이 활성화된다.
2. 삭제 확인 대화상자를 표시한다.
3. 확인하면 Coordinate를 제거한다.
4. 마지막 항목이었다면 기본 Coordinate를 즉시 추가한다.
5. snapshot과 Preview가 갱신된다.

런타임 `Cells`는 자동으로 제거/재생성되지 않으므로 `Generate Cells`가 필요하다.

### 8.3 Import From Recipe

`[추론] (코드 확인)`

```text
Recipe 파일 선택
  -> RecipeStore.Open(autoLoad: true)
  -> source.GlassMap.GlassMapDesignSnapshot 확인
  -> JSON serialize/deserialize로 깊은 복사
  -> 현재 Document.GlassMap.GlassMapDesignSnapshot 교체
  -> CoordinateModels 재바인딩
  -> 현재 Recipe의 GlassSize로 Cells 재생성
  -> 컬렉션/Preview 갱신
```

중요한 범위:

- 가져오는 데이터는 다른 Recipe의 `GlassMapDesignSnapshot`이다.
- 다른 Recipe의 `GlassSizeSnapshot` 자체를 함께 적용하지 않는다.
- 셀 생성은 **현재 Recipe의 GlassSize와 naming policy**를 사용한다.
- 현재 Recipe의 기존 Cells에서 `Use`, `IpNo`, `RoundCell`, `UserDefinedName`을 가능한 범위에서 보존한다.
- 가져오기 전에 현재 snapshot을 덮어쓸지 별도 확인하지 않는다.
- 가져오기 결과는 메모리 변경이며 최종 보존에는 RecipeWindow의 Save가 필요하다.

### 8.4 Generate Cells

공식 구조상 설계 snapshot을 실행용 셀로 전개하는 핵심 명령이다.

`[추론] (코드 확인)` 처리 순서:

```text
CoordinateModels -> GlassMapDesignSnapshot 동기화
  -> BuildCellsFromGlassMapDesign
  -> GlassInfoHelper.MakeCells
  -> RoiInfo를 ConsoleCellPlan으로 좌표 변환
  -> Y 내림차순, X 오름차순 정렬
  -> 기존 Cell 속성 병합
  -> XIndex / YIndex 계산
  -> IP 배정 유지 또는 자동 배정
  -> Document.GlassMap.Cells 교체
  -> RecipeWindow 컬렉션 재바인딩
  -> Preview 및 모션 대상 갱신
```

기존 속성 보존 규칙:

1. 먼저 `CellId`로 기존 Cell을 찾는다.
2. ID가 없으면 자동 생성 `Name`으로 찾는다.
3. 찾으면 `Use`, `IpNo`, `RoundCell`, `UserDefinedName`을 새 Cell로 복사한다.

`[추론]` 배치 구조가 크게 바뀌어 같은 `CellId`가 다른 물리 위치를 가리키게 되면, ID 우선 병합 때문에 이전 속성이 의도하지 않은 새 셀에 이어질 가능성이 있다. 대규모 Coordinate 변경 뒤에는 셀 목록에서 `Use`, `IpNo`, 사용자 정의 이름을 재검토해야 한다.

### 8.5 Refresh Preview

`[추론] (코드 확인)` 이 명령은 다음을 수행한다.

- 화면 컬렉션을 현재 Document에 동기화
- 기존 `Cells`의 이름과 `XIndex/YIndex` 갱신
- PG mapping 동기화
- Cell motion target 갱신
- 런타임 Cells 기반 `PreviewMapInfo` 갱신
- Coordinate snapshot 기반 `GlassMapEditPreviewMapInfo` 갱신

그러나 Coordinate 설계에서 런타임 Cell geometry를 다시 만드는 `RegenerateCellsFromSnapshot`은 호출하지 않는다. 따라서 Coordinate 수정 후 `Refresh Preview`만 누르는 것은 `Generate Cells`의 대체가 아니다.

## 9. Preview 렌더링 구조

### 9.1 Preview 데이터 생성

`RefreshGlassMapEditPreview()`는 다음 데이터로 `GlassMapInfo`를 만든다.

| `GlassMapInfo` 필드 | 입력 원본 |
|---|---|
| `GlassSize` | 현재 Recipe의 GlassSize |
| `CutMark` | 현재 GlassSize naming policy의 `CuttingMarkPosition` |
| `CellInfo` | `GlassMapDesignSnapshot.Coordinates`를 `GlassInfoHelper.MakeCells`로 생성한 `RoiInfo` 목록 |

이 경로는 `Document.GlassMap.Cells`를 사용하지 않는다.

### 9.2 GlassMapControl 출력

`[추론] (코드 확인)` `GlassMapControl`은 다음 순서로 그린다.

1. 흰색 배경
2. 글래스 외곽과 Cutting Mark
3. 각 `RoiInfo.Rect`를 화면 사각형으로 변환해 셀 채움/테두리 표시
4. `Use=false`이면 사선 hatch 표시
5. 셀이 충분히 크면 셀 이름 표시
6. 선택된 셀이 있으면 선택 테두리 표시

이 창에서는 운영 상태, 결함 overlay, ingress, partition name overlay 바인딩을 사용하지 않는다.

### 9.3 회전과 방향

`GlassMapEditPreviewRotationAngle`은 현재 항상 `0`을 반환한다. 이는 공식 변경 기록의 “Recipe Glass Map Window는 도면 입력용이며 운영 표시 회전과 ingress를 적용하지 않는다”는 기준과 일치한다.

MainWindow나 RecipeWindow의 운영/셀 맵 Preview가 `PanelAngleDeg`, ingress, partition overlay를 표시하더라도 이 창과 모양의 방향이 다를 수 있다. 이는 오류가 아니라 화면 목적 차이다.

## 10. Generate Cells 이후 프로그램 전체 영향

공식 문서에서 `Cells`는 단순 표시 데이터가 아니라 Console 실행의 핵심 단위다.

| 변경 결과 | 프로그램 영향 |
|---|---|
| `CellRectGlassUm` | 셀 중심 및 장비 축 목표 계산의 기반 |
| `XIndex` | StageX 기준 실행 line/group 순서 |
| `YIndex` | 같은 XIndex 내 실행 순서, IP 분배/Split/PG mapping 기준 |
| `Use` | 검사 대상 포함/제외 |
| `IpNo` | IP1/Unit1 또는 IP2/Unit2 담당 결정 |
| `Name`/`DisplayName` | IP Cell Job 이름, 이미지 폴더/파일, 로그 표시에 사용 |
| `MapColumnIndex/MapRowIndex` | XIndex/YIndex 그룹 축을 결정하는 내부 map index |

`XIndex/YIndex`는 PanelAngle로 단순 회전한 행/열 번호가 아니다. GlassSize affine calibration과 Unit1 검사 카메라 offset으로 Cell의 StageX/InspectionUnit1Y target을 계산하고, map column/row 중 StageX 변화가 큰 축을 X group 축으로 선택하여 0-base 순서를 정한다. 공식 문서상 `PanelAngleDeg`는 표시/회전 기준이며 `XIndex/YIndex` 계산에는 사용하지 않는다.

## 11. Save와 Validate 관계

공식 권장 순서는 GlassSize 확인 → Cells 재생성/IP 확인 → Pattern/Point/ROI 확인 → Align/Control 확인 → Validate → Save다.

`[추론] (코드 확인)` 현재 `Save`, `Save As`, `Validate`는 `SyncCollectionsToDocument()`를 실행한다. 이 메서드는 Coordinate snapshot과 기존 Cells를 문서에 반영하고 기존 Cells의 이름/인덱스를 갱신하지만 Cell geometry를 Coordinate로부터 자동 재생성하지 않는다.

따라서 다음 상태가 가능하다.

```text
GlassMapDesignSnapshot = 새 Coordinate 설계
GlassMap.Cells          = 이전 설계에서 생성한 기존 셀 좌표
```

기존 Cells가 양수 크기 등 기본 검증을 통과하면 Validate가 이 둘의 불일치를 직접 검출하지 못할 수 있다. 이 때문에 `Generate Cells`는 사용자가 명시적으로 수행해야 하는 필수 단계다.

## 12. Docs ↔ 코드 검증 결과

| 검증 항목 | 공식 문서 기준 | 현재 코드 | 판정 |
|---|---|---|---|
| 설계/실행 데이터 분리 | Snapshot은 설계 원본, Cells는 실행 결과 | 동일 | 일치 |
| 셀 생성 흐름 | Coordinates → MakeCells → BuildCells → ConsoleCellPlan | 동일 | 일치 |
| Coordinate 수정 반영 | 설계 수정 후 Cells 재확인/재생성 필요 | 입력은 Preview만 즉시 갱신, Generate Cells가 별도 | 일치 |
| 편집 Preview 회전 | 도면 입력 화면은 운영 회전 미적용 | 각도 항상 0 | 일치 |
| Ingress 표시 | 편집 화면 미적용 | `False` | 일치 |
| Partition overlay | 편집 기본 화면에서 숨김 | `False` | 일치 |
| FirstCellPosition | 이름과 실제 시작 위치에 반영 | X/Y mirror 계산에 반영 | 일치 |
| Import 범위 | 다른 Recipe snapshot 가져오기 | snapshot만 복제, 현재 GlassSize로 재생성 | 일치 |
| Template 버튼 | 제거 | XAML에 없음 | 일치 |
| 전역 Template 편집기 | 최신 변경 기록에서 삭제 | 현재 메뉴/Window 없음 | 일치 |
| 고정 4문자 셀 이름 | `glass-map.md`에 과거 단순 설명 존재 | GlassSize naming policy 기반 | 문서 내 과거 설명과 차이, 최신 변경 기록/코드 우선 |
| Snapshot Summary 파일 상태 | 현재 구조는 레시피 snapshot 중심 | 과거 Template 경로를 계속 표시 | 잔여 UI 의미 불명확 |
| Coordinate 범위 검증 | 문서에 구체적인 전체 범위 없음 | Cell size 외 대부분 제한 없음 | 코드 확인 필요 사항 |
| 설계와 Cells 일관성 검증 | 설계에서 재생성 가능한 구조 | Save/Validate가 자동 geometry 재생성/불일치 비교 안 함 | 운영 주의 필요 |

## 13. 미구현·제한·주의 항목

- Coordinate 설계와 현재 `Cells` geometry가 같은지 비교하는 검증은 구현되어 있지 않다.
- Coordinate 값의 글래스 범위 초과, 셀 중첩, 음수 거리/offset에 대한 전용 검증이 없다.
- 이 창에는 자체 Save/Validate 버튼이 없다. RecipeWindow에서 수행해야 한다.
- 이 창에는 IP 자동 분배, Split 적용, Use 토글, 개별 Cell 편집 UI가 없다. RecipeWindow의 셀 목록/셀 맵에서 확인한다.
- Preview의 셀 클릭은 Coordinate 목록 선택과 연결되지 않는다.
- `Snapshot Summary`의 파일 경로 표현은 현재 per-recipe snapshot 구조와 맞지 않는 과거 Template 상태를 포함한다.

## 14. 2차 검증 체크리스트

본 문서는 다음 순서로 2차 검증했다.

1. 공식 Docs에서 `GlassMapDesignSnapshot`, `Cells`, GlassSize, 좌표계, 이름 정책 확인
2. RecipeWindow 메뉴 이벤트와 단일 Window 활성화 경로 확인
3. RecipeGlassMapWindow XAML의 모든 버튼, 표시값, 입력 바인딩 확인
4. code-behind의 Window 상태 전이 확인
5. `RecipeEditorViewModel` 명령 생성, Coordinate 동기화, Import, Preview, Generate 로직 확인
6. `GlassCoordinateViewModel`의 실제 모델 wrapping 및 변경 알림 확인
7. `GlassInfoHelper.MakeCells`의 block 배분, 좌표 계산, FirstCellPosition, 이름 생성 확인
8. `RecipeService`의 실행 좌표 변환, 기존 속성 보존, 인덱스/IP 처리 확인
9. `GlassMapControl`의 렌더링·클릭 동작과 XAML 연결 여부 확인
10. Save/Validate 경로가 Cell geometry를 자동 재생성하지 않는지 재확인
11. 최신 change-log와 과거 `glass-map.md` 설명의 차이를 분리 기록

## 15. 관련 코드

- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml`
- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml.cs`
- `uLedAoiConsole/Windows/Recipe/RecipeGlassMapWindow.xaml`
- `uLedAoiConsole/Windows/Recipe/RecipeGlassMapWindow.xaml.cs`
- `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`
- `uLedAoiConsole/ViewModels/GlassCoordinateViewModel.cs`
- `uLedAoiConsole/Models/GlassMapDesignModel.cs`
- `uLedAoiConsole/Models/GlassMapInfo.cs`
- `uLedAoiConsole/Controls/GlassMapControl.cs`
- `uLedAoiConsole/Recipes/RecipeService.cs`

