# WPF Markdown Memo App 아키텍처 개선안 v2

## 1. 개선 방향 요약

기존 설계는 메모 앱의 큰 방향을 잡는 데 충분하지만, 실제 구현과 학습을 함께 진행하려면 몇 가지 기준을 더 명확히 하는 것이 좋다.

개선이 필요한 부분은 다음과 같다.

- 메모 파일 저장 규칙을 더 엄격하게 정의한다.
- Markdown metadata와 실제 파일명 관계를 정리한다.
- MVVM 학습 범위를 단계별로 나눈다.
- WPF UI 학습을 위한 화면 단위 목표를 만든다.
- 검색, 자동 저장, 백업은 처음부터 과하게 만들지 않고 단계적으로 확장한다.
- 작업 기록 기준을 별도 문서로 분리한다.

## 2. 앱의 최종 목표

이 앱은 단순 메모장이 아니라 다음 목적을 가진 개인 업무 지식 관리 도구다.

- 회사 업무 메모 저장
- 프로젝트별 TODO 관리
- 프로젝트별 수정 내용 기록
- 오류 분석 및 해결 과정 기록
- WPF/MVVM 학습 프로젝트로 활용
- 모든 데이터를 Markdown 파일로 보존

핵심 원칙은 다음과 같다.

```text
앱이 없어도 메모 파일은 사람이 읽을 수 있어야 한다.
```

따라서 저장 형식은 `.md` 파일을 기본으로 하고, 검색 인덱스나 캐시는 보조 데이터로만 사용한다.

## 3. 추천 프로젝트 구조

WPF 프로젝트 내부 구조는 아래처럼 나눈다.

```text
MemoApp
├─ App.xaml
├─ MainWindow.xaml
├─ Models
│  ├─ MemoDocument.cs
│  ├─ MemoMetadata.cs
│  ├─ MemoProject.cs
│  ├─ MemoTag.cs
│  ├─ TodoItem.cs
│  └─ AppSettings.cs
├─ ViewModels
│  ├─ MainViewModel.cs
│  ├─ ProjectTreeViewModel.cs
│  ├─ MemoListViewModel.cs
│  ├─ MemoEditorViewModel.cs
│  ├─ SearchViewModel.cs
│  └─ TodoViewModel.cs
├─ Views
│  ├─ ProjectTreeView.xaml
│  ├─ MemoListView.xaml
│  ├─ MemoEditorView.xaml
│  ├─ MarkdownPreviewView.xaml
│  └─ TodoView.xaml
├─ Services
│  ├─ MemoFileService.cs
│  ├─ MemoMetadataService.cs
│  ├─ MemoSearchService.cs
│  ├─ MarkdownRenderService.cs
│  ├─ TodoScanService.cs
│  ├─ BackupService.cs
│  └─ AppSettingsService.cs
├─ Stores
│  ├─ MemoStore.cs
│  └─ AppStateStore.cs
├─ Commands
├─ Converters
├─ Styles
│  ├─ Colors.xaml
│  ├─ Buttons.xaml
│  ├─ TextInputs.xaml
│  └─ DataViews.xaml
└─ Docs
   └─ development-log.md
```

## 4. 저장 폴더 구조

앱 데이터는 앱 설치 폴더가 아니라 사용자가 지정한 Vault 폴더에 저장한다.

추천 기본값:

```text
D:\MemoVault
```

Vault 구조:

```text
D:\MemoVault
├─ Company
│  ├─ 업무규칙.md
│  └─ 회의록
│     └─ 2026-07-13_주간회의.md
├─ Projects
│  ├─ SDC_uLED
│  │  ├─ TODO.md
│  │  ├─ 수정내용.md
│  │  └─ 이슈분석
│  │     └─ 2026-07-11_CAM3_ContactCheck.md
│  └─ MemoApp
│     ├─ 설계.md
│     └─ 개발일지.md
├─ Daily
│  └─ 2026-07-13.md
├─ Templates
│  ├─ 회의록.md
│  ├─ 이슈분석.md
│  └─ 개발작업.md
└─ .memoapp
   ├─ settings.json
   ├─ index.json
   └─ backups
```

`.memoapp` 폴더는 앱 내부 데이터용이다. 사용자가 직접 작성하는 메모와 분리한다.

