# ConfigWindow - Connections 탭 분석

## 1. 화면 목적

`ConfigWindow > Connections`는 Console이 검사 실행에 필요한 외부 구성요소와 통신하기 위한 연결 정보를 관리한다. 화면은 다음 세 연결을 다룬다.

1. uLedIp(영상 검사 IP) TCP endpoint
2. CA-410 색도계 RS232C endpoint
3. Light Controller의 Light On/Off RS232C endpoint

공식 문서 기준으로 Console은 전체 glass run을 오케스트레이션하고, IP는 셀 단위 검사 실행을 맡는다. IP endpoint가 정상이어야 Console이 `StartJob → StartStep/Grab 반복 → EndJob → EvtJobCompleted`의 IP 검사 흐름을 수행할 수 있다. CA-410과 Light 연결은 선택한 검사/CA410 공정에서만 추가로 사용된다.

## 2. 화면 구성

| 구역 | XAML 컨트롤 | 용도 |
|---|---|---|
| IP Endpoints | 행 추가 가능 `DataGrid` | Recipe 창이 직접 연결할 uLedIp 서버 목록 |
| CA-410 RS232C | CheckBox, 숫자 입력 3개, 행 추가 불가 `DataGrid` | CA-410 측정 옵션, timeout 및 장치별 COM 설정 |
| LED RS232C | COM Port/baud/data bits 입력 | Light On/Off 통신용 단일 조명 제어기 설정 |

탭 내부에는 연결 테스트·연결 해제 버튼이 없다. 실제 연결 성공 여부는 별도 실행/연결 상태 및 로그로 확인해야 한다.

## 3. 컨트롤 분석

### 3.1 IP Endpoints

| 컨트롤명 | 종류 | 바인딩 | 기능/영향 | 입력 기준 |
|---|---|---|---|---|
| No | DataGridTextColumn | `IpEndpointItems[].No` | endpoint 순번 | 1부터 고유하게 관리한다. 0 이하이면 저장 시 목록 순번으로 보정된다. **[추론]** |
| Name | DataGridTextColumn | `.Name` | endpoint 표시·식별 이름 | 장비 역할을 알 수 있는 이름을 입력한다. 비어 있으면 저장 시 `IP-{No}` 형식으로 보정된다. **[추론]** |
| IP Address | DataGridTextColumn | `.IpAddress` | uLedIp 서버의 IPv4/hostname 주소 | 실제 IP 프로세스가 수신 중인 주소를 입력한다. 공백은 `127.0.0.1`로 보정된다. **[추론]** |
| Port | DataGridTextColumn | `.Port` | uLedIp TCP 포트 | 유효 범위는 1~65535이다. 범위를 벗어나면 저장 시 해당 No의 기본 포트로 보정된다. **[추론]** |
| Enabled | DataGridCheckBoxColumn | `.Enabled` | endpoint 사용 여부 | 사용하지 않을 IP는 해제한다. **[추론]** 실행 대상/할당 규칙은 레시피·runtime registry에서 추가 확인이 필요하다. |

기본 모델은 IP-1=`127.0.0.1:5003`, IP-2=`127.0.0.1:5004`이다. 공식 `automation-api.md`의 포트 예약도 IP에 5003·5004를 배정한다.

### 3.2 CA-410 RS232C

