# Chapter 5. FOV · Resolution · Magnification 집중 계산

> Phase 4 · 5일차 · 예상 학습 시간: 10~14시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 FOV, Sensor Size, Pixel Count, Pixel Pitch, Magnification의 연결
- 🔴 Object Space Sampling(`μm/pixel`)과 Feature의 Pixel 점유 수
- 🔴 0.25×/0.5×/1×/2× 배율 비교
- 🔴 검사 FOV와 Sampling을 동시에 만족하는 최소 Pixel Count 역산
- 🔴 Margin을 포함한 실제 요구 FOV 산정
- 🔴 설계값과 Calibration 측정값 교차 검산
- 🟠 Width/Height/Diagonal 조건의 독립 검토
- 🟠 Camera ROI, Binning, Resize가 계산에 미치는 영향
- 🟠 Sampling 요구와 Optical Resolution 요구의 분리

### 실무 목표

Camera와 Lens 사양을 받아 FOV와 `μm/pixel`을 계산하는 데서 끝나지 않고, 검사 대상 크기와 최소 Feature 요구사항으로부터 필요한 Image Pixel Count와 배율을 역산한다. 서로 동시에 만족할 수 없는 요구사항을 계산으로 찾아내고 Camera, Lens, Multi-shot 또는 검사 사양을 조정할 수 있어야 한다.

---

## 2. 선수 지식

- [[03-camera-pixel|Chapter 3]]의 Pixel Pitch와 Object Space 관계
- [[04-lens-optics|Chapter 4]]의 Camera-Lens-Object System
- 단위 변환: `1 mm = 1,000 μm`
- 비율, 반비례, 올림(`ceil`)

### 2.1 이번 Chapter의 기본식

```text
Sensor Size = Pixel Count × Pixel Pitch
FOV = Sensor Size ÷ Magnification
Object Sampling = Pixel Pitch ÷ Magnification
Object Sampling = FOV ÷ Image Pixel Count
Feature Pixels = Feature Size ÷ Object Sampling
Required Pixel Count = Required FOV ÷ Required Sampling
```

길이 단위를 먼저 통일해야 한다. FOV가 mm이면 μm로 변환한 후 `μm/pixel`과 계산한다.

> [!WARNING]
> 이 Chapter의 `Resolution`은 문맥상 주로 **Object Space Sampling(μm/pixel)**을 뜻한다. Optical Resolution, 반복 정밀도, 측정 정확도와 같은 말이 아니다.

---

## 3. 핵심 개념

### 3.1 FOV란 무엇인가?

**FOV(Field of View)**는 한 Frame에서 실제 Object Space로 보이는 범위다. 보통 Width×Height를 mm로 표현한다.

FOV는 다음을 모두 포함해야 한다.

- 검사 대상의 최대 크기
- 제품 투입 위치 편차
- Align Pattern과 검사 ROI
- 회전 시 Corner가 움직이는 범위
- 기구 및 Calibration 오차 Margin

제품 폭이 10 mm라고 FOV를 정확히 10 mm로 잡으면 가장자리 Feature가 잘리거나 Align이 실패할 수 있다.

### 3.2 FOV와 Sampling의 직접 관계

```text
Object Sampling = FOV / Pixel Count
```

같은 Camera Pixel Count에서 FOV가 넓어지면 한 Pixel이 담당하는 Object 영역이 커진다. 즉 더 넓게 보지만 Sampling은 거칠어진다.

```text
같은 2048 pixel Camera

FOV 10 mm → 4.8828 μm/pixel
FOV 20 mm → 9.7656 μm/pixel
```

### 3.3 배율과 Trade-off

고정 Sensor에서:

```text
Magnification ↑ → FOV ↓ → μm/pixel ↓ → Feature Pixel 수 ↑
Magnification ↓ → FOV ↑ → μm/pixel ↑ → Feature Pixel 수 ↓
```

배율을 높이면 작은 특징이 더 많은 Pixel로 나타나지만, 제품 전체 또는 Align Pattern이 FOV 밖으로 나갈 수 있다. 또한 DOF, Focus 민감도 및 조명 배치도 영향을 받는다.

