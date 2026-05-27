# 08 - Building EXE

ChunkShare can run with Python, but a Windows `.exe` is easier for demos.

The executable is built with PyInstaller.

## Folder Build

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1
```

Or double-click:

```text
build_exe.bat
```

## Output

After building, run:

```text
dist/ChunkShare/ChunkShare.exe
```

The build script also copies:

- `sample_files/`
- `torrents/`
- `docs/`
- `README.md`

This makes the `dist/ChunkShare/` folder easier to share for demos.

## One-File Build

If you want to send only one executable file:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_onefile_exe.ps1
```

Or double-click:

```text
build_onefile_exe.bat
```

Output:

```text
dist/ChunkShare.exe
```

This version can be sent by itself. The seeder and leechers still need the same `.mtorrent` file for the file being shared.

## How To Share With Teammates

For the folder build, share the whole folder:

```text
dist/ChunkShare/
```

Do not share only `ChunkShare.exe` if you want the sample files and docs included.

For the one-file build, share:

```text
dist/ChunkShare.exe
```

Also send the `.mtorrent` file for the file you want them to download.

## If The EXE Does Not Open

Most common cause:

```text
You sent dist/ChunkShare/ChunkShare.exe without the _internal folder.
```

Fix:

- Send the whole `dist/ChunkShare/` folder, or
- Use the one-file build at `dist/ChunkShare.exe`.

Other possible fixes:

- Right-click the EXE, choose `Properties`, then check `Unblock` if Windows shows it.
- Click the dashboard `Firewall` button and approve the Windows prompt for LAN testing.
- Or manually allow `ChunkShare.exe` through Windows Firewall.
- Keep the app window open while sharing or downloading.

## Important Notes

- The executable still runs one role at a time: tracker, seeder, or leecher.
- Across-device testing still needs multiple devices or multiple running app windows.
- The tracker must stay open while peers are using it.
- The seeder must stay open so leechers can download chunks.
- After a leecher completes the download, it becomes a seeder if it stays online.

## If Windows Shows A Security Warning

That can happen because the executable is locally built and unsigned.

For a class demo, this is usually fine. For public release, the executable would need signing, which is outside the scope of this project.
