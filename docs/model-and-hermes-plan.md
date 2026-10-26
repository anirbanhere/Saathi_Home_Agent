# Models, runtime interchangeability and Hermes

## Present implementation

`FreeModelAgent` calls OpenRouter's chat-completions interface with validated function schemas. It accepts free routes only and is further gated by the authenticated model catalogue: zero input/output price, `:free` identifier, tools/tool_choice support and key permissions. Last live tests permitted only Gemma 4 26B and received429; catalogue inclusion is not evidence of working inference.

The local `MusePlanner` is a separate adapter, not a connected hosted Meta model. The stdio MCP household server and `integrations/hermes-public-browser/` plugin are prepared and tested at protocol/handler level. None proves an actual Hermes session. Do not describe the existing loop as Hermes.

Nous's eight candidate free models were catalogued, but the human then chose **skip**. Do not add a Nous key request, account signup, paid access, x402 transaction or required migration to this plan. Reconsider only if explicitly reopened.

## Proposed provider-neutral interface

Keep the deterministic domain/tool policy independent of SDK/runtime. Introduce a narrow adapter seam around existing planning code rather than a wholesale framework rewrite.

```text
ModelProfile:
  provider_id, model_id, endpoint_profile, capabilities,
  free_only_policy, request/token budgets, timeout, policy_version

AgentInput:
  task_id/version, requested_locale, scoped messages,
  allowed tool schemas, bounded observations, remaining budget

AgentOutput:
  reply | clarification | validated tool-call proposals,
  provider/model identity, usage, latency, normalized failure
```

These are proposed internal types, not current exported classes. The application injects principal/task context. Model output cannot choose account identity, approvals or arbitrary endpoints. Credentials come from the provider-specific server configuration and must never be sent to another provider's endpoint. Endpoint profiles should be fixed/validated; replacing a model ID is not enough to switch providers safely.

Provider selection must be a user/operator policy choice. A failure may allow switching to another permitted free choice, but not paid fallback or guardrail relaxation. Maintain task identity, observations, approved payload and operation state across changes. Do not replay already committed actions when retrying reasoning. A larger context window or declared tool support is not a substitute for measured task success.

## Model acceptance protocol

1. Verify current account permissions, actual zero prices and required parameters before inference. Save provider/model/version/date metadata without credentials.
2. Use a fresh synthetic workspace. Test an actual `inventory_list` tool call, application observation and grounded final reply. Plain “hello” does not verify tool execution.
3. Test required clarification for missing journey date and account/recipient identifiers. Reject fabricated values rather than passing model guesses to a provider.
4. Test one research task that reads a supported official page, then finishes with a matching quote and source. A blocked source must hand off.
5. Test malformed/disallowed tool calls, prompt injection in observed pages, capacity errors and bounded retries.
6. Test Tamil/Malayalam/Kannada/Hindi/English task interpretation and critical-field preservation using the evaluation plan. Native review remains necessary; model-written fluency claims are not scores.
7. Record cold/warm latency, provider requests per successful task and actual usage/cost fields. Only then select the demo default.

Use model ID/provider as a test dimension, not an application branch scattered through UI/domain code. Keep the existing key-scoped catalogue behavior; unsupported entries stay out of the selectable list.

## Hermes integration sequence

The last inspected upstream source pin is `d49e2ebbaed42718659c13f82c04cde7d8ab10bd`; its supported PM-managed environment required Python 3.14 at inspection. Verify the pinned/current official source before installation; do not install an unrelated package named Hermes into the app's Python 3.12 environment. See the existing [plugin setup](../integrations/hermes-public-browser/README.md).

1. Create an isolated supported Hermes source environment, separate from the production website runtime and its secrets.
2. Enable only the restricted `saathi_public_browser` toolset for the public-research profile. Disable terminal/arbitrary-code browser/filesystem/messaging/payment tools and personal memory/context loading in this profile.
3. Use workload identity with invocation access only to the private browser worker. Keep the worker's egress/profile policy unchanged.
4. Verify actual model→registered plugin→private worker→validated observation→answer. Record runtime commit/config and allowed tools. Handler mocks are insufficient.
5. Introduce a task-state adapter between hosted tasks and the runtime; the current plugin does not synchronize hosted visitor history by itself. Keep canonical task IDs, ownership and operation policy in the application.
6. Verify same synthetic domain workflow using the application loop and Hermes adapter before enabling a runtime selector. Model swapping and runtime swapping are different features.

If the isolated runtime is unavailable, retain the application loop and record the integration gap. Do not block direct browser, railway or kitchen utility on a framework installation.

## Meta and hackathon boundary

Meta access is deferred. When credentials and event requirements are available, verify the current official endpoint, model IDs, tool parameters and access terms, then add a tested adapter through the same contract. Do not infer that a model branded Muse in an old example is currently available or that the demo satisfies event rules. A truthful submission records which actual calls used Meta, which used OpenRouter, and which were fixtures/simulations.
