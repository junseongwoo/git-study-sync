# 17일차 B. Modern C++17과 OpenCV 구현 원칙

> Phase 16 · 권장 학습 시간: 12~16시간 · 난이도: 중급~고급 · 핵심: 수명, 소유권, 실패 처리, 테스트

## 1. 이 Chapter에서 배우는 것

- 장비 SW에서 RAII가 중요한 이유
- `cv::Mat`의 얕은 복사와 Camera Buffer 수명
- `const`, `enum class`, 스마트 포인터 선택 기준
- 제품 NG와 예외를 분리하는 오류 처리
- Thread 간 Frame 전달과 Backpressure
- 불필요한 복사 없이 안전하게 성능을 확보하는 방법
- 영상 알고리즘의 Unit/Integration/Replay Test 설계

### 실무 목표

빠른 Demo가 아니라 장시간 운전해도 누수, Use-after-free, 조건 혼합, 무한 Queue가 발생하지 않는 검사 엔진의 구현 원칙을 익힌다.

---

## 2. 선수 지식

- [[17a-recipe-software-architecture|Recipe와 SW Architecture]]
- [[16b-inspection-pipeline|Inspection Pipeline]]
- C++17 기본 문법과 OpenCV `cv::Mat`

---

## 3. 소유권과 RAII

Pointer를 고르기 전에 생성자, 파괴자, 공유 범위, 비동기 수명을 결정한다.

- 값 또는 `unique_ptr`: 소유자가 하나일 때 기본 선택
- `shared_ptr`: 실제로 수명을 공유해야 할 때만 사용
- Reference/Raw Pointer: 소유하지 않는 짧은 접근
- `weak_ptr`: 공유 객체를 관찰하지만 수명을 늘리지 않을 때

`shared_ptr`를 무조건 사용하면 순환 참조와 불명확한 파괴 시점이 생긴다.

### 3.1 Camera Resource를 RAII로 관리한다

```cpp
#include <stdexcept>

class ICameraSdk {
public:
    using Handle = void*;
    virtual ~ICameraSdk() = default;
    virtual Handle open(int index) = 0;
    virtual void start(Handle handle) = 0;
    virtual void stop(Handle handle) noexcept = 0;
    virtual void close(Handle handle) noexcept = 0;
};

class CameraSession {
public:
    CameraSession(ICameraSdk& sdk, int index) : sdk_(sdk), handle_(sdk_.open(index)) {
        if (handle_ == nullptr) throw std::runtime_error("camera open failed");
        try {
            sdk_.start(handle_);
            started_ = true;
        } catch (...) {
            sdk_.close(handle_);
            handle_ = nullptr;
            throw;
        }
    }

    ~CameraSession() noexcept {
        if (handle_ == nullptr) return;
        if (started_) sdk_.stop(handle_);
        sdk_.close(handle_);
    }

    CameraSession(const CameraSession&) = delete;
    CameraSession& operator=(const CameraSession&) = delete;
    ICameraSdk::Handle handle() const noexcept { return handle_; }

private:
    ICameraSdk& sdk_;
    ICameraSdk::Handle handle_{nullptr};
    bool started_{false};
};
```

Destructor는 예외를 던지지 않는다. SDK가 실패 코드를 반환한다면 Destructor에서는 Log만 남기고, 명시적 `shutdown()`에서 오류를 처리하는 방식을 고려한다.

---

## 4. `cv::Mat`과 Buffer 수명

### 4.1 얕은 복사와 깊은 복사

```cpp
#include <opencv2/imgcodecs.hpp>

cv::Mat a = cv::imread("input.png", cv::IMREAD_GRAYSCALE);
cv::Mat b = a;          // pixel buffer 공유
cv::Mat c = a.clone();  // 독립 pixel buffer

b.at<unsigned char>(0, 0) = 0; // a의 같은 pixel도 변경됨

cv::Mat roiView = a(cv::Rect(10, 10, 100, 80)); // a와 buffer 공유
cv::Mat roiCopy = roiView.clone();               // 독립 buffer
```

OpenCV가 소유하는 `Mat`은 Reference Count로 Buffer 수명을 유지한다. Camera SDK가 소유한 외부 메모리를 감싼 `Mat`은 SDK가 Buffer를 재사용하면 픽셀이 바뀐다.

### 4.2 외부 Camera Buffer를 감쌀 때

