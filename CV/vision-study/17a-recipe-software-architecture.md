# 17일차 A. Recipe와 검사 장비 SW 아키텍처

> Phase 15 · 권장 학습 시간: 12~16시간 · 난이도: 중급~고급 · 핵심: 재현성, 버전, 추적성

## 1. 이 Chapter에서 배우는 것

- Recipe가 단순한 설정 파일이 아닌 이유
- Parameter, Calibration, Result, Image의 관계
- 운전 중 설정 변경에도 한 제품의 검사 조건을 고정하는 방법
- 제품 NG와 장비·통신·알고리즘 오류를 구분하는 방법
- 결과를 사후 재현할 수 있는 데이터 구조
- Recipe 검증, 버전 이관, 배포와 되돌리기 전략
- C++17에서 불변 Recipe Snapshot을 사용하는 구조

### 실무 목표

“어떤 영상이 어떤 조건으로 검사되어 왜 NG가 되었는가?”를 몇 달 후에도 설명할 수 있는 구조를 설계한다. UI의 현재 값이 아니라 **검사 시작 시점에 확정된 Recipe, Calibration, SW Build, 원본 영상**을 결과와 연결하는 것이 핵심이다.

---

## 2. 선수 지식

- [[16b-inspection-pipeline|Inspection Pipeline과 Result]]
- [[15-coordinate-systems|좌표계와 Transform Chain]]
- [[14a-calibration-coordinate-transform|Image–Machine Calibration]]
- C++ 구조체, `enum class`, 스마트 포인터의 기본 사용법

---

## 3. 핵심 개념

### 3.1 Recipe란 무엇인가

Recipe는 특정 제품을 동일한 조건으로 검사하기 위한 **버전이 있는 실행 계약**이다.

- 제품과 공정 식별자
- Camera: 노출, Gain, Trigger, Pixel Format
- Illumination: 채널별 밝기와 점등 순서
- Alignment: Mark, 기준 좌표, 탐색 영역, Score 기준
- ROI: 기준 좌표계에서 정의한 검사 영역
- Algorithm: 종류, Parameter, 전처리 순서
- Spec: 상·하한, 판정 규칙, Guard Band
- Calibration 참조 ID와 유효 조건
- 저장 정책: 원본, Overlay, NG 영상, 중간 영상

Recipe는 “현재 화면의 입력값 묶음”과 다르다. 승인·활성화된 Recipe는 직접 수정하지 않고 새 Revision을 만든다.

### 3.2 구분해야 할 네 가지 버전

| 구분 | 의미 | 변경 예시 |
|---|---|---|
| Schema Version | 파일 구조의 형식 | 새 필드 추가, 단위 표현 변경 |
| Recipe Revision | 제품 검사 조건 | Threshold 110 → 118 |
| Calibration ID | 좌표·광학 보정 결과 | Camera 재장착 후 재교정 |
| Algorithm/SW Build | 실행 코드 | Blob 필터 버그 수정 |

Recipe Revision이 같아도 Calibration이나 SW Build가 다르면 결과가 달라질 수 있다. 따라서 Result에는 네 정보를 모두 남겨야 한다.

### 3.3 기준 좌표로 ROI를 저장한다

ROI를 현재 영상 Pixel에만 저장하면 Glass가 이동하거나 회전했을 때 검사 위치가 틀어진다. ROI는 Recipe Reference 좌표로 저장하고, 매 제품에서 계산한 Align Transform으로 현재 영상에 변환한다.

```text
Recipe Reference ROI
        │ current alignment T
        ▼
Current Image ROI ──► inspection
```

좌표의 단위와 기준점을 필드 이름에 드러내야 한다. `x`보다 `referenceX_mm`, `imageU_px`가 안전하다.

### 3.4 불변 Snapshot

검사 도중 작업자가 Threshold를 바꾸면 한 제품의 ROI마다 서로 다른 값이 적용될 수 있다. 제품 검사 시작 시 활성 Recipe의 불변 Snapshot을 얻고, 모든 Stage가 같은 Snapshot을 공유해야 한다.

