# Mini Torrent Distributed File Sharing Demo

This is a simple Python project that demonstrates torrent-like file sharing for a distributed computing class.

It supports:

- Hashing with SHA-256
- Chunking files into fixed-size pieces
- Seeding complete files
- Leeching missing chunks
- Peer discovery through a tracker
- A leecher becoming a seeder after download

It is intentionally not a full BitTorrent implementation. The goal is to make the main concepts easy to run, inspect, and explain.

## Requirements

- Python 3.10 or newer
- No external packages

## Quick Start

Open PowerShell in this project folder.

### 1. Use the included sample file

The project already includes `sample_files/hello.txt` so the demo can run immediately.

### 2. Create metadata

```powershell
python -m mini_torrent.cli create-torrent sample_files/hello.txt
```

### 3. Start tracker

Terminal 1:

```powershell
python -m mini_torrent.cli tracker --host 127.0.0.1 --port 8000
```

### 4. Start seeder

Terminal 2:

```powershell
python -m mini_torrent.cli seed torrents/hello.txt.mtorrent --file sample_files/hello.txt --host 127.0.0.1 --port 9001 --peer-id seeder-1
```

### 5. Start leecher

Terminal 3:

```powershell
python -m mini_torrent.cli leech torrents/hello.txt.mtorrent --output downloads/hello.txt --host 127.0.0.1 --port 9002 --peer-id leecher-1
```

The leecher verifies every chunk and then verifies the final file hash.

## Commands

### Create a torrent metadata file

```powershell
python -m mini_torrent.cli create-torrent <file> [--chunk-size 262144] [--output torrents/file.mtorrent]
```

### Run tracker

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

Add `--exit-when-done` if you want the leecher to stop after the download instead of continuing to seed.

## Documentation

- `docs/01_PROJECT_PLAN.md` - what we will do, what is done, and what should be done next
- `docs/02_IMPLEMENTATION_TASKS.md` - checklist of implemented and pending tasks
- `docs/03_HOW_THE_SYSTEM_WORKS.md` - descriptive explanation of the whole system
- `docs/04_SYSTEM_WORKFLOW.md` - command workflow for demo and LAN testing
- `docs/05_TECHNICAL_EXPLANATION.md` - technical details of hashing, chunking, tracker, seeder, and leecher
- `docs/06_CODE_REFERENCE.md` - file-by-file and function-by-function explanation
