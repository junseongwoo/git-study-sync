# RecipeWindow - 에이징 탭 개발 노트

## 1. 문서 우선순위와 분석 경계

확인한 상위 공식 문서는 Console이 상위 recipe와 실행 orchestration을 소유하는 구조를 설명하지만, AgingPlan의 실행 계약·PG pattern 제어·checkpoint 재개 정책은 별도로 규정하지 않는다. 그러므로 이 문서의 구현 설명은 모두 **[추론: 현행 코드 기준]** 이며, 공식 에이징 문서가 추가되면 그 문서를 우선 적용해야 한다.

## 2. 책임 분리

| 계층 | 파일/형식 | 책임 |
|---|---|---|
| UI | `RecipeWindow.xaml` | step 편집 표와 테스트 진입점 제공 |
| 편집 VM | `RecipeEditorViewModel` | 컬렉션 편집, document 동기화, 선택 cell PG 해석, 테스트 수명 관리 |
| recipe 모델 | `ConsoleRecipeDocument.cs` | `ConsoleAgingPlan`, `ConsoleAgingStep` 영속 구조 정의 |
| 실행 서비스 | `AgingSequenceRunner` | step 검증/실행, runtime 획득, 취소·실패 처리 |
| 저장소 | `AgingCheckpointStore` | 실행 checkpoint JSON의 load/save/delete |
| 진행 VM/UI | `AgingProgressViewModel`, `AgingProgressWindow` | snapshot을 진행 상태 화면으로 투영 |

## 3. 모델 및 상태

**[추론]** 편집 모델은 `ConsoleAgingPlan.Steps : List<ConsoleAgingStep>`이고, 실행 시 `AgingExecutionStep`으로 변환한다. 실행 상태는 `Pending`, `Running`, `Completed`, `Skipped`, `Canceled`, `Failed`다.

`AgingExecutionCheckpoint`에는 run ID, recipe path, PG index, 시작/저장 시각, 실행 step 상태를 보관한다. 기본 checkpoint 위치는 `Vars.RuntimeDir\aging-checkpoint.json`이다.

## 4. 코드 진행 상세

### 4.1 편집 → Document 반영

**[추론]**

- `AddAgingStep`은 목록의 최대 step 번호 다음 값을 사용한다.
- `RemoveSelectedAgingStep`/`ClearAgingSteps`는 confirmation 이후 컬렉션을 변경한다.
- `SyncCollectionsToDocument`는 `AgingSteps`를 `StepNo` 순으로 `Document.AgingPlan.Steps`에 반영한다.
- `RebindCollections`는 컬렉션 clear 과정의 변경 이벤트가 document의 원본 list를 빈 목록으로 덮어쓰지 않도록, 기존 step을 먼저 별도 목록으로 확보한 후 다시 바인딩한다.

이 보호 로직을 제거하거나 순서를 바꾸면 recipe load/rebind 도중 AgingPlan이 비어 저장될 위험이 있다. **[추론]**

### 4.2 테스트 시작

**[추론: `TestAgingPlanAsync`]**

1. `ResolveSelectedCellPgIndex` 전에 PG mapping을 document에 동기화한다.
2. 선택 cell의 `YIndex`로 PG index를 해석한다.
3. 현재 step 목록을 document에 반영하고 recipe path를 수집한다.
4. `_agingTestCts`를 새 linked CTS로 교체한다.
5. `AgingProgressViewModel.ConfigureStopHandler`에 CTS 취소 동작을 연결한다.
6. progress 창을 표시하고 `AgingSequenceRunner.RunAsync`에 `IProgress<AgingProgressSnapshot>`을 전달한다.
7. completion/cancellation/error를 각기 `MarkCompleted`/`MarkCanceled`/`MarkFailed`와 로그/상태 메시지로 반영한다.

### 4.3 runner 실행 불변 흐름

**[추론: `AgingSequenceRunner`]**

```text
Use step 필터링·StepNo 정렬
  → 유효성 검증
  → 동일 recipe path + PG index checkpoint 적용
  → PG runtime 획득
  → step별 pattern 선택 또는 소등
  → 매초 checkpoint 저장 + progress 보고
  → 공통 안전 소등
  → 완료 시 checkpoint 삭제 / 취소·실패 시 checkpoint 유지
```

검증은 실행 대상이 비었는지, `StepNo` 중복, duration 1초 미만, PatternOn의 pattern 1~25 범위를 차단한다. `OffWait`는 `TurnOffAsync`를 호출하므로 pattern 값의 범위를 검사하지 않는다.

