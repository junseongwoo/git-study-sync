# Threshold, 카메라 해상도, DenseMap Defect 분석

## 1. 문서 목적

이 문서는 다음 세 가지 질문을 현재 코드와 관련 Docs를 교차 확인해 설명한다.

1. 검사 Pattern의 Threshold를 30에서 50으로 높이거나 50에서 30으로 낮추면 무엇이 달라지는가?
2. 카메라 영상에서 “1 Pixel당 몇 µm”라는 말은 이미지와 장비 관점에서 각각 무엇을 뜻하는가?
3. 표준맵을 사용하지 않는 DenseMap 검사에서 암점, 암선, 명점, 명선, 미점등, 점등불량을 어떻게 검출하고 분류하는가?

> NOTE
>
> 이 문서에서 `Threshold`는 영상에서 밝은 Dot Blob을 찾기 위한 이진화 임계값이다.  
> Dot의 최종 밝기 등급을 나누는 Grade 기준이나 명점 WD 기준과는 서로 다른 값이다.
>
> 사용자가 예로 든 약 3.3~3.7 µm/px는 장비의 확정값으로 사용하지 않는다. 정확한 값은 선택한 Recipe의 물리 Pitch와 해당 광학 조건에서 실측한 영상 Pitch로 계산해야 한다.
>
> 코드와 Docs가 충돌하면 현재 실행 코드와 runtime Recipe를 기준으로 적었으며, 확인되지 않은 제작 의도는 기술하지 않는다.

### 핵심 요약

- Threshold는 Dot 좌표를 찾는 검출 민감도다.
- 최종 Defect는 별도로 측정한 밝기 Level과 공간 배열을 이용해 분류한다.
- µm/px는 영상 1칸이 제품면의 어느 길이를 나타내는지 표현한 공간 환산값이다.

---

## 2. 먼저 구분해야 하는 세 가지 Threshold

Recipe와 판정 설정에는 서로 다른 역할의 기준값이 존재한다.

| 구분 | 기본 예 | 역할 |
|---|---:|---|
| 영상 검출 Threshold | 30 | 밝은 Blob을 검출해 Dot 위치와 DenseMap을 만들기 위한 이진화 기준 |
| Grade 기준 | 코드 기본 A 50%, B 30%, C 10% | 측정한 Dot 밝기를 A/B/C/D로 나누는 기준. 실제 검사는 선택 Recipe 값을 사용 |
| White Defect Threshold | 50% | 다른 RGB 위상 위치의 발광을 명점 WD로 인정하는 기준 |

예를 들어 검사 Pattern 탭의 Threshold를 30에서 50으로 변경했다고 해서 D 등급 기준이 30%에서 50%로 바뀌는 것은 아니다.

```text
영상 Threshold
→ Dot으로 사용할 Blob을 찾음
→ DenseMap 좌표 생성

Grade Threshold
→ 생성된 좌표에서 밝기 측정
→ A/B/C/D 분류

White Defect Threshold
→ 다른 RGB 위상 좌표의 밝기 측정
→ 명점 WD 분류
```

### 핵심 요약

> Threshold 30과 Grade B 기준 30%는 숫자가 같아 보여도 전혀 다른 값이다.

---

## 3. 영상 Threshold가 의미하는 것

### 3.1 이진화의 의미

영상의 각 Pixel은 밝기값을 가진다. 이진화는 각 Pixel을 밝은 영역과 배경으로 둘 중 하나로 나누는 과정이다.

OpenCV Binary Threshold의 개념은 다음과 같다.

```text
검출 Source의 Pixel 값 > Threshold
→ 255, 밝은 영역

검출 Source의 Pixel 값 <= Threshold
→ 0, 배경
```

Threshold가 30이면 30보다 큰 Pixel이 밝은 영역으로 남고, Threshold가 50이면 50보다 큰 Pixel만 남는다.

단, 현재 DenseMap 검사의 배경 평탄화가 활성화되어 있으면 원본 Gray 영상에 바로 Threshold를 적용하지 않는다.

```text
원본 Gray
→ White Top-hat
→ 완만한 배경 밝기 제거
→ 지역 배경보다 돌출된 밝기 성분
→ Threshold
```

따라서 배경 평탄화가 켜진 상태의 Threshold 30은 보통 “원본 Gray가 30 이상”이라는 의미보다 “지역 배경보다 밝게 돌출된 값이 30을 넘는다”는 의미에 가깝다.

### 핵심 요약

- Threshold는 Gray Level을 직접 Defect로 판정하는 값이 아니다.
- 배경 평탄화가 켜지면 지역 대비가 큰 밝은 Blob을 선택하는 기준이 된다.

### 3.1.1 “영상이 밝다”와 “Dot이 밝다”를 구분해야 하는 이유

현재 코드의 검출 Source는 다음 두 경우 중 하나다.

```text
배경 평탄화 OFF
DetectionSource(x,y) = Gray(x,y)

배경 평탄화 ON
DetectionSource(x,y) = Gray(x,y) - Opening(Gray, Kernel)(x,y)
```

그 후 정확한 이진화 조건은 다음과 같다.

```text
DetectionSource(x,y) > Threshold  → 255
DetectionSource(x,y) <= Threshold → 0
```

따라서 밝기 변화는 다음과 같이 나눠 해석해야 한다.

| 실제 변화 | 배경 평탄화 OFF | 배경 평탄화 ON |
|---|---|---|
| Dot만 배경보다 더 밝아짐 | Dot Pixel이 Threshold를 넘기 쉬워짐 | Top-hat 잔차가 커진 Pixel이 Threshold를 넘기 쉬워짐 |
| Dot만 어두워짐 | Dot Pixel이 Threshold 아래로 내려가기 쉬움 | Top-hat 잔차가 작아진 Pixel이 Threshold 아래로 내려가기 쉬움 |
| 배경만 밝아짐 | 배경까지 전경이 되어 노이즈·병합 가능 | 완만한 배경 성분은 opening으로 제거되는 방향 |
| 영상 전체에 일정한 밝기값이 더해짐 | 더 많은 Pixel이 Threshold를 넘을 수 있음 | 포화가 없고 opening 결과도 같은 양만큼 이동하면 차영상은 변하지 않음 |
| Exposure·PG 변화로 Dot과 배경의 값 및 대비가 함께 변함 | 실제 Gray 분포가 Threshold를 통과하는지에 따라 결정 | 실제 Top-hat 잔차 분포가 Threshold를 통과하는지에 따라 결정 |

마지막 두 행의 결과를 이미지 없이 “항상 증가” 또는 “항상 감소”라고 단정할 수는 없다. 코드가 판정하는 것은 원인 이름이 아니라 **실제로 계산된 DetectionSource의 각 Pixel이 Threshold를 넘었는지** 여부다.

---

### 3.2 하나의 Dot에서 Threshold를 30에서 50으로 올리는 경우

Dot은 보통 중앙이 밝고 가장자리로 갈수록 어두운 형태다.

예를 들어 Top-hat 이후 Dot 단면이 다음과 같다고 가정한다.

```text
10  20  30  20  10
20  40  55  40  20
30  55  70  55  30
20  40  55  40  20
10  20  30  20  10
```

Threshold 30에서는 30보다 큰 부분, 즉 정수 8-bit 영상이라면 31~255가 남는다.

```text
0 0 0 0 0
0 1 1 1 0
0 1 1 1 0
0 1 1 1 0
0 0 0 0 0
```

Threshold 50에서는 50보다 큰 중앙부, 즉 51~255만 남는다.

```text
0 0 0 0 0
0 0 1 0 0
0 1 1 1 0
0 0 1 0 0
0 0 0 0 0
```

실제 검사에서 나타나는 변화는 다음과 같다.

