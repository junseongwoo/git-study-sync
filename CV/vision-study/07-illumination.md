# Chapter 7. Illumination: 조명으로 검사 특징 만들기

> Phase 6 · 7일차 · 예상 학습 시간: 10~14시간 · 난이도: 입문→중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 조명은 Image를 밝게 하는 장치가 아니라 **검사 특징의 Contrast를 만드는 광학계**
- 🔴 Bright Field와 Dark Field의 입사·반사 Geometry
- 🔴 Back Light, Ring Light, Coaxial Light, Dome Light의 선택 기준
- 🔴 Diffuse Light와 Directional Light의 차이
- 🔴 조명 방식과 Threshold/Edge/Blob/Pattern Matching의 연결
- 🔴 Exposure, Gain, Saturation, Motion Blur의 Trade-off
- 🟠 조명 각도, Working Distance, 균일도, 편광(Polarization)
- 🟠 파장(Color), Strobe, LED 온도·열화와 재현성
- 🟠 Histogram, Contrast, CNR을 이용한 후보 조명 비교

### 실무 목표

검사 대상과 결함의 반사 특성을 보고 조명 후보를 선택하며, “밝아 보이는 Image”가 아니라 검사 특징과 Background가 안정적으로 분리되는 Image를 고른다. 후보 조명을 동일한 Camera 조건과 위치에서 촬영해 CNR, Saturation, 균일도 및 알고리즘 결과로 비교한다.

---

## 2. 선수 지식

- [[06-optical-resolution|Chapter 6]]의 MTF, Blur, CNR, Exposure
- Gray Level, Histogram, Saturation
- 반사, 투과, 산란의 직관적 의미
- Threshold, Edge, Blob, Pattern Matching의 역할

### 2.1 먼저 구분할 두 가지 분류

**조명 장치 형태**와 **광학 Geometry**는 같은 분류가 아니다.

- 장치 형태: Ring, Bar, Dome, Coaxial, Back Light
- Geometry: Bright Field, Dark Field, Directional, Diffuse

예를 들어 Ring Light도 설치 각도에 따라 Bright Field 또는 Dark Field에 가까운 효과를 만들 수 있다. “Ring Light니까 어떤 결함에 좋다”라고 장치 이름만으로 결정하지 않는다.

---

## 3. 핵심 개념

### 3.1 조명이 검사 알고리즘보다 먼저다

```text
Object의 물리적 차이
    │ 조명 Geometry/파장/편광
    ▼
반사·투과·산란 차이
    │ Lens + Camera
    ▼
Gray/Color Contrast
    │ Algorithm
    ▼
Threshold / Edge / Blob / Matching
```

정상과 불량이 Image에서 같은 Gray Level로 보이면 복잡한 알고리즘도 안정적으로 분리하기 어렵다. 반대로 조명으로 결함만 밝거나 어둡게 만들면 단순 Threshold와 Blob만으로 강건한 검사가 가능하다.

### 3.2 정반사, 난반사, 산란, 투과

- **Specular Reflection(정반사)**: 거울처럼 입사각과 반사각이 대응하는 방향으로 강하게 반사
- **Diffuse Reflection(난반사)**: 거친 표면에서 여러 방향으로 분산
- **Scattering(산란)**: Scratch, Particle, Edge 등에서 진행 방향이 다양하게 바뀜
- **Transmission(투과)**: 빛이 Object를 지나감

검사 핵심은 Camera가 어떤 빛을 받게 하고 어떤 빛을 받지 않게 할지 설계하는 것이다.

### 3.3 Bright Field

정상 표면의 주 반사광이 Lens로 들어오도록 조명과 Camera를 배치한다.

```text
Light ──► Surface ── specular reflection ──► Camera
```

일반적 영상:

- 정상 평탄면: 밝음
- 빛을 산란시키는 Scratch/거칠기/Particle: 어둡거나 Contrast 발생

잘 맞는 대상:

- 평탄 금속/Glass의 얼룩과 반사율 차이
- 인쇄 Pattern, 표면 색/명암
- 밝은 Background 위의 Dark Defect

잘 맞는 알고리즘:

- Gray Threshold
- Background Difference
- Pattern Matching
- Local Contrast/Stain 검사

### 3.4 Dark Field

정상 표면의 주 반사광은 Lens 밖으로 보내고 Scratch, Edge, Particle에서 산란된 빛만 Lens에 들어오게 한다.

```text
Low-angle Light ──► flat surface ──► away from Camera
                         ▲
                    scratch/edge
                         └─ scattered light ──► Camera
```

