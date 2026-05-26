"""Leecher download logic."""

from __future__ import annotations

import random
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .metadata import TorrentMeta
from .storage import ChunkStorage
from .tracker_client import announce_to_tracker, get_peers


def request_chunk(peer: dict, meta: TorrentMeta, index: int, timeout: float = 5.0) -> bytes:
    """Download one chunk from one peer."""
    query = urlencode({"file_hash": meta.file_hash, "index": index})
    url = f"http://{peer['host']}:{peer['port']}/chunk?{query}"
    with urlopen(url, timeout=timeout) as response:
        return response.read()


def download_until_complete(
    meta: TorrentMeta,
    storage: ChunkStorage,
    tracker_url: str,
    peer_id: str,
    listen_host: str,
    listen_port: int,
    max_rounds: int = 60,
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