| 항목 | 30 → 50 변경 영향 |
|---|---|
| Binary 전경 Pixel | DetectionSource 값 31~50인 Pixel이 255에서 0으로 바뀜. 전경 집합은 반드시 같거나 작아짐 |
| 개별 연결 성분 | 줄거나 사라질 수 있고, 하나의 성분이 여러 개로 분리될 수도 있음 |
| 형상 필터 전 Blob 면적 | 전경 Pixel이 제거되므로 전체 전경 면적은 증가하지 않음 |
| 형상 필터 통과 Object 수 | 감소·유지·증가 모두 가능. 분리와 Min/Max 형상 필터 결과에 따라 결정 |
| 약한 Dot | 잔차 Peak가 50 이하이면 사라짐 |
| 배경 노이즈 | 잔차가 31~50이면 제거됨 |
| 인접 Dot 병합 | 두 Dot을 잇던 잔차가 제거되면 분리될 수 있음 |
| `MinArea` 미만 탈락 | 증가할 수 있음 |
| DenseMap 실제 Object Anchor | 감소할 수 있음 |
| Predicted 좌표 | 증가할 수 있음 |
| Seed 검출 실패 | Threshold가 과도하면 발생 가능 |

Peak가 45인 약한 Dot은 Threshold 30에서는 검출되지만 Threshold 50에서는 Binary 영상에서 완전히 사라진다.

그러나 “Blob으로 검출되지 않았다”와 “최종 밝기를 측정하지 않는다”는 같은 의미가 아니다.

DenseMap이 주변 Dot으로 정상적으로 만들어졌다면 검출되지 않은 칸에도 Pitch 기반 Predicted 좌표를 만든다. 그 좌표에서 원본 영상 밝기를 7 × 7 Gaussian으로 측정한다.

```text
Threshold 50에서 Blob 검출 실패
→ 주변 DenseMap으로 좌표 예측
→ 예측 위치에서 원본 밝기 측정
→ Normal 대비 비율로 Grade 계산
```

따라서 약한 Dot은 좌표 검출 단계에서는 사라져도 Predicted 좌표에서 최종 Level과 Grade가 계산된다.

현재 IP 결과 조립에서는 이렇게 샘플링한 `LevelSampleModel.IsMissingPoint`를 `false`로 기록한다. 따라서 현재 Console/uLed.Export 경로에서는 내부 `Predicted` 자체를 곧바로 암점으로 판정하지 않고, 샘플링된 Level이 최종 D인지로 암점 여부가 결정된다. `CellJudgmentAnalyzer`는 일반 입력 계약상 `Missing 또는 D`를 암점 Mask로 받을 수 있지만, 현재 IP가 만든 Pixel block의 missing flag는 모두 0이다.

문제는 Threshold가 너무 높아 정상 Dot 다수가 사라지는 경우다.

- DenseMap을 시작할 Seed를 찾지 못할 수 있다.
- 실제 Object Anchor가 부족해 Pitch 전파 오차가 커질 수 있다.
- 달라진 좌표에서 밝기를 측정하면 Level과 Grade 분포가 달라질 수 있다.
- R/G/B 세 채널 모두 맵 확정에 실패할 수 있다.
- 이 경우 ROI 중심 기준 격자에서 Level을 측정한 후 미점등 또는 점등불량으로 분류될 수 있다.

### 핵심 요약

> Threshold를 30에서 50으로 올리면 DetectionSource 값 31~50이 Binary 전경에서 제거된다. 약한 Dot과 약한 노이즈가 모두 제거 대상이며, 최종 유효 Object 수는 CCL 분리와 형상 필터까지 수행한 뒤에만 알 수 있다.

---

### 3.3 Threshold를 50에서 30으로 내리는 경우

Threshold를 낮추면 더 어두운 Pixel까지 밝은 영역에 포함된다.

| 항목 | 50 → 30 변경 영향 |
|---|---|
| Binary 전경 Pixel | DetectionSource 값 31~50인 Pixel이 0에서 255로 바뀜. 전경 집합은 반드시 같거나 커짐 |
| 개별 연결 성분 | 새로 생기거나 서로 병합될 수 있음 |
| 형상 필터 전 전경 면적 | 감소하지 않음 |
| 형상 필터 통과 Object 수 | 증가·유지·감소 모두 가능. 병합과 Min/Max 형상 필터 결과에 따라 결정 |
| 약한 Dot | 잔차가 31~50이면 전경에 포함 |
| 배경 노이즈 | 잔차가 31~50이면 함께 포함 |
| 먼지·반사·광학 노이즈 | Blob 후보로 들어올 가능성 증가 |
| 인접 Dot 병합 | 증가할 수 있음 |
| `MaxArea`, Width, Height 초과 | 증가할 수 있음 |
| 가짜 Seed 또는 오배정 | Threshold가 과도하게 낮으면 가능 |

낮은 Threshold가 항상 더 많은 유효 Object를 만드는 것은 아니다.

두 Dot 사이의 약한 밝기까지 연결되면 원래 두 개였던 Blob이 하나의 큰 Blob으로 합쳐질 수 있다.

```text
Threshold 50
→ Dot A와 Dot B가 각각 작은 Blob 2개

Threshold 30
→ 중간 밝기까지 연결
→ 큰 Blob 1개
→ MaxArea 또는 MaxWidth 초과로 탈락 가능
```

또한 배경 반사나 노이즈가 Object로 들어오면 다음 문제가 발생할 수 있다.

- Seed 후보가 잘못 선택됨
- 실제 Dot이 아닌 Blob이 Grid에 배정됨
- Object 검증에서 위치 잔차가 커져 Predicted로 강등됨
- 격자 밖에서 검출된 밝은 Blob이 명점 WD 후보가 됨
- Map Shift 점수가 왜곡될 수 있음

현재 알고리즘은 이를 줄이기 위해 다음 방어 로직을 사용한다.

1. Area, Width, Height 필터
2. Seed 주변 Pitch Consensus
3. 사용한 Object의 중복 배정 금지
4. 주변 Object와 Pitch 일관성 검증
5. 위치 잔차가 큰 Object의 Predicted 강등
6. Recipe 유효 Map과 관측 Object Mask의 Shift Matching

### 핵심 요약

> Threshold를 50에서 30으로 내리면 DetectionSource 값 31~50이 Binary 전경에 추가된다. 약한 Dot을 살릴 수 있지만 배경·반사·Dot 사이 연결부도 같은 조건으로 추가되므로 최종 Object 수는 반드시 증가하지 않는다.

---

### 3.4 Threshold는 최종 Dot 밝기값을 잘라내지 않는다

이 부분이 가장 중요하다.

Threshold가 50이라고 해서 최종 Dot Level이 50 미만이면 무조건 0으로 기록되는 구조가 아니다.

Threshold는 좌표 검출용 Binary 영상에만 적용된다. 최종 Level은 확정 또는 예측된 좌표에서 원본 Gray 영상을 다시 샘플링한다.

```text
검출용
원본 → Top-hat → Threshold → Blob 중심

밝기 판정용
원본 → 확정 좌표의 7×7 Gaussian Level → Normal 대비 비율 → Grade
```

예를 들어 다음 상황이 가능하다.

```text
Threshold = 50
Dot Blob 검출 = 실패
Predicted 좌표 = 정상
원본 Gaussian Level = 42
Normal Level = 100
Ratio = 42%
Grade = B
```

즉 Object로 검출하지 못했지만 밝기 Grade는 정상 범주가 될 수도 있다.

반대 상황도 가능하다.

```text
Threshold = 30
Dot Blob 검출 = 성공
원본 Gaussian Level = 8
Normal Level = 100
Ratio = 8%
Grade = D
```

