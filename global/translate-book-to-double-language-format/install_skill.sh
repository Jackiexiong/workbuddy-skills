#!/bin/bash
# ==============================================
# translate-book-to-double-language-format Skill
# macOS/Linux One-Click Installer
# ==============================================

echo
echo ==============================================
echo TRANSLATE-BOOK-TO-DOUBLE-LANGUAGE-FORMAT SKILL
echo ==============================================
echo

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.7 or newer."
    echo "macOS: brew install python3"
    echo "Linux: sudo apt install python3 python3-pip"
    exit 1
fi
echo "✓ Python is installed"
python3 --version
echo

# Check and install Python packages
echo "[2/5] Checking and installing Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install pypandoc beautifulsoup4 markdown
echo "✓ Python packages ready"
echo

# Check Calibre
echo "[3/5] Checking Calibre installation..."
if ! command -v ebook-convert &> /dev/null; then
    echo "WARNING: Calibre not found!"
    echo "Please install Calibre from: https://calibre-ebook.com/download"
    echo "macOS: brew install --cask calibre"
    echo
else
    echo "✓ Calibre is installed"
fi
echo

# Check Pandoc
echo "[4/5] Checking Pandoc installation..."
if ! command -v pandoc &> /dev/null; then
    echo "WARNING: Pandoc not found!"
    echo "Please install Pandoc from: https://pandoc.org/installing.html"
    echo "macOS: brew install pandoc"
    echo "Linux: sudo apt install pandoc"
    echo
else
    echo "✓ Pandoc is installed"
fi
echo

# Run environment check
echo "[5/5] Running full environment check..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/check_env.py"
echo

echo ==============================================
echo INSTALLATION COMPLETE!
echo ==============================================
echo
echo "What's next?"
echo "1. Read the QUICKSTART.md file for usage instructions"
echo "2. In WorkBuddy, just say: \"Translate this book: [path to your book]\""
echo
echo "Troubleshooting?"
echo "- Run check_env.py again to verify your setup"
echo "- Check the README.md for detailed documentation"
echo