| 컨트롤명 | 종류 | 바인딩 | 기능/영향 | 범위·기본값 |
|---|---|---|---|---|
| Connection | 읽기 전용 TextBox | 없음 | 현재 탭의 CA-410 연결 방식이 RS232C임을 표시한다. | `RS232C` 고정 |
| Include XYZ | CheckBox | `Ca410IncludeXyz` | CA-410 측정 옵션의 `IncludeXyz`로 전달된다. | 기본 `true` |
| Command ms | CalcTextBox | `Ca410CommandTimeoutMs` | CA-410 명령 1회의 응답 제한 시간이다. 초과 시 CA-410 통신/측정 실패로 처리될 수 있다. | UI 최소 1000 ms, 기본 10000 ms |
| ZRC timeout ms | CalcTextBox | `Ca410CalibrationTimeoutMs` | CA-410 보정(ZRC) 명령의 제한 시간이다. | UI 최소 1000 ms, 기본 30000 ms |
| RS232 idle ms | CalcTextBox | `Ca410SerialResponseIdleMs` | RS232C 응답이 끝났다고 판단하기 위한 idle 시간이다. | UI 최소 10 ms, 기본 150 ms |
| No | DataGridTextColumn | `Ca410DeviceItems[].No` | CA-410 장치 순번 | 행 추가는 허용되지 않는다. 기본 2대 구성이다. |
| Name | DataGridTextColumn | `.Name` | CA-410 장치 식별명 | 기본 `CA410-1`, `CA410-2` |
| Align Camera | DataGridTextColumn | `.AlignCameraName` | CA-410 장치와 대응하는 Align 카메라 이름 | 기본은 CA410-1=CAM2, CA410-2=CAM1. Heads 탭의 Align Camera 이름과 일치시켜야 한다. |
| COM Port | DataGridTextColumn | `.SerialPortName` | 장치가 연결된 Windows COM 포트 | 기본 COM1/COM2 |
| Baud | DataGridTextColumn | `.SerialBaudRate` | CA-410 직렬 통신 속도 | 기본 38400. 0 이하면 저장 시 38400으로 보정된다. **[추론]** |
| Data Bits | DataGridTextColumn | `.SerialDataBits` | 직렬 데이터 비트 수 | 5~8만 유효, 기본 7. 범위 밖은 저장 시 7로 보정된다. **[추론]** |
| Enabled | DataGridCheckBoxColumn | `.Enabled` | 해당 CA-410 사용 여부 | 사용하지 않는 장치는 해제한다. **[추론]** 실제 장치 선택 규칙은 CA410 runner에서 확인이 더 필요하다. |

XAML에 표시된 CA-410 기본 직렬 규격은 `38400 bps, 7 data bits, even parity, 2 stop bits, RTS/CTS`이다. 공식 CA-410 protocol 문서도 RS232C가 Ethernet header 없이 동일한 ASCII 명령/응답을 사용한다고 명시한다.

### 3.3 LED RS232C

| 컨트롤명 | 종류 | 바인딩 | 기능/영향 | 범위·기본값 |
|---|---|---|---|---|
| COM Port | TextBox | `Config.LightConfig.PortName` | Light Controller 연결 COM 포트 | 기본 COM5 |
| Baud | CalcTextBox | `.BaudRate` | 조명 제어기 직렬 통신 속도 | UI 최소 1, 기본 9600 |
| Data Bits | CalcTextBox | `.DataBits` | 조명 제어기 직렬 데이터 비트 | UI 5~8, 기본 8 |

이 영역은 XAML 안내대로 Light Controller 1대의 Light On/Off 통신용이다. **[추론]** 저장 후 `LightRuntime.ApplyConfig`는 열려 있던 포트를 닫고 새 Port/Baud/DataBits/Parity.None/StopBits.One을 적용한다. 현재 UI에는 parity·stop bits 입력이 없으므로 Light Controller의 이 두 값은 고정이다.

## 4. 이벤트 분석

| 사용자 동작 | 코드 흐름 | 결과 |
|---|---|---|
| IP endpoint 행 추가/편집 | `IpEndpointItems`에 TwoWay 바인딩 | 화면의 편집 컬렉션만 변경된다. 저장 전에는 config 파일 및 runtime 재구성이 확정되지 않는다. **[추론]** |
| CA-410/Light 값 편집 | `ConfigViewModel` 또는 `Config.LightConfig`에 바인딩 | 값이 메모리의 Config에 반영된다. 일부 `CalcTextBox`는 `UpdateSourceTrigger=Explicit`이므로 포커스/저장 시점의 반영 동작을 실제 UI에서 확인해야 한다. **[추론]** |
| Config 창의 Save | `SaveWithChangeReport` → 유효값 보정 → 변경 확인 대화상자 → backup 생성 → YAML 저장 | `IpRuntimes.Reconfigure(Config.IpEndpoints)`, `LightRuntime.ApplyConfig(Config.LightConfig)`가 호출된다. 즉 IP 및 Light runtime은 저장 직후 새 설정으로 재구성된다. **[추론]** |
| Config 창의 Reload | store 재로딩 → 항목 컬렉션 refresh → IP runtime 재구성 | 저장하지 않은 변경은 확인 후 폐기되고 파일의 값으로 되돌아간다. **[추론]** CA-410의 재초기화는 이 메서드에서 직접 확인되지 않는다. |

