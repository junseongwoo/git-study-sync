# 9일차. 영상처리 기초 1: Histogram · Contrast · Threshold

> Phase 7-1 · 예상 학습 시간: 8~10시간 · 난이도: 입문→중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Gray Level과 Histogram
- 🔴 Brightness와 Contrast의 차이
- 🔴 Threshold와 Binary Image
- 🔴 Foreground/Background Polarity
- 🔴 Global, Otsu, Adaptive Threshold의 선택 기준
- 🔴 ROI와 Mask를 이용한 제한적 처리
- 🟠 Normalization과 Contrast Stretching
- 🟠 Threshold Margin과 조명 변화 Robustness
- 🟠 8/12/16-bit Image에서 Threshold 의미

### 실무 목표

검사 Image의 Histogram과 ROI 통계를 보고 Manual/Otsu/Adaptive Threshold 중 적합한 방식을 선택한다. Binary 결과를 만든 뒤 Foreground 비율과 Blob/Edge 후속 처리를 고려하며, 한 장에서 잘 되는 Threshold가 아니라 Lot·위치·조명 변화에서도 분리가 유지되는 Parameter를 검증한다.

---

## 2. 선수 지식

- [[02-image-basic|Chapter 2]]의 Gray Scale, Bit Depth, Dynamic Range
- [[07-illumination|Chapter 7]]의 조명 Contrast와 CNR
- ROI, 평균, 표준편차의 기초
- OpenCV `cv::Mat`, `CV_8UC1`

### 2.1 오늘의 Pipeline 위치

```text
Camera Image
   ↓
ROI 선택
   ↓
Gray / Brightness / Contrast 확인
   ↓
Histogram 분석
   ↓
Threshold
   ↓
Binary Image
   ↓
Morphology / Blob / Measurement / Judgement
```

Threshold는 최종 검사가 아니라 **Gray Image를 Object 후보와 Background 후보로 나누는 중간 단계**다.

---

## 3. 핵심 개념

### 3.1 Gray Level

8-bit Gray Image에서 각 Pixel은 일반적으로 `0~255` 값을 가진다.

```text
0   = Black
255 = White
```

하지만 Gray 값은 Object의 절대 속성이 아니다.

```text
Gray Level
= Object 반사/투과 특성
 + 조명 Geometry/세기
 + Lens/Aperture
 + Exposure/Gain
 + Sensor Response/Noise
 + Image Processing
```

같은 제품도 조명 온도, Exposure, 표면 오염과 위치 변화로 Gray Level이 달라질 수 있다.

### 3.2 Histogram

Histogram은 각 Gray Level 또는 구간에 Pixel이 몇 개 있는지 나타낸다.

```text
Pixel Count
   ▲
   │   Background Peak        Object Peak
   │       ███                   ███
   │     ██████                ██████
   └──────────────────────────────────► Gray Level
         40~80        T         170~220
```

두 Peak 사이 Valley에 Threshold `T`를 놓으면 분리하기 쉽다. 그러나 다음 경우 Histogram만으로는 위치 정보를 알 수 없다.

- 다른 위치의 서로 다른 Object가 같은 Gray 값
- 넓은 조명 Gradient
- 작은 Defect가 전체 Histogram에서 거의 보이지 않음
- ROI 밖 Background가 대부분을 차지

따라서 전체 Image Histogram보다 검사 ROI와 정상/결함 Sample의 분포를 비교한다.

### 3.3 Brightness와 Contrast

- **Brightness**: Image 전체 또는 영역이 밝고 어두운 정도
- **Contrast**: 서로 다른 영역의 밝기 차이

```text
Image A: Background=50, Object=100 → Difference=50
Image B: Background=150, Object=200 → Difference=50
```

B가 전체적으로 밝지만 단순 평균 차이는 같다. 조명 Noise가 B에서 더 크다면 검사 성능은 다를 수 있으므로 CNR과 분포 겹침을 본다.

대표적인 단순 Contrast:

```text
Absolute Contrast = |μ_object - μ_background|
Michelson Contrast = (I_max-I_min)/(I_max+I_min)
```

### 3.4 Threshold

Threshold는 Pixel 값을 기준으로 두 Class로 나눈다.

