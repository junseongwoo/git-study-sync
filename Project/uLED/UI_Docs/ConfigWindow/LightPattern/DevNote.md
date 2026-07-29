# ConfigWindow - Light / Pattern 탭 개발 노트

## 데이터 및 runtime 흐름

```text
ULedConfig.EecP725R2
  ├─ DisplayCount / Displays[Index, Host, Port]
  ├─ PatternOnDelayMs / ConnectTimeoutMs / ResponseTimeoutMs
  └─ Patterns[Index, Name, VoltageChannelIndex, DisplayBlack/WhiteVoltage]
       ↓
ConfigViewModel Save
       ↓
Vars.EecP725R2Lights.Reconfigure(...)
       ↓
검사 step / CA410 / Aging의 공유 PG cluster
```

## 구현 포인트

- Display 행은 `DisplayCount`에 따라 최소 개수가 생성되고 Index는 0-base로 다시 부여된다.
- Pattern 행은 저장 시 1-base index로 재부여된다. 빈 이름은 `PTN_nn`, R/G/B의 0 이하 Voltage Ch는 67/68/69로 보정한다.
- `DisplayBlackVoltage`와 `DisplayWhiteVoltage`는 UI 색·밝기 계산 기준이며 `White < Black`을 보장하도록 정규화된다.
- Save/Reload는 PG cluster `Reconfigure`를 호출한다.
- PG simulator 선택은 Config per endpoint 값이 아니라 최신 공식 기준상 전역 Simulation Mode 소유다.

## 공식 문서와 화면 불일치

| 항목 | 최신 공식 기준 | 현재 XAML 안내 |
|---|---|---|
| PG simulator 결정 | 전역 Simulation Mode가 단일 결정 주체 | 검사 run은 Test Runner, recipe 편집기 테스트는 전역 Simulation Mode라고 표기 |

운영·개발 해석은 최신 공식 문서가 우선이다. XAML 안내문은 갱신 후보로 기록한다.

## 추가 확인 필요

1. `EecP725R2LightCluster.Reconfigure`가 활성 연결을 끊고 즉시 다시 연결하는지 확인한다.
2. Display Count 축소 시 기존 PG mapping의 validation·실행 정책을 확인한다.
3. 실제 PG protocol의 voltage channel 유효 범위와 R/G/B 배선표를 현장 사양으로 확정한다.
4. `CalcTextBox`의 Explicit update가 Save 전에 모든 값을 commit하는지 UI 테스트한다.
5. Display Black/White V를 사용하는 converter와 모든 화면을 추적해 사용자 매뉴얼의 "표시 전용" 설명을 검증한다.

## 주요 소스

- `uLedAoiConsole/Windows/Core/ConfigWindow.xaml`
- `uLedAoiConsole/ViewModels/ConfigViewModel.cs`
- `uLedAoiConsole/Models/ULedSettings.cs`
- `docs/main-glass-inspection-flow.md`
- `docs/ca410-inspection-flow.md`
- `docs/development/architecture-decisions.md`
- `docs/development/change-log.md`
