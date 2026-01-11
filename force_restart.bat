@echo off
echo ===================================================
echo   FORCE RESTARTING API SERVER
echo ===================================================
echo.
echo 1. Killing stuck Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 2. Starting API fresh...
call start_api.bat
