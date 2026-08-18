# Chapter 2. Image와 Pixel 기본

> Phase 1 · 2일차 · 예상 학습 시간: 8~10시간 · 난이도: 입문 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Image, Pixel, Width/Height, Pixel Coordinate
- 🔴 Gray Scale, RGB, Channel
- 🔴 Bit Depth와 8/10/12/16-bit Image
- 🔴 Gray Level과 Dynamic Range
- 🔴 Camera Resolution, Image Resolution, Pixel Size, Spatial Resolution, Optical Resolution의 차이
- 🟠 Histogram, Saturation, Quantization
- 🟠 OpenCV `cv::Mat`의 크기, 채널, Depth, Step

### 실무 목표

이미지의 `2048×2048`, `8-bit`, `3.45 μm pixel`이 각각 무엇을 뜻하는지 구분한다. Camera SDK가 전달한 Image의 Width, Height, Channel, Depth, Row Stride를 검증하고, 실제 길이 또는 검출 가능성을 Pixel 개수만 보고 단정하지 않는다.

---

## 2. 선수 지식

- `1 byte = 8 bit`
- `2^8 = 256`, `2^10 = 1024`, `2^12 = 4096`, `2^16 = 65536`
- `1 mm = 1,000 μm`
- 2차원 배열의 행(Row)과 열(Column)
- Chapter 1의 `Camera → Acquisition → Image → Inspection` 흐름

```text
빛 → Sensor의 각 Pixel → 전기 신호 → A/D 변환 → 숫자 배열(Image)
```

빛은 연속적이지만 디지털 Image는 공간과 밝기를 이산적인 값으로 표현한다. 공간을 나누는 단위가 Pixel이고, 밝기를 나누는 단계 수를 결정하는 것이 Bit Depth다.

---

## 3. 핵심 개념

### 3.1 Image와 Pixel

**Image(영상)**는 Pixel이 Width×Height 형태로 배열된 데이터다. **Pixel(Picture Element)**은 디지털 Image의 한 위치에 저장된 샘플이다.

```text
Image 4×3

       x=0   x=1   x=2   x=3
y=0   [ 12] [ 15] [ 18] [ 20]
y=1   [ 11] [120] [125] [ 19]
y=2   [ 10] [118] [122] [ 18]
```

`image.at<std::uint8_t>(y, x)`처럼 메모리 접근은 보통 `(row, column) = (y, x)` 순서다. 반면 `cv::Point(x, y)`와 `cv::Rect(x, y, width, height)`는 `(x, y)` 순서다.

> [!WARNING]
> OpenCV에서 `(row, col)`과 `(x, y)`를 섞으면 사각형 Image에서는 오류가 바로 드러나지만 정사각형 Image에서는 우연히 정상처럼 보여 더 위험하다.

### 3.2 Gray Scale과 Gray Level

**Gray Scale Image(그레이스케일 영상)**는 각 Pixel에 밝기 값 하나를 저장한다. 8-bit라면 보통 `0=검정`, `255=흰색`이며 그 사이 값은 회색이다.

- Gray Level: 한 Pixel의 수치
- Brightness: 사람이 느끼거나 영상에서 관찰되는 밝기
- Intensity: 문맥에 따라 Pixel 값 또는 빛의 세기를 뜻함

Pixel 값은 물체의 고유 속성만이 아니다. 조명 세기와 각도, 표면 반사, Lens, Exposure, Gain, Sensor Response의 결과다. 따라서 같은 물체도 촬영 조건이 바뀌면 Gray Level이 바뀐다.

### 3.3 RGB와 Channel

RGB Image는 일반적으로 Pixel마다 Red, Green, Blue 세 값을 저장한다. OpenCV의 기본 Color 순서는 대부분 **BGR**이다.

```text
한 Pixel: B=20, G=80, R=200
OpenCV Vec3b 접근: pixel[0]=B, pixel[1]=G, pixel[2]=R
```

산업 검사에서는 Color가 판별 특징이면 RGB/Color Camera를 사용한다. 형상, Edge, 치수, 표면 Contrast가 핵심이라면 Mono Camera가 해상도·감도·처리량 측면에서 유리할 수 있다. 무조건 Gray 변환하기 전에 검사 특징이 색에 있는지 판단한다.

