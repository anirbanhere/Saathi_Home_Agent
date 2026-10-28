# Private local audio review

Implemented28 October2026 after the human asked to continue development. This is a bounded continuation of [Phase0/1](saathi-phase01-report.md): audio storage, playback and deletion under the existing local session. It does not complete the PRD's verified identity, real speech or public media requirements. [Implementation contract](../tasks/saathi-local-media.md).

## Behavior and boundaries

A local user can choose a WAV, explicitly confirm permission, upload it, play it back, reload the page and delete it. Uploaded audio is never added to a task, transcribed, synthesized, sent to an AI/speech provider or exposed at a public URL. The earlier synthetic audio-fixture booking flow is separate and still mocked. Do not label an uploaded tone as an ASR result.

The API remains loopback-only. The existing anonymous local session cookie determines ownership; it is not verified personal/household identity. Possession of a media ID alone does not grant access. Write requests require matching Origin, CSRF and content type; upload also requires an explicit consent header. No client filename, filesystem path, user ID or provider URL is accepted.

| Constraint | Implemented value |
| --- | --- |
| Container | Complete RIFF/WAVE with bounded chunk traversal and exact container length |
| Encoding | Uncompressed PCM, mono16kHz,16-bit; no OGG/Opus/transcoding |
| Duration | More than zero, at most60 seconds |
| Received bytes | At most2,000,000 on exact `POST /api/media`; other requests retain60,000 |
| Per-user storage quota | Five stored active records by default, including unpurged expired files |
| Lifetime record budget | Fifty per user, including deletion tombstones; deletion does not reset it |
| Access expiry | Fifteen minutes by default; configurable60–3600 seconds |
| Physical deletion | Explicit Delete or operator cleanup command; no background scheduler |

Metadata is stored in additive `saathi_media` SQL table, migration0002. Frozen v1 metadata/migration remain unchanged. File contents live under a configured local directory, named with random opaque32-character IDs. Filenames and paths are not returned. SHA256, size and duration support bounded integrity checks. Files are opened exclusively and flushed/fsynced; Unix modes are requested. Windows ACLs, encryption at rest and backup controls require operator configuration; `chmod` is not an ACL guarantee.

## HTTP contract

All routes require a valid local session. Responses retain `Cache-Control: no-store` and security headers. Errors use the existing `error.code`/`error.message` envelope and avoid private paths or raw parser errors.

| Route | Input / result |
| --- | --- |
| `POST /api/media` | Raw `audio/wav`; `X-Saathi-CSRF` and `X-Saathi-Media-Consent: local-review`;201 metadata |
| `GET /api/media` | At most50 owned, non-deleted metadata records |
| `GET /api/media/{id}` | Owned metadata, including effective expired state or minimal deletion tombstone |
| `GET /api/media/{id}/content` | Owned, active, unexpired and integrity-checked WAV bytes |
| `DELETE /api/media/{id}` | Same-origin JSON/CSRF request; removes bytes and clears hash/size/duration/consent; repeated deletion succeeds |

Unknown IDs and IDs belonging to another session return404 for read/delete. An owner's expired/deleted content returns410; corrupt or missing content also fails closed with410. Malformed audio returns422; missing consent/origin/CSRF/type returns403; quotas429; unavailable file storage503; excessive received bytes413 even for chunked requests. No Range/streaming or resumable-upload contract is implemented; the bounded clip is returned as a complete response.

## Expiry, deletion and recovery

Expiry checks use server UTC time on every new content request. A stale UI card may still display controls until refreshed, but a new server read after expiry is denied. Previously downloaded browser buffers cannot be revoked. `no-store` is a cache directive, not a guarantee that a recipient cannot retain a copy.

Expiry alone does **not** delete bytes. Run the explicit cleanup command against the same database and media root; it removes up to50 expired records' files per invocation, clears their sensitive metadata and marks them expired. Repeat until the reported count is zero. There is no scheduled cleanup or automatic guaranteed physical retention window. Minimal scoped tombstones retain IDs/ownership/timestamps/state; full account deletion/export and backup erasure are not implemented.