### 3.4 배율별 기준표

Camera:

- 2048×2048
- Pixel Pitch = 3 μm
- Sensor = 6.144×6.144 mm

| Magnification | FOV Width×Height | Object Sampling | 24 μm Feature 점유 |
|---:|---:|---:|---:|
| 0.25× | 24.576×24.576 mm | 12 μm/pixel | 2 pixel |
| 0.5× | 12.288×12.288 mm | 6 μm/pixel | 4 pixel |
| 1× | 6.144×6.144 mm | 3 μm/pixel | 8 pixel |
| 2× | 3.072×3.072 mm | 1.5 μm/pixel | 16 pixel |

이는 Sampling 비교다. 24 μm Feature의 실제 Contrast와 형태가 2/4/8/16 Pixel에 이상적으로 보인다는 보장은 없다.

### 3.5 Feature가 몇 Pixel을 차지하는가?

```text
Feature Pixels = Feature Size / μm-per-pixel
```

20 μm Defect와 5 μm/pixel이라면:

```text
20 μm / 5 μm/pixel = 4 pixel
```

하지만 실제 Scratch Width, Particle Diameter, Edge Transition은 다른 방식으로 Pixel에 나타난다. “최소 4 Pixel” 같은 규칙은 알고리즘과 품질 목표에 맞춰 검증된 내부 기준이어야 한다.

### 3.6 요구사항 역산

FOV와 필요한 Sampling이 주어졌다면 최소 Pixel Count는:

```text
Required Pixel Count = Required FOV / Maximum Allowed μm-per-pixel
```

12 mm FOV에서 3 μm/pixel 이하가 필요하다면:

```text
12 mm = 12,000 μm
12,000 / 3 = 4,000 pixel
```

따라서 Width가 최소 4000 Pixel인 Camera가 필요하다. Height 방향도 별도로 계산하고 실제 Camera Resolution 후보로 올림한다.

### 3.7 배율 역산

Camera Pixel Pitch `p`와 목표 Object Sampling `r`로 필요한 최소 배율을 구할 수 있다.

```text
M = p / r
```

3 μm Pixel Camera에서 2 μm/pixel이 필요하면:

```text
M = 3 / 2 = 1.5×
```

그러나 이 배율에서 필요한 FOV도 만족하는지 반드시 확인한다. 4096 Pixel Sensor라면 Sensor Width는 12.288 mm이고 FOV는 `12.288/1.5=8.192 mm`다. 12 mm FOV 요구와 동시에 만족하지 못한다.

### 3.8 FOV와 Sampling 동시 만족 조건

Camera Pixel Pitch와 배율은 FOV와 Sampling 양쪽에 들어가지만 다음 항등식이 핵심이다.

```text
FOV / Sampling = Pixel Count
```

따라서 FOV 12 mm와 2 μm/pixel을 동시에 요구하면:

```text
12,000 μm / 2 μm/pixel = 6,000 pixel
```

가로 최소 6000 Pixel이 필요하다. 배율만 변경해 Pixel Count 부족을 해결할 수 없다.

대안:

- 더 높은 Resolution Camera
- FOV 축소
- 허용 Sampling 완화
- Camera 여러 대 또는 Multi-shot/Tiling
- 검사 항목별 Camera 분리

### 3.9 Margin 산정

제품 Width가 10 mm이고 좌우 위치 편차가 각각 최대 ±0.5 mm라면 최소 FOV는 단순히 10 mm가 아니다.

```text
Minimum FOV Width = Product Width + 2 × Position Variation + Safety Margin
```

양쪽 Safety Margin을 0.25 mm씩 추가하면:

```text
10 + 2×0.5 + 2×0.25 = 11.5 mm
```

Rotation이 있다면 Axis-aligned Bounding Box가 더 커진다. Width `W`, Height `H`의 Rectangle을 `θ`만큼 회전했을 때 필요한 Bounding Box는:

```text
Rotated Width  = |W cosθ| + |H sinθ|
Rotated Height = |W sinθ| + |H cosθ|
```

### 3.10 설계값과 Calibration 값

설계 계산:

```text
Pixel Pitch / Nominal Magnification
```

실측 계산:

