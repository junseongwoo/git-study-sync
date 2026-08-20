# 13일차. Alignment 심화: Matching에서 X/Y/Theta까지

> Phase 9 · 예상 학습 시간: 16~22시간 · 난이도: 중급→고급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 Alignment의 목적과 Global/Local Align
- 🔴 Translation, Rotation, Scale과 2D Rigid Transform
- 🔴 Fiducial/Align Mark의 설계 원칙
- 🔴 Template, Pattern, Feature Matching의 차이
- 🔴 Match Score와 Position Accuracy의 차이
- 🔴 2점/3점 이상으로 X/Y/Theta 계산
- 🔴 Residual, Mark 거리와 Geometry 검증
- 🟠 Pyramid/Angle Search/Sub-pixel Refinement
- 🟠 RANSAC과 Outlier 제거
- 🟠 Align 실패 정책과 Review Data

### 실무 목표

검출된 Mark 좌표를 제품 기준좌표와 대응시켜 최적 X/Y/Theta를 계산한다. Match Score만으로 성공을 판단하지 않고 Mark ID, 위치 범위, Pair 거리, Rigid Fit Residual과 재촬영 오차를 검증한다.

---

## 2. 선수 지식

- [[08-vision-align-glass|3개 Align Mark Glass 사례]]
- [[12-roi-transform|ROI Rigid Transform]]
- Rotation Matrix와 `atan2`
- Image→Machine Calibration의 필요성

```text
p_current = R(θ)q_reference + t
```

`q`와 `p`는 반드시 같은 단위/축 방향의 좌표여야 한다.

---

## 3. 핵심 개념

### 3.1 Alignment란?

Reference 제품과 현재 제품의 Pose 차이를 추정하는 과정이다.

```text
Reference Geometry + Current Image Features
                  ↓
            X / Y / Theta
                  ↓
      Stage Correction 또는 ROI Transform
```

Alignment는 Calibration과 다르다. Calibration은 좌표계 사이 관계를 구하고 Align은 그 관계를 이용해 제품마다 달라지는 Pose를 구한다.

### 3.2 Global과 Local Alignment

- Global Align: 제품 전체의 대표 X/Y/Theta. Glass 외곽 또는 2~3개 Global Mark 사용.
- Local Align: 특정 검사 영역 주변의 추가 위치/각도 보정. Pattern 변형, 공정 Scale, 대형 기판 지역 오차 대응.

```text
Global Pose → 모든 ROI 1차 배치 → Local Mark → 해당 ROI 미세 보정
```

Local Align으로 Global Calibration 불량을 숨기지 않는다. Local Correction 분포를 장비 상태 지표로 활용한다.

### 3.3 Transform 자유도

| Model | 자유도 | 최소 대응점 | 적용 |
|---|---:|---:|---|
| Translation | 2 | 1 | 회전 없는 위치 편차 |
| Rigid | 3 | 2 | 강체 X/Y/Theta |
| Similarity | 4 | 2 | Rigid+균일 Scale |
| Affine | 6 | 3 non-collinear | X/Y Scale+Shear 포함 |
| Homography | 8 | 4 non-collinear | Perspective Plane |

강체 Glass Align은 Rigid가 기본이다. 자유도를 늘리면 Residual은 줄지만 Calibration/기구 오류를 Scale·Shear로 흡수할 수 있다.

### 3.4 Fiducial 설계

좋은 Mark의 조건:

- Background와 높은 Contrast
- 회전/반전 ID 구분
- 주변 Pattern과 고유성
- 오염/파손에도 중심 정의가 안정적
- 가능한 긴 Baseline과 비공선 배치
- Camera FOV와 Stage 이동 범위 안
- Etching/Printing 공정 Variation이 작음

원은 중심은 안정적이지만 자체 각도를 제공하지 않는다. 여러 원의 배치 Vector로 제품 각도를 구한다.

### 3.5 Template Matching

Reference Patch를 Current Image의 각 위치와 비교한다.

대표 Score:

- Normalized Cross Correlation
- Squared Difference

장점: 구현과 해석이 쉬우며 고정 Pattern에 강함.  
약점: 회전, Scale, 조명, 부분 가림에 민감. Angle/Scale Search가 필요하면 계산량이 증가한다.

### 3.6 Pattern Matching

