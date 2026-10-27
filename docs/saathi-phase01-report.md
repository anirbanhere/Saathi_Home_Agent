# Saathi Phase0/1 implementation report

Completed mock-foundation scope:28 October2026, Asia/Kolkata. Governing requirements: [PRD.md](../PRD.md), Section14. Branch: `codex/saathi-phase01`. The existing public Home Agents website has not been replaced or redeployed.

## Outcome and evidence scope

A local web user or CLI scenario can submit text or one of three synthetic audio fixtures, clarify missing city/date, inspect mocked dental availability, review exact India date/time and no-charge conditions, approve a scoped preview, obtain one verified **MOCK** booking reference, and persist a reminder intent. Explicit mock outbox draining records a simulated delivery receipt. Restart, stale/changed consent, cross-user access, contention and ambiguous response recovery are tested.

This completes a deterministic mock vertical slice, not the PRD's real-voice/real-provider MVP release gate. Actual Hindi/Tamil/English speech recognition and synthesis quality remain unverified. Audio fixtures are generated WAV tones mapped by digest to predetermined text; mock TTS returns a tone. Sarvam/ElevenLabs adapters have injected HTTP contract tests only. No live inference, real appointment, WhatsApp message, phone call, purchase, payment, IRCTC ticket or legal clearance is claimed.

## Phase deliverables

| Requirement | Implemented evidence | Limit / remaining gate |
| --- | --- | --- |
| Phase0 policy/architecture | New PRD, current architecture, ADR0004, vendor-gate report | Terms endpoint blocked; exact latest India AI eligibility requires authoritative review. Gate defaults false |
| Bootstrap/local stack | FastAPI/Pydantic2, PostgreSQL/Redis compose, locked runtime packages, health endpoints, Alembic | Local Docker Linux daemon unavailable. Compose config validates; actual PostgreSQL/Redis ran in CI, not local containers |
| Vendor feasibility spikes | Official STT/TTS/WhatsApp/Hermes/Swiggy/Exotel/IRCTC documentation reviewed; speech request/response contracts tested | No credentials/access/approved recipients; live vendor spikes and official WhatsApp test number remain blocked. Calls are explicitly excluded by kickoff |
| Normalized input/identity | Typed messages, separate local channel/principal, HTTP-only session cookie, CSRF/origin checks, SQL conversations and deduplicated response history | Local anonymous mock identity only; no verified consumer login/linking/family membership |
| Independent provider roles | Reasoning, conversation, STT, TTS profiles; mock/mock_alt selection and task-pinned snapshots; timeout bounds | Runtime rejects live providers; vendor STT/TTS classes are contract spikes. General live-model router and vendor capability/quality acceptance remain later work |
| Planning/tool policy | Typed bounded four-step dental plan, native registry, strict schemas, external policy/approval enforcement | Fixed dental orchestrator; no arbitrary-goal execution or remote MCP/OAuth client enabled |
| Durable tasks/consent | SQL state machine, canonical preview hash, hashed one-time nonce, expiry, task version, owner checks, unique operation reference | After reload, a pending approval requires reselecting the slot to issue a new nonce/review; nonce is never stored raw |
| Commit/recovery/outbox | Atomic mock slot/operation/task/outbox transaction, same approval returns prior effect, explicit reconciliation, mock delivery drain | Real nontransactional writes need independent operation/reconciliation and cancellation provider semantics; no unattended scheduler/notifications. Bounded mock turns run in a worker thread around synchronous SQL; do not add slow live IO inside that transaction |
| Audio fixtures/locales | en-IN/hi-IN/ta-IN mock voice→booking API/CLI checks and native-script response templates | Tone lookup is not ASR. OGG/Opus/transcoding, human speech samples, Malayalam/native review and actual spoken replies are not accepted |

## Changed implementation files