```text
Known Object Distance / Measured Pixel Distance
```

실제 Measurement에는 Calibration 값을 사용한다. 설계값은 후보 선정과 예상 성능에, 실측값은 장비 좌표·치수 변환에 사용한다.

### 3.11 Width와 Height를 따로 확인

가로 조건만 만족하고 세로 FOV가 부족할 수 있다. Camera Resolution과 Sensor Size는 비율이 다를 수 있고 제품 Rotation이 Height 요구를 키울 수 있다.

```text
Horizontal: FOV_x / N_x
Vertical:   FOV_y / N_y
```

정사각 Pixel이고 왜곡이 작다면 X/Y Scale이 비슷해야 하지만 Calibration에서 각각 확인한다.

### 3.12 Camera ROI, Binning, Resize

- Camera ROI: Sensor 일부를 읽으므로 FOV가 줄지만 1:1 Readout이면 μm/pixel은 유지
- 2×2 Binning: 출력 Pixel 수가 절반이고 Output Pixel당 Object 영역은 보통 2배
- Software Crop: FOV는 줄지만 원본 μm/pixel 유지
- Resize: 출력 배열 Sampling 표현이 변하지만 새 Optical Detail은 생성되지 않음

같은 `1024×1024` 출력이라도 어떤 과정으로 만들어졌는지 알아야 올바르게 계산한다.

---

## 4. 그림으로 이해하기

### 4.1 설계 흐름

```text
Inspection Requirement
├── Product Size + Position/Rotation Margin → Required FOV
└── Minimum Feature + Required Pixels       → Required μm/pixel
                       │
                       ▼
Required Pixel Count = FOV / μm-per-pixel
                       │
                       ▼
Camera Resolution Candidate
                       │
                       ▼
Pixel Pitch / Magnification → Lens Candidate
                       │
                       ▼
WD / DOF / MTF / Distortion / Light 검증
                       │
                       ▼
Calibration + Sample Test
```

### 4.2 FOV와 Detail의 줄다리기

```text
Wide FOV                              Narrow FOV
┌────────────────────────┐            ┌──────────┐
│ product + margin       │            │ detail   │
│ small feature = 2 px   │            │ = 8 px   │
└────────────────────────┘            └──────────┘
   낮은 배율, 거친 Sampling               높은 배율, 촘촘한 Sampling
```

### 4.3 요구사항 충돌

```text
FOV 12 mm / 2 μm-per-pixel = 6000 horizontal pixels required

4096 px Camera
├── FOV를 12 mm로 맞추면 2.93 μm/px
└── 2 μm/px로 맞추면 FOV는 8.192 mm

배율 변경만으로 두 조건을 동시에 만족할 수 없음
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Camera/Lens 사양 협의

“5 MP Camera”보다 `필요 FOV`, `목표 μm/pixel`, `Feature당 최소 Pixel`, `WD`, `DOF`를 먼저 제시해야 비전 엔지니어가 적절한 조합을 검토할 수 있다.

### Align ROI 확보

검사 ROI만 가까스로 FOV에 들어오더라도 제품이 이동·회전하면 Fiducial이 잘릴 수 있다. Align Search Range와 회전 Bounding Box를 FOV Margin에 포함한다.

### Recipe 변경

제품 크기가 커진 새 Recipe가 기존 FOV를 초과할 수 있다. Parameter만 바꾸기 전에 Optical Configuration의 적용 가능 범위를 검사한다.

### Multi-shot 검사

한 Frame에서 넓은 FOV와 미세 Sampling을 동시에 만족할 수 없으면 Stage 이동 후 여러 Frame을 촬영한다. Stitching 오차, Cycle Time, Overlap, 좌표 Calibration을 추가 고려한다.

### Camera ROI 최적화

검사 영역이 Sensor 일부에만 있고 제품 편차가 작다면 Camera ROI로 Frame Rate와 대역폭을 개선할 수 있다. 단, μm/pixel이 좋아지는 것은 아니며 FOV만 줄어든다.

---

## 6. 숫자로 이해하기

### 예제 1: 0.25×~2× 전체 비교

Camera: `2048×2048`, `3 μm`

```text
Sensor Width = 2048 × 3 μm = 6.144 mm
```

| M | FOV | μm/pixel | 30 μm Feature |
|---:|---:|---:|---:|
| 0.25× | 24.576 mm | 12 | 2.5 pixel |
| 0.5× | 12.288 mm | 6 | 5 pixel |
| 1× | 6.144 mm | 3 | 10 pixel |
| 2× | 3.072 mm | 1.5 | 20 pixel |

### 예제 2: FOV로 Sampling과 Feature Pixel 계산

조건:

- Horizontal FOV = 10 mm
- Image Width = 2048 pixel
- Feature Width = 20 μm

```text
Sampling = 10,000 μm / 2048 pixel
         = 4.8828125 μm/pixel

