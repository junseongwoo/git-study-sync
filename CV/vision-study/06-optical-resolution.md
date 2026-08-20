# Chapter 6. Optical Resolution과 실제 검사 Resolution

> Phase 5 · 6일차 · 예상 학습 시간: 12~16시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Pixel Sampling과 실제 검출 능력의 차이
- 🔴 Nyquist Frequency와 Alias
- 🔴 Optical Resolution과 Lens MTF
- 🔴 PSF, Blur, Focus, Defocus
- 🔴 Motion Blur와 Exposure Time
- 🔴 Illumination Contrast, Noise, SNR/CNR
- 🔴 2 μm Defect와 3 μm Pixel Camera 사례 분석
- 🟠 Diffraction, Numerical Aperture(NA), F-number
- 🟠 Detection과 Measurement의 요구 조건 차이
- 🟠 Resolution Budget과 실제 Sample 검증

### 실무 목표

`Object Sampling = 3 μm/pixel`이라는 계산만으로 `3 μm Defect 검출 가능`이라고 결론 내리지 않는다. Sampling, Optical Transfer, Motion, Contrast/Noise, 알고리즘 조건을 분리해 검토하고, 검출률과 오검률로 최종 성능을 검증하는 절차를 설계한다.

---

## 2. 선수 지식

- [[05-fov-resolution|Chapter 5]]의 FOV/Sampling 계산
- `Object μm/pixel = Pixel Pitch/Magnification`
- 주기(Period)와 공간 주파수(Spatial Frequency)의 역수 관계
- 평균, 표준편차, Contrast의 기초

### 2.1 용어와 단위

| 용어 | 의미 | 대표 단위 |
|---|---|---|
| Sampling Pitch | 인접 Image Sample 간 Object 거리 | μm/pixel |
| Spatial Frequency | 길이당 밝기 패턴 반복 수 | lp/mm, cycles/mm |
| MTF | 공간 주파수별 Contrast 전달 비율 | 0~1 또는 % |
| PSF | 점 Object가 Image에 퍼지는 모양 | Pixel 또는 μm |
| SNR | Signal 크기 대비 Noise | 비율, dB |
| CNR | Defect와 Background 차이 대비 Noise | 비율 |

**Line Pair(lp)**는 밝은 선 하나와 어두운 선 하나의 한 쌍이다. `100 lp/mm`이면 한 주기의 길이는 `1/100 mm = 10 μm`이고 이상적으로 밝고 어두운 선 하나씩은 약 5 μm 폭이다.

---

## 3. 핵심 개념

### 3.1 검사 성능은 여러 단계의 곱이다

```text
Defect의 물리적 형상/반사 특성
        ↓ Illumination이 Contrast 생성
Lens/Optics가 공간 정보를 전달(MTF/PSF)
        ↓
Sensor가 공간과 밝기를 Sampling
        ↓ Exposure/Gain/Noise/ADC
Digital Image
        ↓ Preprocessing/Algorithm
Detection / Measurement / Judgement
```

어느 한 단계에서 정보가 사라지면 뒤 단계가 완전히 복구할 수 없다. Sharpness Filter는 이미 존재하는 Edge Contrast를 강조할 수 있지만 Optical Blur로 없어진 세부를 새로 만들지는 못한다.

### 3.2 Sampling Pitch와 Resolution

`5 μm/pixel`은 Object Space에서 Image Sample 중심 간격이 5 μm라는 뜻이다. 이는 다음과 같지 않다.

- 5 μm Defect를 항상 검출
- 5 μm 치수를 5 μm 정확도로 측정
- 1 Pixel보다 작은 Feature는 절대 영향이 없음

Sub-pixel Feature도 한 Pixel이 모으는 빛의 평균을 바꿀 수 있다. 하지만 Feature 위치, Fill Factor, PSF, Contrast와 Noise에 따라 신호가 달라져 안정성이 낮을 수 있다.

### 3.3 Nyquist Sampling

주기적인 신호를 Alias 없이 Sampling하려면 이상적으로 한 주기당 최소 2 Sample이 필요하다.

```text
Sensor Nyquist Frequency = 1 / (2 × Pixel Pitch)
```

3 μm Pixel은 `0.003 mm`이므로 Image Space Nyquist는:

```text
1 / (2 × 0.003 mm) = 166.67 cycles/mm ≈ 166.67 lp/mm
```

Object Space Sampling이 6 μm/pixel이면 Object Space Nyquist는:

```text
1 / (2 × 0.006 mm) = 83.33 lp/mm
```

