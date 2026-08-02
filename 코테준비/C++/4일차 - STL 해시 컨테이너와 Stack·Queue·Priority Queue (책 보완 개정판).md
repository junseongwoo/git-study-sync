---
tags:
  - 코딩테스트
  - C++
  - unordered_map
  - unordered_set
  - stack
  - queue
  - priority_queue
  - container-adapter
date: 2026-08-02
day: 4
version: book-verified-revised
source:
  - Cpp코테.pdf
---

# 4일차 — STL 해시 컨테이너 + Stack·Queue·Priority Queue

기존 4일차의 `unordered_map`, `unordered_set`, `stack`, `queue` 내용을 유지하면서 책의 C++ 해시 테이블과 컨테이너 어댑터 장을 바탕으로 보완한 개정판이다.

- 1부: `unordered_set`과 `unordered_map`
- 2부: 컨테이너 어댑터와 `stack`
- 3부: `queue`와 `priority_queue`
- 4부: 책 연습문제를 재구성한 URL 매핑·프린터 대기열 실습

> 오늘의 완료 기준: 문제에서 존재 여부, 키별 값, 최근 값, 입력 순서, 우선순위 중 무엇이 필요한지 구분해 자료구조를 선택한다.

---

## 참고한 책의 범위

`Cpp코테.pdf`의 다음 내용을 코딩 테스트용으로 재구성했다.

- 1.9 컨테이너 어댑터
- 1.9.1 `std::stack`
- 1.9.2 `std::queue`
- 1.9.3 `std::priority_queue`
- 사무실 공유 프린터 대기 목록 실습
- 3.4 C++ 해시 테이블
- STL 해시 테이블 삽입·검색·삭제 실습
- 긴 URL을 짧은 URL로 매핑하는 실습

책의 실습 목표를 유지하되 프로그래머스 함수 형식과 현재 학습 수준에 맞게 문제를 다시 설계했다.

### PDF 대조 검증 기록

- 1차 검증: 컨테이너 어댑터와 C++ 해시 테이블 관련 페이지 전체를 확인했다.
- 2차 검증: Stack의 기본 기반 컨테이너와 `O(1)` 연산, Queue의 FIFO, Priority Queue의 힙 구성 비용, 어댑터의 반복자 미지원, 프린터 대기열, URL 매핑 실습을 정확한 페이지와 다시 대조했다.
- 보완 결과: 기존 노트에 없던 `priority_queue`, 부하율 API, 범위 생성자의 `O(N)` 힙 구성, 책 기반 실습 4개를 추가했다.

---

## 오늘의 학습 일정

| 구간 | 내용 | 권장 시간 |
|---|---|---:|
| 1부 | STL 해시 컨테이너 | 60분 |
| 1부 실습 | Hash 문제 | 55분 |
| 휴식 | 자리에서 일어나기 | 15분 |
| 2부 | Stack과 괄호 문제 | 45분 |
| 3부 | Queue와 Priority Queue | 55분 |
| 4부 | 책 실습 재구성 | 65분 |
| 마무리 | 종합 문제·오답 정리 | 30분 |

---

# 1부 — `unordered_set`과 `unordered_map`

## 1. `unordered_set`

값의 존재 여부나 서로 다른 값의 집합이 필요할 때 사용한다.

```cpp
#include <unordered_set>
using namespace std;

unordered_set<int> numbers;

numbers.insert(10);
numbers.insert(20);
numbers.insert(10);  // 중복이므로 새 원소가 생기지 않음
```

### 존재 여부

```cpp
if (numbers.find(10) != numbers.end()) {
    // 10이 존재함
}
```

### 삭제

```cpp
numbers.erase(10);
```

### 크기

```cpp
numbers.size();
numbers.empty();
```

### 삽입 성공 여부

`insert()`의 결과로 새로 삽입되었는지 확인할 수 있다.

```cpp
auto [it, inserted] = numbers.insert(30);

if (inserted) {
    // 30이 새로 삽입됨
}
```

이 문법은 C++17 기준이다.

---

## 2. `unordered_map`

