# This file runs the tracker that keeps track of peers and their chunks.
"""HTTP tracker server for ChunkShare.

The tracker does not store files. It only stores which peer claims to have
which chunks for a given file hash.
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .constants import DEFAULT_TRACKER_HOST, DEFAULT_TRACKER_PORT, PEER_TTL_SECONDS
from .dashboard import format_bytes, render_dashboard_html


# This class stores which peers have which chunks.
class TrackerState:
    """In-memory table of files, peers, and available chunks."""

    # This method creates an empty tracker table.
    def __init__(self) -> None:
        """Create an empty tracker state."""
        self.files: dict[str, dict[str, dict]] = {}
        self._lock = threading.Lock()

    # This method adds or updates a peer's chunk list.
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

    # This method returns live peers for one file.
    def peers_for(self, file_hash: str) -> list[dict]:
        """Return live peers for a file hash and remove stale entries."""
        now = time.time()
        with self._lock:
            peers = self.files.get(file_hash, {})
            self._remove_stale_peers(peers, now)
            return [dict(peer) for peer in peers.values()]

    # This method removes a peer when it stops sharing.
    def leave(self, file_hash: str, peer_id: str) -> bool:
        """Remove one peer from one tracked file."""
        with self._lock:
            peers = self.files.get(file_hash)
            if not peers or peer_id not in peers:
                return False
            peers.pop(peer_id, None)
            if not peers:
                self.files.pop(file_hash, None)
            return True

    # This method builds a dashboard-friendly snapshot of all torrents.
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

                total_chunks = _first_int(live_peers, "total_chunks")
                if total_chunks is None:
                    highest_chunk = max(
                        (max(peer["chunks"]) for peer in live_peers if peer["chunks"]),
                        default=-1,
                    )
                    total_chunks = highest_chunk + 1

                file_size = _first_int(live_peers, "file_size")
                filename = _first_text(live_peers, "filename", "Unknown file")
                available = sorted(
                    {
                        chunk
                        for peer in live_peers
                        for chunk in peer.get("chunks", [])
                    }
                )
                total = total_chunks or 0
                seeders = sum(
                    1
                    for peer in live_peers
                    if total > 0 and len(peer.get("chunks", [])) >= total
                )
                leechers = len(live_peers) - seeders
                pieces = [
                    2 if index in available else 0
                    for index in range(total)
                ]
                availability = (len(available) / total * 100) if total else 0

                torrents.append(
                    {
                        "file_hash": file_hash,
                        "filename": filename,
                        "file_size": file_size,
                        "file_size_label": format_bytes(file_size),
                        "total_chunks": total,
                        "available_chunks": len(available),
                        "availability_percent": round(availability, 2),
                        "seeders": seeders,
                        "leechers": leechers,
                        "peer_count": len(live_peers),
                        "pieces": pieces,
                        "peers": [
                            {
                                "peer_id": peer["peer_id"],
                                "host": peer["host"],
                                "port": peer["port"],
                                "chunk_count": len(peer.get("chunks", [])),
                                "role": "Seeder"
                                if total > 0 and len(peer.get("chunks", [])) >= total
                                else "Leecher",
                                "updated_seconds_ago": int(now - float(peer["updated_at"])),
                            }
                            for peer in live_peers
                        ],
                    }
                )

        torrents.sort(key=lambda torrent: torrent["filename"].lower())
        return {"ok": True, "torrents": torrents, "updated_at": int(now)}

    # This method removes peers that have not announced recently.
    def _remove_stale_peers(self, peers: dict[str, dict], now: float) -> None:
        """Remove peer entries that have stopped announcing."""
        stale_peer_ids = [
            peer_id
            for peer_id, peer in peers.items()
            if now - float(peer["updated_at"]) > PEER_TTL_SECONDS
        ]
        for peer_id in stale_peer_ids:
            peers.pop(peer_id, None)


# This class handles HTTP requests sent to the tracker.
class TrackerRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for tracker endpoints."""

    state = TrackerState()

    # This method handles tracker pages, health checks, state, and peer lookups.
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

    # This method handles peer announce and leave requests.
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

    # This method removes a peer from the tracker.
    def _handle_leave(self) -> None:
        """Remove a peer entry when a local job stops."""
        try:
            payload = self._read_json()
            for field in ("file_hash", "peer_id"):
                if field not in payload:
                    raise ValueError(f"{field} is required")
            removed = self.state.leave(str(payload["file_hash"]), str(payload["peer_id"]))
        except (json.JSONDecodeError, ValueError) as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, {"ok": True, "removed": removed})

    # This method prints shorter tracker log messages.
    def log_message(self, format: str, *args: object) -> None:
        """Print compact tracker logs."""
        print(f"[tracker] {self.address_string()} - {format % args}")

    # This method reads JSON from an HTTP request body.
    def _read_json(self) -> dict:
        """Read a JSON request body."""
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    # This method sends a JSON response to the client.
    def _send_json(self, status: int, payload: dict) -> None:
        """Send a JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # This method sends an HTML response to the browser.
    def _send_html(self, status: int, body_text: str) -> None:
        """Send an HTML response."""
        body = body_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# This function runs the tracker server until the user stops it.
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


# This function creates a tracker server without starting it.
def create_tracker_server(
    host: str = DEFAULT_TRACKER_HOST,
    port: int = DEFAULT_TRACKER_PORT,
) -> ThreadingHTTPServer:
    """Create a tracker HTTP server without starting it yet."""
    return ThreadingHTTPServer((host, port), TrackerRequestHandler)


# This function starts the tracker server in the background.
def start_tracker_server(
    host: str = DEFAULT_TRACKER_HOST,
    port: int = DEFAULT_TRACKER_PORT,
) -> ThreadingHTTPServer:
    """Start the tracker HTTP server in a background thread."""
    server = create_tracker_server(host, port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# This function converts a value to an integer when possible.
def _optional_int(value: object) -> int | None:
    """Convert a value to int, or return None when it is missing."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# This function finds the first integer value in peer data.
def _first_int(peers: list[dict], key: str) -> int | None:
    """Return the first integer value found in peer metadata."""
    for peer in peers:
        value = _optional_int(peer.get(key))
        if value is not None:
            return value
    return None


# This function finds the first non-empty text value in peer data.
def _first_text(peers: list[dict], key: str, default: str) -> str:
    """Return the first non-empty string value found in peer metadata."""
    for peer in peers:
        value = str(peer.get(key, "")).strip()
        if value:
            return value
    return default