밝은 Object를 Foreground로 만들면:

```text
if pixel > T:
    output = 255
else:
    output = 0
```

어두운 Object를 Foreground로 만들면 반대로 Binary Inverse를 사용한다.

```text
if pixel <= T:
    output = 255
else:
    output = 0
```

Binary의 255는 “흰색으로 보인다”보다 **후속 처리에서 선택된 Foreground**라는 의미가 중요하다.

### 3.5 Global Manual Threshold

Image 또는 ROI 전체에 하나의 고정값 `T`를 적용한다.

장점:

- 빠르고 해석하기 쉬움
- Recipe Parameter가 명확함
- 조명이 안정적이고 분포가 분리되면 매우 강건

단점:

- 밝기 Drift와 위치별 Shading에 민감
- Product Lot별 반사율 변화에 취약

잘 맞는 예:

- Back Light 외곽
- 안정된 Dark Field의 밝은 Particle
- 일정한 조명에서 Dark Mark/Print

### 3.6 Otsu Threshold

Otsu는 Histogram을 두 Class로 나눌 때 Class 내부 분산이 작아지는 Threshold를 자동 선택한다.

잘 맞는 조건:

- Object와 Background가 두 분포를 형성
- ROI 안에서 두 Class가 의미 있는 면적을 차지
- 조명 Gradient가 작음

주의할 조건:

- 작은 Defect가 Pixel의 극히 일부
- Background가 여러 재질/Pattern으로 구성
- Histogram이 단봉형
- 정상 Image와 불량 Image에서 선택 Threshold가 크게 달라짐

Otsu가 “최적 검사 Threshold”를 보장하지 않는다. 한 Image의 Histogram 분할 기준일 뿐 Spec과 검출률은 별도로 검증한다.

### 3.7 Adaptive Threshold

각 Pixel 주변의 Local Mean 또는 Gaussian Weighted Mean을 기준으로 Threshold를 계산한다.

```text
T(x,y) = LocalMean(x,y) - C
```

장점:

- 완만한 조명 Gradient와 Shading에 대응
- 문서/OCR/Mark처럼 Local Contrast가 중요한 경우

단점:

- `Block Size`와 `C`에 민감
- Texture/Noise를 Foreground로 만들 수 있음
- 큰 Defect와 작은 Window가 충돌할 수 있음
- Parameter 의미가 Global Threshold보다 직관적이지 않음

Block Size는 검출하려는 Feature보다 충분히 큰 주변 Background를 포함해야 하며 홀수여야 한다.

### 3.8 Threshold 방식 비교

| 방식 | 기준 | 장점 | 약점 | 대표 적용 |
|---|---|---|---|---|
| Manual Global | Recipe의 고정 T | 빠름, 재현·해석 쉬움 | Brightness Drift | Back Light, 안정 조명 |
| Otsu | 현재 Histogram | Parameter 감소 | Class 비율/분포 의존 | 두 Peak가 명확한 분할 |
| Adaptive Mean | Local 평균-C | Shading 대응 | Texture/Noise | Print, 불균일 배경 |
| Adaptive Gaussian | Local 가중 평균-C | 중심 주변 반영 | 계산량/Parameter | Local Mark/문자 |
| Range/InRange | Low≤pixel≤High | 중간 밝기 선택 | 범위 관리 필요 | 특정 Gray/Color Band |

### 3.9 ROI와 Mask

- **Rectangular ROI**: Image의 사각형 일부를 처리
- **Mask**: 임의 형태의 유효 Pixel만 선택

```text
Full Image
┌──────────────────────────┐
│ irrelevant pattern       │
│       ┌──────────┐       │
│       │ inspect  │       │
│       │   ROI    │       │
│       └──────────┘       │
└──────────────────────────┘
```

ROI를 사용하면:

- Histogram이 검사 대상 분포를 더 잘 반영
- False Positive 감소
- 처리 시간 감소
- Recipe 의도가 명확

Align 전 고정 ROI를 사용하면 제품 이동 시 실제 부위가 벗어날 수 있다. Align 후 Transform된 ROI에서 Threshold를 수행한다.

### 3.10 Normalization