상용 Vision Library에서 Pattern Matching은 Edge/Geometry 기반, Pyramid와 Angle Search, Sub-pixel Pose를 포함하는 더 넓은 기능을 뜻하는 경우가 많다. Library마다 의미와 Score 정의가 다르므로 API 문서를 기준으로 계약한다.

### 3.7 Feature Matching

ORB/SIFT 계열 Keypoint와 Descriptor를 비교한다.

장점:

- 회전/Scale/부분 가림에 상대적으로 강함
- 넓은 Scene의 대응점 제공

약점:

- 단순/반복 Pattern에서 불안정
- Outlier와 잘못된 대응
- 정밀 반복성은 전용 Mark/Pattern Matcher보다 낮을 수 있음

검사 장비의 정밀 Align에는 명확한 Fiducial/Geometry가 우선이며 Feature Matching은 복잡한 Texture나 Coarse Align에 검토한다.

### 3.8 Coarse-to-Fine

```text
넓은 ROI + Image Pyramid + 넓은 Angle
                  ↓
Coarse Pose
                  ↓
작은 ROI + 원본 해상도 + 좁은 Angle
                  ↓
Sub-pixel Pose
```

처리 시간과 오검출을 함께 줄인다. Coarse 단계 실패 시 Fine Search를 억지로 실행하지 않는다.

### 3.9 Match Score는 정확도가 아니다

높은 Score는 Pattern 유사도가 높다는 의미이지 위치가 정확하다는 보장이 아니다.

- 반복 Pattern의 잘못된 Peak
- Blur 상태의 넓은 Peak
- 대칭 Mark의 180° 모호성
- 부분 가림에도 높은 배경 상관

Score와 함께 Peak Separation, Expected Position, Angle, Mark Geometry, Residual을 확인한다.

### 3.10 2점 Align

Reference `q1,q2`, Current `p1,p2`:

```text
θ = angle(p2-p1) - angle(q2-q1)
t = p1 - R(θ)q1
```

두 점 거리도 비교한다.

```text
scale check = |p2-p1| / |q2-q1|
```

Rigid 모델이면 1에 가까워야 한다.

### 3.11 N점 Rigid Least Squares

Centroid를 뺀 좌표 `q'`, `p'`에서:

```text
A = Σ(qx'px' + qy'py')
B = Σ(qx'py' - qy'px')
θ = atan2(B,A)
t = p_bar - R(θ)q_bar
```

각 Point Residual:

```text
e_i = |p_i - (R q_i+t)|
RMS = sqrt(Σe_i²/N)
```

### 3.12 RANSAC

대응점이 많고 Outlier가 있을 때 일부 Point로 Model을 반복 생성하고 Inlier가 가장 많은 Model을 선택한다. 세 개뿐인 중요한 Align Mark에서는 Mark별 Geometry/ID 검증과 명시적 실패가 더 적합할 수 있다. 잘못된 Mark를 자동 제외한 사실을 숨기지 않는다.

### 3.13 Align Result에 포함할 데이터

- X/Y/Theta와 좌표계/단위
- Mark별 Image/Machine 좌표와 Score
- Reference/Current Pair 거리
- Mark별 Residual, RMS/Max Residual
- Search ROI와 사용 Algorithm Version
- Calibration/Recipe Version
- 처리 시간, 반복 횟수, 실패 사유

---

## 4. 그림으로 이해하기

```text
Reference marks qᵢ          Current detections pᵢ
●────────●                  /●────────●
    ●                →          ●

Correspondence → Rigid Fit → X/Y/Theta → Residual Check
```

```text
Match success
  ├─ Score pass?
  ├─ Expected ROI/angle pass?
  ├─ Mark ID/geometry pass?
  ├─ Pair distance pass?
  └─ Fit residual pass? → Align Success
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- Glass/Panel Global Pose 보정
- Pad/Mark 주변 Local ROI 배치
- Stage X/Y/Theta Physical Correction
- Review Overlay와 NG 좌표의 Reference 변환
- Multi-camera 측정 결과를 제품 좌표로 통합

제품이 X±20 Pixel, Y±15 Pixel, Rotation±1°로 움직이면 고정 ROI는 Edge/Defect 위치를 잘못 측정한다. Align Pose로 ROI를 이동·회전해야 한다.

---

## 6. 숫자로 이해하기

### 예제 1: 2점 각도

```text
Reference: q1=(0,0), q2=(300,0)
Current:   p1=(10,-5), p2=(309.954,0.236)

