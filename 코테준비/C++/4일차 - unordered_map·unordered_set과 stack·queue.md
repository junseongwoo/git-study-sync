---
tags:
  - 코딩테스트
  - C++
  - 프로그래머스
  - unordered_map
  - unordered_set
  - stack
  - queue
date: 2026-08-01
day: 4
intensity: double
---

# 4일차 — Hash 자료구조 + Stack·Queue

오늘부터는 **하루에 기존 2일치 분량**을 진행한다.

- 1부: `unordered_map`, `unordered_set`
- 2부: `stack`, `queue`
- 3부: 두 개념을 섞은 종합 문제

> 완료 기준: 자료구조의 사용법만 외우는 것이 아니라, 문제를 읽고 어떤 자료구조를 선택해야 하는지 설명할 수 있어야 한다.

---

## 오늘의 학습 일정

권장 학습 시간은 약 4시간이다. 한 번에 하기 어렵다면 오전과 오후로 나눈다.

| 구간 | 내용 | 권장 시간 |
|---|---|---:|
| 1부 | Hash 개념과 예제 | 50분 |
| 1부 실습 | Hash 기본·응용 문제 | 60분 |
| 휴식 | 자리에서 일어나기 | 15분 |
| 2부 | Stack·Queue 개념과 예제 | 50분 |
| 2부 실습 | Stack·Queue 기본·응용 문제 | 60분 |
| 종합 | 혼합 문제와 오답 정리 | 45분 |

---

# 1부 — `unordered_map`과 `unordered_set`

## 1. 왜 새로운 자료구조가 필요한가?

3일차에는 값의 범위가 작을 때 빈도 배열을 사용했다.

```cpp
vector<int> count(26, 0);
count[ch - 'a']++;
```

하지만 다음 입력은 빈도 배열로 다루기 불편하다.

```text
"apple"  → 3번
"banana" → 5번
"orange" → 2번
```

문자열 자체를 키로 사용하려면 `unordered_map`이 적합하다.

```cpp
unordered_map<string, int> count;

count["apple"]++;
count["banana"]++;
```

`unordered_map`은 **키와 값의 쌍**을 저장한다.

```text
키(key)        값(value)
"apple"   →   3
"banana"  →   5
```

---

## 2. `unordered_map` 기본 문법

```cpp
#include <unordered_map>
using namespace std;

unordered_map<string, int> count;
```

`unordered_map<string, int>`는 다음 뜻이다.

- 키의 자료형: `string`
- 값의 자료형: `int`

### 값 저장과 수정

```cpp
count["apple"] = 3;
count["apple"]++;
count["banana"] += 2;
```

존재하지 않는 키에 `[]`로 접근하면 기본값이 만들어진다. `int`의 기본값은 0이다.

```cpp
unordered_map<string, int> count;
count["apple"]++;  // 0에서 1이 됨
```

### 키가 존재하는지 확인

```cpp
if (count.find("apple") != count.end()) {
    // "apple" 키가 존재함
}
```

```cpp
if (count.find("apple") == count.end()) {
    // "apple" 키가 존재하지 않음
}
```

### 원소 제거

```cpp
count.erase("apple");
```

### 크기와 비어 있는지 확인

```cpp
count.size();
count.empty();
```

---

## 3. `unordered_map` 순회

```cpp
for (const auto& entry : count) {
    cout << entry.first << ' ' << entry.second << '\n';
}
```

- `entry.first`: 키
- `entry.second`: 값
- `auto`: 컴파일러가 자료형을 추론
- `const auto&`: 복사하지 않고 읽기만 함

더 알아보기 쉬운 이름으로 구조 분해를 사용할 수도 있다. C++17 기준이다.

```cpp
for (const auto& [key, value] : count) {
    cout << key << ' ' << value << '\n';
}
```

### 중요한 주의점

`unordered_map`의 순회 순서는 정해져 있지 않다.

```cpp
for (const auto& [key, value] : count) {
    // 입력 순서나 알파벳 순서가 보장되지 않음
}
```

