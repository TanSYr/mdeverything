# Third-party notices and provenance

This repository's source code and original demo text are licensed under MIT. Dependencies, model weights and third-party media retain their own licenses.

- yt-dlp: https://github.com/yt-dlp/yt-dlp — see its LICENSE and bundled-component notices.
- faster-whisper / CTranslate2: https://github.com/SYSTRAN/faster-whisper and https://github.com/OpenNMT/CTranslate2 — see upstream licenses.
- FastAPI: https://github.com/fastapi/fastapi — MIT.
- FFmpeg: https://ffmpeg.org/legal.html — licensing depends on build configuration. The Docker image installs the distribution package; this repository does not distribute a custom FFmpeg binary.
- Ollama and selected models: https://github.com/ollama/ollama — model licenses vary; models are downloaded separately by the user.

Product inspiration: https://github.com/Downvid/downvid. No DownVid source, logo, screenshots or trademark assets are copied into this repository. The UI and document model are original.

The author's earlier local Video2Text project informed the download → transcription workflow and offline-cache-first model loading. This project was implemented independently around a shared Python document pipeline. No vendored Douyin signing code or browser-cookie scraping helpers from the earlier project are included.

The demo transcript is original, contains no third-party video transcript, and is included under this repository's MIT license. Screenshots demonstrate that bundled text through the real conversion pipeline.