```text
Draft 편집 → Validate → Approve → Activate
                                  │
Trigger ──► Snapshot R42 ──► 모든 검사 Stage ──► Result(recipe=R42)
                     새 R43 활성화 ──► 다음 제품부터 적용
```

### 3.5 NG와 Error는 다른 상태다

- **OK**: 측정이 유효하고 Spec 안이다.
- **NG**: 측정이 유효하지만 Spec 밖이다.
- **Review**: 경계 또는 정책상 작업자 확인이 필요하다.
- **Invalid**: 영상 품질이나 Feature 검출 실패로 측정이 성립하지 않는다.
- **Error**: Camera, 파일, 메모리, 통신, 내부 예외 등 시스템 문제다.

Feature를 찾지 못한 경우가 결함으로 정의된 검사라면 NG일 수 있지만, Align Mark 검출 실패로 검사 위치 자체가 불명확하다면 Invalid 또는 Error 정책이 적절하다. 이 결정은 Recipe에 명시한다.

---

## 4. 수식과 정량 설계

### 4.1 Spec 판정과 Guard Band

측정값 \(m\), 하한 \(L\), 상한 \(U\)일 때 기본 판정은 다음과 같다.

$$
\mathrm{OK} \iff L \le m \le U
$$

양쪽 Guard Band \(g\)를 두면 자동 OK 구간은 다음처럼 좁아진다.

$$
L + g \le m \le U - g
$$

고객 Spec이 9.90~10.10 mm이고 \(g=0.02\) mm이면 자동 OK 범위는 9.92~10.08 mm다. 화면 표시값이 아니라 원 측정값으로 판정한 뒤 표시만 반올림한다.

### 4.2 저장 용량 추정

2,048×2,048 Mono8 원본 한 장은 4.00 MiB다.

$$
2048 \times 2048 \times 1 = 4{,}194{,}304\ \mathrm{byte}=4.00\ \mathrm{MiB}
$$

제품당 4장, 하루 20,000개를 무압축 저장하면 약 312.5 GiB/day다.

$$
4.00\ \mathrm{MiB} \times 4 \times 20{,}000=320{,}000\ \mathrm{MiB}=312.5\ \mathrm{GiB}
$$

OK는 Sampling, NG는 전량, Error는 원본과 진단 정보를 전량 저장하는 식으로 정책과 보존 기간을 설계한다.

### 4.3 추적성 최소 Key

```text
lotId + productId + frameId + cameraId
+ recipeId/revision + calibrationId + softwareBuild
+ timestamp + resultId
```

시간만으로 영상을 연결하면 Camera 간 동시 촬영이나 시계 보정 때문에 충돌할 수 있다. 생성 시점에 고유 Result ID를 발급한다.

---

## 5. C++17 데이터 모델 예제

```cpp
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <utility>
#include <vector>

enum class Verdict { Ok, Ng, Review, Invalid, Error };
enum class Unit { Pixel, Millimeter, SquareMillimeter, Degree, Dimensionless };

struct RangeSpec {
    double lower{};
    double upper{};
    double guardBand{};
    Unit unit{Unit::Dimensionless};
};

struct CameraRecipe {
    std::string cameraId;
    double exposureUs{};
    double gainDb{};
    int illuminationChannel{};
    double illuminationPercent{};
};

struct RoiRecipe {
    std::string roiId;
    std::vector<std::pair<double, double>> referencePolygonMm;
    std::string inspectorType;
    RangeSpec spec;
};

struct InspectionRecipe {
    std::uint32_t schemaVersion{};
    std::string recipeId;
    std::uint32_t revision{};
    std::string productCode;
    std::string calibrationId;
    std::vector<CameraRecipe> cameras;
    std::vector<RoiRecipe> rois;
};

struct Measurement {
    std::string name;
    std::optional<double> value;
    Unit unit{Unit::Dimensionless};
    RangeSpec appliedSpec;
    Verdict verdict{Verdict::Invalid};
    std::string reasonCode;
};

struct InspectionResult {
    std::string resultId;
    std::string lotId;
    std::string productId;
    std::string recipeId;
    std::uint32_t recipeRevision{};
    std::string calibrationId;
    std::string softwareBuild;
    Verdict overall{Verdict::Invalid};
    std::vector<Measurement> measurements;
    std::vector<std::string> imagePaths;
};
```

