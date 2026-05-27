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

The top toolbar is ordered like the action panel:

```text
Metadata -> Seed -> Leech
```

The toolbar also has local job controls:

- `Stop` pauses the selected local seeding or leeching job and removes it from the tracker.
- `Resume` starts the selected stopped job again.
- `Delete` removes the selected local job from the dashboard. It does not delete the real file from disk.

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

For your own file, use the `Select` buttons instead of typing paths manually:

- `Select` beside `.mtorrent path` chooses the metadata file.
- `Select` beside `Complete file path` chooses the real complete file on the seeder laptop.

### 3. Download The Sample File

In the right panel, open `Download File`.

Use the defaults:

```text
.mtorrent path: torrents/hello.txt.mtorrent
Output file path: downloads/hello.txt
Upload port: 9002
```

Click `Start Leech`.

For your own file, use the `Select` button beside `.mtorrent path`, then use `Save As` beside `Output file path` to choose where the downloaded file should be written.

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

## Troubleshooting LAN Downloads

Use the dashboard counts in this order:

1. On the hub laptop, after starting the seeder, `Seeders` should become `1`.
2. After starting the leecher, `Leechers` or `Peers` should increase.
3. If the leecher appears but downloads nothing, check the leecher's `Local Jobs` message.

Common checks:

- The seeder and leecher must use the same hub tracker URL.
- The tracker URL should be the hub laptop LAN IP, such as `http://192.168.1.154:8000`, not `127.0.0.1`.
- `This peer IP` should be each device's own LAN IP.
- If testing on one laptop, use different upload ports such as `9001` and `9002`.
- If testing on two laptops, allow `ChunkShare.exe` or Python through Windows Firewall.
- From the leecher laptop, open `http://SEEDER_IP:SEEDER_PORT/health` in a browser. If it does not show JSON, the leecher cannot reach the seeder's upload server.

## Creating Metadata

Use the `Create Metadata` panel in the dashboard.

Example:

```text
File to share: sample_files/hello.txt
Chunk size: 262144
Output .mtorrent path: torrents/hello.txt.mtorrent
```

Every device must use the same `.mtorrent` file for the same shared file.

The dashboard has picker buttons:

- `Select` beside `File to share` opens a file chooser.
- `Save As` beside `Output .mtorrent path` chooses where to save the metadata.

When metadata is created, the dashboard also fills the seed and leech `.mtorrent` fields with the newly created path.

## Build A Windows Executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Output:

```text
dist/ChunkShare/ChunkShare.exe
```

Share the whole `dist/ChunkShare/` folder for demos.
