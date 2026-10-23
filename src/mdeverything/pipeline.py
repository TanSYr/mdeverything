"""Shared local-first conversion pipeline for CLI and web workers."""

import ipaddress
import re
import shutil
import socket
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from .models import Document, Segment
from .subtitles import parse_subtitles

MEDIA_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".mov",
    ".webm",
    ".avi",
    ".m4v",
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg",
    ".opus",
    ".aac",
    ".aiff",
    ".wma",
}
SUBTITLE_EXTENSIONS = {".vtt", ".srt"}
MODELS = {"tiny", "base", "small", "medium", "large-v3"}


def validate_url(value: str) -> str:
    value = value.strip()
    url = urlsplit(value)
    host = (url.hostname or "").lower().rstrip(".")
    if url.scheme not in ("https", "http") or not host or url.username or url.password:
        raise ValueError("Use an HTTP(S) video URL without embedded credentials.")
    if any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError("URLs cannot contain whitespace or control characters.")
    if (
        host == "localhost"
        or host.endswith((".localhost", ".local", ".internal"))
        or "." not in host
        and ":" not in host
    ):
        raise ValueError("Local network URLs are not supported.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            address = ipaddress.ip_address(socket.inet_aton(host))
        except OSError:
            address = None
    if address is not None and not address.is_global:
        raise ValueError("Private network URLs are not supported.")
    if url.port and url.port not in (80, 443):
        raise ValueError("Only standard HTTP(S) ports are supported.")
    if len(value) > 4096:
        raise ValueError("URL is too long.")
    return value


def choose_caption(info: dict, language: str):
    for kind in ("subtitles", "automatic_captions"):
        tracks = info.get(kind) or {}
        languages = [k for k, entries in tracks.items() if entries and k != "live_chat"]
        if language != "auto":
            languages = [k for k in languages if k == language or k.startswith(language + "-")]
        else:
            original = info.get("language") or ""
            languages.sort(key=lambda k: (k != original, k not in ("en", "zh", "zh-Hans"), k))
        if languages:
            return languages[0], kind
    return None


def _transcribe(path: Path, language: str, model: str, progress):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            'Local transcription is not installed. From the repository run: pip install -e ".[transcribe]".'
        ) from exc
    from .speech_models import ensure_model

    model_directory = ensure_model(model, progress)
    progress("Loading local speech model", 35)
    engine = WhisperModel(str(model_directory), device="cpu", compute_type="int8", local_files_only=True)
    raw, info = engine.transcribe(
        str(path), language=None if language == "auto" else language, vad_filter=True
    )
    result = []
    for segment in raw:
        if segment.text.strip():
            result.append(Segment(segment.start, segment.end, segment.text.strip()))
        progress("Transcribing on your device", min(88, 35 + int(segment.end / max(info.duration, 1) * 53)))
    if not result:
        raise ValueError("No speech detected. Check that the recording contains audible speech.")
    return result, info.language


class _QuietLogger:
    def debug(self, message):
        pass

    def warning(self, message):
        pass

    def error(self, message):
        pass


