# RecipeWindow / 명점 검사(WD) 탭 인수인계 노트

## XAML 바인딩

이 탭의 직접 편집 대상은 다음 다섯 값뿐이다.

| XAML Binding | 의미 |
|---|---|
| `Document.IpRecipe.WhiteDefect.ThresholdPercent` | 명점 임계값 |
| `Document.IpRecipe.WhiteDefect.RgbPhaseOffsets.GFromR.Dx` | R→G X offset |
| `Document.IpRecipe.WhiteDefect.RgbPhaseOffsets.GFromR.Dy` | R→G Y offset |
| `Document.IpRecipe.WhiteDefect.RgbPhaseOffsets.BFromR.Dx` | R→B X offset |
| `Document.IpRecipe.WhiteDefect.RgbPhaseOffsets.BFromR.Dy` | R→B Y offset |

모든 수치 입력은 `NumericTextConverter`와 `UpdateSourceTrigger=LostFocus`를 사용한다.

## 결과 계약

- IP의 최종 결과에는 `WdDefects` 컬렉션이 있다.
- 탭이 안내하는 결과 필드는 `channel`, `type`, `x`, `y`, `level`이다.
- IP/algorithm 내부와 통신 계약은 dot 단위 IP index를 유지한다.
- Console/Verifier는 GlassSize의 `DotIndexOrigin`, `DotIndexBase`, `DotIndexSwapXY` 설정을 사용해 최종 `row/column`으로 변환한다.

## 표준맵/FindPitch 연결

- `FindPitchCurrentBufferCommand`는 RecipeWindow의 IP 메뉴에서 노출된다.
- `FindPitchCurrentBufferAsync`는 현재 buffer를 IP에 분석 요청하고 결과 창을 표시한다.
- 결과 창 선택에 따라 pitch, phase offset, ROI를 recipe에 적용할 수 있다.
- 표준맵 생성 흐름은 `CreateStandardMapForCellAsync`와 연결되며, 생성 후 `Document.StandardMapPlan.UseStandardDenseMap`을 활성화할 수 있다.
- 이 탭에는 `UseStandardDenseMap` 또는 표준맵 경로를 직접 편집하는 control이 없다.

## 공식 문서 우선 사항

- 운영 본검사의 기본 경로는 표준맵 검사다.
- 표준맵은 R 좌표를 저장하며 G/B는 recipe의 phase offset으로 파생한다.
- 표준맵 검사 실패 시 자동정합이 폴백한다.
- 맵 좌표가 확정되면 세 채널의 레벨은 확정 좌표에서 샘플링한다.

## 유지보수 주의

- 결과 안내의 `x/y`를 UI/CSV의 `row/column`과 혼용하지 않는다.
- WD 탭의 설정 변경이 `RecipeModel` JSON 및 IP metadata 전달에 실제 반영되는지, 업로드 경로 변경 시 함께 확인한다.
- 표준맵 사용 여부/경로 UI를 이 탭에 추가하려면 `StandardMapPlan`과 `WhiteDefect`의 책임을 섞지 않고, 공식 문서의 표준맵 생성·검사 흐름과 맞춰 설계한다.

## 추가 확인 대상

- WhiteDefect 검사 알고리즘 및 `WhiteDefectResultModel`: threshold의 판정식과 WVL/WHL 생성 조건
- `FindPitchResultWindow`와 `ApplyFindPitchResult(...)`: Dx/Dy 단위와 recipe 반영 범위
- `ConsoleRecipeDocument.StandardMapPlan`: 표준맵 경로·사용 여부의 저장/업로드 규칙

[추론] WD 탭은 `WhiteDefect`의 최소 조정값만 노출하고, 표준맵 운용은 별도 분석 결과 창으로 분리해 일반 사용자가 표준맵 파일 경로를 직접 변경하지 않도록 한 구조로 보인다.
