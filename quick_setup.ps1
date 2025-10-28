# Quick Setup Script for H. pylori CDSS
# This script starts the server and creates the admin account

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "H. pylori CDSS - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "Starting server in background..." -ForegroundColor Green

# Start server in background
$job = Start-Job -ScriptBlock {
    Set-Location $args[0]
    & .\.venv\Scripts\Activate.ps1
    uvicorn main:app --host 0.0.0.0 --port 8000
} -ArgumentList (Get-Location).Path

Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Check if server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ Server is running!" -ForegroundColor Green
} catch {
    Write-Host "Server is still starting..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "Creating admin account..." -ForegroundColor Yellow
python create_admin.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: Admin@2024" -ForegroundColor White
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000/ui/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the server later, press Ctrl+C in this window" -ForegroundColor Gray
Write-Host ""
