# 10일차. 영상처리 기초 2: Filtering · Gradient · Edge

> Phase 7-2 · 예상 학습 시간: 10~14시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Filter를 사용하는 이유와 Kernel/Convolution의 의미
- 🔴 Mean, Gaussian, Median, Bilateral Filter의 차이
- 🔴 Noise 제거와 Detail/Edge 보존의 Trade-off
- 🔴 Gradient, Magnitude, Direction
- 🔴 Sobel과 Canny Edge Detection
- 🔴 Edge Polarity와 Search Direction
- 🔴 Edge Position으로 Width/Distance 측정
- 🟠 Border 처리와 ROI 경계 Artifact
- 🟠 Edge Spread, Sub-pixel 위치와 측정 반복성
- 🟠 Filter/Edge Parameter 검증 방법

### 실무 목표

Noise 종류와 검사 Feature 크기를 기준으로 Filter를 선택하고, Sobel/Canny 결과를 단순히 보기 좋은 Edge Image가 아니라 위치·폭·방향·연결성 측정에 사용한다. Filter가 작은 Defect를 제거하거나 Edge 위치를 이동시킬 수 있음을 이해하고 실제 Sample에서 Bias와 Repeatability를 검증한다.

---

## 2. 선수 지식

- [[09-image-processing-01-threshold|9일차]]의 Gray, Histogram, ROI, Binary
- Pixel 좌표와 `CV_8UC1`
- 평균, 중앙값, 표준편차
- 미분은 “위치에 따른 값의 변화량”이라는 직관

### 2.1 오늘의 Pipeline 위치

```text
Gray ROI
   ↓
Noise/Texture 확인
   ↓
Filter 선택
   ↓
Gradient/Sobel/Canny
   ↓
Edge 후보
   ↓
방향·Polarity·연결성 Filtering
   ↓
Edge Position / Width / Distance / Angle
```

Filter와 Edge Detection은 목적 없이 연속 적용하는 고정 절차가 아니다. 원본 Image와 검사 Feature에 따라 필요한 단계만 선택한다.

---

## 3. 핵심 개념

### 3.1 Filtering을 왜 사용하는가?

Filtering의 목적:

- Random Noise 완화
- 작은 밝기 Spike 제거
- Background의 완만한 변화 추정
- Edge/Line 같은 특정 특징 강조
- Downstream Threshold와 Edge 결과 안정화

그러나 모든 Smoothing Filter는 어느 정도 Detail을 잃는다.

```text
Noise 감소 ↑
      ↕ Trade-off
작은 Defect/Sharp Edge 보존 ↓
```

Kernel 크기를 결함보다 크게 잡으면 검사하려던 결함 자체를 지울 수 있다.

### 3.2 Kernel과 Convolution

Kernel은 주변 Pixel을 어떤 가중치로 결합할지 정의한 작은 행렬이다.

3×3 Mean Kernel:

```text
1/9 × [1 1 1
       1 1 1
       1 1 1]
```

각 출력 Pixel은 주변 3×3 Pixel 평균이 된다. Convolution은 Kernel을 Image 위로 이동하며 이 계산을 반복하는 과정이다.

확인할 Parameter:

- Kernel Size: 3×3, 5×5, 7×7...
- Weight/Shape
- Border 처리
- 입력/출력 Depth
- ROI와 Feature 크기의 관계

### 3.3 Mean Filter

주변 Pixel을 동일 가중치로 평균한다.

장점:

- 단순하고 빠름
- Random Noise 완화
- Background 평균화

단점:

- Edge와 작은 Defect를 쉽게 Blur
- Salt-and-Pepper Noise에 강하지 않음
- 큰 Kernel에서 Detail 손실

검사 적용:

- 완만한 Background 추정
- 정밀 Edge 측정 전보다 대략적 Segmentation 전처리
- Difference Image의 작은 Random Noise 완화

### 3.4 Gaussian Filter

중심 Pixel에 큰 가중치, 멀수록 작은 가중치를 사용한다.

```text
근사 3×3 Gaussian Kernel
1/16 × [1 2 1
        2 4 2
        1 2 1]
```

Parameter:

- Kernel Size
- `sigma`: Gaussian 분포 폭

장점:

- Mean보다 자연스러운 Low-pass
- Gaussian 계열 Random Noise 완화
- Canny 전처리의 일반적인 선택

