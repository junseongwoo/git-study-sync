# Main 화면 사용자 매뉴얼

## 화면 목적

Main 화면은 현재 사용할 레시피와 글래스 셀 배치를 확인하고, 장비 연결 상태를 보면서 설정·편집·테스트 기능으로 이동하는 시작 화면입니다. 현재 구현에서는 검사 진행과 선택 셀의 결과도 이 화면에서 확인할 수 있습니다.

## 화면을 보는 방법

- 상단: 알람, IP/Control 연결 상태, Simulation 상태, 메뉴, Map 확대율
- 왼쪽 위: Glass Map. 셀을 클릭하면 해당 셀을 선택합니다.
- 왼쪽 아래: 로그와 검사 진행/요약/통계/CA410 결과 탭
- 오른쪽: 검사 실행 버튼, 현재 레시피와 LOT/Glass ID, 선택 셀 판정과 불량 이미지

## 기본 사용 순서

1. 상단의 `IP Connected`, `Control Connected` 상태를 확인합니다.
2. 필요하면 `Tool > Load Recipe...`에서 사용할 레시피를 엽니다.
3. `Tool > Glass Size Model`에서 글래스 모델을, `Tool > Recipe`에서 검사 조건을 확인하거나 수정합니다.
4. Glass Map에서 확인할 셀을 클릭합니다.
5. 오른쪽의 셀 판정·불량 목록·이미지에서 선택 셀의 결과를 확인합니다.
6. 장비/검사 준비가 끝난 경우 `INSPECT`를 사용합니다.

공식 문서의 권장 준비 순서는 Config → Glass Size Model → Recipe → Align/Control → Pattern → 장비 테스트 → Validate → IP 업로드입니다.

## 메뉴 설명

| 메뉴 | 용도 |
|---|---|
| Tool > Load Recipe... | 기존 레시피를 선택하여 현재 레시피로 전환합니다. 연결된 IP가 있으면 자동 업로드될 수 있습니다. |
| Tool > Glass Size Model | 글래스 크기, 회전, Align mark 등 글래스 기준 정보를 관리하는 창을 엽니다. |
| Tool > Recipe | Pattern, Point, Cell, Align, Control 등 상위 레시피 편집 창을 엽니다. |
| Tool > Config | 장비/통신 관련 설정 창을 엽니다. |
| Tool > Simulation | Control, PG, CA410의 Simulation 모드를 켜거나 끕니다. 장비 동작을 대체하지 않으므로 실제 장비가 필요한 기능은 실패할 수 있습니다. |
| Tool > Export... | 현재 검사 결과의 내보내기를 시작합니다. |
| View > Refresh Map | 현재 레시피 기준으로 Glass Map 표시를 갱신합니다. |
| View > Alarm Manager | 활성 알람을 확인하고 관리합니다. |
| Test > Inspect > Load Saved Glass... | 이전에 저장된 글래스 검사 결과를 화면에 불러옵니다. |
| Test > Inspect > Release Glass... | 글래스 검사 실행 절차를 시작합니다. |
| Test > Inspect > Debug Glass... | 검사 재생/디버그 절차를 시작합니다. |
| Test > Inspect > Clear | 화면의 검사 재생 상태를 초기화합니다. |
| Test > Load Ready / Unload Ready | 반입/반출 준비 flow를 실행합니다. |
| Test > Flow Test | 통신 기반 flow 검증 화면을 엽니다. |
| Test > EEC-P725R2 PG Test / CA-410 Test | PG 점등 또는 CA-410 측정 테스트 화면을 엽니다. |

## 검사 결과 확인

1. Glass Map에서 셀을 클릭합니다.
2. 오른쪽 `셀 판정`에서 선택 셀의 최종 판정과 불량 종류별 수량을 확인합니다.
3. 아래 불량 목록에서 행을 선택합니다.
4. `Crop`에서 해당 불량 영역 이미지를, `Mapping Image`에서 패턴별 결과 이미지를 확인합니다.
5. 왼쪽 `Cell Summary`, `패턴별 통계`, `CA410` 탭에서 전체 또는 패턴별 결과를 확인합니다.

## 주의 사항

- `INSPECT`를 누르기 전 현재 Recipe, LOT ID, Glass ID, IP/Control 연결 상태를 확인하십시오.
- 공식 문서상 레시피 선택은 Main 화면, IP 연결·상태 확인·수동 업로드는 Recipe Editor에서 수행합니다.
- `STOP`은 검사 중지 요청입니다. 결과 저장 완료 여부는 상태/로그를 함께 확인하십시오.
- Simulation 모드는 실장치 의존 기능을 성공한 것처럼 처리하지 않습니다.
- 화면의 `AutoRun`은 켜기/끄기 상태만 표시합니다. [추론] 정확한 자동 시작 조건과 반복 방식은 실행 옵션 및 Test Runner 설정에 따라 달라질 수 있습니다.
