@echo off
echo ===================================================
echo     STARTING API SERVER
echo ===================================================
echo.
echo 1. Cleaning up old processes...
taskkill /F /IM python.exe 2>nul
timeout /t 1 /nobreak >nul

echo.
echo 2. Verifying Environment...
if not exist .env312\Scripts\python.exe (
    echo.
    echo ERROR: Virtual environment .env312 not found!
    echo Please run setup_fix.bat or ensure .env312 is present.
    pause
    exit /b 1
)

echo.
echo 3. Starting FastAPI Server...
echo    (Keep this window OPEN while using the frontend)
echo.
.env312\Scripts\python.exe backend/app.py

pause
