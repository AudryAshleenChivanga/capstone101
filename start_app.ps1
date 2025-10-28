# Simple App Startup Script for H. pylori CDSS

Write-Host "========================================"
Write-Host "  H. PYLORI CDSS - Starting Server"
Write-Host "========================================"
Write-Host ""

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] Activating virtual environment..."
    & .venv\Scripts\Activate.ps1
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] Activating virtual environment..."
    & venv\Scripts\Activate.ps1
} else {
    Write-Host "[1/4] No virtual environment found, using system Python..."
}

Write-Host "[2/4] Checking dependencies..."
pip install -q -r requirements.txt

Write-Host "[3/4] Updating database..."
python -c "from app.db import create_tables; create_tables(); print('Database ready')"

Write-Host "[4/4] Starting server..."
Write-Host ""
Write-Host "Server will be available at:"
Write-Host "  Landing Page:  http://localhost:8000"
Write-Host "  Login:         http://localhost:8000/ui/index.html"
Write-Host "  Dashboard:     http://localhost:8000/ui/dashboard.html"
Write-Host "  3D Biopsy:     http://localhost:8000/ui/biopsy-simulation.html"
Write-Host "  API Docs:      http://localhost:8000/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host "========================================"
Write-Host ""

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

