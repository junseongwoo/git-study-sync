# ConfigWindow - Light / Pattern 탭 분석

## 1. 화면 목적

`ConfigWindow > Light / Pattern`은 EEC-P725R2 PG(Display/Pattern Generator)의 공통 통신 구성과 패턴별 전압 채널 역할·표시 기준을 관리하는 장비 설정 화면이다.

공식 설계 결정 기준에서 **PG voltage channel index는 Recipe가 아니라 이 Config의 EEC-P725R2 Pattern 설정이 단일 소유**한다. Recipe는 R/G/B 전압값 및 CA410 step 전압만 보관하고, Console은 이 탭의 R/G/B `VoltageChannelIndex`와 Recipe 전압을 조합해 PG에 전송한다.

따라서 이 탭의 값은 단순 테스트 UI가 아니라, 검사 카메라 촬영 전 점등 및 CA410 측정 전 전압 sweep에 영향을 주는 설비 공통값이다.

## 2. 화면 구성

| 구역 | 컨트롤 | 역할 |
|---|---|---|
| EEC-P725R2 공통 설정 | Display Count, Simulation Port Base, Pattern On Delay, Connect/Response Timeout | PG endpoint 수·시뮬레이터 포트·통신 대기 기준 |
| Display endpoint 목록 | 행 추가 불가 DataGrid | 각 PG display의 Index, Host, Port |
| Pattern 설정 안내 | TextBlock | R/G/B Voltage Channel이 Recipe·CA410 PG 전압 적용에 사용됨을 안내 |
| Pattern 목록 | 행 추가 가능 DataGrid | 패턴 이름, PG voltage channel, 표시 전압 기준 |
| 공통 하단 버튼 | Reload / Save / Close | Config 전체 재로딩·저장·닫기 |

## 3. 컨트롤 분석

### 3.1 EEC-P725R2 공통 설정

| 컨트롤명 | 종류 | 바인딩 | 기능 | 범위·영향 |
|---|---|---|---|---|
| Display Count | CalcTextBox | `EecDisplayCount` | 사용할 PG display endpoint 행 수 | 최소 1. 변경하면 해당 수만큼 Display 행을 보장하고 목록을 새로 표시한다. **[추론]** 수를 줄이면 기존 목록의 뒤쪽 endpoint 설정은 Config에는 남지만 현재 표시/실행 대상에서 제외될 수 있으므로 저장 전 확인이 필요하다. |
| Simulation Port Base | CalcTextBox | `EecSimulationPortBase` | PG simulator의 시작 포트 | UI 1024~65500. XAML 안내상 simulator endpoint는 `127.0.0.1:(Base + Index)`이다. 실제 PG와 포트가 충돌하지 않도록 설정한다. |
| Pattern On Delay (ms) | CalcTextBox | `EecPatternOnDelayMs` | PG 패턴/전압 적용 후 촬영·측정 전 대기 | UI 0~10000, 모델 기본 100 ms. 공식 검사 flow에서 `REQ_PTN_SEL → PatternOnDelay → StartStep/Grab` 순서를 지킨다. 너무 짧으면 점등 안정 전 이미지/계측이 수행될 수 있고, 길면 셀 cycle time이 증가한다. |
| Connect Timeout (ms) | CalcTextBox | `EecConnectTimeoutMs` | PG TCP 연결의 제한 시간 | UI 1~60000, 기본 1000 ms. 작으면 정상 네트워크 지연에도 연결 실패, 크면 장애 감지가 느려진다. **[추론]** |
| Response Timeout (ms) | CalcTextBox | `EecResponseTimeoutMs` | PG 명령 응답의 제한 시간 | UI 1~60000, 기본 5000 ms. 초과하면 PG 통신/점등 실패 alarm으로 이어질 수 있다. **[추론]** |

### 3.2 Display endpoint 목록

| 열 | 바인딩 | 기능 | 설정 방법 및 영향 |
|---|---|---|---|
| Index | `EecDisplayItems[].Index` (읽기 전용) | PG endpoint 식별 번호 | 0부터 자동 부여된다. Recipe의 PG mapping이 어느 endpoint를 뜻하는지 해석하는 기준이므로 임의 변경할 수 없다. **[추론]** |
| Host | `.Host` | 실 PG의 네트워크 주소 | 해당 display/PG 장치의 IP 또는 hostname을 입력한다. 기본 모델은 `192.168.0.101`이다. 잘못되면 그 PG의 패턴 선택·점등이 실패한다. |
| Port | `.Port` | 실 PG의 TCP 포트 | PG 장치 사양과 일치시킨다. 기본 모델은 1000이다. |

