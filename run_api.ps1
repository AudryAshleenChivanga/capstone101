# PowerShell script to run H. pylori CDSS API

Write-Host "🏥 H. pylori CDSS - Starting API Server" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Check for .env file
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file with your configuration!" -ForegroundColor Yellow
}

# Check for models directory
if (-Not (Test-Path "models")) {
    Write-Host "⚠️  Warning: models directory not found. Creating..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "Please place your model files in the models/ directory!" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend UI at: http://localhost:8000/ui/index.html" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000