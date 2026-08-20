# Chapter 4. Camera + Lens + Optical System

> Phase 3 · 4일차 · 예상 학습 시간: 12~16시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Camera, Sensor, Lens, Object, Image의 관계
- 🔴 Focal Length(초점거리)와 Magnification(배율)의 차이
- 🔴 Working Distance(WD), Object Distance, Image Distance 구분
- 🔴 Sensor Size, Magnification, FOV 관계
- 🔴 Object Space와 Image Space
- 🔴 Focus, Depth of Field(DOF), Defocus
- 🔴 Distortion과 치수·좌표 오차
- 🟠 F-number, Aperture, Diffraction, Exposure의 Trade-off
- 🟠 일반 Lens와 Telecentric Lens의 차이
- 🟠 Lens Resolution/MTF와 Sensor Sampling의 조합

### 실무 목표

검사 요구사항을 `FOV → 필요한 μm/pixel → Sensor/Lens 조합 → WD/DOF → 조명/Exposure → Calibration` 순서로 검토한다. “같은 Camera인데 Lens를 바꾸면 왜 검사 결과가 달라지는가?”를 FOV, Sampling, Contrast, Blur, Distortion 관점에서 설명한다.

---

## 2. 선수 지식

- [[03-camera-pixel|Chapter 3]]의 다음 관계식

```text
Sensor Size = Pixel Count × Pixel Pitch
FOV = Sensor Size ÷ Magnification
Object Space Pixel Size = Pixel Pitch ÷ Magnification
```

- 단위: `1 mm = 1,000 μm`
- 비율과 역수
- Lens 사양의 명목값과 장착 후 Calibration 값은 다를 수 있음

### 2.1 기호

| 기호 | 의미 | 단위 |
|---|---|---|
| `f` | Focal Length | mm |
| `u` | Object Distance(주평면 기준 이상 모델) | mm |
| `v` | Image Distance(주평면 기준 이상 모델) | mm |
| `M` | Magnification의 절댓값 `v/u` | × |
| `N` | F-number | 무차원 |
| `c` | 허용 Circle of Confusion | mm |

> [!WARNING]
> 실제 제품의 **Working Distance**는 보통 Lens의 기계적 전면 또는 제조사가 정한 기준면부터 Object까지의 거리다. Thin Lens 식의 `u`는 광학 주평면(Principal Plane) 기준이므로 두 값을 같은 것으로 취급하면 안 된다.

---

## 3. 핵심 개념

### 3.1 Camera만으로 Image가 만들어지지 않는다

```text
Illumination
     ↓
Object Surface ── 반사/투과된 빛 ──► Lens ──► Sensor ──► Digital Image
                                      │          │
                               FOV/Blur/DOF   Pixel/Noise
```

Camera Sensor는 도달한 빛을 Sampling한다. Lens는 Object의 어느 범위를 Sensor에 어떤 배율과 선명도로 맺을지 결정한다. 조명은 검사 특징이 Lens에 들어오는 Contrast를 만든다.

같은 Camera라도 Lens가 달라지면 다음이 바뀔 수 있다.

- FOV와 Object Space μm/pixel
- Working Distance와 장비 배치
- Optical Resolution과 Contrast
- DOF와 Focus 민감도
- Distortion과 위치·치수 오차
- Sensor 전체를 덮는 Image Circle
- 필요한 조명 배치와 Exposure

### 3.2 Object Space와 Image Space

- **Object Space**: 실제 검사 대상이 존재하는 공간. mm, μm 등 실제 단위를 사용한다.
- **Image Space**: Lens가 Sensor 위에 형성한 Optical Image 공간. Sensor mm 또는 Pixel 좌표로 표현한다.

```text
Object 10 mm  ── 0.5× Lens ──► Sensor Image 5 mm
Object  5 mm  ── 1.0× Lens ──► Sensor Image 5 mm
Object 2.5 mm ── 2.0× Lens ──► Sensor Image 5 mm
```

Sensor의 3 μm Pixel은 Image Space의 Sampling Pitch다. Object Space에서는 배율을 적용해 각각 6, 3, 1.5 μm/pixel이 된다.

### 3.3 Focal Length와 Magnification

