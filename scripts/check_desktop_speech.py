"""End-to-end first model setup and offline frozen transcription on each native runner."""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

from smoke_desktop import speech_smoke

parser = argparse.ArgumentParser()
parser.add_argument("--engine", type=Path, required=True)
parser.add_argument("--runtime", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="mde-model-test-") as folder:
    engine = str(args.engine.resolve())
    env = {**os.environ, "MDE_MODEL_DIR": folder, "PYTHONIOENCODING": "utf-8"}
    # The actual frozen download entry tests the installed TLS/proxy dependencies too.
    subprocess.run([engine, "--download-model", "tiny"], env=env, check=True, timeout=600)
    os.environ["MDE_SMOKE_EXPECT"] = "transcript"
    speech_smoke([engine], args.runtime.resolve(), root / "tests/fixtures/original-speech.wav", folder)
