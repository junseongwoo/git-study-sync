# RecipeWindow 도구 메뉴 인수인계 개발 노트

작성일: 2026-08-03

## 1. 직접 확인한 구현

- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml`
- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml.cs`
- `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`
- `uLedAoiConsole/Windows/Recipe/AlignWindow.xaml.cs`
- `uLedAoiConsole/Services/EecP725R2/*`
- `uLedAoiConsole/Protocols/Ca410/*`
- `uLedAoiConsole/Models/ULedSettings.cs`

공식 문서:

- `docs/전체 flow.md`
- `docs/main-glass-inspection-flow.md`
- `docs/ca410-inspection-flow.md`
- `docs/glass-axis-affine-transform-design.md`
- `docs/alarm-policy.md`
- `docs/development/change-log.md`

## 2. 메뉴 연결표

| Header | Handler/Command | 구현 메서드 |
|---|---|---|
| Align Flow 실행 | Code-behind Click | `RunManualAlignFlow_Click` |
| 축 위치 읽기 | AsyncRelayCommand | `ReadControlAxisStatusAsync` |
| 선택 IP를 셀로 이동 | AsyncRelayCommand | `MoveSelectedIpToSelectedCellAsync` |
| 패턴 점등 | AsyncRelayCommand | `TurnSelectedPatternOnAsync` → `TurnOnSelectedPatternAsync` |
| 패턴 소등 | AsyncRelayCommand | `TurnPatternOffAsync` → `TurnPatternOffCoreAsync` |
| 전체 PG 패턴 점등 | AsyncRelayCommand | `TurnAllUsedPgOnAsync` |
| 전체 PG 패턴 소등 | AsyncRelayCommand | `TurnAllUsedPgOffAsync` |
| 컨택 On | AsyncRelayCommand | `ContactOnAsync` |
| 컨택 Off | AsyncRelayCommand | `ContactOffAsync` → `ContactOffCoreAsync` |
| CA410 이동 | AsyncRelayCommand | `MoveCa410ToSelectedCellAsync` |
| CA410 측정 | AsyncRelayCommand | `MeasureCa410Async` |
| CA410 영점 보정 | AsyncRelayCommand | `CalibrateCa410Async` |

모든 메뉴는 구현되어 있다.

## 3. Align Flow 책임 경계

Code-behind가 다음 두 객체를 조율한다.

```text
RecipeEditorViewModel
  -> MoveAlignReferencePositionOrThrowAsync

AlignWindow
  -> StartLiveModeAsync
       LeftCamera.Connect
       RightCamera.Connect
       Left/Right StartLive
```

Auto Align 알고리즘을 호출하지 않는다. 기능명 또는 향후 refactor에서 이 경계를 유지해야 한다.

`MoveAlignReferencePositionOrThrowAsync`는 ControlPlan의 nullable pose 중 값이 있는 축만 보낸다. `moves.Count == 0`일 때만 실패한다. 공식적으로 완전한 6축 pose를 강제하려면 validation을 별도로 추가해야 한다.

## 4. Motion target 계산

### 검사 카메라 셀 이동

```text
GetCellCenterGlass
  -> TryBuildBridgeCalibration(GlassSize)
  -> ResolveCellMoveToolOffset(index=0)
       ResolveInspectCameraOffset
  -> CoordinateTransformService.ResolveToolAxisTarget
  -> ApplyCellMapCorrection
       UnitY += correction(YIndex)
       StageX += correction(XIndex)
  -> target bridge + opposite EscapeY
```

### CA410 이동

```text
GetCellCenterGlass
  -> selected cell IpNo로 bridge 선택
  -> ResolveCa410Offset
       X = InspectCameraFromAlign.X
       Y = Ca410FromAlign.Y
  -> affine target
  -> target bridge + opposite EscapeY
```

CA410의 합성 offset은 최신 변경 기록과 현재 코드가 일치한다. 일반 설계 문서의 `Ca410OffsetFromAlign(dx,dy)` 예시는 개념 설명이고 현재 장비 적용 정본은 Inspect X + CA410 Y 합성이다.

### CellMap 보정 불일치

- `MoveSelectedIpToSelectedCellAsync` → `TryResolveCellMotionTarget` → `ApplyCellMapCorrection` 적용
- `MoveCa410ToSelectedCellAsync` → `TryResolveBridgeMoveTarget` 직접 호출 → CellMap 보정 미적용
- 자동 검사/CA410 → `GlassInspectionStepPreparationService.ApplyCellMapCorrection` 적용

공식 문서는 자동 검사와 CA410 촬상 좌표에 보정을 적용한다고 정의한다. 수동 CA410 이동까지 동일 기준으로 만들지는 사용자 결정이 필요하지만, 현재 수동/자동 위치가 달라질 수 있다는 사실은 유지보수 시 반드시 고려해야 한다.