### 3.4 Bit Depth

Bit Depth는 한 Pixel 또는 한 Channel이 표현할 수 있는 디지털 단계 수다.

| Bit Depth | 가능한 코드 범위 | 단계 수 | 일반적 저장 |
|---:|---:|---:|---|
| 8-bit | 0~255 | 256 | `CV_8U`, 1 byte |
| 10-bit | 0~1023 | 1,024 | 보통 16-bit Container 또는 Packed Format |
| 12-bit | 0~4095 | 4,096 | 보통 16-bit Container 또는 Packed Format |
| 16-bit | 0~65535 | 65,536 | `CV_16U`, 2 byte |

10/12-bit Camera Image가 항상 Pixel당 정확히 10/12 bit로 메모리에 놓이는 것은 아니다.

- **Unpacked**: 16-bit Container에 저장. 접근은 쉽지만 여유 bit가 존재한다.
- **Packed**: 여러 Pixel을 bit 단위로 압축. 대역폭은 절약하지만 해제 과정이 필요하다.
- **정렬 방식**: 유효 bit가 상위(MSB) 또는 하위(LSB)에 정렬될 수 있다.

Camera SDK의 Pixel Format, 유효 Bit 수, 정렬 방식을 확인하지 않고 `uint16_t` 최댓값을 65535로 가정하면 Histogram과 Threshold가 틀어진다.

### 3.5 Dynamic Range와 Bit Depth의 차이

- **Bit Depth**: 디지털 코드가 몇 단계인가?
- **Dynamic Range**: 구분 가능한 가장 큰 신호와 가장 작은 신호의 비율은 얼마인가?

12-bit가 4096단계를 제공해도 Sensor Noise가 크면 모든 하위 단계를 유효하게 구분하지 못한다. 반대로 Dynamic Range가 넓어도 Display나 저장 과정에서 8-bit로 잘못 축소하면 정보가 손실될 수 있다.

```text
Bit Depth: 값을 담는 눈금의 개수
Dynamic Range: 실제로 의미 있게 측정 가능한 어두움~밝음의 범위
```

### 3.6 Saturation과 Quantization

- **Saturation(포화)**: 신호가 표현 가능한 최댓값을 넘어 모두 같은 최대 코드로 잘린 상태
- **Underexposure(노출 부족)**: 신호가 Noise Floor 근처에 몰려 특징 대비가 부족한 상태
- **Quantization(양자화)**: 연속 신호를 제한된 코드 단계로 반올림하는 과정

포화된 영역은 물체가 더 밝아도 값이 증가하지 않으므로 내부 차이를 복구할 수 없다. 단순히 Contrast를 후처리로 키워도 잃어버린 정보는 돌아오지 않는다.

### 3.7 Resolution 용어 비교

| 용어 | 정확한 의미 | 대표 단위/표현 | 무엇이 결정하는가? | 흔한 오해 |
|---|---|---|---|---|
| Camera Resolution | Camera Sensor의 유효 Pixel 개수 | 2048×2048, 5 MP | Sensor 설계 및 출력 Mode | 실제 1 pixel의 μm 크기라고 오해 |
| Image Resolution | 저장·전송된 Image의 Pixel 배열 크기 | Width×Height | Camera Mode, ROI/Binning/Resizing | 원본 Sensor 크기와 항상 같다고 오해 |
| Pixel Size | Sensor에서 한 Physical Pixel의 Pitch | 3.45 μm/pixel | Sensor 설계 | 물체 3.45 μm가 항상 1 pixel이라고 오해 |
| Spatial Resolution | Object Space에서 Image 1 pixel이 담당하는 길이 또는 구분 가능한 공간 간격 | μm/pixel, lp/mm | FOV/Pixel Count, Magnification 및 광학계 | Pixel Size와 같은 값이라고 오해 |
| Optical Resolution | Lens/광학계가 실제로 분리해 전달할 수 있는 세부 정도 | μm, lp/mm, MTF | Lens, NA, 파장, Focus, 수차 | Sensor Pixel 수가 높으면 자동 향상된다고 오해 |

#### 꼭 구분할 문장

