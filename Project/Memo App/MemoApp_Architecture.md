# WPF Markdown Memo App 프로젝트 아키텍처 정리

## 1. 프로젝트 목표

이 프로젝트는 PC에서 사용하는 개인/업무용 메모 앱을 만드는 것을 목표로 한다.

주요 목적은 다음과 같다.

- 회사에서 자주 사용하는 업무 내용 정리
- 프로젝트별 해야 할 일 관리
- 프로젝트별 수정 내용 및 이슈 기록
- 기억해야 할 내용, 회의 내용, 개발 노트 저장
- Markdown 파일 기반으로 장기 보관 가능한 메모 저장
- WPF UI와 MVVM 패턴을 학습하면서 실제 앱을 구현

최종적으로는 단순 메모장이 아니라, 로컬 Markdown 파일을 기반으로 동작하는 작은 업무 지식 관리 도구를 지향한다.

## 2. 핵심 기능

### 2.1 기본 메모 기능

- Markdown 파일 생성
- Markdown 파일 수정
- Markdown 파일 삭제
- 메모 제목 변경
- 메모 자동 저장
- 최근 수정일 기준 정렬
- 즐겨찾기 또는 고정 메모

### 2.2 프로젝트별 관리

메모를 프로젝트 단위로 관리한다.

예시:

```text
D:\MemoVault
├─ Company
│  ├─ 업무규칙.md
│  └─ 회의록.md
├─ Projects
│  ├─ SDC_uLED
│  │  ├─ TODO.md
│  │  ├─ 수정내용.md
│  │  └─ 이슈정리.md
│  └─ MemoApp
│     ├─ 설계.md
│     └─ 개발일지.md
└─ Daily
   └─ 2026-07-13.md
```

### 2.3 검색 기능

검색 대상:

- 파일명
- 제목
- 본문
- 태그
- 프로젝트명
- TODO 항목

초기 버전에서는 모든 `.md` 파일을 읽어 메모리에 올린 뒤 LINQ로 검색한다. 메모가 많아지면 이후 SQLite 또는 Lucene.NET 기반 인덱싱으로 확장할 수 있다.

### 2.4 Markdown 편집 및 미리보기

권장 구성:

- 편집기: AvalonEdit 또는 WPF TextBox
- Markdown 파서: Markdig
- 미리보기: WebView2 또는 FlowDocument

초기 버전은 TextBox 기반으로 시작해도 된다. 이후 Markdown 문법 강조가 필요하면 AvalonEdit으로 교체한다.

### 2.5 TODO 관리

Markdown 체크박스를 활용한다.

```md
## 해야 할 일

- [ ] PG Recipe Control Window UI 정리
- [ ] Config 연동 구조 정리
- [x] 기본 프로젝트 생성
```

앱에서는 전체 메모를 스캔해서 `- [ ]`, `- [x]` 항목만 모아 TODO 화면에 표시할 수 있다.

## 3. 추천 화면 구성

전체 화면은 3분할 구조를 추천한다.

```text
┌─────────────────────────────────────────────────────────────┐
│ SearchBox                                                    │
├───────────────┬───────────────────────┬─────────────────────┤
│ Project Tree  │ Memo List             │ Markdown Editor     │
│ Category      │ - 최근 메모            │ Preview             │
│ Tags          │ - 검색 결과            │ Metadata            │
│ TODO          │                       │                     │
└───────────────┴───────────────────────┴─────────────────────┘
```

### 3.1 왼쪽 영역

역할:

- 프로젝트 목록
- 카테고리 목록
- 태그 목록
- 전체 메모
- 오늘 메모
- TODO 모아보기
- 즐겨찾기

사용 WPF 컨트롤:

- TreeView
- ListBox
- Button

### 3.2 가운데 영역

역할:

- 선택된 프로젝트의 메모 목록 표시
- 검색 결과 표시
- 최근 수정 순 정렬

사용 WPF 컨트롤:

- ListBox
- DataGrid
- ListView

초기 구현은 ListBox가 간단하다.

### 3.3 오른쪽 영역

역할:

- Markdown 편집
- 제목/태그 표시
- 미리보기

사용 WPF 컨트롤:

- TextBox 또는 AvalonEdit
- WebView2
- TabControl

예시:

```text
오른쪽 영역
├─ 제목 TextBox
├─ 태그 TextBox
├─ TabControl
│  ├─ Edit
│  └─ Preview
└─ 상태 표시: 저장됨 / 수정됨 / 자동 저장 중
```

## 4. MVVM 아키텍처

이 프로젝트는 WPF 학습 목적도 있으므로 MVVM 구조를 명확히 분리한다.

```text
Views
├─ MainWindow.xaml
├─ MemoEditorView.xaml
├─ MemoListView.xaml
└─ ProjectTreeView.xaml

ViewModels
├─ MainViewModel.cs
├─ MemoEditorViewModel.cs
├─ MemoListViewModel.cs
├─ ProjectTreeViewModel.cs
└─ SearchViewModel.cs

Models
├─ MemoDocument.cs
├─ MemoMetadata.cs
├─ MemoSearchResult.cs
├─ ProjectNode.cs
└─ TodoItem.cs

Services
├─ MemoFileService.cs
├─ MarkdownMetadataService.cs
├─ MemoSearchService.cs
├─ TodoScanService.cs
├─ AppSettingsService.cs
└─ BackupService.cs
```

