# Recipe Glass Map 사용자 매뉴얼

작성일: 2026-08-03

## 1. 화면 목적

`Recipe Glass Map` 창은 현재 레시피의 셀 배치 설계값을 편집하고, 그 설계값으로 실제 검사에 사용할 Cell 목록을 만드는 화면이다.

이 화면에서는 다음 작업을 수행한다.

- 분판/Coordinate별 셀 크기, 수량, 간격, block 구조 입력
- 입력 결과를 도면 형태로 미리 확인
- 다른 Recipe의 Glass Map 설계 가져오기
- 설계값으로 실행용 `Cells` 재생성

중요:

> 화면의 Preview가 바뀌었다고 실제 검사 Cell이 자동으로 바뀐 것은 아니다. 좌표를 수정한 뒤 반드시 `Generate Cells`를 눌러야 한다.

## 2. 화면 열기

1. MainWindow에서 RecipeWindow를 연다.
2. 편집할 Recipe를 열거나 새 Recipe를 준비한다.
3. RecipeWindow 메뉴에서 `레시피 Glass Map`을 누른다.

같은 RecipeWindow에서 이 메뉴를 다시 누르면 이미 열린 창이 앞으로 활성화된다.

## 3. 작업 전 확인 사항

Glass Map을 입력하기 전에 다음 항목을 먼저 확인한다.

1. RecipeWindow의 현재 Recipe가 맞는지 확인한다.
2. `Glass Size` 표시에서 올바른 GlassSize 모델이 연결되어 있는지 확인한다.
3. GlassSize의 폭/높이와 다음 이름 정책이 현장 기준과 맞는지 확인한다.
   - Cutting Mark 위치
   - First Cell Position
   - Partition 이름 사용 여부
   - X/Y 이름 규칙
   - Cell 이름 token 순서
4. 기존 Cell의 `Use`, `IpNo`, 사용자 정의 이름을 유지해야 한다면 현재 셀 목록을 먼저 확인한다.

GlassSize가 틀리면 셀 배치 반전, 이름, Cutting Mark, 실행 좌표 및 축 목표값이 함께 달라질 수 있다.

## 4. 화면 구성

### 4.1 왼쪽: Recipe Preview

현재 Coordinate 설계값을 글래스 외곽과 셀 사각형으로 표시한다.

- 셀 이름은 셀이 화면에서 충분히 크게 보일 때 표시된다.
- 편집값을 바꾸면 Preview가 즉시 갱신된다.
- 이 화면은 도면 입력용이므로 장비 운영 화면의 회전과 인입 방향 화살표를 표시하지 않는다.
- 분판 이름의 큰 overlay도 표시하지 않는다.

`[추론] (코드 확인)` Preview에서 셀을 클릭하면 선택 테두리가 보일 수 있지만, 클릭으로 Coordinate가 선택되거나 Cell의 Use 값이 바뀌지는 않는다.

### 4.2 왼쪽 아래: 상태 메시지

버튼 실행 결과와 오류를 표시한다.

예:

- Coordinate model 추가/삭제
- 다른 Recipe에서 가져오기 성공/실패
- Cells 재생성 성공/실패
- Preview 갱신 실패

오류가 발생하면 다음 작업으로 넘어가기 전에 메시지를 확인한다.

### 4.3 오른쪽 위: Recipe Snapshot

버튼, 현재 Recipe 정보, GlassSize 정보, Coordinate 목록을 표시한다.

Coordinate 목록에서 항목을 선택하면 아래 `Snapshot Coordinate Editor`에 해당 값이 표시된다.

### 4.4 오른쪽 아래: Snapshot Coordinate Editor

선택된 Coordinate의 셀 크기, 수량, 위치, 간격, block 구성을 입력한다.

모든 거리/크기 값의 기본 단위는 `µm`이다.

## 5. 버튼 사용법

### 5.1 Add Copy

현재 선택한 Coordinate를 복사하여 새 Coordinate를 추가한다.

사용 순서:

1. Coordinate 목록에서 복사할 항목을 선택한다.
2. `Add Copy`를 누른다.
3. 새로 추가된 Coordinate가 선택되는지 확인한다.
4. Name, offset, block 거리 등 다른 값을 수정한다.
5. Preview에서 새 배치를 확인한다.
6. 모든 입력이 끝나면 `Generate Cells`를 누른다.

`[추론] (코드 확인)` 새 이름은 중복을 피하여 `A`~`Z`, 이후 `Coord N` 순으로 자동 생성된다.

주의:

- 복사 직후에는 이전 Coordinate와 같은 위치에 셀이 겹쳐 보일 수 있다.
- 새 Coordinate의 offset 또는 block 배치를 반드시 현장 도면에 맞게 수정한다.
- Add Copy만으로 실행용 Cells는 바뀌지 않는다.

