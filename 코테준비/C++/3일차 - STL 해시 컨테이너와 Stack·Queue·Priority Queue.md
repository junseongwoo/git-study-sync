---
tags:
  - 코딩테스트
  - C++
  - 프로그래머스
  - unordered-set
  - unordered-map
  - stack
  - queue
  - priority-queue
date: 2026-08-03
day: 3
version: revised-integrated
intensity: double
source:
  - Cpp코테.pdf
---

# 3일차 - STL 해시 컨테이너 + Stack·Queue·Priority Queue

오늘은 두 개의 큰 주제를 한 번에 진행한다.

- 1부: `unordered_set`, `unordered_map`을 이용한 해시 실전
- 2부: `stack`, `queue`, `priority_queue`와 문제 패턴
- 3부: 책 기반 실습과 프로그래머스형 연습문제

> 오늘의 완료 기준: 존재 여부와 빈도 문제에 해시 컨테이너를 적용하고, LIFO·FIFO·우선순위 처리 문제에서 올바른 컨테이너를 선택해 직접 구현한다.

---

## 0. 책에서 참고한 범위와 2단계 검증 기준

`Cpp코테.pdf`의 다음 범위를 중심으로 보완했다.

- 1.8 `std::deque`
- 1.9 컨테이너 어댑터
- 1.9.1 `std::stack`
- 1.9.2 `std::queue`
- 1.9.3 `std::priority_queue`
- 1.9.4 어댑터 반복자
- 1.10 벤치마킹
- 실습 문제 3: 사무실 공유 프린터의 인쇄 대기 목록 시뮬레이션
- 3.4 C++ 해시 테이블
- 연습문제 16: STL에서 제공하는 해시 테이블
- 사용자 정의 자료형의 해시와 비교 함수

### 검증 방식

1. **1차 검증**: 관련 장 전체를 순서대로 읽고 자료구조의 성질, API, 예제 흐름을 확인한다.
2. **2차 검증**: 문서 작성 후 연습문제와 핵심 설명 페이지를 다시 열어 코드, 문제 조건, 용어를 재대조한다.

2차 대조 결과, 책 64~66쪽의 `deque`, 67~70쪽의 컨테이너 어댑터, 71쪽의 공유 프린터 실습, 142~147쪽의 C++ 해시 테이블과 연습문제 16 및 사용자 정의 해시 설명이 이 문서에 올바르게 반영되었음을 확인했다.

책의 문제는 학습 목적에 맞게 요약·변형했다. 원문의 문장을 길게 옮기지 않고, 프로그래머스에서 바로 사용할 수 있는 함수 형태로 보완했다.

---

## 오늘의 학습 일정

권장 시간은 약 **5시간**이다.

| 구간 | 내용 | 권장 시간 |
|---|---|---:|
| 복습 | 2일차 빈도 배열, 해시 충돌, 평균 복잡도 | 20분 |
| 1부 | `unordered_set`, `unordered_map` | 60분 |
| 해시 연습 | H1~H9 | 65분 |
| 휴식 | 막힌 문제의 입력 제한 다시 읽기 | 15분 |
| 2부 | `stack`, `queue`, `priority_queue` | 65분 |
| 어댑터 연습 | S1~S5, Q1~Q5, P1~P4 | 85분 |
| 책 기반 | B1~B5 | 35분 |
| 마무리 | 최종 테스트와 오답 노트 | 15분 |

---

# 1부 - STL 해시 컨테이너

## 1. 집합과 맵의 차이

| 컨테이너 | 저장 형태 | 대표 목적 |
|---|---|---|
| `unordered_set<Key>` | 키만 저장 | 존재 여부, 중복 제거 |
| `unordered_map<Key, Value>` | 키와 값 저장 | 빈도, 이름별 점수, ID별 정보 |

```text
unordered_set: {10, 20, 30}
unordered_map: {"apple": 3, "banana": 2}
```

두 컨테이너 모두 해시 테이블을 기반으로 하므로 삽입·탐색·삭제가 평균적으로 `O(1)`, 최악에는 `O(N)`이다.

---

## 2. `unordered_set` 기본 사용법

