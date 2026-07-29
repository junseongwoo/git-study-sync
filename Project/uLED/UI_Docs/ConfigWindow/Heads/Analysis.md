# ConfigWindow - Heads 탭 분석

## 1. 화면 목적

`ConfigWindow > Heads`는 두 검사 헤드(Y1, Y2)의 카메라 식별자, Align 카메라 영상 좌표계, Align 기준 도구 오프셋, 안전 이동 및 Z 높이를 관리하는 장비 공통 설정 화면이다.

공식 문서 기준으로 Y1은 기존 Right/CAM1, Y2는 기존 Left/CAM2에 대응하며, Align·CA410·검사 카메라는 동일한 Y축 번호의 mirror 구조로 운용한다. 즉 이 탭은 레시피별 검사 조건이 아니라, **각 물리 헤드가 Glass 좌표의 목표를 어떤 축 위치와 높이에서 수행할지**를 정의한다.

공식 좌표계 문서의 도구 목표 계산식은 다음과 같다.

```text
toolAxisTarget = GlassToAxis(desiredGlassTarget) - headOffsetFromAlignAxis
```

따라서 오프셋 또는 카메라 좌표계가 틀리면 Align은 성공하더라도 검사 카메라 또는 CA410이 의도한 Glass 지점에 도달하지 못한다.

## 2. 화면 구성

| 구역 | 표시 컨트롤 | 설정 대상 |
|---|---|---|
| Head Mapping | Y1/Y2 Align Camera, Contact Check Cam | 사용할 물리 카메라 이름 |
| Align Camera Geometry | `AlignCameraItems` DataGrid | 카메라 pixel 크기와 축 이동에 대한 영상 방향 벡터 |
| Align 기준 Offset (Glass 0deg) | Y1/Y2 별 Inspect/CA410/Escape Y/Idle·Capture·Measure Z | Align 기준에서 각 도구 위치와 안전 이동 높이 |
| 이동 보조값 | Escape Y 허용 오차, Capture/Measure Z 안정화 시간 | 안전 구역 판정과 높이 이동 후 대기 시간 |

단위는 별도 표기가 없는 오프셋·축 위치·Z 위치가 `um`, Z 안정화 시간은 `ms`이다. `Pixel X/Y`는 `um/pixel`이다.

## 3. 컨트롤 분석

### 3.1 Head Mapping

| 컨트롤 | 바인딩/저장값 | 설정 방법 | 검사 영향 |
|---|---|---|---|
| Y1 Align Camera | `AlignY1CameraName` → `Config.AlignY1CameraName` | 장비의 Y1 Align 카메라 `UserDefinedName`과 정확히 동일하게 입력한다. 기본 구성은 CAM1이다. | Y1 Align 영상을 가져올 카메라를 선택한다. 이름이 틀리면 Y1 Align 연결·촬영이 실패하거나 의도하지 않은 카메라를 사용할 수 있다. |
| Y2 Align Camera | `AlignY2CameraName` → `Config.AlignY2CameraName` | Y2 물리 카메라 이름을 입력한다. 기본 구성은 CAM2이다. | Y2 Align의 카메라 선택 기준이다. Y1/Y2를 바꾸어 입력하면 mirror 헤드와 실제 카메라의 대응이 깨진다. |
| Contact Check Cam | `ContactCheckCameraName` → `Config.ContactCheckCameraName` | 컨택 확인 전용 카메라 이름을 입력한다. 기본 구성은 CAM3이다. | Contact Check 시퀀스가 이 카메라를 연다. XAML 안내처럼 `uLedCameraViewer`가 점유 중이면 컨택 시퀀스가 거부된다. 일반 검사 헤드의 검사 카메라 오프셋을 선택하는 값은 아니다. |

### 3.2 Align Camera Geometry DataGrid

