# 11일차. 영상처리 기초 3: Morphology · Connected Component · Blob

> Phase 7-3 · 예상 학습 시간: 10~14시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Binary Foreground와 Structuring Element(Kernel)
- 🔴 Erosion, Dilation, Opening, Closing
- 🔴 Morphology가 형상과 측정값에 주는 영향
- 🔴 4/8 Connectivity와 Connected Component Labeling
- 🔴 Blob의 Area, Bounding Box, Centroid, Width/Height
- 🔴 Perimeter, Circularity, Aspect Ratio
- 🔴 Pixel 면적을 실제 단위로 변환하는 방법
- 🟠 Border Blob, Hole, 붙은 Blob과 분리 문제
- 🟠 Blob 조건을 이용한 Presence/Particle/결함 검사

### 실무 목표

Threshold 결과에 Morphology를 무조건 적용하지 않고 제거할 Noise와 보존할 최소 Defect 크기를 기준으로 Kernel을 선택한다. Connected Component/Blob 특징을 측정해 후보를 Filtering하고, Morphology 전후 측정 Bias와 Calibration 단위를 검증한다.

---

## 2. 선수 지식

- [[09-image-processing-01-threshold|9일차]]의 Binary, Polarity, ROI
- [[10-image-processing-02-filter-edge|10일차]]의 Kernel과 Border
- Pixel 좌표, `μm/pixel`, 면적 단위

이 Chapter에서는 `255=검사할 Foreground`, `0=Background`로 통일한다. Polarity가 반대면 먼저 Binary를 반전한다.

---

## 3. 핵심 개념

### 3.1 Structuring Element

Morphology는 Kernel 안에서 Foreground의 형태를 비교·변형한다.

```text
Rect 3×3       Cross 3×3       Ellipse 3×3
1 1 1          0 1 0           0 1 0
1 1 1          1 1 1           1 1 1
1 1 1          0 1 0           0 1 0
```

Kernel의 크기와 모양이 처리할 방향과 최소 형상을 결정한다. `5 μm/pixel`에서 3×3 Kernel의 폭은 약 15 μm이며, 한 번의 Erosion은 평평한 경계를 각 방향 약 1 Pixel(5 μm) 후퇴시킨다.

### 3.2 Erosion(침식)

Kernel이 Foreground 내부에 완전히 들어갈 때만 중심을 Foreground로 유지한다.

효과:

- 밝은 Foreground 축소
- 작은 밝은 Noise 제거
- 가는 연결부 끊기
- Hole 확대

위험:

- 작은 실제 Defect 소실
- Width/Area 감소
- 얇은 Line 단절

### 3.3 Dilation(팽창)

Kernel 안에 Foreground가 하나라도 있으면 중심을 Foreground로 만든다.

효과:

- Foreground 확대
- 작은 Hole/Gap 축소
- 가까운 Blob 연결
- 끊긴 Line 보완

위험:

- 서로 다른 결함이 하나로 합쳐짐
- Width/Area 증가
- Background Noise 확대

### 3.4 Opening

```text
Opening = Erosion → Dilation
```

큰 형상의 전체 크기를 대략 복원하면서 Kernel보다 작은 밝은 Foreground를 제거한다.

적용:

- Binary의 작은 밝은 Noise
- 큰 제품 외곽 주변의 작은 돌기 제거

위험:

- 작은 Particle/Scratch 자체가 검사 대상이면 함께 제거
- Corner가 둥글어지고 가는 구조가 끊길 수 있음

### 3.5 Closing

```text
Closing = Dilation → Erosion
```

작은 검은 Hole과 Gap을 메우고 가까운 Foreground를 연결한다.

적용:

- Threshold로 끊긴 문자/외곽 연결
- Blob 내부 작은 Hole 채우기

위험:

- 서로 다른 Particle이 합쳐짐
- 실제 Crack/Gap을 제거

### 3.6 Morphology 비교

