"""ChunkShare dashboard app.

This file starts a local app server, starts the ChunkShare hub/tracker,
and opens a dashboard in the user's browser.
"""

from __future__ import annotations

import json
import os
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
from mini_torrent.tracker_client import announce_to_tracker, leave_tracker

APP_HOST = "127.0.0.1"
APP_PORT = 7331
HUB_HOST = "0.0.0.0"
HUB_PORT = 8000
ANNOUNCE_INTERVAL_SECONDS = 5
FILE_DIALOG_LOCK = threading.Lock()


def pick_local_path(
    mode: str,
    title: str,
    initial_path: str = "",
    default_extension: str = "",
    filetypes: list[tuple[str, str]] | None = None,
) -> str:
    """Open a local file dialog and return the selected Windows path."""
    import tkinter as tk
    from tkinter import filedialog

    initial = Path(initial_path) if initial_path else Path.cwd()
    initial_dir = initial if initial.is_dir() else initial.parent
    if not initial_dir.exists():
        initial_dir = Path.cwd()

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    root.update()
    try:
        options: dict[str, Any] = {
            "title": title,
            "initialdir": str(initial_dir),
        }
        if filetypes:
            options["filetypes"] = filetypes
        if default_extension:
            options["defaultextension"] = default_extension

        if mode == "save":
            selected = filedialog.asksaveasfilename(**options)
        elif mode == "directory":
            selected = filedialog.askdirectory(**options)
        else:
            selected = filedialog.askopenfilename(**options)
        return str(Path(selected)) if selected else ""
    finally:
        root.destroy()


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
        self.server: Any | None = None
        self.thread: threading.Thread | None = None
        self.listen_host = "0.0.0.0"
        self._start_server()

    def _start_server(self) -> None:
        """Start this peer's upload server if it is not already running."""
        if self.server is None:
            self.server = start_peer_server(self.storage, self.listen_host, self.port)

    def start_seeding(self) -> None:
        """Start the peer announce loop in a background thread."""
        if self.thread and self.thread.is_alive() and not self.stop_event.is_set():
            self.message = "This job is already running."
            return
        self.stop_event.clear()
        self._start_server()
        self.role = "Seeder"
        self.status = "Seeding"
        self.thread = threading.Thread(target=self._announce_loop, daemon=True)
        self.thread.start()

    def start_leeching(self) -> None:
        """Start the download loop in a background thread."""
        if self.thread and self.thread.is_alive() and not self.stop_event.is_set():
            self.message = "This job is already running."
            return
        self.stop_event.clear()
        self._start_server()
        if self.role != "Seeder":
            self.role = "Leecher"
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
                stop_event=self.stop_event,
                progress_callback=self._set_message,
            )
            if self.stop_event.is_set():
                self.status = "Stopped"
                self.message = "Download stopped by user."
                return
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

    def _set_message(self, message: str) -> None:
        """Update the local job message from a worker thread."""
        self.message = message

    def stop(self) -> None:
        """Stop this local job and remove it from the tracker."""
        self.stop_event.set()
        leave_message = "Stopped."
        try:
            leave_tracker(self.tracker_url, self.meta.file_hash, self.peer_id)
            leave_message = "Stopped and removed from tracker."
        except OSError as exc:
            leave_message = f"Stopped locally. Tracker leave failed: {exc}"

        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)

        self.status = "Stopped"
        self.message = leave_message

    def resume(self) -> None:
        """Resume a stopped or incomplete local job."""
        if self.status not in {"Stopped", "Incomplete", "Error"}:
            self.message = "This job is already running."
            return
        if self.role == "Seeder":
            self.start_seeding()
        else:
            self.start_leeching()

    def to_dict(self) -> dict[str, Any]:
        """Return dashboard-friendly local peer state."""
        available_chunks = len(self.storage.list_chunks())
        return {
            "role": self.role,
            "peer_id": self.peer_id,
            "host": self.host,
            "listen_host": self.listen_host,
            "port": self.port,
            "tracker_url": self.tracker_url,
            "filename": self.meta.filename,
            "file_hash": self.meta.file_hash,
            "status": self.status,
            "message": self.message,
            "available_chunks": available_chunks,
            "total_chunks": self.meta.total_chunks,
            "progress_percent": round(
                (available_chunks / self.meta.total_chunks * 100)
                if self.meta.total_chunks
                else 0,
                2,
            ),
            "can_stop": self.status not in {"Stopped"},
            "can_resume": self.status in {"Stopped", "Incomplete", "Error"},
        }

    def close(self) -> None:
        """Stop the local peer server."""
        self.stop()


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

    def inspect_metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Read a `.mtorrent` file and return useful dashboard defaults."""
        torrent_path = str(payload.get("torrent_path") or "")
        if not torrent_path:
            raise ValueError("Choose a .mtorrent file first")
        meta = TorrentMeta.load(torrent_path)
        return {
            "ok": True,
            "filename": meta.filename,
            "file_size": meta.file_size,
            "chunk_size": meta.chunk_size,
            "total_chunks": meta.total_chunks,
            "file_hash": meta.file_hash,
            "default_output_path": str(Path("downloads") / meta.filename),
        }

    def pick_path(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Open a native local file dialog for dashboard path fields."""
        purpose = str(payload.get("purpose") or "file")
        initial_path = str(payload.get("initial_path") or "")
        suggested_name = str(payload.get("suggested_name") or "")

        mode = "open"
        title = "Select file"
        default_extension = ""
        filetypes = [("All files", "*.*")]

        if purpose == "source_file":
            title = "Select file to share"
        elif purpose == "torrent_file":
            title = "Select .mtorrent metadata"
            filetypes = [("ChunkShare metadata", "*.mtorrent"), ("All files", "*.*")]
        elif purpose == "save_torrent":
            mode = "save"
            title = "Save .mtorrent metadata"
            default_extension = ".mtorrent"
            filetypes = [("ChunkShare metadata", "*.mtorrent"), ("All files", "*.*")]
            if suggested_name and not initial_path:
                initial_path = str(Path("torrents") / suggested_name)
        elif purpose == "download_output":
            mode = "save"
            title = "Choose download output path"
            if suggested_name and not initial_path:
                initial_path = str(Path("downloads") / suggested_name)

        with FILE_DIALOG_LOCK:
            selected = pick_local_path(
                mode,
                title,
                initial_path,
                default_extension,
                filetypes,
            )
        return {"ok": True, "path": selected}

    def start_seed(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Start a local seeder from dashboard input."""
        tracker_url = str(payload.get("tracker_url") or self.local_tracker_url)
        torrent_path = str(payload.get("torrent_path") or "torrents/hello.txt.mtorrent")
        file_path = str(payload.get("file_path") or "sample_files/hello.txt")
        host = str(payload.get("host") or self.lan_ip)
        port = int(payload.get("port") or 9001)
        peer_id = str(payload.get("peer_id") or f"seeder-{uuid.uuid4().hex[:6]}")

        self._remove_existing_peer(peer_id)
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

        self._remove_existing_peer(peer_id)
        meta = TorrentMeta.load(torrent_path)
        if output_path == "downloads/downloaded-file":
            output_path = str(Path("downloads") / meta.filename)
        storage = ChunkStorage(meta, output_path, complete_source=False)
        peer = ManagedPeer("Leecher", peer_id, tracker_url, host, port, meta, storage)
        with self.lock:
            self.local_peers[peer_id] = peer
        peer.start_leeching()
        return {"ok": True, "peer_id": peer_id}

    def job_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Stop, resume, or delete a local dashboard job."""
        peer_id = str(payload.get("peer_id") or "")
        action = str(payload.get("action") or "").lower()
        if not peer_id:
            raise ValueError("peer_id is required")
        if action not in {"stop", "resume", "delete"}:
            raise ValueError("action must be stop, resume, or delete")

        with self.lock:
            peer = self.local_peers.get(peer_id)
        if peer is None:
            raise ValueError(f"Unknown local job: {peer_id}")

        if action == "stop":
            peer.stop()
        elif action == "resume":
            peer.resume()
        else:
            peer.stop()
            with self.lock:
                self.local_peers.pop(peer_id, None)

        return {
            "ok": True,
            "peer_id": peer_id,
            "action": action,
            "status": peer.status,
            "message": peer.message,
        }

    def _remove_existing_peer(self, peer_id: str) -> None:
        """Stop and remove a same-name peer before replacing it."""
        with self.lock:
            existing = self.local_peers.pop(peer_id, None)
        if existing is not None:
            existing.stop()

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
            "/api/inspect-torrent": self.state.inspect_metadata,
            "/api/pick-path": self.state.pick_path,
            "/api/job-action": self.state.job_action,
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
    if os.environ.get("CHUNKSHARE_NO_BROWSER") != "1":
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
