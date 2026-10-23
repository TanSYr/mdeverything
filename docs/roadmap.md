# Roadmap

A useful release beats a broad promise. Dates are intentionally not committed before feasibility is tested.

## Shipped in 0.1

- Local browser workspace and CLI
- URL input via yt-dlp, captions-first and local Whisper fallback
- Local video/audio and SRT/VTT input
- Source metadata, timestamped transcripts, upstream chapters
- Markdown, SRT and JSON output
- Single-worker persisted queue, cancel/retry/delete, searchable history
- English/Chinese UI, responsive layout, explicit working demo
- Optional local Ollama notes
- Source Docker configuration, source/wheel distribution, CI matrix

## Shipped in 0.2 desktop preview

- macOS Apple Silicon/Intel and Windows x64 packaging with embedded Python, Whisper engine, FFmpeg and Node
- Model setup with real download progress, checksum verification, cancellation and resume
- Automatic model preparation on first transcription; offline recordings after setup
- Per-session desktop API token, isolated renderer, native export save dialog
- Persistent preferences, library and models outside the application

## Next: first-use experience

1. Developer signing/notarization, tested automatic updates and broader real-device installer testing.
2. Real platform compatibility fixtures, extractor error guidance and more robust rolling-caption handling.
3. Save an entire playlist into a clean folder of documents, with explicit limits.
4. Import cookies securely for authenticated content without exposing them to the renderer.

## Then: richer documents

- Optional keyframes and slide OCR with original timestamps
- Speaker labels and editable transcript corrections
- Optional translation that preserves the original text
- Obsidian-friendly output templates and frontmatter customization

## Later: everything

PDF, web articles and other formats should use independent input adapters feeding the same portable document contract. These are not current capabilities.

## What we optimize for

Time to first useful document, successful conversions, repeat use and reproducible community contributions. Stars reflect discovery; they are not a reason to ship fake platform claims or require users to star before using the software.
