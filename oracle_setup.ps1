# ================================================
# Oracle Cloud Setup Helper Script for Windows
# ================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$InstanceIP = ""
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Oracle Cloud Setup Helper" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to print colored messages
function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[X] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Cyan
}

# Step 1: Check prerequisites
Write-Host "Step 1: Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check if SSH is available
try {
    $sshVersion = ssh -V 2>&1
    Write-Success "SSH is available"
} catch {
    Write-Error-Custom "SSH is not available!"
    Write-Info "Please install OpenSSH Client from Windows Settings"
    exit 1
}

# Check if SCP is available
try {
    $scpCheck = Get-Command scp -ErrorAction Stop
    Write-Success "SCP is available"
} catch {
    Write-Error-Custom "SCP is not available!"
    exit 1
}

Write-Host ""

# Step 2: Generate SSH Key
Write-Host "Step 2: SSH Key Generation" -ForegroundColor Yellow
Write-Host ""

$sshDir = "$HOME\.ssh"
$keyPath = "$sshDir\oracle_key"
$pubKeyPath = "$keyPath.pub"

if (!(Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Success "Created .ssh directory"
}

if (Test-Path $keyPath) {
    Write-Warning-Custom "SSH key already exists at: $keyPath"
    $overwrite = Read-Host "Do you want to use the existing key? (Y/N)"
    if ($overwrite -eq "N" -or $overwrite -eq "n") {
        Write-Info "Generating new SSH key..."
        ssh-keygen -t rsa -b 4096 -f $keyPath -N """"
        Write-Success "SSH key generated!"
    }
} else {
    Write-Info "Generating SSH key..."
    ssh-keygen -t rsa -b 4096 -f $keyPath -N """"
    Write-Success "SSH key generated!"
}

# Set proper permissions on the key
Write-Info "Setting proper permissions on SSH key..."
icacls $keyPath /inheritance:r | Out-Null
icacls $keyPath /grant:r "$($env:USERNAME):(R)" | Out-Null
Write-Success "Permissions set"

Write-Host ""

# Display public key
Write-Host "========================================" -ForegroundColor Green
Write-Host "YOUR PUBLIC SSH KEY (copy this):" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Get-Content $pubKeyPath
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Info "1. Copy the public key above"
Write-Info "2. Go to Oracle Cloud Console"
Write-Info "3. Create a new Compute Instance"
Write-Info "4. Paste this public key when creating the instance"
Write-Host ""

# Step 3: Wait for user to create instance
Write-Host "Step 3: Oracle Instance Setup" -ForegroundColor Yellow
Write-Host ""

if ($InstanceIP -eq "") {
    Write-Info "Please create your Oracle Cloud instance with the public key above"
    $InstanceIP = Read-Host "Enter your Oracle Instance Public IP address"
}

Write-Success "Instance IP: $InstanceIP"
Write-Host ""

# Step 4: Test SSH connection
Write-Host "Step 4: Testing SSH Connection..." -ForegroundColor Yellow
Write-Host ""

Write-Info "Attempting to connect to: ubuntu@$InstanceIP"
Write-Warning-Custom "If this is your first time connecting, type YES when prompted"
Write-Host ""

$testConnection = Read-Host "Ready to test connection? (Y/N)"
if ($testConnection -eq "Y" -or $testConnection -eq "y") {
    Write-Info "Testing connection..."
    $result = ssh -i $keyPath -o "StrictHostKeyChecking=no" ubuntu@$InstanceIP "echo Connection successful; uname -a"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "SSH connection successful!"
        Write-Host $result
    } else {
        Write-Error-Custom "SSH connection failed!"
        Write-Info "Troubleshooting:"
        Write-Info "  1. Check if instance is running in Oracle Cloud Console"
        Write-Info "  2. Verify Security Rules allow SSH (port 22)"
        Write-Info "  3. Check if you used the correct public key"
        Write-Info "  4. Wait a few more minutes for instance to fully start"
        exit 1
    }
}

Write-Host ""

# Step 5: Save connection info
Write-Host "Step 5: Saving Connection Information..." -ForegroundColor Yellow
Write-Host ""

$connectionFile = "oracle_connection_info.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$connectionInfo = @"
================================================
Oracle Cloud Connection Information
================================================
Generated: $timestamp

Instance IP: $InstanceIP
SSH Key: $keyPath
Username: ubuntu

SSH Command:
  ssh -i "$keyPath" ubuntu@$InstanceIP

SCP Command (copy files to server):
  scp -i "$keyPath" -r ./* ubuntu@${InstanceIP}:~/hpylori-cdss/

Application URLs (after deployment):
  Main App: http://$InstanceIP:8000
  Health: http://$InstanceIP:8000/health
  API Docs: http://$InstanceIP:8000/docs
  Login: http://$InstanceIP:8000/ui/login.html

================================================
Next Steps:
================================================

1. Install Docker on Oracle instance
2. Install Docker Compose
3. Configure firewall
4. Transfer files
5. Deploy application

See ORACLE_STEP_BY_STEP.md for detailed instructions

================================================
"@

$connectionInfo | Out-File -FilePath $connectionFile -Encoding UTF8
Write-Success "Connection info saved to: $connectionFile"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Success "Your SSH key is ready"
Write-Success "Connection tested successfully"
Write-Success "Connection info saved to: $connectionFile"
Write-Host ""

Write-Info "Quick Commands:"
Write-Host ""
Write-Host "Connect to Oracle instance:" -ForegroundColor Cyan
Write-Host "  ssh -i `"$keyPath`" ubuntu@$InstanceIP" -ForegroundColor White
Write-Host ""
Write-Host "Transfer files to Oracle:" -ForegroundColor Cyan
Write-Host "  scp -i `"$keyPath`" -r ./* ubuntu@${InstanceIP}:~/hpylori-cdss/" -ForegroundColor White
Write-Host ""

Write-Info "Next: Follow ORACLE_STEP_BY_STEP.md for deployment steps"
Write-Host ""

# Offer to connect now
$connectNow = Read-Host "Do you want to connect to your Oracle instance now? (Y/N)"
if ($connectNow -eq "Y" -or $connectNow -eq "y") {
    Write-Info "Connecting to Oracle instance..."
    ssh -i $keyPath ubuntu@$InstanceIP
}

Write-Host ""
Write-Host "Ready to deploy!" -ForegroundColor Green