단점:

- Edge와 작은 Feature가 여전히 Blur
- sigma/Kernel이 커지면 Edge Spread 증가

### 3.5 Median Filter

주변 Pixel을 정렬한 뒤 중앙값으로 대체하는 비선형 Filter다.

```text
[10, 11, 10,
 12,255, 11,
 10, 12, 11]

정렬 중앙값 = 11
```

중앙의 255 Spike가 제거된다.

장점:

- Salt-and-Pepper/Impulse Noise에 강함
- Mean보다 일부 Edge를 잘 보존

단점:

- 작은 Point/Line Defect도 Noise로 보고 제거할 수 있음
- 큰 Kernel에서 형상 변형
- Gaussian Noise에는 항상 최선이 아님

Particle 검사가 목표라면 Median이 Particle을 지우지 않는지 반드시 확인한다.

### 3.6 Bilateral Filter

공간적으로 가까운 Pixel뿐 아니라 밝기가 비슷한 Pixel에 더 큰 가중치를 주는 Edge-preserving Filter다.

- `sigmaSpace`: 공간 거리 영향
- `sigmaColor`: Gray 차이 허용 범위

장점:

- 영역 내부 Noise를 줄이면서 큰 Edge 보존

단점:

- Mean/Gaussian보다 계산량이 큼
- Parameter 의미와 성능 최적화가 복잡
- 약한 Defect Contrast가 Background와 섞일 수 있음

실시간 검사에서는 처리 시간과 실제 개선량을 측정하고 사용한다.

### 3.7 Filter 선택표

| 상황 | 1차 후보 | 이유 | 주요 위험 |
|---|---|---|---|
| Gaussian 계열 Random Noise | Gaussian | 주파수/공간적으로 안정적 Smoothing | Edge Spread |
| Salt-and-Pepper Spike | Median | Outlier 제거 | 작은 Particle 제거 |
| 단순 Background 평균화 | Mean/Gaussian | 빠르고 해석 쉬움 | Detail 손실 |
| 큰 Edge 보존하며 영역 Noise 감소 | Bilateral | 밝기 차이 보존 | 느림, 약한 Defect 손실 |
| 매우 작은 Scratch/Particle | No Filter 또는 작은 Gaussian | Feature 보존 우선 | Noise 증가 |

### 3.8 Gradient

Gradient는 x/y 방향 Gray 변화량이다.

```text
Gx = x 방향 미분
Gy = y 방향 미분

Magnitude = sqrt(Gx² + Gy²)
Direction = atan2(Gy, Gx)
```

- 수직 Edge: x 방향 변화가 크므로 `|Gx|`가 큼
- 수평 Edge: y 방향 변화가 크므로 `|Gy|`가 큼

Gradient 부호는 밝기 변화 방향을 나타낸다.

```text
Dark → Bright: Positive Edge
Bright → Dark: Negative Edge
```

부호를 활용하면 원하는 방향의 Edge만 선택할 수 있다.

### 3.9 Sobel Operator

대표적인 3×3 x 방향 Sobel Kernel:

```text
[-1 0 +1
 -2 0 +2
 -1 0 +1]
```

y 방향:

```text
[-1 -2 -1
  0  0  0
 +1 +2 +1]
```

Sobel은 미분과 약한 Smoothing을 결합한다. 출력은 8-bit 범위를 넘거나 음수가 될 수 있으므로 `CV_16S` 또는 `CV_32F`로 계산해야 한다.

> [!WARNING]
> Sobel 결과를 바로 `CV_8U`에 저장하면 Negative Gradient가 사라지고 큰 값이 Saturation되어 방향과 크기 정보를 잃을 수 있다.

### 3.10 Canny Edge Detection

Canny의 주요 단계:

```text
Gaussian Smoothing
   ↓
Gradient 계산
   ↓
Non-Maximum Suppression
   ↓
Double Threshold
   ↓
Hysteresis Tracking
```

- High Threshold 이상: Strong Edge
- Low~High 사이: Strong Edge와 연결되면 유지
- Low 미만: 제거

장점:

- 비교적 얇고 연결된 Binary Edge
- 후속 Contour/Line 검출에 편리

단점:

- Low/High Threshold와 Blur Parameter에 민감
- Texture가 많으면 Edge가 과다 발생
- Gradient 크기와 Polarity 정보가 Binary 결과에서 사라짐

