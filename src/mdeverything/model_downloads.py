"""Supervise optional model downloads without loading inference in the API process."""

import os
import subprocess
import threading

from .jobs import JobManager
from .runtime import child_process_options, worker_command
from .speech_models import CATALOG, model_status


class ModelDownloads:
    def __init__(self):
        self.lock = threading.RLock()
        self.processes = {}
        self.stopped = False

    def list(self):
        with self.lock:
            return [
                {
                    **model_status(name),
                    "can_cancel": name in self.processes and self.processes[name].poll() is None,
                }
                for name in CATALOG
            ]

    def start(self, name):
        if name not in CATALOG:
            raise ValueError("Unsupported speech model.")
        with self.lock:
            if self.stopped:
                raise ValueError("Application is shutting down.")
            status = model_status(name)
            if status["status"] == "ready" or name in self.processes and self.processes[name].poll() is None:
                return status
            if status["status"] in ("downloading", "verifying"):
                return status  # A conversion owns this model's lock; don't spawn another download.
            if any(process.poll() is None for process in self.processes.values()):
                raise ValueError("Another model is downloading. Wait for it to finish or cancel it first.")
            process = subprocess.Popen(
                worker_command("download-model", name),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                **child_process_options(),
            )
            self.processes[name] = process
            return {**status, "status": "downloading", "can_cancel": True}

    def cancel(self, name):
        if name not in CATALOG:
            raise ValueError("Unsupported speech model.")
        with self.lock:
            process = self.processes.get(name)
            if process and process.poll() is None:
                JobManager._kill(process)
            elif model_status(name)["status"] in ("downloading", "verifying"):
                raise ValueError("A conversion is preparing this model. Cancel that conversion to stop it.")
            return model_status(name)

    def stop(self):
        with self.lock:
            self.stopped = True
            for process in self.processes.values():
                JobManager._kill(process)
