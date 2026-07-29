# MainWindow - 메뉴/상단 툴바 사용 요약

| 메뉴 | 언제 사용하나 | 주의사항 |
|---|---|---|
| Tool > Load Recipe | 검사할 레시피를 바꿀 때 | 검사 중에는 변경할 수 없습니다. |
| Tool > Glass Size Model / Recipe / Config | Glass 크기, 레시피, 장비 공통 설정을 변경할 때 | 변경 후에는 단일 셀/저속 검증을 권장합니다. |
| Tool > Simulation | 장비 없이 시험하거나 simulator를 전환할 때 | 최신 기준으로 PG simulation도 전역 mode입니다. 실장비 성공을 흉내내지 않습니다. |
| Tool > Export | 완료된 검사 결과를 수동 export할 때 | 검사 실행 기능이 아닙니다. 입력 결과와 대상 경로를 확인합니다. |
| View > Refresh Map | 레시피/Glass Size 변경 뒤 Main Map을 다시 볼 때 | 검사 결과를 재계산하지 않고 화면 map을 갱신합니다. |
| View > Alarm Manager | 현재/과거 알람을 확인할 때 | 알람 관리 설정과는 별도 창일 수 있습니다. |
| Test > Test Runner | Capture/Inspect, Replay, Aging, CA410 등의 시험을 실행할 때 | 양산 실행 전 장비 검증 용도로 사용합니다. |
| Test > Inspect | 저장 결과 로드, 검사 시작, Debug 실행, 화면 상태 정리에 사용 | Clear는 화면/replay 상태와 checkpoint 정리 기능입니다. |
| Test > Load/Unload Ready | Load/Unload Control flow를 단독 점검할 때 | 실제 장비 이동이 포함될 수 있으므로 안전 상태를 확인합니다. |
| Test > PG/Flow/CA410/API Test | 각 장치·통신·API를 개별 점검할 때 | 운영 중에는 사용하지 않습니다. |
| ETC > 전체 불량 오버레이 표시 | Map에서 결함 표시를 많이/적게 볼 때 | 표시 옵션입니다. 검사 결과를 바꾸지 않습니다. |

`Data` 메뉴는 현재 비어 있으며 **미구현**입니다.
