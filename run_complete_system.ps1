# =========================================
# H. PYLORI CDSS - COMPLETE SYSTEM STARTUP
# Enhanced Features + Landing Page + All Systems
# Version 5.0 - Production Ready
# =========================================

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  H. PYLORI CDSS - COMPLETE SYSTEM" -ForegroundColor Cyan
Write-Host "  Starting All Systems..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in correct directory
if (!(Test-Path "main.py")) {
    Write-Host "❌ ERROR: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Current directory: $PWD" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/8] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Activating venv..." -ForegroundColor Green
    & venv\Scripts\Activate.ps1
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Activating .venv..." -ForegroundColor Green
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "  ⚠ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & venv\Scripts\Activate.ps1
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/8] Installing/updating dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "[4/8] Checking required directories..." -ForegroundColor Yellow
$directories = @(
    "uploads",
    "uploads/signatures",
    "uploads/pdfs",
    "logs",
    "models"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Exists: $dir" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[5/8] Verifying ML models..." -ForegroundColor Yellow
$models = @(
    "models/screening_hp_pos_calibrated.joblib",
    "models/staging_3class.joblib"
)

$modelsOk = $true
foreach ($model in $models) {
    if (Test-Path $model) {
        Write-Host "  ✓ Found: $model" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $model" -ForegroundColor Red
        $modelsOk = $false
    }
}

if (-not $modelsOk) {
    Write-Host ""
    Write-Host "⚠ WARNING: ML models not found!" -ForegroundColor Yellow
    Write-Host "  The system will start but AI features may not work." -ForegroundColor Yellow
    Write-Host "  Please ensure model files are in the models/ directory." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "[6/8] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
    
    # Check for critical settings
    $envContent = Get-Content .env -Raw
    if ($envContent -match "JWT_SECRET.*change_me") {
        Write-Host "  ⚠ WARNING: Using default JWT_SECRET!" -ForegroundColor Yellow
        Write-Host "    Please update .env with a secure JWT_SECRET for production" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path "env.template") {
        Copy-Item "env.template" ".env"
        Write-Host "  ✓ .env created. PLEASE CONFIGURE IT!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ env.template not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[7/8] Updating database schema..." -ForegroundColor Yellow
try {
    python -c "from app.db import create_tables; create_tables(); print('  ✓ Database tables updated')"
} catch {
    Write-Host "  ❌ Error updating database" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[8/8] Checking user accounts..." -ForegroundColor Yellow
$userCheck = python -c "from app.db import SessionLocal; from app.models import User; db = SessionLocal(); count = db.query(User).count(); print(count); db.close()" 2>&1

if ($userCheck -eq "0") {
    Write-Host "  ⚠ No users found in database" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  FIRST TIME SETUP DETECTED" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You need to create an admin user." -ForegroundColor White
    Write-Host ""
    
    $createNow = Read-Host "Create admin user now? (y/n)"
    
    if ($createNow -eq "y" -or $createNow -eq "Y") {
        Write-Host ""
        Write-Host "Creating admin user..." -ForegroundColor Yellow
        python direct_create_user.py
    } else {
        Write-Host ""
        Write-Host "⚠ You can create an admin user later by:" -ForegroundColor Yellow
        Write-Host "   1. Running: python direct_create_user.py" -ForegroundColor White
        Write-Host "   2. Or visit: http://localhost:8000/ui/index.html#signup" -ForegroundColor White
    }
} else {
    Write-Host "  ✓ Found $userCheck user(s) in database" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ PRE-FLIGHT CHECKS COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 SYSTEM FEATURES AVAILABLE:" -ForegroundColor Cyan
Write-Host "  ✓ Landing Page (Professional UI)" -ForegroundColor Green
Write-Host "  ✓ AI Screening & Staging" -ForegroundColor Green
Write-Host "  ✓ Digital Signatures" -ForegroundColor Green
Write-Host "  ✓ Profile Management" -ForegroundColor Green
Write-Host "  ✓ PDF Preview" -ForegroundColor Green
Write-Host "  ✓ Admin Panel" -ForegroundColor Green
Write-Host "  ✓ Video Consultation" -ForegroundColor Green
Write-Host "  ✓ Appointment Scheduling" -ForegroundColor Green
Write-Host "  ✓ SMS Notifications" -ForegroundColor Green
Write-Host "  ✓ Case Management" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 STARTING SERVER..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor White
Write-Host "  🏠 Landing Page:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  🔐 Login:         http://localhost:8000/ui/index.html" -ForegroundColor Cyan
Write-Host "  📊 Dashboard:     http://localhost:8000/ui/dashboard.html" -ForegroundColor Cyan
Write-Host "  📚 API Docs:      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ❤️  Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
try {
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host ""
    Write-Host "❌ Server error occurred" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check if port 8000 is already in use" -ForegroundColor White
    Write-Host "  2. Verify all dependencies are installed" -ForegroundColor White
    Write-Host "  3. Check server logs above for details" -ForegroundColor White
    exit 1
}