정렬된 순서가 필요하면 별도로 `vector`에 옮겨 정렬하거나 이후에 배울 `map`을 검토한다.

---

## 4. 빈도 계산 패턴

문자열 배열에서 각 문자열이 몇 번 등장하는지 센다.

```cpp
unordered_map<string, int> count;

for (const string& word : words) {
    count[word]++;
}
```

특정 문자열의 등장 횟수:

```cpp
return count[target];
```

전체 빈도 중 최댓값:

```cpp
int maxCount = 0;

for (const auto& [word, frequency] : count) {
    if (frequency > maxCount) {
        maxCount = frequency;
    }
}
```

---

## 5. `unordered_set` 기본 문법

`unordered_set`은 값을 중복 없이 저장한다. `map`처럼 별도의 값은 없고 **키만 저장**한다.

```cpp
#include <unordered_set>

unordered_set<int> numbers;

numbers.insert(10);
numbers.insert(20);
numbers.insert(10);  // 이미 있으므로 추가되지 않음
```

결과적으로 저장된 값은 10과 20 두 개다.

### 존재 여부 확인

```cpp
if (numbers.find(10) != numbers.end()) {
    // 10이 존재함
}
```

C++20을 사용할 수 있다면 다음도 가능하지만, 프로그래머스 호환성을 위해 당분간 `find()` 형태를 사용한다.

```cpp
numbers.contains(10);
```

### 삭제

```cpp
numbers.erase(10);
```

### 서로 다른 값의 개수

```cpp
unordered_set<int> uniqueNumbers(numbers.begin(), numbers.end());
return uniqueNumbers.size();
```

---

## 6. `map`과 `set` 중 무엇을 선택할까?

| 필요한 정보 | 선택 |
|---|---|
| 존재하는지만 확인 | `unordered_set` |
| 등장 횟수도 필요 | `unordered_map<T, int>` |
| 키마다 별도의 정보 저장 | `unordered_map` |
| 중복을 제거 | `unordered_set` |

예시:

```text
"apple"이 목록에 있는가?       → unordered_set
"apple"이 몇 번 나왔는가?     → unordered_map
회원 ID별 점수 저장            → unordered_map
서로 다른 방문자 수            → unordered_set
```

---

## 7. 평균 시간복잡도

| 연산 | 평균 시간복잡도 |
|---|---:|
| 삽입 `insert` | `O(1)` |
| 검색 `find` | `O(1)` |
| 삭제 `erase` | `O(1)` |

해시 충돌이 심한 최악의 경우 `O(N)`이 될 수 있지만, 일반적인 코딩 테스트 풀이에서는 평균 `O(1)`로 생각한다.

---

## 8. Hash에서 자주 하는 실수

### `count[key]`로 존재 여부를 확인함

```cpp
if (count[key] > 0) {
}
```

이 코드는 없던 키도 새로 만든다. 키의 존재 여부만 확인한다면 `find()`가 의도를 더 정확히 표현한다.

```cpp
if (count.find(key) != count.end()) {
}
```

### 순회 순서를 믿음

`unordered_map`과 `unordered_set`은 정렬된 순서를 보장하지 않는다.

### 중복이 필요한데 `set`을 사용함

`unordered_set`에는 같은 값을 여러 번 저장할 수 없다. 등장 횟수가 필요하면 `unordered_map`을 사용한다.

---

## Hash 연습 문제

### H1 — 서로 다른 숫자의 개수

정수 배열에서 서로 다른 숫자의 개수를 반환한다.

```text
입력: {1, 2, 2, 3, 1, 4}
출력: 4
```

<details>
<summary>정답</summary>

```cpp
#include <unordered_set>

int solution(vector<int> numbers) {
    unordered_set<int> uniqueNumbers;

    for (int number : numbers) {
        uniqueNumbers.insert(number);
    }

    return uniqueNumbers.size();
}
```

</details>

