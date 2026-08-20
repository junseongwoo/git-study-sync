# 20일차 Advanced. 산업 검사에서 딥러닝 Vision을 선택하는 기준

> Advanced 선택 과정 · 권장 학습 시간: 8~12시간 · 우선순위: 🟡 알아두면 좋음 · 전제: 전통 머신비전 Pipeline 완성

## 1. 이 Chapter에서 배우는 것

- 전통 알고리즘이 어려운 문제와 광학·Rule 개선으로 풀 문제의 구분
- Classification, Detection, Segmentation, Anomaly Detection의 출력 차이
- Dataset 분리, Label 품질, 지표, Threshold 선정
- C++ 검사 Pipeline에 Model Inference를 넣는 위치
- Model Version, Fail-safe, Drift, Replay 운영 원칙

### 실무 목표

딥러닝을 “정확도가 좋아 보이는 Black Box”로 추가하지 않고, 입력 계약과 출력 단위, 실패 상태, 고정 평가 Dataset, 배포 Version을 가진 하나의 Inspector로 다룬다.

---

## 2. 선수 지식

- 🔴 [[07-illumination|조명과 Contrast]]
- 🔴 [[16a-inspection-algorithms|전통 검사 알고리즘]]
- 🔴 [[16b-inspection-pipeline|검사 Pipeline]]
- 🔴 [[17a-recipe-software-architecture|Recipe와 Result Traceability]]
- 🟠 [[17b-modern-cpp-opencv|C++ Buffer와 Test]]

딥러닝은 Focus 불량, Saturation, 해상도 부족, 흔들림, 잘못된 Label을 자동으로 해결하지 않는다.

---

## 3. 핵심 개념

| 종류 | 입력→출력 | 검사 예 | 주의점 |
|---|---|---|---|
| Classification | ROI→Class/Score | 부품 방향 정상/역방향 | 위치와 크기를 직접 주지 않음 |
| Object Detection | Image→Box/Class/Score | 이물 위치와 종류 | 작은 결함 Box 품질 |
| Segmentation | Pixel→Class/Probability | Scratch 영역 | Label 비용과 경계 오차 |
| Anomaly Detection | 정상 대비 이상 Score/Map | 종류가 다양한 외관 이상 | 정상 Dataset 범위와 Threshold |

### 전통 방식이 우선인 경우

- 치수, 위치, 원/Hole처럼 형상이 명확하다.
- 조명과 Threshold로 대상/배경이 안정적으로 분리된다.
- 결과 설명과 Subpixel 측정이 중요하다.
- 결함 Sample이 적고 Spec이 수치로 정의된다.

### 딥러닝 후보인 경우

- Texture와 결함 변동이 크고 Rule 조합이 지나치게 복잡하다.
- 정상 외관 변동과 결함 경계가 사람이 보는 Pattern에 가깝다.
- 충분하고 대표성 있는 Dataset과 Label 검수 체계가 있다.
- 배포, 재학습, Drift Monitoring 비용을 감당할 수 있다.

---

## 4. 그림으로 이해하기

```text
Camera/Optics
    │
    ▼
Image Quality Gate ──fail──► Invalid/Error
    │ pass
    ▼
Alignment → Dynamic ROI → Deterministic Preprocess
                              │
                              ▼
                         Model Inference
                              │ score/map
                              ▼
                     Postprocess + Rule/Spec
                              │
                              ▼
                    Result + Model Version + Raw
```

Model이 Align과 Calibration을 무조건 대체하는 것은 아니다. 먼저 안정된 ROI를 제공하면 Dataset 변동과 Model 부담을 줄일 수 있다.

---

## 5. 실제 검사 장비에서 어디에 사용하는가

- 반복 Texture 위의 비정형 Scratch/오염
- Rule로 열거하기 어려운 외관 등급
- 정상 Sample은 많지만 결함 종류가 계속 추가되는 Anomaly Screening
- Detection/Segmentation으로 후보를 찾고 전통 측정으로 크기를 판정하는 Hybrid 검사

