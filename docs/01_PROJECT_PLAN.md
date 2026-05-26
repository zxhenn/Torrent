# 01 - Project Plan

ChunkShare is a small torrent-like distributed file sharing system. It is not a full BitTorrent client. The goal is to show the basic distributed computing ideas clearly:

- Hashing
- Chunking
- Seeding
- Leeching
- Peer discovery through a tracker

## What We Will Do

1. Create metadata for a file.
   - The metadata stores the file name, file size, chunk size, whole-file hash, and every chunk hash.

2. Run a tracker.
   - The tracker remembers which peers have chunks.
   - The tracker does not store or transfer the shared file.

3. Run a seeder.
   - A seeder has the complete file.
   - It announces its chunks to the tracker.
   - It uploads requested chunks to leechers.

4. Run a leecher.
   - A leecher asks the tracker for peers.
   - It downloads missing chunks from peers.
   - It checks every chunk hash before saving.
   - After finishing, it can stay online and become another seeder.

5. Provide an app-style dashboard.
   - The dashboard opens first.
   - It can create metadata, start seeders, start leechers, and show swarm state.

## What Is Done

- Python package structure created in `mini_torrent/`.
- SHA-256 file hashing implemented.
- SHA-256 chunk hashing implemented.
- Torrent metadata generation implemented.
- Tracker server implemented.
- Tracker dashboard implemented.
- App dashboard with seed/leech controls implemented.
- Peer upload server implemented.
- Seeder command implemented.
- Leecher command implemented.
- Dashboard app implemented.
- Windows launcher and local demo script added.
- Windows EXE build script added.
- Cross-device testing guide added.
- Resume progress file implemented for partial downloads.
- Documentation structure created in `docs/`.
- Included sample file created at `sample_files/hello.txt`.
- Sample metadata created at `torrents/hello.txt.mtorrent`.
- Local smoke test passed with tracker, seeder, and leecher.
- Dashboard HTTP and tracker state endpoint tested locally.
- Dashboard app API tested locally.

## What We Should Do Next

- Use `docs/02_IMPLEMENTATION_TASKS.md` as the main team checklist.
- Add screenshots or terminal logs for the final report.
- Add dashboard screenshot for the final report.
- Test on two different laptops in the same network.
- Add a simple diagram to the report.
- Add optional chunk selection strategy like rarest-first.
- Add automated tests if required by the instructor.
- Improve the app UI if there is extra time.

## Current Limitations

- This is not the real BitTorrent protocol.
- The tracker stores peer data only in memory.
- Peers communicate through simple HTTP endpoints.
- There is no encryption or authentication.
- Peers trust the tracker list, but chunks are still verified by hash.
