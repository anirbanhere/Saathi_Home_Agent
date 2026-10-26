---
name: home-agents-task-execution
description: Maintain everyday-task tools, approval boundaries, task state and provider-backed execution in Home Agents.
---

# Task execution

Read `AGENTS.md`, `HANDOFF.md`, and the relevant tests first. Use `home_agent/service.py`, `contracts.py`, `agent_loop.py`, and `hosted.py` as the implementation map.

Collect exact required fields. Present a specific proposed action and make approval separate from interpretation/selection. Only application-authorized paths commit an action. Reject model-supplied approval flags. Record observations, references, status and idempotency. Check provider status before retrying an uncertain irreversible operation.

Bill and journey tools remain sandbox simulations. Train running reports use the configured RailRadar adapter in production; local development defaults to fixtures. Preserve source, requested journey start date, provider update and retrieval times. Reject mismatched records; never label stale/estimated data live or use fixtures after provider failure. The owned clinic-calendar workflow remains planned.

Verify duplicates, changed inputs, stale/mismatched authorization, cross-visitor access, provider failures and restart recovery. Automated live model tests use fresh synthetic-only state. This skill describes engineering practice and does not grant new tool permissions.
