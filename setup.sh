#!/bin/bash

echo "========================================"
echo "  AI Blog Writer - 환경 설정 (Mac/Linux)"
echo "========================================"
echo

# Python 확인
echo "[1/4] Python 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python이 설치되지 않았습니다."
    echo
    echo "[2/4] Python 자동 설치 중..."

    # Mac: Homebrew로 설치
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo "Homebrew 설치 중..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3
    # Linux: apt로 설치
    elif command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3 python3-pip
    # Linux: yum으로 설치
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    else
        echo "⚠️ 자동 설치 실패. 수동 설치가 필요합니다."
        echo
        echo "Mac: brew install python3"
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "또는: https://www.python.org/downloads/"
        exit 1
    fi
    echo "✅ Python 설치 완료!"
    echo
fi

PYVER=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python $PYVER 확인됨"

# pip 확인 및 업그레이드
echo
echo "[2/4] pip 확인 및 업그레이드..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip 준비 완료"

# 패키지 설치
echo
echo "[3/4] 필수 패키지 설치 중..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo
    echo "⚠️ 일부 패키지 설치 실패."
    echo "다음 명령어로 재시도해보세요:"
    echo "  pip3 install --user -r requirements.txt"
    exit 1
fi

# Playwright 설치 안내
echo
echo "[4/4] Playwright 브라우저 설치 (선택)"
echo
echo "/monthly 기능(이달의 블로그)을 사용하려면 Playwright가 필요합니다."
echo "약 200MB를 다운로드합니다."
echo
read -p "Playwright를 설치할까요? (Y/N): " INSTALL_PW
if [[ "$INSTALL_PW" =~ ^[Yy]$ ]]; then
    echo
    echo "Chromium 브라우저 설치 중..."
    playwright install chromium
    echo "✅ Playwright 설치 완료"
fi

echo
echo "========================================"
echo "  ✅ 설치 완료!"
echo "========================================"
echo
echo "이제 Claude Code에서 다음 명령어를 사용할 수 있습니다:"
echo "  /search [블로그ID]  - 블로그 스크래핑"
echo "  /review [블로그ID]  - 블로그 분석"
echo "  /setup check        - 환경 점검"
echo
