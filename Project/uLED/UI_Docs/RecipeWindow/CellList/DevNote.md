# RecipeWindow - 셀 목록 탭 인수인계 노트

## 1. 핵심 클래스와 의존 관계

| 계층 | 클래스/파일 | 책임 |
|---|---|---|
| 화면 | `RecipeWindow.xaml` | 셀 목록 DataGrid와 command binding 선언 |
| ViewModel | `RecipeEditorViewModel` | UI collection, 확인 대화상자, service 호출, preview/모션 표시 갱신 |
| recipe 모델 | `ConsoleRecipeDocument`, `ConsoleGlassMapPlan`, `ConsoleCellPlan` | Cell, split, 글래스 map, IP 담당 데이터 저장 |
| recipe service | `RecipeService` | Cell 재생성, X/Y index 부여, 자동/수동 IP 분배 |
| 좌표 변환 | `CoordinateTransformService`, `BridgeCalibration` | 글래스 중심 → StageX/Y1/Y2 변환 |
| 설정 | `ULedConfig.MinSafeGlassYGapUm`, GlassSize model | 자동 split의 안전거리와 calibration 입력 |

## 2. 중점 기능의 호출 관계

### IP 자동 할당

```text
AutoAssignIpToCellsCommand
  → RecipeEditorViewModel.AutoAssignIpToCells
  → SyncCollectionsToDocument
  → RecipeService.AutoAssignIpNumbers(Document)
  → RebindCollections + RefreshPreview
```

공식 규칙: YIndex 기준, 안전거리 기준, 균등 split 우선, 안전 split 불가 시 단일 IP.

**[추론: 구현 상세]** `AutoAssignIpNumbers`는 각 YIndex 그룹의 stage Y 방향 글래스 중심 평균을 구하고, 절반에 가까운 split 후보부터 안전한 후보를 찾는다. 성공 시 앞쪽 그룹은 IP1, 나머지는 IP2이며 반환된 IP1 그룹 수를 `IpSplitColumn`에 저장한다.

### 수동 분할 적용

```text
ApplyIpSplitColumnCommand
  → RecipeEditorViewModel.ApplyIpSplitColumn
  → SyncCollectionsToDocument
  → RecipeService.AssignIpNumbersBySplitColumn(Document, split)
  → RebindCollections + RefreshPreview
```

**[추론]** 수동 split은 고유 YIndex를 정렬한 뒤 순번으로 나눈다. `IpSplitColumn`은 값 비교 경계가 아니라 IP1에 배정할 앞쪽 그룹 개수다. 이 경로는 `MinSafeGlassYGapUm` 안전성을 검사하지 않는다.

### 좌표 재계산

```text
RefreshCellMotionTargetsCommand
  → RefreshCellMotionTargets
  → SyncCellMapCorrectionRows
  → TryBuildBridgeCalibration
  → TryResolveCellMotionTarget (각 Cell)
  → MotionStageX / MotionY1 / MotionY2 갱신
```

**[추론]** 계산은 Cell 중심 글래스 좌표, IP별 bridge, 선택 도구 offset, affine transform, CellMap correction을 사용한다. `IpNo`가 1/2가 아니거나 calibration 생성이 실패하면 대상 계산이 실패한다. 전체 calibration 생성 실패 시 모든 표시는 0으로 초기화한다.

## 3. DataGrid 바인딩 유의사항

| 항목 | 내용 |
|---|---|
| 목록 source | `ObservableCollection<ConsoleCellPlan> Cells` |
| 선택 source | `SelectedCell` |
| 읽기 전용 | `XIndex`, `YIndex`, `MotionStageX`, `MotionY1`, `MotionY2` |
| 즉시 입력 반영 | CellId/Name/UserDefinedName/IpNo/X/Y 및 `IpSplitColumn`은 `UpdateSourceTrigger=PropertyChanged`를 사용 |
| service 변경 후 | `RebindCollections()`로 document의 변경 결과를 UI에 재연결 |

**[추론]** 개별 `ConsoleCellPlan`의 property change 통지 구현 여부와 변경 시 자동 저장 여부는 모델 구현 및 저장 command를 추가 확인해야 한다. UI edit가 document save까지 이어지는 정확한 시점은 `SyncCollectionsToDocument` 호출 위치와 저장 흐름을 함께 점검한다.