Min-Max Normalization:

```text
output = (input-min)/(max-min) × 255
```

장점:

- 좁은 Gray 범위를 Display/분석에 확대
- 일부 전처리에서 Contrast 확보

위험:

- Frame마다 Min/Max가 달라지면 동일 물체의 Gray 의미가 변함
- Noise/Outlier 하나가 범위를 결정
- 정상/불량 차이를 인위적으로 확대 또는 축소

검사에서는 고정 Calibration 범위, Percentile 기반 Stretch 또는 Reference 기반 보정을 고려한다. Review용 Normalize와 검사 원본을 분리한다.

### 3.11 Threshold Margin

정상 Background 최대값과 Object 최소값 사이 간격을 본다.

```text
Background distribution: 50~90
Object distribution:     150~210

Valid Threshold interval: 90 < T < 150
Margin width: 60 Gray Level
```

한 Sample이 아니라 여러 Lot, 위치, 시간의 분포를 겹쳐야 한다.

```text
Worst Background Max = 130
Worst Object Min     = 140
Available Margin     = 10
```

Margin이 작으면 Threshold 미세 조정보다 조명과 촬영 조건 개선이 우선일 수 있다.

### 3.12 Bit Depth와 Threshold

8-bit의 Threshold 128을 12-bit Image에 그대로 사용하면 의미가 다르다.

전체 범위의 50% 기준:

```text
8-bit:  255 × 0.5 ≈ 128
12-bit: 4095 × 0.5 ≈ 2048
16-bit: 65535 × 0.5 ≈ 32768
```

10/12-bit가 16-bit Container에 저장되는 경우 유효 Bit 정렬과 Black Level도 확인한다.

### 3.13 Binary 결과의 품질

Threshold 이후 다음을 확인한다.

- Foreground가 검사 Object와 일치하는가?
- Object 내부 Hole/Noise가 생겼는가?
- 서로 붙어야 할 영역이 끊겼는가?
- 서로 다른 Object가 붙었는가?
- FOV 가장자리/ROI 경계가 False Blob이 되었는가?
- Foreground 비율이 정상 범위인가?

다음 단계의 Morphology는 작은 결함을 지울 수도 있으므로 Threshold 원본과 전처리 결과를 함께 Review한다.

---

## 4. 그림으로 이해하기

### 4.1 Gray에서 Binary로

```text
Gray:    [ 20  45  80  125  160  210  250 ]
T=128
Binary:  [  0   0   0    0  255  255  255 ]
```

### 4.2 조명 Gradient에서 Global Threshold 실패

```text
Left side dark                         Right side bright
Background: 40 ───────────────────────────────► 140
Object:     100 ──────────────────────────────► 200

Global T=120:
왼쪽 Object 일부 누락 + 오른쪽 Background 일부 검출
```

### 4.3 Align과 ROI의 연결

```text
Reference ROI
    ↓ Align X/Y/Theta
Transformed ROI
    ↓ Histogram / Threshold
Binary Feature
    ↓ Blob / Measurement
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Back Light 외곽 검사

밝은 Background와 어두운 제품을 `THRESH_BINARY_INV`로 분리해 Contour와 Width를 측정한다. Edge가 포화/Blur되지 않도록 Exposure와 광원 Geometry를 조정한다.

### Dark Field Particle 검사

어두운 Background 위 밝은 Particle을 Threshold한 뒤 작은 Blob의 Area와 밝기를 측정한다. Background Texture와 Sensor Noise가 False Blob이 되지 않도록 Local Contrast와 크기 조건을 함께 사용한다.

### Mark/Print Presence

Align된 ROI에서 Dark Mark를 Binary로 분리하고 Foreground Area 또는 Pattern 특징으로 누락을 판정한다. ROI Alignment 없이 Threshold하면 위치 편차가 면적 변화처럼 보일 수 있다.

### Stain/불균일 검사

Global Threshold보다 Background Estimation 또는 Adaptive/Local Difference가 유리할 수 있다. 넓고 약한 얼룩은 단순 Pixel Threshold보다 Reference Difference와 통계 검사가 필요하다.

### Recipe Monitoring

Foreground Ratio, ROI Mean, Standard Deviation, Otsu Threshold 값을 Result에 기록하면 조명 Drift와 제품 분포 변화를 조기에 찾을 수 있다.

---

## 6. 숫자로 이해하기

### 예제 1: Threshold Margin

여러 정상 Sample에서:

```text
Background: mean=70, stddev=8
Object:     mean=170, stddev=10
```

각 분포의 `mean ± 3σ`를 보수적 범위로 보면:

```text
Background upper ≈ 70 + 3×8  = 94
Object lower     ≈ 170 - 3×10 = 140

