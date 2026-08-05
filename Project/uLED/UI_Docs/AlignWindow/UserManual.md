# AlignWindow 사용자 매뉴얼

## 화면 용도

AlignWindow는 좌·우 Align 카메라의 영상을 확인하고 기준 이미지를 등록하며, 현재 위치의 Align 오차를 평가하거나 실제 UVW 보정을 실행하는 화면입니다.

`실제 Align 실행`, `Camera 설정`, `UVW Jog`, `Align 위치 이동`은 실제 장비 축을 움직일 수 있습니다. 장비 안전 상태와 Control 연결을 확인한 뒤 사용하십시오.

## 상단 버튼

| 버튼 | 사용 목적 | 사용 결과 |
|---|---|---|
| Align 위치 이동 | 좌·우 Align mark 촬영 기준 위치로 이동 | Recipe의 AlignReferencePose 위치로 장비가 이동합니다. |
| 현재 이미지 평가 | 화면에 이미 있는 두 영상을 평가 | 새 촬영이나 축 이동 없이 X/Y/Theta 오차를 계산합니다. |
| 촬영 후 평가 | 현재 장비 상태를 새로 촬영해 평가 | Live를 정지하고 양쪽을 단발 촬영한 뒤 오차를 계산합니다. |
| Align Image 등록 | 현재 좌·우 영상을 기준 template으로 등록 | Recipe 폴더에 `align_left.png`, `align_right.png`로 저장합니다. |
| 실제 Align 실행 | 장비의 Align 오차를 실제로 보정 | Theta 보정 후 XY 보정을 반복하고 결과를 기록합니다. |
| Camera 설정 | 카메라 pixel 크기와 영상 방향 교정 | UVW stage를 ±X/±Y/±Theta로 움직여 Config를 계산·저장합니다. |
| UVW Jog | UVW 보정 이동을 수동 시험 | 별도 Jog 창이 열립니다. |
| Axis → Glass | 좌표 변환 확인 | 별도 Axis/Glass 좌표 확인 창이 열립니다. |

## 카메라 툴바

왼쪽과 오른쪽 카메라에 동일한 도구가 있습니다.

| 아이콘 ToolTip | 사용 방법 |
|---|---|
| Connect | Camera Name에 입력한 카메라를 연결합니다. |
| Disconnect | 해당 카메라 연결을 종료합니다. |
| Grab One | 한 장을 촬영합니다. |
| Start Live | 연속 영상을 시작합니다. |
| Stop Live | 연속 영상을 중지합니다. |
| Load Image | 파일의 이미지를 현재 영상으로 불러옵니다. |
| Save Image | 현재 영상을 사용자가 지정한 파일로 저장합니다. |
| Load Align Image | 현재 Recipe의 등록된 Align template을 불러옵니다. |
| Test Match | 현재 영상이 template과 얼마나 일치하는지 시험합니다. |
| Select Search Area | 검색 영역 사각형을 선택해 위치와 크기를 조절합니다. |

## Overlay 색상

| 색상 | 의미 |
|---|---|
| 주황색 사각형 | Template으로 사용할 특징 영역 |
| 하늘색 점선 사각형 | Template을 찾을 검색 범위 |
| Cyan 중심선 | 전체 이미지 중심 |
| 연두색 사각형·십자선 | 최근 template match 위치와 중심 |

Template은 mark의 특징이 분명하고 반복 촬영에서 형태가 유지되는 영역으로 잡습니다. Search 영역은 Template보다 넓고 예상되는 mark 이동 범위를 포함해야 합니다.

## 기준 이미지 등록 절차

1. Recipe를 먼저 저장합니다.
2. Align 위치로 이동합니다.
3. 양쪽 카메라를 연결합니다.
4. Live 영상으로 좌·우 mark가 정상인지 확인합니다.
5. Live를 중지하거나 `Align Image 등록`이 자동으로 중지하도록 합니다.
6. 좌·우 영상이 동일한 정상 Align 상태인지 확인합니다.
7. `Align Image 등록`을 누르고 저장 파일명을 확인합니다.
8. `촬영 후 평가`로 두 카메라의 match가 모두 PASS인지 확인합니다.
9. Recipe를 저장해 Template/Search rectangle 변경도 보존합니다.

## 실제 Align 실행 절차

1. Glass Size의 Align mark와 Recipe Align tolerance가 올바른지 확인합니다.
2. Config의 카메라 geometry가 검증됐는지 확인합니다.
3. 좌·우 template match가 모두 PASS인지 확인합니다.
4. 장비 주변 안전과 UVW 이동 가능 상태를 확인합니다.
5. `실제 Align 실행`을 누릅니다.
6. 확인창의 MaxIteration 및 X/Y/Theta tolerance를 확인합니다.
7. 하단 결과에서 반복 횟수, 잔여 오차, 누적 UVW를 확인합니다.

MaxIteration 안에 tolerance를 만족하지 못하면 실패합니다. tolerance를 임의로 크게 바꾸기 전에 template, search 영역, 카메라 초점, geometry 및 mark 상태를 먼저 확인하십시오.

## Camera 설정 사용 주의

Camera 설정은 단순 카메라 화면 설정이 아닙니다. UVW stage가 다음 범위로 실제 이동합니다.

- X: +1000 um / -1000 um
- Y: +1000 um / -1000 um
- Theta: +0.1° / -0.1°

장비 셋업 담당자만 사용해야 하며, 이동 공간과 glass/헤드 간섭 여부를 먼저 확인하십시오. 촬영 후 계산값을 확인하고 승인해야 Config에 저장됩니다.

## Y1/Y2 명칭 주의

공식 좌표 문서의 Left/Right Align 명칭과 이 창의 화면 좌/우 pane 명칭은 서로 다르게 매핑되어 있습니다.

- 현재 화면 왼쪽 pane: Y2 / 번호 2
- 현재 화면 오른쪽 pane: Y1 / 번호 1

카메라 이름을 설정할 때 화면의 Left/Right 글자만 보지 말고 Y1/Y2와 CAM1/CAM2를 함께 확인하십시오.

## Emulation Mode 주의

Emulation Mode는 Align 카메라 입력을 Basler emulator로 연결하는 기능입니다. 실제 Control 축 이동까지 자동으로 simulation 처리한다고 간주하면 안 됩니다. Emulation 상태에서도 이동 버튼을 누르기 전 Control mode와 장비 상태를 확인하십시오.
