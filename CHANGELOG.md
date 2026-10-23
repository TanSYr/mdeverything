# Changelog

## 0.2.0 — 2026-10-23

Desktop preview for macOS arm64/x64 and Windows x64. Electron shell, frozen Python engine, embedded faster-whisper, FFmpeg and Node. No system Python required. Speech models download on demand with real progress, resumable partial files, integrity checks and a shared offline cache. Adds model management, persistent desktop preferences, session-token isolation, native export saves and multi-platform installer builds.

Initial desktop packages are unsigned/not notarized. Model setup requires access to Hugging Face; optional Ollama notes still need a separate installation. CPU transcription only, no automatic application updater.

## 0.1.0 — 2026-10-23

Initial alpha: local web workspace and CLI for converting video/audio/subtitles into timestamped Markdown, SRT and JSON. Includes captions-first yt-dlp integration, optional local faster-whisper transcription, persistent task queue, cancellation/retry, safe document preview, English/Chinese UI, an original demo, optional Ollama notes, Docker source build and cross-platform CI.

Known limits: no native desktop installer, playlist expansion, OCR, translation, diarization, PDF/web conversion or public multi-user hosting. Live site compatibility remains dependent on yt-dlp and platform policies.