**Focal Length(초점거리)**는 Lens의 광학적 특성으로, 무한대에 가까운 평행광을 맺는 기준 거리와 관련된다. **Magnification(배율)**은 특정 Object 거리와 Image 거리에서 Object 크기가 Sensor 위에 맺힌 크기의 비율이다.

```text
Magnification = Image Size / Object Size
```

따라서 `50 mm Lens = 0.5× Lens`가 아니다. 같은 Focal Length도 Working Distance와 Extension/Focus 조건에 따라 배율이 달라진다. Fixed Magnification Telecentric Lens처럼 특정 WD에서 배율을 사양으로 제공하는 제품도 있다.

#### 이상적인 Thin Lens 모델

```text
1/f = 1/u + 1/v
M = |v/u|
```

배율 `M`이 주어지면 이상 모델에서:

```text
u = f × (1 + 1/M)
v = f × (1 + M)
```

이 식은 개념과 1차 추정에 유용하지만 실제 Compound Lens의 주평면 위치, Internal Focusing, Mount Flange Distance, 제조사 WD 정의를 반영하지 않는다. Lens 선정은 제조사 Datasheet와 Lens Calculator를 우선한다.

### 3.4 Working Distance

Working Distance는 Lens와 Object 사이에 실제로 확보되는 작업 거리다. 다음을 함께 결정한다.

- Stage, Robot, Nozzle, Cover와의 기계 간섭
- Ring/Coaxial/Dome/Back Light를 설치할 공간
- 진동과 높이 편차에 대한 민감도
- 안전 및 유지보수 접근성
- 원하는 FOV와 배율을 만들 수 있는 Lens 조합

WD를 임의로 바꾸고 Focus만 다시 맞추면 배율과 FOV가 달라질 수 있으므로 Calibration을 재검토해야 한다.

### 3.5 FOV와 Sensor Coverage

고정 배율 Lens의 1차 계산:

```text
Horizontal FOV = Sensor Width / M
Vertical FOV   = Sensor Height / M
```

Lens의 **Image Circle**이 Sensor 대각선을 충분히 덮어야 한다. 작으면 모서리가 어두워지는 Vignetting 또는 심한 화질 저하가 생길 수 있다.

```text
Sensor Diagonal = sqrt(Width² + Height²)
```

Sensor Format의 “1/2 inch” 같은 관용 표기는 실제 Sensor 대각선과 같지 않을 수 있으므로 mm 단위 Active Area를 확인한다.

### 3.6 Aperture와 F-number

```text
F-number N = Focal Length / Entrance Pupil Diameter
```

- 작은 F-number(예: F/2.8): 더 많은 빛, 짧은 Exposure 가능, DOF가 얕을 수 있음
- 큰 F-number(예: F/8): 빛 감소, DOF 증가 경향, 너무 조이면 Diffraction 증가

조리개를 조이면 무조건 선명해지는 것이 아니다. 수차가 줄다가 Diffraction이 증가하는 최적 구간이 있으며, Sensor Pixel Pitch와 요구 MTF에서 실제 Test해야 한다.

### 3.7 Focus와 Depth of Field

**Focus**는 관심 Plane의 Detail이 Sensor에 가장 선명하게 맺히는 상태다. **Depth of Field(DOF)**는 허용 가능한 선명도로 보이는 Object 방향 깊이 범위다.

DOF는 일반적으로 다음 경향을 가진다.

- F-number 증가 → DOF 증가 경향
- Magnification 증가 → DOF 급격히 감소
- 허용 Blur 기준이 느슨함 → DOF 증가
- Object 높이 편차가 큼 → 더 큰 DOF 필요

Macro 영역에서 사용하는 대칭 근사식 중 하나:

```text
Total DOF ≈ 2 × N × c × (1 + M) / M²
```

이는 근사적 비교용이다. `c` 선택, Pupil Magnification, 비대칭 전후 DOF, Diffraction과 Lens 설계를 생략하므로 최종 사양은 제조사 DOF 자료와 실제 Target으로 검증한다.

### 3.8 Distortion

Distortion은 Object의 위치가 이상적인 선형 투영 위치와 다르게 맺히는 기하 오차다.

