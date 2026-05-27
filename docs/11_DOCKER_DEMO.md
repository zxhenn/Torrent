# 11 - Docker Demo (Extra Peer On One Laptop)

This guide runs the ChunkShare app on the host and a leecher inside Docker to simulate a second device.

## Requirements

- Windows with Docker Desktop running
- Python 3.10+ on the host (for the app dashboard)

## Step 1: Start the app on the host

From the project folder:

```powershell
python app.py
```

The dashboard opens in your browser.

## Step 2: Start the seeder in the dashboard

Use the right-side `Seed Complete File` panel with the sample file:

```text
.mtorrent path: torrents/hello.txt.mtorrent
Complete file path: sample_files/hello.txt
Upload port: 9001
```

Important for Docker:

- Set `This peer IP` to `host.docker.internal`
- Keep `Tracker URL` as shown by the dashboard (usually `http://127.0.0.1:8000`)

Click `Start Seed`.

## Step 3: Run the Docker leecher

In a new PowerShell window, run:

```powershell
docker compose -f docker-compose.demo.yml up --build
```

Or use the one-click script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_docker_demo.ps1
```

This starts a leecher container that:

- Reads `torrents/hello.txt.mtorrent`
- Downloads to `downloads/hello-docker.txt`
- Connects to the host tracker at `http://host.docker.internal:8000`
- Stays online and keeps seeding after download

## Verify

- The host dashboard shows a leecher peer.
- The file appears at `downloads/hello-docker.txt` on the host.

## Stop

Press `Ctrl+C` in the Docker terminal, then:

```powershell
docker compose -f docker-compose.demo.yml down
```

## Notes

- This setup is intended for one-laptop demos only.
- If you want multiple real devices, use the normal LAN steps in the main guide.
