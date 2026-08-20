# Chapter 3. Camera Pixel Size와 실제 물체의 관계

> Phase 2 · 3일차 · 예상 학습 시간: 10~14시간 · 난이도: 입문→중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Camera Pixel Size(Pixel Pitch)의 정확한 의미
- 🔴 Sensor Size = Pixel Count × Pixel Size
- 🔴 Object Space Pixel Size = Camera Pixel Size ÷ Magnification
- 🔴 FOV = Sensor Size ÷ Magnification
- 🔴 Object Space Pixel Size = FOV ÷ Image Pixel Count
- 🔴 0.5×, 1×, 2× 배율에서 FOV와 μm/pixel 변화
- 🟠 명목 배율과 실제 배율, Calibration Scale의 차이
- 🟠 Sampling과 실제 Defect 검출 능력의 차이

### 실무 목표

`Camera Pixel Size = 3 μm`라는 사양을 보고 Sensor의 Physical Pixel Pitch임을 설명한다. Camera Resolution과 Lens Magnification을 이용해 Sensor Size, FOV, Object Space Pixel Resolution을 계산하고, 측정한 FOV로 결과를 교차 검산한다.

> [!IMPORTANT]
> **“3 μm Camera이므로 물체의 3 μm가 항상 Image 1 Pixel이다”는 틀린 문장이다.**  
> 3 μm는 Sensor 위의 Pixel Pitch다. 물체 기준 μm/pixel은 Lens Magnification 또는 실제 FOV가 있어야 정해진다.

---

## 2. 선수 지식

- Chapter 2의 Camera Resolution, Image Resolution, Pixel Size 구분
- `1 mm = 1,000 μm`
- 배율(Magnification)은 `Image Space 크기 ÷ Object Space 크기`
- Width와 Height 방향 계산은 각각 독립적임

### 2.1 이번 Chapter의 기호

| 기호 | 의미 | 단위 |
|---|---|---|
| `N_x`, `N_y` | Sensor/Image Pixel Count | pixel |
| `p` | Camera Sensor Pixel Pitch | μm/pixel |
| `S_x`, `S_y` | Sensor Physical Size | μm 또는 mm |
| `M` | Optical Magnification | 무차원, × |
| `FOV_x`, `FOV_y` | Object Space에서 보이는 범위 | μm 또는 mm |
| `r_o` | Object Space Pixel Size/Sampling | μm/pixel |

이 Chapter는 정사각형 Pixel, 일정한 배율, 왜곡이 무시 가능한 이상적 모델부터 시작한다. 실제 장비에서는 Calibration으로 위치별 Scale과 왜곡을 확인한다.

---

## 3. 핵심 개념

### 3.1 Camera Pixel Size = 3 μm의 의미

Camera 사양의 `Pixel Size = 3 μm × 3 μm`는 보통 Sensor 위에서 인접 Pixel 중심 사이 간격인 **Pixel Pitch**가 가로·세로 각각 약 3 μm라는 뜻이다.

```text
Camera Sensor

       3 μm pitch
    ◄──────────►
    ┌──────────┐
    │  Pixel   │  ▲
    │          │  │ 3 μm pitch
    └──────────┘  ▼
```

이는 다음과 같은 뜻이 아니다.

- 물체의 3 μm Defect를 반드시 검출한다.
- Image의 1 Pixel이 항상 물체의 3 μm다.
- Lens가 없어도 물체 크기를 계산할 수 있다.

Sensor Pixel의 실제 광감지 영역(Photosensitive Area)은 Pixel Pitch 전체와 다를 수 있다. Microlens, 회로, Fill Factor도 감도에 영향을 주지만 현재 단계에서는 Pixel Pitch를 Sensor Size 계산에 사용한다.

### 3.2 Sensor Size 계산

```text
Sensor Width  = Horizontal Pixel Count × Pixel Size
Sensor Height = Vertical Pixel Count × Pixel Size
```

2048×2048, 3 μm Camera라면:

```text
Sensor Width = 2048 pixel × 3 μm/pixel
             = 6144 μm = 6.144 mm

Sensor Height = 6.144 mm
```

