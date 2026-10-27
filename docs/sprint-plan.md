# Sprint plan

**Superseded ordering:** the user adopted the replacement Saathi PRD and requested its Section14 Phase0/1. Use [the implementation report](saathi-phase01-report.md) and latest HANDOFF.md for current work. This older calendar/ticket selection is historical wherever it conflicts; Phase2 work needs an explicit scoped assignment.

Status: proposed schedule, not a commitment or completed checklist. Baseline: 26 October 2026. Capacity assumption: one engineer, roughly 4–6 focused engineering hours/day plus AI assistance; outside account/language review is not guaranteed. Re-estimate after the first completed tickets. Use acceptance evidence, not elapsed time, to mark work done.

## Immediate demo cadence

The user supplied October 26–November 4 as the demo window. Dates below use Asia/Kolkata and are planning anchors; verify official event timezone/rules independently. The current prototype already exists, so rebuilding infrastructure is out of scope.

| Sprint | Dates | Goal | Must-have selection | Stretch only | Review evidence |
| --- | --- | --- | --- | --- | --- |
| D0: baseline and engine | Oct 26–28 | Reproducible system and one actual model/tool attempt with useful failure handling | `DOC-01`, `MODEL-01`, `QA-01`; start `MODEL-02` if capacity permits | Isolated Hermes environment preflight | Clone/run instructions, test baseline, real provider result or dated capacity blocker, current demo script |
| D1: one voice path | Oct 29–Nov 1 | Web audio→critical-field review→existing safe tool→response | `VOICE-01`; bounded slice of `VOICE-02`; `QA-02` | `VOICE-03`, `WA-01`, `HERMES-01` | Actual permitted audio sample, ownership/size/deletion tests, transcript and task evidence; otherwise retain text-only demo |
| D2: hardening and presentation | Nov 2–4 | Rehearsed truthful public demo with recoverable failures | `DEMO-01`, `OPS-01`; finish highest-priority defects from D0/D1 | Approved WhatsApp test only if its foundations/preflight already pass | Deployed known revision, rehearsal/recording, source/receipt labels, rollback notes, independently checked submission requirements |

Tickets are candidates, not all committed scope. `VOICE-02` must be decomposed if selected before full identity/media foundations: synthetic-only local/staging evaluation can proceed, but public audio collection cannot skip ownership/retention gates. D1 should not expand into a complete shared-household schema, all language benchmarks and channel integration at once.

### Daily operating rhythm

- Start: check HANDOFF.md, current branch/status, provider/channel blockers and one selected ticket's prerequisites.
- Choose one user-visible acceptance path; reserve about 25% of capacity for verification, integration failures and documentation.
- Midday: capture the smallest verified result. If an external provider is blocked, mark the ticket blocked with evidence and choose an independent ready ticket; do not poll indefinitely or change paid/guardrail policies.
- End: commit a tested slice, update backlog/HANDOFF, record the next exact action. Avoid new risky deployment work immediately before recording.

### Demo scope cuts

If free inference is still unavailable by end of D0, keep the capacity issue visible and rehearse direct tools/inspection; do not claim agentic inference acceptance. If speech licensing/hardware/quality is not feasible by mid-D1, finish evaluation contracts and show the working text journey instead of a fake audio loop. WhatsApp and clinic appointments stay off the demo's claimed capability list unless actual acceptance passes. If Meta access/event eligibility is not established, state that gap rather than imply compliance.

## Subsequent two-week sprints

These sprints are dependency-ordered planning buckets. No fixed calendar is assigned before the demo review and resource/channel decisions. Limit planned tickets to observed team capacity, and split anything that cannot be independently reviewed in 1–3 days.

| Sprint | Outcome | Candidate tickets | Entry gate | Exit gate |
| --- | --- | --- | --- | --- |
| S1 | Reliable provider seam and isolated runtime proof | `MODEL-02`, `MODEL-03`, `HERMES-01`, `HERMES-02`, `QA-01` | Current baseline preserved | Same synthetic tool journey through supported adapters; actual Hermes proof if available, otherwise prepared status retained |
| S2 | Identity and durable storage foundation | `FOUND-01`, `IDENT-01`, `IDENT-02`, `MEDIA-01` | Store/identity ADR and budget reviewed | Authorized scope, workspace migration rehearsal, retained backups and deletion/restore tests |
| S3 | Recoverable voice/channel jobs | `JOBS-01`, `JOBS-02`, `VOICE-01`/`VOICE-02`, `WA-01` | Identity/store/media boundary ready | Durable inbox/leases/outbox, actual web voice and selected channel preflight |
| S4 | Owned appointment vertical slice | `CLINIC-01`, `CLINIC-02`, `CLINIC-03`, `WA-02` | Atomic DB constraints and jobs available | No-charge demo booking/status/cancel; duplicate/concurrency/restart cases pass |
| S5 | WhatsApp voice and locale quality | `WA-03`, `VOICE-03`, `EVAL-01`, `OPS-02` | Approved sender/recipient and actual transport | Recorded per-language outcomes, source/receipt fidelity and controlled reminder delivery |
| S6 | Household reuse and beta hardening | `KITCHEN-01`/`02`, `INV-01`/`02`, `QA-03`, `DEMO-02` | Membership and provenance ready | Reviewed extraction, stock ledger correctness, privacy/recovery and beta review |

Some buckets intentionally exceed a single engineer's unmeasured capacity. At sprint planning, choose a vertical subset and roll remaining candidates forward; do not relabel unfinished work done. `TXN-01` is an optional design gate after beta foundations, not part of an automatic financial launch.

## Definition of ready

The ticket has an explicit owner/session, concrete input→outcome, required source/tests, prerequisites, scoped data/permissions, acceptance cases and known external dependencies. Any provider, license, route or spend decision necessary for that slice is resolved or the ticket is marked blocked. Draft interfaces are labeled proposed until implemented.

## Definition of done

The intended behavior works through its application boundary; meaningful success/error/ownership/retry tests pass; real integration evidence exists wherever “live” is claimed; secrets/private data are excluded; user labels remain truthful; affected docs and HANDOFF are updated. A production change also needs known image/revision, post-deploy smoke evidence and rollback. Documentation-only work needs link/path/consistency review and no unintended runtime changes.

Use the [sprint review template](templates/sprint-review.md). Close each sprint with delivered IDs/evidence, defects/blockers, capacity observations and the next smallest ready slice.
