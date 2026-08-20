# 12일차. ROI와 Align 기반 Coordinate Transform

> Phase 8 · 예상 학습 시간: 10~14시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 ROI의 목적과 Static/Dynamic ROI
- 🔴 Align 결과 X/Y/Theta를 ROI에 적용하는 방법
- 🔴 회전 중심(Pivot)과 Transform 순서
- 🔴 Rect, RotatedRect, Polygon, Mask의 차이
- 🔴 Reference Coordinate와 Current Image Coordinate
- 🔴 ROI Clip/Out-of-image 처리
- 🟠 Search ROI와 Inspection ROI 분리
- 🟠 Image Warp와 ROI Point Transform의 선택

### 실무 목표

Recipe에 기준 좌표로 저장된 ROI를 제품의 현재 Align Pose에 맞춰 이동·회전한다. Axis-aligned Rect를 억지로 회전시키지 않고 Polygon/RotatedRect/Mask를 사용하며, Transform Pivot·좌표 방향·경계 오류를 명확히 처리한다.

---

## 2. 선수 지식

- [[08-vision-align-glass|8일차]]의 Rigid Transform과 Glass 중심
- Image Coordinate `(x,y)`와 Machine Coordinate
- 삼각함수와 2×2 Rotation Matrix

```text
R(θ) = [ cosθ -sinθ ]
       [ sinθ  cosθ ]
```

OpenCV Image는 보통 아래쪽이 +y이므로 수학 좌표의 CCW 부호와 화면상 회전 방향이 다르게 보일 수 있다. Align Module과 ROI Module의 부호 계약을 Test로 고정한다.

---

## 3. 핵심 개념

### 3.1 ROI를 왜 사용하는가?

- 검사 위치를 명시
- 계산량과 False Positive 감소
- 검사 항목별 Parameter 분리
- Review Overlay와 Recipe Editing 제공

ROI는 단순 Crop이 아니라 **제품 좌표계에 정의된 검사 Geometry**다.

### 3.2 Static ROI와 Dynamic ROI

- Static ROI: Image의 고정 Pixel 위치. 제품 위치가 반복 정밀도 안에서 고정될 때 사용.
- Dynamic ROI: Reference ROI에 Align Transform을 적용. 제품 X/Y/Theta 변화에 대응.

```text
Reference Product ROI --Align Pose--> Current Image ROI
```

### 3.3 Search ROI와 Inspection ROI

- Align Search ROI: Mark가 이동할 가능성을 포함하는 넓은 영역
- Inspection ROI: Align 후 실제 검사할 좁은 영역

Inspection ROI로 Mark를 먼저 찾으려 하면 제품 편차가 ROI보다 큰 순간 Align이 실패한다.

### 3.4 기본 Rigid Transform

Reference Point `p=(x,y)`를 Current Point로 변환:

```text
p_current = R(θ) × p_reference + t
t = (tx,ty)
```

회전 중심 `c`가 별도로 주어지면:

```text
p_current = R(θ) × (p_reference-c) + c + t
```

Glass 중심 또는 Align 기준점을 Pivot으로 사용하는 경우가 일반적이다.

### 3.5 Transform 순서가 중요한 이유

```text
Rotate about origin → Translate
```

와

```text
Translate → Rotate about origin
```

은 결과가 다르다. Recipe에서 Align X/Y가 “회전 전 Reference Frame의 Translation”인지 “회전 후 Current Frame의 Translation”인지 인터페이스로 고정한다.

### 3.6 ROI 표현

| 표현 | 회전 | Mask | 장점 | 한계 |
|---|---:|---:|---|---|
| `cv::Rect` | 불가 | 사각 | 빠른 Crop | 회전 ROI 표현 불가 |
| `cv::RotatedRect` | 가능 | 사각 | Center/Size/Angle 직관적 | 복잡 형상 불가 |
| Polygon | 가능 | 가능 | 임의 형상, Point Transform | Raster Mask 생성 필요 |
| Binary Mask | 가능 | 직접 | Pixel 선택에 편리 | Transform 보간/관리 필요 |

회전된 ROI의 Axis-aligned Bounding Rect만 검사하면 원하지 않는 Background까지 포함된다. Bounding Rect로 Crop한 뒤 Polygon Mask를 적용한다.

### 3.7 ROI를 움직일까, Image를 움직일까?

#### ROI Transform

