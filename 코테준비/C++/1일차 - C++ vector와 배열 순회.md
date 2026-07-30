---
tags:
  - 코딩테스트
  - C++
  - 프로그래머스
  - 배열
  - vector
date: 2026-07-29
day: 1
---

# 1일차 — C++ `vector`와 배열 순회

## 오늘의 목표

프로그래머스 Level 1 배열 문제의 기본 형태를 익힌다.

- `vector<int>`에 여러 정수를 저장할 수 있다.
- 인덱스 반복문과 범위 기반 반복문을 구분해 사용할 수 있다.
- 합계, 개수, 최댓값을 직접 구할 수 있다.
- 프로그래머스의 `solution` 함수 형식에 익숙해진다.

> 오늘의 완료 기준: 정수 배열에서 **음수의 개수**를 세는 함수를 답을 보지 않고 작성한다.

---

## 1. `vector`란?

`vector`는 같은 자료형의 값을 여러 개 저장하는 동적 배열이다. 코딩 테스트에서는 일반 배열보다 `vector`를 훨씬 자주 사용한다.

```cpp
#include <vector>
using namespace std;

vector<int> numbers = {3, 1, 4, 1, 5};
```

| 표현 | 의미 | 결과 |
|---|---|---:|
| `numbers[0]` | 첫 번째 원소 | `3` |
| `numbers[1]` | 두 번째 원소 | `1` |
| `numbers.size()` | 원소 개수 | `5` |
| `numbers.back()` | 마지막 원소 | `5` |
| `numbers.empty()` | 비어 있는지 확인 | `false` |

인덱스는 반드시 `0`부터 시작한다. 원소가 5개라면 사용할 수 있는 인덱스는 `0`부터 `4`까지다.

```text
값:       3   1   4   1   5
인덱스:   0   1   2   3   4
```

### 원소 추가

```cpp
vector<int> numbers;

numbers.push_back(10);
numbers.push_back(20);
```

결과는 `{10, 20}`이다.

---

## 2. `vector` 순회하기

### 방법 A: 인덱스 반복문

현재 위치가 필요할 때 사용한다.

```cpp
for (int i = 0; i < numbers.size(); i++) {
    cout << numbers[i] << '\n';
}
```

- `int i = 0`: 첫 번째 인덱스부터 시작
- `i < numbers.size()`: 원소 개수보다 작은 동안 반복
- `i++`: 인덱스를 1 증가

다음 코드는 잘못된 코드다.

```cpp
for (int i = 0; i <= numbers.size(); i++) {
    cout << numbers[i] << '\n';
}
```

`i == numbers.size()`가 되면 배열 범위를 벗어난다. 마지막 조건은 `<=`가 아니라 `<`를 사용한다.

### 방법 B: 범위 기반 반복문

인덱스는 필요 없고 값만 필요할 때 사용한다.

```cpp
for (int number : numbers) {
    cout << number << '\n';
}
```

`numbers`에서 원소를 하나씩 꺼내 `number`에 복사한다.

### 어떤 반복문을 선택할까?

| 상황 | 권장 방식 |
|---|---|
| 모든 값을 차례로 읽기 | `for (int number : numbers)` |
| 현재 위치 `i`가 필요함 | `for (int i = 0; i < numbers.size(); i++)` |
| 앞뒤 원소를 비교함 | 인덱스 반복문 |
| 원본 원소를 수정함 | `for (int& number : numbers)` |

---

## 3. 프로그래머스 함수 형식

프로그래머스에서는 대부분 `main()`을 작성하지 않고 `solution()` 함수만 완성한다.

```cpp
#include <string>
#include <vector>

using namespace std;

int solution(vector<int> numbers) {
    int answer = 0;

    for (int number : numbers) {
        answer += number;
    }

    return answer;
}
```

위 함수는 다음 순서로 동작한다.

1. `vector<int> numbers`를 입력받는다.
2. `answer`에 모든 원소를 더한다.
3. 계산한 정수 `answer`를 반환한다.

```cpp
반환자료형 함수이름(매개변수) {
    // 계산
    return 결과;
}
```

---

## 4. 반드시 익힐 세 가지 패턴

### 패턴 1: 합계 구하기

```cpp
int sum = 0;

for (int number : numbers) {
    sum += number;
}
```

`sum += number`는 `sum = sum + number`와 같다.

합계의 시작값이 `0`인 이유는 어떤 수에 0을 더해도 값이 변하지 않기 때문이다.

### 패턴 2: 조건에 맞는 개수 세기

짝수의 개수를 센다.

```cpp
int count = 0;

for (int number : numbers) {
    if (number % 2 == 0) {
        count++;
    }
}
```