`Measurement::value`가 없을 수 있으므로 0.0 같은 가짜 값을 넣지 않는다. 값 부재와 실제 0은 의미가 다르다.

### 5.1 Recipe 의미 검증

```cpp
#include <cmath>
#include <string>
#include <vector>

struct ValidationIssue { std::string path; std::string message; };

std::vector<ValidationIssue> validateRecipe(const InspectionRecipe& recipe) {
    std::vector<ValidationIssue> issues;
    if (recipe.recipeId.empty()) issues.push_back({"recipeId", "must not be empty"});
    if (recipe.calibrationId.empty()) issues.push_back({"calibrationId", "is required"});

    for (std::size_t i = 0; i < recipe.cameras.size(); ++i) {
        const auto& camera = recipe.cameras[i];
        const std::string base = "cameras[" + std::to_string(i) + "]";
        if (!std::isfinite(camera.exposureUs) || camera.exposureUs <= 0.0)
            issues.push_back({base + ".exposureUs", "must be finite and positive"});
        if (!std::isfinite(camera.gainDb))
            issues.push_back({base + ".gainDb", "must be finite"});
        if (!std::isfinite(camera.illuminationPercent) ||
            camera.illuminationPercent < 0.0 || camera.illuminationPercent > 100.0)
            issues.push_back({base + ".illuminationPercent", "must be in [0, 100]"});
    }
    for (std::size_t i = 0; i < recipe.rois.size(); ++i) {
        const auto& roi = recipe.rois[i];
        const std::string base = "rois[" + std::to_string(i) + "]";
        if (roi.referencePolygonMm.size() < 3U)
            issues.push_back({base + ".referencePolygonMm", "needs at least 3 points"});
        if (!(roi.spec.lower <= roi.spec.upper))
            issues.push_back({base + ".spec", "lower must not exceed upper"});
        const double halfWidth = (roi.spec.upper - roi.spec.lower) * 0.5;
        if (!std::isfinite(roi.spec.guardBand) ||
            roi.spec.guardBand < 0.0 || roi.spec.guardBand > halfWidth)
            issues.push_back({base + ".spec.guardBand", "is outside valid range"});
    }
    return issues;
}
```

Parser가 성공했다는 사실은 Recipe가 유효하다는 뜻이 아니다. `NaN`, 무한대, 범위 역전, 빈 ROI, 중복 ID, 지원하지 않는 Camera 조합까지 검증한다.

### 5.2 불변 Snapshot 저장소

```cpp
#include <memory>
#include <mutex>
#include <stdexcept>
#include <utility>

class RecipeStore {
public:
    void activate(InspectionRecipe recipe) {
        const auto issues = validateRecipe(recipe);
        if (!issues.empty())
            throw std::invalid_argument("invalid recipe: " + issues.front().path);

        auto next = std::make_shared<const InspectionRecipe>(std::move(recipe));
        std::lock_guard<std::mutex> lock(mutex_);
        active_ = std::move(next);
    }

    std::shared_ptr<const InspectionRecipe> snapshot() const {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!active_) throw std::runtime_error("no active recipe");
        return active_;
    }

private:
    mutable std::mutex mutex_;
    std::shared_ptr<const InspectionRecipe> active_;
};
```

검사 Thread는 시작할 때 Snapshot을 한 번 받아 완료할 때까지 유지한다. 실제 장비에서는 Camera/조명 변경과 Recipe 활성화를 제품 사이 Safe Point에서 원자적으로 묶어야 한다.

---

## 6. SW 아키텍처

```text
UI/Recipe Editor
   │ draft, validation, approval
   ▼
Recipe Service ──► Versioned Repository
   │ immutable snapshot
   ▼
Inspection Orchestrator
   ├─ Acquisition Adapter
   ├─ Alignment Service
   ├─ Inspector Registry
   ├─ Judgement Policy
   └─ Result Builder
             ├─ Result DB/CIM
             ├─ Image Storage
             └─ Review UI
```

