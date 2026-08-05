# RecipeWindow 도구 메뉴 개발자 분석

작성일: 2026-08-03  
분석 대상: `RecipeWindow > 도구`

## 1. 핵심 결론

`도구` 메뉴는 Recipe 데이터를 편집하는 메뉴가 아니라 현재 Recipe와 선택 상태를 사용해 **Control 축, Align 카메라, PG, Contact, CA410를 직접 시험 운전하는 수동 조작 메뉴**다.

메뉴의 12개 항목은 모두 이벤트 또는 `AsyncRelayCommand`에 연결되어 있어 미구현 항목은 없다. 다만 메뉴 이름만 보고 자동 검사 전체 flow로 오해하면 안 되는 항목이 있다.

- `Align Flow 실행`: 자동 Align 완료가 아니라 기준 pose 이동 → AlignWindow 열기 → 양쪽 카메라 Live 시작까지 수행한다.
- `축 위치 읽기`: 축 상태를 상태 문구와 로그에 표시할 뿐 Recipe 위치값에 저장하지 않는다.
- `CA410 측정`: XY 이동이나 PG 점등 없이 현재 위치에서 Z를 측정 높이로 맞춘 뒤 단발 측정한다.
- `CA410 영점 보정`: ZRC 명령만 실행하며 광학 조건이나 안전 위치를 프로그램이 확인하지 않는다.
- 개별 PG 점등과 전체 PG 점등은 동작이 다르다. 개별 점등은 Pattern 선택과 R/G/B 전압 적용을 함께 하지만, 전체 점등은 현재 코드에서 Pattern 선택만 수행한다.

```text
RecipeWindow 도구 메뉴
  ├─ Align 준비: 기준 위치 이동 + AlignWindow Live
  ├─ Motion 진단: 축 상태 읽기, 선택 셀 이동
  ├─ PG 수동 제어: 개별/전체 Pattern ON/OFF
  ├─ Contact 수동 제어: Contact/Release
  └─ CA410 수동 제어: XY 이동, 단발 측정, ZRC
```

## 2. 분석 기준과 사실 우선순위

### 2.1 적용한 공식 문서

1. `docs/프로젝트 구조.md`
2. `docs/전체 flow.md`
3. `docs/main-glass-inspection-flow.md`
4. `docs/ca410-inspection-flow.md`
5. `docs/glass-axis-affine-transform-design.md`
6. `docs/alarm-policy.md`
7. `docs/development/change-log.md`

공식 문서 기준으로 Console은 Align, Motion, PG, Contact, CA410를 포함한 전체 flow를 오케스트레이션한다. CA410 조건은 IP Pattern 속성이 아니라 Console Recipe의 `Ca410Plan`이 소유하며, Glass 좌표에서 축 좌표로의 이동은 GlassSize calibration과 head offset을 사용한다.

`dist-lib/docs/README.md`는 저장소 지침상 우선 확인 대상이지만 현재 checkout의 `dist-lib`가 비어 있어 읽을 수 없었다.

### 2.2 최신 문서 해석

과거 변경 기록에는 CA410/Align 이동 시 사용하지 않는 반대 UnitY를 `0`으로 보낸다고 적혀 있다. 최신 Main flow 문서는 작업 대상이 없는 unit을 Config의 `EscapeYUm`으로 이동하도록 정의하고, 현재 Recipe 코드도 `ResolveEscapeY(...)`를 사용한다. 따라서 본 분석은 **Config EscapeY가 현재 기준**이라고 해석한다.

## 3. XAML 메뉴와 구현 상태