키마다 값을 연결해 저장한다.

```cpp
#include <unordered_map>

unordered_map<string, int> score;

score["kim"] = 90;
score["lee"] = 85;
```

```text
key       value
"kim"  → 90
"lee"  → 85
```

### 빈도 계산

```cpp
unordered_map<string, int> count;

for (const string& word : words) {
    count[word]++;
}
```

존재하지 않는 키에 `[]`를 사용하면 기본값이 생성된다. `int`의 기본값은 0이므로 빈도 계산에 편리하다.

---

## 3. `[]`, `find()`, `at()`의 차이

### `[]`

```cpp
int value = count["apple"];
```

키가 없으면 `"apple" → 0` 원소를 새로 만든다.

### `find()`

```cpp
auto it = count.find("apple");

if (it != count.end()) {
    cout << it->second;
}
```

키를 새로 만들지 않고 존재 여부를 확인한다.

### `at()`

```cpp
int value = count.at("apple");
```

키가 없으면 예외를 발생시킨다. 반드시 있다고 확신할 때 사용한다.

### 선택 기준

| 목적 | 권장 방식 |
|---|---|
| 빈도 증가 | `count[key]++` |
| 존재 여부만 확인 | `find()` |
| 존재하는 키의 값 읽기 | `find()` 결과 또는 `at()` |
| 없는 키도 기본값으로 생성 | `[]` |

---

## 4. 순회

```cpp
for (const auto& [key, value] : count) {
    cout << key << ' ' << value << '\n';
}
```

`unordered_set`과 `unordered_map`의 순회 순서는 정해져 있지 않다.

```text
입력 순서 보장 안 됨
정렬 순서 보장 안 됨
```

결과를 사전순이나 숫자순으로 반환해야 한다면 키를 `vector`에 옮겨 정렬하거나 `map`, `set`을 검토한다.

---

## 5. 삽입·삭제·검색

```cpp
unordered_map<string, int> inventory;

inventory.insert({"pen", 3});
inventory["book"] = 5;

inventory.erase("pen");

auto it = inventory.find("book");
```

`insert()`는 이미 같은 키가 있으면 기존 값을 덮어쓰지 않는다.

```cpp
inventory["book"] = 10;       // 값을 10으로 변경
inventory.insert({"book", 20}); // 이미 있으면 변경 안 됨
```

---

## 6. 버킷과 부하율

3일차에서 배운 해시 테이블 내부 원리를 STL에서도 확인할 수 있다.

```cpp
unordered_map<string, int> count;

count.bucket_count();
count.load_factor();
count.max_load_factor();
count.reserve(1000);
count.rehash(2000);
```

- `reserve(n)`: 원소 약 `n`개를 저장할 공간을 미리 준비하도록 요청
- `rehash(n)`: 버킷 수가 최소 `n` 이상이 되도록 요청

일반적인 코딩 테스트에서는 기본 설정으로도 충분하다. 입력이 매우 크고 원소 수를 미리 알 때 `reserve()`를 고려할 수 있다.

---

## 7. 중복 키가 필요하다면

```cpp
unordered_multiset<int> values;
unordered_multimap<string, int> records;
```

이 컨테이너들은 같은 키를 여러 번 저장한다. 다만 등장 횟수만 필요하다면 `unordered_map<T, int>`로 직접 세는 방식이 더 이해하기 쉬운 경우가 많다.

---

## 8. 평균 시간복잡도

| 연산 | 평균 | 최악 |
|---|---:|---:|
| `insert()` | `O(1)` | `O(N)` |
| `find()` | `O(1)` | `O(N)` |
| `erase()` | `O(1)` | `O(N)` |

해시 충돌이 적고 분포가 고른 일반적인 경우 평균 `O(1)`이다.

---

# Hash 연습 문제

## H1 — 서로 다른 숫자의 개수

