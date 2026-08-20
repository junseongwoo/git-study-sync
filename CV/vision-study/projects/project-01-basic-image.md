# Project 01. Image Load → Gray → Threshold → Blob

> 연결 학습: [[../02-image-basic|Image 기본]], [[../09-image-processing-01-threshold|Threshold]], [[../11-image-processing-03-morphology-blob|Blob]]

## 1. 목적

한 장의 영상을 읽어 전경 후보를 분리하고 Blob별 면적·중심·Bounding Box를 반환하는 가장 작은 검사기를 만든다. 화면 출력보다 입력 계약, Parameter, 결과 수치, 실패 처리를 먼저 완성한다.

## 2. 요구사항

- PNG/BMP의 Mono8 또는 BGR8 입력을 허용한다.
- BGR은 Gray로 변환하고 Mono는 불필요하게 변환하지 않는다.
- Fixed/Otsu Threshold 중 하나를 Recipe로 선택한다.
- Open/Close는 선택 사항이며 Kernel 크기는 홀수 양수만 허용한다.
- 면적 범위로 Blob을 Filtering한다.
- Blob마다 Label, Area px², Centroid px, Bounding Box px를 출력한다.
- 입력 실패, 지원하지 않는 Type, Blob 없음은 서로 다른 상태로 반환한다.

## 3. 입력과 출력 계약

```cpp
#include <opencv2/core.hpp>

enum class ProjectStatus { Success, NoBlob, InvalidInput, ProcessingError };

struct BasicParameters {
    bool useOtsu{};
    double threshold{};
    bool invert{};
    int morphologyKernel{1};
    int minAreaPx{1};
    int maxAreaPx{1'000'000};
};

struct BasicBlob {
    int label{};
    int areaPx{};
    cv::Point2d centroidPx{};
    cv::Rect boundingBoxPx{};
};
```

Parameter 검증은 영상 처리 전에 수행한다. `minAreaPx <= maxAreaPx`, Threshold 0~255, Kernel 홀수 여부를 확인한다.

## 4. Pipeline

```text
Load → Validate → Gray → Histogram(optional)
→ Threshold → Morphology(optional)
→ Connected Components → Area Filter → Result/Overlay
```

Overlay는 결과를 확인하는 파생 산출물이다. 측정은 Overlay 영상이 아닌 Label/통계 데이터에서 계산한다.

## 5. 구현 순서

1. 정상/빈 경로/지원하지 않는 영상의 Load Test를 만든다.
2. 100×100 합성 영상에 20×30 사각형을 그린다.
3. Threshold 후 전경 Pixel 수가 이론값 600 px인지 확인한다.
4. Connected Components에서 Background Label을 제외한다.
5. 경계에 닿은 Blob을 허용할지 Recipe 정책을 추가한다.
6. 결과를 CSV 또는 JSON 형태로 출력한다.
7. 원본과 Parameter를 고정한 Replay Test를 만든다.

## 6. 정량 합격 기준

- 합성 사각형 면적: 기대값 대비 0 px 오차
- 중심: 기대 좌표 대비 ≤ 0.01 px
- 빈 영상/잘못된 Type에서 명시적 `InvalidInput`
- Blob 없음에서 예외가 아니라 `NoBlob`
- 같은 입력 100회 결과 완전 동일
- 2,048×2,048 Mono8 한 장의 처리 시간과 환경 기록

## 7. 필수 시험 Dataset

- 균일 배경 + 밝은 사각형
- 밝기 Gradient 배경
- 경계에 닿은 Blob
- 1 px Noise 100개
- 서로 붙은 두 Blob
- 검은 전경/밝은 배경
- Mono16 입력: 거부하거나 명시적으로 Scaling하는 정책 검증

## 8. 실패 주입

- 존재하지 않는 파일
- 빈 `cv::Mat`
- Threshold -1, 256, NaN
- 짝수 Kernel, 0 Kernel
- 역전된 면적 범위
- 출력 폴더 쓰기 실패

## 9. 제출물

- Source와 Build 설정
- Parameter 예제
- 원본/Threshold/Label Overlay
- 자동 Test 결과
- 면적·중심 오차 표
- 실패 사례 3개와 개선 기록

## 10. 완료 점검

- [ ] 화면 없이 함수 단위 실행이 가능하다.
- [ ] 모든 좌표와 면적 필드에 px 단위가 드러난다.
- [ ] Background Label을 Blob으로 세지 않는다.
- [ ] Otsu 사용 시 입력 Threshold가 무시됨을 설명할 수 있다.
- [ ] Morphology가 작은 실제 결함까지 없애지 않는지 검증했다.
