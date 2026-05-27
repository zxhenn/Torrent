# 10 - How To Run ChunkShare

This guide is for classmates who only need to run the demo and understand which fields to fill in.

## What ChunkShare Does

ChunkShare is a simplified torrent-like file sharing app.

It does not send the whole file through the tracker. Instead:

1. A `.mtorrent` metadata file describes the real file.
2. A seeder keeps the complete file.
3. A leecher downloads chunks from peers.
4. After the leecher completes the download, it can become another seeder.

Use only files you are allowed to share for class testing.

## What Everyone Needs

Each laptop needs:

- `ChunkShare.exe`
- The same `.mtorrent` file
- Same Wi-Fi or hotspot connection
- Windows Firewall permission for `ChunkShare.exe`

Only the seeder needs the complete original file.

The leecher does not need the original file. The leecher only needs:

- `ChunkShare.exe`
- `.mtorrent` file
- Output path where the downloaded file will be saved

## Important Rule

Everyone uses the same `Tracker URL`.

Each laptop uses its own `This peer IP`.

Every ChunkShare app opens its own tracker automatically, but a demo should choose only one tracker as the hub.

Example:

- Laptop A is the hub/tracker.
- Laptop B also opens ChunkShare, but it should ignore its own tracker URL.
- Laptop B should still type Laptop A's tracker URL.

If each laptop uses its own tracker URL, each laptop only announces to itself and the peers will not find each other.

Example:

```text
Hub/seeder laptop IP: 192.168.1.154
Leecher laptop IP:    192.168.1.173
```

Seeder:

```text
Tracker URL: http://192.168.1.154:8000
This peer IP: 192.168.1.154
Upload port: 9001
```

Leecher:

```text
Tracker URL: http://192.168.1.154:8000
This peer IP: 192.168.1.173
Upload port: 9002
```

Do not use `127.0.0.1` for across-device testing. `127.0.0.1` only means the current laptop.

## Role 1: Hub Laptop

One laptop acts as the hub/tracker.

Usually this can be the same laptop as the first seeder.

Steps:

1. Open `ChunkShare.exe`.
2. Wait for the dashboard to open.
3. Copy the tracker URL shown in the toolbar.

Example:

```text
http://192.168.1.154:8000
```

Send this tracker URL to every seeder and leecher.

Other laptops may show their own tracker URL too. Do not use those for the same demo swarm unless you intentionally want a separate swarm.

## Role 2: Seeder Laptop

The seeder laptop has the complete original file.

Steps:

1. Open `ChunkShare.exe`.
2. Open `Create Metadata`.
3. Click `Select` beside `File to share`.
4. Choose the complete original file.
5. Use chunk size `1048576`.
6. Click `Save As` beside `Output .mtorrent path`.
7. Save the metadata inside the `torrents` folder or anywhere easy to find.
8. Click `Create`.
9. Send the created `.mtorrent` file to classmates.
10. Open `Seed Complete File`.
11. Put the hub `Tracker URL`.
12. Select the same `.mtorrent` file.
13. Select the complete original file.
14. Put this laptop's own IP in `This peer IP`.
15. Use upload port `9001`.
16. Click `Start Seed`.

Seeder success looks like:

```text
Seeder - Seeding
278/278 chunks (100%)
Announced to tracker.
```

## Role 3: Leecher Laptop

The leecher laptop downloads the file.

Steps:

1. Open `ChunkShare.exe`.
2. Open `Download File`.
3. Put the same hub `Tracker URL`.
4. Click `Select` beside `.mtorrent path`.
5. Choose the `.mtorrent` file from the seeder.
6. Click `Save As` beside `Output file path`.
7. Choose where the downloaded file should be saved.
8. Put this leecher laptop's own IP in `This peer IP`.
9. Use upload port `9002`.
10. Click `Start Leech`.

If the download completes, the leecher becomes another seeder while ChunkShare stays open.

## Testing With Two Leechers

Use different upload ports:

```text
Seeder:   9001
Leecher1: 9002
Leecher2: 9003
```

All of them still use the same `Tracker URL`.

## Phone Hotspot Without Internet

Yes, this can work with a phone hotspot even if the phone has no internet.

The hotspot only needs to make a local network between the two laptops. ChunkShare does not need an outside server because:

- The hub/tracker runs on one laptop.
- The seeder upload server runs on one laptop.
- The leecher connects directly to those local IP addresses.

Use the hotspot IPs shown by each laptop. Keep the same rule:

- Everyone uses the hub laptop's `Tracker URL`.
- Each laptop uses its own `This peer IP`.

If the hotspot has a setting like client isolation, device isolation, or guest mode, turn it off. That setting blocks laptops from talking to each other.

