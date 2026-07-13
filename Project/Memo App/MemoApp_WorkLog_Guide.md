# MemoApp 작업 기록 기준

## 1. 목적

이 문서는 WPF Markdown Memo App을 개발하면서 작업 내용을 일관되게 기록하기 위한 기준이다.

작업 기록의 목적은 다음과 같다.

- 오늘 무엇을 했는지 남긴다.
- 왜 그렇게 구현했는지 남긴다.
- 막힌 문제와 해결 과정을 남긴다.
- WPF/MVVM 학습 내용을 따로 정리한다.
- 나중에 프로젝트를 다시 볼 때 맥락을 빠르게 복원한다.

## 2. 기록 파일 위치

추천 위치:

```text
D:\_WJS\Memo\WorkLogs
```

일자별 기록:

```text
D:\_WJS\Memo\WorkLogs\2026-07-13.md
D:\_WJS\Memo\WorkLogs\2026-07-14.md
```

주제별 기록:

```text
D:\_WJS\Memo\WorkLogs\Topics\MVVM_Binding.md
D:\_WJS\Memo\WorkLogs\Topics\Markdown_Save_Load.md
D:\_WJS\Memo\WorkLogs\Topics\Search.md
```

## 3. 일일 작업 로그 형식

아래 형식을 기본으로 사용한다.

```md
# MemoApp 작업 로그 - 2026-07-13

## 오늘 목표

- [ ] MainWindow 기본 레이아웃 구성
- [ ] MainViewModel 연결
- [ ] md 파일 목록 로드 테스트

## 작업 내용

### 1. MainWindow 레이아웃 구성

작업:

- Grid 3분할 구조 생성
- 왼쪽 Project 영역
- 가운데 Memo List 영역
- 오른쪽 Editor 영역

이유:

- WPF Grid 레이아웃 학습
- 앱의 기본 화면 구조 확정

관련 파일:

- MainWindow.xaml

## 배운 내용

- RowDefinition의 Auto는 내부 컨트롤 크기만큼 잡힌다.
- ColumnDefinition의 *는 남은 공간을 비율로 나눈다.

## 문제 및 해결

### 문제 1. ListBox가 화면 아래로 밀림

원인:

- Margin으로 위치를 억지로 조정했다.

해결:

- Grid.RowDefinitions를 추가하고 Row를 분리했다.

## 다음 작업

- [ ] MemoDocument 모델 생성
- [ ] MemoFileService 초안 작성
- [ ] Vault 폴더에서 md 파일 검색
```

## 4. 작업 단위 기록 기준

작업 하나는 아래 항목을 포함하면 좋다.

```md
### 작업명

목표:

수정 내용:

이유:

관련 파일:

검증:

남은 문제:
```

예:

```md
### MemoFileService 생성

목표:

- Markdown 파일을 읽어서 MemoDocument로 변환한다.

수정 내용:

- MemoFileService.cs 추가
- LoadMemoAsync 메서드 작성

이유:

- 파일 I/O를 ViewModel에서 분리하기 위해

관련 파일:

- Services/MemoFileService.cs
- Models/MemoDocument.cs

검증:

- 테스트 md 파일 3개를 정상 로드함

남은 문제:

- YAML front matter 파싱은 아직 단순 문자열 처리
```

## 5. 이슈 분석 기록 기준

버그나 막힌 문제는 별도 형식으로 남긴다.

```md
## 이슈: 제목

발생 일시:

증상:

재현 방법:

관련 로그:

원인 추정:

확인한 코드:

해결 방법:

재발 방지:
```

예:

```md
## 이슈: Markdown 파일 저장 후 한글 깨짐

발생 일시:

- 2026-07-13 15:20

증상:

- 저장된 md 파일을 다시 열면 한글이 깨져 보임

재현 방법:

1. 한글이 포함된 메모 작성
2. 저장
3. 앱 재시작 후 다시 열기

원인 추정:

- 저장 인코딩이 UTF-8로 고정되지 않았을 가능성

해결 방법:

- File.WriteAllTextAsync 사용 시 Encoding.UTF8 지정

재발 방지:

- 모든 md 저장은 MemoFileService만 담당하도록 제한
```

## 6. 학습 기록 기준

WPF/MVVM 학습 내용은 작업 로그 안에 섞어도 되지만, 반복해서 볼 내용은 Topics 폴더에 따로 정리한다.

예:

```text
Topics\MVVM_Binding.md
Topics\Grid_Layout.md
Topics\Command.md
Topics\ObservableCollection.md
```

학습 기록 형식:

```md
# 주제명

## 개념

## 왜 필요한가

## 예제

## MemoApp에서 사용한 위치

## 헷갈린 점

## 정리
```

## 7. 변경 이력 기록 기준

기능이 어느 정도 만들어진 뒤에는 변경 이력을 따로 남긴다.

파일:

```text
D:\_WJS\Memo\CHANGELOG.md
```

형식:

```md
# 변경 이력

## 2026-07-13

### Added

- MainWindow 기본 3분할 레이아웃 추가
- MemoDocument 모델 추가

### Changed

- 없음

### Fixed

- 없음

### Notes

- WPF Grid 구조 학습 완료
```

## 8. 커밋 메시지 기준

Git을 사용한다면 커밋 메시지는 짧고 명확하게 작성한다.

예:

```text
Add memo document model
Add markdown file loader
Implement main window layout
Add memo search filter
Fix markdown save encoding
```

한글 커밋을 쓴다면:

```text
메모 파일 로드 기능 추가
메인 화면 레이아웃 구성
Markdown 저장 인코딩 수정
```

## 9. 완료 기준

작업 완료로 볼 수 있는 기준:

- 코드 작성 완료
- 실행 확인 완료
- 실패 케이스 하나 이상 확인
- 작업 로그 작성 완료
- 다음 작업 메모 작성 완료

## 10. 작업 로그 템플릿

새 날짜 작업을 시작할 때 아래 내용을 복사해서 사용한다.

```md
# MemoApp 작업 로그 - YYYY-MM-DD

## 오늘 목표

- [ ] 
- [ ] 
- [ ] 

## 작업 내용

### 1. 

목표:

수정 내용:

이유:

관련 파일:

검증:

남은 문제:

## 배운 내용

- 

## 문제 및 해결

### 문제 1.

증상:

원인:

해결:

## 다음 작업

- [ ] 
- [ ] 
- [ ] 
```

## 11. 결론

작업 기록은 길게 쓰는 것보다 꾸준히 남기는 것이 중요하다.

최소한 아래 4가지는 매번 남긴다.

```text
무엇을 했는가
왜 했는가
어떻게 확인했는가
다음에 무엇을 할 것인가
```