- 짝수: `number % 2 == 0`
- 홀수: `number % 2 != 0`
- `count++`: `count`를 1 증가

### 패턴 3: 최댓값 구하기

```cpp
int maxValue = numbers[0];

for (int number : numbers) {
    if (number > maxValue) {
        maxValue = number;
    }
}
```

최댓값의 초기값을 무조건 `0`으로 정하면 안 된다.

```cpp
vector<int> numbers = {-5, -2, -8};
```

모든 원소가 음수일 때 `0`은 배열에 없는 값이므로 오답이 된다. 배열에 원소가 하나 이상 있다는 조건이라면 첫 원소 `numbers[0]`으로 초기화한다.

---

## 5. 시간복잡도 기초

배열의 원소가 `N`개일 때 전체를 한 번 순회하면 시간복잡도는 `O(N)`이다.

```cpp
for (int number : numbers) {
    // 각 원소를 한 번 확인
}
```

지금은 다음 정도로 이해하면 충분하다.

- 원소 10개 → 약 10번 확인
- 원소 1,000개 → 약 1,000번 확인
- 원소 수에 비례해 실행 횟수가 증가 → `O(N)`

합계, 개수, 최댓값은 모두 한 번의 순회로 계산할 수 있다.

---

## 6. 자주 하는 실수

### 배열 범위를 벗어남

```cpp
// 잘못된 조건
i <= numbers.size()

// 올바른 조건
i < numbers.size()
```

### 비교와 대입을 혼동함

```cpp
if (number = 0)   // 대입: 잘못 작성한 경우가 많음
if (number == 0)  // 비교
```

### 세는 변수의 초기화를 빠뜨림

```cpp
int count = 0;
```

### 최댓값을 무조건 0으로 초기화함

음수가 들어올 수 있으면 첫 원소를 초기값으로 사용한다.

---

## 7. 단계별 실습

### 연습 1 — 홀수의 합

정수 배열 `numbers`가 주어질 때 홀수인 원소들의 합을 반환한다.

```text
입력: {1, 2, 3, 4, 5}
출력: 9
```

```cpp
int solution(vector<int> numbers) {
    int answer = 0;

    // 작성

    return answer;
}
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    int answer = 0;

    for (int number : numbers) {
        if (number % 2 != 0) {
            answer += number;
        }
    }

    return answer;
}
```

</details>

### 연습 2 — 최댓값

원소가 하나 이상인 정수 배열에서 가장 큰 값을 반환한다.

```text
입력: {-7, -3, -10, -1}
출력: -1
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    int answer = numbers[0];

    for (int number : numbers) {
        if (number > answer) {
            answer = number;
        }
    }

    return answer;
}
```

</details>

### 연습 3 — 음수의 개수

정수 배열에서 음수인 원소의 개수를 반환한다.

```text
입력: {-3, 0, 7, -1, -9}
출력: 3
```

```cpp
int solution(vector<int> numbers) {
    // 답을 보지 않고 작성
}
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    int answer = 0;

    for (int number : numbers) {
        if (number < 0) {
            answer++;
        }
    }

    return answer;
}
```

</details>

### 도전 — 조건을 만족하는 원소만 새 배열에 담기

정수 배열에서 양수만 골라 새로운 배열로 반환한다.

```text
입력: {-2, 5, 0, 3, -1}
출력: {5, 3}
```

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    vector<int> answer;

    for (int number : numbers) {
        if (number > 0) {
            answer.push_back(number);
        }
    }

    return answer;
}
```

</details>

---

## 8. 오늘의 핵심 문법

```cpp
vector<int> numbers;
numbers.push_back(10);
numbers[i];
numbers.size();
```

```cpp
for (int number : numbers) {
    // 값 사용
}
```

```cpp
for (int i = 0; i < numbers.size(); i++) {
    // 인덱스와 값 사용
}
```

```cpp
if (조건) {
    // 조건이 참일 때 실행
}
```

---

## 9. 복습 체크리스트

- [ ] `vector<int>`가 무엇인지 설명할 수 있다.
- [ ] 인덱스가 0부터 시작한다는 것을 기억한다.
- [ ] `i < numbers.size()`를 직접 작성할 수 있다.
- [ ] 범위 기반 반복문을 작성할 수 있다.
- [ ] 합계를 구할 때 변수를 0으로 초기화한다.
- [ ] 최댓값을 첫 번째 원소로 초기화하는 이유를 설명할 수 있다.
- [ ] 음수의 개수를 세는 문제를 답을 보지 않고 풀었다.

## 다음 학습

[[2일차 - 문자열 string과 문자 순회]]

