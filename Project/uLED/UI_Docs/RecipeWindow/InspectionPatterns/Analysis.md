# RecipeWindow / 검사 패턴 탭 분석

## 1. 화면 목적

### 공식 문서 기준

IP의 실행 단위는 `Pattern × Point` 조합이며, 모든 Pattern은 공통 Point 집합을 공유한다. Pattern은 조명·검사 조건을, Point는 촬영 위치와 ROI를 담당한다. `RecipeWindow`에서는 Pattern/Point/ROI를 조정한 뒤 Validate, Save, Upload/Activate 순으로 진행한다.

공식 문서는 노출값을 외부 카메라 전용 프로그램의 Live 화면에서 먼저 확정한 뒤, 그 값을 Pattern의 `ExposureUs`에 반영하는 운영 순서를 안내한다.

근거: `docs/프로젝트 구조.md`, `docs/전체 flow.md`, `docs/recipe-editor-requirements.md`, `docs/시작 가이드.md`, `docs/rgb-level-inspection-algorithm.md`.

## 2. 화면 구성

| 영역 | XAML 구성 | 역할 |
|---|---|---|
| 상단 작업 버튼 | 패턴 추가 / 패턴 삭제 / 공통 파라미터 | Pattern 행을 관리하고 공통 검사 기준 창을 연다. |
| 검사 패턴 목록 | DataGrid | 전체 Pattern의 핵심 조건을 한 표에서 확인·편집한다. |
| 선택된 패턴 | 상세 폼 | 선택 Pattern의 개별 검사 조건을 편집한다. |
| 검사 ROI | 상세 폼 | 현재 기본 Point(`PrimaryPoint`)의 ROI 좌표·크기를 편집한다. |

상단/목록과 상세 영역은 `GridSplitter`로 높이를 조정할 수 있다.

## 3. 검사 패턴 목록

| 열 | 바인딩 | 의미 |
|---|---|---|
| 번호 | `Pattern.PatternIndex` | Pattern 식별 인덱스 |
| 이름 | `Pattern.PatternName` | Pattern 표시 이름 |
| 종류 | `Pattern.PatternType` | 검사 Pattern 유형 |
| R/G/B 전압 | `Voltage.Red/Green/BlueVoltage` | Pattern별 RGB 전압 설정 |
| 노출(us) | `Pattern.ExposureUs` | 카메라 노출 시간 |
| 공통 사용 | `UseCommonRecipe` | 공통 검사 파라미터를 이 Pattern에 적용할지 여부 |
| 기준 상위 %, 임계값, 면적/폭/높이 | Pattern InspectionConfig | 검사 기준 요약 |

`공통 사용`이 켜진 행은 임계값·면적·Blob 크기·정상레벨 기준 등 공통 관리 항목의 편집이 잠긴다. 목록에는 공통값이 반영된 실제 적용값이 표시된다.

## 4. 선택된 패턴 상세 설정

| 항목 | 바인딩 | 기능 |
|---|---|---|
| 공통 파라미터 사용 | `SelectedPatternRow.UseCommonRecipe` | 공통 InspectionConfig를 적용한다. |
| 공통 값 복사해 오기 | `CopyCommonRecipeToSelectedPatternCommand` | 공통값을 선택 Pattern의 설정으로 복사한다. |
| 이름 | `SelectedPattern.PatternName` | Pattern 이름 수정 |
| Timeout / 노출 / Gain | `TimeoutMs`, `ExposureUs`, `Gain` | 입력 대기·카메라 입력 조건 |
| 임계값 | `InspectionConfig.ThresholdInput` | 단일 값 또는 콤마 목록의 threshold 입력 |
| 면적 최소/최대 | `MinArea`, `MaxArea` | Blob 면적 필터 |
| Blob 폭/높이 최소/최대 | `BlobMin/MaxWidth/Height` | Blob 형상 필터 |
| 정상레벨 기준 상위 % | `SelectedPatternReferenceTopPercent` | 정상레벨 산출에 사용할 상위 백분위 영역 |
| 절대값 | `SelectedPatternUseAbsoluteLevel` | 등급 기준을 비율 대신 gray-level 절대값으로 해석 |
| 등급 A/B/C 기준 % | `GradeSpec.GradeA/B/CMinRatioPercent` | Pattern별 grade 하한 |

`절대값`을 켜면 정상레벨 기준 상위 % 입력은 비활성화된다. 이는 정상레벨 기반 비율 판정을 사용하지 않는다는 UI 정책이다.

### 공식 알고리즘 연결

공식 문서상 Pattern 검사는 ROI 안에서 threshold와 connected component로 blob을 검출하고, grid 복원/level 측정/정상레벨 대비 ratio/grade 계산을 수행한다. 이 탭의 threshold, blob 크기, 정상레벨 기준, grade 값은 그 검사 조건을 입력하는 위치다.

## 5. 검사 ROI

ROI 영역은 `PrimaryPoint`의 `RoiX`, `RoiY`, `RoiWidth`, `RoiHeight`에 직접 바인딩된다.