Threshold interval: 94 < T < 140
Margin width: 46
```

정규분포 가정과 독립 Sample 조건을 확인해야 하며 실제 Worst Case 분포도 함께 본다.

### 예제 2: Min-Max Normalization

ROI Gray 범위가 50~200이고 Pixel 값이 100이라면:

```text
(100-50)/(200-50) × 255
= 50/150 × 255
= 85
```

다음 Frame의 범위가 80~180이면 같은 입력 100은:

```text
(100-80)/(180-80) × 255 = 51
```

Frame별 Min-Max Normalize가 절대 Threshold 의미를 바꾸는 예다.

### 예제 3: Foreground Ratio

ROI가 `400×300=120,000 Pixel`이고 Binary Foreground가 18,600 Pixel이면:

```text
Foreground Ratio = 18,600 / 120,000 × 100
                 = 15.5%
```

정상 범위가 14~17%라면 15.5%는 범위 안이지만 Blob 분리 상태와 위치도 확인해야 한다.

### 예제 4: Bit Depth Threshold 변환

8-bit Threshold 180과 같은 전체 범위 비율을 12-bit로 변환하면:

```text
Normalized ratio = 180 / 255 ≈ 0.705882
12-bit threshold = 0.705882 × 4095 ≈ 2891
```

Gamma, Black Level과 Sensor Response가 다르면 단순 비례값이 동일한 광학 조건을 보장하지 않는다.

---

## 7. C++ 구현

### C++17/OpenCV Threshold Pipeline

```cpp
#include <opencv2/opencv.hpp>

#include <cmath>
#include <limits>
#include <stdexcept>

enum class ThresholdMode {
    Manual,
    Otsu,
    AdaptiveMean,
    AdaptiveGaussian
};

struct ThresholdRecipe final {
    ThresholdMode mode{ThresholdMode::Manual};
    double manualThreshold{128.0};
    bool inverse{false};
    int gaussianKernel{1};
    int adaptiveBlockSize{31};
    double adaptiveC{5.0};
};

struct ThresholdResult final {
    cv::Mat binary;
    double usedGlobalThreshold{};
    double foregroundRatio{};
};

