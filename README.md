# Kunsan University Dormitory Auto Check

군산대학교 기숙사 **일일체크 자동화 시스템**입니다.

Playwright 기반 브라우저 자동화를 활용하여:

- 로그인
- 통합정보시스템 진입
- MY MENU 탐색
- 일일체크 신청
- 저장 및 팝업 처리

과정을 자동 수행합니다.

군산대학교 통합정보시스템의 Nexacro 기반 구조와  
iframe / popup / 동적 DOM 환경에 대응하도록 설계되었습니다.

---

# 🚨 IMPORTANT (가장 먼저 해주세요)

## 필수 사전 설정: "일일체크" 즐겨찾기 등록

자동화를 실행하기 전에 반드시 아래 작업을 먼저 해주세요.

```text
통합정보시스템
→ 학생생활관
→ 일일체크
→ ⭐ 즐겨찾기 등록
```

⚠️ 이 과정이 되어있지 않으면 자동화가 정상 동작하지 않습니다.

이 프로젝트는 단순 URL 이동 방식이 아니라,  
사용자의 개인화된 메뉴 구조(My Menu / 즐겨찾기)를 기준으로
일일체크 메뉴를 탐색합니다.

즉, 즐겨찾기가 등록되어 있지 않으면:

- 메뉴 탐색 실패
- DOM 경로 불일치
- 자동 클릭 실패
- 자동화 전체 중단

문제가 발생할 수 있습니다.

자동화를 사용하지 않으려면,
즐겨찾기를 다시 해제하면 됩니다.


---

# 🎥 Demo

<img src="./docs/demo.gif" width="100%">


모든 실행 로직은 아래와 같습니다:)

```md

1. 로그인
2. 통합정보 클릭
3. MY MENU 이동
4. 일일체크 탐색
5. 저장 버튼 클릭
6. 예 버튼 자동 처리
7. 완료 로그 출력

```

---

# 🏗 System Architecture

```text
┌────────────────────┐
│   User Scheduler   │
│ (GitHub Actions /  │
│  Local Cron / iOS) │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│   Runtime Worker   │
│  (Execution Core)  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Playwright Engine  │
│ Chromium Automation│
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Kunsan Portal DOM  │
│ Nexacro Framework  │
└────────────────────┘
```

---

# ✨ Features

- 자동 로그인
- 통합정보시스템 자동 진입
- 새 창(tab) 자동 감지
- MY MENU 기반 메뉴 탐색
- iframe 탐색 대응
- 저장 버튼 자동 처리
- 팝업 자동 처리
- 중복 로그인 처리
- 실패 fallback 전략 내장
- Runtime 로그 출력
- Scriptable(iOS) 대응 구조

---

# 🤔 Why Playwright?

## 왜 Selenium이 아니라 Playwright를 사용했는가?

군산대학교 통합정보시스템은:

- 동적 DOM 렌더링
- iframe 구조
- Nexacro 기반 UI
- 새 창(tab) 전환
- popup layer
- 비동기 이벤트 처리

등 일반적인 웹사이트보다 복잡한 구조를 가지고 있습니다.

Playwright를 선택한 이유:

| 이유 | 설명 |
|---|---|
| 강력한 비동기 처리 | asyncio 기반 |
| 새 탭 감지 안정성 | context.expect_page() 지원 |
| iframe 탐색 강점 | frame 접근 용이 |
| Chromium 직접 제어 | 실제 사용자 행동과 유사 |
| auto-wait 기능 | DOM 안정성 향상 |
| locator 시스템 | 복잡한 selector 대응 |

특히 Nexacro 기반 환경에서는:

```python
locator()
wait_for()
expect_page()
frame traversal
```

기반 접근이 매우 중요했습니다.

---

# 🔍 DOM Traversal Strategy

## DOM 탐색 전략

이 프로젝트는 단순 CSS selector 자동화가 아닙니다.

군산대 통합정보시스템은:

- iframe 중첩
- 동적 생성 버튼
- popup layer
- 늦게 생성되는 DOM
- Nexacro 이벤트 시스템

등의 특수 구조를 가지고 있습니다.

따라서 다음과 같은 다중 fallback 탐색 전략을 사용합니다.

---

## 1차 탐색

```python
locator("button:has-text('저장')")
```

일반 DOM 기반 빠른 탐색

---

## 2차 탐색

```python
frame.get_by_role("button", name="저장")
```

iframe 내부 탐색

---

## 3차 탐색

```python
keyboard.press("Enter")
```

popup focus 기반 강제 승인

---

## 4차 탐색

```python
모든 frame 순회
→ 모든 button 탐색
→ text 기반 fallback 처리
```

최종 Recovery Strategy

---

이 구조 덕분에:

- selector 일부 변경
- frame 구조 변화
- popup 구조 변화

등이 발생해도 즉시 전체 시스템이 붕괴되지 않도록 설계되었습니다.

---

# 🧠 Runtime Skeleton Architecture

## Runtime Lifecycle

이 프로젝트는 단순 script가 아니라  
"Runtime Execution Pipeline" 개념으로 설계되었습니다.

```text
Task Definition
    ↓
Browser Runtime
    ↓
Authentication
    ↓
Portal Navigation
    ↓
DOM Discovery
    ↓
Action Execution
    ↓
Popup Resolution
    ↓
Result Validation
    ↓
Logging & Exit
```

각 단계는 서로 독립적으로 실패를 처리할 수 있도록 구성되어 있습니다.

즉:

- 로그인 실패
- popup 실패
- DOM 탐색 실패
- frame 탐색 실패

등이 발생해도 Runtime 상태를 추적할 수 있습니다.

---

# ⚠ Nexacro Compatibility Layer

군산대학교 통합정보시스템은 Nexacro 기반 구조를 사용합니다.

일반 웹사이트 자동화와 달리:

- synthetic click 무시
- DOM 접근 제한
- TouchEvent 충돌
- iframe 중첩
- 이벤트 신뢰성 문제

등이 발생할 수 있습니다.

따라서 Scriptable/iOS 버전에서는:

- MouseEvent
- TouchEvent
- parent bubbling
- isTrusted override

등을 활용한 강제 이벤트 전파 전략을 사용합니다.

---

# 📂 Project Structure

```bash
.
├── .github/
│   ├── workflows/
│   │    └── main.txt
│   └── kunsan_github.py
│ 
├── README.md
├── LICENSE
│
├── docs/
│   ├── demo.gif
│   ├── architecture.png
│   ├── runtime.png
│   ├── flowchart.png
│   └── screenshots/
│        └── Login_screen.png
│
└── logs/
     └── new.txt
```

---

# ⚙ Installation

## 1. Repository Clone

```bash
git clone https://github.com/seongbin45/Kunsan-University-Dormitory-auto-check.git
```

---

## 2. Move Directory

```bash
cd Kunsan-University-Dormitory-auto-check
```

---

# 🐍 Python 설치

Python 다운로드:

https://www.python.org/downloads/

설치 시 반드시:

```text
Add Python to PATH
```

체크 필요

---

# 📦 Playwright 설치

```bash
pip install playwright
```

---

# 🌐 Chromium 설치

```bash
playwright install chromium
```

만약 오류가 발생한다면:

```bash
python -m playwright install chromium
```

---

# 🔐 GitHub Actions Secrets 설정 (매우 중요)

GitHub Actions에서 자동 실행하려면  
반드시 GitHub Repository Secrets에 학번과 비밀번호를 등록해야 합니다.

이 과정을 하지 않으면:

- 로그인 실패
- USER_ID 없음
- USER_PW 없음
- GitHub Actions 실행 실패

문제가 발생합니다.

---

# 📍 이동 경로

GitHub Repository에서 아래 경로로 이동해주세요.

```text
Settings
→ Security and quality
→ Secrets and variables
→ Actions
```

