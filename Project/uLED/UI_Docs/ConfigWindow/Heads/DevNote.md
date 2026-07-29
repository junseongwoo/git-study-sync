# ConfigWindow - Heads 탭 개발 노트

## 1. 소유 모델과 바인딩

| UI 속성 | 설정 모델 |
|---|---|
| `AlignY1CameraName`, `AlignY2CameraName`, `ContactCheckCameraName` | `ULedConfig`의 동명 속성 |
| `AlignCameraItems` | 저장 시 `ULedConfig.AlignCameras` (`AlignCameraGeometryConfig`) |
| `InspectCameraOffsetX/Y`, `Y1/Y2Ca410OffsetY` | `HeadOffsets.Y1/Y2.InspectCameraFromAlignUm`, `.Ca410FromAlignUm` |
| `Y1/Y2IdleZUm`, `CaptureZUm`, `MeasureZUm`, `EscapeYUm` | `HeadOffsets.Y1/Y2` |
| `UnitEscapeYToleranceUm`, Z settle delay | `ULedConfig` 전역 값 |

## 2. 코드상 주의점

- `InspectCameraOffsetXText/YText`는 빈 문자열을 0으로, 소수 값을 정수 um로 반올림한다. UI 입력 정밀도와 모델 정밀도의 차이를 문서화하거나 컨트롤 표시를 정리할 필요가 있다.
- `AlignCameraItems` 저장 시 pixel size가 0 이하이면 1.0으로 대체하고, 방향 벡터는 정규화한다. **[추론]** 자동 대체는 잘못된 교정값을 정상처럼 저장할 위험이 있으므로 validation/error UI가 더 적합할 수 있다.
- `ReadHeadZAsync`는 현재 위치 조회만 하며 이동하지 않는다. 제어 연결과 status refresh를 수행한다.
- 실행 코드에서 CA410 offset은 `X = InspectCameraFromAlignUm.X`, `Y = Ca410FromAlignUm.Y`로 조합한다. 독립 CA410 X가 필요한 요구가 생기면 모델·UI·좌표 변환의 명시적인 확장이 필요하다.
- `ResolveCameraCaptureZ`는 Recipe `ControlPlan.Y1/Y2CameraCaptureZUm`을 Config CaptureZ보다 우선한다. 반면 CA410 MeasureZ는 Heads Config의 값을 사용한다.

## 3. 공식 문서와 코드 정합성

| 주제 | 공식 기준 | 코드 확인 |
|---|---|---|
| 도구 축 목표 | `GlassToAxis(target) - headOffsetFromAlignAxis` | Recipe/좌표 변환 호출에서 Inspect offset이 전달된다. |
| 안전 높이 | `IdleZ <= CaptureZ <= MeasureZ`, Escape 영역은 IdleZ 우선 | Heads 설정 모델과 검사 실행 보조 로직이 Y1/Y2 Z 값을 조회한다. |
| 촬영/측정 전 안정화 | Capture/Measure Z 이동 후 각각 settle delay | Config의 두 delay를 읽는 실행 코드가 있다. |
| 카메라 높이 override | Recipe Capture Z가 Config Capture Z보다 우선 | `ResolveCameraCaptureZ`에서 확인된다. |

## 4. 확인이 필요한 설계 항목

1. Y2 mirror camera geometry의 정확한 행렬/부호 규칙을 공식 문서 또는 장비 시험으로 확정한다.
2. 저장 중 Config 변경의 실행 적용 시점(Glass Job 시작 snapshot 여부)을 명시한다.
3. CA410 X 공통 사용이 기구 사양으로 보장되는지 확인한다.
4. `IdleZ <= CaptureZ <= MeasureZ`가 축 좌표의 실제 안전 방향과 일치하는지 축 설정 문서와 함께 확인한다.
5. Camera Name 중복, 빈 이름, 0 pixel size에 대한 저장 전 validation을 검토한다.

## 5. 주요 소스

- `uLedAoiConsole/Windows/Core/ConfigWindow.xaml`
- `uLedAoiConsole/ViewModels/ConfigViewModel.cs`
- `uLedAoiConsole/Models/ULedSettings.cs`
- `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`
- `uLedAoiConsole/Recipes/RecipeService.cs`
- `docs/main-glass-inspection-flow.md`
- `docs/stage-glass-coordinate-system.md`
