# Project 02. Edge 기반 위치와 폭 측정

> 연결 학습: [[../10-image-processing-02-filter-edge|Filtering과 Edge]], [[../05-fov-resolution|FOV와 Resolution]], [[../14a-calibration-coordinate-transform|단위 변환]]

## 1. 목적

1D Edge Profile 또는 2D Edge를 이용해 부품의 좌·우 경계를 찾고 Pixel 폭과 mm 폭을 측정한다. Canny 결과를 무조건 세는 방식이 아니라 측정 방향, 극성, Subpixel, Calibration을 설계한다.

## 2. 요구사항

- 기준 ROI와 측정 방향을 Recipe로 정의한다.
- 여러 Scan Line을 평균해 Noise를 줄인다.
- Gaussian Sigma와 Edge 극성(Dark→Bright/Bright→Dark)을 지정한다.
- Gradient Peak를 찾고 Subpixel 위치를 계산한다.
- 양 Edge 사이 폭을 px와 mm로 반환한다.
- Edge 없음, 한쪽만 검출, 후보 과다를 구분한다.

## 3. 측정 원리

평균 Profile \(I(x)\)의 Gradient \(g(x)\)에서 극성에 맞는 Peak를 찾는다. 정수 Peak \(x_0\) 주변 세 값으로 포물선 보간하면:

$$
\delta=\frac{1}{2}\frac{g(x_0-1)-g(x_0+1)}{g(x_0-1)-2g(x_0)+g(x_0+1)}
$$

$$
x_{sub}=x_0+\delta
$$

분모가 0에 가깝거나 \(|\delta|>1\)이면 Subpixel 결과를 무효화한다. 폭은 \(w_{px}=x_R-x_L\), 균일 Scale \(s\) mm/px이면 \(w_{mm}=s w_{px}\)다.

## 4. Pipeline

```text
Image/Aligned ROI → Validate → Scan-line Average
→ Gaussian 1D → Gradient → Polarity/Strength Filter
→ Left/Right Pairing → Subpixel → Unit Conversion → Judge
```

## 5. 구현 단계

1. 이상적인 Step Edge 합성 Profile을 만든다.
2. 정수 위치에서 Gradient Peak와 극성을 검증한다.
3. Blur, Gaussian Noise, 밝기 Offset을 단계별로 추가한다.
4. 여러 Scan Line 평균 전후의 위치 표준편차를 비교한다.
5. Edge Pair의 최소/최대 간격과 순서를 검증한다.
6. Calibration Scale과 ID를 Result에 저장한다.
7. ROI/Edge/측정선을 Overlay하되 원 수치는 별도로 보관한다.

## 6. 정량 합격 기준

- 이상적 합성 Edge 위치 오차 ≤ 0.05 px
- Noise Dataset의 폭 반복성 표준편차 ≤ 0.10 px
- Edge 극성이 반대면 잘못된 후보를 선택하지 않을 것
- 단위 변환 오차 ≤ 1e-9 mm(동일 Double 계산 기준)
- Validation Set의 Max 오차를 평균과 함께 제시할 것
- P99 처리 시간이 요구 Cycle Time 안일 것

## 7. Dataset과 시험

- Sharp/Blurred Edge
- Gradient 배경과 Vignetting
- Scratch가 Edge를 가로지르는 영상
- 한쪽 Edge가 ROI 밖인 영상
- Double Edge와 반사 Ghost
- 회전한 부품: Align 전후 비교
- 서로 다른 위치의 Calibration Validation Target

## 8. 주요 실패 원인

- Canny의 두꺼운 Edge 양쪽을 실제 두 경계로 오인
- ROI 회전 미적용으로 사선 폭을 측정
- 가장 큰 Gradient만 선택해 반사 Edge를 채택
- Pixel 폭을 단일 Scale로 변환했지만 Perspective가 큼
- Display 반올림값으로 Spec 판정

## 9. 제출물

- Profile/Gradient Plot
- Edge 후보와 선택 근거
- Ground Truth 대비 Mean/Std/Max 오차
- Noise/Blur별 성능 표
- px/mm Result와 Calibration ID
- 실패 영상 Replay Test

## 10. 완료 점검

- [ ] 측정 방향과 Edge 극성을 설명할 수 있다.
- [ ] Subpixel 분모와 범위를 검증한다.
- [ ] Edge 미검출을 0 px로 반환하지 않는다.
- [ ] Align Transform 후 ROI를 적용한다.
- [ ] 독립 Validation Target으로 mm 오차를 확인했다.