## 5. 데이터 바인딩 분석

```text
Connections XAML
  ├─ IpEndpointItems : ObservableCollection<IpEndpointConfig>
  │    └─ Save → Config.IpEndpoints → Vars.IpRuntimes.Reconfigure(...)
  ├─ Ca410DeviceItems : ObservableCollection<Ca410DeviceConfig>
  │    └─ Save → Config.Ca410.Devices → CA410 측정 옵션 생성 시 참조
  └─ Config.LightConfig
       └─ Save → Vars.LightRuntime.ApplyConfig(...)
```

`ConfigViewModel` 생성 시 Config 저장소를 읽고 `RefreshIpEndpointItems`, `RefreshCa410DeviceItems`로 각 `ObservableCollection`을 채운다. Save는 편집 컬렉션을 Config의 List로 다시 구성한다. 이 때문에 DataGrid 변경은 저장 전에는 영속 파일 기준 변경이 아니다.

CA-410 측정 옵션은 `Ca410Config.ToMeasurementOptions(device)`에서 항상 `ConnectionKind.Rs232c`로 생성되며, 장치 COM/baud/data bits, idle timeout, command timeout, Include XYZ를 넘긴다. CA-410 simulator 사용 여부는 Connections 탭이 아니라 전역 Simulation Mode에서 결정된다.

## 6. 사용자 입장에서 설명

### 권장 설정 순서

1. **검사를 중지**하고, 네트워크 주소·COM 포트가 다른 프로그램에 점유되어 있지 않은지 확인한다.
2. IP Endpoints에 실제 uLedIp 프로세스의 IP 주소와 포트를 입력한다. 로컬 실행이 아닌 경우 `127.0.0.1`을 그대로 사용하지 않는다.
3. IP마다 `Enabled`를 확인하고, No/Name이 중복되지 않도록 정리한다.
4. CA-410 장치별 COM Port, Baud, Data Bits를 장비 연결 사양과 맞춘다. Align Camera에는 해당 CA-410이 배치된 헤드의 카메라 이름을 입력한다.
5. Light Controller COM/baud/data bits를 실제 컨트롤러 사양과 맞춘다.
6. Save를 누르고 변경 목록을 검토한 뒤 저장한다.
7. IP 연결 상태, CA-410 단발 측정, Light On/Off를 각각 낮은 위험의 시험 동작으로 확인한다.

### timeout 설정 원칙

- Command timeout: 정상 명령 응답 시간보다 약간 길게 둔다. 너무 짧으면 정상 장치도 timeout이 될 수 있고, 너무 길면 실제 통신 장애를 늦게 감지한다.
- ZRC timeout: 보정은 일반 측정보다 오래 걸릴 수 있으므로 별도 값으로 관리한다.
- RS232 idle: 장치가 여러 응답 조각을 보낼 수 있다면 너무 짧게 두지 않는다. 반대로 과도하게 길면 측정 cycle이 느려질 수 있다.

## 7. 업무 로직 추론

공식 main flow의 IP 관련 부분은 다음 순서를 지킨다.

```text
Console이 IP endpoint에 Cell Job 준비(StartJob)
  → 각 pattern × point 입력(StartStep 또는 Grab)
  → EndJob ACK 후 다음 셀의 motion/PG 준비 진행
  → IP worker의 EvtJobCompleted(final_result) 수신
```