- Root: `PRD.md`, `requirements-saathi*.txt`, `alembic-saathi.ini`, `.env.example`, `docker-compose.yml`, `Saathi.Dockerfile`; CI adds a synthetic PostgreSQL/Redis job without production secrets or deployment.
- `saathi/contracts.py`, `config.py`, `providers.py`, `speech.py`, `vendor_speech.py`, `channels.py`: typed contracts, independent roles, bounded fixture lookup and gated HTTP adapter spikes.
- `saathi/db/`: frozen schema-v1, Alembic migration and transactional store; SQL includes users/sessions, conversations, deduplicated message responses, task graph/profiles, approvals, slots, operations, audit and outbox. Task steps persist within typed plan JSON in this slice.
- `saathi/runtime.py`, `state.py`, `policy.py`, `registry.py`, `outbox.py`: domain state, preview/consent, single mock commit, recovery and explicit mock delivery.
- `saathi/main.py`, `http_limits.py`, `observability.py`, `cli.py`: local API/CLI, received-byte caps even for chunked requests, redacted proposed-transition logs and diagnostics. SQL audit/task state, not a pre-commit log line, proves committed state.
- `saathi_web/`: standalone local demo with explicit mock labels, review controls, scoped history, reload/review behavior and keyboard focus. Review recap displays clinic/service/city/date/time/cost/conditions rather than internal actor IDs.
- `saathi_tests/`: contract, vendor-normalization, workflow, policy/state, API/e2e, migration, outbox and real PostgreSQL/Redis checks.
- Architecture/onboarding/backlog/handoff documents identify this new reference service separately from the still-deployed legacy app.

## Reproducible setup and demo commands

From repository root, Python3.12 and Node available:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-saathi-dev.txt
.\.venv\Scripts\python.exe -m saathi.cli migrate
.\.venv\Scripts\python.exe -m uvicorn saathi.main:create_app --factory --host 127.0.0.1 --port 8781
```

Open `http://127.0.0.1:8781/`. Start a local mock session, request “Book dental cleaning in Chennai tomorrow morning”, review a returned slot, then approve **MOCK** booking. Try the Tamil/Hindi audio-fixture button after selecting language. Reload and use saved history; a pending preview needs a fresh slot selection before approval. Do not enter private/real clinical details.

`python` below means your virtual environment's Python (`.venv/bin/python` on POSIX). The application reads process environment and the example provider config; it does not load `.env` automatically. Default new database: `data/saathi-demo.sqlite3`; no legacy DB is migrated.

```text
python -m saathi.cli providers
python -m saathi.cli fixtures
python -m saathi.cli demo --approve-mock
python -m saathi.cli demo --approve-mock --voice --locale hi-IN
python -m saathi.cli demo --approve-mock --voice --locale ta-IN --simulate-timeout
```

Each demo creates a new mock principal. Availability is shared within that mock database and a committed slot stays taken. For independent repeatable happy-path runs, choose a fresh task-specific file, e.g. PowerShell `$env:SAATHI_DATABASE_URL='sqlite:///artifacts/saathi-run-hi-01.sqlite3'`, or POSIX `export SAATHI_DATABASE_URL=sqlite:///artifacts/saathi-run-hi-01.sqlite3`. Choose another new filename for another isolated run; do not delete existing state to hide failures. Generated WAV files stay in ignored `artifacts/saathi-audio`.

### PostgreSQL/Redis local option

When Docker Desktop's Linux engine is running:

```text
docker compose up -d postgres redis
```

Set `SAATHI_DATABASE_URL=postgresql+psycopg://saathi:local-demo-only@127.0.0.1:54329/saathi` and `SAATHI_REDIS_URL=redis://127.0.0.1:63799/0` in your process, then run migrate/web commands above. These published ports and credentials are intentionally loopback/local-demo only. Do not use them for a public service.

Alternatively `docker compose --profile demo up --build` provides the app container with health-gated database/cache dependencies and a port published only on127.0.0.1:8781. This container build/run was not executed locally because the daemon was unavailable. `docker compose config --quiet` was executed successfully. Do not expose the local-identity demo through a public tunnel or publish the container port globally. `docker compose down` stops services while retaining data volumes; no volume deletion is part of normal instructions.

### Operator configuration and permissions

`SAATHI_PROVIDER_CONFIG` selects the operator-owned YAML file; `config/providers.example.yaml` defines four independent roles. Change one role to `provider: mock_alt` to test switching. New tasks adopt it; resumed tasks retain saved profiles. Clients cannot select providers, grant live tools or change role profiles through chat input. `WHATSAPP_PRODUCTION_ELIGIBLE`, `SAATHI_LIVE_ACTIONS_ENABLED` and `SAATHI_LIVE_SPEECH_ENABLED` default false; true is rejected by Phase1 settings rather than becoming an execution permission.

Sarvam/ElevenLabs model/voice identifiers must be supplied explicitly when future live work is authorized. Standard CI and demos require no API key. Secrets remain outside source, snapshots, prompts and logs. The new service currently has no public account recovery, data export/deletion API or media-retention store; use synthetic local data only.