### 4.1 View

View는 화면만 담당한다.

View에서 해야 할 일:

- 버튼, TextBox, ListBox 배치
- Binding 선언
- Grid, StackPanel, DockPanel 등 레이아웃 구성

View에서 하지 말아야 할 일:

- 파일 저장 로직
- 검색 로직
- Markdown 파싱 로직
- 비즈니스 판단 로직

### 4.2 ViewModel

ViewModel은 화면 상태와 명령을 담당한다.

예시 역할:

- `ObservableCollection<MemoDocument>` 관리
- 선택된 메모 관리
- 검색어 관리
- 새 메모 생성 Command
- 저장 Command
- 삭제 Command
- 자동 저장 타이머 제어

예시:

```csharp
public partial class MainViewModel : ObservableObject
{
    public ObservableCollection<MemoDocument> Memos { get; } = new();

    [ObservableProperty]
    private MemoDocument? selectedMemo;

    [ObservableProperty]
    private string searchText = string.Empty;

    [RelayCommand]
    private void CreateMemo()
    {
    }

    [RelayCommand]
    private async Task SaveMemoAsync()
    {
    }
}
```

### 4.3 Model

Model은 데이터 구조만 표현한다.

예시:

```csharp
public sealed class MemoDocument
{
    public string Title { get; set; } = string.Empty;
    public string FilePath { get; set; } = string.Empty;
    public string ProjectName { get; set; } = string.Empty;
    public List<string> Tags { get; set; } = new();
    public string Body { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
```

### 4.4 Service

Service는 실제 작업을 담당한다.

예시:

- 파일 읽기/쓰기
- Markdown front matter 파싱
- 검색
- TODO 추출
- 백업

ViewModel은 Service를 호출하고, Service는 UI를 모른다.

## 5. Markdown 파일 형식

각 메모 파일은 Markdown 본문과 YAML front matter를 함께 가진다.

```md
---
title: PG Recipe Control Window 정리
project: SDC_uLED
tags: [wpf, mvvm, pg]
created: 2026-07-13
updated: 2026-07-13
status: active
favorite: false
---

# PG Recipe Control Window 정리

## 목적

PG Recipe를 선택하고 PG 장비에 적용하는 UI를 만든다.

## 해야 할 일

- [ ] PG 목록 ComboBox 구성
- [ ] Model List Up 버튼 구현
- [ ] 다운로드 진행률 표시
```

이 형식을 쓰면 일반 텍스트 편집기에서도 열 수 있고, 앱에서는 메타데이터를 읽어 검색/분류에 활용할 수 있다.

## 6. 데이터 저장 위치

추천 저장 위치:

```text
D:\MemoVault
```

앱 설정 파일:

```text
D:\MemoVault\.memoapp\settings.json
```

검색 캐시:

```text
D:\MemoVault\.memoapp\index.json
```

자동 백업:

```text
D:\MemoVault\.memoapp\backups
```

## 7. WPF UI 학습 포인트

이 프로젝트를 진행하면서 익히면 좋은 WPF 개념은 다음과 같다.

### 7.1 Layout Panel

필수로 익힐 것:

- Grid
- StackPanel
- DockPanel
- ScrollViewer

자주 쓰는 패턴:

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="240"/>
        <ColumnDefinition Width="*"/>
        <ColumnDefinition Width="2*"/>
    </Grid.ColumnDefinitions>
</Grid>
```

### 7.2 Binding

WPF의 핵심이다.

```xml
<TextBox Text="{Binding SearchText, UpdateSourceTrigger=PropertyChanged}"/>
<ListBox ItemsSource="{Binding Memos}" SelectedItem="{Binding SelectedMemo}"/>
<Button Content="Save" Command="{Binding SaveMemoCommand}"/>
```

### 7.3 ObservableCollection

화면에 표시되는 목록에는 `ObservableCollection<T>`를 사용한다.

```csharp
public ObservableCollection<MemoDocument> Memos { get; } = new();
```

### 7.4 Command

버튼 클릭은 code-behind의 Click보다 Command를 사용한다.

```xml
<Button Content="New Memo" Command="{Binding CreateMemoCommand}"/>
```

### 7.5 Style과 Resource

버튼, TextBox, ListBox 스타일을 공통화한다.

```xml
<Style x:Key="PrimaryButton" TargetType="Button">
    <Setter Property="Height" Value="32"/>
    <Setter Property="Padding" Value="12,0"/>