[[nodiscard]] ThresholdResult ApplyThreshold(
    const cv::Mat& gray,
    const ThresholdRecipe& recipe)
{
    if (gray.empty() || gray.type() != CV_8UC1) {
        throw std::invalid_argument{"CV_8UC1 image is required"};
    }
    if (recipe.gaussianKernel <= 0 || recipe.gaussianKernel % 2 == 0) {
        throw std::invalid_argument{"Gaussian kernel must be positive and odd"};
    }

    cv::Mat filtered;
    if (recipe.gaussianKernel == 1) {
        filtered = gray;
    } else {
        cv::GaussianBlur(gray, filtered,
                         cv::Size{recipe.gaussianKernel, recipe.gaussianKernel},
                         0.0);
    }

    cv::Mat binary;
    double usedThreshold = std::numeric_limits<double>::quiet_NaN();
    const int baseType = recipe.inverse ? cv::THRESH_BINARY_INV
                                        : cv::THRESH_BINARY;

    switch (recipe.mode) {
    case ThresholdMode::Manual:
        if (!std::isfinite(recipe.manualThreshold) ||
            recipe.manualThreshold < 0.0 || recipe.manualThreshold > 255.0) {
            throw std::invalid_argument{"Manual threshold must be in [0,255]"};
        }
        usedThreshold = cv::threshold(filtered, binary,
                                      recipe.manualThreshold, 255.0, baseType);
        break;

    case ThresholdMode::Otsu:
        usedThreshold = cv::threshold(filtered, binary, 0.0, 255.0,
                                      baseType | cv::THRESH_OTSU);
        break;

    case ThresholdMode::AdaptiveMean:
    case ThresholdMode::AdaptiveGaussian:
        if (recipe.adaptiveBlockSize <= 1 ||
            recipe.adaptiveBlockSize % 2 == 0 ||
            recipe.adaptiveBlockSize > std::min(gray.rows, gray.cols)) {
            throw std::invalid_argument{
                "Adaptive block size must be odd and fit the image"};
        }
        cv::adaptiveThreshold(
            filtered, binary, 255.0,
            recipe.mode == ThresholdMode::AdaptiveMean
                ? cv::ADAPTIVE_THRESH_MEAN_C
                : cv::ADAPTIVE_THRESH_GAUSSIAN_C,
            baseType, recipe.adaptiveBlockSize, recipe.adaptiveC);
        break;
    }

    const double foregroundRatio =
        static_cast<double>(cv::countNonZero(binary)) /
        static_cast<double>(binary.total());

    return {binary, usedThreshold, foregroundRatio};
}
```

### Histogram 계산

```cpp
[[nodiscard]] cv::Mat CalculateHistogram256(const cv::Mat& gray)
{
    if (gray.empty() || gray.type() != CV_8UC1) {
        throw std::invalid_argument{"CV_8UC1 image is required"};
    }

    constexpr int channel = 0;
    constexpr int bins = 256;
    const float range[] = {0.0F, 256.0F};
    const float* ranges[] = {range};
    cv::Mat histogram;

    cv::calcHist(&gray, 1, &channel, cv::Mat{}, histogram,
                 1, &bins, ranges, true, false);
    return histogram;
}
```

### Unit Test

```cpp
#include <cassert>
#include <cmath>

void TestManualThreshold()
{
    cv::Mat image(100, 100, CV_8UC1, cv::Scalar(50));
    image(cv::Rect{50, 0, 50, 100}).setTo(200);

    ThresholdRecipe recipe;
    recipe.mode = ThresholdMode::Manual;
    recipe.manualThreshold = 128.0;

    const auto result = ApplyThreshold(image, recipe);
    assert(std::abs(result.foregroundRatio - 0.5) < 1e-12);
    assert(result.usedGlobalThreshold == 128.0);
}

void TestOtsuSeparatesTwoLevels()
{
    cv::Mat image(100, 100, CV_8UC1, cv::Scalar(50));
    image(cv::Rect{50, 0, 50, 100}).setTo(200);

    ThresholdRecipe recipe;
    recipe.mode = ThresholdMode::Otsu;

    const auto result = ApplyThreshold(image, recipe);
    assert(std::abs(result.foregroundRatio - 0.5) < 1e-12);
    assert(std::isfinite(result.usedGlobalThreshold));
}