## 5. Contact 이동 보호

상수:

```text
ContactStageXToleranceUm = 10.0
```

Contact On 성공 시 다음 로컬 상태를 저장한다.

- `IsContactActive = true`
- `_contactedRowIndex = SelectedCell.YIndex`
- `_contactedStageX = 선택 셀의 검사 카메라 target.StageX`

셀/CA410/Align 카메라 이동에서 `ConfirmAndReleaseForRowChangeAsync`를 호출한다.

- 같은 StageX: StageX move 생략, `ContactSafeStep`
- 다른 StageX: 확인 → Pattern OFF → Release → General move

### 위험

`IsControlContacted`는 runtime 표시용이고, 이동 보호 조건은 로컬 `IsContactActive`다. 외부 또는 다른 창에서 Contact가 켜진 경우 `_contactedStageX`가 없어 자동 Release 보호가 적용되지 않는다.

개선 시 실제 runtime Contact 상태와 contact target StageX 소유권을 단일화해야 한다. 임의 fallback으로 현재 선택 셀 StageX를 추정하지 않는다.

## 6. PG 제어 비교

| 경로 | endpoint 선택 | SelectPattern | SetPatternVoltages | 확인 |
|---|---|---:|---:|---:|
| 개별 ON | SelectedCell YIndex mapping | O | O | X |
| 개별 OFF | SelectedCell YIndex mapping | - | - | X |
| 전체 ON | Cells의 distinct mapped PG | O | X | O |
| 전체 OFF | Cells의 distinct mapped PG | - | - | O |

### 확인된 비대칭

1. 개별 ON은 Pattern 선택 후 `BuildInspectionPatternVoltages`를 적용한다.
2. 전체 ON은 Pattern만 선택한다.
3. `ResolveUsedPgRuntimes`는 메서드 이름과 달리 `Cells.Where(x => x.YIndex >= 0)`이며 `x.Use` 조건이 없다.
4. 개별 ON CanExecute는 SelectedPattern만 본다. SelectedCell 누락은 실행 단계에서 오류가 된다.
5. 개별 OFF/전체 OFF는 CanExecute가 없어 항상 활성이다.

이 차이를 수정할 때는 공식 요구를 먼저 확정해야 한다. 전체 ON에 전압 적용을 추가하면 실제 모든 PG의 전압 상태가 바뀌는 동작 변경이다.

## 7. Contact On/Off 세부

### Contact On

- SelectedCell 검사
- local active 검사
- `ControlPlan.ContactX` 검사
- ContactorX abs move + 도착 검증
- `FlowContact`, parameter `od_um`
- ContactorX 재검증
- local lock state 기록

선택 셀의 StageX/Y축으로 이동하지 않는다. 작업자가 먼저 이동했다는 전제를 코드가 검증하지 않는다.

### Contact Off

- `TurnPatternOffCoreAsync`
- `FlowRelease`
- local state clear

`TurnPatternOffCoreAsync`가 자체 catch로 오류를 흡수하므로 Release는 계속한다. Release 성공 뒤 `StatusMessage`가 “Pattern OFF + Release”가 되면 앞의 PG OFF 실패 문구가 덮일 수 있다.

## 8. CA410 세 경로의 차이

| 메뉴 | 대상 선택 | Motion | PG | CA410 통신 | 저장 |
|---|---|---|---|---|---|
| CA410 이동 | SelectedCell.IpNo | XY만 | X | X | X |
| CA410 측정 | SelectedIp | MeasureZ | X | MES 1회 | summary/log만 |
| ZRC | SelectedIp | X | X | COM,1 옵션 + ZRC | 장비 calibration 상태 |

자동 CA410 flow는 위 세 메뉴를 단순 연결한 것이 아니다. `Ca410Plan.Patterns/Steps`, PG pattern 유지, voltage sweep, ELVDD, 결과 artifact를 포함하는 별도 실행 경로다.

### Simulation

- `Ca410Config.ToMeasurementOptions`가 `UseSimulator = Vars.IsCa410SimulationMode`를 설정한다.
- 단발 측정의 `Ca410MeasurementClient`는 이 옵션으로 simulator client를 만든다.
- ZRC의 직접 client 연결도 동일 전역 토글을 확인한다.
- CA410 XY/Z motion은 ControlRuntime이므로 CA410 Simulation만으로는 대체되지 않는다.

## 9. Axis status 조회

`ReadControlAxisStatusAsync`는 `RefreshStatusAsync` 결과를 format한다. `FormatAxisStatus`는 position만 표시하며 servo/ready/alarm 상세는 보여주지 않는다.