## 5. Markdown 파일 표준

모든 메모는 Markdown 본문과 front matter를 가진다.

```md
---
id: 20260713-110000-memoapp-architecture
title: MemoApp 아키텍처 정리
project: MemoApp
category: 설계
tags: [wpf, mvvm, markdown]
created: 2026-07-13 11:00:00
updated: 2026-07-13 11:00:00
status: active
favorite: false
---

# MemoApp 아키텍처 정리

## 목적

WPF와 MVVM을 학습하면서 실제 사용할 수 있는 Markdown 메모 앱을 만든다.
```

### 5.1 필수 metadata

필수 항목:

- `id`
- `title`
- `project`
- `created`
- `updated`
- `status`

선택 항목:

- `category`
- `tags`
- `favorite`
- `related`

### 5.2 파일명 규칙

파일명은 사람이 보기 쉬워야 한다.

추천:

```text
YYYY-MM-DD_제목.md
프로젝트명_TODO.md
이슈명_분석.md
```

예:

```text
2026-07-13_MemoApp_아키텍처.md
SDC_uLED_CAM3_ContactCheck_분석.md
PGRecipeControlWindow_UI정리.md
```

파일명은 표시용이고, 앱 내부 식별은 metadata의 `id`를 기준으로 한다.

## 6. MVVM 학습 로드맵

이 프로젝트는 MVVM을 배우기 위한 실습 프로젝트이므로 기능 구현 순서와 학습 목표를 연결한다.

### 6.1 1단계: Binding

목표:

- TextBox와 ViewModel 문자열 바인딩
- Button Command 바인딩
- ListBox ItemsSource 바인딩

학습할 것:

- `DataContext`
- `INotifyPropertyChanged`
- `ObservableObject`
- `ObservableCollection`
- `RelayCommand`

### 6.2 2단계: ViewModel 분리

목표:

- MainViewModel이 모든 것을 처리하지 않도록 분리
- ProjectTree, MemoList, Editor 역할 나누기

학습할 것:

- ViewModel 책임 분리
- 선택 상태 공유
- 부모 ViewModel과 자식 ViewModel 관계

### 6.3 3단계: Service 분리

목표:

- 파일 저장/로드를 ViewModel에서 제거
- 검색 로직을 Service로 분리

학습할 것:

- Service 계층
- 비동기 파일 I/O
- ViewModel 테스트 가능성

### 6.4 4단계: UI Resource와 Style

목표:

- 반복되는 버튼/입력 스타일 공통화
- 앱 전체의 색상/간격 통일

학습할 것:

- ResourceDictionary
- StaticResource
- Style
- ControlTemplate는 후순위

## 7. WPF UI 구성 개선안

초기 화면은 복잡하게 만들지 않는다.

```text
┌─────────────────────────────────────────────────────────────┐
│ 검색창                                      새 메모  저장     │
├───────────────┬────────────────────┬────────────────────────┤
│ 프로젝트 트리  │ 메모 목록           │ 편집기                 │
│ 태그           │                    │ 미리보기 탭             │
│ TODO           │                    │                        │
└───────────────┴────────────────────┴────────────────────────┘
```

### 7.1 Grid 비율

추천 비율:

```xml
<Grid.ColumnDefinitions>
    <ColumnDefinition Width="220"/>
    <ColumnDefinition Width="320"/>
    <ColumnDefinition Width="*"/>
</Grid.ColumnDefinitions>
```

왼쪽과 가운데는 고정 폭, 오른쪽 편집 영역은 남은 공간을 사용한다.

### 7.2 상단 검색 영역

상단은 `DockPanel` 또는 `Grid`를 사용한다.

구성:

- 검색 TextBox
- 새 메모 Button
- 저장 Button
- 설정 Button

### 7.3 편집 영역

편집 영역은 `TabControl`을 추천한다.

```text
Edit | Preview | Metadata
```

초기 버전에서는 Edit만 구현하고, Preview는 2차 단계로 미룬다.

## 8. 기능 우선순위 재정리

### 8.1 반드시 먼저 만들 기능

1. Vault 폴더 선택
2. `.md` 파일 목록 로드
3. 메모 선택
4. 본문 편집
5. 저장
6. 제목 검색
7. 본문 검색