| 메뉴 | 연결 | 구현 | 핵심 결과 |
|---|---|---:|---|
| Align Flow 실행 | `RunManualAlignFlow_Click` | 구현 | Align pose 이동 후 AlignWindow 양쪽 Live 시작 |
| 축 위치 읽기 | `ReadControlAxisStatusCommand` | 구현 | Control process/축 위치를 상태와 로그에 표시 |
| 선택 IP를 셀로 이동 | `MoveSelectedIpToSelectedCellCommand` | 구현 | 선택 셀의 검사 카메라 위치로 StageX/Y1/Y2 이동 |
| 패턴 점등 | `TurnPatternOnCommand` | 구현 | 선택 셀 PG에 Pattern 선택 + 검사 전압 적용 |
| 패턴 소등 | `TurnPatternOffCommand` | 구현 | 선택 셀 PG OFF |
| 전체 PG 패턴 점등 | `TurnAllUsedPgOnCommand` | 구현 | Recipe가 참조하는 PG들에 Pattern 선택 |
| 전체 PG 패턴 소등 | `TurnAllUsedPgOffCommand` | 구현 | Recipe가 참조하는 PG들 OFF |
| 컨택 On | `ContactOnCommand` | 구현 | ContactorX 이동 후 `FlowContact` |
| 컨택 Off | `ContactOffCommand` | 구현 | 선택 셀 PG OFF 시도 후 `FlowRelease` |
| CA410 이동 | `MoveCa410ToSelectedCellCommand` | 구현 | 선택 셀 중심의 CA410 XY 위치로 이동 |
| CA410 측정 | `MeasureCa410Command` | 구현 | 선택 IP 장비의 Z 이동·정착 후 단발 측정 |
| CA410 영점 보정 (ZRC) | `CalibrateCa410Command` | 구현 | 선택 IP 장비에 ZRC 전송 |

## 4. 공통 상태와 의존 관계

| 상태/설정 | 사용 기능 | 의미 |
|---|---|---|
| `SelectedCell` | 셀 이동, 개별 PG, Contact, CA410 이동 | 대상 셀과 YIndex/IP 배정을 제공 |
| `SelectedIp` | 셀 이동 검증, CA410 측정·ZRC | UI에서 선택한 IP/장비 번호 |
| `SelectedPattern` | Pattern ON, 전체 PG ON | `PgPatternIndex`와 검사 전압 조건 제공 |
| `ControlPlan` | Align Flow, Contact | Align reference pose, ContactX, OD 제공 |
| `PgMappings` | 개별/전체 PG | Cell YIndex → PG endpoint index 해석 |
| GlassSize calibration | 셀/CA410 이동 | Glass 중심 좌표 → StageX/UnitY affine 변환 |
| Head offsets | 검사 카메라/CA410 이동 | Align camera 기준 tool offset |
| CellMap correction | 선택 IP 셀 이동 | XIndex/YIndex별 StageX/UnitY 보정 |
| Config EscapeY | 셀/CA410 이동 | 사용하지 않는 반대 inspection unit 대피 위치 |
| Control/PG/CA410 Simulation | 해당 장비 수동 조작 | 세 Simulation은 서로 독립 |

수동 메뉴는 자동 검사 실행 여부와 별개로 직접 장비 명령을 보낸다. 실행 전에 Main의 Simulation 배지, Control 접속, PG endpoint, CA410 장비 번호와 실제 장비 주변 안전 상태를 확인해야 한다.

## 5. Align Flow 실행

### 5.1 코드 진행

```text
메뉴 선택
  -> “Align 위치로 이동하고 Align 창을 Live mode로 전환” 확인
  -> MoveAlignReferencePositionOrThrowAsync()
       ControlPlan에서 값이 있는 축만 move 목록에 추가
       StageX
       InspectionUnit2Y = Align2/Left UnitY
       InspectionUnit1Y = Align1/Right UnitY
       StageU / StageV / StageW
       -> Control Move(General)
  -> 기존 AlignWindow 활성화 또는 새 창 생성
  -> Left/Right Align camera Connect
  -> 양쪽 StartLive 동시 실행
  -> AlignWindow Activate
```

Recipe의 reference pose는 GlassSize 값을 자동 fallback하지 않는다. GlassSize 값을 사용하려면 Align/제어 탭에서 Recipe로 명시적으로 가져와야 한다.

### 5.2 실제 영향

- 실제 Control 6축 중 값이 설정된 축을 이동시킨다.
- 양쪽 Align 카메라 연결과 Live를 시작한다.
- AlignWindow가 열려 있으면 중복 창을 만들지 않는다.
- 실패 시 RecipeWindow 상태 문구와 `ManualAlign` 로그를 남긴다.

### 5.3 하지 않는 일

이 메뉴는 다음 작업을 수행하지 않는다.

- Template matching
- X/Y/θ 오차 계산
- UVW/XY 반복 보정
- Align 성공 판정
- Recipe 저장

따라서 이름은 `Align Flow 실행`이지만 실제 역할은 **수동 Align을 시작하기 위한 위치·Live 준비**다.

`[추론]` reference pose의 일부 축만 입력돼 있어도 해당 축만 이동하고 계속 진행하므로, 현장에서는 6축 pose가 모두 올바른지 별도로 확인하는 것이 안전하다.

