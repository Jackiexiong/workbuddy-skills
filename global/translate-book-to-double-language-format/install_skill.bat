@echo off
REM ==============================================
REM translate-book-to-double-language-format Skill
REM Windows One-Click Installer
REM ==============================================

echo.
echo ==============================================
echo TRANSLATE-BOOK-TO-DOUBLE-LANGUAGE-FORMAT SKILL
echo ==============================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.7 or newer from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo ✓ Python is installed
python --version
echo.

REM Check and install Python packages
echo [2/5] Checking and installing Python packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pypandoc beautifulsoup4 markdown
if %errorlevel% neq 0 (
    echo WARNING: Some packages might have installation issues, continuing anyway...
)
echo ✓ Python packages ready
echo.

REM Check Calibre
echo [3/5] Checking Calibre installation...
where ebook-convert >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Calibre not found in PATH!
    echo Please install Calibre from: https://calibre-ebook.com/download_windows
    echo After installation, you may need to restart your terminal or add it to PATH.
    echo.
) else (
    echo ✓ Calibre is installed
)
echo.

REM Check Pandoc
echo [4/5] Checking Pandoc installation...
where pandoc >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Pandoc not found in PATH!
    echo Please install Pandoc from: https://github.com/jgm/pandoc/releases/latest
    echo.
) else (
    echo ✓ Pandoc is installed
)
echo.

REM Run environment check
echo [5/5] Running full environment check...
python "%~dp0check_env.py"
echo.

echo ==============================================
echo INSTALLATION COMPLETE!
echo ==============================================
echo.
echo What's next?
echo 1. Read the QUICKSTART.md file for usage instructions
echo 2. In WorkBuddy, just say: "Translate this book: [path to your book]"
echo.
echo Troubleshooting?
echo - Run check_env.py again to verify your setup
echo - Check the README.md for detailed documentation
echo.
pause

