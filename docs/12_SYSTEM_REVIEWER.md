# 12 - ChunkShare System Reviewer

This reviewer explains the whole ChunkShare project in plain but technical language.

Use this when you need to review the system before a demo, explain it to a classmate, or answer professor questions.

## One-Sentence Summary

ChunkShare is a simplified torrent-like distributed file sharing system where one tracker helps peers find each other, seeders upload chunks, leechers download chunks, and completed leechers can become new seeders.

## Main Analogy

Think of the shared file as a book that has been cut into numbered pages.

- The `.mtorrent` file is the table of contents and fingerprint list.
- The tracker is the bulletin board that says who has which pages.
- A seeder is a person who already has the complete book.
- A leecher is a person collecting missing pages.
- Hashing is the page authenticity check.
- Chunking is cutting the book into pages.
- Peer-to-peer transfer means people exchange pages directly, not through the bulletin board.

The tracker does not hold the book. It only tells people where to ask.

## System Roles

### Tracker

The tracker is the meeting point.

It stores:

- File hash
- Peer name
- Peer IP/host
- Peer upload port
- Which chunks each peer has

It does not store or upload the actual file data.

Analogy: The tracker is like a classroom whiteboard saying:

```text
Alice has chunks 0-20.
Ben has chunks 0-5.
Cara has chunks 8-14.
```

### Seeder

A seeder has the complete original file.

It:

1. Loads the `.mtorrent` metadata.
2. Verifies the real file matches the metadata.
3. Starts an upload server.
4. Announces all chunks to the tracker.
5. Sends chunks to leechers when requested.

Analogy: A seeder is the classmate who has the complete notes and can photocopy any page.

### Leecher

A leecher is still downloading.

It:

1. Loads the same `.mtorrent` metadata.
2. Creates or resumes an output file.
3. Asks the tracker which peers exist.
4. Downloads missing chunks from peers.
5. Verifies every chunk with SHA-256.
6. Saves correct chunks.
7. Becomes a seeder after completing the file.

Analogy: A leecher is building the complete notes page by page. Once finished, they can also photocopy pages for others.

### Metadata

The `.mtorrent` file describes the shared file.

It contains:

- Original filename
- Original file size
- Chunk size
- Whole-file hash
- Hash of every chunk

Analogy: Metadata is the recipe card. It does not contain the food, but it says what the final food should be and how to check every part.

### Hashing

ChunkShare uses SHA-256 hashes.

- A chunk hash checks one downloaded chunk.
- A whole-file hash checks the final completed file.

Analogy: Hashing is like a tamper-proof seal. If even one byte changes, the hash does not match.

### Chunking

Chunking splits the file into smaller pieces.

Example:

```text
File size: 2.5 MB
Chunk size: 1 MB

Chunk 0: 1 MB
Chunk 1: 1 MB
Chunk 2: 0.5 MB
```

Analogy: Instead of carrying one heavy box, ChunkShare carries smaller boxes one at a time.

## Full System Flow

### 1. Create Metadata

The user selects a file and ChunkShare creates a `.mtorrent` file.

The original file is not copied into the `.mtorrent`; only information about the file is stored.

### 2. Start Tracker

The app starts a tracker automatically.

The tracker URL looks like:

```text
http://192.168.1.154:8000
```

Every seeder and leecher in the same demo should use the same tracker URL.

### 3. Start Seeder

The seeder selects:

- The `.mtorrent` file
- The complete original file
- Its own IP address
- Its upload port

The seeder announces to the tracker:

```text
I am seeder-1.
I have this file hash.
I have chunks 0 to N.
Other peers can reach me at my IP and port.
```

### 4. Start Leecher

The leecher selects:

- The same `.mtorrent` file
- The output path for the downloaded file
- Its own IP address
- Its upload port

The leecher asks the tracker:

```text
Who has chunks for this file hash?
```

Then it downloads chunks directly from peers.

### 5. Leecher Becomes Seeder

After the leecher finishes and verifies the file, it can keep running.

Then it announces that it now has all chunks too.

