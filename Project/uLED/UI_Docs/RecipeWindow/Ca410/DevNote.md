# RecipeWindow / CA410 탭 인수인계 노트

## 모델과 저장

- UI 컬렉션: `Ca410InspectionPatterns : ObservableCollection<ConsoleCa410InspectionPattern>`
- 선택 Pattern: `SelectedCa410InspectionPattern`
- 선택 Step 목록: `SelectedCa410VoltageSteps`
- 선택 Step: `SelectedCa410VoltageStep`
- 저장 대상: `Document.Ca410Plan.Patterns`
- 측정 결과: `Ca410TestResults : ObservableCollection<Ca410TestResultViewModel>`

CA410 조건은 `IpRecipe.Patterns`에 넣지 않는다. IP runtime recipe와 Console의 `Ca410Plan`은 의도적으로 분리된다.

## 실행 제어

- 실행 중 상태: `IsCa410TestRunning`
- 취소: `_ca410TestCts`와 `StopCa410TestCommand`
- `Run Selected` 가능 조건: 선택 Pattern이 있고 실행 중이 아님
- `Run All Used` 가능 조건: `Use=true` Pattern 안에 `Use=true` Step이 하나 이상 있고 실행 중이 아님
- `Clear` 가능 조건: 결과가 있고 실행 중이 아님

`RunCa410PatternsAsync`는 PatternOrder/StepNo로 정렬한 Step들을 순차 실행한다. 동시 실행으로 바꾸면 CA410의 요청-응답 직렬 규칙을 위반할 수 있다.

## PG/CA410 연동

- `ApplySelectedCa410StepLightingAsync`가 선택 PG runtime에 연결해 Pattern 선택과 R/G/B voltage sweep을 수행한다.
- `BuildCa410PatternVoltages`는 Config의 EEC-P725R2 R/G/B `VoltageChannelIndex`를 사용해야 한다. 채널 인덱스를 레시피에 복제하지 않는다.
- CA410 측정 client는 TCP 또는 Serial 연결을 사용하며, CA410 프로토콜 명령은 직렬화된다.
- 측정 결과에는 CA410 record와 별도로 `ReadSelectedPgElvddCurrentAsync`의 ELVDD 값을 넣는다.

## Result Window

- `Ca410ResultWindow`는 부모와 동일 ViewModel을 DataContext로 공유한다.
- 창 닫기는 test cancel을 자동 호출하지 않는다. 실행 제어는 ViewModel의 Stop 명령이 소유한다.
- `ExportCa410Results`는 사용자가 지정한 CSV에 모든 결과를 PatternOrder → StepNo → MeasuredAt 순으로 기록한다.

## 검증 체크리스트

- PatternOrder와 StepNo 중복/범위(1~30)를 Validate에서 실제로 막는지 확인한다.
- PG voltage 입력이 signed 2-byte millivolt 범위를 넘었을 때 명확히 실패하는지 확인한다.
- Result Window 실행 전에 선택 셀과 CA410 XY 위치가 보장되는지 확인한다.
- CA410 `DisplayMode`가 `XyLv`가 아닐 때 ca_x/ca_y/Lv가 null로 남는 현재 코드 동작을 UI/CSV 사용자에게 명확히 안내하는지 확인한다.
- 일부 실패 시 Error/Message와 남은 값이 의도대로 CSV에 기록되는지 확인한다.

## 공식 문서/코드 차이

- 공식 문서는 CA410 Step에 PG Pattern `1`을 고정해 설명하지만, 현재 코드는 `ResolveRecipePatternNo()`로 recipe의 PatternNo를 사용한다.
- 공식 자동 검사 흐름은 셀 중심 이동을 포함한다. Result Window의 반복 코드는 CA410 Z 확보를 수행하지만 XY는 상위 flow 또는 별도 `CA410 이동` 명령에 의존한다.

## 추가 확인 대상

- `ConsoleCa410Plan` / `ConsoleCa410VoltageStep` validation: 순서·전압 범위 검증의 실제 구현
- `BuildCa410PatternVoltages`: display black/white voltage, R/G/B voltage channel mapping
- `MeasureCa410RecordAsync` / `Ca410MeasurementOptions`: display mode, sync, timeout, probe 선택
- `GlassInspectionStepPreparationService`: 자동 검사에서 CA410 이동·측정·CSV 저장의 전체 경로

[추론] 현재 Result Window는 recipe 작성 단계의 장비 검증·전압 sweep 시험 용도이며, 생산 자동 검사에서는 별도 MainFlow가 같은 `Ca410Plan`을 소비하는 구조로 보인다.