Feature Pixels = 20 μm / 4.8828125 μm/pixel
               = 4.096 pixel
```

### 예제 3: 최소 Pixel Count 역산

조건:

- Required FOV = 18 mm
- Feature = 30 μm
- 내부 기준: Feature가 최소 5 Pixel

허용 Sampling:

```text
30 μm / 5 pixel = 6 μm/pixel
```

필요 Pixel Count:

```text
18,000 μm / 6 μm/pixel = 3000 pixel
```

가로 3000 Pixel 이상의 Camera가 필요하다. 실제 후보가 3072 또는 4096 Pixel이면 그 후보의 Height/FOV도 별도로 확인한다.

### 예제 4: Rotation Margin

제품 크기 `W=10 mm`, `H=6 mm`, 최대 회전 `θ=5°`라면:

```text
Rotated Width
= 10×cos5° + 6×sin5°
≈ 10.485 mm

Rotated Height
= 10×sin5° + 6×cos5°
≈ 6.849 mm
```

여기에 Translation 편차와 Safety Margin을 추가해야 한다.

### 예제 5: 설계값과 실측값 오차

설계 Sampling이 `6 μm/pixel`, Calibration Target 실측이 `6.08 μm/pixel`이면:

```text
Relative Difference
= |6.08 - 6.00| / 6.00 × 100
≈ 1.333%
```

이 차이를 무시하고 1000 Pixel을 6 mm로 계산하면 실제 Scale 기준으로는 6.08 mm여서 0.08 mm 차이가 난다.

---

## 7. C++ 구현

### FOV 요구사항 후보 평가기

```cpp
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <stdexcept>

struct AxisRequirement final {
    double requiredFovMm{};
    double minimumFeatureUm{};
    double requiredPixelsPerFeature{};
};

struct AxisDesign final {
    std::size_t availablePixels{};
    double pixelPitchUm{};
    double magnification{};
};

struct AxisEvaluation final {
    double sensorSizeMm{};
    double actualFovMm{};
    double objectUmPerPixel{};
    double featurePixels{};
    std::size_t minimumRequiredPixels{};
    bool fovSatisfied{};
    bool samplingSatisfied{};
};

[[nodiscard]] bool IsPositiveFinite(const double value) noexcept
{
    return std::isfinite(value) && value > 0.0;
}

[[nodiscard]] AxisEvaluation EvaluateAxis(
    const AxisRequirement& requirement,
    const AxisDesign& design)
{
    if (!IsPositiveFinite(requirement.requiredFovMm) ||
        !IsPositiveFinite(requirement.minimumFeatureUm) ||
        !IsPositiveFinite(requirement.requiredPixelsPerFeature) ||
        design.availablePixels == 0 ||
        !IsPositiveFinite(design.pixelPitchUm) ||
        !IsPositiveFinite(design.magnification)) {
        throw std::invalid_argument{"All dimensions must be positive"};
    }

    const double maximumUmPerPixel =
        requirement.minimumFeatureUm /
        requirement.requiredPixelsPerFeature;
    const double requiredFovUm = requirement.requiredFovMm * 1000.0;
    const auto minimumRequiredPixels = static_cast<std::size_t>(
        std::ceil(requiredFovUm / maximumUmPerPixel));

    const double sensorSizeMm =
        static_cast<double>(design.availablePixels) *
        design.pixelPitchUm / 1000.0;
    const double actualFovMm = sensorSizeMm / design.magnification;
    const double objectUmPerPixel =
        design.pixelPitchUm / design.magnification;
    const double featurePixels =
        requirement.minimumFeatureUm / objectUmPerPixel;

    constexpr double tolerance = 1e-12;
    return {
        sensorSizeMm,
        actualFovMm,
        objectUmPerPixel,
        featurePixels,
        minimumRequiredPixels,
        actualFovMm + tolerance >= requirement.requiredFovMm,
        featurePixels + tolerance >= requirement.requiredPixelsPerFeature
    };
}

