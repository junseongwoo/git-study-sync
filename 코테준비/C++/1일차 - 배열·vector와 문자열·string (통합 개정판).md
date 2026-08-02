---
tags:
  - 코딩테스트
  - C++
  - 프로그래머스
  - array
  - vector
  - string
  - iterator
date: 2026-08-02
day: 1
version: revised-integrated
intensity: double
source:
  - Cpp코테.pdf
---

# 1일차 — 배열·`vector` + 문자열·`string`

기존 1일차와 2일차를 하나로 합친 통합 개정판이다.

- 1부: 배열, `std::array`, `std::vector`, 반복자
- 2부: `std::string`, 문자 순회와 변환
- 3부: 배열과 문자열을 함께 사용하는 종합 문제

> 오늘의 완료 기준: 배열과 문자열을 직접 순회해 합계·개수·최댓값·필터링·뒤집기·대소문자 변환을 구현하고, 각 연산의 시간복잡도를 설명한다.

---

## 이 노트에서 참고한 책의 범위

`Cpp코테.pdf`의 다음 내용을 코딩 테스트 입문 수준에 맞게 재구성했다.

- 1.2 연속된 자료 구조와 연결된 자료 구조
- 1.3 `std::array`
- 1.4 `std::vector`
- 1.6 반복자

책은 자료구조의 내부 동작과 일반적인 C++ 컨테이너 사용법을 설명한다. 이 노트에서는 그중 프로그래머스 Level 1·2 문제 풀이에 바로 필요한 부분을 선택했다.

---

## 오늘의 학습 일정

권장 시간은 약 4시간이다.

| 구간 | 내용 | 권장 시간 |
|---|---|---:|
| 준비 | 문법 워밍업과 전체 코드 실행 | 20분 |
| 1부 | 배열·`vector`·반복자 | 55분 |
| 1부 실습 | 배열 문제 8개 | 55분 |
| 휴식 | 자리에서 일어나기 | 15분 |
| 2부 | 문자열·문자 처리 | 50분 |
| 2부 실습 | 문자열 문제 8개 | 55분 |
| 종합 | 혼합 문제와 오답 정리 | 50분 |

---

# 0부 — 코딩 테스트용 C++ 워밍업

## 0.1 전체 실행 코드와 프로그래머스 코드의 차이

로컬에서 실행하는 전체 코드는 `main()`이 필요하다.

```cpp
#include <iostream>
#include <string>
#include <vector>
using namespace std;

int main() {
    vector<int> numbers = {1, 2, 3};

    for (int number : numbers) {
        cout << number << ' ';
    }

    cout << '\n';
    return 0;
}
```

프로그래머스에서는 대부분 `solution()` 함수만 작성한다.

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

함수 구조:

```cpp
반환자료형 함수이름(매개변수) {
    // 계산
    return 결과;
}
```

---

# 1부 — 배열, `std::array`, `std::vector`, 반복자

## 1. 연속된 자료 구조란?

배열과 `vector`는 같은 자료형의 원소를 메모리에서 연속적으로 저장한다.

```text
값:       10    20    30    40
인덱스:    0     1     2     3
메모리:  [10]  [20]  [30]  [40]
```

연속 저장의 중요한 장점은 인덱스로 원하는 원소에 즉시 접근할 수 있다는 점이다.

```cpp
numbers[2];  // 세 번째 원소
```

인덱스 접근의 시간복잡도는 `O(1)`이다.

반면 배열 중간에 원소를 삽입하거나 삭제하면 뒤쪽 원소들을 이동해야 하므로 보통 `O(N)`이다.

```text
{10, 20, 30, 40}의 인덱스 1에 15 삽입
              ↓ 뒤 원소 이동
{10, 15, 20, 30, 40}
```

> 배열 계열 자료구조는 임의 위치 읽기에 강하고, 중간 삽입·삭제에는 비용이 든다.

---

## 2. C 스타일 배열, `std::array`, `std::vector`

### C 스타일 배열

```cpp
int numbers[4] = {10, 20, 30, 40};
```

사용할 수는 있지만 코딩 테스트에서는 크기 관리와 함수 전달이 편한 `vector`를 주로 사용한다.

### `std::array`

크기가 컴파일할 때 결정되는 고정 크기 배열이다.

