# AlignWindow 분석

## 1. 화면 목적

`AlignWindow`는 RecipeWindow의 `OpenAlignWindow_Click`에서 열리는 Align 전용 시험·설정 창이다. 주요 목적은 다음과 같다.

- 좌·우 Align 카메라 연결, 단발 촬영 및 Live 영상 확인
- 레시피별 Align 기준 이미지 등록
- Template/Search 영역 설정과 template match 시험
- 현재 영상의 Align 오차 평가
- Align 기준 위치 이동
- Theta → XY 순서의 실제 UVW 보정 실행
- Align 카메라의 pixel 크기와 영상 방향 자동 교정
- UVW Jog 및 Axis→Glass 좌표 확인 보조 창 진입

공식 `전체 flow.md` 기준으로 Align은 Load 이후 Process 전에 수행하는 독립 단계다. Align 위치 이동은 `StartJob`이나 검사 `InputStep`의 책임이 아니며, 좌·우 기준 마크 촬영 → offset 계산 → UVW correction → 허용 오차 확인 순서로 수행한다.

## 2. RecipeWindow에서의 호출 흐름

```text
RecipeWindow
  → OpenAlignWindow_Click
  → DataContext가 RecipeEditorViewModel인지 확인
  → 기존 AlignWindow가 있으면 활성화
  → 없으면 new AlignWindow(recipeEditorViewModel)
  → Owner = RecipeWindow
  → modeless Show
```

`OpenAlignWindow_Click`은 단순히 창을 연다. RecipeWindow의 별도 `RunManualAlignFlow_Click`은 확인 후 먼저 Align 기준 위치로 이동하고, AlignWindow를 연 다음 좌·우 Live까지 시작한다.

## 3. 화면 구성

| 영역 | 주요 컨트롤 | 역할 |
|---|---|---|
| 상단 Recipe/작업 영역 | Recipe 요약, 경로, Emulation Mode, 작업 버튼 8개 | 현재 레시피 확인 및 Align 주요 작업 실행 |
| 좌측 카메라 영역 | 카메라 이름, 카메라 툴바, `leftViewer` | Left pane 영상과 template/search/match overlay |
| 우측 카메라 영역 | 카메라 이름, 카메라 툴바, `rightViewer` | Right pane 영상과 template/search/match overlay |
| 하단 결과 영역 | `AlignResultSummary`, 양쪽 상태 및 Match 결과 | 이동·평가·보정 결과와 카메라별 상태 표시 |

## 4. 상단 컨트롤 분석

| 컨트롤 | 종류/바인딩 | 기능 | 검사·설정 영향 |
|---|---|---|---|
| Current Recipe | TextBlock / `CurrentRecipeSummary` | IP Recipe ID와 Version 표시 | 현재 어느 레시피의 AlignPlan과 기준 이미지를 다루는지 확인한다. |
| Recipe Folder Path | TextBlock / `RecipeFolderPath` | 현재 recipe.json의 폴더 표시 | Align 기준 이미지 `align_left.png`, `align_right.png`의 저장 기준 폴더다. |
| Emulation Mode | CheckBox / `UseEmulationMode` | 양쪽 카메라의 Basler emulator 연결 모드 전환 | 카메라 입력만 emulation으로 바꾼다. **[추론]** Control/UVW 이동을 simulation으로 바꾸는 옵션은 아니므로 실제 Align 실행 전에 Control 상태를 별도로 확인해야 한다. |
| AlignMoveStatus | TextBlock | Align 위치 이동의 진행·성공·실패 표시 | Control 이동 결과 확인용이다. |
| Align 위치 이동 | Button / `MoveAlignPositionCommand` | 확인 후 Recipe의 AlignReferencePose 위치로 이동 | 실제 축 이동이 발생한다. RecipeWindow의 동일 기능 구현을 재사용한다. |
| 현재 이미지 평가 | Button / `EvaluateAlignCommand` | 현재 양쪽 이미지와 등록 template을 비교해 X/Y/Theta 오차 계산 | 새 촬영은 하지 않는다. 현재 frame, template, geometry가 모두 유효해야 한다. |
| 촬영 후 평가 | Button / `GrabAndEvaluateAlignCommand` | Live 정지 → 양쪽 단발 촬영 → Align 오차 평가 | 현재 장비 상태를 새 영상으로 평가하지만 축 보정 이동은 하지 않는다. |
| Align Image 등록 | Button / `SaveAlignImages_Click` | 현재 좌·우 frame을 recipe 폴더의 기준 이미지로 저장 | Live를 정지하고 두 영상이 모두 있을 때 `align_left.png`, `align_right.png`로 저장한다. 두 영상은 반드시 동일한 Align 상태에서 촬영해야 한다. |
| 실제 Align 실행 | Button / `RunThetaThenXyAlignCommand` | Theta 보정 후 XY 보정을 반복 실행 | 실제 UVW 상대 이동이 발생한다. `MaxIteration`, X/Y/Theta tolerance를 만족할 때까지 반복한다. 현재 구현은 `ThetaThenXY` 모드만 지원한다. |
| Camera 설정 | Button / `CalibrateAlignCameraGeometryCommand` | 실제 UVW 이동·촬영으로 카메라 geometry 계산 | Config의 `AlignCameras`에 PixelSize 및 +X/+Y 영상 방향을 저장한다. 장비 설정용 위험 동작이다. |
| UVW Jog | Button / `OpenUvwJogWindow_Click` | `UvwJogWindow` 열기 | X/Y/T 입력을 U/V/W 상대 이동으로 변환해 수동 확인한다. |
| Axis → Glass | Button / `OpenAxisGlassWindow_Click` | `AxisGlassCoordinateWindow` 열기 | 축 좌표와 Glass 좌표 변환을 확인한다. |

