"""Local workspace API. No remote authentication or arbitrary path inputs."""

import importlib.util
import json
import os
import re
import shutil
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from . import __version__
from .jobs import JobManager
from .pipeline import MEDIA_EXTENSIONS, SUBTITLE_EXTENSIONS, validate_url

PACKAGE = Path(__file__).parent
MAX_UPLOAD = 512 * 1024**2


class Options(BaseModel):
    language: str = "auto"
    model: Literal["tiny", "base", "small", "medium", "large-v3"] = "base"
    notes: bool = False

    @field_validator("language")
    @classmethod
    def valid_language(cls, value):
        if not re.fullmatch(r"auto|[a-z]{2,3}(?:-[A-Za-z]{2,8})?", value):
            raise ValueError("Use auto or a language code such as en, zh, ja.")
        return value


class Batch(Options):
    urls: list[str] = Field(min_length=1, max_length=20)

    @field_validator("urls")
    @classmethod
    def valid_urls(cls, values):
        return [validate_url(v) for v in values]


def create_app(data_dir: Path | None = None):
    directory = Path(data_dir or os.environ.get("MDE_DATA_DIR", Path.home() / ".mdeverything"))
    manager = JobManager(directory)

    @asynccontextmanager
    async def lifespan(app):
        manager.start()
        yield
        manager.stop()

    app = FastAPI(title="mdeverything", version=__version__, lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.manager = manager

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        allowed = {"localhost", "127.0.0.1", "::1"}
        allowed.update(h.strip() for h in os.environ.get("MDE_ALLOWED_HOSTS", "").split(",") if h.strip())
        if request.url.hostname not in allowed:
            return JSONResponse({"detail": "Invalid Host. This is a local workspace."}, status_code=400)
        origin = request.headers.get("origin")
        if origin:
            parsed = urlsplit(origin)
            if parsed.scheme not in ("http", "https") or parsed.netloc != request.headers.get("host"):
                return JSONResponse({"detail": "Cross-origin requests are not allowed."}, status_code=403)
        if request.method not in ("GET", "HEAD", "OPTIONS") and request.headers.get("x-mde-client") != "web":
            return JSONResponse({"detail": "Missing X-MDE-Client header."}, status_code=403)
        length = request.headers.get("content-length")
        if length:
            try:
                too_large = int(length) > MAX_UPLOAD + 1024 * 1024
            except ValueError:
                return JSONResponse({"detail": "Invalid Content-Length."}, status_code=400)
            if too_large:
                return JSONResponse({"detail": "Upload limit is 512 MiB."}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        )
        return response

    @app.exception_handler(KeyError)
    async def not_found(request, exc):
        return JSONResponse({"detail": "Job not found."}, status_code=404)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.get("/api/health")
    def health():
        return {
            "version": __version__,
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "whisper": importlib.util.find_spec("faster_whisper") is not None,
            "data_dir": str(manager.directory),
            "ollama": shutil.which("ollama") is not None or bool(os.environ.get("MDE_OLLAMA_URL")),
        }

    @app.get("/api/jobs")
    def jobs():
        return {"jobs": manager.list()}

    @app.post("/api/jobs")
    def batch(body: Batch):
        with manager.lock:
            pending = sum(j["status"] in ("queued", "running") for j in manager.list())
            if pending + len(body.urls) > 100:
                raise HTTPException(429, "Queue limit is 100 jobs.")
            return {
                "jobs": [
                    manager.create(url, language=body.language, model=body.model, notes=body.notes)
                    for url in body.urls
                ]
            }

    @app.post("/api/upload")
    async def upload(
        file: UploadFile = File(...),
        language: str = Form("auto"),
        model: str = Form("base"),
        notes: bool = Form(False),
    ):
        from pydantic import ValidationError

        try:
            options = Options(language=language, model=model, notes=notes)
        except ValidationError as exc:
            raise HTTPException(422, "Invalid language or model option.") from exc
        name = Path((file.filename or "upload").replace("\\", "/")).name
        suffix = Path(name).suffix.lower()
        if suffix not in MEDIA_EXTENSIONS | SUBTITLE_EXTENSIONS:
            raise HTTPException(415, "Choose a supported video, audio, .srt or .vtt file.")
        with tempfile.TemporaryDirectory(prefix="upload-", dir=manager.directory) as temp:
            path = Path(temp) / ("upload" + suffix)
            total = 0
            try:
                with path.open("wb") as target:
                    while chunk := await file.read(1024 * 1024):
                        total += len(chunk)
                        if total > MAX_UPLOAD:
                            raise HTTPException(413, "Upload limit is 512 MiB. Use the CLI for larger files.")
                        target.write(chunk)
                if total == 0:
                    raise HTTPException(422, "The uploaded file is empty.")
                return manager.create(name, upload=path, title=Path(name).stem, **options.model_dump())
            finally:
                await file.close()

    @app.post("/api/demo")
    def demo():
        return manager.create(
            "Original demo · demo.vtt",
            upload=PACKAGE / "data" / "demo.vtt",
            language="en",
            title="From watching to knowing",
        )

    @app.get("/api/jobs/{job_id}")
    def job(job_id: str):
        return manager.get(job_id)

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel(job_id: str):
        return manager.cancel(job_id)

    @app.post("/api/jobs/{job_id}/retry")
    def retry(job_id: str):
        return manager.retry(job_id)

    @app.delete("/api/jobs/{job_id}")
    def delete(job_id: str):
        manager.delete(job_id)
        return {"ok": True}

    def done_path(job_id):
        if manager.get(job_id)["status"] != "done":
            raise HTTPException(409, "This document is not ready yet.")
        return manager.path(job_id)

    @app.get("/api/jobs/{job_id}/document")
    def document(job_id: str):
        folder = done_path(job_id)
        return {
            "markdown": (folder / "document.md").read_text(encoding="utf-8"),
            "document": json.loads((folder / "document.json").read_text(encoding="utf-8")),
        }

    @app.get("/api/jobs/{job_id}/download")
    def download(job_id: str, format: Literal["md", "srt", "json"] = "md"):
        folder = done_path(job_id)
        title = re.sub(r"[^\w\- .]", "", manager.get(job_id)["title"])[:100].strip() or "document"
        media = {"md": "text/markdown", "srt": "application/x-subrip", "json": "application/json"}[format]
        return FileResponse(folder / f"document.{format}", media_type=media, filename=f"{title}.{format}")

    app.mount("/static", StaticFiles(directory=PACKAGE / "static"), name="static")

    @app.get("/")
    def index():
        return FileResponse(PACKAGE / "static" / "index.html")

    return app
