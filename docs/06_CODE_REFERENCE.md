# 06 - Code Reference

This document follows the requested format:

- Directory with file name
- Function
- Description
- Block of code
- Explanation

## Directory/File: `mini_torrent/constants.py`

### Function: module constants

Description: Stores shared default values.

Block of code:

```python
DEFAULT_CHUNK_SIZE = 256 * 1024
DEFAULT_TRACKER_HOST = "127.0.0.1"
DEFAULT_TRACKER_PORT = 8000
DEFAULT_TRACKER_URL = f"http://{DEFAULT_TRACKER_HOST}:{DEFAULT_TRACKER_PORT}"
PEER_ANNOUNCE_INTERVAL_SECONDS = 15
PEER_TTL_SECONDS = 45
PROGRESS_SUFFIX = ".progress.json"
```

Explanation: These constants keep repeated settings in one place. The chunk size is `256 KB`, the tracker defaults to localhost port `8000`, CLI/Docker peers announce every `15` seconds, peer records expire after `45` seconds, and partial downloads use `.progress.json`.

## Directory/File: `mini_torrent/dashboard.py`

### Function: `format_bytes`

Description: Converts a byte count into a readable size label.

Block of code:

```python
def format_bytes(size: int | None) -> str:
    """Convert a byte count into a short human-readable label."""
    if size is None:
        return "Unknown"
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.1f} {units[unit_index]}"
```

Explanation: The dashboard uses this so file sizes show as labels like `104 B`, `1.5 MB`, or `2.0 GB`.

### Function: `render_dashboard_html`

Description: Returns the full HTML, CSS, and JavaScript dashboard page.

Block of code:

```python
def render_dashboard_html() -> str:
    """Return the tracker dashboard page."""
    return """<!doctype html>
    ...
    """
```

Explanation: The tracker serves this page at `/dashboard`. The page calls `/api/state` every few seconds to show active torrents, seeders, leechers, peers, and chunk availability.

## Directory/File: `mini_torrent/hashing.py`

### Function: `sha256_bytes`

Description: Hashes one byte string.

Block of code:

```python
def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of a byte string."""
    return hashlib.sha256(data).hexdigest()
```

Explanation: This is used to verify chunks. The function returns a hexadecimal SHA-256 string.

### Function: `sha256_file`

Description: Hashes a whole file.

Block of code:

```python
def sha256_file(path: str | Path, read_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 hex digest of a whole file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        while True:
            block = file.read(read_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()
```

Explanation: The file is read in blocks so large files do not need to be loaded fully into memory.

### Function: `iter_file_chunks`

Description: Reads a file chunk by chunk.

Block of code:

```python
def iter_file_chunks(path: str | Path, chunk_size: int) -> Iterator[tuple[int, bytes]]:
    """Yield file chunks as ``(chunk_index, bytes)`` pairs."""
    index = 0
    with Path(path).open("rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield index, chunk
            index += 1
```

Explanation: This powers chunking. It yields the chunk number and the chunk bytes.

### Function: `chunk_count`

Description: Calculates the number of chunks needed for a file.

Block of code:

```python
def chunk_count(file_size: int, chunk_size: int) -> int:
    """Return how many chunks are needed for a file size."""
    if file_size == 0:
        return 0
    return (file_size + chunk_size - 1) // chunk_size
```

Explanation: This uses ceiling division. If a file does not divide evenly, the last chunk is smaller.

## Directory/File: `mini_torrent/metadata.py`

### Function/Class: `TorrentMeta`

Description: Holds all metadata needed to share and verify one file.

Block of code:

```python
@dataclass(frozen=True)
class TorrentMeta:
    """Data needed to download and verify one shared file."""

    filename: str
    file_size: int
    chunk_size: int
    file_hash: str
    chunk_hashes: list[str]
```

Explanation: This class represents the `.mtorrent` JSON content in Python.

### Function: `TorrentMeta.total_chunks`

Description: Returns the number of chunks.

Block of code:

```python
@property
def total_chunks(self) -> int:
    """Return the expected number of chunks."""
    return len(self.chunk_hashes)
```

Explanation: The chunk count comes from the number of chunk hashes.

### Function: `TorrentMeta.to_dict`

Description: Converts metadata into a dictionary.

Block of code:

```python
def to_dict(self) -> dict:
    """Convert metadata to a JSON-friendly dictionary."""
    return asdict(self)
```

Explanation: JSON saving needs dictionary-like data.

### Function: `TorrentMeta.from_dict`

Description: Builds metadata from loaded JSON and checks required fields.

Block of code:

```python
@classmethod
def from_dict(cls, data: dict) -> "TorrentMeta":
    """Create metadata from a dictionary and validate basic fields."""
    required = {"filename", "file_size", "chunk_size", "file_hash", "chunk_hashes"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"Torrent metadata is missing: {', '.join(sorted(missing))}")
    meta = cls(
        filename=str(data["filename"]),
        file_size=int(data["file_size"]),
        chunk_size=int(data["chunk_size"]),
        file_hash=str(data["file_hash"]),
        chunk_hashes=list(data["chunk_hashes"]),
    )
    expected = chunk_count(meta.file_size, meta.chunk_size)
    if expected != meta.total_chunks:
        raise ValueError(
            f"Metadata says {meta.total_chunks} chunks, expected {expected}"
        )
    return meta
```

Explanation: This prevents broken `.mtorrent` files from being used.

### Function: `TorrentMeta.load`

Description: Loads a `.mtorrent` file.

Block of code:

```python
@classmethod
def load(cls, path: str | Path) -> "TorrentMeta":
    """Load a ``.mtorrent`` metadata file."""
    with Path(path).open("r", encoding="utf-8") as file:
        return cls.from_dict(json.load(file))
```

Explanation: The JSON file becomes a `TorrentMeta` object.

### Function: `TorrentMeta.save`

Description: Saves metadata to disk.

Block of code:

```python
def save(self, path: str | Path) -> None:
    """Save metadata to a ``.mtorrent`` JSON file."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as file:
        json.dump(self.to_dict(), file, indent=2)
        file.write("\n")
```

Explanation: This writes readable JSON and creates the parent folder if needed.

### Function: `create_torrent`

Description: Creates metadata from a local file.

Block of code:

```python
def create_torrent(
    file_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> TorrentMeta:
    """Create torrent metadata for a local file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    chunk_hashes = [
        sha256_bytes(chunk) for _, chunk in iter_file_chunks(path, chunk_size)
    ]
    return TorrentMeta(
        filename=path.name,
        file_size=path.stat().st_size,
        chunk_size=chunk_size,
        file_hash=sha256_file(path),
        chunk_hashes=chunk_hashes,
    )
```