## 4. 공식 문서 대비 구현 확인 사항

| 항목 | 공식 문서 | 현 코드 |
|---|---|---|
| YIndex | IP 분배·Split·PG mapping 기준 | 동일하게 YIndex group 기반으로 구현 |
| 자동 분배 | 안전거리 고려, 안전하지 않으면 단일 IP | `ResolveSafeIpSplitColumn`으로 구현 |
| 수동 split | IpSplitColumn이 YIndex 기준 | 구현은 정렬된 고유 YIndex의 **순번**으로 배정 — 세부 해석은 **[추론]** |
| Cell 재생성 | 기존 Use/IpNo/RoundCell/UserDefinedName 보존, index 재계산 | `RegenerateCellsFromSnapshot(... preserveExistingValues:true)`가 이를 호출 |
| 좌표 재계산 | 별도 공식 규정 없음 | 표시용 motion target 재계산으로 구현 — **[추론]** |

## 5. 확인된 좌표 계산식

`CoordinateTransformService` 기준으로 `CellRectGlassUm`은 글래스 중심 `(0,0)`, +Y 위 기준의 좌상단 사각형 좌표다.

```text
CellRect.X = CornerRect.X - GlassWidth / 2
CellRect.Y = GlassHeight / 2 - CornerRect.Y
CellCenter = (CellRect.X + Width / 2, CellRect.Y - Height / 2)
```

`ToBridgeAxes`는 Glass 중심 `(gx, gy)`를 다음 affine 식으로 축 좌표로 바꾼다.

```text
UnitYBase = AxisXCoeffX*gx + AxisXCoeffY*gy + AxisXOffset
StageXBase = AxisYCoeffX*gx + AxisYCoeffY*gy + AxisYOffset
```

그 후 `ResolveToolAxisTarget`은 선택 도구 offset을 빼고, `ApplyCellMapCorrection`은 `YIndex` 기반 UnitY 보정과 `XIndex` 기반 StageX 보정을 더한다. IP1은 결과 UnitY를 Y1에, IP2는 Y2에 기록하고 반대편 축은 EscapeY로 둔다. 표시값은 현재 선택 이동 도구(검사 카메라/CA410/Align 카메라)의 offset을 사용한다. **[추론: UI의 MotionStageX/Y1/Y2 구성 경로]**

## 6. 추가 확인 필요 항목

1. `RecipeWindow.xaml.cs`에 DataGrid selection 또는 저장과 관련된 code-behind가 추가로 있는지 확인한다.
2. `ConsoleCellPlan`의 `INotifyPropertyChanged` 구현 및 `MotionStageX/Y1/Y2`의 영속 여부를 확인한다.
3. `SyncCollectionsToDocument`와 recipe Save command의 호출 순서를 확인해 수동 DataGrid 편집의 저장 보장을 확정한다.
4. `CoordinateTransformService.BuildBridgeCalibration`의 source 우선순위와 GlassSize validation 오류 조건을 확인한다.
5. `CellMapCorrectionPlan`의 UI 편집 탭과 보정값 단위(um/px 표시 전환)를 확인한다.
6. 현장 `MinSafeGlassYGapUm` 설정값과, 수동 분할 사용을 허용하는 운영 승인 절차를 확인한다.
7. Auto Assign이 `Use=false` Cell도 포함하는 현 동작이 운영 요구와 일치하는지 확인한다. **[추론: 코드상 모든 Cells를 group화]**

## 7. 변경 시 검증 체크리스트

1. Cell map 재생성 후 기존 Use/IpNo/사용자명 보존과 XIndex/YIndex 재계산을 확인한다.
2. 안전한 split과 안전하지 않은 split 각각에서 Auto Assign 결과 및 `IpSplitColumn` 값을 확인한다.
3. 수동 split에서 비연속 YIndex(예: 0,2,4)로 순번 분할이 예상대로 작동하는지 확인한다.
4. IP1/IP2가 아닌 IpNo에서 선택 Cell 이동과 좌표 계산이 안전하게 실패하는지 확인한다.
5. GlassSize/calibration 정상·오류 상태에서 StageX/Y1/Y2 갱신값을 확인한다.
6. XIndex/YIndex 보정이 각각 StageX/UnitY 축에 적용되는지 확인한다.
7. DataGrid 값 변경 후 저장·다시 열기 시 값이 유지되는지 확인한다.
