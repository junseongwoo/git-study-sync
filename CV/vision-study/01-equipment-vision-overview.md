# Chapter 1. 검사 장비와 비전 SW 전체 구조

> Phase 0 · 예상 학습 시간: 8~10시간 · 난이도: 입문 · 중요도: 🔴 반드시 알아야 함

## 1. 이 Chapter에서 배우는 것

### 핵심 개념

- 🔴 검사 장비의 `Camera → Result → Review/CIM` 전체 데이터 흐름
- 🔴 Vision SW와 Equipment SW의 책임 경계
- 🔴 Image Acquisition, Trigger, Exposure, Frame, Buffer
- 🔴 Inspection Recipe, ROI, Measurement, Judgement, Result
- 🔴 이미지 좌표계(Image Coordinate)와 장비 좌표계(Machine Coordinate)
- 🟠 실패 처리, 추적성(Traceability), 재현성(Reproducibility)

### 실무 목표

학습 후에는 “이미지 한 장이 어떻게 생성되고, 어떤 단계를 거쳐 OK/NG 및 Review/CIM 데이터가 되는가?”를 모듈과 데이터 관점에서 설명할 수 있어야 한다. 또한 카메라 입력, 알고리즘 결과, 장비 상태를 한 클래스에 섞지 않고 책임을 나눠 간단한 C++ Pipeline을 설계할 수 있어야 한다.

---

## 2. 선수 지식

### 2.1 단위

- pixel: 이미지의 이산 좌표 및 샘플 단위
- μm, mm: 실제 물체 및 장비 이동 거리의 단위
- ms: Exposure와 처리 시간의 단위

`100 pixel`은 그 자체로 실제 길이가 아니다. Calibration 또는 Object Space Pixel Resolution이 있어야 `몇 μm`인지 알 수 있다.

### 2.2 C++ 관점

- `struct`: Recipe/Result처럼 데이터를 표현
- `class`: Camera/InspectionEngine처럼 상태와 동작을 캡슐화
- RAII: 카메라 핸들, 버퍼 등 자원을 객체 수명으로 관리
- `const`: 검사 입력과 Recipe가 의도치 않게 바뀌지 않도록 계약 표현
- 예외와 검사 결과: 시스템 실패와 제품 NG를 구분

> [!WARNING]
> 제품이 불량인 `NG`는 정상적인 검사 결과다. 카메라 연결 끊김, 잘못된 Recipe, 빈 Image 같은 상태는 검사 시스템 오류다. 둘을 같은 `bool false`로 표현하면 복구와 추적이 어려워진다.

---

## 3. 핵심 개념

### 3.1 검사 장비의 일반적인 SW 구조

```text
PLC / Motion / Sensor
        │ trigger, position, interlock
        ▼
Equipment Controller ───────────────┐
        │                           │ recipe / command
        ▼                           ▼
Camera → Acquisition → Image → Vision Pipeline
                                 │
               Preprocess → Alignment → ROI Transform
                                 │
                     Inspection → Measurement
                                 │
                     Judgement → Result
                                 │
             ┌───────────────────┼──────────────────┐
             ▼                   ▼                  ▼
          Review/UI        Result Storage          CIM
```

검사 장비 SW는 단지 이미지를 처리하는 프로그램이 아니다. 제품 투입, 축 이동, Trigger, 안전 Interlock, Recipe 전환, 검사, 배출, 결과 전송까지 하나의 상태 흐름을 관리한다.

### 3.2 Vision SW와 Equipment SW

| 구분 | Vision SW | Equipment SW |
|---|---|---|
| 주 책임 | 이미지로부터 위치·치수·결함을 추출 | 장비 시퀀스, Motion, I/O, 안전, 생산 흐름 |
| 대표 입력 | Image, Recipe, Calibration | 센서, PLC, 작업 지시, Vision Result |
| 대표 출력 | Align Pose, Measurement, OK/NG, Overlay | 축 명령, 분류/배출, Host 보고, Alarm |
| 시간 관심사 | 알고리즘 처리 시간, 이미지 품질 | Cycle Time, Timeout, Interlock |
| 실패 예 | Focus 불량, Match 실패, 과노출 | Servo Alarm, Trigger Timeout, 제품 미도착 |

경계는 제품마다 달라질 수 있지만 인터페이스는 명시해야 한다. 예를 들어 Vision이 반환하는 `X/Y/Theta`의 단위, 좌표 원점, 축 방향, 회전 부호, 신뢰도(Score)를 계약으로 고정한다.

