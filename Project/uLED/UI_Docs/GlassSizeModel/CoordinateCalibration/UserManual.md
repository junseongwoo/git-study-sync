# GlassSizeWindow - 좌표계 보정 탭 사용자 매뉴얼

## 이 탭의 역할

좌표계 보정은 Glass X/Y 좌표를 장비의 StageX, Y1, Y2 이동값으로 바꾸는 기준을 설정합니다. 값이 잘못되면 카메라가 mark나 cell의 반대 방향 또는 잘못된 위치로 이동할 수 있으므로, 승인된 보정 절차가 있는 작업자만 변경해야 합니다.

## 각 항목의 사용 방법

| 항목                                | 무엇을 입력하나요?                              | 어떻게 설정하나요?                                                      |
| --------------------------------- | --------------------------------------- | --------------------------------------------------------------- |
| 기본 Matrix 값 적용                    | Panel Angle 기준 기본 방향값                   | 새 모델 또는 Panel Angle 변경 후 출발값이 필요할 때 누릅니다. 실제 계측 보정을 대신하지는 않습니다. |
| GlassX / GlassY × StageX / UnitY1 | Glass 1 µm 변화에 대한 motor 축 변화량           | 승인된 calibration 결과가 있을 때 4개 계수를 입력합니다. 일반 운영 중에는 임의 수정하지 않습니다.  |
| StageX                            | 좌/우 align mark 위치에서 공통인 StageX 절대값      | 카메라가 mark에 정확히 맞은 상태에서 `현재값 읽기`를 누릅니다.                          |
| Left Y2                           | 왼쪽 align mark 위치의 InspectionUnit2Y 절대값  | 왼쪽 Y2 카메라가 mark를 보는 위치에서 읽습니다.                                  |
| Right Y1                          | 오른쪽 align mark 위치의 InspectionUnit1Y 절대값 | 오른쪽 Y1 카메라가 mark를 보는 위치에서 읽습니다.                                 |

## 안전한 설정 순서

1. General 탭에서 Glass Size, Panel Angle, 좌/우 Align mark 좌표를 먼저 저장합니다.
2. 글래스를 실제 생산과 같은 방향으로 장착합니다.
3. 안전한 Jog 절차로 왼쪽 mark를 Y2 align camera 시야 중앙에 맞춥니다.
4. 오른쪽 mark를 Y1 align camera 시야 중앙에 맞춥니다.
5. 두 mark 기준 위치가 맞는 상태에서 `현재값 읽기`를 사용해 pose를 입력합니다.
6. `기본 Matrix 값 적용` 또는 승인된 실측 matrix를 입력합니다.
7. 저장 전 변경 목록에서 4개 계수와 3개 pose가 의도한 값인지 확인합니다.
8. 저속/안전 조건에서 알려진 Glass 좌표 몇 개를 시험해 StageX/Y1/Y2 목표가 맞는지 확인합니다.

## 값 변경의 영향

|변경|어떤 현상이 바뀌나요?|
|---|---|
|StageXPerGlassX/Y|Glass 위치에 따른 StageX 이동량과 방향이 바뀝니다.|
|UnitY1PerGlassX/Y|Glass 위치에 따른 Y1 이동량, mirror된 Y2 이동량과 방향이 바뀝니다.|
|StageX pose|좌·우 align 기준의 StageX 절대 위치가 함께 이동합니다.|
|Left Y2 pose|왼쪽 align camera의 Y2 절대 기준이 이동합니다.|
|Right Y1 pose|오른쪽 align camera의 Y1 절대 기준이 이동합니다.|
|Panel Angle 후 기본값 적용|새 안착 방향에 맞춰 matrix preset과 내부 calibration 점이 다시 생성됩니다.|

## 현재값 읽기 사용 시 주의

- 이 기능은 축을 이동하지 않습니다. 현재 Control이 보고한 값만 읽습니다.
- 반드시 mark가 카메라 시야의 승인된 기준 위치에 있을 때 사용하세요.
- 글래스 미장착, 컨택 상태, 잘못된 camera 위치에서 읽은 값도 그대로 입력될 수 있습니다. 상태 메시지의 `GlassPresent`, `Contacted`도 함께 확인하세요.
- Control 연결이 안 되면 읽을 수 없습니다.

## 저장 오류와 점검

|오류/상황|확인 사항|
|---|---|
|matrix 저장 오류|4개 값이 두 Glass 방향을 구분하는지 확인합니다. 서로 같은 방향만 가리키면 singular matrix가 됩니다.|
|align이 반대 방향으로 움직임|Panel Angle, matrix 계수 부호, Y1/Y2 기준 pose와 mark 입력을 확인합니다.|
|left/right 위치가 모두 일정하게 어긋남|Reference Pose를 mark 위치에서 다시 teach합니다.|
|거리가 멀수록 오차가 커짐|matrix scale/cross-axis 계수와 실제 calibration 절차를 점검합니다.|
|Panel Angle을 바꾼 뒤 이상|matrix는 자동 변경되지 않습니다. 기본값 적용 또는 승인 matrix 재입력 뒤 검증합니다.|
