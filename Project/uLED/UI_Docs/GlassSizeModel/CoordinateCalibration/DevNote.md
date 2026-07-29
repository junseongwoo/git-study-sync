# GlassSizeWindow - 좌표계 보정 탭 개발 노트

## 모델 계약

```text
GlassSizeModel
├─ GlassToMotorCalibration
│  ├─ StageXPerGlassX
│  ├─ UnitY1PerGlassX
│  ├─ StageXPerGlassY
│  └─ UnitY1PerGlassY
├─ AlignStageSharedPose.StageX
├─ AlignBridgeReferencePose.LeftAlignUnitY
├─ AlignBridgeReferencePose.RightAlignUnitY
├─ LeftAlignCameraCalibration.Points   // 자동 생성 P1~P3
└─ RightAlignCameraCalibration.Points  // 자동 생성 R1~R3
```

## 자동 생성 로직

`GlassSizeItemViewModel.ApplyToModel()`은 먼저 `RebuildDerivedCalibrationPoints()`를 호출한다.

```text
P1 = (LeftAlignX, LeftAlignY)  → (Left Y2, StageX)
R1 = (RightAlignX, RightAlignY) → (Right Y1, StageX)

P2/R2 = P1/R1 + GlassX 1000µm delta
P3/R3 = P1/R1 + GlassY 1000µm delta
```

left의 UnitY delta에는 `-1`, right의 UnitY delta에는 `+1` mirror sign이 적용된다. 산출 delta는 matrix determinant가 0에 가까우면 생성 중 예외가 난다.

## Default preset

`ApplyDefaultGlassToMotorMatrix()`은 `ResolveDefaultGlassToMotorMatrix(PanelAngleDeg)`를 호출한다.

```text
glass basis를 -PanelAngle 회전
StageX 계수 = 회전된 glass X 성분의 음수
UnitY1 계수 = 회전된 glass Y 성분
```

공식 기록상 화면 기준 CW PanelAngle로 0/90/180/270 preset을 만들며, 270도 Y2 방향 검증이 추가돼 있다. matrix를 수동 수정한 뒤에도 저장 시 파생 3점이 재생성되므로, 내부 3점만 따로 보정하는 설계는 현재 UI 계약에 맞지 않는다.

## 현재 축값 읽기

`ReadCurrentAxesAsync()`은 다음 protocol axis만 읽는다.

|UI|Protocol axis|
|---|---|
|StageX|`StageX`|
|Left Y2|`InspectionUnit2Y`|
|Right Y1|`InspectionUnit1Y`|

`EnsureConnectedAsync` 후 `RefreshStatusAsync`로 상태를 읽는다. motion command는 전송하지 않는다. `AxisNumberBox`의 개별 read도 `AxisPositionReader.ReadAsync`를 사용하고 `UpdateSource()`로 LostFocus binding을 즉시 반영한다.

## 유효성

`GlassSizeStore`는 다음을 검사한다.

- Glass→Motor matrix 존재
- determinant 절대값이 `0.0000001` 이상
- left/right calibration points 각각 정확히 3개
- 각 point의 Glass 좌표와 필요한 axis 값 존재

좌표계 보정 UI가 3점 grid를 제거했어도 3점 구조가 사라진 것이 아니다. matrix/pose에서 자동 생성된 3점을 runtime affine solver의 입력으로 유지한다.

## 변경 시 금지·주의

- PanelAngle setter만으로 matrix를 자동 재계산하지 않는다. 사용자가 기본 preset 또는 승인 matrix를 명시적으로 적용해야 한다.
- General의 AlignMark, matrix, Reference Pose는 함께 일관되어야 한다. 어느 하나만 변경한 모델을 실장비 motion 기준으로 사용하지 않는다.
- reference pose에 U/V/W를 다시 추가하지 않는다. 공식 변경 기록상 모델 standard pose에서 의미 없는 UVW는 제거되었고, 기존 JSON의 UVW도 로드 시 무시된다.
- matrix가 불명확할 때 0 또는 이전 모델의 값으로 fallback하지 않는다. 장비 calibration 근거가 없으면 저장/실행 전에 확인이 필요하다.

## 검증

|검증|예상 결과|
|---|---|
|0/90/180/270 default preset|각 각도에서 matrix·P2/P3/R2/R3 delta가 공식 방향과 일치|
|singular matrix|Save validation 거부|
|현재값 읽기|3개 protocol axis만 해당 pose 필드에 반영, motion 없음|
|align mark 변경 후 Save|P1/R1 glass point와 파생점이 새 mark 기준으로 재생성|
|pose 변경 후 Save|해당 side의 3점 절대 축값이 같이 이동|
|matrix 변경 후 cell target 계산|StageX/Y1/Y2와 Cell List target이 예상대로 변함|
|PanelAngle 변경만 수행|matrix 자동 변경 없음 확인 및 운영 절차 경고|

## 관련 파일

- `uLedAoiConsole/Windows/Recipe/GlassSizeWindow.xaml`
- `uLedAoiConsole/ViewModels/GlassSizeViewModel.cs`
- `uLedAoiConsole/Controls/AxisNumberBox.cs`
- `uLedAoiConsole/Stores/GlassSizeStore.cs`
- `docs/glass-axis-affine-transform-design.md`
- `docs/stage-glass-coordinate-system.md`
