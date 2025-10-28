@echo off
echo ================================================
echo   H. pylori CDSS - Starting Server
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo [3/3] Starting server...
echo.
echo ================================================
echo   SERVER STARTING!
echo ================================================
echo.
echo Access at: http://localhost:8000/ui/index.html
echo API docs at: http://localhost:8000/docs
echo.
echo Login Credentials:
echo   Username: admin
echo   Password: Admin@2024
echo.
echo Press Ctrl+C to stop
echo.
echo ================================================
echo.

python main.py
pause