| 열 | 모델 속성 | 의미 및 검사 영향 |
|---|---|---|
| Camera Name | `Name` | 위 Y1/Y2 Align Camera 이름과 대응되는 geometry 행의 키이다. 이름 불일치는 해당 카메라의 geometry를 찾지 못하게 할 수 있다. |
| Pixel X / Pixel Y (um) | `PixelSizeXUm`, `PixelSizeYUm` | 영상 pixel 이동량을 실제 길이(um)로 환산하는 비율이다. 값이 커지면 동일 pixel 오차가 더 큰 물리 오차로 환산되어 Align 보정 이동량도 커진다. 반드시 실제 배율·해상도 기준으로 교정한다. |
| +StageX Img UX/UY | `StagePlusXImageUnitX/Y` | 스테이지 +X 이동이 영상의 어느 단위 방향으로 나타나는지를 나타내는 2차원 방향 벡터다. 축 방향 또는 부호가 틀리면 X 보정이 반대 또는 비스듬한 방향으로 적용될 수 있다. |
| +Y1 Img UX/UY | `StagePlusY1ImageUnitX/Y` | Y1 축의 +방향이 영상에서 보이는 단위 방향 벡터다. Y1의 이동 방향 교정에 사용된다. |

저장 시 ViewModel은 각 행의 두 방향 벡터를 정규화한다. 즉 벡터의 길이 자체가 아니라 **방향**이 의미를 가지도록 처리한다. pixel 크기는 0보다 커야 하며, 코드상 0 이하 값은 저장 시 `1.0`으로 대체된다. 이는 잘못된 입력을 숨길 수 있으므로 운영자는 0을 유효값으로 사용하면 안 된다.

`+Y1`만 화면에 노출되고 Y2 전용 방향 열이 없는 이유 및 Y2 mirror 변환의 정확한 부호 규칙은 공식 문서에 명시되지 않았다. **[추론]** 현재 화면 구조는 Y1 방향 정의와 헤드별 mirror 관계를 조합하여 Y2 Align 보정을 해석하려는 설계로 보인다. 실제 장비에서 Y2 보정 방향을 반드시 별도 검증해야 한다.

### 3.3 Align 기준 Offset (Glass 0deg)

| 컨트롤 | 저장 위치 | 설정 방법 | 검사 진행 영향 |
|---|---|---|---|
| Y1/Y2 Inspect X, Y | `HeadOffsets.Y1/Y2.InspectCameraFromAlignUm.X/Y` | Align 카메라로 기준점을 맞춘 후, 같은 Glass 지점이 검사 카메라 중심에 오도록 필요한 X·해당 Unit Y 차이를 실측해 입력한다. 부호는 임의로 맞추지 말고 실제 이동 검증으로 확정한다. | 셀 검사 카메라의 목표 축 좌표 계산에 사용된다. 공식 식처럼 Glass→Axis 결과에서 이 오프셋을 빼므로 X/Y 값 변화만큼 검사 카메라의 실제 위치가 이동한다. 값이 틀리면 모든 셀의 촬영 중심이 같은 방향으로 벗어날 수 있다. |
| Y1/Y2 CA410 Y | `HeadOffsets.Y1/Y2.Ca410FromAlignUm.Y` | Align 기준점에서 CA410 측정 중심까지의 해당 Y 차이를 실측해 입력한다. | CA410 도구 위치를 계산할 때 사용한다. 코드상 CA410의 X는 Inspect X를 공통 사용하고, Y만 이 설정값을 사용한다. 따라서 CA410 Y만 수정해도 CA410 측정 위치만 바뀌며 검사 카메라 Y는 바뀌지 않는다. **[추론]** CA410 X를 독립 보정해야 하는 장비라면 현재 UI만으로는 직접 입력할 수 없다. |
| Y1/Y2 Escape Y | `HeadOffsets.Y1/Y2.EscapeYUm` | 해당 헤드를 충돌 회피 위치로 이동시킬 Y 축 절대 좌표를 장비 안전 위치에서 티칭한다. `Read Axis`는 현재 축 위치를 읽어 입력칸에 반영할 뿐, 축을 움직이지 않는다. | 대상 없는 반대 헤드를 회피시키는 위치다. 공식 flow에서 이 영역으로 이동할 때 Idle Z 안전 높이를 먼저 확보한다. 잘못된 값은 헤드 간섭 또는 불필요한 이동을 유발할 수 있다. |
| Y1/Y2 Idle Z | `HeadOffsets.Y1/Y2.IdleZUm` | Escape Y 영역에서 안전한 Z 높이를 티칭한다. | 공식 기준상 회피 영역 이동 전 필요한 충돌 회피 높이다. 값이 없거나 실행 조건에 맞지 않으면 안전 이동을 수행할 수 없다. |
| Y1/Y2 Capture Z | `HeadOffsets.Y1/Y2.CaptureZUm` | 검사 카메라가 초점·작업 거리를 만족하는 높이를 티칭한다. | 일반 XY/Y 이동의 최소 허용 높이이자 카메라 입력 직전의 촬영 높이이다. 단, 레시피 `ControlPlan.Y1CameraCaptureZUm` 또는 `Y2CameraCaptureZUm`이 있으면 그 레시피 값이 Config Capture Z보다 우선한다. |
| Y1/Y2 Measure Z | `HeadOffsets.Y1/Y2.MeasureZUm` | CA410이 실제로 측정해야 하는 높이를 티칭한다. | CA410 측정 직전에 해당 Z로 이동하고 안정화 대기 후 측정한다. Capture Z와 혼용하면 카메라 촬영 또는 CA410 측정의 작업 거리가 틀어질 수 있다. |
| Escape Y Tolerance | `UnitEscapeYToleranceUm` | Escape 위치에서 허용할 축 위치 오차 범위를 um로 입력한다. 음수는 ViewModel에서 0으로 제한된다. | 현재 Y가 Escape Y 근처인지 판정하는 범위다. 너무 작으면 안전 위치에 있어도 escape 상태로 인식하지 못할 수 있고, 너무 크면 일반 위치를 escape로 잘못 분류할 수 있다. |
| Capture Z Settle Delay | `CaptureZSettleDelayMs` | Capture Z 이동 후 진동·초점 안정에 필요한 시간을 ms로 입력한다. 음수는 0으로 제한된다. | 검사 촬영 직전의 대기 시간이다. 작으면 흔들림/초점 미안정 상태의 촬영 위험이 있고, 크면 셀당 검사 시간이 증가한다. |
| Measure Z Settle Delay | `MeasureZSettleDelayMs` | Measure Z 이동 후 CA410 측정이 안정되는 시간을 ms로 입력한다. 음수는 0으로 제한된다. | CA410 측정 직전의 대기 시간이다. 작으면 측정 반복성 저하, 크면 CA410 공정 시간이 증가할 수 있다. |

