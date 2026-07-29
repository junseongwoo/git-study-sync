# ConfigWindow - General 탭 사용자 매뉴얼

## 이 탭의 역할

General 탭은 Console 전체의 표시와 검사 산출물 기본값을 설정합니다. Glass의 크기·Align mark·좌표계 보정은 여기서 설정하지 않고 Glass Size Model에서 관리합니다.

## 항목별 사용 방법

|항목|사용 방법|주의 사항|
|---|---|---|
|Config File / Backup Dir|현재 운영 설정과 백업 위치를 확인합니다.|읽기 전용입니다. 저장 전 어느 환경을 수정하는지 확인할 때 사용합니다.|
|Version|설정 버전을 확인합니다.|저장할 때 자동으로 증가합니다. 직접 수정하지 않습니다.|
|분판 이름 Overlay|Cell Map에서 분판 이름을 보일지 선택합니다.|표시만 바꾸며 cell 물리 배치를 바꾸지 않습니다.|
|투입 방향|실제 글래스가 장비로 들어오는 방향을 선택합니다.|Glass Size의 Panel Angle과 함께 map 표시 방향에 영향을 줍니다.|
|Show Angle|현장 승인값이 있을 때만 입력합니다.|현재 사용처를 확정하지 못했으므로 임의 변경하지 마세요.|
|Save Original Images|원본을 run folder/NAS에 보관해야 하면 켭니다.|저장 용량·NAS 성능·검사 처리량에 영향을 줄 수 있습니다.|
|Lot ID / Glass ID|자주 쓰는 기본 식별자를 입력합니다.|실제 생산 run 전에는 작업 지시와 일치하는지 다시 확인합니다. 비워두면 `LotID`, `GlassID` 기본값을 사용합니다.|
|Image NAS Root|원본 이미지 저장 최상위 폴더를 절대 경로로 입력합니다.|Console과 IP가 모두 쓰기 가능한 경로여야 합니다.|
|Inline Crop Max|완료 결과에 포함할 crop 최대 수를 0~1000에서 입력합니다.|0이면 crop을 포함하지 않습니다. 큰 값은 payload와 메모리 사용량을 늘릴 수 있습니다.|
|Find Pitch Min/Max|실제 pitch의 object 거리 범위를 px로 입력합니다.|min은 max보다 작아야 합니다. 현물/버퍼 이미지로 검증합니다.|
|Find Pitch Margins|검색 ROI 여유와 결과 ROI 여유를 px로 입력합니다.|너무 작으면 edge를 잘라낼 수 있고, 너무 크면 불필요한 영역을 포함할 수 있습니다.|

## 저장 절차

1. 변경할 항목을 입력합니다. 숫자 입력란은 값을 확정하도록 다른 항목을 클릭합니다.
2. Save를 누릅니다.
3. 표시되는 변경 목록에서 예상하지 못한 변경이 없는지 확인합니다.
4. 확인하면 기존 Config는 Backup Dir에 자동 백업되고 새 YAML이 저장됩니다.
5. 저장 후 새 검사 또는 관련 화면에서 실제 반영 결과를 확인합니다.

## 원본 이미지 저장 설정 예시

1. NAS 공유 폴더가 Console/검사 IP process에서 접근 가능한지 확인합니다.
2. `Image NAS Root`에 절대 경로를 입력합니다.
3. 원본 보관이 필요하면 `Save Original Images`를 켭니다.
4. 시험 glass 1장으로 run을 수행합니다.
5. Lot/Glass 하위 폴더가 생성되고 원본이 저장되는지, 저장 지연이나 buffer 경고가 없는지 확인합니다.

## Find Pitch 설정 예시

1. 대표 현재 buffer 이미지를 준비합니다.
2. 예상 object 간 거리보다 조금 넓게 Min/Max를 설정합니다.
3. Find Pitch를 실행해 후보·pitch·ROI가 맞는지 확인합니다.
4. 오검출이 있으면 범위를 좁히고, 대상이 누락되면 범위를 넓힙니다.
5. 결과 ROI가 너무 가장자리에 붙으면 Search/Result Margin을 조정합니다.

## 주의 사항

- Save Original Images를 켠 상태에서는 NAS 성능이 낮으면 저장이 밀려 IP buffer 문제가 발생할 수 있습니다.
- Image NAS Root가 비어 있거나 권한이 없으면 원본 저장이 실패할 수 있습니다. 화면 입력만으로 경로가 검증되지는 않습니다.
- 투입 방향은 Panel Angle을 대체하지 않습니다. 제품 방향은 GlassSize Model에서도 별도로 맞춰야 합니다.
- 설정 저장은 현재 Recipe의 내용을 자동 변경하지 않습니다.
