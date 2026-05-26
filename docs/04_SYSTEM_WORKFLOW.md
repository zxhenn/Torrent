# 04 - System Workflow

## App Dashboard Flow

The easiest way to run ChunkShare is to open the dashboard app:

```powershell
python app.py
```

Or run the executable:

```text
dist/ChunkShare/ChunkShare.exe
```

The dashboard opens immediately in a browser. It can be empty at first. That is normal because no seeder or leecher has joined yet.

## One-Laptop Demo

### 1. Open The App

```powershell
python app.py
```

The app starts:

- Local dashboard app
- Local hub/tracker
- Browser dashboard

### 2. Seed The Sample File

In the right panel, open `Seed Complete File`.

Use the defaults:

```text
.mtorrent path: torrents/hello.txt.mtorrent
Complete file path: sample_files/hello.txt
Upload port: 9001
```

Click `Start Seed`.

### 3. Download The Sample File

In the right panel, open `Download File`.

Use the defaults:

```text
.mtorrent path: torrents/hello.txt.mtorrent
Output file path: downloads/hello.txt
Upload port: 9002
```

Click `Start Leech`.

The dashboard should show:

- Torrent row
- Seeder count
- Leecher count
- Peer count
- Chunk availability
- Local jobs

## Across-Device Demo

On every laptop, open ChunkShare.

```powershell
python app.py
```

Or use:

```text
ChunkShare.exe
```

### 1. Hub Laptop

Use one laptop as the hub. Its dashboard opens automatically.

Copy the tracker URL shown by the app, for example:

```text
http://192.168.1.10:8000
```

### 2. Seeder Laptop

On the laptop that has the complete file:

1. Open `Seed Complete File`.
2. Paste the hub laptop tracker URL.
3. Enter the `.mtorrent` path.
4. Enter the complete file path.
5. Use this laptop's own LAN IP as `This peer IP`.
6. Click `Start Seed`.

### 3. Leecher Laptop

On the laptop that will download:

1. Open `Download File`.
2. Paste the same hub laptop tracker URL.
3. Enter the same `.mtorrent` path.
4. Choose an output file path.
5. Use this laptop's own LAN IP as `This peer IP`.
6. Click `Start Leech`.

After downloading, the leecher becomes another seeder if it stays online.

## Creating Metadata

Use the `Create Metadata` panel in the dashboard.

Example:

```text
File to share: sample_files/hello.txt
Chunk size: 262144
Output .mtorrent path: torrents/hello.txt.mtorrent
```

Every device must use the same `.mtorrent` file for the same shared file.

## Build A Windows Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Output:

```text
dist/ChunkShare/ChunkShare.exe
```

Share the whole `dist/ChunkShare/` folder for demos.

