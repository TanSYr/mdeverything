# Product and architecture

mdeverything turns videos into documents you own. Its first release deliberately focuses on video, audio, and subtitles. “Everything” is a direction, not a claim that every URL or file type works.

## Why this exists

Video2Text established the local download → audio → faster-whisper workflow. DownVid demonstrates the value of making yt-dlp accessible through a coherent interface, dependency guidance and well-presented open-source documentation. mdeverything builds an independent implementation around the resulting document: source, timestamps, chapters, complete transcript and optional local AI notes.

## v0.1 contract

- Paste individual video URLs (batch up to 20), or upload a local media/subtitle file.
- Prefer captions in the requested language; use local speech recognition when unavailable. Auto language prefers original/manual captions. Language selection controls transcription, not translation.
- Preserve evidence: timestamped transcript and available source chapters. Never replace transcript with a summary.
- Export self-contained Markdown, SRT and JSON. No image dependencies.
- Local browser workspace and CLI share the same conversion pipeline. No account or paid API key.
- Optional Ollama notes are explicitly generated, may contain errors, and cannot change the underlying transcript. Long transcripts are processed in bounded chunks.
- Durable single-worker queue, honest stage updates, cancellation, retry and searchable history.

## Modules

`models` is the document contract. `subtitles` parses and deduplicates rolling captions. `pipeline` resolves input, obtains captions or audio and transcribes. `export` emits portable outputs. `notes` is the optional local generation adapter. `worker` is an isolated process per job, allowing cancellation to terminate model work. `jobs` persists jobs and supervises the worker. `api` serves only the workspace and generated artifacts. `cli` exposes conversion and local serving.

Data flows from URL/upload → job request → worker → document model → exports. The UI reads job state and documents; it never receives arbitrary filesystem access. SQLite and job files are stored in the user-selected data directory. Uploads and intermediate media stay local and can be deleted with the job.

## Boundaries

No native installer yet; no OCR, diarization, translation or PDF support. No hosted public multi-user service. yt-dlp platform support changes over time; authenticated content may need a user-provided cookies file via CLI. No bundled credentials, signing helpers, browser scraping fallback, telemetry or tracking. Models require an initial download. Docker is provided as a source build, not an already-published registry image.
