# ==============================================
# H. pylori CDSS - Windows Deployment Script
# ==============================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  H. pylori CDSS - Production Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "[X] .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file from env.template:" -ForegroundColor Yellow
    Write-Host "  Copy-Item env.template .env"
    Write-Host "  notepad .env  # Edit with your actual values"
    exit 1
}

Write-Host "[OK] .env file found" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "[X] Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows" -ForegroundColor Yellow
    Write-Host "https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "[OK] Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "[X] Docker Compose is not installed!" -ForegroundColor Red
    exit 1
}

# Stop existing containers
Write-Host ""
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

Write-Host "[OK] Containers stopped" -ForegroundColor Green

# Build the Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker-compose build --no-cache

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker image built" -ForegroundColor Green
} else {
    Write-Host "[X] Failed to build Docker image" -ForegroundColor Red
    exit 1
}

# Start the containers
Write-Host ""
Write-Host "Starting containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Containers started" -ForegroundColor Green
} else {
    Write-Host "[X] Failed to start containers" -ForegroundColor Red
    exit 1
}

# Wait for the application to be ready
Write-Host ""
Write-Host "Waiting for application to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if the application is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] Application is running!" -ForegroundColor Green
} catch {
    Write-Host "[!] Application may not be ready yet. Checking logs..." -ForegroundColor Yellow
    docker-compose logs --tail=50
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor White
Write-Host "  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Dashboard: http://localhost:8000/ui/dashboard_new.html" -ForegroundColor Yellow
Write-Host "  Login: http://localhost:8000/ui/login.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "View logs:" -ForegroundColor White
Write-Host "  docker-compose logs -f" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stop the application:" -ForegroundColor White
Write-Host "  docker-compose down" -ForegroundColor Cyan
Write-Host ""