> [!WARNING]
> Nyquist의 2 Sample 기준은 이상적인 주기 신호를 복원하기 위한 이론적 하한이다. 단일 Particle, Scratch, Edge의 안정적 검출·치수 측정에 “2 Pixel이면 충분하다”는 뜻이 아니다.

### 3.4 Alias

Sampling 가능한 주파수보다 높은 Detail은 사라지기만 하는 것이 아니라 낮은 주파수의 거짓 패턴으로 보일 수 있다.

```text
Fine periodic pattern + insufficient sampling
                  ↓
       Moiré / false spacing / unstable brightness
```

반복 회로 Pattern, Mesh, Display Pixel, Wafer Pattern 검사에서 특히 주의한다. Lens Blur나 Optical Low-pass 특성이 일부 고주파를 줄이지만 검사 Detail도 함께 약해질 수 있다.

### 3.5 MTF(Modulation Transfer Function)

Object Pattern의 Contrast:

```text
Contrast = (I_max - I_min) / (I_max + I_min)
```

MTF는 특정 공간 주파수에서 Image Contrast가 Object Contrast 대비 얼마나 남는지 나타낸다.

```text
MTF(f) = Image Contrast(f) / Object Contrast(f)
```

예를 들어 Object Contrast가 0.8이고 광학계 MTF가 0.25라면 이상적인 Image Contrast는 약 `0.8×0.25=0.2`다. Sensor와 Noise를 거치면 실제 검출 가능한 Contrast는 더 낮아질 수 있다.

Lens의 MTF Chart를 볼 때 확인할 항목:

- 공간 주파수(lp/mm)
- Image Center와 Corner 위치
- Sagittal/Tangential 방향
- 사용 F-number와 파장
- 대상 Sensor Size와 Pixel Pitch
- Object-side인지 Image-side인지

### 3.6 Image Space와 Object Space 주파수

배율 `M`에서 Object의 길이 `T_o`는 Image에서 `T_i=M×T_o`가 된다. 따라서:

```text
Image-space frequency = Object-space frequency / M
Object-space frequency = M × Image-space frequency
```

0.5× Lens에서 Object Pattern이 50 lp/mm라면 Image Space에서는 `50/0.5=100 lp/mm`가 필요하다. Lens MTF Chart가 Image-side 기준이라면 100 lp/mm 성능을 확인한다.

### 3.7 PSF와 Blur

**PSF(Point Spread Function)**는 이상적인 점이 Image에서 얼마나 퍼지는지를 나타낸다. 실제 Image는 Object Detail이 PSF와 Convolution된 결과로 볼 수 있다.

Blur 원인:

- Lens 수차와 낮은 MTF
- Defocus
- Diffraction
- Motion Blur
- 진동
- Sensor Pixel Aperture
- 보호 Glass 또는 오염

서로 다른 Blur는 방향과 형태가 다르다. Motion Blur는 이동 방향으로 길어지고, Defocus는 대체로 여러 방향으로 퍼진다.

### 3.8 Focus와 Defocus

Focus가 벗어나면 Edge Transition 폭이 넓어지고 Gradient Peak가 낮아진다.

```text
In focus:    0 0 0 10 240 255 255
Defocused:   0 5 25 80 160 225 250
```

Threshold 위치와 Edge 측정값도 변할 수 있다. 선명도 Score 하나만 보지 말고 FOV 전체 Focus Map, 제품 높이 편차, Lens Tilt와 DOF를 확인한다.

### 3.9 Diffraction

빛의 파동 특성 때문에 완벽한 Lens도 점을 무한히 작게 맺을 수 없다. Image Space Airy Disk의 첫 번째 영점 지름 근사:

```text
Airy Diameter ≈ 2.44 × wavelength × F-number
```

파장 `λ=0.55 μm`, `F/8`이면:

```text
2.44 × 0.55 × 8 ≈ 10.74 μm
```

3 μm Pixel 기준 약 `3.58 Pixel` 지름이다. 이 값은 회절 크기 비교용이며 실제 Lens MTF, 파장 대역, 유효 F-number, 배율과 Pupil Magnification을 추가 고려해야 한다.

Object Space의 회절 한계를 직관적으로 볼 때 사용하는 Rayleigh 근사:

```text
d ≈ 0.61 × wavelength / NA
```

`λ=0.55 μm`, `NA=0.10`이면 약 `3.36 μm`, `NA=0.25`이면 약 `1.34 μm`다. 실제 산업 영상의 검출/측정 한계와 동일한 숫자로 사용하지 말고 광학 설계 비교용으로 본다.

### 3.10 Motion Blur