`2048×2048`은 Image 배열의 Pixel 수이고 `6.144×6.144 mm`는 Sensor의 물리적 크기다.

### 3.3 Optical Magnification

```text
Magnification M = Image Size on Sensor / Object Size
```

- `M = 1×`: 물체의 1 mm가 Sensor 위 1 mm로 결상
- `M = 0.5×`: 물체의 1 mm가 Sensor 위 0.5 mm로 결상
- `M = 2×`: 물체의 1 mm가 Sensor 위 2 mm로 결상

배율이 커지면 같은 Sensor에 물체의 더 작은 영역만 보인다. FOV는 줄고 Object Space Sampling은 더 촘촘해진다.

### 3.4 Object Space Pixel Size

Sensor의 Pixel Pitch `p`에 대응하는 물체 공간의 길이는:

```text
Object Space Pixel Size r_o = p / M
```

| Pixel Size | Magnification | Object Space Pixel Size |
|---:|---:|---:|
| 3 μm | 0.5× | 6 μm/pixel |
| 3 μm | 1× | 3 μm/pixel |
| 3 μm | 2× | 1.5 μm/pixel |

`0.5×`에서는 물체가 Sensor에 절반 크기로 맺히므로 Sensor 1 Pixel이 물체의 더 넓은 6 μm 구간을 담당한다. `2×`에서는 물체가 두 배로 확대되어 1 Pixel이 물체의 1.5 μm 구간을 담당한다.

### 3.5 FOV 계산

```text
FOV = Sensor Size / Magnification
```

6.144 mm Sensor라면:

| Magnification | Horizontal FOV | Vertical FOV |
|---:|---:|---:|
| 0.5× | 12.288 mm | 12.288 mm |
| 1× | 6.144 mm | 6.144 mm |
| 2× | 3.072 mm | 3.072 mm |

배율이 2배가 되면 FOV와 μm/pixel은 절반이 된다. 반대로 배율이 절반이면 FOV와 μm/pixel은 2배가 된다.

### 3.6 FOV 방식으로 교차 검산

```text
Object Space Pixel Size = FOV / Image Pixel Count
```

0.5× 예제:

```text
12.288 mm / 2048 pixel
= 0.006 mm/pixel
= 6 μm/pixel
```

이는 `3 μm / 0.5 = 6 μm/pixel`과 같다. 두 방식의 결과가 다르면 다음을 확인한다.

- 사용한 Image가 Full Sensor인지 Camera ROI/Crop인지
- Lens의 명목 배율과 실제 배율이 같은지
- FOV 측정 기준이 Sensor 전체인지
- Pixel Size와 Pixel Count가 해당 Camera Mode의 값인지
- Lens Distortion/Perspective가 큰지

### 3.7 Sensor Pixel과 Image Pixel은 같은가?

Full Resolution, 1:1 Readout, Software Resize 없음이라면 Sensor Pixel 하나가 출력 Image Pixel 하나에 대응한다고 볼 수 있다. 하지만 다음 경우에는 단순 대응이 깨진다.

- Binning: 여러 Sensor Pixel을 출력 Pixel 하나로 결합
- Decimation/Skipping: 일부 Sensor Pixel만 읽음
- Camera ROI: Sensor 일부만 출력하지만 ROI 내부에서는 1:1일 수 있음
- Debayer: Color Filter Array의 Sensor Sample로 Color Pixel을 보간
- Software Resize: 출력 배열을 보간해 새 Pixel Grid 생성

따라서 SDK의 Pixel Format과 Camera Mode를 확인해야 한다.

### 3.8 명목 배율과 실제 배율

Lens에 `0.5×`라고 적혀 있어도 실제 장착 조건, Working Distance, Focus, Tube Length 등에 따라 유효 배율이 달라질 수 있다. 실무에서는 알려진 길이의 Calibration Target을 촬영해 실제 Scale을 측정한다.

```text
Known Length = 10.000 mm
Measured Pixel Distance = 1660 pixel

Measured Scale = 10,000 μm / 1660 pixel
               ≈ 6.024 μm/pixel
```

3 μm Pixel 기준 실제 배율은:

```text
M_effective = 3 μm/pixel / 6.024 μm/pixel
            ≈ 0.498×
```

