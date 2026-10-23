import subprocess
from unittest.mock import Mock

import pytest

from mdeverything import model_downloads


def test_managed_download_has_private_stdin_and_can_cancel(monkeypatch):
    process = Mock()
    process.poll.return_value = None
    launch = Mock(return_value=process)
    kill = Mock()
    monkeypatch.setattr(model_downloads.subprocess, "Popen", launch)
    monkeypatch.setattr(model_downloads.JobManager, "_kill", kill)
    monkeypatch.setattr(model_downloads, "model_status", lambda name: {"name": name, "status": "missing"})
    manager = model_downloads.ModelDownloads()
    result = manager.start("tiny")
    assert result["can_cancel"] and result["status"] == "downloading"
    assert launch.call_args.kwargs["stdin"] == subprocess.DEVNULL
    assert launch.call_args.args[0][-1] == "tiny"
    manager.start("tiny")
    assert launch.call_count == 1
    manager.cancel("tiny")
    kill.assert_called_once_with(process)
    manager.stop()
    with pytest.raises(ValueError, match="shutting down"):
        manager.start("base")