Current vector ≈ (299.954,5.236)
θ=atan2(5.236,299.954)≈1.000°
t=(10,-5)
```

### 예제 2: Baseline과 각도 Noise

Point 반복성 `σ=0.005 mm`일 때:

```text
σθ≈√2σ/L
L=300 mm → 0.00135°
L=50 mm  → 0.00810°
```

### 예제 3: Residual

세 Mark Residual이 `0.012,0.018,0.030 mm`이면:

```text
RMS=sqrt((0.012²+0.018²+0.030²)/3)
   ≈0.02136 mm
Max=0.030 mm
```

RMS와 Max를 모두 사용하면 한 Mark만 크게 벗어난 상황을 찾기 쉽다.

### 예제 4: 큰 Glass 가장자리 오차

중심에서 250 mm 떨어진 ROI에 Theta Error `0.02°`가 남으면:

```text
arc≈250×0.02π/180≈0.0873 mm=87.3 μm
```

각도 허용값은 Glass 크기와 ROI 위치 오차 요구로 역산한다.

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>

struct RigidPose final { double tx{},ty{},thetaDegrees{},rmsResidual{},maxResidual{}; };

[[nodiscard]] RigidPose EstimateRigidPose(
    const std::vector<cv::Point2d>& reference,
    const std::vector<cv::Point2d>& measured)
{
    if(reference.size()!=measured.size()||reference.size()<2)
        throw std::invalid_argument{"At least two corresponding points required"};
    cv::Point2d qbar{},pbar{};
    for(size_t i=0;i<reference.size();++i){qbar+=reference[i];pbar+=measured[i];}
    qbar*=1.0/reference.size(); pbar*=1.0/measured.size();

    double a=0,b=0;
    for(size_t i=0;i<reference.size();++i){
        const auto q=reference[i]-qbar, p=measured[i]-pbar;
        a+=q.x*p.x+q.y*p.y;
        b+=q.x*p.y-q.y*p.x;
    }
    if(std::hypot(a,b)<1e-12) throw std::runtime_error{"Degenerate mark geometry"};
    const double theta=std::atan2(b,a), c=std::cos(theta),s=std::sin(theta);
    const cv::Point2d rqbar{c*qbar.x-s*qbar.y,s*qbar.x+c*qbar.y};
    const cv::Point2d translation=pbar-rqbar;

    double sumSquared=0,maxResidual=0;
    for(size_t i=0;i<reference.size();++i){
        const auto& q=reference[i];
        const cv::Point2d predicted{c*q.x-s*q.y+translation.x,
                                    s*q.x+c*q.y+translation.y};
        const double residual=cv::norm(measured[i]-predicted);
        sumSquared+=residual*residual;
        maxResidual=std::max(maxResidual,residual);
    }
    constexpr double pi=3.14159265358979323846;
    return {translation.x,translation.y,theta*180.0/pi,
            std::sqrt(sumSquared/reference.size()),maxResidual};
}

struct TemplateHit final { cv::Point2d center; double score{}; };

[[nodiscard]] TemplateHit MatchTranslationOnly(
    const cv::Mat& searchImage,const cv::Mat& templ)
{
    if(searchImage.empty()||templ.empty()||searchImage.type()!=templ.type()||
       templ.cols>searchImage.cols||templ.rows>searchImage.rows)
        throw std::invalid_argument{"Invalid template/search image"};
    cv::Mat response;
    cv::matchTemplate(searchImage,templ,response,cv::TM_CCOEFF_NORMED);
    double minValue=0,maxValue=0; cv::Point minLocation,maxLocation;
    cv::minMaxLoc(response,&minValue,&maxValue,&minLocation,&maxLocation);
    return {{maxLocation.x+(templ.cols-1)/2.0,
             maxLocation.y+(templ.rows-1)/2.0},maxValue};
}
```

### Unit Test

```cpp
#include <cassert>

void TestRigidPose()
{
    const std::vector<cv::Point2d> q{{0,0},{300,0},{0,200}};
    constexpr double pi=3.14159265358979323846;
    const double th=1.0*pi/180.0,c=std::cos(th),s=std::sin(th);
    std::vector<cv::Point2d> p;
    for(const auto& v:q)p.push_back({c*v.x-s*v.y+10,s*v.x+c*v.y-5});
    const auto pose=EstimateRigidPose(q,p);
    assert(std::abs(pose.tx-10)<1e-9&&std::abs(pose.ty+5)<1e-9);
    assert(std::abs(pose.thetaDegrees-1)<1e-9&&pose.rmsResidual<1e-9);
}
```