명목 0.5×와 가깝지만 측정/Calibration 값이 실제 치수 계산의 기준이 된다.

### 3.9 Sampling과 실제 Resolution

`1.5 μm/pixel`이라고 해서 1.5 μm Defect를 안정적으로 검출한다는 뜻은 아니다.

```text
Object Space Sampling
        + Lens MTF / Focus
        + Illumination Contrast
        + Sensor Noise / Exposure
        + Motion Blur
        + Algorithm의 최소 필요 Pixel 수
        = 실제 검사 성능
```

Defect가 1 Pixel보다 작아도 Pixel 평균값에 영향을 주어 보일 수 있지만 위치·Contrast에 민감하다. 안정적인 검출이나 치수 측정에는 일반적으로 여러 Pixel에 걸친 표현이 필요하며, 필요한 수는 결함과 알고리즘별 실험으로 정해야 한다.

---

## 4. 그림으로 이해하기

### 4.1 Camera-Lens-Object 관계

```text
Object Space                Lens                 Image Space

12.288 mm object FOV        0.5×              6.144 mm Sensor
┌──────────────────┐         )(               ┌──────────┐
│                  │ ───────────────────────► │ 2048 px  │
└──────────────────┘                          └──────────┘

Object: 6 μm/pixel                           Sensor: 3 μm/pixel
```

### 4.2 배율 변화

```text
M = 0.5×   wide FOV, coarse sampling   12.288 mm, 6 μm/px
M = 1.0×   middle                      6.144 mm, 3 μm/px
M = 2.0×   narrow FOV, fine sampling   3.072 mm, 1.5 μm/px

Magnification ↑  → FOV ↓ → Object μm/pixel ↓ → 더 촘촘한 Sampling
Magnification ↓  → FOV ↑ → Object μm/pixel ↑ → 더 넓은 영역
```

### 4.3 한 Pixel까지의 흐름

```text
Object의 작은 영역
       │ Lens Magnification
       ▼
Sensor의 3 μm Pixel Pitch
       │ A/D conversion
       ▼
Image Pixel Value
```

Image Pixel 값은 해당 Object 영역의 “크기 값”이 아니라 그 영역에서 광학계가 전달한 빛을 Sensor가 Sampling한 밝기 값이다.

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Lens 및 Camera 선정

검사 대상 폭이 10 mm이고 양쪽 Margin을 포함해 12 mm FOV가 필요하다면 6.144 mm Sensor에서 약 `0.512×` 이하 배율이 필요하다. 원하는 μm/pixel과 FOV를 동시에 만족하는지 확인해야 한다.

### 치수 측정

Edge 간 거리가 500 pixel이고 Calibration Scale이 6 μm/pixel이면 이상적인 길이는 3 mm다. 하지만 위치별 Scale과 Sub-pixel Edge 알고리즘의 Bias를 Gauge로 검증해야 한다.

### Defect 사양 협의

고객이 2 μm Defect 검출을 요구할 때 Camera Pixel Size만 보고 가능하다고 답하지 않는다. FOV와 Sampling, Lens MTF, 조명 Contrast, Exposure/Noise, Defect 형상과 검출률 기준을 함께 확인한다.

### Recipe와 Calibration 관리

Camera ROI, Binning, Lens, Working Distance 또는 Focus를 바꾸면 Scale이 변할 수 있다. Recipe에 Camera Mode, Optical Configuration ID, Calibration Version을 함께 저장해야 한다.

### Stage 이동량 계산

Align 결과가 `+20 pixel`이고 Calibration Scale이 `5 μm/pixel`이라면 크기는 100 μm다. 실제 Stage 명령에는 축 방향, Rotation, Offset 및 Camera와 Stage의 관계를 추가 적용한다.

---

## 6. 숫자로 이해하기

### 예제 1: 3 μm, 2048×2048, 1×

```text
Sensor Size
= 2048 pixel × 3 μm/pixel
= 6144 μm = 6.144 mm

Object Space Pixel Size
= 3 μm/pixel ÷ 1
= 3 μm/pixel

FOV
= 6.144 mm ÷ 1
= 6.144 mm × 6.144 mm
```

