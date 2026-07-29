# ConfigWindow - Motion / Coordinate 탭 개발 노트

## 모델 구조

```text
ULedConfig
├─ Control: IpAddress, Port
├─ MinSafeGlassYGapUm
└─ UvwCoordinateSystem
   ├─ UseAutoCalculation
   ├─ PositiveThetaDirection
   ├─ GlassPlacement
   │  ├─ ReferenceGlassWidthUm / HeightUm
   │  ├─ GlassMinusXEdgeStageXUm
   │  └─ GlassCenterStageYUm
   └─ UvwGeometry
      └─ U/V/W: TranslationAxis, AxisLineStageXUm, AxisLineStageYUm
```

## Runtime UVW 계산

`UvwParameterResolver.Resolve(coordinateSystem, glassSizeModel, fallback)`가 effective parameter를 만든다.

```text
UseAutoCalculation=true
  → current GlassSize width/height와 PanelAngle 사용
  → stage center 계산
  → U/V/W 각 axis의 direction + line raw geometry로 PerX/PerY/Rotation 계산
  → CCW이면 RotationPerThetaRad 부호 반전

UseAutoCalculation=false
  → fallback AlignUvw.ToParameters()
```

자동 계산은 GlassSize의 유효 크기를 우선하고, 없거나 0이면 ReferenceGlass W/H를 fallback한다. 이는 현재 코드 사실이며, “GlassSize가 없으면 정직하게 실패”라는 recipe 모델 정본 원칙과 충돌 가능성이 있다. **문서/코드 차이**로 취급하고 신규 코드에서 fallback 확대를 추가하지 않는다.

## 공식 계산 기준

공식 UVW calibration standard:

```text
centerX = GlassMinusXEdgeStageXUm + GlassWidthUm / 2
centerY = GlassCenterStageYUm
```

현재 resolver는 90/270° panel angle에서 `GlassHeightUm / 2`를 stage X span으로 사용한다. 이는 sideways placement의 stage footprint 보정이다.

direction별 parameter:

|Direction|PerX|PerY|Rotation 기준|
|---|---:|---:|---|
|PlusX|+1|0|AxisLineY - centerY|
|MinusX|-1|0|centerY - AxisLineY|
|PlusY|0|+1|centerX - AxisLineX|
|MinusY|0|-1|AxisLineX - centerX|

## Safe gap 의존성

`MinSafeGlassYGapUm`은 `RecipeService`의 auto IP assignment 및 glass inspection batch 계획에서 사용한다. panel angle을 반영한 stage 방향 center를 비교하고, 조건 미달 pair는 동시 batch 대신 단독 step으로 나눈다.

이 값은 safety rule이므로 `0` 또는 작은 테스트값으로 보정하지 않는다. ConfigViewModel setter는 0 이상을 허용하지만, XAML은 minimum 1이며 공식 기본값은 300,000 µm다.

## Control endpoint 적용 경계

Config save는 Control endpoint reconfigure를 직접 수행하지 않는다. endpoint 결정·simulation 모드 분기는 `MainWindowViewModel.ApplyControlEndpointForCurrentMode` 단일 지점이어야 한다. 이 탭에서 endpoint 변경 기능을 확장할 때 `Vars.ControlRuntime.ApplyConfig` 직접 호출을 추가하면 connection monitor가 endpoint를 되돌리는 회귀 위험이 있다.

## 검증

|시나리오|기대 결과|
|---|---|
|Control endpoint 변경|재연결 뒤 새 host status 수신, simulation/실장비 endpoint 분리 유지|
|gap 경계 pair|gap 미만은 단독, 이상은 동시 batch|
|90/270 PanelAngle|stage X center가 height 기반으로 계산|
|각 Direction|effective PerX/PerY가 표와 일치|
|CW/CCW|rotation coefficient 부호만 반전|
|axis line 변경|병진 PerX/PerY는 유지, theta rotation coefficient 변경|
|UseAuto=false|fallback path 사용 사실 확인 및 production 사용 금지 검토|
|jog|+X/+Y/+Theta 물리 방향·align correction 수렴 확인|

## 관련 파일

- `uLedAoiConsole/Windows/Core/ConfigWindow.xaml`
- `uLedAoiConsole/ViewModels/ConfigViewModel.cs`
- `uLedAoiConsole/Models/ULedSettings.cs`
- `uLedAoiConsole/Services/Coordinates/UvwParameterResolver.cs`
- `uLedAoiConsole/Recipes/RecipeService.cs`
- `uLedAoiConsole/ViewModels/MainWindowViewModel.cs`
- `docs/uvw-coordinate-calibration-standard.md`
- `docs/main-glass-inspection-flow.md`