일반적 영상:

- 정상 평탄면: 어두움
- Scratch, Particle, Edge: 밝음

잘 맞는 대상:

- 평탄 표면의 미세 Scratch
- Particle, 먼지, Burr
- 양각/음각 문자와 Edge

잘 맞는 알고리즘:

- Bright Blob Detection
- Top-hat/Local Threshold
- Line/Edge Detection
- 방향성 Filter

> [!WARNING]
> 방향성 Dark Field는 조명 방향과 평행한 Scratch가 약하게 보일 수 있다. 여러 방향 Bar Light, Segment Ring 또는 촬영 다중화가 필요할 수 있다.

### 3.5 Back Light

Object 뒤에서 Camera 방향으로 빛을 비춘다. 표면 Texture보다 Silhouette를 만든다.

```text
Back Light ──► Object ──► Camera
bright background / dark silhouette
```

강조 특징:

- 외곽 Edge
- Hole, Gap, Profile
- Width, Height, Diameter, Presence
- 투명체의 일부 내부 구조(조건에 따라)

일반적 영상:

- Background: 밝고 균일
- 불투명 Object: 어두움
- 경계: 높은 Contrast

잘 맞는 알고리즘:

- Threshold + Binary Image
- Edge Position
- Contour/Blob
- Diameter/Width/Gap Measurement

한계:

- Object 표면 Scratch/얼룩은 잘 보이지 않음
- Lens/조명 크기와 Object-Lamp 간격에 따라 Edge가 퍼질 수 있음
- Telecentric Back Light 또는 Collimated Light가 치수 정확도에 유리할 수 있음

### 3.6 Ring Light

Lens 주위를 둘러싼 원형 조명이다. 설치 높이와 LED 각도에 따라 효과가 달라진다.

- Low-angle Ring: Dark Field 효과, Edge/Scratch 강조
- High-angle Ring: 비교적 Bright Field, 일반 표면 관찰
- Diffuse Ring: Hot Spot 완화
- Segment Ring: 방향별 점등으로 형상 방향성 분석

잘 맞는 대상:

- 원형 또는 방향성이 다양한 부품
- 문자, 조립 상태, 일반 Presence
- 낮은 각도에서 Burr/Particle

주의:

- 반사면 중앙에 Ring 모양 Hot Spot
- 3D 형상에서 Shadow와 방향별 밝기 차이
- Lens FOV/WD 변화에 따른 균일도 변화

### 3.7 Coaxial Light

Beam Splitter를 통해 Lens Optical Axis와 거의 같은 방향으로 조명한다.

```text
LED → Beam Splitter ↓
                    ↓ optical axis
                 Flat Object
                    ↑ reflection
                    ↑ Camera
```

강조 특징:

- 평탄한 반사면의 Pattern, Mark, 얼룩
- PCB Pad, Wafer, Glass/Film 표면
- 정면 반사에서 생기는 밝기 차이

일반적 영상:

- Camera에 수직인 평탄면: 밝음
- Tilt, Scratch, 거친 영역: 빛이 벗어나 어둡거나 Contrast 발생

잘 맞는 알고리즘:

- Pattern Matching/OCR 전처리
- Threshold
- Background Difference
- Stain/Non-uniformity 검사

한계:

- 높이 차와 경사면은 어두워질 수 있음
- Beam Splitter 광손실
- 큰 FOV에서 균일도 확보가 어려울 수 있음

### 3.8 Dome Light

반구형 확산면의 여러 방향에서 Object를 비춘다. 반사면의 Hot Spot과 Shadow를 줄여 균일한 영상을 만든다.

강조 특징:

- 곡면, 주름진 포장, 광택 Plastic
- 불규칙 형상의 Color/Print
- 일반 조명에서 반사가 심한 표면의 균일한 외관

일반적 영상:

- 넓고 부드러운 반사
- Shadow 감소
- 미세한 방향성 Scratch Contrast는 약해질 수 있음

잘 맞는 알고리즘:

- Color/Gray Segmentation
- Pattern Matching/OCR
- 인쇄 누락/색상 검사

### 3.9 Diffuse Light와 Directional Light

| 구분 | Diffuse Light | Directional Light |
|---|---|---|
| 빛의 방향 | 여러 방향으로 분산 | 특정 방향이 강함 |
| 장점 | Hot Spot/Shadow 완화, 균일도 | Edge, 높이, Scratch 방향 강조 |
| 단점 | 미세 형상 Contrast가 약해질 수 있음 | 방향 의존, Shadow, 균일도 문제 |
| 대표 장치 | Dome, Diffuser Panel | Bar, Low-angle Ring, Collimated Back Light |
| 잘 맞는 검사 | Print/Color/Pattern | Scratch/Burr/Edge/Height 변화 |