- **Barrel Distortion**: 직선이 바깥쪽으로 볼록하게 휘어 보임
- **Pincushion Distortion**: 직선이 안쪽으로 당겨진 것처럼 보임
- **Mustache/Wave Distortion**: 위치에 따라 복합 형태

Distortion은 Blur와 다르다. Edge가 선명해도 위치가 틀릴 수 있다. 치수·위치 검사에서는 Lens 사양의 Distortion 값뿐 아니라 Working Distance, Focus, 실제 FOV에서 Grid Calibration Residual을 확인한다.

### 3.9 Perspective Error와 Telecentric Lens

일반 Lens에서는 Object가 Lens에 가까워지면 더 크게 보인다. 높이 편차가 있는 부품 치수 검사에서 배율 오차가 발생한다.

**Object-side Telecentric Lens**는 일정 범위 내에서 Object 거리 변화에 따른 배율 변화를 줄이고 Perspective를 억제한다.

장점:

- 높이 변화에 따른 치수 변화 감소
- 원통/단차 부품의 가장자리 관찰 안정성
- 낮은 Distortion 제품을 통한 정밀 측정

Trade-off:

- 크고 비싸며 무거울 수 있음
- 제한된 FOV, WD, Telecentric Range
- 큰 Sensor/FOV에서 Lens 직경 증가
- Telecentric Lens도 Calibration과 Focus 검증이 필요

### 3.10 Optical Resolution과 MTF

Lens Resolution은 단순히 “몇 μm까지 보인다” 한 숫자로 끝나지 않는다. **MTF(Modulation Transfer Function)**는 공간 주파수별 Contrast 전달 능력을 나타낸다.

```text
Object Detail
   └─ Lens가 Contrast를 얼마나 전달하는가?  → MTF
       └─ Sensor가 얼마나 촘촘히 Sampling하는가? → μm/pixel
           └─ Noise/조명/알고리즘이 구분 가능한가? → 실제 검사 성능
```

높은 해상도 Camera를 저해상도 Lens에 연결하면 Pixel 수만 늘고 실제 Detail은 Blur될 수 있다. 반대로 좋은 Lens라도 Object Sampling이 너무 거칠면 Alias가 발생한다.

---

## 4. 그림으로 이해하기

### 4.1 Optical System

```text
Object Space                         Image Space

Object        WD        Lens         Sensor
┌─────┐ ◄────────────►  )(       ┌──────────────┐
│ FOV │ ───────────────►)(──────►│ Pixel Grid   │
└─────┘                  │        └──────────────┘
  mm, μm              focal length   sensor mm, pixel

Object FOV / Sensor Size = 1 / Magnification
```

### 4.2 Focus와 DOF

```text
            acceptable DOF
        ◄──────────────────►
Object  [blur] [acceptable] [BEST FOCUS] [acceptable] [blur]
                             ▲
                         Focus Plane
```

### 4.3 일반 Lens와 Telecentric Lens

