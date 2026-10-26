# Proposed build plan: Home Agent hackathon demo

Current delivery sequence: [roadmap](../docs/roadmap.md), [sprint plan](../docs/sprint-plan.md) and [backlog](../docs/backlog.md). This document and [voice-first-plan.md](voice-first-plan.md) preserve earlier prototype/voice planning; the working public Cloud Run/hybrid release supersedes their original ordering.

Status: User authorized implementation. The local prototype is built; see ../docs/implementation-status.md for evidence and remaining integrations. This file preserves the proposed delivery plan.
Updated: 26 October 2026, IST.

## Confirmed scope

- User has hackathon acceptance; Meta Model API setup will happen later.
- Hermes + Meta Muse + open-weight Indic speech is the intended foundation.
- Tamil, Malayalam, Kannada, and Hindi are the initial languages.
- All three capabilities remain in scope; everyday tasks (Agent 3) come first.

## Working assumptions

Plan conservatively for one builder until team capacity is known. Hosted Muse, SQLite persistence, and a thin Python tool service are proposed. Payment/booking demonstrations use explicit sandbox data unless working provider integrations are available. Model choice, machine/GPU access, and WhatsApp deployment route still need validation.

## First demonstration

Start with train-status lookup: voice request -> missing-detail clarification -> read-only provider call -> source/time-stamped answer in the same language. The provider access check must happen early; any local replay remains visibly labeled.

Then add a bill-payment sandbox: fetch bill -> show biller/amount -> record approval -> execute sandbox operation -> verify status -> return sandbox receipt. This proves controlled action execution and provides a useful failure/retry demonstration.

Ticket booking is a separate third tool flow. Build its bounded sandbox version after the two primary task paths work. Real booking depends on provider access and is not a prerequisite for the demo.

## Architecture

Use one runtime and gateway with three domain toolsets. Keep speech, model, messaging, and service providers behind replaceable adapters. The application owns durable task states, approvals, and duplicate-event protection. The model interprets requests and calls tools; tools supply task outcomes.

Build real deterministic tools while Meta access is pending. Model fixtures may drive development tests, but they are not evidence of live Muse understanding. Once credentials are available, replace the fixture adapter and run the actual four-language evaluation.

Do not select a GPU model or hosting plan until available hardware is known. Run speech models in a separate process so their deployment does not dictate the Hermes host.

## Sequence and dependency graph

1. Validate rules, WhatsApp connection, machine resources, and data-provider access.
2. Deliver one text-based train-status path with durable task records.
3. Integrate Hermes/Muse when credentials arrive; verify tool calling and follow-up turns.
4. Add one voice round trip, then validate all four languages.
5. Add sandbox billing and booking paths with persistent approval/execution state.
6. Connect grocery-bill ingestion and inventory to customized cooking instructions.
7. Evaluate failures, record the demo, and prepare submission artifacts.

WhatsApp and provider connectivity checks can proceed while deterministic tool logic is built. Full Muse acceptance testing depends on credentials. Cooking depends on inventory queries and accessible recipe evidence; consumption updates depend on confirmed meal completion.

## Suggested windows

| Dates (IST) | Deliverable |
| --- | --- |
| 26–27 Oct | WhatsApp/provider checks, application skeleton, text task path |
| 28–29 Oct | Target Meta access; actual Hermes/Muse tools and voice round trip |
| 30 Oct | All four language paths; sandbox action execution |
| 31 Oct–1 Nov | Inventory and customized cooking connected |
| 2 Nov | Evaluation, service failure, approval, retry, and access tests |
| 3 Nov | Demo recording, clean setup rehearsal, documentation |
| 4 Nov | Scope freeze, final portal requirements, early submission |

Meta access on 28 October is a planning target, not a confirmed availability date. If access is delayed, continue independent tasks and report the live-model milestone as incomplete.

## Checkpoints

- Foundation: messages reach the actual gateway, one text tool result is persisted, data source is identified, and failure states are truthful.
- Agent 3: a real Muse-driven voice task works; all four languages are evaluated; transaction execution is controlled and duplicate-safe.
- Household: bill ingestion and recipe customization use the same persisted inventory, with corrections and consumption estimates.
- Submission: recorded features match actual behavior; setup is reproducible; actual official requirements and receipt are checked.

## Risks and decisions

| Risk | Response |
| --- | --- |
| Meta access delayed | Build independent tools/evals now; validate real model behavior as soon as possible. |
| WhatsApp setup blocks demo | Test immediately. Keep a labeled local transport for debugging; changing the final presentation channel is a scope decision. |
| No train/billing provider access | Use visible sandbox/replay mode; never describe it as live. |
| Speech too slow or inaccurate | Measure on available hardware and select checkpoints from actual four-language samples. |
| YouTube evidence inaccessible | Select a recipe with accessible source material; disclose exactly what was processed. |
| All workflows exceed available time | Finish two Agent 3 paths first, then one complete cooking/inventory path; defer breadth beyond these examples. |

## Next practical dependency

Identify development-machine OS, RAM, GPU/VRAM (if any), and whether a dedicated WhatsApp number is available. These determine speech deployment and messaging setup. API credentials should be entered through local configuration, not pasted into chat.
