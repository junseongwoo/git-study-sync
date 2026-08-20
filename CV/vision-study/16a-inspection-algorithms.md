# 16일차 A. 산업용 검사 알고리즘 선택과 측정

> Phase 13 · 예상 학습 시간: 14~18시간 · 난이도: 중급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

- 🔴 Presence/Position/Size/Distance/Angle 검사
- 🔴 Edge, Blob, Pattern Matching의 선택 기준
- 🔴 Scratch/Particle/Crack/Missing/Stain/Contamination
- 🔴 Feature Extraction과 Measurement/Judgement 분리
- 🔴 Reference/Golden Image 기반 Difference
- 🔴 검출률, 오검률, 반복성과 Guard Band
- 🟠 전통 Vision과 Deep Learning 적용 경계

### 실무 목표

결함 이름만으로 Algorithm을 선택하지 않고 Image에서 나타나는 밝기·Edge·형상·Texture 특징으로 분해한다. 측정값과 판정을 분리하고 정상/불량 Variation으로 성능을 검증한다.

---

## 2. 선수 지식

- Threshold/Edge/Blob/Matching
- Align/ROI/Calibration
- 조명과 CNR

```text
Physical Defect → Optical Contrast → Image Feature → Algorithm → Measurement → Spec
```

---

## 3. 핵심 개념

### 3.1 검사 문제를 Feature로 번역

```text
“Scratch를 찾아라”
→ 배경보다 밝거나 어두운가?
→ 길고 가는 Line/Edge인가?
→ 방향/폭/길이 범위는?
→ 표면 Texture와 어떻게 다른가?
```

### 3.2 기본 검사 선택표

| 검사 | 주요 Feature | 대표 Algorithm | 주요 Risk |
|---|---|---|---|
| Presence/Absence | Area/Pattern 유무 | Blob, Matching | 위치 편차/가림 |
| Position | Mark/Edge Center | Matching, Edge, Blob Centroid | Calibration |
| Width/Height | 두 반대 Edge | 1D Profile/Sobel/Sub-pixel | Focus/Polarity |
| Area | Binary Region | Threshold+Component | Threshold Bias |
| Distance | Point/Line 간 거리 | Edge/Geometry+Calibration | Distortion |
| Angle | Line/Mark Vector | Line Fit, Matching | Baseline |
| Diameter | Circle Edge | Circle/Ellipse Fit | Perspective |
| Roundness | Radius Variation | Contour/Circle Residual | Pixelization |
| Edge Position | Gradient Peak | Profile/Sobel | Blur/Bias |

### 3.3 Defect 검사 선택표

| 결함 | Image 특징 | 1차 Algorithm | 보강 |
|---|---|---|---|
| Scratch | 길고 가는 Contrast/Edge | Directional Filter, Line/Blob | Dark Field 다방향 |
| Particle | 국부 밝기/어두운 Blob | Threshold/Top-hat+Blob | Area/Circularity/CNR |
| Crack | 가는 분기 Dark/bright Line | Ridge/Edge, Morphology | Skeleton/Length |
| Missing | Expected Feature 부재 | Matching/Blob Count | Align 성공 전제 |
| Stain | 넓고 약한 Local Difference | Background/Reference Difference | Local 통계 |
| Contamination | 불규칙 Blob/Texture | Threshold/Texture/Difference | 정상 Variation |
| Pattern Defect | 기준 Pattern과 불일치 | Align+Reference Difference | Registration Residual |

### 3.4 Presence

단순 Count만 아니라 Expected ROI, Area/Position/Shape/Score를 함께 사용한다. Absence와 “검사 불능”을 분리한다. Align 실패나 빈 Image는 Missing NG가 아니라 System/Inspection Error다.

### 3.5 Position

Pattern Center, Blob Centroid, Edge Intersection 중 제품에서 반복 가능한 Datum을 선택한다. Blob Centroid는 밝기/Threshold 변화로 움직일 수 있고 Pattern Center는 Template Center Offset 정의가 필요하다.

### 3.6 치수

Binary Bounding Box보다 Gray Edge Profile의 Sub-pixel Edge Pair가 정밀 치수에 유리하다. Calibration, Distortion, Focus, 조명 Telecentricity와 Gauge R&R을 포함한다.