공식 문서상 현재 운영에서는 Point를 사실상 단일 ROI 설정으로 사용한다. 따라서 이 탭에서 보이는 ROI는 Pattern 개별 ROI가 아니라 공통 Point/ROI 설정이다.

### 코드 차이

공식 시작 가이드는 `검사 패턴` 탭의 `Inspection ROI` 영역과 `Recipe Image / ROI` 창에서 ROI를 조정한다고 설명한다. 현재 검사 패턴 탭의 `이미지 창 열기` 버튼은 XAML에서 주석 처리되어 있어, 이 탭에서 직접 이미지 창을 열 수 없다. 이미지 창은 현재 RecipeWindow 상단 `창 > 이미지 창` 메뉴에서 열 수 있다.

## 6. 버튼 및 새 창 분석

### 탭에서 직접 실행되는 버튼

| 버튼 | 처리 | 새 창 여부 |
|---|---|---|
| 패턴 추가 | `AddPatternCommand` | 없음 |
| 패턴 삭제 | `RemovePatternCommand` | 없음 |
| 공통 값 복사해 오기 | `CopyCommonRecipeToSelectedPatternCommand` | 없음 |
| 공통 파라미터... | `OpenCommonRecipeParameterWindow_Click` | 있음 |

### CommonRecipeParameterWindow

`공통 파라미터...`는 `CommonRecipeParameterWindow`를 열고, 부모 RecipeWindow와 동일한 `RecipeEditorViewModel`을 DataContext로 사용한다. 이 창을 닫으면 `ApplyCommonRecipeToCommonPatterns()`가 호출되어 `공통 사용` Pattern들에 변경된 공통값을 다시 복사한다.

| 공통 창 항목 | 바인딩 | 의미 |
|---|---|---|
| 임계값 | `CommonInspectionConfig.ThresholdInput` | 공통 threshold |
| 정상레벨 기준 / 절대값 | `CommonReferenceTopPercent`, `CommonUseAbsoluteLevel` | 공통 정상레벨/절대값 mode |
| 등급 A/B/C | `CommonInspectionConfig.GradeSpec` | 공통 grade 하한 |
| 불량 판정 기준 등급 | `DefectCutoffGrade` | defect 처리 cutoff grade |
| 면적/Blob 폭/높이 | `CommonInspectionConfig` | 공통 blob 필터 |

이 창은 `닫기` 버튼만 제공하며, 입력값은 부모와 공유하는 ViewModel에 즉시 반영된다. 별도의 OK/Cancel 복제본이나 되돌리기 기능은 확인되지 않는다.

### [추론] 공통값 적용 방식

공통값은 참조 공유가 아니라 `InspectionConfig`를 복제해 각 Pattern에 반영하는 방식으로 보인다. 따라서 공통 창에서 값을 바꾼 직후에는 창을 닫아 재반영하거나, 공통 사용을 다시 켜는 동작이 필요할 수 있다. 실제 적용 시점은 `ApplyCommonRecipeToCommonPatterns()` 호출을 기준으로 확인한다.

## 7. 주요 이벤트/명령

- `AddPatternCommand`: 새 Pattern과 공통 설정 행·전압 기본값을 추가한다.
- `RemovePatternCommand`: 선택 Pattern을 삭제한다.
- `CopyCommonRecipeToSelectedPatternCommand`: 공통 InspectionConfig를 선택 Pattern에 복사하고 상세 바인딩을 갱신한다.
- `OpenCommonRecipeParameterWindow_Click`: 창을 1개만 열거나 기존 창을 활성화한다.
- `CommonRecipeParameterWindow.Closed`: 공통 사용 중 Pattern에 공통값을 재반영한다.

## 8. 주의 및 추가 확인

- Pattern은 Point에 종속되지 않으며, 모든 Pattern이 공통 Point 집합을 공유한다.
- 노출값은 공식 가이드에 따라 외부 카메라 프로그램에서 확인한 뒤 `ExposureUs`에 반영한다.
- 공통 사용 Pattern의 잠긴 값은 개별값이 아니라 공통 적용값이다.
- [추론] `ThresholdInput`의 다중 후보 중 최종 선택 점수는 각 후보의 통과 개수와 병합 감점으로 판단한다는 XAML 툴팁이 있으나, 정확한 점수식은 IP 검출 코드 확인이 필요하다.
- [추론] `TimeoutMs`와 `Gain`의 실제 카메라/통신 적용 범위는 IP 입력 명령 구현을 확인해야 한다.

## 근거 파일

- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\docs\시작 가이드.md`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\docs\rgb-level-inspection-algorithm.md`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\Windows\Recipe\RecipeWindow.xaml`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\Windows\Recipe\RecipeWindow.xaml.cs`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\Windows\Recipe\CommonRecipeParameterWindow.xaml`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\Windows\Recipe\CommonRecipeParameterWindow.xaml.cs`
- `D:\ELP\Project\01.SDC\A1\uLED\Source\uLED_Develop_최신\uLedAoiConsole\ViewModels\RecipeEditorViewModel.cs`