SQL transactions serialize per-user quotas and owned operations. PostgreSQL row locking protects content/delete and cleanup; SQLite uses its existing immediate transactions. Filesystem and SQL are not one atomic storage system: a failed upload attempts to remove its file, but a crash can leave an orphan; deletion/cleanup can unlink a file before SQL commit fails. Missing bytes are never presented as valid audio. Retry deletion to repair an owned missing-file record. Orphan discovery, crash repair, multi-host object storage and backup reconciliation need a later design. Downgrading0002 drops media metadata only; it does not erase files. Do not use migration downgrade as a retention tool.

## Local demo

From the repository root, use the existing isolated environment and install `requirements-saathi-dev.txt` if needed. `.env` is not loaded automatically. No provider key is required.

```powershell
$env:SAATHI_DATABASE_URL='sqlite:///data/saathi-media-demo.sqlite3'
$env:SAATHI_MEDIA_ROOT='data/saathi-media-demo'
$env:SAATHI_MEDIA_TTL_SECONDS='900'
python -m saathi.cli fixtures
python -m uvicorn saathi.main:create_app --factory --host 127.0.0.1 --port 8781
```

Open `http://127.0.0.1:8781`, start a local mock session, select `artifacts/saathi-audio/en-IN.wav`, confirm local-review permission and upload. This generated0.25s tone demonstrates transport/playback only. Play, reload, then Delete. A new browser session cannot access the first session's files. Existing recordings are not needed for this rehearsal.

In another shell with the **same** database/root variables:

```powershell
python -m saathi.cli media-cleanup
```

Default persistent paths are ignored `data/`; tests/review use isolated ignored `artifacts/` paths. Git and container context exclude private data, test artifacts and Playwright browser state. Do not point the cleanup command at a different database/root pair. The Saathi container's existing writable `data/` directory supports this local reference; public/multi-instance media hosting is not implemented.

## Verification

- Local:74 Saathi tests passed, one real PostgreSQL/Redis integration test skipped because the local Linux Docker daemon is unavailable. Legacy97 tests passed. New/legacy JavaScript syntax and Python compilation pass. No dependency added.
- Regressions cover ownership/404 isolation, consent/CSRF/origin/type, chunked request ceiling, malformed/empty/truncated/extended PCM, exact60s duration, quota contention, restart, expiry versus physical cleanup, duplicate deletion, pre-commit failure cleanup, invalid path IDs and missing/corrupt files. Migration upgrade preserves an existing mock booking/approval/outbox. CI extends the real PostgreSQL integration with actual media metadata/read/delete.
- Actual isolated Chromium: generated tone chosen through native file input, consent, upload201, playback `readyState=4`, duration0.25s, ended=true, error=null; metadata/control restored after reload. Delete removed the audio control and the stored file. A focus regression found during this rehearsal was fixed and rechecked: deletion returns keyboard focus to Refresh audio after controls are re-enabled. Mobile390px viewport client/scroll375/375, desktop1440px client/scroll1425/1425; DevTools mobile emulation390/390. Screenshots remain ignored under `artifacts/output/playwright/`.
- Browser console showed only the existing missing `/favicon.ico`404; no application JavaScript failures. The DevTools connector could not read workspace file paths; the upload flow was verified with a separate isolated Playwright CLI browser instead.
- CI and final-head evidence are recorded in [HANDOFF.md](../HANDOFF.md). Nothing is merged/deployed by these checks.
- [Implementation CI40638228924](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40638228924) passed for runtime `13dfcb6`:75 Saathi tests including actual PostgreSQL16/Redis7,97 legacy tests, image build and loopback readiness. [PR2](https://github.com/anirbanhere/Saathi_Home_Agent/pull/2) is based on PR1; merge/review that foundation first.

Format handling uses Python's standard [wave module](https://docs.python.org/3.12/library/wave.html); complete-container, byte, format and duration validation are application checks, not assumptions from the filename/MIME.

## Next development slice

Before real speech: agree a narrow permissioned STT evaluation (provider/model/license/hardware, synthetic or expressly permissioned samples, English/Hindi/Tamil critical-field accuracy, latency and cost), inject its transport into contract tests, and keep it out of this upload route until data-use consent and a durable execution boundary are designed. Verified identity, automatic retention/crash recovery, real booking/calendar, channel eligibility, voice reply acceptance and public operations each remain separate gates. Phase2 is not complete because this media slice exists.
