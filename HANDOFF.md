# Home Agents development handoff

Updated: 26 October 2026, Asia/Kolkata. Branch:`codex/home-agent-demo`. Source baseline before this documentation delivery:`6f4eb4a`.

## Latest human objective

Write a detailed development documentation pack in the existing repository so Claude can continue: roadmap, sprint plan, architecture, engineering contracts and context/handoff. This is a documentation-only change; no app redeployment or new external integration is requested.

## Entry points

- [CLAUDE.md](CLAUDE.md): short coding-agent entry point.
- [Documentation index](docs/README.md): current versus historical authority map.
- [Current state](docs/current-state.md): implemented/deployed/live/unverified matrix.
- [Roadmap](docs/roadmap.md), [sprints](docs/sprint-plan.md), [backlog](docs/backlog.md): proposed delivery work and acceptance.
- [Claude starter prompt](docs/handoff/CLAUDE_START_HERE.md): copyable next task and context bundles.
- [Operations](docs/operations-runbook.md): deployment, IAM, secret references, recovery and cost boundaries.

## Current release

Public URL:`https://home-agents-xswei7prnq-uc.a.run.app`. Canonical repo:`https://github.com/anirbanhere/Saathi_Home_Agent`; preserve public visibility and `previous-origin` historical remote.

- Website:`home-agents-00007-r6f`, build`7f41ad49-a6a6-40d7-a9a4-7c91844f7b8a`; previous verified rollback:`home-agents-00006-x47`.
- Private worker:`home-agents-browser-00001-w2m`, build`0604bf8b-5c08-4f48-84d5-a2b4d8f5f07f`; no mounted provider secrets/project-data roles; website runtime has service-scoped invocation.
- Real public Chromium inspection/form actions, source persistence/retry, RailRadar direct lookup and kitchen/stock tools have dated verification. Checkout drafts require manual provider completion; bill/journey approvals are sandbox only.
- Last live OpenRouter inference returned 429; only Gemma 4 26B was key-permitted. A complete actual model-to-tool/browser-answer journey remains unverified. No paid fallback or guardrail change.
- Hermes MCP/plugin preparation is tested, but actual runtime/state integration is not connected. Meta, hosted ASR/TTS, WhatsApp, clinic and real financial actions remain unconnected.
- Existing implementation evidence: 80 tests and [passing CI](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40358466068), source `4644463f9a5648b7a59727a8e877f4a239690069`; prior browser dependency audit clean at that date.

## Important latest decision

The human explicitly chose **skip** for Nous credential setup/model testing. Eight free/tool-capable models were catalogued, but actual tests/provider wiring did not happen. Do not ask for a Nous key again, initiate signup/payment or require it for the roadmap unless the human reopens it. Existing OpenRouter remains the configured inference provider.

## This documentation delivery

The pack covers product/current state, deployed/target architecture, data/operation design, HTTP/tools, model/Hermes seams, voice/WhatsApp, phased roadmap, three demo sprints and later two-week planning buckets, 34 scoped backlog tickets, testing, security/privacy, operations, risks and reusable task/sprint/session templates. README is corrected to distinguish hosted/local/static editions. Detailed previous handoff is preserved in [history](docs/history/2026-10-26-pre-documentation-handoff.md).

Local verification: 54 Markdown files checked; no broken relative links/unbalanced fences; all 34 unique ticket IDs and references consistent; documented source/test/config paths resolved; credential scan of all 33 changed files found zero matches. Existing regression suite rerun with synthetic provider environment: 80 passed; JavaScript syntax and `git diff --check` passed. The documented hosted test-client example passed with the documented writable-temp workaround; all four JSON examples parsed. Changes are Markdown only. No runtime source, cloud configuration, account settings or deployed revision changed.

Published documentation commit: `315ca6565ad1d8d9a784e813c670aed9d999393a` on canonical `main`; [documentation CI passed](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40367095065). This final handoff-evidence update is a subsequent documentation-only commit. `DOC-01` is complete; remaining product tickets are still proposed/unstarted unless later evidence says otherwise.

## Next development session

Start `MODEL-01` with a fresh synthetic workspace, existing key-permitted catalogue and bounded actual tool attempt. If external capacity blocks it, record the normalized error and choose `QA-01` or a narrow `MODEL-02` contract slice; do not repeat provider polling or claim mocked inference is live. Continue subsequent tickets by prerequisites, not by implementing the whole roadmap at once. Account/channel/financial gates remain explicit.
