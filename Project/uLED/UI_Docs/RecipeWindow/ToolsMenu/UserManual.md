# RecipeWindow 도구 메뉴 사용자 매뉴얼

작성일: 2026-08-03  
대상: `RecipeWindow > 도구`

## 1. 메뉴 목적

도구 메뉴는 Recipe에 저장된 위치·PG·Contact·CA410 설정을 사용해 실제 장비를 수동으로 시험하는 메뉴다. 메뉴 실행 자체는 Recipe를 저장하지 않는다.

축 이동, 점등, Contact, 영점 보정이 즉시 장비에 전달될 수 있으므로 실행 전에 다음을 확인한다.

1. Main의 실제 장비/Simulation 상태
2. Control과 PG 연결
3. 선택 Cell, Selected IP, 선택 Pattern
4. Contact 상태와 장비 간섭 여부
5. Recipe의 Align pose, ContactX/OD, PG Mapping
6. GlassSize calibration, Head offset, EscapeY 설정
7. CA410 장비 번호와 MeasureZ

## 2. 기능 요약

| 메뉴 | 사용 목적 | 구현 상태 |
|---|---|---:|
| Align Flow 실행 | Align 기준 위치로 이동하고 양쪽 카메라 Live 시작 | 구현 |
| 축 위치 읽기 | Control 축과 Glass/Contact 상태 확인 | 구현 |
| 선택 IP를 셀로 이동 | 선택 셀의 검사 카메라 위치로 이동 | 구현 |
| 패턴 점등/소등 | 선택 셀의 PG 한 대를 제어 | 구현 |
| 전체 PG 패턴 점등/소등 | Recipe가 참조하는 여러 PG를 일괄 제어 | 구현 |
| 컨택 On/Off | Contact/Release 수동 실행 | 구현 |
| CA410 이동 | 선택 셀의 CA410 XY 위치로 이동 | 구현 |
| CA410 측정 | 현재 XY에서 Z 준비 후 단발 측정 | 구현 |
| CA410 영점 보정 | 선택 장비에 ZRC 실행 | 구현 |

## 3. Align Flow 실행

### 사용 순서

1. `Align / 제어` 탭에서 Recipe Align 기준 pose를 확인한다.
2. 장비가 이동 가능한 상태인지 확인한다.
3. `도구 > Align Flow 실행`을 선택한다.
4. 확인 창의 설명을 읽고 진행한다.
5. 축 이동 후 AlignWindow가 열리는지 확인한다.
6. 좌·우 Align 카메라 Live 영상을 확인한다.
7. 이후 실제 matching과 Align 보정은 AlignWindow에서 별도로 실행한다.

주의: 이 메뉴만 실행해도 Align이 완료되는 것은 아니다. 기준 위치 이동과 Live 준비까지만 수행한다.

## 4. 축 위치 읽기

Control 상태를 새로 요청해 다음 정보를 RecipeWindow 하단 상태와 로그에 표시한다.

- Glass 존재와 Contact 상태
- StageX/U/V/W
- Unit1/Unit2 Y축
- Contactor X/Z
- Unit/Camera Z축

이 기능은 상태 조회만 수행한다. 읽은 위치를 Recipe Align/Contact 값으로 저장하지 않는다.

## 5. 선택 IP를 셀로 이동

### 준비

1. 셀 목록 또는 셀 맵에서 Cell을 선택한다.
2. 선택 Cell의 IP 할당을 확인한다.
3. RecipeWindow의 Selected IP가 Cell의 IpNo와 같은지 확인한다.
4. Contact 중이면 같은 StageX 이동인지 확인한다.

### 실행

`도구 > 선택 IP를 셀로 이동`을 선택하고 확인 창에서 다음 목표값을 확인한다.

- Cell 이름과 IP
- Glass 중심 X/Y
- StageX
- Y1/Y2

Contact 상태에서 다른 StageX로 이동하려 하면 Pattern OFF와 Release를 먼저 수행할지 다시 묻는다.

이 기능은 선택 셀 중심을 **검사 카메라**가 보도록 이동한다. CA410 위치로 이동하려면 `CA410 이동`을 사용한다.

