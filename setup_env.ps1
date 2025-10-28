# PowerShell script to create .env file

Write-Host "🔧 H. pylori CDSS - Environment Setup" -ForegroundColor Cyan
Write-Host ""

# Check if .env already exists
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit
    }
}

# Create .env content
$envContent = @"
# H. pylori CDSS Configuration

# Model paths
SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH=models/staging_3class.joblib

# Screening threshold (0.0 to 1.0)
SCREEN_THRESH=0.60

# JWT secret key (CHANGE THIS IN PRODUCTION!)
JWT_SECRET=change_me_to_a_secure_random_string_dev_only

# CORS allowed origins (comma-separated)
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:8000,http://localhost:5500

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///./cdss.db
"@

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANT: Before running in production:" -ForegroundColor Yellow
Write-Host "   1. Change JWT_SECRET to a secure random string" -ForegroundColor Yellow
Write-Host "   2. Verify model paths are correct" -ForegroundColor Yellow
Write-Host "   3. Update ALLOWED_ORIGINS for your domain" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "   1. Ensure model files are in the models/ directory"
Write-Host "   2. Run: .\run_api.ps1"
Write-Host "   3. Open: http://localhost:8000/ui/index.html"
Write-Host ""