치수 측정에서는 Canny Pixel을 그대로 사용하는 것보다 1D Profile/Gradient Peak와 Sub-pixel Fit이 더 적합할 수 있다.

### 3.11 Edge Detection과 Edge Measurement

- **Detection**: Edge가 있는 Pixel 후보를 찾음
- **Localization**: Edge 위치를 결정
- **Measurement**: 두 Edge 간 거리/각도를 실제 단위로 계산

```text
Left Edge x₁ = 120.3 pixel
Right Edge x₂ = 320.8 pixel

Width = (x₂-x₁) × scale
```

정밀 Measurement에는 다음을 확인한다.

- Search Direction
- Edge Polarity
- Gradient Peak 선택
- 여러 Edge 중 올바른 Edge ID
- Sub-pixel 방법
- Calibration Scale/Distortion
- Filter에 의한 Bias

### 3.12 1D Edge Profile

2D Image에서 측정 방향을 따라 여러 Scan Line을 평균하면 Noise를 줄이고 Edge Profile을 얻을 수 있다.

```text
ROI 여러 행 평균
    ↓
1D Gray Profile
    ↓ derivative
1D Gradient
    ↓
Peak Position = Edge
```

평균할 행 수가 많으면 Noise는 줄지만 기울어진 Edge나 Curved Edge가 퍼질 수 있다. Align 후 Edge 방향과 Profile 방향을 맞춘다.

### 3.13 Sub-pixel Edge

Edge 주변 Gradient Peak를 Parabola/Gaussian/Line Model 등으로 Fit하여 Pixel 사이 위치를 추정할 수 있다.

Sub-pixel은 실제 Optical Resolution을 초월하는 새 Detail이 아니다. 충분한 SNR과 안정된 Edge Shape에서 위치 반복성을 개선하는 추정 방법이다.

다음이 바뀌면 Bias가 달라질 수 있다.

- Focus/Blur
- Threshold/Gradient Kernel
- 조명과 Edge Polarity
- Pixel Phase
- Lens Distortion

### 3.14 Border 처리

Kernel이 Image/ROI 경계를 벗어나면 OpenCV는 Border 값을 만들어 계산한다.

대표 방식:

- Replicate
- Reflect
- Constant

ROI를 잘라 Filter하면 ROI 밖 문맥이 사라져 경계에 Artifact가 생길 수 있다. 필요하면 ROI를 Margin만큼 확장해 처리한 뒤 원래 ROI로 Crop한다.

---

## 4. 그림으로 이해하기

### 4.1 Noise와 Filter

```text
Original:   ___/¯¯¯¯¯\___  + random spikes
Gaussian:   __/~~~~~\__      noise↓ edge spread↑
Median:     ___/¯¯¯¯¯\___      impulse removed
```

### 4.2 Edge와 Gradient

```text
Gray Profile:      20  20  25  80 180 220 220
Gradient:           0   5  55 100  40   0
                                ▲
                           Edge 후보 위치
```

### 4.3 실제 측정 흐름

```text
Align된 Measurement ROI
          ↓
방향에 수직인 Gray Profile
          ↓
Filter + Gradient
          ↓
Polarity/Strength로 Left·Right Edge 선택
          ↓
Sub-pixel Position
          ↓
Pixel Distance × Calibration
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Back Light Width 측정

고Contrast 외곽에서 좌→우 Profile을 만들고 Negative/Positive Edge Pair를 선택해 Width를 구한다. Canny 전체 Contour보다 측정 방향과 Edge Pair를 명시하는 방식이 해석하기 쉽다.

### Scratch 검사

조명 방향과 Scratch 방향에 맞춰 Gradient/Line Response를 사용한다. Gaussian Blur가 너무 크면 얇은 Scratch가 사라지고, 너무 작으면 Texture Edge가 과다 검출된다.

### Gap 검사

두 부품 Edge를 각각 찾고 Calibration된 거리로 Gap을 측정한다. 잘못된 내부 Texture Edge를 선택하지 않도록 Search Range, Polarity, Expected Position을 사용한다.

### Particle 전처리

Impulse Noise는 Median으로 줄일 수 있지만 실제 Particle도 함께 제거될 수 있다. Raw Image와 Filtered Image의 Blob Area/Count 차이를 검증한다.

### Focus Monitoring

Golden Edge의 Gradient Peak, Edge Spread Width, Laplacian Variance 등을 추적해 Focus 변화를 감시할 수 있다. 제품 Pattern 변화와 Focus 변화를 구분할 Reference가 필요하다.

---

## 6. 숫자로 이해하기

### 예제 1: Mean Filter와 Impulse

3×3 영역에서 중심만 255이고 나머지가 0이라면:

```text
[0   0   0
 0 255   0
 0   0   0]

