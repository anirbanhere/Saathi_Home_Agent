import asyncio
import base64
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select, func
from saathi.config import Settings
from saathi.contracts import InboundMessage, Profile
from saathi.db import Store, schema
from saathi.runtime import Runtime, DomainError
from saathi.speech import fixture_audio

NOW = datetime(2026, 10, 27, 5, tzinfo=timezone.utc)


@pytest.fixture
def world(tmp_path):
    store = Store(f"sqlite:///{tmp_path / 'demo.sqlite3'}")
    runtime = Runtime(store, Settings(), clock=lambda: NOW)
    user = runtime.create_user("en-IN")
    yield runtime, user
    store.engine.dispose()


def run(coro):
    return asyncio.run(coro)


def search(runtime, user, external="one", **kwargs):
    return run(
        runtime.handle(
            user,
            InboundMessage(
                external_id=external,
                text="Book dental cleaning in Chennai 2026-10-31 morning",
                **kwargs,
            ),
        )
    )


def prepare(runtime, user):
    task = search(runtime, user)
    return runtime.preview(
        user, task["id"], task["payload"]["slots"][0]["id"], task["version"]
    )


def approve(runtime, user, task):
    a = task["payload"]["approval"]
    return runtime.decide(user, a["id"], "approve", a["token"], task["version"])


def count(runtime, table):
    with runtime.store.engine.connect() as c:
        return c.scalar(select(func.count()).select_from(table))


def test_booking_commits_once_and_survives_restart(world):
    runtime, user = world
    prepared = prepare(runtime, user)
    result = approve(runtime, user, prepared)
    assert result["status"] == "COMPLETED" and result["payload"]["receipt"][
        "reference"
    ].startswith("MOCK-")
    again = approve(runtime, user, prepared)
    assert again["payload"]["receipt"] == result["payload"]["receipt"]
    assert count(runtime, schema.operations) == 1 and count(runtime, schema.outbox) == 1
    restarted = Runtime(Store(runtime.store.url), Settings(), clock=lambda: NOW)
    assert restarted.get(user, result["id"])["status"] == "COMPLETED"
    restarted.store.engine.dispose()


def test_duplicate_inbound_and_changed_payload_are_distinct(world):
    runtime, user = world
    first = search(runtime, user)
    assert search(runtime, user) == first
    with pytest.raises(DomainError, match="different contents"):
        run(
            runtime.handle(
                user, InboundMessage(external_id="one", text="Book Chennai tomorrow")
            )
        )


def test_cross_owner_approval_and_task_reads_denied(world):
    runtime, user = world
    prepared = prepare(runtime, user)
    other = runtime.create_user("en-IN")
    with pytest.raises(DomainError):
        runtime.get(other, prepared["id"])
    with pytest.raises(DomainError):
        approve(runtime, other, prepared)
    assert count(runtime, schema.operations) == 0


def test_expired_approval_and_changed_preview_require_new_consent(world):
    runtime, user = world
    prepared = prepare(runtime, user)
    runtime.clock = lambda: NOW + timedelta(minutes=6)
    with pytest.raises(DomainError, match="expired"):
        approve(runtime, user, prepared)
    runtime.clock = lambda: NOW
    next_preview = runtime.preview(
        user, prepared["id"], prepared["payload"]["slots"][1]["id"], prepared["version"]
    )
    with pytest.raises(DomainError):
        approve(runtime, user, prepared)
    assert approve(runtime, user, next_preview)["status"] == "COMPLETED"


def test_reject_cancel_and_slot_contention_do_not_create_false_receipts(world):
    runtime, user = world
    prepared = prepare(runtime, user)
    other = runtime.create_user("en-IN")
    other_preview = prepare(runtime, other)
    assert approve(runtime, user, prepared)["status"] == "COMPLETED"
    assert approve(runtime, other, other_preview)["status"] == "REQUIRES_USER_ACTION"
    assert count(runtime, schema.operations) == 1
    cancelled = search(runtime, other, "two")
    assert (
        runtime.cancel(other, cancelled["id"], cancelled["version"])["status"]
        == "CANCELLED"
    )
    with pytest.raises(DomainError):
        runtime.cancel(
            user, prepared["id"], runtime.get(user, prepared["id"])["version"]
        )


