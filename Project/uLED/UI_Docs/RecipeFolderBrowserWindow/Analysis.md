# RecipeFolderBrowserWindow 컨트롤 분석

## 1. 화면 목적

`RecipeFolderBrowserWindow`는 레시피를 **열기(Open)** 또는 **저장(Save)** 할 때 사용할 레시피 폴더 경로를 선택하는 공용 대화상자다.

공식 `recipe-folder-structure.md` 기준으로 Console 레시피의 저장 단위는 단일 JSON 파일이 아니라 레시피 폴더이며, 기본 구조는 다음과 같다.

```text
{RecipesDir}\{GlassSizeId}\{RecipeName}\recipe.json
```

이 창은 삭제·이름 변경 기능을 제공하지 않는다. 레시피를 선택하거나 저장 대상 경로를 만들기 위한 창이다.

## 2. 화면 구성

| 영역 | Open 모드 | Save 모드 |
|---|---|---|
| Header | 제목·설명 표시 | 제목·설명 표시 |
| 좌측 목록 | Glass Size Model 목록 | 숨김 |
| 우측 목록 | 검색창 + 레시피 목록 | 숨김 |
| 저장 입력 | 숨김 | Glass Size ID, 레시피 이름, 계산된 저장 경로 |
| Footer | 상태, 폴더 열기, 열기, 취소 | 상태, 폴더 열기, 저장, 취소 |

`RecipeFolderBrowserMode` enum이 `Open`이면 OpenContent만, 그 외 SaveContent만 보인다.

## 3. 컨트롤별 설명

### 3.1 공통 Header/Footer

| 컨트롤명 | 종류 | 기능 | 실제 동작 |
|---|---|---|---|
| `ModeTitleTextBlock` | TextBlock | 현재 모드 제목 | Open: `레시피 열기`, Save: `레시피 저장`으로 code-behind가 설정한다. |
| `ModeDescriptionTextBlock` | TextBlock | 현재 모드 사용 안내 | Open은 Size Model 필터 안내, Save는 Glass Size/이름 입력 안내를 표시한다. |
| `StatusTextBlock` | TextBlock | 상태 및 선택 경로 표시 | Open 초기에는 필터된 레시피 개수, 선택 후에는 선택한 `recipe.json` 전체 경로, 오류 시 안내문을 표시한다. |
| `OpenFolderButton` | Button | 탐색기에서 대상 폴더 열기 | Open에서는 선택 레시피가 있는 폴더, Save에서는 계산된 대상 경로의 상위 폴더를 연다. 폴더가 아직 없으면 열지 못하고 상태 메시지를 표시한다. |
| `OkButton` | Button | 모드별 확정 | Open: 선택 레시피 경로를 `SelectedRecipePath`에 설정하고 `DialogResult=true`. Save: Glass Size ID와 레시피 이름을 검증해 대상 경로를 설정하고 `DialogResult=true`. `IsDefault=True`이다. |
| 취소 Button | Button | 대화상자 취소 | `DialogResult=false`로 닫는다. `IsCancel=True`이다. |

### 3.2 Open 모드 컨트롤

| 컨트롤명 | 종류 | 기능 | 이벤트/동작 | 사용자 주의사항 |
|---|---|---|---|---|
| `OpenContent` | Grid | Open 모드 전체 영역 | Save 모드에서는 `Collapsed` | 직접 조작하지 않는 컨테이너다. |
| `SizeModelListBox` | ListBox | Glass Size Model별 레시피 필터 | `SelectionChanged`에서 `_selectedSizeModel`을 갱신하고 목록 filter를 새로 적용한다. | `전체 (All)`을 선택하면 모든 Glass Size의 레시피가 표시된다. |
| `SearchTextBox` | TextBox | 레시피 검색 | `TextChanged`마다 목록 filter를 다시 적용한다. | Glass Size ID, 레시피 이름, 설명, 파일 경로에 포함된 문자열을 대·소문자 구분 없이 찾는다. |
| `RecipeGrid` | ListBox | 검색/필터 결과인 레시피 목록 | `SelectionChanged`로 선택 경로를 반영하고, `MouseDoubleClick`으로 즉시 확정한다. | 이름과 설명만 표시된다. 설명이 없으면 `(설명 없음)`으로 표시된다. |
| RecipeGrid ItemTemplate | DataTemplate | 각 레시피의 제목/설명 표시 | `RecipeName`, `DescriptionDisplay` 바인딩 | 긴 이름/설명은 줄임표로 잘릴 수 있다. 전체 경로는 선택 후 footer에서 확인한다. |