## 6. 축 위치 읽기

### 6.1 읽는 상태

ControlRuntime 연결을 확인하고 최신 status를 요청한 뒤 다음을 한 문자열로 표시한다.

- `GlassPresent`, `Contacted`
- `StageX`, `StageU`, `StageV`, `StageW`
- `InspectionUnit1Y`, `InspectionUnit2Y`
- `ContactorX`, `ContactorZ`
- `InspectionUnit1Z`, `InspectionUnit2Z`
- `InspectionCamera1Z`, `InspectionCamera2Z`

축 위치는 소수점 셋째 자리까지 출력하고 status에 없는 축은 `N/A`로 표시한다.

### 6.2 영향

이 명령은 읽기 전용이다. 결과를 `StatusMessage`와 `ControlAxisStatus` 로그에 기록하며 다음 값은 변경하지 않는다.

- Recipe의 Align/Contact pose
- 셀의 StageX/Y1/Y2
- 화면의 `CurrentX1/CurrentX2/CurrentY`

현재 축값을 Recipe Align 또는 Contact 위치에 저장하려면 각 탭의 별도 `현재값 읽기` 기능을 사용해야 한다.

## 7. 선택 IP를 셀로 이동

### 7.1 실행 가능 조건

버튼이 활성화되려면 다음 조건을 모두 만족해야 한다.

- Cell이 선택됨
- Cell의 `IpNo`가 1 또는 2
- Cell의 `IpNo`와 화면 `SelectedIp`가 동일

### 7.2 목표 좌표 계산

```text
Cell center in GlassCS
  X = CellRect.X + Width / 2
  Y = CellRect.Y - Height / 2

GlassSize affine calibration
  -> 선택 IP의 left/right bridge transform
  -> InspectCameraFromAlign tool offset
  -> CellMap correction
       StageX += XIndex 보정
       UnitY  += YIndex 보정
  -> 대상 bridge UnitY
  -> 반대 bridge EscapeY
```

IP1과 IP2의 좌우 bridge 선택은 `IpNo`로 결정된다. 메뉴는 항상 검사 카메라 tool index `0`을 사용하므로 CA410나 Align 카메라 위치가 아니라 검사 카메라 중심이 셀 중심을 보도록 계산한다.

### 7.3 Contact 중 이동 보호

이 ViewModel에서 Contact On을 수행한 상태라면 Contact 당시 목표 StageX를 저장한다.

- 목표 StageX 차이 `< 10 µm`: 같은 StageX로 간주하고 StageX를 움직이지 않는다. `ContactSafeStep`으로 UnitY만 이동한다.
- 차이 `>= 10 µm`: 사용자 확인 후 Pattern OFF와 Release를 수행한 다음 일반 이동한다.

Control move에는 Z 안전 profile도 전달되어 평면 이동 전에 필요한 idle Z 처리가 적용된다.

`[추론] (코드 확인)` 이 보호는 로컬 `IsContactActive`를 기준으로 한다. 다른 창이나 외부 장비 조작으로 이미 Contact된 상태는 `IsControlContacted` 표시에는 반영되지만 로컬 StageX lock 정보가 없을 수 있다.

## 8. 패턴 점등

### 8.1 대상 PG 선택

선택 Cell의 `YIndex`를 Recipe `PgMappings`로 해석하여 PG index를 구하고 해당 endpoint runtime을 사용한다.

### 8.2 실행 순서

```text
SelectedPattern 확인
  -> PgPatternIndex > 0 확인
  -> SelectedCell의 YIndex -> PgIndex
  -> PG 새 연결
  -> SelectPattern(PgPatternIndex)
  -> SetPatternVoltages(R/G/B 검사 전압)
  -> Config PatternOnDelayMs 대기, 기본 100 ms
  -> 화면 점등색/상태 갱신
```

R/G/B 전압은 `PgVoltagePlan`에서 선택 Pattern에 대응하는 `ConsoleInspectionPatternVoltage`를 사용한다. 화면 색은 Black/White 표시 전압 범위와 실제 채널 전압으로 계산한 참고색이다.

### 8.3 현재 UI 주의점

- Pattern 선택 확인 대화상자는 코드에서 주석 처리돼 있어 즉시 전송한다.
- `CanExecute`는 Pattern 선택만 검사한다. Cell이 없어도 메뉴가 활성화될 수 있으며 실행 시 “PG 제어 대상 셀이 선택되지 않았습니다” 오류가 상태에 표시된다.
- `PgPatternIndex <= 0`이면 실행하지 않는다.

