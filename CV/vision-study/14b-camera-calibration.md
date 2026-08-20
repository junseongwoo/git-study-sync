# 14일차 B. Camera Calibration: Intrinsic · Extrinsic · Distortion

> Phase 11 · 예상 학습 시간: 10~14시간 · 난이도: 중급→고급 · 중요도: 🟠 실무에서 중요

## 1. 이 Chapter에서 배우는 것

- 🔴 Intrinsic Matrix `K`: fx, fy, cx, cy
- 🔴 Extrinsic: Camera Pose R,t
- 🔴 Radial/Tangential Distortion
- 🔴 Target/View 수집과 Reprojection Error
- 🔴 Undistort와 독립 Validation

### 실무 목표

OpenCV Camera Calibration 결과의 물리적 의미를 설명하고 왜곡 보정 전후 Residual을 검증한다. Telecentric/작은 FOV에서 단순 Plane Mapping이 충분한지, 일반 Lens에서 Distortion Model이 필요한지 판단한다.

---

## 2. 선수 지식

- [[14a-calibration-coordinate-transform|Image→Machine Calibration]]
- Pinhole Camera와 3D→2D 투영의 직관

---

## 3. 핵심 개념

### 3.1 Pinhole Model

```text
s[u v 1]ᵀ=K[R|t][X Y Z 1]ᵀ
```

`[R|t]`는 World를 Camera Coordinate로, `K`는 Camera Point를 Pixel로 투영한다.

### 3.2 Intrinsic

```text
K=[fx skew cx]
  [0  fy   cy]
  [0  0    1 ]
```

`fx/fy`는 Pixel 단위 Focal Length, `cx/cy`는 Principal Point다. 이상적으로 `fx≈f_mm/pixelPitch_mm`지만 실제 값은 Focus와 Model에 따른 유효값이다.

### 3.3 Extrinsic

Target/World Coordinate를 Camera Coordinate로 바꾸는 Rotation과 Translation이다. View마다 상대 Pose가 달라 `rvec/tvec`도 달라진다.

### 3.4 Radial Distortion

```text
x_d=x(1+k1r²+k2r⁴+k3r⁶)
y_d=y(1+k1r²+k2r⁴+k3r⁶)
```

중심에서 멀수록 Barrel/Pincushion 위치 Error가 커진다.

### 3.5 Tangential Distortion

Lens/Sensor 비중심 정렬을 `p1,p2`로 모델링한다. 계수를 늘리면 Fit Error는 줄 수 있지만 Data가 부족하면 Overfit한다.

### 3.6 Target

- Checkerboard
- Symmetric/Asymmetric Circle Grid
- 정밀 Dot/Grid Target

Target Pitch 정확도가 최종 Scale을 제한한다. 종이 출력물은 정밀 Calibration Target으로 부적합할 수 있다.

### 3.7 좋은 View

- Target이 중앙/모서리를 덮음
- 거리와 Tilt가 다양함
- Blur/Saturation 없음
- 거의 같은 View만 반복하지 않음

장수보다 Parameter를 관측할 Pose 다양성이 중요하다.

### 3.8 Reprojection Error

```text
e=|p_detected-p_projected|
```

전체 RMS 외에 View별/위치별 Max와 Vector Pattern을 본다. Fit Corner Error가 작아도 Machine 측정 정확도를 보장하지 않는다.

### 3.9 Undistort

`initUndistortRectifyMap`으로 Map을 미리 만들고 `remap`할 수 있다. 보간이 Gray/Edge를 바꾸므로 정밀 측정은 Raw Point를 `undistortPoints`로 보정하는 방식과 비교한다.

### 3.10 검사 장비 적용 범위

- 일반 Lens/넓은 FOV: 왜곡 Model 중요
- Telecentric/작은 FOV: Grid Residual로 단순 Model 충분성 확인
- 평면 검사: Undistortion+Plane Mapping
- 높이 변화: 단일 Homography 부족 가능

---

## 4. 그림으로 이해하기

```text
World → Extrinsic(R,t) → Camera → Intrinsic(K) → Ideal Pixel
                                                    ↓ Distortion
                                               Measured Pixel
```