Blob이 검출됐다고 해서 밝기가 정상인 것도 아니다. Threshold 검출은 위치를 찾기 위한 조건이고 Grade는 제품 밝기를 판정하기 위한 조건이다.

다만 “Threshold가 최종 Level에 전혀 영향을 주지 않는다”도 정확하지 않다.

```text
동일 이미지 + Threshold만 변경 + 최종 샘플 좌표도 동일
→ 원본 7×7 Level은 동일

동일 이미지 + Threshold 변경 + 기준 Object/Seed/Pitch/Shift/샘플 좌표 변경
→ 다른 위치를 샘플링하므로 Level·Normal·Grade가 달라질 수 있음
```

표준맵 미사용 경로에서는 첫 성공 기준 채널의 맵을 G/B도 공유한다. 따라서 R Threshold 변화로 R 맵 좌표가 달라지면 G/B 영상 자체는 같아도 G/B 샘플 좌표와 Level이 함께 달라질 수 있다.

화면 표현도 두 가지를 구분해야 한다.

| 화면·산출물 | Threshold 변경 시 표현 |
|---|---|
| Binary/Object 검출 Overlay | 30에서는 Blob이 넓고 많이 보이며, 50에서는 Blob이 작아지거나 약한 Blob이 사라짐 |
| 최종 Grade Overlay | Recipe Map의 유효 Dot마다 사각형을 표시하며, 사각형 색은 Threshold가 아니라 최종 A/B/C/D Grade로 결정 |
| Predicted Dot | 검출 Blob이 없어도 예측 좌표에 Grade 사각형이 표시될 수 있음 |

즉 Threshold를 올렸다고 최종 Overlay의 모든 Dot 사각형이 작아지는 것은 아니다. Blob 검출 Overlay에서는 크기가 달라지지만 최종 Grade Overlay는 논리 Dot 위치의 검사 결과를 표시한다.

### 핵심 요약

- 검출 성공은 정상 판정을 의미하지 않는다.
- 검출 실패도 바로 암점 판정을 의미하지 않는다.
- 좌표가 같다면 Threshold는 원본 Level 값을 자르지 않는다.
- Threshold 때문에 확정 좌표가 바뀌면 Level·Grade·Defect도 간접적으로 바뀔 수 있다.

---

### 3.5 Threshold가 너무 높거나 낮을 때의 전형적인 결과

| 상태 | 로그·결과에서 보이는 현상 | 예상 원인 |
|---|---|---|
| 너무 높음 | Object 수 급감 | 약한 Dot이 Binary에서 사라짐 |
| 너무 높음 | Predicted 수 증가 | 실제 Object Anchor 부족 |
| 너무 높음 | R 실패 후 G 또는 B가 기준 채널이 됨 | R Threshold 또는 R 점등 상태 문제 |
| 너무 높음 | 세 채널 맵 확정 실패 | Seed/Object가 없음 |
| 너무 높음 | D, 미점등, 점등불량 증가 가능 | 기준 맵 변경 또는 중심 배치 좌표에서 낮은 Level이 측정된 경우 |
| 너무 낮음 | Object 수가 많아지거나 오히려 감소 | 배경·반사 추가 또는 Blob 병합·형상 상한 탈락 |
| 너무 낮음 | Oversized penalty 증가 | Dot 간 Blob 병합 |
| 너무 낮음 | Rejected Object 증가 | 격자와 맞지 않는 Blob |
| 너무 낮음 | WD 명점 증가 | Off-grid 밝은 Blob 회수 |
| 너무 낮음 | Shift 또는 Seed 불안정 | 가짜 Object가 DenseMap에 영향 |

### 핵심 요약

Threshold의 적정값은 “Object가 가장 많아지는 값”이 아니라 정상 Dot을 안정적으로 분리하면서 배경·병합 Blob을 억제하는 값이다.

---

### 3.6 Multi-threshold의 동작

Recipe에 Threshold를 여러 개 입력할 수 있다.

```text
30, 40, 50
```

알고리즘은 각 Threshold를 병렬로 시험하고 다음 점수를 계산한다.

```text
score
  = Area/Width/Height 필터를 통과한 Object 수
  - Oversized Blob 면적 / (PitchX × PitchY)
```

동점이면 더 높은 Threshold를 선택한다.

예를 들어 다음과 같다고 가정한다.

| Threshold | 유효 Object | 병합 추정 Penalty | Score |
|---:|---:|---:|---:|
| 30 | 100,000 | 8,000 | 92,000 |
| 40 | 98,000 | 1,000 | 97,000 |
| 50 | 91,000 | 100 | 90,900 |

이 경우 Object 수만 보면 30이 가장 많지만 최종 선택은 Score가 높은 40이다.

로그에는 다음과 유사한 형식으로 남는다.

```text
Threshold=[30:100000(-8000),40:98000(-1000),50:91000(-100)->40]
```

### 핵심 요약

> Multi-threshold는 낮은 Threshold의 검출 이점과 Blob 병합 위험을 점수로 비교해 가장 안정적인 후보를 선택한다.

---

## 4. “1 Pixel당 몇 µm”의 정확한 의미

### 4.1 카메라 Pixel과 제품의 Dot은 다르다

이 프로젝트에서 구분해야 할 단위는 다음과 같다.

| 용어 | 의미 |
|---|---|
| Camera Pixel, px | 촬영된 디지털 이미지의 가장 작은 격자 한 칸 |
| Dot | Cell 안의 R/G/B Sub Dot을 포함하는 논리 표시 Dot |
| Sub Dot | R, G, B 각각의 발광 요소 |
| µm/px | 제품면에서 카메라 영상 1 Pixel이 나타내는 실제 길이 |

“1 Pixel이 3.5 µm”라는 말은 예를 들어 카메라 영상에서 서로 1 px 떨어진 두 영상 좌표가 검사 대상 Glass 면에서는 약 3.5 µm 떨어진 위치에 대응한다는 뜻이다.

```text
영상에서 1 px 이동
≈ 제품면에서 µm/px 값만큼 이동
```

이 문서의 µm/px는 카메라 센서 칩 위의 물리 Pixel Pitch를 뜻하지 않는다. 현재 프로젝트 코드는 제품의 물리 Dot Pitch와 영상에서 측정한 Dot 중심 간격을 이용해 **Glass 대상면 기준 환산값**을 만든다.

따라서 렌즈 배율, 카메라 설치 높이와 working distance, 포커스 조건이 반영된 object-space scale로 이해해야 한다.

### 핵심 요약

> µm/px는 “카메라 영상 좌표 차이를 Glass 대상면의 길이 차이로 번역하는 환산비”다.

---

### 4.2 현재 프로젝트가 µm/px를 계산하는 방법

현재 Console의 Recipe 업로드 경로는 Recipe의 물리 Dot Pitch와 Find Pitch에서 실측한 영상 Dot Pitch를 이용한다.

```text
CameraPixelSizeUm
  = DisplayPixelWidthUm
    / DisplayPixelPitchCameraPixelX
```

단위까지 쓰면 다음과 같다.

```text
µm/px
  = 논리 Dot의 실제 Pitch(µm)
    / 영상에서 같은 Dot Pitch가 차지한 Pixel 수(px)
```

예를 들어 실제 Dot Pitch가 `P_um`, 영상에서 측정한 Pitch가 `P_px`라면 다음과 같다.

```text
Object-space scale = P_um / P_px
```

따라서 약 3.3~3.7 µm/px라는 범위는 개념 설명에는 사용할 수 있지만, 그중 어느 값이 현재 장비의 정답인지는 선택 Recipe와 현재 Find Pitch 결과 없이 확정할 수 없다.