- UI는 검사 알고리즘을 직접 호출하지 않는다.
- Inspector는 화면이나 DB에 의존하지 않고 입력, Parameter, Calibration을 받아 결과를 반환한다.
- Result Builder가 공통 추적 정보를 한 번만 확정한다.
- 저장 실패가 검사 판정을 바꾸지 않도록 판정과 전송 상태를 분리한다.

### 6.1 Transactional Activation

1. Draft를 별도 공간에서 편집한다.
2. Schema와 의미 검증을 수행한다.
3. Camera/조명/Calibration의 존재와 호환성을 확인한다.
4. 장비가 제품 사이 Safe Point인지 확인한다.
5. 하드웨어 설정 적용에 성공하면 Snapshot을 활성화한다.
6. 일부 적용 실패 시 이전 설정으로 복구하고 Error를 기록한다.

### 6.2 Result는 append-only로 취급한다

재판정이 필요하면 기존 Result를 덮어쓰지 말고 `parentResultId`, 재판정 이유, 새 Recipe/SW 버전을 가진 새 Result를 생성한다.

---

## 7. Recipe 파일과 이관 전략

- 단위를 명시한다. `exposureUs`, `diameterMm`처럼 이름에 포함한다.
- 알 수 없는 필드와 누락 필드 정책을 정한다.
- 저장 전 정규화하고 Hash 또는 서명을 남긴다.
- Schema Migration은 `v1 → v2 → v3`처럼 단계별 순수 변환으로 만든다.
- Migration 후 반드시 현재 Validator를 다시 실행한다.
- 원본 파일과 변환 결과를 모두 추적 가능하게 보관한다.

```text
load bytes → parse → schema migrate → semantic validate
           → dependency validate → immutable domain object
```

파일명만 같고 내용이 바뀌는 문제를 막으려면 활성화 시 계산한 Content Hash도 Result에 넣는 것이 좋다.

---

## 8. 결과와 영상 저장 정책

- Raw: 재검증이 가능한 원본. 가능하면 압축 전 Bit Depth 보존
- Display: Review UI용 밝기 변환 영상
- Overlay: ROI, Feature, 수치, 판정을 그린 파생 영상
- Intermediate: 문제 분석을 위한 Threshold/Edge/Mask 등

Overlay만 저장하면 원 알고리즘을 재실행할 수 없다. 저장 실패가 발생해도 검사 결과 NG를 OK로 바꾸지 않고 보관 상태를 `StorageError`로 별도 기록한다. 장비 정지·알람 여부는 운영 정책으로 결정한다.

---

## 9. 실무 실패 사례와 진단

### 사례 1. 같은 제품인데 재검사 결과가 다르다

- 확인: Raw, Recipe Hash, Calibration ID, SW Build, OpenCV/SDK 버전
- 원인: UI의 현재 Recipe로 재실행, 자동 노출, 비결정적 병렬 순서
- 대책: Result가 참조한 Snapshot으로 Offline Replay한다.

### 사례 2. Recipe 변경 직후 몇 개 제품만 이상하다

- 확인: Trigger/활성화 시각, Frame별 Revision, Camera 설정 ACK
- 원인: 운전 중 객체 직접 수정, Camera와 Algorithm 적용 시점 불일치
- 대책: 불변 Snapshot과 Safe Point Activation을 사용한다.

### 사례 3. Calibration이 바뀌었는데 이전 ROI를 쓴다

- 확인: Recipe 요구 Calibration ID와 실제 활성 ID
- 원인: ID가 아닌 최신 파일명만 참조
- 대책: 명시적 ID와 Camera/렌즈/해상도 호환성을 확인한다.

### 사례 4. 0.0 값이 정상 측정인지 실패인지 모른다

- 원인: 실패를 숫자 Sentinel로 표현
- 대책: `optional`, Verdict, Reason Code를 별도 필드로 둔다.