```cpp
#include <unordered_set>
using namespace std;

unordered_set<int> numbers;

numbers.insert(10);
numbers.insert(20);
numbers.insert(10); // 중복이므로 원소 수는 증가하지 않음

if (numbers.find(20) != numbers.end()) {
    // 20이 존재함
}

numbers.erase(10);
int count = static_cast<int>(numbers.size());
bool empty = numbers.empty();
```

### 자주 사용하는 API

| 코드 | 의미 | 평균 복잡도 |
|---|---|---:|
| `insert(value)` | 삽입 | `O(1)` |
| `find(value)` | 반복자 반환, 없으면 `end()` | `O(1)` |
| `count(value)` | 집합에서는 0 또는 1 | `O(1)` |
| `erase(value)` | 삭제 | `O(1)` |
| `size()` | 원소 수 | `O(1)` |
| `clear()` | 전체 삭제 | `O(N)` |

프로그래머스의 C++ 표준 버전 호환성을 생각하면 `contains()`보다 `find()` 또는 `count()`를 익혀 두는 편이 안전하다.

### 삽입 성공 여부 확인

`insert()`의 반환값에서 `.second`를 보면 실제로 새 원소가 들어갔는지 알 수 있다.

```cpp
unordered_set<int> seen;

for (int number : numbers) {
    if (!seen.insert(number).second) {
        // 이미 존재하므로 number는 중복
    }
}
```

---

## 3. `unordered_map` 기본 사용법

```cpp
#include <string>
#include <unordered_map>
using namespace std;

unordered_map<string, int> frequency;

frequency["apple"]++;
frequency["banana"] += 2;

if (frequency.find("apple") != frequency.end()) {
    int count = frequency["apple"];
}

frequency.erase("banana");
```

### `operator[]`의 중요한 성질

존재하지 않는 키에 `[]`를 사용하면 기본값을 가진 원소가 새로 생긴다.

```cpp
unordered_map<string, int> score;

int value = score["kim"];
// "kim"이 없었다면 {"kim", 0}이 삽입됨
```

빈도 계산에는 편리하다.

```cpp
for (const string& word : words) {
    frequency[word]++;
}
```

존재 여부만 확인할 때는 새 원소를 만들지 않는 `find()`를 사용한다.

```cpp
auto it = score.find("kim");

if (it != score.end()) {
    cout << it->second;
}
```

---

## 4. 해시 컨테이너 순회

```cpp
unordered_map<string, int> frequency = {
    {"apple", 3},
    {"banana", 2}
};

for (const auto& entry : frequency) {
    cout << entry.first << ' ' << entry.second << '\n';
}
```

- `entry.first`: 키
- `entry.second`: 값

주의할 점은 **출력 순서가 정렬되어 있지 않다**는 것이다. 오름차순 출력이 필요하면 키를 `vector`에 옮겨 정렬하거나 처음부터 `map`, `set`을 고려한다.

---

## 5. 빈도 배열과 `unordered_map` 선택

| 입력 조건 | 선택 |
|---|---|
| 소문자 26개 | `array<int, 26>` 또는 `vector<int>(26)` |
| 정수 0~100 | `vector<int>(101)` |
| 정수 범위가 매우 큼 | `unordered_map<int, int>` |
| 문자열별 빈도 | `unordered_map<string, int>` |
| 문자열 중복 확인 | `unordered_set<string>` |

해시가 강력하다고 모든 문제에 해시를 쓰는 것은 아니다. 작은 연속 범위에서는 빈도 배열이 더 단순하고 메모리 배치도 효율적이다.

---

## 6. `reserve()`와 적재율

원소 수를 어느 정도 예상할 수 있으면 버킷을 미리 확보해 재해싱 횟수를 줄일 수 있다.

```cpp
unordered_set<int> seen;
seen.reserve(numbers.size());

unordered_map<string, int> frequency;
frequency.reserve(words.size());
```

관련 API:

```cpp
container.load_factor();      // 현재 적재율
container.max_load_factor();  // 최대 적재율 기준
container.bucket_count();     // 버킷 수
```

입문 문제에서는 대부분 기본 설정으로 충분하다. `reserve()`는 대량 삽입이 예상될 때 선택적으로 사용한다.