### 3.7 Scratch

방향성 Dark Field와 Line/Gradient가 일반적이다. Scratch 폭이 Optical PSF보다 작으면 Width 측정보다 Presence/Contrast Energy 검출로 정의할 수 있다. 방향별 사각지대를 Test한다.

### 3.8 Particle

Background를 제거한 Local Contrast Image에서 Blob을 분석한다. Area만으로 Dust, Texture, Sensor Hot Pixel을 구분하지 못하므로 Peak/Mean Contrast, Shape, 지속성, 위치를 사용한다.

### 3.9 Crack

Crack은 가늘고 분기하며 Contrast가 위치별로 달라질 수 있다. Ridge/Edge, 방향성 Filter, Closing/Skeleton을 사용할 수 있지만 Morphology가 길이와 연결성을 바꾼다. Raw Overlay와 End/Branch Point를 검증한다.

### 3.10 Stain/Contamination

넓고 약한 결함은 Global Threshold보다 Background Estimation, Reference Difference, Local Mean/Variance가 유리하다. 정상 Shading, Pattern, 조명 Drift가 False Positive를 만든다.

### 3.11 Pattern Defect

Reference와 Current Image를 정확히 Align한 뒤 Difference한다. 0.1 Pixel Registration Error도 강한 정상 Edge에 큰 Difference를 만든다. Edge 주변 Tolerance Band 또는 Distance-aware 비교를 검토한다.

### 3.12 Feature/Measurement/Judgement 분리

```text
Feature: edges/blobs/matches
Measurement: width=1.0025 mm, area=0.020 mm²
Judgement: min≤value≤max → OK/NG
```

Spec 변경이 Image Processing을 바꾸지 않도록 분리한다.

### 3.13 Guard Band

측정 불확실도가 Spec에 비해 크면 경계값 판정이 흔들린다.

```text
Spec OK: 9.90~10.10 mm
Guard Band: 9.92~10.08 mm만 자동 OK
경계: Review/재검 정책
```

Guard Band는 품질/계측 합의와 Measurement System Analysis에 근거한다.

### 3.14 Deep Learning 적용 경계

전통 Vision이 유리:

- 명확한 Geometry/치수/Threshold
- 설명 가능한 Rule과 적은 Data

DL을 검토:

- 정상 Texture Variation이 크고 결함 모양이 다양
- Rule 조합이 과도하며 충분한 Label Data가 있음

DL도 조명/광학/좌표/Result Architecture를 대체하지 않는다.

---

## 4. 그림으로 이해하기

```text
Requirement → Visual Feature → Preprocess → Extract → Measure → Judge
     ↑                                                    ↓
 Physical Sample ←──── Review/Failure Analysis ←──── Result
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- 조립 유무/방향 판정
- Pad/Mark Position과 Align
- 외경/Gap/Width 측정
- Glass/Metal 표면 결함
- Pattern 누락/오염 Review
- 품질 통계와 공정 Feedback

---

## 6. 숫자로 이해하기

### 예제 1: Width

```text
Edge=(120.3,320.8) px, Scale=5 μm/px
Width=(320.8-120.3)×5=1002.5 μm=1.0025 mm
```

### 예제 2: Particle Area

```text
Area=180 px², sx=4.8 μm/px, sy=5.1 μm/px
Area=180×4.8×5.1=4406.4 μm²=0.0044064 mm²
```

### 예제 3: Detection 성능

불량 200개 중 194 검출, 정상 1000개 중 12개 오검:

```text
Detection Rate=194/200=97%
False Positive Rate=12/1000=1.2%
```

### 예제 4: Angle Error 영향

100 mm 길이에서 `0.05°` 방향 Error의 끝단 횡오차:

```text
100×tan(0.05°)≈0.0873 mm
```

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>
#include <algorithm>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

enum class Verdict { Ok,Ng,Error };
struct Measurement {std::string name;double value,lower,upper;std::string unit;};
struct InspectionOutput {Verdict verdict;std::vector<Measurement> values;cv::Mat overlay;std::string reason;};

class IInspector {
public:
 virtual ~IInspector()=default;
 [[nodiscard]] virtual InspectionOutput Inspect(const cv::Mat& gray) const=0;
};

class PresenceByArea final:public IInspector {
public:
 PresenceByArea(double threshold,int minArea,int maxArea)
  :threshold_(threshold),minArea_(minArea),maxArea_(maxArea)
 {if(threshold<0||threshold>255||minArea<0||minArea>maxArea)throw std::invalid_argument{"Invalid recipe"};}

 [[nodiscard]] InspectionOutput Inspect(const cv::Mat& gray) const override {
  if(gray.empty()||gray.type()!=CV_8UC1)return {Verdict::Error,{}, {},"Invalid image"};
  cv::Mat binary; cv::threshold(gray,binary,threshold_,255,cv::THRESH_BINARY);
  cv::Mat labels,stats,centroids;
  const int n=cv::connectedComponentsWithStats(binary,labels,stats,centroids,8);
  int largest=0;
  for(int i=1;i<n;++i)largest=std::max(largest,stats.at<int>(i,cv::CC_STAT_AREA));
  const bool ok=largest>=minArea_&&largest<=maxArea_;
  return {ok?Verdict::Ok:Verdict::Ng,
          {{"largest_area",static_cast<double>(largest),
            static_cast<double>(minArea_),static_cast<double>(maxArea_),"px^2"}},
          {},ok?"":"Presence area out of range"};
 }
private: double threshold_;int minArea_,maxArea_;
};
```

