# ========================================
# H. PYLORI CDSS - ENHANCED FEATURES SETUP
# Automated setup script for Windows
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " H. PYLORI CDSS - ENHANCED FEATURES" -ForegroundColor Cyan
Write-Host " Signature Pad | Profile Editor | PDF | Admin" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running in correct directory
if (!(Test-Path "main.py")) {
    Write-Host "ERROR: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "[1/6] Checking Python environment..." -ForegroundColor Yellow

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Activating virtual environment..." -ForegroundColor Green
    & venv\Scripts\Activate.ps1
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Activating virtual environment..." -ForegroundColor Green
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "  ! Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "[2/6] Installing required packages..." -ForegroundColor Yellow
Write-Host "  - signature_pad (via CDN - no install needed)" -ForegroundColor Gray
Write-Host "  - All Python dependencies from requirements.txt" -ForegroundColor Gray
pip install -q -r requirements.txt

Write-Host ""
Write-Host "[3/6] Creating upload directories..." -ForegroundColor Yellow
$directories = @("uploads", "uploads/signatures", "uploads/pdfs", "logs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Exists: $dir" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[4/6] Setting up environment configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Write-Host "  ! Creating .env from template..." -ForegroundColor Yellow
    Copy-Item "env.template" ".env"
    Write-Host "  ✓ .env file created - PLEASE EDIT WITH YOUR VALUES!" -ForegroundColor Green
    Write-Host "  → Edit .env file with your Twilio credentials and JWT secret" -ForegroundColor Cyan
} else {
    Write-Host "  ✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "[5/6] Updating database schema..." -ForegroundColor Yellow
try {
    python -c "from app.db import create_tables; create_tables(); print('  ✓ Database tables updated')"
} catch {
    Write-Host "  ! Error updating database" -ForegroundColor Red
    Write-Host "  → Run manually: python -c `"from app.db import create_tables; create_tables()`"" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[6/6] Verifying installation..." -ForegroundColor Yellow

# Check if enhanced files exist
$requiredFiles = @(
    "ui/app_enhanced.js",
    "ui/dashboard_enhanced_elements.html",
    "app/routes_admin.py",
    "env.template",
    "PRODUCTION_DEPLOYMENT_GUIDE.md",
    "INTEGRATION_GUIDE.md"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (MISSING)" -ForegroundColor Red
        $allFilesExist = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allFilesExist) {
    Write-Host " ✅ SETUP COMPLETE!" -ForegroundColor Green
} else {
    Write-Host " ⚠ SETUP INCOMPLETE - Some files missing" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. INTEGRATE FEATURES INTO DASHBOARD:" -ForegroundColor Yellow
Write-Host "   → Follow instructions in INTEGRATION_GUIDE.md" -ForegroundColor White
Write-Host "   → Add scripts to dashboard.html:" -ForegroundColor White
Write-Host "     <script src=`"https://cdn.jsdelivr.net/npm/signature_pad@4.1.7/dist/signature_pad.umd.min.js`"></script>" -ForegroundColor Gray
Write-Host "     <script src=`"app_enhanced.js?v=5.0`"></script>" -ForegroundColor Gray
Write-Host ""

Write-Host "2. CONFIGURE ENVIRONMENT:" -ForegroundColor Yellow
Write-Host "   → Edit .env file with your settings" -ForegroundColor White
Write-Host "   → Set JWT_SECRET (generate with: openssl rand -hex 32)" -ForegroundColor White
Write-Host "   → Add Twilio credentials for SMS features" -ForegroundColor White
Write-Host ""

Write-Host "3. CREATE ADMIN USER (if not exists):" -ForegroundColor Yellow
Write-Host "   → Run: python direct_create_user.py" -ForegroundColor White
Write-Host ""

Write-Host "4. START THE SERVER:" -ForegroundColor Yellow
Write-Host "   → Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "   → Or: .\run_api.ps1" -ForegroundColor White
Write-Host ""

Write-Host "5. ACCESS THE APPLICATION:" -ForegroundColor Yellow
Write-Host "   → Dashboard: http://localhost:8000/ui/dashboard.html" -ForegroundColor White
Write-Host "   → API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "📚 DOCUMENTATION:" -ForegroundColor Cyan
Write-Host "   → INTEGRATION_GUIDE.md - How to integrate new features" -ForegroundColor White
Write-Host "   → PRODUCTION_DEPLOYMENT_GUIDE.md - Deploy to production" -ForegroundColor White
Write-Host "   → env.template - Environment variables reference" -ForegroundColor White
Write-Host ""

Write-Host "🎯 NEW FEATURES AVAILABLE:" -ForegroundColor Cyan
Write-Host "   ✅ Digital Signature Pad" -ForegroundColor Green
Write-Host "   ✅ Profile Editor with Signature Upload" -ForegroundColor Green
Write-Host "   ✅ PDF Document Preview" -ForegroundColor Green
Write-Host "   ✅ Admin Panel for User Management" -ForegroundColor Green
Write-Host "   ✅ Enhanced Error Handling & Toast Notifications" -ForegroundColor Green
Write-Host "   ✅ Production Configuration Templates" -ForegroundColor Green
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