```text
General Lens                    Object-side Telecentric

   \  |  /                         |  |  |
    \ | /                          |  |  |
     \|/                           |  |  |
     Lens                          Lens

높이 변화 → 배율 변화             지정 범위에서 배율 변화 억제
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### 치수 검사

높이가 ±0.5 mm 달라지는 부품의 직경을 일반 Lens로 측정하면 Focus뿐 아니라 Perspective Magnification도 달라질 수 있다. 공차가 작다면 Telecentric Lens, 제품 높이 고정, Autofocus 또는 높이별 Calibration을 검토한다.

### 표면 Defect 검사

Lens MTF가 낮거나 Defocus가 있으면 Scratch의 Contrast가 줄어 Threshold/Edge 결과가 불안정해진다. Camera Pixel 수를 늘리기 전에 Focus Map과 조명 조건을 확인한다.

### 장비 기구 설계

원하는 FOV만 보고 Lens를 선택했는데 WD에 조명을 설치할 공간이 없을 수 있다. Optics, Lighting, Mechanical Layout을 함께 검토해야 한다.

### Multi-Camera Matching

같은 Model Lens라도 장착 높이와 Focus, 조리개가 다르면 FOV/밝기/MTF가 달라진다. Camera별 Calibration과 Golden Image 통계를 관리한다.

### Align

FOV 가장자리에서 Distortion이 크면 Pattern 위치와 회전 추정에 Bias가 생긴다. 기준 Pattern 위치를 고정하거나 Distortion Correction 후 Align하고 Calibration Residual을 확인한다.

---

## 6. 숫자로 이해하기

### 예제 1: Sensor와 배율로 FOV 계산

조건:

- Camera: 2448×2048
- Pixel Pitch: 3.45 μm
- Lens Magnification: 0.5×

Sensor Size:

```text
Width  = 2448 × 3.45 μm = 8445.6 μm = 8.4456 mm
Height = 2048 × 3.45 μm = 7065.6 μm = 7.0656 mm
```

FOV:

```text
FOV Width  = 8.4456 / 0.5 = 16.8912 mm
FOV Height = 7.0656 / 0.5 = 14.1312 mm
```

Object Sampling:

```text
3.45 μm / 0.5 = 6.9 μm/pixel
```

교차 검산:

```text
16.8912 mm / 2448 pixel = 0.0069 mm/pixel = 6.9 μm/pixel
```

### 예제 2: Thin Lens 개념 계산

이상적인 Thin Lens에서:

- Focal Length `f = 50 mm`
- Magnification `M = 0.1×`

```text
u = f × (1 + 1/M)
  = 50 × (1 + 10)
  = 550 mm

v = f × (1 + M)
  = 50 × 1.1
  = 55 mm
```

검산:

```text
1/50 = 1/550 + 1/55 = 0.001818... + 0.018181... = 0.02
M = v/u = 55/550 = 0.1
```

`u=550 mm`는 Lens 주평면 기준 이상값이지 Datasheet의 Mechanical WD와 같다고 단정할 수 없다.

### 예제 3: DOF 경향 비교

근사 조건:

- `N = 8`
- 허용 Circle of Confusion `c = 0.01 mm`

`M=0.5×`:

```text
DOF ≈ 2 × 8 × 0.01 × (1 + 0.5) / 0.5²
    = 0.96 mm
```

`M=1×`:

```text
DOF ≈ 2 × 8 × 0.01 × (1 + 1) / 1²
    = 0.32 mm
```

다른 조건이 같다면 배율 증가로 DOF가 크게 감소한다. 이 값은 비교용 근사이며 Lens Datasheet와 실제 Target Test로 확정한다.

### 예제 4: Sensor 대각선과 Image Circle

Sensor 크기가 `8.4456×7.0656 mm`라면:

```text
Diagonal = sqrt(8.4456² + 7.0656²)
         ≈ 11.01 mm
```

Lens의 유효 Image Circle은 최소한 이 대각선을 덮어야 하며, 모서리 MTF와 Vignetting도 별도로 확인한다.

---

## 7. C++ 구현

### Optical System 1차 계산기

```cpp
#include <cmath>
#include <cstddef>
#include <stdexcept>

struct SensorSpec final {
    std::size_t widthPixels{};
    std::size_t heightPixels{};
    double pixelPitchUm{};
};

struct OpticalResult final {
    double sensorWidthMm{};
    double sensorHeightMm{};
    double sensorDiagonalMm{};
    double fovWidthMm{};
    double fovHeightMm{};
    double objectUmPerPixel{};
};

struct ThinLensResult final {
    double objectDistanceMm{}; // principal-plane based ideal value
    double imageDistanceMm{};  // principal-plane based ideal value
};

[[nodiscard]] bool IsPositiveFinite(const double value) noexcept
{
    return std::isfinite(value) && value > 0.0;
}

[[nodiscard]] OpticalResult CalculateOpticalSystem(
    const SensorSpec& sensor,
    const double magnification)
{
    if (sensor.widthPixels == 0 || sensor.heightPixels == 0 ||
        !IsPositiveFinite(sensor.pixelPitchUm) ||
        !IsPositiveFinite(magnification)) {
        throw std::invalid_argument{"Invalid sensor or magnification"};
    }

    constexpr double umPerMm = 1000.0;
    const double widthMm = static_cast<double>(sensor.widthPixels) *
                           sensor.pixelPitchUm / umPerMm;
    const double heightMm = static_cast<double>(sensor.heightPixels) *
                            sensor.pixelPitchUm / umPerMm;

    return {
        widthMm,
        heightMm,
        std::hypot(widthMm, heightMm),
        widthMm / magnification,
        heightMm / magnification,
        sensor.pixelPitchUm / magnification
    };
}