## 9. 패턴 소등

선택 Cell의 YIndex로 해석한 **한 PG endpoint**에 `TurnOff`를 전송한다.

- 확인 대화상자는 주석 처리돼 있어 즉시 실행한다.
- 메뉴는 항상 활성화되어 있으나 Cell 또는 PG mapping/runtime이 없으면 실패한다.
- 성공 시 점등 표시를 회색과 `OFF`로 변경한다.
- 다른 PG endpoint는 꺼지지 않는다.

## 10. 전체 PG 패턴 점등

### 10.1 대상 수집

화면의 모든 Cell에서 `YIndex >= 0`을 수집하고, 각 YIndex를 PgMapping으로 변환해 중복 PG index를 제거한다. Config의 endpoint 범위를 벗어난 mapping이 하나라도 있으면 시작하지 않는다.

### 10.2 실행

1. 선택 Pattern과 `PgPatternIndex > 0`을 확인한다.
2. 대상 PG 목록과 endpoint를 확인 대화상자에 표시한다.
3. 각 PG에 순차적으로 `SelectPattern(PgPatternIndex)`를 전송한다.
4. 성공한 PG가 하나 이상이면 `PatternOnDelayMs`를 한 번 대기한다.
5. 성공/실패 개수와 endpoint별 오류를 표시한다.

### 10.3 개별 점등과 차이

현재 전체 점등 코드는 `SetPatternVoltages`를 호출하지 않는다. 따라서 다음 차이가 있다.

| 기능 | Pattern Select | R/G/B 검사 전압 적용 |
|---|---:|---:|
| 패턴 점등 | O | O |
| 전체 PG 패턴 점등 | O | X |

`[추론] (코드 확인)` 명칭은 `TurnAllUsedPg...`이지만 대상 수집 시 `Cell.Use`를 검사하지 않는다. Unuse Cell에만 존재하는 YIndex의 PG도 대상에 포함될 수 있다.

## 11. 전체 PG 패턴 소등

전체 점등과 같은 방식으로 Recipe Cell들이 참조하는 PG endpoint를 수집한 뒤 각 PG에 `TurnOff`를 순차 전송한다.

- 실행 전 대상 PG 목록을 확인한다.
- 일부 PG 실패가 나도 나머지 PG의 OFF를 계속 시도한다.
- 최종 상태에 성공/실패 개수와 상세 오류를 표시한다.
- 현재 대상 계산은 `Cell.Use`를 필터링하지 않는다.

## 12. 컨택 On

### 12.1 선행 조건

- 선택 Cell 필요
- 이 ViewModel의 `IsContactActive=false`
- `Document.ControlPlan.ContactX` 설정 필요
- ControlRuntime 연결 필요

### 12.2 실행 순서

```text
사용자 확인
  -> ContactorX를 Recipe ContactX로 절대 이동
  -> 축 도착 확인
  -> FlowContact(od_um = ContactOdUm)
  -> ContactX 위치 재확인
  -> local IsContactActive = true
  -> 선택 Cell의 YIndex와 계산 StageX를 contact lock 정보로 저장
```

Contact On은 선택 Cell의 StageX/Y1/Y2로 이동하지 않는다. 선택 Cell은 Contact 상태의 row/StageX 기준을 기록하는 데 사용된다.

`[추론]` 따라서 실제 운영 순서는 `선택 셀로 이동 -> 위치 확인 -> Contact On`이어야 한다. 셀 이동을 먼저 하지 않아도 코드가 Contact를 막지 않으므로 현재 축 위치를 작업자가 확인해야 한다.

## 13. 컨택 Off

```text
사용자 확인
  -> 선택 Cell의 PG Pattern OFF 시도
  -> FlowRelease
  -> 성공 시 local contact row/StageX 상태 초기화
```

Pattern OFF 내부 오류는 상태와 로그에 기록되지만 예외를 다시 던지지 않으므로 Release는 계속 시도된다. 즉 PG OFF가 실패해도 Contact Off가 완료로 표시될 가능성이 있다.

`[추론]` Contact Off 후에는 PG 상태와 Control의 실제 `Contacted` 표시를 함께 확인해야 한다.

## 14. CA410 이동

### 14.1 대상과 계산

선택 Cell의 `IpNo`가 1 또는 2이면 활성화된다. 이 기능은 화면 `SelectedIp`와 Cell IpNo 일치까지 요구하지 않으며 **Cell에 배정된 IP/bridge**를 사용한다.

