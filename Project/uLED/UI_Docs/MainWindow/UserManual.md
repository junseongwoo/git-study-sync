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

## 오른쪽 검사 정보 영역

오른쪽 영역은 **현재 진행 중인 Glass Job 정보**와 **Glass Map에서 선택한 셀의 검사 결과**를 보여줍니다. 숫자가 글래스 전체 합계인지 선택 셀의 값인지 혼동하지 않도록 아래 구분을 확인하십시오.

### 검사 상태와 기본 정보

| 표시/컨트롤 | 표시되는 내용 | 확인 방법 |
|---|---|---|
| `AUTORUN` | 자동 운전 사용 여부 | 켜짐/꺼짐 상태를 확인합니다. 세부 실행 조건은 검사 실행 옵션을 따릅니다. |
| `INSPECT` | Glass Job 검사 시작 | 검사 대상과 옵션을 확인한 뒤 실행합니다. |
| `STOP` | 현재 검사 중지 요청 | 중지 후 상태 표시와 로그에서 실제 종료 여부를 확인합니다. |
| `SET UP` | Recipe 편집 창 열기 | 검사 조건을 확인하거나 수정할 때 사용합니다. |
| 큰 `INSPECT`/`STOP` 표시 | 현재 Glass Job 실행 상태 | 검사 실행 중에는 `INSPECT`, 실행 중이 아니면 `STOP`으로 표시됩니다. |
| `RECIPE` | 현재 선택된 레시피 이름 | 검사 전에 올바른 레시피인지 확인합니다. |
| `LOT ID` | 현재 검사 Lot 식별자 | 결과가 어느 Lot에 속하는지 확인합니다. |
| `GlassID` | 현재 검사 Glass 식별자 | 저장 결과 폴더와 검사 결과를 구분하는 기준입니다. |
| `Start Time` | 시작 시각 표시 예정 영역 | **현재 XAML에는 값 바인딩이 없어 표시되지 않는 미구현 항목입니다.** |

### 셀 판정

`셀 판정`은 글래스 전체 합계가 아니라 **Glass Map에서 현재 선택한 셀 1개**의 요약입니다. 검사가 끝난 셀을 선택하면 다음 값이 표시됩니다.

| 항목 | 의미 |
|---|---|
| `Cell Judge` | 선택 셀의 최종 판정 코드입니다. 판정 규칙의 우선순위에 따라 대표 판정이 결정됩니다. |
| `Defect Name` | 최종 판정을 대표하는 불량 이름입니다. |
| `Black` | 암점으로 분류된 dot 수입니다. |
| `Dark` | 휘도 불량으로 분류된 dot 수입니다. |
| `Cluster` | 서로 인접한 암점이 군집으로 판정된 건수입니다. |
| `White` | 명점으로 판정된 건수입니다. |
| `WVL` | White Vertical Line, 세로 명선 건수입니다. |
| `WHL` | White Horizontal Line, 가로 명선 건수입니다. |
| `BVL` | Black Vertical Line, 세로 암선 건수입니다. |
| `BHL` | Black Horizontal Line, 가로 암선 건수입니다. |
| `LightFail` | 점등은 되었지만 점등량/점등 상태가 판정 기준을 만족하지 못한 건수입니다. |
| `MissLight` | 미점등으로 판정된 건수입니다. |

셀을 선택하지 않았거나 아직 해당 셀의 결과가 수신되지 않았다면 `-`, `판정 없음`, `선택된 셀 결과 없음`이 표시될 수 있습니다.

### 불량 목록

불량 목록은 선택 셀에서 검출된 개별 불량과 분석 결과를 `defects.csv`와 같은 체계로 보여줍니다.