```cpp
#include <array>

array<int, 4> numbers = {10, 20, 30, 40};
```

```cpp
numbers[0];
numbers.size();
numbers.front();
numbers.back();
```

크기를 실행 중에 바꿀 수 없다.

```cpp
array<int, 4> numbers;
// push_back()을 사용할 수 없음
```

### `std::vector`

원소 개수를 실행 중에 변경할 수 있는 가변 크기 배열이다.

```cpp
#include <vector>

vector<int> numbers = {10, 20, 30, 40};
numbers.push_back(50);
```

프로그래머스에서는 입력 배열이 대부분 `vector<int>` 형태로 주어진다.

### 비교

| 구분 | `std::array` | `std::vector` |
|---|---|---|
| 크기 | 고정 | 가변 |
| 인덱스 접근 | `O(1)` | `O(1)` |
| 뒤에 원소 추가 | 불가능 | `push_back()` |
| 코딩 테스트 사용 빈도 | 제한된 크기에서 사용 | 매우 높음 |

---

## 3. `vector` 생성 방법

```cpp
vector<int> a;                 // 빈 벡터: {}
vector<int> b = {1, 2, 3};     // {1, 2, 3}
vector<int> c(5);              // {0, 0, 0, 0, 0}
vector<int> d(5, 7);           // {7, 7, 7, 7, 7}
```

괄호와 중괄호를 구분한다.

```cpp
vector<int> a(5);   // 원소 5개, 모두 0
vector<int> b{5};   // 원소 1개, 값은 5
```

빈도 배열을 만들 때 자주 사용하는 형태:

```cpp
vector<int> count(10, 0);
```

---

## 4. 인덱스와 원소 접근

```cpp
vector<int> numbers = {3, 1, 4, 1, 5};

numbers[0];       // 3
numbers[1];       // 1
numbers.front();  // 3
numbers.back();   // 5
numbers.size();   // 5
numbers.empty();  // false
```

원소가 5개라면 유효한 인덱스는 `0`부터 `4`까지다.

```text
값:       3   1   4   1   5
인덱스:   0   1   2   3   4
```

### `[]`와 `.at()`

```cpp
numbers[2];
numbers.at(2);
```

- `[]`: 빠르지만 범위를 검사하지 않는다.
- `.at()`: 범위를 검사하고 잘못된 인덱스면 예외를 발생시킨다.

코딩 테스트에서는 입력 조건과 인덱스를 직접 관리하며 `[]`를 자주 사용한다. 디버깅 중 범위 오류가 의심되면 `.at()`도 도움이 된다.

### 범위 오류

```cpp
numbers[numbers.size()];  // 마지막 다음 위치이므로 잘못된 접근
```

마지막 원소는 다음과 같다.

```cpp
numbers[numbers.size() - 1];
numbers.back();
```

단, 빈 `vector`에서는 `back()`과 `size() - 1`을 사용하면 안 된다.

---

## 5. `size`와 `capacity`

책에서 강조하는 `vector`의 핵심 개념이다.

- `size()`: 실제 저장된 원소의 개수
- `capacity()`: 메모리를 다시 할당하지 않고 저장할 수 있는 공간

```cpp
vector<int> numbers;

cout << numbers.size() << '\n';
cout << numbers.capacity() << '\n';
```

공간이 부족한 상태에서 `push_back()`을 호출하면 `vector`는 일반적으로 더 큰 메모리 공간을 확보하고 기존 원소를 새 공간으로 복사하거나 이동한다.

```text
기존 공간: [1][2][3]  꽉 참
새 공간:   [1][2][3][ ][ ][ ]
```

여러 원소가 추가될 것을 미리 안다면 `reserve()`로 공간만 확보할 수 있다.

```cpp
vector<int> numbers;
numbers.reserve(1000);
```

`reserve(1000)`은 원소를 1000개 만드는 것이 아니다. `size()`는 그대로 0이고 저장 공간만 미리 확보한다.

```cpp
vector<int> a(1000);   // size가 1000

vector<int> b;
b.reserve(1000);       // size는 0, capacity를 미리 확보
```

Level 1 문제에서는 직접 `reserve()`를 쓸 일이 많지 않지만 `size`와 `capacity`의 차이는 알아둔다.

---

## 6. 원소 추가와 삭제

### 맨 뒤에 추가

