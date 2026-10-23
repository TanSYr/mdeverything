import hashlib
import json

import httpx
import pytest

from mdeverything import speech_models as sm


@pytest.fixture
def model(tmp_path, monkeypatch):
    data = b"original synthetic weights for download tests"
    record = {"name": "model.bin", "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    monkeypatch.setattr(
        sm,
        "CATALOG",
        {
            "tiny": {
                "repo": "Systran/faster-whisper-tiny",
                "revision": "a" * 40,
                "bytes": len(data),
                "files": [record],
            }
        },
    )
    monkeypatch.setenv("MDE_MODEL_DIR", str(tmp_path))
    return data, tmp_path


def client_for(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def test_download_verified_then_works_offline(model):
    data, root = model
    with client_for(lambda request: httpx.Response(200, content=data)) as client:
        path = sm.ensure_model("tiny", client=client)
    assert (path / "model.bin").read_bytes() == data
    assert sm.model_status("tiny")["status"] == "ready"
    with client_for(lambda request: pytest.fail("Ready model must not use network")) as client:
        assert sm.ensure_model("tiny", client=client) == path
    (path / "model.bin").unlink()
    assert sm.model_status("tiny")["status"] != "ready"


def test_download_resumes_and_checks_content_range(model):
    data, root = model
    folder = sm.model_path("tiny")
    folder.mkdir(parents=True)
    (folder / "model.bin.part").write_bytes(data[:8])

    def response(request):
        assert request.headers["range"] == "bytes=8-"
        return httpx.Response(
            206, headers={"Content-Range": f"bytes 8-{len(data) - 1}/{len(data)}"}, content=data[8:]
        )

    with client_for(response) as client:
        sm.ensure_model("tiny", client=client)
    assert sm.model_status("tiny")["status"] == "ready"


def test_ignored_range_restarts_safely(model):
    data, root = model
    folder = sm.model_path("tiny")
    folder.mkdir(parents=True)
    (folder / "model.bin.part").write_bytes(b"old partial")
    with client_for(lambda request: httpx.Response(200, content=data)) as client:
        sm.ensure_model("tiny", client=client)
    assert (folder / "model.bin").read_bytes() == data


def test_bad_hash_never_becomes_ready(model):
    data, root = model
    with client_for(lambda request: httpx.Response(200, content=b"x" * len(data))) as client:
        with pytest.raises(ValueError, match="checksum"):
            sm.ensure_model("tiny", client=client)
    assert sm.model_status("tiny")["status"] == "error"
    assert not (sm.model_path("tiny") / "ready.json").exists()
    assert not (sm.model_path("tiny") / "model.bin.part").exists()


def test_interrupted_download_can_retry(model):
    data, root = model
    with client_for(lambda request: httpx.Response(503)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            sm.ensure_model("tiny", client=client)
    with client_for(lambda request: httpx.Response(200, content=data)) as client:
        sm.ensure_model("tiny", client=client)
    assert sm.model_status("tiny")["status"] == "ready"


def test_invalid_model_rejected_before_path_access(model):
    with pytest.raises(ValueError):
        sm.model_path("../../outside")


def test_stale_downloading_state_is_paused(model):
    _, root = model
    folder = sm.model_path("tiny")
    folder.mkdir(parents=True)
    (folder / "status.json").write_text(json.dumps({"status": "downloading", "downloaded_bytes": 10}))
    assert sm.model_status("tiny")["status"] == "paused"


def test_same_size_corruption_can_be_repaired(model):
    data, _ = model
    with client_for(lambda request: httpx.Response(200, content=data)) as client:
        path = sm.ensure_model("tiny", client=client)
        (path / "model.bin").write_bytes(b"x" * len(data))
        sm.ensure_model("tiny", client=client)
    assert (path / "model.bin").read_bytes() == data
    assert sm.model_status("tiny")["status"] == "ready"


def test_cached_model_is_verified_even_with_unchanged_stat(model, monkeypatch):
    data, _ = model
    with client_for(lambda request: httpx.Response(200, content=data)) as client:
        path = sm.ensure_model("tiny", client=client)
        fingerprint = sm._fingerprint(path / "model.bin")
        (path / "model.bin").write_bytes(b"z" * len(data))
        monkeypatch.setattr(sm, "_fingerprint", lambda path: fingerprint)
        assert sm._ready("tiny")  # Simulate a filesystem with unchanged timestamp metadata.
        sm.ensure_model("tiny", client=client)
    assert (path / "model.bin").read_bytes() == data
