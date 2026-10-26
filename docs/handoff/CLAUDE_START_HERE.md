# Continue Home Agents with Claude

Use the existing [repository](https://github.com/anirbanhere/Saathi_Home_Agent). Clone/open it with Claude Code, or provide the relevant files to a Claude chat that can propose patches. Repository access does not automatically grant GCP/provider/account access.

## Copy this starting prompt

```text
Continue the Home Agents project in this repository.

Read CLAUDE.md, AGENTS.md and HANDOFF.md first, then docs/current-state.md
and docs/README.md. Preserve unrelated working-tree changes. Use source/tests
as the authority for implemented behavior, and mark proposals separately.

Choose the next ready ticket from the latest HANDOFF.md. As of 27 October,
MODEL-01 was checked and remains capacity-blocked; MODEL-02's shared completion
seam and MODEL-03's request observations are implemented. Prefer an independent
QA-02 or bounded VOICE-01 slice rather than repeat the same blocked request.
Inspect existing source/tests first. Do not require a new provider, paid
inference or weakened guardrails. Nous setup/testing was explicitly skipped.

If a selected integration is externally blocked, record its exact redacted
blocker and continue an independent ready slice. Do not recreate already
implemented adapters, poll unavailable providers or fabricate live evidence.

Before implementation, state the selected acceptance path and relevant files.
Implement one coherent slice, run appropriate existing/new checks, review
ownership/replay/security behavior, and update ticket evidence plus HANDOFF.md.
Do not refactor the whole app or deploy documentation-only changes.

The public website is already on GCP Cloud Run. The private browser worker,
RailRadar lookup, kitchen inventory and handoff drafts exist. Actual Hermes
orchestration, WhatsApp, hosted Indic speech, appointments and real payments
are not connected. Preserve those truthful labels. Never send third-party
messages or execute transactions without explicit human authorization.

Finish with the concrete change, commands/results, remaining gap and next
ready ticket. Keep secrets, recordings, databases and private user content out
of commits and output. Follow docs/development-and-claude.md and the runbook
for any later authorized runtime rollout.
```

This prompt selects work from the latest checkpoint, not proof that live MODEL-01 acceptance succeeded or authorization for unrelated external effects. Edit the selected ticket if your next priority changes.

## Context bundles by task

| Work | Load after entry files |
| --- | --- |
| Model reliability | `docs/model-and-hermes-plan.md`, `agent_loop.py`, `model_catalog.py`, `integrations.py` and matching tests |
| Browser research | `docs/hybrid-browser.md`, `research.py`, `browser_*` source and browser/research tests |
| Household identity/storage | `docs/data-and-task-design.md`, `docs/security-and-privacy.md`, `cloud_state.py`, `store.py`, hosted boundary/tests |
| Voice | `docs/voice-and-whatsapp-plan.md`, `docs/testing-and-evaluation.md`, local speech contracts and media ticket |
| WhatsApp | Voice/channel plan, identity/jobs decisions, chosen provider's current official docs |
| Clinic | Product/data/task design and selected clinic ticket; no existing clinic module to assume |
| Kitchen/inventory | `service.py`, `store.py`, `catalog.py`, `skills/kitchen/SKILL.md` and workflow tests |
| Deployment | `docs/operations-runbook.md`, `deploy/gcp/`, relevant Docker/Cloud Build config and current release evidence |

Source basenames above are under `home_agent/` unless another path is specified. Avoid loading all history/docs into every task; read the relevant bundle and current source.

## What a good handoff response contains

The selected ticket and scope, concrete files changed, actual commands/results, live versus mocked evidence, any deployment IDs, remaining uncertainty and a precise next step. “Everything works” without evidence or “continue from here” without paths is insufficient. Use the [session template](../templates/session-handoff.md).
