"""Hashing and chunk-reading helpers.

This file keeps the low-level file hashing logic in one place so the
tracker, peer server, and downloader do not need to know how SHA-256 works.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterator


def sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 hex digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


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


def chunk_count(file_size: int, chunk_size: int) -> int:
    """Return how many chunks are needed for a file size."""
    if file_size == 0:
        return 0
    return (file_size + chunk_size - 1) // chunk_size