### H2 — 중복된 숫자가 있는가?

정수 배열에 같은 숫자가 두 번 이상 등장하면 `true`, 아니면 `false`를 반환한다.

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

### H3 — 특정 단어의 등장 횟수

문자열 배열 `words`에서 `target`이 등장한 횟수를 반환한다.

<details>
<summary>정답</summary>

```cpp
int solution(vector<string> words, string target) {
    unordered_map<string, int> count;

    for (const string& word : words) {
        count[word]++;
    }

    return count[target];
}
```

</details>

### H4 — 완주하지 못한 선수

참가자 이름 배열 `participant`와 완주자 이름 배열 `completion`이 주어진다. 완주하지 못한 한 명을 반환한다. 동명이인이 있을 수 있다.

```text
participant = {"leo", "kiki", "eden"}
completion  = {"eden", "kiki"}
출력: "leo"
```

<details>
<summary>정답</summary>

```cpp
string solution(vector<string> participant, vector<string> completion) {
    unordered_map<string, int> count;

    for (const string& name : participant) {
        count[name]++;
    }

    for (const string& name : completion) {
        count[name]--;
    }

    for (const auto& [name, frequency] : count) {
        if (frequency > 0) {
            return name;
        }
    }

    return "";
}
```

</details>

### H5 — 첫 중복 값

정수 배열을 왼쪽부터 확인할 때 처음으로 두 번째 등장한 값을 반환한다. 중복이 없으면 `-1`을 반환한다.

```text
입력: {3, 1, 4, 1, 3}
출력: 1
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    unordered_set<int> seen;

    for (int number : numbers) {
        if (seen.find(number) != seen.end()) {
            return number;
        }

        seen.insert(number);
    }

    return -1;
}
```

</details>

### H6 — 두 배열의 공통 원소 개수

두 정수 배열에서 양쪽에 모두 존재하는 **서로 다른 숫자**의 개수를 반환한다. 각 배열 안에는 중복이 있을 수 있다.

```text
A = {1, 2, 2, 3}
B = {2, 2, 3, 4}
출력: 2
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> a, vector<int> b) {
    unordered_set<int> first(a.begin(), a.end());
    unordered_set<int> common;

    for (int number : b) {
        if (first.find(number) != first.end()) {
            common.insert(number);
        }
    }

    return common.size();
}
```

</details>

### H7 — 문자열을 만들 수 있는가?

문자열 배열 `inventory`의 각 단어를 저장된 횟수만큼만 사용할 수 있다. `request`의 모든 단어를 제공할 수 있으면 `true`, 아니면 `false`를 반환한다.

```text
inventory = {"pen", "pen", "book"}
request   = {"pen", "book"}
출력: true
```

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

### H8 — 전화번호 목록

어떤 전화번호가 다른 전화번호의 접두어이면 `false`, 그렇지 않으면 `true`를 반환한다.

```text
입력: {"119", "97674223", "1195524421"}
출력: false
```

이 문제는 해시를 이용할 수 있지만 문자열 길이만큼 접두어를 잘라 확인해야 한다.

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

# 2부 — `stack`과 `queue`

## 9. 자료구조는 꺼내는 순서가 핵심이다

같은 데이터를 저장하더라도 어떤 순서로 꺼내야 하는지에 따라 자료구조가 달라진다.

```text
stack: 마지막에 넣은 것을 먼저 꺼냄 → LIFO
queue: 처음에 넣은 것을 먼저 꺼냄 → FIFO
```

- LIFO: Last In, First Out
- FIFO: First In, First Out

---

## 10. `stack` — 가장 최근 값부터 처리

접시를 쌓는 모습을 생각한다. 마지막에 올린 접시를 먼저 꺼낸다.

```cpp
#include <stack>

stack<int> s;

s.push(10);
s.push(20);
s.push(30);
```

현재 맨 위는 30이다.

```cpp
s.top();    // 30: 맨 위 값 확인
s.pop();    // 30 제거, 반환값은 없음
s.size();   // 원소 개수
s.empty();  // 비어 있는지 확인
```