## 6. 패턴 점등

### 사용 순서

1. Cell을 선택한다.
2. 검사 Pattern을 선택한다.
3. Pattern의 `PG Pattern Index`와 R/G/B 검사 전압을 확인한다.
4. PG Mapping 탭에서 Cell YIndex의 PG endpoint를 확인한다.
5. `패턴 점등`을 선택한다.
6. 화면의 Pattern 상태와 실제 점등을 확인한다.

이 기능은 선택 Pattern 번호를 PG에 선택하고 R/G/B 검사 전압을 함께 적용한 뒤 `PatternOnDelayMs`만큼 기다린다.

현재 확인 대화상자 없이 바로 전송되므로 메뉴를 누르기 전에 대상 Cell과 Pattern을 확인해야 한다.

## 7. 패턴 소등

선택 Cell의 YIndex에 매핑된 PG 한 대만 끈다.

1. 끌 PG에 해당하는 Cell을 선택한다.
2. `패턴 소등`을 선택한다.
3. 화면 상태가 `OFF`인지 확인한다.
4. 실제 PG도 꺼졌는지 확인한다.

이 기능도 확인 대화상자 없이 즉시 실행된다. 다른 PG는 자동으로 꺼지지 않는다.

## 8. 전체 PG 패턴 점등

Recipe Cell들이 참조하는 여러 PG에 같은 Pattern 번호를 선택한다.

1. Pattern을 선택한다.
2. `PG Pattern Index > 0`인지 확인한다.
3. `전체 PG 패턴 점등`을 선택한다.
4. 확인 창에서 대상 PG와 주소를 확인한다.
5. 실행 후 성공/실패 개수를 확인한다.

중요: 현재 전체 점등은 Pattern 번호만 선택하고 개별 `패턴 점등`처럼 R/G/B 검사 전압을 다시 적용하지 않는다. 정확한 전압이 필요한 시험은 각 PG의 현재 전압 상태를 확인해야 한다.

또한 현재 코드는 Unuse Cell의 YIndex도 대상 계산에 포함할 수 있다.

## 9. 전체 PG 패턴 소등

1. `전체 PG 패턴 소등`을 선택한다.
2. 확인 창의 대상 PG 목록을 확인한다.
3. 실행 후 성공/실패 개수를 확인한다.
4. 일부 실패가 있으면 상세 endpoint를 확인하고 해당 PG를 별도로 점검한다.

일부 PG가 실패해도 나머지 PG의 OFF는 계속 수행한다.

## 10. 컨택 On

권장 작업 순서:

```text
Cell 선택
  -> 선택 IP를 셀로 이동
  -> 실제 StageX/Y 위치 확인
  -> ContactX/OD 확인
  -> 컨택 On
```

`컨택 On`은 ContactorX를 Recipe ContactX로 이동하고 `FlowContact`에 OD 값을 전달한다. 선택 Cell의 검사 위치로 자동 이동하지 않으므로 셀 이동을 먼저 수행해야 한다.

실행 후 다음 두 상태를 함께 확인한다.

- RecipeWindow의 Contact 상태
- ControlRuntime의 실제 `Contacted` 표시

## 11. 컨택 Off

`컨택 Off`는 다음 순서로 동작한다.

```text
선택 Cell PG OFF 시도 -> Control Release
```

1. Contact된 row에 해당하는 Cell을 선택한다.
2. `컨택 Off`를 선택한다.
3. 확인 창에서 진행한다.
4. PG가 꺼졌는지 확인한다.
5. Control의 실제 Contacted가 OFF인지 확인한다.

PG OFF가 실패해도 Release는 계속 시도되므로 완료 메시지만 보지 말고 실제 PG 상태를 확인한다.

## 12. CA410 이동

### 사용 순서

1. CA410로 측정할 Cell을 선택한다.
2. Cell의 IpNo가 1 또는 2인지 확인한다.
3. `CA410 이동`을 선택한다.
4. 확인 창에서 Cell, Glass X/Y, StageX, 이동할 UnitY를 확인한다.
5. 이동 완료 후 축 상태를 확인한다.