### 5.2 Remove

선택한 Coordinate를 삭제한다.

사용 순서:

1. 삭제할 Coordinate를 선택한다.
2. `Remove`를 누른다.
3. 확인 메시지의 Model 이름을 확인한다.
4. 삭제를 확정한다.
5. Preview에서 배치가 제거되었는지 확인한다.
6. `Generate Cells`를 눌러 실행용 Cells에서도 제거한다.

`[추론] (코드 확인)` 마지막 Coordinate를 삭제하면 빈 목록 대신 기본 Coordinate 하나가 다시 추가된다.

### 5.3 Import From Recipe

다른 Recipe에 저장된 Glass Map 설계 snapshot을 현재 Recipe로 가져온다.

사용 순서:

1. 현재 Recipe의 미저장 변경이 필요한지 확인하고 먼저 저장한다.
2. `Import From Recipe`를 누른다.
3. 원본 Recipe 파일을 선택한다.
4. 상태 메시지에서 가져오기 성공 여부를 확인한다.
5. Coordinate 목록과 Preview를 확인한다.
6. RecipeWindow의 셀 목록에서 생성된 Cell 수, 이름, Use, IP를 확인한다.
7. 현재 Recipe를 Validate 후 Save한다.

가져오기 범위:

- 가져옴: 원본 Recipe의 `GlassMapDesignSnapshot`
- 가져오지 않음: 원본 Recipe의 GlassSize 자체
- 셀 생성 기준: 현재 Recipe의 GlassSize와 이름 정책

`[추론] (코드 확인)` 이 기능은 가져오기 전에 현재 snapshot을 덮어쓸지 별도 확인하지 않는다. 또한 현재 Recipe의 기존 Cell과 ID 또는 자동 이름이 일치하면 `Use`, `IpNo`, `RoundCell`, 사용자 정의 이름을 보존한다.

주의:

- 크기가 다른 GlassSize의 Recipe에서 가져오면 현재 GlassSize 기준으로 좌표가 반전되거나 글래스 밖에 배치될 수 있다.
- 가져온 뒤 Preview만 보지 말고 셀 목록과 셀 맵을 모두 확인한다.
- 가져오기 결과는 Save해야 파일에 남는다.

### 5.4 Generate Cells

현재 Coordinate 입력을 실제 검사에 사용할 `GlassMap.Cells`로 재생성한다.

이 버튼은 Coordinate 편집 후 가장 중요한 버튼이다.

실행 결과:

- 셀 위치와 크기 생성
- 셀 ID와 자동 이름 생성
- 글래스 중심 실행 좌표로 변환
- XIndex/YIndex 재계산
- 기존 Use/IP/사용자 이름 일부 보존
- 필요 시 IP 배정 보정
- RecipeWindow 셀 목록/셀 맵 갱신
- 모션 목표값 갱신

사용해야 하는 경우:

- 셀 크기 변경
- 셀 수 변경
- offset 변경
- cell/block 간격 변경
- block 수 변경
- Coordinate 추가/삭제
- Coordinate 이름 변경
- GlassSize 이름 정책 또는 First Cell Position 변경

작업 후 반드시 확인할 항목:

1. 전체 Cell 수
2. 분판별 셀 배치
3. 첫 Cell 위치
4. 자동 Cell 이름
5. XIndex/YIndex
6. IP1/IP2 배정
7. Use/Unuse
8. 사용자 정의 Cell 이름
9. StageX/Y1/Y2 등 모션 목표

### 5.5 Refresh Preview

현재 화면과 문서 상태를 동기화하고 Preview를 다시 그린다.

사용할 때:

- 외부 창에서 GlassSize 관련 값을 변경한 뒤
- Preview가 최신 상태로 보이지 않을 때
- 현재 셀 인덱스/모션 대상과 표시를 다시 계산할 때

주의:

> `Refresh Preview`는 `Generate Cells`가 아니다. Coordinate 변경 후 실제 Cell 좌표를 만들려면 반드시 `Generate Cells`를 사용한다.

## 6. 입력 파라미터 사용법

### 6.1 Name

Coordinate 또는 분판을 식별하는 이름이다.

셀 이름에 Partition token을 사용하는 GlassSize 정책이면 Name의 첫 영문/숫자 문자가 자동 셀 이름의 Partition prefix로 사용된다.

예:

- `A` → Partition prefix `A`
- `B-Right` → Partition prefix `B`
- 이름이 비었거나 사용할 문자가 없으면 Coordinate 순서 기반 prefix 사용

같은 prefix가 중복되면 셀 이름이 겹칠 수 있으므로 Coordinate별로 구분되는 이름을 권장한다.

### 6.2 CELL_SIZE_X / CELL_SIZE_Y

셀 사각형의 폭과 높이다.