---

## 10. 실습 과제

1. Camera 1대, 조명 2채널, Align Mark 3개, Dynamic ROI 4개인 Glass 검사 Recipe를 설계한다.
2. Scratch 초과, Mark 미검출, Camera Timeout, Calibration 만료, DB 단절을 NG/Invalid/Error로 분류하고 장비 동작을 정한다.
3. 과거 한 제품을 현재 UI 값 없이 재실행하기 위한 입력과 버전을 나열한다.
4. Recipe 활성화 일부 실패 시 Rollback Sequence를 상태도로 그린다.

---

## 11. 이해 점검 문제

1. Schema Version과 Recipe Revision의 차이는 무엇인가?
2. 검사 시작 시 Snapshot을 고정해야 하는 이유는 무엇인가?
3. ROI를 Reference 좌표로 저장하는 이유는 무엇인가?
4. Feature 미검출이 항상 NG가 아닌 이유는 무엇인가?
5. Result에 Calibration ID와 SW Build가 필요한 이유는 무엇인가?
6. Overlay만 저장했을 때 재현성 문제는 무엇인가?
7. Recipe 활성화를 Safe Point에서 수행해야 하는 이유는 무엇인가?
8. 저장 실패와 검사 판정을 분리해야 하는 이유는 무엇인가?

---

## 12. 면접 질문 6개

### Q1. Recipe를 어떻게 정의하겠습니까?
- 초보자: 제품별 검사 설정의 묶음입니다.
- 실무자: Camera·조명·Align·ROI·Algorithm·Spec·Calibration 참조를 포함한 버전 있는 실행 계약입니다.
- 30초 답변: 승인 Recipe를 불변 Snapshot으로 적용하고 Revision·Calibration·SW Build를 Result에 남겨 재현성을 확보합니다.

### Q2. 운전 중 Recipe 변경을 어떻게 처리합니까?
- 초보자: 검사가 끝난 다음 변경합니다.
- 실무자: Draft 검증 후 Safe Point에서 하드웨어 설정과 Snapshot을 원자적으로 전환합니다.
- 30초 답변: 현재 제품은 기존 Snapshot으로 끝내고 다음 Trigger부터 새 Revision을 사용합니다.

### Q3. NG와 Error의 차이는 무엇입니까?
- 초보자: NG는 제품 불량이고 Error는 장비 문제입니다.
- 실무자: NG는 유효 측정의 Spec 위반이고 Error는 검사가 정상 수행되지 못한 상태입니다.
- 30초 답변: Invalid/Error는 별도 Reason Code와 장비 정책을 가져야 합니다.

### Q4. 결과 재현에 어떤 정보가 필요합니까?
- 초보자: 원본 영상과 검사 조건입니다.
- 실무자: Raw, Recipe, Calibration, SW Build, Camera 조건과 입력 ID가 필요합니다.
- 30초 답변: Result ID를 기준으로 원본과 네 가지 버전을 고정해 Offline Replay가 가능해야 합니다.

### Q5. Recipe 파일을 읽었으면 바로 적용해도 됩니까?
- 초보자: 형식이 맞는지 확인해야 합니다.
- 실무자: Parse 외에 수치 범위, ID, ROI, Calibration/Camera 호환성까지 검증합니다.
- 30초 답변: Parse→Migration→의미/의존성 검증 후 불변 객체로 활성화합니다.

### Q6. 검사 영상 저장 정책은 어떻게 정합니까?
- 초보자: NG 영상을 우선 저장합니다.
- 실무자: 데이터량, 추적성, 보존 기간을 고려해 OK Sampling과 NG/Error 저장을 구분합니다.
- 30초 답변: Raw는 재실행용, Overlay는 Review용으로 분리하고 일일 용량과 장애 정책까지 설계합니다.

---

## 다음 학습

[[17b-modern-cpp-opencv|17일차 B. Modern C++17과 OpenCV 구현 원칙]]에서 메모리 수명, RAII, 오류 처리, 동시성, 테스트 관점으로 구현한다.
