# 15일차. Coordinate System: Image · Camera · Stage · Machine · Product

> Phase 12 · 예상 학습 시간: 10~14시간 · 난이도: 중급→고급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

- 🔴 좌표계(Frame) 이름, 원점, 축, 단위
- 🔴 Image/Camera/Stage/Machine/World/Product Coordinate
- 🔴 Forward/Inverse Transform과 합성 순서
- 🔴 Align Pose와 Calibration Transform의 결합
- 🔴 Stage 이동 시 촬영 Pose 결합
- 🔴 좌표 결과의 Traceability와 Unit Safety
- 🟠 Hand-eye/Camera-to-stage 관계
- 🟠 2D Plane Model의 한계

### 실무 목표

Point 값만 전달하지 않고 어떤 Frame의 어떤 단위인지 계약한다. Transform 이름을 `T_target_source`로 읽고 여러 Camera/Stage/제품 좌표를 공통 Machine Frame으로 변환한다.

---

## 2. 선수 지식

- [[14a-calibration-coordinate-transform|Image→Machine Calibration]]
- [[13-alignment-advanced|Align Pose]]
- 3×3 Homogeneous Transform

```text
p_target = T_target_source × p_source
```

`T_machine_image`는 Image Point를 Machine Point로 바꾸는 Matrix다.

---

## 3. 핵심 개념

### 3.1 좌표는 숫자 두 개가 아니다

`(100,200)`만으로는 의미가 없다.

```text
Frame: image-raw / image-undistorted / stage / machine / product
Unit: pixel / μm / mm
Axis: +x/+y direction
Origin: where?
Time/Pose: which frame capture?
```

### 3.2 Image Coordinate

보통 좌상단 `(0,0)`, 오른쪽 +u, 아래 +v, 단위 pixel이다. Camera ROI/Crop/Binning/Resize가 원점과 Scale을 바꿀 수 있다.

### 3.3 Camera Coordinate

Pinhole Model에서 Camera Optical Center 원점, 보통 +Z가 광축 방향인 3D 좌표다. Normalized Image Coordinate와 혼동하지 않는다. 2D 평면 검사에서는 Distortion 보정 후 Plane Mapping으로 직접 Machine 좌표를 구할 수도 있다.

### 3.4 Stage Coordinate

Motion Controller/Encoder가 사용하는 좌표다. Command Position과 Actual Position, Local/Global Frame, 회전 Pivot을 구분한다.

### 3.5 Machine Coordinate

장비 전체의 공통 Frame이다. 여러 Camera, Stage, Robot, Review 좌표를 통합한다. 장비 기구 Datum과 연결되고 mm 또는 μm를 사용한다.

### 3.6 World/Product Coordinate

- World: 공정/Cell/Line 기준 좌표
- Product: 제품 중심/Datum 기준 좌표

Align은 Current Product Frame이 Machine Frame에서 어디에 있는지 구한다.

```text
p_machine = T_machine_product × p_product
p_product = inverse(T_machine_product) × p_machine
```

### 3.7 Raw와 Undistorted Image Frame

왜곡 보정 전/후 Pixel Coordinate는 서로 다른 Frame이다. Raw Image에서 검출한 Point에 Undistorted Calibration Matrix를 바로 적용하면 안 된다.

### 3.8 Transform Chain

```text
p_machine = T_machine_stage
          × T_stage_camera
          × T_camera_image
          × p_image
```

Matrix는 Point에 가까운 오른쪽부터 적용된다. 각 중간 Frame의 Source/Target이 맞지 않으면 합성할 수 없다.

### 3.9 Fixed Camera와 Moving Camera

#### Fixed Camera, Moving Product Stage

Camera↔Machine 관계는 고정이고 Product Pose가 Stage와 함께 변한다.

#### Moving Camera

촬영마다 Stage Actual Pose가 Camera Frame에 들어간다.

```text
p_machine_i = T_machine_stage(capture_i)
            × T_stage_camera
            × p_camera_i
```

여러 Mark를 순차 촬영하면 각 Frame의 Timestamp/Stage Pose가 반드시 필요하다.

### 3.10 Align Pose 방향

Align Module이 반환하는 Pose를 명시한다.