### 3.10 조명 선택 비교표

| 조명/Geometry | 주 대상 | 강조되는 특징 | 예상 Image | 잘 맞는 알고리즘 |
|---|---|---|---|---|
| Back Light | 외곽, Hole, Gap | Silhouette Edge | 밝은 배경+어두운 Object | Threshold, Contour, Edge |
| High-angle Ring | 일반 부품 | 표면/문자/조립 | 비교적 균일한 전면 | Matching, Threshold |
| Low-angle Ring | 평탄 표면 | Scratch, Burr, Particle | 어두운 배경+밝은 결함 | Blob, Line, Edge |
| Coaxial | 평탄 반사면 | Mark, 얼룩, Tilt | 수직면 밝음 | Matching, Stain, Threshold |
| Dome | 곡면/광택면 | Print, Color, 전체 외관 | Hot Spot/Shadow 감소 | Segmentation, OCR, Matching |
| Directional Bar | 형상/방향 결함 | 특정 방향 Edge/Scratch | 방향성 Contrast/Shadow | Gradient, Line, Edge |
| Diffuse Panel | 반사/표면 검사 | 넓은 균일도 | 부드러운 Contrast | Background, Threshold |

### 3.11 Exposure, Gain, 조명 세기

- 조명 세기 증가: Signal 증가, Exposure 단축 가능
- Exposure 증가: Signal 증가, Motion Blur와 Cycle Time 위험
- Gain 증가: 밝아지지만 Noise도 증폭되고 Dynamic Range가 줄 수 있음
- Aperture 개방: 광량 증가, DOF/수차 변화

조명 후보를 비교할 때 Auto Exposure/Auto Gain을 끄고 동일 조건을 유지해야 한다. 그렇지 않으면 조명 Geometry가 아니라 Camera 자동 보정 결과를 비교하게 된다.

### 3.12 Saturation과 밝기 목표

8-bit Image에서 정상부가 255에 몰리면 더 밝은 차이를 잃는다. 반대로 Defect와 Background가 모두 0 근처면 Noise에 묻힌다.

실무에서는 다음을 함께 본다.

- Defect/Background 평균 차이
- 각 영역 표준편차와 CNR
- Saturated Pixel 비율
- FOV 균일도
- Lot/위치/방향 변화에서 분포 간격

### 3.13 Polarization

Light와 Lens에 Polarizer를 사용하고 방향을 교차시키면 직접 정반사를 줄일 수 있다.

- Cross Polarization: Glare 억제, Plastic/Film 아래 Print 관찰
- Parallel/특정 각도: 반사 특징 유지 또는 응력/재질 효과 관찰

한계:

- 광량 감소로 Exposure 증가
- 금속 반사와 비금속 표면에서 효과가 다름
- 곡면/복굴절 재질에서 예상과 다를 수 있음

### 3.14 파장(Color)

물체 색과 조명 파장의 조합으로 Contrast를 바꿀 수 있다.

- 같은 계열 파장: 해당 색이 상대적으로 밝게 보이는 경향
- 보색 계열: 해당 색이 상대적으로 어둡게 보이는 경향
- Blue: 짧은 파장으로 미세 산란/표면 특징에 유리할 수 있으나 재질 의존
- Red/IR: 일부 재질 투과, 표면 Pattern 억제 등에 유리할 수 있음

Color Camera를 쓰기 전에 Mono Camera+파장 선택으로 더 단순하고 강한 Contrast를 만들 수 있는지 검토한다.

### 3.15 Strobe, 온도, 열화

Strobe는 짧은 시간 강하게 발광해 Motion Blur를 줄일 수 있다. 확인할 항목:

- Pulse Width와 Exposure의 Timing
- Trigger Delay/Jitter
- Peak Current와 허용 Duty Cycle
- LED Controller의 Overdrive Limit
- 열에 따른 밝기와 파장 변화
- 장기 열화와 Camera 간 편차

조명 Parameter와 Controller Version을 Recipe에 저장하고, Warm-up 및 기준 Image 점검 절차를 둔다.

---

## 4. 그림으로 이해하기

### 4.1 Bright Field와 Dark Field

