# RecipeWindow - 컨택 확인 탭 개발 노트

## 책임 경계

|계층|구성 요소|책임|
|---|---|---|
|View|`RecipeWindow.xaml`|point 편집 DataGrid와 명령 버튼을 제공한다.|
|ViewModel|`RecipeEditorViewModel`|레시피 컬렉션 동기화, 사용자 확인, 상태·로그 표시, 서비스 호출을 담당한다.|
|Recipe model|`ConsoleControlPlan.ContactCheckPoints`|`Name`, `YUm`으로 된 촬영 위치를 recipe에 보관한다.|
|Service|`ContactCheckService`|CAM3 독점 확인, 카메라 connect/grab/disconnect, Control flow·축 이동, PNG 저장을 담당한다.|
|Control|`Vars.ControlRuntime`|`FlowContactCheckReady`, `AxisMove(ContactorCameraY)`, `FlowContactCheckEnd`를 수행한다.|
|Camera|`Vars.AlignCameras`|`ContactCheckCameraName`에 해당하는 CAM3 runtime을 제공한다.|

## 데이터 구조

```csharp
ConsoleControlPlan.ContactCheckPoints : List<ConsoleContactCheckPoint>

ConsoleContactCheckPoint
├─ Name : string
└─ YUm  : double
```

공식 변경 기록상 이 구조는 과거의 단일 legacy 필드를 대체한 현재 레시피 계약이다. 자동 migration/fallback 없이 위 목록을 기준으로 사용한다.

## UI와 레시피 동기화

```text
Document.ControlPlan.ContactCheckPoints
  ↕ (Rebind / CollectionChanged)
ObservableCollection<ConsoleContactCheckPoint> ContactCheckPoints
  ↕ (ItemsSource)
DataGrid
```

`CollectionChanged`에서 `EnsureControlPlan().ContactCheckPoints = ContactCheckPoints.ToList()`로 목록을 갱신한다. rebind 시에는 문서의 point를 snapshot한 뒤 컬렉션을 비우고 다시 넣는다. 이는 `Clear()` 중 발생한 컬렉션 변경 이벤트가 빈 목록으로 문서를 덮어쓰던 회귀를 방지하는 조치다.

주의: 행 속성(`Name`, `YUm`) 편집은 컬렉션 추가/삭제 이벤트가 아니다. 현재 구현은 목록의 동일 point 객체를 model과 UI가 공유하는 방식으로 보인다. **[추론]** 레시피 저장을 수정할 때 point를 deep-copy하는 구조로 바꾼다면, 속성 변경 알림 또는 명시적 동기화도 함께 설계해야 한다.

## 실행 구현

### 수동 전체 실행

`RunContactCheckCommand`는 point 존재 여부와 사용자 확인 뒤 다음을 호출한다.

```csharp
ContactCheckService.RunAsync(
    points,
    ContactCheckService.BuildManualOutputFolderPath(),
    cancellationToken);
```

서비스 내부 순서는 아래와 같다.

```text
RunSync.WaitAsync(0)                      // 동시 실행 차단
→ Control runtime / camera 설정 / point 확인
→ CAM3 runtime IsConnected, IsGrabbing 확인
→ CAM3 ConnectAsync(useEmulationMode: false)
→ FlowContactCheckReady
→ foreach point
   → SendMoveAsync(ContactorCameraY, Abs, ContactSafeStep)
   → GrabOneAsync(timeout: 5s)
   → PNG 저장
→ finally: FlowContactCheckEnd 시도
→ finally: CAM3 DisconnectAsync 시도
→ RunSync.Release()
```

`CaptureTestImageAsync`도 같은 실행 잠금을 사용하지만, point 이동과 Control flow를 생략하고 카메라 1회 촬영만 수행한다.

### 예외·정리 규칙

- 카메라 점유, Control 미연결, camera 설정 누락, point 없음은 실행 전에 실패한다.
- 준비 flow 성공 후 point 처리 중 실패하면 이후 point 처리를 멈춘다.
- 종료 flow 전송과 카메라 disconnect는 `finally`에서 시도한다. 정리 중 오류는 원래 실행 실패를 덮어쓰지 않도록 로그로 남긴다. **[추론: 서비스의 결과 처리 구조]**
- 카메라 강제 탈취·점유 해제는 하지 않는다.

## 메인 검사 연동

공식 확정 흐름에서는 `UseContactCheck`가 켜진 glass run에서 row 컨택 성공 후 컨택 확인을 실행한다. 자동 실행의 결과 이미지는 검사 세션 `contactimages`에 저장되며, CAM3 점유를 포함한 어떤 실패도 `CON-CONTACT-CHECK-FAIL`로 run 중지 대상이다.

수동 탭 실행은 `Contact` 명령을 직접 호출하지 않는다. **[추론]** 메인 flow의 “컨택 성공 후” 보장을 수동 실행까지 확대하려면, 별도 상태 interlock 설계와 운영 승인 없이는 추가하면 안 된다.

## 코드 변경 시 지켜야 할 조건

- CAM3 점유 확인 → ready → point 이동/촬영 → end 순서를 바꾸지 않는다.
- point별 촬영 전에 이동 완료 응답을 기다리는 동기 순서를 유지한다.
- 오류가 난 뒤에도 end flow와 camera disconnect의 정리 시도를 제거하지 않는다.
- simulation에서 실카메라 성공을 가짜로 반환하지 않는다.
- `YUm`의 안전 범위는 Console 임의 기본값으로 보완하지 않는다. Control의 실제 축 한계 또는 확정된 장비 사양을 기준으로 검증을 추가해야 한다.
- model 변경 시 기존 legacy point 자동 해석이나 migration은 사용자 승인 없이 추가하지 않는다.

## 검증 체크리스트

|검증|기대 결과|
|---|---|
|현재 위치 추가|실제 `ContactorCameraY` 좌표와 `P{n}`이 새 행에 들어간다.|
|직접 행 추가|Name/YUm 입력 행이 레시피 저장·재로딩 뒤 유지된다.|
|point 없음|전체 실행이 시작되지 않고 명확한 안내가 나온다.|
|카메라 점유|강제 종료 없이 실패하고 촬영하지 않는다.|
|정상 point 2개|Ready 1회, Y 이동·촬영 2회, End 1회, PNG 2개가 생성된다.|
|두 번째 point 이동 실패|첫 오류 뒤 후속 촬영을 하지 않고 End/Disconnect를 시도한다.|
|테스트 촬영|축 이동 및 Ready/End 없이 PNG 한 장만 생성한다.|
|메인 자동 실행 실패|`CON-CONTACT-CHECK-FAIL`과 run 중지, 세션 산출물 경로가 확인된다.|

## 추가 확인이 필요한 의존성

1. Control 프로젝트의 `FlowContactCheckReady`/`FlowContactCheckEnd`가 실제로 제어하는 IO·interlock.
2. `ContactorCameraY`의 soft limit, 단위, 컨택 중 허용 위치 범위.
3. 메인 검사 run에서 `UseContactCheck`가 `ContactCheckService`에 전달되는 정확한 호출부와 cancellation 전파.
4. 생산 품질 기준의 정상/불량 컨택 이미지 판정 기준.

## 관련 파일

- `uLedAoiConsole/Windows/Recipe/RecipeWindow.xaml`
- `uLedAoiConsole/ViewModels/RecipeEditorViewModel.cs`
- `uLedAoiConsole/Services/ContactCheckService.cs`
- `uLedAoiConsole/Models/Recipe/ConsoleControlPlan.cs`
- `docs/axis-system-structure.md`
- `docs/alarm-policy.md`
- `docs/development/change-log.md`