[[nodiscard]] double CalculateRotatedBoundingWidthMm(
    const double widthMm,
    const double heightMm,
    const double angleDegrees)
{
    if (!IsPositiveFinite(widthMm) || !IsPositiveFinite(heightMm) ||
        !std::isfinite(angleDegrees)) {
        throw std::invalid_argument{"Invalid rectangle or angle"};
    }

    constexpr double pi = 3.14159265358979323846;
    const double radians = angleDegrees * pi / 180.0;
    return std::abs(widthMm * std::cos(radians)) +
           std::abs(heightMm * std::sin(radians));
}
```

### Unit Test

```cpp
#include <cassert>
#include <cmath>

[[nodiscard]] bool NearlyEqual(
    const double lhs,
    const double rhs,
    const double tolerance = 1e-9)
{
    return std::abs(lhs - rhs) <= tolerance;
}

void TestHalfMagnificationCandidate()
{
    const AxisRequirement requirement{12.0, 30.0, 5.0};
    const AxisDesign design{2048, 3.0, 0.5};
    const auto result = EvaluateAxis(requirement, design);

    assert(NearlyEqual(result.sensorSizeMm, 6.144));
    assert(NearlyEqual(result.actualFovMm, 12.288));
    assert(NearlyEqual(result.objectUmPerPixel, 6.0));
    assert(NearlyEqual(result.featurePixels, 5.0));
    assert(result.minimumRequiredPixels == 2000);
    assert(result.fovSatisfied);
    assert(result.samplingSatisfied);
}

void TestRequirementConflict()
{
    // 12 mm FOV at 2 um/pixel requires at least 6000 pixels.
    const AxisRequirement requirement{12.0, 10.0, 5.0};
    const AxisDesign design{4096, 3.0, 1.5};
    const auto result = EvaluateAxis(requirement, design);

    assert(result.minimumRequiredPixels == 6000);
    assert(NearlyEqual(result.objectUmPerPixel, 2.0));
    assert(result.samplingSatisfied);
    assert(!result.fovSatisfied); // actual FOV = 8.192 mm
}