```text
Bright Field                          Dark Field

Light                                 low-angle Light →→→
  \                                      _________ flat surface
   \ incidence                         / scratch \  scattered ↑
    \________ surface ________          reflected normal light → away
             \ reflection
              \ Camera                Camera receives scratch scattering

정상면 밝음, 결함이 어둡거나 변화         정상면 어두움, 결함/Edge 밝음
```

### 4.2 조명에서 알고리즘까지

```text
Geometry 선택
    ↓
Defect Contrast 생성
    ↓
Exposure/Gain으로 유효 범위 확보
    ↓
Histogram/CNR/Uniformity 비교
    ↓
Threshold / Edge / Blob / Matching
    ↓
Detection Rate / False Positive / Repeatability
```

### 4.3 방향성 Scratch

```text
Light A →→→   Scratch ─────   약한 산란 가능
Light B ↓↓↓   Scratch ─────   강한 산란 가능

한 방향 영상만으로 모든 Scratch 방향을 보장하지 않는다.
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### 외곽 치수 검사

Back Light로 고Contrast Silhouette를 만들고 Threshold/Edge로 Width와 Diameter를 측정한다. 광원 크기, Object와 Light 거리, Telecentricity가 Edge 위치 Bias에 영향을 줄 수 있다.

### 금속 표면 Scratch

Low-angle Dark Field로 Scratch 산란광을 밝게 만든다. 여러 방향 조명을 순차 점등하거나 Segment를 합성해 방향 의존성을 줄인 뒤 Line/Blob 검사를 수행한다.

### PCB/반도체 Mark Align

Coaxial Light로 평탄 Pad/Mark Contrast를 만들고 Pattern Matching을 적용한다. 높이/기울기 변화로 Mark 밝기가 달라지는지 Recipe 범위에서 검증한다.

### 광택 포장 인쇄 검사

Dome+편광으로 Hot Spot을 줄이고 Color/Gray Segmentation 및 OCR을 적용한다. 주름과 제품 위치 변화까지 포함해 Background 균일성을 평가한다.

### 투명 Film Particle

Dark Field 또는 Back/Diffuse 조명 후보를 비교한다. Particle의 산란, Film Texture, Dust와 실제 Defect를 CNR/Blob 특징으로 분리한다.

---

## 6. 숫자로 이해하기

### 예제 1: 조명 후보 CNR 비교

동일한 Defect ROI와 Background ROI를 측정한다.

| 후보 | Defect 평균/표준편차 | Background 평균/표준편차 | 평균 차이 | CNR |
|---|---:|---:|---:|---:|
| A | 140 / 6 | 110 / 5 | 30 | `30/√61 ≈ 3.84` |
| B | 180 / 12 | 100 / 10 | 80 | `80/√244 ≈ 5.12` |
| C | 250 / 4 | 200 / 4 | 50 | `50/√32 ≈ 8.84` |

C가 CNR은 높지만 Defect나 정상부의 Saturation이 발생하는지 별도로 확인해야 한다. CNR 하나만으로 최종 선택하지 않는다.

### 예제 2: Exposure와 Motion Blur

조건:

- Object 속도: 40 mm/s
- Object Sampling: 4 μm/pixel
- 기존 Exposure: 1.5 ms

```text
Motion = 40 mm/s × 1.5 ms = 60 μm
Blur = 60 μm / 4 μm/pixel = 15 pixel
```

Strobe와 광량 증가로 Effective Exposure를 0.05 ms로 줄이면:

```text
Motion = 40 × 0.05 = 2 μm
Blur = 2 / 4 = 0.5 pixel
```

### 예제 3: Saturation 비율

2048×2048 Image에서 Gray 250 이상 Pixel이 83,886개라면:

```text
Total = 2048 × 2048 = 4,194,304 pixel
High-level ratio = 83,886 / 4,194,304 × 100 ≈ 2.00%
```

이 Pixel들이 검사 ROI/기준면에 집중되어 있다면 전체 2%라도 문제가 될 수 있다. 위치 Mask와 함께 본다.

### 예제 4: Strobe Duty Cycle

Pulse Width `100 μs`, 촬영 빈도 `50 Hz`라면:

```text
Duty Cycle = 100 μs × 50 / 1,000,000 μs × 100
           = 0.5%
```

허용 Peak Current와 Duty Cycle은 LED/Controller Datasheet를 따라야 하며 단순 계산만으로 Overdrive를 허용하지 않는다.

---

## 7. C++ 구현

### 조명 후보 영상 평가기

```cpp
#include <opencv2/opencv.hpp>

#include <cmath>
#include <stdexcept>

struct RegionStatistics final {
    double mean{};
    double standardDeviation{};
};