```cpp
numbers.push_back(10);
```

평균적인 시간복잡도는 `O(1)`이다. 재할당이 발생하는 특정 순간에는 `O(N)`이지만 여러 번의 추가를 평균 내면 상수 시간으로 본다. 이를 **분할 상환 `O(1)`**이라고 한다.

### 맨 뒤에서 삭제

```cpp
numbers.pop_back();
```

`pop_back()`은 값을 반환하지 않는다. 값을 먼저 저장한 후 삭제한다.

```cpp
int last = numbers.back();
numbers.pop_back();
```

### 중간에 삽입

```cpp
numbers.insert(numbers.begin() + 2, 99);
```

### 중간에서 삭제

```cpp
numbers.erase(numbers.begin() + 2);
```

범위를 삭제할 수도 있다. 끝 위치는 포함하지 않는다.

```cpp
numbers.erase(numbers.begin() + 1, numbers.begin() + 4);
// 인덱스 1, 2, 3 삭제
```

중간 삽입과 삭제는 뒤 원소를 이동하므로 `O(N)`이다.

### 모두 삭제

```cpp
numbers.clear();
```

---

## 7. `vector` 순회

### 인덱스가 필요할 때

```cpp
for (int i = 0; i < numbers.size(); i++) {
    cout << numbers[i] << '\n';
}
```

다음 조건은 범위를 벗어나므로 잘못되었다.

```cpp
i <= numbers.size()  // 잘못됨
i < numbers.size()   // 올바름
```

### 값만 필요할 때

```cpp
for (int number : numbers) {
    cout << number << '\n';
}
```

### 원본을 수정할 때

```cpp
for (int& number : numbers) {
    number *= 2;
}
```

| 형태 | 의미 |
|---|---|
| `int number` | 값을 복사해서 읽음 |
| `int& number` | 원본 원소를 직접 읽고 수정 |
| `const int& number` | 복사하지 않고 읽기만 함 |

`int`처럼 작은 자료형은 값 복사도 충분하다. `string`처럼 상대적으로 큰 객체를 읽기만 할 때는 `const string&`를 자주 사용한다.

---

## 8. 반복자 `begin()`과 `end()`

반복자는 컨테이너의 특정 위치를 가리키는 객체다.

```cpp
auto it = numbers.begin();
cout << *it;  // 첫 원소
```

- `begin()`: 첫 원소를 가리킴
- `end()`: 마지막 원소의 다음 위치를 가리킴
- `*it`: 반복자가 가리키는 원소
- `++it`: 다음 원소로 이동

```cpp
for (auto it = numbers.begin(); it != numbers.end(); ++it) {
    cout << *it << '\n';
}
```

`end()`는 실제 원소가 아니므로 역참조하면 안 된다.

```cpp
cout << *numbers.end();  // 잘못된 접근
```

범위 기반 반복문도 내부적으로 `begin()`과 `end()`를 사용하는 방식이라고 이해할 수 있다.

### 반복자 무효화

`vector`가 공간을 다시 할당하거나 중간 삽입·삭제로 원소를 이동하면 기존 반복자가 더 이상 유효하지 않을 수 있다.

```cpp
auto it = numbers.begin();
numbers.push_back(100);  // 재할당 가능
// 이후 it 사용은 위험할 수 있음
```

초보 단계에서는 다음 규칙을 따른다.

> `vector`를 삽입·삭제한 뒤에는 이전에 저장한 반복자나 원소 주소를 다시 사용하지 않는다.

---

## 9. 배열 문제의 세 가지 기본 패턴

### 합계

```cpp
int sum = 0;

for (int number : numbers) {
    sum += number;
}
```

### 조건을 만족하는 개수

```cpp
int count = 0;

for (int number : numbers) {
    if (number % 2 == 0) {
        count++;
    }
}
```

### 최댓값

```cpp
int maxValue = numbers[0];

for (int number : numbers) {
    if (number > maxValue) {
        maxValue = number;
    }
}
```

최댓값을 무조건 0으로 시작하면 음수만 있는 배열에서 실패한다.

```text
{-5, -2, -8}의 최댓값은 -2
```

배열에 원소가 하나 이상이라는 조건이라면 첫 원소로 초기화한다.

---

## 10. `vector` 주요 연산의 시간복잡도