| 연산 | Foreground 효과 | 대표 사용 | 측정 위험 |
|---|---|---|---|
| Erosion | 축소 | 작은 밝은 Noise/접촉 분리 | Area·Width 감소 |
| Dilation | 확대 | Gap 연결/Hole 축소 | Area·Width 증가 |
| Opening | 작은 밝은 형상 제거 | Speckle 제거 | 작은 Defect 소실 |
| Closing | 작은 어두운 Gap 제거 | 끊긴 Object 연결 | 결함/Blob 병합 |

Morphology 결과를 최종 치수 측정에 사용해야 한다면 Golden Gauge로 Bias를 계측한다. 가능하면 Morphology는 후보 검출에 사용하고 정밀 Edge/치수는 Gray 원본에서 다시 측정한다.

### 3.7 Connectivity

```text
1 0
0 1
```

- 4-connectivity: 상하좌우만 연결. 위 두 Pixel은 별개.
- 8-connectivity: 대각선 포함. 위 두 Pixel은 하나.

대각선 접촉을 같은 Object로 볼지 검사 의미에 따라 정한다. OpenCV Connected Components에서는 Connectivity를 명시한다.

### 3.8 Connected Component Labeling

Binary Foreground를 연결된 그룹으로 분리해 각 그룹에 Label을 붙인다.

```text
0 0 1 1 0 2
0 0 1 1 0 2
3 0 0 0 0 0
```

각 Label에서 Area, Bounding Box, Centroid를 얻는다. Background는 보통 Label 0이다.

### 3.9 Blob 특징

- Area: Foreground Pixel 수
- Bounding Box: Blob을 포함하는 최소 축 정렬 사각형
- Centroid: Pixel/면적 중심
- Width/Height: Bounding Box 크기
- Perimeter: Contour 길이
- Aspect Ratio: Width/Height
- Circularity: `4π×Area/Perimeter²`
- Border Touch: ROI/Image 경계 접촉 여부

Circularity는 이상적인 원에서 1에 가깝고 길거나 불규칙하면 작아진다. 작은 Blob은 Pixel Quantization 때문에 값이 불안정하다.

### 3.10 Blob과 실제 검사 연결

| 검사 | 주요 Blob 특징 | 추가 조건 |
|---|---|---|
| Presence | Count, Area, Position | 예상 ROI |
| Particle | Area, Peak Gray, Circularity | Dark Field CNR |
| Missing | Expected Blob 부재 | Align/ROI 정상 여부 |
| Stain | Area, Mean Difference, Elongation | Background 보정 |
| Burr | Border 위치, Area, 방향 | 외곽 기준 |
| Hole | 내부 Background Component | Contour Hierarchy |
| Scratch | 길이, Aspect, Orientation | Line/Gradient와 결합 |

### 3.11 Pixel 면적을 실제 단위로 변환

X/Y Scale이 각각 `s_x`, `s_y` μm/pixel이면:

```text
Area(μm²) = Pixel Area × s_x × s_y
```

단일 `μm/pixel`을 제곱하는 방식은 X/Y Scale이 같고 Perspective/Distortion이 작은 경우의 근사다. 정밀 면적은 Calibration Transform의 위치별 Jacobian 또는 보정 Image를 사용한다.

### 3.12 Border Blob

ROI 경계에 닿은 Blob은 실제 전체 크기를 알 수 없다.

- 검사 대상이 ROI 밖으로 잘림
- Threshold가 ROI 경계를 Object Edge로 만듦
- Align 오차로 Object가 이동

Area/Width 판정 전에 Border Touch를 별도 상태로 처리하거나 Margin ROI에서 검출한다.

### 3.13 붙은 Blob과 떨어진 Blob

Touching Blob 분리 방법:

- Erosion/Opening
- Distance Transform + Watershed
- Concavity/Contour 분석
- Gray Image의 Local Peak

끊긴 Blob 연결 방법:

- Dilation/Closing
- 방향성 Kernel
- Line/Contour Model

Morphology만으로 물리적으로 다른 Object를 정확히 복원한다고 가정하지 않는다.

---

## 4. 그림으로 이해하기

```text
Original       Erosion        Dilation
  ███            █            █████
  ███          (shrink)        █████
  ███                           █████

Opening: small white dot removed
Closing: small black hole filled
```