---

## 7. 사용자 정의 키 해시

`int`, `string` 같은 기본 자료형은 표준 해시가 준비되어 있다. `pair<int, int>` 같은 사용자 정의 키에는 해시 함수를 제공해야 할 수 있다.

```cpp
#include <functional>
#include <unordered_set>
#include <utility>
using namespace std;

struct PairHash {
    size_t operator()(const pair<int, int>& value) const noexcept {
        size_t firstHash = hash<int>{}(value.first);
        size_t secondHash = hash<int>{}(value.second);
        return firstHash ^ (secondHash << 1);
    }
};

unordered_set<pair<int, int>, PairHash> visited;
visited.insert({2, 3});
```

같은 키로 판단되는 두 객체는 반드시 같은 해시값을 만들어야 한다. 사용자 정의 구조체를 키로 쓸 때는 동등 비교의 기준과 해시의 기준을 일치시킨다.

---

# 2부 - Stack, Queue, Priority Queue

## 8. 컨테이너 어댑터란?

책에서는 `stack`, `queue`, `priority_queue`를 **컨테이너 어댑터**로 설명한다. 내부 컨테이너를 사용하지만 목적에 필요한 제한된 인터페이스만 제공한다.

```text
stack          -> 마지막 원소만 확인·제거
queue          -> 맨 앞 원소를 확인·제거, 뒤에 삽입
priority_queue -> 우선순위가 가장 높은 원소를 확인·제거
```

일반적인 `vector`처럼 임의 위치에 접근하거나 반복자로 전체를 순회하는 구조가 아니다. 제한된 인터페이스가 자료구조의 규칙을 지켜 준다.

---

## 9. `deque`를 먼저 알아두기

`deque`는 양쪽 끝에서 삽입과 삭제를 지원한다.

```cpp
#include <deque>
using namespace std;

deque<int> values;

values.push_front(1);
values.push_back(2);
values.pop_front();
values.pop_back();
```

`stack`과 `queue`는 기본 내부 컨테이너로 `deque`를 사용한다. 코딩 테스트에서 양쪽 끝을 모두 직접 다뤄야 할 때는 `deque`를 사용한다.

---

## 10. `stack` - LIFO

LIFO는 Last In, First Out이다. 마지막에 넣은 원소가 가장 먼저 나온다.

```text
push 10 -> [10]
push 20 -> [10, 20]
push 30 -> [10, 20, 30]
pop     -> [10, 20]
```

```cpp
#include <stack>
using namespace std;

stack<int> values;

values.push(10);
values.push(20);

int topValue = values.top();
values.pop();
```

### API

| 코드 | 의미 |
|---|---|
| `push(value)` | 맨 위에 삽입 |
| `top()` | 맨 위 원소 확인 |
| `pop()` | 맨 위 원소 제거 |
| `empty()` | 비었는지 확인 |
| `size()` | 원소 수 |

`pop()`은 제거한 값을 반환하지 않는다. `top()`으로 먼저 읽고 `pop()`을 호출한다.

### 대표 문제 신호

- 괄호 짝 검사
- 최근 작업 취소
- 뒤로 가기
- 인접한 원소 제거
- 다음 큰 수
- 문자열 폭발

---

## 11. 올바른 괄호 템플릿

```cpp
#include <stack>
#include <string>
using namespace std;

bool solution(string text) {
    stack<char> opened;

    for (char ch : text) {
        if (ch == '(') {
            opened.push(ch);
        } else {
            if (opened.empty()) {
                return false;
            }

            opened.pop();
        }
    }

    return opened.empty();
}
```

닫는 괄호가 나왔을 때 스택이 비어 있는지 반드시 먼저 확인한다.

---

## 12. `queue` - FIFO

FIFO는 First In, First Out이다. 먼저 들어온 원소가 먼저 나온다.

```text
push 10 -> [10]
push 20 -> [10, 20]
push 30 -> [10, 20, 30]
pop     -> [20, 30]
```

```cpp
#include <queue>
using namespace std;

queue<int> waiting;

waiting.push(10);
waiting.push(20);

int first = waiting.front();
int last = waiting.back();
waiting.pop();
```

### API

