# 00 - Torrenting Concept

This document explains the general idea of torrenting before looking at ChunkShare.

## What Torrenting Means

Torrenting is a peer-to-peer file sharing method.

In normal downloading, one client downloads a file from one server:

```text
Server -> Downloader
```

In torrenting, many computers can help share the same file:

```text
Peer A -> Peer B
Peer C -> Peer B
Peer B -> Peer D
```

The important idea is that the file does not need to come from only one server. It can come from other users who already have the file or even users who only have some parts of the file.

Torrenting itself is just a technology. It can be used legally for things like Linux installers, public domain media, game patches, datasets, and open-source files. It can also be misused for copyrighted files. For this project, the goal is only to understand the distributed computing concept.

## Main Terms

### Torrent File

A torrent file is like an instruction sheet. It usually contains:

- File name
- File size
- Chunk or piece information
- Hashes for checking correctness
- Tracker information

In our project, the `.mtorrent` file plays this role.

### Peer

A peer is any computer participating in the file sharing network.

A peer can download, upload, or do both.

### Seeder

A seeder is a peer that has the complete file.

Seeders are important because they can provide every chunk of the file.

### Leecher

A leecher is a peer that is still downloading the file.

In casual usage, people sometimes use "leecher" to mean someone who only downloads and does not upload. In technical torrenting, a leecher can still upload the chunks it already has.

### Swarm

A swarm is the group of peers sharing the same file.

Example:

```text
1 seeder + 5 leechers = 6 peers in the swarm
```

### Tracker

A tracker is a server that helps peers find each other.

The tracker does not usually send the actual file. It only tells peers where other peers are.

In our project:

```text
Tracker = peer directory
Seeder/Leecher = actual file transfer
```

## Why Files Are Split Into Chunks

A torrent does not usually send the whole file as one big block. It splits the file into many small chunks.

Example:

```text
File: game.iso

Chunk 0
Chunk 1
Chunk 2
Chunk 3
...
```

This helps because:

- A leecher can download different chunks from different peers.
- A peer can upload chunks even before finishing the whole file.
- Bad or corrupted chunks can be rejected without restarting the entire download.
- The download can resume if interrupted.

## Why Hashing Is Needed

Hashing gives each chunk a unique fingerprint.

When a peer receives a chunk, it hashes the chunk and compares it to the expected hash.

```text
Downloaded chunk hash == Expected chunk hash
```

If they match, the chunk is accepted.

If they do not match, the chunk is rejected.

This prevents corrupted or wrong data from becoming part of the final file.

## How Downloading Works

Basic torrent-like flow:

1. User opens a torrent metadata file.
2. Client asks the tracker for peers.
3. Tracker returns a list of peers.
4. Client asks peers for missing chunks.
5. Client verifies each chunk using hashes.
6. Client saves valid chunks.
7. Client also uploads chunks it already has.
8. When all chunks are complete, the client verifies the final file.

## Are Fewer Leechers Slower?

Not always.

Download speed depends mostly on:

- Number of seeders
- Seeder upload speed
- Number of peers that have useful chunks
- Network speed
- How many people are competing for upload bandwidth
- Whether leechers are also uploading chunks

The simple rule is:

```text
More seeders usually means faster downloads.
No seeders usually means the file may never complete.
```

Leechers are different. More leechers can make the download slower if they only take bandwidth from a few seeders. But leechers can also make the swarm faster if they upload chunks to each other.

Example:

```text
1 seeder + 1 leecher
The leecher can only get chunks from the seeder.

1 seeder + 5 leechers
The leechers can get chunks from the seeder and from each other.
```

So the better explanation is:

```text
Fewer seeders usually makes downloads slower.
Fewer useful peers can make downloads slower.
More leechers can help or hurt depending on whether they upload.
```

## Why Torrenting Is Distributed Computing

Torrenting is distributed because the work is shared across many machines.

Instead of one server doing all the uploading:

```text
Server uploads 100 percent of the file to everyone.
```

The peers help each other:

```text
Seeder uploads chunk 1 to Peer A.
Seeder uploads chunk 2 to Peer B.
Peer A uploads chunk 1 to Peer B.
Peer B uploads chunk 2 to Peer A.
```

This spreads the workload across the network.

## How Our Project Relates To Real Torrenting

ChunkShare copies the basic ideas:

- A metadata file describes the shared file.
- The file is split into chunks.
- Each chunk has a SHA-256 hash.
- A tracker helps peers find each other.
- A seeder uploads chunks.
- A leecher downloads chunks.
- A leecher can become a seeder.

Our project does not implement the full BitTorrent protocol. It is a smaller version made for learning and demonstration.

## Simple Mental Model

Think of the file like a puzzle.

- The metadata file is the picture on the box.
- Each chunk is one puzzle piece.
- The hash checks if the piece is correct.
- The tracker tells you who has pieces.
- Seeders have the full puzzle.
- Leechers are still completing the puzzle.
- Once a leecher gets pieces, it can share those pieces too.