Explanation: This is the chunking and hashing step used before sharing a file.

### Function: `validate_file_against_metadata`

Description: Checks that a seeder's local file matches the metadata.

Block of code:

```python
def validate_file_against_metadata(file_path: str | Path, meta: TorrentMeta) -> None:
    """Raise an error if a local file does not match torrent metadata."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    if path.stat().st_size != meta.file_size:
        raise ValueError("File size does not match torrent metadata")
    if sha256_file(path) != meta.file_hash:
        raise ValueError("File hash does not match torrent metadata")
```

Explanation: A seeder should not upload a file that does not match the `.mtorrent` file.

## Directory/File: `mini_torrent/tracker_client.py`

### Function: `_read_json_response`

Description: Opens an HTTP request and reads JSON.

Block of code:

```python
def _read_json_response(request: Request | str, timeout: float = 5.0) -> dict:
    """Open a URL request and decode the JSON response."""
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))
```

Explanation: This avoids repeating JSON decoding in tracker client functions.

### Function: `announce_to_tracker`

Description: Sends a peer's chunk list to the tracker.

Block of code:

```python
def announce_to_tracker(
    tracker_url: str,
    file_hash: str,
    peer_id: str,
    host: str,
    port: int,
    chunks: list[int],
    filename: str | None = None,
    file_size: int | None = None,
    total_chunks: int | None = None,
) -> dict:
    """Tell the tracker which chunks this peer can upload."""
    payload = json.dumps(
        {
            "file_hash": file_hash,
            "peer_id": peer_id,
            "host": host,
            "port": port,
            "chunks": chunks,
            "filename": filename,
            "file_size": file_size,
            "total_chunks": total_chunks,
        }
    ).encode("utf-8")
    request = Request(
        tracker_url.rstrip("/") + "/announce",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return _read_json_response(request)
```

Explanation: Seeders and leechers use this to tell the tracker what they can share. The filename, file size, and total chunk count are included so the dashboard can show readable torrent information.

### Function: `get_peers`

Description: Gets peer addresses for a file hash.

Block of code:

```python
def get_peers(tracker_url: str, file_hash: str) -> list[dict]:
    """Ask the tracker which peers are sharing a file."""
    query = urlencode({"file_hash": file_hash})
    data = _read_json_response(tracker_url.rstrip("/") + f"/peers?{query}")
    return list(data.get("peers", []))
```

Explanation: Leechers call this before downloading chunks.

### Function: `leave_tracker`

Description: Removes a peer from the tracker when it stops.

Block of code:

```python
def leave_tracker(tracker_url: str, file_hash: str, peer_id: str) -> dict:
    """Tell the tracker that this peer is no longer sharing a file."""
```

Explanation: Stop and delete actions use this so the dashboard does not keep showing a peer that has already stopped.

## Directory/File: `mini_torrent/storage.py`

### Function/Class: `ChunkStorage`

Description: Manages local chunk reading, writing, verification, and progress.

Block of code:

```python
class ChunkStorage:
    """Read, write, verify, and remember chunks for one file."""
```

Explanation: Both seeders and leechers use this class. Seeders read chunks from a complete file. Leechers write and track downloaded chunks.

### Function: `ChunkStorage.__init__`

Description: Prepares storage for a seeder or leecher.

Block of code:

```python
def __init__(
    self,
    meta: TorrentMeta,
    data_path: str | Path,
    complete_source: bool = False,
) -> None:
    """Prepare storage for a seeder file or a leecher output file."""
    self.meta = meta
    self.data_path = Path(data_path)
    self.complete_source = complete_source
    self.progress_path = self.data_path.with_name(
        self.data_path.name + PROGRESS_SUFFIX
    )
    self.available_chunks: set[int] = set()

    if self.complete_source:
        self.available_chunks = set(range(self.meta.total_chunks))
    else:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_output_file_size()
        self.available_chunks = self._load_progress()
        self._verify_progress_chunks()
        self._save_progress()
```

Explanation: A seeder starts with all chunks. A leecher creates the output file and loads any previous progress.

### Function: `ChunkStorage._ensure_output_file_size`

Description: Creates or resizes the leecher output file.

Block of code:

```python
def _ensure_output_file_size(self) -> None:
    """Create the output file and resize it to the expected file size."""
    with self.data_path.open("ab"):
        pass
    with self.data_path.open("r+b") as file:
        file.truncate(self.meta.file_size)
```

Explanation: This allows chunks to be written directly to their final positions.

### Function: `ChunkStorage._load_progress`

Description: Loads downloaded chunk indexes.

Block of code:

```python
def _load_progress(self) -> set[int]:
    """Load the chunk indexes already downloaded by a leecher."""
    if not self.progress_path.exists():
        return set()
    with self.progress_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return {int(index) for index in data.get("chunks", [])}
```

Explanation: This helps resume a partial download.

### Function: `ChunkStorage._save_progress`

Description: Saves downloaded chunk indexes.

Block of code:

```python
def _save_progress(self) -> None:
    """Save the leecher's current chunk list to a sidecar JSON file."""
    if self.complete_source:
        return
    with self.progress_path.open("w", encoding="utf-8") as file:
        json.dump({"chunks": self.list_chunks()}, file, indent=2)
        file.write("\n")
```

Explanation: This creates the `.progress.json` file next to a leecher output file.

### Function: `ChunkStorage._verify_progress_chunks`

Description: Removes bad saved progress.

Block of code:

```python
def _verify_progress_chunks(self) -> None:
    """Remove any saved progress entries whose bytes no longer match."""
    verified: set[int] = set()
    for index in self.available_chunks:
        if 0 <= index < self.meta.total_chunks and self._chunk_matches(index):
            verified.add(index)
    self.available_chunks = verified
```

Explanation: If a partial file was modified, incorrect chunks are not trusted.

### Function: `ChunkStorage._chunk_offset`

Description: Finds where a chunk starts in the file.

Block of code:

```python
def _chunk_offset(self, index: int) -> int:
    """Return the byte offset where a chunk begins."""
    return index * self.meta.chunk_size
```

Explanation: This maps chunk number to byte position.

### Function: `ChunkStorage._expected_chunk_size`

Description: Calculates expected chunk size.

Block of code:

```python
def _expected_chunk_size(self, index: int) -> int:
    """Return the expected byte size for a chunk index."""
    if index < 0 or index >= self.meta.total_chunks:
        raise IndexError(f"Invalid chunk index: {index}")
    start = self._chunk_offset(index)
    return min(self.meta.chunk_size, self.meta.file_size - start)
```

Explanation: The final chunk may be smaller than the normal chunk size.