Mean = 255 / 9 ≈ 28.33
```

한 Pixel Spike가 주변 3×3 영역으로 낮게 퍼진다. Median은 9개 중 중앙값 0을 선택해 Spike를 제거한다.

### 예제 2: Sobel Gx

3×3 Patch가 왼쪽 0, 오른쪽 100이라고 하자.

```text
Image:        Sobel Gx:
[0 0 100]     [-1 0 1]
[0 0 100]  ×  [-2 0 2]  → 100+200+100 = 400
[0 0 100]     [-1 0 1]
```

출력이 255보다 크므로 8-bit에 바로 저장하면 Magnitude를 잃는다. `CV_32F`에서 400으로 유지한 뒤 Display/Threshold 목적에 맞게 변환한다.

### 예제 3: Edge Width Measurement

```text
Left Edge  = 120.3 pixel
Right Edge = 320.8 pixel
Scale      = 5 μm/pixel

Pixel Width = 320.8-120.3 = 200.5 pixel
Object Width = 200.5×5 = 1002.5 μm = 1.0025 mm
```

Scale이 단일값으로 유효하다는 전제이며 정밀 측정에는 Calibration Transform을 사용한다.

### 예제 4: Profile 평균과 Noise

서로 독립이고 같은 표준편차 `σ=12`인 Scan Line 16개를 평균하면 이상적으로 평균 Noise 표준편차는:

```text
σ_mean = 12 / sqrt(16) = 3
```

실제 Image Noise가 공간적으로 상관되어 있거나 Edge가 기울어져 있으면 이론만큼 줄지 않는다.

### 예제 5: Canny Threshold

Gradient Magnitude가 다음과 같고 Low=40, High=100이라면:

```text
30  → 제거
60  → Weak Edge, Strong Edge와 연결될 때 유지
130 → Strong Edge
```

Low/High 비율에 보편적인 정답은 없다. 실제 Edge/Noise Gradient 분포로 정한다.

---

## 7. C++ 구현

### Filter와 Edge Pipeline

```cpp
#include <opencv2/opencv.hpp>

#include <cmath>
#include <stdexcept>

enum class FilterType {
    None,
    Mean,
    Gaussian,
    Median,
    Bilateral
};

enum class EdgeType {
    Sobel,
    Canny
};

struct FilterRecipe final {
    FilterType type{FilterType::Gaussian};
    int kernelSize{3};
    double gaussianSigma{1.0};
    double bilateralSigmaColor{25.0};
    double bilateralSigmaSpace{3.0};
};

struct EdgeRecipe final {
    EdgeType type{EdgeType::Canny};
    double sobelMagnitudeThreshold{50.0};
    double cannyLowThreshold{40.0};
    double cannyHighThreshold{100.0};
};

struct EdgeResult final {
    cv::Mat filtered;
    cv::Mat gradientX;
    cv::Mat gradientY;
    cv::Mat magnitude;
    cv::Mat binaryEdges;
};

[[nodiscard]] cv::Mat ApplyFilter(
    const cv::Mat& gray,
    const FilterRecipe& recipe)
{
    if (gray.empty() || gray.type() != CV_8UC1) {
        throw std::invalid_argument{"CV_8UC1 image is required"};
    }
    if (recipe.kernelSize <= 0 || recipe.kernelSize % 2 == 0) {
        throw std::invalid_argument{"Kernel size must be positive and odd"};
    }

    cv::Mat output;
    if (recipe.type == FilterType::None || recipe.kernelSize == 1) {
        output = gray.clone();
        return output;
    }

    switch (recipe.type) {
    case FilterType::None:
        output = gray.clone();
        break;
    case FilterType::Mean:
        cv::blur(gray, output, cv::Size{recipe.kernelSize, recipe.kernelSize});
        break;
    case FilterType::Gaussian:
        if (!std::isfinite(recipe.gaussianSigma) ||
            recipe.gaussianSigma <= 0.0) {
            throw std::invalid_argument{"Gaussian sigma must be positive"};
        }
        cv::GaussianBlur(gray, output,
                         cv::Size{recipe.kernelSize, recipe.kernelSize},
                         recipe.gaussianSigma);
        break;
    case FilterType::Median:
        cv::medianBlur(gray, output, recipe.kernelSize);
        break;
    case FilterType::Bilateral:
        if (!std::isfinite(recipe.bilateralSigmaColor) ||
            !std::isfinite(recipe.bilateralSigmaSpace) ||
            recipe.bilateralSigmaColor <= 0.0 ||
            recipe.bilateralSigmaSpace <= 0.0) {
            throw std::invalid_argument{"Bilateral sigma must be positive"};
        }
        cv::bilateralFilter(gray, output, recipe.kernelSize,
                            recipe.bilateralSigmaColor,
                            recipe.bilateralSigmaSpace);
        break;
    }
    return output;
}