Exposure 중 Object Image가 이동한 거리는 Blur가 된다.

```text
Object Motion(μm) = Velocity(mm/s) × Exposure(ms)
Motion Blur(pixel) = Object Motion(μm) / Object Sampling(μm/pixel)
```

수치상 `mm/s × ms = μm`이므로 단위 변환이 간단하지만 단위를 반드시 적는다.

50 mm/s, 2 ms Exposure, 5 μm/pixel이면:

```text
Motion = 50 × 2 = 100 μm
Blur = 100 / 5 = 20 pixel
```

정밀 Edge 검사에서 허용 Blur를 0.5 Pixel로 정하면 허용 Exposure는 훨씬 짧아진다.

### 3.11 Illumination Contrast와 Noise

같은 크기의 Defect도 조명 방식에 따라 거의 보이지 않거나 강한 Contrast로 나타난다.

- Dark Field: Scratch/Edge 산란광 강조
- Bright Field: 반사율 및 평탄한 표면 차이
- Back Light: 외곽 Silhouette와 Hole
- Coaxial: 평탄 반사면의 얼룩/Pattern

단순 Contrast만 아니라 Noise 대비 차이를 본다. 두 영역의 평균과 표준편차를 이용한 간단한 CNR:

```text
CNR = |μ_defect - μ_background| / sqrt(σ_defect² + σ_background²)
```

CNR이 높을수록 단순 Threshold로 분리하기 쉽지만, 위치별 Background 변화와 구조 Pattern도 False Positive를 만들 수 있다.

### 3.12 Detection과 Measurement

- **Detection**: Feature가 존재하는가?
- **Localization**: 어디에 있는가?
- **Measurement**: 크기·거리·폭이 얼마인가?

Feature가 약하게 한두 Pixel 값에 영향을 주면 Detection은 가능할 수 있지만 정확한 Width Measurement는 불가능할 수 있다. 검사 요구사항에서 무엇을 보장해야 하는지 구분한다.

### 3.13 3 μm Camera로 2 μm Defect를 검사할 수 있는가?

정답은 **Pixel Size만으로 판단할 수 없다**다.

#### 1× 배율

```text
Object Sampling = 3 μm/pixel
2 μm Defect의 기하 점유 = 2/3 ≈ 0.67 pixel
```

Defect가 Pixel 평균값에 영향을 줄 수는 있지만 위치와 Contrast에 매우 민감하다. 안정적인 형상 측정은 어렵다.

#### 2× 배율

```text
Object Sampling = 1.5 μm/pixel
2 μm Defect의 기하 점유 ≈ 1.33 pixel
```

Sampling은 개선되지만 여전히 Lens가 Object의 2 μm Detail Contrast를 전달하는지, 조명이 Defect를 강조하는지, Noise보다 신호가 큰지 확인해야 한다.

#### 내부 기준이 4 Pixel이라면

```text
Required Sampling = 2 μm / 4 = 0.5 μm/pixel
Required Magnification = 3 μm / 0.5 μm = 6×
```

6×에서는 FOV와 DOF가 크게 줄고 높은 Object-side Optical Resolution이 필요하다. 일반적인 구성으로 가능한지 단정하지 말고 Microscope Objective/고NA 광학, 진동, Focus, 조명, Cycle Time을 함께 검토해야 한다.

#### 올바른 판단 절차

1. Defect를 Detection할지 정확히 측정할지 정의한다.
2. FOV와 Sampling으로 Camera Pixel Count/배율을 계산한다.
3. Lens의 Object/Image-side MTF와 NA를 확인한다.
4. 조명으로 Defect CNR을 확보한다.
5. Exposure와 Motion Blur Budget을 정한다.
6. 실제 Defect Sample에서 위치·방향·Lot 변화를 포함해 검출률/오검률을 측정한다.

---

## 4. 그림으로 이해하기

### 4.1 Resolution Chain

```text
2 μm Defect
    │ illumination contrast
    ▼
Optical Image ── MTF / PSF / Defocus / Diffraction
    │
    ▼
Sensor Sampling ── μm/pixel / Nyquist / Pixel Aperture
    │
    ▼
Digital Signal ── Exposure / Gain / Noise / Bit Depth
    │
    ▼
Algorithm ── Filter / Threshold / Edge / Blob
    │
    ▼
Detection Rate + False Positive Rate + Measurement Error
```

### 4.2 Sampling은 촘촘하지만 Blur가 큰 경우