```text
Binary → Morphology → Labeling → Feature Filter → Measurement
           │              │             │
       shape changes   components    area/position/circularity
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Particle 검사

Threshold 후 작은 Component를 찾는다. Median/Opening이 실제 최소 Particle까지 제거하지 않는지 확인하고 Area뿐 아니라 Gray Contrast와 위치를 함께 판정한다.

### Presence 검사

Expected ROI 안에 지정 Area/Position의 Blob이 정확히 하나 있는지 확인한다. Count가 0이면 Missing, 여러 개면 파손/Noise 가능성을 구분한다.

### 외곽 Burr 검사

정상 외곽 Mask와 현재 Binary의 차이를 구해 바깥쪽 Blob Area/길이를 측정한다. ROI Border Blob과 정상 위치 오차가 Burr로 판정되지 않도록 Align이 선행되어야 한다.

### 문자/Pattern 연결

끊긴 Stroke를 방향성 Closing으로 연결할 수 있다. Kernel 방향과 길이가 다른 문자를 합치지 않는지 OCR/Matching 결과로 검증한다.

---

## 6. 숫자로 이해하기

### 예제 1: 5×5 정사각형과 3×3 Kernel

무한 Background 안의 5×5 Foreground 정사각형에 Rect 3×3을 한 번 적용하면 이상적으로:

```text
Original Area = 5×5 = 25 pixel²
Erosion Area  = 3×3 = 9 pixel²
Dilation Area = 7×7 = 49 pixel²
```

### 예제 2: 실제 면적 변환

```text
Blob Area = 800 pixel²
s_x = s_y = 5 μm/pixel

Area = 800×5×5 = 20,000 μm²
     = 0.020 mm²
