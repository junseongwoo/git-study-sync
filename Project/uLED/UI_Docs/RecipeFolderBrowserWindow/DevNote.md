# RecipeFolderBrowserWindow 개발 노트

## 구현 구조

- code-behind 중심 대화상자이며 별도 ViewModel은 없다.
- 생성자 `mode`에 따라 `OpenContent`/`SaveContent`의 Visibility와 제목·확인 버튼 텍스트가 바뀐다.
- `_entriesView`는 `ICollectionView`이며 Size Model과 검색어 두 조건을 `FilterEntry`에서 함께 적용한다.
- Open 결과는 선택한 `RecipeFolderEntry.RecipePath`, Save 결과는 `Vars.GetRecipePath(glassSizeId, recipeName)`을 `SelectedRecipePath`로 반환한다.
- 창 lifecycle은 `WindowProcessStateMachine`으로 Initializing → Ready → Closing → Closed를 관리한다.

## 구현상 주의점

- `LoadEntries`는 `Vars.RecipesDir`에서 `recipe.json`을 재귀 탐색한다.
- Description 로드 예외를 숨기므로 손상 레시피도 목록에 남을 수 있다.
- Save 입력에는 파일명 금지문자/경로 traversal/중복 파일에 대한 이 창 내부 validation이 없다.
- Save 모드의 `TargetPathTextBox`는 안내용 계산값이며 실제 디렉터리를 만들지 않는다.

## 추가 확인 대상

1. `RecipeFolderBrowserWindow`를 호출하는 RecipeWindow의 Open/Save handler
2. 실제 저장을 담당하는 `RecipeStore`/`RecipeService`의 overwrite 및 directory 생성 정책
3. `Vars.GetRecipePath`의 경로 정규화·입력 검증 규칙
4. 레시피 parse 실패 시 상위 호출부의 사용자 오류 메시지
