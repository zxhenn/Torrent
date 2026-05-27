# 09 - AI Handoff Prompt

Use this document as the first message/context for another AI assistant that will continue this project.

## Project Name

ChunkShare

## Project Goal

ChunkShare is a student-friendly distributed file sharing project inspired by torrenting.

It does not need to implement the real BitTorrent protocol. The goal is to demonstrate the important distributed computing concepts:

- Hashing
- Chunking
- Seeding
- Leeching
- Peer discovery through a tracker/hub
- Peer-to-peer chunk transfer
- A leecher becoming a seeder after download

The implementation should stay understandable for a third-year student. Prefer simple, robust code over complex production torrent behavior.

## Current User Expectation

The user does not want a purely terminal/manual workflow.

The expected experience is now:

```text
Open ChunkShare.exe
Dashboard opens
User can create metadata, seed, and leech from the dashboard
Dashboard shows torrent-like rows, peers, seeders, leechers, and chunks
```

The user wants the app to feel closer to a lightweight torrent client dashboard, similar in spirit to uTorrent, but much simpler.

## Current Architecture

The project is Python standard-library based.

Important folders and files:

```text
app.py
mini_torrent/
  app_dashboard.py
  cli.py
  constants.py
  dashboard.py
  downloader.py
  hashing.py
  metadata.py
  peer_server.py
  storage.py
  tracker.py
  tracker_client.py
docs/
sample_files/
torrents/
downloads/
scripts/
dist/ChunkShare/ChunkShare.exe
```

## Main App Flow

`app.py` is now the main app entry point.

It:

1. Starts a local ChunkShare dashboard app server.
2. Starts a local hub/tracker automatically.
3. Opens the dashboard in the browser.
4. Exposes app API routes for dashboard actions.
5. Lets the dashboard start local seeders and leechers.

Main dashboard URL:

```text
http://127.0.0.1:<app_port>/app
```

The tracker/hub URL for LAN peers is shown by the app, usually:

```text
http://LAN_IP:8000
```

## Core Concepts To Preserve

### Metadata

`.mtorrent` files are JSON metadata files.

They contain:

- filename
- file size
- chunk size
- whole-file SHA-256 hash
- per-chunk SHA-256 hashes

### Hashing

Use SHA-256.

Every downloaded chunk must be verified before saving.

The final completed file must be verified against the whole-file hash.

### Chunking

Files are split into fixed-size chunks.

The final chunk can be smaller.

### Tracker/Hub

The tracker does not store files.

It stores:

- peer ID
- host
- port
- file hash
- available chunk indexes
- file metadata for dashboard display

It helps peers find each other.

### Seeder

A seeder has the complete file and uploads chunks.

### Leecher

A leecher downloads missing chunks.

After download completes, it should keep announcing and become a seeder if it stays online.

## Important Existing Files

### `app.py`

Main dashboard app.

Contains:

- `ManagedPeer`
- `AppState`
- `AppRequestHandler`
- `run_app`

This is the main file to modify if improving the app dashboard behavior.

### `mini_torrent/app_dashboard.py`

Contains the HTML/CSS/JavaScript for the app-style dashboard.

This is the main file to modify if improving the UI.

### `mini_torrent/tracker.py`

Tracker/hub server.

Important endpoints:

- `GET /health`
- `GET /peers`
- `POST /announce`
- `GET /api/state`
- `GET /dashboard`

### `mini_torrent/peer_server.py`

Peer upload server.

Important endpoints:

- `GET /health`
- `GET /bitfield`
- `GET /chunk`

### `mini_torrent/downloader.py`

Leecher download logic.

Downloads chunks from peers, verifies them, and writes them to storage.

### `mini_torrent/storage.py`

Handles chunk reading, writing, verification, progress, and final file verification.

### `mini_torrent/metadata.py`

Creates, loads, saves, and validates `.mtorrent` files.

### `scripts/build_exe.ps1`

Builds:

```text
dist/ChunkShare/ChunkShare.exe
```

Uses PyInstaller inside `.venv`.

Important: if build fails with file lock errors, close any running `ChunkShare.exe` first.

## What Currently Works

The project currently supports:

- Creating `.mtorrent` metadata
- Starting the app dashboard
- Starting a tracker/hub automatically
- Starting a seeder from the dashboard
- Starting a leecher from the dashboard
- Uploading chunks from seeder to leecher
- Verifying downloaded chunks
- Verifying completed file hash
- Showing active torrents and peers in the dashboard
- Building a Windows executable with PyInstaller

The latest verified behavior:

```text
python -m compileall app.py mini_torrent
```

passed.

The dashboard app was tested through HTTP:

```text
app_title=True
initial_empty=True
seed_ok=True
torrent_count_after_seed=1
```

The EXE was rebuilt and tested:

```text
exe_api_ok=True
exe_html_has_seed=True
exe_tracker_url=http://192.168.1.154:8000
```

## How To Run

Python:

```powershell
python app.py
```

Windows executable:

```text
dist/ChunkShare/ChunkShare.exe
```

Build EXE:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

## How To Test Across Devices

1. Connect all laptops to the same Wi-Fi or hotspot.
2. Open ChunkShare on every laptop.
3. On the hub laptop, copy the tracker URL shown by the app.
4. On the seeder laptop, paste the hub tracker URL in the seed form.
5. On the leecher laptop, paste the same tracker URL in the leech form.
6. Start seeder first.
7. Start leecher second.
8. Watch the dashboard for seeders, leechers, peers, and chunks.

Important:

- Do not use `127.0.0.1` across devices.
- Use the LAN IP, for example `192.168.1.10`.
- Allow Python or `ChunkShare.exe` through Windows Firewall.

## What To Improve Next

Good next tasks:

- Add browse file buttons or easier file path selection.
- Add stop buttons for local seed/leech jobs.
- Add clearer progress percentage per local job.
- Add upload/download speed counters.
- Add better error messages in the dashboard.
- Add automatic peer port selection when a port is already used.
- Add screenshots to docs.
- Add automated integration tests.
- Test with two real devices on LAN.

Avoid making the project too complex unless the user asks.

## Development Guidelines

Keep the code simple and readable.

Prefer:

- Python standard library
- Clear functions
- Small classes
- Explicit names
- Good documentation

Avoid:

- Implementing the full BitTorrent protocol
- Adding unnecessary dependencies
- Overengineering networking
- Large refactors unless needed

## Suggested First Response From New AI

If continuing from this handoff, say something like:

```text
I understand ChunkShare is a simplified torrent-like distributed file sharing app. It now opens a dashboard first, starts a local hub/tracker, and lets users seed or leech from the dashboard. I will preserve the simple third-year-student-friendly architecture and focus on practical improvements like file browsing, better progress, stop controls, and LAN testing.
```