### Function: `ChunkStorage._chunk_matches`

Description: Checks whether stored bytes match the expected chunk hash.

Block of code:

```python
def _chunk_matches(self, index: int) -> bool:
    """Return true when stored chunk bytes match the metadata hash."""
    try:
        data = self._read_raw_chunk(index)
    except OSError:
        return False
    return sha256_bytes(data) == self.meta.chunk_hashes[index]
```

Explanation: This prevents corrupted chunks from being used.

### Function: `ChunkStorage._read_raw_chunk`

Description: Reads chunk bytes directly from the file.

Block of code:

```python
def _read_raw_chunk(self, index: int) -> bytes:
    """Read chunk bytes without checking whether the chunk is available."""
    expected_size = self._expected_chunk_size(index)
    with self.data_path.open("rb") as file:
        file.seek(self._chunk_offset(index))
        return file.read(expected_size)
```

Explanation: Higher-level methods decide whether to trust the bytes.

### Function: `ChunkStorage.has_chunk`

Description: Checks whether this peer has one chunk.

Block of code:

```python
def has_chunk(self, index: int) -> bool:
    """Return true if this peer can upload a chunk."""
    return index in self.available_chunks
```

Explanation: The peer server uses this before serving chunk bytes.

### Function: `ChunkStorage.list_chunks`

Description: Lists available chunks.

Block of code:

```python
def list_chunks(self) -> list[int]:
    """Return available chunk indexes in sorted order."""
    return sorted(self.available_chunks)
```

Explanation: This list is sent to the tracker.

### Function: `ChunkStorage.missing_chunks`

Description: Lists chunks not downloaded yet.

Block of code:

```python
def missing_chunks(self) -> list[int]:
    """Return chunk indexes that still need to be downloaded."""
    return [
        index
        for index in range(self.meta.total_chunks)
        if index not in self.available_chunks
    ]
```

Explanation: The leecher loops over this list.

### Function: `ChunkStorage.read_chunk`

Description: Reads and verifies a chunk before upload.

Block of code:

```python
def read_chunk(self, index: int) -> bytes:
    """Read and verify a chunk before sending it to another peer."""
    if not self.has_chunk(index):
        raise FileNotFoundError(f"Chunk is not available: {index}")
    data = self._read_raw_chunk(index)
    if sha256_bytes(data) != self.meta.chunk_hashes[index]:
        raise ValueError(f"Stored chunk failed hash check: {index}")
    return data
```

Explanation: A peer should only upload chunks that pass hashing.

### Function: `ChunkStorage.write_chunk`

Description: Writes a downloaded chunk after validation.

Block of code:

```python
def write_chunk(self, index: int, data: bytes) -> bool:
    """Write a downloaded chunk after validating its size and hash."""
    expected_size = self._expected_chunk_size(index)
    if len(data) != expected_size:
        return False
    if sha256_bytes(data) != self.meta.chunk_hashes[index]:
        return False
    with self.data_path.open("r+b") as file:
        file.seek(self._chunk_offset(index))
        file.write(data)
    self.available_chunks.add(index)
    self._save_progress()
    return True
```

Explanation: This is the main safety check for leeching.

### Function: `ChunkStorage.verify_complete_file`

Description: Verifies the final downloaded file.

Block of code:

```python
def verify_complete_file(self) -> bool:
    """Return true when every chunk and the whole file hash are correct."""
    if len(self.available_chunks) != self.meta.total_chunks:
        return False
    return sha256_file(self.data_path) == self.meta.file_hash
```

Explanation: This confirms that the reconstructed file is correct.

## Directory/File: `mini_torrent/tracker.py`

### Function/Class: `TrackerState`

Description: Stores peer information in memory.

Block of code:

```python
class TrackerState:
    """In-memory table of files, peers, and available chunks."""
```

Explanation: The tracker state maps file hashes to peers.

### Function: `TrackerState.__init__`

Description: Creates an empty tracker table.

Block of code:

```python
def __init__(self) -> None:
    """Create an empty tracker state."""
    self.files: dict[str, dict[str, dict]] = {}
    self._lock = threading.Lock()
```

Explanation: The first key is file hash. The second key is peer ID. The lock protects the tracker table because the HTTP server can handle multiple requests at the same time.

### Function: `TrackerState.announce`

Description: Adds or updates one peer.

Block of code:

```python
def announce(self, peer: dict) -> None:
    """Add or update one peer entry."""
    file_hash = str(peer["file_hash"])
    peer_id = str(peer["peer_id"])
    with self._lock:
        self.files.setdefault(file_hash, {})[peer_id] = {
            "peer_id": peer_id,
            "host": str(peer["host"]),
            "port": int(peer["port"]),
            "chunks": sorted({int(index) for index in peer.get("chunks", [])}),
            "filename": str(peer.get("filename") or "Unknown file"),
            "file_size": _optional_int(peer.get("file_size")),
            "total_chunks": _optional_int(peer.get("total_chunks")),
            "updated_at": time.time(),
        }
```

Explanation: Every announce refreshes the peer's available chunks, metadata, and timestamp.

### Function: `TrackerState.peers_for`

Description: Returns active peers for a file.

Block of code:

```python
def peers_for(self, file_hash: str) -> list[dict]:
    """Return live peers for a file hash and remove stale entries."""
    now = time.time()
    with self._lock:
        peers = self.files.get(file_hash, {})
        self._remove_stale_peers(peers, now)
        return [dict(peer) for peer in peers.values()]
```

Explanation: Peers that stop announcing are removed after the timeout.

### Function: `TrackerState.leave`

Description: Removes one peer from one tracked file immediately.

Block of code:

```python
def leave(self, file_hash: str, peer_id: str) -> bool:
    """Remove one peer from one tracked file."""
```

Explanation: This supports the tracker `/leave` endpoint used by dashboard stop and delete controls.

### Function: `TrackerState.snapshot`

Description: Builds dashboard-friendly tracker state.

Block of code:

```python
def snapshot(self) -> dict:
    """Return tracker state formatted for the dashboard."""
    now = time.time()
    torrents = []
    with self._lock:
        for file_hash, peers in self.files.items():
            self._remove_stale_peers(peers, now)
            live_peers = [dict(peer) for peer in peers.values()]
            if not live_peers:
                continue
            ...
    return {"ok": True, "torrents": torrents, "updated_at": int(now)}
```

Explanation: This powers `/api/state`. It groups peers by file hash and calculates seeders, leechers, peer count, chunk availability, and dashboard piece bars.

### Function: `TrackerState._remove_stale_peers`

Description: Removes peers that stopped announcing.

Block of code:

