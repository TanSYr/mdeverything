"""Process entry points shared by source and self-contained desktop builds."""

import os
import subprocess
import sys
from pathlib import Path


def worker_command(mode: str, *args: str | Path) -> list[str]:
    modules = {"worker": "mdeverything.worker", "download-model": "mdeverything.speech_models"}
    if mode not in modules:
        raise ValueError(f"Unknown child process mode: {mode}")
    arguments = [str(argument) for argument in args]
    if getattr(sys, "frozen", False):
        return [sys.executable, f"--{mode}", *arguments]
    return [sys.executable, "-u", "-m", modules[mode], *arguments]


def child_process_options() -> dict:
    # Desktop stdin is the parent-lifetime pipe and has an outstanding read. Inheriting
    # it can deadlock Windows CRT startup (GetFileType waits for that synchronous IO).
    # Disposable workers receive input only through argv/files, never this pipe.
    options = {"stdin": subprocess.DEVNULL}
    if os.name == "nt":
        return {**options, "creationflags": subprocess.CREATE_NO_WINDOW}
    return {**options, "start_new_session": True}