```text
선택 Cell 중심 Glass 좌표
  -> GlassSize left/right affine transform
  -> CA410 tool offset
       StageX 방향 = InspectCameraFromAlign.X 공통 offset
       UnitY 방향  = Ca410FromAlign.Y 전용 offset
  -> 대상 bridge UnitY
  -> 반대 bridge Config EscapeY
```

최신 변경 기록은 Recipe, Main 검사, Console API가 위 offset 합성 기준을 함께 사용하도록 정의한다.

### 14.2 CellMap 보정 차이

공식 표준맵 문서는 자동 검사/CA410 셀 이동의 촬상 좌표에 `CellMapCorrectionPlan`을 적용하도록 정의한다. 자동 검사 경로의 `GlassInspectionStepPreparationService`는 검사 카메라와 CA410 이동 모두에 이 보정을 적용한다.

그러나 RecipeWindow의 수동 `CA410 이동`은 `TryResolveBridgeMoveTarget`을 직접 사용하고 `ApplyCellMapCorrection`을 호출하지 않는다. 같은 창의 `선택 IP를 셀로 이동`에는 CellMap 보정이 적용되므로 두 수동 이동 사이에도 차이가 있다.

`[추론] (코드 확인)` CellMap 보정값이 0이 아니면 수동 CA410 이동 위치와 자동 검사 CA410 위치가 달라질 수 있다.

### 14.3 이동 순서

- Contact 중 다른 StageX가 필요하면 확인 후 Pattern OFF + Release
- 같은 Contact StageX면 StageX를 잠그고 UnitY만 이동
- `InspectionUnit1Y`, `InspectionUnit2Y`를 함께 전송
- 일반 이동이면 `StageX`도 전송
- 응답 후 실제 축 도착을 다시 검증

이 메뉴는 CA410 Z축을 측정 높이로 옮기지 않는다. XY 이동 후 `CA410 측정`이 Z를 별도로 준비한다.

## 15. CA410 측정

### 15.1 대상 선택

이 기능은 Selected Cell이 아니라 화면의 `SelectedIp`로 CA410 장비를 선택한다.

```text
Config.Ca410.Devices에서 Enabled && No == SelectedIp 우선
  -> 없으면 첫 Enabled 장비
  -> 없으면 첫 장비
  -> 없으면 default 장비
```

### 15.2 실행

1. Control의 실제 Contacted 상태를 읽는다.
2. 선택 bridge의 CA410 Z축을 Config `MeasureZ`로 이동한다.
3. Contact 상태에 따라 `ContactSafeStep` 또는 일반 move mode를 사용한다.
4. Z 도착 확인, `MeasureZSettleDelayMs` 대기, 위치 재확인한다.
5. CA410에 단발 `MES` 측정을 요청한다.
6. 결과를 `Ca410Summary`, 상태, 로그에 표시한다.

CA410 Simulation이 켜져 있으면 측정 통신은 in-process simulator를 사용한다. Control Simulation과 CA410 Simulation은 별도이므로 Z 이동과 계측 통신에 필요한 모드를 각각 확인해야 한다.

### 15.3 하지 않는 일

- 선택 Cell로 CA410 XY 이동
- PG Pattern 선택 또는 전압 sweep
- `Ca410Plan.Patterns` 반복
- ELVDD 전류 읽기
- 자동 검사 결과/CSV 저장

따라서 이 메뉴는 현재 광학 위치의 장비 단발 응답을 확인하는 진단 기능이다. 공식 자동 CA410 검사의 전체 flow와 다르다.

## 16. CA410 영점 보정 (ZRC)

### 16.1 실행

1. SelectedIp 기준 CA410 장비와 측정 옵션을 결정한다.
2. CA410 Simulation이면 simulator, 아니면 serial client에 연결한다.
3. Config가 remote mode를 요구하면 `COM,1`을 먼저 전송한다.
4. `max(1000 ms, CalibrationTimeoutMs)` timeout으로 `ZRC`를 보낸다.
5. 응답 성공 여부를 확인하고 상태와 로그를 갱신한다.

### 16.2 주의

- 확인 대화상자가 없다.
- CA410 XY/Z 이동이나 PG OFF를 하지 않는다.
- Probe가 영점 보정 가능한 광학 상태인지 프로그램이 확인하지 않는다.
- 선택 Cell과 무관하며 SelectedIp가 장비 선택 기준이다.