def test_ambiguous_mock_timeout_requires_reconciliation_not_reexecute(world):
    runtime, user = world
    runtime.mock_commit_timeout = True
    prepared = prepare(runtime, user)
    result = approve(runtime, user, prepared)
    assert (
        result["status"] == "RECONCILIATION_REQUIRED"
        and "receipt" not in result["payload"]
    )
    assert approve(runtime, user, prepared)["status"] == "RECONCILIATION_REQUIRED"
    assert count(runtime, schema.operations) == 1
    result = runtime.reconcile(user, result["id"], result["version"])
    assert result["status"] == "COMPLETED" and count(runtime, schema.operations) == 1


@pytest.mark.parametrize("locale", ["en-IN", "hi-IN", "ta-IN"])
def test_mock_voice_to_approved_booking_with_all_four_profiles(world, locale):
    runtime, user = world
    message = InboundMessage(
        external_id=locale,
        locale=locale,
        audio_base64=base64.b64encode(fixture_audio(locale)).decode(),
    )
    result = run(runtime.handle(user, message))
    assert result["status"] == "PLANNED" and set(result["profiles"]) == {
        "reasoning",
        "conversation",
        "stt",
        "tts",
    }
    preview = runtime.preview(
        user, result["id"], result["payload"]["slots"][0]["id"], result["version"]
    )
    assert approve(runtime, user, preview)["status"] == "COMPLETED"


def test_clarification_pins_task_profiles_across_configuration_changes(world):
    runtime, user = world
    task = run(
        runtime.handle(
            user, InboundMessage(external_id="missing", text="Book dental cleaning")
        )
    )
    assert task["status"] == "CLARIFICATION_REQUIRED"
    runtime.settings.reasoning = Profile(
        provider="mock_alt", model="changed-for-new-tasks"
    )
    result = run(
        runtime.handle(
            user,
            InboundMessage(
                external_id="details",
                text="Chennai 2026-10-31",
                conversation_id=task["conversation_id"],
            ),
        )
    )
    assert (
        result["id"] == task["id"]
        and result["profiles"]["reasoning"]["provider"] == "mock"
    )


def test_two_concurrent_users_compete_for_one_slot_without_duplicate_booking(world):
    from concurrent.futures import ThreadPoolExecutor

    runtime, user = world
    other = runtime.create_user("en-IN")
    first, second = prepare(runtime, user), prepare(runtime, other)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(approve, runtime, u, t)
            for u, t in [(user, first), (other, second)]
        ]
        statuses = sorted(f.result()["status"] for f in futures)
    assert statuses == ["COMPLETED", "REQUIRES_USER_ACTION"]
    assert count(runtime, schema.operations) == 1


def test_raw_approval_nonce_is_not_persisted_and_tampered_preview_cannot_commit(world):
    from sqlalchemy import update

    runtime, user = world
    task = prepare(runtime, user)
    assert "token" not in runtime.get(user, task["id"])["payload"]["approval"]
    saved = runtime.get(user, task["id"])
    saved["payload"]["preview"]["amount_paise"] = 1
    with runtime.store.transaction(user) as c:
        c.execute(
            update(schema.tasks)
            .where(schema.tasks.c.id == task["id"])
            .values(payload=saved["payload"])
        )
    with pytest.raises(DomainError, match="Preview changed"):
        approve(runtime, user, task)
    assert count(runtime, schema.operations) == 0


@pytest.mark.parametrize("role", ["reasoning", "conversation", "stt", "tts"])
def test_role_swap_preserves_entire_mock_voice_booking_semantics(world, role):
    runtime, user = world
    setattr(runtime.settings, role, Profile(provider="mock_alt", model="alternate-v1"))
    task = run(
        runtime.handle(
            user,
            InboundMessage(
                external_id=role,
                locale="en-IN",
                audio_base64=base64.b64encode(fixture_audio("en-IN")).decode(),
            ),
        )
    )
    prepared = runtime.preview(
        user, task["id"], task["payload"]["slots"][0]["id"], task["version"]
    )
    completed = approve(runtime, user, prepared)
    assert completed["status"] == "COMPLETED" and count(runtime, schema.operations) == 1
    assert completed["profiles"][role]["provider"] == "mock_alt"