공식 안전 관계는 `IdleZ <= CaptureZ <= MeasureZ`이다. 장비의 실제 좌표 방향에서 이 부등식이 안전 높이의 의미와 일치하는지, 티칭 전 제어 축의 방향 정의를 먼저 확인해야 한다.

## 4. 이벤트 분석

| 사용자 동작 | XAML/코드 흐름 | 결과 |
|---|---|---|
| 텍스트·숫자 입력 | TwoWay 바인딩으로 `ConfigViewModel` 속성 갱신 | 입력값이 설정 객체에 반영된다. Inspect X/Y text는 빈 문자열을 0으로, 소수 입력을 정수 um로 반올림해 처리한다. |
| Escape Y `Read Axis` | `AxisNumberBox`가 `InspectionUnit1Y` 또는 `InspectionUnit2Y`의 현재 위치를 읽음 | 현재 축 위치를 Escape Y 입력값으로 가져온다. 이동 명령이 아니므로 티칭 위치에서 눌러야 한다. |
| Idle/Capture/Measure Z `Read` | `ReadHeadZAsync` → 제어 연결 확인 → 상태 갱신 → Y1/Y2 Z 현재 위치 조회 | 선택한 Z 항목에 현재 축 좌표를 기록하고 Glass/Contact 상태를 로그에 남긴다. |
| 저장 | `SaveWithChangeReport` → `AlignCameraItems`를 `Config.AlignCameras`로 동기화 → 저장 | camera geometry 벡터를 정규화하고 Config를 영속화한다. 실제 장비 상태를 검증하거나 축을 이동시키는 저장 동작은 아니다. |

## 5. 데이터 바인딩

```text
ConfigWindow.xaml (Heads 탭)
  └─ TwoWay Binding
       └─ ConfigViewModel
            └─ Vars.EMRConfig (ULedConfig)
                 ├─ AlignY1CameraName / AlignY2CameraName / ContactCheckCameraName
                 ├─ AlignCameras : List<AlignCameraGeometryConfig>
                 ├─ HeadOffsets.Y1 / HeadOffsets.Y2
                 ├─ UnitEscapeYToleranceUm
                 ├─ CaptureZSettleDelayMs
                 └─ MeasureZSettleDelayMs
```