```text
Camera Resolution = 센서가 몇 개의 Pixel로 구성되었는가?
Image Resolution  = 지금 처리하는 Image 배열이 몇 Pixel인가?
Pixel Size        = 센서의 한 Pixel Pitch가 몇 μm인가?
Spatial Resolution= 물체 공간에서 한 Pixel 또는 구분 간격이 얼마인가?
Optical Resolution= 광학계가 세부 정보를 얼마나 선명하게 전달하는가?
```

### 3.8 Image Size의 두 의미

`Image Size`라는 말은 모호하므로 구분해서 말한다.

- Pixel Dimension: `2048×2048 pixel`
- Memory Size: `약 4 MiB`
- 화면 표시 크기: UI의 `800×800 logical pixel`
- 실제 FOV: 물체 공간의 `10×10 mm`

회의에서는 “Image Size가 크다” 대신 어떤 의미인지 단위와 함께 말한다.

### 3.9 Camera ROI, Binning, Resizing

- **Camera ROI**: Sensor 일부만 읽어 출력 Width/Height와 대역폭을 줄임
- **Binning**: 인접 Sensor Pixel의 신호를 결합. 출력 Pixel 수와 Sampling이 변함
- **Software Crop**: 이미 받은 Image의 일부만 참조/복사. Acquisition 대역폭은 그대로
- **Resize**: 보간으로 Image Pixel 배열을 변경. 새로운 실제 세부 정보가 생기지 않음

---

## 4. 그림으로 이해하기

```text
Real Object
   │ reflected light
   ▼
Lens: optical detail and blur
   │
   ▼
Sensor Grid: physical Pixel Size, e.g. 3.45 μm
   │ spatial sampling
   ▼
A/D Converter: 8/10/12/16-bit code
   │
   ▼
Image Buffer: Width × Height × Channel × Container Bytes
   │
   ├─ Preprocessing
   ├─ Alignment
   └─ Inspection
```

```text
공간을 나눔                          밝기를 나눔

FOV ──► Pixel Grid                  Analog Signal ──► Digital Code
10 mm / 2000 pixel                  0~100% ──► 0~4095 (12-bit)
= 5 μm/pixel
```

공간 Sampling과 밝기 Quantization은 서로 다른 축이다. Pixel 수를 늘린다고 Bit Depth가 늘지 않고, Bit Depth를 늘린다고 작은 Defect가 더 많은 Pixel로 표현되지 않는다.

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Threshold 검사

8-bit Image에서 Threshold 128을 사용하던 코드를 12-bit 원본에 그대로 적용하면 거의 모든 Pixel이 흰색이 될 수 있다. 입력 Bit Depth와 유효 범위를 기준으로 Parameter 의미를 정해야 한다.

### Review 표시

12/16-bit Image를 화면에 바로 표시하면 매우 어둡게 보일 수 있다. Display용 8-bit 변환과 검사 원본을 분리한다. Review를 보기 좋게 만든 변환 Image로 검사를 다시 수행하면 결과가 달라질 수 있다.

### Camera 교체

같은 2048×2048 Camera라도 Pixel Size가 다르면 Sensor Size가 다르고, 동일 Lens에서 FOV 및 광학 조건이 달라질 수 있다. Camera Resolution만 같다는 이유로 동일한 검사 조건을 기대하면 안 된다.

### Camera ROI와 Cycle Time

Sensor 전체가 필요하지 않다면 Camera ROI로 전송량을 줄여 Frame Rate를 높일 수 있다. 하지만 Align 범위와 제품 편차를 포함하는 충분한 영역을 확보해야 한다.

### Color 검사

빨강과 초록 부품이 Gray 변환 후 비슷한 밝기가 되면 구분이 사라질 수 있다. Channel별 Histogram, HSV/Lab 변환 또는 적절한 광학 Filter와 조명을 검토한다.

---

## 6. 숫자로 이해하기

### 예제 1: 8-bit Gray Image 메모리

조건:

- 2048×2048
- 8-bit Gray, 1 Channel

```text
2048 × 2048 × 1 byte
= 4,194,304 byte
= 4 MiB
```

20 fps이면 Pixel Payload만 약 `80 MiB/s`다.

### 예제 2: 12-bit Image 저장 크기

조건:

- 4096×3000
- 12-bit Mono