```python
def _remove_stale_peers(self, peers: dict[str, dict], now: float) -> None:
    """Remove peer entries that have stopped announcing."""
    stale_peer_ids = [
        peer_id
        for peer_id, peer in peers.items()
        if now - float(peer["updated_at"]) > PEER_TTL_SECONDS
    ]
    for peer_id in stale_peer_ids:
        peers.pop(peer_id, None)
```

Explanation: The tracker and dashboard should not show peers that have been offline for too long.

### Function/Class: `TrackerRequestHandler`

Description: Handles HTTP requests for the tracker.

Block of code:

```python
class TrackerRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for tracker endpoints."""

    state = TrackerState()
```

Explanation: All tracker requests share the same in-memory state.

### Function: `TrackerRequestHandler.do_GET`

Description: Handles dashboard, health check, tracker state, and peer list requests.

Block of code:

```python
def do_GET(self) -> None:
    """Handle dashboard, health, state, and peer list requests."""
    parsed = urlparse(self.path)
    if parsed.path in ("/", "/dashboard"):
        self._send_html(200, render_dashboard_html())
        return
    if parsed.path == "/health":
        self._send_json(200, {"ok": True, "role": "tracker"})
        return
    if parsed.path == "/api/state":
        self._send_json(200, self.state.snapshot())
        return
    if parsed.path == "/peers":
        query = parse_qs(parsed.query)
        file_hash = query.get("file_hash", [""])[0]
        if not file_hash:
            self._send_json(400, {"error": "file_hash is required"})
            return
        self._send_json(200, {"file_hash": file_hash, "peers": self.state.peers_for(file_hash)})
        return
    self._send_json(404, {"error": "not found"})
```

Explanation: Leechers use `/peers` to discover uploaders. Browsers use `/dashboard` for the visual page and `/api/state` for live dashboard data.

### Function: `TrackerRequestHandler.do_POST`

Description: Handles `/announce` and `/leave`.

Block of code:

```python
def do_POST(self) -> None:
    """Handle peer announce and leave requests."""
    parsed = urlparse(self.path)
    if parsed.path == "/leave":
        self._handle_leave()
        return
    if parsed.path != "/announce":
        self._send_json(404, {"error": "not found"})
        return
    try:
        payload = self._read_json()
        for field in ("file_hash", "peer_id", "host", "port", "chunks"):
            if field not in payload:
                raise ValueError(f"{field} is required")
        self.state.announce(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        self._send_json(400, {"error": str(exc)})
        return
    self._send_json(200, {"ok": True})
```

Explanation: Peers call `/announce` to register or refresh their chunk list. The app calls `/leave` when a job stops or is deleted.

### Function: `TrackerRequestHandler.log_message`

Description: Prints tracker logs.

Block of code:

```python
def log_message(self, format: str, *args: object) -> None:
    """Print compact tracker logs."""
    print(f"[tracker] {self.address_string()} - {format % args}")
```

Explanation: This keeps terminal output understandable.

### Function: `TrackerRequestHandler._read_json`

Description: Reads request JSON.

Block of code:

```python
def _read_json(self) -> dict:
    """Read a JSON request body."""
    length = int(self.headers.get("Content-Length", "0"))
    return json.loads(self.rfile.read(length).decode("utf-8"))
```

Explanation: Announce requests send JSON bodies.

### Function: `TrackerRequestHandler._send_json`

Description: Sends JSON responses.

Block of code:

```python
def _send_json(self, status: int, payload: dict) -> None:
    """Send a JSON response."""
    body = json.dumps(payload).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
```

Explanation: All tracker responses use JSON.

### Function: `TrackerRequestHandler._send_html`

Description: Sends HTML responses.

Block of code:

```python
def _send_html(self, status: int, body_text: str) -> None:
    """Send an HTML response."""
    body = body_text.encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "text/html; charset=utf-8")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
```

Explanation: The dashboard page uses HTML instead of JSON.

### Function: `run_tracker`

Description: Starts the tracker server.

Block of code:

```python
def run_tracker(
    host: str = DEFAULT_TRACKER_HOST,
    port: int = DEFAULT_TRACKER_PORT,
) -> None:
    """Start the tracker HTTP server and block until interrupted."""
    server = create_tracker_server(host, port)
    print(f"Tracker running at http://{host}:{port}")
    print(f"Dashboard available at http://{host}:{port}/dashboard")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTracker stopped.")
    finally:
        server.server_close()
```

Explanation: This command stays running until the user presses `Ctrl+C`. It also prints the dashboard URL.

### Function: `create_tracker_server`

Description: Creates the tracker HTTP server without starting it.

Block of code:

```python
def create_tracker_server(
    host: str = DEFAULT_TRACKER_HOST,
    port: int = DEFAULT_TRACKER_PORT,
) -> ThreadingHTTPServer:
    """Create a tracker HTTP server without starting it yet."""
    return ThreadingHTTPServer((host, port), TrackerRequestHandler)
```

Explanation: This helper lets both the direct CLI and the launcher create the same tracker server.

### Function: `start_tracker_server`

Description: Starts the tracker HTTP server in the background.

Block of code:

```python
def start_tracker_server(
    host: str = DEFAULT_TRACKER_HOST,
    port: int = DEFAULT_TRACKER_PORT,
) -> ThreadingHTTPServer:
    """Start the tracker HTTP server in a background thread."""
    server = create_tracker_server(host, port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
```

Explanation: The launcher uses this so the Hub + Dashboard can run while the menu remains usable.

### Function: `_optional_int`

Description: Converts optional metadata values to integers.

Block of code:

```python
def _optional_int(value: object) -> int | None:
    """Convert a value to int, or return None when it is missing."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
```

Explanation: Tracker announces come from HTTP JSON, so metadata values are checked before they are used.

### Function: `_first_int`

Description: Gets the first usable integer from peer metadata.

Block of code:

```python
def _first_int(peers: list[dict], key: str) -> int | None:
    """Return the first integer value found in peer metadata."""
    for peer in peers:
        value = _optional_int(peer.get(key))
        if value is not None:
            return value
    return None
```

Explanation: The dashboard uses this to find file size and total chunk count from peer announces.

### Function: `_first_text`

Description: Gets the first usable text value from peer metadata.

Block of code:

```python
def _first_text(peers: list[dict], key: str, default: str) -> str:
    """Return the first non-empty string value found in peer metadata."""
    for peer in peers:
        value = str(peer.get(key, "")).strip()
        if value:
            return value
    return default
```

Explanation: The dashboard uses this to show a readable filename.

## Directory/File: `mini_torrent/peer_server.py`

### Function/Class: `PeerHttpServer`

Description: HTTP server that owns a `ChunkStorage` object.

Block of code:

