@echo off
echo ===================================================
echo     FORCE PYTHON 3.12 SETUP
echo ===================================================

echo 1. Checking for Python 3.12...
py -3.12 --version
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12 is not detected!
    echo Please ensure you installed Python 3.12 and checked "Add to PATH".
    pause
    exit /b 1
)

echo.
echo 2. Creating a FRESH virtual environment (.env312)...
:: Using a new name to avoid "Access is denied" errors on the old folder
if exist .env312 rmdir /s /q .env312
py -3.12 -m venv .env312

echo.
echo 3. Activating environment...
call .env312\Scripts\activate

echo.
echo 4. Verifying Python Version in environment...
python --version
:: Should say Python 3.12.x

echo.
echo 5. Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 6. Running Tests...
python tests/test_phase_5_addiction.py
python tests/test_phase_6_ranker.py

echo.
echo ===================================================
echo If you see "OK" above, the environment is fixed!
echo To use this environment in the future, run:
echo    .env312\Scripts\activate
echo ===================================================
pause