치수 측정은 Edge/Calibration으로 수행하고, 표면 이상 후보만 Model이 찾는 Hybrid가 실무적으로 설명 가능하고 안전한 경우가 많다.

---

## 6. 숫자로 이해하기

### 예제 1. Confusion Matrix

결함 200개 중 190개 검출, 정상 1,000개 중 30개 오검이라면:

$$
\mathrm{Recall}=190/200=95\%
$$

$$
\mathrm{FPR}=30/1000=3\%
$$

전체 Accuracy는 `(190+970)/1200 ≈ 96.67%`지만 결함 10개를 놓쳤다. 검사에서는 Class 불균형 때문에 Accuracy 하나만 보고 판단하면 안 된다.

### 예제 2. Inference 처리량

Camera가 20 fps이고 Model P99 Inference가 60 ms라면 단일 순차 Worker의 최대 처리량은 약 16.7 fps다.

$$
1000/60\approx16.7\ \mathrm{frame/s}
$$

입력이 더 빠르므로 Queue를 키우는 것으로 해결되지 않는다. ROI 축소, Model 경량화, Batch/병렬 처리, Trigger 속도 조정 중 정확도와 지연을 함께 검증해야 한다.

---

## 7. C++/OpenCV DNN 구현 골격

아래는 Model 호출 경계를 보여주는 예제다. Input 크기, Channel 순서, Scale, Mean은 학습 때의 전처리와 정확히 같아야 한다.

```cpp
#include <cmath>
#include <opencv2/core.hpp>
#include <opencv2/dnn.hpp>
#include <opencv2/imgproc.hpp>
#include <stdexcept>
#include <string>

struct ClassPrediction {
    int classId{};
    float score{};
};

class ClassificationModel {
public:
    explicit ClassificationModel(const std::string& onnxPath)
        : net_(cv::dnn::readNetFromONNX(onnxPath)) {
        if (net_.empty()) throw std::runtime_error("failed to load ONNX model");
    }

    ClassPrediction predict(const cv::Mat& bgr) {
        if (bgr.empty() || bgr.type() != CV_8UC3)
            throw std::invalid_argument("expected non-empty CV_8UC3 input");

        cv::Mat blob = cv::dnn::blobFromImage(
            bgr, 1.0 / 255.0, cv::Size(224, 224), cv::Scalar(), true, false);
        net_.setInput(blob);
        const cv::Mat output = net_.forward();
        if (output.empty() || output.total() == 0U)
            throw std::runtime_error("model returned empty output");

        const cv::Mat scores = output.reshape(1, 1);
        cv::Point maxLocation;
        double maxScore = 0.0;
        cv::minMaxLoc(scores, nullptr, &maxScore, nullptr, &maxLocation);
        if (!std::isfinite(maxScore))
            throw std::runtime_error("model returned non-finite score");
        return {maxLocation.x, static_cast<float>(maxScore)};
    }

private:
    cv::dnn::Net net_;
};
```

이 Score가 확률인지 Logit인지는 Model 출력 정의에 달려 있다. 필요하면 Softmax/Sigmoid를 명시적으로 적용하고, Threshold는 Validation Set에서 고정한 뒤 Test Set으로 평가한다. `Net`의 동시 호출 정책은 사용 Backend와 OpenCV Build에서 검증하고, 안전성이 불명확하면 Worker별 Instance 또는 직렬화를 사용한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1. 현장 영상에서만 정확도 하락

학습 Dataset과 실제 조명, Camera, Focus, 압축, 제품 Lot 분포가 다를 수 있다. Raw와 영상 품질 지표를 Version별로 비교하고 Domain Shift를 확인한다.

### 문제 2. Score는 높은데 엉뚱한 배경을 본다

ROI가 잘못되었거나 Shortcut Feature를 학습했을 수 있다. Hard Negative, Mask, 설명 Map을 진단 보조로 사용하되 최종 근거로 과신하지 않는다.

### 문제 3. Model 교체 후 수율 급변

Model, 전처리, Label Map, Threshold 중 하나가 바뀌었을 수 있다. Model만 Versioning하지 말고 전체 Inference Contract Hash를 Result에 남긴다.