---

# ➕ USER_ID 등록 방법

## 1. "New repository secret" 버튼 클릭

오른쪽 초록색 버튼을 눌러주세요.

---

## 2. 아래처럼 입력

### Name

```text
USER_ID
```

### Secret

```text
본인 학번 입력
```

---

# ➕ USER_PW 등록 방법

다시 한 번:

```text
New repository secret
```

버튼을 누른 후 아래처럼 입력해주세요.

---

## Name

```text
USER_PW
```

---

## Secret

```text
본인 통합정보시스템 비밀번호 입력
```

---

# ⚠ 매우 중요

절대로 아래처럼 코드를 작성하지 마세요.

❌ 잘못된 방법(본인 개인정보를 만천하에 공개):

```python
user_id = "20201234"
user_pw = "mypassword"
```

---

# ✅ 올바른 방법

```python
import os

user_id = os.environ.get("USER_ID")
user_pw = os.environ.get("USER_PW")
```

GitHub Secrets에 저장된 값이
런타임에서 자동으로 주입됩니다.

---

# ⚙ GitHub Actions 활성화 (매우 중요)

현재 레포지스토리에는 실제 GitHub Actions Workflow 코드가 들어있는 파일이:

```text
main.txt
```

형태로 저장되어 있습니다.

⚠️ 하지만 GitHub Actions는:

```text
.yml
```

확장자만 Workflow 파일로 인식합니다.

즉:

```text
main.txt
```

상태로는 자동 실행이 절대로 동작하지 않습니다.

반드시:

```text
main.yml
```

로 변경해야 합니다.

---

# 📍 Workflow 파일 위치

레포지스토리에서 아래 경로로 이동해주세요.

```text
.github
→ workflows
→ main.txt
```

---

# 🖱 main.txt 파일 여는 방법

## 1. GitHub 레포지스토리 접속

https://github.com/seongbin45/Kunsan-University-Dormitory-auto-check-Public

---

## 2. `.github` 폴더 클릭

왼쪽 파일 목록에서:

```text
.github
```

클릭

---

## 3. `workflows` 폴더 클릭

그 다음:

```text
workflows
```

클릭

---

## 4. `main.txt` 클릭

아래 파일을 눌러주세요.

```text
main.txt
```

---

# ✏ 파일 수정 모드 들어가기

## 우측 상단 "연필(Edit)" 버튼 클릭

아래 버튼을 눌러주세요.

```text
✏ Edit this file
```

또는:

```text
연필 모양 버튼
```

클릭

---

# 📝 가장 중요한 단계: 파일 이름 변경

화면 상단을 보면:

```text
main.txt
```

라고 적혀 있습니다.

여기서:

```text
.txt
```

를 지우고:

```text
.yml
```

로 변경해주세요.

즉:

❌ 변경 전

```text
main.txt
```

✅ 변경 후

```text
main.yml
```

---

# 📌 왜 .yml 이어야 하는가?

GitHub Actions는:

```text
.github/workflows/
```

폴더 안의:

```text
*.yml
또는
*.yaml
```

파일만 자동 실행 Workflow로 인식합니다.

즉:

| 파일명 | 동작 여부 |
|---|---|
| main.txt | ❌ 실행 안됨 |
| main.py | ❌ 실행 안됨 |
| main.yml | ✅ 실행됨 |

입니다.

---

# 💾 저장하기 (Commit)

파일 이름을 변경했다면:

우측 상단의:

```text
Commit changes...
```

버튼을 눌러주세요.

---

## Commit message 입력

예시:

```text
Rename workflow to yml
```

---

## 마지막 저장 버튼 클릭

```text
Commit changes
```

를 다시 눌러주세요.

---

# ✅ 성공적으로 완료되면?

정상적으로 완료되면:

- GitHub가 Workflow를 자동 인식
- Actions 탭 활성화
- 자동 스케줄 실행 가능
- 수동 실행 가능

상태가 됩니다.