- IP endpoint 설정 오류는 이 Cell Job 입력 또는 최종 결과 수신을 실패시키므로 검사 진행에 직접 영향을 준다.
- 공식 CA410 flow에서 자동 검사에 CA410 옵션이 켜지면 셀 단위 IP 검사와 별개로 CA410 측정이 수행된다. CA-410 장치 연결 오류는 `CON-CA410-COMM-FAIL` alarm과 연결된다.
- **[추론]** CA410 device의 `AlignCameraName`은 어느 검사 헤드/Align 기준에 장치를 대응할지 결정하는 키로 보인다. 이름 불일치는 잘못된 CA-410 장치 선택 또는 장치 미발견으로 이어질 수 있다.
- **[추론]** Light RS232C는 `LightRuntime.OnOff`를 통해 외부 조명 On/Off를 제어하는 별도 통신이며, EEC-P725R2 PG 패턴 통신과는 다른 runtime이다. 따라서 이 탭의 Light 설정은 `Light / Pattern` 탭의 PG endpoint 설정을 대체하지 않는다.

## 8. 문서 작성용 요약

- Connections 탭은 IP 검사 서버, CA-410 색도계, Light On/Off 제어기의 통신 정보를 설정하는 화면이다.
- IP 주소/포트가 틀리면 검사 이미지 입력과 결과 수신이 실패한다.
- CA-410의 COM·직렬 규격·timeout은 CA410 측정의 성공률과 검사 시간이 좌우한다.
- Light COM 설정은 단일 Light Controller의 On/Off 통신에 사용된다.
- 설정 변경은 검사 중에 하지 말고 저장 후 각 장치를 개별 시험한다.

## 9. 이해되지 않는 부분

| 추가 확인 항목 | 이유 |
|---|---|
| Enabled=false IP endpoint를 runtime registry가 실제로 어떻게 제외하는지 | UI에는 선택 규칙이 없으며 IP 할당 서비스 확인이 필요하다. |
| CA-410 device No/AlignCameraName으로 측정 장치를 선택하는 정확한 규칙 | 설정 모델은 확인했지만 CA410 runner의 선택 분기를 추가 추적해야 한다. |
| Save 후 CA-410 연결을 즉시 재연결하는지, 다음 측정 시 새 값으로 연결하는지 | Save에는 CA410 runtime reconfigure 직접 호출이 없다. 앱 생명주기와 측정 runner 확인이 필요하다. |
| `CalcTextBox`의 Explicit source update 확정 시점 | 컨트롤 구현체와 ConfigWindow 저장 전 commit 동작 확인이 필요하다. |
| Light RS232C와 실제 검사 조명/PG의 역할 경계 | LightRuntime 호출부 및 장비 배선 사양을 확인해야 한다. |

## 10. 전체 프로젝트와 연결

| 연결 대상 | Connections 탭과의 연결 |
|---|---|
| MainWindow / 검사 실행 | Console은 IP endpoint를 통해 Cell Job을 전달하고 최종 검사 결과를 받는다. |
| RecipeWindow | XAML 안내대로 Recipe 창은 IP Endpoints에 등록한 uLedIp에 직접 연결한다. |
| RecipeWindow > CA410 | CA410 Plan이 활성화된 경우 이 탭의 RS232C 장치/timeout/XYZ 옵션을 사용한다. |
| ConfigWindow > Heads | CA410 Device의 Align Camera 이름은 Heads의 Y1/Y2 Align Camera 명칭과 일관되어야 한다. |
| ConfigWindow > Light / Pattern | 이 탭은 Light On/Off 직렬 연결, Light / Pattern은 EEC-P725R2 PG의 패턴·표시 설정을 담당한다. |
| Automation API / CIM | 공식 문서의 Automation API는 외부 요청을 Console의 동일 검사 진입점으로 전달한다. IP 연결 상태는 Automation status의 관찰 대상이다. |

### 참조 근거

- 공식 문서: `docs/main-glass-inspection-flow.md`, `docs/automation-api.md`, `docs/ca410-inspection-flow.md`, `docs/ca410-ethernet-protocol.md`, `docs/alarm-policy.md`
- UI: `uLedAoiConsole/Windows/Core/ConfigWindow.xaml` (`Connections` 탭)
- ViewModel/Model: `uLedAoiConsole/ViewModels/ConfigViewModel.cs`, `uLedAoiConsole/Models/ULedSettings.cs`
- Runtime: `uLedAoiConsole/App.xaml.cs`, `uLedAoiConsole/Services/LightRuntime.cs`
