# Saathi development handoff

Updated:28 October2026, Asia/Kolkata. Branch: `codex/saathi-phase01`. Runtime source: `cf9bff1` (concurrent HTTP fix); CI/container source included. Later context/report and test-format changes do not change application behavior.

## Human objective and current scope

The human replaced the prior plan with `Saathi_PRD_Codex.md` and explicitly requested Section14 Phase0/1 kickoff. Root [PRD.md](PRD.md) is the new product requirement; [execution plan](tasks/saathi-phase01.md) and [implementation report/demo commands/Phase2 proposal](docs/saathi-phase01-report.md) track this work. Preserve the existing public Home Agents app; no production migration or new public deployment was performed.

Review artifact: [PR1 — Saathi Phase0/1 mock booking foundation](https://github.com/anirbanhere/Saathi_Home_Agent/pull/1), targeting `main` from `codex/saathi-phase01`. It is published for review, not merged/deployed. Inspect the PR's current-head checks; the implementation CI evidence below refers to the explicitly named tested source. The final local preview remains running on127.0.0.1:8781 with synthetic state.

The coordinator session owns this additive implementation. The other four developer slots remain unassigned; old proposed lanes must be re-planned against the new PRD. Contributors still use separate branches/checkouts, confirmed scope and task-specific handoffs. This coordinator maintains root status.

## Implemented Phase0/1 foundation

- Separate `saathi/` FastAPI/Pydantic2/SQLAlchemy service, PostgreSQL/Alembic target, Redis readiness, local SQLite mock option; compose and a non-root app container with loopback-only published port. Legacy `home_agent/` is unchanged.
- Independent typed reasoning/conversation/STT/TTS roles, normalized local web/CLI channels, task-pinned provider profiles, deterministic mock/mock_alt router. Sarvam/ElevenLabs STT/TTS have disabled-live HTTP contract spikes with fixed endpoints and explicit model/voice IDs. Runtime rejects live profiles/flags.
- SQL users/sessions, conversations/deduplicated message responses, typed task plan/state, canonical preview hashes, scoped one-time approval with hashed nonce/expiry/version, atomic mock slot/operation/outbox, audit and explicit mock delivery drain.
- Human web controls own review/approve/edit/reject/cancel; no model approval. Duplicate approval returns the same effect, unknown response enters RECONCILIATION_REQUIRED and reconciles saved operation rather than reexecuting. Post-commit cancellation is not falsely claimed.
- Local UI and CLI exercise text or three generated acoustic-token WAV fixtures → mock dental options → exact review → approval → verified MOCK booking reference → durable reminder intent/mock delivery sink. Fixtures are not spoken recordings or actual ASR/TTS quality evidence.
- Session ownership, CSRF/origin checks, strict bounded schemas, received-byte limits including chunked bodies and secret-free event logging. Logs label proposed transitions; SQL state/audit after commit proves completion.
- New architecture/ADR0004/vendor-gate discovery/report; agent/onboarding/root status entry points point to the new PRD and preserve legacy evidence.

## Verification and CI

- Local new-service suite:52 passed, one real PostgreSQL/Redis test skipped because the local Docker Linux daemon is unavailable. The Docker CLI exists; compose configuration validates. No local-container execution is claimed.
- Legacy97 tests passed after new dependencies were installed; no test/security boundary weakened. New and legacy JS syntax checks and Python compilation passed. New runtime dependency audit:27 resolved/pinned packages, zero known advisories at the recorded check.
- [Final runtime test CI40563359294](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40563359294), source `c8e061d902c9cdaa3b3bd86d157a0c62a2d18e7f`:52 new tests passed, including actual PostgreSQL16/Redis7 migration/concurrent contention/restart;97 legacy tests passed.
- Initial container CI40564024264 built the image successfully and passed52+97 tests, but the immediate curl health probe hit connection reset before readiness; it did not retry that error. CI-only fix `1f26ba7` adds bounded all-error startup retries and failed-container log capture. [Repaired container CI40564413284](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40564413284) passed for `1f26ba76bed331e85b8b34116830d204abc68197`:52 new +97 legacy tests, image build and loopback readiness smoke all passed. The smoke uses local SQLite in the container; real PostgreSQL/Redis evidence comes from the separate integration test.
- Actual CLI smoke: separate fresh synthetic DB per en-IN/hi-IN/ta-IN audio-fixture scenario; all completed with mock booking/delivery references; Tamil exercised simulated response loss and reconciliation.
- Actual local Chromium: text request, exact review/approve, persisted completed task after reload, Tamil fixture/native-script reply, pending-preview reload without a recoverable raw nonce, fresh slot reselect/new review and mock completion. Actual390px client/scroll390/390, desktop1440px client/scroll1425/1425; no console warnings/errors observed. No real clinic, external message or provider account used.

- Final review reproduced simultaneous HTTP requests blocking the model event loop while synchronous SQL held a lock. Added a delayed-model concurrent-duplicate regression; it failed before the fix, then passed in about1s. Each bounded mock turn now runs in a separate worker thread/event loop; SQL remains authoritative. Do not extend this mock transaction to slow real-provider IO without the Phase2 durable execution design. [Final implementation CI40565249140](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40565249140) passed for `cf9bff155c0e55ee35f2e8ac3cceb3631a0c6606`:53 new +97 legacy tests, real PostgreSQL/Redis integration, container build and health smoke. Local preview was restarted on final source at127.0.0.1:8781 using ignored synthetic `artifacts/saathi-web-review.sqlite3`; readiness returned mock/SQLite.

## Current limits and launch gates

This is a completed deterministic mock foundation, not the PRD's live-provider MVP. Real Hindi/Tamil/English speech recognition/synthesis, arbitrary-goal/model reasoning, real booking/calendar providers, remote MCP/OAuth, durable background scheduler/delivery, verified household/consumer accounts, public media/retention/export/deletion and production operational limits remain unverified/unimplemented for this new service. The report lists acceptance gaps per phase deliverable; do not turn mock test counts into language-quality or fulfillment claims.

WHATSAPP_PRODUCTION_ELIGIBLE=false; live speech/actions also default false and are rejected if enabled in this release. Current terms URL redirected to blocked login during discovery; PRD country-exception details were not independently re-confirmed. Authoritative offering-specific review and test-account access remain gates. No unofficial bridge, new WhatsApp account, message, real call, purchase/payment or IRCTC action was attempted. Nous setup stays skipped.

No secret payload is published or logged. Ordinary new tests use injected transports and fresh synthetic state. Pending approval after reload must issue a fresh nonce/review; raw nonce is never persisted. Local identity/cookies are not verified family identity. PostgreSQL is the target; SQLite success is not PostgreSQL concurrency evidence. Redis is currently a readiness dependency, not the task ledger or implemented scheduler.

## Demo and continuation

Read [the implementation report](docs/saathi-phase01-report.md) for full setup, migration, mock audio/text demo commands and proposed Phase2 PRs. Quick local web: install `requirements-saathi-dev.txt`, then `python -m uvicorn saathi.main:create_app --factory --host 127.0.0.1 --port 8781`. CLI: `python -m saathi.cli demo --approve-mock --voice --locale hi-IN`. Use a fresh task-specific database filename for isolated happy paths; do not wipe prior state. No API keys are required for this mock service.

Before starting more work, fetch the feature branch/PR, inspect its actual head/CI and avoid recreating Phase0/1. Phase2 work is proposed only; obtain a concrete assignment. First gates are verified identity/media and real permissioned speech acceptance; real appointment/channel/scheduler integrations follow their own eligibility/access/reconciliation design. Do not silently overwrite/deploy the legacy app.

## Preserved public legacy release

URL: `https://home-agents-xswei7prnq-uc.a.run.app`. Website `home-agents-00010-w5z`, build `db1242d9-a0cd-42de-8102-a6c22607bb73`, source `08d0bbe`. Rollback `home-agents-00009-xhz`, build `3c7a6caf-5c61-4ee5-ae81-421b412816d6`. Private browser remains `home-agents-browser-00001-w2m`; production secret references/config/IAM were not changed by this phase. Last real legacy OpenRouter attempt returned429; no new inference retries or paid fallback were introduced. See [prior handoff](docs/history/2026-10-27-pre-saathi-handoff.md) and [operations runbook](docs/operations-runbook.md).