```text
Forward: p_current = T_current_reference × p_reference
Inverse: p_reference = inverse(T_current_reference) × p_current
```

“X=+10”만 전달하지 말고 `reference→current`, Pivot, 단위와 축을 포함한다.

### 3.11 Physical와 Virtual Correction

- Physical: Stage를 움직여 Current Product Frame을 Reference에 맞춤
- Virtual: Image/ROI/측정 Point를 Product Reference Frame으로 역변환

Stage Correction은 Pivot과 Controller Frame을 포함한 Pose 역변환이다. 단순 부호 반전은 작은 각도의 근사일 수 있다.

### 3.12 Transform Graph와 단일 경로

좌표계 관계를 Graph로 관리하되 같은 Source→Target에 여러 경로가 생기면 어떤 Calibration Version이 권위 있는지 정한다. Runtime에 임의 Matrix를 섞지 않는다.

### 3.13 단위 안전

변수명/Type에 단위를 표현한다.

```text
imagePointPx
machinePointMm
objectScaleUmPerPixel
thetaDegrees / thetaRadians
```

단위 변환은 경계 함수 한 곳에서 수행하고 Result에도 Unit을 저장한다.

---

## 4. 그림으로 이해하기

```text
Raw Image(px)
   │ distortion correction
Undistorted Image(px)
   │ plane calibration
Camera/Stage(mm)
   │ capture stage pose / hand-eye
Machine(mm)
   │ inverse product align pose
Product(mm)
   │ line/cell transform
World(mm)
```

```text
T_A_B : B point → A point
T_A_C = T_A_B × T_B_C
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- 여러 Mark 순차 촬영 좌표 통합
- Align Result로 Stage 또는 ROI 보정
- NG Defect의 Product/Machine 좌표 저장
- Multi-camera 결과 Fusion
- Review Overlay와 Motion Go-to-position
- Recipe ROI를 Current Image에 배치

---

## 6. 숫자로 이해하기

### 예제 1: 요청 예제의 좌표 계약

가정:

```text
Current Image Point p=(1250,850) pixel
Reference Pivot c=(1024,1024) pixel
Align Forward Pose: reference→current
tx=+10 pixel, ty=-20 pixel, theta=+0.5°
```

Current Point를 Product Reference로 되돌린다.

```text
p_ref = R(-theta) × (p-c-t) + c

p-c-t=(216,-154)
p_ref≈(1238.648,868.121) pixel
```

### 예제 2: Reference Pixel→Product 실제 좌표

Reference Origin `(1024,1024)`, Scale 2 μm/pixel, Product +Y가 Image -v라면:

```text
X=(1238.648-1024)×2≈+429.296 μm
Y=-(868.121-1024)×2≈+311.758 μm
```

Offset/Rotation/왜곡이 없는 단순 Scale 예이며 실제 장비는 Calibration Matrix를 사용한다.

### 예제 3: Transform 합성 순서

Camera Point `(1,0) mm`, Camera가 Stage에서 +100 mm X Offset, Stage가 Machine에서 20 mm Y에 있다면:

```text
p_stage=(101,0) mm
p_machine=(101,20) mm
```

### 예제 4: 단위 오류

`0.2 mm` 보정량을 `200 μm` 단위 API에 숫자 `0.2`로 넘기면 1000배 작은 명령이 된다. API 경계에서 명시적으로 변환한다.

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>
#include <cmath>
#include <stdexcept>

class Transform2d final {
public:
    explicit Transform2d(const cv::Matx33d& m):m_(m)
    {
        for(double v:m_.val) if(!std::isfinite(v))
            throw std::invalid_argument{"Finite transform required"};
        if(std::abs(cv::determinant(cv::Mat(m_)))<1e-12)
            throw std::invalid_argument{"Invertible transform required"};
    }

    [[nodiscard]] static Transform2d FromPose(
        double tx,double ty,double thetaDegrees)
    {
        constexpr double pi=3.14159265358979323846;
        const double r=thetaDegrees*pi/180.0,c=std::cos(r),s=std::sin(r);
        return Transform2d{{c,-s,tx,s,c,ty,0,0,1}};
    }

    [[nodiscard]] cv::Point2d Apply(const cv::Point2d& p) const
    {
        const cv::Vec3d h=m_*cv::Vec3d{p.x,p.y,1};
        if(std::abs(h[2])<1e-12) throw std::runtime_error{"Point at infinity"};
        return {h[0]/h[2],h[1]/h[2]};
    }

    [[nodiscard]] Transform2d Inverse() const {return Transform2d{m_.inv()};}

    // this * rhs means rhs is applied first.
    [[nodiscard]] Transform2d operator*(const Transform2d& rhs) const
    { return Transform2d{m_*rhs.m_}; }
private:
    cv::Matx33d m_;
};
```