## One-Laptop Docker Demo

If you do not have a second device, or if the class requires Docker, use Docker to simulate peers on the same laptop:

- See [11_DOCKER_DEMO.md](11_DOCKER_DEMO.md).

If you still want to use `ChunkShare.exe`, use the manual Docker peer mode from that guide. It lets Docker act as only one seeder or only one leecher.

## Dashboard Buttons

- `Metadata` opens the metadata creation form.
- `Seed` opens the seeding form.
- `Leech` opens the download form.
- `Resume` resumes the selected local job.
- `Stop` stops the selected local job.
- `Delete` removes the selected local job from the dashboard.
- `Firewall` asks Windows for permission to allow ChunkShare LAN ports.
- `Copy URL` copies the tracker URL.

`Delete` does not delete the real file from disk.

Click `Firewall` on the hub/seeder laptop if other laptops get URL timeout. Windows should show an admin permission prompt. Approve it to allow tracker ports `8000-8099` and peer upload ports `9000-9100`.

## Why A Peer May Stay Visible For A Bit

When a peer stops normally, ChunkShare tells the tracker to remove it.

If Docker is force-stopped, a laptop sleeps, the app crashes, or the network drops, the tracker may not receive that remove message. In that case, the peer disappears automatically after the stale-peer timeout.

## Quick Troubleshooting

### Seeder Does Not Appear On Hub

The seeder is not reaching the tracker.

Check:

- Seeder `Tracker URL` is the hub URL.
- Seeder laptop is on the same Wi-Fi or hotspot.
- Windows Firewall allows `ChunkShare.exe`.
- Hub app is still open.

Test this from the seeder laptop browser:

```text
http://HUB_IP:8000/health
```

Example:

```text
http://192.168.1.154:8000/health
```

Expected result:

```json
{"ok": true, "role": "tracker"}
```

### Leecher Times Out

First test the tracker from the leecher laptop browser:

```text
http://HUB_IP:8000/health
```

If this fails, the leecher cannot reach the hub/tracker.

### Works On Same Laptop But Not Other Laptop

This usually means the tracker is running locally, but the network is blocking other laptops.

On the hub laptop, test local tracker health:

```text
http://127.0.0.1:8000/health
```

Then on the other laptop, test the hub tracker:

```text
http://HUB_IP:8000/health
```

If local works but the other laptop times out, check:

- Rebuild `ChunkShare.exe` if you recently changed code.
- Click the dashboard `Firewall` button on the hub laptop and approve the Windows prompt.
- Allow `ChunkShare.exe` through Windows Firewall on the hub laptop.
- Set the Wi-Fi/hotspot network profile to `Private`.
- Make sure both laptops are on the same hotspot/router.
- Make sure the hotspot does not use client isolation, device isolation, or guest mode.

PowerShell port test from the other laptop:

```powershell
Test-NetConnection HUB_IP -Port 8000
```

PowerShell listener check on the hub laptop:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

The hub should be listening on `0.0.0.0:8000` or the hub's LAN IP. If it only listens on `127.0.0.1:8000`, the other laptop cannot reach it.

Then test the seeder upload server from the leecher laptop browser:

```text
http://SEEDER_IP:SEEDER_PORT/health
```

Example:

```text
http://192.168.1.154:9001/health
```

Expected result:

```json
{"ok": true, "role": "peer"}
```

If this fails, the leecher can see the tracker but cannot reach the seeder upload server.

Common fixes:

- Allow `ChunkShare.exe` through Windows Firewall on the seeder laptop.
- Set the Wi-Fi network profile to `Private`.
- Make sure the seeder `This peer IP` is the seeder laptop IP.
- Make sure the seeder upload port is `9001`.
- Make sure the laptops are not on guest Wi-Fi with client isolation.

### Same Metadata But Still Not Downloading

Check:

- Seeder has the exact original file used to create the `.mtorrent`.
- Leecher selected the same `.mtorrent`.
- Seeder is still running.
- Seeder shows `100%` chunks.
- Leecher `This peer IP` is the leecher laptop IP, not the seeder IP.
- Leecher upload port is different from the seeder upload port.



## Recommended Demo Script

1. Open ChunkShare on the hub/seeder laptop.
2. Create metadata for a small ZIP first.
3. Start seeding.
4. Open ChunkShare on leecher laptop 1.
5. Start leeching.
6. Open ChunkShare on leecher laptop 2.
7. Start leeching with upload port `9003`.
8. Keep all laptops open after download.
9. Show that completed leechers become seeders.

Start with a small file first. After the small demo works, test with a bigger ZIP.
