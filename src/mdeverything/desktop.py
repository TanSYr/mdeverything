"""Frozen engine entry point. The Electron parent owns its lifetime through stdin."""

import asyncio
import json
import os
import socket
import sys
import threading


def diagnostic(stage):
    if os.environ.get("MDE_DEBUG_DESKTOP"):
        print(
            "desktop-debug "
            + json.dumps({"stage": stage, "pid": os.getpid(), "parent": os.getppid(), "args": sys.argv[1:]}),
            file=sys.stderr,
            flush=True,
        )


def self_check():
    """Import native dependencies and verify packaged speech/JavaScript assets."""
    import importlib.metadata
    from pathlib import Path

    import av
    import ctranslate2
    import faster_whisper
    import onnxruntime
    import yt_dlp
    import yt_dlp_ejs

    # Importing the native libraries catches missing dylibs/DLLs before installer creation.
    assert av.library_versions and ctranslate2.get_supported_compute_types("cpu")
    assert onnxruntime.get_available_providers()
    speech = Path(faster_whisper.__file__).parent
    assert list(speech.glob("assets/*.onnx")), "Missing Whisper VAD assets"
    javascript = Path(yt_dlp_ejs.__file__).parent
    assert list(javascript.rglob("*.js")), "Missing yt-dlp EJS JavaScript assets"
    assert yt_dlp.version.__version__
    print(
        json.dumps(
            {
                "frozen": bool(getattr(sys, "frozen", False)),
                "dependencies": {
                    name: importlib.metadata.version(name)
                    for name in ("faster-whisper", "ctranslate2", "av", "onnxruntime", "yt-dlp", "yt-dlp-ejs")
                },
            }
        ),
        flush=True,
    )
    return 0


def serve():
    import uvicorn

    from mdeverything.api import create_app

    if not os.environ.get("MDE_DESKTOP_TOKEN"):
        raise RuntimeError("Desktop engine requires MDE_DESKTOP_TOKEN from its parent")
    app = create_app()
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    listener.setblocking(False)
    port = listener.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, log_level="warning", access_log=False, timeout_graceful_shutdown=8)
    )

    def watch_parent():
        try:
            while sys.stdin.buffer.read(1):
                pass
        finally:
            server.should_exit = True

    threading.Thread(target=watch_parent, name="desktop-parent", daemon=True).start()

    async def run():
        task = asyncio.create_task(server.serve(sockets=[listener]))
        while not server.started and not task.done():
            await asyncio.sleep(0.02)
        if server.started and not server.should_exit:
            print("::mde-ready::" + json.dumps({"port": port}), flush=True)
        await task

    try:
        asyncio.run(run())
    finally:
        listener.close()
        app.state.manager.stop()
    return 0


def main():
    # PyInstaller multiprocessing children must be intercepted before parsing our flags.
    import multiprocessing

    diagnostic("before-freeze-support")
    if os.environ.get("MDE_DEBUG_DESKTOP"):
        import faulthandler

        faulthandler.enable()
        faulthandler.dump_traceback_later(20, repeat=True)
    multiprocessing.freeze_support()
    diagnostic("after-freeze-support")
    args = sys.argv[1:]
    if args[:1] == ["--worker"] and len(args) == 2:
        diagnostic("before-worker-import")
        from mdeverything.worker import main as worker_main

        diagnostic("before-worker-main")
        return worker_main(args[1])
    if args[:1] == ["--download-model"] and len(args) == 2:
        from mdeverything.speech_models import download_main

        return download_main(args[1])
    if args == ["--self-check"]:
        return self_check()
    if args:
        raise SystemExit("Expected --worker DIR, --download-model NAME, --self-check, or no arguments")
    return serve()


if __name__ == "__main__":
    sys.exit(main())