[[nodiscard]] EdgeResult DetectEdges(
    const cv::Mat& gray,
    const FilterRecipe& filterRecipe,
    const EdgeRecipe& edgeRecipe)
{
    EdgeResult result;
    result.filtered = ApplyFilter(gray, filterRecipe);

    cv::Sobel(result.filtered, result.gradientX, CV_32F, 1, 0, 3);
    cv::Sobel(result.filtered, result.gradientY, CV_32F, 0, 1, 3);
    cv::magnitude(result.gradientX, result.gradientY, result.magnitude);

    switch (edgeRecipe.type) {
    case EdgeType::Sobel:
        if (!std::isfinite(edgeRecipe.sobelMagnitudeThreshold) ||
            edgeRecipe.sobelMagnitudeThreshold < 0.0) {
            throw std::invalid_argument{"Invalid Sobel threshold"};
        }
        cv::compare(result.magnitude,
                    edgeRecipe.sobelMagnitudeThreshold,
                    result.binaryEdges, cv::CMP_GE);
        break;

    case EdgeType::Canny:
        if (!std::isfinite(edgeRecipe.cannyLowThreshold) ||
            !std::isfinite(edgeRecipe.cannyHighThreshold) ||
            edgeRecipe.cannyLowThreshold < 0.0 ||
            edgeRecipe.cannyLowThreshold >= edgeRecipe.cannyHighThreshold) {
            throw std::invalid_argument{"Invalid Canny thresholds"};
        }
        cv::Canny(result.filtered, result.binaryEdges,
                  edgeRecipe.cannyLowThreshold,
                  edgeRecipe.cannyHighThreshold,
                  3, true);
        break;
    }
    return result;
}
```

### Unit Test

```cpp
#include <cassert>

void TestMeanPreservesConstantImage()
{
    const cv::Mat image(20, 20, CV_8UC1, cv::Scalar(123));
    FilterRecipe recipe;
    recipe.type = FilterType::Mean;
    recipe.kernelSize = 5;

    const cv::Mat filtered = ApplyFilter(image, recipe);
    assert(cv::countNonZero(filtered != image) == 0);
}

void TestMedianRemovesSingleImpulse()
{
    cv::Mat image = cv::Mat::zeros(5, 5, CV_8UC1);
    image.at<unsigned char>(2, 2) = 255;

    FilterRecipe recipe;
    recipe.type = FilterType::Median;
    recipe.kernelSize = 3;

    const cv::Mat filtered = ApplyFilter(image, recipe);
    assert(filtered.at<unsigned char>(2, 2) == 0);
}