Display 행은 직접 추가할 수 없다. `Display Count`를 늘리면 ViewModel이 필요한 행을 생성한다. **[추론]** 새 행은 기본 Host/Port로 만들어지므로, 수를 늘린 뒤에는 새 endpoint의 실 장비 주소를 반드시 입력해야 한다.

### 3.3 Pattern 목록

| 열 | 바인딩 | 기능 | 검사 영향 및 설정 방법 |
|---|---|---|---|
| Index | `EecPatternItems[].Index` (읽기 전용) | Config 패턴 순번 | 저장/정규화 시 목록 순서대로 1부터 다시 부여된다. 행 순서를 변경하면 index 의미도 바뀔 수 있다. **[추론]** |
| Pattern Name | `.Name` | 패턴/색상 역할 이름 | R/G/B는 PG 전압 채널 기본값을 판정하는 역할명이다. 비어 있으면 `PTN_01` 같은 이름으로 보정된다. **[추론]** |
| Voltage Ch | `.VoltageChannelIndex` | PG `REQ_CH_VOLTAGE_SWEEP`에 사용할 실제 채널 번호 | **설비 공통 상수**다. 공식 문서 기준 R/G/B 채널은 이 값과 Recipe 전압을 조합해 전송된다. R=67, G=68, B=69가 기본값이다. 잘못되면 올바른 색의 전압이 다른 PG 채널에 적용될 수 있다. |
| Display Black V | `.DisplayBlackVoltage` | UI 점등 색/밝기 계산의 검정 기준 전압 | 기본 4.5 V. 실제 PG 전압 부호/극성을 반영하는 표시 기준이다. 검사 장비에 보내는 Recipe 전압값 자체는 아니다. |
| Display White V | `.DisplayWhiteVoltage` | UI 점등 색/밝기 계산의 백색 기준 전압 | 기본 1.0 V. Black V보다 작아야 한다. 저장 시 White가 Black 이상이면 보정된다. **[추론]** |

공식 표시 밝기 계산식은 다음과 같다.

```text
level = clamp((DisplayBlackVoltage - ChannelVoltage)
              / (DisplayBlackVoltage - DisplayWhiteVoltage), 0, 1)
```

즉 이 두 기준값은 Recipe/CA410 전압을 사람이 보는 UI 색과 밝기로 표현하는 기준이며, 패널의 실제 구동 전압을 새로 정의하는 값이 아니다.

## 4. 이벤트 분석

| 동작 | 연결 코드/흐름 | 결과 |
|---|---|---|
| Display Count 입력 | `EecDisplayCount` setter → `EnsureDisplayRows` → `RefreshEecDisplayItems` | 최소 1로 제한하고, 표시 수만큼 endpoint 행을 생성/표시한다. |
| Host/Port 편집 | `EecDisplayItems` 행의 TwoWay 바인딩 | 편집 컬렉션 항목이 변경된다. 저장 후 `EecP725R2Lights.Reconfigure`가 호출된다. **[추론]** |
| Pattern 행 추가·편집 | `EecPatternItems` TwoWay 바인딩 | Pattern Name/채널/표시 기준을 편집한다. 저장 시 `SyncPatternItemsToConfig` 및 `NormalizePatternRows`로 정리된다. |
| Save | `SaveWithChangeReport` | 변경 비교 확인 → config backup → YAML 저장 → `Vars.EecP725R2Lights.Reconfigure(Config.EecP725R2)` 실행. 기존 PG runtime 연결 상태는 저장 후 재확인해야 한다. **[추론]** |
| Reload | `Reload` → Config 재로드 → EEC 행/패턴 목록 refresh → PG cluster 재구성 | 저장하지 않은 값은 확인 후 버려지고 파일 기준값이 다시 표시된다. |

각 수치 `CalcTextBox`는 다수가 `UpdateSourceTrigger=Explicit`를 사용한다. **[추론]** 입력 직후 다른 곳을 클릭했을 때와 Save 직전에 값이 commit되는 정확한 동작은 `CalcTextBox` 구현 및 UI 시험으로 확인해야 한다.