`AlignCameraItems`는 화면 편집용 항목 컬렉션이며 저장 때 `AlignCameras`로 다시 구성된다. Y1/Y2에 입력한 카메라 이름의 행이 없으면 저장 로직은 해당 이름의 geometry 행을 보장한다. **[추론]** 이 자동 행 생성 때문에 Camera Name을 빈 값 또는 오타로 저장하면 의도하지 않은 기본 geometry 행이 생길 수 있으므로, 저장 전 DataGrid 이름과 Head Mapping 이름을 대조해야 한다.

## 6. 사용자 입장에서

### 권장 설정 절차

1. 장비 연결 전, 카메라 프로그램의 실제 `UserDefinedName`을 확인하고 Y1=CAM1/Right, Y2=CAM2/Left, Contact=CAM3의 대응을 확인한다.
2. 각 Align 카메라의 pixel size와 `+StageX`, `+Y1` 영상 방향을 작은 단위의 실제 jog 이동으로 측정한다. 한 번에 큰 이동을 주지 않는다.
3. Glass 0deg 상태에서 Align 기준점을 맞춘 다음, 같은 기준점이 검사 카메라와 CA410 중심에 오도록 이동하여 Inspect X/Y와 CA410 Y를 티칭한다.
4. Y1과 Y2 각각에 대해 간섭 없는 Escape Y, Idle Z, Capture Z, Measure Z를 티칭한다. 이때 `IdleZ <= CaptureZ <= MeasureZ` 관계를 확인한다.
5. `Read`는 현재 위치 채우기 기능이므로, 축을 안전한 티칭 위치로 먼저 이동시킨 뒤 사용한다.
6. 저장 후 저속 단일 셀에서 Align → 검사 카메라 중심 → CA410 중심 → Escape 이동 순으로 검증한다. 양산 검사부터 실행하지 않는다.

### 변경 후 증상으로 찾는 항목

| 증상 | 우선 확인할 값 |
|---|---|
| Align 보정이 반대 방향 또는 대각선으로 움직임 | Pixel X/Y, +StageX 및 +Y1 방향 벡터, 카메라 이름 |
| Align은 맞지만 모든 검사 셀의 중심이 일정하게 벗어남 | 해당 헤드 Inspect X/Y |
| CA410만 목표점에서 벗어남 | 해당 헤드 CA410 Y, Inspect X(공통 사용) |
| 이동 중 안전 높이 오류 또는 헤드 간섭 위험 | Escape Y, Idle Z, Escape tolerance |
| 이미지가 흔들리거나 초점이 일정하지 않음 | Capture Z, Capture Z settle delay, 레시피 Capture Z override |
| CA410 값이 불안정함 | Measure Z, Measure Z settle delay |

## 7. 업무 로직 추론

다음은 공식 `main-glass-inspection-flow.md`와 좌표계 문서를 우선으로 정리하고, 화면 및 코드 연결만 `[추론]`으로 표시한 실행 흐름이다.

```text
Glass 좌표의 셀/측정 목표 결정
  → GlassToAxis 변환
  → Y1 또는 Y2의 Align 기준 도구 오프셋 차감
  → 대상 헤드의 이동 안전 높이 결정
      ├─ Escape Y 영역: Idle Z 확보 후 Y/XY 이동
      └─ 일반 검사 영역: Capture Z 확보 후 Y/XY 이동
  → 검사 카메라 직전: Capture Z 확인 → Capture settle 대기 → PG/입력 단계
  → CA410 직전: Measure Z 확인 → Measure settle 대기 → 측정
```

- 공식 기준에서 실제 검사 카메라 입력은 `StartStep` 또는 `Grab` 직전 훅에서 수행되고, PG 표시도 같은 시점에 동기화된다.
- **[추론]** `InspectCameraFromAlignUm`은 셀 이동의 검사 카메라 도구 오프셋으로, `Ca410FromAlignUm.Y`는 CA410 도구 오프셋으로 선택된다. 코드상 CA410 X에는 Inspect X를 함께 사용한다.
- **[추론]** Y1은 `InspectionUnit1Y/Z`, Y2는 `InspectionUnit2Y/Z`를 사용해 동일한 절차를 독립적으로 수행한다.
- **[추론]** 레시피에 Camera Capture Z override가 있으면 Config의 Capture Z를 바꿔도 그 레시피의 촬영 높이는 바뀌지 않는다. CA410 Measure Z와 Escape/Idle Z는 이 탭의 Config 값을 계속 기준으로 한다.