```python
class PeerHttpServer(ThreadingHTTPServer):
    """HTTP server carrying one ChunkStorage instance."""

    allow_reuse_address = True
```

Explanation: The request handler uses this storage to answer chunk requests. `allow_reuse_address` helps stopped jobs resume on the same upload port.

### Function: `PeerHttpServer.__init__`

Description: Creates a peer server.

Block of code:

```python
def __init__(self, server_address: tuple[str, int], storage: ChunkStorage) -> None:
    """Create a peer server bound to one local storage object."""
    super().__init__(server_address, PeerRequestHandler)
    self.storage = storage
```

Explanation: The peer server keeps its local file/chunk state.

### Function/Class: `PeerRequestHandler`

Description: Handles peer HTTP upload endpoints.

Block of code:

```python
class PeerRequestHandler(BaseHTTPRequestHandler):
    """Serve metadata about chunks and chunk bytes."""

    server: PeerHttpServer
```

Explanation: Other peers call these endpoints to ask for chunks.

### Function: `PeerRequestHandler.do_GET`

Description: Routes peer GET requests.

Block of code:

```python
def do_GET(self) -> None:
    """Handle peer health, bitfield, and chunk requests."""
    parsed = urlparse(self.path)
    if parsed.path == "/health":
        self._send_json(200, {"ok": True, "role": "peer"})
        return
    if parsed.path == "/bitfield":
        self._handle_bitfield(parsed.query)
        return
    if parsed.path == "/chunk":
        self._handle_chunk(parsed.query)
        return
    self._send_json(404, {"error": "not found"})
```

Explanation: The main chunk download route is `/chunk`.

### Function: `PeerRequestHandler.log_message`

Description: Prints peer server logs.

Block of code:

```python
def log_message(self, format: str, *args: object) -> None:
    """Print compact peer server logs."""
    print(f"[peer] {self.address_string()} - {format % args}")
```

Explanation: This shows requests without the default noisy server format.

### Function: `PeerRequestHandler._handle_bitfield`

Description: Returns available chunks.

Block of code:

```python
def _handle_bitfield(self, query_string: str) -> None:
    """Return the chunks this peer can currently upload."""
    query = parse_qs(query_string)
    if query.get("file_hash", [""])[0] != self.server.storage.meta.file_hash:
        self._send_json(404, {"error": "unknown file hash"})
        return
    self._send_json(200, {"chunks": self.server.storage.list_chunks()})
```

Explanation: This endpoint can help check what a peer has.

### Function: `PeerRequestHandler._handle_chunk`

Description: Sends one chunk.

Block of code:

```python
def _handle_chunk(self, query_string: str) -> None:
    """Send one verified chunk as binary data."""
    query = parse_qs(query_string)
    file_hash = query.get("file_hash", [""])[0]
    if file_hash != self.server.storage.meta.file_hash:
        self._send_json(404, {"error": "unknown file hash"})
        return
    try:
        index = int(query.get("index", [""])[0])
        data = self.server.storage.read_chunk(index)
    except (IndexError, ValueError, FileNotFoundError):
        self._send_json(404, {"error": "chunk unavailable"})
        return

    self.send_response(200)
    self.send_header("Content-Type", "application/octet-stream")
    self.send_header("Content-Length", str(len(data)))
    self.send_header("X-Chunk-Index", str(index))
    self.send_header("X-Chunk-Hash", self.server.storage.meta.chunk_hashes[index])
    self.end_headers()
    self.wfile.write(data)
```

Explanation: This is where actual file data is uploaded from one peer to another.

### Function: `PeerRequestHandler._send_json`

Description: Sends JSON responses.

Block of code:

```python
def _send_json(self, status: int, payload: dict) -> None:
    """Send a JSON response."""
    body = json.dumps(payload).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)
```

Explanation: Peer error and status responses use JSON.

### Function: `start_peer_server`

Description: Starts a peer upload server in the background.

Block of code:

```python
def start_peer_server(storage: ChunkStorage, host: str, port: int) -> PeerHttpServer:
    """Start a peer upload server in a background thread."""
    server = PeerHttpServer((host, port), storage)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
```

Explanation: Leechers need a server while they are downloading so they can share chunks too.

## Directory/File: `mini_torrent/downloader.py`

### Function: `request_chunk`

Description: Downloads one chunk from one peer.

Block of code:

```python
def request_chunk(peer: dict, meta: TorrentMeta, index: int, timeout: float = 5.0) -> bytes:
    """Download one chunk from one peer."""
    query = urlencode({"file_hash": meta.file_hash, "index": index})
    url = f"http://{peer['host']}:{peer['port']}/chunk?{query}"
    with urlopen(url, timeout=timeout) as response:
        return response.read()
```

Explanation: This fetches raw bytes. The storage layer verifies them before saving.

### Function: `download_until_complete`

Description: Main leeching loop.

Block of code:

```python
def download_until_complete(
    meta: TorrentMeta,
    storage: ChunkStorage,
    tracker_url: str,
    peer_id: str,
    listen_host: str,
    listen_port: int,
    max_rounds: int = 60,
    stop_event: threading.Event | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> bool:
    """Download missing chunks from peers until the file is complete."""
    announce_to_tracker(
        tracker_url,
        meta.file_hash,
        peer_id,
        listen_host,
        listen_port,
        storage.list_chunks(),
        meta.filename,
        meta.file_size,
        meta.total_chunks,
    )

    for round_number in range(1, max_rounds + 1):
        missing = storage.missing_chunks()
        if not missing:
            return storage.verify_complete_file()

        peers = [
            peer
            for peer in get_peers(tracker_url, meta.file_hash)
            if peer.get("peer_id") != peer_id
        ]
        random.shuffle(peers)

        made_progress = False
        for chunk_index in missing:
            candidates = [
                peer for peer in peers if chunk_index in set(peer.get("chunks", []))
            ]
            for peer in candidates:
                try:
                    data = request_chunk(peer, meta, chunk_index)
                except (HTTPError, URLError, TimeoutError, OSError):
                    continue
                if storage.write_chunk(chunk_index, data):
                    made_progress = True
                    print(
                        f"Downloaded chunk {chunk_index + 1}/{meta.total_chunks} "
                        f"from {peer['peer_id']}"
                    )
                    announce_to_tracker(
                        tracker_url,
                        meta.file_hash,
                        peer_id,
                        listen_host,
                        listen_port,
                        storage.list_chunks(),
                        meta.filename,
                        meta.file_size,
                        meta.total_chunks,
                    )
                    break

        if not made_progress:
            print(
                f"No new chunks found in round {round_number}. "
                "Waiting for seeders or leechers..."
            )
            time.sleep(2)

    return storage.verify_complete_file()
```

