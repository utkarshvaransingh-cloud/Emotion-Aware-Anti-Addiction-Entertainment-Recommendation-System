@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running Phase 5 Tests (Anti-Addiction)...
python tests/test_phase_5_addiction.py

echo.
echo Running Phase 6 Tests (Final Ranker)...
python tests/test_phase_6_ranker.py

echo.
echo Done.
pause
