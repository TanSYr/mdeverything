"""One disposable process per conversion; stdout carries structured events."""

import json
import sys
from pathlib import Path

from .export import write_document
from .pipeline import convert


def emit(**data):
    print("::mde::" + json.dumps(data, ensure_ascii=False), flush=True)


def main():
    directory = Path(sys.argv[1])
    request = json.loads((directory / "request.json").read_text(encoding="utf-8"))
    try:
        doc = convert(
            request["input"],
            language=request["language"],
            model=request["model"],
            notes=request["notes"],
            title=request.get("title"),
            progress=lambda stage, progress: emit(stage=stage, progress=progress),
        )
        if request.get("display_source"):
            doc.source = request["display_source"]
        write_document(doc, directory)
        emit(title=doc.title, stage="Ready to read", progress=100)
    except Exception as exc:
        emit(error=str(exc)[:1500] or type(exc).__name__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