## 5. 데이터 바인딩 분석

```text
Light / Pattern XAML
  └─ ConfigViewModel
       ├─ EecDisplayCount / timeout / delay / simulation port
       ├─ EecDisplayItems : ObservableCollection<EecP725R2DisplayConfig>
       └─ EecPatternItems : ObservableCollection<EecP725R2PatternConfig>
              ↓ Save
          ULedConfig.EecP725R2
              ↓ Reconfigure
          Vars.EecP725R2Lights (공유 PG cluster)
```

`EecDisplayItems`는 `DisplayCount`만큼 `Config.EecP725R2.Displays`에서 보여 주는 편집 컬렉션이다. `EecPatternItems`는 Config의 전체 Pattern 목록을 보여 주며 행 추가가 가능하다.

저장 중 패턴은 다음처럼 정규화된다.

- index를 화면 목록 순서에 따라 1-base로 다시 부여
- 빈 이름을 `PTN_nn`으로 보정
- `VoltageChannelIndex <= 0`이면 이름이 R/Red, G/Green, B/Blue인 경우 각각 67/68/69로 보정
- Black/White 전압이 유효하지 않거나 `White >= Black`이면 안전한 표시 기준으로 보정

위 보정은 구현 사실이므로, 의도한 채널을 0으로 비워 기본값에 의존하지 말고 설비 사양값을 명시적으로 입력해야 한다.

## 6. 사용자 입장에서 설명

### 설정 절차

1. 검사와 Aging을 중지한다.
2. 실제 PG 장비 수를 확인한 뒤 `Display Count`를 입력한다.
3. 각 Index의 Host와 Port를 PG 장비 통신 사양과 일치시킨다.
4. Pattern 목록에서 R/G/B 이름과 `Voltage Ch`가 실제 PG의 전압 채널 배선과 일치하는지 확인한다.
5. Black/White V는 UI 표시 기준값이므로 현장에서 확정된 전압 극성·표시 기준을 유지한다.
6. `Pattern On Delay`는 PG가 안정적으로 점등된 뒤 촬영/측정할 수 있는 최소 시간으로 설정한다.
7. Save를 누르고 변경 목록을 확인한다.
8. 저속 단일 셀에서 `패턴 선택 → 점등 안정화 → 촬영` 순서 및 실제 색/전압을 검증한다.

### 값 변경 후 현상

| 변경값 | 주로 나타나는 영향 |
|---|---|
| Display Count/Host/Port | 특정 PG 미연결, PG mapping 선택 불가, 해당 셀 점등 실패 |
| Pattern On Delay | 너무 짧으면 안정 전 촬영·CA410 측정, 너무 길면 검사 시간 증가 |
| Connect/Response Timeout | PG 장애 검출 시점과 통신 실패 빈도 |
| R/G/B Voltage Ch | 전압이 잘못된 색 채널로 출력되어 검사/CA410 결과가 무효가 될 수 있음 |
| Black/White V | 화면의 점등 색·밝기 표현만 달라져 운영자가 상태를 오해할 수 있음 |

## 7. 업무 로직 추론

공식 main flow 및 CA410 flow 기준의 PG 처리 흐름은 다음과 같다.

```text
셀/step의 PG endpoint 결정
  → 검사 카메라 이동
  → REQ_PTN_SEL(패턴 선택)
  → Recipe 전압 + Config R/G/B Voltage Ch로 전압 적용
  → PatternOnDelayMs 대기
  → StartStep 또는 Camera Grab
  → 셀 마지막에 REQ_PTN_OFF
```

- 공식 기준에서 PG·Motion은 `StartStep` 또는 `Grab` 직전 훅에 붙으며, `StartJob accepted`만으로 패턴 전체를 미리 점등하면 안 된다.
- CA410 자동 측정은 IP 검사와 별도의 Console 공정이다. CA410 전체/선택 반복 측정에서는 첫 step 전에 PG pattern 1을 선택하고 이후에는 channel voltage sweep과 `PatternOnDelayMs` 대기 후 측정한다.
- **[추론]** `EecP725R2LightCluster`는 Display endpoint 설정을 가지고 PG 연결을 생성·재구성하며, Recipe의 PG mapping index로 해당 endpoint를 고르는 구조다.
- **[추론]** PG 통신 또는 패턴 적용 실패는 `CON-PG-FAIL` alarm으로 검사 run 중단/실패에 연결될 수 있다.

