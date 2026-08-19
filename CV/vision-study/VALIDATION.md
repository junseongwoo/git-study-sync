# 문서·수식·C++ 검증 기록

> 목적: 학습 자료를 생성한 뒤 내용과 코드를 한 번 더 검토하여, 잘못된 지식이나 실행 불가능한 예제가 누적되는 것을 방지한다.

## 모든 Chapter에 적용할 검증 절차

### 1. 요구사항 검증

- [ ] 고정 출력 형식 12개 항목을 모두 포함했는가?
- [ ] 개념 → 필요성 → 장비 적용 → 이미지에서의 모습 → 관련 개념 → C++ 구현 → 실무 문제 순서가 드러나는가?
- [ ] 숫자 예제가 최소 2개인가?
- [ ] 실무 문제 최소 3개, 면접 질문 최소 5개, 실습 문제 최소 3개인가?
- [ ] 각 면접 질문에 초보자/실무자/30초 답변이 있는가?
- [ ] 우선순위, 난이도, 예상 학습 시간을 표시했는가?
- [ ] Phase 미니 프로젝트가 있는가?

### 2. 기술 내용 검증

- [ ] 동일하거나 비슷한 용어를 명확히 구분했는가?
- [ ] 수식의 전제 조건과 적용 범위를 썼는가?
- [ ] 모든 계산에서 pixel, μm, mm, degree 단위가 일관적인가?
- [ ] 이상적 계산과 실제 검출 성능을 혼동하지 않았는가?
- [ ] Camera → Lens → Image → Align → Calibration → Inspection 연결이 맞는가?
- [ ] 좌표 원점, 축 방향, 회전 부호, 단위를 명시했는가?
- [ ] NG, 검사 불능, 시스템 Error를 구분했는가?

### 3. C++/OpenCV 검증

- [ ] 사용한 표준 함수에 필요한 표준 헤더가 모두 있는가?
- [ ] OpenCV 함수의 입력 채널, Depth, 좌표 및 반환 의미가 맞는가?
- [ ] 입력 Image와 ROI의 유효성을 검사하는가?
- [ ] RAII, `const` correctness, `enum class`, STL을 적절히 사용했는가?
- [ ] Camera/SDK Buffer의 소유권과 수명을 오해하게 만들지 않는가?
- [ ] Measurement 단위를 명시했는가?
- [ ] 제품 NG와 예외/시스템 Error를 분리했는가?
- [ ] 최소한의 정상·경계·오류 테스트를 제시했는가?
- [ ] 가능한 환경에서는 실제 Build 또는 Syntax Check를 수행했는가?

### 4. Markdown/Obsidian 검증

- [ ] UTF-8로 정상 저장되었는가?
- [ ] 코드 Fence의 시작과 끝이 맞는가?
- [ ] 내부 링크 대상 파일이 실제로 존재하는가?
- [ ] 표, Callout, ASCII Diagram이 깨지지 않는가?
- [ ] 파일명과 Chapter 번호가 Roadmap과 일치하는가?

## 현재 파일 검증 결과

검증일: 2026-08-18

| 파일 | 구조 | 내용·계산 | 코드 | 링크·형식 | 결과 |
|---|:---:|:---:|:---:|:---:|:---:|
| `README.md` | 통과 | 통과 | 해당 없음 | 통과 | 통과 |
| `00-roadmap.md` | 통과 | 통과 | 해당 없음 | 통과 | 통과 |
| `01-equipment-vision-overview.md` | 통과 | 통과 | 정적 검토 통과 | 통과 | 통과 |
| `02-image-basic.md` | 통과 | 통과 | 정적 검토 통과 | 통과 | 통과 |
| `03-camera-pixel.md` | 통과 | 통과 | 정적 검토 통과 | 통과 | 통과 |
| `04-lens-optics.md` | 통과 | 통과 | 정적 검토 통과 | 통과 | 통과 |
| `05-fov-resolution.md` | 통과 | 통과 | 정적 검토 통과 | 통과 | 통과 |

## Chapter 1 상세 검토 기록