This is the distributed part: the next leecher can download from both the original seeder and the completed leecher.

## Important Network Idea

Every ChunkShare app starts its own tracker, but a demo swarm should choose only one tracker as the hub.

Correct:

```text
Laptop A tracker: http://192.168.1.154:8000
Laptop B seeder uses: http://192.168.1.154:8000
Laptop C leecher uses: http://192.168.1.154:8000
```

Wrong:

```text
Laptop A uses Laptop A tracker.
Laptop B uses Laptop B tracker.
Laptop C uses Laptop C tracker.
```

If each laptop uses its own tracker, they announce only to themselves and never find each other.

## File And Folder Reviewer

This section explains the purpose of each important file in the project.

Generated folders like `.venv/`, `build/`, `dist/`, and `__pycache__/` are not system design files. They are created by Python, PyInstaller, or local runs.

## Root Files

### `README.md`

Main project introduction.

It explains what ChunkShare is, how to run the app, optional CLI commands, Docker demo commands, EXE build commands, and the documentation list.

Analogy: This is the front page of the project notebook.

### `app.py`

The main dashboard application.

It starts:

- The local web dashboard
- The tracker/hub
- Local seeder jobs
- Local leecher jobs
- Native file picker support
- Firewall helper API

Important parts:

- `AppState` stores app-level state.
- `ManagedPeer` manages one local seeder or leecher.
- `AppRequestHandler` serves dashboard API routes.
- `run_app()` starts everything.

Analogy: This is the control room. It starts the whiteboard, opens the dashboard, and manages local workers.

### `start_app.bat`

Windows shortcut for running:

```text
python app.py
```

If `python` fails, it tries:

```text
py app.py
```

Analogy: This is the easy start button.

### `build_exe.bat`

Windows shortcut for building the folder-style EXE.

It runs:

```text
scripts/build_exe.ps1
```

Analogy: This is the packaging button for a folder release.

### `build_onefile_exe.bat`

Windows shortcut for building one standalone `ChunkShare.exe`.

It runs:

```text
scripts/build_onefile_exe.ps1
```

Analogy: This is the packaging button for a single-file release.

### `Dockerfile`

Defines how Docker builds a ChunkShare container.

It:

- Uses Python 3.11 slim
- Copies the project into `/app`
- Uses `python -m mini_torrent.cli` as the entry point

Analogy: This is the recipe for making a small Linux computer that knows how to run ChunkShare commands.

### `.dockerignore`

Tells Docker what not to copy into the image.

It excludes generated or unnecessary files like:

- `.git`
- `.venv`
- `build`
- `dist`
- `downloads`
- Python cache files

Analogy: This is the packing checklist saying, "Do not bring trash or heavy local output into the container."

### `.gitignore`

Tells Git what not to commit.

It ignores:

- Python cache files
- Virtual environment
- Build output
- Downloaded files
- Progress files

Analogy: This keeps the repository clean by ignoring temporary classroom mess.

### `ChunkShare.spec`

PyInstaller build configuration generated during EXE builds.

It tells PyInstaller how the app was packaged.

This is useful for rebuilding, but it is not part of the peer-to-peer logic.

Analogy: This is a packaging receipt.

## Docker Compose Files

### `docker-compose.full.yml`

Runs a full distributed demo inside Docker.

Services:

- `tracker`
- `seeder`
- `leecher1`
- `leecher2`

This is the best Docker proof that the system has separate roles.

Analogy: Four students in four separate rooms: one bulletin board manager, one complete-file holder, and two downloaders.

### `docker-compose.demo.yml`

Runs one Docker leecher that connects to the Windows host app.

This is for hybrid testing:

- Windows app acts as tracker/seeder.
- Docker acts as leecher.

Analogy: One classmate is inside Docker, but still asks the host computer for chunks.

### `docker-compose.manual.yml`

Contains both manual Docker services:

- `docker-seeder`
- `docker-leecher`

It uses environment variables so the user can change torrent paths, output paths, tracker URL, ports, and peer IDs.

Analogy: A flexible lab setup where either container can be assigned a role.

### `docker-compose.leecher.yml`

