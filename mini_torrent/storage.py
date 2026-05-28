# This file stores, reads, writes, and verifies downloaded chunks.
"""Chunk storage for seeders and leechers."""

from __future__ import annotations

import json
from pathlib import Path

from .constants import PROGRESS_SUFFIX
from .hashing import sha256_bytes, sha256_file
from .metadata import TorrentMeta


# This class manages the chunks for one seeder or leecher.
class ChunkStorage:
    """Read, write, verify, and remember chunks for one file."""

    # This method prepares storage for a complete file or a download target.
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

    # This method creates or resizes the output file for downloading.
    def _ensure_output_file_size(self) -> None:
        """Create the output file and resize it to the expected file size."""
        with self.data_path.open("ab"):
            pass
        with self.data_path.open("r+b") as file:
            file.truncate(self.meta.file_size)

    # This method loads the list of chunks already downloaded.
    def _load_progress(self) -> set[int]:
        """Load the chunk indexes already downloaded by a leecher."""
        if not self.progress_path.exists():
            return set()
        with self.progress_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return {int(index) for index in data.get("chunks", [])}

    # This method saves the list of chunks already downloaded.
    def _save_progress(self) -> None:
        """Save the leecher's current chunk list to a sidecar JSON file."""
        if self.complete_source:
            return
        with self.progress_path.open("w", encoding="utf-8") as file:
            json.dump({"chunks": self.list_chunks()}, file, indent=2)
            file.write("\n")

    # This method checks saved progress and removes bad chunks.
    def _verify_progress_chunks(self) -> None:
        """Remove any saved progress entries whose bytes no longer match."""
        verified: set[int] = set()
        for index in self.available_chunks:
            if 0 <= index < self.meta.total_chunks and self._chunk_matches(index):
                verified.add(index)
        self.available_chunks = verified

    # This method finds where a chunk starts inside the file.
    def _chunk_offset(self, index: int) -> int:
        """Return the byte offset where a chunk begins."""
        return index * self.meta.chunk_size

    # This method calculates the expected size of a chunk.
    def _expected_chunk_size(self, index: int) -> int:
        """Return the expected byte size for a chunk index."""
        if index < 0 or index >= self.meta.total_chunks:
            raise IndexError(f"Invalid chunk index: {index}")
        start = self._chunk_offset(index)
        return min(self.meta.chunk_size, self.meta.file_size - start)

    # This method checks if a stored chunk matches its hash.
    def _chunk_matches(self, index: int) -> bool:
        """Return true when stored chunk bytes match the metadata hash."""
        try:
            data = self._read_raw_chunk(index)
        except OSError:
            return False
        return sha256_bytes(data) == self.meta.chunk_hashes[index]

    # This method reads chunk bytes directly from the file.
    def _read_raw_chunk(self, index: int) -> bytes:
        """Read chunk bytes without checking whether the chunk is available."""
        expected_size = self._expected_chunk_size(index)
        with self.data_path.open("rb") as file:
            file.seek(self._chunk_offset(index))
            return file.read(expected_size)

    # This method checks if this peer has a specific chunk.
    def has_chunk(self, index: int) -> bool:
        """Return true if this peer can upload a chunk."""
        return index in self.available_chunks

    # This method lists all chunks this peer has.
    def list_chunks(self) -> list[int]:
        """Return available chunk indexes in sorted order."""
        return sorted(self.available_chunks)

    # This method lists the chunks this peer still needs.
    def missing_chunks(self) -> list[int]:
        """Return chunk indexes that still need to be downloaded."""
        return [
            index
            for index in range(self.meta.total_chunks)
            if index not in self.available_chunks
        ]

    # This method reads and verifies a chunk before uploading it.
    def read_chunk(self, index: int) -> bytes:
        """Read and verify a chunk before sending it to another peer."""
        if not self.has_chunk(index):
            raise FileNotFoundError(f"Chunk is not available: {index}")
        data = self._read_raw_chunk(index)
        if sha256_bytes(data) != self.meta.chunk_hashes[index]:
            raise ValueError(f"Stored chunk failed hash check: {index}")
        return data

    # This method writes a downloaded chunk after checking it.
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

    # This method checks if the finished file is complete and correct.
    def verify_complete_file(self) -> bool:
        """Return true when every chunk and the whole file hash are correct."""
        if len(self.available_chunks) != self.meta.total_chunks:
            return False
        return sha256_file(self.data_path) == self.meta.file_hash