16-bit Container에 Unpacked 저장하면:

```text
4096 × 3000 × 2 byte
= 24,576,000 byte
≈ 23.44 MiB/frame
```

이상적으로 12-bit Packed라면:

```text
4096 × 3000 × 12 / 8 byte
= 18,432,000 byte
≈ 17.58 MiB/frame
```

Packed가 약 25% 작지만 실제 Row Padding과 Protocol Overhead는 별도다.

### 예제 3: FOV로 Object Space Pixel Size 계산

조건:

- Image Width: 2000 pixel
- Horizontal FOV: 10 mm = 10,000 μm

```text
Object Space Pixel Size
= 10,000 μm / 2000 pixel
= 5 μm/pixel
```

이미지에서 Edge 사이 거리가 240 pixel이면 이상적인 길이 계산은:

```text
240 pixel × 5 μm/pixel = 1,200 μm = 1.2 mm
```

이는 Calibration Scale이 균일하고 왜곡·Perspective가 무시 가능한 경우의 계산이다.

### 예제 4: Bit Depth 변환

12-bit 유효 값 `3072`를 전체 범위 기준으로 8-bit에 선형 Mapping하면:

```text
3072 / 4095 × 255 ≈ 191.30 → 191
```

단순히 하위 8-bit만 취하면 전혀 다른 값이 된다. 변환 목적과 유효 Bit 정렬을 확인해야 한다.

---

## 7. C++ 구현

### Image 정보와 통계 검사

```cpp
#include <opencv2/opencv.hpp>

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

struct ImageStatistics final {
    double minimum{};
    double maximum{};
    double mean{};
    double standardDeviation{};
    double saturatedRatio{};
};

[[nodiscard]] std::string DescribeType(const cv::Mat& image)
{
    const std::string depth = [&image] {
        switch (image.depth()) {
        case CV_8U:  return std::string{"CV_8U"};
        case CV_16U: return std::string{"CV_16U"};
        case CV_32F: return std::string{"CV_32F"};
        default:     return std::string{"unsupported"};
        }
    }();

    return depth + "C" + std::to_string(image.channels());
}

[[nodiscard]] ImageStatistics CalculateMonoStatistics(
    const cv::Mat& image,
    const double validMaximum)
{
    if (image.empty()) {
        throw std::invalid_argument{"Image is empty"};
    }
    if (image.channels() != 1) {
        throw std::invalid_argument{"Mono image is required"};
    }
    if (validMaximum <= 0.0) {
        throw std::invalid_argument{"validMaximum must be positive"};
    }

    double minimum = 0.0;
    double maximum = 0.0;
    cv::minMaxLoc(image, &minimum, &maximum);

    cv::Scalar mean;
    cv::Scalar standardDeviation;
    cv::meanStdDev(image, mean, standardDeviation);

    cv::Mat saturatedMask;
    cv::compare(image, validMaximum, saturatedMask, cv::CMP_GE);
    const double pixelCount = static_cast<double>(image.total());
    const double saturatedRatio =
        static_cast<double>(cv::countNonZero(saturatedMask)) / pixelCount;

    return {minimum, maximum, mean[0], standardDeviation[0],
            saturatedRatio};
}

[[nodiscard]] cv::Mat Convert12BitTo8BitForDisplay(const cv::Mat& image12)
{
    if (image12.empty() || image12.type() != CV_16UC1) {
        throw std::invalid_argument{"CV_16UC1 image is required"};
    }

    cv::Mat display8;
    constexpr double scale = 255.0 / 4095.0;
    image12.convertTo(display8, CV_8U, scale);
    return display8;
}

int main(int argc, char* argv[])
{
    if (argc != 2) {
        std::cerr << "Usage: image_info <image-path>\n";
        return 1;
    }

    const cv::Mat image = cv::imread(argv[1], cv::IMREAD_UNCHANGED);
    if (image.empty()) {
        std::cerr << "Failed to load image\n";
        return 2;
    }

    std::cout << "width=" << image.cols
              << ", height=" << image.rows
              << ", type=" << DescribeType(image)
              << ", element-bytes=" << image.elemSize()
              << ", row-step=" << image.step << '\n';

    if (image.channels() == 1) {
        const double validMaximum = image.depth() == CV_8U ? 255.0 : 65535.0;
        const auto stats = CalculateMonoStatistics(image, validMaximum);
        std::cout << "min=" << stats.minimum
                  << ", max=" << stats.maximum
                  << ", mean=" << stats.mean
                  << ", stddev=" << stats.standardDeviation
                  << ", saturated=" << stats.saturatedRatio * 100.0
                  << "%\n";
    }
}
```