void TestRotatedWidth()
{
    const double width = CalculateRotatedBoundingWidthMm(10.0, 6.0, 5.0);
    assert(std::abs(width - 10.485) < 0.001);
}
```

### 코드에서 봐야 할 점

1. 요구사항과 Camera/Lens 설계값을 별도 구조체로 나눴다.
2. 최소 Pixel Count는 부족하지 않도록 `std::ceil`로 올림한다.
3. FOV 만족과 Sampling 만족을 별도 Boolean으로 반환한다.
4. 한 조건만 만족하는 후보를 합격 처리하지 않는다.
5. 단위가 변수명에 포함되어 mm/μm 혼용을 줄인다.
6. 실제 시스템에서는 X/Y 축을 각각 평가하고 WD, DOF, MTF, Distortion을 추가한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: 제품 크기만 FOV에 반영

- 증상: 위치 편차나 회전 시 제품/Align Pattern이 잘림
- 대응: Translation, Rotation Bounding Box, Safety Margin 포함

### 문제 2: 가로만 계산하고 세로 FOV 누락

- 증상: Landscape 제품은 들어오지만 회전 시 Height 방향이 잘림
- 대응: X/Y 요구사항과 Sensor Aspect Ratio를 독립 검토

### 문제 3: 최소 Feature가 1 Pixel이면 된다고 가정

- 증상: Defect 위치와 조명 변화에 따라 검출률 급변
- 대응: 알고리즘별 필요 Sampling을 Sample Test로 정의

### 문제 4: 배율만 올려 요구사항을 해결하려 함

- 증상: Sampling은 만족하지만 FOV 부족
- 대응: `Required Pixels = FOV/Sampling`으로 Pixel Count부터 검토

### 문제 5: Camera ROI와 Binning을 동일하게 취급

- 증상: Output Image 크기는 같지만 Scale 계산이 틀림
- 대응: Sensor Readout Mode와 Output Pixel 의미를 Recipe/Calibration에 기록

### 문제 6: 명목 FOV로 치수 계산

- 증상: 장비별 측정값이 일정 비율로 다름
- 대응: Calibration Target 기반 실측 Scale과 Residual 사용

### 문제 7: Multi-shot 선택 후 Cycle Time 누락

- 증상: 광학 요구는 만족하지만 생산성 미달
- 대응: Stage Move/Settle/Trigger/Processing/Stitching 시간 예산 포함

---

## 9. 흔한 오해

1. **“FOV가 넓고 Resolution도 좋은 Lens를 고르면 된다.”**  
   고정 Pixel Count에서는 FOV와 μm/pixel이 직접 연결되므로 동시 요구는 Camera Pixel Count를 결정한다.

2. **“배율을 높이면 모든 요구사항이 좋아진다.”**  
   Sampling은 좋아지지만 FOV와 DOF는 줄어든다.

3. **“2 μm/pixel이면 2 μm Defect가 1 Pixel로 정확히 보인다.”**  
   Sampling 간격일 뿐이며 Optical Blur와 Pixel Aperture로 에너지가 분산된다.

4. **“Camera ROI를 줄이면 μm/pixel이 좋아진다.”**  
   1:1 Crop이면 Scale은 유지되고 FOV와 데이터량만 줄어든다.

5. **“Image를 2배 Resize하면 Resolution이 2배다.”**  
   배열 크기는 늘지만 Optical Information은 늘지 않는다.

6. **“계산상 4.1 Pixel이면 언제나 4 Pixel로 보인다.”**  
   위치, Orientation, Blur, Threshold에 따라 실제 표현은 달라진다.

7. **“설계 배율로 치수를 계산해도 충분하다.”**  
   실제 장착 후 Calibration Scale을 사용해야 한다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. FOV와 Resolution의 관계를 설명해 주세요.

**초보자가 이해할 수 있는 답변**  
같은 Pixel 수에서 더 넓은 영역을 보면 한 Pixel이 담당하는 실제 크기가 커져 작은 특징 표현이 거칠어집니다.

**실무자 답변**  
Object Sampling은 `FOV/Pixel Count`다. 고정 Camera에서 FOV가 증가하면 μm/pixel이 증가한다. 요구 FOV와 허용 μm/pixel로 최소 Pixel Count를 먼저 역산하고 Lens 배율, WD, MTF와 DOF를 검토한다.

**면접용 30초 답변**  
“같은 Camera에서는 `μm/pixel = FOV/Pixel Count`이므로 FOV를 넓히면 Sampling이 거칠어집니다. 그래서 제품 크기와 위치 Margin으로 FOV를, 최소 Feature와 필요한 Pixel 수로 μm/pixel을 정한 뒤 두 조건으로 최소 Camera Resolution을 계산합니다.”

### Q2. Magnification이 0.5×에서 1×가 되면 무엇이 바뀌나요?

**초보자가 이해할 수 있는 답변**  
배율이 두 배가 되므로 보이는 범위와 물체 기준 μm/pixel은 절반이 됩니다.

**실무자 답변**  
고정 Sensor에서 FOV와 Object Sampling은 배율에 반비례한다. Feature Pixel 수는 두 배가 되지만 DOF 감소, Focus 민감도, WD/조명 배치 변화를 함께 평가한다.

**면접용 30초 답변**  
“0.5×에서 1×로 올리면 같은 Sensor의 FOV와 μm/pixel은 절반이 되고 Feature가 차지하는 Pixel 수는 두 배가 됩니다. 대신 제품 전체가 FOV에 들어오는지와 DOF, Focus, WD 조건을 다시 확인해야 합니다.”

### Q3. 12 mm FOV에서 2 μm/pixel이 필요하면 최소 몇 Pixel인가요?

**초보자가 이해할 수 있는 답변**  
12 mm는 12,000 μm이므로 2로 나누면 가로 6000 Pixel이 필요합니다.

**실무자 답변**  
이상적 최소 Width는 `ceil(12,000/2)=6000 pixel`이다. 실제 후보 Resolution, Margin, Camera ROI, Optical MTF와 Feature별 최소 Sampling을 추가 검증한다.

**면접용 30초 답변**  
“`Required Pixels = FOV/μm-per-pixel`이므로 `12,000/2=6000 pixel`입니다. 이는 Sampling의 최소 조건이고 실제 선택에서는 FOV Margin, Sensor Height, Lens MTF와 검출률을 추가 확인합니다.”

### Q4. Camera ROI와 Binning의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
ROI는 Sensor 일부만 잘라 읽는 것이고 Binning은 여러 Sensor Pixel 신호를 합쳐 출력 Pixel 하나로 만드는 것입니다.

**실무자 답변**  
1:1 Camera ROI는 FOV와 데이터량을 줄이지만 원래 μm/pixel을 유지한다. 2×2 Binning은 출력 Pixel Count를 절반으로 만들며 Output Pixel의 Object Sampling이 대략 두 배가 되고 감도/Noise 특성도 달라질 수 있다.

**면접용 30초 답변**  
“Camera ROI는 Sensor 일부를 1:1로 읽는 Crop이라 일반적으로 μm/pixel은 유지되고 FOV만 줄어듭니다. Binning은 인접 Pixel 신호를 합쳐 출력 Pixel 수와 Sampling 의미가 바뀌므로 기존 Calibration을 그대로 쓰면 안 됩니다.”

### Q5. 작은 Defect가 최소 몇 Pixel이어야 하나요?

**초보자가 이해할 수 있는 답변**  
한 가지 고정 답은 없습니다. 결함 형태와 Lens, 조명, Noise 및 알고리즘에 따라 실제 Sample로 정해야 합니다.

**실무자 답변**  
Detection과 Measurement의 필요 Sampling이 다르다. Point-like Particle, Scratch Width, Edge 간격은 영상 형성이 다르므로 MTF/PSF, Contrast, SNR, Orientation, Sub-pixel 위치와 목표 Detection/False Positive Rate를 포함해 내부 기준을 검증한다.

**면접용 30초 답변**  
“고정된 정답은 없습니다. 먼저 알고리즘 후보에 필요한 Pixel 수를 가정해 광학계를 설계하고, Lens MTF·조명·Noise·Defect 위치를 포함한 실제 Sample로 검출률과 오검률을 측정해 최소 Sampling 기준을 확정합니다.”

### Q6. 설계 μm/pixel과 Calibration μm/pixel이 다른 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Lens 장착 거리와 Focus, 제조 공차 때문에 실제 배율이 사양값과 조금 달라질 수 있습니다.

**실무자 답변**  
명목 배율, WD, Focus, Camera/Lens 자세, Distortion 및 Target 측정 오차가 차이를 만든다. 설계값은 후보 선정에 사용하고 실제 Measurement에는 Traceable Target으로 얻은 Calibration Transform과 Residual을 사용한다.

**면접용 30초 답변**  
“설계값은 Pixel Pitch/명목 배율이지만 실제 장착에서는 WD, Focus, 공차와 Distortion으로 유효 배율이 달라집니다. 따라서 치수와 좌표 변환에는 Calibration Target으로 얻은 실제 Scale과 보정 후 Residual을 사용합니다.”

---

## 11. 실습 문제

### 실습 1: 배율 비교표 작성

Camera `4096×3000`, Pixel Pitch `3.45 μm`에 대해 0.25×/0.5×/1×/2×의 다음 값을 계산한다.

- Sensor Width/Height
- FOV Width/Height
- X/Y μm/pixel
- 20 μm와 50 μm Feature의 Pixel 점유 수

### 실습 2: 요구사항 충돌 찾기

조건:

- Required FOV: 25×18 mm
- 최소 Defect: 30 μm
- 내부 Sampling 기준: 최소 6 Pixel
- 후보 Camera: 4096×3000

필요 μm/pixel, 최소 Width/Height Pixel Count를 구하고 후보 Camera의 합격 여부와 대안을 제안한다.

### 실습 3: Rotation Margin 계산

제품 `20×8 mm`, 위치 편차 X/Y 각각 ±0.5 mm, 회전 ±3°, 양쪽 Safety Margin 0.3 mm일 때 필요한 최대 FOV Width/Height를 계산한다.

### 실습 4: Calculator 구현

C++ 후보 평가기에 다음을 추가한다.

- X/Y 동시 평가
- 여러 Camera/Lens 후보 CSV 입력
- FOV/Sampling/Pixel Count 합격 사유 출력
- Calibration 실측 Scale과 설계값 오차율 Warning
- Invalid Unit 및 Overflow 방지 Test

### Phase 4 미니 프로젝트: Vision Requirement Calculator

```text
Product Geometry + Position/Rotation Margin
                  ↓
             Required FOV