```text
Fine Pixel Grid: |.|.|.|.|.|.|.|.|.|.|.|.|.|.|.|.|.|.|.| 
Optical Edge:          ________/~~~~~~~~\________

Pixel 수가 많아도 광학 Edge가 넓게 퍼지면 Detail Contrast가 낮다.
```

### 4.3 Motion Blur

```text
Exposure start     movement direction →      Exposure end
      ●────────────────────────────────────────●
      └──────────── accumulated streak ────────┘
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### Scratch 검사

Scratch 폭만으로 Camera를 선택하지 않는다. Dark Field가 Scratch 산란광을 충분히 만들고, Scratch 방향별 Contrast와 Lens MTF, Focus, Motion Blur를 확인한다.

### Edge 치수 측정

Edge가 검출된다는 사실과 치수 정확도는 다르다. Edge Spread, Threshold/Gradient 위치 Bias, Distortion, Calibration 및 반복 정밀도를 Gauge로 검증한다.

### 이동 중 촬영

Line Scan 또는 Area Scan의 On-the-fly 촬영에서는 Exposure 동안의 이동량을 Pixel Blur Budget과 비교한다. 광량을 늘려 Exposure를 줄이거나 Strobe를 사용한다.

### Focus 유지보수

장비 온도, Lens Mount, Stage 높이, 제품 Warpage로 Focus가 변할 수 있다. Golden Target의 Edge Width/Sharpness와 위치별 Focus Map을 예방보전 지표로 사용할 수 있다.

### Camera 고해상도 Upgrade

기존 Lens가 새 Pixel Pitch에서 필요한 MTF를 전달하는지 확인한다. 처리량, Exposure, Noise, Sensor 크기와 Lens Image Circle도 함께 검토한다.

---

## 6. 숫자로 이해하기

### 예제 1: Sensor와 Object Space Nyquist

Camera Pixel Pitch `3 μm`, Magnification `0.5×`:

```text
Image-space Nyquist
= 1 / (2 × 0.003 mm)
= 166.67 lp/mm

Object Sampling
= 3 / 0.5 = 6 μm/pixel = 0.006 mm/pixel

Object-space Nyquist
= 1 / (2 × 0.006 mm)
= 83.33 lp/mm
```

주파수 변환으로도:

```text
Object Nyquist = M × Image Nyquist
               = 0.5 × 166.67
               = 83.33 lp/mm
```

### 예제 2: MTF와 Contrast

Object Pattern의 `I_max=180`, `I_min=20`이라면:

```text
Object Contrast = (180-20)/(180+20) = 0.8
```

해당 주파수에서 Optical MTF가 0.25라면 단순 선형 모델의 Image Contrast:

```text
0.8 × 0.25 = 0.20
```

실제 Sensor Noise와 Processing을 포함하기 전의 1차 예상이다.

### 예제 3: Motion Blur Budget

조건:

- Stage Velocity = 50 mm/s
- Sampling = 5 μm/pixel
- 허용 Motion Blur = 0.5 pixel

허용 Object 이동:

```text
5 μm/pixel × 0.5 pixel = 2.5 μm
```

최대 Exposure:

```text
2.5 μm / 50,000 μm/s = 0.00005 s
= 50 μs = 0.05 ms
```

### 예제 4: Airy Diameter 비교

`λ=0.55 μm`일 때:

```text
F/4:  2.44 × 0.55 × 4  = 5.368 μm
F/8:  2.44 × 0.55 × 8  = 10.736 μm
F/16: 2.44 × 0.55 × 16 = 21.472 μm
```

3 μm Pixel 기준 Image Space 지름은 약 1.79/3.58/7.16 Pixel이다. 조리개를 조이면 DOF가 증가하지만 Diffraction Blur가 커지는 Trade-off를 보여준다.

### 예제 5: CNR

```text
Defect:     mean=120, stddev=5
Background: mean=100, stddev=4

CNR = |120-100| / sqrt(5²+4²)
    = 20 / sqrt(41)
    ≈ 3.12
```

다른 조명에서 평균 차이가 10으로 줄고 Noise가 같다면 CNR은 약 1.56으로 절반이 된다.

---

## 7. C++ 구현

### 검출 가능성 1차 계산기

```cpp
#include <cmath>
#include <stdexcept>

struct ResolutionInput final {
    double sensorPixelPitchUm{};
    double magnification{};
    double featureSizeUm{};
    double velocityMmPerSecond{};
    double exposureMs{};
    double wavelengthUm{};
    double fNumber{};
};

struct ResolutionEstimate final {
    double objectUmPerPixel{};
    double featurePixels{};
    double imageNyquistLpPerMm{};
    double objectNyquistLpPerMm{};
    double motionUm{};
    double motionBlurPixels{};
    double airyDiameterImageUm{};
    double airyDiameterImagePixels{};
};