### 3.3 Save 모드 컨트롤

| 컨트롤명 | 종류 | 기능 | 이벤트/동작 | 사용자 주의사항 |
|---|---|---|---|---|
| `SaveContent` | Border | Save 모드 입력 영역 | Open 모드에서는 `Collapsed` | 직접 조작하지 않는 컨테이너다. |
| `GlassSizeComboBox` | 편집 가능 ComboBox | 저장할 Glass Size ID 선택 또는 입력 | `SelectionChanged`와 `LostFocus`에서 대상 경로를 다시 계산한다. 기존 레시피/Glass Size JSON의 ID를 목록으로 제공한다. | 새 ID를 직접 입력할 수 있으나, 실제 Glass Size Model이 존재하는지 별도로 확인해야 한다. **[추론]** |
| `RecipeNameTextBox` | TextBox | 저장할 레시피 폴더명 입력 | `TextChanged`에서 대상 경로를 다시 계산한다. | 빈 값이면 저장할 수 없다. 파일명에 사용할 수 없는 문자는 사전에 검증되지 않는다. **[추론]** |
| `TargetPathTextBox` | 읽기 전용 TextBox | 계산된 저장 대상 표시 | `{GlassSizeId}`와 `{RecipeName}`이 모두 있으면 `Vars.GetRecipePath` 결과를 표시한다. | 실제 저장 완료나 폴더 생성 여부를 보장하지 않는다. 확정 후 상위 호출자가 저장을 수행한다. **[추론]** |

## 4. 이벤트 분석

| 이벤트 | 연결 메서드 | 처리 내용 |
|---|---|---|
| Window Loaded | `OnLoaded` | Window process 상태를 Ready로 전환한다. |
| Window Closing / Closed | `OnClosing` / `OnClosed` | 중복 종료를 막고 Closed 상태로 전환한다. |
| Size Model 선택 변경 | `SizeModelListBox_OnSelectionChanged` | Glass Size 필터 적용 및 결과 개수 갱신 |
| 검색어 변경 | `SearchTextBox_OnTextChanged` | 검색 filter 적용 및 결과 개수 갱신 |
| 레시피 선택 변경 | `RecipeGrid_OnSelectionChanged` | 선택한 `recipe.json` 경로를 `SelectedRecipePath`에 설정 |
| 레시피 더블 클릭 | `RecipeGrid_OnMouseDoubleClick` | 선택 항목이 있으면 열기 확정 |
| Save 입력 변경 | `SaveInput_OnChanged` | TargetPath 다시 계산 |
| 폴더 열기 | `OpenFolderButton_OnClick` | 대상/상위 폴더가 존재하면 Windows 탐색기 실행 |
| 열기/저장 | `OkButton_OnClick` → `ConfirmSelection` | 모드에 따라 선택 경로를 검증·확정 |
| 취소 | `CancelButton_OnClick` | `DialogResult=false` |

## 5. 데이터 흐름

```text
Vars.RecipesDir 아래 모든 recipe.json 검색
  → RecipeFolderEntry(GlassSizeId, RecipeName, Description, RecipePath)
  → ICollectionView Filter
      ├─ SizeModelListBox 선택
      └─ SearchTextBox 검색어
  → RecipeGrid 표시/선택
  → SelectedRecipePath
  → 호출 창이 DialogResult=true 확인 후 열기 또는 저장 수행
```

`LoadEntries()`는 `Vars.RecipesDir` 아래의 모든 `recipe.json`을 재귀 검색한다. 각 파일은 `RecipeStore.Open(..., autoLoad:true)`로 열어 Description을 읽는다. 읽기 실패한 레시피도 목록에서는 제외되지 않지만 Description은 빈 값으로 표시된다. **[추론]** 이 경우 선택 후 실제 레시피 로드 단계에서 실패할 수 있다.

Save 모드에서 목록의 Glass Size ID는 기존 레시피 항목과 `Vars.GlassSizesDir`의 `*.json` 파일명에서 합쳐 생성된다.

## 6. 사용자 입장에서 설명

### 레시피 열기