현재 구현은 `DisplayPixelWidthUm / DisplayPixelPitchCameraPixelX`, 즉 X 방향 기준으로 단일 µm/px 값을 파생한다.

IP에는 독립 실행을 위한 `CameraPixelSizeUm` 설정 기본값도 존재하지만, Console이 Job을 만드는 정상 경로에서는 `ULedIpConnection.ResolveCameraPixelSizeUm()`이 위 Recipe 실측식으로 계산해 metadata에 전달한다. 따라서 Console 검사에서 임의의 3.3 또는 3.6을 고정값으로 대입하는 흐름이 아니다.

### 핵심 요약

- µm/px는 물리 Pitch를 영상 Pitch로 나눈 값이다.
- 현재 Console 경로는 X 방향 실측 Pitch로 단일 값을 파생한다.
- 현재 장비값은 선택 Recipe와 Find Pitch 결과로 확인해야 하며 예시값으로 확정하면 안 된다.

---

### 4.3 이미지에서 무엇을 뜻하는가

µm/px가 작을수록 같은 물리 길이가 영상에서 더 많은 Pixel을 차지한다.

사용자가 제시한 약 3.3~3.7 µm/px 범위를 단순 환산 예로만 사용하면 다음과 같다.

```text
1 px   ≈ 3.3~3.7 µm
0.5 px ≈ 1.65~1.85 µm
5 px   ≈ 16.5~18.5 µm
10 px  ≈ 33~37 µm
```

이미지에서 두 Dot 중심이 10 px 떨어져 있고 환산값이 3.5 µm/px로 확정됐다면 제품면 중심 간 거리는 약 35 µm로 해석한다.

```text
물리 거리(µm) = 영상 좌표 차이(px) × µm/px
```

FOV도 같은 원리다.

```text
대상면 FOV 폭(µm)
  ≈ 영상 폭(px) × X축 µm/px
```

단, 현재 코드의 단일 값은 X Pitch에서 파생한다. X/Y 배율 차이, 렌즈 왜곡 또는 위치별 scale 변화까지 보정하는 완전한 2D 카메라 calibration 값으로 해석하면 안 된다.

### 핵심 요약

> 이미지에서의 의미는 Pixel 거리와 Glass 물리 거리 사이의 길이 환산이다.

---

### 4.4 장비에서 무엇을 뜻하는가

이 프로젝트에서 확인되는 장비적 사용처는 다음과 같다.

- 영상에서 측정한 위치 오차를 제품면 µm로 해석
- CellMap 보정값을 µm와 px 표시 사이에서 변환
- 물리 Dot Pitch와 영상 Dot Pitch 사이를 변환
- 카메라 조건 변경 뒤 Find Pitch 결과가 달라졌는지 확인

`CellMapCorrectionRowViewModel`은 px 입력값을 다음과 같이 µm 정본으로 바꿔 저장한다.

```text
보정량 µm = 입력 보정량 px × µm/px
```

반대로 µm 정본을 px로 표시할 때는 다음과 같다.

```text
표시 보정량 px = 보정량 µm / µm/px
```

그러나 µm/px 하나만으로 다음 성능이 자동 보장되는 것은 아니다.

- 광학적으로 분리 가능한 최소 결함 크기
- Dot 중심 측정 정확도
- Stage 반복정밀도
- 렌즈 왜곡 보정 정확도
- 포커스와 진동을 포함한 검사 정확도

즉 `3.5 µm/px`는 대상면의 **sampling scale**이지 “3.5 µm 크기의 모든 결함을 반드시 검출한다” 또는 “장비가 3.5 µm 정확도로 움직인다”는 성능 보증값이 아니다. 현재 코드도 µm/px 값에서 광학 MTF, 포커스, 노이즈, Stage 반복정밀도를 계산하지 않는다.

### 핵심 요약

- 장비에서는 카메라 위치 오차와 보정량을 제품면 길이로 번역하는 데 사용한다.
- 광학 해상력이나 Stage 정확도와 같은 뜻은 아니다.

---

### 4.5 카메라 높이와 배율이 바뀌면 왜 다시 측정해야 하는가

카메라 높이, working distance 또는 렌즈 배율이 바뀌면 동일한 물리 Dot Pitch가 영상에서 차지하는 Pixel 수가 달라진다.

```text
카메라·렌즈 조건 변경
→ 영상에서 측정되는 Dot Pitch(px) 변경
→ DisplayPixelWidthUm / 실측 PitchX 결과 변경
→ µm/px 변경
→ 같은 px Offset의 물리 길이 해석 변경
```

현재 Console 코드는 `DisplayPixelWidthUm` 또는 `DisplayPixelPitchCameraPixelX`가 없으면 임의 기본값으로 대체하지 않고 Recipe 업로드를 실패시키며, 현재 버퍼 분석의 Find Pitch를 수행하라는 오류를 발생시킨다.

Threshold와 Level은 밝기 단위이므로 µm/px로 환산하지 않는다.

### 핵심 요약

- 광학 조건이 바뀌면 Find Pitch를 다시 측정해야 한다.
- µm/px는 거리 환산값이고 Threshold와 Gray Level은 밝기값이다.

---

## 5. 표준맵 미사용 DenseMap의 전체 검사 흐름

```text
R/G/B 이미지 준비
        ↓
R 채널에서 Blob 검출 및 DenseMap 확정 시도
        ↓ 실패
G 채널 시도
        ↓ 실패
B 채널 시도
        ↓
첫 성공 채널을 기준 맵으로 확정
        ↓
형제 채널 좌표 = 기준 맵 + RGB Phase Offset
        ↓
모든 유효 Dot 위치에서 원본 Level 측정
        ↓
Normal Level과 밝기 비율 계산
        ↓
A/B/C/D Grade 계산
        ↓
Cross-channel WD 명점 검사
        ↓
Console CellJudgmentAnalyzer
        ↓
암점·암선·명점·명선·군집·미점등·점등불량
        ↓
셀 대표 판정 OK / R/P / R/J
```

### 핵심 요약

DenseMap의 역할은 Defect 이름을 직접 정하는 것이 아니라 각 논리 Dot의 정확한 좌표와 밝기 측정 위치를 만드는 것이다.

---

## 6. DenseMap 좌표 생성 알고리즘

### 6.1 기준 채널 선택

표준맵을 사용하지 않으면 R→G→B 순으로 DenseMap 확정을 시도한다.

```text
R 성공
→ R이 기준 채널
→ G/B는 R 좌표에서 Phase Offset만 이동

R 실패, G 성공
→ G가 기준 채널
→ R/B는 G 좌표에서 상대 Phase Offset만 이동

R/G/B 모두 실패
→ ROI 중심에 Recipe Pitch 격자 배치
→ 모든 채널 Level을 강제로 측정
```

같은 Cell의 R/G/B Grab 사이에는 Stage가 움직이지 않는다는 장비 전제를 이용한 설계다.

> NOTE
>
> R 채널이 DenseMap 확정에 성공했다면 G와 B는 자기 Threshold로 Blob을 다시 검출하지 않는다.  
> G/B는 R 기준 좌표와 Phase Offset으로 Level을 측정한다.

따라서 G Threshold를 30에서 50으로 바꿨더라도 R이 항상 맵을 확정한다면 G 좌표 생성에는 영향이 없을 수 있다. 반대로 R이 실패해 G가 기준 후보가 되는 상황에서는 G Threshold가 맵 성공 여부에 영향을 준다.

### 핵심 요약

- Threshold의 좌표 검출 영향은 실제 기준 채널이 무엇인지와 함께 봐야 한다.
- 정상적으로 R이 기준이면 G/B Threshold는 형제 채널 좌표 검출에는 사용되지 않는다.

---

### 6.2 Object 검출

기준 채널 후보 영상에서 다음 순서로 Object를 검출한다.

