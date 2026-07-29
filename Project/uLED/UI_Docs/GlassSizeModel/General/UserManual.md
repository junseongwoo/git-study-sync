# GlassSizeWindow - General 탭 사용자 매뉴얼

## 이 탭에서 설정하는 것

General 탭에서는 글래스의 실제 크기·장착 방향·Align mark 위치와, Cell 이름·결과 좌표 표기 기준을 설정합니다. 잘못된 값은 Cell Map, Align, Motion 좌표, defect CSV의 row/column 표기에 영향을 줄 수 있습니다.

## 기본 정보 설정

|항목|설정 방법|주의 사항|
|---|---|---|
|Description|제품명, 규격, 용도를 작성|식별 보조용입니다. 파일명/GlassSizeId를 바꾸지 않습니다.|
|Glass Width/Height|승인된 실제 외곽 치수를 µm로 입력|반드시 0보다 커야 합니다. mm 값을 그대로 넣지 않도록 주의합니다.|
|Panel Angle|stage 위 실제 안착 방향을 0/90/180/270에서 선택|회전 방향이 불확실하면 장비 배치 도면으로 확인합니다. 90/270 변경은 특히 검사 grouping·좌표에 영향을 줍니다.|
|Left Align (Y2), Right Align (Y1)|각 align mark의 글래스 X/Y 좌표를 µm로 입력|motor 좌표가 아닌 글래스 좌표입니다. 좌표계 보정 탭 값과 혼용하지 마세요.|

## Cell 이름·Map 기준 설정

|항목|선택 기준|
|---|---|
|Cutting Mark|실제 글래스 cut mark가 있는 corner를 선택합니다. Map의 방향 확인 기준입니다.|
|First Cell Pos|현장에서 첫 번째로 부르는 cell이 있는 corner를 선택합니다. 물리 배치가 아닌 이름 시작 방향입니다.|
|분판 이름 사용|cell 이름 앞에 분판 식별자가 필요할 때 켭니다.|
|X Rule / Y Rule|현장 표기 규칙에 따라 `01`, `1`, `A`, User Defined를 선택합니다.|
|Name Order|`X then Y` 또는 `Y then X` 중 현장 cell 명명 순서를 선택합니다.|
|X/Y Labels|User Defined를 선택한 축에 실제 label을 쉼표로 구분해 입력합니다.|

예를 들어 X Rule=`A,B,C`, Y Rule=`01,02`, Name Order=`X then Y`이면 cell 이름은 `A01`, `A02`와 같은 형식이 됩니다. 분판 이름 사용 시 partition token이 앞에 붙습니다. **[추론: token 조합 코드 기준]**

## 결과 좌표 기준 설정

|항목|언제 조정하나요?|
|---|---|
|Raw Index Origin|IP raw `(0,0)`이 현물의 어떤 corner인지 mapping image와 맞추어야 할 때|
|Dot Index Origin|고객/생산 표의 row/column 시작 corner와 IP 좌표 방향이 다를 때|
|Dot Index Base|결과표가 0부터 시작하는지, 1부터 시작하는지에 맞출 때|
|XY Swap|IP X/Y 축과 현장 표기 축이 서로 바뀌어 있을 때|

이 항목은 IP 검사 내부 index를 바꾸는 기능이 아니라, Console/Verifier가 최종 defect row/column을 표시·CSV로 저장할 때 적용하는 변환 기준입니다.

## 저장 및 적용 절차

1. 값을 입력한 뒤 다른 필드로 이동해 입력값을 확정합니다.
2. Save를 누릅니다.
3. 표시되는 변경 목록에서 의도한 필드만 바뀌었는지 확인합니다.
4. 저장 후 현재 Recipe에 적용할지 묻는 경우, 모델 ID와 적용 범위를 확인합니다.
5. 적용했다면 Cell List, Cell Map, Align 기준, 테스트 defect CSV를 검증합니다.

## 변경 후 점검표

- 크기 변경: cell 범위·중심·glass 외곽이 맞는지
- 각도 변경: map 회전과 실제 장착 방향, auto IP split/safety gap이 맞는지
- Align mark 변경: 좌우 mark와 실제 카메라 시야·align 실행이 맞는지
- Naming 변경: Cell List/Map 및 export folder의 cell name이 맞는지
- Index 변경: 이미 알려진 defect 한 건의 overlay와 CSV row/column이 맞는지

## 주의 사항

- Panel Angle은 `XIndex/YIndex` 자체를 계산하는 값은 아닙니다. 다만 표시 회전, stage 방향, grouping과 IP 분할에는 영향을 줍니다.
- 새 모델의 일반 값만 입력하고 바로 생산에 사용하지 마세요. 좌표계 보정 탭의 matrix와 reference pose, recipe 적용 뒤의 cell 재생성까지 검증해야 합니다.
- User Defined label 수가 실제 cell 수보다 부족하거나 중복되지 않도록 관리하세요. General 탭에서 충분한 개수 검증이 보이지 않습니다.
- 모델 저장과 Recipe 적용은 분리된 단계입니다. 저장만 했다고 모든 Recipe가 자동으로 새 값으로 바뀌는 것은 아닙니다.
