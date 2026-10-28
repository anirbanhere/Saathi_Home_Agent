import io
import wave
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from saathi.config import Settings
from saathi.db import Store
from saathi.runtime import Runtime, DomainError
from saathi.media import MediaStore
from saathi.speech import fixture_audio

NOW = datetime(2026, 10, 28, 6, tzinfo=timezone.utc)


def wav_seconds(seconds):
    output = io.BytesIO()
    with wave.open(output, "wb") as clip:
        clip.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        clip.writeframes(b"\0\0" * int(seconds * 16000))
    return output.getvalue()


@pytest.fixture
def media_world(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'media.sqlite3'}",
        media_root=str(tmp_path / "audio"),
    )
    store = Store(settings.database_url)
    runtime = Runtime(store, settings)
    media = MediaStore(store, settings, clock=lambda: NOW)
    users = [runtime.create_user("en-IN") for _ in range(2)]
    yield media, users
    store.engine.dispose()


def test_owner_lifecycle_restart_and_repeat_delete(media_world):
    media, (user, other) = media_world
    audio = fixture_audio("en-IN")
    saved = media.upload(user, audio, "audio/wav", consent=True)
    assert saved["duration_ms"] == 250 and saved["bytes"] == len(audio)
    assert "path" not in saved and media.content(user, saved["id"]) == audio
    restarted = MediaStore(media.store, media.settings, clock=lambda: NOW)
    assert restarted.content(user, saved["id"]) == audio
    for action in [
        lambda: media.get(other, saved["id"]),
        lambda: media.content(other, saved["id"]),
        lambda: media.delete(other, saved["id"]),
    ]:
        with pytest.raises(DomainError) as error:
            action()
        assert error.value.status == 404
    assert media.list(other) == []
    assert media.delete(user, saved["id"])["state"] == "deleted"
    assert media.delete(user, saved["id"])["state"] == "deleted"
    assert not list(Path(media.settings.media_root).glob("*.wav"))
    assert media.get(user, saved["id"])["sha256"] is None
    with pytest.raises(DomainError) as error:
        media.content(user, saved["id"])
    assert error.value.status == 410


def test_expiry_denies_content_and_explicit_cleanup_removes_bytes(media_world):
    media, (user, other) = media_world
    saved = media.upload(user, fixture_audio("hi-IN"), "audio/wav", consent=True)
    media.clock = lambda: NOW + timedelta(minutes=16)
    assert media.get(user, saved["id"])["state"] == "expired"
    with pytest.raises(DomainError) as error:
        media.content(user, saved["id"])
    assert error.value.status == 410
    assert len(list(Path(media.settings.media_root).glob("*.wav"))) == 1
    assert media.purge_expired() == 1
    assert media.purge_expired() == 0
    assert not list(Path(media.settings.media_root).glob("*.wav"))


@pytest.mark.parametrize(
    "audio,mime,consent",
    [
        (b"not audio", "audio/wav", True),
        (fixture_audio("en-IN")[:-1], "audio/wav", True),
        (fixture_audio("en-IN"), "audio/mpeg", True),
        (fixture_audio("en-IN"), "audio/wav", False),
        (wav_seconds(0), "audio/wav", True),
        (wav_seconds(61), "audio/wav", True),
    ],
    ids=["not-wav", "truncated", "wrong-mime", "no-consent", "empty", "over-duration"],
)
def test_invalid_audio_and_missing_consent_never_store_files(
    media_world, audio, mime, consent
):
    media, (user, other) = media_world
    with pytest.raises(DomainError):
        media.upload(user, audio, mime, consent=consent)
    assert media.list(user) == []
    assert not list(Path(media.settings.media_root).glob("*.wav"))


def test_sixty_second_boundary_quota_and_missing_file(media_world):
    media, (user, other) = media_world
    saved = media.upload(user, wav_seconds(60), "audio/wav", consent=True)
    assert saved["duration_ms"] == 60000
    for _ in range(4):
        media.upload(user, fixture_audio("ta-IN"), "audio/wav", consent=True)
    with pytest.raises(DomainError) as error:
        media.upload(user, fixture_audio("ta-IN"), "audio/wav", consent=True)
    assert error.value.status == 429
    (Path(media.settings.media_root) / (saved["id"] + ".wav")).unlink()
    with pytest.raises(DomainError) as error:
        media.content(user, saved["id"])
    assert error.value.status == 410


def test_concurrent_upload_quota_is_serialized(media_world):
    from concurrent.futures import ThreadPoolExecutor

    media, (user, other) = media_world
    media.settings.media_max_objects_per_user = 1

    def upload_one():
        try:
            media.upload(user, fixture_audio("en-IN"), "audio/wav", consent=True)
            return 201
        except DomainError as error:
            return error.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(lambda _: upload_one(), range(2))) == [201, 429]
    assert len(media.list(user)) == 1


def test_persistence_failure_rolls_back_row_and_removes_written_file(
    media_world, monkeypatch
):
    from contextlib import contextmanager

    media, (user, other) = media_world
    original = media.store.transaction

    @contextmanager
    def fail_before_commit(*args, **kwargs):
        with original(*args, **kwargs) as connection:
            yield connection
            raise RuntimeError("synthetic pre-commit failure")

    monkeypatch.setattr(media.store, "transaction", fail_before_commit)
    with pytest.raises(RuntimeError):
        media.upload(user, fixture_audio("en-IN"), "audio/wav", consent=True)
    monkeypatch.setattr(media.store, "transaction", original)
    assert media.list(user) == []
    assert not list(Path(media.settings.media_root).glob("*.wav"))


@pytest.mark.parametrize(
    "media_id", ["../.env", "a/../../secret", "not-a-uuid", "f" * 33]
)
def test_untrusted_ids_never_become_paths(media_world, media_id):
    media, (user, other) = media_world
    for action in [media.get, media.content, media.delete]:
        with pytest.raises(DomainError) as error:
            action(user, media_id)
        assert error.value.status == 404


def test_corrupted_file_fails_integrity_check(media_world):
    media, (user, other) = media_world
    saved = media.upload(user, fixture_audio("en-IN"), "audio/wav", consent=True)
    path = Path(media.settings.media_root) / (saved["id"] + ".wav")
    data = path.read_bytes()
    path.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
    with pytest.raises(DomainError) as error:
        media.content(user, saved["id"])
    assert error.value.status == 410


def test_nonzero_pcm_extension_is_rejected():
    import struct
    from saathi.media import inspect_wav

    clip = bytearray(fixture_audio("en-IN"))
    clip[16:20] = struct.pack("<I", 18)
    clip[36:36] = b"\x02\x00"
    clip[4:8] = struct.pack("<I", len(clip) - 8)
    with pytest.raises(DomainError):
        inspect_wav(bytes(clip), "audio/wav")
