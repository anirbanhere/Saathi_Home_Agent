# Developer task handoff — copy per developer and ticket

Copy this to `docs/handoff/devN-TICKET-ID.md` on the developer's own branch. Replace placeholders; do not overwrite another developer's note. Coordinator summarizes integrated work in root HANDOFF.md.

## Identity and scope

- Human developer / slot / coding tool:
- Coordinator / reviewer:
- Ticket / slice / acceptance outcome:
- Updated time and timezone:
- Checkout / branch / base commit / current commit:
- Working tree: clean, or exact intended uncommitted paths:
- Allowed paths / actual changed paths:
- Recorded publication/cloud/live-provider authorization (no credentials):

## Dependencies and interfaces

- Required merged PRs / commits:
- Agreed contract path/version and accepting owner:
- Inputs/outputs, error states and ownership/replay invariants affected:
- Shared files requiring coordination / agreed merge order:
- Proposed decisions still awaiting acceptance:

## Completed work and evidence

- Problem and resulting behavior:
- Exact verification commands and outcomes:
- Relevant failure, duplicate, ownership and recovery cases:
- Actual browser/device dimensions and console findings, if UI changed:
- Synthetic/mock evidence versus actual external provider evidence:
- Redacted evidence paths (no recordings/private payloads in Git):
- PR URL / reviewed head / CI URL and status, when available:

## Remaining work and next action

- Acceptance criteria still unmet:
- Blocker, normalized error, affected source and owner:
- Independent work that can continue:
- Exact next file/command/check:
- Scope changes or human decisions still needed:

## Integration notes for coordinator

- Files/PRs likely to conflict and intended resolution:
- Root HANDOFF/backlog/workboard/MEMORY updates to summarize at merge:
- Dependencies/schema/config changed; migration or rollback implications:
- Deployment: none, or authorized build/revision/rollback and verified scope:
- Public capability wording that must remain limited:

No keys, cookies, raw household messages, private account details, voice recordings or databases belong here. “Tests pass” needs the actual command, result and commit; “deployed” needs the verified build/revision. A blocked live provider is not proof that a feature works.
