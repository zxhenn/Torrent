$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root

Write-Host "Starting only the Docker seeder."
Write-Host "Keep ChunkShare.exe open on the host as the tracker/dashboard."
Write-Host "In the host leech form, use the normal local tracker URL:"
Write-Host "  Tracker URL: http://127.0.0.1:8000"
Write-Host "The Docker seeder announces as 127.0.0.1:9011 by default."
Write-Host ""

& docker compose -f docker-compose.manual.yml up --build docker-seeder