### 8.2 다음 단계 기능

1. 프로젝트 TreeView
2. 태그 파싱
3. TODO 추출
4. 자동 저장
5. Markdown 미리보기
6. 백업

### 8.3 나중에 만들 기능

1. Git 연동
2. Lucene.NET 검색 인덱스
3. 전역 단축키 Quick Capture
4. 여러 창 동시 편집
5. 플러그인 구조

## 9. 자동 저장 정책

자동 저장은 편리하지만 처음부터 넣으면 디버깅이 어려워질 수 있다.

권장 순서:

1. 수동 저장만 구현
2. 수정됨 표시 구현
3. Ctrl+S 구현
4. 2초 debounce 자동 저장 구현
5. 저장 실패 시 알림 구현

자동 저장 규칙:

```text
마지막 입력 후 2초 동안 추가 입력이 없으면 저장한다.
```

주의:

- 저장 중 다시 입력되면 다음 저장 예약
- 저장 실패 시 본문을 잃지 않도록 메모리에 유지
- 앱 종료 시 미저장 변경 여부 확인

## 10. 검색 설계

초기 검색은 단순하게 구현한다.

```text
앱 시작
→ 모든 md 파일 읽기
→ MemoDocument 목록 생성
→ 검색어 입력 시 메모리에서 필터링
```

검색 대상:

- title
- file name
- body
- project
- tags

검색 결과 정렬:

1. 제목 일치
2. 태그 일치
3. 본문 일치
4. 최근 수정일

나중에 메모가 많아지면 index 파일을 만든다.

```text
D:\MemoVault\.memoapp\index.json
```

## 11. 백업 설계

백업은 사용자가 신뢰할 수 있어야 한다.

초기 백업:

- 앱 시작 시 하루 1회 zip 백업
- 최근 30개 유지

백업 경로:

```text
D:\MemoVault\.memoapp\backups\backup_yyyyMMdd_HHmmss.zip
```

주의:

- `.memoapp\backups`는 다시 백업 대상에 포함하지 않는다.
- 저장 실패 로그를 남긴다.

## 12. 추천 NuGet 패키지

처음부터 필요한 것:

```text
CommunityToolkit.Mvvm
```

Markdown preview 단계에서 추가:

```text
Markdig
Microsoft.Web.WebView2
```

편집기 개선 단계에서 추가:

```text
ICSharpCode.AvalonEdit
```

front matter 파싱 개선 단계에서 추가:

```text
YamlDotNet
```

## 13. 구현 시 주의할 점

### 13.1 View에 로직을 넣지 않는다

가능한 피할 것:

```csharp
private void SaveButton_Click(...)
{
    File.WriteAllText(...);
}
```

권장:

```xml
<Button Content="저장" Command="{Binding SaveCommand}"/>
```

### 13.2 파일 경로와 UI 표시명을 분리한다

파일명은 변경될 수 있다. 내부 식별은 `id`를 사용한다.

### 13.3 삭제는 반드시 확인한다

삭제 동작은 실수 방지가 중요하다.

권장:

- 휴지통 폴더로 이동
- 완전 삭제는 별도 동작

### 13.4 인코딩은 UTF-8 고정

Markdown 파일은 UTF-8로 저장한다.

## 14. 최종 개발 순서

추천 순서:

1. WPF 프로젝트 생성
2. CommunityToolkit.Mvvm 설치
3. MainWindow 3분할 UI 작성
4. MainViewModel 연결
5. MemoDocument 모델 작성
6. MemoFileService 작성
7. Vault 폴더의 md 파일 목록 로드
8. ListBox 표시
9. 선택한 메모 본문 표시
10. 저장 기능
11. 검색 기능
12. 프로젝트 TreeView
13. TODO 추출
14. Markdown preview
15. 백업

## 15. 결론

이 앱은 업무 도구이면서 WPF/MVVM 학습용 프로젝트다.

처음부터 완성형 노트 앱을 만들려고 하지 말고, 다음 최소 기능부터 만든다.

```text
md 파일 목록 표시
선택한 md 열기
본문 수정
저장
검색
```

이 기능이 안정화되면 프로젝트 분류, 태그, TODO, Preview, 백업 순서로 확장한다.