## 5. 좌·우 카메라 컨트롤 분석

양쪽 카메라 툴바의 구조와 동작은 동일하다.

| 컨트롤/ToolTip | 활성 조건 | 동작 |
|---|---|---|
| Camera Name TextBox | 항상 | 연결할 카메라 이름을 편집한다. LostFocus 시 바인딩된다. |
| Connect | 항상 | 선택 이름 또는 emulator 이름으로 카메라를 연결한다. |
| Disconnect | `IsConnected=true` | 카메라 연결을 종료한다. |
| Grab One | 연결됨 | 한 장을 촬영하고 viewer를 갱신·FitHeight 한다. |
| Start Live | 연결됨 | 연속 촬영을 시작한다. |
| Stop Live | `IsGrabbing=true` | 연속 촬영을 중지한다. |
| Load Image | 항상 | 파일 선택 창에서 current image를 불러온다. 카메라 없이 template match 시험에 사용할 수 있다. |
| Save Image | current image 있음 | 현재 이미지를 사용자가 지정한 이미지 파일로 저장한다. Recipe 기준 이미지 등록과는 별도 기능이다. |
| Load Align Image | 항상 | recipe 폴더의 고정 기준 이미지 `align_left.png` 또는 `align_right.png`를 로드한다. |
| Test Match | current image 있음 | current image와 Align Image를 template match하고 score·중심 차이를 표시한다. Align Image가 없으면 실패한다. |
| Select Search Area | current image 있음 | viewer의 Search rectangle을 선택해 편집할 수 있게 한다. |
| `RatelViewer` | 항상 | 이미지, template/search 사각형, 이미지 중심선 및 match 결과를 표시한다. |

### Camera Name 변경 영향

코드에서 pane의 Camera Name 변경은 즉시 Config에 반영되고 Config store 저장을 시도한다.

- 화면 왼쪽 pane → `Config.AlignY2CameraName`
- 화면 오른쪽 pane → `Config.AlignY1CameraName`

따라서 카메라 이름은 단순한 임시 선택이 아니라 이후 Heads/Align 연결에도 영향을 주는 장비 설정값이다.

### 공식 문서와 현재 코드의 명칭 차이

공식 `stage-glass-coordinate-system.md`는 다음 기준을 설명한다.

- Left Align = 우상 mark, Unit1/Y1
- Right Align = 우하 mark, Unit2/Y2

현재 AlignWindow는 왼쪽 pane을 Config Y2에, 오른쪽 pane을 Config Y1에 저장하며 하단에도 왼쪽 `2`, 오른쪽 `1`을 표시한다.

**코드 불일치 표시:** 공식 문서의 논리적 Left/Right mark 명칭과 현재 창의 화면 좌/우 pane 명칭이 동일한 의미가 아니다. **[추론]** 현재 창의 `LeftCamera`/`RightCamera`는 화면 배치 또는 물리 카메라 위치를 뜻하고, 공식 문서의 `Left Align`/`Right Align`은 mark 역할을 뜻하는 것으로 보인다. 운영 문서에서는 Y1/Y2 및 CAM1/CAM2를 함께 표기해 혼동을 피해야 한다.

## 6. Viewer와 Overlay 분석

