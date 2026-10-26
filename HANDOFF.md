# Home Agents development handoff

Updated: 27 October 2026, Asia/Kolkata. Branch: `codex/home-agent-demo`. Runtime source checkpoint: `f72913f`.

## Latest human objective

Continue development from the documented roadmap. MODEL-01 was retried once against a fresh synthetic hosted workspace and remained blocked by actual OpenRouter 429. Independent MODEL-02 and MODEL-03 request-observation work was implemented and deployed; no new provider/key, paid inference, guardrail change or third-party message was introduced.

## Entry points

[CLAUDE.md](CLAUDE.md) → [documentation index](docs/README.md) → [current state](docs/current-state.md) / [backlog](docs/backlog.md). New implementation details: [shared model adapters and availability](docs/model-adapters.md). Deployment/recovery: [operations runbook](docs/operations-runbook.md).

## Current release and rollout

Public URL: `https://home-agents-xswei7prnq-uc.a.run.app`. Canonical public repository: `https://github.com/anirbanhere/Saathi_Home_Agent`; preserve `previous-origin` and existing visibility.

- Initial adapter/status rollout: website `home-agents-00008-hq7`, build `2670e362-67db-4588-beaf-55532d5e42fb`; previous verified revision `home-agents-00007-r6f`.
- Current ready website: `home-agents-00009-xhz`, final numeric-metadata fix build `3c7a6caf-5c61-4ee5-ae81-421b412816d6`; previous verified rollback target: `home-agents-00008-hq7`.
- Private browser remains `home-agents-browser-00001-w2m`, build `0604bf8b-5c08-4f48-84d5-a2b4d8f5f07f`, with the same dedicated identity and service-scoped invoker. It has no mounted model/railway credentials or project-data roles.
- Both production provider secret references and literal environment names were verified after the initial rollout. No secret payload was accessed or printed. Source upload manifest and credential checks were separately reviewed before each build.

## What changed

- `model_adapters.py`: typed profile/request/result and common completion interface, OpenRouter-free and existing local Meta adapters, copied request payloads, bounded normalized responses/usage, sanitized transport/embedded error codes. Caller key/model gates remain enforced; no hosted Meta selector.
- Ordinary conversation, public research and local Meta planning use the seam. Domain tool validation, cookie ownership, budgets, approval rules, stock commits and message/task replay remain application-controlled.
- `model_health.py`: bounded process-local provider/model observations, five-minute expiry and stable outcome/code/time/duration only. No prompts, raw errors, keys or user context retained; GET state is not an inference probe. A responded request is not verified task success.
- Connections/banner now distinguish configured catalogue access from last inference result. Conversation failures refresh this observation; Refresh connection status makes no completion request. Direct tools remain usable.

## Verification

- 97 tests passed: 80 existing plus 17 adapter/availability/workflow tests. New cases include common OpenRouter/Meta contracts, model/provider separation, malformed and embedded errors, bounded numeric metadata, repeat-safe messages, saved tool results after follow-up outage, stale/bounded health, no probes on state reads and retained research evidence.
- JavaScript syntax and Python compilation passed. Reproduced the oversized-usage-number overflow, then fixed it with bounded numeric validation and a regression case.
- Actual initial deployed UI: a fresh synthetic request returned429; the banner and Connections changed from unobserved to rate-limited automatically. Timestamp/normalized health were verified via public API. Refresh preserved the inference observation timestamp. The only console error was the expected HTTP429; no unexpected JavaScript errors were observed.
- Direct dal recipe plan saved/reloaded during provider outage. Public website→private browser inspection of Python.org succeeded without changing model observation time. Successful full live model/tool or model/browser-answer acceptance remains unverified.
- Final metadata-fix rollout verified: health `ok`, direct inventory succeeded, observation cache reset to `unobserved` as expected, both secret references preserved. [Release CI passed](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40396119648) for `f72913f19b5dbfdc113e4487b796c37a2fc681c7`. Meta evidence uses synthetic transport tests only; no Meta/Hermes/ASR/TTS/WhatsApp/clinic/payment capability is newly claimed.

## Stable decisions and limits

The human explicitly skipped Nous credential setup/model testing. Do not request a Nous key again or make it a prerequisite unless reopened. OpenRouter remains the configured provider; last permitted route is Gemma 4 26B free and actual capacity is unavailable. Do not substitute fixtures or paid models for failed inference.

Anonymous visitor snapshots are not shared family identity or a financial operation ledger. Checkout drafts still require manual provider completion; bills/journey receipts are sandbox only. The complete documentation pack and historical handoff remain in the repository; Markdown is engineering context, not runtime personal memory or authorization.

## Next ready work

MODEL-02's completion seam is implemented; full task/runtime/provider swapping remains future work. MODEL-03's request-observation slice is implemented; durable metrics/budgets and provider-specific backoff remain future work. MODEL-01 live success remains externally blocked; do not keep repeating the same request.

Choose an independent ready slice: QA-02 for broader research/handoff/keyboard/narrow-screen validation, or VOICE-01 for a bounded, license-verified speech benchmark using synthetic/permissioned samples and existing resource constraints. No unattended GPU provisioning, account pairing, messages to contacts or financial execution follows automatically. Preserve current website utility and recorded rollback.
