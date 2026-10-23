import time

import pytest
from fastapi.testclient import TestClient

from mdeverything.api import create_app

HEADERS = {"X-MDE-Client": "web"}


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path), base_url="http://localhost") as client:
        yield client


def wait_done(client, job):
    for _ in range(120):
        value = client.get("/api/jobs/" + job["id"]).json()
        if value["status"] in ("done", "error", "cancelled"):
            return value
        time.sleep(0.05)
    pytest.fail("Worker did not finish within 6s")


def test_demo_actual_conversion_and_all_exports(client):
    response = client.post("/api/demo", headers=HEADERS)
    assert response.status_code == 200
    job = wait_done(client, response.json())
    assert job["status"] == "done", job
    document = client.get(f"/api/jobs/{job['id']}/document").json()
    assert "Transcript" in document["markdown"]
    assert len(document["document"]["segments"]) == 8
    for fmt in ("md", "srt", "json"):
        result = client.get(f"/api/jobs/{job['id']}/download?format={fmt}")
        assert result.status_code == 200
        assert "attachment" in result.headers["content-disposition"]
    assert client.get("/api/jobs").json()["jobs"][0]["id"] == job["id"]
    assert client.delete(f"/api/jobs/{job['id']}", headers=HEADERS).status_code == 200
    assert client.get(f"/api/jobs/{job['id']}").status_code == 404


def test_upload_and_retry(client):
    text = b"1\n00:00:00,000 --> 00:00:02,000\nHello actual upload\n"
    response = client.post("/api/upload", headers=HEADERS, files={"file": ("hello.srt", text, "text/plain")})
    job = wait_done(client, response.json())
    assert job["status"] == "done", job
    retry = client.post(f"/api/jobs/{job['id']}/retry", headers=HEADERS).json()
    assert retry["id"] != job["id"]
    assert wait_done(client, retry)["status"] == "done"


def test_bad_file_has_actionable_error(client):
    response = client.post("/api/upload", headers=HEADERS, files={"file": ("bad.vtt", b"not a subtitle")})
    job = wait_done(client, response.json())
    assert job["status"] == "error"
    assert "subtitle" in job["error"].lower()


def test_api_has_no_arbitrary_file_read(client):
    response = client.post("/api/jobs", headers=HEADERS, json={"urls": ["/etc/passwd"]})
    assert response.status_code == 422
    response = client.post("/api/upload", headers=HEADERS, files={"file": ("script.py", b"print(1)")})
    assert response.status_code == 415
    assert client.get("/api/jobs/not-a-uuid/document").status_code == 404


def test_foreign_sites_cannot_submit_jobs(client):
    assert client.post("/api/demo").status_code == 403
    assert client.post("/api/demo", headers={**HEADERS, "Origin": "https://evil.example"}).status_code == 403
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 400


def test_batch_atomic_validation_and_limit(client):
    assert (
        client.post(
            "/api/jobs", headers=HEADERS, json={"urls": ["https://example.com/video", "file:///etc/passwd"]}
        ).status_code
        == 422
    )
    assert client.get("/api/jobs").json()["jobs"] == []
    assert (
        client.post(
            "/api/jobs", headers=HEADERS, json={"urls": ["https://example.com/video"] * 21}
        ).status_code
        == 422
    )


def test_restart_preserves_done_documents(tmp_path):
    with TestClient(create_app(tmp_path), base_url="http://localhost") as one:
        job = wait_done(one, one.post("/api/demo", headers=HEADERS).json())
    with TestClient(create_app(tmp_path), base_url="http://localhost") as two:
        assert two.get("/api/jobs").json()["jobs"][0]["status"] == "done"
        assert two.get(f"/api/jobs/{job['id']}/document").status_code == 200
