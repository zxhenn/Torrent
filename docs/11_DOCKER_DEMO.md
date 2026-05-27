# 11 - Docker Demo

Docker is used to run ChunkShare peers as separate containers.

Best proof for class:

```text
tracker container
seeder container
leecher1 container
leecher2 container
```

The main `ChunkShare.exe` dashboard is still best for manual app demos. Docker is best for proving the distributed roles.

## Option A: Full Docker Demo

Use this when the professor asks for Docker.

Start:

```powershell
docker compose -f docker-compose.full.yml up --build
```

Open:

```text
http://localhost:18000/dashboard
```

This automatically runs:

```text
tracker   -> internal 8000, browser 18000
seeder    -> internal 9001, host test 19001
leecher1  -> internal 9002, host test 19002
leecher2  -> internal 9003, host test 19003
```

Downloaded files appear in:

```text
downloads/hello-docker-1.txt
downloads/hello-docker-2.txt
```

Stop:

```powershell
docker compose -f docker-compose.full.yml down
```

## Option B: Manual Docker Peer With ChunkShare.exe

Use this when you want to keep using `ChunkShare.exe` and only make Docker act as one peer.

Use these separate files:

```text
docker-compose.leecher.yml  -> Docker only leeches
docker-compose.seeder.yml   -> Docker only seeds
```

`docker-compose.manual.yml` still exists as a combined backup, but the separate files are easier to understand.

### EXE Seeder, Docker Leecher

1. Open `ChunkShare.exe`.
2. Start a seed in the dashboard.
3. Use:

```text
Tracker URL: http://127.0.0.1:8000
This peer IP: host.docker.internal
Upload port: 9001
```

4. Run:

```powershell
docker compose -f docker-compose.leecher.yml up --build
```

Docker downloads to:

```text
downloads/hello-docker-manual.txt
```

### Docker Seeder, EXE Leecher

1. Open `ChunkShare.exe`.
2. Run:

```powershell
docker compose -f docker-compose.seeder.yml up --build
```

3. In the EXE dashboard, start a leech with:

```text
Tracker URL: http://127.0.0.1:8000
This peer IP: 127.0.0.1
Upload port: 9002
```

The Docker seeder announces as:

```text
127.0.0.1:9011
```

Stop manual Docker peer:

```powershell
docker compose -f docker-compose.leecher.yml down
docker compose -f docker-compose.seeder.yml down
```

## Option C: Host Dashboard Plus Docker Leecher

This is the older hybrid demo.

1. Run:

```powershell
python app.py
```

2. Seed in the dashboard with:

```text
Tracker URL: http://127.0.0.1:8000
This peer IP: host.docker.internal
Upload port: 9001
```

3. Run:

```powershell
docker compose -f docker-compose.demo.yml up --build
```

Stop:

```powershell
docker compose -f docker-compose.demo.yml down
```

## Useful Scripts

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_docker_full_demo.ps1
powershell -ExecutionPolicy Bypass -File scripts/run_docker_manual_leecher.ps1
powershell -ExecutionPolicy Bypass -File scripts/run_docker_manual_seeder.ps1
powershell -ExecutionPolicy Bypass -File scripts/run_docker_demo.ps1
```

## Common Problems

### Docker Desktop Is Not Running

Open Docker Desktop first, then test:

```powershell
docker ps
```

### Port Already In Use

Stop old containers:

```powershell
docker compose -f docker-compose.full.yml down
docker compose -f docker-compose.leecher.yml down
docker compose -f docker-compose.seeder.yml down
docker compose -f docker-compose.manual.yml down
docker compose -f docker-compose.demo.yml down
```

### Docker Cannot Reach The Windows App

Use:

```text
host.docker.internal
```

That is why Docker leecher uses the host tracker:

```text
http://host.docker.internal:8000
```

### Docker Leecher Timed Out After Downloading Some Chunks

If the leecher already downloaded many chunks and then exits with `urlopen error timed out`, run the leecher again:

```powershell
docker compose -f docker-compose.leecher.yml up --build
```

ChunkShare saves progress in a `.progress.json` file, so it should resume from the chunks already downloaded.

### Clean Download Files

Delete old Docker outputs if you want a fresh test:

```text
downloads/hello-docker-1.txt
downloads/hello-docker-2.txt
downloads/hello-docker-manual.txt
downloads/hello-docker.txt
```

You can also delete matching `.progress.json` files.