Explanation: The leecher repeatedly asks the tracker for peers, downloads missing chunks, verifies them through `ChunkStorage.write_chunk`, and announces progress after each successful chunk. `stop_event` lets the dashboard stop a download cleanly. `progress_callback` lets the dashboard show useful messages such as no peers found or peer unreachable.

## Directory/File: `mini_torrent/cli.py`

### Function: `build_parser`

Description: Creates the command line interface.

Block of code:

```python
def build_parser() -> argparse.ArgumentParser:
    """Create the command parser and subcommands."""
    parser = argparse.ArgumentParser(
        prog="chunkshare",
        description="Simple chunk-based peer-to-peer file sharing demo.",
    )
```

Explanation: The full function defines the `create-torrent`, `tracker`, `seed`, and `leech` commands.

### Function: `add_peer_arguments`

Description: Adds shared peer options.

Block of code:

```python
def add_peer_arguments(parser: argparse.ArgumentParser) -> None:
    """Add shared options used by seed and leech commands."""
    parser.add_argument("--tracker", default=DEFAULT_TRACKER_URL)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--listen-host", default=None)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peer-id", help="Friendly peer name")
```

Explanation: Seeders and leechers both need tracker address, announced host, listening host, port, and optional peer ID. This is useful for Docker because a peer can listen on one address but announce another address to the tracker.

### Function: `command_create_torrent`

Description: Handles the create metadata command.

Block of code:

```python
def command_create_torrent(args: argparse.Namespace) -> None:
    """Create metadata for a file and save it to disk."""
    meta = create_torrent(args.file, args.chunk_size)
    output = Path(args.output) if args.output else Path("torrents") / f"{meta.filename}.mtorrent"
    meta.save(output)
    print(f"Created torrent metadata: {output}")
    print(f"File hash: {meta.file_hash}")
    print(f"Chunks: {meta.total_chunks}")
```

Explanation: This generates the `.mtorrent` file used by all peers.

### Function: `command_tracker`

Description: Runs the tracker.

Block of code:

```python
def command_tracker(args: argparse.Namespace) -> None:
    """Run the tracker server."""
    run_tracker(args.host, args.port)
```

Explanation: This delegates to `run_tracker`.

### Function: `command_seed`

Description: Runs a seeder peer.

Block of code:

```python
def command_seed(args: argparse.Namespace) -> None:
    """Run a peer that has the complete file."""
    meta = TorrentMeta.load(args.torrent)
    validate_file_against_metadata(args.file, meta)
    storage = ChunkStorage(meta, args.file, complete_source=True)
    peer_id = args.peer_id or f"seed-{uuid.uuid4().hex[:8]}"
    listen_host = args.listen_host or args.host
    server = start_peer_server(storage, listen_host, args.port)
```

Explanation: The full function validates the complete file, starts an upload server, keeps announcing all chunks, and sends a tracker leave request when it shuts down normally.

### Function: `command_leech`

Description: Runs a leecher peer.

Block of code:

```python
def command_leech(args: argparse.Namespace) -> None:
    """Run a peer that downloads missing chunks and then seeds them."""
    meta = TorrentMeta.load(args.torrent)
    output = Path(args.output) if args.output else Path("downloads") / meta.filename
    storage = ChunkStorage(meta, output, complete_source=False)
    peer_id = args.peer_id or f"leech-{uuid.uuid4().hex[:8]}"
    listen_host = args.listen_host or args.host
    server = start_peer_server(storage, listen_host, args.port)
```

Explanation: The full function starts an upload server, downloads chunks, verifies the file, optionally stays online as a seeder, and sends a tracker leave request when it shuts down normally.

### Function: `leave_tracker_quietly`

Description: Removes a CLI/Docker peer from the tracker during shutdown.

Block of code:

```python
def leave_tracker_quietly(tracker_url: str, file_hash: str, peer_id: str) -> None:
    """Ask the tracker to remove this peer without crashing during shutdown."""
    try:
        leave_tracker(tracker_url, file_hash, peer_id)
        print("Left tracker.")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"Could not leave tracker cleanly: {exc}")
```

Explanation: Docker peers used to stay visible until the tracker timeout if they were stopped from Docker. This helper lets them remove themselves cleanly.

### Function: `install_shutdown_signal_handler`

Description: Makes Docker stop signals run normal cleanup code.

Block of code:

```python
def install_shutdown_signal_handler() -> None:
    """Turn Docker stop signals into normal cleanup flow."""
    def raise_keyboard_interrupt(signum: int, frame: object) -> None:
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGTERM, raise_keyboard_interrupt)
    except (AttributeError, ValueError):
        pass
```

Explanation: `docker compose down` sends a stop signal. This handler turns that into the same cleanup path as pressing `Ctrl+C`.

### Function: `main`

Description: CLI entry point.

Block of code:

```python
def main() -> None:
    """Program entry point."""
    install_shutdown_signal_handler()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
```

Explanation: This installs shutdown cleanup, parses the command, and runs the selected function.

## Directory/File: `app.py`

### Function: `pick_local_path`

Description: Opens a native file/save dialog and returns the selected local path.

Block of code:

```python
def pick_local_path(
    mode: str,
    title: str,
    initial_path: str = "",
    default_extension: str = "",
    filetypes: list[tuple[str, str]] | None = None,
) -> str:
    """Open a local file dialog and return the selected Windows path."""
```

Explanation: The dashboard runs in a browser, but normal browser file inputs hide full Windows paths. This helper lets the local Python app open a native dialog for source files, `.mtorrent` files, and save paths.

### Function/Class: `ManagedPeer`

Description: Represents one local seeding or leeching job started from the dashboard.

```python
class ManagedPeer:
    """One local seeding or leeching job controlled by the dashboard."""
```

Explanation: The app dashboard uses this to remember local peer role, peer ID, port, metadata, storage, status, and background thread.

### Function: `ManagedPeer.start_seeding`

Description: Starts a seeder announce loop.

```python
def start_seeding(self) -> None:
    """Start the peer announce loop in a background thread."""
    self.status = "Seeding"
    self.thread = threading.Thread(target=self._announce_loop, daemon=True)
    self.thread.start()
```

Explanation: The peer keeps telling the tracker which chunks it has.

### Function: `ManagedPeer.start_leeching`

Description: Starts a leecher download loop.

```
def start_leeching(self) -> None:
    """Start the download loop in a background thread."""
    self.status = "Leeching"
    self.thread = threading.Thread(target=self._download_loop, daemon=True)
    self.thread.start()
```

Explanation: The leecher downloads chunks in the background while the dashboard stays open.