### 매우 중요한 규칙

`pop()`은 값을 반환하지 않는다.

```cpp
int value = s.pop();  // 컴파일 오류
```

값을 먼저 확인한 다음 제거한다.

```cpp
int value = s.top();
s.pop();
```

빈 스택에서 `top()`이나 `pop()`을 호출하면 안 된다.

```cpp
if (!s.empty()) {
    int value = s.top();
    s.pop();
}
```

---

## 11. Stack이 필요한 문제 신호

- 가장 최근 항목을 취소한다.
- 괄호의 짝을 검사한다.
- 뒤에서부터 제거한다.
- 이전 상태로 돌아간다.
- 연속된 같은 값을 제거한다.
- 가장 가까운 이전 원소를 찾는다.

### 대표 예제 — 올바른 괄호

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

실패 조건은 두 가지다.

1. 닫는 괄호가 나왔는데 대응할 여는 괄호가 없다.
2. 문자열을 모두 처리했는데 여는 괄호가 남아 있다.

---

## 12. `queue` — 먼저 들어온 값부터 처리

줄을 서는 모습을 생각한다. 먼저 온 사람이 먼저 처리된다.

```cpp
#include <queue>

queue<int> q;

q.push(10);
q.push(20);
q.push(30);
```

```cpp
q.front();  // 10: 맨 앞 값
q.back();   // 30: 맨 뒤 값
q.pop();    // 맨 앞의 10 제거, 반환값은 없음
q.size();
q.empty();
```

값을 꺼내 처리하는 기본 패턴:

```cpp
while (!q.empty()) {
    int current = q.front();
    q.pop();

    // current 처리
}
```

---

## 13. Queue가 필요한 문제 신호

- 먼저 들어온 작업부터 처리한다.
- 대기 순서를 관리한다.
- 일정 시간마다 맨 앞 작업을 확인한다.
- 주변으로 한 단계씩 퍼져 나간다.
- BFS로 최단 거리를 구한다.

BFS는 이후 별도 학습일에 깊게 다룬다. 오늘은 Queue의 선입선출 동작에 집중한다.

---

## 14. Stack과 Queue 비교

| 구분 | `stack` | `queue` |
|---|---|---|
| 꺼내는 순서 | 마지막 입력부터 | 첫 입력부터 |
| 삽입 | `push()` | `push()` |
| 확인 | `top()` | `front()` |
| 제거 | `pop()` | `pop()` |
| 대표 문제 | 괄호, 취소, 역순 | 대기열, 작업 처리, BFS |

둘 다 `pop()`은 제거만 하며 값을 반환하지 않는다.

---

## Stack·Queue 연습 문제

### SQ1 — Stack 역순 출력

정수 배열의 원소를 스택에 모두 넣은 뒤 꺼내어 역순 배열을 반환한다.

```text
입력: {1, 2, 3, 4}
출력: {4, 3, 2, 1}
```

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    stack<int> s;

    for (int number : numbers) {
        s.push(number);
    }

    vector<int> answer;

    while (!s.empty()) {
        answer.push_back(s.top());
        s.pop();
    }

    return answer;
}
```

</details>

### SQ2 — 올바른 괄호

`'('`와 `')'`로만 구성된 문자열이 올바른 괄호 문자열인지 판별한다.

```text
"(())()" → true
"(()"    → false
")("     → false
```

<details>
<summary>정답</summary>

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

</details>

### SQ3 — 같은 숫자는 싫어

배열에서 연속해서 나타나는 같은 숫자는 하나만 남긴다.

```text
입력: {1, 1, 3, 3, 0, 1, 1}
출력: {1, 3, 0, 1}
```

스택의 `top()`을 이전 값으로 사용한다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    stack<int> s;

    for (int number : numbers) {
        if (s.empty() || s.top() != number) {
            s.push(number);
        }
    }

    vector<int> answer(s.size());

    for (int i = static_cast<int>(answer.size()) - 1; i >= 0; i--) {
        answer[i] = s.top();
        s.pop();
    }

    return answer;
}
```

