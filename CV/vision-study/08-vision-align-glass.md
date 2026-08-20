# 8일차. 3개 Align Mark로 370×470 Glass 중심 정렬하기

> 특별 학습 주제 · 예상 학습 시간: 6~8시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함  
> 이번 문서는 요청에 따라 코드 구현 없이 **개념, 수식, Teaching 및 자동 Align Logic**에 집중한다.

## 1. 오늘 해결할 문제

Glass 크기:

```text
X 방향 Width  = 370 mm
Y 방향 Height = 470 mm
Glass 설계 중심 = (0, 0)
```

Glass 위에 Align Mark가 3개 있고 Camera 한 대로 각 Mark를 확인한다고 가정한다. 목표는 다음과 같다.

1. 처음 기준 Glass를 올바른 자세로 놓고 Align 기준을 등록한다.
2. 이후 Glass가 X/Y로 이동하거나 회전되어 투입되어도 Mark 3개를 자동 검출한다.
3. 검출한 Mark로 현재 Glass 중심좌표와 회전각 `X/Y/Theta`를 계산한다.
4. Stage를 보정하거나 검사 ROI를 Transform하여 기준 Glass와 같은 좌표계로 검사한다.

## 2. 가장 먼저 정할 좌표계

### 2.1 Glass 설계 좌표계

Glass 중심을 원점으로 둔다.

```text
                       +Y
                        ▲
         (-185,+235)    │    (+185,+235)
                 ┌──────┼──────┐
                 │      │      │
                 │      ● C    │  C = Glass Center (0,0)
                 │      │      │
                 └──────┼──────┘
         (-185,-235)    │    (+185,-235)
                        └────────────► +X
```

- X 범위: `-185~+185 mm`
- Y 범위: `-235~+235 mm`
- Mark의 설계 위치는 이 중심 기준 좌표로 저장한다.

### 2.2 Image 좌표계

보통 Camera Image는 좌상단 원점이고 아래쪽이 +y다.

```text
(0,0) ─────────► image +x
  │
  │
  ▼ image +y
```

Glass/Machine 좌표의 +Y가 위쪽이라면 Image y와 부호가 반대다. Image Pixel 좌표로 바로 각도를 계산하면 회전 부호를 잘못 해석할 수 있으므로 먼저 Calibration을 적용해 공통 Machine 좌표계로 변환한다.

### 2.3 Machine/Stage 좌표계

실제 Stage가 사용하는 X/Y/Theta 좌표계다. 다음을 명확히 정의해야 한다.

- X/Y축의 +방향
- 길이 단위(mm 또는 μm)
- Theta의 +방향(CCW인지 CW인지)
- Stage 회전 중심(Pivot)
- Camera가 고정인지 이동하는지
- Glass가 이동하는지 Camera가 이동하는지

## 3. 3개 Mark 배치 예제

질문의 배치를 아래와 같은 대표적인 삼각형 Layout으로 가정한다.

```text
                  +Y
                   ▲
      Mark A ●─────┼─────● Mark B
             (-a,+b)     (+a,+b)
                   │
                   ● Glass Center (0,0)
                   │
                   ● Mark C
                 (0,-c)
```

- Mark A/B: Y축을 기준으로 좌우 대칭
- Mark C: Y축 위에 위치
- 세 Mark가 Glass 중심을 둘러싸는 넓은 삼각형을 구성

370×470 mm Glass의 설명용 예:

```text
Mark A = (-150, +200) mm
Mark B = (+150, +200) mm
Mark C = (   0, -200) mm
Glass Center = (0, 0) mm
```

이 Mark 위치는 설명용이다. 실제 값은 Glass Drawing의 Mark 중심 좌표를 사용한다.