```cpp
#include <cstddef>
#include <opencv2/core.hpp>
#include <stdexcept>

cv::Mat wrapMono8(unsigned char* data, int width, int height, std::size_t stride) {
    if (data == nullptr || width <= 0 || height <= 0 ||
        stride < static_cast<std::size_t>(width)) {
        throw std::invalid_argument("invalid camera buffer");
    }
    return cv::Mat(height, width, CV_8UC1, data, stride);
}

cv::Mat acquireOwnedCopy(unsigned char* data, int width, int height,
                         std::size_t stride) {
    return wrapMono8(data, width, height, stride).clone();
}
```

비동기 Pipeline에는 다음 중 하나를 사용한다.

- 즉시 `clone()`하여 애플리케이션이 소유
- SDK Buffer Handle과 수명 객체를 함께 전달하고 완료 후 반환
- 고정 크기 Buffer Pool로 복사 비용과 수명 관리

SDK Callback이 끝난 뒤 무효가 되는 Pointer만 Queue에 넣으면 안 된다.

### 4.3 `const`의 한계

입력을 수정하지 않는 함수는 `const cv::Mat&`로 받는다. 다만 Mat Header의 `const`가 공유 Pixel의 완전한 불변성을 보장하지는 않으므로, 입력을 수정하지 않고 출력 Mat을 분리한다는 팀 규칙이 필요하다.

```cpp
#include <opencv2/core.hpp>
#include <vector>

struct BlobFeature { double areaPx{}; cv::Point2d centerPx{}; };
std::vector<BlobFeature> findBlobs(const cv::Mat& binary);
```

---

## 5. Frame Packet과 시간

```cpp
#include <chrono>
#include <cstdint>
#include <memory>
#include <opencv2/core.hpp>
#include <stdexcept>
#include <string>
#include <utility>

struct InspectionRecipe;

struct FramePacket {
    std::uint64_t frameId{};
    std::string cameraId;
    std::chrono::steady_clock::time_point acquiredAt;
    cv::Mat image;
    std::shared_ptr<const InspectionRecipe> recipe;
};

FramePacket makePacket(std::uint64_t id, std::string cameraId,
                       const cv::Mat& ownedImage,
                       std::shared_ptr<const InspectionRecipe> recipe) {
    if (ownedImage.empty()) throw std::invalid_argument("empty frame");
    if (!recipe) throw std::invalid_argument("null recipe snapshot");
    return {id, std::move(cameraId), std::chrono::steady_clock::now(),
            ownedImage, std::move(recipe)};
}
```

`ownedImage`는 OpenCV가 소유한 Buffer라는 전제다. 외부 Buffer라면 복제하거나 SDK 수명 객체를 Packet에 함께 보관한다.

- Cycle Time: 역행하지 않는 `steady_clock`
- 외부 추적 Timestamp: UTC 기반 `system_clock`

NTP 보정으로 System Clock이 움직일 수 있으므로 처리 시간 측정에는 쓰지 않는다.

---

## 6. 오류 처리

### 6.1 예외와 Domain Result를 구분한다

- 예외/Error: Camera Open, 파일 I/O, 잘못된 Recipe, 불변 조건 위반
- 정상 Domain 결과: Spec 초과, Scratch 존재, Review 판정
- 예상 가능한 검출 실패: Status/Reason Code로 표현하고 정책에서 NG/Invalid 결정

```cpp
#include <optional>
#include <string>

enum class DetectionStatus { Found, NotFound, Ambiguous, InvalidInput };

struct CircleDetection {
    DetectionStatus status{DetectionStatus::InvalidInput};
    std::optional<cv::Point2d> centerPx;
    std::optional<double> radiusPx;
    double score{};
    std::string reason;
};
```

`catch (...)` 뒤 OK나 0.0을 반환하면 결함이 은폐된다. Component 경계에서 Stage, Frame ID, 원인 정보를 추가하고 Result Error로 변환한다.

### 6.2 `assert`와 실행 검증

`assert`는 Release Build에서 사라질 수 있다. 외부 입력, Recipe, Camera Frame은 항상 실행 중 검증하고, `assert`는 개발자가 보장해야 하는 내부 불변 조건에만 사용한다.

---

## 7. 동시성과 Backpressure

입력 12 fps, 처리 10 fps, Frame 4 MiB라면 10분 후 Queue에 약 4.69 GiB가 쌓인다.