실전에서는 `vector`의 마지막 원소를 이용하는 풀이가 더 간결하지만, 이번 문제는 스택 연습용이다.

</details>

### SQ4 — 문자열 폭발 기초

문자열에서 연속된 같은 문자 두 개를 만나면 제거한다. 제거 후 새롭게 붙은 문자도 같으면 다시 제거한다. 최종 문자열을 반환한다.

```text
입력: "baabaa"
출력: ""
```

<details>
<summary>정답</summary>

```cpp
string solution(string text) {
    stack<char> s;

    for (char ch : text) {
        if (!s.empty() && s.top() == ch) {
            s.pop();
        } else {
            s.push(ch);
        }
    }

    string answer = "";

    while (!s.empty()) {
        answer += s.top();
        s.pop();
    }

    reverse(answer.begin(), answer.end());
    return answer;
}
```

`reverse()`를 사용하므로 `<algorithm>`이 필요하다.

</details>

### SQ5 — 기능 실행 순서

정수 배열을 Queue에 넣은 순서대로 꺼내 같은 순서의 배열로 반환한다. Queue의 기본 동작을 확인하는 문제다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    queue<int> q;

    for (int number : numbers) {
        q.push(number);
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

### SQ6 — 카드 돌리기

1부터 `N`까지 번호가 적힌 카드가 Queue에 있다. 맨 앞 카드를 버리고, 다음 맨 앞 카드를 맨 뒤로 옮기는 동작을 카드가 한 장 남을 때까지 반복한다. 마지막 카드를 반환한다.

```text
N = 4
{1,2,3,4} → 1 버림 → {2,3,4} → 2 이동 → {3,4,2}
결과: 4
```

<details>
<summary>정답</summary>

```cpp
int solution(int n) {
    queue<int> q;

    for (int number = 1; number <= n; number++) {
        q.push(number);
    }

    while (q.size() > 1) {
        q.pop();

        q.push(q.front());
        q.pop();
    }

    return q.front();
}
```

</details>

### SQ7 — 프린터 대기열 기초

작업 시간이 담긴 Queue에서 앞의 작업부터 하나씩 처리한다. 누적 시간이 `limit`을 초과하기 직전까지 처리할 수 있는 작업 수를 반환한다.

```text
tasks = {3, 1, 4, 2}, limit = 7
출력: 2
설명: 3 + 1은 가능하지만 다음 4를 더하면 8이다.
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> tasks, int limit) {
    queue<int> q;

    for (int task : tasks) {
        q.push(task);
    }

    int usedTime = 0;
    int answer = 0;

    while (!q.empty()) {
        if (usedTime + q.front() > limit) {
            break;
        }

        usedTime += q.front();
        q.pop();
        answer++;
    }

    return answer;
}
```

</details>

### SQ8 — 다중 괄호 검사

`()`, `[]`, `{}` 세 종류의 괄호가 올바르게 짝지어졌는지 판별한다.

```text
"({[]})" → true
"([)]"   → false
```

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

        if (s.empty()) {
            return false;
        }

        if (ch == ')' && s.top() != '(') return false;
        if (ch == ']' && s.top() != '[') return false;
        if (ch == '}' && s.top() != '{') return false;

        s.pop();
    }

    return s.empty();
}
```

</details>

---

# 3부 — 종합 문제

## 종합 1 — 중복 명령 무시하기

문자열 명령이 순서대로 주어진다. 한 번이라도 처리한 명령은 다시 Queue에 넣지 않는다. 처음 등장한 명령만 입력 순서대로 반환한다.

```text
입력: {"save", "load", "save", "quit", "load"}
출력: {"save", "load", "quit"}
```

사용 자료구조:

- 중복 확인: `unordered_set`
- 처리 순서 유지: `queue`

<details>
<summary>정답</summary>

```cpp
vector<string> solution(vector<string> commands) {
    unordered_set<string> seen;
    queue<string> q;

    for (const string& command : commands) {
        if (seen.find(command) == seen.end()) {
            seen.insert(command);
            q.push(command);
        }
    }

    vector<string> answer;

    while (!q.empty()) {
        answer.push_back(q.front());
        q.pop();
    }

    return answer;
}
```

</details>

## 종합 2 — 최근 검색어

검색어 배열이 주어진다. 같은 검색어가 연속으로 들어오면 하나만 Stack에 남긴다. 최종 검색 기록을 입력 순서로 반환한다.

```text
입력: {"cpp", "cpp", "hash", "stack", "stack"}
출력: {"cpp", "hash", "stack"}
```

<details>
<summary>정답</summary>

```cpp
vector<string> solution(vector<string> searches) {
    stack<string> history;

    for (const string& search : searches) {
        if (history.empty() || history.top() != search) {
            history.push(search);
        }
    }

    vector<string> answer(history.size());

    for (int i = static_cast<int>(answer.size()) - 1; i >= 0; i--) {
        answer[i] = history.top();
        history.pop();
    }

    return answer;
}
```

</details>

## 종합 3 — 작업별 처리 횟수

Queue에서 작업 이름을 앞에서부터 꺼내 모두 처리하고, 작업 이름별 처리 횟수를 반환한다.

```text
입력: {"A", "B", "A", "C", "B", "A"}
결과: A=3, B=2, C=1
```

<details>
<summary>정답</summary>

```cpp
unordered_map<string, int> solution(vector<string> tasks) {
    queue<string> q;

    for (const string& task : tasks) {
        q.push(task);
    }

    unordered_map<string, int> answer;

    while (!q.empty()) {
        answer[q.front()]++;
        q.pop();
    }

    return answer;
}
```

</details>

## 종합 4 — 방문하지 않은 요청만 처리

요청 번호 배열이 주어진다. 이전에 처리한 적이 없는 요청만 Queue에 넣어 순서대로 처리하고, 처리된 요청 번호를 반환한다.

이 문제는 종합 1과 비슷하지만 코드를 보지 않고 처음부터 작성한다.

```text
입력: {10, 20, 10, 30, 20, 40}
출력: {10, 20, 30, 40}
```

---

# 추가 훈련 — 정답 없이 풀기

## 추가 1 — 회원별 최고 점수

이름 배열과 점수 배열이 같은 길이로 주어진다. 같은 이름이 여러 번 나오면 해당 회원의 최고 점수만 저장하라.

## 추가 2 — 두 번째 등장한 단어

문자열 배열에서 처음으로 등장 횟수가 2가 되는 단어를 반환하라. 없다면 빈 문자열을 반환하라.

## 추가 3 — 실행 취소

정수 문자열은 Stack에 저장하고, 문자열 `"undo"`가 나오면 가장 최근 정수를 제거한다. 모든 명령을 처리한 뒤 남은 정수의 합을 반환하라.

```text
입력: {"10", "20", "undo", "5"}
출력: 15
```

`stoi(text)`를 사용하면 숫자 문자열을 정수로 변환할 수 있다.

## 추가 4 — Queue 회전

1부터 `N`까지의 수를 Queue에 넣고, 맨 앞 원소를 맨 뒤로 옮기는 동작을 `K`번 수행한 뒤 맨 앞 값을 반환하라.

## 추가 5 — 괄호 제거 횟수

괄호 문자열이 주어질 때 올바른 괄호 문자열로 만들기 위해 제거해야 하는 최소 괄호 수를 계산하라.

```text
입력: "(()))(("
출력: 3
```

## 추가 6 — 고유 작업 대기열

작업 이름이 차례로 들어온다. 현재 Queue에 이미 들어 있는 작업은 추가하지 않는다. 작업을 하나 처리하면 같은 이름의 작업이 나중에 다시 들어올 수 있다. 필요한 자료구조를 직접 선택하라.

---

# 자료구조 선택 훈련

아래 상황에 맞는 자료구조를 먼저 답한 후 이유를 말한다.

| 상황 | 선택 |
|---|---|
| 이름별 점수를 저장 | `unordered_map<string, int>` |
| 이미 본 숫자인지 확인 | `unordered_set<int>` |
| 가장 최근 명령 취소 | `stack` |
| 접수 순서대로 처리 | `queue` |
| 단어별 등장 횟수 | `unordered_map<string, int>` |
| 중복 제거 | `unordered_set` |
| 괄호 검사 | `stack` |
| BFS 탐색 순서 관리 | `queue` |

문제를 읽을 때 다음 질문을 순서대로 한다.

```text
1. 존재 여부만 필요한가, 키별 값도 필요한가?
2. 데이터를 어떤 순서로 꺼내야 하는가?
3. 중복을 유지해야 하는가?
4. 정렬된 순서가 필요한가?
```

---

# 오늘의 필수 암기 코드

## `unordered_map`

```cpp
unordered_map<string, int> count;
count[word]++;

