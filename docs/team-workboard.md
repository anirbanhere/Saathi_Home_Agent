# Four-developer coordination workboard

**Current coordinator scope,28 October2026:** the human directly assigned Section14 Phase0/1 of the replacement root PRD.md to this coordinator session, on `codex/saathi-phase01`. Owned additive paths: `saathi/`, `saathi_web/`, `saathi_tests/`, config/migrations/requirements/CI and transition docs. [Implementation report](saathi-phase01-report.md). Other four developer slots remain unassigned; the proposed old lanes below must be re-planned against this PRD before coding. No parallel contributor was silently assigned or contacted.

Created27 October2026. **Coordinator: project owner, unless the humans name a replacement. No developer/task reservation is active yet.** The rows below are a suggested initial split for four developer/Claude pairs. Replace slot labels with actual names and confirm scope before coding.

Coordinator is the primary writer of this file and aggregate root context/status. Developers own their ticket-specific handoffs and feature branches. Each developer can review another lane, with the coordinator resolving cross-lane dependencies. This document is not a lock service or repository permission control.

## Suggested first allocation

| Slot | Proposed slice | Proposed owned paths | First concrete output | Status |
| --- | --- | --- | --- | --- |
| Dev1 | VOICE-01: bounded open-weight Indic speech evaluation | Task-specific evaluation scripts/report; exact new paths agreed before creation. Existing speech adapter changes require separate contract agreement | Exact licences/versions/hardware bounds, permitted synthetic samples and measured transcript/critical-field evidence for one initial path | Proposed; unassigned |
| Dev2 | WA-01: current official channel preflight | A ticket-specific channel report and handoff; no runtime/channel code in this first slice | Supported route/voice/media/group constraints, setup gaps and a Proposed decision. No account pairing or messages | Proposed; unassigned |
| Dev3 | FOUND-01: local storage decision/migration design | Ticket-specific schema/decision draft and synthetic fixture rehearsal, after coordinator agrees scope | Current-to-target ownership/schema mapping and reversible local rehearsal plan. No provisioned DB or production migration | Proposed; unassigned |
| Dev4 | QA-01 / DEMO-01 bounded rehearsal slice | Task-specific regression/rehearsal evidence; proposed new tests agreed before creation | Reproduce current suite/edition boundaries and rehearse current website with synthetic data. Event/Meta requirements must be verified before eligibility claims | Proposed; unassigned |

These slices can start with investigation/evaluation without implementing dependent public speech, WhatsApp or clinic features. FOUND-01's target-store choice must be accepted before a real migration; VOICE-02/public uploads still depend on speech and media/ownership gates. Do not silently assign the same shared source file to several lanes.

## Confirmed assignments — coordinator fills before implementation

| Slot / human | Ticket and exact slice | Branch / base commit | Allowed paths / primary writer | Reviewer | Dependencies / accepted contract | Task handoff path | Status / updated time |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Dev1 / TBD | TBD | TBD | TBD | TBD | TBD | TBD | Unassigned |
| Dev2 / TBD | TBD | TBD | TBD | TBD | TBD | TBD | Unassigned |
| Dev3 / TBD | TBD | TBD | TBD | TBD | TBD | TBD | Unassigned |
| Dev4 / TBD | TBD | TBD | TBD | TBD | TBD | TBD | Unassigned |

Statuses: Unassigned → Assigned → In progress → Ready for review → Merged → Deployed (runtime changes only). Blocked records the dependency and useful independent work. Do not mark a ticket complete merely because one narrower slice merged; link remaining acceptance gaps.

Record a timestamp with timezone and PR/head commit at review. Reassignments require explicit coordinator confirmation; an old local snapshot or absence of a PR does not prove a slot is free. If two claims collide, preserve both branches and resolve ownership before more overlapping edits.

## Integration queue — coordinator maintains

| Order | Ticket / PR / head commit | Prerequisite PRs/contracts | Test/runtime evidence | Review disposition | Merged commit / deployment |
| --- | --- | --- | --- | --- | --- |
| 1 | PRD Phase0/1 · [PR1](https://github.com/anirbanhere/Saathi_Home_Agent/pull/1) | Replacement PRD Section14; standalone additive reference | Runtime `cf9bff1`:53 new +97 legacy checks, PostgreSQL/Redis and container smoke; see report/HANDOFF | Published for independent review; reviewer not assigned | Not merged or deployed |

## Coordination rhythm

- At session start: developer verifies assigned row, branch/base and dependencies; coordinator confirms conflicts/reassignments.
- Before changing a shared interface: publish the proposed contract through the team's authorized coordination channel; coordinator/relevant owners agree a primary writer and merge order.
- At each useful checkpoint/end: developer updates their own task handoff with evidence and next action, then reports through a channel the human authorized. Do not send messages automatically just because this guide mentions reporting.
- Before merge/release: coordinator checks actual PR head/CI, integrates serially, updates shared state and follows the deployment runbook when necessary.

See [development initialization](../DEVELOPMENT_START.md) for setup, review criteria and a copyable agent prompt.
