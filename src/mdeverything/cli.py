"""Small CLI surface over the same pipeline used by the web workspace."""

import argparse
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

from . import __version__
from .export import write_document
from .pipeline import MODELS, convert


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="mde", description="Turn videos into portable Markdown. Local-first, captions-first."
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve", help="Open the local browser workspace")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--data-dir", type=Path)
    conv = commands.add_parser("convert", help="Convert URLs or local media/subtitle files")
    conv.add_argument("sources", nargs="*")
    conv.add_argument("--batch", type=Path, help="UTF-8 file with one URL or path per line")
    conv.add_argument("-o", "--output", type=Path, default=Path("mde-output"))
    conv.add_argument("--language", default="auto")
    conv.add_argument("--model", choices=sorted(MODELS), default="base")
    conv.add_argument("--notes", action="store_true", help="Generate optional local Ollama notes")
    conv.add_argument("--cookies", type=Path, help="Your Netscape cookies file (CLI only)")
    commands.add_parser("doctor", help="Check runtime dependencies")
    args = parser.parse_args(argv)
    if args.command == "serve":
        import uvicorn

        from .api import create_app

        print(f"Open http://{args.host}:{args.port} in your browser. Press Ctrl+C to stop.")
        uvicorn.run(create_app(args.data_dir), host=args.host, port=args.port)
        return 0
    if args.command == "doctor":
        print(
            json.dumps(
                {
                    "version": __version__,
                    "python": sys.version.split()[0],
                    "ffmpeg": shutil.which("ffmpeg"),
                    "yt_dlp": importlib.util.find_spec("yt_dlp") is not None,
                    "faster_whisper": importlib.util.find_spec("faster_whisper") is not None,
                    "ollama": shutil.which("ollama"),
                },
                indent=2,
            )
        )
        return 0
    sources = list(args.sources)
    if args.batch:
        sources.extend(
            s.strip()
            for s in args.batch.read_text(encoding="utf-8").splitlines()
            if s.strip() and not s.lstrip().startswith("#")
        )
    if not sources:
        parser.error("Provide a URL/path or --batch file.")
    failures = 0
    for source in sources:
        try:
            doc = convert(
                source,
                language=args.language,
                model=args.model,
                notes=args.notes,
                cookies=str(args.cookies) if args.cookies else None,
                progress=lambda stage, percent: print(f"[{percent:3}%] {stage}", file=sys.stderr),
            )
            stem = re.sub(r"[^\w\- .]", "", doc.title)[:90].strip(" .") or "document"
            args.output.mkdir(parents=True, exist_ok=True)
            destination = args.output / stem
            number = 2
            while True:
                try:
                    destination.mkdir(exist_ok=False)
                    break
                except FileExistsError:
                    destination = args.output / f"{stem}-{number}"
                    number += 1
            write_document(doc, destination)
            print(destination.resolve() / "document.md")
        except Exception as exc:
            failures += 1
            print(f"Error: {source}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
