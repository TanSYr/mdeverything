# Desktop builds

The application is an Electron window around the same local conversion API used by the source edition. A PyInstaller one-directory bundle contains Python, the application, yt-dlp and faster-whisper's native dependencies. Separate bundled executables provide FFmpeg/ffprobe and Node. End users install only the desktop package; model weights download through the app when needed.

## Build from source

Use the target OS and architecture; PyInstaller is not a cross-compiler. Use Python 3.11 and Node 22+ for the build tooling (these are build-machine requirements only).

```bash
python -m pip install -e '.[dev,transcribe]' -r desktop/requirements.txt
python scripts/prepare_runtime.py
python scripts/build_engine.py
python scripts/smoke_desktop.py --engine desktop/engine/mde-engine/mde-engine --runtime desktop/runtime
cd desktop
npm ci
npm test
npm run dist
```

On Windows, use `desktop/engine/mde-engine/mde-engine.exe` for `--engine`.

See `.github/workflows/desktop.yml` for the authoritative platform prerequisites and exact commands, including the native FFmpeg compiler toolchain. Generated engines/runtime/build folders are ignored by Git. Installer outputs are in `desktop/release/`. Runtime downloads and sources are pinned and verified; models are not inside an installer. Keep dependency licenses and the included FFmpeg source/build recipe when redistributing.

## Process and security boundary

The main process generates a session token and passes it to the backend through its environment. The backend chooses a free loopback port and reports readiness. The shell adds the token only to requests for that exact local origin. The renderer remains sandboxed, cannot run Node or request arbitrary local paths, and opens external links in the default browser. Existing same-origin and mutation-header protections also apply.

The desktop app uses its OS application-data directory, separate from the installed application, for library, preferences and models. One conversion runs at a time. A conversion and a setup download share a cross-process model lock. Stopping the app closes backend stdin, shuts down the server, and terminates active child processes.

## Verification and release

The desktop workflow builds macOS arm64, macOS x64 and Windows x64. Before packaging, the frozen smoke script validates native imports/assets, bundled executable availability, unauthorized API rejection, a real subtitle conversion, output download and graceful shutdown with a minimal PATH. This prevents an installed system Python from hiding missing runtime files. A separate speech check uses an original synthetic recording and the downloaded Tiny model; model downloads are not mocked for that check.

Initial packages are unsigned and not notarized. The release must disclose platform verification prompts. No automatic updater is enabled. Release installer assets only after CI and frozen smoke checks pass; include SHA256SUMS. Developer signing/notarization needs separate maintained credentials and is a future release task.