| 연산 | 시간복잡도 |
|---|---:|
| `numbers[i]` | `O(1)` |
| `front()`, `back()` | `O(1)` |
| 전체 순회 | `O(N)` |
| `push_back()` | 평균 `O(1)` |
| `pop_back()` | `O(1)` |
| 중간 `insert()` | `O(N)` |
| 중간 `erase()` | `O(N)` |
| 값 찾기 | `O(N)` |

---

# 배열·`vector` 연습 문제

## V1 — 전체 합

정수 배열의 모든 원소 합을 반환한다.

<details>
<summary>정답</summary>

```cpp
int solution(vector<int> numbers) {
    int answer = 0;

    for (int number : numbers) {
        answer += number;
    }

    return answer;
}
```

</details>

## V2 — 음수의 개수

정수 배열에서 음수인 원소의 개수를 반환한다.

```text
입력: {-3, 0, 7, -1, -9}
출력: 3
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

## V3 — 홀수의 합

정수 배열에서 홀수인 원소들의 합을 반환한다.

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

## V4 — 최댓값

원소가 하나 이상인 정수 배열에서 가장 큰 값을 반환한다.

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

## V5 — 양수만 남기기

정수 배열에서 양수만 입력 순서대로 골라 반환한다.

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

## V6 — 모든 원소 두 배

정수 배열의 모든 값을 두 배로 바꿔 반환한다. 범위 기반 반복문과 참조를 사용한다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    for (int& number : numbers) {
        number *= 2;
    }

    return numbers;
}
```

</details>

## V7 — 인덱스와 값의 합

각 원소에 자신의 인덱스를 더한 배열을 반환한다.

```text
입력: {10, 10, 10}
출력: {10, 11, 12}
```

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    for (int i = 0; i < numbers.size(); i++) {
        numbers[i] += i;
    }

    return numbers;
}
```

</details>

## V8 — 첫 번째와 마지막 교환

원소가 하나 이상인 배열의 첫 번째 원소와 마지막 원소를 교환해 반환한다.

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<int> numbers) {
    int temp = numbers.front();
    numbers.front() = numbers.back();
    numbers.back() = temp;
    return numbers;
}
```

`#include <algorithm>`을 배웠다면 `swap(numbers.front(), numbers.back())`도 가능하다.

</details>

---

# 2부 — 문자열과 문자 처리

## 11. `string`과 `char`

```cpp
#include <string>

char letter = 'a';
string word = "apple";
```

| 자료형 | 저장하는 값 | 표기 |
|---|---|---|
| `char` | 문자 하나 | `'a'` |
| `string` | 문자 여러 개 | `"apple"` |

작은따옴표와 큰따옴표를 구분한다.

```cpp
char ch = 'a';
string text = "a";
```

`string`도 문자들이 연속된 순서로 저장되며 `vector`와 비슷한 방식으로 인덱스와 반복자를 사용할 수 있다.

```cpp
string word = "hello";

word[0];       // 'h'
word.size();   // 5
word.front();  // 'h'
word.back();   // 'o'
```

---

## 12. 문자열 생성과 연결

```cpp
string a = "hello";
string b = "world";
string c = a + " " + b;
// "hello world"
```

문자 하나를 뒤에 붙인다.

```cpp
string answer = "";
answer += 'a';
answer.push_back('b');
// "ab"
```

문자열을 여러 번 뒤에 붙이는 작업은 일반적으로 편리하지만, 매우 큰 입력에서 문자열 앞쪽 삽입을 반복하면 원소 이동 때문에 느릴 수 있다.

---

## 13. 문자열 순회

### 문자만 필요할 때

```cpp
for (char ch : word) {
    cout << ch << '\n';
}
```

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

```cpp
for (char ch : word) {
    ch = 'x';  // 복사본만 바뀌므로 word는 그대로
}
```

---

## 14. 문자의 범위와 논리 연산자

### 영문 대문자

```cpp
if ('A' <= ch && ch <= 'Z') {
}
```

### 영문 소문자

```cpp
if ('a' <= ch && ch <= 'z') {
}
```

### 숫자 문자

```cpp
if ('0' <= ch && ch <= '9') {
}
```

### `a` 또는 `A`

```cpp
if (ch == 'a' || ch == 'A') {
}
```

- `&&`: 그리고
- `||`: 또는
- `!`: 아니다
- `!=`: 같지 않다

