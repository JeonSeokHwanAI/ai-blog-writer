#!/bin/bash
echo "========================================"
echo "  AI Blog Writer - Update"
echo "========================================"
echo ""

# Git check
echo "[1/4] Checking Git..."
if ! command -v git &> /dev/null; then
    echo "[X] Git is not installed."
    echo ""
    echo "========================================"
    echo "  Git Installation Guide"
    echo "========================================"
    echo ""
    echo "Run this command to install Git:"
    echo "  xcode-select --install"
    echo ""
    echo "Or install via Homebrew:"
    echo "  brew install git"
    echo ""
    echo "Then run this script again."
    exit 1
fi

GITVER=$(git --version | awk '{print $3}')
echo "[OK] Git $GITVER found"

# Check if git repo exists
echo ""
echo "[2/4] Checking git repository..."
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "[!] Git not initialized. Setting up..."
    echo ""
    git init
    git remote add origin https://github.com/JeonSeokHwanAI/ai-blog-writer.git
    git fetch origin
    git reset origin/main
    echo ""
    echo "[OK] Git connected to ai-blog-writer"
else
    echo "[OK] Git repository found"
fi

# Pull latest
echo ""
echo "[3/4] Downloading latest version..."
git pull origin main
if [ $? -ne 0 ]; then
    echo ""
    echo "[!] Update failed. There may be file conflicts."
    echo "    Please ask in the group chat for help."
    exit 1
fi
echo "[OK] Code updated"

# Install packages
echo ""
echo "[4/4] Updating packages..."
pip3 install -r requirements.txt > /dev/null 2>&1 || pip install -r requirements.txt > /dev/null 2>&1
echo "[OK] Packages updated"

echo ""
echo "========================================"
echo "  [OK] Update Complete!"
echo "========================================"
echo ""
echo "Your data (docs/, output/) is preserved."
echo ""
echo "New features available - check CLAUDE.md for details."
