@echo off
echo ===================================================
echo     LAUNCHING DASHBOARD
echo ===================================================

echo 1. Activating Environment (.env312)...
call .env312\Scripts\activate

echo.
echo 2. Ensuring Streamlit is installed...
python -m pip install streamlit

echo.
echo 3. Starting App...
python -m streamlit run src/dashboard/app.py --server.address localhost

pause
