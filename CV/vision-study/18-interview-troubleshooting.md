# 18일차. 비전·광학 통합 면접과 트러블슈팅

> Phase 17 · 권장 학습 시간: 16~20시간 · 난이도: 종합 · 핵심: 원리→수치→실험→판단

## 1. 이 Chapter의 목표

면접 답변은 용어 정의로 끝나지 않아야 한다. 다음 순서를 습관화한다.

1. 현상을 다시 정의한다.
2. 물리·좌표·데이터 흐름에서 원인 후보를 분류한다.
3. Log, Raw Image, 수치로 가설을 좁힌다.
4. 한 번에 한 조건만 바꾸는 실험을 설계한다.
5. 정확도, Cycle Time, 오검·미검 Trade-off를 설명한다.
6. 재발 방지를 Recipe, Calibration, Test, Monitoring에 반영한다.

---

## 2. 30초 답변 구조

```text
정의 1문장
→ 장비에서 중요한 이유
→ 핵심 수식/판단 기준
→ 실패 원인과 검증 방법
→ 실제 적용 예시
```

모르는 수치를 지어내지 않는다. “현재 정보만으로 단정할 수 없으며 Raw, Calibration ID, 조명 조건을 먼저 비교하겠습니다”처럼 필요한 증거를 말하는 것이 더 정확하다.

---

## 3. Camera·Lens·FOV 질문

### Q1. Pixel Size와 Object Resolution의 차이는?

Sensor Pixel Size는 Sensor의 물리 Pixel Pitch이고, Object Resolution은 물체 공간에서 Pixel 하나가 나타내는 길이다. FOV 폭 \(W\), 가로 Pixel 수 \(N\)이면:

$$
r_x = \frac{W}{N}\quad[\mathrm{mm/pixel}]
$$

FOV 100 mm, 2,000 px라면 0.05 mm/px = 50 µm/px다. 실제 검출 가능 크기는 Sampling만이 아니라 Lens MTF, 조명, SNR, 알고리즘에 좌우된다.

### Q2. 20 µm 결함을 20 µm/px로 검사할 수 있는가?

결함이 겨우 1 px이므로 안정적 형상 판별은 어렵다. 결함 검출에 필요한 최소 Pixel 수를 먼저 정하고 광학 Blur와 공정 변동을 포함해 여유를 둔다. “Pixel 해상도 = 검사 해상도”는 아니다.

### Q3. FOV가 부족하면 어떻게 하는가?

Sensor 해상도 증가, 배율 감소, Camera 추가, Stage Scan을 비교한다. 배율을 낮추면 FOV는 넓어지지만 Object Resolution이 나빠진다. Scan은 Stitching과 Cycle Time 오차를 추가한다.

### Q4. Lens를 바꾼 뒤 Calibration만 다시 하면 충분한가?

아니다. FOV, Working Distance, Focus, Distortion, 밝기, DOF, Telecentricity를 다시 확인하고 Camera Calibration 및 Image–Machine Calibration을 재수행한다. 기존 Recipe ROI와 Spec의 호환성도 검증한다.

---

## 4. 조명·영상 품질 질문

### Q5. Threshold가 매번 바뀌어야 하는 원인은?

제품 자체보다 먼저 조명 밝기·각도, 노출, Gain, 표면 반사, 주변광, Lens 오염, 광원 열화를 확인한다. Histogram의 평균만 보지 말고 대상/배경 분포, Saturation 비율, 시간 추세를 비교한다.

### Q6. Gain을 올리면 어두운 문제를 해결할 수 있는가?

Signal과 Noise를 함께 증폭하므로 마지막 수단에 가깝다. 노출 증가의 Motion Blur, 조명 증가의 Saturation·열, Aperture의 DOF 변화를 함께 비교한다.

### Q7. 반사 Glass의 Edge가 끊기는 이유는?

정반사 방향, 높이 변화, 편광, 보호 필름, 먼지가 주요 후보다. Dome/Coaxial/Dark-field 조명과 편광 조합을 동일 노출 조건에서 비교하고 Edge Profile과 Contrast를 수치화한다.

### Q8. 영상 품질을 어떤 지표로 관리하는가?

평균·표준편차, Saturation/Black 비율, 대상-배경 Contrast, Edge Gradient, Focus Metric, Pattern Score를 후보로 둔다. 단일 지표로 합격을 결정하지 말고 공정 정상 범위와 상관성을 검증한다.

---

## 5. 영상처리 질문

### Q9. Global Threshold와 Adaptive Threshold 선택 기준은?

배경 조명이 균일하고 Histogram이 분리되면 Global이 단순하고 안정적이다. 국부 밝기 변화가 크면 Adaptive를 고려하지만 Window Size가 결함 크기보다 작거나 비슷하면 결함을 배경으로 흡수할 수 있다.

### Q10. Gaussian과 Median Filter 차이는?

Gaussian은 일반 Noise 감소에 유용하지만 Edge를 흐린다. Median은 Salt-and-pepper Noise에 강하고 Edge 보존이 상대적으로 좋지만 Kernel이 크면 작은 결함을 제거한다. Filter는 “깨끗해 보임”이 아니라 검출률과 위치 오차로 평가한다.