```

`1 mm²=1,000,000 μm²`를 사용했다.

### 예제 3: Circularity

Area 314 pixel², Perimeter 62.8 pixel인 Blob:

```text
Circularity = 4π×314 / 62.8² ≈ 1.000
```

동일 Area에서 Perimeter가 100이면 약 0.395로 불규칙하거나 긴 형상일 가능성이 높다.

### 예제 4: 회전각 Noise와 Centroid

Blob Pixel 좌표 `(10,10),(11,10),(10,11),(11,11)`의 Centroid:

```text
x_c=(10+11+10+11)/4=10.5
y_c=(10+10+11+11)/4=10.5
```

Centroid가 소수라고 해서 실제 광학 정밀도가 자동으로 Sub-pixel 수준이 되는 것은 아니다.

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>

#include <cmath>
#include <stdexcept>
#include <vector>

enum class MorphOperation { None, Erode, Dilate, Open, Close };
enum class KernelShape { Rect, Cross, Ellipse };

struct MorphRecipe final {
    MorphOperation operation{MorphOperation::None};
    KernelShape shape{KernelShape::Ellipse};
    int kernelSize{3};
    int iterations{1};
};

struct BlobFeature final {
    int label{};
    int areaPixels{};
    cv::Rect boundingBox;
    cv::Point2d centroid;
    double perimeterPixels{};
    double circularity{};
    double aspectRatio{};
    bool touchesBorder{};
};

[[nodiscard]] int ToOpenCvShape(const KernelShape shape)
{
    switch (shape) {
    case KernelShape::Rect: return cv::MORPH_RECT;
    case KernelShape::Cross: return cv::MORPH_CROSS;
    case KernelShape::Ellipse: return cv::MORPH_ELLIPSE;
    }
    throw std::invalid_argument{"Unknown kernel shape"};
}

[[nodiscard]] cv::Mat ApplyMorphology(
    const cv::Mat& binary, const MorphRecipe& recipe)
{
    if (binary.empty() || binary.type() != CV_8UC1) {
        throw std::invalid_argument{"CV_8UC1 binary image is required"};
    }
    if (recipe.kernelSize <= 0 || recipe.kernelSize % 2 == 0 ||
        recipe.iterations <= 0) {
        throw std::invalid_argument{"Kernel must be positive/odd; iterations positive"};
    }
    if (recipe.operation == MorphOperation::None) {
        return binary.clone();
    }

    const cv::Mat kernel = cv::getStructuringElement(
        ToOpenCvShape(recipe.shape),
        cv::Size{recipe.kernelSize, recipe.kernelSize});
    cv::Mat output;

    switch (recipe.operation) {
    case MorphOperation::None: output = binary.clone(); break;
    case MorphOperation::Erode:
        cv::erode(binary, output, kernel, cv::Point{-1,-1}, recipe.iterations);
        break;
    case MorphOperation::Dilate:
        cv::dilate(binary, output, kernel, cv::Point{-1,-1}, recipe.iterations);
        break;
    case MorphOperation::Open:
        cv::morphologyEx(binary, output, cv::MORPH_OPEN, kernel,
                         cv::Point{-1,-1}, recipe.iterations);
        break;
    case MorphOperation::Close:
        cv::morphologyEx(binary, output, cv::MORPH_CLOSE, kernel,
                         cv::Point{-1,-1}, recipe.iterations);
        break;
    }
    return output;
}

[[nodiscard]] std::vector<BlobFeature> AnalyzeBlobs(
    const cv::Mat& binary, const int connectivity = 8)
{
    if (binary.empty() || binary.type() != CV_8UC1) {
        throw std::invalid_argument{"CV_8UC1 binary image is required"};
    }
    if (connectivity != 4 && connectivity != 8) {
        throw std::invalid_argument{"Connectivity must be 4 or 8"};
    }

    cv::Mat labels, stats, centroids;
    const int count = cv::connectedComponentsWithStats(
        binary, labels, stats, centroids, connectivity, CV_32S);
    std::vector<BlobFeature> features;
    constexpr double pi = 3.14159265358979323846;

    for (int label = 1; label < count; ++label) {
        const cv::Rect box{
            stats.at<int>(label, cv::CC_STAT_LEFT),
            stats.at<int>(label, cv::CC_STAT_TOP),
            stats.at<int>(label, cv::CC_STAT_WIDTH),
            stats.at<int>(label, cv::CC_STAT_HEIGHT)};
        const int area = stats.at<int>(label, cv::CC_STAT_AREA);

        cv::Mat componentMask;
        cv::compare(labels, label, componentMask, cv::CMP_EQ);
        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(componentMask, contours, cv::RETR_EXTERNAL,
                         cv::CHAIN_APPROX_NONE);
        double perimeter = 0.0;
        for (const auto& contour : contours) {
            perimeter += cv::arcLength(contour, true);
        }
        const double circularity = perimeter > 0.0
            ? 4.0*pi*static_cast<double>(area)/(perimeter*perimeter)
            : 0.0;
        const bool border = box.x == 0 || box.y == 0 ||
            box.x + box.width == binary.cols ||
            box.y + box.height == binary.rows;

        features.push_back({
            label, area, box,
            {centroids.at<double>(label,0), centroids.at<double>(label,1)},
            perimeter, circularity,
            static_cast<double>(box.width)/static_cast<double>(box.height),
            border});
    }
    return features;
}
```

### Unit Test

```cpp
#include <cassert>

void TestSingleRectangleBlob()
{
    cv::Mat image = cv::Mat::zeros(30, 30, CV_8UC1);
    image(cv::Rect{5, 7, 10, 8}).setTo(255);
    const auto blobs = AnalyzeBlobs(image);
    assert(blobs.size() == 1);
    assert(blobs[0].areaPixels == 80);
    assert(blobs[0].boundingBox == cv::Rect(5, 7, 10, 8));
    assert(!blobs[0].touchesBorder);
}

void TestOpeningRemovesOnePixelNoise()
{
    cv::Mat image = cv::Mat::zeros(30, 30, CV_8UC1);
    image(cv::Rect{10,10,7,7}).setTo(255);
    image.at<unsigned char>(2,2)=255;
    const cv::Mat opened = ApplyMorphology(
        image, {MorphOperation::Open, KernelShape::Rect, 3, 1});
    assert(opened.at<unsigned char>(2,2) == 0);
    assert(cv::countNonZero(opened) == 49);
}
```

