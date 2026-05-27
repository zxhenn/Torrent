"""HTTP peer server that uploads chunks to other peers."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .storage import ChunkStorage


class PeerHttpServer(ThreadingHTTPServer):
    """HTTP server carrying one ChunkStorage instance."""

    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], storage: ChunkStorage) -> None:
        """Create a peer server bound to one local storage object."""
        super().__init__(server_address, PeerRequestHandler)
        self.storage = storage


class PeerRequestHandler(BaseHTTPRequestHandler):
    """Serve metadata about chunks and chunk bytes."""

    server: PeerHttpServer

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

    def log_message(self, format: str, *args: object) -> None:
        """Print compact peer server logs."""
        print(f"[peer] {self.address_string()} - {format % args}")

    def _handle_bitfield(self, query_string: str) -> None:
        """Return the chunks this peer can currently upload."""
        query = parse_qs(query_string)
        if query.get("file_hash", [""])[0] != self.server.storage.meta.file_hash:
            self._send_json(404, {"error": "unknown file hash"})
            return
        self._send_json(200, {"chunks": self.server.storage.list_chunks()})

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

    def _send_json(self, status: int, payload: dict) -> None:
        """Send a JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_peer_server(storage: ChunkStorage, host: str, port: int) -> PeerHttpServer:
    """Start a peer upload server in a background thread."""
    server = PeerHttpServer((host, port), storage)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