| 코드 | 의미 |
|---|---|
| `push(value)` | 뒤에 삽입 |
| `front()` | 맨 앞 원소 확인 |
| `back()` | 맨 뒤 원소 확인 |
| `pop()` | 맨 앞 원소 제거 |
| `empty()` | 비었는지 확인 |
| `size()` | 원소 수 |

### 대표 문제 신호

- 요청이 들어온 순서대로 처리
- 대기열
- 프린터 큐
- 기능 배포 묶음
- 너비 우선 탐색 BFS
- 시간 순서 시뮬레이션

---

## 13. 큐 안전 처리 템플릿

```cpp
while (!waiting.empty()) {
    int current = waiting.front();
    waiting.pop();

    // current 처리
}
```

`front()`, `back()`, `top()`은 컨테이너가 비어 있을 때 호출하면 안 된다.

---

## 14. `priority_queue` - 우선순위가 높은 원소부터

기본 `priority_queue<int>`는 가장 큰 값이 먼저 나오는 최대 힙이다.

```cpp
#include <queue>
using namespace std;

priority_queue<int> maximums;

maximums.push(10);
maximums.push(30);
maximums.push(20);

cout << maximums.top(); // 30
```

### 최소 힙

```cpp
#include <functional>
#include <queue>
#include <vector>
using namespace std;

priority_queue<int, vector<int>, greater<int>> minimums;

minimums.push(10);
minimums.push(30);
minimums.push(20);

cout << minimums.top(); // 10
```

### 복잡도

| 연산 | 복잡도 |
|---|---:|
| `top()` | `O(1)` |
| `push()` | `O(log N)` |
| `pop()` | `O(log N)` |

### 대표 문제 신호

- 항상 최댓값 또는 최솟값부터 처리
- 가장 작은 두 값을 반복해서 결합
- 우선순위가 높은 작업부터 실행
- 상위 K개 유지

---

## 15. 세 컨테이너 선택표

| 필요한 규칙 | 컨테이너 |
|---|---|
| 가장 최근 원소부터 | `stack` |
| 가장 먼저 들어온 원소부터 | `queue` |
| 최댓값부터 | 기본 `priority_queue` |
| 최솟값부터 | `priority_queue<..., greater<...>>` |
| 양쪽 끝을 직접 조작 | `deque` |

문제를 읽고 “무엇이 다음에 처리되는가?”를 한 문장으로 적으면 선택이 쉬워진다.

---

# 3부 - 연습문제 28개

## 문제 풀이 전 체크

1. 저장할 정보는 키뿐인가, 키와 값인가?
2. 처리 순서는 최근순, 입력순, 우선순위순 중 무엇인가?
3. 빈 컨테이너에서 `top()`이나 `front()`를 호출할 가능성은 없는가?
4. 해시 컨테이너의 출력 순서가 필요한가?
5. 시간 복잡도가 입력 제한을 만족하는가?

---

## A. 해시 실전 H1~H9

### H1. 중복을 제거한 개수

정수 배열에서 서로 다른 값의 개수를 반환하라.

```cpp
#include <unordered_set>
#include <vector>
using namespace std;

int solution(vector<int> numbers) {
    unordered_set<int> uniqueNumbers(numbers.begin(), numbers.end());
    return static_cast<int>(uniqueNumbers.size());
}
```

---

### H2. 가장 먼저 발견되는 중복

배열을 왼쪽부터 읽을 때, 두 번째 등장 시점이 가장 빠른 값을 반환하라. 중복이 없으면 `-1`을 반환한다.

```cpp
int solution(vector<int> numbers) {
    unordered_set<int> seen;

    for (int number : numbers) {
        if (!seen.insert(number).second) {
            return number;
        }
    }

    return -1;
}
```

---

### H3. 문자열 빈도

문자열 배열에서 각 문자열의 등장 횟수를 계산하라.

```cpp
unordered_map<string, int> solution(vector<string> words) {
    unordered_map<string, int> frequency;

    for (const string& word : words) {
        frequency[word]++;
    }

    return frequency;
}
```

---

### H4. 목표 합을 만드는 두 수

정수 배열에서 서로 다른 두 원소의 합이 `target`이 되는지 판별하라.

