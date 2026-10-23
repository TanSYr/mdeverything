"""Durable single-worker queue; SQLite state, isolated cancellable processes."""

import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

TERMINAL = {"done", "error", "cancelled"}


def now():
    return datetime.now(UTC).isoformat()


class JobManager:
    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.database = self.directory / "jobs.sqlite3"
        self.lock = threading.RLock()
        self.wake = threading.Event()
        self.stopping = threading.Event()
        self.process = None
        self.active_id = None
        self.thread = None
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        for job in self.list():
            if job["status"] == "running":
                self.update(
                    job["id"],
                    status="error",
                    stage="Interrupted",
                    error="Server stopped during conversion. Retry this job.",
                )

    def connect(self):
        return sqlite3.connect(self.database, timeout=20)

    def start(self):
        self.thread = threading.Thread(target=self._run, name="mde-queue", daemon=True)
        self.thread.start()

    def stop(self):
        self.stopping.set()
        self.wake.set()
        with self.lock:
            if self.process:
                self._kill(self.process)
        if self.thread:
            self.thread.join(timeout=6)

    def list(self):
        with self.lock, self.connect() as db:
            rows = db.execute("SELECT payload FROM jobs").fetchall()
        return sorted((json.loads(row[0]) for row in rows), key=lambda j: j["created_at"], reverse=True)

    def get(self, job_id):
        with self.lock, self.connect() as db:
            row = db.execute("SELECT payload FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return json.loads(row[0])

    def path(self, job_id):
        self.get(job_id)  # IDs must exist before they can address the filesystem.
        return self.directory / job_id

    def update(self, job_id, **changes):
        with self.lock, self.connect() as db:
            job = self.get(job_id)
            job.update(changes, updated_at=now())
            db.execute("UPDATE jobs SET payload=? WHERE id=?", (json.dumps(job), job_id))
        return job

    def create(self, source, *, language="auto", model="base", notes=False, upload=None, title=None):
        with self.lock:
            if sum(j["status"] not in TERMINAL for j in self.list()) >= 100:
                raise ValueError("Queue is full (100 jobs). Wait for a job to finish.")
            job_id = uuid.uuid4().hex
            folder = self.directory / job_id
            folder.mkdir()
            input_source = source
            if upload:
                target = folder / ("input" + Path(upload).suffix.lower())
                shutil.copyfile(upload, target)
                input_source = str(target)
            request = {
                "input": input_source,
                "display_source": source,
                "language": language,
                "model": model,
                "notes": notes,
                "title": title,
            }
            (folder / "request.json").write_text(json.dumps(request), encoding="utf-8")
            job = {
                "id": job_id,
                "source": source,
                "title": title or source,
                "status": "queued",
                "stage": "Waiting in queue",
                "progress": 0,
                "error": None,
                "created_at": now(),
                "updated_at": now(),
                "language": language,
                "model": model,
                "notes": notes,
            }
            with self.connect() as db:
                db.execute("INSERT INTO jobs VALUES (?, ?)", (job_id, json.dumps(job)))
        self.wake.set()
        return job

    def cancel(self, job_id):
        with self.lock:
            job = self.get(job_id)
            if job["status"] in TERMINAL:
                return job
            job = self.update(job_id, status="cancelled", stage="Cancelled")
            if self.active_id == job_id and self.process:
                self._kill(self.process)
            return job

    def retry(self, job_id):
        with self.lock:
            job = self.get(job_id)
            if job["status"] not in TERMINAL:
                raise ValueError("Only finished jobs can be retried.")
            request = json.loads((self.path(job_id) / "request.json").read_text())
            source = request["input"]
            upload = source if Path(source).is_file() else None
            return self.create(
                job["source"],
                language=job["language"],
                model=job["model"],
                notes=job["notes"],
                upload=upload,
                title=request.get("title"),
            )

    def delete(self, job_id):
        with self.lock:
            if self.get(job_id)["status"] not in TERMINAL or self.active_id == job_id:
                raise ValueError("Wait for the worker to stop before deleting this job.")
            folder = self.path(job_id)
            with self.connect() as db:
                db.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def _kill(process):
        if process.poll() is not None:
            return
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                process.kill()

    def _run(self):
        while not self.stopping.is_set():
            self.wake.clear()
            queued = [j for j in reversed(self.list()) if j["status"] == "queued"]
            if not queued:
                self.wake.wait(timeout=1)
                continue
            job = queued[0]
            try:
                self._execute(job["id"])
            except KeyError:
                # A queued job may be cancelled/deleted after the snapshot.
                continue
            except Exception as exc:
                with self.lock:
                    self.process = None
                    self.active_id = None
                    try:
                        if self.get(job["id"])["status"] != "cancelled":
                            self.update(job["id"], status="error", stage="Failed", error=str(exc)[:1500])
                    except KeyError:
                        pass

    def _execute(self, job_id):
        with self.lock:
            if self.get(job_id)["status"] != "queued" or self.stopping.is_set():
                return
            folder = self.path(job_id)
            self.update(job_id, status="running", stage="Starting conversion")
            self.active_id = job_id
            # Put temporary media inside the job directory so cancel/delete can clean it.
            temp = folder / "tmp"
            temp.mkdir(exist_ok=True)
            env = {
                **os.environ,
                "TMPDIR": str(temp),
                "TMP": str(temp),
                "TEMP": str(temp),
                "PYTHONIOENCODING": "utf-8",
            }
            self.process = subprocess.Popen(
                [sys.executable, "-u", "-m", "mdeverything.worker", str(folder)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                start_new_session=os.name == "posix",
            )
            process = self.process
        error = None
        for line in process.stdout:
            if not line.startswith("::mde::"):
                continue
            try:
                event = json.loads(line[7:])
            except ValueError:
                continue
            with self.lock:
                if self.get(job_id)["status"] == "cancelled":
                    continue
                if "error" in event:
                    error = event["error"]
                else:
                    self.update(
                        job_id, **{k: v for k, v in event.items() if k in ("stage", "progress", "title")}
                    )
        code = process.wait()
        process.stdout.close()
        with self.lock:
            self.process = None
            self.active_id = None
            if self.get(job_id)["status"] != "cancelled":
                if code == 0 and (folder / "document.json").is_file():
                    self.update(job_id, status="done", progress=100, stage="Ready to read")
                else:
                    self.update(
                        job_id,
                        status="error",
                        stage="Failed",
                        error=error or "Conversion was interrupted. Retry or check your input.",
                    )
        shutil.rmtree(temp, ignore_errors=True)
