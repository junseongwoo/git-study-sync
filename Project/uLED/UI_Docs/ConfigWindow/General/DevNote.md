# ConfigWindow - General 탭 개발 노트

## 모델 및 바인딩

`ConfigViewModel`은 `Vars.EMRConfigStore`의 `DataStore<ULedConfig>`를 사용한다. General 탭의 대부분은 `Config` 속성에 직접 two-way binding하며, 일부 수치는 ViewModel wrapper를 거친다.

|UI|Model / wrapper|보정 규칙|
|---|---|---|
|Partition overlay, Ingress, Show Angle|`ULedConfig` direct|없음|
|Lot/Glass/Output Root|`ULedConfig` direct|Output Root는 trim|
|Inline Crop Max|`MaxInlineCropImageCount`|0~1000 clamp|
|Find Pitch Min/Max|`FindPitchMinDistancePx`, `FindPitchMaxDistancePx`|min≥0, max>min|
|Find Pitch margins|wrapper|각각 ≥0|

## 저장 흐름

```text
SaveWithChangeReport
→ Ensure*/Sync* 정규화
→ ObjectChangeTracker diff
→ 사용자 확인
→ CreateConfigBackup
→ Config.Version = VersionStamp.Next
→ DataStore.Save
→ tracker reset / 변경 로그
→ EEC Light, IP runtime, Light runtime 일부 Reconfigure
```

backup은 기존 config 파일이 존재할 때만 만들며 최대 30개로 prune한다. General 표시·검사 옵션 변경에 대해 Save 후 모든 runtime이 즉시 재구성된다고 가정하면 안 된다. 저장 코드에서 명시적으로 Reconfigure하는 것은 EEC light/IP endpoint/LightConfig이다.

## 하류 의존성

|설정|소비처|
|---|---|
|`ShowGlassMapPartitionNameOverlay`|RecipeWindow의 `GlassMapControl.ShowPartitionNameOverlay` binding|
|`GlassIngressDirection`|RecipeWindow `GlassMapControl.IngressDirection`, GlassMap ingress arrow|
|`SaveOriginalImages`|검사 run 원본 저장 정책의 기본값/실행 옵션|
|`OriginalImageOutputRootFolder`|Console run output root, IP 원본 저장 절대 경로 전달|
|`MaxInlineCropImageCount`|IP artifact 결과의 crop 생성/inline 포함 상한|
|`FindPitch`|현재 buffer Find Pitch의 object 거리 필터, search/result ROI margin|
|`LotId`, `GlassId`|검사 run 기본 식별자 및 output 경로 구성|

## 불변 조건

- thumbnail/artifact 생성자는 IP `InspectionResultArtifactBuilder` 하나다. Config General을 이유로 Console에서 crop/thumbnail 재인코딩을 추가하지 않는다.
- `MaxInlineCropImageCount = 0`이면 crop 생성 자체를 건너뛴다.
- General의 Glass Map View 설정과 GlassSize의 `PanelAngleDeg`/naming policy 책임을 혼동하지 않는다.
- 원본 저장 경로는 Console이 run folder를 정하고 IP에 절대 경로를 전달한다.

## 검증 체크리스트

|변경|검증|
|---|---|
|overlay on/off|Cell Map 분판 이름 overlay 즉시/재진입 표시 확인|
|ingress direction|화살표 방향과 PanelAngle 조합 확인|
|Save Original/NAS root|run folder 생성·IP 저장·권한·NAS 지연·buffer alarm 확인|
|inline crop 0/소수/다수|완료 이벤트 crop 개수 및 IP artifact 생성 정책 확인|
|Find Pitch min/max/margin|fixture/current-buffer에서 후보·ROI 결과 비교|
|Save/Reload|diff 취소 시 파일 미변경, backup/version/save, reload 시 UI·일부 runtime 갱신 확인|

## 추가 추적 대상

1. `ShowGlassAngle`의 정확한 소비처와 현장 사용 여부.
2. run dialog/TestRunner의 SaveOriginalImages가 General 값과 충돌할 때의 우선순위.
3. NAS root의 directory create·권한 실패 시 run 차단/경고 처리.
4. Find Pitch service가 Config 값을 snapshot하는 시점.

## 관련 파일

- `uLedAoiConsole/Windows/Core/ConfigWindow.xaml`
- `uLedAoiConsole/Windows/Core/ConfigWindow.xaml.cs`
- `uLedAoiConsole/ViewModels/ConfigViewModel.cs`
- `uLedAoiConsole/Models/ULedSettings.cs`
- `uLedAoiConsole/Controls/GlassMapControl.cs`
- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml`