| 열 | 의미 |
|---|---|
| `#` | 화면 목록의 표시 순번 |
| `P` | 불량이 검출된 검사 패턴의 인덱스 |
| `Channel` | 불량과 관련된 R/G/B/W 채널 |
| `Code` | `BLACK`, `DARK`, `WHITE`, `CLUSTER`, `WVL`, `WHL`, `BVL`, `BHL`, `ETC` 등의 불량 코드 |
| `Row` | 표시/CSV 기준의 세로 dot 번호 |
| `Column` | R/G/B sub dot을 포함한 표시 열 번호 |
| `X Index` | R/G/B를 하나로 묶은 가로 dot 번호 |
| `Count` | 불량 dot 수. 점은 보통 1, 선은 선 위 불량 dot 수, 군집은 군집을 구성하는 dot 수 |
| `SX`, `SY` | 불량 영역이 시작되는 X Index와 표시 Row |
| `W`, `H` | 불량 영역의 가로·세로 크기이며 단위는 dot |
| `Level` | 해당 불량의 검사 레벨 값 |
| `CamX`, `CamY` | 원본 검사 이미지에서의 카메라 pixel 좌표 |

`Column`과 `X Index`는 같은 값이 아닙니다. `X Index`는 논리 dot 열이고, `Column`은 R/G/B 위상을 펼친 sub dot 열입니다. 따라서 한 `X Index`에 R/G/B `Column` 세 개가 대응합니다. `CamX/CamY`는 이미지 위치를 찾기 위한 물리 pixel 좌표입니다.

> **Docs-코드 차이:** 공식 export 문서 기준으로 셀의 `defects.csv`는 암점 계열을 모두 담는 파일이 아닙니다. 현재 Main 화면 코드는 사용자가 한 화면에서 판정을 확인할 수 있도록 `rgb_merged` 계열 결과의 `BLACK`과 `DARK`도 불량 목록에 합쳐 표시합니다. 따라서 화면의 행 수와 저장된 `defects.csv`의 행 수가 항상 같지는 않습니다.

### Crop과 Mapping Image

1. 불량 목록에서 확인할 행을 선택합니다.
2. `Crop`에는 선택 불량 주변의 원본 기반 확대 이미지가 표시됩니다.
3. `Mapping Image`에는 선택 셀의 패턴별 intensity/thumbnail 이미지와 불량 표시 이미지가 나타납니다.
4. 패턴 탭 또는 탭 안의 선택 항목을 바꾸면 같은 셀의 다른 패턴 이미지를 비교할 수 있습니다.

Crop은 IP가 생성한 검사 산출물을 우선 사용합니다. 저장된 Crop이 없는 과거 결과는 원본 이미지와 카메라 좌표가 있을 때 화면 분석용 Crop을 만들 수 있습니다. [추론] 원본 이미지 또는 유효한 좌표가 없으면 Crop이 비어 있을 수 있습니다.

### 검사 중 확인 순서

1. 큰 상태 표시가 `INSPECT`인지 확인합니다.
2. `RECIPE`, `LOT ID`, `GlassID`가 현재 검사 대상과 일치하는지 확인합니다.
3. Glass Map에서 검사 완료 셀을 클릭합니다.
4. `셀 판정`에서 최종 판정과 종류별 수량을 확인합니다.
5. 불량 목록의 `Code`, `Row/Column`, `Count`, `Level`을 확인합니다.
6. 필요한 불량 행을 선택하여 `Crop`과 `Mapping Image`로 위치와 형상을 확인합니다.
7. `마지막 불량셀 보기`를 켜면 새 불량 셀이 확인될 때 그 셀을 자동 선택합니다. [추론] 작업자가 특정 셀을 계속 비교해야 할 때는 이 옵션을 끄는 것이 적합합니다.
8. 글래스 전체 요약은 왼쪽 `Cell Summary`, 패턴별 결과는 `패턴별 통계`, 계측 결과는 `CA410` 탭에서 확인합니다.

## 주의 사항

- `INSPECT`를 누르기 전 현재 Recipe, LOT ID, Glass ID, IP/Control 연결 상태를 확인하십시오.
- 공식 문서상 레시피 선택은 Main 화면, IP 연결·상태 확인·수동 업로드는 Recipe Editor에서 수행합니다.
- `STOP`은 검사 중지 요청입니다. 결과 저장 완료 여부는 상태/로그를 함께 확인하십시오.
- Simulation 모드는 실장치 의존 기능을 성공한 것처럼 처리하지 않습니다.
- 화면의 `AutoRun`은 켜기/끄기 상태만 표시합니다. [추론] 정확한 자동 시작 조건과 반복 방식은 실행 옵션 및 Test Runner 설정에 따라 달라질 수 있습니다.
