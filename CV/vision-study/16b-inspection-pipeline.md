# 16일차 B. Inspection Pipeline: Acquisition에서 Result까지

> Phase 14 · 예상 학습 시간: 12~16시간 · 난이도: 중급→고급 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

- 🔴 Pipeline 단계별 책임과 Data Contract
- 🔴 Acquisition/Preprocess/Align/ROI/Feature/Measure/Judge
- 🔴 제품 NG와 System Error 분리
- 🔴 Recipe Snapshot과 Result Traceability
- 🔴 Intermediate Image/Overlay/NG 저장
- 🔴 Cycle Time과 비동기 저장
- 🟠 Stage별 Timing/Quality Gate
- 🟠 Testable Architecture

### 실무 목표

한 함수에 모든 OpenCV 호출을 섞지 않고 단계별 입력/출력과 실패 정책을 설계한다. 동일 Frame/Recipe/Calibration로 재현 가능한 Result를 만들고 UI/Review/CIM이 같은 확정 Result를 소비하게 한다.

---

## 2. 선수 지식

- [[16a-inspection-algorithms|검사 알고리즘 선택]]
- [[13-alignment-advanced|Alignment]]
- [[12-roi-transform|Dynamic ROI]]
- [[14a-calibration-coordinate-transform|Calibration]]

---

## 3. 핵심 개념

### 3.1 전체 Pipeline

```text
Image Acquisition
→ Validation
→ Preprocessing
→ Alignment
→ ROI Transform
→ Feature Extraction
→ Inspection/Measurement
→ Judgement
→ Result Finalize
→ Review/Storage/CIM
```

### 3.2 Acquisition

Frame Image와 Camera ID, Frame/Trigger/Product ID, Timestamp, Exposure/Gain, Buffer Ownership을 확정한다. 빈/불완전/오래된 Frame은 제품 NG가 아니라 Acquisition Error다.

### 3.3 Validation

- Image Type/Size/Channel
- Sequence/Product ID
- Recipe/Calibration 호환성
- Saturation/Mean 등 선택적 Quality Gate

입력 계약이 깨졌으면 Algorithm을 실행하지 않는다.

### 3.4 Preprocessing

검사에 필요한 Gray/Filter/Normalize/Difference를 생성한다. 원본은 불변으로 보존하고 Parameter와 중간 Image를 추적 가능하게 한다.

### 3.5 Alignment

Mark를 검출하고 X/Y/Theta, Score, Residual을 반환한다. Align 실패를 제품 Missing으로 바꾸지 않는다. 일부 검사만 Align 없이 가능한지 Recipe 정책을 명시한다.

### 3.6 ROI Transform

Reference ROI를 Current Pose로 변환하고 경계/Mask를 검증한다. 어떤 ROI가 잘렸는지 Inspector가 모르게 숨기지 않는다.

### 3.7 Feature Extraction

Threshold/Edge/Blob/Matching 등 Image에서 후보를 만든다. 이 단계는 가능하면 Spec 판정을 하지 않고 Feature와 품질 지표를 반환한다.

### 3.8 Measurement

Feature를 Pixel/실제 단위의 Width/Area/Position/Score로 변환한다. Calibration ID와 단위를 Measurement에 포함한다.

### 3.9 Judgement

Recipe Spec, Guard Band, Invalid 상태로 OK/NG/Review/Error를 결정한다. 여러 항목의 Overall 규칙도 명시한다.

### 3.10 Result Finalize

Result는 확정 후 불변으로 취급한다.

- 모든 항목 Measurement/Spec/Verdict
- Align/Calibration/Recipe Version
- Error/Warning
- Timing
- Raw/NG/Overlay 경로

### 3.11 Review/Storage/CIM

동일 Result를 서로 다른 Consumer가 사용한다. 비동기 저장은 Cycle Time을 줄이지만 Queue Limit, Backpressure, 종료 시 Flush와 실패 Alarm이 필요하다.

### 3.12 Fail-fast와 Partial Result

Camera Frame Error처럼 이후 결과가 무의미하면 Fail-fast한다. 한 검사 항목만 실패하고 나머지가 유효하면 항목별 Invalid와 Overall 정책을 사용한다. 임의 기본값 `0`으로 채우지 않는다.

### 3.13 Determinism/Reproducibility

동일 Raw Image, Recipe Snapshot, Calibration/Algorithm Version이면 동일 Result가 나와야 한다. Thread 순서, Random Seed, Adaptive Parameter와 외부 상태를 통제한다.

### 3.14 Timing Budget

