# ConfigWindow - Motion / Coordinate 탭 사용자 매뉴얼

## 이 탭의 역할

이 탭은 Control 통신, 두 검사 unit의 동시 이동 안전거리, UVW 보정 기구 좌표계를 설정합니다. 잘못된 값은 통신 실패, 동시 이동 충돌 위험, Align 보정 반대 방향 이동으로 이어질 수 있습니다.

## Control 설정

|항목|사용 방법|주의 사항|
|---|---|---|
|Control IP|실제 Control host IP/hostname을 입력|저장만으로 현재 연결이 즉시 바뀐다고 가정하지 말고 재연결 후 status를 확인합니다.|
|Control Port|Control host 포트를 1~65535로 입력|기본 Control host 5001과 simulator 5002를 혼동하지 마세요.|
|Min Safe GlassY Gap|기구 간섭 검토로 승인된 최소 거리 입력|기본 300,000 µm는 충돌 방지 safety rule입니다. 처리량을 위해 임의로 낮추지 마세요.|

## UVW 설정

|항목|설정 기준|
|---|---|
|GlassSize 기반 UVW 자동 계산 사용|일반 생산에서는 켜 둡니다. 제품별 GlassSize 폭/높이/각도를 반영해 계산합니다.|
|Positive Theta|현장 +Theta jog가 CW인지 CCW인지의 승인 결과를 선택합니다.|
|Ref Glass W/H|장비 셋업 시 기준 글래스 치수를 µm로 기록합니다.|
|-X Edge StageX|글래스의 -X edge가 놓이는 실제 StageX 기준 위치입니다.|
|Center StageY|글래스 중심이 놓이는 StageY 기준 위치입니다.|
|U/V/W Dir|각 축을 단독 jog했을 때 만들어지는 stage 병진 방향을 선택합니다.|
|U/V/W Line X/Y|각 축 작용선의 실제 stage 좌표를 입력합니다. 기구 도면·계측값을 사용합니다.|

## 안전한 변경 절차

1. 생산 run과 장비 자동 이동을 중지하고, 현재 Config backup 위치를 확인합니다.
2. Control IP/Port는 host 설정을 확인한 뒤 변경합니다.
3. 안전 gap은 기구 간섭 승인값을 유지합니다.
4. UVW geometry는 장비 도면/계측 raw 값을 사용합니다. 추정값을 입력하지 않습니다.
5. Save의 변경 목록을 확인합니다.
6. Control을 재연결하고 status를 확인합니다.
7. 저속 안전 조건에서 +X, +Y, +Theta jog를 각각 검증합니다.
8. 알려진 align fixture로 theta 및 XY 보정이 예상 방향으로 수렴하는지 확인합니다.

## 값 변경의 영향

|변경|영향|
|---|---|
|안전 gap 증가|동시 검사 step이 줄고 안전 여유가 증가할 수 있습니다.|
|안전 gap 감소|동시 검사 가능성이 늘 수 있지만 충돌 위험이 커집니다.|
|Positive Theta|theta 보정에서 U/V/W 축 움직임의 부호가 바뀝니다.|
|Glass placement|글래스 중심 및 theta 회전 보상 기준이 바뀝니다.|
|U/V/W Direction|XY 보정 시 해당 축이 움직이는 방향이 바뀝니다.|
|U/V/W Line|theta 보정 시 회전 lever arm과 축별 보상량이 바뀝니다.|

## 주의 사항

- `Use Auto Calculation`을 끄면 현재 코드가 기존 고정 AlignUvw 값을 사용합니다. 이는 공식 raw geometry 기반 원칙과 다르므로 일반 운영에서 사용하지 마세요.
- 90/270도 GlassSize는 stage X footprint에 Glass Height가 사용됩니다. 제품 회전값은 GlassSize Model에서 정확히 설정해야 합니다.
- U/V/W 설정을 바꾼 뒤에는 +Theta만이 아니라 +X/+Y 병진도 함께 검증해야 합니다.
- Config 저장은 현재 Recipe의 GlassSize나 AlignPlan을 자동으로 변경하지 않습니다.
