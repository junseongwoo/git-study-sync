# 19일차. Final Project — Mini Vision Inspection System

> 종합 프로젝트 · 권장 기간: 4~8주 · 대상: 370×470 Glass · 핵심: 광학→Align→검사→Result의 재현 가능한 연결

## 1. 프로젝트 목표

한 대의 Camera로 3개 Align Mark를 검출해 Glass 중심 기준 X/Y/Theta를 계산하고, Dynamic ROI에서 Edge와 Blob 검사를 수행하는 Mini 검사 시스템을 만든다. 실제 Camera가 없어도 File/Simulator 입력으로 Core를 완성하고 Adapter만 교체할 수 있어야 한다.

최종 결과는 단순히 Overlay가 보이는 프로그램이 아니다. 다음 질문에 답할 수 있어야 한다.

- 어떤 FOV와 mm/px 조건에서 촬영했는가?
- 어떤 Recipe/Calibration/SW로 검사했는가?
- Mark를 어떻게 찾고 Align 신뢰성을 어떻게 판정했는가?
- 어떤 수치가 어떤 Spec을 벗어나 NG가 되었는가?
- 같은 Raw Image를 Offline에서 동일하게 재현할 수 있는가?

---

## 2. 시스템 요구사항

### 기능 요구사항

- File Camera와 실제 Camera Adapter Interface
- Mono8 기준 입력 검증과 영상 품질 Gate
- 3-Mark 검출, Rigid Align, 잔차 평가
- Glass 중심 및 Dynamic ROI 계산
- Edge 폭 측정 1종, Blob 결함 검사 1종 이상
- px↔mm 단위 변환과 Calibration ID 확인
- 불변 Recipe Snapshot과 Safe Point 전환
- OK/NG/Review/Invalid/Error 판정
- Raw/Overlay/Result 저장과 Offline Replay
- Stage별 Timing, Queue Depth, Error Log

### 비기능 요구사항

- Core는 GUI, 파일 시스템, 특정 Camera SDK와 분리
- 모든 Queue는 유한하고 Full/Close 정책 보유
- 동일 입력의 결정성
- Resource의 소유권과 수명 문서화
- Unit/Golden/Replay/Integration/Soak Test

---

## 3. 광학과 좌표 전제

Glass 전체 370×470 mm를 한 장에 담는다면 실제 FOV는 설치 여유를 포함해 예를 들어 400×500 mm 이상이어야 한다. Sensor가 4,000×5,000 px일 때 단순 Sampling은 양축 0.1 mm/px다.

$$
r_x=400/4000=0.1\ \mathrm{mm/px}
$$

$$
r_y=500/5000=0.1\ \mathrm{mm/px}
$$

0.05 mm 결함은 0.5 px이므로 이 구성으로 안정적으로 형상을 검사하기 어렵다. 전체 Align Camera와 국부 고해상도 검사 Camera를 분리하거나, 더 높은 해상도·작은 FOV·Scan 방식을 검토해야 한다. 최종 설계에서는 목표 결함 크기와 필요한 Pixel 수를 먼저 적고 광학 구성을 결정한다.

### 좌표계

```text
Recipe Glass Reference (mm, center origin)
        │ alignment pose
        ▼
Current Glass / Current Image (px)
        │ image-machine calibration
        ▼
Machine / Stage (mm)
```

각 Transform은 Source, Target, 단위, 축 방향, 적용 시점을 이름과 문서에 명시한다.

---

## 4. 전체 Architecture

```text
Recipe Editor ──► Validator ──► Versioned Store
                                      │ snapshot
Trigger ─► Frame Source ─► Quality Gate ─► Mark Detectors
                                             │ 3 poses
                                             ▼
                                      Alignment Solver
                                             │ R,t,residual
                                             ▼
                                      Dynamic ROI Mapper
                                       ┌─────┴─────┐
                                  Edge Inspector  Blob Inspector
                                       └─────┬─────┘
                                             ▼
                                      Judgement Policy
                                             ▼
                                        Result Builder
                                  ┌──────────┼──────────┐
                              Image Sink  Result Sink  Review
```

Orchestrator가 순서를 제어하되 알고리즘 구현을 직접 포함하지 않는다. Inspector는 영상과 Type-safe Parameter를 받고 Domain Measurement를 반환한다.

---

## 5. Domain Model과 Interface