### 코드에서 봐야 할 점

1. `cols=Width`, `rows=Height`다.
2. `depth()`는 Channel 하나의 자료형이고 `type()`은 Depth와 Channel을 결합한다.
3. `elemSize()`는 한 Pixel의 전체 Byte 수다.
4. `step`은 한 Row에서 다음 Row까지의 Byte 간격이며 `cols×elemSize()`보다 클 수 있다.
5. 12-bit가 16-bit Container에 들어 있다면 `validMaximum=4095`를 Camera Format에 맞게 전달해야 한다.
6. 검사 원본과 Display용 8-bit Image를 분리한다.

### 간단한 Unit Test

```cpp
#include <cassert>
#include <cmath>

void TestEightBitStatistics()
{
    const cv::Mat image = (cv::Mat_<std::uint8_t>(2, 2) << 0, 255, 100, 200);
    const auto stats = CalculateMonoStatistics(image, 255.0);

    assert(stats.minimum == 0.0);
    assert(stats.maximum == 255.0);
    assert(std::abs(stats.mean - 138.75) < 1e-9);
    assert(std::abs(stats.saturatedRatio - 0.25) < 1e-9);
}

void TestTwelveBitDisplayMapping()
{
    const cv::Mat image12 =
        (cv::Mat_<std::uint16_t>(1, 3) << 0, 2048, 4095);
    const cv::Mat display8 = Convert12BitTo8BitForDisplay(image12);

    assert(display8.at<std::uint8_t>(0, 0) == 0);
    assert(display8.at<std::uint8_t>(0, 2) == 255);
}
```

> [!NOTE]
> 12-bit 값이 16-bit 상위 Bit에 정렬된 Format이라면 먼저 정렬을 해석해야 한다. 위 함수는 유효 값이 `0~4095`로 하위 정렬되어 있다는 전제다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: 12-bit를 8-bit로 잘못 읽음

- 증상: 줄무늬, 밝기 왜곡, Width 이상
- 원인: Pixel당 Byte 수와 Packed/Unpacked Format 오해
- 대응: SDK Pixel Format, Stride, 유효 Bit 정렬 확인

### 문제 2: Row Padding 무시

- 증상: Image가 기울거나 다음 Row 시작점이 어긋남
- 원인: `width × bytesPerPixel`만으로 Row 주소 계산
- 대응: SDK의 Pitch/Stride 또는 `cv::Mat::step` 사용

### 문제 3: RGB/BGR Channel 순서 혼동

- 증상: 빨강과 파랑이 뒤바뀌고 Color Threshold 실패
- 원인: SDK RGB와 OpenCV BGR의 차이
- 대응: Interface 경계에서 Pixel Format을 명시하고 변환 테스트

### 문제 4: 포화 Image에 후처리만 적용

- 증상: 밝은 부위의 Edge/Texture가 사라짐
- 원인: Exposure/Gain 과다로 원본 정보가 Clipping됨
- 대응: Exposure·조명 조정, Histogram과 Saturation Ratio 감시

### 문제 5: Resize Image로 치수 측정

- 증상: UI 표시 Image에서 측정한 값과 원본 검사값이 다름
- 원인: Display Resize Scale과 원본 좌표를 혼용
- 대응: 검사는 원본 좌표로 수행하고 Overlay만 Display Transform 적용

### 문제 6: Camera Resolution만으로 작은 결함 검출을 보장

- 증상: Pixel 수는 충분하지만 Defect Contrast가 낮거나 Blur됨
- 원인: Lens MTF, Focus, 조명, Noise와 필요한 Sampling 수 무시
- 대응: Object Space Sampling과 Optical Resolution을 함께 평가

---

## 9. 흔한 오해