정수 배열에서 서로 다른 숫자의 개수를 반환한다.

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    unordered_set<int> uniqueNumbers(numbers.begin(), numbers.end());
    return uniqueNumbers.size();
}
```

</details>

## H2 — 중복이 있는가?

정수 배열에 같은 값이 두 번 이상 등장하면 `true`를 반환한다.

<details>
<summary>정답</summary>

```cpp
bool solution(vector<int> numbers) {
    unordered_set<int> seen;

    for (int number : numbers) {
        if (seen.find(number) != seen.end()) {
            return true;
        }

        seen.insert(number);
    }

    return false;
}
```

</details>

## H3 — 단어별 등장 횟수

문자열 배열에서 각 단어의 등장 횟수를 `unordered_map<string, int>`로 반환한다.

<details>
<summary>정답</summary>

```cpp
unordered_map<string, int> solution(vector<string> words) {
    unordered_map<string, int> answer;

    for (const string& word : words) {
        answer[word]++;
    }

    return answer;
}
```

</details>

## H4 — 완주하지 못한 선수

참가자 배열과 완주자 배열이 주어진다. 완주하지 못한 한 명을 반환한다. 동명이인이 있을 수 있다.

<details>
<summary>정답</summary>

```cpp
string solution(vector<string> participant, vector<string> completion) {
    unordered_map<string, int> count;

    for (const string& name : participant) count[name]++;
    for (const string& name : completion) count[name]--;

    for (const auto& [name, frequency] : count) {
        if (frequency > 0) {
            return name;
        }
    }

    return "";
}
```

</details>

## H5 — 두 배열의 공통 원소

두 정수 배열에 모두 등장하는 서로 다른 값들을 반환한다. 결과 순서는 자유롭다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> first, vector<int> second) {
    unordered_set<int> firstSet(first.begin(), first.end());
    unordered_set<int> common;

    for (int number : second) {
        if (firstSet.find(number) != firstSet.end()) {
            common.insert(number);
        }
    }

    return vector<int>(common.begin(), common.end());
}
```

결과 순서를 정렬해야 한다면 반환하기 전에 `sort()`를 적용한다.

</details>

## H6 — 재고 요청 처리

상품 이름 배열 `inventory`에는 보유 중인 상품이 중복되어 들어 있다. 요청 배열 `request`의 모든 상품을 수량만큼 제공할 수 있으면 `true`를 반환한다.

<details>
<summary>정답</summary>

```cpp
bool solution(vector<string> inventory, vector<string> request) {
    unordered_map<string, int> count;

    for (const string& item : inventory) {
        count[item]++;
    }

    for (const string& item : request) {
        count[item]--;

        if (count[item] < 0) {
            return false;
        }
    }

    return true;
}
```

</details>

## H7 — 첫 번째로 두 번 등장한 단어

문자열 배열을 왼쪽부터 확인할 때 처음으로 등장 횟수가 2가 되는 단어를 반환한다. 없으면 빈 문자열을 반환한다.

<details>
<summary>정답</summary>

```cpp
string solution(vector<string> words) {
    unordered_map<string, int> count;

    for (const string& word : words) {
        count[word]++;

        if (count[word] == 2) {
            return word;
        }
    }

    return "";
}
```

</details>

## H8 — 전화번호 접두어

어떤 전화번호가 다른 전화번호의 접두어이면 `false`, 아니면 `true`를 반환한다.

<details>
<summary>정답</summary>

```cpp
bool solution(vector<string> phoneBook) {
    unordered_set<string> numbers(phoneBook.begin(), phoneBook.end());

    for (const string& phone : phoneBook) {
        string prefix = "";

        for (int i = 0; i < static_cast<int>(phone.size()) - 1; i++) {
            prefix += phone[i];

            if (numbers.find(prefix) != numbers.end()) {
                return false;
            }
        }
    }

    return true;
}
```

</details>

---

# 2부 — 컨테이너 어댑터와 Stack

## 9. 컨테이너 어댑터란?

컨테이너 어댑터는 기존 컨테이너를 감싸 특정한 접근 방식만 제공한다.

```text
deque 또는 vector
        ↓ 필요한 기능만 공개
stack / queue / priority_queue
```