각 Stage의 Average뿐 아니라 P95/P99/Max를 본다. 저장/압축/Network를 검사 Thread에서 동기 실행하지 않되 Memory Queue가 무한 증가하지 않게 한다.

---

## 4. 그림으로 이해하기

```text
Frame+Metadata ──► Pure-ish Vision Pipeline ──► Final Result
                         │                           │
                    Stage traces                fan-out
                         │               ┌──────────┼─────────┐
                    Debug/Review         UI       Storage     CIM
```

```text
NG = valid inspection says product is bad
Error = system cannot produce a trustworthy judgement
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

- Product ID와 Frame ID 결합
- Mark Align 후 다수 ROI 검사
- 항목별 측정과 Overall 판정
- NG Image/Overlay Review
- CIM/MES 결과와 장비 분류 동기화
- 성능/오류 Monitoring

---

## 6. 숫자로 이해하기

### 예제 1: Cycle Time

```text
Acquire 15 + Validate 2 + Preprocess 12 + Align 35
+ ROI 3 + Inspect 48 + Finalize 5 = 120 ms
```

목표 150 ms이면 30 ms Margin이다. 동기 Image 저장 45 ms를 추가하면 초과한다.

### 예제 2: Queue Memory

12 MiB Raw+Overlay 묶음을 100개 Queue하면 약 1.17 GiB다. Queue 20개 제한이면 약 240 MiB이며 초과 시 NG 우선/Backpressure/Error 정책이 필요하다.

### 예제 3: Overall

10항목 중 8 OK, 1 NG, 1 Invalid라면 단순 Majority OK가 아니다. Recipe가 `Any NG→NG`, `Any required Invalid→Error`라면 Overall Error이며 NG 정보도 보존한다.

### 예제 4: Throughput

처리 평균 80 ms지만 P99가 180 ms이고 Input 간격이 100 ms면 순간 Queue가 증가한다. Average만으로 안정성을 판단하지 않는다.

---

## 7. C++ 구현

```cpp
#include <opencv2/opencv.hpp>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

enum class Verdict { Ok,Ng,Review,Error };

struct Frame final {cv::Mat image;std::uint64_t frameId{};std::string productId,cameraId;};
struct Recipe final {std::string id;std::uint32_t version{};cv::Rect referenceRoi;double threshold{},minArea{},maxArea{};};
struct AlignPose final {double tx{},ty{},thetaDegrees{},score{},rmsResidual{};bool valid{};};
struct Measurement final {std::string name;double value{},lower{},upper{};std::string unit;Verdict verdict{Verdict::Error};};
struct InspectionResult final {
 std::uint64_t frameId{};std::string productId,recipeId,error;
 std::uint32_t recipeVersion{};Verdict overall{Verdict::Error};
 AlignPose align;std::vector<Measurement> measurements;cv::Mat overlay;
 double elapsedMs{};
};

class IAligner {public:virtual ~IAligner()=default;virtual AlignPose Align(const cv::Mat&)const=0;};

class InspectionEngine final {
public:
 explicit InspectionEngine(const IAligner& aligner):aligner_(aligner){}

