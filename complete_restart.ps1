# Complete server restart script

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMPLETE SERVER RESTART"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any running uvicorn processes
Write-Host "[1/4] Stopping all uvicorn processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "  [OK] Processes stopped" -ForegroundColor Green

# Step 2: Activate venv and verify bcrypt
Write-Host ""
Write-Host "[2/4] Checking bcrypt version..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
$bcryptVersion = pip show bcrypt 2>$null | Select-String "Version"
Write-Host "  $bcryptVersion" -ForegroundColor White

if ($bcryptVersion -like "*4.0.1*") {
    Write-Host "  [OK] bcrypt 4.0.1 installed" -ForegroundColor Green
} else {
    Write-Host "  [FIXING] Installing bcrypt 4.0.1..." -ForegroundColor Yellow
    pip uninstall bcrypt -y | Out-Null
    pip install bcrypt==4.0.1 | Out-Null
    Write-Host "  [OK] bcrypt 4.0.1 installed" -ForegroundColor Green
}

# Step 3: Wait a moment
Write-Host ""
Write-Host "[3/4] Waiting for cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "  [OK] Ready to start" -ForegroundColor Green

# Step 4: Start server
Write-Host ""
Write-Host "[4/4] Starting server with fresh bcrypt..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SERVER STARTING"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your system at:" -ForegroundColor Cyan
Write-Host "  - Dashboard: http://localhost:8000/ui/index.html" -ForegroundColor White
Write-Host "  - Admin Panel: http://localhost:8000/ui/admin.html" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Login: admin / Admin@2024" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
