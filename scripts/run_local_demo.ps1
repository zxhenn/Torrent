$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = "python"
$Torrent = "torrents/hello.txt.mtorrent"
$Source = "sample_files/hello.txt"
$Download = "downloads/hello-local-demo.txt"

Set-Location $Root

if (Test-Path $Download) {
    Remove-Item -LiteralPath $Download -Force
}

if (Test-Path "$Download.progress.json") {
    Remove-Item -LiteralPath "$Download.progress.json" -Force
}

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$Root'; $Python -m mini_torrent.cli tracker --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$Root'; $Python -m mini_torrent.cli seed $Torrent --file $Source --host 127.0.0.1 --port 9001 --peer-id local-demo-seeder"
)

Start-Sleep -Seconds 2

Start-Process "http://127.0.0.1:8000/dashboard"

& $Python -m mini_torrent.cli leech $Torrent --output $Download --host 127.0.0.1 --port 9002 --peer-id local-demo-leecher --exit-when-done

Write-Host ""
Write-Host "Local demo finished. Tracker and seeder windows stay open so the dashboard still works."
Write-Host "Close those windows or press Ctrl+C inside them when done."