---

## 15. 문자 숫자를 정수로 변환

```cpp
'7'  // 문자
7    // 정수
```

숫자 문자에서 `'0'`을 빼면 실제 정수 값이 된다.

```cpp
int number = '7' - '0';  // 7
```

숫자 문자열의 각 자리 합:

```cpp
int sum = 0;

for (char ch : numberString) {
    sum += ch - '0';
}
```

반대로 0부터 9까지의 정수를 문자로 만들려면 `'0'`을 더한다.

```cpp
char ch = '0' + 7;  // '7'
```

---

## 16. 대소문자 변환

```cpp
#include <cctype>

char upper = toupper('a');  // 'A'
char lower = tolower('Z');  // 'z'
```

문자열 전체를 대문자로 바꾼다.

```cpp
for (char& ch : word) {
    ch = toupper(static_cast<unsigned char>(ch));
}
```

영문 알파벳만 입력된다는 코딩 테스트 조건에서는 다음처럼 간단히 작성하는 경우가 많다.

```cpp
ch = toupper(ch);
```

---

## 17. 부분 문자열 `substr()`

```cpp
string text = "programming";

text.substr(0, 7);  // "program"
text.substr(3, 4);  // 인덱스 3부터 4글자: "gram"
text.substr(7);     // 인덱스 7부터 끝까지: "ming"
```

```cpp
text.substr(시작인덱스, 가져올길이)
```

두 번째 인자는 마지막 인덱스가 아니라 **문자 개수**다.

---

## 18. 문자열 검색 `find()`

```cpp
string text = "hello world";
size_t position = text.find("world");
```

찾지 못하면 `string::npos`를 반환한다.

```cpp
if (text.find("world") != string::npos) {
    // 부분 문자열이 존재함
}
```

처음 단계에서는 위치가 필요하지 않다면 위 패턴을 그대로 사용한다.

---

## 19. 문자열 뒤집기

뒤에서 앞으로 순회한다.

```cpp
string answer = "";

for (int i = static_cast<int>(text.size()) - 1; i >= 0; i--) {
    answer += text[i];
}
```

`size()`는 부호 없는 정수형을 반환하므로 빈 문자열까지 안전하게 처리하려면 정수로 변환한 후 1을 뺀다.

표준 알고리즘을 사용하면 다음과 같다.

```cpp
#include <algorithm>

reverse(text.begin(), text.end());
```

`begin()`과 `end()`가 `vector`뿐 아니라 `string`에서도 같은 방식으로 사용되는 것을 확인한다.

---

## 20. 문자열 문제의 기본 패턴

### 특정 문자 세기

```cpp
int count = 0;

for (char ch : text) {
    if (ch == 'a') {
        count++;
    }
}
```

### 조건에 맞는 문자만 남기기

```cpp
string answer = "";

for (char ch : text) {
    if (ch != 'a') {
        answer += ch;
    }
}
```

### 원본 문자 변경

```cpp
for (char& ch : text) {
    ch = toupper(ch);
}
```

---

## 21. 문자열 연산의 시간복잡도

길이를 `N`이라고 한다.

| 연산 | 일반적인 시간복잡도 |
|---|---:|
| `text[i]` | `O(1)` |
| `size()` | `O(1)` |
| 전체 순회 | `O(N)` |
| 뒤에 문자 추가 | 평균 `O(1)` |
| 문자열 뒤집기 | `O(N)` |
| 부분 문자열 생성 | 생성 길이에 비례 |
| 일반적인 부분 문자열 검색 | 구현과 입력에 따라 달라짐 |

---

# 문자열 연습 문제

## T1 — 특정 문자 개수

문자열에서 `'a'`가 등장한 횟수를 반환한다.

<details>
<summary>정답</summary>

```cpp
int solution(string text) {
    int answer = 0;

    for (char ch : text) {
        if (ch == 'a') {
            answer++;
        }
    }

    return answer;
}
```

</details>

## T2 — 대문자의 개수

영문 문자열에서 대문자의 개수를 반환한다.

<details>
<summary>정답</summary>

```cpp
int solution(string text) {
    int answer = 0;

    for (char ch : text) {
        if ('A' <= ch && ch <= 'Z') {
            answer++;
        }
    }

    return answer;
}
```

</details>