def _remote(url: str, language: str, model: str, directory: Path, progress, cookies: str | None):
    from yt_dlp import YoutubeDL

    progress("Reading source and looking for captions", 5)
    options = {
        "quiet": True,
        "no_warnings": True,
        "logger": _QuietLogger(),
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 2,
        "outtmpl": str(directory / "source.%(ext)s"),
        "restrictfilenames": True,
        "max_filesize": 2 * 1024**3,
    }
    runtimes = {name: {} for name in ("deno", "node") if shutil.which(name)}
    if runtimes:
        options["js_runtimes"] = runtimes
    if cookies:
        options["cookiefile"] = cookies
    with YoutubeDL(options) as downloader:
        downloader.params["ignore_no_formats_error"] = True
        info = downloader.extract_info(url, download=False)
    if not info or info.get("_type") in ("playlist", "multi_video") or info.get("entries") is not None:
        raise ValueError("Paste individual video URLs. Playlist expansion is not supported yet.")
    if info.get("is_live"):
        raise ValueError("Live streams are not supported. Try a finished recording.")
    choice = choose_caption(info, language)
    warnings = []
    if choice:
        lang, kind = choice
        progress("Using existing captions — no speech model needed", 20)
        try:
            caption_options = {
                **options,
                "skip_download": True,
                "ignore_no_formats_error": True,
                "writesubtitles": kind == "subtitles",
                "writeautomaticsub": kind == "automatic_captions",
                "subtitleslangs": [re.escape(lang)],
                "subtitlesformat": "vtt/srt",
            }
            with YoutubeDL(caption_options) as downloader:
                saved = downloader.extract_info(url, download=True)
            requested = (saved.get("requested_subtitles") or {}).get(lang, {})
            caption_path = requested.get("filepath")
            if not caption_path:
                candidates = list(directory.glob("*.vtt")) + list(directory.glob("*.srt"))
                caption_path = candidates[0] if candidates else None
            if not caption_path or Path(caption_path).stat().st_size > 20 * 1024**2:
                raise ValueError("Captions unavailable or larger than 20 MiB")
            segments = parse_subtitles(Path(caption_path).read_text(encoding="utf-8-sig"))
            return _document(
                info, url, lang, "auto-captions" if kind == "automatic_captions" else "captions", segments
            )
        except Exception:
            warnings.append("Captions could not be read; this document uses local speech recognition.")
    import importlib.util

    if importlib.util.find_spec("faster_whisper") is None:
        raise RuntimeError(
            'No usable captions found. Install local transcription: pip install -e ".[transcribe]" from the repository.'
        )
    progress("Downloading audio for local transcription", 22)

    def hook(event):
        if event.get("status") == "downloading":
            total = event.get("total_bytes") or event.get("total_bytes_estimate") or 0
            if total:
                progress("Downloading audio", 22 + min(7, int(event.get("downloaded_bytes", 0) / total * 7)))

    with YoutubeDL({**options, "format": "bestaudio/best", "progress_hooks": [hook]}) as downloader:
        saved = downloader.extract_info(url, download=True)
        path = Path(downloader.prepare_filename(saved))
    if not path.is_file():
        raise RuntimeError("The downloader did not produce an audio file.")
    segments, detected = _transcribe(path, language, model, progress)
    doc = _document(info, url, detected, "whisper", segments)
    doc.warnings.extend(warnings)
    return doc


def _document(info, url, language, method, segments):
    chapters = [
        {"start": float(c.get("start_time", 0)), "title": str(c.get("title") or "Chapter")}
        for c in (info.get("chapters") or [])
    ]
    return Document(str(info.get("title") or "Untitled video"), url, language, method, segments, chapters)


def convert(
    source: str, *, language="auto", model="base", notes=False, progress=None, cookies=None, title=None
) -> Document:
    if model not in MODELS:
        raise ValueError("Unsupported speech model.")
    if not re.fullmatch(r"auto|[a-z]{2,3}(?:-[A-Za-z]{2,8})?", language):
        raise ValueError("Use auto or a language code such as en, zh, ja.")
    progress = progress or (lambda stage, percent: None)
    if source.startswith(("http://", "https://")):
        url = validate_url(source)
        with tempfile.TemporaryDirectory(prefix="mde-") as temp:
            doc = _remote(url, language, model, Path(temp), progress, cookies)
    else:
        path = Path(source).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Input file does not exist: {path.name}")
        if path.suffix.lower() in SUBTITLE_EXTENSIONS:
            progress("Reading subtitle file", 25)
            if path.stat().st_size > 20 * 1024**2:
                raise ValueError("Subtitle files must be smaller than 20 MiB.")
            segments = parse_subtitles(path.read_text(encoding="utf-8-sig"))
            doc = Document(
                title or path.stem,
                path.name,
                "und" if language == "auto" else language,
                "subtitles",
                segments,
            )
        elif path.suffix.lower() in MEDIA_EXTENSIONS:
            segments, detected = _transcribe(path, language, model, progress)
            doc = Document(title or path.stem, path.name, detected, "whisper", segments)
        else:
            raise ValueError("Unsupported file. Choose video, audio, .srt or .vtt.")
    if title:
        doc.title = title
    if notes:
        from .notes import generate_notes

        progress("Writing notes with your local model", 90)
        try:
            doc.notes = generate_notes(doc)
        except Exception as exc:
            doc.warnings.append(
                f"AI notes unavailable ({type(exc).__name__}). Full transcript preserved. Check Ollama and MDE_OLLAMA_MODEL."
            )
    progress("Exporting your document", 98)
    return doc