[[nodiscard]] ThinLensResult CalculateIdealThinLens(
    const double focalLengthMm,
    const double magnification)
{
    if (!IsPositiveFinite(focalLengthMm) ||
        !IsPositiveFinite(magnification)) {
        throw std::invalid_argument{"Invalid focal length or magnification"};
    }

    return {
        focalLengthMm * (1.0 + 1.0 / magnification),
        focalLengthMm * (1.0 + magnification)
    };
}

[[nodiscard]] double CalculateApproximateMacroDofMm(
    const double fNumber,
    const double circleOfConfusionMm,
    const double magnification)
{
    if (!IsPositiveFinite(fNumber) ||
        !IsPositiveFinite(circleOfConfusionMm) ||
        !IsPositiveFinite(magnification)) {
        throw std::invalid_argument{"Invalid DOF parameter"};
    }

    return 2.0 * fNumber * circleOfConfusionMm *
           (1.0 + magnification) /
           (magnification * magnification);
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

void TestHalfMagnificationFov()
{
    const auto result = CalculateOpticalSystem({2448, 2048, 3.45}, 0.5);
    assert(NearlyEqual(result.sensorWidthMm, 8.4456));
    assert(NearlyEqual(result.sensorHeightMm, 7.0656));
    assert(NearlyEqual(result.fovWidthMm, 16.8912));
    assert(NearlyEqual(result.fovHeightMm, 14.1312));
    assert(NearlyEqual(result.objectUmPerPixel, 6.9));
}

void TestIdealThinLens()
{
    const auto result = CalculateIdealThinLens(50.0, 0.1);
    assert(NearlyEqual(result.objectDistanceMm, 550.0));
    assert(NearlyEqual(result.imageDistanceMm, 55.0));
}

void TestDofTrend()
{
    const double dofAtHalfX = CalculateApproximateMacroDofMm(8.0, 0.01, 0.5);
    const double dofAtOneX = CalculateApproximateMacroDofMm(8.0, 0.01, 1.0);
    assert(NearlyEqual(dofAtHalfX, 0.96));
    assert(NearlyEqual(dofAtOneX, 0.32));
    assert(dofAtOneX < dofAtHalfX);
}
```

### 코드에서 봐야 할 점

1. 실제 Camera/Lens 선정 계산과 Thin Lens 교육용 계산을 함수로 분리했다.
2. `std::hypot`으로 Sensor 대각선을 계산한다.
3. 단위가 변수명에 포함되어 μm/mm 혼용을 줄인다.
4. NaN, Infinity, 0, 음수 입력을 거부한다.
5. DOF 함수 이름에 `ApproximateMacro`를 넣어 결과의 한계를 드러낸다.
6. 제품 코드에서는 Lens Datasheet 값과 실측 Calibration 결과를 별도 구조체로 관리한다.

> [!CAUTION]
> Thin Lens와 DOF 함수는 교육 및 1차 비교용이다. 이 계산값만으로 Lens를 구매하거나 장비 공차를 확정하지 않는다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: Sensor보다 작은 Image Circle

- 증상: 모서리 어두움, 가장자리 Resolution 저하
- 대응: Sensor 대각선 Coverage와 Corner MTF 확인

### 문제 2: WD 변경 후 기존 Calibration 사용

- 증상: 치수 Scale과 Align 보정량이 달라짐
- 대응: 광학/기구 변경을 Calibration 무효화 조건으로 관리

### 문제 3: 제품 높이 편차가 DOF를 초과

- 증상: Lot 또는 위치별 Edge/Match Score 변화
- 대응: F-number, 배율, Lens, 제품 평탄도, Autofocus 및 Telecentric 적용 검토

### 문제 4: 조리개를 과도하게 조임

- 증상: Exposure가 길어지고 Motion Blur 또는 Diffraction으로 Detail 감소
- 대응: 조명 세기, Exposure, F-number의 실험적 최적점 결정

### 문제 5: Distortion을 단일 Scale로 처리

- 증상: 중앙 치수는 맞지만 가장자리에서 오차 증가
- 대응: Grid Calibration, 왜곡 보정, 위치별 Residual Map 확인

### 문제 6: Focus 조정으로 배율도 바뀜

- 증상: 선명도는 회복했지만 FOV와 측정값 변화
- 대응: Focus Lock, 장착 기준 관리, Focus 변경 후 Calibration 검증

### 문제 7: Lens 표면 오염

- 증상: 국부 Contrast 저하, Flare, 얼룩 모양의 False Defect
- 대응: 청소 기준, 보호 Glass 영향 확인, Reference Image/Histogram 감시

---

## 9. 흔한 오해

1. **“Focal Length가 곧 Magnification이다.”**  
   Focal Length는 Lens 특성이고 배율은 Object/Image 거리 조건과 함께 정해진다.

2. **“Working Distance는 Thin Lens의 Object Distance다.”**  
   기준면이 다르므로 동일하지 않을 수 있다.

3. **“조리개를 조일수록 항상 선명하다.”**  
   DOF는 늘지만 빛이 줄고 Diffraction이 증가할 수 있다.

4. **“Focus만 맞으면 치수가 정확하다.”**  
   배율, Distortion, Perspective, Calibration Residual도 중요하다.

5. **“Telecentric Lens면 Calibration이 필요 없다.”**  
   배율 변화와 Perspective를 줄이지만 장착 Rotation, Scale, Offset, 잔여 Distortion은 검증해야 한다.

6. **“Lens가 Sensor를 덮으면 전체 화질도 같다.”**  
   Image Circle Coverage와 Corner MTF/Vignetting은 별도 조건이다.

7. **“DOF 안이면 모든 높이에서 동일 성능이다.”**  
   허용 선명도 기준 내라는 뜻이며 Contrast와 측정 Bias가 완전히 같다는 뜻은 아니다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. 같은 Camera라도 Lens에 따라 검사 성능이 달라지는 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Lens가 보이는 범위와 확대 정도, 선명도와 왜곡을 결정하기 때문입니다.

**실무자 답변**  
Lens의 배율이 FOV와 Object Sampling을 결정하고, MTF/수차/Focus가 Defect Contrast를, Distortion/Perspective가 위치·치수 정확도를 결정한다. WD와 DOF는 기구 배치와 높이 공차에도 영향을 준다.

**면접용 30초 답변**  
“Camera는 Sensor Sampling을 담당하지만 Lens는 FOV, 배율, MTF, DOF와 Distortion을 결정합니다. 그래서 같은 Camera라도 Lens에 따라 μm/pixel과 결함 Contrast, 치수 오차가 달라집니다. 실제 선정 시 FOV뿐 아니라 WD, Corner MTF, DOF, 왜곡을 함께 검증합니다.”

### Q2. Focal Length와 Magnification의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Focal Length는 Lens 자체의 광학 특성이고 Magnification은 특정 거리에서 물체가 Sensor에 몇 배 크기로 맺히는지입니다.

**실무자 답변**  
Focal Length는 Lens의 주평면과 초점 관계를 나타내며 화각과 거리 조건에 관여한다. Magnification은 Image/Object 크기 비이고 Focus/Working 조건에 따라 달라질 수 있다. Fixed Magnification Lens는 지정 WD에서 배율 사양을 제공한다.

**면접용 30초 답변**  
“Focal Length는 mm로 표현하는 Lens의 광학 특성이고 Magnification은 Image Size/Object Size라는 무차원 비율입니다. 같은 50 mm Lens도 Object 거리와 Extension에 따라 배율이 달라질 수 있으므로 둘을 같은 사양으로 보면 안 됩니다.”

### Q3. Working Distance가 중요한 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Lens와 제품 사이에 조명과 기구를 설치할 공간을 정하고, 거리 변화가 배율과 초점에도 영향을 주기 때문입니다.

**실무자 답변**  
WD는 광학 배율/FOV 조건뿐 아니라 조명 배치, Motion 간섭, 유지보수, 높이 공차와 진동 민감도를 제약한다. WD 또는 Focus를 변경하면 FOV와 Calibration Scale이 변할 수 있어 재검증이 필요하다.

**면접용 30초 답변**  
“WD는 단순 초점 거리가 아니라 Lens와 Object 사이의 실제 작업 공간입니다. 원하는 FOV를 만족하면서 조명·Stage와 간섭이 없어야 하고, WD 변경은 배율과 Focus, Calibration에 영향을 줄 수 있어 기구와 광학을 함께 검토합니다.”

### Q4. DOF를 늘리려면 어떻게 해야 하나요?

**초보자가 이해할 수 있는 답변**  
조리개를 조이거나 배율을 낮추면 DOF가 늘어나는 경향이 있지만 다른 영향도 확인해야 합니다.

**실무자 답변**  
F-number 증가와 Magnification 감소가 일반적인 방법이다. 다만 F-number 증가는 광량 저하와 Diffraction, Exposure 증가를 만들고 Magnification 감소는 Sampling을 거칠게 한다. 조명 강화, 제품 높이 안정화, Telecentric/특수 Lens, Focus 전략을 함께 검토한다.

**면접용 30초 답변**  
“일반적으로 F-number를 키우거나 배율을 낮추면 DOF가 증가합니다. 하지만 조리개를 과도하게 조이면 Diffraction과 Exposure 증가가 생기고, 배율을 낮추면 μm/pixel이 나빠집니다. 그래서 조명, 높이 공차, Sampling과 함께 실험적으로 최적화합니다.”

### Q5. Distortion이 검사에 어떤 문제를 만드나요?

**초보자가 이해할 수 있는 답변**  
Image 가장자리에서 직선과 위치가 휘어 보여 실제 거리와 좌표가 틀릴 수 있습니다.

**실무자 답변**  
Distortion은 위치에 따라 이상 투영 좌표에서 벗어나는 기하 오차다. 단일 μm/pixel로 치수를 계산하면 위치별 Bias가 발생하고 Align/좌표 변환에도 영향을 준다. Grid Calibration과 왜곡 보정 후 Residual을 검사 공차와 비교한다.

**면접용 30초 답변**  
“Distortion은 Blur가 아니라 위치 오차입니다. 중앙과 가장자리의 Scale이 달라져 치수와 Machine 좌표 변환에 Bias를 만들 수 있습니다. 따라서 Grid Target으로 왜곡을 보정하고 보정 후 Residual이 검사 공차보다 충분히 작은지 확인합니다.”

### Q6. Telecentric Lens는 언제 사용하나요?

**초보자가 이해할 수 있는 답변**  
제품 높이가 조금 달라도 크기가 변해 보이지 않게 해야 하는 정밀 치수 검사에 사용합니다.

**실무자 답변**  
높이 공차나 단차로 Perspective/Magnification Error가 문제 되는 치수·위치 검사에 Object-side Telecentric Lens를 고려한다. 요구 FOV, Sensor Size, WD, Telecentric Range, Distortion, Resolution과 비용/크기를 함께 평가한다.

**면접용 30초 답변**  
“Telecentric Lens는 Object 높이 변화에 따른 배율과 Perspective 오차를 줄여야 하는 정밀 치수 검사에 사용합니다. 다만 지정 Telecentric Range와 FOV 안에서만 장점이 있고 크기와 비용이 증가하므로 공차 예산과 Calibration 결과로 필요성을 판단합니다.”

---

## 11. 실습 문제

### 실습 1: Lens 선정표 작성

다음 요구사항을 사용한다.

- Object 검사 영역: 14×10 mm
- Margin: 각 방향 10%
- Camera: 2448×2048, 3.45 μm
- 최소 WD: 100 mm

필요 FOV, 최대 허용 배율, μm/pixel을 계산하고 후보 Lens의 배율, WD, Image Circle, Distortion, MTF 확인표를 만든다.

### 실습 2: 높이 편차와 DOF

제품 높이가 기준면에서 `±0.4 mm` 변한다. DOF 근사 결과가 0.6 mm인 시스템과 1.2 mm인 시스템을 비교한다.

1. 전체 높이 범위를 계산한다.
2. 단순 DOF 기준에서 어느 시스템이 범위를 포함하는가?
3. DOF 경계에서 Measurement Bias를 별도 검증해야 하는 이유는 무엇인가?
4. F-number 증가 외의 개선 방법을 제안한다.

### 실습 3: Distortion 측정 설계

Grid Target을 사용해 다음 절차를 설계한다.

- 중앙 및 네 모서리의 Point 검출
- 이상적인 Grid Position과 측정 Position 비교
- Pixel Residual과 μm Residual 계산
- 보정 전/후 최대·RMS Residual 비교
- 허용 측정 공차 대비 Calibration 합격 기준 정의

### 실습 4: C++ Calculator 확장

Chapter 3 Calculator에 다음을 추가한다.

- Sensor Diagonal
- Thin Lens 교육용 u/v 계산
- Approximate DOF 비교
- Lens Image Circle Coverage 판정
- 여러 Lens 후보를 FOV/WD/DOF/Distortion 기준으로 정렬

### Phase 3 미니 프로젝트: Optical Configuration Evaluator

```text
Inspection Requirement
├── Required FOV
├── Minimum Feature
├── Height Variation
├── Minimum WD
└── Measurement Tolerance
          ↓
Camera + Lens Candidate 입력
          ↓
FOV / Sampling / Sensor Coverage / DOF 비교
          ↓
Risk Warning
├── FOV 부족
├── Sampling 부족
├── Image Circle 부족
├── DOF 부족
└── Calibration 필수 조건
```

결과에는 계산값뿐 아니라 **왜 해당 후보가 탈락 또는 보류인지** 근거를 남긴다. MTF, Distortion, WD처럼 Datasheet/실측이 필요한 항목을 단순 계산으로 만들어내지 않는다.

---

## 12. Chapter 핵심 요약

- 🔴 Camera, Lens, 조명, Object를 하나의 Optical System으로 봐야 한다.
- 🔴 Focal Length와 Magnification은 서로 다른 개념이다.
- 🔴 Object Space와 Image Space의 단위와 의미를 구분한다.
- 🔴 FOV와 Object μm/pixel은 Sensor Size와 배율로 1차 계산한다.
- 🔴 Working Distance는 광학뿐 아니라 조명·기구 배치를 제약한다.
- 🔴 배율이 증가하면 Sampling은 촘촘해지지만 FOV와 DOF가 줄어든다.
- 🔴 Distortion은 선명도 문제가 아니라 위치·치수의 기하 오차다.
- 🟠 조리개를 조이면 DOF는 늘지만 광량 저하와 Diffraction을 고려해야 한다.
- 🟠 Telecentric Lens는 높이 변화에 따른 Perspective/배율 오차를 줄인다.
- 🟠 계산값은 Datasheet와 Calibration Target 실측으로 검증해야 한다.

---

## 4일차 권장 학습 순서

- [ ] 40분: Object/Image Space와 Focal Length/Magnification 구분
- [ ] 50분: FOV, Sensor Coverage, Sampling 계산
- [ ] 40분: WD, Focus, DOF 관계와 Trade-off 정리
- [ ] 30분: Distortion과 Telecentric Lens 비교
- [ ] 60~90분: C++ Optical Calculator 확장
- [ ] 60분: Lens 선정표 실습
- [ ] 30분: 면접 Q1~Q6 30초 답변 연습

## 학습 완료 체크

- [ ] Focal Length와 Magnification을 구분해 설명한다.
- [ ] Working Distance와 Thin Lens의 Object Distance가 다를 수 있음을 안다.
- [ ] FOV, Sensor Diagonal, Object μm/pixel을 계산한다.
- [ ] DOF를 늘릴 때의 Trade-off를 설명한다.
- [ ] Distortion과 Blur의 차이를 설명한다.
- [ ] Telecentric Lens가 필요한 검사 조건을 설명한다.
- [ ] Optical Configuration Evaluator를 설계하거나 구현했다.

## 다음 Chapter 예고

다음 Chapter에서는 FOV, Pixel Count, Pixel Size, Sensor Size, Magnification, Object Resolution을 하나의 계산 체계로 묶고 0.25×/0.5×/1×/2× 비교 및 검사 요구사항 역산을 집중 연습한다.