| Overlay | 표시 | 데이터 소유 |
|---|---|---|
| Template rectangle | 주황색 실선 | `AlignPlan.Left/RightTemplateRect` |
| Search rectangle | 하늘색 점선 | `AlignPlan.Left/RightSearchAreaRect` |
| 이미지 중심선 | Cyan 가로/세로선 | 현재 이미지 Width/Height 중심 |
| Match rectangle | LimeGreen 점선 | 최근 template match 검출 위치 |
| Match center | LimeGreen 십자선 | 최근 match 중심 |

Viewer에서 Template/Search rectangle을 이동하거나 크기를 바꾸면 AlignPlan의 pixel rectangle 값이 갱신되고 RecipeEditorViewModel에 AlignPlan 변경을 알린다. 따라서 rectangle 편집 후 Recipe를 저장해야 다음 실행에서도 유지된다.

Viewer 이미지를 클릭하면 해당 image pixel 좌표가 `AlignResultSummary`와 로그에 추가된다. 클릭은 축 이동 명령이 아니다.

이미지 파일을 viewer에 Drag & Drop하는 기능도 code-behind에 구현되어 있다. 첫 번째 존재 파일을 current image로 불러오며 지원 확장자 자체를 Drop 단계에서 제한하지는 않는다. **[추론]** 실제 디코딩 가능 여부는 이미지 로더에서 결정된다.

## 7. 주요 실행 로직

### 7.1 창 초기화·종료

```text
Window Loaded
  → Viewer drag/drop 및 shape event 연결
  → overlay 초기화 / FitHeight
  → RefreshDevicesAsync (현재 no-op)
  → Left/Right camera 병렬 자동 Connect

Window Closing
  → 중복 종료 차단
  → AlignViewModel.DisposeAsync
  → 카메라 Live/연결 정리
  → UVW Jog, Axis→Glass 자식 창 닫기
```

`RefreshDevicesAsync()`는 현재 `Task.CompletedTask`만 반환하므로 실제 장치 목록 재검색 기능은 **미구현 상태**다. 다만 창 초기화의 자동 Connect는 별도로 구현되어 있다.

### 7.2 현재 이미지 평가

```text
각 pane의 Current Image 확인
  → align_left/right.png 확인
  → AlignPlan TemplateRect/SearchAreaRect로 template match
  → MatchScore ≥ MatchThreshold인지 확인
  → Config.AlignCameras geometry로 pixel delta → Stage um delta 변환
  → Glass Size의 Left/Right Align mark 간격으로 Theta 계산
  → 회전 성분 제거 후 좌/우 translation 일관성 검증
  → 평균 X/Y translation + Theta 결과 표시
```

좌·우 translation 차이는 최소 30 um 또는 `max(ToleranceX, ToleranceY) × 3` 중 큰 값을 초과하면 실패한다. 이는 두 카메라가 서로 모순되는 결과를 낼 때 잘못된 UVW 이동을 막는 검증이다. **[추론]**

### 7.3 실제 Align 실행

공식 flow와 현재 구현의 순서는 다음과 같다.

```text
확인 대화상자
  → CorrectionMode가 ThetaThenXY인지 검증
  → Glass Size/UVW parameter 로드
  → align_left/right.png 로드
  → AlignReferencePose로 이동
  → 반복 1..MaxIteration
      1) 양쪽 촬영 및 Theta/X/Y 평가
      2) 허용 오차 이내면 완료
      3) Theta 초과 시 UVW 회전 이동
      4) 재촬영 및 XY 평가
      5) X/Y 초과 시 UVW 병진 이동
      6) 재촬영 및 최종 tolerance 확인
  → 성공/실패 결과 기록
```

성공과 실패 모두 `AlignRunResultStore`를 통해 `align_result.json` 및 `LastAlignResult`에 기록된다. 기록값에는 최종 dX/dY/dTheta, tolerance, 좌·우 score, 누적 U/V/W, recipe 이름이 포함된다.

### 7.4 Camera 설정

Camera 설정은 다음 실제 이동을 수행한다.

```text
Ori 촬영
  → +X 1000 um 촬영 → 원위치
  → -X 1000 um 촬영 → 원위치
  → +Y 1000 um 촬영 → 원위치
  → -Y 1000 um 촬영 → 원위치
  → +Theta 0.1 deg 촬영 → 원위치
  → -Theta 0.1 deg 촬영 → 원위치
```

각 촬영은 `Data/AlignCamImage/yyyyMMdd_HHmmss`에 BMP로 저장된다. ±X/±Y의 match 중심 차이로 다음 Config 값을 계산한다.

- `PixelSizeXUm`, `PixelSizeYUm`
- `StagePlusXImageUnitX/Y`
- `StagePlusY1ImageUnitX/Y`

