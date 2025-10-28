# PowerShell script to install enhanced professional features

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  H. pylori CDSS - Enhanced Features Setup"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Activate virtual environment
Write-Host "[1/6] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path .venv) {
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "ERROR: Virtual environment not found. Run .\run_api.ps1 first!" -ForegroundColor Red
    exit 1
}

# Step 2: Install new dependencies
Write-Host "[2/6] Installing new packages..." -ForegroundColor Yellow
pip install reportlab==4.0.9 twilio==8.11.1 pillow==10.1.0 aiofiles==23.2.1 --quiet
Write-Host "  Packages installed!" -ForegroundColor Green

# Step 3: Create upload directories
Write-Host "[3/6] Creating upload directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path uploads/signatures | Out-Null
New-Item -ItemType Directory -Force -Path uploads/pdfs | Out-Null
New-Item -ItemType Directory -Force -Path uploads/profiles | Out-Null
Write-Host "  Directories created!" -ForegroundColor Green

# Step 4: Update .env file
Write-Host "[4/6] Updating .env configuration..." -ForegroundColor Yellow
if (!(Test-Path .env)) {
    Write-Host "  ERROR: .env file not found!" -ForegroundColor Red
    exit 1
}

$envContent = Get-Content .env -Raw

# Add new config if not present
if ($envContent -notmatch "TWILIO_ACCOUNT_SID") {
    Add-Content .env "`n# Twilio Configuration (for real SMS)"
    Add-Content .env "TWILIO_ACCOUNT_SID=your_account_sid_here"
    Add-Content .env "TWILIO_AUTH_TOKEN=your_auth_token_here"
    Add-Content .env "TWILIO_PHONE_NUMBER=+1234567890"
    Add-Content .env "`n# File Storage"
    Add-Content .env "UPLOAD_DIR=uploads"
    Add-Content .env "SIGNATURES_DIR=uploads/signatures"
    Add-Content .env "PDF_DIR=uploads/pdfs"
    Write-Host "  Configuration added to .env!" -ForegroundColor Green
} else {
    Write-Host "  Configuration already exists!" -ForegroundColor Green
}

# Step 5: Update database schema
Write-Host "[5/6] Updating database schema..." -ForegroundColor Yellow
python -c "from app.db import create_tables; create_tables(); print('  Database updated!')"

# Step 6: Verify installation
Write-Host "[6/6] Verifying installation..." -ForegroundColor Yellow
$testResult = python -c "
try:
    from app.utils.pdf_generator import generate_recommendation_pdf
    from app.utils.sms_sender import SMSSender
    from app.routes_profile import router
    print('  All modules loaded successfully!')
except Exception as e:
    print(f'  ERROR: {e}')
"
Write-Host $testResult -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "New Features Available:" -ForegroundColor Yellow
Write-Host "  Profile Management     - http://localhost:8000/profile/me" -ForegroundColor White
Write-Host "  Digital Signatures     - Upload via profile" -ForegroundColor White
Write-Host "  PDF Generation         - Automatic for all cases" -ForegroundColor White
Write-Host "  Real SMS via Twilio    - Configure in .env" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env and add your Twilio credentials (optional)" -ForegroundColor White
Write-Host "  2. Restart the server: uvicorn main:app --reload" -ForegroundColor White
Write-Host "  3. Update your profile: http://localhost:8000/profile/me" -ForegroundColor White
Write-Host "  4. Upload your digital signature" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  See INSTALL_ENHANCED_FEATURES.md for details" -ForegroundColor White
Write-Host "  See IMPLEMENTATION_GUIDE.md for full features" -ForegroundColor White
Write-Host ""