원본 Image는 유지하고 ROI Point만 Current Pose로 변환한다.

- 보간에 의한 Image 변화 없음
- 여러 ROI에 효율적
- 각 알고리즘이 회전 ROI를 처리해야 함

#### Image Warp/Rectification

Current Image를 Reference 좌표로 역변환한다.

- 모든 ROI를 Reference 위치에서 처리 가능
- 구현이 단순해질 수 있음
- 보간, Border, 처리 시간과 측정 Bias 발생

정밀 Edge 측정은 가능한 한 원본 Image 좌표에서 수행하고 좌표만 Transform하는 방식을 우선 검토한다.

### 3.8 Dynamic RotatedRect

Reference RotatedRect가 Center `r`, Size `(w,h)`, Angle `α`라면 Rigid Align 후:

```text
center' = R(θ)(r-c)+c+t
size'   = (w,h)
angle'  = α+θ
```

Rigid Transform에서는 Size가 변하지 않는다. Scale까지 바뀐다면 Similarity/Affine 모델의 사용 근거를 별도로 확인한다.

### 3.9 ROI 경계 처리

Transform 후 ROI 일부가 Image 밖이면 선택지는 다음과 같다.

- Align/Inspection Error로 처리
- 허용 Margin 이내만 Clip하고 `partial=true` 기록
- Border Padding 후 처리
- Search 범위/Camera FOV 재설계

치수/Area 검사에서 잘린 ROI를 정상 처리하면 안 된다. Clip을 숨기지 말고 Result 상태로 남긴다.

### 3.10 좌표 반올림

Transform Point는 `double/float`로 유지한다. Crop용 Bounding Rect를 만들 때:

- Left/Top: `floor`
- Right/Bottom: `ceil`

을 사용해 Polygon 전체가 포함되도록 한다. 조기 정수 반올림은 반복 Transform과 측정에 Bias를 만든다.

---

## 4. 그림으로 이해하기

```text
Reference Product                 Current Product
┌──────────────┐                  /──────────────/
│   ┌──ROI──┐  │    X/Y/Theta    /  ┌──ROI──┐  /
│   └───────┘  │  ───────────►  /───└───────┘─/
└──────────────┘                /──────────────/
```

```text
ROI Polygon Points → Rigid Transform → Bounding Rect Crop
                                      + Polygon Mask
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- Align 후 Mark/Pad/Particle 검사 ROI 이동
- Glass의 여러 검사 영역을 Global Align Pose로 배치
- Local Mark로 특정 영역만 추가 보정
- Review Overlay를 현재 Image에 표시
- 검사 결과 좌표를 Reference 제품 좌표로 역변환

큰 Glass는 Global Rigid Align만으로 지역 변형을 모두 설명하지 못할 수 있다. Global ROI 배치 후 Local Align/Calibration Residual을 확인한다.

---

## 6. 숫자로 이해하기

### 예제 1: ROI 중심을 Pivot 자체로 회전

Reference ROI Center `(1000,800)`, Align `tx=+12.5`, `ty=-3.2`, `θ=+0.15°`이고 Pivot이 ROI Center라면:

```text
Current Center = (1012.5,796.8)
Current Angle  = Reference Angle + 0.15°
```

Pivot 위 Point는 Rotation으로 이동하지 않는다.

### 예제 2: Glass 중심 Pivot

Pivot `c=(1024,1024)`, ROI Center `r=(1000,800)`:

```text
r-c = (-24,-224)
θ = 0.15° ≈ 0.00261799 rad

R(θ)(r-c) ≈ (-23.4135,-224.0621)
center' ≈ (1024,1024)+(-23.4135,-224.0621)+(12.5,-3.2)
        ≈ (1013.0865,796.7379)
