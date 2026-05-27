# 05 - Technical Explanation

## Language and Approach

The system uses Python and only standard library modules. HTTP is used instead of raw sockets because it is easier to inspect, debug, and explain during a class demo.

## Main Components

### Torrent Metadata

The `.mtorrent` file is a JSON file. It describes one shared file:

```json
{
  "filename": "example.txt",
  "file_size": 12345,
  "chunk_size": 262144,
  "file_hash": "sha256 hash of the whole file",
  "chunk_hashes": [
    "sha256 hash of chunk 0",
    "sha256 hash of chunk 1"
  ]
}
```

The metadata is generated before sharing. Every peer uses the same metadata so they agree on how many chunks exist and what each chunk hash should be.

### Hashing

The project uses SHA-256.

- The whole-file hash proves the final downloaded file is correct.
- Each chunk hash proves every downloaded piece is correct before it is saved.

If a downloaded chunk does not match the expected hash, the leecher rejects it.

### Chunking

The file is divided into fixed-size chunks. The code default is `256 KB`, while the dashboard starts with `1048576` bytes (`1 MiB`) because it is better for larger demo files.

For example, if the file is `700 KB`, the chunks are:

- Chunk 0: `256 KB`
- Chunk 1: `256 KB`
- Chunk 2: `188 KB`

The last chunk can be smaller.

### Tracker

The tracker is a discovery server. It receives announcements from peers and answers the question:

> Who has chunks for this file hash?

The tracker does not upload the shared file. It only stores peer information:

- Peer ID
- Host
- Port
- File hash
- Available chunk indexes
- Last update time

The tracker can also serve a read-only browser dashboard at `/dashboard`. The main ChunkShare app uses a larger dashboard served by `app.py`.

When a local job stops, the app calls the tracker `/leave` endpoint. This removes the peer immediately instead of waiting for the stale-peer timeout.

### Seeder

A seeder is a peer with the full file. It:

1. Loads the `.mtorrent` file.
2. Checks if the local file matches the metadata.
3. Starts an HTTP server.
4. Announces all chunks to the tracker.
5. Uploads chunks when leechers request them.

### Leecher

A leecher is a peer that still needs chunks. It:

1. Loads the `.mtorrent` file.
2. Creates or resumes the output file.
3. Starts its own HTTP server.
4. Announces its current chunks to the tracker.
5. Requests missing chunks from peers.
6. Verifies each chunk before saving.
7. Verifies the whole file after all chunks are downloaded.
8. Can stay online and become a seeder.

### App Dashboard

The main dashboard is a simple HTML page served by `app.py`. It is not a separate frontend framework.

It shows:

- Active torrent metadata
- File availability percentage
- Seeder count
- Leecher count
- Peer count
- Chunk availability bars
- Peer roles based on how many chunks each peer has
- Local seed/leech jobs

The dashboard can also start actions:

- Create `.mtorrent` metadata
- Start a seeder
- Start a leecher
- Open native file/save dialogs for local path selection
- Stop, resume, and delete local dashboard jobs

### Dashboard App Server

`app.py` starts a local HTTP app server and opens the dashboard in the browser. It also starts a local hub/tracker automatically.

The dashboard uses these local API routes:

- `GET /app` shows the dashboard.
- `GET /api/status` returns dashboard state.
- `POST /api/create-torrent` creates metadata.
- `POST /api/inspect-torrent` reads metadata and returns useful defaults.
- `POST /api/pick-path` opens a native file or save dialog on the local computer.
- `POST /api/job-action` stops, resumes, or deletes a local dashboard job.
- `POST /api/seed` starts a local seeder.
- `POST /api/leech` starts a local leecher.

The app still uses distributed roles underneath. The dashboard only makes them easier to control.

The picker API exists because browser file inputs do not expose full local Windows paths to JavaScript. ChunkShare is a local desktop-style web app, so `app.py` can safely open a native file dialog and return the chosen path to the dashboard.

### Executable Build

The project can be packaged into `ChunkShare.exe` with PyInstaller.

The executable is easier to run during demos, but it does not change the system design. It opens the same dashboard app and still exchanges chunks peer-to-peer.

### Docker Demo

Docker is used as a demo environment for the distributed roles.

The full Docker demo runs separate containers for:

- Tracker
- Seeder
- Leecher 1
- Leecher 2

The containers communicate through Docker's internal network using service names such as `tracker`, `seeder`, and `leecher1`. This proves that the system is not just one process pretending to do every role.

The main Windows dashboard is not the best thing to put fully inside Docker because it uses local file picker dialogs. For Docker demos, the tracker dashboard at `/dashboard` is enough to observe the swarm.

## Robustness Choices

- Chunks are verified before being saved.
- Final file hash is verified after download.
- Partial progress is saved in a sidecar `.progress.json` file.
- Peer entries expire from the tracker after a timeout.
- Failed peer requests are skipped so the leecher can try another peer.