1. **“Pixel은 실제 물체의 작은 정사각형이다.”**  
   Image의 Pixel은 샘플 위치다. 실제 물체에서 담당하는 크기는 Lens Magnification/FOV에 따라 달라진다.

2. **“3.45 μm Pixel Camera이면 물체 3.45 μm가 1 Pixel이다.”**  
   3.45 μm는 Sensor Pixel Pitch다. Object Space 값은 배율을 적용해야 한다.

3. **“12-bit는 8-bit보다 공간 해상도가 높다.”**  
   Bit Depth는 밝기 단계이고 공간 Sampling 개수와 다르다.

4. **“16-bit Container이면 항상 16-bit 유효 데이터다.”**  
   10/12-bit 값이 16-bit Container에 저장될 수 있다.

5. **“Resize로 Image를 두 배 키우면 해상도가 두 배 좋아진다.”**  
   Pixel 배열은 커지지만 원본에 없던 광학 세부 정보가 생기지 않는다.

6. **“Pixel 값은 물체의 절대 밝기다.”**  
   조명, Exposure, Gain, Lens, Sensor 및 후처리의 결과다.

7. **“2048×2048이면 항상 4 MiB다.”**  
   8-bit Mono일 때의 Pixel Payload다. Channel, Container, Stride에 따라 달라진다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. Camera Resolution과 Pixel Size의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Camera Resolution은 센서에 Pixel이 몇 개 있는지이고, Pixel Size는 센서 Pixel 하나의 물리적 간격이 몇 μm인지입니다.

**실무자 답변**  
Resolution은 `Width×Height` Pixel Count이며 데이터 크기와 Sampling 개수를 좌우합니다. Pixel Size는 Sensor Pixel Pitch로 Sensor Size와 감도·광학 설계에 영향을 줍니다. 물체 기준 μm/pixel은 Pixel Size를 광학 배율로 나누거나 FOV를 Image Pixel 수로 나눠 계산합니다.

**면접용 30초 답변**  
“Camera Resolution은 2048×2048처럼 Pixel 개수이고 Pixel Size는 3.45 μm처럼 Sensor의 물리적 Pixel Pitch입니다. 실제 물체에서 1 pixel이 몇 μm인지는 Pixel Size만으로 정할 수 없고 Lens Magnification 또는 측정된 FOV가 필요합니다.”

### Q2. Bit Depth가 높으면 무엇이 좋아지나요?

**초보자가 이해할 수 있는 답변**  
밝기를 더 많은 단계로 나눠 미세한 밝기 차이를 표현할 수 있습니다.

**실무자 답변**  
높은 Bit Depth는 Quantization 단계를 늘려 충분한 Sensor SNR과 Dynamic Range가 있을 때 미세 Contrast 보존에 유리합니다. 하지만 데이터 크기와 처리 비용이 증가하며, Noise가 크거나 포화되면 명목상 Bit 수가 실제 정보 증가로 이어지지 않습니다.

**면접용 30초 답변**  
“Bit Depth는 한 Channel의 밝기 단계 수입니다. 8-bit는 256단계, 12-bit는 4096단계라 미세 Contrast 보존에 유리하지만 공간 해상도가 증가하는 것은 아닙니다. 실제 이득은 Sensor Noise와 Dynamic Range, Exposure가 받쳐줄 때 생깁니다.”

### Q3. Spatial Resolution과 Optical Resolution은 어떻게 다른가요?

**초보자가 이해할 수 있는 답변**  
Spatial Resolution은 물체가 Image Pixel에 얼마나 촘촘히 나뉘는지이고, Optical Resolution은 Lens가 실제 세부를 얼마나 선명하게 보여주는지입니다.

**실무자 답변**  
Spatial Sampling은 보통 μm/pixel로 계산하지만 Optical Resolution은 Lens MTF, NA, 파장, Focus, 수차에 제한됩니다. Sampling이 촘촘해도 Optical Image가 Blur되면 세부를 복원할 수 없고, 광학이 좋아도 Sampling이 부족하면 Alias가 발생합니다.

**면접용 30초 답변**  
“Spatial Resolution은 FOV/Pixel Count로 얻는 Object Space Sampling이고, Optical Resolution은 렌즈와 조명이 전달할 수 있는 실제 세부 한계입니다. 검사 가능성은 두 조건을 함께 봐야 하며 μm/pixel만으로 결함 검출을 단정하지 않습니다.”