Runs only a Docker leecher.

It is useful when:

- The Windows app is tracker/seeder.
- Docker is pretending to be another computer downloading the file.

Analogy: A test student who only downloads.

### `docker-compose.leecher2.yml`

Runs a second Docker leecher.

It uses a different output path and upload port, so it can test multiple leechers at once.

Analogy: Another test student downloading separately, so you can prove multiple peers can exist.

### `docker-compose.seeder.yml`

Runs only a Docker seeder.

It is useful when:

- The Windows app is the tracker/dashboard.
- Docker pretends to be the machine that owns the full file.

Analogy: A test student who already has the complete notes.

## `mini_torrent/` Package

This folder contains the actual system logic.

### `mini_torrent/__init__.py`

Marks `mini_torrent` as a Python package.

It lets Python run commands like:

```text
python -m mini_torrent.cli
```

Analogy: This is the folder label that says, "These files belong together."

### `mini_torrent/constants.py`

Stores shared default values.

Examples:

- Default chunk size
- Default tracker host and port
- Peer announce interval
- Peer timeout
- Progress file suffix

Analogy: This is the settings board that everyone reads from.

### `mini_torrent/hashing.py`

Handles SHA-256 hashing.

It can hash:

- Raw bytes
- Whole files
- Individual file chunks

Analogy: This is the fingerprint machine.

### `mini_torrent/metadata.py`

Creates, saves, loads, and validates `.mtorrent` metadata.

It defines `TorrentMeta`, which represents:

- Filename
- File size
- Chunk size
- Whole-file hash
- Chunk hashes

Analogy: This is the file's ID card and checklist.

### `mini_torrent/storage.py`

Manages local file storage for chunks.

It:

- Creates or opens the output file
- Tracks downloaded chunks
- Saves progress to `.progress.json`
- Reads chunks for uploading
- Writes chunks to the correct position
- Verifies chunks before accepting them

Analogy: This is the warehouse shelf. Each chunk has a numbered slot.

### `mini_torrent/tracker.py`

Implements the tracker HTTP server.

Endpoints include:

- `/health`
- `/announce`
- `/leave`
- `/peers`
- `/api/state`
- `/dashboard`

The tracker stores peer information in memory.

Analogy: This is the classroom bulletin board and the person updating it.

### `mini_torrent/tracker_client.py`

Contains helper functions used by peers to talk to the tracker.

It can:

- Announce a peer's chunks
- Ask for peers
- Tell the tracker a peer is leaving

Analogy: This is the messenger that posts notes on the bulletin board and reads it back.

### `mini_torrent/peer_server.py`

Runs the upload server for a seeder or leecher.

Endpoints include:

- `/health`
- `/bitfield`
- `/chunk`

Other peers call `/chunk` to download a chunk.

Analogy: This is the service window where classmates ask, "Can I get page 5?"

### `mini_torrent/downloader.py`

Handles leecher download logic.

It:

- Announces current chunks
- Gets peers from the tracker
- Finds who has a missing chunk
- Requests chunks from peers
- Verifies downloaded chunks
- Saves correct chunks
- Stops cleanly when requested

Analogy: This is the student walking around the room asking classmates for missing pages.

### `mini_torrent/cli.py`

Command-line interface for ChunkShare.

Commands:

- `create-torrent`
- `tracker`
- `seed`
- `leech`

This is used by Docker and optional terminal demos.

Analogy: This is the non-dashboard remote control.

### `mini_torrent/dashboard.py`

Builds the simple tracker dashboard HTML.

This is the read-only tracker dashboard available at:

```text
/dashboard
```

It is mostly used for Docker demos and tracker-only viewing.

Analogy: This is a simple wall display for the bulletin board.

### `mini_torrent/app_dashboard.py`

Builds the main app-style dashboard HTML, CSS, and JavaScript.

It provides:

- Torrent-style table
- Sidebar counts
- Metadata form
- Seed form
- Leech form
- File picker buttons
- Stop, resume, delete buttons
- Firewall button
- Local jobs list

Analogy: This is the full control panel that looks like a small torrent client.

