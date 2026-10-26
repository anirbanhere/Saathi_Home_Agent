# MODEL-02 / MODEL-03: shared completion boundary and observed availability

Date: 27 October 2026. Authorized by the human's request to continue development.

MODEL-01 was retried once through a fresh synthetic hosted workspace: the key-permitted Gemma4 26B route returned429. Do not poll repeatedly or reopen Nous onboarding. Continue the independent adapter/recovery slice.

## This slice

- Introduce a small typed completion request/result and provider profile, with separate OpenRouter-free and existing local Meta adapters. Share response normalization; retain application tool/ownership/approval rules.
- Route ordinary planning, research and the local Meta planner through that boundary. Preserve current HTTP contracts, prompt scopes, budgets, duplicate handling and free/key-permitted gates. No new provider credentials or paid fallback.
- Record only provider/model, request outcome/code, timestamp and duration in a bounded process-local availability cache. GET state performs no inference probes. Expired observations become stale, and a response never certifies a tool/task outcome.
- Show this distinction in Connections and the conversation status, including rate-limit recovery. Preserve useful direct tools during outages.

## Verification

Failing contract/availability tests first; then existing unit/API suite, syntax checks, actual browser UI and one bounded synthetic deployed request. Verify malformed/provider errors, credentials/endpoints, stale availability, no prompt/key retention, replay safety and Meta mock status. Keep real Meta/Hermes/voice claims unverified. Deploy only after tests, review, separate upload-manifest/credential-scan verification, then record revisions and GitHub CI.
