import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from mdeverything import jobs, runtime


def test_frozen_worker_dispatch_uses_engine_flags(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert runtime.worker_command("worker", Path("job-dir")) == [sys.executable, "--worker", "job-dir"]
    assert runtime.worker_command("download-model", "tiny") == [sys.executable, "--download-model", "tiny"]


def test_source_worker_dispatch_uses_python_modules(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert runtime.worker_command("worker", "folder")[1:] == ["-u", "-m", "mdeverything.worker", "folder"]
    with pytest.raises(ValueError):
        runtime.worker_command("arbitrary-module")


def test_windows_cancellation_terminates_descendants(monkeypatch):
    process = Mock(pid=123)
    process.poll.return_value = None
    run = Mock()
    with monkeypatch.context() as patch:
        patch.setattr(jobs.os, "name", "nt")
        patch.setattr(subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
        patch.setattr(subprocess, "run", run)
        jobs.JobManager._kill(process)
    assert run.call_count == 1
    assert run.call_args.args[0][-4:] == ["/PID", "123", "/T", "/F"]
    assert run.call_args.kwargs["creationflags"] == 0x08000000