void TestCannyFindsVerticalStep()
{
    cv::Mat image = cv::Mat::zeros(100, 100, CV_8UC1);
    image(cv::Rect{50, 0, 50, 100}).setTo(255);

    FilterRecipe filter;
    filter.type = FilterType::Gaussian;
    filter.kernelSize = 3;
    EdgeRecipe edge;
    edge.type = EdgeType::Canny;
    edge.cannyLowThreshold = 40.0;
    edge.cannyHighThreshold = 100.0;

    const auto result = DetectEdges(image, filter, edge);
    assert(cv::countNonZero(result.binaryEdges) > 0);
    assert(result.gradientX.type() == CV_32FC1);
}
```

### 코드에서 봐야 할 점

1. Filter 선택과 Edge 선택을 독립 Recipe로 분리했다.
2. 입력 Image를 수정하지 않고 Filtered Image를 별도 생성한다.
3. Sobel Gx/Gy와 Magnitude를 `CV_32F`로 유지한다.
4. Canny를 사용하더라도 Gradient Image를 Result에 남겨 원인 분석이 가능하다.
5. Kernel Size, Sigma와 Threshold의 범위를 사용 전에 검증한다.
6. 실제 Measurement에서는 Binary Edge 전체가 아니라 방향/Polarity/예상 위치로 올바른 Edge를 선택한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: 큰 Gaussian Kernel로 작은 Defect가 사라짐

- 대응: Feature Width 대비 Kernel/Sigma Sweep, Raw/Filtered 검출률 비교

### 문제 2: Median이 실제 Particle 제거

- 대응: Noise와 최소 Particle 크기 분포 비교, Filter 전후 Blob Count 저장

### 문제 3: 8-bit Sobel로 Negative Edge 손실

- 대응: Signed/Float Depth에서 Gx/Gy 유지, Display 변환 분리

### 문제 4: Canny가 Texture를 모두 Edge로 검출

- 대응: 조명 개선, ROI, Gradient 방향/크기, 연결 길이와 형상 조건

### 문제 5: ROI 경계가 강한 Edge가 됨

- 대응: 원본 문맥 포함 Margin ROI에서 Filter/Edge 후 내부 ROI만 사용

### 문제 6: 여러 Edge 중 잘못된 Pair 선택

- 대응: Expected Position/Width, Polarity, Search Direction, Score와 Recipe Range

### 문제 7: Focus 변화로 측정 Bias

- 대응: Edge Spread/Gradient Monitoring, Calibration Target 반복 측정, Focus 관리

### 문제 8: Bilateral로 Cycle Time 초과

- 대응: ROI 축소, Parameter/해상도 최적화, 단순 Filter 대비 이득 계측

---

## 9. 흔한 오해

1. **“Filter를 많이 적용할수록 Image 품질이 좋다.”**  
   Noise와 함께 검사 Detail도 손실되며 단계마다 Bias가 추가될 수 있다.

2. **“Median은 Edge를 보존하므로 작은 Particle도 보존한다.”**  
   Kernel보다 작은 Point Feature는 제거될 수 있다.

3. **“Canny Edge가 곧 실제 Object 경계다.”**  
   Parameter와 Texture에서 생성된 후보이며 올바른 Edge ID를 선택해야 한다.

4. **“Sobel Magnitude만 보면 Edge 방향도 안다.”**  
   Magnitude는 절댓값 정보이고 Gx/Gy 또는 `atan2`가 방향을 제공한다.

5. **“Sub-pixel이면 Pixel Size보다 작은 Defect를 볼 수 있다.”**  
   안정된 Edge 위치를 추정하는 것이며 새로운 Optical Detail을 생성하지 않는다.

6. **“큰 Kernel은 Noise가 더 줄어 항상 유리하다.”**  
   Edge Spread와 Feature 손실, 처리 시간이 증가한다.

7. **“Edge Pixel 거리×Scale이면 정확한 치수다.”**  
   Distortion, Focus, Edge Model, Calibration과 반복성 오차를 포함해야 한다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. Mean, Gaussian, Median Filter의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Mean은 주변 평균, Gaussian은 중심에 더 큰 가중치를 둔 평균, Median은 정렬한 값의 중앙값을 사용합니다.

**실무자 답변**  
Mean/Gaussian은 Linear Low-pass로 Random Noise를 줄이지만 Edge를 Blur한다. Median은 비선형 Order Filter로 Impulse Noise에 강하지만 작은 Particle/Line을 제거할 수 있다. Noise와 최소 Feature 크기로 선택한다.

**면접용 30초 답변**  
“Mean은 동일 가중 평균, Gaussian은 거리 기반 가중 평균, Median은 주변 중앙값입니다. Gaussian은 Random Noise, Median은 Salt-and-Pepper에 주로 검토하며, 어떤 Filter든 최소 Defect와 Edge Bias를 실제 Sample로 확인합니다.”

### Q2. Bilateral Filter는 언제 사용하나요?

**초보자가 이해할 수 있는 답변**  
영역 내부 Noise는 줄이면서 밝기 차이가 큰 Edge는 최대한 유지하고 싶을 때 사용합니다.

**실무자 답변**  
공간 거리와 Intensity 차이를 함께 가중해 큰 Edge를 보존한다. sigmaColor/Space가 약한 결함 Contrast를 섞지 않는지와 높은 계산 비용이 Cycle Time에 가치가 있는지 검증한다.

**면접용 30초 답변**  
“Bilateral은 가까우면서 밝기도 비슷한 Pixel을 평균해 큰 Edge를 보존합니다. 다만 느리고 약한 Defect도 Background로 평활화할 수 있어 Gaussian 대비 검출률 개선과 처리 시간을 측정한 뒤 사용합니다.”

### Q3. Sobel Gx와 Gy는 무엇을 의미하나요?

**초보자가 이해할 수 있는 답변**  
Gx는 x 방향 밝기 변화, Gy는 y 방향 밝기 변화입니다. 수직 Edge는 Gx가 크고 수평 Edge는 Gy가 큽니다.

**실무자 답변**  
Sobel은 미분과 직교 방향 Smoothing을 결합한다. Signed Gx/Gy로 Polarity와 Gradient 방향을 얻고 Magnitude로 강도를 계산한다. 출력 범위를 위해 16-bit Signed 또는 Float를 사용한다.

**면접용 30초 답변**  
“Gx는 좌우 밝기 변화라 수직 Edge에, Gy는 상하 변화라 수평 Edge에 강하게 응답합니다. `sqrt(Gx²+Gy²)`로 강도, `atan2(Gy,Gx)`로 방향을 얻으며 부호는 Dark-to-Bright 같은 Polarity를 나타냅니다.”

### Q4. Canny의 Low/High Threshold는 어떤 역할인가요?

**초보자가 이해할 수 있는 답변**  
High보다 강하면 확실한 Edge, Low와 High 사이는 강한 Edge와 연결될 때만 유지합니다.

**실무자 답변**  
Double Threshold/Hysteresis가 약한 Edge 중 구조적으로 Strong Edge와 연결된 것만 보존한다. Gradient/Noise 분포, Filter와 조명 조건으로 정하고 Result의 연결성/False Edge를 검증한다.

**면접용 30초 답변**  
“High 이상은 Strong Edge, Low~High는 Strong Edge와 연결된 경우만 유지하는 Weak Edge입니다. 고정 비율을 맹신하지 않고 실제 Gradient 분포와 필요한 Edge 연결성, Texture 오검출을 기준으로 정합니다.”

### Q5. Edge로 치수를 측정할 때 무엇을 확인해야 하나요?

**초보자가 이해할 수 있는 답변**  
원하는 방향과 밝기 변화의 Edge인지 확인하고 두 Edge 위치 차이에 Calibration Scale을 적용합니다.

**실무자 답변**  
Search ROI/Direction, Polarity, Expected Position, Edge Strength와 Pair ID를 고정한다. Sub-pixel Model, Filter/Focus Bias, Distortion Calibration, Repeatability와 Gauge R&R을 검증한다.

**면접용 30초 답변**  
“먼저 Align된 ROI에서 Search 방향과 Polarity로 올바른 Edge Pair를 선택합니다. Sub-pixel 위치 차이에 Calibration을 적용하고, Focus·Filter·조명 변화에 따른 Bias와 반복 정밀도가 측정 공차를 만족하는지 확인합니다.”

### Q6. Filtering이 Edge 위치를 바꿀 수 있나요?

**초보자가 이해할 수 있는 답변**  
대칭적인 이상 Edge에서는 중심이 유지될 수 있지만 실제 비대칭 형상, 주변 Pattern과 경계에서는 위치가 달라질 수 있습니다.

**실무자 답변**  
대칭 Kernel과 고립 Step Edge의 이론적 중심은 유지되지만 PSF, 비대칭 밝기, 인접 Edge, ROI Border, Nonlinear Median/Bilateral과 Threshold 방식이 Bias를 만든다. Golden Gauge로 Filter별 Bias를 계측한다.

**면접용 30초 답변**  
“가능합니다. 이상적 대칭 Step Edge에서는 중심이 유지될 수 있지만 실제 Image는 비대칭 Blur, 주변 Edge와 ROI Border가 있어 Filter가 Gradient Peak나 Threshold 위치를 이동시킬 수 있습니다. 따라서 Filter 전후 Bias와 반복성을 측정합니다.”

---

## 11. 실습 문제

### 실습 1: Filter 비교

동일 Image에 None/Mean/Gaussian/Median/Bilateral을 적용하고 다음을 비교한다.

- Background 표준편차
- Edge Gradient Peak
- Edge Spread Width
- 최소 Defect Contrast
- 처리 시간

### 실습 2: Kernel Sweep

Gaussian Kernel 1/3/5/7과 sigma를 바꾸며 Scratch/Particle 검출률과 Noise Edge 수를 기록한다. “가장 매끄러운 Image”가 아니라 검사 결과가 가장 안정적인 Parameter를 선택한다.

### 실습 3: Edge Profile 측정

Back Light 부품 Image에서 여러 Scan Line을 평균해 1D Profile을 만들고 Left/Right Gradient Peak로 Width를 측정한다. Scan Line 수에 따른 Noise와 Edge Bias를 비교한다.

### 실습 4: Canny Parameter Map

Low/High Threshold 조합을 Sweep하고 다음을 표로 저장한다.

- Edge Pixel Count
- Connected Component 수
- Target Edge 연결률
- False Edge 수
- 처리 시간

### Phase 7-2 미니 프로젝트: Edge Measurement Workbench

```text
Image + Align된 ROI
        ↓