## T3 — 숫자의 합

숫자로만 구성된 문자열의 각 자리 숫자 합을 반환한다.

```text
입력: "5072"
출력: 14
```

<details>
<summary>정답</summary>

```cpp
int solution(string numberString) {
    int answer = 0;

    for (char ch : numberString) {
        answer += ch - '0';
    }

    return answer;
}
```

</details>

## T4 — 모음 제거

소문자 모음 `a`, `e`, `i`, `o`, `u`를 제거한다.

```text
입력: "nice to meet you"
출력: "nc t mt y"
```

<details>
<summary>정답</summary>

```cpp
string solution(string text) {
    string answer = "";

    for (char ch : text) {
        if (ch != 'a' && ch != 'e' && ch != 'i' &&
            ch != 'o' && ch != 'u') {
            answer += ch;
        }
    }

    return answer;
}
```

</details>

## T5 — 문자열 뒤집기

문자열을 거꾸로 뒤집어 반환한다. 먼저 반복문으로 풀고, 이후 `reverse()`로도 풀어본다.

<details>
<summary>반복문 정답</summary>

```cpp
string solution(string text) {
    string answer = "";

    for (int i = static_cast<int>(text.size()) - 1; i >= 0; i--) {
        answer += text[i];
    }

    return answer;
}
```

</details>

<details>
<summary>표준 알고리즘 정답</summary>

```cpp
string solution(string text) {
    reverse(text.begin(), text.end());
    return text;
}
```

</details>

## T6 — 대소문자 바꾸기

대문자는 소문자로, 소문자는 대문자로 변환한다. 입력은 영문 알파벳으로만 구성된다.

```text
입력: "HelloWorld"
출력: "hELLOwORLD"
```

<details>
<summary>정답</summary>

```cpp
string solution(string text) {
    for (char& ch : text) {
        if ('A' <= ch && ch <= 'Z') {
            ch = tolower(ch);
        } else {
            ch = toupper(ch);
        }
    }

    return text;
}
```

</details>

## T7 — 부분 문자열 포함 여부

문자열 `text`에 문자열 `target`이 들어 있으면 `true`, 아니면 `false`를 반환한다.

<details>
<summary>정답</summary>

```cpp
bool solution(string text, string target) {
    return text.find(target) != string::npos;
}
```

</details>

## T8 — 앞뒤가 같은 문자열

문자열이 앞에서 읽어도 뒤에서 읽어도 같으면 `true`, 아니면 `false`를 반환한다.

```text
"level" → true
"hello" → false
```

<details>
<summary>정답</summary>

```cpp
bool solution(string text) {
    int left = 0;
    int right = static_cast<int>(text.size()) - 1;

    while (left < right) {
        if (text[left] != text[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}
```

</details>

---

# 3부 — 배열과 문자열 종합 문제

## C1 — 문자열 길이 배열

문자열 배열의 각 문자열 길이를 정수 배열로 반환한다.