```

단순히 `(1012.5,796.8)`로 이동한 값과 다르다. Pivot에서 멀수록 작은 각도도 위치 차이를 만든다.

### 예제 3: 회전으로 인한 이동 크기

Pivot에서 250 mm 떨어진 ROI가 `0.1°` 회전하면 Arc 이동 근사:

```text
s = rθ = 250×(0.1π/180) ≈ 0.4363 mm
```

큰 Glass에서는 매우 작은 Theta도 ROI 위치에 큰 영향을 준다.

### 예제 4: Bounding Rect 반올림

변환 Polygon x 범위가 `100.2~300.7`, y 범위가 `50.8~180.1`이면:

```text
left=floor(100.2)=100
top=floor(50.8)=50
right=ceil(300.7)=301
bottom=ceil(180.1)=181
Rect size = 201×131
```

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>

#include <cmath>
#include <stdexcept>
#include <vector>

struct Pose2d final {
    double txPixels{};
    double tyPixels{};
    double thetaDegrees{};
};

[[nodiscard]] cv::Point2d TransformPoint(
    const cv::Point2d& point,
    const cv::Point2d& pivot,
    const Pose2d& pose)
{
    if (!std::isfinite(pose.txPixels) || !std::isfinite(pose.tyPixels) ||
        !std::isfinite(pose.thetaDegrees)) {
        throw std::invalid_argument{"Pose must be finite"};
    }
    constexpr double pi=3.14159265358979323846;
    const double radians=pose.thetaDegrees*pi/180.0;
    const double c=std::cos(radians), s=std::sin(radians);
    const cv::Point2d q=point-pivot;
    return {c*q.x-s*q.y+pivot.x+pose.txPixels,
            s*q.x+c*q.y+pivot.y+pose.tyPixels};
}

[[nodiscard]] std::vector<cv::Point2d> TransformPolygon(
    const std::vector<cv::Point2d>& polygon,
    const cv::Point2d& pivot,
    const Pose2d& pose)
{
    if (polygon.size()<3) {
        throw std::invalid_argument{"ROI polygon needs at least 3 points"};
    }
    std::vector<cv::Point2d> result;
    result.reserve(polygon.size());
    for (const auto& p:polygon) result.push_back(TransformPoint(p,pivot,pose));
    return result;
}

[[nodiscard]] cv::Rect SafeBoundingRect(
    const std::vector<cv::Point2d>& polygon,
    const cv::Size& imageSize)
{
    if (polygon.empty() || imageSize.width<=0 || imageSize.height<=0) {
        throw std::invalid_argument{"Invalid polygon or image size"};
    }
    double minX=polygon[0].x,maxX=polygon[0].x;
    double minY=polygon[0].y,maxY=polygon[0].y;
    for (const auto& p:polygon) {
        minX=std::min(minX,p.x); maxX=std::max(maxX,p.x);
        minY=std::min(minY,p.y); maxY=std::max(maxY,p.y);
    }
    const cv::Rect requested{
        static_cast<int>(std::floor(minX)),
        static_cast<int>(std::floor(minY)),
        static_cast<int>(std::ceil(maxX)-std::floor(minX)),
        static_cast<int>(std::ceil(maxY)-std::floor(minY))};
    const cv::Rect imageBounds{0,0,imageSize.width,imageSize.height};
    const cv::Rect clipped=requested & imageBounds;
    if (clipped != requested) {
        throw std::out_of_range{"Transformed ROI leaves the image"};
    }
    return requested;
}
```

### Unit Test

```cpp
#include <cassert>

void TestGivenAlignExample()
{
    const auto p=TransformPoint({1000,800},{1024,1024},{12.5,-3.2,0.15});
    assert(std::abs(p.x-1013.0865)<0.001);
    assert(std::abs(p.y-796.7379)<0.001);
}

void TestNinetyDegreeRotation()
{
    const auto p=TransformPoint({11,10},{10,10},{0,0,90});
    assert(std::abs(p.x-10)<1e-9);
    assert(std::abs(p.y-11)<1e-9);
}
```

### 코드에서 봐야 할 점

1. Point와 Pose는 정수로 조기 반올림하지 않는다.
2. Pivot을 명시적 인자로 전달한다.
3. Polygon 전체를 변환한 뒤 Bounding Rect를 만든다.
4. ROI가 Image 밖이면 조용히 Clip하지 않고 Error로 드러낸다.
5. OpenCV 화면 좌표의 Angle Convention은 실제 Align 출력과 Golden Test로 확인한다.

---

## 8. 실무에서 발생하는 문제

1. **Pivot을 ROI 중심으로 잘못 사용**: Glass 중심/Align 기준점 계약 확인.
2. **Image y축과 Machine Y축 부호 혼동**: Calibration 후 좌표에서 Transform.
3. **회전 ROI를 Axis-aligned Rect로만 검사**: Polygon Mask 적용.
4. **ROI 일부가 FOV 밖인데 계속 검사**: Partial/Error 상태와 Margin 설계.
5. **Point마다 정수 반올림**: double 유지, Raster 단계에서만 floor/ceil.
6. **Global Align로 큰 Glass 전체를 가정**: 지역 Residual과 Local Align 검토.
7. **Image Warp 후 정밀 Edge 측정**: 보간 Bias를 원본 좌표 측정과 비교.