### 3.3 Camera 제어와 Image Acquisition

1. Equipment Controller가 검사 위치 도착을 확인한다.
2. 조명 안정화 후 Trigger를 발생시킨다.
3. Camera가 Exposure 시간 동안 광자를 수집한다.
4. Sensor 데이터가 Camera Interface 또는 Frame Grabber를 통해 전송된다.
5. 수신 Buffer가 완전한 Frame인지 검증한다.
6. Frame ID, Timestamp, Recipe ID, Camera ID를 Image와 결합한다.
7. 소유권이 보장된 Image를 Vision Pipeline에 전달한다.

핵심 용어:

- **Trigger**: 촬영 시작을 지시하는 사건. Software/Hardware Trigger가 있다.
- **Exposure**: 센서가 빛을 모으는 시간. 길면 밝아지지만 Motion Blur 위험이 증가한다.
- **Frame**: 한 번의 촬영으로 생성된 완전한 이미지 단위.
- **Frame Grabber / Interface**: Camera Link, CoaXPress, GigE Vision, USB3 Vision 등의 영상을 호스트 메모리로 전달한다.
- **Buffer**: 전송 중이거나 처리 대기 중인 Frame의 메모리. 수명과 재사용 시점이 중요하다.
- **Image Acquisition**: Trigger부터 유효한 Frame과 Metadata를 애플리케이션에 넘기는 전체 과정.

### 3.4 Image Processing, Alignment, Inspection

- **Preprocessing(전처리)**: 노이즈 제거, 밝기 정규화, Contrast 개선 등 다음 단계가 안정적으로 동작하도록 Image를 준비한다.
- **Alignment(정렬)**: 제품의 기준 위치와 현재 위치의 차이인 X/Y/Theta 등을 구한다.
- **ROI Transform**: 기준 Recipe에 저장된 ROI를 Align 결과에 맞게 이동·회전한다.
- **Inspection(검사)**: Presence, 결함, 형상 조건 등을 판정할 특징을 찾는다.
- **Measurement(측정)**: 위치, 거리, 폭, 면적 같은 연속값을 계산한다.
- **Judgement(판정)**: 측정값과 Recipe Spec을 비교하여 OK/NG를 결정한다.

Measurement와 Judgement를 분리하면 Spec만 변경할 때 영상처리를 다시 설계하지 않아도 되고, Review에서 “왜 NG인가?”를 수치로 설명할 수 있다.

### 3.5 Recipe, Result, Review, CIM

#### Inspection Recipe

제품 종류별 검사 조건의 버전 관리된 집합이다.

- Camera: Exposure, Gain, Trigger Mode
- Optical context: Camera/Lens/조명 구성 식별자
- Algorithm: Threshold, Filter Size, Match Score
- Geometry: 기준점, ROI, Calibration ID
- Judgement: Min/Max Spec

#### Result Data

최소한 다음을 남긴다.

- Lot/Panel/Product ID, Sequence ID
- Timestamp, Equipment/Camera ID
- Recipe 이름과 버전
- Calibration 버전
- Align X/Y/Theta와 Score
- 검사 항목별 Measurement, Spec, Judgement
- 전체 OK/NG 및 Error Code
- 원본/NG/Overlay Image 경로

### 3.6 좌표계

```text
Image Coordinate                 Machine Coordinate
origin (0,0) ───► +x             +Y
    │                              ▲
    │                              │
    ▼ +y                   -X ◄────┼────► +X
                                   │
                                   ▼ -Y
unit: pixel                       unit: μm or mm
```

이미지는 보통 좌상단 원점, 오른쪽 +x, 아래쪽 +y다. 장비 좌표는 장비 설계에 따라 원점과 방향이 다르다. 그러므로 `pixel × scale`만으로는 일반적인 좌표 변환을 완성할 수 없다. 원점 Offset, 축 반전, Rotation, Lens Distortion을 고려할 수 있다.

### 3.7 전체 흐름의 연결

