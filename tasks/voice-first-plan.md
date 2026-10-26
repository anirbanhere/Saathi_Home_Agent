# Home Agents voice-first delivery plan

Current cross-domain delivery and sprint selection: [roadmap](../docs/roadmap.md), [sprints](../docs/sprint-plan.md), [backlog](../docs/backlog.md). This file preserves the earlier voice/clinic proposal and its acceptance ideas.

Current delivery priority: [hybrid-agent-plan.md](hybrid-agent-plan.md), authorized after the user requested broader browser-based execution. This file preserves the voice/appointment roadmap.

Date: 26 October 2026. Status: planned, not implemented.
Design authority: `../docs/home-agents-redesign.md`.

Priority update: the user requested the running public website first. The hosted implementation and evidence are tracked in `../docs/hosted-deployment.md` and `../HANDOFF.md`. This file preserves the broader voice/appointment roadmap; its closing implementation-status statement describes the original redesign checkpoint, not the latest hosted release.

## Confirmed

- WhatsApp voice is the primary intended interface; the web app is a companion.
- Models must be interchangeable; free OpenRouter inference is the initial preference and Meta access comes later.
- Tamil, Malayalam, Kannada, Hindi, and English remain targets.
- Use an owned demo clinic calendar. Its appointments must always be labeled as demo records.
- Agent 3 is first priority; cooking and inventory follow on the shared foundation.
- GCP project `sathi-home-agent` is confirmed active with billing linked. The user selected `us-central1`. Remaining credits, expiry, quotas, and pricing are unverified; see `../docs/gcp-setup.md`.

## Ordered slices

| Order | Deliverable | Exit evidence |
| --- | --- | --- |
| 0 | Channel feasibility and project preflight | Chosen WhatsApp route's eligibility, number/authentication and reminder constraints documented; GCP project/region/credit/quotas checked before spending |
| 1 | Durable demo clinic workflow | Search slots, selection, exact-action approval, atomic booking, lookup, cancellation, restart persistence; all labeled demo |
| 2 | Identity and worker boundary | Sender membership, private personal tasks, shared kitchen roles, durable inbox/jobs/outbox; production API boundary specified and authenticated |
| 3 | Provider-neutral reasoning + Hermes | Same tool schemas work through two adapters; bounded observe/recover loop; no direct model-controlled approvals |
| 4 | Four-language voice loop | Real audio download/normalization, ASR, critical-field clarification, localized response and TTS; measured samples reviewed by speakers |
| 5 | WhatsApp connection and reminders | Actual inbound and outbound direct messages; signed ingress where applicable; reminder survives restart and respects messaging rules |
| 6 | GCP deployment | HTTPS, private secrets/media, supervised worker, consistent backup and restore rehearsal; remote end-to-end test |
| 7 | Household reuse | One reviewed grocery input -> persisted stock -> voice-customized recipe -> confirmed meal consumption and correction |
| 8 | Hackathon evidence | Meaningful live Meta usage if required and available; model-swap demonstration; truthful recording and final requirements checked |

Slice 0 can proceed alongside the deterministic demo calendar. The calendar can be built before credentials; a live WhatsApp claim cannot. Voice evaluation can use recorded audio before a number is paired. No public repository or submission is created simply because the reference brief suggests one.

## Required acceptance cases

- One full voice journey in each of Tamil, Malayalam, Kannada, and Hindi, plus English; mixed-language dates, clinic names, and numbers included.
- Start with ten recorded tasks per Indian language and five English tasks. Proposed release target: at least eight of ten per Indian language reach the correct tool outcome, with every executed action matching the details approved by the user. Ambiguous inputs should clarify rather than guess. Report task success and critical-field transcription errors separately; do not reuse the old synthetic text scores as speech evidence.
- Demonstrate model swap on the same persisted conversation at a safe boundary, using two real available providers/models. Fixtures can verify contracts in development but do not fulfill this live-model criterion.
- A rejected/expired approval, forged model approval, altered action details, and a second pending task cannot authorize execution.
- Duplicate inbound events, two concurrent approvals, and crash/restart after commit create one booking and return its existing reference.
- Two users competing for one slot produce one successful booking. The other gets fresh options and must approve again.
- An uncertain external timeout triggers status reconciliation, never an unverified success receipt or blind second commit.
- Changing/cancelling a pending task invalidates approval. Cancelling a confirmed demo booking updates booking and reminder state consistently.
- Reminder retries create no duplicate booking; deduplicate sends using provider capabilities and record any ambiguous delivery outcome. Do not claim exactly-once network delivery where it cannot be guaranteed.
- ASR/TTS/model/provider failure produces a recoverable response and retains task state. A speech retry must not execute a tool again.
- Cross-household IDs and cook-role requests cannot reveal another member's private appointments or bills.
- Audio retention/deletion works; logs contain opaque references rather than personal content or secrets.
- Backup restore recovers bookings, approvals, operations, jobs, and reminders; stale leases resume safely.
- Measure transcription, reasoning/tool, synthesis, queue, and overall reply latency and model requests per journey. Establish targets from the first hardware benchmark rather than promising unmeasured speed.

## Demo story

Use one three-minute story: voice request -> exact-date clarification -> available slots -> explicit approval -> persistent demo appointment -> same-language voice confirmation -> short requested test reminder. Show a slot becoming unavailable or a provider failure, then recovery. If possible, replay another locale and swap the reasoning provider without changing domain tools.

Record which parts use real inference, real WhatsApp transport, our owned calendar, and fixtures. Keep existing train/bill/cooking prototypes as secondary examples. Do not expand into live payments or broad browser-based bookings before this workflow passes.

## Current status

The redesign and this plan are complete. The current application still has the behavior documented in `../docs/implementation-status.md`. No new appointment, voice, model-switching, WhatsApp, reminder, or GCP capability is shipped by these documentation changes.