void TestInversePolarity()
{
    const cv::Mat image =
        (cv::Mat_<unsigned char>(1, 3) << 10, 100, 200);
    ThresholdRecipe recipe;
    recipe.manualThreshold = 128.0;
    recipe.inverse = true;

    const auto result = ApplyThreshold(image, recipe);
    assert(result.binary.at<unsigned char>(0, 0) == 255);
    assert(result.binary.at<unsigned char>(0, 2) == 0);
}
```

### 코드에서 봐야 할 점

1. 입력 Type을 `CV_8UC1`로 제한해 Threshold 의미를 명확히 했다.
2. Manual/Otsu/Adaptive 방식과 Polarity를 Recipe로 분리했다.
3. Gaussian Kernel과 Adaptive Block Size를 사용 전 검증한다.
4. Adaptive 방식에는 단일 Global Threshold가 없으므로 `NaN`으로 표현한다.
5. Binary와 함께 사용 Threshold 및 Foreground Ratio를 Result로 남긴다.
6. 실제 검사는 Align 후 ROI를 전달하고 원본/중간/결과 Image를 Review 가능하게 저장한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: 조명 열화로 고정 Threshold 실패

- 증상: 시간 경과에 따라 Foreground Area 감소
- 대응: ROI Mean/Histogram Monitoring, 조명 안정화, Threshold Margin 재검증

### 문제 2: Auto Exposure와 Otsu를 동시에 사용

- 증상: Frame마다 Image와 Threshold가 함께 변해 결과 원인 추적이 어려움
- 대응: Camera Parameter 고정, Otsu 값과 분포 기록, 허용 범위 설정

### 문제 3: 전체 Image Histogram 사용

- 증상: 큰 Background가 Histogram을 지배해 작은 Defect 분포가 사라짐
- 대응: Align된 검사 ROI와 Feature/Background Mask 사용

### 문제 4: Adaptive Block Size가 Feature보다 작음

- 증상: Object 내부가 Background처럼 사라지거나 Edge만 남음
- 대응: Feature와 조명 Gradient Scale을 기준으로 Window 설정

### 문제 5: Frame별 Normalize 후 고정 Threshold

- 증상: Outlier와 정상 Variation에 따라 동일 Gray가 다른 값으로 변환
- 대응: 검사 Normalize 기준 고정 또는 Reference 기반, Raw 통계 저장

### 문제 6: Foreground Polarity 반대

- 증상: Object가 아니라 Background 전체가 Blob으로 검출
- 대응: Recipe에 밝은/어두운 Object 정의, Foreground Ratio Sanity Check

### 문제 7: 12-bit Container 해석 오류

- 증상: Threshold 범위가 비정상이고 Histogram이 한쪽에 몰림
- 대응: Pixel Format, 유효 Bit, Alignment, Black Level 확인

---

## 9. 흔한 오해

1. **“Otsu는 항상 최적 Threshold를 찾는다.”**  
   현재 Histogram의 두 Class 분할값이지 검사 Spec 최적값이 아니다.

2. **“Binary 255는 항상 실제 Object다.”**  
   알고리즘이 Foreground로 선택한 Pixel일 뿐 Polarity에 따라 의미가 달라진다.

3. **“Contrast가 크면 Threshold는 항상 안정적이다.”**  
   Noise, 분포 Tail, 위치별 Shading과 Lot Variation을 함께 봐야 한다.

4. **“Adaptive Threshold가 Global보다 고급이므로 더 좋다.”**  
   Texture와 Noise에 민감하고 Parameter가 늘어난다. 안정 조명에서는 Global이 더 단순하고 강건할 수 있다.

5. **“Normalization하면 원본 정보가 좋아진다.”**  
   값의 표현 범위를 바꿀 뿐 손실된 Optical Contrast를 복구하지 않는다.

6. **“Threshold만 잘 조정하면 조명 문제를 해결한다.”**  
   정상/불량 분포가 겹치면 조명 Geometry와 촬영 조건을 먼저 개선해야 한다.

7. **“Foreground Ratio가 정상이라면 Binary도 정상이다.”**  
   같은 면적이어도 위치와 Shape가 틀릴 수 있으므로 Blob Geometry를 확인한다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. Threshold는 검사 Pipeline에서 어떤 역할을 하나요?

**초보자가 이해할 수 있는 답변**  
Gray Image를 기준 밝기보다 밝거나 어두운 두 그룹으로 나눠 검사할 Object 후보를 만듭니다.

**실무자 답변**  
Threshold는 Gray Feature를 Binary Foreground/Background로 분할하는 Segmentation 단계다. 이후 Morphology, Blob, Contour와 Measurement가 사용한다. ROI, Polarity, Bit Depth와 조명 Variation을 포함해 Parameter Margin을 검증한다.

**면접용 30초 답변**  
“Threshold는 Gray Image에서 검사 대상 후보를 Binary Foreground로 분리하는 단계입니다. Align된 ROI에 적용하고 Polarity와 Bit Depth를 명확히 하며, 여러 Lot의 Background 최대와 Object 최소 사이 Margin을 검증한 뒤 Blob/Measurement로 연결합니다.”

### Q2. Manual과 Otsu Threshold의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Manual은 사람이 고정값을 정하고 Otsu는 현재 Histogram을 두 그룹으로 잘 나누는 값을 자동 계산합니다.

**실무자 답변**  
Manual은 Parameter 의미와 재현성이 명확하지만 Drift에 민감하다. Otsu는 Bimodal Histogram에 유리하지만 Object 비율과 분포 변화에 따라 값이 바뀐다. 선택 Threshold와 품질 분포를 Result에 기록한다.

**면접용 30초 답변**  
“Manual은 Recipe에 고정 Threshold를 두어 빠르고 해석하기 쉽습니다. Otsu는 현재 Histogram의 Class 내 분산을 최소화해 자동 선택하지만 작은 Defect나 단봉 Histogram에는 부적합할 수 있습니다. 조명 안정성과 분포 형태로 선택합니다.”

### Q3. Adaptive Threshold는 언제 사용하나요?

**초보자가 이해할 수 있는 답변**  
Image 위치마다 밝기가 달라 하나의 Threshold로 분리하기 어려울 때 주변 밝기를 기준으로 사용합니다.

**실무자 답변**  
완만한 Shading 아래 Local Mark/Print처럼 Feature Scale과 Background Scale이 분리될 때 사용한다. Block Size는 Feature보다 큰 Background 문맥을 포함해야 하며 Texture/Noise와 경계 Artifact를 검증한다.

**면접용 30초 답변**  
“Global Threshold가 조명 Gradient 때문에 실패할 때 Local Mean 또는 Gaussian 기준의 Adaptive Threshold를 검토합니다. Block Size와 C가 Feature 크기보다 적절한지 확인하고 Texture를 False Foreground로 만들지 않는지 검증합니다.”

### Q4. Threshold가 조명 변화에 민감한 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
조명이 바뀌면 같은 물체의 Pixel 값이 바뀌어 원래 Threshold의 반대쪽으로 이동할 수 있기 때문입니다.

**실무자 답변**  
Threshold는 Absolute 또는 Local Gray 분포를 기준으로 한다. LED 온도/열화, Exposure, 표면 반사와 위치별 Shading이 Object/Background 분포를 이동·확장해 Tail이 겹친다. 조명 안정화와 CNR/Threshold Margin 관리가 우선이다.

**면접용 30초 답변**  
“Pixel 값은 물체 고유값이 아니라 조명·Exposure·반사의 결과입니다. 변화가 Object와 Background 분포를 이동시켜 Threshold Margin을 줄입니다. 그래서 ROI Histogram과 분포를 Monitoring하고 광학 조건을 안정화한 뒤 Parameter를 정합니다.”

### Q5. ROI에서 Histogram을 봐야 하는 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
전체 Image에는 검사와 관계없는 Background가 많아 실제 검사 부위의 밝기 분포를 가릴 수 있기 때문입니다.

**실무자 답변**  
Global Histogram은 면적이 큰 무관 영역에 지배된다. Align된 ROI 또는 Mask에서 Feature/Background 분포를 측정해야 Threshold Margin과 CNR이 실제 검사 조건을 반영한다.

**면접용 30초 답변**  
“작은 Defect는 전체 Image Histogram에서 거의 보이지 않고 큰 Background가 분포를 지배합니다. Align 후 검사 ROI와 Feature/Background Mask의 Histogram을 분리해 Threshold Margin과 Variation을 평가해야 합니다.”

### Q6. Normalization 사용 시 주의할 점은 무엇인가요?

**초보자가 이해할 수 있는 답변**  
매 Image의 최소·최대값으로 바꾸면 같은 밝기의 Pixel도 Frame마다 다른 값이 될 수 있습니다.

**실무자 답변**  
Frame별 Min-Max는 Outlier와 Sample 구성에 따라 Transfer Function이 변해 Fixed Threshold와 Image 간 비교를 깨뜨린다. Display와 Inspection 경로를 분리하고 고정/Reference/Percentile 기준의 Robustness를 검증한다.

**면접용 30초 답변**  
“Normalization은 Contrast 표현을 넓히지만 Frame별 Min-Max를 쓰면 Gray의 절대 의미가 사라집니다. 검사에는 고정 또는 Reference 기반 Mapping을 사용하고 Raw 통계와 변환 Parameter를 함께 남기며 Display용 변환과 분리합니다.”

---

## 11. 실습 문제

### 실습 1: Histogram과 Threshold Sweep

동일 ROI에서 Threshold를 50~220까지 5씩 변경하며 다음을 저장한다.

- Foreground Ratio
- Blob Count
- Largest Blob Area
- 정상/불량 판정

안정적으로 같은 결과를 내는 Threshold 구간을 찾는다.

### 실습 2: 조명 Drift 시뮬레이션

Gray Image에 `-30,-15,0,+15,+30` Offset을 적용하고 Manual/Otsu/Adaptive 결과를 비교한다. 각 방식의 Foreground Area 변화와 실패 유형을 기록한다.

### 실습 3: ROI와 전체 Histogram 비교

작은 Defect가 있는 Image에서 전체 Histogram과 Defect 주변 ROI Histogram을 비교한다. 작은 결함 분포가 전체 Histogram에서 보이지 않는 이유를 Pixel 면적 비율로 설명한다.

### 실습 4: 12-bit Threshold

12-bit 유효 Image에서 Histogram, Threshold, 8-bit Display 변환을 분리한다. 유효 범위가 0~4095인지 MSB 정렬인지 확인하고 동일 비율 Threshold를 계산한다.

### Phase 7-1 미니 프로젝트: Threshold Inspection Workbench

```text
Image Load
   ↓
