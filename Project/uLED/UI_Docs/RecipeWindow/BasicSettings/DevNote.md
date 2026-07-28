# RecipeWindow / 기본 설정 탭 인수인계 노트

## 파일 책임

| 파일 | 책임 |
|---|---|
| `Windows/Recipe/RecipeWindow.xaml` | 전체 창 레이아웃과 기본 설정 탭의 control/binding 정의 |
| `Windows/Recipe/RecipeWindow.xaml.cs` | `RecipeEditorViewModel` 생성, 파일/모델/보조 창 대화상자, 창 생명주기, Map 선택 이벤트 |
| `ViewModels/RecipeEditorViewModel.cs` | `ConsoleRecipeDocument` 편집, 저장·검증·GlassSize 동기화·Pixel Map sidecar 처리 |

## 핵심 모델 경계

- `ConsoleRecipeDocument`: Console 상위 레시피. `IpRecipe`, `GlassMap`, `AlignPlan`, `ControlPlan`, metadata를 포함한다.
- `IpRecipe : RecipeModel`: IP 실행 계약. 표시 pixel 정보, Pattern, Point, thumbnail 설정 등을 포함한다.
- `GlassMap.GlassSizeSnapshot`: 레시피에 저장되는 GlassSize 냉동 스냅샷이다.
- `GlassSizeId`: 외부 GlassSize model의 참조 식별자다.

GlassSize model 파일과 레시피 스냅샷은 같은 책임이 아니다. `모델 적용`은 model → recipe snapshot, `모델 복원`은 recipe snapshot → model 파일 방향으로 이해한다.

## 기본 설정 탭의 주요 바인딩

- 읽기 상태: `Document.Version`, `RecipeName`, `GlassSizeModelVersion`, `Document.ConfigVersion`, `GlassSizeSyncInfo`, `SelectedPointDisplay`
- 수정 값: `Document.GlassMap.GlassSizeId`, `Document.PatternNo`, `Document.GrabRotationDeg`, `Document.IpRecipe.ThumbnailWidth`, `Document.ExportRecipePrefix`, DisplayPixel 관련 속성, `Document.Description`
- 판정 목록: `GradeTypeMappings`, `DefectTypeOptions`

숫자 입력은 `NumericTextConverter`와 `UpdateSourceTrigger=LostFocus`를 사용한다. 따라서 입력 중 값과 모델 반영 시점이 다를 수 있으므로 검증/저장 전에 포커스를 이동해 값 반영을 확인한다.

## 저장과 sidecar 파일

- 레시피 기본 파일은 `Data/Recipes/<GlassSizeId>/<RecipeId>/recipe.json`이다.
- Display Pixel Map의 표준 sidecar 이름은 `map.txt`다.
- 가져오기/생성/정리 명령은 ViewModel에서 recipe 폴더로 파일을 복사하고 `DisplayPixelMapPath`를 표준 이름으로 유지한다.
- Save As 시 `CopyRecipeSidecarFilesForSaveAs(...)`가 sidecar 파일을 새 레시피 폴더로 복사한다.

## 창 생명주기 및 보조 창

- 생성자에서 `RecipeEditorViewModel`을 DataContext로 설정하고 콜백(파일 선택, GlassSize 선택·편집 등)을 주입한다.
- Closing은 `ConfirmClose()`로 미저장 변경을 확인한 후, 한 번만 종료 정리를 수행한다.
- Recipe Glass Map, Align, Image, Defect/Result Review, CA410 Result, Aging Progress 등 보조 창을 열고 재사용한다.

## 공식 문서와 코드 차이

- 문서의 요약 탭 구조(General/Patterns/Points/Cells/Map/Align-Control)보다 현재 XAML의 실제 탭이 더 세분화되어 있다.
- Display Pixel Map과 defect grade mapping은 공식 레시피 구조 문서에서 핵심 필드로 상세 설명되지 않지만, 코드상 기본 설정 탭에서 관리된다. 이 내용은 코드 확인 사항이며, 업무 의미는 단정하지 않는다.

## 후속 탭 분석 시 확인할 연결점

- `검사 패턴`: `IpRecipe.Patterns` 및 Pattern×Point 실행 계약
- `셀 목록`, `셀 맵`, `CellMap 보정`: `GlassMapDesignSnapshot`, `Cells`, XIndex/YIndex/IP 분배
- `Align / Control`: `AlignPlan`, `ControlPlan`, GlassSize 기준 mark 및 runtime align 결과의 분리
- `PG 매핑`, `CA410`, `에이징`: `PatternNo`, Pattern별 설정 및 외부 장비 명령의 관계

## 추가 확인 필요

- [추론] `PatternNo`와 PG 매핑 정보의 실제 우선순위는 `PG 매핑` 탭 및 PG 전송 서비스에서 확인한다.
- [추론] defect grade mapping의 최종 적용 위치는 IP 결과 후처리/Console export 판정 코드를 확인한다.
- `GlassSizeSyncState`의 비교 범위(어떤 필드가 불일치로 판정되는지)는 `RecipeGlassSizeSyncViewModel` 또는 동기화 서비스 분석이 필요하다.