[[nodiscard]] bool IsPositiveFinite(const double value) noexcept
{
    return std::isfinite(value) && value > 0.0;
}

[[nodiscard]] ResolutionEstimate EstimateResolution(
    const ResolutionInput& input)
{
    if (!IsPositiveFinite(input.sensorPixelPitchUm) ||
        !IsPositiveFinite(input.magnification) ||
        !IsPositiveFinite(input.featureSizeUm) ||
        !std::isfinite(input.velocityMmPerSecond) ||
        input.velocityMmPerSecond < 0.0 ||
        !std::isfinite(input.exposureMs) || input.exposureMs < 0.0 ||
        !IsPositiveFinite(input.wavelengthUm) ||
        !IsPositiveFinite(input.fNumber)) {
        throw std::invalid_argument{"Invalid resolution parameter"};
    }

    const double objectUmPerPixel =
        input.sensorPixelPitchUm / input.magnification;
    const double pixelPitchMm = input.sensorPixelPitchUm / 1000.0;
    const double imageNyquist = 1.0 / (2.0 * pixelPitchMm);
    const double objectNyquist = input.magnification * imageNyquist;

    // Numerically, mm/s * ms equals um.
    const double motionUm =
        input.velocityMmPerSecond * input.exposureMs;
    const double airyDiameterUm =
        2.44 * input.wavelengthUm * input.fNumber;

    return {
        objectUmPerPixel,
        input.featureSizeUm / objectUmPerPixel,
        imageNyquist,
        objectNyquist,
        motionUm,
        motionUm / objectUmPerPixel,
        airyDiameterUm,
        airyDiameterUm / input.sensorPixelPitchUm
    };
}

[[nodiscard]] double CalculateCnr(
    const double defectMean,
    const double backgroundMean,
    const double defectStdDev,
    const double backgroundStdDev)
{
    if (!std::isfinite(defectMean) || !std::isfinite(backgroundMean) ||
        !std::isfinite(defectStdDev) || !std::isfinite(backgroundStdDev) ||
        defectStdDev < 0.0 || backgroundStdDev < 0.0) {
        throw std::invalid_argument{"Invalid CNR parameter"};
    }

    const double noise = std::hypot(defectStdDev, backgroundStdDev);
    if (noise == 0.0) {
        throw std::invalid_argument{"CNR is undefined for zero noise"};
    }
    return std::abs(defectMean - backgroundMean) / noise;
}
```

### Unit Test

```cpp
#include <cassert>
#include <cmath>

[[nodiscard]] bool NearlyEqual(
    const double lhs,
    const double rhs,
    const double tolerance = 1e-6)
{
    return std::abs(lhs - rhs) <= tolerance;
}

void TestNyquistAndMotionBlur()
{
    const ResolutionInput input{
        3.0, 0.5, 24.0, 50.0, 2.0, 0.55, 8.0
    };
    const auto result = EstimateResolution(input);

    assert(NearlyEqual(result.objectUmPerPixel, 6.0));
    assert(NearlyEqual(result.featurePixels, 4.0));
    assert(NearlyEqual(result.imageNyquistLpPerMm, 166.666667));
    assert(NearlyEqual(result.objectNyquistLpPerMm, 83.333333));
    assert(NearlyEqual(result.motionUm, 100.0));
    assert(NearlyEqual(result.motionBlurPixels, 16.666667));
    assert(NearlyEqual(result.airyDiameterImageUm, 10.736));
}