### Unit Test

```cpp
#include <cassert>
void TestCompositionAndInverse(){
 const auto cameraToStage=Transform2d::FromPose(100,0,0);
 const auto stageToMachine=Transform2d::FromPose(0,20,0);
 const auto cameraToMachine=stageToMachine*cameraToStage;
 const auto p=cameraToMachine.Apply({1,0});
 assert(std::abs(p.x-101)<1e-9&&std::abs(p.y-20)<1e-9);
 const auto back=cameraToMachine.Inverse().Apply(p);
 assert(cv::norm(back-cv::Point2d{1,0})<1e-9);
}
```

제품 코드에서는 `ImagePointPx`, `MachinePointMm` 같은 별도 Type/Wrapper로 잘못된 Frame 합성을 Compile-time에 줄이는 것이 좋다.

---

## 8. 실무에서 발생하는 문제

1. Source/Target Matrix 방향 반대.
2. Degree를 Radian API에 전달.
3. Image +v와 Machine +Y 혼동.
4. Command Stage Pose를 Actual Capture Pose로 사용.
5. Raw Point에 Undistorted Matrix 적용.
6. Camera ROI Origin Offset 누락.
7. Stage Pivot/Local Frame 누락.
8. mm/μm 1000배 오류.

---

## 9. 흔한 오해

1. 좌표는 x/y만 있으면 된다.
2. Matrix 곱 순서는 바꿔도 된다.
3. Align X/Y는 항상 Image Pixel이다.
4. Inverse는 tx/ty/theta 부호만 바꾸면 된다.
5. Camera가 이동해도 같은 Image→Machine Matrix다.
6. Product와 Machine 원점은 같다.

---

## 10. 면접에서 나올 수 있는 질문

1. **Image/Stage/Machine 차이?** Pixel 배열, Motion 축, 장비 공통 Datum.
2. **Transform 이름?** `T_target_source`는 Source Point를 Target으로 변환.
3. **합성 순서?** Point에 가까운 오른쪽 Matrix부터 적용.
4. **Align Pose 방향?** Reference→Current인지 계약하고 반대는 Inverse.
5. **Moving Camera 주의?** Frame마다 Actual Stage Pose/Timestamp 결합.
6. **단위 오류 방지?** Typed Point/변수명/경계 변환과 Golden Test.

---

## 11. 실습 문제

1. 본인 장비의 모든 Frame 원점/축/단위 표를 만든다.
2. Camera→Stage→Machine→Product Matrix Chain을 그린다.
3. ROI Crop Origin `(200,100)`을 포함한 Raw Pixel 변환을 계산한다.
4. Degree/Radian, mm/μm, y Flip 오류를 잡는 Unit Test를 작성한다.

### Phase 12 미니 프로젝트: Transform Graph Inspector

Frame과 Versioned Transform을 등록하고 Source→Target 경로, 합성 Matrix, Inverse Round-trip Error, Unit/Axis Metadata와 Point 변환 로그를 보여준다.

---

## 12. Chapter 핵심 요약

- 🔴 Point에는 Frame, Unit, Axis, Origin과 Capture Pose가 필요하다.
- 🔴 `T_target_source` Naming으로 방향을 고정한다.
- 🔴 Matrix 합성 순서는 교환되지 않는다.
- 🔴 Align Forward/Inverse Pose를 구분한다.
- 🔴 Moving Camera는 Frame별 Stage Actual Pose가 필요하다.
- 🔴 Raw/Undistorted Image Frame을 구분한다.
- 🔴 단위와 좌표 Type을 코드 계약으로 표현한다.

## 다음 학습 예고

16일차에는 Presence/Position/치수/Scratch/Particle/Crack 검사 알고리즘과 전체 Pipeline을 연결한다.