```text
입력: {"cpp", "algorithm", "a"}
출력: {3, 9, 1}
```

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<string> words) {
    vector<int> answer;
    answer.reserve(words.size());

    for (const string& word : words) {
        answer.push_back(word.size());
    }

    return answer;
}
```

</details>

## C2 — 특정 문자로 시작하는 단어

문자열 배열에서 문자 `target`으로 시작하는 단어만 입력 순서대로 반환한다. 빈 문자열도 입력될 수 있다.

<details>
<summary>정답</summary>

```cpp
vector<string> solution(vector<string> words, char target) {
    vector<string> answer;

    for (const string& word : words) {
        if (!word.empty() && word.front() == target) {
            answer.push_back(word);
        }
    }

    return answer;
}
```

</details>

## C3 — 가장 긴 단어

문자열 배열에서 가장 긴 단어를 반환한다. 길이가 같으면 먼저 등장한 단어를 반환한다. 배열에는 원소가 하나 이상 있다.

<details>
<summary>정답</summary>

```cpp
string solution(vector<string> words) {
    string answer = words[0];

    for (const string& word : words) {
        if (word.size() > answer.size()) {
            answer = word;
        }
    }

    return answer;
}
```

동률일 때 먼저 등장한 단어를 유지하려고 `>`를 사용한다.

</details>

## C4 — 각 단어의 모음 개수

영문 소문자 문자열 배열에서 각 단어의 모음 개수를 정수 배열로 반환한다.

```text
입력: {"apple", "sky", "queue"}
출력: {2, 0, 4}
```

<details>
<summary>정답</summary>

```cpp
vector<int> solution(vector<string> words) {
    vector<int> answer;

    for (const string& word : words) {
        int count = 0;

        for (char ch : word) {
            if (ch == 'a' || ch == 'e' || ch == 'i' ||
                ch == 'o' || ch == 'u') {
                count++;
            }
        }

        answer.push_back(count);
    }

    return answer;
}
```

</details>

## C5 — 숫자 문자열만 합산

문자열 배열에는 숫자로만 구성된 문자열이 들어 있다. 각 문자열을 정수로 변환한 뒤 전체 합을 반환한다.

```text
입력: {"10", "25", "3"}
출력: 38
```

<details>
<summary>정답</summary>

```cpp
int solution(vector<string> numbers) {
    int answer = 0;

    for (const string& number : numbers) {
        answer += stoi(number);
    }

    return answer;
}
```

</details>

## C6 — 가장 긴 단어의 인덱스

문자열 배열에서 가장 긴 단어의 인덱스를 반환한다. 길이가 같으면 가장 작은 인덱스를 반환한다.

이 문제는 정답 코드를 보지 않고 직접 작성한다.

---

# 추가 훈련 — 정답 없이 풀기

## 추가 1 — 최솟값과 인덱스

정수 배열에서 최솟값과 그 값이 처음 등장한 인덱스를 `vector<int>{최솟값, 인덱스}`로 반환한다.

## 추가 2 — 구간 합

정수 배열과 인덱스 `left`, `right`가 주어진다. 양 끝을 포함한 구간의 합을 반환한다.

## 추가 3 — 공백 제거

문자열에서 모든 공백 문자를 제거한다.

## 추가 4 — 숫자만 남기기

영문자와 숫자로 구성된 문자열에서 숫자 문자만 입력 순서대로 남긴다.

## 추가 5 — 단어 뒤집기

문자열 배열의 각 단어를 뒤집어 반환한다. 단어 배열의 순서는 유지한다.

## 추가 6 — 회문 단어의 개수

문자열 배열에서 앞뒤가 같은 단어가 몇 개인지 반환한다.

## 추가 7 — 연속 중복 문자 제거

문자열에서 연속으로 반복되는 문자는 하나만 남긴다.

```text
입력: "aaabccdddd"
출력: "abcd"
```

## 추가 8 — 인덱스 안전성 설명

아래 코드가 어떤 입력에서 위험한지 설명하고 안전하게 고친다.

```cpp
return numbers[numbers.size() - 1];
```

---

# 자주 하는 실수와 반례

## 1. 범위를 벗어난 반복

```cpp
for (int i = 0; i <= numbers.size(); i++)  // 잘못됨
```

마지막 조건은 `<`다.

## 2. 비교와 대입 혼동

```cpp
if (number = 0)   // 대입
if (number == 0)  // 비교
```

## 3. 최댓값을 0으로 초기화

반례:

```text
{-7, -3, -10}
```

## 4. 빈 배열에서 `front()` 또는 `back()` 사용

```cpp
if (!numbers.empty()) {
    cout << numbers.back();
}
```

## 5. 복사본을 수정

```cpp
for (char ch : text) {
    ch = toupper(ch);  // 원본은 바뀌지 않음
}
```

원본을 수정할 때는 `char& ch`를 사용한다.

## 6. 문자와 문자열 혼동

```cpp
ch == 'a';      // 문자 비교
text == "a";   // 문자열 비교
```

## 7. `size()`와 마지막 인덱스 혼동

원소가 5개면 `size()`는 5이고 마지막 인덱스는 4다.

## 8. 삽입 후 기존 반복자를 계속 사용

`vector`가 재할당되면 기존 반복자가 무효가 될 수 있다. 삽입·삭제 후 필요한 반복자는 다시 얻는다.

---

# 문제 풀이 사고 순서

배열이나 문자열 문제를 보면 먼저 다음을 확인한다.

```text
1. 모든 원소를 한 번씩 봐야 하는가?
2. 인덱스가 필요한가, 값만 필요한가?
3. 원본을 수정할 것인가, 새 결과를 만들 것인가?
4. 입력이 비어 있을 수 있는가?
5. 합계가 int 범위를 넘을 수 있는가?
6. 한 번의 순회 O(N)로 해결할 수 있는가?
```

반복문 선택:

| 상황 | 선택 |
|---|---|
| 값만 읽음 | `for (int value : values)` |
| 큰 객체를 읽기만 함 | `for (const string& value : values)` |
| 원본 수정 | `for (int& value : values)` |
| 인덱스 필요 | 인덱스 `for`문 |

---

# 오늘의 필수 암기 코드

## `vector`

```cpp
vector<int> numbers;
numbers.push_back(10);

