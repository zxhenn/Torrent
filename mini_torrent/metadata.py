"""Torrent metadata creation, loading, saving, and validation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .constants import DEFAULT_CHUNK_SIZE
from .hashing import chunk_count, iter_file_chunks, sha256_bytes, sha256_file


@dataclass(frozen=True)
class TorrentMeta:
    """Data needed to download and verify one shared file."""

    filename: str
    file_size: int
    chunk_size: int
    file_hash: str
    chunk_hashes: list[str]

    @property
    def total_chunks(self) -> int:
        """Return the expected number of chunks."""
        return len(self.chunk_hashes)

    def to_dict(self) -> dict:
        """Convert metadata to a JSON-friendly dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TorrentMeta":
        """Create metadata from a dictionary and validate basic fields."""
        required = {"filename", "file_size", "chunk_size", "file_hash", "chunk_hashes"}
        missing = required.difference(data)
        if missing:
            raise ValueError(f"Torrent metadata is missing: {', '.join(sorted(missing))}")
        meta = cls(
            filename=str(data["filename"]),
            file_size=int(data["file_size"]),
            chunk_size=int(data["chunk_size"]),
            file_hash=str(data["file_hash"]),
            chunk_hashes=list(data["chunk_hashes"]),
        )
        expected = chunk_count(meta.file_size, meta.chunk_size)
        if expected != meta.total_chunks:
            raise ValueError(
                f"Metadata says {meta.total_chunks} chunks, expected {expected}"
            )
        return meta

    @classmethod
    def load(cls, path: str | Path) -> "TorrentMeta":
        """Load a ``.mtorrent`` metadata file."""
        with Path(path).open("r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))

    def save(self, path: str | Path) -> None:
        """Save metadata to a ``.mtorrent`` JSON file."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)
            file.write("\n")


def create_torrent(
    file_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> TorrentMeta:
    """Create torrent metadata for a local file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")

    chunk_hashes = [
        sha256_bytes(chunk) for _, chunk in iter_file_chunks(path, chunk_size)
    ]
    return TorrentMeta(
        filename=path.name,
        file_size=path.stat().st_size,
        chunk_size=chunk_size,
        file_hash=sha256_file(path),
        chunk_hashes=chunk_hashes,
    )


def validate_file_against_metadata(file_path: str | Path, meta: TorrentMeta) -> None:
    """Raise an error if a local file does not match torrent metadata."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
    if path.stat().st_size != meta.file_size:
        raise ValueError("File size does not match torrent metadata")
    if sha256_file(path) != meta.file_hash:
        raise ValueError("File hash does not match torrent metadata")

