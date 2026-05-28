# This file stores shared default settings like ports, chunk size, and timeouts.
"""Shared default values used by the ChunkShare system."""

DEFAULT_CHUNK_SIZE = 256 * 1024
DEFAULT_TRACKER_HOST = "127.0.0.1"
DEFAULT_TRACKER_PORT = 8000
DEFAULT_TRACKER_URL = f"http://{DEFAULT_TRACKER_HOST}:{DEFAULT_TRACKER_PORT}"
PEER_ANNOUNCE_INTERVAL_SECONDS = 15
PEER_TTL_SECONDS = 45
PROGRESS_SUFFIX = ".progress.json"