```cpp
#pragma once

#include <chrono>
#include <cstdint>
#include <memory>
#include <opencv2/core.hpp>
#include <optional>
#include <string>
#include <vector>

enum class Verdict { Ok, Ng, Review, Invalid, Error };

struct Pose2d {
    double xMm{};
    double yMm{};
    double thetaDeg{};
};

struct AlignResult {
    Verdict verdict{Verdict::Invalid};
    Pose2d currentGlassCenter;
    double rmsResidualPx{};
    double maxResidualPx{};
    std::vector<cv::Point2d> detectedMarksPx;
    std::string reasonCode;
};

struct MarkDetection {
    Verdict verdict{Verdict::Invalid};
    std::optional<cv::Point2d> centerPx;
    double score{};
    std::string reasonCode;
};

struct Measurement {
    std::string itemId;
    std::optional<double> value;
    std::string unit;
    double lower{};
    double upper{};
    Verdict verdict{Verdict::Invalid};
    std::string reasonCode;
};

struct FrameContext {
    std::uint64_t frameId{};
    std::string productId;
    cv::Mat image;
    std::shared_ptr<const struct InspectionRecipe> recipe;
    std::chrono::steady_clock::time_point acquiredAt;
};

class IMarkDetector {
public:
    virtual ~IMarkDetector() = default;
    virtual MarkDetection detect(const cv::Mat& image,
                                 const cv::Rect& searchRoi) const = 0;
};

class IInspector {
public:
    virtual ~IInspector() = default;
    virtual Measurement inspect(const cv::Mat& image,
                                const cv::Mat& roiMask) const = 0;
};
```

실제 구현에서는 Mark 검출에 Peak Ratio와 Covariance/Uncertainty도 추가한다. 위 코드는 Component 경계를 보여주는 최소 골격이다.

### 소유권 원칙

- `FrameContext::image`는 OpenCV 소유 Buffer이거나 Camera Handle 수명 객체를 함께 가진다.
- Recipe는 `shared_ptr<const ...>`로 제품 전체에서 고정한다.
- Inspector는 입력 영상을 수정하지 않는다.
- Overlay는 Raw와 별도 Mat으로 만든다.

---

## 6. Align 상세 흐름

### Teach Mode

1. 기준 Glass와 안정된 광학 조건을 준비한다.
2. 원/십자 등 기하 Mark는 Feature 규칙으로, 복잡 Mark는 Template으로 검출한다.
3. Mark M1/M2/M3의 중심과 Glass 중심 기준 설계 좌표를 연결한다.
4. Search ROI와 Angle/Score 범위를 저장한다.
5. 반복 촬영으로 Mark 중심 표준편차를 측정한다.
6. Template, Recipe, Calibration의 ID와 촬영 조건을 저장한다.

### Run Mode

1. Search ROI에서 각 Mark 후보를 검출한다.
2. ID, 점 간 거리, 삼각형 방향으로 대응을 검증한다.
3. 세 점의 Rigid Transform \(q_i=Rp_i+t\)를 추정한다.
4. Mark별 잔차와 RMS/Max를 계산한다.
5. Quality Gate 통과 시 Glass 중심과 Dynamic ROI를 변환한다.
6. 실패하면 잘못된 ROI 검사를 계속하지 않고 Invalid/Error 정책을 적용한다.

### Stage 보정

검출된 Glass Pose를 기준으로 보내기 위한 Image 보정과 Stage 명령은 같은 값이 아닐 수 있다. Camera가 고정되고 Stage가 Glass를 움직이면 필요한 명령은 보통 측정 변위의 반대 방향이지만, 회전 중심 Offset과 Image–Machine Transform이 포함된다. +X/+Y/+Theta 단위 이동 실험으로 부호와 Matrix 방향을 검증한다.

---

## 7. 검사와 판정

### Edge 검사

- Align된 측정 ROI에서 여러 Scan Line 평균
- 극성에 맞는 두 Edge와 Subpixel 위치
- px 폭과 Calibration 기반 mm 폭
- Edge Strength와 후보 수 Quality Gate

### Blob 검사

- 배경 보정/Threshold/Morphology
- Area, Centroid, Circularity, Border Touch
- 결함 크기와 Kernel 영향 검증
- 면적 px²와 mm² 단위 분리

### Overall Verdict 예시

```text
System Error 존재 → Error
필수 Align/Measurement 무효 → Invalid
유효한 Spec 위반 존재 → NG
Guard Band/정책 대상 → Review
그 외 → OK
```

Mark 미검출을 곧바로 제품 NG로 셀지, 재촬영 후 Invalid로 처리할지는 공정 정책으로 결정한다. 수율 통계에는 유효한 제품 판정만 포함한다.

---

## 8. Recipe와 Result

### Recipe 최소 항목

- Schema Version, Recipe ID/Revision, Product Code
- Camera/조명/영상 품질 Parameter
- Mark Reference 좌표, Detector, Search ROI, Score/잔차 기준
- Calibration ID와 Image Size
- 검사 ROI, Inspector Parameter, Spec/Guard Band
- Overall Rule, Retry, 저장/보존 정책

### Result 최소 항목

- Result/Lot/Product/Frame/Camera ID와 UTC Timestamp
- Recipe Revision/Content Hash, Calibration ID, SW Build
- 영상 품질, Align Pose/Score/Residual
- 검사별 Measurement/Spec/Verdict/Reason
- Overall Verdict와 Stage Timing
- Raw/Overlay URI와 저장/전송 상태

활성 Recipe는 수정하지 않고 새 Revision을 생성한다. 검사 시작 시 Snapshot을 고정하고 새 Revision은 다음 제품부터 적용한다.

---

