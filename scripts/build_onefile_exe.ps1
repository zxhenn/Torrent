$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$AppName = "ChunkShare"
$VenvDir = Join-Path $Root ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$OutputExe = Join-Path $Root "dist\$AppName.exe"

Set-Location $Root

$RunningApp = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -eq "$AppName.exe" -and
        $_.CommandLine -like "*$OutputExe*"
    }

if ($RunningApp) {
    throw "$AppName.exe is currently running from dist. Close it before building again."
}

$SystemPython = "python"
try {
    & $SystemPython --version | Out-Null
}
catch {
    $SystemPython = "py"
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating local build environment..."
    & $SystemPython -m venv $VenvDir
}

Write-Host "Installing build tool..."
& $VenvPython -m pip install --upgrade pip pyinstaller

Write-Host "Building one-file $AppName.exe..."
& $VenvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --name $AppName `
    app.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "One-file build complete."
Write-Host "Send this file:"
Write-Host $OutputExe

