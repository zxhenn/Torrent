# This file lets peers announce themselves to the tracker and ask for peer lists.
"""Small HTTP client used by peers to talk to the tracker."""

from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# This function opens a tracker request and reads the JSON reply.
def _read_json_response(request: Request | str, timeout: float = 10.0) -> dict:
    """Open a URL request and decode the JSON response."""
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


# This function tells the tracker what chunks this peer has.
def announce_to_tracker(
    tracker_url: str,
    file_hash: str,
    peer_id: str,
    host: str,
    port: int,
    chunks: list[int],
    filename: str | None = None,
    file_size: int | None = None,
    total_chunks: int | None = None,
) -> dict:
    """Tell the tracker which chunks this peer can upload."""
    payload = json.dumps(
        {
            "file_hash": file_hash,
            "peer_id": peer_id,
            "host": host,
            "port": port,
            "chunks": chunks,
            "filename": filename,
            "file_size": file_size,
            "total_chunks": total_chunks,
        }
    ).encode("utf-8")
    request = Request(
        tracker_url.rstrip("/") + "/announce",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return _read_json_response(request)


# This function asks the tracker for peers sharing a file.
def get_peers(tracker_url: str, file_hash: str) -> list[dict]:
    """Ask the tracker which peers are sharing a file."""
    query = urlencode({"file_hash": file_hash})
    data = _read_json_response(tracker_url.rstrip("/") + f"/peers?{query}")
    return list(data.get("peers", []))


# This function tells the tracker this peer is leaving.
def leave_tracker(tracker_url: str, file_hash: str, peer_id: str) -> dict:
    """Tell the tracker that this peer is no longer sharing a file."""
    payload = json.dumps(
        {
            "file_hash": file_hash,
            "peer_id": peer_id,
        }
    ).encode("utf-8")
    request = Request(
        tracker_url.rstrip("/") + "/leave",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    return _read_json_response(request)
