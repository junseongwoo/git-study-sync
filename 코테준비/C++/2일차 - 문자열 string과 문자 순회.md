---
tags:
  - 코딩테스트
  - C++
  - 프로그래머스
  - 문자열
  - string
date: 2026-07-30
day: 2
---

# 2일차 — 문자열 `string`과 문자 순회

## 오늘의 목표

프로그래머스 Level 1 문자열 문제의 기본 형태를 익힌다.

- `string`과 `char`의 차이를 설명할 수 있다.
- 문자열의 각 문자를 순회할 수 있다.
- 특정 문자의 개수를 셀 수 있다.
- 조건에 맞는 문자만 골라 새 문자열을 만들 수 있다.
- 대문자와 소문자를 판별하고 변환할 수 있다.
- 문자열을 거꾸로 뒤집을 수 있다.

> 오늘의 완료 기준: 대문자는 소문자로, 소문자는 대문자로 바꾸는 함수를 답을 보지 않고 작성한다.

---

## 1. `string`과 `char`

```cpp
#include <string>
using namespace std;

string word = "hello";
char letter = 'h';
```

| 자료형 | 저장하는 값 | 표기 |
|---|---|---|
| `char` | 문자 하나 | `'a'` |
| `string` | 문자 여러 개 | `"apple"` |

작은따옴표와 큰따옴표를 구분해야 한다.

```cpp
char ch = 'a';          // 올바름
string word = "apple";  // 올바름
```

문자열은 `vector`와 비슷하게 인덱스로 접근할 수 있다.

```cpp
string word = "hello";

word[0];       // 'h'
word[1];       // 'e'
word.size();   // 5
word.empty();  // false
```

```text
문자:     h   e   l   l   o
인덱스:   0   1   2   3   4
```

---

## 2. 문자열 순회

### 값만 필요할 때

```cpp
for (char ch : word) {
    cout << ch << '\n';
}
```

각 문자가 차례대로 `ch`에 복사된다.

### 인덱스가 필요할 때

```cpp
for (int i = 0; i < word.size(); i++) {
    cout << i << ": " << word[i] << '\n';
}
```

### 원본 문자를 수정할 때

```cpp
for (char& ch : word) {
    ch = 'x';
}
```

`&`는 여기서 원본 문자를 직접 가리킨다는 뜻이다.

| 코드 | 동작 |
|---|---|
| `for (char ch : word)` | 문자를 복사해서 읽음 |
| `for (char& ch : word)` | 원본 문자에 접근하므로 수정 가능 |

처음에는 다음처럼 기억한다.

- 읽기만 한다 → `char ch`
- 원본을 수정한다 → `char& ch`

---

## 3. 특정 문자 세기

문자열에서 `'a'`가 몇 번 나오는지 센다.

```cpp
int count = 0;

for (char ch : word) {
    if (ch == 'a') {
        count++;
    }
}
```

프로그래머스 함수로 작성하면 다음과 같다.

```cpp
int solution(string word) {
    int answer = 0;

    for (char ch : word) {
        if (ch == 'a') {
            answer++;
        }
    }

    return answer;
}
```

### `'a'` 또는 `'A'` 세기

```cpp
if (ch == 'a' || ch == 'A') {
    answer++;
}
```

- `||`: 또는
- `&&`: 그리고
- `!`: 아니다

---

## 4. 문자의 범위 판별

### 대문자

```cpp
if ('A' <= ch && ch <= 'Z') {
    // ch는 영문 대문자
}
```

### 소문자

```cpp
if ('a' <= ch && ch <= 'z') {
    // ch는 영문 소문자
}
```

### 숫자 문자

```cpp
if ('0' <= ch && ch <= '9') {
    // ch는 숫자 문자
}
```

주의:

```cpp
'7'  // 숫자 모양의 문자
7    // 정수
```

문자 `'7'`을 실제 정수 `7`로 바꾸려면 `'0'`을 뺀다.

```cpp
int number = '7' - '0';  // 7
```

