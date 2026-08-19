# 검사 장비 SW 개발자를 위한 비전·광학 집중 학습

> 대상: 검사 장비 SW 개발 경력 4년차, 비전·광학 입문자  
> 목표: 비전 엔지니어와 검사 조건을 논의하고, 기본 검사 파이프라인을 C++/OpenCV로 직접 구현할 수 있는 수준  
> 권장 기간: 32주(약 8개월), 평일 1~2시간 + 주말 3~5시간

## 이 학습 노트의 사용법

이 과정은 `Camera → Lens → Image → Processing → Alignment → ROI → Calibration → Inspection → Result`의 연결을 반복해서 학습한다. 문서를 읽는 데 그치지 말고 각 Chapter의 계산 문제, C++ 실습, 면접 답변을 함께 수행한다.

현재는 첫 학습 단위만 작성되어 있다.

1. [[00-roadmap|전체 로드맵]]을 읽고 학습 순서를 확인한다.
2. [[01-equipment-vision-overview|Chapter 1. 검사 장비와 비전 SW 전체 구조]]를 학습한다.
3. [[02-image-basic|Chapter 2. Image와 Pixel 기본]]을 학습한다.
4. [[03-camera-pixel|Chapter 3. Camera Pixel Size와 실제 물체의 관계]]를 학습한다.
5. [[04-lens-optics|Chapter 4. Camera + Lens + Optical System]]을 학습한다.
6. [[05-fov-resolution|Chapter 5. FOV · Resolution · Magnification 집중 계산]]을 학습한다.
7. 각 Chapter의 실습과 면접 질문에 답한 뒤 다음 Chapter로 이동한다.

## 최종 학습 목표

- Camera Pixel Size, Lens Magnification, FOV, Object Space Resolution의 관계를 계산하고 설명한다.
- Align과 Calibration의 차이를 구분하고 Image Coordinate를 Machine Coordinate로 변환한다.
- Threshold, Edge, Blob, Morphology, Pattern Matching을 C++/OpenCV로 구현한다.
- Camera에서 Result/Review/CIM까지 이어지는 검사 Pipeline을 설계한다.
- Recipe, Parameter, Result, NG Image를 포함한 검사 SW 구조를 설계한다.
- 비전 엔지니어와 조명, 광학 조건, 검사 알고리즘 및 오차 원인을 기술적으로 논의한다.

## 나의 출발점

- 강점: C++ 기반 장비 제어, UI/Review, CIM 개발 경험 및 장비 도메인 이해
- 보완 영역: 머신비전, 영상처리, 카메라·렌즈·조명, Align, Calibration, 검사 알고리즘
- 학습 전략: 프로그래밍 문법보다 **물리량의 의미, 좌표계, 데이터 흐름, 오차 전파, 검사 조건**에 집중

## 반드시 먼저 공부할 선수 지식

| 순서 | 내용 | 필요한 이유 | 우선순위 |
|---:|---|---|:---:|
| 1 | 검사 장비 데이터 흐름과 모듈 책임 | 알고리즘이 장비 SW 어디에 위치하는지 이해 | 🔴 |
| 2 | 단위 변환(mm, μm, pixel) | FOV·분해능·측정값 계산의 기초 | 🔴 |
| 3 | 2D 좌표와 행렬 기초 | Align·ROI Transform·Calibration의 기반 | 🔴 |
| 4 | Image/Pixel/Gray Level/Bit Depth | 모든 영상처리의 입력 표현 | 🔴 |
| 5 | C++17, STL, RAII, 예외 처리 | 안정적인 검사 Pipeline 구현 | 🟠 |
| 6 | OpenCV의 `cv::Mat`과 기본 I/O | 실습 구현의 공통 도구 | 🟠 |
| 7 | 기초 통계(평균, 분산, 표준편차) | 노이즈와 Threshold 판단 | 🟠 |
| 8 | 삼각함수와 회전 | X/Y/Theta 좌표 변환 | 🟠 |

## 우선순위 기준

- 🔴 반드시 알아야 함: 구현·협업·면접에 직접 필요한 핵심
- 🟠 실무에서 중요: 검사 성능과 장애 분석에 자주 사용
- 🟡 알아두면 좋음: 응용 범위를 넓히는 내용
- ⚪ 현재는 몰라도 됨: 현 목표에서 우선순위가 낮은 심화 이론

시간이 부족하면 아래 순서로 압축 학습한다.

1. 🔴 Chapter 1~5: 전체 흐름과 Camera/Lens/FOV
2. 🔴 Chapter 8~12: 영상처리, ROI, Align, Calibration, 좌표계
3. 🔴 Chapter 13~16: 검사 알고리즘과 제품 SW 구조
4. 🟠 조명·광학 해상도 보강
5. 🟡 면접 정리와 선택 심화

## 전체 Progress Checklist

- [ ] Phase 0. 검사 장비 구조
- [ ] Phase 1. Image 기본
- [ ] Phase 2. Camera / Pixel
- [ ] Phase 3. Lens / Optical
- [ ] Phase 4. FOV / Resolution
- [ ] Phase 5. Optical Resolution
- [ ] Phase 6. Illumination
- [ ] Phase 7. Image Processing
- [ ] Phase 8. ROI
- [ ] Phase 9. Alignment
- [ ] Phase 10. Calibration
- [ ] Phase 11. Camera Calibration
- [ ] Phase 12. Coordinate System
- [ ] Phase 13. Inspection Algorithm
- [ ] Phase 14. Inspection Pipeline
- [ ] Phase 15. Recipe / Architecture
- [ ] Phase 16. C++ Implementation
- [ ] Phase 17. Interview
- [ ] Final Project

## 프로젝트 진행 순서

1. Image Load → Gray → Threshold → Blob
2. Edge 위치 측정
3. Blob 특징 측정
4. Pattern Matching과 X/Y/Theta Align
5. Calibration과 좌표 변환
6. Recipe 기반 Inspection Engine
7. 최종 Mini Vision Inspection System

## 면접 준비 방법

각 질문을 세 단계로 연습한다.

1. **초보자 설명**: 비유와 쉬운 숫자로 정확히 설명한다.
2. **실무자 설명**: 오차 원인, 모듈 책임, 검증 방법을 포함한다.
3. **30초 답변**: 정의 → 필요한 이유 → 장비 예시 순으로 압축한다.

답변을 외우기보다 직접 그린 Pipeline과 계산식을 보며 말한다. 모든 기술 용어는 실제 프로젝트 경험인 Review/CIM/UI/장비 제어와 연결한다.

## 문서 목록

- [[00-roadmap|00. 32주 학습 로드맵]]
- [[01-equipment-vision-overview|01. 검사 장비와 비전 SW 전체 구조]]
- [[02-image-basic|02. Image와 Pixel 기본]]
- [[03-camera-pixel|03. Camera Pixel Size와 실제 물체의 관계]]
- [[04-lens-optics|04. Camera + Lens + Optical System]]
- [[05-fov-resolution|05. FOV · Resolution · Magnification 집중 계산]]
- [[VALIDATION|문서·수식·C++ 검증 기록]]

> 이후 Chapter는 앞 Chapter 학습과 질문 정리가 끝난 뒤 순차적으로 추가한다.

## 생성 후 검증 원칙

앞으로 모든 Chapter는 초안 작성 후 바로 완료 처리하지 않고, [[VALIDATION|공통 검증 절차]]에 따라 다시 확인한다. 특히 광학 수식은 단위와 전제 조건을 함께 검토하고, C++ 예제는 필요한 표준 헤더, 입력 유효성, OpenCV 자료형, 좌표·단위 및 NG/Error 구분을 확인한다.