```text
Multiple Views → calibrateCamera → Reproject → Error Map
→ Independent Grid Validation → Deploy Map/Version
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- FOV Corner의 치수/위치 Bias 감소
- Multi-camera 통합 전 왜곡 보정
- Mark/Edge의 Plane Mapping
- Lens/Camera 장착 상태 및 Drift 확인

---

## 6. 숫자로 이해하기

### 예제 1: Focal Pixel

```text
f=16 mm, pitch=3.45 μm=0.00345 mm
fx≈16/0.00345≈4637.68 pixel
```

### 예제 2: Radial 항

`k1=-0.1`, `r=0.5`, 다른 항 0:

```text
scale=1-0.1×0.25=0.975
```

반경 좌표가 2.5% 안쪽으로 이동하는 단순 예다.

### 예제 3: Reprojection Error

```text
RMS=0.2 pixel, Sampling=5 μm/pixel → 단순 환산 1 μm
```

측정 정확도 1 μm를 보장하는 뜻은 아니다.

### 예제 4: Corner

Corner Error 1.2 Pixel, 4 μm/pixel이면 단순 위치 Error는 4.8 μm다. 전체 RMS로 Corner 문제를 숨기지 않는다.

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <vector>

struct CameraCalibrationResult final {
 cv::Mat cameraMatrix,distCoeffs;
 std::vector<cv::Mat> rvecs,tvecs;
 double rmsPixels{},meanErrorPixels{},maxErrorPixels{};
};

[[nodiscard]] CameraCalibrationResult CalibrateCamera(
 const std::vector<std::vector<cv::Point3f>>& objectPoints,
 const std::vector<std::vector<cv::Point2f>>& imagePoints,
 const cv::Size imageSize)
{
 if(objectPoints.size()!=imagePoints.size()||objectPoints.size()<3||
    imageSize.width<=0||imageSize.height<=0)
  throw std::invalid_argument{"Invalid observations"};
 cv::Mat K=cv::Mat::eye(3,3,CV_64F),dist;
 std::vector<cv::Mat> rvecs,tvecs;
 const double rms=cv::calibrateCamera(objectPoints,imagePoints,imageSize,
                                      K,dist,rvecs,tvecs);
 double sum=0,maxError=0; size_t count=0;
 for(size_t i=0;i<objectPoints.size();++i){
  std::vector<cv::Point2f> projected;
  cv::projectPoints(objectPoints[i],rvecs[i],tvecs[i],K,dist,projected);
  if(projected.size()!=imagePoints[i].size())
   throw std::runtime_error{"Projection size mismatch"};
  for(size_t j=0;j<projected.size();++j){
   const double e=cv::norm(projected[j]-imagePoints[i][j]);
   sum+=e; maxError=std::max(maxError,e); ++count;
  }
 }
 if(count==0) throw std::runtime_error{"No calibration points"};
 return {K,dist,rvecs,tvecs,rms,sum/static_cast<double>(count),maxError};
}
```

### 검증 Test

1. fx/fy 양수, Principal Point 범위
2. View별 RMS/Max와 Corner Vector
3. 독립 Grid의 실제 거리 Error
4. Image Size/ROI/Binning 불일치 거부
5. 보정 전/후 측정 Bias 비교

---

## 8. 실무에서 발생하는 문제

1. 중앙에만 Target 배치.
2. 동일 Pose 반복으로 관측성 부족.
3. 부정확한 Target Pitch.
4. Resize/ROI 변경 후 K 재사용.
5. RMS만 저장해 Corner Outlier 누락.
6. 과도한 계수로 Overfit.
7. Remap 보간 Edge Bias.

---

## 9. 흔한 오해

1. fx는 Lens 표기 mm와 같은 단위다.
2. Extrinsic은 Camera 고유값이다.
3. RMS 0.2 Pixel이면 측정 정확도도 0.2 Pixel이다.
4. View가 많기만 하면 좋다.
5. Telecentric Lens는 Calibration이 필요 없다.
6. Undistort하면 모든 Error가 사라진다.

---

## 10. 면접에서 나올 수 있는 질문

1. **Intrinsic?** fx/fy/cx/cy의 내부 투영 Parameter.
2. **Extrinsic?** World/Target 대비 Camera Pose.
3. **Radial/Tangential?** 반경 Lens 왜곡과 비중심 정렬 왜곡.
4. **좋은 View?** FOV 전체와 다양한 Tilt/거리의 선명한 Target.
5. **평가?** 위치/View별 RMS/Max와 독립 실제 거리.
6. **ROI 변경?** K 조정 근거를 검증하거나 재Calibration.

---

## 11. 실습 문제

1. Checkerboard Object Point를 mm로 생성한다.
2. View/Corner별 Reprojection Error Map을 만든다.
3. `undistortPoints`와 Remapped Edge 위치를 비교한다.
4. Image 0.5배 Resize 시 fx/fy/cx/cy를 계산한다.

### Phase 11 미니 프로젝트

Image Set에서 Corner를 검출하고 K/Distortion, View별 RMS/Max, Error Vector, Undistort Preview, 독립 Grid 거리 Error와 Metadata를 저장한다.

---

## 12. Chapter 핵심 요약

- 🔴 Intrinsic과 Extrinsic을 구분한다.
- 🔴 Distortion은 위치에 따른 기하 Error다.
- 🔴 Target 정확도와 View 다양성이 중요하다.
- 🔴 전체 RMS 외 위치/View별 Max를 본다.
- 🔴 독립 Target의 실제 거리로 검증한다.
- 🔴 Image Size/ROI Mode는 Calibration 조건이다.

## 다음 학습 예고

15일차에는 Image/Camera/Stage/Machine/World Coordinate를 하나의 Transform Chain으로 연결한다.
