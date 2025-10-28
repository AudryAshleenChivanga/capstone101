# Complete Server Restart Script
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "RESTARTING SERVER WITH FRESH FILES" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Kill any existing uvicorn processes
Write-Host "Killing existing server processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting fresh server..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment and start server
if (Test-Path .venv) {
    .\.venv\Scripts\Activate.ps1
    
    Write-Host "Server starting on port 8000..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "IMPORTANT: After server starts, open these URLs IN ORDER:" -ForegroundColor Yellow
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "1. FIRST: http://localhost:8000/ui/test_new.html" -ForegroundColor Cyan
    Write-Host "   (Should show purple page with SUCCESS message)" -ForegroundColor White
    Write-Host ""
    Write-Host "2. THEN: Click the button to go to dashboard" -ForegroundColor Cyan
    Write-Host "   OR go directly to: http://localhost:8000/ui/dashboard.html" -ForegroundColor White
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: python -m venv .venv" -ForegroundColor Yellow
}
