# Testing and evaluation strategy

## Baseline and interpretation

The implementation checkpoint has 97 unit/API tests (80 prior plus 17 adapter/health/workflow cases) and JavaScript syntax/compile checks. CI uses synthetic/mocked external services and no production secrets. Actual public-browser and railway checks are separately recorded. Last real OpenRouter inference returned 429. An offline phrase score, a language dropdown, a handler mock or a declared model capability cannot establish live voice/agent task success.

```text
python -m pip install -r requirements-hosted.txt
python -m unittest discover -s tests -v
node --check web/app.js
python -m compileall -q home_agent
```

Use fixtures/clean process environment for the suite. Do not load production keys from `.env`. The existing offline evaluation command `python -m evals.run` writes `data/evaluation-results.json` **and regenerates** `docs/evaluation-results.md`; run it deliberately and review that tracked-file change. It evaluates 40 narrow text-template cases, not general Indic speech or LLM comprehension.

## Existing automated coverage map

| Area | Existing tests | Behaviors to preserve |
| --- | --- | --- |
| Domain workflows | `test_workflows.py`, `test_checkout_handoff.py` | Repeat approval/meal/import/correction, stock conservation, role limits, no draft execution |
| Hosted boundary/state | `test_hosted.py`, `test_cloud_state.py` | Cookie/origin/isolation, CAS conflicts, persistence, malformed requests |
| Shared model adapters / request observations | `test_model_adapters.py`, `test_model_adapter_workflows.py`, `test_model_health.py`, `test_hosted_model_health.py` | Provider contract equivalence, replay/recovery, sanitized failures, stale/bounded observations and no inference probes on state reads |
| Model/catalogue | `test_agent_loop.py`, `test_model_catalog.py` | Tool observations, bounds, permitted zero-price choices, forbidden actions, provider errors |
| Public research | `test_browser_research.py`, `test_browser_hosted.py` | Versions, duplicates, cancellation, retained pages, matching quotes, blocked evidence, six-step budget |
| Worker/policy | `test_browser_policy.py`, `test_browser_worker.py` | Private/credential URL rejection, pinned outbound IP, prohibited code/actions |
| Railway | `test_trains.py` | Identity/date/freshness, stale/estimated labels, bounded provider behavior |
| Local/adapters/UI | `test_http.py`, `test_integrations.py`, `test_ui_markup.py` | Local HTTP boundaries, optional adapter schemas, markup constraints |
| Hermes bridge | `test_hermes_browser_plugin.py` | Restricted registration and handler validation; not actual runtime inference |

## New-feature acceptance matrix

| Layer | Minimum meaningful cases | Evidence required |
| --- | --- | --- |
| Identity | Cross-user/household IDs, revoked role, forged sender, workspace claim | Application-boundary denial, not only helper mocks |
| Inbox/jobs/outbox | Duplicate/out-of-order delivery, expired lease, crash, uncertain send | Restart/concurrency tests and actual controlled delivery when connected |
| Owned clinic | Slot search, two-user contention, stale/changed/expired approval, duplicate booking, cancel/reminder | Atomic unique booking invariant and persisted references |
| ASR/TTS | Real codec input, wrong MIME/size/duration, noise, timeout, TTS failure | Actual recordings/transcripts/audio plus field/task review |
| Models | Actual function call, tool observation, final grounding, clarification, forbidden tool | Real authorized free-provider trace with synthetic state |
| Research | Supported site/form, blocked/login/error source, prompt injection, invalid quote | Real Chromium observation plus bounded policy tests |
| Media | Cross-owner access, expiry/deletion, revoked reference, oversize | Storage/HTTP boundary tests with private synthetic media |
| Inventory/extraction | Duplicate reference, unit uncertainty, partial failure, correction/reversal | Reviewed draft→one import→one meal deduction; exact balances/events |
| Transactions later | Lost response after commit, status lookup, stale approval, replay, provider refusal | Provider-specific sandbox and reconciliation proof before activation |

## Four-language evaluation protocol

Collect 10 permissioned tasks each in Tamil/Malayalam/Kannada/Hindi plus 5 English. Include straightforward requests, code switching, spoken identifiers/quantities, relative/ambiguous dates, place/person names, noise and an unsupported task. Keep human reference transcripts and expected critical fields; have a speaker review responses. Do not publish identifiable samples by default.

For each case record test ID, locale, audio reference/consent, human reference, ASR hypothesis, extracted critical fields, clarification path, tool arguments, confirmed details, actual result/source/receipt, response language/quality and phase durations. Separate transcript error, critical-field exact match, correct clarification, task success and unintended-action rate. Do not merge all locales into one flattering score.

Proposed early target: at least 8/10 correct tool outcomes per Indian language; **every actually executed action must match the exact details the human confirmed**. This is an acceptance target, not existing measured performance. A safe clarification can be successful behavior for an ambiguous sample; annotate expected outcome before running it.

## Live smoke-test procedure

1. Use a fresh synthetic-only workspace/database. Do not transmit the real household history to a provider during automated testing.
2. Verify configured provider permissions/price/profile; retain no credential in artifacts.
3. Exercise one representative path and one useful failure path. For train reports record source/update/retrieval/mode, not an assertion that a train is always at the same station.
4. For browser tests assert the actual expected content/result structure. Public pages change: do not rely solely on titles, language-specific banners or a test site's continued availability.
5. Save date/time, source commit, model/runtime ID, tool/operation IDs, outcome and redacted trace. Distinguish source observation time from source data freshness.
6. For UI work inspect DOM, network/console errors, keyboard behavior and narrow/desktop layouts in a real browser. Record actual viewport dimensions.
7. Mark unsupported/blocked capacity honestly and stop bounded retries; do not fall back to paid models or fixtures silently.

## Release gates

**Public prototype update:** relevant regression checks, ownership/replay/policy cases, truthful UI labels and public smoke after an actual deployment. **Voice claim:** actual audio path and per-locale evidence. **Hermes claim:** real isolated runtime round trip. **WhatsApp claim:** actual verified ingress and approved-recipient delivery. **Beta:** deletion/revocation/restore/operational checks. **Real transactions:** independent identity/approval/operation/reconciliation/receipt acceptance and explicit authorized activation.

Documentation-only updates need relative-link/path/API-consistency and secret review; no new runtime test implementation or cloud rollout is necessary. CI may still run the existing suite on push. Report actual commands/results, not an unchecked “all tests pass.”
