---
tags:
  - 코딩테스트
  - C++
  - 프로그래머스
  - DFS
  - BFS
  - graph
  - dynamic-programming
  - memoization
  - tabulation
date: 2026-08-10
day: 5
version: revised-integrated
intensity: double
source:
  - Cpp코테.pdf
---

# 5일차 - DFS·BFS + 간단한 동적 계획법

오늘은 두 개의 큰 주제를 한 번에 진행한다.

- 1부: 그래프 표현과 DFS·BFS
- 2부: 격자 탐색과 최단거리
- 3부: 메모이제이션·타뷸레이션을 이용한 동적 계획법
- 4부: 책 기반 문제와 프로그래머스형 연습문제

> 오늘의 완료 기준: 그래프와 격자에서 방문 배열을 사용해 DFS·BFS를 구현하고, 반복되는 부분 문제가 있는 문제에서 상태·점화식·초깃값을 정의해 DP로 바꿀 수 있다.

---

## 0. 책에서 참고한 범위와 검증 기준

`Cpp코테.pdf`의 다음 내용을 중심으로 보완했다.

### 그래프 탐색

- 6.1 들어가며
- 6.2 그래프 순회 문제
- 6.2.1 너비 우선 탐색
- 연습문제 28: BFS 구현하기
- 6.2.3 깊이 우선 탐색
- 연습문제 29: DFS 구현하기
- 실습문제 13: 이분 그래프 판별하기

### 동적 계획법

- 8.1 들어가며
- 8.2 동적 계획법이란?
- 8.3 메모이제이션: 하향식 접근 방법
- 8.4 타뷸레이션: 상향식 접근 방법
- 8.5 부분집합의 합 문제
- 연습문제 36~39: 완전 탐색, 백트래킹, 메모이제이션, 타뷸레이션
- 실습문제 18: 여행 경로

### 2단계 검증 방식

1. **1차 검증**: 그래프 탐색 범위와 DP 입문 범위를 순서대로 확인해 알고리즘의 전개와 예제를 파악한다.
2. **2차 검증**: 문서 작성 후 연습문제 28·29·36~39, 실습문제 13·18의 원문 페이지를 다시 열어 문제 조건과 설명을 대조한다.

2차 대조 결과, 책 248쪽의 BFS, 256쪽의 DFS, 260쪽의 이분 그래프, 337쪽의 완전 탐색, 344쪽의 백트래킹, 350쪽의 메모이제이션, 356쪽의 타뷸레이션, 360쪽의 여행 경로 조건이 이 문서의 K1~K8에 올바르게 반영되었음을 확인했다.

책의 그래프 구현은 일반화를 위해 클래스와 여러 STL 컨테이너를 사용한다. 이 문서에서는 코딩 테스트에서 바로 작성하기 쉬운 `vector<vector<int>>`, `queue`, 방문 배열 중심으로 단순화했다.

---

## 오늘의 학습 일정

권장 시간은 약 **6시간**이다.

| 구간 | 내용 | 권장 시간 |
|---|---|---:|
| 복습 | `stack`, `queue`, 2차원 `vector` | 20분 |
| 1부 | 그래프 표현과 DFS·BFS | 70분 |
| 그래프 연습 | G1~G12 | 90분 |
| 휴식 | 방문 처리 시점을 말로 설명하기 | 15분 |
| 2부 | DP 사고법, 메모이제이션, 타뷸레이션 | 70분 |
| DP 연습 | D1~D12 | 90분 |
| 책 기반 | K1~K8 | 45분 |
| 마무리 | 최종 테스트와 오답 노트 | 20분 |

---

# 1부 - 그래프와 DFS·BFS

## 1. 그래프란?

그래프는 정점과 간선으로 관계를 표현하는 자료구조다.

```text
정점(Vertex): 사람, 도시, 컴퓨터, 격자의 칸
간선(Edge): 친구 관계, 도로, 연결선, 이동 가능 관계
```

```text
1 --- 2
|     |
3 --- 4
```

### 무방향 그래프

`1 - 2`라면 1에서 2로, 2에서 1로 이동할 수 있다.

### 방향 그래프

`1 -> 2`라면 1에서 2로만 이동할 수 있다.

문제를 읽을 때 간선을 양쪽에 모두 추가해야 하는지 먼저 확인한다.

---

## 2. 인접 리스트

코딩 테스트에서 가장 자주 사용하는 그래프 표현이다.