이 명령을 teach 기능으로 바꾸지 않는다. Recipe pose write-back은 `ApplyCurrentPositionToAlignCommand`, `ApplyCurrentPositionToContactCommand` 등 별도 명령이 소유한다.

## 10. 개선 후보와 우선순위

### 높은 우선순위

1. Contact 보호의 local/runtime 상태 불일치
2. Contact On 전 선택 셀 StageX/UnitY 도착 검증 부재
3. Contact Off에서 PG OFF 실패 상태가 Release 완료 문구로 덮이는 문제
4. 수동 CA410 이동과 자동 CA410 이동의 CellMap 보정 차이

### 중간 우선순위

1. 전체 PG ON의 전압 미적용 여부 공식화
2. `ResolveUsedPgRuntimes`의 Cell.Use 필터 여부 공식화
3. Pattern ON/OFF CanExecute 조건 정합
4. CA410 측정 전에 SelectedCell/SelectedIp/현재 XY를 확인하는 UX

### 문구 개선

1. `Align Flow 실행`의 실제 범위 표시
2. `축 위치 읽기`가 Recipe 저장이 아님을 ToolTip에 표시
3. CA410 측정이 자동 plan 실행이 아닌 단발 측정임을 표시

## 11. 변경 시 금지 사항

- GlassSize calibration이 없을 때 과거 cell StageX/Y 값을 fallback으로 사용하지 않는다.
- Contact target StageX가 없을 때 현재 선택 셀 값으로 자동 추정하지 않는다.
- Control Simulation이 Align camera 또는 CA410 계측까지 성공시킨다고 가정하지 않는다.
- CA410 조건을 IP `PatternPlanModel.UseCa410`로 되돌리지 않는다.
- Export/자동 검사 결과 저장을 수동 단발 CA410 메뉴에 암묵적으로 추가하지 않는다.
- Main 공식 `StartJob/InputStep/EndJob` flow를 수동 도구 로직과 섞지 않는다.

## 12. 테스트 체크리스트

### Align/축

- [ ] Align pose 6축 이동 request 확인
- [ ] pose 전체 미설정 시 실패 확인
- [ ] 양쪽 camera connect/live 확인
- [ ] 축 조회가 Recipe 값을 변경하지 않는지 확인

### Cell motion

- [ ] Cell IpNo와 SelectedIp 불일치 시 메뉴 비활성 확인
- [ ] IP1/IP2 target/escape 축 확인
- [ ] XIndex/YIndex CellMap correction 반영 확인
- [ ] Contact 같은 StageX에서 StageX move 생략 확인
- [ ] 다른 StageX에서 OFF/Release 후 이동 확인

### PG

- [ ] 개별 ON의 Pattern + R/G/B 전압 packet 확인
- [ ] 개별 OFF 대상 endpoint 확인
- [ ] 전체 ON의 대상과 현재 전압 유지 여부 확인
- [ ] 일부 PG 실패 후 나머지 계속 실행 확인
- [ ] Unuse-only YIndex가 대상에 포함되는 현재 동작 확인

### Contact

- [ ] ContactX move/도착 확인
- [ ] FlowContact `od_um` 확인
- [ ] 외부 Contact 상태에서 이동 보호 확인
- [ ] Pattern OFF 실패 후 Release 및 최종 메시지 확인

### CA410

- [ ] Cell IpNo 기준 좌우 CA410 XY 이동 확인
- [ ] CellMap 보정이 있는 Recipe에서 수동/자동 CA410 target 차이 확인
- [ ] 반대 unit EscapeY 확인
- [ ] SelectedIp 기준 MeasureZ/장비 선택 확인
- [ ] MeasureZ settle/recheck 확인
- [ ] 단발 측정이 PG/CSV를 건드리지 않는지 확인
- [ ] 실제/Simulation ZRC 확인

## 13. 2차 검증 결론

도구 메뉴의 모든 항목은 구현되어 있으며, 공식 좌표·CA410·Simulation 기준과 대부분 일치한다. 인수인계 시 특히 다음을 혼동하지 않아야 한다.

1. Align Flow는 자동 Align이 아니라 위치+Live 준비다.
2. 개별 PG ON과 전체 PG ON의 전압 적용 범위가 다르다.
3. Contact 이동 보호는 runtime 실제 상태가 아니라 현재 Window의 local state에 의존한다.
4. CA410 이동·측정·ZRC는 서로 독립된 수동 기능이다.
5. 수동 CA410 측정은 자동 `Ca410Plan` 실행이나 결과 export가 아니다.

이번 작업은 분석 문서만 작성했으며 소스 코드는 수정하지 않았다.