선택 Cell에 배정된 IP가 좌/우 CA410 bridge를 결정한다. 이 기능은 화면 Selected IP와 Cell IpNo 일치를 요구하지 않는다.

CA410 이동은 XY 위치만 준비하며 MeasureZ로는 이동하지 않는다.

현재 수동 CA410 이동에는 Recipe의 CellMap StageX/UnitY 보정이 적용되지 않는다. 자동 검사 CA410 이동에는 보정이 적용되므로 CellMap 보정값이 0이 아니면 두 위치가 달라질 수 있다.

## 13. CA410 측정

권장 순서:

```text
Cell 선택 -> CA410 이동 -> Selected IP 확인 -> CA410 측정
```

`CA410 측정`은 화면 Selected IP에 대응하는 장비를 사용한다. 실행 시 CA410 Z축을 MeasureZ로 이동하고 정착을 기다린 뒤 한 번 측정한다.

이 기능은 다음 작업을 하지 않는다.

- Cell XY로 자동 이동
- PG 점등 또는 전압 sweep
- CA410 Pattern/Step 반복
- 결과 CSV 저장

따라서 먼저 CA410 이동과 필요한 PG 점등을 수행한 뒤 단발 응답 확인 용도로 사용한다.

장비 없이 시험할 때는 Main에서 `CA410 Simulation`을 켠다. Z축 이동도 모의하려면 별도로 `Control Simulation`이 필요하다.

## 14. CA410 영점 보정 (ZRC)

1. Main의 실제/CA410 Simulation 상태를 확인한다.
2. Selected IP가 영점 보정할 장비 번호와 맞는지 확인한다.
3. 제조사 절차에 따라 probe와 광학 환경을 영점 보정 상태로 준비한다.
4. `CA410 영점 보정 (ZRC)`을 선택한다.
5. 상태와 로그에서 완료 또는 오류를 확인한다.

이 메뉴는 확인 창 없이 즉시 ZRC를 보낸다. CA410 위치 이동, Z 이동, PG 소등을 자동 수행하지 않는다.

## 15. Simulation 사용

| 시험 대상 | 필요한 모드 |
|---|---|
| 축 이동/Contact | Control Simulation 또는 실제 Control |
| PG On/Off | PG Simulation 또는 실제 PG |
| CA410 계측/ZRC | CA410 Simulation 또는 실제 CA410 |
| Align 카메라 Live | 실제/구성된 Align camera runtime |

Control Simulation만 켜도 CA410와 Align camera가 자동 성공하지 않는다. 각 Simulation은 독립적으로 선택한다.

## 16. 문제 발생 시 확인

| 증상 | 확인 항목 |
|---|---|
| Align Flow 실패 | Recipe Align pose, Control 연결, 좌·우 camera 연결 |
| 셀 이동 메뉴 비활성 | Cell IpNo, Selected IP 일치 여부 |
| 검사 카메라 셀 위치 오류 | GlassSize calibration, inspect head offset, CellMap correction, EscapeY |
| 수동/자동 CA410 위치 차이 | 수동 메뉴의 CellMap 보정 미적용, 자동 검사 보정값, CA410 head offset |
| Pattern ON 실패 | Cell 선택, PgMapping, endpoint, PgPatternIndex |
| 전체 PG 일부 실패 | 상태 문구의 endpoint별 오류, PG 연결 |
| Contact On 실패 | Cell, ContactX, OD, Control 연결 |
| Contact Off 후 PG 점등 유지 | 선택 Cell PG mapping, 별도 Pattern OFF 또는 전체 OFF |
| CA410 측정값 없음 | Selected IP/장비, XY 위치, MeasureZ, serial/simulator |
| ZRC 실패 | 장비 상태, remote 설정, COM port, calibration timeout |

운영 로그 위치:

```text
c:\elp\uLedAoi\logs\yyyyMM\
```

주요 로그 category는 `ManualAlign`, `ControlAxisStatus`, `StageMove`, `RecipePg`, `RecipeContact`, `RecipeCa410`, `ControlMove`다.
