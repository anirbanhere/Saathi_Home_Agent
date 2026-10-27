# Saathi PRD v1: Phase 0 and Phase 1 execution

User-authorized27 October2026: adopt root PRD.md, execute Section14 kickoff. This supersedes the prior next-ticket selection and proposed team lanes for this scoped work; no other lane is assigned. Coordinator session owns additive `saathi/`, `saathi_web/`, `saathi_tests/`, configuration/migrations and the matching root documentation. Existing Home Agents source/deployment remains a compatibility baseline.

## Scope and assumptions

- Product reference becomes Saathi; first locales en-IN/hi-IN/ta-IN. Malayalam is next-phase evaluation; Kannada remains a deferred earlier request, not silently claimed tested.
- FastAPI/Pydantic2, SQLAlchemy/Alembic/PostgreSQL and Redis compose; no new cloud resources. Docker CLI exists but Linux daemon is unavailable on this machine. Supply a real PostgreSQL CI integration path and SQLite local/mock mode; do not claim SQLite proves PostgreSQL concurrency.
- All consequential providers remain deterministic mocks or disabled. Fresh local browser identity; no WhatsApp pairing, telephony, purchases, real clinic, IRCTC, production-data migration or public deployment.
- Speech adapters get deterministic transport tests; synthetic audio fixtures explicitly do not demonstrate native-language ASR quality. Missing vendor credentials are an evidence gap, not a reason to fake live recognition.
- WhatsApp production eligibility defaults false. Current terms endpoint redirected to blocked login; document that verification limit rather than asserting PRD policy details as independently verified legal clearance.

## Ordered increments

1. Adopt PRD, architecture/ADR/vendor gates, deployment/config/dependency foundation.
2. Typed channel/model/STT/TTS contracts, independent router settings, deterministic mock fixtures and disabled vendor adapters; contract/forbidden-combination tests.
3. Versioned relational schema, identity/conversations, task graph/state, approval preview hashes/expiry, atomic mock commit/idempotency/outbox, restart/reconciliation tests.
4. Authenticated local web/CLI scenario and health endpoints, migrations/demo commands, real browser verification, PostgreSQL/Redis CI and implementation report/Phase2 PR breakdown.

## Acceptance and verification

- Voice-fixture/text request → clarification/resolved India date → sourced mock slots → exact preview → human approval → one MOCK booking reference → verified result and durable reminder intent. No reminder transport or real appointment claim.
- Swap each of reasoning/conversation/STT/TTS without changing task business logic; pin profiles per task; resume uses saved profile; unknown provider/language fails explicitly.
- Cross-owner IDs, duplicate inbound, changed/expired/reused approval, stale slot, concurrent commit, ambiguous timeout, cancellation and restart retain invariants. No blind replay of ambiguous writes.
- Legacy97 tests and JS check remain green. New unit/contract/API/e2e/migration tests use no production keys. Database/outbox are authoritative; Redis is a wake-up/health dependency, never the operation ledger.
- User receives changed-file/test/demo/gap report; vendor/account/legal/hardware limitations stay visible. Phase2 remains proposed.
