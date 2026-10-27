import pytest
from fastapi.testclient import TestClient
from saathi.config import Settings
from saathi.main import create_app

BASE = "http://127.0.0.1:8781"
HEADERS = {"Origin": BASE, "Content-Type": "application/json"}


@pytest.fixture
def client(tmp_path):
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'api.sqlite3'}"))
    with TestClient(app, base_url=BASE) as client:
        response = client.post(
            "/api/session", json={"consent_mock_data": True}, headers=HEADERS
        )
        assert response.status_code == 200
        client.headers.update({**HEADERS, "X-Saathi-CSRF": response.json()["csrf"]})
        yield client
    app.state.runtime.store.engine.dispose()


def test_full_authenticated_web_flow_and_cached_inbound_do_not_repeat_booking(client):
    message = {"external_id": "one", "text": "Book dental cleaning in Chennai tomorrow"}
    result = client.post("/api/chat/messages", json=message)
    assert result.status_code == 200, result.text
    task = result.json()
    assert client.post("/api/chat/messages", json=message).json() == task
    preview = client.post(
        f"/api/tasks/{task['id']}/preview",
        json={"version": task["version"], "slot_id": task["payload"]["slots"][0]["id"]},
    ).json()
    a = preview["payload"]["approval"]
    decision = {
        "version": preview["version"],
        "token": a["token"],
        "decision": "approve",
    }
    done = client.post(f"/api/approvals/{a['id']}/decision", json=decision).json()
    assert done["status"] == "COMPLETED"
    assert (
        client.post(f"/api/approvals/{a['id']}/decision", json=decision).json() == done
    )
    assert (
        "token"
        not in client.get(f"/api/tasks/{task['id']}").json()["payload"]["approval"]
    )


def test_origin_csrf_identity_override_and_ownership(client):
    body = {"external_id": "one", "text": "Book Chennai tomorrow"}
    assert (
        client.post(
            "/api/chat/messages", json=body, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/chat/messages", json=body, headers={"X-Saathi-CSRF": "wrong"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/chat/messages", json={**body, "user_id": "forged"}
        ).status_code
        == 422
    )
    task = client.post("/api/chat/messages", json=body).json()
    client.post("/api/session", json={"consent_mock_data": True})
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404


def test_health_no_live_webhooks_and_operator_only_profiles(client):
    assert client.get("/health/ready").json()["mode"] == "mock"
    assert not client.get("/health/live").json()["whatsapp_production_eligible"]
    assert (
        client.get("/api/provider-connections").json()["profiles"]["stt"]["provider"]
        == "mock"
    )
    assert client.post("/webhooks/whatsapp", json={}).status_code == 404
    assert (
        client.post("/api/provider-connections", json={"provider": "paid"}).status_code
        == 405
    )


@pytest.mark.parametrize("locale", ["en-IN", "hi-IN", "ta-IN"])
def test_api_audio_fixture_to_approval_and_mock_audio_reply(client, locale):
    fixture = client.get(f"/api/fixtures/{locale}").json()
    task = client.post(
        "/api/chat/messages",
        json={
            "external_id": locale,
            "locale": locale,
            "audio_base64": fixture["audio_base64"],
        },
    ).json()
    assert task["status"] == "PLANNED"
    preview = client.post(
        f"/api/tasks/{task['id']}/preview",
        json={"version": task["version"], "slot_id": task["payload"]["slots"][0]["id"]},
    ).json()
    approval = preview["payload"]["approval"]
    completed = client.post(
        f"/api/approvals/{approval['id']}/decision",
        json={
            "version": preview["version"],
            "token": approval["token"],
            "decision": "approve",
        },
    ).json()
    assert (
        completed["status"] == "COMPLETED" and completed["payload"]["receipt"]["mock"]
    )
    audio = client.get(f"/api/tasks/{task['id']}/audio").json()
    assert audio["mock"] and audio["mime"] == "audio/wav" and "tone" in audio["notice"]