<details>
<summary>정답 확인</summary>

```cpp
bool solution(vector<int> numbers, int target) {
    unordered_set<int> seen;

    for (int number : numbers) {
        if (seen.count(target - number) > 0) {
            return true;
        }

        seen.insert(number);
    }

    return false;
}
```

현재 값을 넣기 전에 필요한 짝을 먼저 찾으면 같은 원소를 두 번 사용하는 실수를 피할 수 있다.

</details>

---

### H5. 첫 번째로 한 번만 등장한 문자

문자열에서 전체적으로 한 번만 등장하며 위치가 가장 앞선 문자를 한 글자 문자열로 반환하라. 없으면 빈 문자열을 반환하라.

요구사항: 문자 범위가 제한되지 않았다고 가정하고 `unordered_map<char, int>`을 사용한다.

---

### H6. 완주하지 못한 선수

참가자 이름 목록과 완주자 이름 목록이 주어진다. 단 한 명의 미완주자를 반환하라. 동명이인이 있을 수 있으므로 집합이 아니라 빈도 맵을 사용한다.

---

### H7. 의상 조합 수

각 의상이 `(이름, 종류)`로 주어질 때 하루에 최소 한 가지를 착용하는 조합 수를 구하라.

힌트: 종류별 개수가 `count`라면 안 입는 선택을 포함해 `count + 1`을 곱하고, 아무것도 입지 않는 경우 1을 뺀다.

---

### H8. 신고 결과

각 사용자가 신고한 대상을 중복 없이 저장하고, 일정 횟수 이상 신고된 사용자를 정지한 뒤 신고자별 알림 횟수를 계산하라.

생각할 자료구조:

- 신고 중복 제거: 사용자별 `unordered_set<string>`
- 피신고 횟수: `unordered_map<string, int>`
- 최종 알림 수: `unordered_map<string, int>`

---

### H9. 좌표 방문 확인

격자에서 방문한 `(x, y)` 좌표를 중복 없이 저장하라. `pair<int, int>`와 `PairHash`를 사용해 방문한 칸 수를 반환한다.

---

## B. 스택 문제 S1~S5

### S1. 올바른 괄호

괄호 문자열이 올바른지 판별하라. 앞의 템플릿을 보지 않고 다시 작성한다.

### S2. 같은 숫자는 싫어

연속해서 나타나는 같은 숫자를 하나만 남겨 반환하라.