</Style>
```

## 8. 개발 단계

### 1단계: 기본 골격

- WPF 프로젝트 생성
- MVVM 폴더 구조 생성
- MainWindow 3분할 UI 구성
- MemoVault 경로 설정

### 2단계: 파일 목록 표시

- `.md` 파일 검색
- 메모 목록 표시
- 선택한 메모 본문 로드

### 3단계: 편집 및 저장

- TextBox로 Markdown 편집
- Ctrl+S 저장
- 자동 저장 구현
- 수정 상태 표시

### 4단계: 검색

- 검색어 입력
- 제목/본문/태그 검색
- 검색 결과 하이라이트는 후순위

### 5단계: 프로젝트/태그 관리

- 폴더 기반 프로젝트 TreeView
- 태그 목록 표시
- 태그 클릭 시 필터링

### 6단계: Markdown 미리보기

- Markdig 적용
- WebView2 미리보기 적용
- Edit/Preview 탭 구성

### 7단계: TODO 모아보기

- 모든 메모에서 `- [ ]` 항목 추출
- TODO 화면 구성
- 완료 항목 토글

### 8단계: 안정화

- 자동 백업
- 파일명 충돌 처리
- 삭제 전 확인
- 최근 열었던 프로젝트 기억

## 9. 추천 NuGet 패키지

초기 버전:

```text
CommunityToolkit.Mvvm
Markdig
```

확장 버전:

```text
Microsoft.Web.WebView2
ICSharpCode.AvalonEdit
YamlDotNet
```

각 패키지 용도:

- `CommunityToolkit.Mvvm`: MVVM 구현 보조
- `Markdig`: Markdown을 HTML로 변환
- `WebView2`: Markdown Preview 표시
- `AvalonEdit`: Markdown 편집기 개선
- `YamlDotNet`: front matter 파싱

## 10. 추가하면 좋은 기능

### 10.1 Daily Note

매일 자동으로 날짜별 메모를 만든다.

```text
Daily/2026-07-13.md
```

### 10.2 Quick Capture

단축키로 빠르게 메모를 추가한다.

예:

```text
Ctrl + Alt + M
```

### 10.3 작업 이력

프로젝트별 수정 내용을 자동으로 모아본다.

```md
## 2026-07-13

- PGRecipeControlWindow UI 구성
- Config의 EEC-P725R2 Display 목록 바인딩 확인
```

### 10.4 템플릿

자주 쓰는 메모 양식을 제공한다.

예:

- 회의록
- 버그 분석
- 코드 수정 기록
- TODO
- 프로젝트 노트

### 10.5 백업

앱 종료 시 또는 하루 1회 zip 백업을 생성한다.

```text
D:\MemoVault\.memoapp\backups\backup_20260713.zip
```

### 10.6 Git 연동

나중에 메모 폴더를 Git 저장소로 관리할 수 있다.

장점:

- 변경 이력 추적
- 실수로 삭제한 메모 복구
- 여러 PC 간 동기화 가능

## 11. 첫 구현 목표

처음부터 모든 기능을 만들지 말고 아래 기능만 먼저 만든다.

- MemoVault 경로 설정
- `.md` 파일 목록 표시
- 메모 선택 시 본문 표시
- 본문 수정
- 저장
- 검색

이 단계까지만 구현해도 실제 업무에 사용할 수 있는 최소 메모 앱이 된다.

## 12. 학습 목표

이 프로젝트를 통해 익힐 내용:

- WPF Grid 레이아웃
- Binding
- ObservableCollection
- INotifyPropertyChanged
- Command
- MVVM 구조
- 파일 I/O
- Markdown 처리
- 검색 로직
- 설정 저장
- 자동 저장

## 13. 권장 첫 화면 XAML 구조

```xml
<Grid>
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="*"/>
    </Grid.RowDefinitions>

    <TextBox Grid.Row="0"
             Text="{Binding SearchText, UpdateSourceTrigger=PropertyChanged}"
             Height="34"
             Margin="8"/>

    <Grid Grid.Row="1">
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="220"/>
            <ColumnDefinition Width="320"/>
            <ColumnDefinition Width="*"/>
        </Grid.ColumnDefinitions>

        <TreeView Grid.Column="0"
                  ItemsSource="{Binding ProjectNodes}"/>

        <ListBox Grid.Column="1"
                 ItemsSource="{Binding FilteredMemos}"
                 SelectedItem="{Binding SelectedMemo}"/>

        <TextBox Grid.Column="2"
                 Text="{Binding SelectedMemo.Body, UpdateSourceTrigger=PropertyChanged}"
                 AcceptsReturn="True"
                 AcceptsTab="True"
                 VerticalScrollBarVisibility="Auto"/>
    </Grid>
</Grid>
```

## 14. 결론

이 메모 앱은 업무에 바로 사용할 수 있는 도구이면서, WPF와 MVVM을 배우기 좋은 프로젝트다.

처음에는 단순하게 시작한다.

```text
Markdown 파일 목록
→ 선택
→ 편집
→ 저장
→ 검색
```

그 다음 프로젝트 분류, 태그, TODO, 미리보기, 백업 기능을 순서대로 확장한다.

핵심은 모든 데이터를 `.md` 파일로 남기는 것이다. 이렇게 하면 앱이 없어도 메모를 열 수 있고, 장기적으로 안전하게 관리할 수 있다.