`MatchTranslationOnly`는 회전/Scale을 처리하지 않는다. 실제 Angle Search는 Pyramid, 회전 Template/Edge Model 또는 검증된 Library를 사용하고 반환 Pose Convention을 Test한다.

---

## 8. 실무에서 발생하는 문제

1. 반복 Pattern의 잘못된 Peak → 고유 Mark, ROI, Peak Separation, Geometry 검증.
2. 대칭 Mark 각도 모호성 → Mark 배치 Vector 또는 비대칭 ID.
3. Score는 높지만 Blur로 위치 반복성 저하 → Peak Width/반복 측정.
4. Mark 한 개 오염 → Residual로 실패 처리, 임의 보간 금지.
5. Camera 순차 촬영 좌표 혼용 → 모든 Point를 Machine 좌표로 변환.
6. 자유도 과다 → Rigid Residual 원인부터 분석.
7. Stage Pivot 오류 → 보정 후 Closed-loop 재촬영.

---

## 9. 흔한 오해

1. Match Score가 높으면 위치도 정확하다.
2. Mark 한 개의 Template Angle이 곧 Glass Angle이다.
3. 3점이면 Affine가 Rigid보다 항상 좋다.
4. Local Align이 많을수록 정확하다.
5. Image 좌표끼리 바로 Fit해도 된다.
6. Outlier를 버리면 Align은 성공이다.
7. Align 완료 후 Residual/재촬영은 필요 없다.

---

## 10. 면접에서 나올 수 있는 질문

1. **Align과 Calibration 차이?** Calibration은 좌표계 관계, Align은 제품별 Pose.
2. **두 Mark로 X/Y/Theta 가능?** Rigid 전제에서 Pair Angle과 Translation으로 가능.
3. **세 번째 Mark 역할?** Noise 평균화, 오검출/Geometry/Scale 이상 검증.
4. **Template와 Feature Matching 차이?** 전자는 고정 Patch 유사도, 후자는 Keypoint 대응과 Outlier Model Fit.
5. **Score 외 무엇을 검증?** ID, 범위, Pair 거리, Angle, Residual, 반복성.
6. **Global/Local 차이?** 제품 전체 Pose와 특정 영역의 추가 보정.

---

## 11. 실습 문제

1. X±20/Y±15/θ±1° Data를 생성해 고정 ROI와 Dynamic ROI 실패율을 비교한다.
2. Mark Baseline 50/150/300 mm에서 5 μm 위치 Noise의 각도 Noise를 계산한다.
3. 한 Mark에 0.2 mm Outlier를 넣고 RMS/Max Residual 변화를 측정한다.
4. Template Score와 실제 위치 오차의 Scatter Plot을 만든다.

### Phase 9 미니 프로젝트: Alignment Evaluator

Mark Image/Reference Geometry를 입력해 Mark별 Score/좌표, X/Y/Theta, Pair 거리, RMS/Max Residual, ROI Overlay와 실패 사유를 저장한다.

---

## 12. Chapter 핵심 요약

- 🔴 Align은 Reference와 Current 제품의 Pose 차이를 구한다.
- 🔴 강체 제품은 최소 자유도의 Rigid Model을 우선한다.
- 🔴 Match Score와 위치 정확도를 구분한다.
- 🔴 3점 이상은 Least Squares와 Residual 검증에 유리하다.
- 🔴 모든 Mark는 공통 Calibration 좌표로 변환한다.
- 🔴 Global Pose 후 필요 영역만 Local Align한다.
- 🟠 Outlier 제거 사실과 실패 사유를 Result에 남긴다.
- 🟠 보정 후 재측정으로 Pivot/Stage Model을 검증한다.

## 13일차 학습 완료 체크

- [ ] Matching 세 종류의 적용 조건을 설명한다.
- [ ] 2점/N점 Rigid Pose를 계산한다.
- [ ] Score/Residual/Geometry를 함께 판정한다.
- [ ] Global/Local Align을 구분한다.
- [ ] Alignment Evaluator를 설계하거나 구현했다.

## 다음 학습 예고

14일차에는 Pixel/Image 좌표를 Machine/World 좌표로 바꾸는 Calibration과 Camera Intrinsic/Distortion을 학습한다.
