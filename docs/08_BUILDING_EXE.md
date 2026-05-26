# 08 - Building EXE

ChunkShare can run with Python, but a Windows `.exe` is easier for demos.

The executable is built with PyInstaller.

## Build Command

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

## How To Share With Teammates

Share the whole folder:

```text
dist/ChunkShare/
```

Do not share only `ChunkShare.exe` if you want the sample files and docs included.

## Important Notes

- The executable still runs one role at a time: tracker, seeder, or leecher.
- Across-device testing still needs multiple devices or multiple running app windows.
- The tracker must stay open while peers are using it.
- The seeder must stay open so leechers can download chunks.
- After a leecher completes the download, it becomes a seeder if it stays online.

## If Windows Shows A Security Warning

That can happen because the executable is locally built and unsigned.

For a class demo, this is usually fine. For public release, the executable would need signing, which is outside the scope of this project.