void TestCnr()
{
    const double cnr = CalculateCnr(120.0, 100.0, 5.0, 4.0);
    assert(std::abs(cnr - 3.123475) < 1e-6);
}
```

### 코드에서 봐야 할 점

1. Sampling, Nyquist, Motion Blur, Diffraction 비교값을 서로 분리한다.
2. `mm/s × ms = μm` 관계를 주석과 변수명으로 명시한다.
3. `featurePixels`를 최종 합격 판정으로 사용하지 않는다.
4. Airy Diameter는 Image Space 비교용 근사값이다.
5. 실제 합격 판정에는 Lens MTF Data, CNR, Focus/Distortion 및 Sample 검증 결과가 추가로 필요하다.

> [!CAUTION]
> 이 계산기는 광학계의 검출 가능성을 보증하지 않는다. 불가능하거나 위험한 조건을 조기에 찾는 1차 Engineering Tool이다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: Pixel 수는 충분하지만 Lens MTF 부족

- 증상: 작은 Pattern이 여러 Pixel에 걸려도 Contrast가 낮음
- 대응: 사용 주파수·F-number·Image Height에서 MTF 확인, 실제 Target 비교

### 문제 2: FOV 중앙만 Focus가 맞음

- 증상: 모서리 Match Score와 Edge Width 악화
- 원인: Lens Tilt, Field Curvature, Sensor Tilt
- 대응: FOV Focus Map, Mount 평행도, Corner MTF/Calibration 점검

### 문제 3: Exposure가 길어 Motion Blur 발생

- 증상: 이동 방향 Edge가 퍼지고 치수 Bias 증가
- 대응: Strobe/광량 증가, Exposure 단축, Stage 정지 촬영, 진동 억제

### 문제 4: 조리개를 조여 DOF만 확보

- 증상: Exposure 증가 또는 Diffraction으로 작은 Defect Contrast 저하
- 대응: DOF·Diffraction·광량을 함께 최적화

### 문제 5: 조명 변화로 CNR 저하

- 증상: Threshold 안정 구간이 사라지고 False Positive 증가
- 대응: 조명 Geometry, 전류/온도 안정화, Exposure Monitor, Adaptive 방법 검토

### 문제 6: Resize/Sharpen Image로 성능 평가

- 증상: Review에서는 선명해 보이나 원본 검출 성능과 불일치
- 대응: Raw/원본 기준 평가, Display Processing 분리

### 문제 7: Golden Sample만으로 검증

- 증상: 실제 Lot, 방향, 위치 변화에서 검출률 하락
- 대응: 정상/불량 Population, 경계 Defect, 위치·방향·높이·온도 변화 포함

---

## 9. 흔한 오해

1. **“1 μm/pixel이면 1 μm Resolution이다.”**  
   Sampling Pitch일 뿐 Optical Resolution과 검출률을 포함하지 않는다.

2. **“Nyquist이므로 2 Pixel이면 Defect를 안정 검출한다.”**  
   2 Sample 기준은 이상적인 주기 신호의 이론적 하한이다.

3. **“Lens MTF가 높으면 Camera는 상관없다.”**  
   Sensor Sampling, Noise, Pixel Aperture와 Exposure가 함께 작동한다.

4. **“Sub-pixel Defect는 절대 보이지 않는다.”**  
   Pixel 평균을 바꿀 수 있지만 위치·Contrast 의존성이 커 안정성 검증이 필요하다.

5. **“조리개를 조이면 Focus 문제를 모두 해결한다.”**  
   Diffraction과 광량 저하, Motion Blur가 증가할 수 있다.

6. **“검출되면 정확히 측정할 수도 있다.”**  
   Detection, Localization, Measurement는 요구 Sampling과 오차 예산이 다르다.

7. **“후처리 Sharpening으로 Optical Blur를 복구할 수 있다.”**  
   일부 Contrast를 강조할 수 있지만 소실된 정보와 불확실성을 없애지 못한다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. 3 μm Pixel Camera로 2 μm Defect를 검사할 수 있나요?

**초보자가 이해할 수 있는 답변**  
Pixel Size만으로는 알 수 없습니다. Lens 배율과 선명도, 조명이 만드는 Contrast, Noise와 흔들림을 함께 확인해야 합니다.

**실무자 답변**  
먼저 배율을 적용해 Object μm/pixel과 Feature Pixel 수를 계산한다. 이후 해당 Object 주파수의 Lens MTF/NA, Focus, Illumination CNR, Sensor Noise, Motion Blur, Defect 위치·방향을 검토하고 목표 Detection Rate와 False Positive Rate로 Sample Test한다.

**면접용 30초 답변**  
“3 μm는 Sensor Pixel Pitch이므로 그것만으로 판단할 수 없습니다. 배율을 적용한 Object Sampling, Lens MTF와 Focus, 조명 CNR, Noise와 Motion Blur를 확인해야 합니다. 최종 가능 여부는 실제 2 μm Defect Sample의 검출률과 오검률로 결정합니다.”

### Q2. Pixel Resolution과 Optical Resolution의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Pixel Resolution은 Image를 얼마나 촘촘히 나누는지이고 Optical Resolution은 Lens가 실제 세부를 얼마나 선명하게 전달하는지입니다.

**실무자 답변**  
Object Sampling은 FOV/Pixel Count의 이산 간격이다. Optical Resolution은 MTF/PSF, NA, 파장, 수차와 Focus에 의해 제한된다. 전체 System Resolution은 Optical Transfer와 Sensor Sampling, SNR의 조합으로 평가한다.

**면접용 30초 답변**  
“Pixel Resolution은 μm/pixel로 표현하는 Sampling 간격이고 Optical Resolution은 Lens가 공간 주파수 Contrast를 전달하는 능력입니다. Sampling이 촘촘해도 Lens가 Blur하면 Detail은 없고, Lens가 좋아도 Sampling이 부족하면 Alias가 생깁니다.”

### Q3. Nyquist 기준을 검사에 어떻게 사용하나요?

**초보자가 이해할 수 있는 답변**  
한 주기 패턴을 표현하려면 이론적으로 최소 2 Pixel이 필요하다는 하한으로 사용합니다.

**실무자 답변**  
Sensor Nyquist `1/(2p)`와 Lens MTF 주파수를 비교해 Sampling 병목과 Alias Risk를 본다. 다만 단일 Defect Detection/Measurement에는 Contrast, PSF와 필요한 Pixel 수가 다르므로 Nyquist만으로 합격 판정하지 않는다.

**면접용 30초 답변**  
“Nyquist는 `1/(2×Sampling Pitch)`으로 이상적 주기 신호의 Alias-free 상한을 제공합니다. Lens MTF와 Sensor Sampling의 균형을 볼 때 사용하지만, 결함 검출에 2 Pixel이면 충분하다는 기준은 아니며 실제 CNR과 검출률을 추가 검증합니다.”

### Q4. Motion Blur를 어떻게 계산하고 줄이나요?

**초보자가 이해할 수 있는 답변**  
Exposure 동안 제품이 움직인 실제 거리를 μm/pixel로 나누면 Pixel Blur가 됩니다. Exposure를 줄이거나 제품을 멈추면 줄어듭니다.

**실무자 답변**  
`Blur pixel = velocity×exposure/object sampling`으로 1차 Budget을 계산한다. Strobe와 광량 증가, Exposure 단축, Trigger 동기화, Stage Settle, 진동 억제 및 이동 방향과 검사 Edge 방향을 함께 최적화한다.

**면접용 30초 답변**  
“Object 이동량은 수치상 `mm/s×ms=μm`이고 이를 μm/pixel로 나누면 Blur Pixel입니다. 허용 Blur에서 최대 Exposure를 역산한 뒤 Strobe, 조명 강화, Stage 정지 촬영과 Trigger 동기화로 맞춥니다.”

### Q5. 조리개를 조이면 어떤 Trade-off가 있나요?

**초보자가 이해할 수 있는 답변**  
DOF는 늘어나는 경향이 있지만 Image가 어두워지고 너무 조이면 Diffraction으로 Detail이 흐려질 수 있습니다.

**실무자 답변**  
F-number 증가로 수차와 Defocus 민감도가 줄 수 있지만 광량 감소로 Exposure/Gain이 증가하고 Diffraction MTF가 낮아진다. 유효 F-number와 Pixel Pitch, 목표 주파수에서 최적 Aperture를 실험한다.

**면접용 30초 답변**  
“조리개를 조이면 DOF는 증가하지만 광량이 줄어 Exposure나 Gain이 필요하고, 너무 조이면 Diffraction Blur가 커집니다. 따라서 Focus 범위만 보지 않고 목표 공간 주파수의 MTF와 Motion Blur까지 포함해 최적 F-number를 정합니다.”

### Q6. 검사 가능성을 어떻게 검증하나요?

**초보자가 이해할 수 있는 답변**  
계산 후 실제 정상·불량 Sample을 다양한 위치와 조건에서 촬영해 얼마나 잘 찾고 얼마나 자주 잘못 찾는지 확인합니다.

**실무자 답변**  
FOV/Sampling과 Optical Budget을 계산하고 MTF, Focus Map, CNR, Motion Blur를 계측한다. 경계 Defect와 정상 변동을 포함한 Dataset에서 Detection Rate, False Positive Rate, Repeatability, Gauge R&R 및 환경 변화 Robustness를 평가한다.

**면접용 30초 답변**  
“먼저 Sampling·MTF·CNR·Motion Budget으로 가능성을 선별하고, 실제 경계 Defect와 정상 Variation을 위치·방향·높이·속도별로 촬영합니다. 그 결과의 검출률, 오검률, 반복 정밀도와 측정 Bias가 요구 기준을 만족하는지 확인합니다.”

---

## 11. 실습 문제

### 실습 1: Nyquist와 MTF 연결

Camera Pixel Pitch `2.74 μm`, Lens 배율 `0.5×`에 대해:

1. Image/Object Space Nyquist를 계산한다.
2. Object 60 lp/mm Pattern이 Image Space에서 몇 lp/mm인지 계산한다.
3. Lens MTF Chart에서 어떤 주파수와 Image Height를 확인해야 하는지 적는다.

### 실습 2: Motion Blur 역산

다음 조건에서 허용 Exposure를 구한다.

- Sampling: 3.5 μm/pixel
- Stage 속도: 120 mm/s
- 허용 Blur: 0.3 pixel

계산 결과를 만족시키기 위한 조명/Trigger/기구 대안을 3개 제안한다.

### 실습 3: 2 μm Defect 검토표

다음 후보를 비교한다.

- Camera A: 3 μm Pixel, 1×
- Camera B: 3 μm Pixel, 2×
- Camera C: 2.2 μm Pixel, 4×

각 후보의 Sampling, 2 μm Feature Pixel 수, FOV Trade-off를 계산한다. 계산만으로 알 수 없는 MTF, NA, CNR, DOF, Motion 조건을 별도 열로 만든다.

### 실습 4: Blur 실험

Sharp Edge Image에 Gaussian Blur와 방향성 Motion Blur를 각각 적용한다.

- Edge Spread Width
- Sobel Gradient Peak
- Threshold Edge Position
- Canny 결과

Blur 크기별 변화를 기록하고 Detection과 Measurement 영향이 다른지 분석한다.

### Phase 5 미니 프로젝트: Resolution Budget Analyzer

```text
Feature Requirement
├── Size / Shape / Orientation
├── Detection or Measurement
└── Required Detection Rate
          ↓
