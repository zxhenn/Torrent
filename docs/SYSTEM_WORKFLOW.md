# System Workflow

## Normal Demo Flow

### 1. Use the Sample File

The project already includes a sample file:

```text
sample_files/hello.txt
```

You can replace it later with your own file. If you do, create a new `.mtorrent` file for that file.

Example optional command:

```powershell
Set-Content sample_files/hello.txt "Hello distributed world"
```

### 2. Create Torrent Metadata

```powershell
python -m mini_torrent.cli create-torrent sample_files/hello.txt
```

This creates:

```text
torrents/hello.txt.mtorrent
```

### 3. Start the Tracker

Open terminal 1:

```powershell
python -m mini_torrent.cli tracker --host 127.0.0.1 --port 8000
```

The tracker waits for peer announcements.

### 4. Start a Seeder

Open terminal 2:

```powershell
python -m mini_torrent.cli seed torrents/hello.txt.mtorrent --file sample_files/hello.txt --host 127.0.0.1 --port 9001 --peer-id seeder-1
```

The seeder announces that it has all chunks.

### 5. Start a Leecher

Open terminal 3:

```powershell
python -m mini_torrent.cli leech torrents/hello.txt.mtorrent --output downloads/hello.txt --host 127.0.0.1 --port 9002 --peer-id leecher-1
```

The leecher downloads missing chunks from the seeder.

### 6. Leecher Becomes Seeder

After the leecher finishes, it keeps running by default. This means it can upload the same chunks to future leechers.

Use this option if you want the leecher to exit after downloading:

```powershell
--exit-when-done
```

## Distributed Version on LAN

On different laptops:

1. One laptop runs the tracker.
2. A seeder runs with its LAN IP address.
3. A leecher connects to the tracker using the tracker's LAN IP address.

Example:

```powershell
python -m mini_torrent.cli tracker --host 0.0.0.0 --port 8000
```

Seeder:

```powershell
python -m mini_torrent.cli seed torrents/hello.txt.mtorrent --file sample_files/hello.txt --tracker http://192.168.1.10:8000 --host 192.168.1.11 --port 9001
```

Leecher:

```powershell
python -m mini_torrent.cli leech torrents/hello.txt.mtorrent --tracker http://192.168.1.10:8000 --host 192.168.1.12 --port 9002
```
