$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root

Write-Host "Starting full Docker ChunkShare demo..."
Write-Host "This runs tracker, seeder, leecher1, and leecher2 as separate containers."
Write-Host "Tracker dashboard: http://localhost:18000/dashboard"
Write-Host ""

& docker compose -f docker-compose.full.yml up --build
