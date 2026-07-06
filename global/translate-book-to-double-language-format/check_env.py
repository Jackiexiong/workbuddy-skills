#!/usr/bin/env python3
"""
Environment Checker for translate-book-to-double-language-format Skill
Checks if all required dependencies are installed
"""

import os
import sys
import subprocess
import importlib.util

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_python_version():
    """Check Python version"""
    print("=" * 60)
    print("Checking Python Version...")
    print("=" * 60)
    
    version = sys.version_info
    print(f"[OK] Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("[OK] Python version is compatible (3.7+)\n")
        return True
    else:
        print("[FAIL] Python version too old - need Python 3.7 or newer\n")
        return False


def check_python_packages():
    """Check required Python packages"""
    print("=" * 60)
    print("Checking Python Packages...")
    print("=" * 60)
    
    packages = {
        "pypandoc": "pypandoc",
        "beautifulsoup4": "bs4",
        "markdown": "markdown"
    }
    
    all_ok = True
    for package_name, import_name in packages.items():
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is not None:
                print(f"[OK] {package_name} is installed")
            else:
                print(f"[FAIL] {package_name} is NOT installed")
                all_ok = False
        except Exception:
            print(f"[FAIL] {package_name} is NOT installed")
            all_ok = False
    
    print()
    return all_ok


def check_calibre():
    """Check if Calibre is installed"""
    print("=" * 60)
    print("Checking Calibre (ebook-convert)...")
    print("=" * 60)
    
    possible_paths = [
        "/Applications/calibre.app/Contents/MacOS/ebook-convert",
        "/usr/bin/ebook-convert",
        "/usr/local/bin/ebook-convert",
        r"C:\Program Files\Calibre2\ebook-convert.exe",
        r"C:\Program Files (x86)\Calibre2\ebook-convert.exe",
        "ebook-convert"  # Check in PATH
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                print(f"[OK] Calibre ebook-convert found at: {path}")
                # Extract version info
                first_line = result.stdout.strip().split('\n')[0] if result.stdout else "Unknown version"
                print(f"  Version: {first_line}")
                print()
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("[FAIL] Calibre ebook-convert NOT found!")
    print("\nPlease install Calibre from: https://calibre-ebook.com/download")
    print()
    return False


def check_pandoc():
    """Check if Pandoc is installed"""
    print("=" * 60)
    print("Checking Pandoc...")
    print("=" * 60)
    
    try:
        result = subprocess.run(["pandoc", "--version"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            first_line = result.stdout.strip().split('\n')[0]
            print(f"[OK] Pandoc found: {first_line}")
            print()
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("[FAIL] Pandoc NOT found!")
    print("\nPlease install Pandoc from: https://pandoc.org/installing.html")
    print()
    return False


def main():
    """Main function to check environment"""
    print("\n" + "=" * 60)
    print("TRANSLATE-BOOK-TO-DOUBLE-LANGUAGE-FORMAT - ENVIRONMENT CHECK")
    print("=" * 60)
    print()
    
    results = {}
    results["Python Version"] = check_python_version()
    results["Python Packages"] = check_python_packages()
    results["Pandoc"] = check_pandoc()
    results["Calibre"] = check_calibre()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{check}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[OK] All dependencies are installed! Skill is ready to use.\n")
        return 0
    else:
        print("\n[FAIL] Some dependencies are missing. Please install them first.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