```text
Camera/Sensor
  └─ 빛을 Pixel 값으로 Sampling
Lens/Light
  └─ FOV, 선명도, Contrast를 결정
Image Acquisition
  └─ Frame + Metadata의 무결성을 보장
Preprocessing
  └─ 검사에 유리한 Image 생성
Alignment
  └─ 기준 대비 X/Y/Theta 추정
ROI Transform
  └─ 현재 제품 위치에 ROI 배치
Inspection/Measurement
  └─ 특징과 수치 추출
Judgement
  └─ Recipe Spec으로 OK/NG 결정
Result/Review/CIM
  └─ 저장, 설명, 생산 의사결정에 사용
```

---

## 4. 그림으로 이해하기

### 4.1 물리 세계에서 Result까지

```text
Real Object
    │ reflected/transmitted light
    ▼
Light + Lens ── optical image ──► Camera Sensor
                                      │ A/D conversion
                                      ▼
                                Digital Image
                                      │ preprocess
                                      ▼
Reference ──► Alignment ──► Transformed ROI
                                      │ feature extraction
                                      ▼
                                  Measurement
                                      │ compare with spec
                                      ▼
                                OK / NG / Error
                                      │
                         Review + Storage + CIM
```

### 4.2 시퀀스 관점

```text
Equipment      Camera        Vision        Review/CIM
    │             │             │               │
move & settle     │             │               │
    ├─trigger────►│             │               │
    │             ├─frame──────►│               │
    │             │             ├─inspect       │
    │◄────────result────────────┤               │
    ├─sort product              ├─save─────────►│
    └─next cycle                └─release image │
```

---

## 5. 실제 검사 장비에서 어디에 사용하는가?

### 상황 A: 제품이 매번 조금씩 틀어져 들어온다

고정 ROI로 검사하면 실제 검사 부위가 ROI 밖으로 벗어난다. Pattern Matching으로 X/Y/Theta를 구하고 ROI Transform 후 검사해야 한다. 이때 Align 실패는 곧바로 제품 결함을 뜻하지 않는다. 이미지 품질, 제품 방향 오류, 기준 패턴 가림 등을 별도 Error/NG 정책으로 다뤄야 한다.

### 상황 B: Review Image와 실제 결과가 맞지 않는다

검사 Buffer를 Camera가 재사용한 뒤 Review Thread가 같은 메모리를 읽었을 수 있다. Frame을 복사하거나 참조 카운팅된 불변 Image로 전달하고, `Frame ID ↔ Product ID ↔ Result ID`를 한 묶음으로 관리해야 한다.

### 상황 C: 카메라는 촬영했지만 이전 제품 이미지가 검사된다

Trigger Sequence와 Frame ID 검증이 없거나 비동기 Queue에 오래된 Frame이 남아 있을 수 있다. Trigger ID, Timestamp, Encoder/Stage Position을 Metadata로 묶고 예상 Sequence와 일치하는지 검사한다.

---

## 6. 숫자로 이해하기

### 예제 1: Cycle Time 예산

한 제품의 목표 Cycle Time이 `200 ms`이고 다음 시간이 필요하다고 하자.

| 단계 | 시간 |
|---|---:|
| Motion settle | 50 ms |
| Exposure | 8 ms |
| Image transfer | 12 ms |
| Preprocessing | 15 ms |
| Alignment | 35 ms |
| Inspection | 45 ms |
| Result packaging | 5 ms |

총 시간:

```text
50 + 8 + 12 + 15 + 35 + 45 + 5 = 170 ms
Margin = 200 - 170 = 30 ms
```

현재 예산상 가능하지만 저장과 CIM 전송을 동기식으로 40 ms 수행하면 `210 ms`가 되어 목표를 넘는다. 저장/전송은 Result의 무결성을 유지한 채 비동기화하는 설계를 검토할 수 있다. 단, 다음 제품과 ID가 섞이지 않도록 해야 한다.

### 예제 2: Frame 데이터 크기와 대역폭

`2048 × 2048`, 8-bit Gray Image 한 장의 원시 크기:

```text
2048 × 2048 × 1 byte = 4,194,304 byte ≈ 4 MiB
```

초당 20 Frame이면 순수 Pixel 데이터만:

```text
4 MiB × 20 = 80 MiB/s
```

카메라 4대라면 약 `320 MiB/s`다. 실제 시스템은 전송 오버헤드, Buffer, 복사, 이미지 저장을 추가로 고려해야 한다. 모든 Frame을 여러 번 깊은 복사하면 메모리 대역폭과 지연이 커진다.

### 예제 3: 좌표의 첫 계산

