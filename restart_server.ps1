# Complete Server Restart Script with Fixed Dependencies

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  H. pylori CDSS - Clean Server Restart"
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Fix bcrypt
Write-Host "[2/4] Installing correct bcrypt version..." -ForegroundColor Yellow
pip uninstall bcrypt -y 2>$null
pip install bcrypt==4.0.1 --quiet

# Install all dependencies
Write-Host "[3/4] Verifying all dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host "[4/4] Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  SERVER READY!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access at: http://localhost:8000/ui/index.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Yellow
Write-Host "  Username: admin"
Write-Host "  Password: Admin@2024"
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