### 예제 2: 같은 Camera, 0.5×

```text
Object Space Pixel Size
= 3 μm/pixel ÷ 0.5
= 6 μm/pixel

FOV
= 6.144 mm ÷ 0.5
= 12.288 mm × 12.288 mm
```

물체 6 μm가 이상적으로 Image 1 Pixel 간격에 대응한다. 이는 6 μm 특징을 안정적으로 검출한다는 보장은 아니다.

### 예제 3: 같은 Camera, 2×

```text
Object Space Pixel Size
= 3 μm/pixel ÷ 2
= 1.5 μm/pixel

FOV
= 6.144 mm ÷ 2
= 3.072 mm × 3.072 mm
```

### 예제 4: 실제 FOV로 Scale 계산

Full Width 2048 pixel에서 실제 Target으로 측정한 FOV가 12.20 mm라면:

```text
12.20 mm = 12,200 μm

Measured Scale
= 12,200 μm / 2048 pixel
≈ 5.95703125 μm/pixel
```

3 μm Camera의 유효 배율:

```text
M_effective = 3 / 5.95703125 ≈ 0.5036×
```

### 예제 5: 요구사항 역산

조건:

- 검사 FOV Width ≥ 10 mm
- Image Width = 2048 pixel
- 최소 결함이 안정적으로 4 Pixel에 걸쳐야 함

FOV 10 mm일 때 Sampling:

```text
10,000 μm / 2048 pixel ≈ 4.8828 μm/pixel
```

4 Pixel에 대응하는 물체 크기:

```text
4 × 4.8828 μm ≈ 19.53 μm
```

따라서 이 단순 Sampling 기준에서는 약 20 μm 특징이 4 Pixel을 차지한다. 10 μm Defect를 4 Pixel로 표현하려면 `2.5 μm/pixel` 이하가 필요하고, 10 mm FOV에서는 가로 4000 Pixel 이상이 필요하다. 광학 조건은 별도로 만족해야 한다.

---

## 7. C++ 구현

### Camera-Lens 계산기

```cpp
#include <cmath>
#include <cstddef>
#include <initializer_list>
#include <iostream>
#include <stdexcept>

struct CameraSpec final {
    std::size_t widthPixels{};
    std::size_t heightPixels{};
    double pixelPitchUm{};
};

struct OpticalCalculation final {
    double sensorWidthMm{};
    double sensorHeightMm{};
    double fovWidthMm{};
    double fovHeightMm{};
    double objectUmPerPixel{};
};

[[nodiscard]] OpticalCalculation CalculateOptics(
    const CameraSpec& camera,
    const double magnification)
{
    if (camera.widthPixels == 0 || camera.heightPixels == 0) {
        throw std::invalid_argument{"Pixel count must be positive"};
    }
    if (!std::isfinite(camera.pixelPitchUm) || camera.pixelPitchUm <= 0.0) {
        throw std::invalid_argument{"Pixel pitch must be finite and positive"};
    }
    if (!std::isfinite(magnification) || magnification <= 0.0) {
        throw std::invalid_argument{"Magnification must be finite and positive"};
    }

    constexpr double umPerMm = 1000.0;
    const double sensorWidthMm =
        static_cast<double>(camera.widthPixels) * camera.pixelPitchUm / umPerMm;
    const double sensorHeightMm =
        static_cast<double>(camera.heightPixels) * camera.pixelPitchUm / umPerMm;

    return {
        sensorWidthMm,
        sensorHeightMm,
        sensorWidthMm / magnification,
        sensorHeightMm / magnification,
        camera.pixelPitchUm / magnification
    };
}

[[nodiscard]] double CalculateMeasuredUmPerPixel(
    const double measuredFovMm,
    const std::size_t imagePixels)
{
    if (!std::isfinite(measuredFovMm) || measuredFovMm <= 0.0 ||
        imagePixels == 0) {
        throw std::invalid_argument{"FOV and pixel count must be positive"};
    }
    return measuredFovMm * 1000.0 / static_cast<double>(imagePixels);
}

[[nodiscard]] double CalculateEffectiveMagnification(
    const double sensorPixelPitchUm,
    const double measuredObjectUmPerPixel)
{
    if (sensorPixelPitchUm <= 0.0 || measuredObjectUmPerPixel <= 0.0) {
        throw std::invalid_argument{"Scale values must be positive"};
    }
    return sensorPixelPitchUm / measuredObjectUmPerPixel;
}

int main()
{
    const CameraSpec camera{2048, 2048, 3.0};

    for (const double magnification : {0.5, 1.0, 2.0}) {
        const auto result = CalculateOptics(camera, magnification);
        std::cout << magnification << "x: FOV="
                  << result.fovWidthMm << " x " << result.fovHeightMm
                  << " mm, sampling=" << result.objectUmPerPixel
                  << " um/pixel\n";
    }

    const double measuredScale = CalculateMeasuredUmPerPixel(12.20, 2048);
    const double effectiveMagnification =
        CalculateEffectiveMagnification(camera.pixelPitchUm, measuredScale);
    std::cout << "Measured scale=" << measuredScale
              << " um/pixel, effective M=" << effectiveMagnification << "x\n";
}
```

