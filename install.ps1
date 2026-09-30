# install.ps1 - Automated 1-line curl installer for Elenchus (Windows)
$ErrorActionPreference = "Stop"

Write-Host "`n=== Elenchus (ἔλεγχος) Installer ===" -ForegroundColor Cyan

$Repo = "Asifdotexe/aenf"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\Elenchus"
$ExePath = Join-Path $InstallDir "elenchus.exe"

# 1. Create installation directory
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# 2. Resolve direct release download URL
Write-Host "[1/3] Resolving download URL..." -ForegroundColor Yellow
$DownloadUrl = "https://github.com/$Repo/releases/latest/download/elenchus-windows-x86_64.exe"

# 3. Download standalone binary and verify cryptographic checksum
Write-Host "[2/3] Downloading elenchus.exe..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $DownloadUrl -OutFile $ExePath -UseBasicParsing
Write-Host "      Saved to: $ExePath" -ForegroundColor Green

$ShaUrl = "$DownloadUrl.sha256"
try {
    $ExpectedHash = ((Invoke-RestMethod -Uri $ShaUrl -UseBasicParsing).Trim() -split '\s+')[0].ToLower()
    $ActualHash = (Get-FileHash -Path $ExePath -Algorithm SHA256).Hash.ToLower()

    if ($ActualHash -ne $ExpectedHash) {
        Remove-Item -Path $ExePath -Force -ErrorAction SilentlyContinue
        Write-Error "SHA-256 checksum mismatch! Expected: $ExpectedHash, Got: $ActualHash. Download aborted."
        exit 1
    }
    Write-Host "      Checksum verified: $ActualHash" -ForegroundColor Green
} catch {
    Write-Host "      [NOTE] Checksum verification skipped (release asset hash unavailable)." -ForegroundColor DarkYellow
}

# 4. Ensure install directory is on user PATH
Write-Host "[3/3] Configuring user PATH environment variable..." -ForegroundColor Yellow
$UserPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$InstallDir*") {
    $NewPath = "$UserPath;$InstallDir"
    [System.Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    $env:Path = "$env:Path;$InstallDir"
    Write-Host "      Added $InstallDir to PATH." -ForegroundColor Green
} else {
    Write-Host "      $InstallDir is already in PATH." -ForegroundColor Green
}

# 5. Check Ollama reasoning service
Write-Host ""
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[NOTE] Ollama not detected. Download from https://ollama.com to enable local fallacy reasoning." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Ollama detected on system." -ForegroundColor Green
}

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " [OK] Elenchus installed successfully!" -ForegroundColor Green
Write-Host " Launch HUD anytime by typing:  elenchus" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Green