책에서 설명하듯 어댑터의 장점은 의도를 명확하게 만들고 잘못된 위치의 원소를 조작하지 못하게 하는 것이다.

- `stack`: 맨 위만 접근
- `queue`: 맨 앞과 맨 뒤만 접근
- `priority_queue`: 우선순위가 가장 높은 값만 접근

어댑터는 전체 원소를 순회하는 반복자를 제공하지 않는다.

---

## 10. `stack`과 LIFO

마지막에 넣은 값을 먼저 꺼낸다.

```text
LIFO = Last In, First Out
```

```cpp
#include <stack>

stack<int> s;

s.push(10);
s.push(20);
s.push(30);

s.top();  // 30
s.pop();  // 30 제거
```

주요 함수:

```cpp
s.push(value);
s.top();
s.pop();
s.size();
s.empty();
```

`pop()`은 값을 반환하지 않는다.

```cpp
int value = s.top();
s.pop();
```

빈 Stack에서 `top()`이나 `pop()`을 호출하면 안 된다.

```cpp
if (!s.empty()) {
    int value = s.top();
    s.pop();
}
```

### 기반 컨테이너

기본적으로 `deque`를 사용한다. 필요하면 `vector`를 기반으로 지정할 수 있다.

```cpp
stack<int, vector<int>> s;
```

일반적인 문제에서는 기본형 `stack<int>`를 사용하면 된다.

---

## 11. Stack 문제 신호

- 가장 최근 명령 취소
- 괄호 짝 검사
- 연속된 같은 값 제거
- 뒤에서부터 처리
- 이전 상태로 돌아가기
- 가장 가까운 이전 원소

---

## 12. 올바른 괄호

```cpp
bool solution(string text) {
    stack<char> s;

    for (char ch : text) {
        if (ch == '(') {
            s.push(ch);
        } else {
            if (s.empty()) {
                return false;
            }

            s.pop();
        }
    }

    return s.empty();
}
```

실패 조건:

1. 닫는 괄호가 나왔는데 여는 괄호가 없다.
2. 입력을 모두 처리했는데 여는 괄호가 남아 있다.

---

# 3부 — Queue와 Priority Queue

## 13. `queue`와 FIFO

먼저 넣은 값을 먼저 꺼낸다.

```text
FIFO = First In, First Out
```

```cpp
#include <queue>

queue<int> q;

q.push(10);
q.push(20);
q.push(30);

q.front();  // 10
q.back();   // 30
q.pop();    // 10 제거
```

기본 처리 패턴:

```cpp
while (!q.empty()) {
    int current = q.front();
    q.pop();

    // current 처리
}
```

Queue는 기본적으로 `deque`를 기반으로 사용한다.

### Queue 문제 신호

- 접수 순서대로 처리
- 대기열
- 먼저 들어온 작업부터 실행
- 일정한 순서로 회전
- BFS에서 가까운 정점부터 탐색

---

## 14. `priority_queue`

입력 순서가 아니라 우선순위가 높은 값을 먼저 꺼낸다. 기본형은 가장 큰 값이 먼저 나오는 최대 힙이다.

```cpp
#include <queue>

priority_queue<int> pq;

pq.push(3);
pq.push(10);
pq.push(5);

pq.top();  // 10
pq.pop();
```

### 최소 힙

가장 작은 값을 먼저 꺼낸다.

```cpp
#include <functional>

priority_queue<int, vector<int>, greater<int>> pq;
```

### 시간복잡도

| 연산 | 시간복잡도 |
|---|---:|
| `top()` | `O(1)` |
| `push()` | `O(log N)` |
| `pop()` | `O(log N)` |

`priority_queue`는 전체를 완전히 정렬해 두는 것이 아니라 맨 위에 우선순위가 가장 높은 값이 오도록 힙 구조를 유지한다.

기본 기반 컨테이너는 `vector`다. 원소를 하나씩 `push()`하면 각 삽입은 `O(log N)`이지만, 범위 생성자로 여러 원소를 한 번에 받아 힙을 구성하는 작업은 `O(N)`에 수행될 수 있다.