Filter 선택/Parameter Sweep
        ↓
Gx/Gy/Magnitude/Canny 시각화
        ↓
1D Profile + Edge Polarity/Peak
        ↓
Sub-pixel Left/Right Position
        ↓
Calibration Width
        ↓
Bias / Repeatability Report
```

**필수 기능**

- Raw/Filtered/Gradient/Binary Edge 저장
- Filter와 Edge Recipe Version
- Search Direction, Polarity, Expected Range
- Pixel/실제 단위 측정값 동시 저장
- Filter별 처리 시간과 측정 Bias 비교
- Constant/Impulse/Step Edge Unit Test

---

## 12. Chapter 핵심 요약

- 🔴 Filter는 Noise와 함께 Detail도 바꾸므로 목적과 Feature 크기로 선택한다.
- 🔴 Mean/Gaussian은 평균 기반, Median은 Outlier 기반 비선형 Filter다.
- 🔴 Bilateral은 큰 Edge를 보존하지만 느리고 약한 결함을 지울 수 있다.
- 🔴 Gradient의 Gx/Gy는 변화 방향과 Polarity를 제공한다.
- 🔴 Sobel 결과는 Signed/Float Depth로 유지한다.
- 🔴 Canny는 얇은 Binary Edge 후보를 만들지만 Measurement 자체는 아니다.
- 🔴 Edge 측정에는 방향, Polarity, 위치 범위와 Calibration이 필요하다.
- 🟠 Sub-pixel은 위치 추정 반복성을 개선하지만 Optical Detail을 새로 만들지 않는다.
- 🟠 ROI Border와 Filter가 Edge Bias를 만들 수 있다.
- 🟠 Parameter는 검출률, Bias, 반복성, 처리 시간으로 검증한다.

---

## 10일차 권장 학습 순서

- [ ] 45분: Mean/Gaussian/Median/Bilateral 비교
- [ ] 45분: Gradient, Gx/Gy, Magnitude/Direction 계산
- [ ] 40분: Sobel/Canny Pipeline 정리
- [ ] 50분: Edge Detection과 Measurement 차이
- [ ] 60~90분: C++ Filter/Edge Pipeline 구현
- [ ] 60분: Filter·Canny Parameter Sweep
- [ ] 30분: 면접 Q1~Q6 30초 답변 연습

## 학습 완료 체크

- [ ] Noise와 Feature 크기로 Filter 후보를 선택한다.
- [ ] Mean/Gaussian/Median/Bilateral의 Trade-off를 설명한다.
- [ ] Sobel Gx/Gy와 Edge 방향/Polarity를 설명한다.
- [ ] Canny의 Double Threshold/Hysteresis를 설명한다.
- [ ] Edge Pair로 실제 Width를 계산한다.
- [ ] Filter가 Measurement Bias를 만들 수 있음을 검증한다.
- [ ] Edge Measurement Workbench를 설계하거나 구현했다.

## 다음 학습 예고

다음 영상처리 Chapter에서는 Erosion, Dilation, Opening, Closing과 Connected Component/Blob을 연결해 Binary Object의 Area, Bounding Box, Centroid, Circularity를 측정한다.
