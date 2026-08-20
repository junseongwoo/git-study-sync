# Project 05. Image–Machine Calibration과 좌표 변환

> 연결 학습: [[../14a-calibration-coordinate-transform|Image–Machine Calibration]], [[../14b-camera-calibration|Camera Calibration]], [[../15-coordinate-systems|좌표계]]

## 1. 목적

Stage의 알려진 위치와 영상 Feature 좌표 쌍으로 Image↔Machine Transform을 계산하고 독립 Validation Point로 정확도를 평가한다. 학습점 Reprojection Error만 낮추는 것이 아니라 실제 이동 명령의 오차와 반복성을 검증한다.

## 2. 적용 모델 선택

- Scale+Translation: 축 정렬과 왜곡이 매우 작을 때
- Similarity: Translation, Rotation, Uniform Scale
- Affine: 축별 Scale과 Shear 포함
- Homography: 동일 평면의 Perspective 포함
- Distortion 보정+위 모델: Lens Distortion이 무시할 수 없을 때

자유도가 큰 모델이 항상 좋지 않다. 물리 조건을 만족하는 가장 단순한 모델을 고르고 독립점 오차로 비교한다.

## 3. 요구사항

- Image `(u_px,v_px)`와 Machine `(X_mm,Y_mm)`의 대응을 명시한다.
- 3×3 Homogeneous Matrix와 적용 방향을 저장한다.
- 학습점과 Validation Point를 분리한다.
- RMS, Max, 축별 Bias와 위치별 Vector를 계산한다.
- Inverse Transform과 왕복 오차를 검증한다.
- Camera/렌즈/해상도/Focus/Stage 조건과 Calibration ID를 저장한다.
- 범위 밖 외삽을 경고하거나 금지한다.

## 4. 오차 지표

예측 Machine 점 \(\hat P_i\), 실제 점 \(P_i\), 개수 \(N\)일 때:

$$
e_i=\|P_i-\hat P_i\|_2
$$

$$
\mathrm{RMS}=\sqrt{\frac{1}{N}\sum_i e_i^2},\qquad
\mathrm{Max}=\max_i e_i
$$

RMS만 작고 특정 Corner의 Max가 크면 실제 검사가 실패한다. X/Y Signed Error 평균으로 Bias도 확인한다.

## 5. Data 수집

1. 장비 Warm-up과 Focus/조명 조건을 고정한다.
2. 작업 영역 전체에 격자 위치를 배치한다.
3. Backlash 영향을 보기 위해 접근 방향을 통일하거나 양방향을 따로 측정한다.
4. 각 위치를 여러 번 촬영해 Feature 반복성을 기록한다.
5. 학습점과 독립 Validation Point를 공간적으로 분산한다.
6. 입력 순서, 단위, 좌표축 부호를 저장한다.

## 6. 구현 단계

1. 알려진 Affine Matrix로 합성 대응점을 만든다.
2. Matrix를 추정하고 계수/점 변환 오차를 검증한다.
3. Noise와 Outlier를 추가하고 RANSAC/Inlier 정책을 시험한다.
4. 실제 점으로 Similarity/Affine/Homography를 비교한다.
5. 독립 Validation RMS/Max가 가장 안정적인 모델을 선택한다.
6. Inverse와 `image→machine→image` 왕복을 Test한다.
7. Matrix, 조건, 잔차, 날짜를 버전 파일로 저장한다.

## 7. 정량 합격 기준

- 합성 Noise-free 점 변환 오차 ≤ 1e-9
- 독립 Validation RMS/Max가 장비 요구 오차 이하
- 30회 반복 σ가 Error Budget 이하
- 작업 범위 Corner를 포함
- 왕복 오차 ≤ 수치 허용오차
- Calibration ID 불일치 시 검사/이동 금지
- 이전 Calibration 대비 오차 악화 시 자동 승인 금지

## 8. Error Budget

독립 오차 성분을 단순 근사하면:

$$
\sigma_{total}\approx\sqrt{\sigma_{feature}^2+\sigma_{cal}^2+
\sigma_{stage}^2+\sigma_{fixture}^2}
$$

예를 들어 각각 0.010, 0.015, 0.020, 0.010 mm이면 총 약 0.0287 mm다. 독립이 아니거나 Bias가 있으면 RSS만으로 충분하지 않으며 별도 보정이 필요하다.

## 9. 실패 시험

- 좌표 대응 한 쌍 교환
- mm와 µm 혼용
- Image Y-down 부호 누락
- 좁은 중앙부 점만 학습
- Z 높이가 다른 대상 적용
- Stage 접근 방향 변경
- Lens 재장착 후 이전 ID 사용

## 10. 제출물과 완료 점검

- [ ] Model 선택 근거
- [ ] 학습/검증점 분리 Plot
- [ ] RMS/Max/Bias/Vector Map
- [ ] Inlier/Outlier와 원인 분석
- [ ] Forward/Inverse/왕복 Test
- [ ] 환경과 Calibration Version
- [ ] 실제 Stage 단위 이동 확인
- [ ] 재교정 Trigger와 승인 기준

