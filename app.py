"""ChunkShare dashboard app.

This file starts a local app server, starts the ChunkShare hub/tracker,
and opens a dashboard in the user's browser.
"""

from __future__ import annotations

import json
import socket
import threading
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mini_torrent.app_dashboard import render_app_html
from mini_torrent.constants import DEFAULT_CHUNK_SIZE
from mini_torrent.downloader import download_until_complete
from mini_torrent.metadata import TorrentMeta, create_torrent, validate_file_against_metadata
from mini_torrent.peer_server import start_peer_server
from mini_torrent.storage import ChunkStorage
from mini_torrent.tracker import TrackerRequestHandler, start_tracker_server
from mini_torrent.tracker_client import announce_to_tracker

APP_HOST = "127.0.0.1"
APP_PORT = 7331
HUB_HOST = "0.0.0.0"
HUB_PORT = 8000
ANNOUNCE_INTERVAL_SECONDS = 5


def get_lan_ip() -> str:
    """Return the most likely LAN IP address for this device."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
        try:
            connection.connect(("8.8.8.8", 80))
            return connection.getsockname()[0]
        except OSError:
            return socket.gethostbyname(socket.gethostname())


def find_free_port(host: str, start_port: int) -> int:
    """Return the first available TCP port at or above start_port."""
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            try:
                probe.bind((host, port))
            except OSError:
                continue
            return port
    raise OSError(f"No available port found near {start_port}")


class ManagedPeer:
    """One local seeding or leeching job controlled by the dashboard."""

    def __init__(
        self,
        role: str,
        peer_id: str,
        tracker_url: str,
        host: str,
        port: int,
        meta: TorrentMeta,
        storage: ChunkStorage,
    ) -> None:
        """Create a managed peer record."""
        self.role = role
        self.peer_id = peer_id
        self.tracker_url = tracker_url
        self.host = host
        self.port = port
        self.meta = meta
        self.storage = storage
        self.status = "Starting"
        self.message = ""
        self.stop_event = threading.Event()
        self.server = start_peer_server(storage, host, port)
        self.thread: threading.Thread | None = None

    def start_seeding(self) -> None:
        """Start the peer announce loop in a background thread."""
        self.status = "Seeding"
        self.thread = threading.Thread(target=self._announce_loop, daemon=True)
        self.thread.start()

    def start_leeching(self) -> None:
        """Start the download loop in a background thread."""
        self.status = "Leeching"
        self.thread = threading.Thread(target=self._download_loop, daemon=True)
        self.thread.start()

    def _announce_once(self) -> None:
        """Announce current chunks to the tracker."""
        announce_to_tracker(
            self.tracker_url,
            self.meta.file_hash,
            self.peer_id,
            self.host,
            self.port,
            self.storage.list_chunks(),
            self.meta.filename,
            self.meta.file_size,
            self.meta.total_chunks,
        )

    def _announce_loop(self) -> None:
        """Keep announcing while the local peer is running."""
        while not self.stop_event.is_set():
            try:
                self._announce_once()
                self.message = "Announced to tracker."
            except OSError as exc:
                self.message = f"Announce failed: {exc}"
            self.stop_event.wait(ANNOUNCE_INTERVAL_SECONDS)

    def _download_loop(self) -> None:
        """Download missing chunks, then keep seeding when complete."""
        try:
            complete = download_until_complete(
                self.meta,
                self.storage,
                self.tracker_url,
                self.peer_id,
                self.host,
                self.port,
                max_rounds=60,
            )
            if complete:
                self.role = "Seeder"
                self.status = "Seeding"
                self.message = "Download complete. Now seeding."
                self._announce_loop()
            else:
                self.status = "Incomplete"
                self.message = "Download incomplete."
        except OSError as exc:
            self.status = "Error"
            self.message = str(exc)

    def to_dict(self) -> dict[str, Any]:
        """Return dashboard-friendly local peer state."""
        return {
            "role": self.role,
            "peer_id": self.peer_id,
            "host": self.host,
            "port": self.port,
            "filename": self.meta.filename,
            "status": self.status,
            "message": self.message,
            "available_chunks": len(self.storage.list_chunks()),
            "total_chunks": self.meta.total_chunks,
        }

    def close(self) -> None:
        """Stop the local peer server."""
        self.stop_event.set()
        self.server.shutdown()
        self.server.server_close()


class AppState:
    """State owned by the ChunkShare dashboard app."""

    def __init__(self) -> None:
        """Start with no app server or local peers."""
        self.lan_ip = get_lan_ip()
        self.hub_port = find_free_port("127.0.0.1", HUB_PORT)
        self.hub_server = start_tracker_server(HUB_HOST, self.hub_port)
        self.app_port = find_free_port(APP_HOST, APP_PORT)
        self.local_peers: dict[str, ManagedPeer] = {}
        self.lock = threading.Lock()

    @property
    def tracker_url(self) -> str:
        """Return tracker URL for other peers on the LAN."""
        return f"http://{self.lan_ip}:{self.hub_port}"

    @property
    def local_tracker_url(self) -> str:
        """Return tracker URL for this device."""
        return f"http://127.0.0.1:{self.hub_port}"

    def snapshot(self) -> dict[str, Any]:
        """Return full app state for the dashboard."""
        with self.lock:
            peers = [peer.to_dict() for peer in self.local_peers.values()]
        return {
            "ok": True,
            "lan_ip": self.lan_ip,
            "app_url": f"http://127.0.0.1:{self.app_port}",
            "tracker_url": self.tracker_url,
            "local_tracker_url": self.local_tracker_url,
            "tracker": TrackerRequestHandler.state.snapshot(),
            "local_peers": peers,
        }

    def create_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create `.mtorrent` metadata from a dashboard request."""
        file_path = str(payload.get("file_path") or "sample_files/hello.txt")
        chunk_size = int(payload.get("chunk_size") or DEFAULT_CHUNK_SIZE)
        meta = create_torrent(file_path, chunk_size)
        output_path = str(
            payload.get("output_path")
            or Path("torrents") / f"{meta.filename}.mtorrent"
        )
        meta.save(output_path)
        return {
            "ok": True,
            "output_path": output_path,
            "file_hash": meta.file_hash,
            "total_chunks": meta.total_chunks,
        }

    def start_seed(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Start a local seeder from dashboard input."""
        tracker_url = str(payload.get("tracker_url") or self.local_tracker_url)
        torrent_path = str(payload.get("torrent_path") or "torrents/hello.txt.mtorrent")
        file_path = str(payload.get("file_path") or "sample_files/hello.txt")
        host = str(payload.get("host") or self.lan_ip)
        port = int(payload.get("port") or 9001)
        peer_id = str(payload.get("peer_id") or f"seeder-{uuid.uuid4().hex[:6]}")

        meta = TorrentMeta.load(torrent_path)
        validate_file_against_metadata(file_path, meta)
        storage = ChunkStorage(meta, file_path, complete_source=True)
        peer = ManagedPeer("Seeder", peer_id, tracker_url, host, port, meta, storage)
        with self.lock:
            self.local_peers[peer_id] = peer
        peer.start_seeding()
        return {"ok": True, "peer_id": peer_id}

    def start_leech(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Start a local leecher from dashboard input."""
        tracker_url = str(payload.get("tracker_url") or self.local_tracker_url)
        torrent_path = str(payload.get("torrent_path") or "torrents/hello.txt.mtorrent")
        output_path = str(payload.get("output_path") or "downloads/downloaded-file")
        host = str(payload.get("host") or self.lan_ip)
        port = int(payload.get("port") or 9002)
        peer_id = str(payload.get("peer_id") or f"leecher-{uuid.uuid4().hex[:6]}")

        meta = TorrentMeta.load(torrent_path)
        if output_path == "downloads/downloaded-file":
            output_path = str(Path("downloads") / meta.filename)
        storage = ChunkStorage(meta, output_path, complete_source=False)
        peer = ManagedPeer("Leecher", peer_id, tracker_url, host, port, meta, storage)
        with self.lock:
            self.local_peers[peer_id] = peer
        peer.start_leeching()
        return {"ok": True, "peer_id": peer_id}

    def close(self) -> None:
        """Stop app-owned background servers."""
        with self.lock:
            peers = list(self.local_peers.values())
        for peer in peers:
            peer.close()
        self.hub_server.shutdown()
        self.hub_server.server_close()


class AppRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler for the ChunkShare dashboard app."""

    state: AppState

    def do_GET(self) -> None:
        """Serve the dashboard and status API."""
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/app"):
            self._send_html(200, render_app_html())
            return
        if parsed.path == "/api/status":
            self._send_json(200, self.state.snapshot())
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        """Handle dashboard actions."""
        routes = {
            "/api/create-torrent": self.state.create_metadata,
            "/api/seed": self.state.start_seed,
            "/api/leech": self.state.start_leech,
        }
        if self.path not in routes:
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        try:
            result = routes[self.path](self._read_json())
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})
            return
        self._send_json(200, result)

    def log_message(self, format: str, *args: object) -> None:
        """Print compact app logs."""
        print(f"[app] {self.address_string()} - {format % args}")

    def _read_json(self) -> dict[str, Any]:
        """Read a JSON request body."""
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        """Send a JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status: int, body_text: str) -> None:
        """Send an HTML response."""
        body = body_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_app() -> None:
    """Start ChunkShare and open the dashboard."""
    state = AppState()
    AppRequestHandler.state = state
    server = ThreadingHTTPServer((APP_HOST, state.app_port), AppRequestHandler)
    app_url = f"http://127.0.0.1:{state.app_port}/app"

    print("ChunkShare is running.")
    print(f"Dashboard: {app_url}")
    print(f"Tracker URL for this device: {state.local_tracker_url}")
    print(f"Tracker URL for LAN peers:   {state.tracker_url}")
    print("Close this window or press Ctrl+C to stop ChunkShare.")
    webbrowser.open(app_url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ChunkShare...")
    finally:
        server.server_close()
        state.close()


def main() -> None:
    """Program entry point."""
    run_app()


if __name__ == "__main__":
    main()