Calibration 결과가 `1 pixel = 2 μm`이고, 이미지에서 기준점 대비 오른쪽으로 `100 pixel`, 아래로 `50 pixel` 이동했다고 하자. 장비 좌표가 오른쪽 +X, 위쪽 +Y라면:

```text
Machine ΔX = +100 × 2 μm = +200 μm
Machine ΔY =  -50 × 2 μm = -100 μm
```

아래 방향인 Image +y가 Machine -Y이므로 부호가 바뀐다. 실제 장비에서는 Rotation과 Offset까지 포함한 Calibration Matrix를 사용한다.

---

## 7. C++ 구현

아래 예제는 실제 SDK 대신 OpenCV Image를 받아 검사하는 최소 구조다. 핵심은 `Acquisition`, `Recipe`, `Engine`, `Result`의 책임과 제품 NG/시스템 오류를 분리하는 것이다.

```cpp
#include <opencv2/opencv.hpp>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class Judgement {
    Ok,
    Ng
};

enum class ErrorCode {
    None,
    EmptyImage,
    InvalidRecipe
};

struct Frame final {
    cv::Mat image;
    std::uint64_t frameId{};
    std::string cameraId;
    std::chrono::steady_clock::time_point capturedAt;
};

struct InspectionRecipe final {
    std::string name;
    std::uint32_t version{};
    cv::Rect roi;
    int threshold{};
    double minArea{};
    double maxArea{};
};

struct Measurement final {
    std::string name;
    double value{};
    std::string unit;
    Judgement judgement{Judgement::Ng};
};

struct InspectionResult final {
    std::uint64_t frameId{};
    std::string recipeName;
    std::uint32_t recipeVersion{};
    Judgement overall{Judgement::Ng};
    ErrorCode error{ErrorCode::None};
    std::vector<Measurement> measurements;
    cv::Mat overlay;

    [[nodiscard]] bool HasSystemError() const noexcept {
        return error != ErrorCode::None;
    }
};

class InspectionEngine final {
public:
    [[nodiscard]] InspectionResult Inspect(
        const Frame& frame,
        const InspectionRecipe& recipe) const
    {
        InspectionResult result;
        result.frameId = frame.frameId;
        result.recipeName = recipe.name;
        result.recipeVersion = recipe.version;

        if (frame.image.empty()) {
            result.error = ErrorCode::EmptyImage;
            return result; // 제품 NG가 아니라 시스템 입력 오류
        }

        if (!IsValidRoi(recipe.roi, frame.image.size()) ||
            recipe.minArea > recipe.maxArea) {
            result.error = ErrorCode::InvalidRecipe;
            return result;
        }

        cv::Mat gray;
        if (frame.image.channels() == 1) {
            gray = frame.image; // 입력은 const이므로 수정하지 않는다.
        } else {
            cv::cvtColor(frame.image, gray, cv::COLOR_BGR2GRAY);
        }

        const cv::Mat roiView = gray(recipe.roi);
        cv::Mat binary;
        cv::threshold(roiView, binary, recipe.threshold, 255,
                      cv::THRESH_BINARY);

        std::vector<std::vector<cv::Point>> contours;
        cv::findContours(binary, contours, cv::RETR_EXTERNAL,
                         cv::CHAIN_APPROX_SIMPLE);

        double largestArea = 0.0;
        for (const auto& contour : contours) {
            largestArea = std::max(largestArea, cv::contourArea(contour));
        }

        const bool areaOk = largestArea >= recipe.minArea &&
                            largestArea <= recipe.maxArea;
        result.measurements.push_back({
            "largest_blob_area", largestArea, "pixel^2",
            areaOk ? Judgement::Ok : Judgement::Ng
        });
        result.overall = areaOk ? Judgement::Ok : Judgement::Ng;

        cv::cvtColor(gray, result.overlay, cv::COLOR_GRAY2BGR);
        cv::rectangle(result.overlay, recipe.roi,
                      areaOk ? cv::Scalar(0, 255, 0)
                             : cv::Scalar(0, 0, 255),
                      2);
        return result;
    }

private:
    [[nodiscard]] static bool IsValidRoi(
        const cv::Rect& roi,
        const cv::Size& imageSize) noexcept
    {
        const cv::Rect imageBounds{0, 0, imageSize.width, imageSize.height};
        return roi.width > 0 && roi.height > 0 &&
               (roi & imageBounds) == roi;
    }
};
```

### 코드에서 봐야 할 점