실제 구현에서는 ROI/Align/Calibration을 Engine이 준비하고 Inspector는 명시된 입력/Recipe로 Feature와 Measurement를 반환한다. Error와 제품 NG를 구분한다.

---

## 8. 실무에서 발생하는 문제

1. 결함 이름만으로 Algorithm 선택.
2. Align 실패를 Missing으로 판정.
3. Golden 한 장에 Overfit.
4. Morphology로 결함 크기 변경.
5. Threshold/조명 Drift로 Area 변동.
6. Detection과 Measurement 성능 혼동.
7. 정상 Variation 부족으로 False Positive 급증.

---

## 9. 흔한 오해

1. Scratch는 Canny 하나로 검사한다.
2. Particle은 Area만 보면 된다.
3. Reference Difference가 크면 결함이다.
4. Sub-pixel이면 실제 해상도가 높아진다.
5. 검출률만 높으면 좋은 검사다.
6. DL이면 조명/Align이 필요 없다.

---

## 10. 면접에서 나올 수 있는 질문

1. **Scratch Feature?** Line/Edge/방향성 Contrast/긴 Blob.
2. **Particle?** Local Threshold/Top-hat+Blob, Area/Contrast/Shape.
3. **Position?** Pattern/Edge/Blob Datum과 Calibration.
4. **Measurement/Judgement 분리 이유?** Spec 변경/추적/Review.
5. **Reference Difference 주의?** Registration/조명 Normal Variation.
6. **성능 평가?** Detection, False Positive, Bias, Repeatability, Cycle Time.

---

## 11. 실습 문제

1. 검사 10종을 Feature/Algorithm/조명/실패 원인 표로 만든다.
2. Particle Area/Contrast/Circularity Rule의 Confusion Matrix를 계산한다.
3. Reference Image를 0.1~1 Pixel 이동해 Difference False Defect를 측정한다.
4. Width 측정의 Bias/Repeatability/Guard Band를 설계한다.

### Phase 13 미니 프로젝트

Presence, Width, Particle 세 Inspector를 동일 Interface로 구현하고 Measurement/Spec/Verdict/Error/Overlay를 JSON과 Image로 저장한다.

---

## 12. Chapter 핵심 요약

- 🔴 결함을 Image Feature로 번역해 Algorithm을 선택한다.
- 🔴 조명/Align/ROI가 Algorithm보다 선행한다.
- 🔴 Detection과 Measurement/Judgement를 분리한다.
- 🔴 Score/Area 하나가 아니라 여러 특징과 위치를 검증한다.
- 🔴 실제 Variation으로 검출률과 오검률을 평가한다.
- 🔴 Error와 제품 NG를 구분한다.
- 🟠 DL은 전통 Vision으로 분리가 어려운 Texture 문제에 제한적으로 검토한다.

## 다음 문서

[[16b-inspection-pipeline|16일차 B. Inspection Pipeline]]
