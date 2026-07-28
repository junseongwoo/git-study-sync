# RecipeWindow / 검사 패턴 탭 인수인계 노트

## 데이터 모델

- 목록: `PatternRows : ObservableCollection<PatternRecipeRowViewModel>`
- 실제 Pattern: `Patterns : ObservableCollection<PatternPlanModel>` → `Document.IpRecipe.Patterns`
- Pattern별 전압: `ConsoleInspectionPatternVoltage`
- 공통 설정: `Document.RecipeParameterPlan.CommonInspectionConfig`
- Pattern별 공통 사용 여부: `ConsolePatternCommonRecipeSetting.UseCommonRecipe`
- ROI: `PrimaryPoint.RoiX/Y/Width/Height`

Pattern과 Point의 관계는 runtime contract 기준으로 공통 Point 집합을 공유하는 `Pattern × Point`다. Pattern별 독립 ROI로 문서화하거나 구현하지 않는다.

## 공통 파라미터 적용 구조

1. `UseCommonRecipe=true`가 되면 `ApplyCommonRecipeToRow()`가 공통 InspectionConfig를 해당 Pattern에 복사한다.
2. 선택 Pattern의 `공통 값 복사해 오기`는 `CopyCommonRecipeToSelectedPattern()`을 호출한다.
3. `CommonRecipeParameterWindow`가 닫히면 부모 창에서 `ApplyCommonRecipeToCommonPatterns()`를 호출한다.
4. 복제 후 `InspectionConfig` 인스턴스가 교체되므로 `SelectedPattern`과 관련 속성의 PropertyChanged를 발생시켜 상세 폼을 갱신한다.

공통 사용 여부만 저장하고, 실행 시 공통 config를 동적으로 참조하는 구조로 가정하면 안 된다. 코드상 공통값은 Pattern 설정으로 복사된다.

## CommonRecipeParameterWindow

- DataContext는 부모 RecipeWindow와 같은 `RecipeEditorViewModel`이다.
- `WindowProcessStateMachine`을 사용해 Initializing → Ready → Closing → Closed 전이를 관리한다.
- 닫기 버튼은 `IsCancel=True`이며, 별도 저장/취소 복제 모델은 없다.
- 부모는 창 인스턴스를 재사용(`ShowOrActivate`)한다.

## 현재 탭에서 열리지 않는 창

`검사 ROI` 내부의 `이미지 창 열기` 버튼은 주석 처리되어 있다. 현재 탭의 분석 범위에서 새 창으로 보지 않는다. `RecipeImageWindow`는 상단 `창 > 이미지 창`에서 열리는 보조 창이므로, 해당 메뉴/창 분석 때 별도로 다룬다.

## 검증 포인트

- Pattern 추가/삭제 후 `PatternRows`, Pattern 전압, 공통 설정 행이 동기화되는지 확인한다.
- 공통 창을 닫은 후 공통 사용 Pattern의 목록 값과 상세 폼 값이 즉시 갱신되는지 확인한다.
- `UseCommonRecipe=true`에서 개별 inspection control이 비활성화되는지 확인한다.
- 저장 전 `SyncCollectionsToDocument()`가 Pattern/공통 설정을 `ConsoleRecipeDocument`에 반영하는지 확인한다.
- IP 업로드 시 Pattern 검사 조건이 metadata가 아닌 `RecipeModel` 계약으로 전달되는 경로를 확인한다.

## 공식 문서와 코드 차이

- 공식 가이드는 `검사 패턴` 탭에서 Image/ROI 창을 통한 ROI 조정을 안내하지만, 현재 탭의 직접 진입 버튼은 주석 처리돼 있다.
- `공통 파라미터`와 Pattern별 공통 사용 여부는 현재 XAML/Console 모델에 구현되어 있으나, 공식 레시피 구조 요약 문서의 핵심 필드 설명에는 상세히 나타나지 않는다.

## 추가 확인 대상

- `RecipeImageWindow`: 실제 이미지 로드·ROI 그리기·저장 반영 흐름
- IP 검사 알고리즘: ThresholdInput 다중 후보 채점, Gain/Timeout 적용 범위
- `PatternPlanModel`/`InspectionConfigModel`: W pattern, defect cutoff, grade의 계약 기본값

[추론] Pattern별 전압은 Console의 PG 제어용 설정이며, `PatternPlanModel`의 PatternType/검사 설정과 별도 계층으로 병행 관리된다. PG 매핑 탭 및 점등 명령을 분석해 실제 우선순위를 확인해야 한다.