```text
ROI
→ White Top-hat 배경 평탄화
→ Threshold 이진화
→ 8방향 Connected Component Labeling
→ Area 필터
→ Width/Height 필터
→ Object 중심 좌표
```

검출된 Object는 실제 Dot 후보다.

### 핵심 요약

Threshold만으로 Dot을 확정하지 않고 Blob의 면적과 가로·세로 크기까지 함께 확인한다.

---

### 6.3 Seed와 Pitch Vector

ROI를 5 × 5 영역으로 나눠 공간적으로 분산된 Seed 후보를 선택한다.

각 후보 주변의 5 × 5 Index 범위에서 Recipe Pitch 위치와 실제 Object가 얼마나 많이 맞는지 채점한다.

가장 많은 이웃이 맞는 후보를 Seed로 선택한다.

Seed 주변 Object의 인접 차분이 충분하면 X/Y Pitch를 단순 스칼라가 아닌 2차원 Vector로 추정한다.

```text
X Pitch Vector = (dxX, dyX)
Y Pitch Vector = (dxY, dyY)
```

이 Vector에는 영상의 미세 회전 성분도 포함된다.

표본이 축별 6개보다 적으면 Recipe Pitch를 사용한다.

```text
X Vector = (Recipe PitchX, 0)
Y Vector = (0, Recipe PitchY)
```

### 핵심 요약

DenseMap은 Recipe Pitch를 시작 기준으로 사용하지만 실제 인접 Object가 충분하면 영상의 회전을 포함한 Pitch Vector로 보정한다.

---

### 6.4 Full DenseMap 확장

Seed에서 다음 순서로 격자를 확장한다.

```text
Seed
→ Seed 행을 좌우로 확장
→ 위·아래 행으로 확장
→ 각 예상 위치에서 가장 가까운 미사용 Object 검색
```

각 칸은 두 종류로 확정된다.

| Source | 의미 |
|---|---|
| Object | 예상 위치 근처에서 실제 Blob을 찾음 |
| Predicted | 실제 Blob은 없지만 이웃과 Pitch로 좌표를 예측함 |

Predicted 좌표가 필요한 이유는 암점이나 미점등 줄처럼 실제 밝은 Blob이 없는 위치에서도 밝기를 측정해야 하기 때문이다.

```text
Blob이 없음
≠ 검사 대상 Dot이 없음

Blob이 없음
→ 논리 Dot Index는 존재
→ 좌표를 예측
→ 그 위치의 Level 측정
```

### 핵심 요약

> DenseMap은 켜진 Dot만 나열하는 맵이 아니라 꺼진 Dot까지 포함한 전체 논리 격자를 복원한다.

---

### 6.5 Object 검증과 Map Shift

Object로 배정된 Dot이 주변 Pitch 관계와 맞지 않으면 오검출 또는 오배정으로 보고 Predicted로 강등한다.

이후 실제 Object가 존재하는 Local Mask와 Recipe의 유효 Dot Map을 Cross-correlation으로 비교한다.

```text
Shift Score
  = 관측 Object Mask와 Recipe 유효 Map이 겹치는 수
```

가장 많이 겹치는 `(dx, dy)`를 선택해 최종 Dot Index를 확정한다.

```text
FinalX = LocalX + ShiftX
FinalY = LocalY + ShiftY
```

### 핵심 요약

- Pitch는 국부 격자를 복원한다.
- Recipe Map Shift는 복원된 격자의 절대 Index를 맞춘다.

---

## 7. DenseMap의 Level과 Grade

### 7.1 Level 측정

Recipe Map에서 유효한 모든 Dot 좌표를 대상으로 원본 Gray 영상을 7 × 7 Gaussian 방식으로 샘플링한다.

1차원 가중치는 다음과 같다.

```text
[1, 6, 15, 20, 15, 6, 1]
```

중앙 Pixel의 영향이 가장 크고 바깥쪽으로 갈수록 영향이 작다.

### 핵심 요약

Threshold Binary 값 0/255를 Level로 사용하는 것이 아니라 원본 영상의 실제 밝기를 다시 측정한다.

---

### 7.2 Normal Level과 Ratio

모든 유효 Dot Level을 정렬하고 Recipe의 `NormalLevelPercentile` 위치 값을 정상 밝기로 사용한다.

기본값은 P90이다.

```text
NormalLevel = P90(모든 유효 Dot Level)
Ratio = DotLevel / NormalLevel × 100
```

예시:

```text
NormalLevel = 120
DotLevel = 48

Ratio = 48 / 120 × 100
      = 40%
```

현재 contract 코드의 기본 Grade 기준:

| Grade | 기본 조건 |
|---|---:|
| A | 50% 이상 |
| B | 30% 이상, 50% 미만 |
| C | 10% 이상, 30% 미만 |
| D | 10% 미만 |

이 값은 코드 기본값이며 실제 검사는 runtime Recipe 값을 사용한다. 예를 들어 검증에 사용한 2026-07-28 `TEST_GLASS` snapshot의 RGB Pattern은 A/B/C 하한이 `80/30/10`이었다. 따라서 검사 결과를 해석할 때는 문서의 기본값이 아니라 해당 run의 `recipe_snapshot.json`을 확인해야 한다.

### 핵심 요약

Dot의 밝기는 고정 Gray값 하나보다 같은 Pattern 안의 정상 발광군과 비교한 상대 비율로 판정하는 것이 기본이다.

---

## 8. DenseMap Defect별 검출과 분류

### 8.1 암점 DARK_POINT

`CellJudgmentAnalyzer`의 일반 입력 계약에서 암점 Mask로 사용하는 것은 다음 Dot이다.

```text
암점 = Missing 또는 Grade D
```

DenseMap에서 실제 Blob이 검출되지 않아도 Predicted 좌표에서 Level을 측정한다. 그 위치가 어두워 Ratio가 C 기준보다 낮으면 D가 된다.

현재 IP의 결과 조립 경로는 샘플링된 모든 `LevelSampleModel.IsMissingPoint`를 `false`로 기록하고 `PixelResultBlock.Flags`도 0으로 둔다. 따라서 현재 Console/uLed.Export의 정상 실행 결과에서는 사실상 Grade D가 암점 Mask를 만든다. `Missing 또는 D` 규칙의 Missing 분기는 missing flag가 들어오는 과거·외부·재생 입력도 처리하기 위한 일반 계약으로 남아 있다.

다음 항목으로 분류된 Dot은 개별 암점에서 제외된다.

1. 암선에 포함된 Dot
2. RGB 군집성암점에 포함된 Dot

남은 D Dot 수가 `DARK_POINT`다.

기본 셀 판정 규칙:

```text
DARK_POINT 4개 이상
→ R/P
```

1~3개이고 다른 상위 Defect가 없으면 기본 규칙상 OK가 될 수 있다.

> NOTE
>
> 기본 Grade-Type 정책에서는 C도 IP Defect 목록에 포함될 수 있다.  
> 하지만 셀 판정기의 DARK_POINT는 현재 D 또는 Missing만 사용한다. C는 휘도불량 통계로는 보일 수 있지만 현재 DARK_POINT 판정 수에는 포함되지 않는다.

### 핵심 요약

현재 정상 실행 경로의 암점은 “Threshold로 Blob을 못 찾은 점”이 아니라 최종 Level이 D 등급인 논리 Dot이다. Blob 미검출은 내부적으로 Predicted 좌표를 만들지만 IP 결과에서는 Missing flag로 내보내지 않는다.

---

### 8.2 암선 DARK_LINE

R/G/B 채널별 암점 좌표를 같은 행과 같은 열로 그룹화한다.

다음 두 조건 중 하나만 만족해도 Line이다.