<details>
<summary>정답 확인</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    vector<int> answer;

    for (int number : numbers) {
        if (answer.empty() || answer.back() != number) {
            answer.push_back(number);
        }
    }

    return answer;
}
```

이 문제는 스택 패턴이지만 반환형이 `vector`이므로 `vector`의 뒤쪽을 스택처럼 사용하면 결과를 다시 옮길 필요가 없다.

</details>

### S3. 짝지어 제거하기

문자열을 왼쪽부터 읽으며 같은 문자가 인접하면 두 문자를 제거한다. 모든 문자를 제거할 수 있는지 판별하라.

```cpp
int solution(string text) {
    stack<char> remaining;

    for (char ch : text) {
        if (!remaining.empty() && remaining.top() == ch) {
            remaining.pop();
        } else {
            remaining.push(ch);
        }
    }

    return remaining.empty() ? 1 : 0;
}
```

### S4. 브라우저 뒤로 가기

`VISIT page`, `BACK` 명령을 처리하라. 방문한 페이지를 스택에 쌓고, `BACK`은 현재 페이지를 제거한 뒤 이전 페이지를 보여 준다. 첫 페이지에서는 더 뒤로 가지 않는다.

### S5. 다음 큰 수

각 원소의 오른쪽에서 처음 만나는 더 큰 값을 반환하라. 없으면 `-1`이다. 인덱스를 저장하는 단조 스택으로 `O(N)`에 해결한다.

힌트:

```cpp
while (!indices.empty() && numbers[indices.top()] < numbers[i]) {
    answer[indices.top()] = numbers[i];
    indices.pop();
}
```

---

## C. 큐 문제 Q1~Q5

### Q1. 명령어 큐

`PUSH x`, `POP`, `FRONT`, `BACK`, `SIZE`, `EMPTY` 명령을 처리하라. 빈 큐에서 `POP`, `FRONT`, `BACK` 요청이 오면 `-1`을 기록한다.

### Q2. 기능 개발

각 기능의 현재 진도와 하루 작업량이 주어진다. 앞 기능이 완료되어야 뒤 기능을 배포할 수 있을 때, 배포일마다 배포되는 기능 수를 반환하라.

먼저 각 기능의 완료 날짜를 계산한다.

```cpp
int days = (100 - progress + speed - 1) / speed;
```

그다음 앞의 완료 날짜를 기준으로 묶는다.

### Q3. 프로세스 실행 순서

대기 큐의 맨 앞 프로세스보다 우선순위가 높은 프로세스가 뒤에 있으면 맨 뒤로 보낸다. 특정 위치의 프로세스가 몇 번째로 실행되는지 구하라.

추천 구조:

- `queue<pair<int, int>>`: `(원래 위치, 우선순위)`
- `priority_queue<int>`: 현재 남은 최대 우선순위

### Q4. 다리를 지나는 트럭

다리 길이, 최대 무게, 트럭 무게가 주어진다. 트럭이 순서대로 다리를 건너는 최소 시간을 구하라. 큐에는 `(트럭 무게, 나갈 시간)`을 저장한다.

### Q5. BFS 미리 보기

인접 리스트 그래프와 시작 정점이 주어질 때 BFS 방문 순서를 반환하라.

```cpp
vector<int> bfs(const vector<vector<int>>& graph, int start) {
    vector<bool> visited(graph.size(), false);
    vector<int> order;
    queue<int> waiting;

    visited[start] = true;
    waiting.push(start);

    while (!waiting.empty()) {
        int current = waiting.front();
        waiting.pop();
        order.push_back(current);

        for (int next : graph[current]) {
            if (!visited[next]) {
                visited[next] = true;
                waiting.push(next);
            }
        }
    }

    return order;
}
```

중복 삽입을 막으려면 큐에서 꺼낼 때가 아니라 **큐에 넣을 때 방문 처리**한다.

---

## D. 우선순위 큐 문제 P1~P4

### P1. K번째로 큰 수

정수 배열에서 K번째로 큰 수를 구하라.

- 방법 1: 최대 힙에 모두 넣고 `K - 1`번 제거
- 방법 2: 크기 K인 최소 힙을 유지

입력이 매우 클 때는 방법 2가 `O(N log K)`라서 유리하다.

### P2. 더 맵게

가장 덜 매운 두 음식을 반복해 섞어 모든 음식의 지수가 기준 이상이 되도록 한다. 섞는 횟수를 구하고 불가능하면 `-1`을 반환한다.

<details>
<summary>정답 확인</summary>

```cpp
int solution(vector<int> values, int target) {
    priority_queue<long long, vector<long long>, greater<long long>> minimums(
        values.begin(), values.end()
    );

    int count = 0;

    while (!minimums.empty() && minimums.top() < target) {
        if (minimums.size() < 2) {
            return -1;
        }

        long long first = minimums.top();
        minimums.pop();
        long long second = minimums.top();
        minimums.pop();

        long long mixed = first + second * 2;
        minimums.push(mixed);
        count++;
    }

    return count;
}
```

문제의 최댓값에 따라 계산 과정과 힙의 자료형을 `long long`으로 바꾸는 것이 더 안전할 수 있다.

</details>

### P3. 가장 작은 두 묶음 합치기

여러 카드 묶음의 크기가 주어진다. 두 묶음을 합칠 때 두 크기의 합만큼 비용이 든다. 모든 묶음을 하나로 만들 때 최소 비용을 구하라.

힌트: 항상 가장 작은 두 묶음을 먼저 합친다.

### P4. 상위 K개 실시간 유지

숫자가 하나씩 들어올 때 지금까지의 값 중 가장 큰 K개만 유지하라. 크기 K의 최소 힙을 사용하고, 새 값이 힙의 최솟값보다 클 때 교체한다.

---

## E. 책 기반 문제 B1~B5

### B1. STL 해시 컨테이너 연산 - 책 연습문제 16 변형

초기 데이터가 `{1, 2, 3, 4, 5}`일 때 다음 연산을 수행하고 결과를 설명하라.

1. `unordered_set<int>`에 `2`, `100` 삽입
2. `4`, `100`, `2` 탐색
3. `2` 삭제
4. `unordered_map<int, int>`에 제곱값 저장
5. 키 `3`, `20` 탐색

핵심 확인:

- 집합의 중복 삽입은 원소 수를 늘리지 않는다.
- `unordered_map[key]`는 없던 키를 만들 수 있다.
- 순회 출력 순서를 예상하면 안 된다.

---

### B2. 적재율과 재해싱 관찰

정수 1,000개를 `unordered_set`에 넣으면서 다음 값을 삽입 전후로 출력하라.

```cpp
size()
bucket_count()
load_factor()
```

그다음 `reserve(1000)`을 먼저 호출한 경우와 비교하라. 버킷 수가 바뀌는 순간이 재해싱이 발생한 시점이다.

---

### B3. 사용자 정의 구조체 해시 - 책의 자동차 예제 변형

다음 구조체에서 `model`, `brand`, `id`가 모두 같으면 같은 자동차로 판단한다.

```cpp
struct Car {
    string model;
    string brand;
    int id;
};
```

`CarHash`와 `operator==`를 작성하고 `unordered_set<Car, CarHash>`에 저장하라. 동등한 두 객체가 서로 다른 해시값을 만들지 않게 모든 필드를 같은 기준으로 조합한다.

---

### B4. 컨테이너 어댑터의 반복자 제한

`stack`, `queue`, `priority_queue`가 일반 반복자를 제공하지 않는 이유를 설명하라.

<details>
<summary>정답 확인</summary>

컨테이너 어댑터는 LIFO, FIFO, 우선순위 처리라는 제한된 규칙을 보장하려고 내부 컨테이너의 일부 기능만 공개한다. 임의 위치 순회나 수정이 가능하면 이 규칙을 우회할 수 있으므로 일반 반복자를 제공하지 않는다. 전체 내용을 봐야 한다면 복사본에서 원소를 하나씩 꺼내거나, 목적에 맞는 다른 컨테이너를 선택한다.

</details>

---

### B5. 사무실 공유 프린터 - 책 실습 문제 3 변형

인쇄 요청은 `(요청 ID, 사용자 이름, 페이지 수)`로 주어지고 들어온 순서대로 처리된다.

요구사항:

1. 요청을 큐에 추가하는 `addJob()`을 작성한다.
2. 맨 앞 요청을 인쇄하고 제거하는 `processNext()`를 작성한다.
3. 큐가 비었을 때 안전하게 처리한다.
4. 페이지당 1초가 걸린다면 모든 작업이 끝나는 시간을 계산한다.
5. 추가 도전: 긴급 요청을 먼저 처리하려면 어떤 자료구조로 바꿔야 하는지 설명한다.

```cpp
struct PrintJob {
    int id;
    string user;
    int pages;
};