예를 들어 문자열 `"507"`의 각 자리 숫자 합은 다음과 같이 구한다.

```cpp
int sum = 0;

for (char ch : text) {
    sum += ch - '0';
}
```

---

## 5. 새 문자열 만들기

문자열에서 `'a'`를 제거한다.

```cpp
string answer = "";

for (char ch : word) {
    if (ch != 'a') {
        answer += ch;
    }
}
```

`answer += ch`는 문자 하나를 문자열 뒤에 추가한다.

```text
입력:  "banana"
출력:  "bnn"
```

이 패턴은 다음 문제에 반복해서 사용된다.

- 특정 문자 제거
- 조건에 맞는 문자만 남기기
- 대소문자를 바꿔 새 문자열 만들기
- 문자열의 순서 바꾸기

---

## 6. 대소문자 변환

`toupper()`와 `tolower()`를 사용하려면 `<cctype>`를 포함한다.

```cpp
#include <cctype>

char upper = toupper('a');  // 'A'
char lower = tolower('Z');  // 'z'
```

문자열 전체를 대문자로 바꾼다.

```cpp
string solution(string word) {
    for (char& ch : word) {
        ch = toupper(ch);
    }

    return word;
}
```

새로운 문자열을 만들어도 된다.

```cpp
string solution(string word) {
    string answer = "";

    for (char ch : word) {
        answer += toupper(ch);
    }

    return answer;
}
```

코딩 테스트 입력이 일반적인 영문자라는 전제에서는 위 코드로 충분하다.

---

## 7. 문자열 뒤집기

뒤에서 앞으로 순회하며 새 문자열에 추가한다.

```cpp
string solution(string my_string) {
    string answer = "";

    for (int i = static_cast<int>(my_string.size()) - 1; i >= 0; i--) {
        answer += my_string[i];
    }

    return answer;
}
```

```text
입력: "coding"
출력: "gnidoc"
```

### 왜 `static_cast<int>`를 사용할까?

`size()`의 반환형은 부호 없는 정수형이다. 빈 문자열에서 `size() - 1`을 계산하면 예상과 다른 매우 큰 값이 될 수 있다. 정수로 변환한 뒤 1을 빼면 빈 문자열에서도 시작값이 `-1`이 되어 반복하지 않는다.

처음에는 아래 형태를 하나의 안전한 패턴으로 익혀도 좋다.

```cpp
for (int i = static_cast<int>(text.size()) - 1; i >= 0; i--) {
}
```

표준 라이브러리의 `reverse()`를 사용할 수도 있다.

```cpp
#include <algorithm>

reverse(my_string.begin(), my_string.end());
return my_string;
```

하지만 반복문 연습 단계에서는 직접 뒤집어 보는 것이 좋다.

---

## 8. 시간복잡도

길이가 `N`인 문자열을 한 번 순회하는 연산은 일반적으로 `O(N)`이다.

```cpp
for (char ch : text) {
    // 각 문자를 한 번 확인
}
```

특정 문자 세기, 모음 제거, 대소문자 변환, 뒤집기는 모두 한 번의 순회로 해결할 수 있으므로 `O(N)`이다.

---

## 9. 자주 하는 실수

### 문자와 문자열 표기를 혼동함

```cpp
ch == 'a'     // 문자 비교
word == "a"   // 문자열 비교
```

### 대입과 비교를 혼동함

```cpp
if (ch = 'a')   // 대입
if (ch == 'a')  // 비교
```

### `||`로 작성해야 할 조건을 `&&`로 작성함

```cpp
// ch가 a 또는 e인지 확인
if (ch == 'a' || ch == 'e')
```

문자 하나가 동시에 `'a'`이면서 `'e'`일 수는 없다.

### 원본을 수정하려는데 복사본을 사용함

```cpp
for (char ch : word) {
    ch = toupper(ch);  // word는 바뀌지 않음
}
```

원본을 수정하려면 참조를 사용한다.

```cpp
for (char& ch : word) {
    ch = toupper(ch);
}
```

