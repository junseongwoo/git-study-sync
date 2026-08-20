# 00. 6~9개월 집중 학습 로드맵

## 운영 기준

- 표준 과정: 32주, 주당 10~15시간
- 여유 과정: 36주, 주당 8~12시간
- 빠른 과정: 26주, 주당 12~18시간
- 권장 리듬: 평일 개념·계산·짧은 코드, 주말 통합 실습·회고
- 매 4주차: 새 내용 70%, 복습·리팩터링·면접 연습 30%

## 단계별 로드맵

| 기간         | Phase                           | 학습 결과물                                          |
| ---------- | ------------------------------- | ----------------------------------------------- |
| 1~2주       | Phase 0. 검사 장비 구조               | Acquisition부터 CIM까지 데이터 흐름도와 인터페이스 정의           |
| 3~4주       | Phase 1. Image 기본               | Bit Depth·Pixel·Resolution 설명 및 `cv::Mat` 분석 도구 |
| 5~6주       | Phase 2. Camera / Pixel         | Pixel Size와 Object Space Pixel Resolution 계산기   |
| 7~8주       | Phase 3. Lens / Optical         | Camera-Lens-Object 관계도와 렌즈 선정표                  |
| 9~10주      | Phase 4. FOV / Resolution       | 배율별 FOV·샘플링 계산 및 요구사항 역산                        |
| 11~12주     | Phase 5. Optical Resolution     | Defect 검출 가능성 평가표, Blur/MTF/Sampling 실험         |
| 13~14주     | Phase 6. Illumination           | 조명별 영상 비교 및 조명 선정 근거                            |
| 15~18주     | Phase 7. Image Processing       | Threshold/Filter/Edge/Morphology/Blob 실습 3종     |
| 19주        | Phase 8. ROI                    | Static/Dynamic ROI와 Transform 구현                |
| 20~22주     | Phase 9. Alignment              | Pattern Matching 기반 X/Y/Theta 보정                |
| 23~24주     | Phase 10. Calibration           | Image → Machine 좌표 변환 모듈                        |
| 25주        | Phase 11. Camera Calibration    | 왜곡 보정 및 Intrinsic/Extrinsic 해석                  |
| 26주        | Phase 12. Coordinate System     | 좌표계 계약서와 변환 검증 테스트                              |
| 27~28주     | Phase 13. Inspection Algorithm  | Presence/치수/결함 검사 선택표와 구현                       |
| 29주        | Phase 14. Inspection Pipeline   | 단계별 책임과 오류 처리 Pipeline                          |
| 30주        | Phase 15. Recipe / Architecture | Recipe·Result·NG Image 저장 구조                    |
| 31주        | Phase 16. C++ Implementation    | RAII·병렬 처리·Unit Test를 적용한 엔진                    |
| 32주        | Phase 17 + Final Project 계획     | 면접 답변 정리와 최종 시스템 설계서                            |
| 33~36주(선택) | Final Project                   | Mini Vision Inspection System 완성·검증             |

## 전체 Chapter 목록