### Q11. Morphology Kernel은 어떻게 정하는가?

제거하거나 연결할 Feature의 크기와 방향을 Object 단위에서 Pixel로 변환해 정한다. 60 µm 이물, 20 µm/px라면 약 3 px이므로 3×3 Kernel부터 실험하되 정상 결함까지 제거되는지 확인한다.

### Q12. Blob 면적을 mm²로 바꾸는 방법은?

직교하고 균일한 Scale이 \(s_x, s_y\) mm/px이면:

$$
A_{mm^2}=A_{px}\,s_xs_y
$$

Perspective나 Distortion이 크면 위치별 Scale이 달라지므로 World Plane으로 윤곽점을 변환하거나 Homography Jacobian을 고려한다.

---

## 6. Align·좌표 질문

### Q13. 두 Mark로 회전각을 계산하는 방법은?

기준 두 점 \(P_1^r,P_2^r\), 현재 두 점 \(P_1^c,P_2^c\)에서:

$$
\theta=\operatorname{atan2}(\Delta y_c,\Delta x_c)
-\operatorname{atan2}(\Delta y_r,\Delta x_r)
$$

점 순서가 뒤집히면 약 180° 오류가 나므로 Mark ID와 방향을 고정한다.

### Q14. 세 Mark를 쓰는 이유는?

Noise 평균화, 잘못된 Mark 검출 확인, Scale/Shear 또는 Glass 변형 진단에 유리하다. 3점이 거의 일직선이면 수직 방향 오차에 약하므로 넓게 배치한다.

### Q15. Glass 중심 기준 Align은 어떻게 계산하는가?

Mark Reference 좌표를 Glass 중심 기준으로 등록하고 현재 Mark와의 Rigid Transform을 최소제곱으로 구한다. 중심 좌표 \(C_r=(0,0)\)의 현재 위치는 \(C_c=RC_r+t=t\)다. Stage 보정 방향은 Camera/Image/Machine 좌표 부호를 확인해 Transform의 역변환으로 명령한다.

### Q16. Mark가 회전했는데 중심을 어떻게 찾는가?

회전해도 물리 Mark의 중심은 같이 변환된다. 회전에 강한 Shape/Edge/Contour Matching으로 전체 Pose를 찾거나, 대칭 형상이라면 Blob/원·십자 교점으로 중심을 구한다. Template 기반이면 Search Angle 범위를 주고 Subpixel Pose를 반환한다.

### Q17. 최초 Align Mark Image는 반드시 필요한가?

항상 필요한 것은 아니다. 원·십자·Hole처럼 형상이 알고리즘으로 정의되면 Template 없이 검출할 수 있다. 복잡한 고유 Mark의 Pattern Matching에는 좋은 기준 Template이 필요하며, 최초 Teach 과정에서 Mark ROI, 중심, Glass 중심 대비 좌표를 등록한다. 자동 검출과 기준 좌표 등록은 서로 다른 문제다.

---

## 7. Calibration 질문

### Q18. Align과 Calibration의 차이는?

Calibration은 좌표계 사이의 지속적인 관계를 구하고, Align은 매 제품의 현재 Pose를 구한다. Calibration 오류를 Align 보정값으로 숨기면 위치별 잔차가 남는다.

### Q19. Homography는 언제 쓰는가?

평면 대상의 Perspective 관계를 8자유도로 표현할 때 사용한다. 최소 4쌍이 필요하지만 실제로는 넓게 분포한 더 많은 점과 RANSAC/잔차 평가를 사용한다. 3D 높이 변화가 있으면 하나의 평면 Homography만으로 해결되지 않는다.

### Q20. Calibration 품질은 무엇으로 판단하는가?

학습 점의 평균 오차만 보지 말고 독립 Validation Point의 RMS, Max, 위치별 Vector Map을 본다. 반복 촬영 Reproducibility와 왕복 Transform 오차도 확인한다.

### Q21. RMS가 작은데 실제 위치 오차가 큰 이유는?

같은 학습 점으로만 평가한 과적합, 좁은 점 분포, 잘못된 좌표 대응, Stage Backlash, Z 높이 차이, Distortion 미보정, 단위 오류가 후보다. 독립 점과 접근 방향을 바꿔 검증한다.

---

## 8. 검사 Pipeline·SW 질문

### Q22. 제품 NG와 System Error를 왜 구분하는가?

NG는 유효한 검사 결과이고 Error는 결과 신뢰성이 없는 실행 실패다. 둘을 섞으면 수율, 설비 가동률, 알람, 재검 정책이 모두 왜곡된다.

### Q23. Recipe Snapshot이 필요한 이유는?

한 제품 처리 중 Parameter가 바뀌는 혼합 조건을 막는다. 검사 시작 시 불변 Snapshot을 고정하고 Result에 Revision, Calibration ID, SW Build를 남긴다.

### Q24. `cv::Mat`을 Queue로 넘길 때 주의점은?