### Q4. OpenCV에서 `rows/cols`와 `x/y`는 어떻게 대응하나요?

**초보자가 이해할 수 있는 답변**  
`cols`가 Width와 x 방향이고, `rows`가 Height와 y 방향입니다. Pixel 배열 접근은 `(y, x)` 순서입니다.

**실무자 답변**  
`cv::Mat::at(row, col)`은 `(y,x)`이며 `cv::Point`와 `cv::Rect`는 `(x,y)`다. 비정사각형 Test Image와 경계값 테스트를 사용해 교환 오류를 검출하고, 좌표 타입/함수 이름으로 의미를 분명히 합니다.

**면접용 30초 답변**  
“OpenCV에서 `cols=width=x축`, `rows=height=y축`입니다. 다만 Mat Pixel 접근은 `at(y,x)`이고 Point나 Rect 생성자는 `(x,y)`이므로 혼동하기 쉽습니다. 저는 비정사각형 테스트와 ROI 경계 검증으로 이를 확인합니다.”

### Q5. 12-bit Image를 8-bit로 변환할 때 무엇을 확인해야 하나요?

**초보자가 이해할 수 있는 답변**  
12-bit 값이 메모리에 어떤 방식으로 저장됐는지 확인하고 0~4095를 0~255 범위로 올바르게 줄여야 합니다.

**실무자 답변**  
Packed/Unpacked, Container 크기, MSB/LSB 정렬, Black Level과 유효 범위를 확인합니다. 검사용 원본은 보존하고 Display/저장 목적에 맞게 고정 범위 또는 Windowing으로 변환합니다. Frame마다 Min-Max Normalize하면 Review 모양과 Threshold 의미가 흔들릴 수 있습니다.

**면접용 30초 답변**  
“먼저 Pixel Format이 Packed인지, 16-bit Container인지, 유효 12-bit가 어느 쪽에 정렬됐는지 확인합니다. 그 후 검사용 원본은 유지하고 Display용으로 0~4095를 0~255에 Mapping합니다. Frame별 자동 Normalize는 영상 간 밝기 비교를 왜곡할 수 있어 목적에 맞게 사용합니다.”

### Q6. 높은 Camera Resolution이면 작은 결함을 항상 검출할 수 있나요?

**초보자가 이해할 수 있는 답변**  
아닙니다. Pixel이 많아도 Lens가 흐리거나 조명 Contrast가 부족하면 결함이 보이지 않습니다.

**실무자 답변**  
결함 크기 대비 Object Space Sampling, Lens MTF와 Focus, 조명 Contrast, Sensor Noise, Motion Blur, 알고리즘에 필요한 Pixel 수를 함께 평가해야 합니다. 검출과 안정적 치수 측정에 필요한 Sampling도 다릅니다.

**면접용 30초 답변**  
“아닙니다. Pixel Count는 Sampling 한 요소일 뿐입니다. 실제 검출에는 FOV 기준 μm/pixel, Lens MTF와 Focus, 조명 Contrast, Noise, Motion Blur 및 알고리즘이 요구하는 최소 Pixel 수가 모두 충족되어야 합니다.”

---

## 11. 실습 문제

### 실습 1: Image Inspector 구현

이미지 파일을 입력받아 다음을 출력한다.

- Width, Height, Channel, Depth, Type
- `elemSize`, `step`, 연속 메모리 여부
- Min, Max, Mean, Standard Deviation
- 8-bit Mono일 때 Histogram CSV
- Saturated Pixel 비율

빈 파일, 8-bit Gray, 8-bit BGR, 16-bit Mono로 테스트한다.

### 실습 2: 메모리와 대역폭 계산

다음을 각각 Unpacked 기준으로 계산한다.

1. 2448×2048, 8-bit Mono, 30 fps
2. 4096×3000, 12-bit Mono를 16-bit Container로 저장, 20 fps
3. 2048×2048, 8-bit BGR, 10 fps, Camera 4대

Pixel Payload와 초당 데이터양을 MiB 단위로 구하고, Image를 3회 Deep Copy할 때 메모리 Traffic이 어떻게 늘어나는지 설명한다.

