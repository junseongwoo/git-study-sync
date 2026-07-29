# GlassSizeWindow - General 탭 개발 노트

## ViewModel → Model 매핑

|ViewModel|저장 모델|
|---|---|
|`Description`|`GlassSizeModel.Description`|
|`GlassWidthUm`, `GlassHeightUm`, `PanelAngleDeg`|동명 필드|
|`LeftAlignX/Y`, `RightAlignX/Y`|`AlignMarks.LeftAlignUm`, `RightAlignUm`|
|`CuttingMarkPosition`, `FirstCellPosition`, naming 규칙|`GlassMapNamingPolicy`|
|`RawIndexOrigin`, `DotIndexOrigin`, `DotIndexBase`, `DotIndexSwapXY`|`GlassMapNamingPolicy`|

`GlassSizeItemViewModel.ApplyToModel()`이 위 mapping의 단일 반영 지점이다. `CellNameOrder`는 `TokenOrder` 목록으로 변환된다.

```text
UsePartitionName=true  → Partition token 먼저 추가
XThenY                 → X, Y
YThenX                 → Y, X
```

## 저장 계약

`SaveWithChangeReport()`는 다음을 고정 순서로 수행한다.

```text
ApplyToModel
→ 저장 경로 파일명으로 GlassSizeId 확정
→ ObjectChangeTracker diff 산출
→ 사용자 확인
→ GlassSizeStore.SaveToPath
→ validation 성공 시 cache/history/version 갱신
→ ModelSaved 이벤트
```

`GlassSizeStore.Validate()`의 General 관련 검증은 다음과 같다.

- `GlassSizeId` 필수
- `GlassWidthUm`, `GlassHeightUm` > 0
- `PanelAngleDeg % 90 == 0`
- `AxisDirection`, Glass→Motor calibration, align camera calibration, AlignMarks 필요

따라서 General 탭만으로 모델 전체 저장 유효성이 보장되지는 않는다. 좌표계 보정 탭의 calibration 객체도 validation 대상이다.

## General 값의 하류 소비처

|값 그룹|주요 소비 경로|
|---|---|
|Width/Height|`RecipeService` cell build/regenerate, GlassMap size, stage footprint/UVW 중심|
|PanelAngle|GlassMap 표시 회전, `GetCellCenterAlongStageYUm`, auto IP split, safe gap, default calibration preset|
|AlignMarks|Align mark 간격·align 기준 검증|
|Naming|`ResolveGlassMapNamingPolicy` → cell naming, GlassMap cut mark|
|Index policy|Console/Verifier 결과 좌표 변환, overlay/CSV/WD defect row·column|

`RecipeService.LoadGlassSizeForRecipe()`는 general 기하의 정본을 model 파일에서 load하며 recipe 사본 fallback을 두지 않는다고 명시한다. model 파일이 없으면 값을 지어내지 않고 실패해야 한다.

## 변경 주의점

- `PanelAngle` 변경 후 matrix를 자동으로 갱신하지 않는다. 사용자가 `좌표계 보정`의 기본 Matrix 적용 또는 승인된 calibration 절차를 수행해야 한다. **[추론: General의 각도 setter와 matrix update가 연결되지 않음]**
- General의 naming 변경은 이미 존재하는 recipe cell name에 즉시 적용되지 않을 수 있다. `RefreshCellIndexes` 또는 재생성·적용 흐름을 통해 `RecipeService.ResolveGlassMapNamingPolicy`를 사용하는 경로를 확인해야 한다.
- Width/Height 또는 naming이 바뀐 모델을 현재 Recipe에 적용할 때 code-behind는 `RegenerateCellsFromSnapshot(... preserveExistingValues: true)`를 호출한다. 보존되는 cell 속성의 정확한 범위는 `MergeCellAttributes`를 기준으로 테스트한다.
- dot index policy 변경은 historical CSV를 재작성하지 않는다. **[추론]** 새 변환 정책이 적용되는 결과/재생성 산출물과 이전 산출물을 구분하여 검증해야 한다.

## 검증 시나리오

|변경|검증|
|---|---|
|Width/Height|0/음수 저장 거부, 정상값 cell map 외곽·cell 좌표 반영|
|PanelAngle|0/90/180/270 map·split·safe-gap 비교, 45도 저장 거부|
|Align marks|좌우 mark 설정 후 align mark 간격 오류/정상 실행 확인|
|Name 정책|4 corner First Cell, X/Y rules, partition on/off, user labels parsing 확인|
|Index 정책|고정 defect fixture로 overlay/CSV의 row, column, phase 변환 확인|
|모델 저장|diff 확인 취소 시 파일 미변경, 성공 시 version/history/cache 갱신|
|Recipe 적용|같은 GlassSizeId만 적용 확인 표시, cell regenerate 후 기존 속성 보존 확인|

## 관련 파일

- `uLedAoiConsole/Windows/Recipe/GlassSizeWindow.xaml`
- `uLedAoiConsole/ViewModels/GlassSizeViewModel.cs`
- `uLedAoiConsole/Models/GlassSizeConfigModels.cs`
- `uLedAoiConsole/Stores/GlassSizeStore.cs`
- `uLedAoiConsole/Recipes/RecipeService.cs`
