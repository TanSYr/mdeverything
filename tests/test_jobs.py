import json

from mdeverything.jobs import JobManager
from mdeverything.pipeline import convert


def test_cancel_queued_job_and_retry_survives_original_deletion(tmp_path):
    source = tmp_path / "speech.srt"
    source.write_text("1\n00:00:00,000 --> 00:00:01,000\nHi\n")
    jobs = JobManager(tmp_path / "data")
    original = jobs.create("speech.srt", upload=source)
    assert jobs.cancel(original["id"])["status"] == "cancelled"
    retry = jobs.retry(original["id"])
    jobs.delete(original["id"])
    request = json.loads((jobs.path(retry["id"]) / "request.json").read_text())
    assert convert(request["input"]).segments[0].text == "Hi"


def test_restart_marks_running_interrupted_and_keeps_queued(tmp_path):
    jobs = JobManager(tmp_path)
    running = jobs.create("https://example.com/a")
    queued = jobs.create("https://example.com/b")
    jobs.update(running["id"], status="running")
    restarted = JobManager(tmp_path)
    assert restarted.get(running["id"])["status"] == "error"
    assert "stopped" in restarted.get(running["id"])["error"]
    assert restarted.get(queued["id"])["status"] == "queued"


def test_optional_notes_failure_keeps_transcript(tmp_path, monkeypatch):
    from mdeverything import notes

    def unavailable(doc):
        raise ConnectionError("offline")

    monkeypatch.setattr(notes, "generate_notes", unavailable)
    path = tmp_path / "a.srt"
    path.write_text("1\n00:00:00,000 --> 00:00:01,000\nOriginal evidence\n")
    doc = convert(str(path), notes=True)
    assert doc.segments[0].text == "Original evidence"
    assert doc.notes is None and doc.warnings


def test_deleted_queued_snapshot_does_not_kill_scheduler(tmp_path, monkeypatch):
    import threading

    jobs = JobManager(tmp_path / "data")
    removed = jobs.create("https://example.com/removed")
    reached = threading.Event()
    proceed = threading.Event()
    original = jobs._execute

    def controlled(job_id):
        if job_id == removed["id"]:
            reached.set()
            assert proceed.wait(3)
        return original(job_id)

    monkeypatch.setattr(jobs, "_execute", controlled)
    jobs.start()
    try:
        assert reached.wait(3)
        jobs.cancel(removed["id"])
        jobs.delete(removed["id"])
        proceed.set()
        source = tmp_path / "a.srt"
        source.write_text("1\n00:00:00,000 --> 00:00:01,000\nStill alive\n")
        next_job = jobs.create("a.srt", upload=source)
        import time

        for _ in range(80):
            if jobs.get(next_job["id"])["status"] == "done":
                break
            time.sleep(0.05)
        assert jobs.get(next_job["id"])["status"] == "done"
    finally:
        proceed.set()
        jobs.stop()