struct LightingMetrics final {
    RegionStatistics feature;
    RegionStatistics background;
    double absoluteContrast{};
    double cnr{};
    double lowClippingRatio{};
    double highClippingRatio{};
};

[[nodiscard]] RegionStatistics CalculateRegionStatistics(
    const cv::Mat& image,
    const cv::Mat& mask)
{
    if (image.empty() || image.type() != CV_8UC1) {
        throw std::invalid_argument{"8-bit mono image is required"};
    }
    if (mask.empty() || mask.type() != CV_8UC1 ||
        mask.size() != image.size() || cv::countNonZero(mask) == 0) {
        throw std::invalid_argument{"Non-empty 8-bit mask is required"};
    }

    cv::Scalar mean;
    cv::Scalar standardDeviation;
    cv::meanStdDev(image, mean, standardDeviation, mask);
    return {mean[0], standardDeviation[0]};
}

[[nodiscard]] double CalculateMaskedRatio(
    const cv::Mat& conditionMask,
    const cv::Mat& regionMask)
{
    cv::Mat intersection;
    cv::bitwise_and(conditionMask, regionMask, intersection);
    return static_cast<double>(cv::countNonZero(intersection)) /
           static_cast<double>(cv::countNonZero(regionMask));
}

[[nodiscard]] LightingMetrics EvaluateLighting(
    const cv::Mat& image,
    const cv::Mat& featureMask,
    const cv::Mat& backgroundMask,
    const int lowClipLevel = 5,
    const int highClipLevel = 250)
{
    if (image.empty() || image.type() != CV_8UC1) {
        throw std::invalid_argument{"8-bit mono image is required"};
    }
    if (lowClipLevel < 0 || highClipLevel > 255 ||
        lowClipLevel >= highClipLevel) {
        throw std::invalid_argument{"Invalid clipping levels"};
    }

    const auto feature = CalculateRegionStatistics(image, featureMask);
    const auto background = CalculateRegionStatistics(image, backgroundMask);
    const double noise = std::hypot(feature.standardDeviation,
                                    background.standardDeviation);

    cv::Mat lowMask;
    cv::Mat highMask;
    cv::compare(image, lowClipLevel, lowMask, cv::CMP_LE);
    cv::compare(image, highClipLevel, highMask, cv::CMP_GE);

    cv::Mat evaluationMask;
    cv::bitwise_or(featureMask, backgroundMask, evaluationMask);

    return {
        feature,
        background,
        std::abs(feature.mean - background.mean),
        noise > 0.0 ? std::abs(feature.mean - background.mean) / noise : 0.0,
        CalculateMaskedRatio(lowMask, evaluationMask),
        CalculateMaskedRatio(highMask, evaluationMask)
    };
}
```

### Unit Test

```cpp
#include <cassert>
#include <cmath>

void TestSeparatedRegions()
{
    cv::Mat image(100, 100, CV_8UC1, cv::Scalar(100));
    const cv::Rect featureRoi{20, 20, 20, 20};
    image(featureRoi).setTo(150);

    cv::Mat featureMask = cv::Mat::zeros(image.size(), CV_8UC1);
    cv::Mat backgroundMask = cv::Mat::zeros(image.size(), CV_8UC1);
    featureMask(featureRoi).setTo(255);
    backgroundMask(cv::Rect{60, 60, 20, 20}).setTo(255);

    const auto metrics = EvaluateLighting(image, featureMask, backgroundMask);
    assert(std::abs(metrics.absoluteContrast - 50.0) < 1e-9);
    assert(metrics.lowClippingRatio == 0.0);
    assert(metrics.highClippingRatio == 0.0);
    // Both synthetic regions have zero noise, so CNR is reported as 0/undefined.
    assert(metrics.cnr == 0.0);
}