1. `Frame`은 Image와 Frame ID/Camera ID/Timestamp를 함께 전달한다.
2. `InspectionRecipe`는 알고리즘 조건과 버전을 가진다.
3. `InspectionResult`는 측정값, 판정, 오류, Overlay를 함께 보관한다.
4. `Judgement::Ng`와 `ErrorCode`를 분리했다.
5. 입력은 `const` 참조로 받아 수정하지 않는다.
6. ROI 유효성을 먼저 확인하여 OpenCV 내부 Assertion보다 의미 있는 오류로 처리한다.
7. 면적 단위는 아직 `pixel²`다. 실제 단위 변환에는 Calibration이 필요하다.

### 간단한 테스트 예제

```cpp
#include <cassert>

void TestBrightBlobIsDetected()
{
    cv::Mat image = cv::Mat::zeros(200, 200, CV_8UC1);
    cv::rectangle(image, {80, 80, 20, 20}, cv::Scalar(255), cv::FILLED);

    const Frame frame{image, 1, "CAM-01", std::chrono::steady_clock::now()};
    const InspectionRecipe recipe{
        "sample", 1, {50, 50, 100, 100}, 128, 350.0, 450.0
    };

    const InspectionEngine engine;
    const InspectionResult result = engine.Inspect(frame, recipe);

    assert(!result.HasSystemError());
    assert(result.overall == Judgement::Ok);
    assert(result.measurements.size() == 1);
}
```

> [!NOTE]
> 이 예제는 Architecture 입문용이다. 아직 Align, Dynamic ROI, Calibration, 저장 Queue, SDK Buffer 수명, Thread Safety는 구현하지 않았다. 이후 Chapter에서 단계적으로 확장한다.

---

## 8. 실무에서 발생하는 문제

### 문제 1: Trigger와 제품 ID가 어긋남

- 증상: 다른 제품의 Result가 현재 제품에 매핑됨
- 원인: 단순 FIFO 가정, Frame Drop, 재촬영, Timeout 후 늦게 도착한 Frame
- 대응: Trigger/Sequence/Frame/Product ID의 명시적 상관관계, Timeout 이후 Frame 폐기 정책, 로그에 ID 기록

### 문제 2: Camera Buffer 수명 오류

- 증상: 이미지가 간헐적으로 깨지거나 Review Image가 바뀜
- 원인: SDK가 Buffer를 재사용하는데 비동기 Consumer가 포인터를 계속 사용
- 대응: SDK의 소유권 규칙 확인, 필요 시 Clone, RAII Wrapper, 불변 Frame 전달

### 문제 3: Recipe가 검사 도중 변경됨

- 증상: 한 제품의 검사 항목마다 서로 다른 Parameter 적용
- 원인: 공유 Recipe 객체를 UI가 직접 수정
- 대응: 검사 시작 시 불변 Recipe Snapshot 사용, Version을 Result에 저장, 안전한 전환 시점 정의

### 문제 4: 조명·Exposure 변경 후 기존 Threshold가 실패

- 증상: 정상 제품 Blob 면적이 급변하거나 Align Score가 하락
- 원인: 영상 조건과 알고리즘 Parameter를 독립적으로 관리
- 대응: Camera/조명 조건을 Recipe에 포함하고 변경 이력 기록, Histogram/Reference Image 비교, 재검증

### 문제 5: 좌표계 부호·단위 오류

- 증상: 보정 명령이 반대 방향으로 움직이거나 1,000배 차이
- 원인: pixel/mm/μm 혼용, Image +y와 Machine +Y 혼동, Rotation 부호 미정의
- 대응: 좌표계 계약 문서, 단위를 타입/변수명에 표현, Known Point를 이용한 자동 테스트

### 문제 6: 저장 지연이 Cycle Time을 초과

- 증상: 검사 알고리즘은 빠른데 장비 생산성이 낮음
- 원인: 원본/Overlay 압축 및 네트워크 저장을 검사 Thread에서 동기 실행
- 대응: 제한된 비동기 Queue, Backpressure/Drop 정책, NG 우선 저장, 저장 실패 Alarm과 재시도 정책

---

## 9. 흔한 오해

1. **“Camera가 이미지를 주면 Acquisition은 끝이다.”**  
   Frame 무결성, Metadata, Timeout, Buffer 수명, Sequence 검증까지 포함해야 한다.