```text
조건 1: 연속 암점 수 >= MinConsecutiveDefects
조건 2: 행 또는 열 전체 길이 대비 암점 비율 >= MinDefectRatioPercent
```

기본값:

```text
MinConsecutiveDefects = 20
MinDefectRatioPercent = 50%
```

예를 들어 한 행의 길이가 100 Dot이면 다음 두 경우 모두 암선이다.

- 암점 20개가 연속됨
- 암점 50개가 띄엄띄엄 존재함

가로선과 세로선은 별도로 집계한다. 십자 형태는 가로 1개와 세로 1개가 될 수 있다.

기본 판정:

```text
DARK_LINE 1개 이상
→ R/J
```

### 핵심 요약

암선은 밝기 기준으로 만들어진 D Mask의 공간 배열을 다시 분석한 결과다.

---

### 8.3 군집성암점 CLUSTER_DARK_POINT

암선을 먼저 제거한 뒤 남은 암점에서 8방향 Connected Component Labeling을 수행한다.

RGB 군집:

- R/G/B 채널별 검사
- 상하좌우와 대각선으로 연결
- 기본 10 Dot 이상이면 군집 1건

W 군집:

```text
WhiteMask
  = R 암점 Mask
    ∩ G 암점 Mask
    ∩ B 암점 Mask
```

- 동일 논리 Dot의 R/G/B가 모두 D인 “완전 꺼짐” Mask
- 별도 W Pattern 밝기로 만드는 것이 아님
- 기본 5 Dot 이상 연결되면 군집 1건
- R/G/B 중 하나라도 미점등 또는 점등불량이면 W 군집 분석 생략

기본 판정:

```text
CLUSTER_DARK_POINT 1건 이상
→ R/P
```

여기서 Count는 군집 안의 Dot 수가 아니라 Connected Component 군집 개수다.

### 핵심 요약

군집성암점은 개별 D Dot의 수가 아니라 서로 붙어 있는 형태를 분석한 Defect다.

---

### 8.4 명점 BRIGHT_POINT

명점은 현재 Pattern에서 원래 켜지면 안 되는 다른 RGB Phase 위치가 밝게 보이는 현상이다.

예를 들어 R Pattern 영상에서는 G와 B Dot 좌표를 샘플링한다.

```text
R 영상의 G 위치 Level / G NormalLevel × 100
R 영상의 B 위치 Level / B NormalLevel × 100
```

Ratio가 Recipe의 `WhiteDefect.ThresholdPercent` 이상이면 WD 명점 후보가 된다.

기본값:

```text
WhiteDefect.ThresholdPercent = 50%
```

DenseMap 미사용 경로에서는 격자 검증에서 탈락한 Off-grid 밝은 Object도 다음 조건을 만족하면 WD로 회수한다.

- WD Threshold 이상
- 기존 Cross-channel WD와 카메라 거리 3 px 초과
- 같은 위치와 채널의 중복이 아님

이후 명선으로 분류되지 않은 WD가 `BRIGHT_POINT`다.

기본 판정:

```text
BRIGHT_POINT 1개 이상
→ R/J
```

### 핵심 요약

명점은 정상 Dot이 단순히 밝은 것이 아니라 다른 RGB 위상 또는 격자 밖에서 발견된 비정상 발광이다.

---

### 8.5 명선 BRIGHT_LINE

IP가 만든 WD 좌표를 암선과 동일한 행·열 알고리즘으로 분석한다.

```text
연속 WD 20개 이상
또는
행/열 전체 대비 WD 50% 이상
```

기본값은 암선과 동일하다.

명선 주변의 WD가 개별 명점으로 중복 집계되는 것을 줄이기 위해 기본 6 Dot 반경을 흡수한다.

```text
가로 명선 Y ± 6
세로 명선 X ± 6
→ 개별 BRIGHT_POINT에서 제외
```

이 값은 명선 검출 기준이 아니라 Report 정리 기준이다.

기본 판정:

```text
BRIGHT_LINE 1개 이상
→ R/J
```

### 핵심 요약

명선은 WD 명점 Mask가 행 또는 열 방향으로 선 형태를 이루는 경우다.

---

### 8.6 미점등 MISSING_LIGHTING

미점등은 Dot 하나가 아니라 R, G, B Pattern 하나의 전체 상태다.

먼저 유효 Dot 비율을 계산한다.

```text
ValidPercent
  = (전체 Dot 수 - D/Missing Dot 수)
    / 전체 Dot 수
    × 100
```

기본 기준:

```text
ValidPercent < 10%
→ MISSING_LIGHTING
```

미점등으로 분류된 Pattern은 수만 개 암점으로 보고하지 않고 해당 Pattern의 개별 암점, 암선, 군집 및 명점 분석을 건너뛴다.

기본 판정:

```text
MISSING_LIGHTING 채널 1개 이상
→ R/J
```

### 핵심 요약

미점등은 거의 모든 Dot이 D인 채널 전체 문제를 하나의 원인성 Defect로 요약한 것이다.

---

### 8.7 점등불량 LIGHTING_FAIL

미점등은 아니지만 채널 전체 발광 상태가 불안정하거나 지나치게 낮을 때 점등불량으로 분류한다.

미점등 검사를 통과한 뒤 다음 세 조건 중 하나라도 만족하면 된다.

```text
평균 Dot Level < 100
또는
ValidPercent < 50%
또는
명선 개수 >= 10
```

기본 유효율 구간:

| ValidPercent | 기본 분류 |
|---:|---|
| 10% 미만 | 미점등 |
| 10% 이상, 50% 미만 | 점등불량 |
| 50% 이상 | 평균 Level과 명선 개수 추가 확인 |

여기서 평균 Level 100은 Ratio 100%가 아니라 모든 Dot의 원본 측정 Level 평균과 같은 단위의 값이다.

`MinWhiteLineCount=10`도 WD Dot 10개가 아니라 검출된 가로·세로 명선의 합이 10개 이상이라는 뜻이다.

점등불량 Pattern은 개별 Defect 분석을 대부분 건너뛴다. 다만 원인 확인을 위해 이미 검출한 명선 개수와 상세 정보는 유지한다.

기본 판정:

```text
LIGHTING_FAIL 채널 1개 이상
→ R/J
```

### 핵심 요약

점등불량은 일부 Dot 불량보다 채널 전체 평균, 유효율 또는 명선 다발이 점등 계통 문제에 가깝다고 판단한 상태다.

---

## 9. Defect 분류 순서가 중요한 이유

현재 분석 순서는 다음과 같다.

```text
1. 미점등
2. 점등불량
3. 암선·명선
4. 암점 군집
5. 남은 개별 암점·명점
6. 셀 대표 판정
```

예를 들어 R Pattern의 95%가 D라면 다음처럼 처리하지 않는다.

```text
암점 95,000개
암선 수천 개
군집 수백 개
```

대신 다음처럼 처리한다.

```text
R Pattern MISSING_LIGHTING 1건
개별 분석 Skip
```

이는 결과 크기를 줄이기 위한 목적뿐 아니라 실제 원인을 더 가깝게 표현하기 위한 장비 판정 구조다.

### 핵심 요약

상위 원인성 상태를 먼저 판정하고 그 상태로 설명할 수 있는 하위 점·선 Defect는 중복 집계하지 않는다.

---

## 10. 최종 셀 판정 우선순위

기본 규칙은 다음 순서다.

| 우선순위 | Defect | 최소 개수 | 셀 판정 |
|---:|---|---:|---|
| 1 | MISSING_LIGHTING | 1 | R/J |
| 2 | LIGHTING_FAIL | 1 | R/J |
| 3 | BRIGHT_LINE | 1 | R/J |
| 4 | DARK_LINE | 1 | R/J |
| 5 | BRIGHT_POINT | 1 | R/J |
| 6 | CLUSTER_DARK_POINT | 1 | R/P |
| 7 | DARK_POINT | 4 | R/P |
| - | 어떤 규칙도 만족하지 않음 | - | OK |