### `mini_torrent/firewall.py`

Adds Windows Firewall helper behavior.

It does not silently change the firewall. When the dashboard button is clicked, Windows asks for admin permission.

If approved, it creates inbound TCP rules for:

```text
Tracker ports: 8000-8099
Peer ports:    9000-9100
```

Analogy: This opens the classroom door so other laptops can reach your tracker and peer upload server.

## `scripts/` Folder

### `scripts/build_exe.ps1`

Builds the folder-style Windows executable with PyInstaller.

Output:

```text
dist/ChunkShare/ChunkShare.exe
```

This version must be sent with its whole folder.

Analogy: This packs the app into a suitcase with supporting files.

### `scripts/build_onefile_exe.ps1`

Builds a single-file Windows executable.

Output:

```text
dist/ChunkShare.exe
```

Analogy: This packs the app into one sealed box.

### `scripts/run_local_demo.ps1`

Runs a one-laptop demo using separate terminal processes.

It starts:

- Tracker
- Seeder
- Leecher

Analogy: One laptop acts as three separate students for testing.

### `scripts/run_docker_full_demo.ps1`

Starts the full Docker demo.

It runs:

```text
docker compose -f docker-compose.full.yml up --build
```

Analogy: This starts the full classroom simulation in Docker.

### `scripts/run_docker_demo.ps1`

Starts the app, then runs the Docker demo leecher.

It is an older hybrid helper.

Analogy: The host is the teacher desk, and Docker is one student.

### `scripts/run_docker_manual_leecher.ps1`

Starts only the Docker leecher.

It reminds the user what values to use in the Windows app when Docker is the leecher.

Analogy: This sends only one student to download.

### `scripts/run_docker_manual_seeder.ps1`

Starts only the Docker seeder.

It reminds the user what values to use in the Windows app when Docker is the seeder.

Analogy: This sends only one student who already has the full notes.

## `sample_files/` Folder

### `sample_files/.gitkeep`

Keeps the folder in Git even if it has no sample files.

Analogy: An empty folder placeholder.

### `sample_files/hello.txt`

Small sample file for quick tests.

This lets the system run immediately without needing a large custom file.

Analogy: A tiny practice book.

## `torrents/` Folder

### `torrents/.gitkeep`

Keeps the metadata folder in Git.

### `torrents/hello.txt.mtorrent`

Sample metadata for `sample_files/hello.txt`.

It is used by the default demo values.

Analogy: The practice book's table of contents and fingerprint sheet.

### `torrents/Type To Continue.zip.mtorrent`

Metadata for the larger ZIP file used during testing.

This file describes the ZIP but does not contain the ZIP itself.

Analogy: A shipping manifest for a large package.

## `downloads/` Folder

### `downloads/.gitkeep`

Keeps the downloads folder in Git.

Downloaded output files are ignored by Git.

### Downloaded files and `.progress.json` files

These are local test outputs.

Examples:

- `downloads/Type To Continue.zip`
- `downloads/Type To Continue.zip.progress.json`

They prove downloading happened, but they are not source code.

The `.progress.json` file tracks which chunks have already been downloaded.

Analogy: The downloaded file is the rebuilt book. The progress file is the checklist of pages already collected.

## `docs/` Folder

### `docs/00_TORRENTING_CONCEPT.md`

Explains torrenting concepts in general.

Read this before the project-specific docs if torrenting is still confusing.

### `docs/01_PROJECT_PLAN.md`

Explains the project goal, scope, what is done, and what remains.

### `docs/02_IMPLEMENTATION_TASKS.md`

Checklist of finished and pending tasks.

Use this for progress tracking.

### `docs/03_HOW_THE_SYSTEM_WORKS.md`

Descriptive explanation of how ChunkShare works as a system.

### `docs/04_SYSTEM_WORKFLOW.md`

Workflow guide for running the system and understanding the order of actions.

### `docs/05_TECHNICAL_EXPLANATION.md`

Technical explanation of the main components.

It is more detailed than the concept docs but shorter than the code reference.

