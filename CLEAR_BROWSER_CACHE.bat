@echo off
echo ========================================
echo    CLEAR BROWSER CACHE - WINDOWS
echo ========================================
echo.
echo Your browser is loading OLD cached files.
echo The server has NEW code but browser won't download it.
echo.
echo DO ONE OF THESE:
echo.
echo OPTION 1: Clear Chrome/Edge Cache
echo --------------------------------
echo 1. Press: Ctrl + Shift + Delete
echo 2. Select: "All time"
echo 3. Check: "Cached images and files"
echo 4. Click: "Clear data"
echo.
echo OPTION 2: Use Incognito
echo ------------------------
echo 1. Press: Ctrl + Shift + N
echo 2. Go to: http://127.0.0.1:8000/ui/login.html
echo.
echo OPTION 3: Start Fresh Browser
echo ------------------------------
echo This batch file will help...
echo.
pause

echo.
echo Killing browser processes...
taskkill /F /IM chrome.exe 2>nul
taskkill /F /IM msedge.exe 2>nul
taskkill /F /IM firefox.exe 2>nul

echo.
echo Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo.
echo Starting Chrome in Incognito with no cache...
start chrome --incognito --disable-cache http://127.0.0.1:8000/ui/login.html

echo.
echo ✅ Chrome opened in Incognito mode!
echo.
echo Login as: admin / Admin@2024
echo Then go to Case History
echo.
echo You WILL see the Sign/PDF buttons now!
echo.
pause