목록 위에서부터 처음 만족한 규칙이 셀 대표 Type과 판정이 된다.

운영 장비에서는 `<WorkDir>/Config/cell-judgment.yaml` 값이 우선한다. 표의 값은 현재 코드의 기본값이다.

### 핵심 요약

여러 Defect가 동시에 존재할 수 있지만 셀 대표 판정은 우선순위가 가장 높은 첫 규칙으로 결정된다.

---

## 11. Threshold 30과 50을 비교할 때 확인할 값

같은 이미지에서 Threshold만 변경해 다음 항목을 비교해야 한다.

| 확인 항목 | 의미 |
|---|---|
| 선택 Threshold | Multi-threshold에서 실제 채택된 값 |
| Objects | 형상 필터를 통과한 Blob 수 |
| Oversized Penalty | 병합 Blob이 덮은 것으로 추정되는 Dot 수 |
| Used Objects | DenseMap에 실제 Anchor로 사용한 수 |
| Rejected Objects | Pitch 일관성 검증에서 탈락한 수 |
| Predicted | Blob 없이 예측 좌표를 사용한 Dot 수 |
| Shift Hit | Recipe Map과 겹친 Object 수 |
| Reference Channel | R/G/B 중 실제 맵을 확정한 채널 |
| Normal Level | 밝기 비율의 기준 |
| A/B/C/D Count | 최종 밝기 분포 |
| WD Count | Cross-channel 및 Off-grid 명점 수 |
| Pattern State | OK, MISSING_LIGHTING, LIGHTING_FAIL |
| Cell Judge | OK, R/P, R/J |

권장 비교 순서:

```text
동일 Cell
동일 R/G/B 원본 이미지
동일 ROI
동일 Pitch
동일 Blob Area/Width/Height
동일 Grade 기준
Threshold만 30 ↔ 50 변경
```

원본 이미지까지 달라지면 Exposure, PG 출력, 포커스, 진동의 영향이 섞이므로 Threshold 영향만 비교할 수 없다.

### 핵심 요약

> Threshold 비교는 최종 불량 개수만 보지 말고 Object → DenseMap → Level → Defect의 각 단계 통계를 함께 봐야 한다.

---

## 12. 장비 개발자가 코드에서 확인해야 할 기준

Threshold를 조정할 때 목표는 다음 두 실패를 동시에 최소화하는 것이다.

```text
False Negative
정상 또는 약한 Dot을 Object로 못 찾음

False Positive
배경·반사·노이즈를 Dot Object로 잘못 찾음
```

Threshold를 높이면 보통 정밀도는 올라가고 검출률은 내려간다.

```text
높은 Threshold
→ 검출된 것의 신뢰도는 높아지는 경향
→ 실제 약한 Dot 누락 증가
```

Threshold를 낮추면 보통 검출률은 올라가고 정밀도는 내려간다.

```text
낮은 Threshold
→ 약한 Dot까지 찾음
→ 배경·병합·가짜 Object 증가
```

현재 코드에는 Threshold 검출 실패가 곧바로 Level 미측정이 되지 않도록 다음 구조가 구현돼 있다.

- Predicted 좌표로 꺼진 Dot 위치 유지
- R/G/B 첫 성공 채널의 맵 공유
- 세 채널 실패 시 ROI 중심 기준 Level 측정
- Level과 Grade를 Binary 검출과 분리
- Dot 배열을 Console 공용 판정기에서 다시 원인별로 분류

즉 Threshold는 제품 합격·불합격 값을 직접 정하는 값이 아니라 정확한 측정 좌표를 안정적으로 확보하기 위한 영상 처리 파라미터다.

이 목록은 제작자의 의도를 추정한 것이 아니라 현재 코드에서 직접 확인되는 동작이다.

### 핵심 요약

> 장비 개발자는 Threshold를 “불량을 더 많이 잡는 값”이 아니라 “좌표 맵을 가장 안정적으로 만드는 값”으로 조정해야 한다.

---

## 13. 코드 확인 순서

1. **uLedInspection.Algorithms/CorrectedDenseMapInspector.cs**
   - Top-hat, Threshold, Blob, Seed, DenseMap, Predicted, Shift, Level, Grade
2. **uLedIp/Inspection/PointGridInspectionAlgorithm.cs**
   - R→G→B 기준 채널 선택, 형제 채널 맵 공유, Cross-channel WD
3. **uLedInspection.Algorithms/FindPitchEstimator.cs**
   - 영상에서 Dot Pitch를 px 단위로 측정하는 과정
4. **uLedAoiConsole/Services/Ip/ULedIpConnection.cs**
   - `DisplayPixelWidthUm / DisplayPixelPitchCameraPixelX`의 µm/px 파생
5. **uLedIp/Inspection/InspectionImageConverter.cs**
   - 입력 영상이 3채널일 때 `max(B,G,R)` Gray를 만드는 현재 검사 Source
6. **uLedIp/Services/FinalPanelResultBuilder.cs**
   - Level을 Pixel block으로 조립하고 missing flags를 기록하는 경로
7. **uLed.Export/Services/CustomerExportService.cs**
   - Pixel block과 WD를 `ChannelAnalysisInput`으로 바꾸는 경로
8. **uLed.Contracts/Judgment/CellJudgmentAnalyzer.cs**
   - 미점등, 점등불량, 선, 군집, 개별 점 분류
9. **uLed.Contracts/Models/CellJudgmentModels.cs**
   - 분석 기준과 최종 판정 기본값

### 핵심 요약

Threshold부터 추적하려면 `CorrectedDenseMapInspector`를 먼저 보고, 중간 결과가 최종 판정 입력으로 바뀌는 과정까지 확인하려면 `FinalPanelResultBuilder → CustomerExportService → CellJudgmentAnalyzer` 순서로 봐야 한다.

---

## 14. 전체 문서 2회 검증 결과

### 14.1 검증 1: Docs에서 시작해 코드 생산 경로를 순방향 대조

확인 순서는 다음과 같다.

1. `docs/dense-local-template-grid-indexer.md`
2. `docs/rgb-level-inspection-algorithm.md`
3. 과거 기술 매뉴얼 `표준맵사용검사-technical-manual.md`의 맵생성검사 절
4. `CorrectedDenseMapInspector`
5. `PointGridInspectionAlgorithm`
6. `InspectionImageConverter`
7. `ULedIpConnection.ResolveCameraPixelSizeUm`

확인 결과는 다음과 같다.

| 검증 항목 | 현재 코드에서 확인된 사실 |
|---|---|
| Threshold 식 | DetectionSource 값이 Threshold보다 클 때만 255 |
| 배경 평탄화 | `Gray - Opening(Gray)` White Top-hat 후 Threshold |
| Multi-threshold | `유효 Object 수 - OversizedArea/(PitchX×PitchY)` 최대 점수, 동점은 높은 Threshold |
| DenseMap 기준 채널 | 표준맵 미사용 시 R→G→B 첫 성공 채널 하나만 맵 확정 |
| 형제 채널 | 기준 맵에 RGB phase offset을 더해 Level 측정, 재검출하지 않음 |
| Level | 원본 검사 Gray의 Gaussian 7×7 |
| Grade | Recipe A/B/C 하한 사용 |
| µm/px | `DisplayPixelWidthUm / DisplayPixelPitchCameraPixelX` |

#### Docs 불일치 확인

현재 `docs/dense-local-template-grid-indexer.md`에는 다음 과거 설명이 남아 있다.