예상 핵심 출력:

```text
0.5x: FOV=12.288 x 12.288 mm, sampling=6 um/pixel
1x: FOV=6.144 x 6.144 mm, sampling=3 um/pixel
2x: FOV=3.072 x 3.072 mm, sampling=1.5 um/pixel
```

### 간단한 Unit Test

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

void TestHalfMagnification()
{
    const auto result = CalculateOptics({2048, 2048, 3.0}, 0.5);
    assert(NearlyEqual(result.sensorWidthMm, 6.144));
    assert(NearlyEqual(result.fovWidthMm, 12.288));
    assert(NearlyEqual(result.objectUmPerPixel, 6.0));
}

void TestFovCrossCheck()
{
    const double scale = CalculateMeasuredUmPerPixel(12.288, 2048);
    assert(NearlyEqual(scale, 6.0));
    assert(NearlyEqual(CalculateEffectiveMagnification(3.0, scale), 0.5));
}

void TestInvalidMagnification()
{
    bool thrown = false;
    try {
        static_cast<void>(CalculateOptics({2048, 2048, 3.0}, 0.0));
    } catch (const std::invalid_argument&) {
        thrown = true;
    }
    assert(thrown);
}
```

### 코드에서 봐야 할 점

1. Pixel Count, Pixel Pitch, Magnification에 단위와 의미가 드러나는 이름을 사용했다.
2. μm와 mm 변환을 한 지점에서 명시했다.
3. `0×`, 음수, NaN/Infinity를 거부한다.
4. Lens 사양 계산값과 실제 FOV 측정값을 별도 함수로 구분했다.
5. 실제 제품에서는 X/Y Pixel Pitch가 다르거나 Calibration이 위치별로 다를 가능성을 모델에 반영해야 한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: 명목 배율만 사용해 치수 오차 발생

- 원인: Working Distance, Focus, 장착 공차로 실제 배율 변화
- 대응: Calibration Target으로 실제 μm/pixel 측정, Calibration Version 관리

### 문제 2: Camera ROI 이후에도 Full Width로 나눔

- 원인: 1024 Pixel ROI Image에 2048 Pixel을 사용해 Scale 계산
- 대응: FOV와 Pixel Count가 동일한 출력 영역을 기준으로 계산

### 문제 3: Resize된 Review Image에서 좌표 측정

- 원인: 원본 2048 Pixel을 UI 1024 Pixel로 줄였는데 Display 좌표를 원본 좌표로 해석
- 대응: Display↔Original Transform을 명시하고 검사는 원본 좌표 사용

### 문제 4: Lens Distortion으로 위치별 Scale이 다름

- 원인: 중심과 가장자리의 배율 차이를 단일 μm/pixel로 처리
- 대응: 왜곡 보정, Grid Calibration, 위치별 Residual 확인

### 문제 5: Pixel Sampling을 실제 검출 Resolution으로 오해

- 원인: Lens MTF, Focus, 조명, Noise, Motion Blur 무시
- 대응: Golden Sample/Defect Sample로 Detection Rate와 False Positive 검증

### 문제 6: Binning Mode 변경 후 Calibration 재사용

- 원인: 출력 Pixel 하나가 결합하는 Sensor 영역이 변했는데 기존 Scale 사용
- 대응: Camera Mode를 Calibration Key에 포함하고 변경 시 무효화

---

## 9. 흔한 오해

1. **“3 μm Pixel Camera면 물체 3 μm가 1 Pixel이다.”**  
   1×일 때의 이상적 Sampling과 우연히 같을 뿐이며 배율이 바뀌면 달라진다.

2. **“배율이 클수록 언제나 좋다.”**  
   Sampling은 촘촘해지지만 FOV와 DOF가 줄고 정렬·초점·진동 민감도가 커질 수 있다.

3. **“μm/pixel이 2 μm면 2 μm Defect를 보장한다.”**  
   Sampling 간격일 뿐 실제 검출에는 광학과 Contrast, Noise, 필요한 Pixel 수가 중요하다.

4. **“Sensor Pixel과 Image Pixel은 언제나 1:1이다.”**  
   Binning, Decimation, Debayer, Resize가 있으면 달라질 수 있다.

5. **“FOV는 Camera 사양만으로 정해진다.”**  
   Sensor Size와 Lens Magnification의 조합으로 정해진다.

6. **“Lens에 적힌 0.5×가 정확한 실제 배율이다.”**  
   장착 조건에 따라 달라질 수 있으므로 실제 Calibration으로 확인한다.

7. **“Pixel Size가 작으면 무조건 영상이 좋다.”**  
   같은 Sensor 기술과 조건에서도 감도, Full Well Capacity, Noise, Lens Resolution 요구와 Trade-off가 있다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. Camera Pixel Size가 3 μm라는 것은 무슨 의미인가요?

**초보자가 이해할 수 있는 답변**  
Camera Sensor에서 Pixel 하나의 물리적 간격이 약 3 μm라는 뜻입니다. 물체의 3 μm가 항상 Image 1 Pixel이라는 뜻은 아닙니다.

**실무자 답변**  
Sensor의 Pixel Pitch가 3 μm라는 뜻이다. Full Resolution 1:1 Readout에서는 출력 Pixel과 Sensor Pixel이 대응하지만, Object Space Sampling은 `3 μm/M`으로 Lens의 유효 배율에 따라 달라진다. 실제 치수는 FOV 또는 Calibration Target으로 Scale을 검증한다.

**면접용 30초 답변**  
“3 μm는 물체가 아니라 Sensor의 Physical Pixel Pitch입니다. 실제 물체에서 1 Pixel이 담당하는 길이는 `Pixel Pitch ÷ Lens Magnification`입니다. 따라서 0.5×면 6 μm/pixel, 1×면 3 μm/pixel, 2×면 1.5 μm/pixel이며 실제 측정은 Calibration으로 확인합니다.”

### Q2. 2048 Pixel, 3 μm Camera의 Sensor Width는 얼마인가요?

**초보자가 이해할 수 있는 답변**  
2048에 3 μm를 곱하면 6144 μm, 즉 6.144 mm입니다.

**실무자 답변**  
정사각 3 μm Pitch와 2048 유효 Pixel이라는 전제에서 `2048×3 μm=6.144 mm`다. Data Sheet의 Active Area, Optical Format, 유효 Pixel과 전체 Pixel의 차이를 확인하고 Lens Image Circle이 Sensor를 커버해야 한다.

**면접용 30초 답변**  
“Sensor Width는 Pixel Count×Pixel Pitch이므로 `2048×3 μm=6144 μm=6.144 mm`입니다. 이 물리적 Sensor Width를 배율로 나누면 Object FOV를 구할 수 있습니다.”

### Q3. Magnification이 증가하면 FOV와 μm/pixel은 어떻게 되나요?

**초보자가 이해할 수 있는 답변**  
배율이 커지면 확대되어 더 좁은 영역을 보고, 물체 기준 한 Pixel의 크기는 작아집니다.

**실무자 답변**  
고정 Sensor에서 `FOV=S/M`, `Object μm/pixel=p/M`이므로 둘 다 배율에 반비례한다. 다만 Sampling 개선이 Optical Resolution 개선을 자동 보장하지 않고, DOF와 조립 공차, Focus 민감도도 함께 평가해야 한다.

**면접용 30초 답변**  
“고정 Camera에서는 배율이 증가할수록 FOV와 Object Space μm/pixel이 배율에 반비례해 감소합니다. 예를 들어 1×에서 3 μm/pixel이면 2×에서 1.5 μm/pixel이지만 FOV는 절반이 됩니다.”

### Q4. Object Space Pixel Size를 두 가지 방식으로 계산해 보세요.

**초보자가 이해할 수 있는 답변**  
Camera Pixel Size를 배율로 나누거나, 실제 FOV를 Image Pixel 수로 나눕니다.

**실무자 답변**  
이상적 설계값은 `p/M`, 실제 측정 기반 값은 `FOV/N`이다. 둘의 차이는 명목/유효 배율, Camera ROI, Distortion, FOV 측정 오차를 찾는 단서다. 치수 검사는 Calibration Target 기반 값을 우선한다.

**면접용 30초 답변**  
“설계 단계에서는 `Sensor Pixel Pitch ÷ Magnification`, 장비에서는 `측정 FOV ÷ Image Pixel Count`로 구합니다. 두 값을 교차 검산하고 차이가 있으면 실제 배율, ROI Mode, 왜곡과 Calibration 조건을 확인합니다.”

### Q5. 3 μm Pixel Camera로 2 μm Defect를 검출할 수 있나요?

**초보자가 이해할 수 있는 답변**  
Pixel Size만으로는 알 수 없습니다. Lens 배율, 선명도, 조명 Contrast와 Noise를 함께 봐야 합니다.

**실무자 답변**  
먼저 Object Space Sampling을 계산하고 Defect가 몇 Pixel에 걸리는지 본다. 이후 Lens MTF/Focus, 조명에 따른 Defect Contrast, Sensor SNR, Motion Blur, Sub-pixel 위치에 따른 응답, 목표 Detection/False Positive Rate를 Sample로 검증해야 한다.

**면접용 30초 답변**  
“Pixel Size 하나로는 판단할 수 없습니다. 배율을 적용한 Object μm/pixel, Lens MTF와 Focus, 조명 Contrast, Noise 및 알고리즘의 최소 Sampling 요구를 확인해야 합니다. 최종 판단은 실제 Defect Sample의 검출률과 오검률로 검증합니다.”

### Q6. 명목 배율 대신 Calibration이 필요한 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
실제로 Lens를 장착하면 거리와 초점 때문에 사양서 배율과 조금 달라질 수 있기 때문입니다.

**실무자 답변**  
Working Distance, Focus, 장착 공차, Sensor/Lens 자세, Distortion으로 실제 Scale과 좌표 방향이 달라진다. 알려진 Target으로 Scale, Rotation, Offset 및 필요 시 위치별 왜곡을 추정하고 Residual을 확인해야 측정 추적성을 확보할 수 있다.

**면접용 30초 답변**  
“Lens의 명목 배율은 설계값이고 실제 장착에서는 WD, Focus, 공차와 왜곡 때문에 Scale이 달라집니다. Calibration Target으로 실제 μm/pixel과 좌표 변환을 구하고 Version을 Recipe/Result에 남겨야 치수와 위치 결과를 재현할 수 있습니다.”

---

## 11. 실습 문제

### 실습 1: 배율별 계산표 만들기

Camera가 `4096×3000`, Pixel Size가 `3.45 μm`일 때 다음 배율을 계산한다.

- 0.25×
- 0.5×
- 1×
- 2×

각각 Sensor Width/Height, FOV Width/Height, Object μm/pixel을 손 계산하고 C++ 결과와 비교한다.

### 실습 2: 요구사항에서 Camera Pixel Count 역산

조건:

- FOV Width = 20 mm
- 최소 Defect Width = 25 μm
- Defect가 최소 5 Pixel에 걸쳐야 한다는 내부 기준

필요한 최대 μm/pixel과 최소 Horizontal Pixel Count를 계산한다. 이후 Lens MTF와 조명을 확인하지 않으면 안 되는 이유도 작성한다.

### 실습 3: 실제 Scale 측정

Grid 또는 자를 촬영한 Image를 사용한다.

1. 멀리 떨어진 두 기준점의 실제 거리를 기록한다.
2. 두 점 사이 Pixel 거리를 측정한다.
3. μm/pixel과 유효 배율을 계산한다.
4. Image 중앙과 가장자리에서 반복한다.
5. 차이를 왜곡 또는 측정 오차 관점에서 분석한다.

### 실습 4: Camera Mode 변경 영향 분석

Full Image 2048×2048에서 다음 Mode로 바뀔 때 Pixel Count, FOV, μm/output-pixel 및 대역폭이 어떻게 달라지는지 설명한다.

- 중앙 Camera ROI 1024×1024, 1:1 Readout
- 2×2 Binning으로 1024×1024 출력
- Software Resize로 1024×1024 저장

세 Mode가 같은 `1024×1024 Image`를 만들더라도 의미가 다른 이유를 적는다.

### Phase 2 미니 프로젝트: Camera–Lens Calculator

C++17로 다음 기능을 구현한다.

```text
Camera Spec 입력
  ├─ Width/Height Pixel
  └─ Pixel Pitch μm