영점 보정은 장비 제조사 절차와 현장 작업 기준을 만족시킨 뒤 실행해야 한다.

## 17. Command 활성화 조건

| 메뉴 | 활성화 조건 | 내부 추가 검증 |
|---|---|---|
| Align Flow 실행 | 항상 | DataContext, pose, Control, camera 연결 |
| 축 위치 읽기 | 항상 | ControlRuntime/연결 |
| 선택 IP를 셀로 이동 | Cell IP=1/2 및 SelectedIp 일치 | calibration, Control, contact 안전 |
| 패턴 점등 | Pattern 선택 | Cell, PgPatternIndex, mapping/runtime |
| 패턴 소등 | 항상 | Cell, mapping/runtime |
| 전체 PG 패턴 점등 | Pattern 선택 | PgPatternIndex, endpoint 범위 |
| 전체 PG 패턴 소등 | 항상 | endpoint/mapping |
| 컨택 On/Off | 항상 | Cell/ContactX/Control 또는 Release 결과 |
| CA410 이동 | Cell IP=1/2 | calibration, Control, contact 안전 |
| CA410 측정/ZRC | 항상 | Config 장비, Control Z 이동 또는 serial/simulator |

## 18. 전체 프로젝트 영향

| 기능군 | 변경하는 상태 | Recipe 저장 변경 | 자동 검사 결과 생성 |
|---|---|---:|---:|
| Align Flow | 실제 축, camera live | X | X |
| 축 위치 읽기 | 상태/로그만 | X | X |
| 셀/CA410 이동 | 실제 축, 화면 current position | X | X |
| PG On/Off | 실제 PG 점등 상태 | X | X |
| Contact On/Off | 실제 Contact/Release, local lock 상태 | X | X |
| CA410 측정 | Z축, CA410 단발 결과 표시 | X | X |
| CA410 ZRC | CA410 calibration 상태 | X | X |

이 메뉴들은 대부분 Recipe 값을 **사용**하지만 Recipe 값을 편집하거나 자동 저장하지 않는다.

## 19. Docs-코드 검증 결과

| 항목 | 공식 Docs 기준 | 현재 코드 | 판정 |
|---|---|---|---|
| Glass→축 이동 | GlassSize affine + head offset | 동일 | 일치 |
| 반대 UnitY | Config EscapeY | `ResolveEscapeY` 사용 | 일치 |
| CA410 offset | 최신 변경 기록: Inspect X + CA410 Y 합성 | 동일 | 일치 |
| CA410 측정 Z | MeasureZ 도착·정착·재확인 | 동일 | 일치 |
| CA410 Simulation | 별도 전역 토글 | 측정/ZRC에 적용 | 일치 |
| CellMap 보정 | 자동 검사/CA410 셀 이동에 적용 | 수동 검사 카메라 이동에는 적용, 수동 CA410 이동에는 미적용 | 경로 차이 |
| 자동 CA410 flow | 이동→Z→PG sweep→측정→결과 저장 | 메뉴 측정은 Z+단발 MES만 | 기능 범위가 다름 |
| 전체 PG 점등 전압 | 공식 Main flow는 Pattern/전압 적용 | 메뉴 전체 점등은 Pattern만 선택 | 차이 표시 필요 |
| Contact 안전 상태 | 실제 Contact 상태가 중요 | row-change 보호는 local 상태 사용 | 제한 사항 |

## 20. 확인된 개선 후보

1. `Align Flow 실행`을 `Align 위치 이동 + Live 시작`처럼 실제 범위가 보이도록 이름 또는 ToolTip 보완
2. Pattern ON/OFF의 CanExecute에 SelectedCell·PG mapping 조건 추가
3. 전체 PG ON에도 개별 ON과 같은 R/G/B 전압 적용이 필요한지 공식 결정
4. 전체 PG 대상에서 `Cell.Use`를 필터링할지 공식 결정
5. Contact row-change 보호를 ControlRuntime의 실제 Contacted 상태와 동기화
6. Contact On 전에 실제 StageX/UnitY가 선택 셀 목표인지 검증
7. Contact Off에서 Pattern OFF 실패를 별도 경고 상태로 유지
8. CA410 측정/ZRC에 대상 장비와 현재 위치를 보여주는 확인 단계 검토
9. 수동 `CA410 이동`에도 자동 검사와 동일한 CellMap 보정을 적용할지 공식 결정