> [!NOTE]
> 만약 질문에서 말한 “X축 대칭 Mark 2개”가 위·아래 대칭을 뜻한다면 X와 Y 역할만 바꾸면 된다. 뒤의 [[#8. Y축 방향 Mark 2개로 각도 계산하기|Y축 방향 Pair 공식]]을 사용한다.

## 4. 일반적인 Vision Align의 목적

Align은 현재 Glass 자세와 기준 Glass 자세의 차이를 구하는 과정이다.

```text
기준 자세: X_ref, Y_ref, Theta_ref
현재 자세: X_cur, Y_cur, Theta_cur

Pose Error:
ΔX     = X_cur - X_ref
ΔY     = Y_cur - Y_ref
ΔTheta = Theta_cur - Theta_ref
```

보통 Align은 다음 둘 중 하나에 사용한다.

### 4.1 Physical Alignment

Stage를 X/Y/Theta로 움직여 Glass 자체를 기준 자세에 맞춘다.

```text
Mark 검출 → Pose 계산 → Stage 보정 → 재촬영 → 허용 오차 확인
```

### 4.2 Virtual Alignment

Glass를 움직이지 않고 검사 ROI와 검사 좌표를 현재 Glass 자세에 맞게 이동·회전한다.

```text
Mark 검출 → Pose 계산 → ROI Transform → 현재 위치에서 검사
```

장비에 정밀 X/Y/Theta Stage가 있으면 Physical Align을, Cycle Time이나 기구 조건상 움직이기 어렵다면 Virtual Align을 사용한다. 두 방식을 결합할 수도 있다.

## 5. 사용자가 생각한 방법은 맞는가?

생각한 흐름은 기본적으로 맞다.

```text
기준 Glass 투입
   ↓
Camera로 Mark 중심 검출
   ↓
Glass를 이동/회전하여 기준 자세로 맞춤
   ↓
Align 기준 등록(Teaching)
   ↓
다음 Glass부터 Mark 자동 검출
   ↓
기준 대비 X/Y/Theta 계산
   ↓
Stage 또는 ROI 자동 보정
```

다만 **정렬된 Image만 저장하는 것으로는 부족하다.** 다음 데이터가 함께 필요하다.

- Mark A/B/C 각각의 Template 또는 검출 조건
- Mark ID와 순서
- 각 Mark의 Glass 중심 기준 설계 좌표 `(x_i, y_i)`
- 기준 등록 시 각 Mark의 Machine 좌표
- Camera Pixel → Machine 좌표 Calibration
- Mark마다 Camera가 이동해야 하는 Stage 촬영 위치
- Glass 기준 중심과 Stage 회전 중심의 관계
- Match Score, Search Range, 허용 위치/각도 오차
- Recipe와 Calibration Version

즉, 등록 대상은 단순 Align Image가 아니라 **Mark Geometry를 포함한 Align Recipe**다.

### 5.1 핵심 질문: 처음에 Align Mark Image가 반드시 있어야 하는가?

정확한 답은 **사용하는 Mark 검출 방식에 따라 다르다**다.

```text
실제 Template Image가 항상 필수인가? → 아니오
Mark에 대한 사전 정의가 필요한가?   → 예
```

Camera가 Image를 촬영했다고 해서 SW가 아무 정보 없이 “이것이 Align Mark다”라고 자동으로 판단할 수는 없다. 시스템에는 최소한 다음 중 하나가 있어야 한다.

1. 실제로 촬영해 등록한 Mark Template Image
2. CAD 또는 Drawing에서 가져온 Mark 형상 Model
3. 원, 십자, 사각형처럼 수학적으로 정의된 Geometry
4. 밝기, 크기, 면적, 원형도 등 Blob 조건
5. QR/AprilTag처럼 미리 정의된 Fiducial 규칙과 ID

즉 **Mark Image가 무조건 필요한 것은 아니지만, 어떤 형상을 Mark라고 부를 것인지에 대한 기준은 무조건 필요하다.**

### 5.2 Mark 종류별 Template Image 필요 여부

| Align Mark 형태 | 일반적인 검출 방법 | 실제 Template Image |
|---|---|---|
| 검은 원/흰 원 | Threshold → Blob/Contour → 원 Fit | 보통 불필요 |
| Ring Mark | Edge → Circle/Ellipse Fit | 보통 불필요 |
| 단순 십자 `+` | Edge/Line 검출 → 두 선 교점 | 보통 불필요 |
| 사각형/마름모 | Contour/Corner 검출 | 보통 불필요 |
| 고유 Logo/복잡한 Pattern | Template/Pattern Matching | 필요 또는 강력 권장 |
| QR/AprilTag 계열 | 규격 Decoder/Corner 검출 | 별도 촬영 Template 불필요 |
| 주변 Pattern과 매우 비슷한 Mark | Pattern Matching + 예상 ROI | 필요 권장 |

#### 예: 검은 원형 Align Mark

```text
Image 촬영
   ↓
Gray/Binary Threshold
   ↓
Blob 후보 검출
   ↓
면적·지름·원형도·예상 위치로 후보 Filtering
   ↓
Contour에 Circle/Ellipse Fit
   ↓
Fit된 원의 Center = Align Mark 중심
```

이 경우에는 Mark Template Image 없이도 `검은 원`, `예상 지름`, `면적 범위`, `원형도`, `예상 ROI`가 Mark의 기준이 된다.

#### 예: 십자 Align Mark

```text
Image 촬영
   ↓
두 방향 Edge/Line 검출
   ↓
수평 계열 중심선 + 수직 계열 중심선 계산
   ↓
두 중심선의 교점 = Align Mark 중심
```

Glass가 회전되어 십자가 기울어져 있어도 두 Line의 각도 범위를 넓게 검색하고 교점을 계산할 수 있다. 이 경우 “수평선은 항상 0°”라고 고정하면 안 된다.

#### 예: 복잡한 고유 Pattern

Mark가 Logo나 복잡한 Pattern이면 기준 Glass에서 촬영한 Image를 Template로 등록하고, Runtime에 위치와 각도를 함께 검색하는 Pattern Matching이 일반적이다.

### 5.3 Image가 전혀 없는 최초 설치 시에는 어떻게 시작하는가?

자동 Align을 처음 개발하거나 장비를 Setup할 때는 아직 촬영 Template가 없을 수 있다. 이때 다음 순서로 **최초 Teaching Image**를 만든다.

```text
Glass Drawing/CAD에서 Mark 설계좌표 확인
   ↓
기준 Glass를 Jig 또는 대략적인 Nominal 위치에 투입
   ↓
Stage를 첫 번째 Mark의 예상 위치로 이동
   ↓
넓은 Search ROI 또는 전체 FOV 촬영
   ↓
Geometry Finder 또는 작업자 확인으로 Mark 후보 선택
   ↓
Exposure/Focus/조명을 조정해 좋은 Mark Image 획득
   ↓
필요하면 이 Image를 Template로 등록
   ↓
Mark 중심 정의와 Glass 중심 기준 좌표를 Recipe에 저장
```

여기서 Drawing의 Mark 좌표와 장비의 Nominal Loading Position이 첫 촬영 위치를 제공한다. 위치 오차가 Camera FOV보다 크다면 다음 중 하나가 추가로 필요하다.

- 더 넓은 FOV의 Coarse Camera
- Stage Raster Search/Spiral Search
- Glass Edge 또는 Corner를 먼저 찾는 Coarse Align
- 기구 Stopper/Jig/Presence Sensor
- 작업자가 최초 Mark 위치를 지정하는 Teaching UI

> [!IMPORTANT]
> Mark가 Camera FOV 밖에 있는데 사전 위치 정보도 없다면 알고리즘은 그 Mark를 찾을 수 없다. “자동 검색”은 정해진 Search Range 안에서 수행되는 것이지 장비 전체 공간에서 무한히 찾는 기능이 아니다.

### 5.4 Template 방식의 최초 등록

Pattern Matching을 사용한다면 최초 한 번은 다음 과정이 필요하다.

1. 기준 Glass를 Nominal 위치에 놓는다.
2. Camera로 Mark가 포함된 Image를 촬영한다.
3. 사용자가 Mark 영역을 ROI로 선택하거나 Geometry Finder가 후보를 제안한다.
4. Mark 중심의 정의를 확인한다.
5. Template Image와 중심 Offset을 저장한다.
6. 허용 Scale/Angle/Search Range와 Match Score를 설정한다.
7. Mark의 Glass 중심 기준 설계좌표를 함께 저장한다.

여기서 Template ROI 중심과 실제 Mark 중심이 반드시 같지는 않다. Template 안에서 Mark 중심이 `(cx,cy)` 어디에 있는지 Center Offset을 저장해야 한다.

### 5.5 Glass가 틀어지면 Mark도 틀어지는데 어떻게 중심을 찾는가?

Glass가 X/Y로 이동하고 `Theta`만큼 회전하면 Mark도 Glass 중심을 기준으로 함께 이동·회전한다.

```text
현재 Mark 위치 = R(Theta) × Mark 설계좌표 + Glass 중심 Translation
```

하지만 **Mark 자체의 중심은 회전해도 중심 그대로다.**

- 원형 Mark: 원을 회전해도 Center는 동일
- 십자 Mark: 두 선이 회전하지만 교점은 Center
- 사각 Mark: 네 Corner가 회전하지만 대각선 교점/Contour 중심으로 Center 계산
- Template Mark: 회전 Matching이 위치 `(x,y)`와 각도 `theta`를 반환

따라서 Runtime Logic은 “Mark가 똑바로 놓여 있을 것”을 가정하지 않고 다음과 같이 검색한다.

```text
예상 위치 주변 Search ROI 설정
   ↓
허용 X/Y 이동 범위 검색
   ↓
허용 Angle 범위 검색 또는 Rotation-invariant Geometry 검출
   ↓
현재 기울어진 Mark의 중심좌표 검출
   ↓
세 Mark 중심으로 Glass 전체 X/Y/Theta 계산
```

예를 들어 Glass 회전 범위가 `±2°`라면 Pattern Matching의 Angle Search를 최소한 그 범위와 여유 Margin까지 설정한다. Geometry 방식에서는 Line/Circle Fit이 해당 각도에서도 안정적으로 중심을 찾는지 검증한다.

### 5.6 무엇이 기준좌표이고 무엇이 측정좌표인가?

Align에서는 서로 다른 세 좌표를 구분해야 한다.

| 좌표 | 의미 | 예시 |
|---|---|---|
| Mark 설계좌표 `q_i` | Glass 중심 `(0,0)`에서 Mark가 원래 있어야 하는 위치 | `A=(-150,+200) mm` |
| Mark Image 좌표 | 현재 촬영 Image에서 검출한 Mark 중심 | `(u,v)=(1023.4,812.7) pixel` |
| Mark Machine 좌표 `p_i` | Calibration과 촬영 Stage Pose를 적용한 실제 장비 좌표 | `(X,Y)=(351.24,927.51) mm` |

처리 흐름:

```text
Image에서 Mark Center (u,v) 검출
              ↓ Camera/Stage Calibration
Machine Mark Center p_i 계산
              ↓ 3개 p_i와 설계 q_i 비교
Glass Center X/Y와 Theta 계산
```

Mark의 기준좌표는 Runtime Image에서 새로 만드는 값이 아니라 Drawing/Teaching 단계에 Recipe로 등록되어 있는 값이다. Runtime에서는 현재 Mark 중심만 측정한다.

### 5.7 Template Matching은 Glass가 회전되어도 찾을 수 있는가?

사용하는 Matcher가 Rotation Search를 지원하고 검색 범위를 올바르게 설정했다면 가능하다.

일반적인 방식:

- Image Pyramid로 Coarse 위치 검색
- 여러 Angle로 Template를 회전하며 비교
- 가장 높은 Score의 X/Y/Theta 선택
- 원본 해상도에서 Sub-pixel Refinement

주의사항:

- 허용 각도가 넓을수록 처리 시간이 증가
- 대칭 Mark는 90°/180° 방향을 구분하지 못할 수 있음
- Mark 일부가 잘리거나 오염되면 Score 저하
- Background에 같은 Pattern이 있으면 오검출 가능
- 예상 ROI와 세 Mark Geometry로 결과를 검증해야 함

원이나 완전 대칭 십자는 자체 각도를 알기 어렵지만 Center 검출은 가능하다. Glass 전체 Theta는 서로 떨어진 Mark 중심을 연결한 Vector로 구하면 된다.

### 5.8 질문에 대한 최종 답

```text
Q. Align Mark Image가 무조건 필요한가?
A. Pattern Matching이면 필요하거나 권장된다.
   원/십자/사각 Geometry 검출이면 실제 Template Image 없이도 가능하다.

Q. 아무 기준 없이 Camera가 알아서 Mark를 찾는가?
A. 아니다. Template, CAD/Geometry, 크기·밝기 조건, 예상 ROI 중
   최소한 하나 이상의 사전 정의가 필요하다.

Q. Glass가 틀어지면 Mark 중심은 어떻게 찾는가?
A. 허용 이동/회전 범위에서 Pattern 또는 Geometry를 검출해
   현재 기울어진 Mark 자체의 중심을 먼저 찾는다.

Q. 그 다음 Align은 어떻게 하는가?
A. 검출 중심을 Machine 좌표로 변환하고, 설계 Mark 좌표와 3점
   Rigid Fit하여 Glass 중심 X/Y/Theta를 계산한다.
```

### 5.9 가장 권장하는 실제 구성

현재 질문의 370×470 Glass와 3개 Mark에는 다음 구성을 권장한다.

```text
[최초 Teaching]
CAD Mark 좌표 + 기준 Glass
→ Mark별 좋은 Image 획득
→ 단순 원/십자면 Geometry Model 저장
→ 복잡한 Mark면 Template Image 저장
→ Mark Center Offset과 Glass 중심 기준 좌표 저장

[Runtime]
Nominal Stage Position으로 이동
→ 넓은 ROI에서 Mark 검출(X/Y/Angle 허용)
→ 현재 Mark Center를 Sub-pixel Refinement
→ Machine 좌표로 통합
→ 3점 Rigid Fit
→ Residual/Pair Distance/Score 검증
→ Stage 또는 ROI Align
→ 필요 시 재촬영 검증
```

즉 사용자가 생각한 **“기준 Align Mark Image를 등록하고 다음 Glass에서 그 Mark를 찾아 Align”**은 올바른 방식 중 하나다. 다만 Mark가 단순 Geometry라면 Image Template 대신 Geometry Model을 사용할 수 있고, 어느 방식이든 Mark 설계좌표와 Glass 중심의 관계를 반드시 함께 등록해야 한다.

## 6. Teaching 단계: 최초 기준 등록

### Step 1. 기준 Glass의 중심과 방향을 확정

가능한 방법:

- 정밀 Jig/Stopper로 기준 위치 고정
- Glass Edge를 측정해 370×470의 기하 중심 계산
- 외부 계측 기준으로 중심/방향 설정
- 설계 Mark 좌표와 Stage 좌표를 Calibration하여 기준 Pose 계산

Mark를 보면서 사람이 “대충 중앙”으로 맞추는 것만으로는 기준 정확도를 보장하기 어렵다. Teaching Glass가 실제로 어느 위치와 방향에 있어야 하는지 물리적 기준이 필요하다.

### Step 2. Mark별 Image 등록

각 Mark에 대해 다음을 등록한다.

- Mark Template 또는 Edge/Blob 검출 조건
- 예상 ROI와 Search ROI
- Polarity: 밝은 Mark인지 어두운 Mark인지
- 중심 정의: Pattern 중심, 원 중심, 교차선 교점 등
- Match Score와 Sub-pixel 적용 여부

세 Mark 모양이 동일하면 잘못 대응될 위험이 있다. 각 Mark의 예상 Stage 위치/ROI를 사용하거나 Mark 디자인을 서로 다르게 만들어 ID를 구분하는 것이 안전하다.

### Step 3. Mark 중심을 공통 Machine 좌표로 변환

Camera 한 대가 Mark마다 이동해 촬영한다면 각 Image의 Pixel 좌표는 서로 다른 Camera 위치에서 얻어진다.

```text
Mark Machine Position
= 촬영 당시 Camera/Stage Pose
 + Image 안에서 검출된 Pixel Offset의 Calibration 변환
```

보다 일반적으로:

```text
p_i(machine) = T_machine←camera(stage_i) × p_i(image)
```

세 Mark를 같은 Image에서 보지 않는다면 이 단계가 특히 중요하다. 각 Image의 `(x,y)`만 서로 빼서 각도를 구하면 잘못된 결과가 된다.

### Step 4. Reference Geometry 저장

두 가지 방식이 있다.

#### 방식 A: 설계 좌표 사용 — 권장

```text
q_A = (-150,+200)
q_B = (+150,+200)
q_C = (0,-200)
Glass Center q_Center = (0,0)
```

설계 좌표 `q_i`와 실제 검출 Machine 좌표 `p_i` 사이 Transform을 계산한다.

#### 방식 B: 잘 정렬된 기준 Glass의 실측 좌표 사용

Teaching 시 Mark Machine 좌표를 Reference로 저장한다.

```text
p_A_ref, p_B_ref, p_C_ref
```

이 방식은 간단하지만 Teaching Glass의 배치 오차가 모든 후속 Glass의 기준에 포함된다. 가능하면 설계 좌표와 정밀 기구 기준을 함께 사용한다.

## 7. X축 방향 Mark 2개로 회전각 계산하기

Mark A/B가 같은 설계 Y에 있고 좌우로 떨어져 있다고 하자.

```text
Reference:
A = (-a, b)
B = (+a, b)

Reference vector A→B = (2a, 0)
Reference angle = 0°
```

현재 검출한 Machine 좌표:

```text
A' = (x_A, y_A)
B' = (x_B, y_B)

dx = x_B - x_A
dy = y_B - y_A
```

현재 Glass 회전각:

```text
Theta = atan2(dy, dx)
```

기준 Pair가 완전히 수평이 아니라 Reference 각도 `Theta_ref`가 있다면:

```text
DeltaTheta = atan2(dy_cur, dx_cur)
           - atan2(dy_ref, dx_ref)
```

`atan(dy/dx)` 대신 `atan2(dy,dx)`를 사용해야 Quadrant와 `dx=0`을 올바르게 처리할 수 있다.

### Pair 중점과 Glass 중심

A/B 중점은:

```text
M_AB = (A' + B') / 2
```

설계상 A/B 중점은 `(0,b)`이지 Glass 중심 `(0,0)`이 아니다. 따라서 중점을 Glass 중심으로 착각하면 Y 방향으로 `b`만큼 틀린다.

회전행렬을 `R(Theta)`라 할 때 현재 Glass 중심 `T`는:

```text
T = M_AB - R(Theta) × (0,b)
```

즉 Mark Pair의 기준 중심 Offset까지 회전시켜 빼야 한다.

## 8. Y축 방향 Mark 2개로 각도 계산하기

Mark 두 개가 같은 X에 있고 위·아래로 배치되었다고 하자.

```text
Bottom = (x0,-b)
Top    = (x0,+b)

Reference vector Bottom→Top = (0,2b)
Reference angle = +90°
```

현재 검출 좌표에서:

```text
dx = x_Top - x_Bottom
dy = y_Top - y_Bottom

Measured vector angle = atan2(dy,dx)
Glass Theta = atan2(dy,dx) - 90°
```

일반식은 항상 같다.

```text
DeltaTheta = Measured Pair Angle - Reference Pair Angle
```

Pair 순서를 뒤집으면 각도가 180° 달라지므로 Bottom/Top 또는 Left/Right ID를 고정해야 한다.

## 9. 3개 Mark를 모두 사용하는 권장 방법

2개 Mark만으로도 이상적인 2D Rigid Transform의 X/Y/Theta를 계산할 수 있다. 세 번째 Mark는 다음 장점이 있다.

- 검출 오류와 잘못된 Mark 대응 확인
- 한 Mark가 오염되거나 가려진 상황 판별
- 위치 Noise를 평균화
- Mark 간 거리 변화로 Glass/Calibration 이상 검출
- 회전 및 중심 계산 Residual 확인

### 9.1 Rigid Transform 모델

Glass 중심 기준 설계 Mark 좌표를 `q_i`, 현재 Machine 좌표를 `p_i`라 하면:

```text
p_i = R(Theta) × q_i + T
```

여기서:

```text
R(Theta) = [ cosTheta  -sinTheta ]
           [ sinTheta   cosTheta ]

T = [ CenterX ]
    [ CenterY ]
```

`q_i`가 Glass 중심 `(0,0)` 기준이므로 Translation `T`가 곧 현재 Glass 중심의 Machine 좌표가 된다.

### 9.2 3점 최소제곱 Rigid Fit

Mark 3개를 모두 사용하는 일반적인 절차:

1. 설계 Mark 좌표의 중심 `q_bar`를 구한다.
2. 측정 Mark 좌표의 중심 `p_bar`를 구한다.
3. 각 Point에서 중심을 뺀 좌표로 최적 회전각을 구한다.
4. `T = p_bar - R(Theta)×q_bar`로 Translation을 구한다.
5. 각 Mark의 예측 위치와 측정 위치 차이인 Residual을 계산한다.

2D에서는 다음 합으로 회전각을 구할 수 있다.

```text
A = Σ(q'_x × p'_x + q'_y × p'_y)
B = Σ(q'_x × p'_y - q'_y × p'_x)

Theta = atan2(B, A)
```

여기서 `q' = q-q_bar`, `p' = p-p_bar`다.

이 방법은 특정 Pair 하나만 쓰는 것보다 세 Mark의 측정 Noise를 함께 반영한다.

### 9.3 Residual 검사

계산된 Pose로 각 Mark 위치를 예측한다.

```text
p_i_predicted = R(Theta) × q_i + T
residual_i = |p_i_measured - p_i_predicted|
```

Residual이 허용값보다 크면 다음 가능성이 있다.

- Mark 오검출 또는 잘못된 ID
- Camera/Stage Calibration 오류
- Stage Position 또는 Encoder 오류
- Glass Scale/변형/파손
- Mark Drawing 좌표 오류
- Camera Focus/조명 문제

이 경우 억지로 Align을 수행하지 말고 `Align Error`로 처리한다.

## 10. 370×470 Glass 수치 예제

설계 Mark:

```text
A = (-150,+200) mm
B = (+150,+200) mm
C = (0,-200) mm
```

실제 Glass가 기준보다 다음만큼 이동/회전했다고 가정한다.

```text
Center Translation T = (+2.000,-1.000) mm
Theta = +0.500° CCW
```

Camera/Stage Calibration 후 얻은 Mark 좌표가 다음과 같다고 하자.

```text
A' ≈ (-149.740, +197.683) mm
B' ≈ (+150.249, +200.301) mm
C' ≈ (  +3.745, -200.992) mm
```

### 10.1 A/B Pair로 각도 계산

```text
dx = 150.249 - (-149.740) ≈ 299.989 mm
dy = 200.301 - 197.683    ≈   2.618 mm

Theta = atan2(2.618, 299.989)
      ≈ +0.500°
```

### 10.2 A/B Pair 중점

```text
M_AB ≈ ((-149.740+150.249)/2,
        (197.683+200.301)/2)
     ≈ (0.255,198.992) mm
```

설계 Pair 중점 `(0,200)`을 0.5° 회전하면 약 `(-1.745,199.992)`가 된다.

```text
Glass Center T
= M_AB - R(0.5°)×(0,200)
≈ (0.255,198.992) - (-1.745,199.992)
≈ (+2.000,-1.000) mm
```

### 10.3 Mark C로 독립 검산

```text
R(0.5°)×(0,-200) ≈ (+1.745,-199.992)

T_C = C' - R(0.5°)×(0,-200)
    ≈ (+3.745,-200.992) - (+1.745,-199.992)
    ≈ (+2.000,-1.000) mm
```

A/B와 C가 같은 Glass 중심을 가리키므로 Geometry가 일관적이다.

## 11. 자동 Align 실행 로직

### 11.1 전체 흐름

```text
1. Align Recipe Load
   ↓
2. Mark A 예상 위치로 이동 → 촬영 → 중심 검출
   ↓
3. Mark B 예상 위치로 이동 → 촬영 → 중심 검출
   ↓
4. Mark C 예상 위치로 이동 → 촬영 → 중심 검출
   ↓
5. 세 Mark Pixel 좌표를 공통 Machine 좌표로 변환
   ↓
6. Mark ID/Score/거리/Triangle Geometry 검증
   ↓
7. 3점 Rigid Fit으로 Glass Center X/Y/Theta 계산
   ↓
8. Mark별 Residual 계산 및 허용 오차 검사
   ↓
9A. Physical: Stage X/Y/Theta 보정
또는
9B. Virtual: ROI/검사 좌표 Transform
   ↓
10. 필요 시 재촬영하여 최종 오차 확인
   ↓
11. Align Result와 Image 저장
```

### 11.2 Coarse-to-Fine Search

초기 Glass 위치 편차가 크다면:

1. 넓은 Search ROI와 낮은 배율/Coarse Parameter로 Mark를 찾는다.
2. 예상 위치를 갱신한다.
3. 작은 ROI와 Sub-pixel 방법으로 Mark 중심을 정밀 측정한다.
4. Score와 주변 유사 Pattern을 검증한다.

이 방식은 전체 Image를 매번 정밀 Matching하는 것보다 빠르고 오검출을 줄이기 쉽다.

### 11.3 Stage 보정 시 주의

계산된 Glass Error가 `(+2 mm,-1 mm,+0.5°)`라고 해서 장비에 항상 단순히 `(-2,+1,-0.5°)`를 입력하면 되는 것은 아니다.

이유:

- Stage 회전 Pivot이 Glass 중심과 다를 수 있음
- X/Y 명령이 Stage Local인지 Machine Fixed 좌표인지 다름
- Rotation 후 Translation의 의미가 달라짐
- Camera가 Stage 위에 있는지 고정 Frame인지 다름

정확한 보정은 Stage Command의 좌표 정의와 Pivot Calibration을 사용해 현재 Pose의 역변환을 적용한다. 처음에는 작은 Correction 후 재촬영하는 Closed-loop 방식으로 검증한다.

### 11.4 반복 Align

```text
Measure Pose Error
   ↓
Correction Command
   ↓
Stage Settle
   ↓
Re-measure
   ↓
Tolerance 이내? ── Yes → Align Complete
   │
   No
   ↓
Max Iteration 초과? ── Yes → Align Error
```

무한 반복하지 않도록 최대 반복 횟수와 최소 개선량을 둔다.

## 12. Mark 3개를 어떻게 역할 분담할까?

권장 방식은 **세 Mark 모두로 X/Y/Theta를 동시에 구하는 Rigid Fit**이다. 이해를 위해 역할을 나누면 다음처럼 볼 수 있다.

- A/B의 긴 X Baseline: 회전각에 강함
- A/B 중점: 상단 기준 위치 제공
- C: Y 방향 Geometry와 Glass 중심 검산
- 세 Point 전체: Translation/Rotation Noise 평균화와 Residual 검사

“A/B로 Theta만 계산하고 C로 Y만 계산”하는 순차 Logic도 만들 수 있지만 측정 Noise가 분리되어 일관성이 떨어질 수 있다. 세 Point를 한 Transform으로 Fit하고 각 Pair 결과는 진단용으로 사용하는 편이 일반적으로 깔끔하다.

## 13. Mark 간 거리가 회전 정밀도에 미치는 영향

두 Mark의 중심 검출 오차 표준편차를 각각 `σ`라고 하면 작은 오차에서 회전각 Noise는 대략 다음 경향을 가진다.

```text
σ_theta ≈ √2 × σ_position / Mark Baseline
```

Mark 중심 반복성이 `5 μm = 0.005 mm`, Baseline이 300 mm라면:

```text
σ_theta ≈ √2 × 0.005 / 300
        ≈ 0.00002357 rad
        ≈ 0.00135°
```

Baseline이 50 mm라면 약 `0.0081°`로 악화된다. 따라서 Mark는 가능한 한 멀리 배치하는 것이 회전 정밀도에 유리하다. 다만 Lens Distortion, Stage Travel, Glass 변형과 FOV 접근성도 고려한다.

## 14. 3개 Mark가 정말 필요한가?

### 2개 Mark

Rigid Body라는 전제에서 X/Y/Theta를 계산할 수 있다.

장점:

- 촬영 수와 Cycle Time 감소
- Logic 단순

한계:

- 한 Mark 오검출 시 검증할 여분이 없음
- Scale/Geometry 이상을 확인하기 어려움

### 3개 Mark

권장되는 이유:

- 과잉 결정(Over-determined)으로 Noise 평균화
- Pair 거리와 Triangle Shape 검증
- 하나의 잘못된 측정을 Residual로 탐지
- Glass 비정상/Calibration 이상 진단

### 3개보다 많은 Mark

큰 Glass에서 지역 변형, Camera/Stage Calibration, 여러 검사 영역의 Local Align을 확인할 때 유리하다. Cycle Time과 관리 복잡도가 증가한다.

## 15. Rigid, Similarity, Affine 중 무엇을 사용할까?

### Rigid Transform — 기본 권장

```text
X/Y Translation + Rotation
```

Glass가 강체이고 Camera/Stage Calibration이 정상이라면 Align은 Rigid가 기본이다.

### Similarity Transform

```text
Translation + Rotation + Uniform Scale
```

온도/공정으로 Glass Scale 변화가 의미 있게 있고 검사에서 이를 모델링해야 할 때 고려한다. 단, Align이 Calibration 오류를 Scale로 숨기지 않도록 주의한다.

### Affine Transform

```text
Translation + Rotation + X/Y Scale + Shear
```

Camera Perspective, Stage 직교도 오류 또는 실제 기판 변형을 흡수할 수 있지만 물리적 원인을 숨길 위험이 있다. 단순 Glass X/Y/Theta Align에는 과도할 수 있다.

> [!IMPORTANT]
> Transform 자유도를 늘리면 Residual은 작아지기 쉽지만 “장비가 정확해진 것”은 아니다. Glass는 강체라는 물리 모델에 맞는 최소 자유도를 사용한다.

## 16. 자동 Align Recipe에 저장할 항목

| 영역 | 저장 항목 |
|---|---|
| Mark 정의 | ID, Template, Polarity, 중심 정의, 예상 크기 |
| 설계 Geometry | Glass Size, 중심 기준 Mark X/Y 좌표 |
| Search | 예상 Stage Position, Search ROI, Search Range |
| Camera | Camera ID, Exposure, Gain, Light Recipe |
| Calibration | Pixel→Machine Transform ID/Version |
| Stage | Rotation Pivot, Axis Direction, Unit, Settle 조건 |
| 판정 | Match Score, Position/Angle/Residual 허용값 |
| 반복 | Max Iteration, 최소 개선량, Timeout |
| 결과 저장 | Mark Image, 좌표, Score, X/Y/Theta, Residual |

## 17. 자동 Align 실패 상황과 대응

### 최초 Search에서 아무 Mark도 보이지 않음

- Nominal Loading Position과 Drawing 좌표가 Camera FOV 안으로 연결되는지 확인
- Glass Edge/Corner 기반 Coarse Align 또는 넓은 FOV Camera 사용
- 제한된 Raster/Spiral Search 범위와 Timeout 설정
- 작업자 Teaching 위치를 초기 Seed로 저장
- FOV 밖 Mark를 Image Processing Parameter 변경으로 찾으려 하지 않음

### Mark를 찾지 못함

- Search ROI 확대 전 제품 범위와 충돌 여부 확인
- Exposure/조명 상태 확인
- Coarse Search 또는 Edge/Blob Backup 검토
- 찾지 못한 Mark를 임의 좌표로 대체하지 않음

### 잘못된 Mark를 찾음

- 예상 위치와 이동 허용 범위 확인
- Mark별 고유 ID 또는 Template 사용
- Pair 거리와 Triangle Geometry 검증
- 3점 Rigid Fit Residual 검사

### 두 Mark 각도와 세 번째 Mark가 맞지 않음

- Camera별/Stage Pose Calibration 오류
- 잘못된 Mark 순서
- Glass 방향 반전 또는 180° 투입
- Glass/Mark 파손
- Stage Backlash 또는 Encoder 문제

### Align 후에도 재측정 오차가 큼

- Rotation Pivot 보정 오류
- Stage Local/Global 좌표 혼동
- Correction 순서 문제
- Stage Settle/진동
- Calibration Scale/Rotation 오류

## 18. 흔한 오해

1. **“A/B 중점이 Glass 중심이다.”**  
   Pair가 Glass 중심을 지나지 않으면 설계 Offset을 회전해 보정해야 한다.

2. **“Mark Image만 등록하면 Glass 중심을 안다.”**  
   Mark 중심과 Glass 중심 사이의 설계 Geometry가 필요하다.

3. **“Image Pixel 좌표끼리 빼면 바로 각도가 나온다.”**  
   여러 촬영 위치의 Image는 공통 Machine 좌표로 먼저 변환해야 한다.

4. **“두 Mark를 각각 중앙에 맞추면 자동으로 Align된다.”**  
   각 촬영 중 Stage를 개별 이동하면 Glass Pose가 바뀔 수 있다. 측정 Pose와 보정 Pose를 분리해야 한다.

5. **“3점이면 Affine을 사용하는 것이 더 정확하다.”**  
   강체 Glass에는 Rigid Fit이 물리적으로 맞고 Affine은 오류를 숨길 수 있다.

6. **“계산 Error에 음수만 붙여 Stage에 명령하면 된다.”**  
   Rotation Pivot과 Stage 좌표 Command 의미를 반영한 역변환이 필요하다.

7. **“한 번 보정했으면 재촬영할 필요가 없다.”**  
   초기 개발과 정밀 Align에서는 Closed-loop 재확인으로 보정 모델을 검증해야 한다.

8. **“Template Image가 없으면 Align 자체가 불가능하다.”**  
   원·십자·사각형처럼 Geometry로 정의할 수 있는 Mark는 Template 없이도 검출할 수 있다.

9. **“Template가 없더라도 AI가 Image에서 알아서 Align Mark를 고른다.”**  
   Mark 정의, 예상 위치, Geometry 또는 학습/Template 기준 없이 특정 Pattern을 Align Mark로 식별할 수는 없다.

10. **“Glass가 회전하면 Mark 중심도 정의할 수 없다.”**  
    원 중심, 선 교점, Corner 중심 또는 회전 Pattern Matching으로 현재 중심을 측정할 수 있다.

## 19. 면접 및 실무 확인 질문

### Q1. Align과 Calibration의 차이는?

**핵심 답변**  
Calibration은 Image Pixel과 Machine 좌표계 사이의 지속적인 관계를 정하고, Align은 그 Calibration을 사용해 매 Glass의 현재 X/Y/Theta 편차를 계산한다.

### Q2. 2개 Mark로 X/Y/Theta를 계산할 수 있는가?

**핵심 답변**  
Rigid Body 전제라면 가능하다. Pair Vector로 Theta를 구하고 한 Point 또는 Pair 중점과 설계 Offset으로 Translation을 구한다. 세 번째 Mark는 Noise 평균화와 오류 검증에 사용한다.

### Q3. 왜 Mark를 멀리 배치하는 것이 좋은가?

**핵심 답변**  
같은 위치 측정 오차에서 Baseline이 길수록 각도 오차가 작아지기 때문이다. 다만 Stage 범위, 왜곡과 Glass 변형을 함께 고려한다.

### Q4. 왜 3개 Mark를 한 번에 Rigid Fit하는가?

**핵심 답변**  
특정 Pair 하나에 의존하지 않고 세 측정의 Noise를 평균화하며, Mark별 Residual로 오검출과 Geometry 이상을 확인할 수 있기 때문이다.

### Q5. Camera 한 대로 Mark를 순차 촬영할 때 가장 중요한 것은?

**핵심 답변**  
각 촬영의 Stage/Camera Pose와 Image Pixel Offset을 결합하여 모든 Mark 중심을 동일한 Machine 좌표계로 변환하는 것이다.

## 20. 8일차 실습 문제

### 실습 1. 본인 장비 좌표계 그리기

다음을 한 그림에 표시한다.

- Glass 중심과 370×470 외곽
- Mark A/B/C의 실제 Drawing 좌표
- Image +x/+y
- Machine +X/+Y/+Theta
- Stage 회전 Pivot
- Camera 이동 방향 또는 Glass 이동 방향

### 실습 2. Pair 공식 손 계산

Mark Pair 기준 좌표와 현재 측정 좌표를 정해 다음을 계산한다.

- Reference Pair Angle
- Current Pair Angle
- DeltaTheta
- Pair Midpoint
- Pair Midpoint에서 Glass Center까지의 회전된 Offset

### 실습 3. Align Recipe 설계

[[#16. 자동 Align Recipe에 저장할 항목|Recipe 표]]를 기준으로 현재 장비에서 이미 알고 있는 값과 아직 모르는 값을 나눈다.

### 실습 4. 실패 판정표 작성

다음 상황의 처리 정책을 정한다.

- Mark 1개 Match 실패
- 3개 Match 성공이지만 한 Mark Residual 초과
- Mark 간 거리 0.2 mm 변화
- Align 보정 후 오차가 오히려 증가
- Max Iteration 초과

## 21. 권장 구현 순서

코드를 작성하기 전에 다음 순서로 작은 검증을 한다.

1. 고정된 기준 Glass에서 Mark 중심 반복 측정 정밀도를 확인한다.
2. Mark마다 Image Pixel을 Machine 좌표로 변환하는 결과를 확인한다.
3. 사람이 Glass를 X/Y로 이동했을 때 계산 Center가 같은 양만큼 움직이는지 확인한다.
4. Glass를 알려진 각도로 회전시켜 계산 Theta를 비교한다.
5. 3점 Rigid Fit Residual과 Pair별 Theta를 비교한다.
6. Stage 보정 없이 Virtual ROI Transform부터 검증한다.
7. 작은 Physical Correction을 적용하고 재촬영한다.
8. Rotation Pivot Compensation을 검증한다.
9. 반복 Align과 실패 정책을 추가한다.
10. Recipe/Result/Review 저장을 연결한다.

## 22. 핵심 결론

- 🔴 Mark 3개의 Image를 등록하는 것보다 Mark와 Glass 중심 사이 Geometry를 등록하는 것이 핵심이다.
- 🔴 모든 Mark 중심을 먼저 하나의 Machine 좌표계로 변환해야 한다.
- 🔴 수평 Pair의 각도는 `atan2(dy,dx)`, 수직 Pair는 그 값에서 기준 90°를 뺀다.
- 🔴 Pair 중점이 Glass 중심이 아니라면 회전된 설계 Offset을 보정해야 한다.
- 🔴 권장 방식은 3개 Mark 전체의 2D Rigid Fit으로 Center X/Y/Theta를 동시에 계산하는 것이다.
- 🔴 세 번째 Mark는 Residual, 거리, Triangle Geometry를 통해 오검출과 Calibration 이상을 찾는다.
- 🔴 Stage 보정에는 Rotation Pivot과 좌표 Command 정의를 반영한 역변환이 필요하다.
- 🔴 최초 개발에서는 보정 후 재촬영하는 Closed-loop Align으로 정확성을 검증한다.
- 🟠 Align Result에는 Mark별 좌표/Score/Image, Center X/Y/Theta와 Residual을 저장한다.
- 🟠 큰 Glass에서는 Global Align 후 검사 영역별 Local Align이 추가로 필요할 수 있다.
- 🔴 실제 Template Image는 검출 방식에 따라 선택 사항이지만 Mark의 사전 정의는 필수다.
- 🔴 최초 Image가 없으면 CAD/Nominal 위치와 Geometry Finder 또는 작업자 Teaching으로 첫 Template를 만든다.
- 🔴 Glass가 회전되어도 회전 허용 검색 또는 Geometry Fit으로 각 Mark 중심을 먼저 측정할 수 있다.

## 8일차 학습 완료 체크

- [ ] Glass 중심 기준으로 Mark A/B/C의 실제 좌표를 적었다.
- [ ] Image 좌표와 Machine 좌표의 축 방향을 그렸다.
- [ ] 수평/수직 Mark Pair로 Theta를 계산할 수 있다.
- [ ] Pair 중점에서 Glass 중심을 구할 때 Offset 회전이 필요한 이유를 안다.
- [ ] 3점 Rigid Fit의 입력과 출력, Residual 의미를 설명한다.
- [ ] Camera 한 대의 순차 촬영 좌표를 Machine 좌표로 합치는 방법을 이해한다.
- [ ] Align Recipe와 자동 실행 상태 흐름을 설계했다.
- [ ] Rotation Pivot을 포함한 Stage 보정 검증 계획을 세웠다.
- [ ] 내 Mark가 Template 방식인지 Geometry 방식인지 선택하고 근거를 적었다.
- [ ] 최초 Template가 없을 때 Mark를 FOV 안으로 가져오는 Coarse Search 방법을 정했다.