- 고정 형식 12개 항목을 모두 확인했다.
- 숫자 예제는 Cycle Time, Frame 용량/대역폭, 좌표 변환의 3개다.
- `2048 × 2048 × 1 byte = 4,194,304 byte = 4 MiB` 계산을 확인했다.
- 20 fps에서 `80 MiB/s`, Camera 4대에서 `320 MiB/s` 계산을 확인했다.
- Image +y가 아래쪽이고 Machine +Y가 위쪽인 예제의 Y 부호 반전을 확인했다.
- 면접 질문 6개에 초보자/실무자/30초 답변이 모두 포함되어 있다.
- C++ 예제에 `std::max`용 `<algorithm>`을 명시했다.
- `cv::Mat`, `cv::Rect`, `cv::threshold`, `cv::findContours`, `cv::contourArea`, `cv::rectangle`의 사용 맥락을 정적 검토했다.
- ROI가 Image 내부에 완전히 포함되는지 검사하고, 빈 Image와 잘못된 Recipe를 Error로 분리했다.
- 모든 Markdown 파일이 유효한 UTF-8이며 코드 Fence 수가 짝수임을 확인했다.
- 현재 환경의 OpenCV C++ 개발 도구 설치 여부와 무관하게 읽을 수 있도록 코드는 문서 내부 예제로 유지했다. 실제 Build 검증은 프로젝트 파일을 생성하는 Phase에서 CMake 구성과 함께 수행한다.

## Chapter 2 상세 검토 기록

- 검증일: 2026-08-18
- 고정 형식 12개 항목을 모두 확인했다.
- Camera Resolution, Image Resolution, Pixel Size, Spatial Resolution, Optical Resolution의 정의·단위·결정 요인을 비교했다.
- `2048 × 2048 × 1 byte = 4,194,304 byte = 4 MiB`를 재계산했다.
- `4096 × 3000` 12-bit Image가 16-bit Container일 때 `24,576,000 byte ≈ 23.44 MiB`임을 재계산했다.
- 동일 Image의 이상적 12-bit Packed 크기가 `18,432,000 byte ≈ 17.58 MiB`임을 재계산했다.
- `10 mm / 2000 pixel = 5 μm/pixel`, `240 pixel = 1.2 mm` 계산과 단위 변환을 확인했다.
- 12-bit 값 `3072`의 전체 범위 8-bit Mapping이 약 `191`임을 확인했다.
- C++ 표준 헤더, `cv::Mat` Type/Depth/Channel, `elemSize`, `step`, 통계 및 12→8-bit 변환 코드를 정적 검토했다.
- 면접 질문 6개에 초보자/실무자/30초 답변이 모두 포함되어 있다.
- 내부 Obsidian 링크 대상, UTF-8, 34개 Code Fence의 짝을 자동 확인했다.
- 현재 시스템에서 C++ Compiler, CMake 및 OpenCV C++ Header를 찾지 못해 실제 Build는 환경 미검증이다. 독립 프로젝트를 시작할 때 Toolchain과 OpenCV를 구성한 뒤 Build/Test를 추가 수행한다.

## Chapter 3 상세 검토 기록

- 검증일: 2026-08-19
- 고정 형식 12개 항목과 면접 질문 6개의 3단계 답변을 모두 확인했다.
- `2048 pixel × 3 μm/pixel = 6144 μm = 6.144 mm` Sensor Size를 재계산했다.
- 0.5×/1×/2×의 FOV가 각각 `12.288/6.144/3.072 mm`임을 재계산했다.
- 같은 배율에서 Object Space Sampling이 각각 `6/3/1.5 μm/pixel`이며 `FOV/N` 결과와 일치함을 확인했다.
- 실측 FOV 12.20 mm에서 `5.95703125 μm/pixel`, 유효 배율 약 `0.5036066×`임을 재계산했다.
- 10 mm FOV와 2048 Pixel에서 `4.8828125 μm/pixel`, 4 Pixel 특징이 `19.53125 μm`임을 확인했다.
- 이상적 배율 계산과 실제 검출 성능을 구분하고 MTF, Focus, Illumination, Noise 및 Motion Blur 조건을 포함했는지 확인했다.
- C++ 입력의 0/음수/NaN 검증, μm/mm 변환, `p/M`과 `FOV/N` 교차 검산 Test를 정적 검토했다.
- 범위 반복이 간접 헤더 포함에 의존하지 않도록 `<initializer_list>`를 명시했다.
- 내부 Obsidian 링크, UTF-8 및 50개 Code Fence의 짝을 자동 확인했다.
- 현재 시스템에 C++ Build Toolchain이 없어 실제 Compile/Run은 환경 미검증이며, 프로젝트 단계에서 CMake 기반으로 추가 검증한다.

