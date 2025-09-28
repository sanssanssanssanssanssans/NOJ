# A − B Problem Setup Guide (for NOJ Admins)

## 0) Problem Overview
- Title: **A − B**
- Description: Given two integers A and B, output `A - B`.
- Input: One line with two integers A, B
- Output: One line with `A - B`
- Constraints: -10^9 ≤ A, B ≤ 10^9
- Compare Policy: `exact` (or `token`/`ignore_ws` if you want to ignore whitespaces)
- Special Judge: not required

## 1) Testcases

### 1.1 ZIP Structure
The uploaded ZIP should contain paired `.in` / `.out` files:

a-b.zip
├─ 01.in
├─ 01.out
├─ 02.in
├─ 02.out
├─ 03.in
├─ 03.out


## 2) Create Problem (Admin UI)
1. Title: `A - B`
2. Description:
3. Time Limit: `1` second
4. Memory Limit: `256` MB
5. Compare Mode: `token` or `ignore_ws` recommended
6. Special Judge: unchecked
7. Upload the ZIP file

## 3) Solutions

### C++17
```cpp
#include <bits/stdc++.h>
using namespace std;
int main() {
    long long A, B;
    cin >> A >> B;
    cout << A - B << "\n";
}
```

### Python

```python
import sys
a, b = map(int, sys.stdin.read().split())
print(a - b)
```