### Function: `ManagedPeer.stop`

Description: Stops a local job, shuts down its upload server, and removes it from the tracker.

Block of code:

```python
def stop(self) -> None:
    """Stop this local job and remove it from the tracker."""
```

Explanation: This is used by the dashboard `Stop` and `Delete` controls. It does not delete the shared file or downloaded file from disk.

### Function: `ManagedPeer.resume`

Description: Restarts a stopped or incomplete local job.

Block of code:

```python
def resume(self) -> None:
    """Resume a stopped or incomplete local job."""
```

Explanation: Seeders resume by announcing again. Leechers resume by continuing from their existing progress file and downloaded chunks.

### Function/Class: `AppState`

Description: Owns dashboard app state, local peers, and the local hub/tracker.

```
class AppState:
    """State owned by the ChunkShare dashboard app."""
```

Explanation: `AppState` starts the hub automatically, provides dashboard status, and starts local seed/leech jobs from API requests.

### Function: `AppState.snapshot`

Description: Returns all dashboard data.


```python
def snapshot(self) -> dict[str, Any]:
    """Return full app state for the dashboard."""
    return {
        "ok": True,
        "lan_ip": self.lan_ip,
        "tracker_url": self.tracker_url,
        "firewall": firewall_summary(),
        "tracker": TrackerRequestHandler.state.snapshot(),
        "local_peers": peers,
    }
```

Explanation: The browser calls `/api/status`, which uses this function to draw the torrent table, peer counts, local jobs, and firewall helper status.

## Directory/File: `mini_torrent/firewall.py`

### Function: `firewall_summary`

Description: Returns firewall setup information for the dashboard.

Block of code:

```python
def firewall_summary() -> dict:
    """Return dashboard-friendly firewall setup information."""
    return {
        "supported": os.name == "nt",
        "requires_admin": True,
        "tracker_ports": TRACKER_PORT_RANGE,
        "peer_ports": PEER_PORT_RANGE,
        "profile": FIREWALL_PROFILE,
    }
```

Explanation: The dashboard uses this to explain that automatic firewall setup is available on Windows and which ports ChunkShare uses.

### Function: `request_windows_firewall_rules`

Description: Opens a Windows admin prompt and adds inbound firewall rules.

Block of code:

```python
def request_windows_firewall_rules() -> dict:
    """Ask Windows for admin permission and add ChunkShare inbound TCP rules."""
    encoded_script = _encode_powershell(_firewall_rule_script())
    launch_command = (
        "$process = Start-Process -FilePath powershell "
        "-ArgumentList "
        f"'-NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded_script}' "
        "-Verb RunAs -WindowStyle Hidden -PassThru -Wait; "
        "exit $process.ExitCode"
    )
```

Explanation: This is called by the dashboard `Firewall` button. Windows still asks the user for admin permission. If the user approves, the app adds inbound rules for tracker ports `8000-8099` and peer ports `9000-9100`.

### Function: `_firewall_rule_script`

Description: Builds the elevated PowerShell script used to add firewall rules.

Block of code:

```python
def _firewall_rule_script() -> str:
    """Return the elevated PowerShell script that creates firewall rules."""
    return f"""
$rules = @(
    @{{ Name = "ChunkShare Tracker TCP"; Ports = "{TRACKER_PORT_RANGE}" }},
    @{{ Name = "ChunkShare Peer TCP"; Ports = "{PEER_PORT_RANGE}" }}
)
"""
```

Explanation: The script recreates two simple inbound TCP rules so other laptops can reach the tracker and peer upload servers during a LAN demo.

## Directory/File: `app.py`

### Function: `AppState.inspect_metadata`

Description: Loads a `.mtorrent` file and returns values the dashboard can use.

Block of code:

```python
def inspect_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Read a `.mtorrent` file and return useful dashboard defaults."""
    meta = TorrentMeta.load(torrent_path)
    return {
        "ok": True,
        "filename": meta.filename,
        "default_output_path": str(Path("downloads") / meta.filename),
    }
```

Explanation: When a user selects a `.mtorrent` file, the dashboard can automatically suggest `downloads/<filename>` for the leecher output path.

### Function: `AppState.pick_path`

Description: Chooses which native picker should open for a dashboard field.

Block of code:

```python
def pick_path(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Open a native local file dialog for dashboard path fields."""
    purpose = str(payload.get("purpose") or "file")
    selected = pick_local_path(mode, title, initial_path, default_extension, filetypes)
    return {"ok": True, "path": selected}
```

Explanation: This route supports `Select` and `Save As` buttons in the dashboard. It keeps the UI easier for demos because users do not need to manually type long Windows paths.

### Function: `AppState.job_action`

Description: Stops, resumes, or deletes a local dashboard job.

Block of code:

```python
def job_action(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Stop, resume, or delete a local dashboard job."""
```

Explanation: This is what the toolbar `Stop`, `Resume`, and `Delete` buttons call. Delete removes the local job from the dashboard but does not remove the real file from disk.

### Function: `AppState.setup_firewall`

Description: Handles the dashboard firewall setup button.

Block of code:

```python
def setup_firewall(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Ask Windows to allow ChunkShare tracker and peer ports."""
    return request_windows_firewall_rules()
```

Explanation: This route asks Windows for admin permission and creates the inbound firewall rules used for two-laptop demos.

### Function: `AppState.start_seed`

Description: Starts a local seeder from dashboard input.


```python
def start_seed(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Start a local seeder from dashboard input."""
    meta = TorrentMeta.load(torrent_path)
    validate_file_against_metadata(file_path, meta)
    storage = ChunkStorage(meta, file_path, complete_source=True)
    peer = ManagedPeer("Seeder", peer_id, tracker_url, host, port, meta, storage)
    peer.start_seeding()
    return {"ok": True, "peer_id": peer_id}
```

Explanation: This is what the `Start Seed` button calls.

### Function: `AppState.start_leech`

Description: Starts a local leecher from dashboard input.


```python
def start_leech(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Start a local leecher from dashboard input."""
    meta = TorrentMeta.load(torrent_path)
    storage = ChunkStorage(meta, output_path, complete_source=False)
    peer = ManagedPeer("Leecher", peer_id, tracker_url, host, port, meta, storage)
    peer.start_leeching()
    return {"ok": True, "peer_id": peer_id}
```

Explanation: This is what the `Start Leech` button calls.

### Function/Class: `AppRequestHandler`

Description: Serves the dashboard page and app API routes.


```python
class AppRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler for the ChunkShare dashboard app."""
```

Explanation: It serves `/app`, `/api/status`, `/api/create-torrent`, `/api/inspect-torrent`, `/api/pick-path`, `/api/job-action`, `/api/setup-firewall`, `/api/seed`, and `/api/leech`.

