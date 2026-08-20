# Project 04. 3-Mark 기반 370×470 Glass Align

> 연결 학습: [[../08-vision-align-glass|Glass Align]], [[../13-alignment-advanced|Alignment 심화]], [[../12-roi-transform|ROI Transform]]

## 1. 목적

Glass 중심을 원점으로 정의한 3개 Mark의 기준 좌표와 현재 검출 좌표로 X/Y/Theta를 구하고, Dynamic ROI를 현재 영상에 배치한다. Pattern 검출과 좌표 정합을 분리하고 오검·미검·잔차 정책을 구현한다.

## 2. 기준 형상

Glass 크기는 X 370 mm, Y 470 mm로 가정한다. Mark는 예를 들어 다음처럼 중심 기준에 배치한다.

```text
M1(-150, +200)        M2(+150, +200)
             Glass center(0, 0)
                    M3(0, -200)
```

실제 Mark 좌표는 도면과 Teach 결과로 확정한다. “X축에 대칭” 같은 설명만 저장하지 말고 각 Mark ID와 `(X_mm,Y_mm)`를 Recipe에 저장한다.

## 3. 요구사항

- Mark별 Reference 좌표, Search ROI, Detector Type을 정의한다.
- Template 또는 기하 검출로 Current 중심과 Score를 반환한다.
- 세 점 Rigid Transform을 최소제곱으로 계산한다.
- Mark별 잔차와 RMS/Max를 계산한다.
- 한 점 Outlier를 식별하되 2점 Fallback 허용 여부는 Recipe로 정한다.
- Glass 중심의 현재 위치와 보정 Stage 명령을 구분한다.
- Reference ROI를 Current Image로 변환한다.

## 4. Rigid Transform

기준점 \(p_i\), 현재점 \(q_i\)에 대해 다음 오차를 최소화한다.

$$
\min_{R,t}\sum_i\|q_i-(Rp_i+t)\|^2,\qquad R^TR=I,\det(R)=1
$$

중심을 뺀 점 집합으로 2D 회전 \(R\)을 구하고:

$$
t=\bar q-R\bar p
$$

Glass 중심이 기준 원점이면 Current 중심은 바로 \(t\)다. Stage가 움직이는 방향과 Glass가 영상에서 움직이는 방향은 반대일 수 있으므로 보정 명령은 별도 Image–Machine Transform과 부호 검증을 거친다.

## 5. 최초 Teach와 자동 검출

1. 안정된 광학 조건에서 기준 Glass를 촬영한다.
2. 기하 Mark이면 Circle/Cross/Contour 규칙으로 후보를 자동 검출한다.
3. 고유 Pattern이면 Mark별 Template과 기준 중심을 등록한다.
4. Mark ID를 도면 좌표와 연결한다.
5. Glass 중심 기준 Mark 좌표와 Search ROI를 Recipe에 저장한다.
6. 이후 생산에서는 Search ROI 내 Mark Pose를 검출하고 Reference와 Current를 대응한다.

Template은 모든 Mark에 무조건 필요한 것이 아니다. 다만 자동으로 “어떤 형상인지” 알 수 없는 복잡한 Mark에는 검출 모델 또는 Template이 필요하다.

## 6. 구현 단계

1. 합성 기준점 3개를 정의한다.
2. 알려진 회전 1.5°와 이동 `(2.0,-3.0)` mm를 적용해 Current 점을 만든다.
3. 추정 X/Y/Theta가 입력값과 일치하는지 확인한다.
4. Gaussian Noise와 한 점 Outlier를 추가한다.
5. Mark ID 뒤바뀜, Mirror 해, 180° 오류를 검출한다.
6. Reference ROI 사각형을 Current 영상에 Overlay한다.
7. Image 보정량을 Machine 명령으로 바꾸는 단위 이동 시험을 한다.

## 7. 품질 Gate

- Mark 수와 ID 유효
- Detector Score와 Peak Ratio
- 점 간 거리/삼각형 방향이 기준 허용 범위 안
- Rigid Fit RMS/Max 잔차 허용 범위 안
- X/Y/Theta가 기구 허용 이동 범위 안
- Transform 역변환 왕복 오차 허용 범위 안

Score가 높아도 기하 잔차가 크면 Align을 채택하지 않는다.

## 8. 정량 합격 기준

- Noise 없는 합성점: 이동 오차 ≤ 1e-9, 각도 오차 ≤ 1e-9°
- 정상 Noise Dataset: 중심 반복성 σ ≤ 요구값의 1/3
- Mark 하나를 5 mm 이동시킨 Outlier Dataset을 Invalid로 판정
- 모든 Dynamic ROI Corner의 왕복 오차 ≤ 1e-6 px
- 단위 Stage 이동 +1 mm X/Y에서 예상 Image 방향 확인
- 실제 Glass 30회 반복의 Mean/Std/Max 기록

## 9. 실패 시험

- Mark 0/1/2개만 검출
- M1/M2 ID 교환
- 세 점 거의 일직선
- 회전 Search 범위 초과
- 같은 모양의 가짜 Mark 추가
- Glass 일부가 FOV 밖
- Calibration ID 또는 Image Size 불일치

## 10. 제출물과 완료 점검

- [ ] Reference/Current/Glass/Machine 좌표 표
- [ ] Mark Detector와 Align Solver가 분리됨
- [ ] 3점 잔차 Vector Overlay
- [ ] Glass 중심과 Stage 보정값을 구분
- [ ] Template 없는 기하 검출과 Template 방식 선택 근거
- [ ] 2점 Fallback의 위험과 허용 조건
- [ ] 반복성/오차/Cycle Time 결과
- [ ] 실패 시 NG가 아닌 Invalid/Error 정책

