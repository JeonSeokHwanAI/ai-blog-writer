# 환경 설정 및 설치

인자: $ARGUMENTS

프로젝트 실행에 필요한 환경을 점검하고 자동 설치합니다.

## 사용법

- `/setup` → 전체 환경 점검 및 설치
- `/setup check` → 점검만 (설치 안 함)
- `/setup update` → 최신 버전으로 업데이트
- `/setup python` → Python만 확인
- `/setup packages` → 패키지만 설치

## 업데이트 흐름 (`/setup update`)

인자가 `update`인 경우 아래 절차를 실행합니다.

### 1단계: git 설치 확인

```bash
git --version
```

**git 없을 때 안내:**
```
## Git 설치가 필요합니다

1. https://git-scm.com/downloads 접속
2. 운영체제에 맞는 버전 다운로드 및 설치
3. 설치 완료 후 VSCode/터미널 재시작
4. `/setup update` 다시 실행
```

### 2단계: git 저장소 확인 및 연결

```bash
git remote -v
```

**결과 분기:**

**A) 이미 origin이 설정된 경우** → 3단계로 이동

**B) git 저장소가 아닌 경우 (ZIP 다운로드 사용자)** → 자동 연결:
```bash
git init
git remote add origin https://github.com/JeonSeokHwanAI/ai-blog-writer.git
git fetch origin
git reset origin/main
git checkout -- .
```

> 이 과정에서 기존 docs/, output/, config/ 상태 파일은 .gitignore에 의해 **그대로 보존**됩니다.

### 3단계: 최신 버전 가져오기

```bash
git pull origin main
```

**충돌 발생 시:**
```
⚠️ 파일 충돌이 발생했습니다.
충돌 파일 목록을 표시하고, 사용자에게 어떻게 처리할지 질문합니다.
```

### 4단계: 패키지 업데이트

```bash
pip install -r requirements.txt
```

### 5단계: 업데이트 완료 확인

```
## 업데이트 완료! 🎉

| 항목 | 상태 |
|------|------|
| git 연결 | ✅ origin/main |
| 코드 업데이트 | ✅ 최신 버전 |
| 패키지 | ✅ 설치 완료 |
| 내 데이터 | ✅ 보존됨 (docs/, output/) |
```

---

## 실행 흐름

### 1단계: Python 설치 확인

```bash
python --version
```

**결과 분기:**
- Python 3.9 이상 → 다음 단계
- Python 없음 또는 버전 낮음 → 설치 안내

**Python 없을 때 안내:**
```
## Python 설치가 필요합니다

1. https://www.python.org/downloads/ 접속
2. "Download Python 3.12" 클릭
3. 설치 시 ✅ "Add Python to PATH" 반드시 체크
4. 설치 완료 후 VSCode/터미널 재시작
5. `/setup` 다시 실행

---
또는 Windows 사용자라면 아래 명령어로 설치:
```powershell
winget install Python.Python.3.12
```
설치 후 터미널을 재시작하세요.
```

### 2단계: pip 확인

```bash
pip --version
```

**pip 없을 때:**
```bash
python -m ensurepip --upgrade
```

### 3단계: 패키지 설치

```bash
pip install -r requirements.txt
```

**설치 진행 상황 표시:**
```
## 패키지 설치 중...

| 패키지 | 상태 |
|--------|------|
| requests | ✅ 설치됨 |
| beautifulsoup4 | ✅ 설치됨 |
| playwright | ✅ 설치됨 |
```

### 4단계: Playwright 브라우저 설치 (선택)

이달의 블로그(`/monthly`) 기능 사용 시 필요:

```bash
playwright install chromium
```

**안내:**
```
Playwright 브라우저를 설치할까요?
- `/monthly` 기능 사용 시 필요합니다
- 약 200MB 다운로드됩니다
```

### 5단계: 설치 완료 확인

```
## 환경 설정 완료! 🎉

| 항목 | 상태 |
|------|------|
| Python | ✅ 3.12.0 |
| pip | ✅ 24.0 |
| requests | ✅ 2.31.0 |
| beautifulsoup4 | ✅ 4.12.0 |
| playwright | ✅ 1.40.0 |
| Chromium | ✅ 설치됨 |

---
이제 `/search <블로그ID>` 로 시작해보세요!
```

## 오류 처리

### pip 권한 오류 시
```bash
pip install --user -r requirements.txt
```

### SSL 오류 시
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### 가상환경 권장 안내
```
💡 가상환경 사용을 권장합니다:
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 출력 형식

**점검 결과:**
```
## 환경 점검 결과

| 항목 | 상태 | 버전/메시지 |
|------|------|-------------|
| Python | ✅ | 3.12.0 |
| pip | ✅ | 24.0 |
| requests | ❌ | 미설치 |

---
`/setup` 으로 자동 설치를 진행하세요.
```
