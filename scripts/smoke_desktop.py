"""Exercise a frozen engine with no Python or developer tools on its PATH."""

import argparse
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path


def smoke(command, runtime):
    with tempfile.TemporaryDirectory(prefix="mde-desktop-smoke-") as temporary:
        root = Path(temporary)
        env = dict(os.environ)
        env.update(
            MDE_DATA_DIR=str(root / "workspace"),
            MDE_MODEL_DIR=str(root / "models"),
            MDE_DESKTOP_TOKEN="desktop-smoke-secret",
            PATH=str(runtime / "bin")
            + os.pathsep
            + (str(Path(os.environ["SystemRoot"]) / "System32") if os.name == "nt" else "/usr/bin:/bin"),
            PYTHONIOENCODING="utf-8",
            MDE_DEBUG_DESKTOP="1",
        )
        # Isolate frozen dispatch from the API supervisor before testing its lifetime pipe.
        direct = root / "direct-worker"
        direct.mkdir()
        (direct / "input.vtt").write_text("WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nDesktop worker probe.\n")
        (direct / "request.json").write_text(
            json.dumps(
                {"input": str(direct / "input.vtt"), "language": "en", "model": "tiny", "notes": False}
            )
        )
        try:
            probe = subprocess.run(
                [*command, "--worker", str(direct)],
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise AssertionError(
                f"Direct frozen worker hung. stdout={exc.stdout!r} stderr={exc.stderr!r}"
            ) from exc
        assert probe.returncode == 0, probe.stdout + probe.stderr
        assert (direct / "document.md").is_file(), probe.stdout + probe.stderr
        print(json.dumps({"direct_worker": "passed", "minimal_path": True}), flush=True)
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=env,
        )
        lines = queue.Queue()
        errors = []
        threading.Thread(target=lambda: [lines.put(line) for line in process.stdout], daemon=True).start()
        threading.Thread(target=lambda: errors.extend(process.stderr), daemon=True).start()
        try:
            deadline = time.monotonic() + 90
            origin = None
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise AssertionError("Engine exited: " + "".join(errors)[-3000:])
                try:
                    line = lines.get(timeout=0.2)
                except queue.Empty:
                    continue
                if line.startswith("::mde-ready::"):
                    origin = "http://127.0.0.1:" + str(json.loads(line[13:])["port"])
                    break
            assert origin, "Engine readiness timed out"

            def request(path, *, method="GET", auth=True):
                headers = {"X-MDE-Client": "web"}
                if auth:
                    headers["X-MDE-Token"] = env["MDE_DESKTOP_TOKEN"]
                req = urllib.request.Request(origin + path, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=15) as response:
                    return response.read()

            try:
                request("/api/health", auth=False)
            except urllib.error.HTTPError as exc:
                assert exc.code == 403, exc.code
            else:
                raise AssertionError("Desktop API accepted a request without the token")
            health = json.loads(request("/api/health"))
            assert health["whisper"] and health["ffmpeg"], health
            assert b"mdeverything" in request("/")
            job = json.loads(request("/api/demo", method="POST"))
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                jobs = json.loads(request("/api/jobs"))["jobs"]
                state = next(item for item in jobs if item["id"] == job["id"])
                if state["status"] in ("done", "error", "cancelled"):
                    break
                time.sleep(0.1)
            if state["status"] != "done":
                listing = [str(file.relative_to(root)) for file in root.rglob("*") if file.is_file()]
                processes = ""
                if os.name == "nt":
                    powershell = (
                        Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
                    )
                    snapshot = subprocess.run(
                        [
                            str(powershell),
                            "-NoProfile",
                            "-Command",
                            "Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'mde-engine.exe'} | "
                            "Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    processes = snapshot.stdout
                raise AssertionError(
                    json.dumps(
                        {
                            "job": state,
                            "files": listing,
                            "server_debug": "".join(errors)[-12000:],
                            "processes": processes,
                        }
                    )
                )
            markdown = request(f"/api/jobs/{job['id']}/download?format=md")
            assert b"Transcript" in markdown and b"timestamp" in markdown, markdown[:200]
            assert not list((root / "models").glob("**/model.bin")), "Demo downloaded a speech model"
            process.stdin.close()
            assert process.wait(timeout=20) == 0, "Engine did not exit gracefully on stdin EOF"
            print(
                json.dumps(
                    {
                        "result": "passed",
                        "health": health,
                        "demo": state["status"],
                        "minimal_path": True,
                        "stdin_shutdown": True,
                    }
                )
            )
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)


def speech_smoke(command, runtime, audio, models):
    """Optional real inference, using an already verified model cache with network disabled."""
    with tempfile.TemporaryDirectory(prefix="mde-speech-smoke-") as temporary:
        folder = Path(temporary)
        request = {"input": str(Path(audio).resolve()), "language": "en", "model": "tiny", "notes": False}
        (folder / "request.json").write_text(json.dumps(request))
        env = dict(os.environ)
        env.update(
            MDE_MODEL_DIR=str(Path(models).resolve()),
            HF_HUB_OFFLINE="1",
            HTTP_PROXY="http://127.0.0.1:1",
            HTTPS_PROXY="http://127.0.0.1:1",
            ALL_PROXY="http://127.0.0.1:1",
            NO_PROXY="",
            PATH=str(runtime / "bin"),
            PYTHONIOENCODING="utf-8",
        )
        result = subprocess.run(
            [*command, "--worker", str(folder)],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        document = json.loads((folder / "document.json").read_text())
        assert document["method"] == "whisper" and document["segments"], document
        if os.environ.get("MDE_SMOKE_EXPECT"):
            assert (
                os.environ["MDE_SMOKE_EXPECT"].lower()
                in " ".join(segment["text"] for segment in document["segments"]).lower()
            ), document
        print(
            json.dumps(
                {
                    "speech": "passed",
                    "offline": True,
                    "transcript": " ".join(segment["text"] for segment in document["segments"]),
                }
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path)
    parser.add_argument("--runtime", type=Path, required=True)
    args = parser.parse_args()
    smoke(
        [str(args.engine.resolve())] if args.engine else [sys.executable, "-m", "mdeverything.desktop"],
        args.runtime.resolve(),
    )

    if os.environ.get("MDE_SMOKE_AUDIO"):
        speech_smoke(
            [str(args.engine.resolve())] if args.engine else [sys.executable, "-m", "mdeverything.desktop"],
            args.runtime.resolve(),
            os.environ["MDE_SMOKE_AUDIO"],
            os.environ["MDE_SMOKE_MODELS"],
        )