### Function: `run_app`

Description: Starts ChunkShare and opens the dashboard.


```python
def run_app() -> None:
    """Start ChunkShare and open the dashboard."""
    state = AppState()
    AppRequestHandler.state = state
    server = ThreadingHTTPServer((APP_HOST, state.app_port), AppRequestHandler)
    app_url = f"http://127.0.0.1:{state.app_port}/app"
    webbrowser.open(app_url)
    server.serve_forever()
```

Explanation: This is the app entry point used by `python app.py` and `ChunkShare.exe`.

## Directory/File: `mini_torrent/app_dashboard.py`

### Function: `render_app_html`

Description: Returns the HTML, CSS, and JavaScript for the app-style dashboard.

Block of code:

```python
def render_app_html() -> str:
    """Return the ChunkShare app dashboard page."""
    return """<!doctype html>
    ...
    """
```

Explanation: The dashboard looks like a torrent client: sidebar, toolbar, torrent table, detail panels, chunk bars, seed/leech forms, picker buttons for file paths, firewall helper button, and stop/resume/delete controls for local jobs.

## Supporting Files

### Directory/File: `README.md`

Function: project guide.

Description: Gives quick start commands, command reference, requirements, and documentation links.

Block of code:

```text
ChunkShare Distributed File Sharing Demo
```

Explanation: This is the first file teammates should read when cloning the repository.

### Directory/File: `start_app.bat`

Function: Windows launcher shortcut.

Description: Runs the interactive launcher from the project folder.

Block of code:

```bat
@echo off
cd /d "%~dp0"
python app.py
if errorlevel 1 py app.py
pause
```

Explanation: This gives Windows users a simple double-clickable entry point.

### Directory/File: `scripts/run_local_demo.ps1`

Function: one-laptop demo script.

Description: Opens tracker and seeder windows, opens the dashboard, and runs one leecher download.

Block of code:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_local_demo.ps1
```

Explanation: This is useful for quickly proving that the system works on one machine before LAN testing.

### Directory/File: `scripts/build_exe.ps1`

Function: Windows executable build script.

Description: Builds `dist/ChunkShare/ChunkShare.exe` with PyInstaller.

Block of code:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Explanation: This creates a local `.venv`, installs PyInstaller, builds the executable, and copies sample files, torrents, docs, and the README into the output folder.

### Directory/File: `build_exe.bat`

Function: Windows build shortcut.

Description: Runs the PowerShell build script.

Block of code:

```bat
@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1
pause
```

Explanation: This is the easiest build entry point for Windows users.

### Directory/File: `.gitignore`

Function: repository cleanup.

Description: Prevents generated files from being committed.

Block of code:

```text
__pycache__/
.smoke_logs/
downloads/*
!downloads/.gitkeep
*.progress.json
```

Explanation: Downloads and runtime progress files are generated during demos, so they should not be pushed accidentally.

### Directory/File: `sample_files/hello.txt`

Function: demo input file.

Description: Small file used for the first hash/chunk/share test.

Block of code:

```text
Hello distributed computing.
```

Explanation: This file lets the demo run immediately after cloning.

### Directory/File: `torrents/hello.txt.mtorrent`

Function: demo metadata file.

Description: Metadata generated from `sample_files/hello.txt`.

Block of code:

```json
{
  "filename": "hello.txt",
  "chunk_size": 32
}
```

Explanation: This prebuilt metadata uses a small chunk size so the sample file splits into multiple chunks for demonstration.

### Directory/File: `docs/00_TORRENTING_CONCEPT.md`

Function: concept explanation.

Description: Explains torrenting terms and ideas before discussing this project.

Block of code:

```text
Seeder
Leecher
Swarm
Tracker
Chunk
Hash
```

Explanation: This should be read first by teammates who are new to torrenting.

### Directory/File: `docs/01_PROJECT_PLAN.md`

Function: project status document.

Description: Lists what the team will do, what is already done, and what should be done next.

Block of code:

```text
What We Will Do
What Is Done
What We Should Do Next
```

Explanation: This helps teammates quickly understand project progress.

### Directory/File: `docs/02_IMPLEMENTATION_TASKS.md`

Function: implementation checklist.

Description: Tracks finished and pending tasks using checkboxes.

Block of code:

```text
- [x] Implemented task
- [ ] Pending task
```

Explanation: This helps the team see what is already done and what can be improved next.

### Directory/File: `docs/03_HOW_THE_SYSTEM_WORKS.md`

Function: descriptive explanation.

Description: Explains the system in plain language.

Block of code:

```text
The tracker is like a directory.
```

Explanation: This is helpful for non-code explanations in presentations.

### Directory/File: `docs/04_SYSTEM_WORKFLOW.md`

Function: demo workflow.

Description: Shows the terminal flow for creating metadata, running the tracker, seeding, and leeching.

Block of code:

```text
create-torrent
tracker
seed
leech
```

Explanation: This is the hands-on guide for running the system.

### Directory/File: `docs/05_TECHNICAL_EXPLANATION.md`

Function: technical notes.

Description: Explains hashing, chunking, the tracker, the seeder, and the leecher.

Block of code:

```text
Hashing
Chunking
Tracker
Seeder
Leecher
```

Explanation: This is useful for reports or defense questions.

### Directory/File: `docs/06_CODE_REFERENCE.md`

Function: code map.

Description: Documents files, functions, code blocks, and explanations.

Block of code:

```text
Directory with file name
Function
Description
Block of code
Explanation
```

Explanation: This follows the requested format and helps teammates study the implementation file by file.

### Directory/File: `docs/07_TESTING_ACROSS_DEVICES.md`

Function: LAN testing guide.

Description: Explains how to test ChunkShare on multiple laptops.

Block of code:

```text
Hub laptop
Seeder laptop
Leecher laptop
```

Explanation: This is the practical guide for proving the distributed behavior across devices.

### Directory/File: `docs/08_BUILDING_EXE.md`

Function: executable build guide.

Description: Explains how to create and share `ChunkShare.exe`.

Block of code:

```text
dist/ChunkShare/ChunkShare.exe
```

Explanation: This helps teammates run the project without typing Python commands, as long as the executable has been built first.

### Directory/File: `docs/09_AI_HANDOFF_PROMPT.md`

Function: AI continuation guide.

Description: Gives another AI assistant the project goal, architecture, current behavior, run commands, and next tasks.

Block of code:

```text
Open ChunkShare.exe
Dashboard opens
User can create metadata, seed, and leech from the dashboard
```

Explanation: This should be given to another AI if it needs to continue the project without the full conversation history.
