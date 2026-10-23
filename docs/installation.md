# Installation and troubleshooting

## Desktop installers

Download from the [v0.2.0 desktop preview release](https://github.com/TanSYr/mdeverything/releases/tag/v0.2.0). Select macOS arm64 for Apple Silicon, macOS x64 for Intel, or Windows x64. Linux can use the source or Docker edition. Windows ARM is not a native target in this release.

- **macOS:** open the `.dmg`, drag mdeverything to Applications, then open it. These preview packages are not signed with an Apple Developer ID or notarized. macOS may require approval in **System Settings → Privacy & Security → Open Anyway** after the first launch attempt. Only approve the release you intentionally downloaded and checked. No command to disable Gatekeeper is needed or recommended.
- **Windows:** run the `.exe` installer. This unsigned preview can trigger SmartScreen's unknown-publisher prompt. Confirm the downloaded file and its checksum before using **More info → Run anyway**, if offered by your system. Managed computers may require administrator approval.

Python, Whisper's inference engine, FFmpeg and Node are included. **Do not install Python or run pip for the desktop edition.** Start with the included demo, which works without downloading a model. In Settings, prepare a speech model or let the first audio conversion prepare it automatically. Model download progress is measured in bytes, cancellation preserves partial downloads, and retry resumes them. Models are checked before being marked ready.

Model setup connects to `huggingface.co` and its CDN. If it fails, check network access, disk space and proxy connectivity, then use Resume / retry. Local recordings stay on your machine. Existing captions and `.srt`/`.vtt` files do not require Whisper weights. Optional AI notes still require a separately installed and running Ollama service.

The library and models persist outside the app: macOS `~/Library/Application Support/mdeverything/`, Windows `%APPDATA%/mdeverything/`. The exact workspace location appears in Settings. Replacing/upgrading the application preserves that directory. Removing the app alone may leave these files; back up documents before manually removing application data. Desktop updates are manual in this preview.

## Source install

Use Python 3.11–3.13. Create an isolated virtual environment before installing.

```bash
git clone https://github.com/TanSYr/mdeverything.git
cd mdeverything
python -m venv .venv
```

Activate on macOS/Linux: `source .venv/bin/activate`. On Windows PowerShell: `.venv\Scripts\Activate.ps1`; on cmd: `.venv\Scripts\activate.bat`. If PowerShell activation is restricted, use `.venv\Scripts\python.exe -m pip ...` and `.venv\Scripts\mde.exe serve` directly.

```bash
python -m pip install -e ".[transcribe]"
mde doctor
mde serve
```

Open http://127.0.0.1:8765. If occupied, `mde serve --port 8790` and open that port. Keep the terminal running; Ctrl+C shuts down the app. Running jobs become retryable errors on interruption; queued jobs resume on the next start. Do not run two server processes against the same data directory.

For captions/subtitles only, install `python -m pip install -e .`. To use uv: `uv sync --extra transcribe`, then `uv run mde serve`. This project has not been published to PyPI; install from source or the release wheel.

## FFmpeg

- macOS with Homebrew: `brew install ffmpeg`
- Debian/Ubuntu: `sudo apt-get install ffmpeg`
- Windows: install an FFmpeg build linked from [ffmpeg.org](https://ffmpeg.org/download.html) and put its `bin` folder on PATH.

Run `mde doctor` to inspect detection. faster-whisper uses PyAV for decoding; FFmpeg is useful for yt-dlp media processing and manual conversion. No FFmpeg is needed for subtitle files.

## YouTube JavaScript runtime

Current yt-dlp uses an external JavaScript runtime for YouTube challenges. Install [Deno](https://deno.com/) (2.3+) or [Node.js](https://nodejs.org/) (22+) on PATH. mdeverything auto-detects both; yt-dlp EJS scripts are installed with the default dependency extra. The Docker source build includes Node 22. See the [upstream EJS setup guide](https://github.com/yt-dlp/yt-dlp/wiki/EJS). Some videos may still require platform authentication/PO tokens or remain unavailable.

## Speech models

Choose tiny for a fast smoke test, base for a small default, small/medium for better accuracy at greater CPU/memory cost. large-v3 is available but can be slow on a CPU. This release uses CPU/int8, including on Apple Silicon; it does not implement Metal acceleration.

Models use an application-managed, revision-pinned cache: source edition `~/.mdeverything/models`, desktop edition its application-data `models` subfolder. `MDE_MODEL_DIR` overrides the location for developer runs. Existing Hugging Face caches from v0.1 are not automatically migrated. Model setup uses resumable downloads and verifies each file; interrupted jobs leave partial downloads ready for retry. Once ready, loading a model makes no model-host requests. Cancel terminates the relevant download/job worker.

| Model | Download (rounded) |
| --- | ---: |
| Tiny | 75 MiB |
| Base | 141 MiB |
| Small | 464 MiB |
| Medium | 1.43 GiB |
| Large v3 | 2.88 GiB |

Larger models can require several GiB of working memory and significantly more CPU time. Start with Tiny or Base.

## Authenticated websites

CLI supports an explicitly provided Netscape-format cookies file:

```bash
mde convert "https://example.com/your-video" --cookies /path/to/cookies.txt
```

Cookies are sensitive credentials. Keep them outside the repository, never post them in an issue, and only use your own authorized session. The web UI does not read browser cookies or upload cookies in this release. Site errors may also be caused by extractor changes; update with `pip install -U yt-dlp`, retry, and include a sanitized error in your report.

## Output and retention

The web app stores SQLite job history, requests, uploaded inputs and exported documents in `~/.mdeverything`. Change with `mde serve --data-dir /your/path` or `MDE_DATA_DIR`. Completed remote downloads are temporary; user uploads remain available for retry. Delete a terminal job from the library to remove its saved data. CLI writes to `./mde-output` by default; `-o` changes this.

Web uploads are limited to 512 MiB (subtitle parsing to 20 MiB). For larger media, use the CLI. URL batches are limited to 20 per request with 100 pending jobs total. One conversion runs at a time to keep CPU and memory predictable. Playlists are not expanded.

## Ollama notes

Run Ollama locally and download a suitable model. `MDE_OLLAMA_MODEL` selects it; default is `qwen3:8b`. Set before starting the server. On Windows PowerShell, `$env:MDE_OLLAMA_MODEL="qwen3:8b"; mde serve`.

Notes are opt-in. The health indicator reports installation/configuration availability, not that the daemon or chosen model is ready. If Ollama is offline, the transcript is still exported with a warning. Long transcripts produce chunk notes rather than an all-document synthesis; transcripts over 600,000 characters skip notes with a warning.

Docker's localhost refers to the container. To use host Ollama on Docker Desktop, configure `MDE_OLLAMA_URL=http://host.docker.internal:11434` and make sure your Ollama daemon accepts that local connection. No Docker-host Ollama setup is performed automatically.

## Limits to expect

- Platform captions and speech recognition can both be inaccurate; check source timestamps.
- Requested language is subtitle/recognition selection, not translation.
- Captions may be unavailable even when visible in a website's browser player.
- Not every yt-dlp site has been tested with this release.
- DRM, ongoing live streams, speaker labels, OCR and PDF/web inputs are not implemented.
- Use the app locally with trusted inputs. It is not a public SaaS server.
