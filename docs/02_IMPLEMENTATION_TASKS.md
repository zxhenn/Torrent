# 02 - Implementation Tasks

This checklist tracks what has been implemented and what still needs to be improved. Check items off as the team finishes them.

## Core System

- [x] Create project folder structure.
- [x] Add Python package folder: `mini_torrent/`.
- [x] Add app dashboard launcher: `app.py`.
- [x] Add dashboard-first app flow.
- [x] Add Windows shortcut launcher: `start_app.bat`.
- [x] Add one-laptop demo script: `scripts/run_local_demo.ps1`.
- [x] Add Windows EXE build script: `scripts/build_exe.ps1`.
- [x] Add Windows EXE build shortcut: `build_exe.bat`.
- [x] Add one-file EXE build script: `scripts/build_onefile_exe.ps1`.
- [x] Add one-file EXE build shortcut: `build_onefile_exe.bat`.
- [x] Add Dockerfile for container-based demos.
- [x] Add full Docker Compose demo with tracker, seeder, and leechers.
- [x] Add hybrid Docker Compose demo with host dashboard and Docker leecher.
- [x] Add manual Docker Compose peer demo for optional seeder/leecher containers.
- [x] Add separate Docker Compose files for leecher-only and seeder-only runs.
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
- [x] Add `/dashboard` browser dashboard.
- [x] Add `/api/state` dashboard data endpoint.
- [x] Add `/leave` endpoint so stopped peers disappear from the tracker.
- [x] Expire stale peers after a timeout.
- [x] Protect tracker peer table with a lock for threaded requests.
- [ ] Save tracker state to a file or database.
- [ ] Add tracker terminal command to list active peers.

## App Dashboard

- [x] Serve app dashboard from `app.py`.
- [x] Open dashboard immediately when the app starts.
- [x] Add create metadata form.
- [x] Add seed form.
- [x] Add leech form.
- [x] Add local jobs list.
- [x] Show active torrents, peers, seeders, leechers, and chunks.
- [x] Add native file picker buttons for choosing source files and `.mtorrent` files.
- [x] Add native save path buttons for metadata output and downloaded files.
- [x] Add metadata inspection so selecting a `.mtorrent` can fill useful download defaults.
- [x] Reorder toolbar actions to `Metadata`, `Seed`, `Leech`.
- [x] Add stop, resume, and delete controls for local jobs.
- [x] Show local job messages for troubleshooting download problems.
- [x] Add Windows Firewall helper button for LAN testing.

## Seeder

- [x] Implement seeder command.
- [x] Validate seeder file before uploading chunks.
- [x] Start peer server for uploading chunks.
- [x] Announce all chunks to the tracker.
- [x] Keep announcing while seeder is online.
- [x] Let dashboard stop, resume, and delete seeder jobs.
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
- [x] Add better dashboard progress display with percentage and messages.
- [x] Let dashboard stop, resume, and delete leecher jobs.
- [x] Make tracker announce timeouts non-fatal during downloads.
- [ ] Add retry limit per chunk.
- [ ] Add option to download chunks in random order.

## Distributed Behavior

- [x] Support multiple peers on different ports.
- [x] Allow leechers to upload chunks they already have.
- [x] Keep file data transfer peer-to-peer instead of through the tracker.
- [x] Add dashboard fields for LAN IP and tracker URL.
- [x] Add dashboard firewall setup for Windows LAN demos.
- [x] Add Docker demo that runs peers as separate containers.
- [x] Add Docker manual peer mode for use with `ChunkShare.exe`.
- [ ] Test on two or more laptops in the same LAN.
- [ ] Document LAN IP setup with screenshots.
- [ ] Add a demo script for localhost testing.

## Documentation

- [x] Add `README.md`.
- [x] Add `docs/00_TORRENTING_CONCEPT.md`.
- [x] Add `docs/01_PROJECT_PLAN.md`.
- [x] Add `docs/03_HOW_THE_SYSTEM_WORKS.md`.
- [x] Add `docs/04_SYSTEM_WORKFLOW.md`.
- [x] Add `docs/05_TECHNICAL_EXPLANATION.md`.
- [x] Add `docs/06_CODE_REFERENCE.md`.
- [x] Add `docs/07_TESTING_ACROSS_DEVICES.md`.
- [x] Add `docs/08_BUILDING_EXE.md`.
- [x] Add `docs/09_AI_HANDOFF_PROMPT.md`.
- [x] Add `docs/10_HOW_TO.md`.
- [x] Add `docs/11_DOCKER_DEMO.md`.
- [x] Add this implementation task checklist.
- [x] Document dashboard URL.
- [x] Add troubleshooting section.
- [ ] Add screenshots or terminal output examples.
- [ ] Add final report-ready architecture diagram.

## Testing

- [x] Run Python compile check.
- [x] Run local smoke test with tracker, seeder, and leecher.
- [x] Confirm downloaded file hash matches source file hash.
- [x] Test dashboard HTML endpoint.
- [x] Test dashboard JSON state endpoint.
- [x] Test app dashboard HTML endpoint.
- [x] Test app seed API endpoint.
- [x] Test dashboard picker buttons render in HTML.
- [x] Test dashboard JavaScript syntax after picker changes.
- [x] Test stop, resume, and delete job API.
- [x] Test local seed/leech flow after job-control changes.
- [ ] Add automated unit tests for hashing and metadata.
- [ ] Add automated integration test for tracker, seeder, and leecher.
- [ ] Test with a larger file.

## Possible Future Features

- [ ] Add rarest-first chunk selection.
- [ ] Add multiple simultaneous chunk downloads.
- [ ] Add peer blacklist for peers that send bad data.
- [x] Add app-style dashboard GUI.
- [x] Add browse file buttons or easier file path selection.
- [ ] Add authentication or peer tokens.
- [ ] Add persistent tracker storage.
- [ ] Add configuration file for default ports and tracker URL.