`PatternOn`은 `ExecuteWithNewConnectionAsync` 범위에서 `SelectPatternAsync`를 호출한다. PG driver의 최종 점등/상태 보장은 이 호출부만으로 확정할 수 없으므로, 장비 계약 문서 또는 driver 구현을 확인하지 않은 이상 ‘선택 요청’으로 기술한다. **[추론]**

## 5. 취소 및 예외 안전성

**[추론]**

- 취소: Running/Pending step을 `Canceled`으로 바꾸고 checkpoint 저장 후 `TurnOffSafeAsync`를 호출한다.
- 실패: Running step을 `Failed`로 바꾸고 checkpoint 저장 후 `TurnOffSafeAsync`를 호출한다.
- 정상: `TurnOffSafeAsync` 후 checkpoint를 삭제한다.
- `TurnOffSafeAsync`의 자체 실패는 로그만 남기고 원래 흐름을 가리지 않도록 처리한다.

이 구조에서 progress 창의 Closing 이벤트는 PG 소등이나 CTS 취소를 호출하지 않는다. 창을 닫아도 runner가 살아 있을 수 있으므로, 창 닫기를 취소 의미로 바꾸려면 명시적 사용자 요구와 종료 UX/안전 정책 확정이 필요하다.

## 6. 재개 정책의 현재 의미

**[추론]** checkpoint는 PG index와 recipe path가 둘 다 일치할 때만 적용한다. 완료 step만 복원하며, 실행 중이던 step은 부분 시간을 복구하지 않고 다시 수행한다. 모든 step이 완료된 checkpoint를 다시 열면 전체를 Pending으로 초기화하여 새 run으로 처리한다.

이 정책은 code fallback/legacy 호환이 아니라 현 구현 자체의 재실행 규칙이다. recipe 경로 변경, 다른 PG 선택, 또는 운영상 recipe 내용을 같은 경로에서 수정한 경우의 식별 정책은 별도의 공식 결정이 필요하다.

## 7. UI/코드 불일치 및 변경 주의

| 항목 | 현 상태 | 변경 시 주의 |
|---|---|---|
| 기본 RGB 추가 | `AddDefaultAgingRgbCommand`는 VM에 있으나 탭 XAML 버튼은 없음 | 노출할 경우 사용자에게 기존 step에 append되는 동작과 pattern 번호의 장비 의미를 명확히 안내해야 함 |
| 창 닫기 | progress 창 닫기는 취소하지 않음 | 닫기=중단으로 바꾸려면 소등 완료/CTS 완료까지의 UX를 설계해야 함 |
| checkpoint | 단일 `aging-checkpoint.json` | 동시 다중 PG/다중 run 지원 시 file key 및 run 소유권 설계가 필요함 |
| PG runtime | 전역 runtime/Simulation Mode를 사용 | 에이징 전용 private simulator를 도입하지 말고 공통 runtime 정책과 정합성을 유지해야 함 |

## 8. 권장 검증 항목

다음은 코드 변경 시 확인할 항목이다. **[추론]**

1. 빈 step, 선택 cell 없음, 중복 step 번호, 0초 duration, PatternOn pattern 0/26이 각각 올바르게 차단되는지 확인한다.
2. PatternOn → OffWait → PatternOn 순서에서 PG 호출과 progress 상태가 step 순서와 일치하는지 로그로 확인한다.
3. Stop 시 checkpoint가 남고 PG 안전 소등이 시도되는지 확인한다.
4. 같은 recipe path/PG에서 재시작 시 완료 step만 skip되는지, 진행 중이던 step은 처음부터 실행되는지 확인한다.
5. 정상 완료 시 checkpoint가 삭제되는지 확인한다.
6. 진행 창을 닫아도 실제 실행은 계속되는 현 동작을 검증하고, 운영 UX와 일치하는지 확인한다.
7. Simulation Mode와 실장치 mode 모두에서 runtime endpoint 선택이 공통 정책대로 적용되는지 확인한다.

## 9. 관련 소스

- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml`
- `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`
- `uLedAoiConsole/Recipes/ConsoleRecipeDocument.cs`
- `uLedAoiConsole/Services/Aging/AgingExecutionModels.cs`
- `uLedAoiConsole/Services/Aging/AgingSequenceRunner.cs`
- `uLedAoiConsole/Services/Aging/AgingCheckpointStore.cs`
- `uLedAoiConsole/ViewModels/AgingProgressViewModel.cs`
- `uLedAoiConsole/Windows/Core/AgingProgressWindow.xaml`
- `uLedAoiConsole/Windows/Core/AgingProgressWindow.xaml.cs`
