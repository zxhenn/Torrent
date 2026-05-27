$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root

Write-Host "Starting only the Docker leecher."
Write-Host "Keep ChunkShare.exe open on the host as tracker/seeder."
Write-Host "In the host seed form for Docker tests, use:"
Write-Host "  Tracker URL: http://127.0.0.1:8000"
Write-Host "  This peer IP: host.docker.internal"
Write-Host "  Upload port: 9001"
Write-Host ""

& docker compose -f docker-compose.leecher.yml up --build