---

## 9. 흔한 오해

1. **“ROI 이동은 X/Y를 더하면 끝이다.”** Theta와 Pivot이 필요하다.
2. **“Rect를 회전하면 또 Rect다.”** 축 정렬 Rect가 아니라 RotatedRect/Polygon이다.
3. **“Bounding Rect가 곧 회전 ROI다.”** 불필요한 Background를 포함한다.
4. **“Clip된 ROI도 같은 검사다.”** 정보가 잘려 결과 의미가 달라진다.
5. **“Image를 회전하면 좌표 문제가 사라진다.”** 보간과 역변환 관리가 추가된다.
6. **“0.1°는 무시할 만큼 작다.”** 큰 Glass 가장자리에서는 수백 μm 이동이다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. Static ROI와 Dynamic ROI의 차이는?
**답변**: Static은 Image 고정 좌표, Dynamic은 Reference ROI에 Align X/Y/Theta를 적용한 현재 제품 좌표다.

### Q2. ROI와 Align은 어떤 관계인가?
**답변**: Align이 제품 Pose를 구하고 ROI Transform이 그 Pose로 검사 Geometry를 현재 Image에 배치한다.

### Q3. 왜 Pivot이 중요한가?
**답변**: 같은 각도라도 회전 중심에서 떨어진 Point의 이동량이 달라지기 때문이다.

### Q4. 회전 ROI를 어떻게 처리하는가?
**답변**: Polygon/RotatedRect Point를 변환하고 Bounding Crop 안에 Mask를 적용한다.

### Q5. ROI가 Image 밖으로 나가면?
**답변**: 검사 의미에 따라 Error/Partial 정책을 명시하며 치수 검사는 일반적으로 Error 처리한다.

### Q6. ROI Transform과 Image Warp 중 무엇이 좋은가?
**답변**: 원본 보존과 정밀 측정에는 Point/ROI Transform을 우선하고, 다수 Reference ROI 처리 편의가 중요하면 Warp를 검증 후 사용한다.

---

## 11. 실습 문제

1. Pivot `(0,0)`, Point `(100,50)`, `tx=10,ty=-5,θ=1°`를 계산한다.
2. 370×470 Glass의 네 Corner를 ±1° 회전해 필요한 FOV Margin을 계산한다.
3. Rect를 Polygon으로 만들고 X/Y/Theta 후 Mask를 생성한다.
4. ROI가 Image를 1/10/50 Pixel 벗어나는 경우의 정책을 설계한다.

### Phase 8 미니 프로젝트: Dynamic ROI Viewer

Reference Image/ROI와 Align Pose를 입력해 변환 Polygon, Bounding Rect, Mask와 경계 상태를 Overlay하고 JSON/CSV로 좌표를 저장한다.

---

## 12. Chapter 핵심 요약

- 🔴 ROI는 제품 기준 검사 Geometry다.
- 🔴 Dynamic ROI는 `R(θ)(p-c)+c+t`로 계산한다.
- 🔴 Pivot과 좌표 축/부호 계약이 필수다.
- 🔴 회전 ROI는 Polygon/RotatedRect와 Mask로 처리한다.
- 🔴 Point는 실수로 유지하고 Raster 단계에서만 반올림한다.
- 🔴 Image 밖 ROI를 숨겨서 Clip하지 않는다.
- 🟠 정밀 측정은 원본 Image 좌표를 우선한다.
- 🟠 큰 Glass는 Global 후 Local Residual을 확인한다.

## 12일차 학습 완료 체크

- [ ] Static/Dynamic ROI를 구분한다.
- [ ] Pivot 포함 Point Transform을 계산한다.
- [ ] Polygon Mask와 Bounding Rect를 구분한다.
- [ ] ROI 경계 및 반올림 정책을 정했다.
- [ ] Dynamic ROI Viewer를 설계하거나 구현했다.

## 다음 학습 예고

13일차에는 Pattern/Template/Feature Matching, Global/Local Alignment와 3점 Rigid Fit을 심화한다.
