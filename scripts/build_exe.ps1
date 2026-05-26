$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$AppName = "ChunkShare"
$VenvDir = Join-Path $Root ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$DistDir = Join-Path $Root "dist"
$AppDistDir = Join-Path $DistDir $AppName
$OutputExe = Join-Path $AppDistDir "$AppName.exe"

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

Write-Host "Building $AppName.exe..."
& $VenvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name $AppName `
    app.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host "Copying sample folders and docs..."
Copy-Item -Path (Join-Path $Root "sample_files") -Destination $AppDistDir -Recurse -Force
Copy-Item -Path (Join-Path $Root "torrents") -Destination $AppDistDir -Recurse -Force
Copy-Item -Path (Join-Path $Root "docs") -Destination $AppDistDir -Recurse -Force
Copy-Item -Path (Join-Path $Root "README.md") -Destination $AppDistDir -Force

New-Item -ItemType Directory -Force -Path (Join-Path $AppDistDir "downloads") | Out-Null

Write-Host ""
Write-Host "Build complete."
Write-Host "Run this file:"
Write-Host $OutputExe
