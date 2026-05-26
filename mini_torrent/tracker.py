"""HTTP tracker server.

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


class TrackerState:
    """In-memory table of files, peers, and available chunks."""

    def __init__(self) -> None:
        """Create an empty tracker state."""
        self.files: dict[str, dict[str, dict]] = {}
        self._lock = threading.Lock()

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
                "updated_at": time.time(),
            }

    def peers_for(self, file_hash: str) -> list[dict]:
        """Return live peers for a file hash and remove stale entries."""
        now = time.time()
        with self._lock:
            peers = self.files.get(file_hash, {})
            stale_peer_ids = [
                peer_id
                for peer_id, peer in peers.items()
                if now - float(peer["updated_at"]) > PEER_TTL_SECONDS
            ]
            for peer_id in stale_peer_ids:
                peers.pop(peer_id, None)
            return [dict(peer) for peer in peers.values()]


class TrackerRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for tracker endpoints."""

    state = TrackerState()

    def do_GET(self) -> None:
        """Handle health checks and peer list requests."""
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(200, {"ok": True, "role": "tracker"})
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

    def do_POST(self) -> None:
        """Handle peer announce requests."""
        if self.path != "/announce":
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

    def log_message(self, format: str, *args: object) -> None:
        """Print compact tracker logs."""
        print(f"[tracker] {self.address_string()} - {format % args}")

    def _read_json(self) -> dict:
        """Read a JSON request body."""
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, status: int, payload: dict) -> None:
        """Send a JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_tracker(
    host: str = DEFAULT_TRACKER_HOST,
    port: int = DEFAULT_TRACKER_PORT,
) -> None:
    """Start the tracker HTTP server and block until interrupted."""
    server = ThreadingHTTPServer((host, port), TrackerRequestHandler)
    print(f"Tracker running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTracker stopped.")
    finally:
        server.server_close()