```cpp
priority_queue<int> pq(numbers.begin(), numbers.end());
```

### 문제 신호

- 매번 최댓값 또는 최솟값을 꺼냄
- 우선순위가 높은 작업부터 처리
- 가장 작은 두 값 반복 선택
- 상위 K개 유지

---

## 15. 세 어댑터 비교

| 자료구조 | 꺼내는 기준 | 확인 함수 | 대표 문제 |
|---|---|---|---|
| `stack` | 가장 최근 입력 | `top()` | 괄호, 취소 |
| `queue` | 가장 먼저 입력 | `front()` | 대기열, BFS |
| `priority_queue` | 가장 높은 우선순위 | `top()` | 최댓값·최솟값 반복 |

세 자료구조 모두 `pop()`은 값을 반환하지 않는다.

---

# Stack·Queue·Priority Queue 연습 문제

## Q1 — 배열 역순

정수 배열을 Stack에 넣었다가 꺼내 역순 배열로 반환한다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    stack<int> s;

    for (int number : numbers) s.push(number);

    vector<int> answer;

    while (!s.empty()) {
        answer.push_back(s.top());
        s.pop();
    }

    return answer;
}
```

</details>

## Q2 — 다중 괄호 검사

`()`, `[]`, `{}`가 올바르게 짝지어졌는지 판별한다.

<details>
<summary>정답</summary>

```cpp
bool solution(string text) {
    stack<char> s;

    for (char ch : text) {
        if (ch == '(' || ch == '[' || ch == '{') {
            s.push(ch);
            continue;
        }

        if (s.empty()) return false;
        if (ch == ')' && s.top() != '(') return false;
        if (ch == ']' && s.top() != '[') return false;
        if (ch == '}' && s.top() != '{') return false;

        s.pop();
    }

    return s.empty();
}
```

</details>

## Q3 — 짝지어 제거하기

문자열에서 같은 문자 두 개가 연속으로 만나면 제거한다. 제거 후 새롭게 붙은 문자도 같으면 다시 제거한다. 모두 제거할 수 있으면 `true`를 반환한다.

<details>
<summary>정답</summary>

```cpp
bool solution(string text) {
    stack<char> s;

    for (char ch : text) {
        if (!s.empty() && s.top() == ch) {
            s.pop();
        } else {
            s.push(ch);
        }
    }

    return s.empty();
}
```

</details>

## Q4 — 실행 취소

명령 배열에서 숫자는 Stack에 넣고 `"undo"`가 나오면 최근 숫자를 제거한다. 모든 명령 처리 후 남은 숫자의 합을 반환한다. Stack이 비어 있을 때의 `undo`는 무시한다.

<details>
<summary>정답</summary>

```cpp
int solution(vector<string> commands) {
    stack<int> s;

    for (const string& command : commands) {
        if (command == "undo") {
            if (!s.empty()) s.pop();
        } else {
            s.push(stoi(command));
        }
    }

    int answer = 0;

    while (!s.empty()) {
        answer += s.top();
        s.pop();
    }

    return answer;
}
```

</details>

## Q5 — 카드 돌리기

1부터 `N`까지의 카드를 Queue에 넣는다. 맨 앞 카드를 버리고 다음 카드를 맨 뒤로 옮기는 동작을 한 장이 남을 때까지 반복한다.

<details>
<summary>정답</summary>

```cpp
int solution(int n) {
    queue<int> q;

    for (int card = 1; card <= n; card++) q.push(card);

    while (q.size() > 1) {
        q.pop();
        q.push(q.front());
        q.pop();
    }

    return q.front();
}
```

</details>

## Q6 — Queue 회전

정수 배열을 Queue에 넣고 맨 앞 원소를 맨 뒤로 옮기는 동작을 `k`번 수행한 후 배열 상태를 반환한다. 입력 배열에는 원소가 하나 이상 있다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers, int k) {
    queue<int> q;

    for (int number : numbers) q.push(number);

    k %= q.size();

    while (k-- > 0) {
        q.push(q.front());
        q.pop();
    }

    vector<int> answer;

    while (!q.empty()) {
        answer.push_back(q.front());
        q.pop();
    }

    return answer;
}
```