2. **“Align과 Calibration은 둘 다 좌표를 바꾸므로 같다.”**  
   Align은 매 제품의 자세 변화를 찾고, Calibration은 좌표계 사이의 지속적인 기하 관계를 정한다.

3. **“NG와 Error는 모두 검사 실패다.”**  
   NG는 제품에 대한 정상 판정이고 Error는 검사 신뢰성을 보장할 수 없는 시스템 상태다.

4. **“ROI를 줄이면 언제나 좋은 최적화다.”**  
   처리량은 줄지만 제품 이동량과 Align 오차를 포함하지 않으면 특징이 잘릴 수 있다.

5. **“Review에는 NG Image만 있으면 된다.”**  
   Recipe/Calibration Version, Overlay, 측정값, Spec, Align 결과가 있어야 재현 가능하다.

6. **“검사 결과는 `bool`이면 충분하다.”**  
   원인 분석, CIM 보고, 재검, 통계에는 항목별 측정값과 상태가 필요하다.

---

## 10. 면접에서 나올 수 있는 질문

### Q1. 검사 장비의 Vision Pipeline을 설명해 주세요.

**초보자가 이해할 수 있는 답변**  
카메라로 이미지를 얻고, 보기 좋게 전처리한 뒤 제품 위치를 맞춥니다. 그 위치에 검사 영역을 옮기고 특징과 크기를 측정한 다음 기준값과 비교해 OK/NG를 만듭니다. 결과와 이미지는 Review 및 상위 시스템으로 보냅니다.

**실무자 답변**  
Trigger와 Exposure를 포함한 Acquisition에서 Frame/Metadata 무결성을 보장하고, Preprocessing, Alignment, ROI Transform, Feature Extraction, Measurement, Judgement 순으로 처리합니다. Result에는 Recipe/Calibration Version과 항목별 측정값, 오류 상태, Image 경로를 넣고 UI·Storage·CIM이 동일한 Result를 소비하게 합니다.

**면접용 30초 답변**  
“장비가 Trigger를 주면 Camera Frame과 제품 ID를 결합하고, 전처리 후 Align으로 X/Y/Theta를 구합니다. 기준 ROI를 현재 제품 위치로 변환해 특징과 치수를 측정하고 Recipe Spec으로 OK/NG를 판정합니다. 확정 Result에는 측정값, Recipe/Calibration Version, Overlay 경로를 포함해 장비 시퀀스, Review, CIM이 동일하게 사용하도록 설계합니다.”

### Q2. Vision SW와 Equipment SW의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Vision SW는 이미지에서 위치와 결함을 찾고, Equipment SW는 장비가 제품을 옮기고 촬영하고 분류하는 전체 순서를 제어합니다.

**실무자 답변**  
Vision은 Image/Recipe를 입력받아 Pose, Measurement, Judgement를 생성합니다. Equipment는 Motion, I/O, Interlock, Cycle, 제품 추적을 관리합니다. 두 영역 사이에는 좌표계, 단위, Timeout, Error 정책이 포함된 명시적 인터페이스가 필요합니다.

**면접용 30초 답변**  
“Vision SW의 핵심 책임은 이미지로부터 정렬값과 검사 측정값을 만드는 것이고, Equipment SW는 Motion·I/O·안전·제품 흐름을 제어합니다. 실제 통합에서는 X/Y/Theta의 좌표계와 단위, Frame/Product ID, Timeout 및 Error 정책을 인터페이스 계약으로 고정하는 것이 중요합니다.”

### Q3. Align과 Calibration의 차이는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
Align은 매번 달라지는 제품 위치를 찾는 것이고, Calibration은 이미지의 위치가 실제 장비의 어디인지 연결하는 기준을 만드는 것입니다.

**실무자 답변**  
Align은 기준 제품 대비 현재 제품의 Pose, 주로 X/Y/Theta를 Frame마다 추정합니다. Calibration은 Image/Camera/Stage/Machine 좌표계 간 Scale, Rotation, Offset, 필요 시 Distortion 관계를 장비 설정 시 추정합니다. Align 결과를 Calibration된 좌표로 변환해 Motion 보정이나 실제 치수에 사용합니다.

**면접용 30초 답변**  
“Align은 제품마다 발생하는 위치·회전 편차를 구하는 동적 보정이고, Calibration은 pixel 좌표와 실제 장비 좌표 사이의 Scale·회전·Offset을 정하는 좌표계 보정입니다. 예를 들어 Align에서 10 pixel 이동을 찾고 Calibration으로 이를 실제 μm 이동량과 장비 축 방향으로 변환합니다.”