$$
(12-10)\ \mathrm{frame/s}\times600\ \mathrm{s}\times4\ \mathrm{MiB}
=4800\ \mathrm{MiB}\approx4.69\ \mathrm{GiB}
$$

Queue는 상한과 Full 정책을 가진다.

- Trigger를 늦추거나 장비를 Interlock으로 정지
- Preview Frame만 Drop
- 검사 Frame은 조용히 버리지 않고 Error 처리

### 7.1 Thread 경계 원칙

- 소유권이 명확한 `FramePacket`을 전달한다.
- Recipe는 `shared_ptr<const ...>` Snapshot으로 공유한다.
- UI 객체를 Worker Thread에서 직접 갱신하지 않는다.
- Queue Close 상태와 `notify_all`로 종료 대기를 해제한다.
- 순서가 중요하면 `productId/frameId`로 결과를 재정렬한다.

제품 Thread Pool과 OpenCV 내부 Thread를 동시에 최대로 쓰면 Oversubscription이 생길 수 있다. 실제 CPU에서 조정하고 평균뿐 아니라 P95/P99 Cycle Time을 본다.

---

## 8. 성능 최적화와 계산

1. 요구 Cycle Time, 영상 크기, Camera 수를 수치로 정한다.
2. Stage별 시간을 측정한다.
3. 가장 큰 병목을 확인한다.
4. ROI 축소, Color 변환 제거, Buffer 재사용을 적용한다.
5. 정확도 회귀 테스트 후 P95/P99와 메모리를 다시 측정한다.

4,096×3,000 Mono8 한 장은 11.71875 MiB다. 20 fps에서 한 번 불필요하게 전체 복사하면 최소 234.375 MiB/s가 추가된다.

$$
4096\times3000/2^{20}=11.71875\ \mathrm{MiB}
$$

$$
11.71875\times20=234.375\ \mathrm{MiB/s}
$$

그러나 안전하지 않은 Zero-copy보다 올바른 한 번의 복사가 낫다. 먼저 수명을 보장한 뒤 Profile로 최적화한다.

---

## 9. 테스트 전략

### 9.1 Unit Test

- Spec: `L`, `U`, `L±ε`, `U±ε`
- 좌표 변환: 알려진 Translation/Rotation과 역변환
- Blob: 합성 원·사각형의 면적과 중심
- Recipe Validator: 누락, NaN, 범위 역전, 중복 ID
- 판정 정책: Found/NotFound/Ambiguous/Error 조합

### 9.2 Golden Image와 Replay

고정 영상과 Recipe로 Feature, Measurement, Verdict를 비교한다. Library 차이를 고려해 중심 오차 ≤ 0.1 px, 면적 상대 오차 ≤ 0.5%처럼 의미 있는 허용오차를 정의한다. 실제 생산 Raw와 당시 Snapshot으로 Offline Pipeline을 재실행하는 Replay Test도 둔다.

### 9.3 Integration Test

- Camera Timeout과 재연결
- Trigger 누락·중복·순서 변경
- Disk Full과 DB 단절
- Recipe 전환 중 Trigger
- 종료 중 Queue에 남은 Frame
- Calibration/해상도 불일치

GUI Click, 성공 영상, 화면 반올림 값, 고정 `sleep`에만 의존하는 Test는 피한다.

---

## 10. 테스트 가능한 Inspector

```cpp
#include <opencv2/core.hpp>
#include <stdexcept>

struct ThresholdParameters { double threshold{}; bool invert{}; };

class IThresholdOperator {
public:
    virtual ~IThresholdOperator() = default;
    virtual cv::Mat apply(const cv::Mat& gray,
                          const ThresholdParameters& parameters) const = 0;
};

class AreaInspector {
public:
    explicit AreaInspector(const IThresholdOperator& op) : op_(op) {}

    double measureForegroundAreaPx(const cv::Mat& gray,
                                   const ThresholdParameters& parameters) const {
        if (gray.empty() || gray.type() != CV_8UC1)
            throw std::invalid_argument("expected non-empty CV_8UC1 image");
        const cv::Mat binary = op_.apply(gray, parameters);
        if (binary.empty() || binary.type() != CV_8UC1 || binary.size() != gray.size())
            throw std::runtime_error("threshold operator returned invalid image");
        return static_cast<double>(cv::countNonZero(binary));
    }

private:
    const IThresholdOperator& op_;
};
```