### 문제 4. GPU 오류로 검사 누락

Warm-up, Memory 부족, Driver/Backend 오류를 System Error로 구분하고 Retry 횟수와 CPU Fallback 또는 장비 정지 정책을 사전에 정한다.

---

## 9. 흔한 오해

- “정상 영상만 많으면 모든 이상을 찾는다” → 정상 범위가 대표적이어야 하고 미지 이상 성능을 보장하지 않는다.
- “Score 0.9는 불량 확률 90%다” → Calibration하지 않은 Score는 확률로 해석할 수 없다.
- “Model이 알아서 전처리한다” → Resize, Color, Scale, Normalize 불일치는 결과를 바꾼다.
- “평균 Inference가 Cycle Time 이하면 된다” → P99, Queue, 전처리·후처리·전송까지 포함해야 한다.
- “재학습하면 기존 결함도 좋아진다” → 고정 회귀 Set으로 이전 성능 저하를 검사해야 한다.

---

## 10. 면접 질문

### Q1. 전통 Vision과 DL 중 어떻게 선택합니까?
광학과 규칙 기반 Baseline을 먼저 만들고 변동성, Dataset, 설명성, 운영 비용, 정확도 요구를 수치로 비교합니다.

### Q2. Dataset Leakage를 어떻게 막습니까?
같은 제품 연속 Frame이나 같은 Lot가 Train/Test에 동시에 들어가지 않게 Group 단위로 분리합니다.

### Q3. Threshold는 어떻게 정합니까?
Validation Set에서 미검/오검 비용과 요구 Recall/FPR을 기준으로 고정하고 독립 Test Set에서 한 번 평가합니다.

### Q4. Model 결과 재현에 무엇이 필요합니까?
Raw, ROI/Align, Model/전처리/후처리 Version, Backend, Threshold, SW Build가 필요합니다.

### Q5. Drift를 어떻게 감시합니까?
입력 품질, Score 분포, Review/NG 비율, 확정 Label 성능을 시간·Lot별로 추적하고 재학습 Trigger를 사전 정의합니다.

### Q6. Fail-safe는 어떻게 설계합니까?
입력/출력 유효성, Timeout, 비정상 Score를 Error로 구분하고 Retry/Fallback/Interlock 정책을 공정 위험에 맞게 정합니다.

---

## 11. 실습 문제

1. 동일 Dataset에 전통 Blob Baseline과 Segmentation Model을 적용한다고 가정하고 Recall, FPR, P99, 개발/운영 비용 비교표를 설계한다.
2. 동일 제품의 연속 Frame 10장이 있을 때 Random Split이 왜 Leakage를 만드는지 설명하고 Lot/Product Group Split을 설계한다.
3. Model 입력이 RGB 224×224, Scale 1/255인데 C++이 BGR과 Mean subtraction을 사용한 오류를 찾고 회귀 Test를 작성한다.
4. Model P99 45 ms, 전후처리 20 ms, 저장 15 ms인 15 fps Line에서 순차/비동기 구조의 처리량을 계산한다.

---

## 12. Chapter 핵심 요약

- 🔴 광학·해상도·좌표 문제를 먼저 해결한다.
- 🔴 Model 입력/출력/전처리 Contract를 Versioning한다.
- 🔴 개발/Validation/Test Dataset을 Group 단위로 분리한다.
- 🔴 Accuracy 대신 Recall, FPR, Sample 수, Worst Case를 본다.
- 🔴 Raw와 Model/Recipe/SW Version으로 Replay 가능하게 한다.
- 🟠 평균뿐 아니라 P99와 Queue 처리량을 검증한다.
- 🟠 Model 실패를 제품 NG와 분리한다.
- 🟠 Hybrid 방식으로 Model 후보를 전통 측정과 결합할 수 있다.
- 🟡 Drift와 재학습은 운영 체계의 일부다.
- 🟡 딥러닝은 전통 머신비전의 대체재가 아니라 선택 가능한 Inspector다.