### Q4. 제품 NG와 검사 시스템 Error를 왜 분리해야 하나요?

**초보자가 이해할 수 있는 답변**  
NG는 카메라와 검사는 정상인데 제품이 기준을 벗어난 경우입니다. Error는 이미지 자체가 없거나 조건이 잘못되어 제품을 믿고 판정할 수 없는 경우입니다.

**실무자 답변**  
둘을 분리해야 장비가 분류, 재검, 정지, Alarm 중 올바른 동작을 선택할 수 있습니다. 통계에서도 품질 불량률과 설비 가동률을 왜곡하지 않으며, CIM의 결과 코드와 장애 코드도 정확히 관리할 수 있습니다.

**면접용 30초 답변**  
“NG는 유효한 검사 결과이고 Error는 유효한 판정을 만들 수 없는 시스템 상태입니다. 그래서 Result에 Judgement와 ErrorCode를 분리하고, NG는 제품 분류로, Camera Timeout이나 Invalid Recipe는 재시도 또는 장비 Alarm으로 처리합니다.”

### Q5. Recipe와 Result에 Version 정보가 필요한 이유는 무엇인가요?

**초보자가 이해할 수 있는 답변**  
나중에 같은 이미지를 다시 검사할 때 당시 어떤 조건을 썼는지 알아야 같은 결과를 확인할 수 있기 때문입니다.

**실무자 답변**  
Threshold, ROI, Spec뿐 아니라 Camera/Light/Calibration 조건 변경이 결과에 영향을 준다. Result에 Recipe와 Calibration Version을 저장하면 NG 원인 분석, 변경 전후 비교, Audit, 재현 검사가 가능하다. 검사 중에는 Version이 고정된 Snapshot을 사용해야 한다.

**면접용 30초 답변**  
“검사 결과의 재현성과 추적성을 위해서입니다. Result에 Recipe·Calibration Version을 남기고 검사 시작 시 불변 Snapshot을 사용하면, Parameter가 변경된 뒤에도 당시 ROI·Threshold·Spec·좌표 변환으로 결과를 재현하고 변경 영향을 분석할 수 있습니다.”

### Q6. ROI는 왜 사용하나요?

**초보자가 이해할 수 있는 답변**  
전체 이미지 중 검사할 부분만 잘라 처리하면 더 빠르고 엉뚱한 부분을 결함으로 찾을 가능성이 줄어듭니다.

**실무자 답변**  
ROI는 계산량과 False Positive를 줄이고 검사 의도를 공간적으로 표현한다. 다만 고정 ROI는 제품 편차에 취약하므로 Align Pose로 Dynamic ROI를 만들고, 최대 이동·회전과 Transform 보간, Image 경계를 검증해야 한다.

**면접용 30초 답변**  
“ROI는 검사 위치를 제한해 속도와 Robustness를 높입니다. 하지만 제품이 움직이면 고정 ROI가 실제 특징을 놓치므로 먼저 Align으로 X/Y/Theta를 구하고 기준 ROI를 변환합니다. 변환 후에는 이미지 경계와 충분한 Margin을 확인합니다.”

---

## 11. 실습 문제

### 실습 1: 현재 경험을 Pipeline에 매핑하기

본인이 개발한 CIM, Review, 장비 제어/UI 기능을 아래 단계에 배치한다.

```text
Acquisition → Preprocessing → Alignment → ROI → Inspection
→ Measurement → Judgement → Result → Review/UI/CIM
```

각 모듈에 대해 입력, 출력, 단위, Timeout, 실패 코드, 담당 Thread/Process를 표로 작성한다.

**완료 조건**

- 모듈 사이에 전달되는 ID를 정의했다.
- NG와 Error의 처리 경로가 구분된다.
- Image/Result의 소유권과 수명이 명시된다.

### 실습 2: 처리 시간과 Buffer 계산

다음 조건을 계산하고 설계를 제안한다.

- 4096×3000, 8-bit Gray
- 15 fps, Camera 2대
- Vision 처리 시간 평균 90 ms, 최대 160 ms
- Camera는 촬영을 계속하며 Frame Drop은 허용하지 않음

질문:

1. Frame 한 장과 초당 원시 데이터 크기는 얼마인가?
2. Vision이 직렬 처리라면 안정적으로 따라갈 수 있는가?
3. 순간 지연을 흡수할 Queue 크기를 어떤 근거로 정할 것인가?
4. 메모리가 무한 증가하지 않게 어떤 Backpressure 정책을 둘 것인가?

### 실습 3: C++ 설계 확장

Chapter 코드에 다음을 추가한다.

- `productId`, `sequenceId`, `calibrationVersion`
- 항목별 `lowerSpec`, `upperSpec`, `measuredValue`
- `AlignFailed`, `AcquisitionTimeout` Error
- Result를 JSON/CSV로 저장하는 별도 Writer Interface
- 빈 Image와 잘못된 ROI를 검증하는 Unit Test

UI나 CIM이 `InspectionEngine` 내부 상태를 직접 읽지 않고 확정된 `InspectionResult`만 소비하게 한다.

### 실습 4: 장애 시나리오 설계

아래 상황별로 **Retry / Skip / NG / Error / Equipment Stop** 중 정책을 선택하고 이유를 적는다.

- Camera Trigger Timeout
- Pattern Match Score 미달
- ROI가 Image 경계를 벗어남
- Result DB 저장 실패
- CIM 전송 일시 실패
- Calibration Version 불일치

### Phase 0 미니 프로젝트: Inspection Flow Simulator

실제 Camera 없이 폴더의 이미지를 Frame처럼 순서대로 읽어 다음을 구현한다.

1. `Frame ID + Product ID + Timestamp` 생성
2. Recipe Snapshot 선택
3. ROI Threshold 및 Blob Area 측정
4. OK/NG/Error 분리
5. Result CSV 저장
6. NG Overlay Image 저장
7. 처리 시간 측정과 로그 출력

**권장 Class 구조**

```text
InspectionFlowSimulator
├── ImageSource
├── RecipeRepository
├── InspectionEngine
├── ResultWriter
├── ImageWriter
└── CycleLogger
```

**검증 시나리오**

- 정상 Image → OK
- 기준 면적 밖 Image → NG
- 손상되거나 빈 Image → Error
- 잘못된 ROI Recipe → Error
- 같은 입력·Recipe → 같은 Measurement

---

## 12. Chapter 핵심 요약

- 🔴 검사 장비 SW는 촬영부터 Review/CIM까지 이어지는 전체 생산 Pipeline이다.
- 🔴 Vision SW는 특징·측정·판정을, Equipment SW는 시퀀스·Motion·I/O·안전을 주로 담당한다.
- 🔴 Frame에는 Image뿐 아니라 Product/Sequence/Camera/Recipe 식별 Metadata가 필요하다.
- 🔴 Preprocessing → Alignment → ROI Transform → Inspection → Measurement → Judgement 순서를 구분한다.
- 🔴 Align은 제품의 현재 Pose를, Calibration은 좌표계 사이 관계를 구한다.
- 🔴 제품 NG와 시스템 Error는 의미와 장비 대응이 다르다.
- 🔴 Recipe Snapshot과 Version은 검사 일관성 및 재현성을 보장한다.
- 🟠 Result는 UI, Storage, CIM이 함께 소비하는 단일 사실 공급원이어야 한다.
- 🟠 비동기 처리에서는 Buffer 수명, ID 상관관계, Queue 제한을 설계해야 한다.
- 🟠 좌표 변환에서는 단위, 원점, 축 방향, 회전 부호를 명시해야 한다.

---

## 학습 완료 체크

- [ ] 전체 Pipeline을 보지 않고 그릴 수 있다.
- [ ] Vision SW와 Equipment SW의 책임 차이를 설명할 수 있다.
- [ ] Trigger, Exposure, Frame, Buffer를 설명할 수 있다.
- [ ] Align과 Calibration의 차이를 30초 안에 설명할 수 있다.
- [ ] NG와 Error를 분리한 이유를 C++ 구조로 보여줄 수 있다.
- [ ] Recipe/Result Version이 필요한 이유를 설명할 수 있다.
- [ ] Phase 0 미니 프로젝트의 설계 또는 구현을 완료했다.

## 다음 Chapter 예고

다음 Chapter에서는 Image, Pixel, Gray Scale, RGB, Bit Depth, Dynamic Range를 배우고 Camera Resolution, Image Resolution, Pixel Size, Spatial Resolution, Optical Resolution을 명확히 구분한다.