OpenCV 소유 Buffer인지 외부 SDK Buffer인지 확인한다. SDK가 Callback 후 재사용하면 `clone()`하거나 Buffer Handle의 수명을 완료 시점까지 보장해야 한다.

### Q25. Cycle Time이 가끔 급증할 때 무엇을 보는가?

평균이 아니라 Stage별 P95/P99, Queue Depth, Disk/Network 지연, OS Scheduling, 메모리 할당, OpenCV 중첩 Thread, Thermal Throttling을 시간축으로 맞춰 본다.

---

## 9. 트러블슈팅 시나리오

### 시나리오 A. 특정 시간대에만 오검 증가

1. 오검 Raw와 정상 Raw를 같은 Recipe로 Replay한다.
2. 조명/노출/Gain, 영상 평균, Contrast, Focus 추세를 비교한다.
3. 설비 온도, 주변광, 광원 점등 누적 시간과 상관관계를 본다.
4. 한 조건씩 고정해 재현한다.
5. 원인이 광원 열화라면 Parameter 완화만 하지 말고 광원 관리와 품질 Gate를 추가한다.

### 시나리오 B. 화면에서는 맞는데 Stage 보정 방향이 반대

1. Image Y-down, Machine Y-up 여부를 확인한다.
2. 현재→기준과 기준→현재 Transform 방향을 확인한다.
3. Camera 이동과 대상 이동의 부호 차이를 확인한다.
4. +X/+Y 단위 이동 실험으로 Jacobian 부호를 검증한다.

### 시나리오 C. Recipe 변경 직후 일부 제품만 이상

Frame별 Recipe Revision과 Camera 설정 적용 ACK를 비교한다. 제품 중간에 Mutable Parameter를 읽었는지 확인하고 Safe Point의 Transactional Activation으로 수정한다.

### 시나리오 D. Align Score는 높은데 ROI가 어긋남

잘못된 유사 Mark, Template 중심 Offset, 회전 중심 오류, 좌표 Transform 순서, Scale 변화가 후보다. 세 Mark 잔차와 Overlay를 위치별로 확인한다.

---

## 10. 실전 답변 훈련

아래 질문마다 ①초보자 설명 ②실무자 설명 ③30초 답변을 직접 작성한다.

1. 검사 분해능을 어떻게 산정합니까?
2. 조명 조건을 어떤 순서로 선정합니까?
3. Threshold 오검을 어떻게 개선합니까?
4. 3개 Align Mark의 Outlier를 어떻게 찾습니까?
5. Calibration 재수행 조건은 무엇입니까?
6. NG Image로 문제를 어떻게 재현합니까?
7. 장시간 운전 안정성을 어떻게 검증합니까?
8. 미검과 오검 중 무엇을 우선합니까?

마지막 질문에는 정답이 하나가 아니다. 결함 위험, 후공정 검출 가능성, Scrap/Rework 비용, 고객 요구를 수치로 비교해야 한다.

---

## 11. 포트폴리오 설명 구조

프로젝트를 설명할 때 다음 증거를 준비한다.

- 문제: 대상, 결함, 요구 Cycle Time/정확도
- 광학: FOV, Resolution, 조명 선정 근거
- 알고리즘: 후보 비교와 선택 이유
- 좌표: Reference/Current/Machine Transform
- SW: Recipe Snapshot, Result, Error 정책
- 검증: Dataset 분리, Detection Rate, False Positive, 반복성, P99
- 실패: 가장 큰 오판과 개선 과정

정확도만 제시하지 말고 Sample 수와 정의를 함께 말한다.

$$
\mathrm{Detection\ Rate}=\frac{TP}{TP+FN},\qquad
\mathrm{False\ Positive\ Rate}=\frac{FP}{FP+TN}
$$

Threshold를 Test Set에 맞춰 고른 뒤 같은 Test Set 성능을 보고하면 낙관적 편향이 생긴다. Train/Validation/Test 또는 개발/고정 평가 Dataset을 분리한다.

---

## 12. 통과 기준

- [ ] FOV, mm/px, 면적 단위 변환을 계산할 수 있다.
- [ ] 광학 Resolution과 Pixel Sampling의 차이를 설명할 수 있다.
- [ ] Threshold/Edge/Blob/Matching 선택 이유를 말할 수 있다.
- [ ] 두 점 회전각과 3점 Rigid Align을 설명할 수 있다.
- [ ] Align과 Calibration의 차이를 설명할 수 있다.
- [ ] NG/Invalid/Error를 구분할 수 있다.
- [ ] Recipe Snapshot과 Result Traceability를 설계할 수 있다.
- [ ] Camera Buffer 수명과 `cv::Mat` 복사를 설명할 수 있다.
- [ ] 재현 가능한 장애 분석 실험을 설계할 수 있다.
- [ ] 정확도, 반복성, Cycle Time을 수치로 제시할 수 있다.

하나라도 막히면 관련 Chapter로 돌아가 계산·실습을 다시 수행한다. 다음 단계는 개념을 작은 실행 단위로 묶는 단계별 프로젝트다.

