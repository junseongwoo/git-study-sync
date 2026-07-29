# RecipeWindow - PG 매핑 탭 개발 노트

## 1. 우선 기준과 문서 차이

공식 `docs/console-recipe-document.md`는 `YIndex`가 PG mapping 기준임을 명시한다. 하지만 문서의 `ConsoleControlPlan` 코드 예시에는 실제 코드의 `PgMappings` 속성이 포함되어 있지 않다.

| 항목 | 공식 문서 | 실제 코드 |
|---|---|---|
| 매핑 기준 | `YIndex` | `YIndex` |
| 저장 모델 | ControlPlan 존재, PgMappings 예시 없음 | `ConsoleControlPlan.PgMappings : List<ConsolePgMapping>` |
| 해석 규칙 | 미정의 | mapping 없으면 YIndex 자체를 PG index로 사용 |

따라서 `YIndex` 기준은 공식 사실이고, 나머지 구현 세부는 모두 **[추론]** 이다. 문서의 모델 예시는 현 코드와 불일치하므로 공식 문서 갱신 여부를 별도로 판단해야 한다.

## 2. 바인딩 및 데이터 흐름

**[추론: 현행 코드]**

```text
RecipeWindow.xaml DataGrid
  ItemsSource = RecipeEditorViewModel.PgMappings
  ComboBox SelectedValue = ConsolePgMapping.PgIndex
        ↓ CollectionChanged
SyncPgMappingsToDocument()
        ↓
Document.ControlPlan.PgMappings
        ↓
RecipeService.ResolvePgIndexForYIndex(recipe, cell.YIndex)
        ↓
PG endpoint/runtime 선택
```

`YIndex` 열은 읽기 전용이다. `PgIndex`만 콤보박스의 `SelectedValueBinding`으로 수정되며 `UpdateSourceTrigger=PropertyChanged`로 즉시 모델에 반영된다.

## 3. 동기화 구현

**[추론: `BuildPgMappingsFromCells`, `SyncPgMappingsFromCellsCore`]**

`SyncPgMappingsFromCellsCommand`는 다음 순서로 작동한다.

1. ControlPlan과 현재 UI collection의 유효 매핑을 `(YIndex → 마지막 PgIndex)` 사전으로 병합한다.
2. `Cells`에서 음수가 아닌 고유 YIndex를 오름차순으로 수집한다.
3. Cell에 YIndex가 없을 때만 기존 사전 key를 사용한다.
4. 기존 선택값이 있으면 유지하고, 없으면 `PgIndex = YIndex`로 생성한다.
5. UI `PgMappings`를 교체한다.
6. `SyncPgMappingsToDocument`로 다시 document에 저장하고 에이징 테스트 PG 표시를 갱신한다.

이 구현은 매핑을 cell 구조에 맞추는 기능이지 endpoint 연결 검증 기능이 아니다.

## 4. endpoint 선택지

**[추론: `RefreshPgEndpointOptions`]**

- endpoint가 있으면 `EecP725R2LightRuntimes.GetOrCreateCluster().Endpoints`의 `Index`, `EffectiveHost`, `EffectivePort`, `UseSimulation`으로 선택지를 만든다.
- endpoint가 없으면 현재 매핑에 등장한 최대 YIndex/PgIndex까지 `(PG 미구성)` placeholder를 만든다.
- 선택값은 ComboBox item의 순번이 아니라 `PgEndpointOption.PgIndex`다.

endpoint 구성을 변경한 뒤 이 목록을 어떤 lifecycle에서 refresh하는지 확인하고, 동적 구성 변경을 지원하려면 명시적으로 refresh 호출 지점을 설계해야 한다. 현 탭은 endpoint 편집 UI가 아니다.

## 5. 해석 및 validation 계약

**[추론]**

`RecipeService.ResolvePgIndexForYIndex`의 계약:

```csharp
YIndex < 0             => YIndex 반환
동일 YIndex mapping 존재 => mapping.PgIndex 반환
mapping 없음            => YIndex 반환
```

`ValidatePgMappings`의 계약:

- `YIndex >= 0`
- `PgIndex >= 0`
- YIndex 중복 불가

UI 동기화/저장 로직은 중복 YIndex를 마지막 항목 하나로 축약하지만, validator는 저장된 recipe에서 중복이 발견되면 오류를 낸다. 외부 JSON 편집이나 다른 writer가 있는 경우에는 validation을 우회하지 않는다.

## 6. 영향 범위

**[추론: 호출부 기준]**

- `RecipeEditorViewModel.ResolveSelectedCellPgIndex`: RecipeWindow의 선택 cell PG 제어/에이징 테스트
- `MainWindowViewModel`: Aging Run의 cell → PG 대상 구성
- `GlassInspectionStepPreparationService`: 검사 준비 중 pattern on/off 및 runtime lock 선택
- `PGRecipeControlWindow`: cell별 PG 대상 해석

PG mapping은 ControlPlan의 일부이므로, 단순 UI 데이터로 복제하거나 IP recipe에 중복 저장하지 않는다. Console이 ControlPlan을 소유한다는 상위 구조와 일치해야 한다.

## 7. 변경 시 검증 항목

1. 서로 다른 YIndex를 가진 cell이 생성된 뒤 동기화하면 각 행이 한 번씩만 나타나는지 확인한다.
2. 기존 `(YIndex, PgIndex)` 선택을 가진 상태에서 동기화해도 선택값이 유지되는지 확인한다.
3. 새 YIndex에는 YIndex와 동일한 PgIndex가 초기값으로 들어가는지 확인한다.
4. mapping 없는 YIndex, 음수 값, 중복 YIndex, endpoint 범위 초과를 각각 validation/실행에서 확인한다.
5. endpoint 구성/Simulation Mode에 따라 콤보박스 display가 예상 주소와 `(SIM)` 상태를 보여 주는지 확인한다.
6. 선택 cell의 PG test, Aging Run, 검사 step에서 동일 YIndex가 동일 PgIndex를 해석하는지 로그로 교차 확인한다.

## 8. 관련 소스

- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml`
- `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`
- `uLedAoiConsole/ViewModels/PgEndpointOption.cs`
- `uLedAoiConsole/Recipes/ConsoleRecipeDocument.cs`
- `uLedAoiConsole/Recipes/RecipeService.cs`
- `uLedAoiConsole/Services/InspectionReplay/GlassInspectionStepPreparationService.cs`
- `uLedAoiConsole/ViewModels/MainWindowViewModel.cs`