계산 결과를 사용자에게 보여 주고 한 번 더 저장 확인을 받은 뒤 `Config.AlignCameras`에 반영한다.

Theta ±0.1° 이미지도 촬영·저장하지만 현재 geometry 계산식에서는 X/Y 결과만 직접 사용한다. **[추론]** Theta 영상은 현장 검증 또는 추후 확장용 자료로 보인다.

## 8. Align Image 등록 흐름

1. 현재 레시피가 먼저 저장되어 Recipe Folder가 있어야 한다.
2. 좌·우 카메라는 동일한 Align 상태에서 각각 current image를 가져야 한다.
3. `Align Image 등록`을 누르면 확인창이 나타난다.
4. Live 중이면 양쪽 Live를 먼저 중지한다.
5. 양쪽 frame 중 하나라도 없으면 등록하지 않는다.
6. `align_left.png`, `align_right.png`에 모두 성공적으로 저장된 경우에만 AlignPlan의 표준 파일명을 반영한다.

개별 `Save Image`는 사용자가 지정한 임의 파일에 current image를 저장하는 기능이고, `Align Image 등록`은 자동 Align에서 사용하는 공식 recipe sidecar 이미지 세트를 갱신하는 기능이다.

## 9. 사용자 입장에서의 권장 순서

1. Recipe를 먼저 저장하고 화면 상단 Recipe ID/경로를 확인한다.
2. Y1/Y2 및 CAM1/CAM2 대응을 확인한 뒤 카메라 이름을 설정한다.
3. 좌·우 카메라가 모두 연결됐는지 확인한다.
4. `Align 위치 이동`으로 기준 위치에 이동한다.
5. Live로 두 mark가 정상 위치에 보이는지 확인한 뒤 Live를 중지한다.
6. Template rectangle은 특징이 분명한 mark 영역에, Search rectangle은 예상 이동을 포함할 만큼 넓게 설정한다.
7. 동일한 정상 Align 상태의 좌·우 frame을 `Align Image 등록`으로 저장한다.
8. `촬영 후 평가`로 score 및 X/Y/Theta가 정상인지 확인한다.
9. 저속·안전 상태에서만 `실제 Align 실행`을 수행한다.
10. Camera geometry가 검증되지 않았을 때만 장비 셋업 담당자가 `Camera 설정`을 수행한다.

## 10. 전체 프로젝트 연결

| 연결 대상 | 관계 |
|---|---|
| RecipeWindow > Align / 제어 | MaxIteration, tolerance, correction mode, Template/Search rectangle 등 AlignPlan을 공유한다. |
| Glass Size Model | Align mark 좌표, PanelAngle, UVW center-pivot parameter의 기준이다. |
| ConfigWindow > Heads | Y1/Y2 Align Camera 이름 및 `Config.AlignCameras` geometry를 공유한다. |
| Control runtime | AlignReferencePose 절대 이동과 U/V/W 상대 보정을 수행한다. |
| Main glass inspection flow | Load 이후 Process 전에 자동 Align을 실행하는 동일 `RunThetaThenXyAlignForInspectionAsync` 진입점을 제공한다. |
| UvwJogWindow | Align 검증을 위한 수동 X/Y/T → U/V/W 상대 이동 창이다. |
| AxisGlassCoordinateWindow | Axis 좌표와 Glass 좌표 변환 확인 창이다. |
| Recipe folder | `align_left.png`, `align_right.png` template sidecar를 저장한다. |

### 공식 문서와 코드 차이 요약

| 항목 | 공식 문서 | 현재 코드 |
|---|---|---|
| Left/Right Align 명칭 | Left=Y1/우상, Right=Y2/우하 | 화면 Left pane→Y2, Right pane→Y1 |
| Align 순서 | 위치 이동→촬영→offset→correction→tolerance 반복 | ThetaThenXY 방식으로 구현됨 |
| 생산 flow | Load 이후 Process 전 별도 Align 단계 | 검사에서 호출 가능한 `RunThetaThenXyAlignForInspectionAsync` 제공 |

### 참조 근거

- 공식 문서: `docs/전체 flow.md`, `docs/main-glass-inspection-flow.md`, `docs/stage-glass-coordinate-system.md`, `docs/uvw-coordinate-calibration-standard.md`
- UI/Code-behind: `uLedAoiConsole/Windows/Recipe/AlignWindow.xaml`, `AlignWindow.xaml.cs`
- ViewModel: `uLedAoiConsole/ViewModels/AlignViewModel.cs`
- 호출부: `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml.cs`
