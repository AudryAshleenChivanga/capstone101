@echo off
echo ========================================
echo H. pylori CDSS - Starting Server
echo ========================================
cd /d "C:\Users\Audry Ashleen\capstone101"
echo Current Directory: %CD%
echo.
echo Starting FastAPI server...
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
