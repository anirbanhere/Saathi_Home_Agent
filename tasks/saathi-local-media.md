# Local private audio boundary

28 October2026. Human said “continue” after Phase0/1. Selected scope: the local-media part of the proposed next-phase foundation; no verified consumer identity, live speech or public deployment. Coordinator owns `saathi/media.py`, additive schema/migration, narrow HTTP/config/CLI/UI integration, tests and matching docs. Other developer lanes remain unassigned.

## API and lifecycle contract

- `POST /api/media`: raw `audio/wav`, same-origin session/CSRF and explicit `X-Saathi-Media-Consent: local-review`. Only this route gets a2MB received-byte ceiling; other JSON requests retain60KB. No user ID, filename, object path, provider/model or URL from the request.
- Accept valid complete PCM WAV, mono16kHz/16-bit, at most60s. Reject MIME mismatch, truncated frames/RIFF, unsupported format, empty clips, over-duration/size and quota excess before publishing metadata. WAV-only is deliberate; no claimed OGG/Opus transcoding.
- Metadata/list/content/delete are scoped to the server-held local principal. `GET /api/media`, `GET /api/media/{id}`, `GET /api/media/{id}/content`, `DELETE /api/media/{id}`. IDs alone grant no access. Never return filesystem paths.
- Store opaque random files outside SQL under ignored `data/` by default. Store ownership/hash/size/duration/consent/expiry in SQL. Default15-minute access expiry; five stored objects and50 lifetime records/user. Local filesystem permissions are not production encryption/identity.
- Expired/deleted content returns410 to its owner; foreign/unknown IDs return404. Delete removes bytes and clears sensitive metadata, keeping minimal scoped tombstone for repeat-safe deletion. Explicit operator cleanup removes expired bytes; no background scheduler/automatic physical-retention claim.
- No uploaded recording is sent to a model or speech vendor, added to chat/task context or included in Git/container build context. Playback is owner-authenticated. Existing synthetic fixture booking continues unchanged.

## Threats and tests

Cover cross-user read/delete, consent/CSRF/origin/MIME, malicious IDs/path traversal, exact byte/duration bounds and chunked uploads, malformed/truncated WAV, quota/concurrent upload, restart, expiry, delete/repeat, failed persistence cleanup and missing/corrupt files. Add an upgrade-from-v1 preservation check plus real PostgreSQL metadata coverage in CI. Verify actual local upload/playback/delete UI at390px and desktop with generated permission-free WAV data.

Use the existing security/API/incremental/TDD workflows. Do not merge PR1 or alter the public legacy service; publish a separate stacked PR with merge order and an honest account/speech boundary.