Sampling / Nyquist
          ↓
Lens MTF / Diffraction / Focus
          ↓
Motion Blur / CNR / Noise
          ↓
Risk Report + Required Sample Tests
```

**필수 기능**

- Object μm/pixel과 Feature Pixel 계산
- Image/Object Nyquist 계산
- Motion Blur 및 허용 Exposure 역산
- Airy Diameter 비교값
- CNR 계산
- 계산만으로 합격을 반환하지 않고 `Need Optical Data`, `Need Sample Test` 상태 제공

---

## 12. Chapter 핵심 요약

- 🔴 μm/pixel은 Sampling Pitch이며 실제 검출 Resolution과 다르다.
- 🔴 Nyquist는 주기 신호의 이론적 하한이지 Defect 2 Pixel 보장 규칙이 아니다.
- 🔴 Lens MTF와 PSF는 작은 Detail의 Contrast와 Blur를 결정한다.
- 🔴 Sampling과 Optical Resolution 중 약한 쪽이 System Detail을 제한한다.
- 🔴 Focus, Defocus, Diffraction, Motion은 서로 다른 Blur를 만든다.
- 🔴 조명이 Defect Contrast를 만들고 Noise 대비 CNR이 검출 안정성을 좌우한다.
- 🔴 Detection 가능과 정확한 Measurement 가능을 구분한다.
- 🔴 3 μm Pixel Camera의 2 μm Defect 가능 여부는 Pixel Size만으로 판단할 수 없다.
- 🟠 조리개는 DOF, 광량, Diffraction의 Trade-off다.
- 🟠 최종 성능은 실제 정상/불량 Variation의 검출률·오검률·반복성으로 검증한다.

---

## 6일차 권장 학습 순서

- [ ] 40분: Sampling과 Optical Resolution 차이 설명
- [ ] 45분: Nyquist와 MTF 예제 계산
- [ ] 40분: PSF/Focus/Diffraction 정리
- [ ] 40분: Motion Blur와 최대 Exposure 역산
- [ ] 60~90분: C++ Resolution Analyzer 구현
- [ ] 60분: 2 μm Defect 후보 비교 실습
- [ ] 30분: 면접 Q1~Q6 30초 답변 연습

## 학습 완료 체크

- [ ] μm/pixel과 실제 Resolution 차이를 설명한다.
- [ ] Image/Object Space Nyquist를 계산한다.
- [ ] MTF와 PSF의 실무 의미를 설명한다.
- [ ] Motion Blur Pixel과 최대 Exposure를 계산한다.
- [ ] 조리개와 DOF/Diffraction Trade-off를 설명한다.
- [ ] 2 μm Defect 질문에 조건부로 답한다.
- [ ] Resolution Budget Analyzer를 설계하거나 구현했다.

## 다음 Chapter 예고

다음 Chapter에서는 Back/Ring/Coaxial/Dome/Dark Field/Bright Field 등 조명 Geometry가 어떤 특징의 Contrast를 만드는지 검사 알고리즘과 연결한다.
