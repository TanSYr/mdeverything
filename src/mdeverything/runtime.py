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
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {"start_new_session": True}
