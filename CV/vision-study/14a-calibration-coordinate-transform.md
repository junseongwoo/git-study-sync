# 14일차 A. Calibration: Image Coordinate를 Machine Coordinate로 변환하기

> Phase 10 · 예상 학습 시간: 12~16시간 · 난이도: 중급→고급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

- 🔴 Calibration의 목적과 Align과의 차이
- 🔴 Pixel/Image/Machine/World Coordinate
- 🔴 Scale, Offset, Rotation, Axis Flip
- 🔴 Similarity/Affine/Homography 선택
- 🔴 Point Correspondence와 Least Squares
- 🔴 Fit/Validation Residual과 Version 관리

### 실무 목표

Image Point `(u,v)`를 Machine Point `(X,Y)`로 변환하고 Model의 전제와 단위를 설명한다. FOV 전체의 독립 검증점에서 RMS/Max Error를 평가한다.

---

## 2. 선수 지식

- [[13-alignment-advanced|Alignment 심화]]
- Homogeneous Coordinate와 Matrix 곱
- `1 mm=1000 μm`

```text
Calibration: 좌표계 사이의 장기적 관계
Alignment: 매 제품의 현재 Pose 변화
```

Camera/Lens/WD/Focus/Resolution/ROI Mode가 바뀌면 Calibration 유효성을 재검토한다.

---

## 3. 핵심 개념

### 3.1 왜 필요한가?

Image에서 100 Pixel 이동했다는 사실만으로 실제 거리를 알 수 없다. Scale, 축 방향, Rotation, 원점 Offset과 왜곡이 필요하다.

```text
Image (u,v) pixel --Calibration--> Machine (X,Y) mm
```

### 3.2 Scale+Offset

```text
X=s_x u+o_x
Y=s_y v+o_y
```

Image +v와 Machine +Y가 반대면 `s_y`가 음수다. 이 Model은 Camera Rotation과 Shear를 설명하지 못한다.

### 3.3 Affine Transform

```text
[X]   [a11 a12][u] + [tx]
[Y] = [a21 a22][v]   [ty]
```

Translation, Rotation, X/Y Scale, Axis Flip, Shear를 표현한다. 평면 Object의 일반적인 2D Calibration에 사용한다.

### 3.4 Homography

```text
[X~ Y~ W~]ᵀ=H[u v 1]ᵀ
X=X~/W~, Y=Y~/W~
```

Plane Perspective를 표현하며 최소 4개 non-collinear Point가 필요하다. Object 높이가 Calibration Plane을 벗어나면 같은 H가 정확하지 않다.

### 3.5 Model 선택

| Model | 조건 | 장점 | 위험 |
|---|---|---|---|
| Scale+Offset | 축 평행/균일 | 단순 | Rotation 미반영 |
| Similarity | Rotation+Uniform Scale | 강체 관계 | X/Y 차이 미반영 |
| Affine | 평면/약한 Perspective | 실용적 | Lens Distortion 미반영 |
| Homography | Plane Perspective | 기울기 대응 | 높이 변화/Overfit |
| Distortion+Pose | 정밀/광각 | 물리 Model | 복잡 |

최소 자유도로 시작하고 Residual의 공간 Pattern을 확인한다.

### 3.6 Point Correspondence

```text
(u_i,v_i) ↔ (X_i,Y_i)
```

Point는 중앙과 네 모서리 등 FOV 전체에 고르게 분포한다. 가까운 세 점의 Affine Fit Error가 0이어도 FOV 밖 정확도는 증명되지 않는다.

### 3.7 Fit과 Validation 분리

```text
e_i=|P_machine_i-Transform(p_image_i)|
RMS=sqrt(Σe_i²/N)
Max=max(e_i)
```

Fit에 사용하지 않은 Point에서 RMS, Max와 Error Vector Map을 평가한다.

### 3.8 Stage 기반 Calibration

Stage 이동량과 Image Mark 이동을 대응시킬 수 있다. Stage Backlash/직교도/반복성, Settle, Encoder와 Command 차이, Trigger 시점 Pose를 검증한다.

### 3.9 Handedness와 Determinant

Image는 아래 +v, Machine은 위 +Y일 수 있다. Affine Linear Part의 Determinant가 음수면 Reflection/Axis Flip이 포함된다. 의도인지 좌표 정의 오류인지 확인한다.

### 3.10 Version

Calibration ID, Camera/Lens/WD/Focus/ROI Mode, Target ID, Matrix, Fit/Validation RMS·Max와 승인 상태를 Result에 연결한다.

---

## 4. 그림으로 이해하기

```text
Image (pixel/down +v) → scale/rotation/flip/origin → Machine (mm/up +Y)
```

```text
Fit Points → Matrix → Separate Validation Points → Residual Map → Accept
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- Align Pixel Offset을 Stage 보정량으로 변환
- Defect 좌표를 mm로 저장
- Multi-camera 결과를 공통 좌표로 통합
- Pixel 거리/면적을 실제 단위로 측정
- Robot/Stage가 Image Feature로 이동

---

## 6. 숫자로 이해하기

### 예제 1: 단순 Scale

```text
2 μm/pixel × 100 pixel=200 μm=0.2 mm
```

### 예제 2: Rotation과 Y Flip

`s=0.002 mm/pixel`, 1° Rotation:

```text
A=[s cos1°   s sin1°]
  [s sin1°  -s cos1°]
