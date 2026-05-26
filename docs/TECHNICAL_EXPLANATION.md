# Technical Explanation

## Language and Approach

The system uses Python and only standard library modules. HTTP is used instead of raw sockets because it is easier to inspect, debug, and explain during a class demo.

## Main Components

### Torrent Metadata

The `.mtorrent` file is a JSON file. It describes one shared file:

```json
{
  "filename": "example.txt",
  "file_size": 12345,
  "chunk_size": 262144,
  "file_hash": "sha256 hash of the whole file",
  "chunk_hashes": [
    "sha256 hash of chunk 0",
    "sha256 hash of chunk 1"
  ]
}
```

The metadata is generated before sharing. Every peer uses the same metadata so they agree on how many chunks exist and what each chunk hash should be.

### Hashing

The project uses SHA-256.

- The whole-file hash proves the final downloaded file is correct.
- Each chunk hash proves every downloaded piece is correct before it is saved.

If a downloaded chunk does not match the expected hash, the leecher rejects it.

### Chunking

The file is divided into fixed-size chunks. The default chunk size is `256 KB`.

For example, if the file is `700 KB`, the chunks are:

- Chunk 0: `256 KB`
- Chunk 1: `256 KB`
- Chunk 2: `188 KB`

The last chunk can be smaller.

### Tracker

The tracker is a discovery server. It receives announcements from peers and answers the question:

> Who has chunks for this file hash?

The tracker does not upload the shared file. It only stores peer information:

- Peer ID
- Host
- Port
- File hash
- Available chunk indexes
- Last update time

### Seeder

A seeder is a peer with the full file. It:

1. Loads the `.mtorrent` file.
2. Checks if the local file matches the metadata.
3. Starts an HTTP server.
4. Announces all chunks to the tracker.
5. Uploads chunks when leechers request them.

### Leecher

A leecher is a peer that still needs chunks. It:

1. Loads the `.mtorrent` file.
2. Creates or resumes the output file.
3. Starts its own HTTP server.
4. Announces its current chunks to the tracker.
5. Requests missing chunks from peers.
6. Verifies each chunk before saving.
7. Verifies the whole file after all chunks are downloaded.
8. Can stay online and become a seeder.

## Robustness Choices

- Chunks are verified before being saved.
- Final file hash is verified after download.
- Partial progress is saved in a sidecar `.progress.json` file.
- Peer entries expire from the tracker after a timeout.
- Failed peer requests are skipped so the leecher can try another peer.