### 코드에서 봐야 할 점

1. Binary Polarity와 Type을 호출 전에 고정한다.
2. Morphology와 Blob Analysis를 별도 단계로 둔다.
3. Label 0 Background를 제외한다.
4. `connectedComponentsWithStats`의 Pixel Area/Centroid와 Contour Perimeter를 결합한다.
5. Border Touch를 Result에 명시한다.
6. Circularity는 작은 Blob과 Pixel Contour에서 1을 넘거나 흔들릴 수 있으므로 경험적 범위를 검증한다.

---

## 8. 실무에서 발생하는 문제

1. **Opening이 최소 Particle을 제거**: Kernel을 물리 단위로 환산하고 Filter 전후 검출률 비교.
2. **Closing이 인접 Defect를 병합**: Blob 간 최소 Gap과 Kernel 크기 검증.
3. **ROI Border Blob의 Area 과소 측정**: Margin ROI와 Border 상태 사용.
4. **4/8 Connectivity 변경으로 Count 변화**: Recipe에 Connectivity 저장.
5. **Threshold 변화가 Blob Area 변화로 확대**: Gray 분포와 Threshold Margin Monitoring.
6. **Circularity로 작은 Particle 오판**: 최소 Area 이상에서만 Shape 조건 적용.
7. **Morphology 결과로 정밀 치수 측정**: Gray 원본 Edge에서 재측정.

---

## 9. 흔한 오해

1. **“Opening은 Noise만 제거한다.”** 실제 작은 Defect도 제거한다.
2. **“Closing은 끊긴 Object를 원래대로 복원한다.”** 다른 Object까지 합칠 수 있다.
3. **“Centroid는 Object의 설계 중심이다.”** Binary 밝기/형상 중심일 뿐이다.
4. **“Circularity 1이면 반드시 원이다.”** Pixel화와 작은 Blob에서 불안정하다.
5. **“Blob Area×Scale²이면 항상 실제 면적이다.”** X/Y Scale과 왜곡을 고려해야 한다.
6. **“Component Count가 맞으면 검사도 정상이다.”** 위치·크기·형상·Gray Contrast가 필요하다.
7. **“Morphology 반복 횟수를 늘리면 더 깨끗하다.”** 형상 Bias도 누적된다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. Erosion과 Dilation의 차이는?

**초보자 답변**: Erosion은 흰 Foreground를 줄이고 Dilation은 늘린다.  
**실무자 답변**: Structuring Element 포함 관계로 Binary 형상을 변형하며 Area/Width Bias와 연결·분리를 만든다.  
**30초 답변**: “255를 Foreground로 정의하면 Erosion은 경계를 안쪽으로, Dilation은 바깥쪽으로 이동시킵니다. Noise 제거·Gap 연결에 쓰지만 측정값이 바뀌므로 Kernel을 최소 Defect와 μm/pixel 기준으로 정합니다.”

### Q2. Opening과 Closing은 언제 사용하는가?

**초보자 답변**: Opening은 작은 흰 Noise를 제거하고 Closing은 작은 검은 Hole/Gap을 메운다.  
**실무자 답변**: Opening=Erode→Dilate, Closing=Dilate→Erode이며 Kernel보다 작은 구조를 선택적으로 제거한다.  
**30초 답변**: “Opening은 작은 Foreground, Closing은 작은 Background Gap 제거에 사용합니다. 실제 Particle/Crack도 지울 수 있어 원본과 결과의 검출률·형상 Bias를 비교합니다.”

### Q3. 4-connectivity와 8-connectivity의 차이는?

**초보자 답변**: 4는 상하좌우, 8은 대각선까지 연결한다.  
**실무자 답변**: 대각선 접촉 Component의 Label/Count가 달라지므로 물리적 Object 정의에 맞춰 Recipe로 고정한다.  
**30초 답변**: “대각선 접촉을 같은 Blob으로 볼지 결정하는 차이입니다. Connectivity 변경은 Count와 Area Grouping을 바꾸므로 검사 의미와 Sample로 선택합니다.”

### Q4. Blob에서 어떤 특징을 측정하는가?

