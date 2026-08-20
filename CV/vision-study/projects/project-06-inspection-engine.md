# Project 06. Recipe 기반 Inspection Engine

> 연결 학습: [[../16b-inspection-pipeline|Inspection Pipeline]], [[../17a-recipe-software-architecture|Recipe Architecture]], [[../17b-modern-cpp-opencv|Modern C++]]

## 1. 목적

Image Acquisition부터 Result까지의 Stage를 UI와 분리한 작은 검사 엔진을 설계한다. 불변 Recipe Snapshot, 입력/출력 계약, NG/Invalid/Error, Timing, 저장 실패 정책을 통합한다.

## 2. Scope

- File Camera로 시작하고 실제 Camera는 Adapter로 교체 가능하게 한다.
- Align은 합성 Transform 또는 Project 04 Solver를 사용한다.
- Inspector는 Project 02 Edge와 Project 03 Blob 중 두 종류 이상을 등록한다.
- Recipe에 Camera, Align, ROI, Inspector, Spec, 저장 정책을 둔다.
- Result에 모든 Measurement, Overall Verdict, Timing, Version을 기록한다.
- Raw/Overlay 저장과 DB 전송은 검사 판단 후 비동기로 분리한다.

## 3. Architecture

```text
IFrameSource → Orchestrator → Quality Gate → Alignment
                              → ROI Transform
                              → Inspector Registry
                              → Judgement → Result Builder
                                               ├─ Image Sink
                                               └─ Result Sink
```

Core는 파일 경로, GUI Widget, 특정 Camera SDK를 직접 알지 않는다. 외부 Resource는 Interface 뒤에 둔다.

## 4. 핵심 계약

```cpp
#include "inspection_domain.hpp" // 17A의 Domain Type 선언
#include <memory>
#include <opencv2/core.hpp>
#include <string>

struct InspectionContext {
    std::string productId;
    cv::Mat image;
    std::shared_ptr<const InspectionRecipe> recipe;
};

class IInspector {
public:
    virtual ~IInspector() = default;
    virtual Measurement inspect(const cv::Mat& roi,
                                const RoiRecipe& parameters) const = 0;
};

class IResultSink {
public:
    virtual ~IResultSink() = default;
    virtual void submit(const InspectionResult& result) = 0;
};
```

여기서 Recipe/Measurement/Result Type은 [[../17a-recipe-software-architecture|17A 데이터 모델]]을 사용한다. 실제 구현에서는 `RoiRecipe` 안의 Inspector별 Parameter를 Type-safe `variant` 또는 분리된 Domain Type으로 표현한다.

## 5. 상태와 판정

각 Inspector는 `Ok/Ng/Review/Invalid/Error` 중 하나와 Reason Code를 반환한다. Overall Rule 예시는 다음과 같다.

1. System Error 하나라도 있으면 Overall Error
2. 필수 검사 Invalid가 있으면 Overall Invalid
3. NG 하나라도 있으면 Overall NG
4. Review 하나라도 있으면 Overall Review
5. 나머지는 OK

공정 요구에 따라 우선순위는 달라질 수 있으므로 코드에 숨기지 않고 정책 Test로 고정한다.

## 6. 구현 단계

1. Domain Type과 Recipe Validator를 만든다.
2. File Frame Source와 In-memory Result Sink를 만든다.
3. 불변 Recipe Snapshot으로 단일 제품을 검사한다.
4. Inspector Registry에서 Type 이름을 실제 객체에 매핑한다.
5. Align 결과로 Reference ROI를 Current Image에 변환한다.
6. Stage별 Timing과 Error Context를 Result Builder에 모은다.
7. Bounded Queue와 저장 Worker를 추가한다.
8. Safe Point Recipe 전환과 Offline Replay를 구현한다.

## 7. 필수 자동 Test

- 정상 2-Inspector 모두 OK
- 한 검사 NG, 나머지 OK
- 필수 ROI가 Image 밖
- Align Invalid로 검사 중단
- Inspector가 예외 발생
- Recipe 전환과 Trigger 경합
- Result Sink 단절과 재전송
- Image Sink Disk Full
- Queue Full/종료 중 잔여 Frame
- 같은 Raw/Recipe 100회 결정성

## 8. 성능과 Backpressure

Acquisition 30 ms, Align 20 ms, 검사 35 ms, Result Build 5 ms가 순차 실행되면 90 ms다. 저장 40 ms를 비동기로 분리해도 저장 처리량이 입력보다 낮으면 Queue가 증가하므로 평균과 P99, Queue Depth를 함께 본다.

Queue 크기 \(Q\), 입력률 \(\lambda\), 소비율 \(\mu\)에서 \(\lambda>\mu\)이면 유한 Queue는 결국 가득 찬다. Queue 크기 증가는 처리량 불일치를 해결하지 않는다.

## 9. 정량 합격 기준

- Result 100%에 Product/Frame/Recipe/Calibration/SW ID 존재
- 동일 입력 100회 Measurement와 Verdict 동일
- 예상 가능한 모든 실패가 Reason Code로 구분
- Queue 상한과 Full 정책 자동 Test 통과
- 8시간 Soak Test에서 메모리/Handle 증가 없음
- 목표 처리량에서 P99 Cycle Time 충족
- 저장/통신 단절 후 중복 없이 재전송 또는 명시적 실패

## 10. 제출물과 완료 점검

- [ ] Component와 Data Flow Diagram
- [ ] Domain Type/Interface/Ownership 표
- [ ] Recipe 예제와 Validator Test
- [ ] Result 예제와 Overall Rule Test
- [ ] Replay/Integration/Soak Test 결과
- [ ] NG/Invalid/Error 통계 분리
- [ ] Queue Depth와 P99 Report
- [ ] 장애 복구 및 종료 Sequence
- [ ] UI 없이 실행 가능한 Core
- [ ] 실제 Camera 연결 시 교체할 Adapter 목록