## Chapter 4 상세 검토 기록

- 검증일: 2026-08-19
- 고정 형식 12개 항목과 면접 질문 6개의 3단계 답변을 모두 확인했다.
- `2448×2048`, 3.45 μm Sensor의 크기가 `8.4456×7.0656 mm`임을 재계산했다.
- 0.5× Lens의 FOV가 `16.8912×14.1312 mm`, Sampling이 `6.9 μm/pixel`임을 확인했다.
- Sensor 대각선이 약 `11.0114 mm`여서 문서의 `≈11.01 mm`와 일치함을 확인했다.
- Thin Lens 예제의 `u=550 mm`, `v=55 mm`, `1/u+1/v=1/50`을 독립적으로 검산했다.
- Macro DOF 근사 예제의 0.5×/1× 결과가 각각 `0.96/0.32 mm`임을 재계산했다.
- Working Distance와 주평면 기준 Object Distance를 동일시하지 않도록 경고가 있는지 확인했다.
- DOF 식을 제조사 Datasheet와 실제 Target 검증을 대체하지 않는 비교용 근사식으로 제한했는지 확인했다.
- C++의 단위 표현, 유효 입력 검사, Sensor/FOV/Diagonal 및 교육용 Thin Lens/DOF 함수 분리를 정적 검토했다.
- 내부 Obsidian 링크, UTF-8 및 52개 Code Fence의 짝을 자동 확인했다.
- 실제 Compile/Run은 C++ Build Toolchain 미설치로 환경 미검증이다.

## Chapter 5 상세 검토 기록

- 검증일: 2026-08-19
- 고정 형식 12개 항목과 면접 질문 6개의 3단계 답변을 모두 확인했다.
- 2048 Pixel, 3 μm Sensor에서 0.25×/0.5×/1×/2× FOV가 `24.576/12.288/6.144/3.072 mm`임을 재계산했다.
- 같은 조건의 Object Sampling이 `12/6/3/1.5 μm/pixel`임을 확인했다.
- 10 mm FOV와 2048 Pixel에서 `4.8828125 μm/pixel`, 20 μm Feature가 `4.096 Pixel`임을 확인했다.
- 18 mm FOV, 30 μm Feature, 최소 5 Pixel 조건에서 최소 가로 Pixel Count가 3000임을 재계산했다.
- `10×6 mm` Rectangle의 5° 회전 Bounding Box가 약 `10.4849×6.8487 mm`임을 독립적으로 계산했다.
- 설계 6.00 μm/pixel과 실측 6.08 μm/pixel의 상대 차이가 약 `1.3333%`임을 확인했다.
- C++ 평가기가 FOV와 Sampling 합격을 분리하고 최소 Pixel Count를 올림하는지 정적 검토했다.
- 내부 Obsidian 링크, UTF-8 및 60개 Code Fence의 짝을 자동 확인했다.
- 실제 Compile/Run은 C++ Build Toolchain 미설치로 환경 미검증이다.

## 검증 결과 표기 규칙

- **통과**: 요구사항 및 정적 검토에서 문제를 발견하지 못함
- **수정 후 통과**: 검토 중 문제를 찾아 수정하고 재확인함
- **환경 미검증**: 외부 SDK, Camera, Lens 또는 Build 환경이 없어 실제 실행을 확인하지 못함
- **보류**: 다음 Chapter의 선수 지식이 필요하여 의도적으로 검증을 미룸

> [!IMPORTANT]
> 정적 검토 통과는 특정 Camera SDK나 장비에서의 동작을 보증한다는 뜻이 아니다. 하드웨어 의존 코드는 실제 SDK Version, Camera 설정, Trigger/Buffer 정책 및 장비 좌표계로 통합 테스트해야 한다.
