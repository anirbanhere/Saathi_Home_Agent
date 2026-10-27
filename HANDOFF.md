# Home Agents development handoff

Updated: 27 October 2026, Asia/Kolkata. Branch: `codex/home-agent-demo`. Runtime source checkpoint: `08d0bbe`.

## Latest human objective

Continue development from the documented roadmap. QA-02 research/handoff usability was selected, verified in a real browser, fixed and deployed. No new provider/key, paid inference, account pairing, messages or transactions were introduced.

## Entry points

[CLAUDE.md](CLAUDE.md) → [documentation index](docs/README.md) → [current state](docs/current-state.md) / [backlog](docs/backlog.md). Current slice: [QA-02 evidence](docs/qa02-usability.md) and [acceptance plan](tasks/qa02-usability-plan.md). Model contracts: [shared adapters/availability](docs/model-adapters.md). Recovery: [operations runbook](docs/operations-runbook.md).

## Current release and rollout

Public URL: `https://home-agents-xswei7prnq-uc.a.run.app`. Canonical public repository: `https://github.com/anirbanhere/Saathi_Home_Agent`; preserve `previous-origin` and visibility.

- Current ready website: **home-agents-00010-w5z**, image build **db1242d9-a0cd-42de-8102-a6c22607bb73**, 100 percent traffic. Runtime source `08d0bbebb5df0e83c7182d62821cecdeca7f2dd5`.
- Previous verified rollback: **home-agents-00009-xhz**, build `3c7a6caf-5c61-4ee5-ae81-421b412816d6`. No schema migration; code rollback must preserve newer snapshots.
- Private browser unchanged: `home-agents-browser-00001-w2m`, build `0604bf8b-5c08-4f48-84d5-a2b4d8f5f07f`. Dedicated identity, private invocation, no provider secrets/project-data roles.
- Both provider secret references, literal environment values and website runtime identity were inspected/preserved. No secret payload was retrieved. Upload manifest selected33 runtime files; separate pre-build scan found no private paths/credential matches. Tests/QA harness/docs remain excluded from cloud source.

## What changed

- Reproduced a real UI defect: discarding a draft updated history but left its result card actionable and dropped focus to BODY.
- Existing result panels now synchronize their displayed task with refreshed canonical state. Result-panel open source/details disclosures are preserved. Cancelled drafts lose their provider continuation links.
- Task actions restore keyboard focus to the refreshed control or named task card when their trigger disappears; surviving focus elsewhere is not deliberately moved. Task cards have a visible focus outline and accessible name/status.
- Research has a separate atomic live progress line. Saved sources remain rendered during the next step; recoverable transport failures have inline guidance. Cancellation updates the status line. No additional polling/probes or external permissions.
- Added `tests/ui_fixture_server.py`: loopback-only temporary synthetic hosted state, page/blocked-page observations and deliberate model failures; no provider requests. Run `python tests/ui_fixture_server.py`, open `http://127.0.0.1:8766` in a fresh context. It is reproducible manual QA data, not a new automated browser suite. Test server was stopped after verification.

## Verification

- **97 existing Python tests passed** using fixture provider/blank model and railway keys, authorized loopback sockets and workspace-specific temporary directory. JS syntax, Python compilation and Git whitespace checks passed.
- [Implementation CI passed](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40458455826) for `08d0bbebb5df0e83c7182d62821cecdeca7f2dd5`. Later documentation-only synchronization does not change the deployed image.
- Actual local Chromium: save/discard, blocked page Needs details, synthetic model outage with retained source, keyboard source expansion/resume/cancel, reload/history resume and cancelled progress line. Literal script-like source text remained text with zero inserted script nodes. Source links retained `noopener noreferrer`.
- Actual Activity viewport measurements:390/390/390,768/753/753,1440/1425/1425 (`innerWidth`/document client/document scroll). Emulation can reload, so Activity was selected again before each measurement. Expanded-source mobile screenshot inspected. Latest fixture console had no warnings/errors. This is targeted QA, not a full screen-reader/axe/Core Web Vitals audit.
- Post-deploy: public health `ok`; fresh synthetic dal plan persisted; public website→private worker inspected Python.org with one source and `succeeded` page-inspection status. No AI summary or transaction was executed. Prior synthetic visitor tasks survived the new revision.
- Actual deployed390px UI: saved then discarded a new synthetic food draft; result showed Cancelled, zero action buttons/links, focus on named Cancelled article, document width390. No console errors/warnings. No provider checkout was opened.

## Stable decisions and limits

OpenRouter shared adapters and process-local request observations remain deployed. The last real inference attempt on27 October returned429, with only Gemma4 26B permitted. No new live inference attempt was needed for this UI slice. MODEL-01 successful live tool/research acceptance remains unverified. Do not keep repeating the same blocked request, relax guardrails or substitute paid/fixture inference.

The human explicitly skipped Nous setup/model tests; do not request a key or make it a prerequisite unless reopened. Meta has synthetic contract coverage only; actual Hermes/ASR/TTS/WhatsApp/clinic/payment execution remains unconnected.

Anonymous visitor snapshots are not shared family identity or a financial operation ledger. Checkout drafts are unverified/manual; bill/journey approvals remain sandbox. Markdown is engineering context, not runtime personal memory or authorization.

## Next actionable work

QA-02's targeted usability slice is complete; consult its evidence rather than redo it. Choose **VOICE-01**, a bounded, license-verified open-weight speech benchmark using synthetic/permissioned audio and existing resource constraints; record actual transcript/output/critical-field/latency evidence before promising language quality. Another independent option is **OPS-01**, a controlled rollback rehearsal with state preservation. No unattended GPU provisioning, contacts/messages or real financial actions follows automatically.

MODEL-02's completion seam and MODEL-03's request-observation slice are implemented. Full task/runtime/provider swapping, durable metrics/budgets/backoff, shared identity, media ownership and durable jobs remain future tickets. No pending human input is needed to begin the next bounded investigation.
