# Implementable development backlog

Baseline: 26 October 2026. All tickets are proposed/unstarted unless explicitly marked otherwise. Existing shipped work is in [current state](current-state.md), not re-listed as unfinished. The documentation pack is `DOC-01`; its verification is recorded in HANDOFF.md.

Priorities: **P0** immediate demo/reliability; **P1** foundation or primary voice/task workflow; **P2** household breadth/beta; **P3** optional later integration. Estimates are engineering effort ranges: XS≤half-day, S≈one focused day, M≈two–three days. They exclude provider access, native-language review and other external waiting. Split larger investigations after the first spike. Owner is unassigned until a developer/Claude session claims one ticket in HANDOFF.md.

## Ready work and dependency gates

Start with `MODEL-01`, `QA-01` or `OPS-01` after `DOC-01`. They can proceed without provisioning another provider. Do not require Nous setup. Storage/channel/spend decisions are explicit prerequisites for later slices. “Ready” means prerequisites are available, not that success at an external API is guaranteed.

## Documentation and model reliability

### DOC-01 — Complete a reusable engineering handoff

**P0 · M · Documentation completed and locally verified · Depends:** current repository audit. GitHub synchronization/CI evidence is recorded in HANDOFF.md.

Deliver indexed current-state/product/architecture/API/data/security/operations docs, roadmap/sprints/tickets, concise CLAUDE.md and a continuation prompt. Correct stale hosted/local wording and the skipped Nous decision. Files: root agent/context files and `docs/`.

**Accept:** local Markdown links resolve; documented source/test/config paths exist; current versus proposed status is clear; no credentials/private artifacts are included; pack is committed/pushed to the selected repository with exact verification in HANDOFF. It must let a fresh engineer choose the next task without the old conversation.

### MODEL-01 — Establish one actual permitted free-model tool journey

**P0 · S · Live acceptance blocked by provider capacity (27 October) · Depends:** existing model catalogue. A fresh synthetic hosted inventory request returned HTTP429/RATE_LIMITED; the permitted catalogue still contained only Gemma4 26B. Diagnostic acceptance is recorded; successful live inference is not claimed.

Use a fresh synthetic workspace through hosted message/research boundaries. Record key-permitted model, actual inventory tool observation and grounded reply; attempt source-backed research separately. Relevant: `agent_loop.py`, `model_catalog.py`, `research.py`, corresponding tests.

**Accept:** real model/tool evidence or a dated reproducible capacity/access blocker; no paid fallback, guardrail relaxation or claim that a plain text response proves tool execution. Keep direct tools usable. Do not repeat Nous onboarding.

### MODEL-02 — Introduce a provider-neutral planning seam

**P1 · M · Implemented contract slice (27 October) · Depends:** `MODEL-01` diagnostics; [model contract](model-and-hermes-plan.md). See [adapter implementation](model-adapters.md). OpenRouter and local Meta share typed completion contracts; Meta evidence is synthetic, not live access.

Wrap existing application/OpenRouter and local Meta planning behavior behind normalized inputs/results/errors. Keep domain policy and task identity outside provider SDKs. New module names are implementation choices; preserve existing HTTP behavior while adapting.

**Accept:** contract tests run the same synthetic task with two adapter implementations; unsupported tools/credentials/endpoints fail closed; switching does not replay saved effects. A mocked second provider is labeled contract coverage until actual access exists.

### MODEL-03 — Make provider limits and recovery observable

**P1 · S · Implemented request-observation slice (27 October) · Depends:** `MODEL-02`. Sanitized request failures and process-local per-model observations are exposed in Connections; durable metrics/budgets and provider-specific backoff remain separate future work.

Expose structured capacity/auth/catalogue/timeout diagnostics and bounded retry guidance. Record model/request/phase latency without prompts or keys; preserve saved tool results on follow-up failure. Files: `integrations.py`, `agent_loop.py`, `research.py`, `web/app.js`.

**Accept:** tested429/403/404/timeout/invalid-output paths; no retry storm; every UI message distinguishes permission from capacity; process-local limits are not labeled global billing caps.

## Quality and operations

### QA-01 — Capture the existing regression and edition baseline

**P0 · S · Ready · Depends:** existing source/tests.

Run documented checks in an isolated environment, map actual hosted/local/static edition behavior, and create reproducible synthetic fixtures for model/provider failures. Files: existing `tests/`, CI, current-state documentation.

**Accept:** existing80-test checkpoint can be reproduced or differences are explained; no production keys/network in CI; hosted-only forms/routes are not promised in the local edition; actual source text/result assertions do not assume a website's title must also occur in its body.

### QA-02 — Verify research and handoff usability

