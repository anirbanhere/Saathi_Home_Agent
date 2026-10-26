# Shared model adapters and observed availability

Implemented: 27 October 2026. Tickets: MODEL-02 and the request-observation slice of MODEL-03. MODEL-01's fresh synthetic production attempt still returned 429; no new live inference acceptance is claimed.

## Completion boundary

`home_agent/model_adapters.py` defines:

| Type | Implemented fields / behavior |
| --- | --- |
| `ModelProfile` | Provider ID and requested model ID; no credential or household context |
| `CompletionRequest` | Messages, allowed tool schemas, `auto`/`none` choice, bounded output-token budget |
| `CompletionResult` | Normalized assistant message/tool calls, reported model ID, whitelisted numeric usage, elapsed milliseconds |
| `CompletionAdapter` | Structural interface: profile plus `complete(request)` |
| `OpenRouterAdapter` | Fixed OpenRouter endpoint, free-model guard, supported-parameter routing, `max_tokens` payload |
| `MetaAdapter` | Existing explicitly configured local Meta route, endpoint/credential checks, `max_completion_tokens` payload; live access remains unverified |

Ordinary hosted conversation, research steps and the local Meta planner now use this shared boundary. Allowed tool arguments, task ownership, stock commits, approvals, request IDs and saved results remain application responsibilities. Hosted model selection still requires the live key-permitted zero-price catalogue; injecting another provider into the free agent is rejected. There is no hosted Meta/provider selector or new key requirement.

Request payloads are copied before sending. Response normalization rejects malformed messages and oversized/invalid call structures while preserving validated tool-call data for the application policy layer. Numeric usage fields are whitelisted; raw metadata, extra provider message fields, keys and prompts are not copied into availability records. Provider credentials remain separate from the public profile.

Embedded errors in a successful HTTP response are normalized too, so an embedded429 does not become a generic malformed-output error. Transport auth/access/quota/timeout/unavailability failures receive stable sanitized codes. Raw provider error text is not surfaced. No automatic paid routing or new provider fallback is added.

## Availability API and UI

`GET /api/state` adds `integrations.model_health`, keyed only by currently permitted model IDs. Each observation includes provider/model, state, stable error code, checked-at time, duration, a user-facing message and scope. Existing state fields remain unchanged.

States: `unobserved`, `responding`, `rate_limited`, `auth_error`, `permission_denied`, `invalid_response`, `unavailable`, `stale`. The last observation becomes stale after five minutes by default. Storage is bounded to 64 profiles and protected for concurrent application threads. It is process-local, resets with an instance/revision and is not a persistent uptime history or distributed budget.

A valid model response means only that the request responded. It does not prove a task succeeded, language quality is acceptable, or the next provider request will work. A verified tool result can remain saved while a later model follow-up fails. Requests that fail the catalogue/app budget before contacting the adapter do not manufacture a provider observation.

Connections and the conversation banner display the last observed result separately from configured key access. A failed conversation refreshes state so its capacity result becomes visible. **Refresh connection status performs no inference probe**; it reads current catalogue/observations. Normal catalogue refresh may make its existing authenticated discovery request. Choosing another model displays that profile's observation without starting a completion.

## Verification scope

97 unit/API tests pass: 80 existing plus 17 adapter/health/workflow tests. New coverage includes common OpenRouter/Meta contracts, guarded endpoint/credential separation, malformed and embedded errors, sanitized transport classes, cached-message replay, cross-provider rejection, retained tool results after follow-up outage, bounded/expired profile observations, no active inference probes on state reads and research evidence retention.

Meta evidence uses a synthetic transport. Actual Meta/Hermes/voice integration remains unverified. See HANDOFF.md for final deployment/build/UI/CI evidence; the release's browser worker and provider secrets must remain unchanged.

## Remaining work

Full task/runtime swapping, provider selection UI, durable metrics/budgets, distributed health, provider-specific Retry-After/backoff and successful live free-model acceptance remain separate work. This change establishes a tested seam and honest request-state reporting rather than a new model service.

Protocol references: [OpenRouter request/response format](https://openrouter.ai/docs/api_reference/overview), [OpenRouter embedded errors and status handling](https://openrouter.ai/docs/api_reference/errors-and-debugging). These support protocol decisions; they are not evidence of account availability.