1. 좌측에서 Glass Size Model을 선택하거나 `전체 (All)`을 유지한다.
2. 필요하면 검색창에 레시피 이름·설명·Glass Size ID 일부를 입력한다.
3. 우측 목록에서 레시피를 한 번 선택한다.
4. footer에 표시된 실제 경로를 확인한다.
5. `열기`를 누르거나 항목을 더블 클릭한다.

### 레시피 저장

1. Glass Size ID를 목록에서 선택하거나 입력한다.
2. 레시피 이름을 입력한다.
3. 읽기 전용 `저장 경로`가 의도한 위치인지 확인한다.
4. `저장`을 누른다.

`폴더 열기`는 파일 자체가 아니라 해당 레시피가 속한 폴더를 Windows 탐색기에서 여는 기능이다. 저장 전에는 대상 폴더가 아직 존재하지 않아 열리지 않을 수 있다.

## 7. 업무 로직 추론

- 공식 문서에서 새 레시피는 특정 Glass Size Model을 선택한 뒤 시작한다. Open 모드의 Glass Size 필터와 Save 모드의 Glass Size ID 입력은 이 분류 규칙을 UI에서 지원한다.
- **[추론]** 이 창은 레시피 파일 내용을 수정하지 않는다. 호출자에게 `SelectedRecipePath`만 반환하며, 실제 `RecipeStore.Open` 또는 저장은 호출 창/서비스가 담당한다.
- **[추론]** 동일 Glass Size ID와 Recipe Name을 입력해도 이 창 자체에는 덮어쓰기 확인이 없다. 파일 존재 여부와 overwrite 정책은 실제 저장 호출부에서 확인해야 한다.
- **[추론]** `OpenFolderButton`은 선택·계산된 폴더가 존재할 때만 탐색기를 실행하므로, 새 레시피의 경로 확인 용도이지 폴더 생성 기능은 아니다.

## 8. 문서 작성용 요약

- 이 창은 레시피 폴더를 열거나 새 저장 대상 경로를 정하는 대화상자다.
- 열기 모드에서는 Glass Size별 필터와 문자열 검색으로 `recipe.json`을 찾는다.
- 저장 모드에서는 Glass Size ID와 레시피 이름을 입력하면 저장 경로를 미리 보여 준다.
- 이 창에는 레시피 삭제·복사·이름 변경·폴더 생성 기능이 없다.
- 저장 경로가 표시되더라도 실제 저장 성공은 다음 저장 단계에서 확인해야 한다.

## 9. 이해되지 않는 부분

| 확인 필요 항목 | 이유 |
|---|---|
| Save 모드 호출자와 overwrite 정책 | 이 창은 path만 반환한다. 기존 recipe.json 덮어쓰기 확인·실제 생성 로직은 호출자를 봐야 한다. |
| Glass Size ID 직접 입력의 유효성 검증 | ComboBox는 editable이지만 존재하지 않는 ID를 막지 않는다. 상위 저장 로직의 검증이 필요하다. |
| `recipe.json` parse 실패 항목의 최종 처리 | 목록 작성 시 오류를 삼키고 설명만 비운다. 실제 열기 단계의 오류 안내를 확인해야 한다. |
| 레시피 폴더를 새로 만드는 기능의 담당 위치 | 이 창에는 `Directory.CreateDirectory` 호출이 없다. 실제 저장 서비스 확인이 필요하다. |

## 10. 전체 프로젝트 연결

| 연결 대상 | 관계 |
|---|---|
| RecipeWindow 파일 메뉴 | 레시피 열기/저장 시 이 대화상자를 사용해 대상 경로를 선택한다. **[추론]** |
| MainWindow > Load Recipe | MainWindow의 파일 선택형 로드와 달리, 이 창은 프로젝트 표준 레시피 폴더 구조를 탐색하는 방식이다. **[추론]** |
| GlassSizeModel | 레시피 상위 분류인 Glass Size ID를 제공하며, Save 모드 목록의 후보에도 사용된다. |
| `RecipeStore` | 목록 생성에서 recipe.json의 Description을 읽고, 상위 호출부에서 선택 path를 실제 레시피로 열거나 저장한다. |
| Explorer | `폴더 열기`는 선택/대상 레시피 폴더를 외부 Windows 탐색기로 연다. |

### 참조 근거

- 공식 문서: `docs/recipe-folder-structure.md`, `docs/README.md`, `docs/development/change-log.md`
- UI/이벤트: `uLedAoiConsole/Windows/Recipe/RecipeFolderBrowserWindow.xaml`, `RecipeFolderBrowserWindow.xaml.cs`
