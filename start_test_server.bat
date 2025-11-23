@echo off
echo Starting H. pylori CDSS Test Server...
echo.
echo Server will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/ui/signup.html (signup page)
echo   http://localhost:8000/ui/login.html (login page)
echo.
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