작은 Interface를 주입하면 Test Double로 Inspector의 입력 검증과 계산을 분리해 검사할 수 있다. 실제 영상 알고리즘은 Golden Image Test로 추가 검증한다.

---

## 11. 실패 사례와 실습

### 자주 발생하는 실패

- 영상이 가끔 섞임: Callback Buffer를 Header만 감싸 Queue에 전달
- 장시간 후 메모리 증가: 무한 Queue, `shared_ptr` 순환, Cache 무제한
- 종료 시 멈춤: Queue Close/`notify_all`/Thread Join 순서 오류
- Debug/Release 차이: 미초기화 값, Data Race, Release에서 사라지는 `assert`

### 실습 과제

1. 사용 중인 Camera SDK의 Callback Buffer 수명 규칙을 확인한다.
2. Pipeline의 모든 `cv::Mat`에 Owner와 Lifetime을 표로 작성한다.
3. 입력 15 fps, 처리 12 fps, Frame 8 MiB인 Queue의 5분 증가량을 계산한다. 정답은 7,200 MiB, 약 7.03 GiB다.
4. Recipe 전환과 Trigger가 동시에 발생하는 Integration Test를 설계한다.
5. 같은 Raw/Recipe를 100회 Replay해 결과 변동과 P99 시간을 측정한다.

### 이해 점검

1. 얕은 복사와 `clone()`의 차이는 무엇인가?
2. 외부 Buffer Mat이 위험한 이유는 무엇인가?
3. `shared_ptr`가 항상 기본값이 아닌 이유는 무엇인가?
4. Destructor에서 예외를 던지지 않는 이유는 무엇인가?
5. 제품 NG를 Exception으로 표현하지 않는 이유는 무엇인가?
6. 검사 Queue에 상한이 필요한 이유는 무엇인가?

---

## 12. 면접 질문 6개

### Q1. RAII가 장비 SW에서 왜 중요합니까?
- 초보자: 객체가 사라질 때 Resource를 자동 해제합니다.
- 실무자: Camera, 파일, Lock을 모든 Return과 예외 경로에서 결정적으로 정리합니다.
- 30초 답변: Resource 수명을 객체와 묶고 복사를 금지해 소유자를 명확히 하며 Destructor는 안전하게 정리합니다.

### Q2. `cv::Mat`을 다른 Thread로 넘길 때 무엇을 봅니까?
- 초보자: 영상이 비어 있지 않은지 봅니다.
- 실무자: Buffer Owner, Reference Count, SDK 재사용 시점, Writer 존재를 확인합니다.
- 30초 답변: OpenCV 소유 Buffer는 수명을 공유할 수 있지만 외부 Buffer는 Clone이나 Handle 수명 전달이 필요합니다.

### Q3. 검사 실패를 모두 Exception으로 처리합니까?
- 초보자: 제품 NG와 프로그램 오류를 나눕니다.
- 실무자: Detection/판정은 Domain Result로, I/O와 불변 조건 위반은 Error로 처리합니다.
- 30초 답변: 정상 NG 흐름과 시스템 실패를 분리해야 통계와 알람이 정확합니다.

### Q4. Queue 증가를 어떻게 막습니까?
- 초보자: Queue 크기를 제한합니다.
- 실무자: Bounded Queue, Backpressure, Trigger 제어, 종류별 Drop 정책을 둡니다.
- 30초 답변: 생산 Frame을 조용히 버리지 않고 Queue Full을 Error/Interlock으로 연결합니다.

### Q5. 영상 알고리즘은 어떻게 테스트합니까?
- 초보자: 여러 영상을 넣어 확인합니다.
- 실무자: 합성 Unit, Golden Image, 실제 Replay, 장애 Integration Test를 구성합니다.
- 30초 답변: UI와 분리하고 고정 Raw·Recipe로 수치와 Verdict를 자동 비교합니다.

### Q6. 성능 최적화는 어디서 시작합니까?
- 초보자: 느린 부분을 측정합니다.
- 실무자: Stage별 평균/P95/P99와 메모리·Queue를 측정합니다.
- 30초 답변: 정확도 회귀 Test를 고정한 뒤 가장 큰 병목부터 개선하고 다시 측정합니다.

---

## 다음 학습

다음 문서에서는 1~17일차의 Camera·광학·영상처리·Align·Calibration·검사 구조를 면접 질문과 장애 분석 시나리오로 통합한다.
