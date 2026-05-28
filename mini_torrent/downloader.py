# This file downloads missing chunks from peers until the file is complete.
"""Leecher download logic."""

from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .metadata import TorrentMeta
from .storage import ChunkStorage
from .tracker_client import announce_to_tracker, get_peers


# This function downloads one chunk from one peer.
def request_chunk(peer: dict, meta: TorrentMeta, index: int, timeout: float = 5.0) -> bytes:
    """Download one chunk from one peer."""
    query = urlencode({"file_hash": meta.file_hash, "index": index})
    url = f"http://{peer['host']}:{peer['port']}/chunk?{query}"
    with urlopen(url, timeout=timeout) as response:
        return response.read()


# This function keeps downloading chunks until the file is complete or it gives up.
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
    # This helper sends progress messages to the dashboard or CLI.
    def report(message: str) -> None:
        if progress_callback:
            progress_callback(message)

    # This helper updates the tracker with the chunks we currently have.
    def announce_progress() -> None:
        try:
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
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            report(f"Tracker announce failed, continuing download: {exc}")

    announce_progress()

    for round_number in range(1, max_rounds + 1):
        if stop_event and stop_event.is_set():
            report("Download stopped by user.")
            return False

        missing = storage.missing_chunks()
        if not missing:
            return storage.verify_complete_file()

        peers = []
        try:
            peers = [
                peer
                for peer in get_peers(tracker_url, meta.file_hash)
                if peer.get("peer_id") != peer_id
            ]
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            report(f"Could not reach tracker: {exc}")
            if stop_event:
                stop_event.wait(2)
            else:
                time.sleep(2)
            continue

        random.shuffle(peers)
        report(
            f"Round {round_number}: found {len(peers)} peer(s), "
            f"missing {len(missing)} chunk(s)."
        )

        made_progress = False
        last_error = ""
        for chunk_index in missing:
            if stop_event and stop_event.is_set():
                report("Download stopped by user.")
                return False

            candidates = [
                peer for peer in peers if chunk_index in set(peer.get("chunks", []))
            ]
            for peer in candidates:
                if stop_event and stop_event.is_set():
                    report("Download stopped by user.")
                    return False

                try:
                    data = request_chunk(peer, meta, chunk_index)
                except (HTTPError, URLError, TimeoutError, OSError) as exc:
                    last_error = (
                        f"Could not get chunk {chunk_index + 1} "
                        f"from {peer.get('peer_id')}: {exc}"
                    )
                    continue
                if stop_event and stop_event.is_set():
                    report("Download stopped by user.")
                    return False
                if storage.write_chunk(chunk_index, data):
                    made_progress = True
                    message = (
                        f"Downloaded chunk {chunk_index + 1}/{meta.total_chunks} "
                        f"from {peer['peer_id']}"
                    )
                    print(message)
                    report(message)
                    announce_progress()
                    break

        if not made_progress:
            message = (
                f"No new chunks found in round {round_number}. "
                "Waiting for seeders or leechers..."
            )
            if not peers:
                message = "No peers found. Check tracker URL and seeder status."
            elif last_error:
                message = f"{last_error}. Check peer IP, upload port, and firewall."
            print(message)
            report(message)
            if stop_event:
                stop_event.wait(2)
            else:
                time.sleep(2)

    return storage.verify_complete_file()