Minimum Feature + Required Feature Pixels
                  ↓
          Required μm-per-pixel

Required FOV / μm-per-pixel
                  ↓
       Minimum Camera Pixel Count
                  ↓
Camera/Lens Candidate Evaluation
                  ↓
Pass / Fail / Need Measurement
```

**필수 출력**

- X/Y Required FOV
- X/Y Required Pixel Count
- 후보별 실제 FOV와 μm/pixel
- Feature Pixel 수
- FOV/Sampling 각각의 합격 여부
- WD/DOF/MTF/Distortion처럼 계산만으로 확정할 수 없는 항목

---

## 12. Chapter 핵심 요약

- 🔴 `μm/pixel = FOV/Pixel Count`다.
- 🔴 FOV가 넓어지면 같은 Pixel Count에서 Sampling은 거칠어진다.
- 🔴 배율이 증가하면 FOV와 μm/pixel은 감소하고 Feature Pixel 수는 증가한다.
- 🔴 `Feature Pixels = Feature Size/μm-per-pixel`이다.
- 🔴 `Required Pixel Count = Required FOV/Required Sampling`이다.
- 🔴 FOV와 Sampling 동시 요구는 최소 Camera Pixel Count를 결정한다.
- 🔴 제품 크기뿐 아니라 Translation, Rotation, Align, Safety Margin을 FOV에 포함한다.
- 🟠 X/Y 방향과 Sensor Aspect Ratio를 각각 확인한다.
- 🟠 Camera ROI, Binning, Resize는 같은 출력 크기라도 의미가 다르다.
- 🟠 Sampling 계산 후에도 MTF, DOF, 조명, Noise 및 실제 검출률을 검증한다.

---

## 5일차 권장 학습 순서

- [ ] 30분: 기본식 6개를 보지 않고 작성
- [ ] 60분: 0.25×~2× 비교표 손 계산
- [ ] 60분: 요구사항 역산 예제 2~5 풀이
- [ ] 60~90분: C++ 후보 평가기 구현 및 Unit Test
- [ ] 45분: Rotation Margin 실습
- [ ] 30분: 면접 Q1~Q6 30초 답변 연습
- [ ] 20분: 현재 업무 장비의 FOV/Pixel Count/Scale 조사 목록 작성

## 학습 완료 체크

- [ ] FOV, Pixel Count, μm/pixel을 양방향으로 계산한다.
- [ ] 배율별 FOV와 Feature Pixel 수를 비교한다.
- [ ] 요구 FOV와 Sampling으로 최소 Camera Resolution을 역산한다.
- [ ] 배율 변경만으로 해결할 수 없는 요구사항을 찾는다.
- [ ] Translation/Rotation/Safety Margin을 FOV에 반영한다.
- [ ] 설계값과 Calibration 값의 사용 목적을 구분한다.
- [ ] Vision Requirement Calculator를 설계하거나 구현했다.

## 다음 Chapter 예고

다음 Chapter에서는 Sampling 계산만으로 실제 검사 Resolution을 보장할 수 없는 이유를 Lens MTF, Nyquist, Blur, Focus, Motion, Illumination과 연결해 학습한다.