**초보자 답변**: 면적, 위치 중심, 사각형 크기와 모양을 측정한다.  
**실무자 답변**: Area/Bounding Box/Centroid/Perimeter/Circularity/Aspect/Border와 원본 Gray 통계를 결합한다.  
**30초 답변**: “Blob 후보마다 Area, 위치, 폭·높이, Perimeter와 Circularity를 구하고 Expected ROI와 Spec으로 Filtering합니다. Border Blob과 작은 Blob의 Shape 불안정성을 별도 처리합니다.”

### Q5. Morphology 후 치수 측정 시 문제는?

**초보자 답변**: 형상이 줄거나 늘어 실제 크기와 달라질 수 있다.  
**실무자 답변**: Kernel/iteration에 따른 systematic bias가 생기며 비대칭/인접 형상에서는 위치도 변한다.  
**30초 답변**: “Morphology는 검출 후보 정리에 사용하고 정밀 치수는 원본 Gray Edge에서 다시 측정하는 편이 안전합니다. 사용해야 한다면 Gauge로 Bias와 반복성을 보정·검증합니다.”

### Q6. Pixel Area를 실제 면적으로 어떻게 바꾸는가?

**초보자 답변**: Pixel 수에 X와 Y 방향 실제 Pixel 크기를 곱한다.  
**실무자 답변**: `A=A_px×s_x×s_y`이며 Perspective/Distortion이 크면 위치별 Jacobian 또는 Rectification이 필요하다.  
**30초 답변**: “단순 Scale이 유효하면 Pixel Area에 X/Y μm-per-pixel을 곱합니다. 정밀 면적은 왜곡 보정과 위치별 Calibration을 적용하고 Target 면적으로 검증합니다.”

---

## 11. 실습 문제

1. 1~9 Pixel Particle Image에서 Rect/Ellipse 3/5 Kernel Opening 전후 생존율을 표로 만든다.
2. 4/8 Connectivity에 따라 Component Count가 달라지는 Test Image를 설계한다.
3. Blob Area 1200 pixel², X=4.8 μm/pixel, Y=5.1 μm/pixel의 실제 면적을 계산한다.
4. 정상/Particle/Scratch Blob의 Area, Circularity, Aspect 분포로 Rule을 설계한다.

### Phase 7-3 미니 프로젝트: Blob Inspection Workbench

```text
Gray ROI → Threshold → Morphology Sweep → Components
→ Area/Position/Shape/Border Filter → Overlay/CSV → OK/NG
```

원본·Binary·Morphology Image, Recipe, Component 전체 목록과 탈락 이유를 저장한다.

---

## 12. Chapter 핵심 요약

- 🔴 Morphology는 Binary 형상을 바꾸므로 검출과 측정 Bias를 함께 만든다.
- 🔴 Opening은 작은 Foreground, Closing은 작은 Background Gap을 제거한다.
- 🔴 Kernel을 Pixel이 아니라 최소 Feature의 실제 크기와 연결한다.
- 🔴 Connectivity는 Component Count와 의미를 바꾼다.
- 🔴 Blob은 Area뿐 아니라 위치·형상·Border·Gray 특징으로 판정한다.
- 🔴 정밀 치수는 가능하면 Morphology 전 Gray Image에서 재측정한다.
- 🟠 Pixel 면적 변환에는 X/Y Scale과 Distortion이 필요하다.
- 🟠 모든 후보와 탈락 이유를 Result/Review에 남긴다.

## 11일차 학습 완료 체크

- [ ] Erosion/Dilation/Opening/Closing을 Foreground 기준으로 설명한다.
- [ ] Kernel 크기를 μm로 환산한다.
- [ ] 4/8 Connectivity를 선택한다.
- [ ] Blob Area/Box/Centroid/Circularity를 계산한다.
- [ ] Border Blob과 Morphology Bias를 처리한다.
- [ ] Blob Workbench를 설계하거나 구현했다.

## 다음 학습 예고

12일차에는 Static/Dynamic ROI, Align X/Y/Theta를 적용한 ROI 이동·회전과 좌표 Transform을 학습한다.