</details>

## Q7 — 최댓값을 차례로 꺼내기

정수 배열의 값을 `priority_queue`에 넣고 큰 값부터 꺼낸 배열을 반환한다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    priority_queue<int> pq(numbers.begin(), numbers.end());
    vector<int> answer;

    while (!pq.empty()) {
        answer.push_back(pq.top());
        pq.pop();
    }

    return answer;
}
```

</details>

## Q8 — 가장 작은 두 수의 합

정수 배열에서 가장 작은 두 값을 반환한다. 원소는 두 개 이상이다. 최소 힙을 사용한다.

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    priority_queue<int, vector<int>, greater<int>> pq(
        numbers.begin(), numbers.end()
    );

    int first = pq.top();
    pq.pop();
    int second = pq.top();

    return first + second;
}
```

</details>

## Q9 — 상위 K개

정수 배열에서 가장 큰 `k`개 값을 큰 순서대로 반환한다. `k`는 배열 크기 이하이다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers, int k) {
    priority_queue<int> pq(numbers.begin(), numbers.end());
    vector<int> answer;

    while (k-- > 0) {
        answer.push_back(pq.top());
        pq.pop();
    }

    return answer;
}
```

</details>

---

# 4부 — 책 연습문제 재구성

## BOOK-STL1 — 해시 컨테이너 기능 확인

책의 STL 해시 테이블 실습을 다음 요구사항으로 재구성한다.

1. `unordered_set<int>`에 숫자를 삽입한다.
2. 중복 삽입 후 크기가 변하지 않는지 확인한다.
3. `find()`로 존재 여부를 확인한다.
4. `erase()` 후 다시 검색한다.
5. `unordered_map<int, int>`에 숫자와 제곱값을 저장한다.
6. 존재하지 않는 키에 `[]`를 사용했을 때 크기가 변하는지 확인한다.

이 문제는 `main()`을 포함한 실험 코드로 직접 작성하고 결과를 오답 노트에 기록한다.

---

## BOOK-STL2 — 단축 URL 서비스

긴 URL을 짧은 코드로 변환하고, 짧은 코드로 원래 URL을 복원하는 클래스를 만든다.

요구사항:

- 같은 긴 URL을 다시 입력하면 기존 짧은 코드를 반환한다.
- 존재하지 않는 짧은 코드를 복원하면 빈 문자열을 반환한다.
- 평균 `O(1)` 검색을 위해 양방향 해시 맵을 사용한다.

<details>
<summary>정답</summary>

```cpp
#include <string>
#include <unordered_map>
using namespace std;

class UrlShortener {
private:
    unordered_map<string, string> longToShort;
    unordered_map<string, string> shortToLong;
    int nextId = 1;

public:
    string shorten(const string& longUrl) {
        auto it = longToShort.find(longUrl);

        if (it != longToShort.end()) {
            return it->second;
        }

        string shortCode = "u" + to_string(nextId++);
        longToShort[longUrl] = shortCode;
        shortToLong[shortCode] = longUrl;
        return shortCode;
    }

    string restore(const string& shortCode) const {
        auto it = shortToLong.find(shortCode);

        if (it == shortToLong.end()) {
            return "";
        }

        return it->second;
    }
};
```

실제 서비스에서는 예측하기 어려운 코드 생성, 영구 저장소, 동시성, 충돌 처리 등이 추가로 필요하다. 위 코드는 해시 매핑 연습용이다.

</details>

---

## BOOK-Q1 — 공유 프린터 대기열

책의 프린터 대기열 실습을 단순화해 구현한다.

각 인쇄 작업은 작업 번호, 사용자 이름, 페이지 수를 가진다. 요청된 순서대로 인쇄하며 처리된 작업 번호 배열을 반환한다.

```cpp
struct PrintJob {
    int id;
    string user;
    int pages;
};
```

<details>
<summary>정답</summary>

```cpp
struct PrintJob {
    int id;
    string user;
    int pages;
};