## 8. 문서작성 요약

- Heads 탭은 물리 헤드·카메라·도구 위치의 공통 장비 교정값을 설정한다.
- Inspect/CA410 offset은 Align 결과를 검사/측정 도구 중심으로 변환하는 핵심값이다.
- Escape Y와 세 Z 값은 단순 속도 설정이 아니라 충돌 회피, 카메라 촬영, CA410 측정의 안전 조건이다.
- Y1/Y2와 카메라 이름, camera geometry 행의 이름이 일관되어야 한다.
- Capture Z는 레시피가 override할 수 있으므로 Config 변경 후에는 적용 레시피의 ControlPlan도 함께 확인해야 한다.

## 9. 이해되지 않는 부분

| 확인 필요 항목 | 이유 |
|---|---|
| Y2 영상 방향을 +Y1 벡터에서 어떻게 mirror 변환하는지 | UI에는 Y2 전용 방향 벡터가 없고 공식 문서에 수식이 없다. 실제 Y2 Align jog 검증 또는 구현 단위 테스트가 필요하다. |
| CA410 X를 Inspect X와 공통으로 사용하는 것이 모든 장비에서 맞는지 | 현재 코드의 조합 방식은 확인됐지만, UI에는 독립 CA410 X 항목이 없다. 기구 중심이 다르면 별도 설계가 필요할 수 있다. |
| 저장 중인 Config가 이미 진행 중인 Glass Job에 적용되는 시점 | 실행 시작 시 설정을 snapshot하는지에 대한 공식 문서 확인이 필요하다. 설정 변경은 진행 중인 검사에서는 하지 않는 것을 원칙으로 한다. |
| `IdleZ <= CaptureZ <= MeasureZ`의 물리적 축 방향 | 공식 문서의 논리 관계는 확정되어 있으나, 실제 Z 양의 방향과 물리 높이는 장비 축 설정으로 검증해야 한다. |

## 10. 전체 프로젝트 연결

| 연결 대상 | Heads 탭과의 관계 |
|---|---|
| ConfigWindow > Motion / Coordinate | Glass→Axis affine 변환을 정의하고, Heads의 도구 오프셋이 그 변환 결과에 적용된다. |
| GlassSizeModel > 좌표계 보정 | Glass 기준 좌표와 Align 기준 pose를 제공한다. Heads는 그 기준에서 검사/CA410 도구까지의 상대 위치를 제공한다. |
| RecipeWindow > Align / 제어 | 레시피의 ControlPlan은 Y1/Y2 Camera Capture Z를 별도로 override할 수 있다. |
| RecipeWindow > 셀 목록 / 셀 맵 | 셀의 Glass 좌표·순회 대상이 Heads의 Inspect offset과 합쳐져 실제 검사 축 목표가 된다. |
| RecipeWindow > CA410 | CA410 측정 대상은 CA410 Y offset, Measure Z, Measure settle delay를 사용한다. |
| Contact Check | CAM3 이름은 Contact Check 전용 카메라 연결 기준이며, 검사 헤드의 CAM1/CAM2와 분리되어 관리된다. |
| Main glass inspection flow | 실제 이동·PG·촬영/입력·비동기 검사 결과 수신 순서에서 Heads 값은 이동 및 촬영/측정 전제 조건을 제공한다. |

### 참조 근거

- 공식 문서: `docs/main-glass-inspection-flow.md`, `docs/stage-glass-coordinate-system.md`, `docs/glass-axis-affine-transform-design.md`, `docs/axis-system-structure.md`
- UI: `uLedAoiConsole/Windows/Core/ConfigWindow.xaml` (`Heads` 탭)
- ViewModel: `uLedAoiConsole/ViewModels/ConfigViewModel.cs`
- 설정 모델: `uLedAoiConsole/Models/ULedSettings.cs`
- 실행 연결 확인: `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`, `uLedAoiConsole/Recipes/RecipeService.cs`