for (int number : numbers) {
}
```

## 인덱스 순회

```cpp
for (int i = 0; i < numbers.size(); i++) {
    cout << numbers[i];
}
```

## 문자열 순회

```cpp
for (char ch : text) {
}
```

## 새 문자열 만들기

```cpp
string answer = "";
answer += ch;
```

## 원본 수정

```cpp
for (char& ch : text) {
    ch = toupper(ch);
}
```

## 뒤에서 앞으로 순회

```cpp
for (int i = static_cast<int>(text.size()) - 1; i >= 0; i--) {
}
```

---

# 오늘의 최종 테스트

다음 여섯 문제를 답을 보지 않고 풀면 통합 1일차를 완료한다.

- [ ] 음수의 개수
- [ ] 양수만 새 배열에 담기
- [ ] 인덱스와 값의 합
- [ ] 모음 제거
- [ ] 대소문자 바꾸기
- [ ] 각 단어의 모음 개수

풀이 후 다음 질문에 답한다.

1. 왜 인덱스 반복문 또는 범위 기반 반복문을 선택했는가?
2. 원본을 수정했는가, 새 결과를 만들었는가?
3. 빈 입력에서도 안전한가?
4. 시간복잡도는 얼마인가?
5. `vector`의 중간 삽입이 왜 `O(N)`인가?
6. `size()`와 `capacity()`의 차이는 무엇인가?

---

# 복습 체크리스트

## 배열과 `vector`

- [ ] 연속된 자료 구조가 무엇인지 설명할 수 있다.
- [ ] `std::array`와 `std::vector`의 크기 차이를 안다.
- [ ] `vector<int> a(5)`와 `vector<int> b{5}`의 차이를 안다.
- [ ] 인덱스가 0부터 시작함을 기억한다.
- [ ] `size()`와 `capacity()`의 차이를 설명할 수 있다.
- [ ] `push_back()`과 `pop_back()`을 사용할 수 있다.
- [ ] 중간 삽입·삭제가 `O(N)`인 이유를 설명할 수 있다.
- [ ] `begin()`과 `end()`의 의미를 설명할 수 있다.
- [ ] 삽입·삭제 후 반복자가 무효가 될 수 있음을 안다.

## 문자열

- [ ] `char`와 `string`의 차이를 설명할 수 있다.
- [ ] 문자와 문자열의 따옴표를 구분한다.
- [ ] 문자 범위로 대문자·소문자·숫자를 판별할 수 있다.
- [ ] `'7' - '0'`이 정수 7이 되는 것을 이해한다.
- [ ] 조건에 맞는 문자만 골라 새 문자열을 만들 수 있다.
- [ ] 원본 수정에 참조 `&`를 사용할 수 있다.
- [ ] `substr()`의 두 번째 인자가 길이라는 것을 안다.
- [ ] `find()` 결과를 `string::npos`와 비교할 수 있다.

## 문제 풀이

- [ ] 정답 포함 문제 21개 중 최소 15개를 직접 풀었다.
- [ ] 정답 없는 문제 9개 중 최소 5개를 풀었다.
- [ ] 틀린 문제마다 반례를 하나 만들었다.
- [ ] 다음 날 오답을 다시 풀도록 표시했다.

---

# 오답 노트

| 문제 | 틀린 원인 | 반례 | 다시 기억할 규칙 | 재풀이 |
|---|---|---|---|---|
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |
|  |  |  |  | [ ] |

## 다음 학습

개정 2일차에서는 책의 해시 테이블 설명을 참고하여 다음 두 개념을 함께 학습한다.

- 빈도 배열과 해시 사고방식
- `unordered_map`과 `unordered_set`
