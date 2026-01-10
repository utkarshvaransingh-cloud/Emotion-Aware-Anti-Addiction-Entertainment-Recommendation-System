@echo off
echo ===================================================
echo     PYTHON 3.14 COMPATIBILITY FIX
echo ===================================================
echo.
echo You are running Python 3.14, which does not yet support 'pandas'.
echo You MUST install Python 3.12 for this project to work.
echo.
echo 1. Download Python 3.12 from: https://www.python.org/downloads/release/python-3120/
echo 2. During installation, check "Add Python to PATH".
echo 3. Once installed, run this script again.
echo.
echo Checking for Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3.12 NOT FOUND.
    echo Please install it and try again.
    pause
    exit /b 1
)

echo.
echo Python 3.12 found! Setting up environment...
rmdir /s /q .venv
py -3.12 -m venv .venv
call .venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running Verification Tests...
python tests/test_phase_5_addiction.py
python tests/test_phase_6_ranker.py

echo.
echo SUCCESS! You can now continue.
pause