---

# 🚀 Workflow 실행 확인 방법

상단 메뉴에서:

```text
Actions
```

탭 클릭

---

정상이라면:

```text
Kunsan Daily Check
```

Workflow가 표시됩니다.

---

# ▶ 수동 실행 방법

Actions 탭에서:

```text
Run workflow
```

버튼 클릭 가능

---

# ⚠ 만약 Workflow가 안 보인다면?

대부분 원인:

| 원인 | 해결 |
|---|---|
| `.txt` 상태 | `.yml`로 변경 |
| workflows 폴더 아님 | `.github/workflows` 확인 |
| 저장 안함 | Commit changes 수행 |
| 문법 오류 | YAML 들여쓰기 확인 |

---

# 🧠 왜 처음부터 .yml이 아니었나요?

GitHub는:

```text
.yml
```

파일이 올라오면 자동으로 Workflow를 실행할 수 있습니다.

따라서 보안을 위해:

- 사용자가 직접 활성화하도록
- 의도하지 않은 자동 실행 방지
- 초보자의 실수 방지

목적으로 처음에는 `.txt` 형태로 제공됩니다.

---

# 🚀 Usage

## 실행

```bash
python kunsan_github.py
```

---

# ⚙ GitHub Actions Workflow Example

`.github/workflows/main.yml`

```yaml
name: Kunsan Daily Check

on:
  schedule:
    - cron: '17 23 * * *'

  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          pip install playwright
          playwright install chromium

      - name: Run Script
        env:
          USER_ID: ${{ secrets.USER_ID }}
          USER_PW: ${{ secrets.USER_PW }}
        run: python main.py
```

---

# 🔄 Runtime Flow

```text
1. 로그인 페이지 접속
2. 로그인 처리
3. 중복 로그인 popup 처리
4. 통합정보 클릭
5. 새 탭 감지
6. 학생서비스 이동
7. MY MENU 탐색
8. 일일체크 신청 클릭
9. 저장 버튼 클릭
10. 예 popup 처리
11. 완료 검증
12. 종료
```

---

# 📱 iOS / Scriptable Support

이 프로젝트는 Scriptable 기반 iOS 자동화 구조도 지원합니다.

Scriptable 버전에서는:

- WKWebView 기반 자동화
- TouchEvent Injection
- Multi-frame Traversal
- Synthetic Click Override

전략을 사용합니다.

---

# ⚠ Warning

이 프로젝트는:

- 개인 학습
- 브라우저 자동화 연구
- 반복 작업 자동화

목적으로 제작되었습니다.

사용 시 반드시:

- 학교 정책
- 서비스 이용 약관
- 계정 보안

등을 고려해야 합니다.

과도한 요청 또는 비정상적 사용은
서비스에 영향을 줄 수 있습니다.

---

# 🛣 Roadmap

- [ ] Docker 지원
- [ ] GitHub Actions Scheduler
- [ ] Telegram 알림
- [ ] Discord Webhook
- [ ] OCR 기반 버튼 탐색
- [ ] AI DOM Recovery
- [ ] Runtime Monitoring
- [ ] Headless Cloud Mode
- [ ] Multi-account Runtime
- [ ] Auto Retry Queue

---

# 📸 Recommended Assets

```text
docs/
├── demo.gif
├── architecture.png
├── runtime.png
├── flowchart.png
└── screenshots/
```

---

# 📖 Technical Notes

군산대학교 통합정보시스템은 일반적인 SPA(Single Page Application)와 달리:

- Nexacro Runtime
- iframe 기반 렌더링
- 동적 popup
- 비표준 이벤트 흐름

구조를 사용합니다.

따라서 단순 Selenium 스타일 자동화보다:

- Runtime state tracking
- DOM recovery strategy
- popup fallback
- frame traversal

중심의 설계가 더 중요했습니다.

---

# 👨‍💻 Author

Developed by

https://github.com/seongbin45

---

# 📄 License

MIT License
