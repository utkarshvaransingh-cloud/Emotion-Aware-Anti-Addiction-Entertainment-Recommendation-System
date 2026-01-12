@echo off
echo Starting backend...
py -3.12 backend\app.py > backend_out.txt 2>&1
echo Done.