**P0 · S · Depends:** current web UI; selected changes under test.

Use a real browser for start/progress/resume/cancel, source expansion, provider outage, draft discard and keyboard flows. Test a 390px device/viewport if supported, plus tablet/desktop. Files: `web/`, browser/API tests.

**Accept:** no unintended horizontal overflow, accessible labels/focus/progress, no recipe-completion button on research, safe rendered source links, visible `needs_input`, and no fake live-flight/transaction claims. Distinguish actual viewport sizes from requested sizes.

### QA-03 — Exercise privacy, injection and recovery boundaries

**P2 · M · Depends:** identity/media/jobs changes selected for beta.

Create adversarial cases for cross-member IDs, stale approvals, page/receipt prompt injection, role revocation, oversized media and interrupted jobs. Use synthetic inputs. Relevant: all public boundaries and [security model](security-and-privacy.md).

**Accept:** unauthorized access denied; model cannot expand tools/permissions; private data not logged; recoverable state retained; no duplicate external operation during retries. Findings have explicit disposition before beta.

### OPS-01 — Rehearse current deployment and rollback

**P0 · S · Ready · Depends:** authorized cloud read access for inspection; new deployment only when actually needed.

Verify current revision/config/worker IAM and document a staging or controlled rollback rehearsal. Preserve both model/railway secrets and private worker invocation. Files: `deploy/gcp/`, Docker/Cloud Build configs, operations docs.

**Accept:** secret-free manifest inspection before upload; known artifact/revision; public app health and private-worker denial; persistence retained; rollback does not overwrite newer state. No redeployment merely because documentation changed.

### OPS-02 — Add bounded operational signals and retention

**P1 · M · Depends:** chosen tasks/jobs/media services.

Add task/phase/operation correlation, latency/error/budget signals, restricted log retention and media/state lifecycle visibility. Verify actual credits/expiry/current prices before resource expansion.

**Accept:** useful diagnostics without raw audio/transcripts/keys; alert owner/action defined; budget alerts described accurately; retention/deletion behavior tested; no unrestricted project-wide role introduced.

## Identity, storage and durable execution

### FOUND-01 — Select and rehearse the transactional-store migration

**P1 · M for first rehearsal · Depends:** architecture/cost decision.

Write an ADR selecting schema/migration tooling and deployment placement, then convert one synthetic visitor workspace with source/target consistency checks. Candidate: PostgreSQL; not provisioned by this ticket description. Preserve existing snapshot edition during transition.

**Accept:** schema versions, ownership mapping, backup/restore and rollback strategy; task/history/balance equality on fixture; one authoritative write store; no live financial writes. Split full migration after rehearsal results.

### IDENT-01 — Add verified principals and channel-neutral ownership

**P1 · M · Depends:** `FOUND-01` schema decision.

Implement principal/household/membership checks around a single current task read/write path, then extend consistently. Choose an authentication mechanism through an explicit design; do not treat visitor cookies as verified household identity.

**Accept:** stored membership controls roles; principal cannot be injected by model/request; two-account isolation and revocation tests; migration/claim behavior does not reveal existing anonymous workspaces.

### IDENT-02 — Link a channel identity without broadening data visibility

**P1 · S/M · Depends:** `IDENT-01`, `WA-01` route choice.

Bind verified channel sender to principal using a revocable, bounded verification flow. Keep personal bills/appointments private and kitchen visibility explicitly shared.

**Accept:** forged sender, expired link, different member and group context cannot access personal tasks; unlink/revoke works; no reusable linking secret appears in logs or source.

### MEDIA-01 — Implement scoped expiring media storage

**P1 · M · Depends:** ownership design and retention decision.

Provide a narrow upload/download reference path with actual MIME/size/duration checks, private storage and deletion/lifecycle handling. New files/routes require API contracts before implementation.

**Accept:** cross-user media denial, oversized/invalid codec rejection, bounded signed/reference access, deletion verification and no recordings in Git. Synthetic-only local evaluation may precede public upload support.

### JOBS-01 — Build durable inbox and leased work processing

**P1 · M · Depends:** `FOUND-01`, scoped task ownership.

Persist deduplicated inbound event/task intent, job due/version/lease/attempt state and bounded recovery. Select database polling or authenticated delivery through an ADR; reuse one canonical task service.

**Accept:** duplicate delivery creates one task intent; worker crash/expired lease resumes; concurrent claims do not execute a local owned action twice; retry/terminal state observable. No promise of exactly-once external delivery.

### JOBS-02 — Add durable outbox and reminder reconciliation

**P1 · M · Depends:** `JOBS-01`, selected channel for real delivery tests.