---

## 10. 단계별 실습

### 연습 1 — 대문자의 개수

문자열에서 영문 대문자의 개수를 반환한다.

```text
입력: "HelloWORLD"
출력: 6
```

<details>
<summary>정답</summary>

```cpp
int solution(string my_string) {
    int answer = 0;

    for (char ch : my_string) {
        if ('A' <= ch && ch <= 'Z') {
            answer++;
        }
    }

    return answer;
}
```

</details>

### 연습 2 — 모음 제거

소문자 모음 `a`, `e`, `i`, `o`, `u`를 모두 제거한다.

```text
입력: "nice to meet you"
출력: "nc t mt y"
```

<details>
<summary>정답</summary>

```cpp
string solution(string my_string) {
    string answer = "";

    for (char ch : my_string) {
        if (ch != 'a' &&
            ch != 'e' &&
            ch != 'i' &&
            ch != 'o' &&
            ch != 'u') {
            answer += ch;
        }
    }

    return answer;
}
```

</details>

### 연습 3 — 숫자의 합

숫자로만 구성된 문자열의 각 자리 숫자 합을 반환한다.

```text
입력: "5072"
출력: 14
```

<details>
<summary>정답</summary>

```cpp
int solution(string number_string) {
    int answer = 0;

    for (char ch : number_string) {
        answer += ch - '0';
    }

    return answer;
}
```

</details>

### 연습 4 — 문자열 뒤집기

```text
입력: "coding"
출력: "gnidoc"
```

<details>
<summary>정답</summary>

```cpp
string solution(string my_string) {
    string answer = "";

    for (int i = static_cast<int>(my_string.size()) - 1; i >= 0; i--) {
        answer += my_string[i];
    }

    return answer;
}
```

</details>

---

## 11. 최종 문제 — 대소문자 바꾸기

알파벳으로 구성된 문자열이 주어진다.

- 대문자는 소문자로 변환한다.
- 소문자는 대문자로 변환한다.
- 변환한 문자열을 반환한다.

```text
입력: "HelloWorld"
출력: "hELLOwORLD"
```

```cpp
#include <string>
#include <cctype>
using namespace std;

string solution(string my_string) {
    string answer = "";

    // 답을 보지 않고 작성

    return answer;
}
```

<details>
<summary>정답</summary>

```cpp
string solution(string my_string) {
    string answer = "";

    for (char ch : my_string) {
        if ('A' <= ch && ch <= 'Z') {
            answer += tolower(ch);
        } else {
            answer += toupper(ch);
        }
    }

    return answer;
}
```

</details>

---

## 12. 오늘의 핵심 문법

```cpp
string text = "hello";
char ch = 'h';
```

```cpp
for (char ch : text) {
    // 문자 읽기
}
```

```cpp
if ('A' <= ch && ch <= 'Z') {
    // 대문자
}
```

```cpp
string answer = "";
answer += ch;
```

```cpp
toupper(ch);
tolower(ch);
```

```cpp
int digit = ch - '0';
```

---

## 13. 복습 체크리스트

- [ ] `char`와 `string`의 차이를 설명할 수 있다.
- [ ] 문자에는 작은따옴표, 문자열에는 큰따옴표를 사용한다.
- [ ] 문자열을 범위 기반 반복문으로 순회할 수 있다.
- [ ] `&&`와 `||`의 차이를 설명할 수 있다.
- [ ] 영문 대문자, 소문자, 숫자 문자를 범위로 판별할 수 있다.
- [ ] `answer += ch`로 새 문자열을 만들 수 있다.
- [ ] `'7' - '0'`이 정수 `7`이 되는 것을 이해한다.
- [ ] 문자열 뒤집기를 반복문으로 구현할 수 있다.
- [ ] 대소문자 변환 문제를 답을 보지 않고 풀었다.

## 다음 학습

3일차에는 배열과 문자열 문제를 조금 더 빠르게 풀기 위해 **빈도 배열과 기초 해시 사고방식**을 학습한다.

