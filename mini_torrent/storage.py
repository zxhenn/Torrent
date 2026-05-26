"""Chunk storage for seeders and leechers."""

from __future__ import annotations

import json
from pathlib import Path

from .constants import PROGRESS_SUFFIX
from .hashing import sha256_bytes, sha256_file
from .metadata import TorrentMeta


class ChunkStorage:
    """Read, write, verify, and remember chunks for one file."""

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

    def _ensure_output_file_size(self) -> None:
        """Create the output file and resize it to the expected file size."""
        with self.data_path.open("ab"):
            pass
        with self.data_path.open("r+b") as file:
            file.truncate(self.meta.file_size)

    def _load_progress(self) -> set[int]:
        """Load the chunk indexes already downloaded by a leecher."""
        if not self.progress_path.exists():
            return set()
        with self.progress_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return {int(index) for index in data.get("chunks", [])}

    def _save_progress(self) -> None:
        """Save the leecher's current chunk list to a sidecar JSON file."""
        if self.complete_source:
            return
        with self.progress_path.open("w", encoding="utf-8") as file:
            json.dump({"chunks": self.list_chunks()}, file, indent=2)
            file.write("\n")

    def _verify_progress_chunks(self) -> None:
        """Remove any saved progress entries whose bytes no longer match."""
        verified: set[int] = set()
        for index in self.available_chunks:
            if 0 <= index < self.meta.total_chunks and self._chunk_matches(index):
                verified.add(index)
        self.available_chunks = verified

    def _chunk_offset(self, index: int) -> int:
        """Return the byte offset where a chunk begins."""
        return index * self.meta.chunk_size

    def _expected_chunk_size(self, index: int) -> int:
        """Return the expected byte size for a chunk index."""
        if index < 0 or index >= self.meta.total_chunks:
            raise IndexError(f"Invalid chunk index: {index}")
        start = self._chunk_offset(index)
        return min(self.meta.chunk_size, self.meta.file_size - start)

    def _chunk_matches(self, index: int) -> bool:
        """Return true when stored chunk bytes match the metadata hash."""
        try:
            data = self._read_raw_chunk(index)
        except OSError:
            return False
        return sha256_bytes(data) == self.meta.chunk_hashes[index]

    def _read_raw_chunk(self, index: int) -> bytes:
        """Read chunk bytes without checking whether the chunk is available."""
        expected_size = self._expected_chunk_size(index)
        with self.data_path.open("rb") as file:
            file.seek(self._chunk_offset(index))
            return file.read(expected_size)

    def has_chunk(self, index: int) -> bool:
        """Return true if this peer can upload a chunk."""
        return index in self.available_chunks

    def list_chunks(self) -> list[int]:
        """Return available chunk indexes in sorted order."""
        return sorted(self.available_chunks)

    def missing_chunks(self) -> list[int]:
        """Return chunk indexes that still need to be downloaded."""
        return [
            index
            for index in range(self.meta.total_chunks)
            if index not in self.available_chunks
        ]

    def read_chunk(self, index: int) -> bytes:
        """Read and verify a chunk before sending it to another peer."""
        if not self.has_chunk(index):
            raise FileNotFoundError(f"Chunk is not available: {index}")
        data = self._read_raw_chunk(index)
        if sha256_bytes(data) != self.meta.chunk_hashes[index]:
            raise ValueError(f"Stored chunk failed hash check: {index}")
        return data

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

    def verify_complete_file(self) -> bool:
        """Return true when every chunk and the whole file hash are correct."""
        if len(self.available_chunks) != self.meta.total_chunks:
            return False
        return sha256_file(self.data_path) == self.meta.file_hash

