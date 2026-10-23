"""Verified, resumable speech weights shared by desktop, CLI and job workers."""

import hashlib
import json
import os
import shutil
import sys
import time
from contextlib import nullcontext
from pathlib import Path

import httpx
from filelock import FileLock, Timeout

CATALOG = json.loads((Path(__file__).parent / "data" / "speech-models.json").read_text())


def model_root():
    return Path(os.environ.get("MDE_MODEL_DIR", Path.home() / ".mdeverything" / "models"))


def model_path(name):
    if name not in CATALOG:
        raise ValueError("Unsupported speech model.")
    return model_root() / f"{name}-{CATALOG[name]['revision'][:12]}"


def _write(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value), encoding="utf-8")
    temp.replace(path)


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _fingerprint(path):
    stat = path.stat()
    return [stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino]


def _ready(name):
    folder = model_path(name)
    meta = CATALOG[name]
    ready = _read(folder / "ready.json")
    if ready.get("revision") != meta["revision"]:
        return False
    try:
        return all(
            (folder / f["name"]).is_file()
            and (folder / f["name"]).stat().st_size == f["size"]
            and _fingerprint(folder / f["name"]) == ready.get("files", {}).get(f["name"])
            for f in meta["files"]
        )
    except OSError:
        return False


def _lock(name):
    root = model_root()
    root.mkdir(parents=True, exist_ok=True)
    return FileLock(str(root / f"{name}.lock"))


def model_status(name):
    folder = model_path(name)
    meta = CATALOG[name]
    result = {
        "name": name,
        "total_bytes": meta["bytes"],
        "downloaded_bytes": 0,
        "status": "missing",
        "error": None,
    }
    if _ready(name):
        return {**result, "status": "ready", "downloaded_bytes": meta["bytes"]}
    stored = _read(folder / "status.json")
    result.update({k: v for k, v in stored.items() if k in ("status", "downloaded_bytes", "error")})
    if result["status"] == "ready":
        result.update(
            status="error",
            error="Model files changed or are incomplete. Download again to verify and repair.",
        )
    try:
        with _lock(name).acquire(timeout=0):
            if result["status"] in ("downloading", "verifying"):
                result["status"] = "paused"
    except Timeout:
        result["status"] = stored.get("status") if stored.get("status") == "verifying" else "downloading"
    return result


def _verify(path, item):
    if not path.is_file() or path.stat().st_size != item["size"]:
        return False
    digest = hashlib.sha256() if item.get("sha256") else hashlib.sha1(usedforsecurity=False)
    if not item.get("sha256"):
        digest.update(f"blob {item['size']}\0".encode())
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest() == (item.get("sha256") or item["git_sha1"])


def _fetch(client, url, target, item, report):
    partial = target.with_suffix(target.suffix + ".part")
    start = partial.stat().st_size if partial.exists() else 0
    if start > item["size"]:
        partial.unlink()
        start = 0
    if start < item["size"]:
        with client.stream("GET", url, headers={"Range": f"bytes={start}-"} if start else {}) as response:
            response.raise_for_status()
            if response.status_code == 206:
                expected = f"bytes {start}-"
                if not response.headers.get("Content-Range", "").startswith(expected):
                    raise ValueError("Invalid download range. Retry the model download.")
            elif response.status_code == 200:
                start = 0  # The server may ignore Range; never append a full response.
            else:
                raise ValueError("Unexpected model download response.")
            with partial.open("ab" if start else "wb") as stream:
                for chunk in response.iter_bytes(256 * 1024):
                    if start + len(chunk) > item["size"]:
                        raise ValueError("Model download exceeds the expected size.")
                    stream.write(chunk)
                    start += len(chunk)
                    report(start, False)
    report(start, True)
    if not _verify(partial, item):
        partial.unlink(missing_ok=True)
        raise ValueError("Model checksum mismatch. Retry to download a fresh copy.")
    partial.replace(target)


def ensure_model(name, progress=None, *, client=None):
    """Return a complete local model. No network at all when already installed."""
    folder = model_path(name)
    if _ready(name):
        return folder
    progress = progress or (lambda stage, percent: None)
    progress("Waiting for speech model download", 30)
    with _lock(name):
        if _ready(name):
            return folder
        folder.mkdir(parents=True, exist_ok=True)
        meta = CATALOG[name]
        completed = 0
        last_report = 0
        downloaded = 0

        def report(current, verifying=False, force=False):
            nonlocal last_report, downloaded
            downloaded = completed + current
            now = time.monotonic()
            if not force and not verifying and now - last_report < 0.3:
                return
            last_report = now
            _write(
                folder / "status.json",
                {
                    "status": "verifying" if verifying else "downloading",
                    "downloaded_bytes": downloaded,
                    "error": None,
                },
            )
            stage = (
                "Verifying speech model" if verifying else "Downloading speech model"
            ) + f" · {name} · {downloaded / 1024**2:.1f} / {meta['bytes'] / 1024**2:.1f} MiB"
            progress(stage, 30 + min(4, int(downloaded / meta["bytes"] * 4)))

        try:
            report(0, force=True)
            existing = sum(
                min((folder / (f["name"] + ".part")).stat().st_size, f["size"])
                for f in meta["files"]
                if (folder / (f["name"] + ".part")).exists()
            )
            existing += sum(f["size"] for f in meta["files"] if (folder / f["name"]).exists())
            if shutil.disk_usage(folder).free < max(0, meta["bytes"] - existing) + 64 * 1024**2:
                raise OSError("Not enough disk space for this model. Free space or choose Tiny.")
            context = (
                nullcontext(client)
                if client is not None
                else httpx.Client(follow_redirects=True, timeout=httpx.Timeout(60, connect=20))
            )
            with context as connection:
                for item in meta["files"]:
                    target = folder / item["name"]
                    if not _verify(target, item):
                        target.unlink(missing_ok=True)
                        url = (
                            f"https://huggingface.co/{meta['repo']}/resolve/{meta['revision']}/{item['name']}"
                        )
                        _fetch(connection, url, target, item, report)
                    completed += item["size"]
                    report(0, force=True)
            _write(
                folder / "ready.json",
                {
                    "revision": meta["revision"],
                    "files": {f["name"]: _fingerprint(folder / f["name"]) for f in meta["files"]},
                },
            )
            _write(
                folder / "status.json", {"status": "ready", "downloaded_bytes": meta["bytes"], "error": None}
            )
            return folder
        except Exception as exc:
            # Avoid persisting redirect URLs or signed CDN query strings from HTTP errors.
            detail = (
                str(exc)
                if isinstance(exc, (ValueError, OSError))
                else f"{type(exc).__name__}: model download interrupted. Check your connection to huggingface.co, then retry."
            )
            _write(
                folder / "status.json",
                {"status": "error", "downloaded_bytes": downloaded, "error": detail[:500]},
            )
            raise


def download_main(name):
    from .worker import emit

    try:
        ensure_model(name, lambda stage, progress: emit(stage=stage, progress=progress))
        emit(stage="Speech model ready", progress=100)
        return 0
    except Exception:
        emit(error=model_status(name).get("error") or "Model download failed. Please retry.")
        return 1


if __name__ == "__main__":
    sys.exit(download_main(sys.argv[1]))