Lens Magnification 입력
        ↓
Sensor Size / FOV / μm-per-pixel 계산
        ↓
Measured FOV 또는 Calibration Distance 입력
        ↓
Measured Scale / Effective Magnification 계산
        ↓
설계값과 측정값 오차율 출력
```

**필수 검증**

- 0/음수/NaN 입력 거부
- μm/mm 단위 변환 Unit Test
- 0.5×/1×/2× Golden Value Test
- `p/M`과 `FOV/N` 교차 검산
- 설계값 대비 측정값 오차가 기준을 넘으면 Warning

---

## 12. Chapter 핵심 요약

- 🔴 Camera Pixel Size는 Sensor의 Physical Pixel Pitch다.
- 🔴 `Sensor Size = Pixel Count × Pixel Pitch`다.
- 🔴 `Object μm/pixel = Pixel Pitch ÷ Magnification`이다.
- 🔴 `FOV = Sensor Size ÷ Magnification`이다.
- 🔴 실제 FOV가 있으면 `FOV ÷ Image Pixel Count`로 Scale을 교차 검산한다.
- 🔴 3 μm Camera에서 0.5×/1×/2×는 각각 6/3/1.5 μm/pixel이다.
- 🔴 배율이 증가하면 FOV와 μm/pixel은 감소한다.
- 🔴 μm/pixel은 Sampling이며 실제 검출 가능성을 단독으로 보장하지 않는다.
- 🟠 Binning, ROI, Resize가 Sensor Pixel과 Image Pixel 관계를 바꿀 수 있다.
- 🟠 실제 치수와 좌표에는 명목 배율보다 검증된 Calibration을 사용한다.

---

## 3일차 권장 학습 순서

- [ ] 40분: Pixel Pitch와 Object Space Pixel Size 차이를 그림으로 설명
- [ ] 50분: 0.5×/1×/2× 계산을 손으로 반복
- [ ] 30분: `p/M`과 `FOV/N` 방식으로 교차 검산
- [ ] 60~90분: C++ Camera–Lens Calculator 구현
- [ ] 60분: 요구사항 역산 실습 1~2
- [ ] 30분: 면접 Q1~Q6을 30초 답변으로 연습
- [ ] 20분: 실제 업무 Camera/Lens 사양에서 모르는 항목 목록 작성

## 학습 완료 체크

- [ ] `3 μm Camera`의 뜻을 오해 없이 설명할 수 있다.
- [ ] Sensor Size, FOV, Object μm/pixel을 단위와 함께 계산한다.
- [ ] 배율 변화의 장점과 FOV Trade-off를 설명한다.
- [ ] Camera ROI/Binning/Resize의 차이를 설명한다.
- [ ] Sampling과 실제 검출 Resolution의 차이를 설명한다.
- [ ] Calculator 또는 계산표를 완성했다.

## 다음 Chapter 예고

다음 Chapter에서는 Camera와 Lens를 하나의 Optical System으로 보고 Focal Length, Magnification, Working Distance, FOV, Object/Image Space, Depth of Field, Distortion의 관계를 학습한다.