Store reply/reminder intent with task/booking version and delivery key, then send through the channel adapter. Keep delivery state separate from booking/task success.

**Accept:** restart retains due work; cancelled booking invalidates reminder; ambiguous send does not recreate booking/action; approved test recipient receives actual evidence when live delivery is enabled.

## Speech, runtime and channel

### VOICE-01 — Benchmark one open-weight Indic speech path

**P0/P1 · M · Ready for synthetic evaluation · Depends:** legal access to candidate weights and a bounded execution environment.

Record exact ASR/TTS versions/licences, CPU/GPU memory, speed and sample quality using permissioned recordings. Reuse `integrations.py` contracts; add evaluation tooling without auto-provisioning GPUs.

**Accept:** real audio/transcript/output, critical-field analysis and cost/hardware decision; unsupported language/cold-start limits recorded. Mock JSON adapters and model marketing do not satisfy this ticket.

### VOICE-02 — Ship one scoped web voice task

**P1 · M · Depends:** tested speech candidate, `MEDIA-01` for public use.

Add hosted speech contracts/routes and review UI around an existing safe tool, initially one declared tested locale. Critical fields require clarification; store task state independently of audio.

**Accept:** actual audio→transcript review→tool→same-language text/audio; speech retry never replays completed effects; missing ASR/TTS preserves usable text/error path; access/deletion/size tests pass.

### VOICE-03 — Evaluate all requested languages and code switching

**P1 · M plus reviewer time · Depends:** `VOICE-02`.

Run 10 recorded tasks per Tamil/Malayalam/Kannada/Hindi and5 English with reference transcripts/expected fields. Review same-language reply and pronunciation with speakers.

**Accept:** per-locale critical-field/task-success/latency report; every executed action matches confirmed details; proposed8/10 task target measured honestly; weak/untested locales remain labeled.

### HERMES-01 — Verify the isolated source runtime

**P1 · S/M · Depends:** supported upstream environment and a usable authorized model.

Use the documented restricted plugin in a separate source environment. Pin/record upstream commit, allowed toolset and workload identity; disable unrestricted tools and personal context.

**Accept:** actual model→plugin→private worker→observation trace; no website keys copied into browser/runtime tools; handler tests alone do not mark connected.

### HERMES-02 — Bridge canonical tasks to the verified runtime

**P1 · M · Depends:** `HERMES-01`, `MODEL-02`.

Adapt task ID/version/scoped observations/allowed tools into the runtime and normalize its output. Keep ownership, approvals and operations in application code.

**Accept:** same synthetic workflow through application and Hermes adapters; model/runtime swaps do not replay effects or reset task identity; rollback to application loop remains possible.

### WA-01 — Decide the WhatsApp route with real preflight evidence

**P1 · S plus account waiting · Ready for research, not unapproved messaging.**

Compare current official route and supported bridge requirements: eligibility, number/session, voice media, signatures, recipient rules, persistence, deployment and groups. Record one ADR and exact setup gaps.

**Accept:** supported direct-message path selected; primary documentation/version/date recorded; group support not assumed; no unsolicited messages or surprise paid resource commitments.

### WA-02 — Implement verified durable text ingress/reply

**P1 · M · Depends:** `WA-01`, `IDENT-02`, `JOBS-01`/`02`, approved test sender/recipient.

Normalize verified inbound messages, deduplicate provider IDs, route a safe existing tool and deliver a reply through the outbox. Clarifications bind to the correct active task/version.

**Accept:** actual approved test conversation; forged/duplicate/out-of-order/revoked cases tested; credentials/session private; message retry does not duplicate domain effects.

### WA-03 — Complete voice/media and reminder transport

**P1 · M · Depends:** `WA-02`, web speech acceptance and media policy.

Fetch authorized voice media, run the existing canonical speech/task pipeline and send concise same-language audio/text. Test one explicitly requested reminder with the owned demo booking when available.

**Accept:** real inbound/outbound audio, sender/task correlation, recoverable media/TTS failure, compliant delivery behavior and no duplicate booking/reminder effects. Do not claim cook-group operation without separate route verification.

## Owned clinic workflow

### CLINIC-01 — Seed and query an owned demo calendar

**P1 · M · Depends:** transactional schema/ownership.

Create demo clinic/service/slot records with explicit timezone and availability versions; implement scoped search/read tools and clear demo labels. Exact tool/file names are proposed until contracts exist.

**Accept:** actual deterministic slot results, exact date/time/timezone, no past/invalid slot selection, fixtures visibly owned-demo and no implied real clinic relationship.

### CLINIC-02 — Approve and book one slot atomically

**P1 · M · Depends:** `CLINIC-01`, payload-bound approval/operation design.