- `CELL_SIZE_X`: X방향 폭
- `CELL_SIZE_Y`: Y방향 높이
- 단위: µm
- 실사용 범위: 0보다 큰 값

0은 입력 컨트롤에서 허용되지만 생성된 Cell 크기 검증에 실패한다.

### 6.3 CELL_X_COUNT / CELL_Y_COUNT

현재 Coordinate 전체의 X/Y 방향 셀 수다.

중요:

- block 하나당 개수가 아니다.
- block이 여러 개면 전체 개수를 block들에 자동 분배한다.
- 정상적인 양수 값일 때 총 셀 수는 `CELL_X_COUNT × CELL_Y_COUNT`다.

예:

```text
CELL_X_COUNT  = 12
BLOCK_COUNT_X = 2
```

X방향 두 block에 `6개 + 6개`가 배치된다.

```text
CELL_Y_COUNT  = 15
BLOCK_COUNT_Y = 2
```

Y방향 두 block에 `8개 + 7개`가 배치된다.

### 6.4 OFFSET_E_X / OFFSET_E_Y

설계 기준 첫 block의 첫 Cell 좌상단 위치다.

- 기준 원점: 글래스 좌상단
- `OFFSET_E_X`: 원점에서 오른쪽 거리
- `OFFSET_E_Y`: 원점에서 아래쪽 거리
- 단위: µm

GlassSize의 First Cell Position이 오른쪽 또는 아래쪽이면 프로그램이 글래스 폭/높이를 기준으로 대칭 변환한다.

### 6.5 CELL_DIST_X / CELL_DIST_Y

같은 block 안에서 인접 Cell 시작점 사이의 거리, 즉 pitch다.

```text
다음 Cell 시작 X = 현재 시작 X + CELL_DIST_X
다음 Cell 시작 Y = 현재 시작 Y + CELL_DIST_Y
```

셀 사이의 실제 빈 간격은 대략 다음과 같다.

```text
X 빈 간격 = CELL_DIST_X - CELL_SIZE_X
Y 빈 간격 = CELL_DIST_Y - CELL_SIZE_Y
```

`[추론]` CELL_DIST가 CELL_SIZE보다 작으면 셀이 겹친다. 현재 프로그램은 중첩을 별도 오류로 검출하지 않으므로 Preview에서 반드시 확인한다.

### 6.6 BLOCK_DIST_X / BLOCK_DIST_Y

인접 block의 시작점 사이 거리다.

```text
n번째 X block 시작 = OFFSET_E_X + n × BLOCK_DIST_X
n번째 Y block 시작 = OFFSET_E_Y + n × BLOCK_DIST_Y
```

이는 마지막 Cell 끝에서 다음 block까지의 빈 간격이 아니라 **block 시작점과 다음 block 시작점 사이 거리**다.

### 6.7 BLOCK_COUNT_X / BLOCK_COUNT_Y

X/Y 방향으로 나눌 block 수다.

- 1: block 분할 없이 하나의 영역
- 2 이상: 전체 셀 수를 여러 block에 앞쪽부터 균등 분배

`[추론] (코드 확인)` 0 이하 값을 입력해도 생성 로직은 1 block으로 처리한다. 그러나 이런 값은 설계 의도를 불명확하게 하므로 1 이상의 값을 사용한다.

## 7. 권장 작업 절차

### 7.1 기존 Glass Map 수정

1. RecipeWindow에서 대상 Recipe를 연다.
2. GlassSize 정보가 올바른지 확인한다.
3. `레시피 Glass Map` 창을 연다.
4. 수정할 Coordinate를 선택한다.
5. Name, 크기, 수량, offset, pitch, block 값을 입력한다.
6. 왼쪽 Preview에서 위치, 방향, 겹침, 글래스 외곽 초과를 확인한다.
7. 다른 Coordinate도 같은 방식으로 수정한다.
8. `Generate Cells`를 누른다.
9. RecipeWindow의 셀 목록에서 Cell 수, 이름, XIndex/YIndex, IP, Use를 확인한다.
10. RecipeWindow의 셀 맵에서 운영 방향을 포함한 전체 배치를 확인한다.
11. 필요하면 IP 자동 할당 또는 분할 적용을 다시 수행한다.
12. `Validate`를 실행한다.
13. `Save`를 실행한다.

### 7.2 새 분판 추가

1. 가장 비슷한 Coordinate를 선택한다.
2. `Add Copy`를 누른다.
3. Name을 새 분판 식별자로 변경한다.
4. OFFSET과 필요 시 block 값을 수정한다.
5. Preview에서 기존 분판과 겹치지 않는지 확인한다.
6. `Generate Cells`를 누른다.
7. 셀 목록에서 새 분판 Cell 이름과 개수를 확인한다.
8. IP/Use/사용자 정의 이름을 검토한다.
9. Validate 후 Save한다.