class Printer {
private:
    queue<PrintJob> jobs;

public:
    void addJob(const PrintJob& job) {
        jobs.push(job);
    }

    bool processNext(int& elapsedSeconds) {
        if (jobs.empty()) {
            return false;
        }

        PrintJob current = jobs.front();
        jobs.pop();
        elapsedSeconds += current.pages;
        return true;
    }
};
```

긴급도 순으로 처리하려면 비교 규칙을 정의한 `priority_queue`를 고려한다.

---

# 4부 - 실수 방지와 선택 훈련

## 16. 자주 하는 실수

### `pop()`이 값을 반환한다고 생각함

```cpp
int value = values.top();
values.pop();
```

### 빈 컨테이너에서 원소 확인

```cpp
if (!values.empty()) {
    int value = values.top();
}
```

### `unordered_map`의 `[]`로 존재 여부 확인

```cpp
if (score.find(name) != score.end()) {
    // 새 원소를 만들지 않음
}
```

### 해시 컨테이너의 순서를 신뢰

실행 환경이나 재해싱에 따라 순서가 달라질 수 있다. 정렬된 결과가 필요하면 별도로 정렬한다.

### 최소 힙 선언을 반대로 작성

```cpp
priority_queue<int, vector<int>, greater<int>> minimums;
```

### 큐 시뮬레이션에서 시간을 한 칸씩만 증가

입력 범위가 크면 다음 사건이 발생하는 시간으로 바로 이동할 수 있는지 검토한다.

### BFS에서 방문 처리가 늦음

큐에 넣을 때 방문 처리해야 같은 정점이 여러 번 들어가는 것을 막을 수 있다.

---

## 17. 최종 테스트

자료를 보지 않고 답한다.

1. `unordered_set`과 `unordered_map`의 차이는?
2. `insert(value).second`는 무엇을 의미하는가?
3. 존재하지 않는 맵 키에 `[]`를 사용하면 어떻게 되는가?
4. 해시 컨테이너 순회 결과가 정렬되지 않는 이유는?
5. 해시 연산의 평균과 최악 복잡도는?
6. `reserve()`를 사용하는 목적은?
7. 사용자 정의 키에서 동등 비교와 해시의 기준이 일치해야 하는 이유는?
8. `stack`, `queue`, `priority_queue`의 처리 순서는 각각 무엇인가?
9. 컨테이너 어댑터가 반복자를 제공하지 않는 이유는?
10. `pop()`으로 제거한 값을 받으려면 어떻게 해야 하는가?
11. 기본 `priority_queue<int>`의 `top()`에는 어떤 값이 오는가?
12. 최소 힙 선언을 작성할 수 있는가?
13. 최소 힙의 `push`, `pop` 복잡도는?
14. BFS에서 방문 처리는 언제 하는가?
15. 양쪽 끝을 직접 조작하려면 어떤 컨테이너를 쓰는가?
16. 문자열 중복 확인과 문자열별 빈도 계산에 각각 무엇을 쓰는가?
17. 동명이인이 있는 완주자 문제에서 `unordered_set`이 부족한 이유는?
18. 가장 최근 작업 취소 문제에는 무엇을 쓰는가?
19. 입력 순서대로 요청을 처리하는 문제에는 무엇을 쓰는가?
20. 항상 가장 작은 두 값을 골라야 하는 문제에는 무엇을 쓰는가?

16개 이상 정확히 설명하면 다음 날로 넘어간다.

---

## 18. 완료 체크리스트

- [ ] `unordered_set`의 삽입·탐색·삭제를 작성할 수 있다.
- [ ] `unordered_map`으로 빈도를 계산할 수 있다.
- [ ] `[]`와 `find()`의 차이를 설명할 수 있다.
- [ ] 해시 컨테이너의 순서를 신뢰하지 않는다.
- [ ] `stack`으로 괄호 문제를 풀 수 있다.
- [ ] `queue`로 FIFO 시뮬레이션을 작성할 수 있다.
- [ ] 최대 힙과 최소 힙을 모두 선언할 수 있다.
- [ ] 빈 컨테이너를 먼저 확인한다.
- [ ] BFS에서 큐에 넣을 때 방문 처리한다.
- [ ] H1~H9 중 최소 7문제를 풀었다.
- [ ] S1~S5와 Q1~Q5 중 최소 8문제를 풀었다.
- [ ] P1~P4 중 최소 3문제를 풀었다.
- [ ] B1~B5를 모두 설명하거나 구현했다.
- [ ] 틀린 문제에 반례와 복잡도를 기록했다.

---

## 19. 오답 노트 템플릿

```text
문제:
처음 선택한 자료구조:
정답에 적합한 자료구조:
처리 순서(LIFO/FIFO/우선순위):
막힌 API:
빈 컨테이너 예외를 확인했는가:
해시 키와 값:
반례:
시간 복잡도:
수정한 핵심 한 줄:
다시 풀 날짜:
```

---

## 연결 문서

- 이전: [[2일차 - 빈도 배열과 해시 테이블 원리]]
- 다음: [[4일차 - 정렬과 이분 탐색]]

> 오늘의 핵심 한 문장: **존재·빈도는 해시로, 최근순은 스택으로, 입력순은 큐로, 최댓값·최솟값 우선 처리는 우선순위 큐로 해결한다.**
