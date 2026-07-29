# MainWindow - 메뉴/상단 툴바 개발 노트

## 구현 상태 판정

- Tool, View, Test, ETC의 표시된 하위 메뉴는 모두 Command 또는 Click handler가 연결되어 있다.
- 최상위 `Data`만 빈 `MenuItem`으로 남아 있어 미구현이다.
- `MainMenu_Click`은 최종 leaf 메뉴의 경로를 로그에 남기는 공통 Click handler다.
- code-behind로 여는 modeless 창은 이미 열려 있으면 새 창 대신 기존 창을 활성화한다: 장비 변수, 알람 관리, 컨택 유니트, Test Runner, PG Recipe.

## 주의점

- 메뉴가 창을 연다는 사실은 구현 상태를 뜻하지만, 해당 보조 창의 모든 세부 기능이 완성됐다는 뜻은 아니다.
- `Release Glass`, `Debug Glass`, `Load/Unload Ready`는 장비/검사 흐름을 실제로 시작할 수 있어 권한·안전 확인이 필요하다.
- PG simulator 정책은 최신 공식 문서의 전역 Simulation Mode 기준을 우선한다.

## 추가 확인 항목

1. AlarmManagementWindow와 AlarmManagerWindow의 역할 차이를 UI/서비스 기준으로 명확히 문서화한다.
2. Data 메뉴를 구현할지 제거할지 제품 요구사항을 확인한다.
3. 상단 4개 운영 버튼(AUTORUN/INSPECT/STOP/SET UP)의 별도 상세 분석은 이 문서 범위에서 제외했다.
