@echo off
echo ===================================================
echo     STARTING API SERVER
echo ===================================================
echo.
echo 1. Cleaning up old processes...
taskkill /F /IM python.exe 2>nul
timeout /t 1 /nobreak >nul

echo.
echo 2. Activating Environment...
call .env312\Scripts\activate

echo.
echo 3. Starting FastAPI Server...
echo    (Keep this window OPEN while using the frontend)
echo.
python backend/app.py

pause
