$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$Root'; python app.py"
)

Write-Host "App started. Use the dashboard to start seeding."
Write-Host "Then this script will run the Docker leecher."
Write-Host ""

& docker compose -f docker-compose.demo.yml up --build
