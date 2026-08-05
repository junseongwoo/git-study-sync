# AlignWindow 개발 노트

## 주요 의존 관계

```text
RecipeWindow.OpenAlignWindow_Click
  → AlignWindow
      → AlignViewModel
          ├─ RecipeEditorViewModel / ConsoleAlignPlan
          ├─ AlignCameraPaneViewModel × 2
          ├─ AlignCameraRuntimeService / Basler
          ├─ CoordinateTransformService
          ├─ CenterPivotUvwConverter
          ├─ Vars.ControlRuntime
          ├─ Vars.EMRConfig.AlignCameras
          └─ AlignRunResultStore
```

## 데이터 소유

| 데이터 | 소유/저장 위치 |
|---|---|
| Template/Search rectangle, match threshold | Recipe `AlignPlan` |
| Align template 이미지 | Recipe 폴더 `align_left.png`, `align_right.png` |
| Y1/Y2 카메라 이름 | Config `AlignY1CameraName`, `AlignY2CameraName` |
| Pixel size 및 영상 축 방향 | Config `AlignCameras` |
| Align mark/PanelAngle/UVW 기구 기준 | Glass Size Model |
| 최근 실행 결과 | `align_result.json`, `LastAlignResult` |

## 구현 상태

- 카메라 Connect/Disconnect/Grab/Live/파일 Load·Save: 구현
- Template/Search rectangle viewer 편집: 구현
- Current/Grab evaluation: 구현
- ThetaThenXY 자동 Align: 구현
- Camera geometry 자동 교정: 구현
- UVW Jog/Axis→Glass 보조 창: 구현
- `RefreshDevicesAsync`: 현재 no-op으로 장치 목록 새로고침은 미구현
- 다른 correction mode: 실제 Align 실행에서 미지원

## 중요한 불일치

공식 좌표 문서는 Left Align=Y1, Right Align=Y2로 설명하지만 현재 창은 Left pane→Y2, Right pane→Y1로 Config에 저장한다. 물리 pane과 논리 mark 명칭의 차이인지 확정하고 다음을 정리할 필요가 있다.

1. UI label을 Y1/Y2 또는 CAM1/CAM2 중심으로 변경
2. `isLeft`가 screen side, mark role, unit 중 무엇을 의미하는지 타입/변수명으로 분리
3. `BuildAlignErrorSnapshot`의 Left/Right mark 전달과 pane mapping 단위 테스트

## 코드상 주의점

- Camera Name은 pane property 변경 즉시 Config store 저장을 시도한다. Recipe Save와 별도 생명주기다.
- Template/Search rectangle은 AlignPlan을 직접 수정하고 Recipe dirty 알림만 발생시킨다. Recipe Save가 필요하다.
- 실제 Align은 exclusive grab 전에 양쪽 Live를 정지한다.
- Camera calibration은 각 상대 이동 후 `finally`에서 원위치 이동을 시도한다. 복귀 실패에 대한 장비 상태 확인이 필요하다.
- `ConvertImageDeltaToStageDelta`는 X/Y pixel size 평균 하나를 두 축 projection에 곱한다. 비등방 pixel이 의미 있게 다른 장비에서 의도한 계산인지 검토가 필요하다. **[추론]**
- Camera calibration은 ±Theta 영상도 저장하지만 현재 `CalculateAlignCameraGeometry`는 ±X/±Y 데이터만 계산에 사용한다.
- Drag & Drop은 첫 번째 존재 파일만 고르고 확장자 선검증이 없다.

## 추가 확인 대상

1. `RecipeService.GetEffectiveAlignMarkPosition`의 Left/Right mark 해석
2. `MoveAlignReferencePositionOrThrowAsync`의 Y1/Y2 target 조립
3. `CenterPivotUvwConverter`와 실제 +Theta 부호 검증
4. `AlignRunResultStore`의 정확한 저장 경로와 DV 갱신 방식
5. 자동 검사에서 AlignWindow를 실제로 생성해 호출하는지, 별도 headless AlignViewModel 경로가 있는지

## 주요 소스

- `uLedAoiConsole/Windows/Recipe/AlignWindow.xaml`
- `uLedAoiConsole/Windows/Recipe/AlignWindow.xaml.cs`
- `uLedAoiConsole/ViewModels/AlignViewModel.cs`
- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml.cs`
- `docs/전체 flow.md`
- `docs/stage-glass-coordinate-system.md`
