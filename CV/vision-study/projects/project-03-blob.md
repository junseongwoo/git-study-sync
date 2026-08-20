# Project 03. Blob 특징 기반 결함 검사

> 연결 학습: [[../11-image-processing-03-morphology-blob|Morphology와 Blob]], [[../16a-inspection-algorithms|산업 검사 알고리즘]], [[../16b-inspection-pipeline|검사 Pipeline]]

## 1. 목적

Threshold 결과의 Blob에서 면적, 중심, 둘레, 원형도, Aspect Ratio를 계산해 이물·Hole·누락 후보를 분류한다. 전처리 Parameter가 결함 크기에 미치는 영향과 Border/Touching Blob 정책을 검증한다.

## 2. 요구사항

- Binary Image 또는 Gray+Threshold를 입력한다.
- Connected Component와 Contour 결과의 차이를 설명한다.
- Blob Feature를 px 및 가능한 항목은 mm 단위로 반환한다.
- Border Touch, Hole, Parent/Child Contour 정책을 정의한다.
- 여러 조건을 AND/OR로 조합하는 판정 규칙을 둔다.
- Blob 없음과 Algorithm Error를 구분한다.

## 3. Feature 정의

면적 \(A\), 둘레 \(P\)인 Blob의 원형도는:

$$
C=\frac{4\pi A}{P^2}
$$

이상적인 원은 1에 가깝지만 Digital Contour, 작은 Blob, 둘레 계산법 때문에 1을 약간 벗어나거나 낮아질 수 있다. 폭 \(w\), 높이 \(h\)의 Aspect Ratio는 팀에서 `w/h`인지 `max/min`인지 명확히 고정한다.

직교 Scale \(s_x,s_y\)에서:

$$
A_{mm^2}=A_{px}s_xs_y
$$

둘레는 Anisotropic Scale이면 단일 평균 Scale을 곱하지 말고 Contour Segment별로 변환한다.

## 4. Pipeline

```text
Aligned ROI → Normalize/Background Difference
→ Threshold → Morphology → Label/Contour
→ Feature → Rule Filter → Aggregate Verdict → Overlay/Result
```

## 5. 구현 단계

1. 원, 사각형, 가느다란 Scratch 합성 영상을 만든다.
2. Connected Components의 Area/Centroid/Bounding Box를 확인한다.
3. Contour에서 Perimeter, Circularity, Convexity를 추가한다.
4. 1·3·5 px Kernel 변화에 따른 면적 편향을 표로 만든다.
5. Border Touch Blob을 제외/포함하는 두 정책을 시험한다.
6. Result에 각 Feature, 적용 Spec, Reason Code를 저장한다.
7. 여러 Blob의 Overall 판정 규칙을 자동 Test한다.

## 6. 정량 합격 기준

- 합성 사각형 Area/Centroid 기대값 일치
- 반지름 20 px 원의 면적 상대 오차를 이론값 \(\pi r^2\) 대비 기록
- 동일 입력 100회 Label 수와 판정 동일
- 결함 크기별 Detection Rate와 정상 영상 False Positive Rate 제시
- Border/Hole 정책별 예상 결과 자동 Test
- Invalid Input이 NG 통계에 포함되지 않을 것

## 7. Dataset 설계

- 크기 1~20 px의 점 결함
- 서로 0~5 px 간격인 두 Blob
- ROI Border를 가로지르는 Blob
- Hole이 있는 Ring 형상
- 긴 Scratch와 원형 Particle
- 불균일 배경과 조명 밝기 변화
- 정상 Texture를 결함으로 오인하기 쉬운 Hard Negative

## 8. Parameter 실험

Threshold, Kernel, Min Area를 한 번에 바꾸지 않는다. 각 조건에서 TP/FN/FP/TN을 저장하고 다음을 계산한다.

$$
\mathrm{Detection\ Rate}=\frac{TP}{TP+FN},\qquad
\mathrm{FPR}=\frac{FP}{FP+TN}
$$

미검 비용과 오검 비용이 다르면 단순 Accuracy 대신 공정 비용 또는 우선순위로 Operating Point를 선택한다.

## 9. 실패 주입

- Empty/Non-binary 입력
- NaN 또는 음수 Spec
- 최소 면적이 최대 면적보다 큰 Recipe
- 1 px Blob 수천 개로 인한 성능 저하
- Contour 둘레 0에 가까운 Degenerate 형상
- Calibration ID 불일치

## 10. 제출물과 완료 점검

- [ ] Feature 정의와 단위 표
- [ ] 합성/실제 Dataset 분리
- [ ] Kernel별 면적 편향 표
- [ ] Detection Rate/FPR와 Sample 수
- [ ] Worst False Positive/Negative 영상 분석
- [ ] Result에 Recipe/Calibration/SW 버전 포함
- [ ] Blob 없음, NG, Invalid, Error를 구분
- [ ] Raw와 Overlay를 별도 저장