### 실습 3: Bit Depth 변환 비교

12-bit Gradient Image를 만들고 다음 방법을 비교한다.

- 고정 범위 `0~4095 → 0~255`
- 특정 검사 범위 `1000~2500 → 0~255`
- Frame별 Min-Max Normalize
- 단순 Bit Shift

각 방법이 Review, Threshold, Frame 간 비교에 미치는 영향을 기록한다.

### 실습 4: Resolution 용어 설명

아래 사양을 보고 5개 Resolution 용어를 각각 한 문장으로 설명한다.

```text
Camera: 2048×2048, Pixel Size 3 μm
Lens Magnification: 0.5×
Saved Image: Camera ROI 적용 후 1024×768
```

아직 계산하지 못하는 값은 “왜 정보가 부족한가?”를 함께 적는다.

### Phase 1 미니 프로젝트: Image Metadata & Quality Inspector

C++17/OpenCV로 다음을 구현한다.

```text
Image Load
   ↓
Metadata Validation
   ↓
Type / Size / Stride Report
   ↓
Histogram / Statistics
   ↓
Underexposure / Saturation Warning
   ↓
Display Conversion
   ↓
CSV + Preview Save
```

**필수 조건**

- 원본 Image를 수정하지 않는다.
- 8-bit/16-bit Mono와 8-bit BGR을 구분한다.
- 검사 통계와 Display 변환을 별도 함수로 만든다.
- 지원하지 않는 Type은 명확한 Error로 반환한다.
- 정상·빈 Image·포화 Image Unit Test를 작성한다.

---

## 12. Chapter 핵심 요약

- 🔴 Image는 Width×Height의 Pixel 배열이며 Pixel은 디지털 샘플이다.
- 🔴 OpenCV에서 `cols=x=Width`, `rows=y=Height`, 배열 접근은 `(y,x)`다.
- 🔴 Bit Depth는 밝기 단계이며 공간 해상도와 다르다.
- 🔴 10/12-bit Image는 16-bit Container 또는 Packed Format일 수 있다.
- 🔴 Camera Resolution, Image Resolution, Pixel Size는 서로 다른 사양이다.
- 🔴 Object Space의 μm/pixel은 FOV/Pixel Count 또는 Pixel Size/Magnification으로 계산한다.
- 🔴 Optical Resolution과 Sampling을 함께 봐야 실제 검출 가능성을 판단할 수 있다.
- 🟠 `step`과 SDK Stride를 사용해야 Row Padding을 안전하게 처리한다.
- 🟠 Saturation으로 손실된 정보는 후처리 Contrast 조정으로 복구되지 않는다.
- 🟠 검사 원본과 Display용 변환 Image를 분리한다.

---

## 2일차 권장 학습 순서

- [ ] 45분: 3.1~3.6 읽고 Bit Depth 표를 직접 다시 작성
- [ ] 45분: Resolution 5종을 본인 말로 비교
- [ ] 30분: 숫자 예제 1~4를 계산기 없이 다시 계산
- [ ] 60~90분: C++ 예제 실행 또는 코드 리뷰
- [ ] 60분: 실습 1의 Image Inspector 구현
- [ ] 30분: 면접 Q1~Q6의 30초 답변 녹음
- [ ] 20분: 틀린 내용과 질문을 문서 하단에 기록

## 학습 완료 체크

- [ ] 8/10/12/16-bit의 범위와 저장 차이를 설명할 수 있다.
- [ ] Camera/Image/Spatial/Optical Resolution과 Pixel Size를 구분한다.
- [ ] `2048×2048 8-bit Mono = 4 MiB`를 계산할 수 있다.
- [ ] OpenCV의 `rows`, `cols`, `channels`, `depth`, `step`을 설명할 수 있다.
- [ ] 12-bit 원본과 8-bit Display Image를 분리해야 하는 이유를 설명한다.
- [ ] Phase 1 미니 프로젝트를 설계하거나 구현했다.

## 다음 Chapter 예고

다음 Chapter에서는 `Camera Pixel Size = 3 μm`의 정확한 의미를 배우고, 0.5×/1×/2× Magnification에서 Sensor Size, FOV, Object Space Pixel Resolution을 직접 계산한다.
