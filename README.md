# ChunkShare Distributed File Sharing Demo

ChunkShare is a simple Python project that demonstrates torrent-like file sharing for a distributed computing class.

It supports:

- Hashing with SHA-256
- Chunking files into fixed-size pieces
- Seeding complete files
- Leeching missing chunks
- Peer discovery through a tracker
- App-style dashboard with seed/leech controls
- A leecher becoming a seeder after download

It is intentionally not a full BitTorrent implementation. The goal is to make the main concepts easy to run, inspect, and explain.

## Requirements

- Python 3.10 or newer
- No external packages for normal Python runs
- PyInstaller is installed automatically into `.venv` only when building the EXE

## Quick Start

Open PowerShell in this project folder.

### App Dashboard

Run the app:

```powershell
python app.py
```

Or run the built EXE:

```text
dist/ChunkShare/ChunkShare.exe
```

ChunkShare opens a dashboard in your browser immediately. From the dashboard, you can:

- Create `.mtorrent` metadata
- Start seeding a complete file
- Start leeching/downloading a file
- Use `Select` and `Save As` buttons instead of manually typing long file paths
- Stop, resume, and delete local jobs
- View active torrents, seeders, leechers, peers, and chunk availability

On Windows, you can also double-click:

```text
start_app.bat
```

For a one-laptop demo, you can also run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_local_demo.ps1
```

### Build a Windows EXE

If you want a Windows executable for demos, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

This creates:

```text
dist/ChunkShare/ChunkShare.exe
```

The build script uses PyInstaller inside a local `.venv` folder.

### 1. Use The Included Sample File

The project already includes `sample_files/hello.txt` so the demo can run immediately.

### 2. Open The App

```powershell
python app.py
```

The dashboard opens before anything is seeded or downloaded.

### 3. Seed From The Dashboard

Use the right-side `Seed Complete File` panel.

Default sample values:

```text
.mtorrent path: torrents/hello.txt.mtorrent
Complete file path: sample_files/hello.txt
Upload port: 9001
```

For your own files, click `Select` beside `.mtorrent path` and `Complete file path`.

Click `Start Seed`.

### 4. Leech From The Dashboard

Use the right-side `Download File` panel.

Default sample values:

```text
.mtorrent path: torrents/hello.txt.mtorrent
Output file path: downloads/hello.txt
Upload port: 9002
```

For your own downloads, click `Select` beside `.mtorrent path` and `Save As` beside `Output file path`.

Click `Start Leech`.

The dashboard table updates as peers announce chunks.

## Optional CLI Commands

The app dashboard is the recommended way to run ChunkShare. These commands are still available for testing and debugging.

### Create a torrent metadata file

```powershell
python -m mini_torrent.cli create-torrent <file> [--chunk-size 262144] [--output torrents/file.mtorrent]
```

### Run tracker directly

```powershell
python -m mini_torrent.cli tracker --host 127.0.0.1 --port 8000
```

### Seed a file

```powershell
python -m mini_torrent.cli seed <torrent> --file <complete-file> --host 127.0.0.1 --port 9001
```

### Leech a file

```powershell
python -m mini_torrent.cli leech <torrent> --output downloads/file --host 127.0.0.1 --port 9002
```

## Testing Across Devices

Run the app on each laptop.

Basic LAN flow:

1. Connect all laptops to the same Wi-Fi or hotspot.
2. On the hub laptop, open ChunkShare and copy the tracker URL shown in the toolbar/details.
3. On the seeder laptop, open ChunkShare and paste that tracker URL into `Seed Complete File`.
4. On the leecher laptop, open ChunkShare and paste that tracker URL into `Download File`.
5. Start the seeder first, then start the leecher.
6. Open the hub laptop dashboard to watch seeders, leechers, peers, and chunks.

If the devices cannot connect, allow Python or `ChunkShare.exe` through Windows Firewall.

After a leecher finishes downloading, it has the complete file and becomes a seeder if it stays online. So the next user can download chunks from the original seeder and from the previous leecher.

Quick troubleshooting:

- If the hub dashboard does not show the seeder, the seeder is not reaching the tracker URL.
- If the hub shows the seeder and leecher but no chunks download, open `http://SEEDER_IP:SEEDER_PORT/health` from the leecher laptop.
- If that health URL fails, check the seeder's `This peer IP`, upload port, and Windows Firewall.

## One-Laptop Docker Demo

If your class requires Docker, run the full Docker demo:

```powershell
docker compose -f docker-compose.full.yml up --build
```

This starts a tracker, seeder, and two leechers as separate containers.

Open:

```text
http://localhost:18000/dashboard
```

If you want to keep the Windows app dashboard and run only one Docker leecher, use `docker-compose.demo.yml`.

If you want manual control with `ChunkShare.exe`, use the separate seeder/leecher Compose files:

```powershell
docker compose -f docker-compose.leecher.yml up --build
docker compose -f docker-compose.seeder.yml up --build
```

See [docs/11_DOCKER_DEMO.md](docs/11_DOCKER_DEMO.md).

## Build A Windows EXE

Folder build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Output:

```text
dist/ChunkShare/ChunkShare.exe
```

Send the whole `dist/ChunkShare/` folder for this version.

Single-file build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_onefile_exe.ps1
```

Output:

```text
dist/ChunkShare.exe
```

Send this one if you want to give classmates only one executable file.

## Documentation

- `docs/00_TORRENTING_CONCEPT.md` - general explanation of torrenting concepts
- `docs/01_PROJECT_PLAN.md` - what we will do, what is done, and what should be done next
- `docs/02_IMPLEMENTATION_TASKS.md` - checklist of implemented and pending tasks
- `docs/03_HOW_THE_SYSTEM_WORKS.md` - descriptive explanation of the whole system
- `docs/04_SYSTEM_WORKFLOW.md` - command workflow for demo and LAN testing
- `docs/05_TECHNICAL_EXPLANATION.md` - technical details of hashing, chunking, tracker, seeder, and leecher
- `docs/06_CODE_REFERENCE.md` - file-by-file and function-by-function explanation
- `docs/07_TESTING_ACROSS_DEVICES.md` - practical LAN test guide
- `docs/08_BUILDING_EXE.md` - how to build `ChunkShare.exe`
- `docs/09_AI_HANDOFF_PROMPT.md` - handoff context for another AI assistant
- `docs/10_HOW_TO.md` - step-by-step guide for classmates running the demo
- `docs/11_DOCKER_DEMO.md` - Docker-based demo instructions