## 9. 개발 Milestone

### M1. Offline Core

- File Camera, Domain Type, Recipe Validator
- 합성 영상으로 Threshold/Edge/Blob Test
- Result를 메모리와 JSON 형태로 출력

### M2. Calibration과 Align

- Image–Machine Calibration Dataset과 독립 검증
- 3-Mark Detector/Solver/Residual Gate
- Dynamic ROI와 좌표 왕복 Test

### M3. Inspection Pipeline

- Inspector Registry와 Overall Policy
- Stage Timing, Raw/Overlay, Offline Replay
- NG/Invalid/Error 분리

### M4. 장비 동작

- 실제 Camera/조명/Stage Adapter
- Trigger, Timeout, Retry, Interlock
- Safe Point Recipe 전환과 Bounded Queue

### M5. 검증과 운영

- Golden/Integration/Soak Test
- Dataset 고정 평가와 Worst Case 분석
- Review/CIM 연계와 장애 복구 절차

각 Milestone은 Demo가 아니라 자동 Test와 수치 Report를 통과해야 끝난다.

---

## 10. 검증 계획

### 정확도

- Mark 검출 반복성: 고정 Glass 30회 이상의 σ/Max
- Align: 알려진 X/Y/Theta 이동 Ground Truth 대비 오차
- Calibration: 독립 Validation RMS/Max/Bias
- Edge/Blob: Ground Truth 대비 Mean/Std/Max
- Dataset: Detection Rate와 False Positive Rate, Sample 수

### 성능

- Stage별 평균/P95/P99/Max
- 입력/처리/저장 처리량과 Queue Depth
- CPU/메모리/Handle 추세
- 8시간 이상 Soak Test와 정상 종료

### 장애

- Mark 0/1/2개, 가짜 Mark, Score 경계
- Camera Timeout/Frame 손상/순서 오류
- Calibration·해상도 불일치
- Disk Full/DB·Network 단절
- Recipe 전환 중 Trigger
- Queue Full과 종료 중 잔여 Frame

### Dataset 분리

Parameter 선택에 쓴 개발 Dataset과 최종 평가 Dataset을 분리한다. 실제 정상 Hard Negative와 결함 경계 크기를 충분히 포함한다.

---

## 11. 최종 합격 기준

- [ ] 목표 결함 크기와 광학 Sampling의 타당성 설명
- [ ] Mark 3개의 ID/중심/기준 좌표/검출 방식 문서화
- [ ] X/Y/Theta와 Glass 중심 오차가 요구값 충족
- [ ] 독립점 Calibration RMS/Max가 요구값 충족
- [ ] Edge/Blob Detection Rate와 FPR가 고정 평가 Set 기준 충족
- [ ] 모든 Result가 Recipe/Calibration/SW/Raw와 추적 가능
- [ ] 동일 Raw/Recipe 100회 결과 결정성
- [ ] NG/Invalid/Error와 저장/전송 실패 분리
- [ ] P99 Cycle Time과 Queue 상한 정책 충족
- [ ] Soak Test에서 Resource 증가 없음
- [ ] Recipe Safe Point 전환 Test 통과
- [ ] 현재 UI 값 없이 Offline Replay 가능

요구 수치는 프로젝트 시작 전에 합의해 빈칸으로라도 명시한다. 시험이 끝난 뒤 결과에 맞춰 합격선을 바꾸지 않는다.

---

## 12. 최종 발표와 면접 답변

### 5분 발표 순서

1. 대상과 요구 결함/정확도/Cycle Time
2. FOV, mm/px, 조명과 광학 Trade-off
3. 3-Mark Align과 Glass 중심 좌표
4. Calibration과 Dynamic ROI
5. Edge/Blob 검사 및 판정
6. Recipe/Result/Replay Architecture
7. 정량 성능과 가장 어려웠던 실패 사례

### 핵심 30초 답변

“370×470 Glass의 중심 기준으로 3개 Mark Reference 좌표를 등록하고, 생산 영상에서 Mark 중심을 검출해 최소제곱 Rigid Transform을 계산했습니다. 잔차 Gate를 통과한 Pose로 ROI를 변환하고 Edge와 Blob 검사를 수행했습니다. 한 제품에는 불변 Recipe Snapshot을 적용했으며 Result에 Calibration과 SW 버전, Raw를 연결해 Offline Replay가 가능하게 했습니다. 성능은 Align 반복성, 독립 Calibration 오차, Detection Rate/FPR, P99 Cycle Time으로 검증했습니다.”

### 다음 확장

- Multi-camera 좌표 통합과 Hand-eye Calibration
- Telecentric/Line-scan 광학
- Height 변화가 있는 3D 검사
- 통계적 공정 관리와 Drift Monitoring
- 규칙 기반이 불안정한 결함에 대한 DL 후보 비교

Deep Learning은 Dataset Label 품질, 배포 환경, Explainability, Drift, Fail-safe 기준까지 준비됐을 때 추가한다. 먼저 광학과 좌표, 결과 추적이 안정되어야 한다.
