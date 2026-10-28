from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from saathi.main import create_app
from saathi.config import Settings
from saathi.speech import fixture_audio

BASE = "http://127.0.0.1:8781"


@pytest.fixture
def client(tmp_path):
    app = create_app(
        Settings(
            database_url=f"sqlite:///{tmp_path / 'api.sqlite3'}",
            media_root=str(tmp_path / "audio"),
        )
    )
    with TestClient(app, base_url=BASE) as client:
        session = client.post(
            "/api/session",
            json={"consent_mock_data": True},
            headers={"Origin": BASE, "Content-Type": "application/json"},
        ).json()
        client.headers.update(
            {
                "Origin": BASE,
                "Content-Type": "application/json",
                "X-Saathi-CSRF": session["csrf"],
            }
        )
        yield client
    app.state.runtime.store.engine.dispose()


def upload(client, **headers):
    return client.post(
        "/api/media",
        content=fixture_audio("en-IN"),
        headers={
            "Content-Type": "audio/wav",
            "X-Saathi-Media-Consent": "local-review",
            **headers,
        },
    )


def test_upload_playback_metadata_and_delete_are_private(client):
    response = upload(client)
    assert response.status_code == 201, response.text
    record = response.json()
    assert not record["transcribed"] and "path" not in record
    assert client.get("/api/media").json()[0]["id"] == record["id"]
    content = client.get(f"/api/media/{record['id']}/content")
    assert content.content == fixture_audio("en-IN")
    assert content.headers["content-type"].startswith("audio/wav")
    assert content.headers["cache-control"] == "no-store"
    assert content.headers["x-content-type-options"] == "nosniff"
    assert (
        client.delete(
            f"/api/media/{record['id']}", headers={"X-Saathi-CSRF": "forged"}
        ).status_code
        == 403
    )
    assert client.delete(f"/api/media/{record['id']}").status_code == 200
    assert client.delete(f"/api/media/{record['id']}").json()["state"] == "deleted"
    assert client.get(f"/api/media/{record['id']}/content").status_code == 410


def test_cross_session_content_and_delete_fail_without_existence_leak(client):
    record = upload(client).json()
    session = client.post("/api/session", json={"consent_mock_data": True}).json()
    client.headers["X-Saathi-CSRF"] = session["csrf"]
    assert client.get("/api/media").json() == []
    assert client.get(f"/api/media/{record['id']}").status_code == 404
    assert client.get(f"/api/media/{record['id']}/content").status_code == 404
    assert client.delete(f"/api/media/{record['id']}").status_code == 404


def test_upload_consent_origin_csrf_and_chunked_size_limits(client):
    assert upload(client, **{"X-Saathi-Media-Consent": ""}).status_code == 403
    assert upload(client, **{"Origin": "https://evil.example"}).status_code == 403
    assert upload(client, **{"X-Saathi-CSRF": "wrong"}).status_code == 403
    assert upload(client, **{"Content-Type": "audio/mpeg"}).status_code == 403
    oversized = client.post(
        "/api/media",
        content=iter([b"x" * 1_000_000, b"x" * 1_000_001]),
        headers={"Content-Type": "audio/wav", "X-Saathi-Media-Consent": "local-review"},
    )
    assert oversized.status_code == 413
    assert client.get("/api/media").json() == []
    # The larger allowance is not inherited by the existing chat boundary.
    assert (
        client.post("/api/chat/messages", content=iter([b" " * 60001])).status_code
        == 413
    )


def test_expired_media_is_not_playable_and_not_transcribed(client):
    record = upload(client).json()
    media = client.app.state.media
    now = media.clock()
    media.clock = lambda: now + timedelta(hours=1)
    assert client.get(f"/api/media/{record['id']}").json()["state"] == "expired"
    assert client.get(f"/api/media/{record['id']}/content").status_code == 410
    assert client.get("/api/tasks").json() == []
