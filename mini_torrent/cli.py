"""Command line interface for the ChunkShare system."""

from __future__ import annotations

import argparse
import time
import uuid
from pathlib import Path

from .constants import DEFAULT_CHUNK_SIZE, DEFAULT_TRACKER_URL
from .downloader import download_until_complete
from .metadata import TorrentMeta, create_torrent, validate_file_against_metadata
from .peer_server import start_peer_server
from .storage import ChunkStorage
from .tracker import run_tracker
from .tracker_client import announce_to_tracker


def build_parser() -> argparse.ArgumentParser:
    """Create the command parser and subcommands."""
    parser = argparse.ArgumentParser(
        prog="chunkshare",
        description="Simple chunk-based peer-to-peer file sharing demo.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    create = subcommands.add_parser("create-torrent", help="Create a .mtorrent file")
    create.add_argument("file", help="File to describe")
    create.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Chunk size in bytes",
    )
    create.add_argument(
        "--output",
        help="Output .mtorrent path. Defaults to torrents/<filename>.mtorrent",
    )
    create.set_defaults(func=command_create_torrent)

    tracker = subcommands.add_parser("tracker", help="Run the tracker server")
    tracker.add_argument("--host", default="127.0.0.1")
    tracker.add_argument("--port", type=int, default=8000)
    tracker.set_defaults(func=command_tracker)

    seed = subcommands.add_parser("seed", help="Seed a complete file")
    seed.add_argument("torrent", help=".mtorrent file")
    seed.add_argument("--file", required=True, help="Complete file to seed")
    add_peer_arguments(seed)
    seed.set_defaults(func=command_seed)

    leech = subcommands.add_parser("leech", help="Download a file from peers")
    leech.add_argument("torrent", help=".mtorrent file")
    leech.add_argument(
        "--output",
        help="Output path. Defaults to downloads/<torrent filename>",
    )
    leech.add_argument("--rounds", type=int, default=60)
    leech.add_argument(
        "--exit-when-done",
        action="store_true",
        help="Exit instead of staying online as a seeder after download",
    )
    add_peer_arguments(leech)
    leech.set_defaults(func=command_leech)

    return parser


def add_peer_arguments(parser: argparse.ArgumentParser) -> None:
    """Add shared options used by seed and leech commands."""
    parser.add_argument("--tracker", default=DEFAULT_TRACKER_URL)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--listen-host",
        default=None,
        help="Bind address for the peer server (defaults to --host)",
    )
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peer-id", help="Friendly peer name")


def command_create_torrent(args: argparse.Namespace) -> None:
    """Create metadata for a file and save it to disk."""
    meta = create_torrent(args.file, args.chunk_size)
    output = Path(args.output) if args.output else Path("torrents") / f"{meta.filename}.mtorrent"
    meta.save(output)
    print(f"Created torrent metadata: {output}")
    print(f"File hash: {meta.file_hash}")
    print(f"Chunks: {meta.total_chunks}")


def command_tracker(args: argparse.Namespace) -> None:
    """Run the tracker server."""
    run_tracker(args.host, args.port)


def command_seed(args: argparse.Namespace) -> None:
    """Run a peer that has the complete file."""
    meta = TorrentMeta.load(args.torrent)
    validate_file_against_metadata(args.file, meta)
    storage = ChunkStorage(meta, args.file, complete_source=True)
    peer_id = args.peer_id or f"seed-{uuid.uuid4().hex[:8]}"
    listen_host = args.listen_host or args.host
    server = start_peer_server(storage, listen_host, args.port)
    print(
        "Seeder {peer_id} listening at http://{listen}:{port} "
        "(announcing {announce}:{port})".format(
            peer_id=peer_id,
            listen=listen_host,
            announce=args.host,
            port=args.port,
        )
    )
    try:
        while True:
            announce_to_tracker(
                args.tracker,
                meta.file_hash,
                peer_id,
                args.host,
                args.port,
                storage.list_chunks(),
                meta.filename,
                meta.file_size,
                meta.total_chunks,
            )
            print(f"Announced {len(storage.list_chunks())} chunks to tracker")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nSeeder stopped.")
    finally:
        server.shutdown()
        server.server_close()


def command_leech(args: argparse.Namespace) -> None:
    """Run a peer that downloads missing chunks and then seeds them."""
    meta = TorrentMeta.load(args.torrent)
    output = Path(args.output) if args.output else Path("downloads") / meta.filename
    storage = ChunkStorage(meta, output, complete_source=False)
    peer_id = args.peer_id or f"leech-{uuid.uuid4().hex[:8]}"
    listen_host = args.listen_host or args.host
    server = start_peer_server(storage, listen_host, args.port)
    print(
        "Leecher {peer_id} listening at http://{listen}:{port} "
        "(announcing {announce}:{port})".format(
            peer_id=peer_id,
            listen=listen_host,
            announce=args.host,
            port=args.port,
        )
    )
    print(f"Downloading to {output}")
    try:
        complete = download_until_complete(
            meta,
            storage,
            args.tracker,
            peer_id,
            args.host,
            args.port,
            max_rounds=args.rounds,
        )
        if complete:
            print("Download complete and file hash verified.")
        else:
            print("Download incomplete. Keep seeders online and try again.")
            return

        if args.exit_when_done:
            return

        print("Now seeding downloaded chunks. Press Ctrl+C to stop.")
        while True:
            announce_to_tracker(
                args.tracker,
                meta.file_hash,
                peer_id,
                args.host,
                args.port,
                storage.list_chunks(),
                meta.filename,
                meta.file_size,
                meta.total_chunks,
            )
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nLeecher stopped.")
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    """Program entry point."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
