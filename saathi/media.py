"""Private local WAV review storage. No speech/model calls or public object URLs."""

import hashlib
import io
import os
import re
import struct
import wave
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from sqlalchemy import select, update, func
from .db import schema
from .db.schema_v2 import media
from .runtime import DomainError

MAX_BYTES = 2_000_000


def inspect_wav(audio, mime):
    if mime != "audio/wav" or not 44 <= len(audio) <= MAX_BYTES:
        raise DomainError("Provide a PCM WAV file up to2MB.", "INVALID_MEDIA", 422)
    if (
        audio[:4] != b"RIFF"
        or audio[8:12] != b"WAVE"
        or struct.unpack("<I", audio[4:8])[0] != len(audio) - 8
    ):
        raise DomainError(
            "WAV container is incomplete or unsupported.", "INVALID_MEDIA", 422
        )
    offset, chunks, count = 12, {}, 0
    while offset < len(audio):
        count += 1
        if count > 128:
            raise DomainError("WAV metadata is too complex.", "INVALID_MEDIA", 422)
        if offset + 8 > len(audio):
            raise DomainError("Truncated WAV chunk.", "INVALID_MEDIA", 422)
        name, length = (
            audio[offset : offset + 4],
            struct.unpack("<I", audio[offset + 4 : offset + 8])[0],
        )
        start, end = offset + 8, offset + 8 + length
        if (
            end + (length % 2) > len(audio)
            or name in chunks
            and name in {b"fmt ", b"data"}
        ):
            raise DomainError("Invalid WAV chunk layout.", "INVALID_MEDIA", 422)
        chunks[name] = (start, length)
        offset = end + length % 2
    if b"fmt " not in chunks or b"data" not in chunks or chunks[b"data"][1] % 2:
        raise DomainError("WAV PCM frame layout is invalid.", "INVALID_MEDIA", 422)
    start, length = chunks[b"fmt "]
    if length not in {16, 18} or struct.unpack(
        "<HHIIHH", audio[start : start + 16]
    ) != (1, 1, 16000, 32000, 2, 16):
        raise DomainError(
            "Only uncompressed PCM WAV is supported.", "INVALID_MEDIA", 422
        )
    if length == 18 and audio[start + 16 : start + 18] != b"\0\0":
        raise DomainError(
            "PCM WAV must not declare extension bytes.", "INVALID_MEDIA", 422
        )
    try:
        with wave.open(io.BytesIO(audio)) as clip:
            frames = clip.getnframes()
            if (
                clip.getnchannels() != 1
                or clip.getsampwidth() != 2
                or clip.getframerate() != 16000
                or not 1 <= frames <= 960000
            ):
                raise ValueError()
            if len(clip.readframes(frames)) != frames * 2:
                raise ValueError()
    except (wave.Error, EOFError, ValueError):
        raise DomainError(
            "Use complete mono16kHz,16-bit PCM WAV audio, at most60 seconds.",
            "INVALID_MEDIA",
            422,
        ) from None
    return round(frames * 1000 / 16000)