ROI/Mask 선택
   ↓
Histogram + Mean/StdDev
   ↓
Manual / Otsu / Adaptive Threshold
   ↓
Binary Preview + Foreground Ratio
   ↓
Threshold Sweep
   ↓
Result CSV + Intermediate Image Save
```

**필수 기능**

- 원본 Image 불변 유지
- Threshold Mode와 Polarity Recipe 저장
- ROI 밖 Pixel이 통계에 포함되지 않도록 처리
- 사용 Threshold, Foreground Ratio와 처리 시간 기록
- 정상/빈 ROI/잘못된 Type Unit Test
- Frame별 Normalize 사용 여부와 Mapping 값 기록

---

## 12. Chapter 핵심 요약

- 🔴 Histogram은 Gray 분포를 보여주지만 위치 정보는 없다.
- 🔴 Threshold는 Gray Image를 Binary Foreground/Background로 분리한다.
- 🔴 Binary 255는 Object 자체가 아니라 선택된 Foreground다.
- 🔴 Manual, Otsu, Adaptive 방식은 분포와 조명 조건에 따라 선택한다.
- 🔴 Align된 ROI에서 Histogram과 Threshold를 적용해야 한다.
- 🔴 여러 Sample의 분포로 Threshold Margin을 검증한다.
- 🔴 8/12/16-bit Threshold 범위와 Pixel Format을 구분한다.
- 🟠 Frame별 Min-Max Normalize는 Gray의 절대 의미를 바꾼다.
- 🟠 Foreground Ratio는 Sanity Check이며 Shape/위치 검증을 대체하지 않는다.
- 🟠 Threshold 실패가 조명 문제라면 Parameter보다 광학 조건을 먼저 개선한다.

---

## 9일차 권장 학습 순서

- [ ] 40분: Gray/Histogram/Brightness/Contrast 정리
- [ ] 50분: Manual/Otsu/Adaptive 비교
- [ ] 40분: ROI, Polarity, Bit Depth 주의사항
- [ ] 60~90분: C++ Threshold Pipeline 구현
- [ ] 60분: Threshold Sweep 및 Drift 실습
- [ ] 30분: 면접 Q1~Q6 30초 답변 연습

## 학습 완료 체크

- [ ] ROI Histogram을 읽고 두 분포와 Margin을 설명한다.
- [ ] Manual/Otsu/Adaptive의 적용 조건을 구분한다.
- [ ] Foreground Polarity를 명확히 정의한다.
- [ ] 8/12-bit Threshold를 올바른 범위로 계산한다.
- [ ] Normalize가 검사 결과를 흔들 수 있는 이유를 설명한다.
- [ ] Threshold Pipeline과 Sweep Tool을 설계하거나 구현했다.

## 다음 학습 예고

다음 영상처리 Chapter에서는 Mean/Gaussian/Median/Bilateral Filter, Gradient, Sobel, Canny와 Edge Position 측정을 연결한다.