 [[nodiscard]] InspectionResult Inspect(const Frame& frame,const Recipe& recipe) const {
  const auto start=std::chrono::steady_clock::now();
  InspectionResult out;out.frameId=frame.frameId;out.productId=frame.productId;
  out.recipeId=recipe.id;out.recipeVersion=recipe.version;
  try {
   Validate(frame,recipe);
   cv::Mat gray;
   if(frame.image.channels()==1)gray=frame.image;
   else cv::cvtColor(frame.image,gray,cv::COLOR_BGR2GRAY);
   out.align=aligner_.Align(gray);
   if(!out.align.valid)throw std::runtime_error{"Alignment failed"};

   // Simplified translation-only ROI; production code applies X/Y/Theta polygon transform.
   const cv::Rect roi=recipe.referenceRoi+cv::Point{
       cvRound(out.align.tx),cvRound(out.align.ty)};
   const cv::Rect bounds{0,0,gray.cols,gray.rows};
   if((roi&bounds)!=roi)throw std::runtime_error{"ROI leaves image"};
   cv::Mat binary;cv::threshold(gray(roi),binary,recipe.threshold,255,cv::THRESH_BINARY);
   cv::Mat labels,stats,centroids;
   const int count=cv::connectedComponentsWithStats(binary,labels,stats,centroids,8);
   int largest=0;for(int i=1;i<count;++i)largest=std::max(largest,stats.at<int>(i,cv::CC_STAT_AREA));
   const bool ok=largest>=recipe.minArea&&largest<=recipe.maxArea;
   out.measurements.push_back({"largest_area",static_cast<double>(largest),
       recipe.minArea,recipe.maxArea,"px^2",ok?Verdict::Ok:Verdict::Ng});
   out.overall=ok?Verdict::Ok:Verdict::Ng;
  } catch(const std::exception& e) {out.overall=Verdict::Error;out.error=e.what();}
  out.elapsedMs=std::chrono::duration<double,std::milli>(
      std::chrono::steady_clock::now()-start).count();
  return out;
 }
private:
 static void Validate(const Frame& f,const Recipe& r){
  if(f.image.empty())throw std::invalid_argument{"Empty image"};
  if(r.id.empty()||r.referenceRoi.area()<=0||r.minArea>r.maxArea||
     r.threshold<0||r.threshold>255)throw std::invalid_argument{"Invalid recipe"};
 }
 const IAligner& aligner_;
};
```

예제 ROI는 코드 복잡도를 제한하기 위해 Translation만 적용한다. 실제 Engine은 [[12-roi-transform|Polygon X/Y/Theta Transform]]을 사용해야 한다. 이 제한을 숨기지 않는다.

### Unit Test 범위

- Empty/잘못된 Type/Recipe → Error
- Align 실패 → Error, Missing NG 아님
- ROI 경계 초과 → Error
- Spec 내부/외부 → OK/NG
- 동일 Input/Recipe → 동일 Measurement
- 저장 실패가 검사 Result를 변조하지 않음

---

## 8. 실무에서 발생하는 문제

1. Algorithm 함수가 Recipe Global 상태를 직접 읽음.
2. 검사 중 UI가 Recipe를 변경.
3. NG와 Error가 bool false 하나로 표현.
4. Buffer 재사용 후 비동기 저장이 깨진 Image 읽음.
5. 저장 Queue 무한 증가.
6. UI와 CIM이 다른 판정 로직 사용.
7. 중간 Image가 없어 NG 원인 재현 불가.
8. P99 지연과 Timeout 무시.

---

## 9. 흔한 오해

1. Pipeline은 OpenCV 함수 호출 순서만 뜻한다.
2. 검사 항목 NG와 Align Error는 같다.
3. 비동기화하면 무조건 빨라진다.
4. Result는 Overall bool이면 충분하다.
5. Recipe Version 없이 Image만 저장해도 재현된다.
6. 평균 처리 시간이 Cycle Time보다 작으면 안정적이다.

---

## 10. 면접에서 나올 수 있는 질문

1. **Pipeline 단계?** Acquisition→Preprocess→Align→ROI→Feature→Measure→Judge→Result.
2. **Measurement/Judgement 분리?** Spec 변경, 추적성과 재판정.
3. **NG/Error 차이?** 유효한 제품 불량과 신뢰 판정 불가.
4. **Recipe Snapshot?** 검사 중 Parameter 일관성과 재현성.
5. **비동기 저장 주의?** Buffer 수명, Queue Limit, Backpressure, 실패 Alarm.
6. **성능 평가?** Stage별 P50/P95/P99/Max와 Queue/Memory.

---

## 11. 실습 문제

1. 현재 장비 기능을 Pipeline Stage와 Data Contract에 매핑한다.
2. 각 Stage의 Error/NG/Warning 정책표를 만든다.
3. 150 ms Cycle Time Budget과 P99 목표를 배분한다.
4. Recipe 변경/Camera Timeout/저장 실패 Integration Test를 작성한다.

### Phase 14 미니 프로젝트

파일 Image Source, Fake Aligner, 3 Inspector, Result Writer를 조합해 Deterministic Pipeline과 Stage Timing/Intermediate Image/JSON Result를 구현한다.

---

## 12. Chapter 핵심 요약

- 🔴 Pipeline은 단계별 책임과 Data Contract다.
- 🔴 원본/Recipe Snapshot/Calibration Version을 고정한다.
- 🔴 Align/ROI 실패와 제품 NG를 분리한다.
- 🔴 Feature→Measurement→Judgement를 분리한다.
- 🔴 Final Result를 UI/Storage/CIM의 단일 Source로 사용한다.
- 🔴 비동기 저장은 Queue/Buffer 수명과 실패 정책이 필요하다.
- 🟠 Average가 아니라 Tail Latency와 Memory를 본다.

## 다음 학습 예고

17일차에는 Recipe/Parameter/Result Data Model과 실제 C++ 검사 SW Architecture를 설계한다.