void TestSaturationDetection()
{
    cv::Mat image(10, 10, CV_8UC1, cv::Scalar(100));
    image(cv::Rect{0, 0, 2, 10}).setTo(255); // 20% high clipping
    const cv::Mat mask(image.size(), CV_8UC1, cv::Scalar(255));

    const auto metrics = EvaluateLighting(image, mask, mask);
    assert(std::abs(metrics.highClippingRatio - 0.2) < 1e-9);
}
```

### 코드에서 봐야 할 점

1. Feature와 Background ROI를 동일 Image에서 명시적으로 분리한다.
2. 평균 차이뿐 아니라 각 영역 Noise를 포함한 CNR을 계산한다.
3. 전체 Image가 아니라 평가 ROI 내부의 Clipping 비율을 구한다.
4. CNR이 높아도 Saturation과 위치 균일도가 나쁘면 탈락할 수 있다.
5. 실제 비교에서는 동일 Exposure/Gain/Aperture와 동일 Sample 위치를 유지한다.
6. 정상/불량 여러 장의 분포와 알고리즘 검출률을 추가해야 한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: 조명 방향에 따라 Scratch가 사라짐

- 원인: 방향성 산란과 단일 Bar/Segment 사용
- 대응: 다방향 촬영, Segment 순차 점등, 방향별 결과 결합

### 문제 2: Auto Exposure로 후보 비교

- 원인: Camera가 각 조명 밝기를 자동 보정
- 대응: Exposure/Gain/Aperture 고정 후 Geometry와 CNR 비교

### 문제 3: LED 온도 상승으로 밝기 변화

- 증상: 장비 가동 직후와 안정화 후 Threshold 분포 변화
- 대응: Warm-up, 정전류 Controller, 온도/광량 Monitoring, 기준 Image

### 문제 4: 반사 Hot Spot과 Saturation

- 원인: Specular Surface와 조명/Camera Geometry
- 대응: Dome/Diffuser/Polarizer, 각도 변경, Exposure 조정

### 문제 5: FOV 중심과 가장자리 균일도 차이

- 원인: 조명 크기/거리, Vignetting, Coaxial/Dome 정렬
- 대응: Flat-field 평가, 조명 크기/WD 개선, Shading Correction 검증

### 문제 6: Strobe Timing 불일치

- 증상: Frame마다 밝기 변화 또는 일부 Frame 암전
- 대응: Exposure Active와 Pulse Timing 측정, Delay/Jitter/Width 검증

### 문제 7: 조명 교체 후 기존 Recipe 사용

- 원인: 같은 Model이라도 광량/파장/배치 편차 존재
- 대응: Optical Configuration ID, 재Calibration/재검증, 변경 이력

---

## 9. 흔한 오해

1. **“Image가 밝을수록 검사하기 좋다.”**  
   Defect와 Background의 분리, Saturation, Noise와 균일도가 더 중요하다.

2. **“Ring Light는 항상 같은 효과다.”**  
   LED 각도와 WD에 따라 Bright/Dark Field 효과가 달라진다.

3. **“Diffuse Light가 모든 반사를 해결한다.”**  
   Hot Spot은 줄지만 Scratch/미세 형상 Contrast도 약해질 수 있다.

4. **“Dark Field면 모든 Scratch가 밝다.”**  
   Scratch 방향, 깊이, 표면과 조명 방향에 따라 산란이 달라진다.

5. **“Exposure를 늘리면 Noise 문제를 모두 해결한다.”**  
   Motion Blur, Saturation, Cycle Time과 Dark/Read Noise 조건을 함께 본다.

6. **“편광을 쓰면 광택 반사가 완전히 사라진다.”**  
   재질/각도/곡률에 따라 효과가 다르고 광량이 감소한다.

7. **“좋은 조명을 고르면 Threshold 하나로 영구히 검사된다.”**  
   Lot, 오염, LED 열화, 위치·높이 변화와 Camera Drift를 검증해야 한다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. 머신비전에서 조명이 중요한 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
조명은 단순히 밝게 하는 것이 아니라 정상과 결함이 서로 다른 밝기로 보이게 만들어 알고리즘이 구분하도록 합니다.

**실무자 답변**  
조명 Geometry, 파장, 편광이 Object의 정반사·난반사·산란·투과를 선택해 Feature CNR을 결정한다. 좋은 조명은 간단한 Threshold/Blob으로도 Robustness를 높이고, 잘못된 조명은 복잡한 알고리즘으로도 Variation을 분리하기 어렵게 한다.

**면접용 30초 답변**  
“조명은 밝기를 공급하는 부품이 아니라 검사 특징의 Contrast를 만드는 Optical Component입니다. 정상과 불량의 반사·산란·투과 차이를 Camera에 유리하게 전달해 CNR을 높이면 Threshold나 Edge 같은 단순한 알고리즘도 안정적으로 동작합니다.”

### Q2. Bright Field와 Dark Field의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Bright Field는 정상 표면의 주 반사광을 Camera가 받아 배경이 밝고, Dark Field는 정상 반사를 피하고 결함의 산란광을 받아 결함이 밝게 보이게 합니다.

**실무자 답변**  
Bright Field는 Specular 또는 주 반사 경로를 Lens에 결합하고, Dark Field는 정상면 반사를 Lens 밖으로 보내 Scratch/Particle/Edge의 산란만 수집한다. 대상 표면과 결함 방향에 따라 입사각과 다방향 조명을 결정한다.

**면접용 30초 답변**  
“Bright Field는 정상면 반사광이 Lens로 들어오도록 해 평탄면이 밝게 보이고, Dark Field는 정상 반사를 피하면서 결함의 산란광만 받아 어두운 배경에 Scratch나 Particle을 밝게 만듭니다. 방향성 결함은 여러 조명 방향으로 검증합니다.”

### Q3. Back Light는 어떤 검사에 사용하나요?

**초보자가 이해할 수 있는 답변**  
물체 뒤에서 비춰 밝은 배경과 어두운 외곽을 만들기 때문에 폭, 직경, Hole과 유무 검사에 사용합니다.

**실무자 답변**  
Back Light는 Surface Texture를 억제하고 고Contrast Silhouette를 만들어 Threshold/Contour/Edge 기반 Profile Measurement에 유리하다. Edge Telecentricity, 광원 균일도, Object-Light 거리와 투명체 투과를 검증한다.

**면접용 30초 답변**  
“Back Light는 밝은 배경과 Object Silhouette를 만들어 외곽, Hole, Gap, Diameter 같은 Profile 검사에 적합합니다. Threshold와 Edge 처리가 단순해지지만 정밀 치수에서는 광원의 Collimation과 Edge Blur, Lens Perspective를 함께 확인합니다.”

### Q4. Coaxial Light와 Dome Light를 언제 구분해 사용하나요?

**초보자가 이해할 수 있는 답변**  
Coaxial은 평평한 반사면을 정면에서 보고, Dome은 곡면이나 광택 물체를 여러 방향에서 부드럽게 비출 때 사용합니다.

**실무자 답변**  
Coaxial은 Optical Axis 방향으로 평탄 Specular Surface의 Mark/얼룩 Contrast를 만든다. Dome은 광범위한 입사각으로 곡면/주름의 Hot Spot과 Shadow를 줄인다. Coaxial은 Tilt에, Dome은 미세 방향성 형상 Contrast 저하에 주의한다.

**면접용 30초 답변**  
“평탄 반사면의 Pad나 Mark라면 Coaxial을 우선 검토하고, 곡면·광택 포장처럼 Hot Spot과 Shadow가 문제라면 Dome을 검토합니다. 최종 선택은 동일 Camera 조건에서 Feature CNR과 균일도, 알고리즘 검출률로 비교합니다.”

### Q5. 조명 후보를 어떻게 정량 비교하나요?

**초보자가 이해할 수 있는 답변**  
같은 Camera 설정에서 정상과 결함의 평균 밝기 차이, Noise, 포화와 화면 전체 균일도를 비교합니다.

**실무자 답변**  
Exposure/Gain/Aperture와 Sample Pose를 고정하고 Feature/Background ROI의 분포와 CNR, Clipping, Uniformity를 측정한다. 여러 정상/불량 Variation에서 Detection Rate, False Positive Rate와 Parameter Margin을 평가한다.

**면접용 30초 답변**  
“Auto 설정을 끄고 동일 조건으로 촬영한 뒤 Feature와 Background의 평균·표준편차로 CNR을 계산하고 Saturation과 FOV 균일도를 봅니다. 그 후 Lot·위치·방향이 다른 Sample에서 검출률, 오검률과 Threshold Margin을 비교해 선택합니다.”

### Q6. Strobe 조명 사용 시 무엇을 확인하나요?

**초보자가 이해할 수 있는 답변**  
Camera Exposure 시간과 조명 Pulse가 정확히 겹치는지, 너무 강하거나 자주 켜 LED가 손상되지 않는지 확인합니다.

**실무자 답변**  
Exposure Active 대비 Trigger Delay/Jitter/Pulse Width, Peak Current, Duty Cycle과 Thermal Limit을 확인한다. Effective Exposure로 Motion Blur Budget을 계산하고 Frame별 밝기 Repeatability와 Controller Error를 Monitoring한다.

**면접용 30초 답변**  
“Strobe는 Motion Blur를 줄이지만 Exposure와 Pulse Timing이 정확히 겹쳐야 합니다. Delay·Jitter·Pulse Width를 계측하고, Peak Current와 Duty Cycle이 Controller/LED 사양 안인지 확인하며 Frame 밝기 반복성과 열화를 관리합니다.”

---

## 11. 실습 문제

### 실습 1: 조명 선택표 만들기

다음 검사별로 1차/2차 후보 조명, 예상 Image, 알고리즘과 실패 Risk를 작성한다.

- 금속 평판 Scratch
- Plastic Cap 외경
- PCB Pad의 Mark
- 광택 포장의 인쇄 누락
- 투명 Film 위 Particle

### 실습 2: 동일 Sample 조명 비교

최소 세 조명 조건을 동일 Exposure/Gain/Aperture로 촬영한다.

- Feature/Background 평균·표준편차
- CNR
- Low/High Clipping 비율
- 중앙/모서리 균일도
- Threshold 가능 범위

숫자가 좋은 후보와 실제 알고리즘 결과가 일치하는지 확인한다.

### 실습 3: 방향성 결함 검증

Scratch Target을 0°, 45°, 90°, 135°로 회전하거나 조명 Segment를 변경한다. 방향별 CNR과 Line Detection 결과를 기록하고 단일 조명 방향의 사각지대를 찾는다.

### 실습 4: Strobe Budget

조건:

- 속도 80 mm/s
- Sampling 3 μm/pixel
- 허용 Blur 0.4 Pixel
- 촬영 40 fps

최대 Effective Exposure와 Pulse Duty Cycle을 계산한다. 필요한 광량과 Datasheet에서 확인할 항목을 적는다.

### Phase 6 미니 프로젝트: Lighting Comparison Analyzer

```text
동일 Sample / Pose / Camera Parameter
              ↓
