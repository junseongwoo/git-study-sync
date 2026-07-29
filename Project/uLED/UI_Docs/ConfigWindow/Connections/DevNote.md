# ConfigWindow - Connections 탭 개발 노트

## 의존 관계

```text
ConfigWindow.xaml
  → ConfigViewModel
      → ULedConfig (YAML store)
          ├─ IpEndpoints → ULedIpRuntimeRegistry.Reconfigure
          ├─ Ca410.Devices / timeout → Ca410MeasurementOptions
          └─ LightConfig → LightRuntime.ApplyConfig
```

## 구현 확인 사항

- `IpEndpointItems`, `Ca410DeviceItems`는 편집용 `ObservableCollection`이며 저장 때 설정 List로 동기화된다.
- Save는 backup을 만든 뒤 설정을 저장하고, IP runtime과 Light runtime을 재구성한다.
- IP port의 유효 범위는 1~65535이며 기본은 `5002 + No`다. 기본 2개는 5003/5004다.
- CA410은 `Ca410Config.ToMeasurementOptions`에서 RS232C 연결로 고정되며, simulator 여부는 전역 `Vars.IsCa410SimulationMode`가 결정한다.
- CA410 Remote mode는 설정 UI가 아니라 앱 시작/종료 생명주기에서 관리한다. 코드 주석 기준으로 시작 시 remote on 및 display mode 설정, 종료 시 remote off를 수행한다.
- `LightRuntime.ApplyConfig`는 열린 포트를 닫고 PortName/BaudRate/DataBits를 적용한다. parity=None, stopBits=One, read/write timeout=1000은 코드 고정이다.

## 공식 문서 우선 기준

- `automation-api.md`: 포트 예약은 Control Host 5001, Control Simulator 5002, IP 5003/5004, Automation 5006.
- `main-glass-inspection-flow.md`: IP step 입력은 sync, 검사 결과는 `EvtJobCompleted` 비동기 수신.
- `ca410-ethernet-protocol.md`: RS232C는 Ethernet frame header 없이 ASCII command text를 사용하며 요청은 직렬화한다.
- `ca410-inspection-flow.md`: CA410 측정은 IP 검사와 별개의 Console 소유 공정이다.

## 확인 필요 / 잠재 리스크

1. CA410 DataGrid는 행 추가가 불가하나 save 후 empty 목록에는 기본 2개를 복원한다. 운영상 장치 수 변경 요구가 있으면 UI 정책을 명확히 해야 한다.
2. CA410 장치 선택이 `No`, `Name`, `AlignCameraName` 중 어느 값으로 이루어지는지 CA410 runner에서 추적한다.
3. Config Save/Reload 시 CA410 연결에 즉시 적용되는지 또는 다음 측정에서 적용되는지 확인한다.
4. IP Enabled=false endpoint의 제외·재할당 정책을 `ULedIpRuntimeRegistry`에서 확인한다.
5. `CalcTextBox`의 `UpdateSourceTrigger=Explicit`이 Save 전에 값 commit을 보장하는지 UI 테스트가 필요하다.
6. LightRuntime RS232C와 EEC-P725R2 PG runtime의 기능 경계를 사용자 문서와 UI 라벨에서 더 분명히 하는 것이 좋다. **[추론]**

## 주요 소스

- `uLedAoiConsole/Windows/Core/ConfigWindow.xaml`
- `uLedAoiConsole/ViewModels/ConfigViewModel.cs`
- `uLedAoiConsole/Models/ULedSettings.cs`
- `uLedAoiConsole/App.xaml.cs`
- `uLedAoiConsole/Services/LightRuntime.cs`
- `docs/automation-api.md`
- `docs/ca410-ethernet-protocol.md`
- `docs/ca410-inspection-flow.md`
