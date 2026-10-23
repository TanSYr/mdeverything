"""Build a relocatable engine using the current (native architecture) Python."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath",
        str(ROOT / "desktop/engine"),
        "--workpath",
        str(ROOT / "desktop/.build/pyinstaller"),
        str(ROOT / "desktop/engine.spec"),
    ],
    check=True,
    cwd=ROOT,
)
