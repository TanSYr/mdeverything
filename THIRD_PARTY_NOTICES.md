# Third-party notices and provenance

This repository's source code and original demo text are licensed under MIT. Dependencies, model weights and third-party media retain their own licenses.

- yt-dlp: https://github.com/yt-dlp/yt-dlp — see its LICENSE and bundled-component notices.
- faster-whisper / CTranslate2: https://github.com/SYSTRAN/faster-whisper and https://github.com/OpenNMT/CTranslate2 — see upstream licenses.
- FastAPI: https://github.com/fastapi/fastapi — MIT.
- FFmpeg: https://ffmpeg.org/legal.html — licensing depends on build configuration. The Docker image installs the distribution package; desktop packages include separately built FFmpeg/ffprobe executables with their upstream LGPL/build/source notices under `runtime/licenses`. Exact version, hashes and upstream source links are in `desktop/runtime-manifest.json` and the runtime preparation script (built with GPL and nonfree options disabled). The MIT license for our source does not relicense bundled dependencies.
- Ollama and selected models: https://github.com/ollama/ollama — model licenses vary; models are downloaded separately by the user.

Product inspiration: https://github.com/Downvid/downvid. No DownVid source, logo, screenshots or trademark assets are copied into this repository. The UI and document model are original.

The author's earlier local Video2Text project informed the download → transcription workflow and offline-cache-first model loading. This project was implemented independently around a shared Python document pipeline. No vendored Douyin signing code or browser-cookie scraping helpers from the earlier project are included.

The demo transcript is original, contains no third-party video transcript, and is included under this repository's MIT license. Screenshots demonstrate that bundled text through the real conversion pipeline.

Desktop packages additionally include Electron (MIT and bundled Chromium/third-party notices), Node.js (MIT and its bundled third-party licenses), and a frozen Python runtime (PSF license). The packaging script retains dependency license files and runtime notices. See `desktop/engine.spec`, `desktop/package-lock.json` and `desktop/runtime-manifest.json` for provenance. Speech model weights are downloaded separately from the SYSTRAN faster-whisper repositories, whose model cards declare MIT licensing; exact revisions and hashes are pinned in `src/mdeverything/data/speech-models.json`.