| No. | 제목 | 핵심 내용 | 난이도 | 중요도 | 예상 시간 |
|---:|---|---|:---:|:---:|---:|
| 1 | 검사 장비와 비전 SW 전체 구조 | Acquisition, Trigger, Recipe, Result, Review/CIM, 좌표계 | 입문 | 🔴 | 8~10시간 |
| 2 | Image 기본 | Pixel, Gray/RGB, Bit Depth, Dynamic Range, Resolution 용어 | 입문 | 🔴 | 8~10시간 |
| 3 | Camera Pixel과 실제 물체 | Sensor Size, Pixel Size, 배율, Object Space Resolution | 입문→중급 | 🔴 | 10~14시간 |
| 4 | Lens와 Optical System | Focal Length, Magnification, WD, DOF, Distortion | 중급 | 🔴 | 12~16시간 |
| 5 | FOV·Resolution·Magnification | 관계식, 요구사항 역산, 배율 비교 | 중급 | 🔴 | 10~14시간 |
| 6 | Optical Resolution과 검출 가능성 | Sampling, Nyquist, MTF, Focus, Blur | 중급 | 🟠 | 12~16시간 |
| 7 | Illumination | Bright/Dark Field, Back/Ring/Coaxial/Dome | 입문→중급 | 🟠 | 10~14시간 |
| 8 | 영상처리 기초 | Histogram, Filter, Edge, Morphology, Blob | 중급 | 🔴 | 24~32시간 |
| 9 | ROI | Static/Dynamic ROI, 이동·회전·Transform | 중급 | 🔴 | 8~10시간 |
| 10 | Alignment | Fiducial, Template/Feature Matching, X/Y/Theta | 중급→고급 | 🔴 | 16~22시간 |
| 11 | Calibration | Scale/Offset/Rotation, Affine, Homography | 중급→고급 | 🔴 | 14~18시간 |
| 12 | Camera Calibration | Intrinsic/Extrinsic, 렌즈 왜곡 보정 | 중급 | 🟠 | 8~12시간 |
| 13 | Coordinate System | Image/Camera/Stage/Machine/World 좌표 | 중급→고급 | 🔴 | 10~14시간 |
| 14 | 검사 알고리즘 | Presence, 치수, 위치, Scratch/Particle/Crack | 중급 | 🔴 | 16~22시간 |
| 15 | 검사 Pipeline | 전처리→Align→ROI→측정→판정→Result | 중급→고급 | 🔴 | 10~14시간 |
| 16 | Recipe와 검사 SW Architecture | Parameter, Engine, Result, Review Data | 고급 | 🔴 | 12~16시간 |
| 17 | Modern C++/OpenCV 구현 | RAII, const, 오류 처리, 성능, Unit Test | 중급→고급 | 🟠 | 10~14시간 |
| 18 | 면접 및 선택 심화 | 30초 답변, 트러블슈팅, DL 적용 경계 | 중급 | 🟠 | 10~14시간 |

## 우선순위별 핵심 개념

### 🔴 반드시 알아야 함

- Image/Pixel/Bit Depth와 각종 Resolution 용어 구분
- Pixel Size ÷ Magnification = Object Space Pixel Size
- Sensor Size, FOV, Magnification의 계산 관계
- Trigger, Exposure, Frame, Buffer와 Image Acquisition 흐름
- Threshold, Edge, Morphology, Blob, Pattern Matching의 선택 기준
- Static ROI와 Align 결과를 적용한 Dynamic ROI
- Align(X/Y/Theta)과 Calibration(Image↔Machine)의 목적 차이
- Affine Transform과 좌표계 방향·원점·단위
- Measurement와 Judgement의 분리
- Recipe/Result/NG Image/Review Data의 버전 및 추적성
- 실패를 Result로 보고할 오류와 시스템 예외의 구분

### 🟠 실무에서 중요

- Lens MTF, Optical Resolution, Nyquist Sampling
- Focus, Defocus, Motion Blur와 조명 변화
- 조명 기하에 따른 특징 강조
- Camera Calibration과 Distortion Correction
- 처리 시간 예산, 버퍼 수명, 멀티스레드 안전성
- Golden Image, Gauge R&R, 반복 정밀도와 재현성

### 🟡 알아두면 좋음

- Feature Matching, Homography의 응용 범위
- Sub-pixel 측정 원리와 한계
- Telecentric Lens의 장점과 선정 조건
- 전통적 비전으로 어려운 결함의 딥러닝 적용 판단

### ⚪ 현재는 몰라도 됨

- CNN/Transformer 모델 구조의 세부 유도
- 자율주행·얼굴 인식 중심 Computer Vision
- 3D Reconstruction의 심화 수학

## 먼저 익힐 계산

### 단위

```text
1 mm = 1,000 μm
1 μm = 0.001 mm
```

### 기본 광학·샘플링 관계

```text
Sensor Width = Pixel Count × Camera Pixel Size
FOV = Sensor Size ÷ Optical Magnification
Object Space Pixel Size = Camera Pixel Size ÷ Optical Magnification
또는 Object Space Pixel Size = FOV ÷ Image Pixel Count
```

이 식들은 이상적인 기하 모델이다. 실제 검출 성능은 렌즈 MTF, 초점, 조명, 노이즈, 모션, 알고리즘 및 필요한 픽셀 수의 영향을 함께 받는다.

## 주간 학습 루프

1. 월: 개념을 장비 Pipeline에 표시한다.
2. 화: 단위와 숫자 문제를 손으로 계산한다.
3. 수: 작은 C++/OpenCV 예제를 실행한다.
4. 목: 파라미터를 바꿔 결과와 실패 조건을 기록한다.
5. 금: 면접 질문을 30초로 답한다.
6. 주말: 미니 프로젝트 구현, 테스트, 회고 문서 작성.

## 다음 문서

[[01-equipment-vision-overview|Chapter 1. 검사 장비와 비전 SW 전체 구조]]