## Tests and actual execution

```text
python -m pytest saathi_tests -q
python -m unittest discover -s tests -v
node --check saathi_web/app.js
node --check web/app.js
python -m compileall -q saathi home_agent
```

Local latest:52 new checks passed, one real-PostgreSQL check skipped because the local daemon is unavailable; legacy97 tests passed. CI runs the PostgreSQL test with actual PostgreSQL16 and Redis7. The initial implementation CI run reported51 new tests passed (before the final chunked-body case) and97 legacy tests passed: [CI40562813755](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40562813755). The final runtime source `c8e061d` passed52 new tests (including actual PostgreSQL/Redis) and97 legacy tests: [CI40563359294](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40563359294). [Container CI40564413284](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40564413284) passed on `1f26ba7`:52 new +97 legacy tests, non-root image build and loopback readiness smoke (SQLite container; separate PostgreSQL/Redis integration). An initial immediate health probe had hit connection reset before readiness; bounded all-error startup retries and failure-log capture fixed that CI race. The subsequent concurrency fix `cf9bff1` passed53 new +97 legacy tests and the same container checks: [CI40565249140](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40565249140). Latest documentation/test-format head status is recorded through Git/PR checks.

Meaningful cases cover: four independent role swaps through complete mock bookings; three locales via audio/API/CLI; strict input/locale/provider rejection; missing detail clarification; duplicate external IDs with payload mismatch; cross-user task/conversation/approval boundaries; changed/expired/reused approvals and hash tampering; slot conflict/concurrent calls; post-commit cancellation denial; timeout/reconciliation without reexecute; migration upgrade/restart/downgrade; outbox due/owner/duplicate constraints; CSRF/origin, nonce non-persistence and chunked-body limits. A delayed-model simultaneous-HTTP regression first reproduced event-loop/SQL blocking, then passed after isolating each bounded mock turn in a worker thread.

Actual CLI runs used three separate fresh synthetic databases and completed en-IN/hi-IN/ta-IN booking/delivery-sink scenarios; Tamil included response-loss reconciliation. Real Chromium mobile check used actual390px viewport, reviewed an exact slot/cost, completed a mock booking, showed saved history after reload and displayed Tamil fixture text. Pending approval was reopened after reload without an available approval nonce; reselecting the slot issued a fresh preview and completed the mock booking. Mobile client/document widths matched390; desktop `innerWidth`1440 had client/scroll1425/1425. No console warning/error was observed during those checks. Further browser evidence is in HANDOFF.md. This is not a full accessibility/native-language audit.

Pinned new runtime dependency audit:27 packages, zero known advisories at the recorded check; no dependency-audit claim is made for unpinned future resolutions. Browser fixtures/source/deterministic tests are not live speech/model evidence.

## Proposed Phase2 PR breakdown — not executed here

1. **Identity/media boundary:** choose verified user auth/linking, consent, private scoped uploads, codec/duration limits/transcoding, retention/deletion/export and account-recovery policy. Test two real principals and revocation before public data collection.
2. **Genuine speech acceptance:** enable an explicitly approved Sarvam/ElevenLabs route with permissioned Hindi/Tamil/English utterances; measure critical fields, latency and same-language spoken replies, including provider swaps. Preserve a clear text fallback; evaluate Malayalam separately.
3. **Owned/approved booking provider:** agree a supported real partner; implement prepare/revalidate/commit/status/cancel against its documented semantics, durable operations/outbox leases and reconciliation. Test lost responses/provider contention before any fulfillment claim.
4. **Permitted channel preflight:** independently resolve current Meta offering eligibility and allowed test scope, then signed official webhook/media and strong linking. Keep production gate false until authoritative clearance; no unofficial bridge workaround.
5. **Scheduler/delivery:** durable leased reminders, opt-out/cancellation/quiet hours and delivery receipts; approved templates when required. A saved reminder intent is not a delivered notification.
6. **Production placement/release:** rehearse PostgreSQL backup/restore/migration, cost/credit checks, public auth/security/rate budgets/observability and rollout/rollback. Preserve or explicitly retire the old website through a reviewed migration; do not silently point it at this local mock app.

Calls, Swiggy ordering, payments, family sharing and IRCTC execution remain later PRD phases with their own access/consent gates. This report authorizes none of them.
