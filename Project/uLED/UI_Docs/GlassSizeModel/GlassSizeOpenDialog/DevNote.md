# Glass Size Model - GlassSizeOpenDialog 개발 노트

## 구성 책임

|구성 요소|책임|
|---|---|
|`MainWindow.xaml`|`OpenGlassSizeCommand` 메뉴 진입점을 제공한다.|
|`MainWindowViewModel`|창 열기 delegate를 호출하고 종료 후 glass map 갱신을 호출한다.|
|`MainWindow`|`GlassSizeWindow`를 모달로 생성한다.|
|`GlassSizeWindow`|시작 대상 해석, 후속 선택/생성 창 호출, `GlassSizeViewModel` 연결을 담당한다.|
|`GlassSizeOpenDialog`|현재 Recipe 모델/운영 모델/새 모델 중 사용자의 의도를 `GlassSizeOpenAction`으로 반환한다.|
|`GlassSizeViewModel`|모델 load, 새 모델 초안 생성, 저장 명령을 담당한다.|
|`GlassSizeStore`|JSON 로드·정규화·검증·저장·version/cache 관리를 담당한다.|

## 상태 계약

```csharp
public enum GlassSizeOpenAction
{
    None,
    OpenRecipeModel,
    SelectLibraryModel,
    CreateNew
}
```

다이얼로그는 `RecipeGlassSizeId`와 `SelectedAction`만 외부에 노출한다. 모델 자체, 파일 목록, ViewModel은 소유하지 않는다.

## 생명주기

`WindowProcessStateMachine` 규칙을 따른다.

```text
생성자: TrySetInitializing()
Loaded: SetReady()
Closing: TryEnterClosing() 실패 시 Cancel
Closed: SetClosed()
```

다이얼로그에는 별도 logger가 할당되어 있지 않다. **[추론]** 선택 동작 자체가 파일 변경이나 장치 제어를 수행하지 않아 현재는 로깅 경계가 상위 편집·store 처리 쪽에 있다.

## 상위 분기 구현

```csharp
return dialog.SelectedAction switch
{
    GlassSizeOpenAction.OpenRecipeModel => _viewModel.LoadById(dialog.RecipeGlassSizeId),
    GlassSizeOpenAction.SelectLibraryModel => SelectLibraryModel(),
    GlassSizeOpenAction.CreateNew => CreateNewModel(),
    _ => false
};
```

`startupGlassSizeId`가 전달된 경우에는 먼저 `LoadById()`를 시도한다. 이 경로가 실패할 때만 안내 후 시작 다이얼로그를 연다.

## Store와 식별 규칙

- 운영 파일은 `GlassSizeStore.GetGlassSizePath(Vars.WorkDir, id)`로 해석한다.
- store load 시 JSON 내부 ID가 아니라 파일명으로 `GlassSizeId`를 확정한다.
- store save 시에도 저장 경로 파일명으로 ID를 다시 설정한다.
- `GlassSizeModel` 유효성 검사는 width/height 양수, angle 90도 단위, axis direction, calibration 행렬, align mark 등을 확인한다.
- load cache는 파일 경로와 최종 수정 시각이 같으면 같은 메모리 instance를 반환한다.

시작 다이얼로그는 `File.Exists`까지만 확인한다. JSON parse·유효성 실패는 `GlassSizeViewModel.LoadById → GlassSizeStore.LoadFromPath`에서 처리한다.

## UI/코드 불일치 주의

`GlassSizeSelectionWindow`는 “Apply to Recipe”라는 UI와 확인 메시지를 제공한다. 하지만 `GlassSizeOpenDialog → SelectLibraryModel()` 경로에서는 반환된 `SelectedModel`의 ID로 `LoadById()`만 수행한다.

따라서 이 호출 경로에서 모델 선택을 Recipe 즉시 적용으로 바꾸려면, 셀 재생성·recipe 저장·history·현재 편집기 동기화 같은 별도 적용 책임을 명확히 설계해야 한다. 문구만 바꾸거나 model clone을 대입하는 방식으로 의미를 바꾸면 안 된다.

## 새 모델 흐름

```text
NewGlassSizeModelWindow
  → NewGlassSizeModelRequest
  → GlassSizeViewModel.AddGlassSize()
  → (copy source이면 JSON clone / 없으면 초기 구조 생성)
  → GlassSizeItemViewModel 선택
  → 별도 SaveCommand에서 파일 저장
```

복사 없는 새 모델은 3개의 left point(P1~P3), 3개의 right point(R1~R3), align mark 객체, 기본 axis direction과 기본 affine preset을 준비한다. 그 상태만으로 store validation을 통과한다고 가정하면 안 된다. **[추론]** 실제 치수·mark·calibration 값 입력 후 Save validation을 통과해야 운영 모델로 사용할 수 있다.

## 변경 시 검증 항목

|시나리오|기대 결과|
|---|---|
|Recipe에 유효한 GlassSizeId 존재|Recipe 모델 열기가 활성이고 해당 ID를 LoadById 한다.|
|ID 없음|버튼 비활성, 운영 모델 선택/새 모델 안내가 표시된다.|
|파일 없음|ID 뒤 “운영 라이브러리에서 찾을 수 없음” 표시, 버튼 비활성이다.|
|파일은 있으나 JSON 오류|다이얼로그는 열기 가능하나 load 단계에서 validation error가 상태 메시지에 표시된다.|
|취소|상위 GlassSizeWindow가 시작 단계에서 닫힌다.|
|운영 모델 선택|선택 모델이 편집 대상으로 열리고 Recipe ID가 즉시 바뀌지 않는지 확인한다.|
|새 모델|중복 파일명·금지 문자 차단, 복사/빈 모델 초안, Save 전 파일 미생성을 확인한다.|
|창 종료 후|Main ViewModel의 glass map 갱신 호출이 현재 map에 미치는 영향을 확인한다.|

## 관련 문서

- `docs/development/architecture-decisions.md` — 파일명과 GlassSizeId 동일 원칙
- `docs/development/change-log.md` — 시작 다이얼로그 외부 JSON 버튼 제거, 선택 UI·모델 관리 변경 기록
- `docs/console-recipe-document.md` — Recipe와 Glass Size 관계의 상위 설명
