# =========================================
# INTEGRATE ENHANCED FEATURES INTO DASHBOARD
# Automatically adds all enhanced features to dashboard.html
# =========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " INTEGRATING ENHANCED FEATURES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Backup existing dashboard
if (Test-Path "ui/dashboard.html") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = "ui/dashboard_backup_$timestamp.html"
    Copy-Item "ui/dashboard.html" $backupPath
    Write-Host "✓ Backup created: $backupPath" -ForegroundColor Green
}

# Read dashboard content
$dashboardContent = Get-Content "ui/dashboard.html" -Raw

# Check if enhanced features are already integrated
if ($dashboardContent -match "signature_pad|app_enhanced") {
    Write-Host "⚠ Enhanced features appear to be already integrated" -ForegroundColor Yellow
    $response = Read-Host "Re-integrate anyway? (y/n)"
    if ($response -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Gray
        exit 0
    }
}

Write-Host ""
Write-Host "[1/3] Adding Signature Pad library..." -ForegroundColor Yellow

# Add signature pad library before closing body tag if not present
if ($dashboardContent -notmatch "signature_pad") {
    $signaturePadScript = @"
    <!-- Signature Pad Library -->
    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.1.7/dist/signature_pad.umd.min.js"></script>
"@
    
    $dashboardContent = $dashboardContent -replace "</body>", "$signaturePadScript`n</body>"
    Write-Host "  ✓ Signature Pad library added" -ForegroundColor Green
} else {
    Write-Host "  ✓ Signature Pad already present" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/3] Adding Enhanced JavaScript..." -ForegroundColor Yellow

if ($dashboardContent -notmatch "app_enhanced") {
    $enhancedScript = @"
    <!-- Enhanced Features JavaScript -->
    <script src="app_enhanced.js?v=5.0"></script>
"@
    
    $dashboardContent = $dashboardContent -replace "</body>", "$enhancedScript`n</body>"
    Write-Host "  ✓ Enhanced JavaScript added" -ForegroundColor Green
} else {
    Write-Host "  ✓ Enhanced JavaScript already present" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[3/3] Adding Enhanced UI Elements..." -ForegroundColor Yellow

# Read enhanced elements
if (Test-Path "ui/dashboard_enhanced_elements.html") {
    $enhancedElements = Get-Content "ui/dashboard_enhanced_elements.html" -Raw
    
    # Remove HTML boilerplate if present
    $enhancedElements = $enhancedElements -replace "(?s)^.*?(?=<!--)", ""
    
    # Add before closing body tag
    $dashboardContent = $dashboardContent -replace "</body>", "$enhancedElements`n</body>"
    Write-Host "  ✓ Enhanced UI elements added" -ForegroundColor Green
} else {
    Write-Host "  ❌ dashboard_enhanced_elements.html not found" -ForegroundColor Red
}

# Write updated dashboard
Set-Content "ui/dashboard.html" $dashboardContent -NoNewline

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ✅ INTEGRATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Enhanced features added to dashboard:" -ForegroundColor White
Write-Host "  ✓ Digital Signature Pad" -ForegroundColor Green
Write-Host "  ✓ Profile Editor UI" -ForegroundColor Green
Write-Host "  ✓ PDF Preview Modal" -ForegroundColor Green
Write-Host "  ✓ Admin Panel Interface" -ForegroundColor Green
Write-Host "  ✓ Enhanced Error Handling" -ForegroundColor Green
Write-Host "  ✓ Toast Notifications" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Clear browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  2. Start server: .\run_complete_system.ps1" -ForegroundColor White
Write-Host "  3. Visit: http://localhost:8000" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