### 7.3 다른 Recipe 배치 재사용

1. 현재 Recipe를 먼저 저장한다.
2. `Import From Recipe`를 누른다.
3. 검증된 원본 Recipe를 선택한다.
4. 현재 GlassSize 기준 Preview를 확인한다.
5. Cell 수와 이름을 원본과 단순 비교하지 말고, 현재 GlassSize 정책에 맞는지 확인한다.
6. 셀 목록의 Use/IP/사용자 이름을 확인한다.
7. Validate 후 Save한다.

## 8. Preview와 실제 Cells를 구분하는 방법

| 확인 위치 | 사용하는 데이터 | 용도 |
|---|---|---|
| Recipe Glass Map의 왼쪽 Preview | `GlassMapDesignSnapshot.Coordinates`에서 즉시 생성 | 설계 입력 확인 |
| RecipeWindow 셀 목록 | `GlassMap.Cells` | 실제 실행 Cell 속성 확인 |
| RecipeWindow 셀 맵 | `GlassMap.Cells` | 실제 실행 배치/운영 표시 확인 |

다음과 같은 경우 설계와 실행 데이터가 다를 수 있다.

```text
Coordinate 값을 수정함
Preview가 바뀜
Generate Cells를 누르지 않음
```

이 경우 왼쪽 Preview는 새 설계를 보여 주지만 셀 목록과 검사 실행은 기존 Cells를 사용할 수 있다.

## 9. 값 입력 시 주의사항

- 모든 거리와 크기는 µm 단위로 입력한다.
- `CELL_SIZE_X/Y`는 반드시 0보다 크게 입력한다.
- `CELL_X/Y_COUNT`는 실제 필요한 양수 개수로 입력한다.
- `BLOCK_COUNT_X/Y`는 1 이상을 사용한다.
- 음수 offset/distance는 의도하지 않은 배치가 될 수 있으므로 사용하지 않는 것을 권장한다.
- 셀이 글래스 외곽을 벗어나거나 서로 겹쳐도 전용 오류가 나오지 않을 수 있으므로 Preview로 확인한다.
- Coordinate 이름 변경은 자동 셀 이름에 영향을 줄 수 있다.
- First Cell Position 변경은 이름뿐 아니라 실제 좌우/상하 배치를 반전시킨다.
- 대규모 배치 변경 뒤에는 보존된 Use/IP/사용자 정의 이름이 올바른 셀에 이어졌는지 확인한다.
- 편집 창을 닫는 것만으로 Recipe가 저장되지 않는다.

## 10. 오류 및 이상 상태 확인

### Preview가 비어 있음

다음을 확인한다.

1. GlassSize가 유효한지
2. Coordinate가 존재하는지
3. CELL_X/Y_COUNT가 양수인지
4. CELL_SIZE_X/Y가 양수인지
5. 상태 메시지에 Preview 갱신 오류가 있는지

### Generate Cells 실패

다음을 확인한다.

1. 현재 Recipe에 올바른 GlassSize가 지정되었는지
2. GlassSize 모델이 로드/검증 가능한지
3. Coordinate 값이 숫자로 입력되었는지
4. 상태 메시지의 예외 내용을 확인한다.

### Preview와 셀 목록이 다름

1. `Generate Cells`를 눌렀는지 확인한다.
2. RecipeWindow 셀 목록을 다시 확인한다.
3. 필요한 경우 `Refresh Preview`를 실행한다.
4. Validate 후 Save한다.

### Snapshot Summary에 `파일 없음` 표시

`[추론] (코드 확인)` 현재 per-recipe snapshot이 없다는 의미가 아니라 과거 Template 파일 경로가 설정되지 않았다는 뜻일 수 있다. Coordinate 개수와 실제 Recipe snapshot/Preview를 함께 확인한다.

## 11. 최종 저장 전 점검표

- [ ] 올바른 Recipe를 편집했는가?
- [ ] 올바른 GlassSize가 적용되어 있는가?
- [ ] 모든 Coordinate 이름이 구분되는가?
- [ ] Cell 크기와 수량이 도면과 일치하는가?
- [ ] Offset과 pitch가 µm 단위로 올바른가?
- [ ] Block 수와 Block 간격이 올바른가?
- [ ] Preview에 겹침이나 글래스 외곽 초과가 없는가?
- [ ] `Generate Cells`를 실행했는가?
- [ ] 셀 목록의 총 Cell 수가 예상과 같은가?
- [ ] Cell 이름과 First Cell 위치가 올바른가?
- [ ] XIndex/YIndex가 장비 순서와 맞는가?
- [ ] IP1/IP2 배정이 올바른가?
- [ ] Use/Unuse와 사용자 정의 이름을 확인했는가?
- [ ] Validate를 통과했는가?
- [ ] Save를 완료했는가?