class MediaStore:
    def __init__(self, store, settings, clock=None):
        self.store, self.settings = store, settings
        self.root = Path(settings.media_root).resolve()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _path(self, media_id):
        if not isinstance(media_id, str) or not re.fullmatch(r"[a-f0-9]{32}", media_id):
            raise DomainError("Audio not found.", "NOT_FOUND", 404)
        path = self.root / (media_id + ".wav")
        if path.is_symlink() or path.resolve().parent != self.root:
            raise DomainError("Stored audio is unavailable.", "MEDIA_UNAVAILABLE", 410)
        return path

    def _row(self, c, user, media_id):
        if not isinstance(media_id, str) or not re.fullmatch(r"[a-f0-9]{32}", media_id):
            raise DomainError("Audio not found.", "NOT_FOUND", 404)
        row = (
            c.execute(
                select(media)
                .where(media.c.id == media_id, media.c.user_id == user)
                .with_for_update()
            )
            .mappings()
            .first()
        )
        if not row:
            raise DomainError("Audio not found.", "NOT_FOUND", 404)
        return dict(row)

    def _public(self, row):
        result = {
            key: row[key]
            for key in [
                "id",
                "state",
                "sha256",
                "bytes",
                "duration_ms",
                "created_at",
                "expires_at",
            ]
        }
        if (
            result["state"] == "active"
            and datetime.fromisoformat(result["expires_at"]) <= self.clock()
        ):
            result["state"] = "expired"
        result["purpose"] = "local_review_only"
        result["transcribed"] = False
        return result

    def upload(self, user, audio, mime, *, consent):
        if consent is not True:
            raise DomainError(
                "Confirm permission for local audio review before uploading.",
                "MEDIA_CONSENT_REQUIRED",
                403,
            )
        duration = inspect_wav(audio, mime)
        media_id, created = uuid4().hex, False
        path = self._path(media_id)
        try:
            with self.store.transaction(user) as c:
                if not c.scalar(
                    select(schema.users.c.id).where(schema.users.c.id == user)
                ):
                    raise DomainError("Unknown local principal.", "UNAUTHORIZED", 401)
                total = c.scalar(
                    select(func.count())
                    .select_from(media)
                    .where(media.c.user_id == user)
                )
                active = c.scalar(
                    select(func.count())
                    .select_from(media)
                    .where(media.c.user_id == user, media.c.state == "active")
                )
                if total >= 50 or active >= self.settings.media_max_objects_per_user:
                    raise DomainError(
                        "Local audio quota reached. Delete stored audio or use another test workspace after its lifetime budget.",
                        "MEDIA_QUOTA",
                        429,
                    )
                self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
                with path.open("xb") as output:
                    created = True
                    os.chmod(path, 0o600)
                    output.write(audio)
                    output.flush()
                    os.fsync(output.fileno())
                now = self.clock().astimezone(timezone.utc)
                row = dict(
                    id=media_id,
                    user_id=user,
                    state="active",
                    sha256=hashlib.sha256(audio).hexdigest(),
                    bytes=len(audio),
                    duration_ms=duration,
                    created_at=now.isoformat(),
                    expires_at=(
                        now + timedelta(seconds=self.settings.media_ttl_seconds)
                    ).isoformat(),
                    consent="local_review",
                )
                c.execute(media.insert().values(**row))
            return self._public(row)
        except BaseException as error:
            if created:
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass  # Access checks still fail closed if cleanup needs operator repair.
            if isinstance(error, OSError):
                raise DomainError(
                    "Local audio storage is unavailable.",
                    "MEDIA_STORAGE_UNAVAILABLE",
                    503,
                ) from None
            raise

    def list(self, user):
        with self.store.transaction(user) as c:
            rows = (
                c.execute(
                    select(media)
                    .where(media.c.user_id == user, media.c.state != "deleted")
                    .order_by(media.c.created_at.desc())
                    .limit(50)
                )
                .mappings()
                .all()
            )
            return [self._public(row) for row in rows]

    def get(self, user, media_id):
        with self.store.transaction(user) as c:
            return self._public(self._row(c, user, media_id))

    def content(self, user, media_id):
        with self.store.transaction(user) as c:
            row = self._row(c, user, media_id)
            if self._public(row)["state"] != "active":
                raise DomainError(
                    "Audio has expired or been deleted.", "MEDIA_GONE", 410
                )
            try:
                path = self._path(media_id)
                if path.stat().st_size != row["bytes"]:
                    raise ValueError()
                with path.open("rb") as source:
                    audio = source.read(MAX_BYTES + 1)
                if (
                    len(audio) != row["bytes"]
                    or hashlib.sha256(audio).hexdigest() != row["sha256"]
                ):
                    raise ValueError()
            except (OSError, ValueError):
                raise DomainError(
                    "Stored audio is missing or damaged; delete it and upload a new copy.",
                    "MEDIA_UNAVAILABLE",
                    410,
                ) from None
            return audio

    def _remove(self, c, row, state):
        try:
            self._path(row["id"]).unlink(missing_ok=True)
        except OSError:
            raise DomainError(
                "Audio could not be removed; try again.",
                "MEDIA_STORAGE_UNAVAILABLE",
                503,
            ) from None
        c.execute(
            update(media)
            .where(media.c.id == row["id"])
            .values(
                state=state,
                sha256=None,
                bytes=None,
                duration_ms=None,
                consent="revoked",
            )
        )
        row.update(
            state=state, sha256=None, bytes=None, duration_ms=None, consent="revoked"
        )
        return self._public(row)

    def delete(self, user, media_id):
        with self.store.transaction(user) as c:
            row = self._row(c, user, media_id)
            return self._remove(c, row, "deleted")

    def purge_expired(self, limit=50):
        if not 1 <= limit <= 50:
            raise ValueError("Cleanup batch must be1..50.")
        with self.store.transaction() as c:
            rows = (
                c.execute(
                    select(media)
                    .where(
                        media.c.state == "active",
                        media.c.expires_at
                        <= self.clock().astimezone(timezone.utc).isoformat(),
                    )
                    .order_by(media.c.expires_at)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
                .mappings()
                .all()
            )
            for row in rows:
                self._remove(c, dict(row), "expired")
            return len(rows)