### 시뮬레이션 기준: 공식 문서와 화면 불일치

공식 최신 변경 이력은 PG simulator 사용 여부를 **전역 Simulation Mode**가 결정한다고 확정한다. Simulation Mode가 OFF이면 실 PG endpoint에 연결하며, PG 미접속이면 정직하게 실패해야 한다.

반면 이 탭 XAML 안내문은 “검사 run은 Test Runner의 PG Simulator, recipe 편집기 테스트는 전역 Simulation Mode”라고 표시한다. 이는 최신 공식 기준과 다르다.

**문서 우선 결론:** 운영·개발 판단에는 전역 Simulation Mode 기준을 사용한다. 화면 안내문은 갱신이 필요한 불일치 항목이다.

## 8. 문서 작성용 요약

- 이 탭은 PG의 endpoint, 통신 대기, 패턴 전압 채널, 화면 표시 기준을 관리한다.
- R/G/B Voltage Ch는 Recipe가 아니라 Config의 설비 공통값이다.
- Pattern On Delay는 점등 뒤 촬영/CA410 측정 전 안정화 시간이다.
- Host/Port 오류 또는 PG 통신 실패는 실제 검사 점등을 막는다.
- Black/White V는 패널 구동 전압이 아니라 UI 색·밝기 표시 기준이다.
- PG simulator 정책은 화면 안내보다 최신 공식 문서의 전역 Simulation Mode 기준을 따른다.

## 9. 이해되지 않는 부분

| 확인 필요 항목 | 이유 |
|---|---|
| Display Count를 줄였을 때 뒤쪽 display 설정과 PG mapping의 처리 | UI는 표시 수만 제한하며 mapping 유효성 검증 위치를 추가 확인해야 한다. |
| Voltage Ch의 유효 범위와 EEC-P725R2 실제 채널 배선표 | 현재 기본값 67/68/69만 확인됐다. 프로토콜·현장 배선 표와 대조가 필요하다. |
| Display Black/White V가 사용되는 모든 UI | 공식 결정은 표시색 계산을 명시하지만 구체적 화면별 converter 호출은 추가 추적이 필요하다. |
| Pattern 이름 변경이 Recipe pattern name과 어떤 식으로 대응하는지 | Config의 R/G/B role 판정은 이름 기반 보정도 하므로 명명 규칙을 확정할 필요가 있다. |
| XAML의 과거 PG simulator 안내 갱신 여부 | 최신 공식 정책과 상충한다. UI 텍스트 수정 여부를 결정해야 한다. |

## 10. 전체 프로젝트와 연결

| 연결 대상 | 관계 |
|---|---|
| RecipeWindow > PG 매핑 | 셀/line이 사용할 PG endpoint index를 선택하며, 이 탭의 Display endpoint 목록이 그 선택지의 기반이다. |
| RecipeWindow > 검사 패턴 | Recipe는 패턴별 전압값을 소유하고, 이 탭은 그 전압을 보낼 PG channel 번호를 소유한다. |
| RecipeWindow > CA410 | CA410 step은 Config R/G/B `VoltageChannelIndex`와 Recipe의 R/G/B 전압을 조합해 PG voltage sweep을 수행한다. |
| Main glass inspection flow | 검사 카메라 이동 후 패턴 선택·전압 적용·Pattern On Delay를 거쳐 StartStep/Grab이 실행된다. |
| Aging | Aging은 공유 PG cluster를 사용해 PG 점등을 수행하므로 Host/Port/timeout 영향을 받는다. |
| MainWindow Simulation Mode | 실 PG와 simulator의 선택은 최신 공식 기준상 전역 Simulation Mode에서 결정한다. |

### 참조 근거

- 공식 문서: `docs/main-glass-inspection-flow.md`, `docs/ca410-inspection-flow.md`, `docs/development/architecture-decisions.md`, `docs/development/change-log.md`, `docs/EEC-P725R2_Protocol_251127.md`, `docs/alarm-policy.md`
- UI: `uLedAoiConsole/Windows/Core/ConfigWindow.xaml`
- ViewModel/Model: `uLedAoiConsole/ViewModels/ConfigViewModel.cs`, `uLedAoiConsole/Models/ULedSettings.cs`