- R/G/B가 각각 독립적으로 Grid를 복원한다.
- R Pattern은 R channel, G Pattern은 G channel, B Pattern은 B channel을 Gray Source로 쓴다.
- Seed는 ROI 중심에 가장 가까운 Object 하나로 선택한다.

현재 실행 코드는 다음과 다르다.

- 표준맵 미사용 본검사는 R→G→B 첫 성공 맵 하나를 공유한다.
- `InspectionImageConverter.ToInspectionGray(image, patternType)`은 pattern type을 사용하지 않고 3채널 입력이면 `max(B,G,R)`을 반환한다.
- Seed 후보는 ROI 5×5 타일에서 공간적으로 뽑고 5×5 index consensus를 채점해 선택한다.

또한 `docs/rgb-level-inspection-algorithm.md`의 `A>=90, B>=50, C>=30, D>=20` 설명은 현재 `GradeSpecModel` 계약과 맞지 않는다. 현재 contract 기본은 `A>=50, B>=30, C>=10, D<10`이며 실제 실행은 runtime Recipe 값을 사용한다.

따라서 이 문서에서는 위 두 Docs의 충돌 구간을 현재 코드 기준으로 수정해 설명했다. 과거 기술 매뉴얼의 `InspectDenseWithConfirmedMap` 설명은 현재 코드와 일치했다.

### 14.2 검증 2: 결과 소비 경로를 역방향 추적하고 실제 설정·로그와 대조

확인 순서는 다음과 같다.

1. `CellJudgmentAnalyzer`의 최종 유형별 Count
2. `CustomerExportService`의 DarkDots/WhiteDefects 입력 생성
3. `FinalPanelResultBuilder`의 Pixel block 생성
4. `PointGridInspectionAlgorithm`의 Level 및 confirmed map 생성
5. 실제 `C:/elp/uLedAoi/Config/cell-judgment.yaml`
6. 실제 `recipe_snapshot.json`
7. 2026-07-28 IP 운영 로그

확인 결과:

- 운영 `cell-judgment.yaml`은 이 문서에 적은 미점등 10%, 점등불량 평균 100/유효율 50%/명선 10개, Line 20개 또는 50%, RGB 군집 10개, W 군집 5개, 흡수 반경 6과 일치했다.
- 최종 셀 판정 우선순위도 운영 YAML과 코드 기본값이 일치했다.
- `CustomerExportService`는 `Missing 또는 Grade D`를 DarkDots로 만들지만, 현재 IP의 Pixel block missing flags는 모두 0이므로 현재 정상 실행에서는 Grade D가 실제 암점 Mask가 된다.
- 실제 snapshot에서 `BackgroundFlattenEnabled=true`와 Recipe별 Threshold/Grade가 확인됐다.
- 해당 snapshot의 `78 µm / 20.825015 px = 3.745496 µm/px`는 코드식을 검증하는 한 run의 사례일 뿐 장비 고정값은 아니다.

동일 R 영상에서 Multi-threshold를 동시에 시험한 실제 로그는 다음과 같다.

```text
Threshold=[30:140514(-0),50:140459(-0),80:140365(-0)->30]
Objects=140514
Used=140511
Rejected=3
Dense=146604
Missing=6093
```

같은 로그의 G/B 결과는 다음과 같다.

```text
G Threshold=[confirmed_map:R] / Objects=0
B Threshold=[confirmed_map:R] / Objects=0
```

이 로그로 다음 내용을 재확인했다.

1. 이 영상에서는 Threshold가 30→50→80으로 올라갈수록 형상 필터 통과 Object가 소폭 감소했다.
2. 이것은 해당 영상의 실측 결과이며 모든 영상에서 감소량이 같다는 의미가 아니다.
3. R이 맵을 확정한 후 G/B는 자기 Threshold로 Object를 다시 검출하지 않았다.
4. 내부 `Missing=6093`은 R DenseMap의 Predicted 수이며, 최종 Pixel block missing flag와는 다른 진단값이다.

### 14.3 근거 파일

| 구분 | 파일 |
|---|---|
| 맵생성 Docs | `docs/dense-local-template-grid-indexer.md` |
| Level Docs | `docs/rgb-level-inspection-algorithm.md` |
| 현재 흐름과 일치하는 과거 기술 절 | `D:/ELP/Project/01.SDC/A1/uLED/Source/uLED_Develop_원본/docs/표준맵사용검사-technical-manual.md` |
| Threshold·DenseMap | `uLedInspection.Algorithms/CorrectedDenseMapInspector.cs` |
| 기준 채널·phase·WD | `uLedIp/Inspection/PointGridInspectionAlgorithm.cs` |
| Gray 변환 | `uLedIp/Inspection/InspectionImageConverter.cs` |
| µm/px 파생 | `uLedAoiConsole/Services/Ip/ULedIpConnection.cs` |
| Pixel block | `uLedIp/Services/FinalPanelResultBuilder.cs` |
| 판정 입력 | `uLed.Export/Services/CustomerExportService.cs` |
| Defect 분류 | `uLed.Contracts/Judgment/CellJudgmentAnalyzer.cs` |
| 운영 판정값 | `C:/elp/uLedAoi/Config/cell-judgment.yaml` |
| 검증 Recipe | `C:/elp/uLedAoi/Data/InspectionResults/Glass/LOT_260728/TEST_GLASS_20260728_105233/runtime/recipe_snapshot.json` |
| 운영 로그 | `C:/elp/uLed/uLedIp/logs/202607/app_20260728.log` |

---

## 15. 최종 정리

```text
Threshold
→ Dot 좌표를 찾기 위한 영상 검출 민감도

µm/px
→ 영상 Pixel을 Glass 실제 길이로 바꾸는 공간 환산비

DenseMap
→ 실제 Object와 Pitch로 꺼진 Dot까지 포함한 전체 논리 좌표 생성

Level/Grade
→ 좌표에서 원본 밝기를 측정해 A/B/C/D 분류

Cell Judgment
→ D와 WD의 공간 배열을 분석해 점·선·군집·채널 상태로 분류
```

Threshold를 30에서 50으로 올리면 DetectionSource 값 31~50인 Pixel이 전경에서 제거되고, 50에서 30으로 내리면 그 Pixel이 전경에 추가된다. 전경 면적의 방향은 확정적이지만 CCL 성분은 분리·병합될 수 있으므로 형상 필터를 통과한 최종 Object 수는 단조롭게 변하지 않는다. 어느 쪽이 더 좋은지는 Object 수만으로 결정하지 않고 DenseMap Anchor, Predicted, Shift Hit, Grade, WD 및 최종 Pattern 상태까지 동일 이미지에서 비교해야 한다.

1 Pixel당 몇 µm라는 값은 고정 암기값이 아니라 현재 제품 Dot Pitch와 영상에서 측정한 Pitch로 파생하는 대상면 공간 환산값이다. 사용자가 예로 든 약 3.3~3.7 µm/px는 가능한 범위의 예시일 뿐 현재 장비의 확정값이 아니다.

DenseMap Defect는 Threshold 값 하나에서 바로 결정되지 않는다. Threshold로 좌표 맵을 만들고, 그 좌표에서 측정한 원본 Level을 Grade로 변환한 뒤, Console 공용 판정기가 암점·암선·명점·명선·군집·미점등·점등불량으로 재분류한다. 단, Threshold로 인해 기준 맵 좌표가 달라지면 같은 원본 영상에서도 샘플 Level과 최종 Defect가 간접적으로 달라질 수 있다.

### 핵심 요약

> 좌표 검출, 밝기 판정, 공간적 Defect 분류를 세 단계로 나누어 이해하면 Threshold와 최종 판정의 관계를 정확히 해석할 수 있다.