```cpp
#include <vector>
using namespace std;

int vertexCount = 5;
vector<vector<int>> graph(vertexCount + 1);

graph[1].push_back(2);
graph[2].push_back(1);
```

무방향 간선 `(a, b)`를 추가하는 함수:

```cpp
void addUndirectedEdge(
    vector<vector<int>>& graph,
    int a,
    int b
) {
    graph[a].push_back(b);
    graph[b].push_back(a);
}
```

정점 번호가 1부터 시작하면 크기를 `vertexCount + 1`로 만든다. 0부터 시작하는 문제에서는 크기 `vertexCount`로 충분하다.

---

## 3. 방문 배열이 필요한 이유

사이클이 있는 그래프에서 방문 표시 없이 탐색하면 같은 정점을 무한히 다시 방문할 수 있다.

```cpp
vector<bool> visited(graph.size(), false);
```

방문 배열은 다음을 구분한다.

- 아직 발견하지 않은 정점
- 이미 탐색 예약 또는 방문한 정점

---

## 4. DFS - 깊이 우선 탐색

DFS는 한 경로를 끝까지 내려간 뒤 돌아와 다른 경로를 탐색한다.

```text
시작 -> 깊게 이동 -> 막힘 -> 되돌아감 -> 다른 경로
```

재귀 호출 자체가 스택 역할을 한다.

```cpp
void dfs(
    int current,
    const vector<vector<int>>& graph,
    vector<bool>& visited,
    vector<int>& order
) {
    visited[current] = true;
    order.push_back(current);

    for (int next : graph[current]) {
        if (!visited[next]) {
            dfs(next, graph, visited, order);
        }
    }
}
```

사용:

```cpp
vector<bool> visited(graph.size(), false);
vector<int> order;

dfs(1, graph, visited, order);
```

### DFS가 잘 맞는 문제

- 연결 요소 개수
- 경로 존재 여부
- 모든 가능한 선택 탐색
- 섬 개수
- 백트래킹
- 사이클 탐지

### 재귀 깊이 주의

정점이 매우 많고 그래프가 긴 사슬 모양이면 재귀 호출이 너무 깊어질 수 있다. 이때 명시적인 `stack`을 사용한 반복 DFS를 고려한다.

---

## 5. 반복문 DFS

```cpp
#include <stack>

vector<int> iterativeDfs(
    const vector<vector<int>>& graph,
    int start
) {
    vector<bool> visited(graph.size(), false);
    vector<int> order;
    stack<int> waiting;

    waiting.push(start);

    while (!waiting.empty()) {
        int current = waiting.top();
        waiting.pop();

        if (visited[current]) {
            continue;
        }

        visited[current] = true;
        order.push_back(current);

        for (auto it = graph[current].rbegin();
             it != graph[current].rend();
             ++it) {
            if (!visited[*it]) {
                waiting.push(*it);
            }
        }
    }

    return order;
}
```

재귀 DFS와 같은 방문 순서를 원하면 인접 정점을 역순으로 스택에 넣어야 할 수 있다.

---

## 6. BFS - 너비 우선 탐색

BFS는 시작점에서 가까운 정점부터 탐색한다.

```text
거리 0 -> 거리 1 -> 거리 2 -> 거리 3
```

먼저 들어온 정점을 먼저 처리해야 하므로 `queue`를 사용한다.