Prepare a selected slot, bind human confirmation to actor/task/version/details/expiry, and create the no-charge booking plus local operation result atomically.

**Accept:** two-user contention yields one booking; repeated/stale/changed approval rejected or returns the prior result; crash/restart does not duplicate; model cannot approve itself.

### CLINIC-03 — Status, cancellation and reminder lifecycle

**P1 · M · Depends:** `CLINIC-02`, durable jobs/outbox for reminders.

Add booking lookup, authorized cancellation and reminder scheduling tied to booking version. Cancellation after commit is a separate operation, not a task-status overwrite.

**Accept:** correct owner/status/reference; cancellation releases only the intended slot; pending reminders invalidated; restart/duplicate delivery tests and one approved live test where transport exists.

## Cooking and inventory expansion

### KITCHEN-01 — Extract a reviewed recipe from accessible source evidence

**P2 · M · Depends:** source retrieval permissions and bounded extraction contract.

Accept an accessible recipe page or permitted video transcript/captions; stage ingredients/quantities/steps with source/time and missing/uncertain fields. Reuse inventory planning.

**Accept:** distinguishes processed transcript/page from watched video; unavailable source requests alternative material; prompt injection cannot change policy; user reviews uncertain ingredients before stock/planning use.

### KITCHEN-02 — Apply voice preferences to a practical cooking plan

**P2 · M · Depends:** `KITCHEN-01`, tested voice/preferences scope.

Apply servings/spice/preferences to reviewed recipe facts, check stock and produce short chosen-language steps. Preference storage is revocable and household-role scoped.

**Accept:** quantities/source/estimate status preserved, missing items explicit, practical speaker review, no stock deduction until confirmed meal completion; cook cannot access private household tasks.

### INV-01 — Stage grocery-image/list extraction for review

**P2 · M · Depends:** media ownership and extraction candidate evaluation.

Convert a permitted bill/list image to a draft of item/quantity/unit/price-as-evidence fields; user corrects then imports through the existing deduplicated ledger. Do not treat OCR confidence as calibrated unless measured.

**Accept:** uncertain/missing units highlighted; image/receipt reference duplicates do not add twice; no silent quantity guessing; source image deletion and injection tests pass.

### INV-02 — Household consumption, corrections and suggestions

**P2 · M · Depends:** household membership and existing inventory ledger.

Scope stock to households, record meal references/estimates and corrective reversals, and improve suggestions from completed dish history/current availability.

**Accept:** concurrent/repeated meal confirmation deducts once; insufficient stock does not partially deduct; correction history/reversal is traceable; one household cannot see another's stock.

## Evaluation, presentation and optional transactions

### EVAL-01 — Build the reproducible end-to-end evidence report

**P1 · M · Depends:** each feature whose live claim is evaluated.

Version synthetic task sets, permissioned locale samples, model/runtime profiles, expected fields/outcomes and measured phase timings. Keep offline phrase scores separate from speech/live provider outcomes.

**Accept:** per-language/per-provider tables with sample counts/failures, safe artifacts and date/revision; no synthetic score presented as actual voice success; reviewers can reproduce the stated scope.

### DEMO-01 — Rehearse and package the truthful hackathon demo

**P0 · S/M · Depends:** verified current capabilities and independently checked event rules.

Prepare a short script/recording showing one useful journey, evidence, recoverable failure and secondary kitchen/stock value. Use only features that actually pass; record what is Meta/OpenRouter/demo/fixture.

**Accept:** public app usable, source/time/receipts visible, no private data/credentials, known revision/rollback, submission requirements checked. Do not claim Meta eligibility if no required live usage is demonstrated.

### DEMO-02 — Private household beta readiness review

**P2 · M · Depends:** identity/channel/voice/evaluation/recovery gates.

Review actual language quality, member roles, retention/deletion, operational cost and incident handling with a small consenting household cohort.

**Accept:** unresolved issues have owners/dispositions; membership revocation/deletion/restore demonstrated; capability statement matches evidence; no financial executor enabled by beta approval alone.

### TXN-01 — Design one real provider operation behind independent gates

**P3 · M for design/spike only · Deferred · Depends:** explicit human integration authorization and durable identity/approval/operation foundation.

Choose one supported bill/order provider, verify its current account/access/terms, define exact approved payload and status/receipt/cancel/reconciliation semantics. Leave actual execution disabled until separate acceptance and authorized activation.

**Accept:** provider-specific threat/timeout/idempotency/reconciliation tests and sandbox evidence; approval binds total/recipient/details; uncertain outcomes do not blindly retry; no real purchase/payment merely because this ticket exists.
