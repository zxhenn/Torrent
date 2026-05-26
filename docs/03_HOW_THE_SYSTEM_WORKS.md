# 03 - How The System Works

Imagine the shared file is too large to send as one piece. The system cuts it into smaller chunks. Each chunk gets its own fingerprint using SHA-256 hashing.

The `.mtorrent` file is the instruction sheet. It tells every peer:

- What the file is called
- How large the file is
- How large each chunk should be
- What the correct final file hash is
- What the correct hash of each chunk is

The tracker is like a directory. It does not hold the file. It only remembers which peers are online and which chunks they say they have.

A seeder starts with the full file. It checks that the file matches the `.mtorrent` metadata, then tells the tracker:

> I am online, and I have these chunks.

A leecher starts without the full file. It asks the tracker:

> Who has chunks for this file?

The tracker replies with peer addresses. The leecher then asks those peers directly for chunks. This is the distributed part: the file data moves between peers, not through the tracker.

When the leecher receives a chunk, it hashes the bytes and compares the result with the expected chunk hash from the `.mtorrent` file.

- If the hash matches, the chunk is saved.
- If the hash does not match, the chunk is rejected.

After all chunks are downloaded, the leecher hashes the final output file. If the final hash matches the metadata, the download is successful.

Once the leecher has chunks, it can also upload those chunks to other leechers. After downloading the whole file, it effectively becomes another seeder.

This is the basic idea behind torrent-style sharing:

- Files are split into chunks.
- Chunks are verified by hash.
- Peers discover each other through a tracker.
- Peers exchange chunks directly.
- Downloaders can become uploaders.