```cpp
#include <queue>

vector<int> bfs(
    const vector<vector<int>>& graph,
    int start
) {
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

### BFS의 핵심

```cpp
visited[next] = true;
waiting.push(next);
```

큐에 넣는 순간 방문 처리한다. 꺼낼 때 처리하면 같은 정점이 큐에 여러 번 들어갈 수 있다.

### BFS가 잘 맞는 문제

- 간선 가중치가 모두 같은 그래프의 최단거리
- 최소 이동 횟수
- 단계별 확산
- 미로 탈출
- 단어 변환
- 가장 가까운 목표 찾기

---

## 7. BFS로 거리 구하기

```cpp
vector<int> distances(
    const vector<vector<int>>& graph,
    int start
) {
    vector<int> distance(graph.size(), -1);
    queue<int> waiting;

    distance[start] = 0;
    waiting.push(start);

    while (!waiting.empty()) {
        int current = waiting.front();
        waiting.pop();

        for (int next : graph[current]) {
            if (distance[next] != -1) {
                continue;
            }

            distance[next] = distance[current] + 1;
            waiting.push(next);
        }
    }

    return distance;
}
```

`distance == -1`을 미방문 표시로 함께 사용한다.

---

## 8. 시간 복잡도

인접 리스트를 사용하면 DFS와 BFS 모두:

```text
O(V + E)
```

- `V`: 정점 수
- `E`: 간선 수

각 정점과 간선을 제한된 횟수만 확인하기 때문이다.

방문 순서는 인접 리스트에 저장된 순서에 따라 달라질 수 있다. 문제에서 작은 번호부터 방문하라고 하면 각 인접 리스트를 정렬한다.

```cpp
for (vector<int>& neighbors : graph) {
    sort(neighbors.begin(), neighbors.end());
}
```

---

## 9. DFS와 BFS 선택표

| 문제의 핵심 | 우선 선택 |
|---|---|
| 모든 연결 영역 확인 | DFS 또는 BFS |
| 경로 존재 여부 | DFS 또는 BFS |
| 모든 조합과 경우의 수 | DFS·백트래킹 |
| 동일 가중치 최소 이동 | BFS |
| 시작점에서 거리 계산 | BFS |
| 깊게 선택하고 되돌리기 | DFS |

둘 다 가능한 문제도 많다. 최소 이동 횟수가 나오면 BFS를 먼저 떠올린다.

---

# 2부 - 격자 탐색

## 10. 2차원 배열도 그래프다

격자의 각 칸을 정점으로 보고, 상하좌우로 이동 가능한 칸 사이를 간선으로 생각한다.

```cpp
int dr[4] = {-1, 1, 0, 0};
int dc[4] = {0, 0, -1, 1};
```

다음 위치:

```cpp
int nextRow = row + dr[direction];
int nextColumn = column + dc[direction];
```

범위 확인을 먼저 한다.

```cpp
bool inside(int row, int column, int rows, int columns) {
    return 0 <= row && row < rows
        && 0 <= column && column < columns;
}
```

---

## 11. 격자 DFS 템플릿

```cpp
void gridDfs(
    int row,
    int column,
    const vector<string>& grid,
    vector<vector<bool>>& visited
) {
    int rows = static_cast<int>(grid.size());
    int columns = static_cast<int>(grid[0].size());

    visited[row][column] = true;

    int dr[4] = {-1, 1, 0, 0};
    int dc[4] = {0, 0, -1, 1};

    for (int direction = 0; direction < 4; direction++) {
        int nextRow = row + dr[direction];
        int nextColumn = column + dc[direction];

        if (!inside(nextRow, nextColumn, rows, columns)) {
            continue;
        }

        if (grid[nextRow][nextColumn] == '0') {
            continue;
        }

        if (!visited[nextRow][nextColumn]) {
            gridDfs(nextRow, nextColumn, grid, visited);
        }
    }
}
```

격자가 비어 있을 수 있는 문제라면 `grid[0]`에 접근하기 전에 먼저 확인한다.

---

## 12. 격자 BFS 최단거리 템플릿

```cpp
int shortestPath(const vector<string>& grid) {
    if (grid.empty() || grid[0].empty()) {
        return -1;
    }

    int rows = static_cast<int>(grid.size());
    int columns = static_cast<int>(grid[0].size());

    vector<vector<int>> distance(
        rows,
        vector<int>(columns, -1)
    );

    queue<pair<int, int>> waiting;
    waiting.push({0, 0});
    distance[0][0] = 1;

    int dr[4] = {-1, 1, 0, 0};
    int dc[4] = {0, 0, -1, 1};

    while (!waiting.empty()) {
        auto [row, column] = waiting.front();
        waiting.pop();

        for (int direction = 0; direction < 4; direction++) {
            int nextRow = row + dr[direction];
            int nextColumn = column + dc[direction];

            if (!inside(nextRow, nextColumn, rows, columns)) {
                continue;
            }

            if (grid[nextRow][nextColumn] == '0') {
                continue;
            }

            if (distance[nextRow][nextColumn] != -1) {
                continue;
            }

            distance[nextRow][nextColumn]
                = distance[row][column] + 1;
            waiting.push({nextRow, nextColumn});
        }
    }

    return distance[rows - 1][columns - 1];
}
```

이 코드는 시작 칸과 도착 칸이 이동 가능한 칸이라는 조건을 가정한다.

---

## 13. 이분 그래프 맛보기

이분 그래프는 인접한 정점끼리 서로 다른 두 색으로 칠할 수 있는 그래프다.

```text
미방문: 0
색 A: 1
색 B: -1
```

BFS 또는 DFS로 탐색하며 이웃에는 현재 색의 반대 색을 준다. 이미 칠해진 이웃이 현재 정점과 같은 색이면 이분 그래프가 아니다.

연결되지 않은 그래프일 수 있으므로 모든 정점을 시작점 후보로 순회해야 한다.

---

# 3부 - 동적 계획법

## 14. 동적 계획법이란?

동적 계획법은 큰 문제를 작은 부분 문제로 나누고, 같은 부분 문제의 답을 다시 계산하지 않는 방법이다.

DP를 고려할 조건:

1. 같은 상태를 여러 번 계산한다.
2. 작은 문제의 답으로 큰 문제의 답을 만들 수 있다.

책에서는 이를 **중복되는 부분 문제**와 **최적 부분 구조**로 설명한다.

---

## 15. 피보나치에서 보이는 중복 계산

단순 재귀:

```cpp
long long fibonacci(int n) {
    if (n <= 1) {
        return n;
    }

    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

`fibonacci(5)`를 계산하면서 `fibonacci(3)`, `fibonacci(2)` 등을 여러 번 다시 계산한다. 시간 복잡도가 지수적으로 커진다.

---

## 16. 메모이제이션 - 하향식 DP

필요한 상태를 재귀적으로 계산하고 결과를 저장한다.

```cpp
long long fibonacciMemo(int n, vector<long long>& memo) {
    if (n <= 1) {
        return n;
    }

    if (memo[n] != -1) {
        return memo[n];
    }

    memo[n] = fibonacciMemo(n - 1, memo)
        + fibonacciMemo(n - 2, memo);

    return memo[n];
}
```

사용:

```cpp
vector<long long> memo(n + 1, -1);
long long answer = fibonacciMemo(n, memo);
```

- 장점: 재귀식과 비슷해 이해하기 쉽다.
- 주의: 재귀 깊이가 너무 크면 스택 문제가 생길 수 있다.

---

## 17. 타뷸레이션 - 상향식 DP

작은 상태부터 표를 채운다.

```cpp
long long fibonacciTable(int n) {
    if (n <= 1) {
        return n;
    }

    vector<long long> dp(n + 1, 0);
    dp[1] = 1;

    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }

    return dp[n];
}
```

- 시간: `O(N)`
- 공간: `O(N)`

이전 두 값만 필요하므로 공간을 `O(1)`로 줄일 수도 있다.

```cpp
long long fibonacciOptimized(int n) {
    if (n <= 1) {
        return n;
    }

    long long previousTwo = 0;
    long long previousOne = 1;

    for (int i = 2; i <= n; i++) {
        long long current = previousTwo + previousOne;
        previousTwo = previousOne;
        previousOne = current;
    }

    return previousOne;
}
```

---

## 18. DP 문제를 푸는 다섯 단계

### 1단계: 상태 정의

```text
dp[i]가 무엇을 의미하는가?
```

예: `dp[i] = i번째 계단까지 올라가는 방법의 수`

### 2단계: 점화식

```text
dp[i] = dp[i - 1] + dp[i - 2]
```

### 3단계: 초깃값

```text
dp[0] = 1
dp[1] = 1
```

### 4단계: 계산 순서

현재 상태에 필요한 이전 상태가 먼저 계산되어 있어야 한다.

### 5단계: 정답 위치

정답이 `dp[n]`인지, 전체 `max(dp)`인지 확인한다.

> 점화식부터 쓰지 말고 `dp[i]`의 뜻을 한글 한 문장으로 먼저 적는다.

---

## 19. 계단 오르기 기본형

한 번에 1칸 또는 2칸 오를 수 있을 때 정확히 `n`칸에 도착하는 방법 수:

```cpp
long long countWays(int n) {
    vector<long long> dp(n + 1, 0);
    dp[0] = 1;

    for (int i = 1; i <= n; i++) {
        dp[i] += dp[i - 1];

        if (i >= 2) {
            dp[i] += dp[i - 2];
        }
    }

    return dp[n];
}
```

`dp[0] = 1`은 아무것도 선택하지 않고 출발점에 있는 한 가지 방법을 의미한다.

---

## 20. 최댓값 DP 기본형

연속한 두 집을 동시에 선택할 수 없을 때 얻을 수 있는 최대 금액:

```cpp
int maximumMoney(const vector<int>& money) {
    if (money.empty()) {
        return 0;
    }

    if (money.size() == 1) {
        return money[0];
    }

    vector<int> dp(money.size(), 0);
    dp[0] = money[0];
    dp[1] = max(money[0], money[1]);

    for (int i = 2; i < static_cast<int>(money.size()); i++) {
        dp[i] = max(
            dp[i - 1],
            dp[i - 2] + money[i]
        );
    }

    return dp.back();
}
```

상태 의미:

```text
dp[i] = 0번부터 i번 집까지 고려했을 때 얻을 수 있는 최대 금액
```

---

## 21. 부분집합의 합 DP

각 숫자를 최대 한 번 사용해 합 `target`을 만들 수 있는지 판별한다.

```cpp
bool subsetSum(const vector<int>& numbers, int target) {
    vector<bool> possible(target + 1, false);
    possible[0] = true;

    for (int number : numbers) {
        for (int sum = target; sum >= number; sum--) {
            if (possible[sum - number]) {
                possible[sum] = true;
            }
        }
    }

    return possible[target];
}
```

### 합을 뒤에서부터 순회하는 이유

앞에서부터 갱신하면 같은 `number`를 이번 반복에서 여러 번 사용할 수 있다. 각 숫자를 한 번만 사용해야 하므로 뒤에서 앞으로 갱신한다.

- 시간: `O(N × target)`
- 공간: `O(target)`

target이 지나치게 크면 이 방법도 적합하지 않을 수 있다.

---

## 22. DFS·메모이제이션·타뷸레이션 관계

| 방식 | 특징 | 같은 상태 재계산 |
|---|---|---|
| 완전 탐색 DFS | 모든 선택을 탐색 | 많음 |
| 백트래킹 | 불가능한 가지를 중간에 중단 | 여전히 가능 |
| 메모이제이션 | DFS 결과를 상태별로 저장 | 제거 |
| 타뷸레이션 | 작은 상태부터 표를 채움 | 제거 |

DFS를 작성한 뒤 함수 인자가 같은 호출이 반복되는지 확인하면 DP로 전환할 단서를 찾을 수 있다.

---

# 4부 - 연습문제 32개

## A. 그래프 탐색 G1~G12

### G1. DFS 방문 순서

무방향 그래프와 시작 정점이 주어질 때 작은 번호의 이웃부터 방문한 DFS 순서를 반환하라.

### G2. BFS 방문 순서

같은 그래프에서 BFS 방문 순서를 반환하라. 방문 배열을 큐에 넣을 때 갱신한다.

### G3. 연결 요소 개수

정점과 무방향 간선 목록이 주어질 때 서로 연결된 정점 그룹의 개수를 구하라.

```cpp
int countComponents(const vector<vector<int>>& graph) {
    vector<bool> visited(graph.size(), false);
    int count = 0;

    for (int vertex = 0;
         vertex < static_cast<int>(graph.size());
         vertex++) {
        if (visited[vertex]) {
            continue;
        }

        vector<int> ignored;
        dfs(vertex, graph, visited, ignored);
        count++;
    }

    return count;
}
```

### G4. 네트워크

컴퓨터 연결 상태가 인접 행렬로 주어진다. 서로 연결된 네트워크 개수를 구하라.

### G5. 타깃 넘버

각 숫자 앞에 `+` 또는 `-`를 붙여 target을 만드는 방법 수를 구하라. 깊이 `index`와 현재 합 `sum`을 상태로 하는 DFS를 작성한다.

### G6. 섬의 개수

`1`은 땅, `0`은 바다인 격자에서 상하좌우로 연결된 섬의 개수를 구하라.

### G7. 게임 맵 최단거리

왼쪽 위에서 오른쪽 아래까지 이동하는 최소 칸 수를 BFS로 구하라. 도달할 수 없으면 `-1`을 반환한다.

### G8. 단어 변환

한 번에 한 글자만 바꾸고 주어진 단어만 사용할 때 시작 단어에서 target까지의 최소 변환 횟수를 구하라.

### G9. 가장 먼 노드

1번 정점에서 최단거리가 가장 먼 정점의 개수를 구하라. BFS 거리 배열을 사용한다.

### G10. 이분 그래프 판별

모든 연결 요소를 두 색으로 칠하며 인접한 두 정점의 색이 같은지 검사하라.

<details>
<summary>핵심 코드 확인</summary>

```cpp
bool isBipartite(const vector<vector<int>>& graph) {
    vector<int> color(graph.size(), 0);

    for (int start = 0;
         start < static_cast<int>(graph.size());
         start++) {
        if (color[start] != 0) {
            continue;
        }

        queue<int> waiting;
        color[start] = 1;
        waiting.push(start);

        while (!waiting.empty()) {
            int current = waiting.front();
            waiting.pop();

            for (int next : graph[current]) {
                if (color[next] == 0) {
                    color[next] = -color[current];
                    waiting.push(next);
                } else if (color[next] == color[current]) {
                    return false;
                }
            }
        }
    }

    return true;
}
```

</details>

### G11. 토마토 익히기

여러 개의 익은 토마토에서 동시에 퍼져 나간다. 모든 시작점을 큐에 먼저 넣는 다중 시작점 BFS로 최소 날짜를 구하라.

### G12. 안전 영역

비의 높이가 달라질 때 잠기지 않는 영역 개수의 최댓값을 구하라. 각 높이마다 방문 배열을 새로 만들고 DFS 또는 BFS를 수행한다.

---

## B. 간단한 DP D1~D12

### D1. 피보나치 세 방식 비교

단순 재귀, 메모이제이션, 타뷸레이션으로 구현하고 호출 횟수 또는 실행 시간을 비교하라.

### D2. 계단 오르기

한 번에 1칸 또는 2칸 올라 정확히 `n`칸에 도착하는 방법 수를 구하라.

### D3. 2×n 타일링

2×1 타일로 2×n 직사각형을 채우는 방법 수를 구하라. 큰 결과는 문제에서 지정한 수로 나눈다.

### D4. 1로 만들기

정수 `n`에 대해 1을 빼거나, 조건이 맞으면 2 또는 3으로 나눌 수 있다. 1을 만드는 최소 연산 횟수를 구하라.

상태:

```text
dp[i] = i를 1로 만드는 최소 연산 횟수
```

### D5. 연속하지 않은 최대 합

서로 인접한 원소를 동시에 고를 수 없을 때 선택한 값의 최대 합을 구하라.

### D6. 정수 삼각형

위에서 아래로 내려가며 인접한 숫자를 선택할 때 최대 합을 구하라.

### D7. 최소 동전 개수

동전 종류를 무제한으로 사용해 target을 만드는 최소 동전 수를 구하라. 만들 수 없으면 `-1`을 반환한다.

초깃값:

```cpp
vector<int> dp(target + 1, INF);
dp[0] = 0;
```

### D8. 동전 조합 수

동전의 순서를 구분하지 않고 target을 만드는 조합 수를 구하라. 동전 반복문을 바깥에 둔다.

### D9. 부분집합의 합

양의 정수 배열에서 각 원소를 최대 한 번 사용해 target을 만들 수 있는지 판별하라.

### D10. 배낭 문제 입문

각 물건의 무게와 가치가 주어질 때 한 번씩만 선택해 제한 무게 안에서 얻는 최대 가치를 구하라. 무게를 뒤에서부터 순회하는 1차원 DP를 사용한다.

### D11. 최장 공통 부분 수열 입문

두 문자열의 LCS 길이를 구하라.

```text
dp[i][j] = 첫 문자열 i개와 두 번째 문자열 j개를 사용한 LCS 길이
```

```cpp
if (a[i - 1] == b[j - 1])
    dp[i][j] = dp[i - 1][j - 1] + 1;
else
    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1]);
```

### D12. 등굣길

오른쪽과 아래로만 이동할 수 있는 격자에서 웅덩이를 피해 학교까지 가는 경로 수를 구하라.

---

## C. 책 기반 문제 K1~K8

### K1. BFS 구현 - 책 연습문제 28 변형

책의 그래프 예제처럼 정점과 간선으로 그래프를 만들고 시작 정점에서 BFS 방문 순서를 출력하라.

확인할 항목:

- 시작 정점을 먼저 방문 처리
- 큐의 `front()`를 읽은 뒤 `pop()`
- 아직 방문하지 않은 이웃만 삽입
- 인접 정점 순서에 따라 방문 결과가 달라질 수 있음
- 복잡도 `O(V + E)`

### K2. DFS 구현 - 책 연습문제 29 변형

같은 그래프를 재귀 DFS와 명시적 스택 DFS로 각각 탐색하고 방문 순서를 비교하라.

추가 질문: 스택에 이웃을 넣는 순서가 방문 순서에 어떤 영향을 주는가?

### K3. 이분 그래프 - 책 실습문제 13 변형

사람을 두 그룹으로 나누되 서로 연결된 사람은 다른 그룹에 있어야 한다. 모든 정점을 두 색으로 칠할 수 있는지 판별하고, 가능하면 각 그룹을 출력하라.

연결 요소가 여러 개일 수 있으므로 방문하지 않은 모든 정점에서 탐색을 다시 시작한다.

### K4. 완전 탐색 부분집합 합 - 책 연습문제 36 변형

각 원소를 선택하거나 선택하지 않는 두 갈래 DFS로 target을 만들 수 있는지 판별하라.

```text
solve(index + 1, sum)
solve(index + 1, sum + numbers[index])
```

시간 복잡도가 `O(2^N)`이 되는 이유를 재귀 트리로 설명한다.

### K5. 백트래킹 부분집합 합 - 책 연습문제 37 변형

모든 수가 양수일 때 현재 합이 target을 넘으면 탐색을 중단하도록 K4를 개선하라.

정렬 후 남은 수를 모두 더해도 target에 도달할 수 없는 경우도 가지치기할 수 있는지 생각한다.

### K6. 메모이제이션 부분집합 합 - 책 연습문제 38 변형

`(index, sum)` 상태의 결과를 저장해 같은 상태를 다시 계산하지 않도록 한다.

```text
memo[index][sum]
-1: 미계산
 0: 불가능
 1: 가능
```

### K7. 타뷸레이션 부분집합 합 - 책 연습문제 39 변형

다음 상태를 정의해 2차원 DP와 1차원 DP를 각각 구현하라.

```text
dp[i][sum] = 앞의 i개 원소로 sum을 만들 수 있는가?
```

1차원으로 줄였을 때 합을 뒤에서 순회해야 하는 이유를 설명한다.

### K8. 여행 경로 - 책 실습문제 18 변형

도시들이 출발지부터 목적지까지 한 줄로 배치되어 있고, `jump[i]`는 i번째 도시에서 앞으로 건너뛸 수 있는 최대 도시 수를 나타낸다. i번째 도시에서는 `i + 1`부터 `i + jump[i]`까지 이동할 수 있을 때 목적지까지 가는 경로 수를 구하라.

책의 문제는 앞쪽 도시에서 뒤쪽 도시로만 이동하는 구조이므로 다음 상태를 생각할 수 있다.

```text
dp[i] = i번째 도시까지 도달하는 경로 수
```

각 도시에 도달하는 방법 수를 다음 도시들에 전달한다.

```cpp
long long countRoutes(const vector<int>& jump) {
    if (jump.empty()) {
        return 0;
    }

    vector<long long> dp(jump.size(), 0);
    dp[0] = 1;

    for (int city = 0;
         city < static_cast<int>(jump.size());
         city++) {
        for (int step = 1; step <= jump[city]; step++) {
            int next = city + step;

            if (next >= static_cast<int>(jump.size())) {
                break;
            }

            dp[next] += dp[city];
        }
    }

    return dp.back();
}
```

경로 수가 커질 수 있으므로 문제에서 나머지 연산을 요구하는지 확인한다.

---

# 5부 - 실수 방지와 선택 훈련

## 23. 자주 하는 실수

### BFS 방문 처리가 늦음

큐에 넣을 때 방문 처리한다.

### 무방향 간선을 한쪽만 추가

```cpp
graph[a].push_back(b);
graph[b].push_back(a);
```

### 연결되지 않은 그래프에서 시작점 하나만 탐색

연결 요소, 이분 그래프 문제는 모든 정점을 순회한다.

### 격자 범위 검사보다 먼저 접근

`grid[nextRow][nextColumn]`을 읽기 전에 범위 안인지 확인한다.

### 최단거리인데 DFS를 사용

가중치가 같은 최소 이동 횟수는 BFS를 먼저 고려한다.

### DP 상태 의미 없이 배열부터 만듦

`dp[i]` 또는 `dp[i][j]`의 뜻을 한글로 먼저 적는다.

### 초깃값 누락

점화식이 맞아도 `dp[0]`, `dp[1]`이 잘못되면 전체가 틀린다.

### 0/1 부분집합 DP를 앞에서 갱신

같은 원소가 중복 사용된다. 각 원소를 한 번만 쓸 때는 합 또는 무게를 뒤에서 순회한다.

### 경로 수 오버플로

문제의 나머지 연산 조건과 `long long` 필요 여부를 확인한다.

### 메모 배열의 미계산 표시 충돌

정답으로 0이 가능한 문제에서 0을 미계산 표시로 쓰지 않는다. `-1`이나 별도의 방문 배열을 사용한다.

---

## 24. 알고리즘 선택표

| 문제 표현 | 먼저 떠올릴 것 |
|---|---|
| 연결되어 있는가 | DFS 또는 BFS |
| 연결된 영역 개수 | DFS 또는 BFS |
| 최소 이동 횟수 | BFS |
| 모든 선택 조합 | DFS·백트래킹 |
| 같은 상태가 반복됨 | 메모이제이션 |
| 작은 상태부터 만들 수 있음 | 타뷸레이션 |
| 각 물건을 한 번만 사용 | 0/1 DP, 역순 갱신 |
| 경로 수·방법 수 | DP 상태와 이전 경로 합 |

---

## 25. 최종 테스트

자료를 보지 않고 답한다.

1. 인접 리스트에서 무방향 간선을 어떻게 추가하는가?
2. DFS의 재귀 호출은 어떤 자료구조 역할을 하는가?
3. BFS가 사용하는 컨테이너는?
4. BFS에서 방문 처리는 언제 하는가?
5. 인접 리스트 DFS·BFS의 시간 복잡도는?
6. 방문 순서가 인접 리스트 순서에 따라 달라지는 이유는?
7. 가중치가 같은 그래프의 최단거리에 BFS를 쓰는 이유는?
8. 연결 요소 개수를 어떻게 세는가?
9. 격자를 그래프로 해석하면 정점과 간선은 무엇인가?
10. 이분 그래프 판별에 필요한 상태는?
11. DP를 적용할 두 가지 조건은?
12. 메모이제이션과 타뷸레이션의 차이는?
13. `dp[i]`의 의미를 먼저 정의해야 하는 이유는?
14. 피보나치 타뷸레이션의 시간 복잡도는?
15. 계단 문제에서 `dp[0] = 1`의 의미는?
16. 최댓값 DP에서 답이 `dp[n]`인지 전체 최댓값인지 어떻게 판단하는가?
17. 부분집합 합 1차원 DP를 역순 갱신하는 이유는?
18. 메모이제이션의 상태에는 어떤 인자가 포함되어야 하는가?
19. 단순 DFS 부분집합 탐색의 시간 복잡도는?
20. 재귀 깊이가 너무 클 때 DFS를 어떻게 바꿀 수 있는가?

16개 이상 정확히 설명하면 다음 날로 넘어간다.

---

## 26. 완료 체크리스트

- [ ] 인접 리스트를 만들고 무방향·방향 간선을 구분한다.
- [ ] 재귀 DFS와 반복 DFS를 작성할 수 있다.
- [ ] BFS와 거리 배열을 작성할 수 있다.
- [ ] 큐에 넣을 때 방문 처리한다.
- [ ] 연결 요소와 격자 영역 문제를 풀 수 있다.
- [ ] BFS로 동일 가중치 최단거리를 구할 수 있다.
- [ ] DP 상태·점화식·초깃값·순서를 설명할 수 있다.
- [ ] 메모이제이션과 타뷸레이션을 모두 구현할 수 있다.
- [ ] 0/1 부분집합 합을 역순 갱신할 수 있다.
- [ ] G1~G12 중 최소 9문제를 풀었다.
- [ ] D1~D12 중 최소 9문제를 풀었다.
- [ ] K1~K8을 모두 설명하거나 구현했다.
- [ ] 틀린 문제에 방문 처리 시점 또는 DP 상태를 기록했다.

---

## 27. 오답 노트 템플릿

```text
문제:
그래프 정점과 간선:
방향/무방향:
DFS/BFS 선택 이유:
방문 처리 시점:
격자 이동 방향:
dp 상태 정의:
점화식:
초깃값:
계산 순서:
정답 위치:
오버플로/나머지 연산:
반례:
시간 복잡도:
수정한 핵심 한 줄:
다시 풀 날짜:
```

---

## 연결 문서

- 이전: [[4일차 - 정렬과 이분 탐색]]
- 다음: [[6일차 - 유형 종합 실전과 약점 보완]]

> 오늘의 핵심 한 문장: **공간의 연결을 탐색할 때는 DFS·BFS를 사용하고, 같은 상태의 답을 반복 계산한다면 상태를 저장해 동적 계획법으로 바꾼다.**