if (count.find(word) != count.end()) {
}
```

## `unordered_set`

```cpp
unordered_set<int> seen;
seen.insert(number);

if (seen.find(number) != seen.end()) {
}
```

## `stack`

```cpp
stack<int> s;
s.push(value);

if (!s.empty()) {
    int value = s.top();
    s.pop();
}
```

## `queue`

```cpp
queue<int> q;
q.push(value);

if (!q.empty()) {
    int value = q.front();
    q.pop();
}
```

---

# 오늘의 최종 테스트

아래 네 문제를 답을 보지 않고 풀면 4일차를 완료한다.

- [ ] 동명이인이 있는 완주하지 못한 선수
- [ ] 두 배열의 서로 다른 공통 원소 개수
- [ ] 다중 괄호 검사
- [ ] 중복 명령을 무시하는 Queue

각 문제를 푼 뒤 다음 내용을 말로 설명한다.

1. 왜 이 자료구조를 선택했는가?
2. 각 자료구조에 무엇을 저장했는가?
3. 시간복잡도는 얼마인가?
4. 빈 자료구조에서 값을 꺼낼 가능성은 없는가?

---

# 복습 체크리스트

## Hash

- [ ] `unordered_map`의 키와 값 개념을 설명할 수 있다.
- [ ] `count[key]++`로 빈도를 셀 수 있다.
- [ ] `find()`와 `end()`로 존재 여부를 확인할 수 있다.
- [ ] `unordered_set`이 중복을 저장하지 않는다는 것을 안다.
- [ ] `unordered_map`의 순회 순서가 보장되지 않음을 안다.
- [ ] 존재 확인과 빈도 계산에 맞는 자료구조를 선택할 수 있다.

## Stack·Queue

- [ ] LIFO와 FIFO의 차이를 설명할 수 있다.
- [ ] `top()`과 `front()`의 차이를 안다.
- [ ] `pop()`이 값을 반환하지 않는다는 것을 안다.
- [ ] 빈 자료구조에서 값을 꺼내지 않도록 검사한다.
- [ ] 올바른 괄호 문제를 Stack으로 풀 수 있다.
- [ ] Queue의 기본 처리 반복문을 작성할 수 있다.

## 문제 풀이

- [ ] 정답이 있는 문제 19개 중 최소 14개를 직접 풀었다.
- [ ] 정답 없는 문제 7개 중 최소 3개를 풀었다.
- [ ] 틀린 문제를 다음 날 다시 풀도록 표시했다.

---

# 오답 노트

| 문제 | 선택한 자료구조 | 틀린 원인 | 고친 핵심 | 재풀이 |
|---|---|---|---|---|
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |

## 이전/다음 학습

- 이전: [[3일차 - 빈도 배열과 기초 해시 사고방식]]
- 다음: 5일차 — 정렬 + 이분탐색