vector<int> solution(vector<PrintJob> jobs) {
    queue<PrintJob> printer;

    for (const PrintJob& job : jobs) {
        printer.push(job);
    }

    vector<int> answer;

    while (!printer.empty()) {
        PrintJob current = printer.front();
        printer.pop();
        answer.push_back(current.id);
    }

    return answer;
}
```

</details>

---

## BOOK-Q2 — 긴급 인쇄 작업

일반 프린터는 FIFO지만 긴급도 값이 큰 작업을 먼저 처리해야 한다. 모든 작업의 긴급도는 서로 다르다고 가정하고 처리되는 작업 ID 순서를 반환한다.

```cpp
struct PrintJob {
    int id;
    int priority;
};
```

<details>
<summary>정답</summary>

```cpp
struct PrintJob {
    int id;
    int priority;
};

struct CompareJob {
    bool operator()(const PrintJob& a, const PrintJob& b) const {
        return a.priority < b.priority;
    }
};

vector<int> solution(vector<PrintJob> jobs) {
    priority_queue<PrintJob, vector<PrintJob>, CompareJob> printer;

    for (const PrintJob& job : jobs) {
        printer.push(job);
    }

    vector<int> answer;

    while (!printer.empty()) {
        answer.push_back(printer.top().id);
        printer.pop();
    }

    return answer;
}
```

</details>

---

# 종합 문제

## 종합 1 — 고유 작업 대기열

작업 이름이 순서대로 들어온다. 이미 Queue에 대기 중인 작업은 다시 추가하지 않는다. 작업을 처리해 Queue에서 빠지면 같은 이름이 나중에 다시 대기할 수 있다.

필요한 자료구조:

- 대기 순서: `queue<string>`
- 현재 대기 여부: `unordered_set<string>`

이 문제는 정답 없이 직접 상태 변화를 설계한다.

## 종합 2 — 명령별 처리 횟수

Queue에서 명령을 입력 순서대로 처리하고 명령 이름별 처리 횟수를 `unordered_map`으로 반환한다.

<details>
<summary>정답</summary>

```cpp
unordered_map<string, int> solution(vector<string> commands) {
    queue<string> q;

    for (const string& command : commands) q.push(command);

    unordered_map<string, int> answer;

    while (!q.empty()) {
        answer[q.front()]++;
        q.pop();
    }

    return answer;
}
```

</details>

## 종합 3 — 최근 검색어 취소

검색어는 Stack에 저장한다. `"undo"`가 나오면 최근 검색을 제거한다. 최종 검색 기록을 오래된 순서부터 반환한다. 같은 검색어가 여러 번 들어갈 수 있다.

## 종합 4 — 사용자별 최고 우선순위

사용자 이름과 작업 우선순위 쌍이 주어진다. 사용자별 가장 높은 우선순위를 해시 맵에 저장하고, 전체 사용자 중 가장 높은 값들을 Priority Queue로 처리한다.

이 문제는 자료형과 반환 형식을 직접 설계한다.

---

# 추가 훈련 — 정답 없이 풀기

## 추가 1 — 회원별 최고 점수

이름과 점수 기록에서 회원별 최고 점수만 저장한다.

## 추가 2 — 공통 문자열

두 문자열 배열에 모두 존재하는 서로 다른 문자열 개수를 반환한다.

## 추가 3 — 최소값 K번 꺼내기

정수 배열에서 가장 작은 값을 `k`번 차례대로 꺼내 배열로 반환한다.

## 추가 4 — 괄호 제거 횟수

괄호 문자열을 올바르게 만들기 위해 제거해야 하는 최소 괄호 수를 계산한다.

## 추가 5 — 작업 시간 제한

Queue의 앞 작업부터 처리할 때 누적 시간이 `limit`을 넘지 않는 최대 작업 수를 반환한다.

## 추가 6 — 자료구조 선택

다음 상황마다 `unordered_set`, `unordered_map`, `stack`, `queue`, `priority_queue` 중 하나를 선택하고 이유를 적는다.

- 이미 본 ID 확인
- 이름별 횟수
- 최근 명령 취소
- 접수 순서 처리
- 매번 가장 작은 값 처리

---

# 자주 하는 실수

## Hash

- `unordered_map`의 순회 순서를 믿는다.
- 존재 여부만 확인하면서 `map[key]`를 사용해 키를 생성한다.
- 등장 횟수가 필요한데 `unordered_set`을 사용한다.
- `insert()`가 기존 값을 덮어쓴다고 착각한다.
- 평균 `O(1)`을 항상 보장되는 `O(1)`로 착각한다.

## Stack·Queue·Priority Queue

- 빈 자료구조에서 `top()` 또는 `front()`를 호출한다.
- `pop()`이 값을 반환한다고 착각한다.
- FIFO 문제에 Stack을 사용한다.
- 입력 순서가 중요한데 Priority Queue를 사용한다.
- 최소 힙의 `greater<int>` 템플릿 인자를 틀린다.
- 어댑터를 범위 기반 반복문으로 순회하려 한다.

---

# 자료구조 선택 훈련

| 필요한 동작 | 선택 |
|---|---|
| 값의 존재 여부 | `unordered_set` |
| 키마다 값 저장 | `unordered_map` |
| 가장 최근 값부터 | `stack` |
| 가장 먼저 들어온 값부터 | `queue` |
| 우선순위가 가장 높은 값부터 | `priority_queue` |

판단 순서:

```text
1. 존재만 필요한가, 키별 값이 필요한가?
2. 중복을 보존해야 하는가?
3. 어떤 순서로 꺼내야 하는가?
4. 정렬된 전체 순서가 필요한가?
5. 평균 O(1) 검색이 필요한가?
```

---

# 오늘의 최종 테스트

- [ ] `find()`와 `[]`의 차이를 설명한다.
- [ ] `unordered_set`과 `unordered_map`을 직접 선언한다.
- [ ] 해시 컨테이너의 순회 순서가 보장되지 않음을 안다.
- [ ] LIFO와 FIFO를 설명한다.
- [ ] 세 어댑터의 확인 함수를 구분한다.
- [ ] 최소 힙 선언을 직접 작성한다.
- [ ] 다중 괄호 문제를 Stack으로 푼다.
- [ ] URL 매핑 실습을 두 개의 해시 맵으로 구현한다.
- [ ] 프린터 대기열을 Queue로 구현한다.
- [ ] 긴급 프린터를 Priority Queue로 구현한다.

---

# 복습 체크리스트

## STL Hash

- [ ] 존재 확인에는 `find()`를 사용할 수 있다.
- [ ] 빈도 계산에는 `count[key]++`를 사용할 수 있다.
- [ ] `insert()`와 `[]` 대입의 차이를 안다.
- [ ] `reserve()`와 `rehash()`의 목적을 설명할 수 있다.
- [ ] 평균과 최악 시간복잡도를 구분한다.

## 컨테이너 어댑터

- [ ] 어댑터가 제한된 인터페이스를 제공한다는 것을 안다.
- [ ] `stack`, `queue`, `priority_queue`는 반복자를 제공하지 않음을 안다.
- [ ] `pop()` 전 값을 먼저 확인한다.
- [ ] 최소 힙과 최대 힙을 구분한다.
- [ ] `push()`와 `pop()`의 시간복잡도를 설명한다.

## 문제 풀이

- [ ] 정답 포함 문제 21개 중 최소 16개를 직접 풀었다.
- [ ] 정답 없는 문제 10개 중 최소 6개를 풀었다.
- [ ] 책 재구성 실습 4개를 모두 수행했다.
- [ ] 틀린 문제의 자료구조 선택 이유를 다시 적었다.

# 오답 노트

| 문제 | 선택한 자료구조 | 틀린 원인 | 수정한 핵심 | 재풀이 |
|---|---|---|---|---|
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |

## 이전/다음 학습

- 이전: [[3일차 - 빈도 배열과 해시 원리 (책 보완 개정판)]]
- 다음: [[5일차 - 정렬과 이분탐색]]
