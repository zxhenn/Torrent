# 07 - Testing Across Devices

This guide shows how to test ChunkShare on two or more laptops.

## What You Need

- All laptops connected to the same Wi-Fi or hotspot.
- Python installed, or the built `ChunkShare.exe`.
- The same `.mtorrent` metadata file on every laptop.
- The complete source file on at least one seeder laptop.

## Roles

### Hub Laptop

The hub laptop runs the tracker service and dashboard. It helps peers find each other.

It does not need to store the shared file.

### Seeder Laptop

The seeder laptop has the complete file.

It uploads chunks to leechers.

### Leecher Laptop

The leecher laptop downloads missing chunks.

While downloading, it can upload chunks it already has. After it finishes, it becomes a seeder if it stays online.

## Test Flow

### 1. Open ChunkShare On Every Laptop

Use Python:

```powershell
python app.py
```

Or use the executable:

```text
ChunkShare.exe
```

Each app opens a dashboard immediately.

### 2. Copy The Hub Tracker URL

On the hub laptop, copy the tracker URL shown by the app.

Example:

```text
http://192.168.1.10:8000
```

This URL is what seeders and leechers use to announce themselves.

### 3. Start The Seeder

On the laptop that has the complete file:

1. Open `Seed Complete File`.
2. Paste the hub tracker URL.
3. Set `.mtorrent path`.
4. Set `Complete file path`.
5. Set `This peer IP` to the seeder laptop's LAN IP.
6. Click `Start Seed`.

Keep this app open.

### 4. Start The Leecher

On the laptop that will download:

1. Open `Download File`.
2. Paste the same hub tracker URL.
3. Set `.mtorrent path`.
4. Set `Output file path`.
5. Set `This peer IP` to the leecher laptop's LAN IP.
6. Click `Start Leech`.

## What Should Happen

The dashboard should show:

- Shared file row
- Seeders
- Leechers
- Peers
- Chunk availability
- Local jobs

The leecher should eventually show all chunks downloaded and verified.

If the leecher stays online after download, it becomes another seeder. A third laptop can then download chunks from both the original seeder and the first leecher.

## Common Problems

### Peers Cannot Connect

Allow Python or `ChunkShare.exe` through Windows Firewall.

### Dashboard Opens But No Peers Show

Check that seeders and leechers used the hub laptop tracker URL.

### Leecher Cannot Download

Check that:

- The seeder app is still running.
- The seeder announced its own LAN IP, not `127.0.0.1`.
- The `.mtorrent` file is the same on every laptop.
- The seeder has the exact file described by the `.mtorrent` metadata.

### `127.0.0.1` Does Not Work Across Devices

`127.0.0.1` means "this same computer." Other laptops cannot use it to reach your hub or peer.

For LAN testing, use the real LAN IP, such as:

```text
192.168.1.10
```