조명 후보별 Image Set
              ↓
Feature & Background ROI Statistics
              ↓
CNR / Clipping / Uniformity / Histogram
              ↓
Algorithm Test
              ↓
Detection Rate / False Positive / Margin
              ↓
Lighting Selection Report
```

**필수 기능**

- 후보명과 Exposure/Gain/Light Current 기록
- Feature/Background ROI Mask 저장
- Image별/후보별 평균과 분산
- CNR 및 Saturation/Underexposure 비율
- Threshold Sweep 결과
- 숫자만으로 자동 최종 선택하지 않고 실패 영상 Review 포함

---

## 12. Chapter 핵심 요약

- 🔴 조명은 검사 특징의 Contrast를 만드는 Optical Component다.
- 🔴 장치 형태와 Bright/Dark Field Geometry를 구분한다.
- 🔴 Back Light는 Silhouette, 외곽, Hole과 치수 검사에 유리하다.
- 🔴 Dark Field는 Scratch, Particle, Burr의 산란광을 강조한다.
- 🔴 Coaxial은 평탄 반사면, Dome은 곡면·광택면의 균일 조명에 유리하다.
- 🔴 Directional Light는 형상을 강조하지만 방향 사각지대가 있다.
- 🔴 조명 후보는 동일 Camera 조건에서 CNR, Clipping, 균일도로 비교한다.
- 🟠 Exposure/Gain/조명 세기는 Motion Blur, Noise, Saturation과 Trade-off다.
- 🟠 편광과 파장 선택은 반사 및 색 Contrast를 크게 바꿀 수 있다.
- 🟠 최종 선택은 실제 Variation의 검출률·오검률과 유지보수 재현성으로 검증한다.

---

## 7일차 권장 학습 순서

- [ ] 40분: 반사·산란·투과와 Bright/Dark Field 정리
- [ ] 60분: 조명 7종 비교표를 직접 다시 작성
- [ ] 40분: 조명과 Threshold/Edge/Blob/Matching 연결
- [ ] 40분: Exposure·Gain·Strobe 계산
- [ ] 60~90분: C++ Lighting Metrics 구현
- [ ] 60분: 실제 검사 5종의 조명 선택 실습
- [ ] 30분: 면접 Q1~Q6 30초 답변 연습

## 학습 완료 체크

- [ ] Bright Field와 Dark Field를 광선 Geometry로 설명한다.
- [ ] Back/Ring/Coaxial/Dome의 적합 대상과 한계를 설명한다.
- [ ] Diffuse와 Directional Light의 Trade-off를 설명한다.
- [ ] 조명 방식과 영상처리 알고리즘을 연결한다.
- [ ] CNR, Saturation, Uniformity로 후보를 비교한다.
- [ ] Motion Blur 기준으로 Strobe/Exposure를 계산한다.
- [ ] Lighting Comparison Analyzer를 설계하거나 구현했다.

## 다음 Chapter 예고

다음 Chapter에서는 조명으로 확보한 Image를 Threshold, Histogram, Filter, Edge, Morphology, Blob으로 처리하는 전통 영상처리 Pipeline을 C++/OpenCV로 구현한다.