### `docs/06_CODE_REFERENCE.md`

Detailed file and function reference.

This follows the requested structure:

```text
Directory/File
Function
Description
Block of code
Explanation
```

### `docs/07_TESTING_ACROSS_DEVICES.md`

Guide for testing on two or more laptops.

Use this when running over Wi-Fi or hotspot.

### `docs/08_BUILDING_EXE.md`

Guide for building and sharing `ChunkShare.exe`.

### `docs/09_AI_HANDOFF_PROMPT.md`

Prompt/context file for another AI assistant.

It explains the project goal and current state.

### `docs/10_HOW_TO.md`

Classmate-friendly guide for running the demo.

This is the practical field guide.

### `docs/11_DOCKER_DEMO.md`

Docker guide.

It explains the full Docker demo and manual Docker peer modes.

### `docs/12_SYSTEM_REVIEWER.md`

This file.

It is a reviewer-style summary of the whole system and every important project file.

## How The Main Code Files Work Together

Here is the simple map:

```text
app.py
  -> renders mini_torrent/app_dashboard.py
  -> starts mini_torrent/tracker.py
  -> creates ManagedPeer jobs

ManagedPeer
  -> uses mini_torrent/storage.py
  -> starts mini_torrent/peer_server.py
  -> announces through mini_torrent/tracker_client.py
  -> leeches through mini_torrent/downloader.py

metadata.py
  -> creates/loads .mtorrent files
  -> uses hashing.py

downloader.py
  -> asks tracker_client.py for peers
  -> requests chunks from peer_server.py endpoints
  -> saves chunks through storage.py
```

## What To Say During A Demo

Use this simple explanation:

ChunkShare is a simplified torrent-like system. First, the original file is described by a `.mtorrent` metadata file. That metadata contains chunk hashes and the whole-file hash. The tracker does not store the file; it only stores which peers have which chunks. A seeder owns the complete file and announces its chunks. A leecher asks the tracker for peers, downloads chunks directly from those peers, verifies each chunk, and saves them. When the leecher completes the file, it can stay online and become another seeder. This shows distributed behavior because the file can spread from peer to peer instead of coming from only one central server.

## Common Professor Questions

### Is this peer-to-peer?

Yes. The tracker helps peers find each other, but file chunks move directly between peers.

### Is the tracker a server?

Yes, but only for discovery. It is not the file server.

### Is this full BitTorrent?

No. It is intentionally simplified for class demonstration.

Missing advanced BitTorrent features include:

- Rarest-first chunk selection
- Multiple simultaneous chunk downloads
- DHT
- Peer choking/unchoking
- Magnet links
- NAT traversal

### Why is there a tracker if this is peer-to-peer?

Peers need a way to find each other. The tracker is like a directory. After discovery, the chunks transfer peer-to-peer.

### Why use hashing?

Hashing proves that downloaded chunks and final files are correct.

Without hashes, a leecher might save corrupted data without knowing.

### Why use chunking?

Chunking lets a leecher download parts of a file independently.

It also lets partial leechers share chunks they already have.

### Why does Docker count as distributed?

Docker containers run as separate processes with separate network identities.

The full Docker demo has a tracker container, seeder container, and leecher containers. That proves the roles are separated even on one physical laptop.

### Why does two-laptop testing fail sometimes?

Usually because the network blocks inbound connections.

Common causes:

- Windows Firewall
- Public network profile
- Phone hotspot device isolation
- Wrong IP address
- Old EXE build

## What The System Proves

ChunkShare proves these distributed computing ideas:

- Different nodes can have different roles.
- Nodes communicate over a network.
- A central coordinator can help with discovery without owning the data.
- Data can move peer-to-peer.
- A node can change role from leecher to seeder.
- Hashing can verify data integrity.
- A file can be rebuilt from independently downloaded chunks.

## Short Memory Version

Remember it like this:

```text
.mtorrent = map
tracker   = directory
seeder    = has full file
leecher   = collecting file
chunk     = file piece
hash      = correctness check
peer      = any participant
```

The tracker tells peers where to go. The peers do the real file sharing.
