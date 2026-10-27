# Home Agents documentation

Maintained baseline: 26 October 2026, Asia/Kolkata. This documentation pack prepares another engineer or Claude session to continue the existing repository. It does not certify unfinished product features as complete.

## Read in this order

| Need | Document |
| --- | --- |
| Resume with Claude | [CLAUDE.md](../CLAUDE.md), [continuation prompt](handoff/CLAUDE_START_HERE.md) |
| Understand what actually exists | [Current state and evidence](current-state.md) |
| Understand the product | [Product requirements](product-requirements.md) |
| Understand deployed and target systems | [Architecture](architecture.md), [data/task design](data-and-task-design.md) |
| Integrate with existing code | [HTTP/tool reference](api-reference.md), [model/Hermes plan](model-and-hermes-plan.md) |
| Inspect the implemented model seam | [Shared completion adapters and observed availability](model-adapters.md) |
| Build voice/channel capability | [Voice and WhatsApp plan](voice-and-whatsapp-plan.md) |
| Choose the next work | [Roadmap](roadmap.md), [sprint plan](sprint-plan.md), [implementable backlog](backlog.md) |
| Run and change the app | [Development and Claude workflow](development-and-claude.md) |
| Verify a feature | [Testing and evaluation](testing-and-evaluation.md), [research/handoff UI evidence](qa02-usability.md) |
| Operate GCP and recover | [Operations runbook](operations-runbook.md) |
| Assess boundaries and unknowns | [Security/privacy](security-and-privacy.md), [risks/decisions](risks-and-decisions.md) |
| Maintain execution context | [HANDOFF.md](../HANDOFF.md), [MEMORY.md](../MEMORY.md), [work templates](templates/task.md) |

## Source of truth and status vocabulary

Human instructions take precedence. For implemented behavior, inspect the source and tests, then dated deployment evidence. For future direction, use the new roadmap/backlog and relevant accepted ADR. Older proposals remain useful history but cannot establish deployment status. If prose conflicts with code, verify and update the prose before building on the assumption.

- **Implemented:** source and meaningful tests exist.
- **Deployed:** a dated Cloud Run revision/build is recorded.
- **Live verified:** an actual external round trip succeeded for the stated scope.
- **Prepared/unverified:** adapter or contract exists without a verified live integration.
- **Proposed:** target design or estimated work, not a running capability.
- **Skipped/deferred:** human choice or scope cut; do not silently reactivate it.

Roadmap estimates are planning assumptions for a small team, not delivery promises. The user's October 26–November 4 event window is a planning input; official rules, required Meta usage and submission requirements must be rechecked independently before submission.

## Existing detailed references

| Existing document | Scope and relationship to this pack |
| --- | --- |
| [Hybrid implementation](hybrid-browser.md) | Deployment evidence and private-browser operations; still authoritative for that release |
| [Hosted deployment](hosted-deployment.md) | Cloud resources and historical release record |
| [Live trains](live-trains.md) | Railway provider validation/freshness and direct lookup |
| [Integrations](integrations.md) | Local Muse, MCP and speech adapter contracts; not proof of hosted connection |
| [Hybrid spec](hybrid-agent-spec.md), [hybrid plan](../tasks/hybrid-agent-plan.md) | Accepted browser feature scope and completion checkpoint |
| [Original voice redesign](home-agents-redesign.md), [voice plan](../tasks/voice-first-plan.md) | Broader product design; VM/clinic-first ordering is historical where later ADRs/plans supersede it |
| [Local HTTP API](api.md) | Loopback edition; use the new API reference for edition differences |
| [Local demo script](demo-script.md), [offline evaluation](evaluation-results.md) | Offline fixture/template evidence only |
| [Original hackathon spec](hackathon-demo-spec.md), [original task plan](../tasks/plan.md), [original checklist](../tasks/todo.md) | Historical starting scope; not the current backlog |
| [Sites deployment](sites-deployment.md) | Earlier static/browser-local edition, separate from the executable GCP app |
| [GCP setup](gcp-setup.md) | Initial target/preflight; historical API readiness may differ from later deployments |
| [Product references](product-references.md) | Inspiration, not a verified implementation description of other products |
| [Archived detailed handoff](history/2026-10-26-pre-documentation-handoff.md) | Prior implementation/deployment history; root HANDOFF.md carries current work and the later Nous skip decision |
| [ADR-001](decisions/0001-whatsapp-voice-model-independent-gcp.md), [ADR-002](decisions/0002-hosted-web-demo.md), [ADR-003](decisions/0003-isolated-public-browser.md) | Decision history; ADR-002 governs the immediate website placement and ADR-003 the isolated browser |

## Documentation maintenance

Every shipped ticket updates its acceptance evidence, any affected API/design section and HANDOFF.md. Change stable choices only in MEMORY.md/ADRs. Keep credentials and private recordings out of examples. Use [task](templates/task.md), [sprint review](templates/sprint-review.md) and [session handoff](templates/session-handoff.md) templates. Preserve historical claims with their scope/date rather than rewriting them as today's capabilities.