```

Image Delta `(100,0)`은 Machine Delta `(0.199970,0.003490) mm`다.

### 예제 3: Residual

Error `0.006,0.008,0.010,0.020 mm`:

```text
RMS≈0.01225 mm, Max=0.020 mm
```

허용 오차 ±0.015 mm라면 RMS만 보면 안 된다.

### 예제 4: Matrix

```text
X=0.002u+0.00002v+100
Y=0.00001u-0.002v+250
(u,v)=(1000,500) → (X,Y)=(102.010,249.010) mm
```

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>

class AffineCalibration final {
public:
    explicit AffineCalibration(const cv::Matx23d& matrix):matrix_(matrix)
    {
        for(double value:matrix_.val)
            if(!std::isfinite(value)) throw std::invalid_argument{"Finite matrix required"};
    }
    [[nodiscard]] cv::Point2d ImageToMachine(const cv::Point2d& p) const noexcept
    {
        return {matrix_(0,0)*p.x+matrix_(0,1)*p.y+matrix_(0,2),
                matrix_(1,0)*p.x+matrix_(1,1)*p.y+matrix_(1,2)};
    }
private: cv::Matx23d matrix_;
};

struct CalibrationQuality final {double rmsMm{},maxMm{};};

[[nodiscard]] CalibrationQuality EvaluateCalibration(
 const AffineCalibration& c,const std::vector<cv::Point2d>& image,
 const std::vector<cv::Point2d>& machine)
{
    if(image.size()!=machine.size()||image.empty())
        throw std::invalid_argument{"Equal non-empty point sets required"};
    double sum=0,maxError=0;
    for(size_t i=0;i<image.size();++i){
        const double e=cv::norm(c.ImageToMachine(image[i])-machine[i]);
        sum+=e*e; maxError=std::max(maxError,e);
    }
    return {std::sqrt(sum/image.size()),maxError};
}
```

`estimateAffine2D/estimateAffinePartial2D`로 Fit할 때 RANSAC Inlier/Outlier를 기록한다. Fit 성공은 Validation 통과가 아니다.

### Unit Test

```cpp
#include <cassert>
void TestKnownAffine(){
 const AffineCalibration c{{0.002,0.00002,100,0.00001,-0.002,250}};
 const auto p=c.ImageToMachine({1000,500});
 assert(std::abs(p.x-102.010)<1e-9&&std::abs(p.y-249.010)<1e-9);
}
```

---

## 8. 실무에서 발생하는 문제

1. 중앙 Point만 사용해 Corner Error 누락.
2. Fit Point로 품질을 평가해 Overfit 통과.
3. Image y Flip 누락으로 Stage 반대 이동.
4. Lens/WD 변경 뒤 Matrix 재사용.
5. Stage Backlash를 Camera 변환으로 Fit.
6. RANSAC Outlier를 숨김.
7. mm/μm 혼용으로 1000배 오류.

---

## 9. 흔한 오해

1. Calibration은 μm/pixel 하나다.
2. Align과 Calibration은 같은 Matrix다.
3. 세 Fit Point Error 0이면 정확하다.
4. Homography가 항상 우수하다.
5. RMS가 작으면 모든 위치가 정확하다.
6. Camera가 같으면 Lens 교체 후에도 같다.

---

## 10. 면접에서 나올 수 있는 질문

1. **왜 필요한가?** Pixel을 실제 좌표/단위/축으로 연결한다.
2. **Align과 차이?** System 관계와 제품별 Pose의 차이다.
3. **Affine/Homography 차이?** 평행성 유지와 Perspective Plane 표현.
4. **100 Pixel은 몇 μm?** 위치/방향 Calibration 없이는 모른다.
5. **품질 평가?** 독립 Point의 RMS/Max와 Residual Map.
6. **재Calibration 시점?** 광학/기구/Mode 변경 또는 Drift 초과.

---

## 11. 실습 문제

1. Y Flip과 2° Rotation을 포함한 Matrix 작성.
2. 3×3 Grid의 Fit/Validation 분리와 Residual Map 설계.
3. 5 μm/pixel, 2048 Width에서 0.2% Scale Error의 끝단 오차 계산.
4. 장비 변경별 Calibration 무효화 표 작성.

### Phase 10 미니 프로젝트

Point Pair CSV에서 Similarity/Affine을 Fit하고 Matrix, Inlier, Fit/Validation RMS·Max, Residual Overlay와 Version Metadata를 저장한다.

---

## 12. Chapter 핵심 요약

- 🔴 Calibration은 Pixel을 Machine/World 좌표로 연결한다.
- 🔴 Scale, Origin, Rotation, Flip과 왜곡을 고려한다.
- 🔴 최소 Transform Model을 선택한다.
- 🔴 Fit과 독립 Validation을 분리한다.
- 🔴 RMS, Max와 공간 Error를 함께 본다.
- 🔴 단위와 좌표 방향을 명시한다.

## 다음 문서

[[14b-camera-calibration|14일차 B. Camera Intrinsic/Extrinsic과 Distortion]]
