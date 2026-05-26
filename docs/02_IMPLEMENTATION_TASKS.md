# 02 - Implementation Tasks

This checklist tracks what has been implemented and what still needs to be improved. Check items off as the team finishes them.

## Core System

- [x] Create project folder structure.
- [x] Add Python package folder: `mini_torrent/`.
- [x] Add sample input folder: `sample_files/`.
- [x] Add downloads folder: `downloads/`.
- [x] Add torrent metadata folder: `torrents/`.
- [x] Add documentation folder: `docs/`.

## Hashing

- [x] Implement SHA-256 hashing for bytes.
- [x] Implement SHA-256 hashing for whole files.
- [x] Use whole-file hash to verify completed downloads.
- [x] Use chunk hashes to verify downloaded chunks.
- [ ] Add a command that only verifies a local file against a `.mtorrent` file.

## Chunking

- [x] Split files into fixed-size chunks.
- [x] Support a smaller final chunk.
- [x] Store all chunk hashes in the `.mtorrent` metadata file.
- [x] Write downloaded chunks directly to the correct file position.
- [ ] Add clearer terminal output showing chunk size and total chunks during download.

## Torrent Metadata

- [x] Create `.mtorrent` JSON metadata files.
- [x] Store file name, file size, chunk size, whole-file hash, and chunk hashes.
- [x] Load `.mtorrent` files from disk.
- [x] Validate missing or invalid metadata fields.
- [ ] Add a sample metadata explanation diagram for the final report.

## Tracker

- [x] Implement tracker HTTP server.
- [x] Add `/announce` endpoint for peer registration.
- [x] Add `/peers` endpoint for peer discovery.
- [x] Add `/health` endpoint for simple checking.
- [x] Expire stale peers after a timeout.
- [x] Protect tracker peer table with a lock for threaded requests.
- [ ] Save tracker state to a file or database.
- [ ] Add tracker terminal command to list active peers.

## Seeder

- [x] Implement seeder command.
- [x] Validate seeder file before uploading chunks.
- [x] Start peer server for uploading chunks.
- [x] Announce all chunks to the tracker.
- [x] Keep announcing while seeder is online.
- [ ] Show upload count per chunk.
- [ ] Add cleaner shutdown message with total chunks served.

## Leecher

- [x] Implement leecher command.
- [x] Ask tracker for peers.
- [x] Download missing chunks from available peers.
- [x] Verify every chunk before saving.
- [x] Save progress to a `.progress.json` file.
- [x] Resume previously downloaded valid chunks.
- [x] Verify whole file after all chunks are downloaded.
- [x] Let leecher stay online as a seeder after download.
- [ ] Add better progress display with percentage.
- [ ] Add retry limit per chunk.
- [ ] Add option to download chunks in random order.

## Distributed Behavior

- [x] Support multiple peers on different ports.
- [x] Allow leechers to upload chunks they already have.
- [x] Keep file data transfer peer-to-peer instead of through the tracker.
- [ ] Test on two or more laptops in the same LAN.
- [ ] Document LAN IP setup with screenshots.
- [ ] Add a demo script for localhost testing.

## Documentation

- [x] Add `README.md`.
- [x] Add `docs/01_PROJECT_PLAN.md`.
- [x] Add `docs/03_HOW_THE_SYSTEM_WORKS.md`.
- [x] Add `docs/04_SYSTEM_WORKFLOW.md`.
- [x] Add `docs/05_TECHNICAL_EXPLANATION.md`.
- [x] Add `docs/06_CODE_REFERENCE.md`.
- [x] Add this implementation task checklist.
- [ ] Add screenshots or terminal output examples.
- [ ] Add final report-ready architecture diagram.
- [ ] Add troubleshooting section.

## Testing

- [x] Run Python compile check.
- [x] Run local smoke test with tracker, seeder, and leecher.
- [x] Confirm downloaded file hash matches source file hash.
- [ ] Add automated unit tests for hashing and metadata.
- [ ] Add automated integration test for tracker, seeder, and leecher.
- [ ] Test with a larger file.

## Possible Future Features

- [ ] Add rarest-first chunk selection.
- [ ] Add multiple simultaneous chunk downloads.
- [ ] Add peer blacklist for peers that send bad data.
- [ ] Add simple GUI.
- [ ] Add authentication or peer tokens.
- [ ] Add persistent tracker storage.
- [ ] Add configuration file for default ports and tracker URL.
