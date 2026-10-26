# Implemented HTTP and tool reference

Baseline: `home_agent/hosted.py`, `service.py`, `contracts.py`, `research.py`. These are current interfaces, not proposed WhatsApp or account APIs. The older [api.md](api.md) describes the loopback edition.

## Hosted boundary

Base: `https://home-agents-xswei7prnq-uc.a.run.app`. JSON mutations require an initialized visitor cookie, same-origin `Origin`, `Content-Type: application/json` and `X-Home-Agent: local-console`. The custom header is a CSRF boundary component, not a standalone authentication secret. The HttpOnly/Secure/SameSite=Lax `__Host-home-agent` cookie scopes the workspace. Initial `GET /api/state` establishes it. `session` groups messages within that workspace and is not an authorization boundary.

Maximum hosted JSON body:32,000 bytes. Responses are private/no-store. Cross-origin API use is not enabled. There is no public API-key interface for arbitrary external callers, user-login route or WhatsApp webhook route yet.

| Method/path | Request fields | Result / notes |
| --- | --- | --- |
| `GET /api/health` | None | `status`, `hosted`, `free_models_only`; no visitor initialization required |
| `GET /api/state?session=demo` | Session text≤100 | Inventory, tasks, messages, recipes, events, metrics, languages, integration/catalogue state |
| `POST /api/messages` | `text`≤4000, `language`, `session`, optional `request_id`≤100, `engine`, `model` | Saved reply, task/trace, mode/model/notice; engine `openrouter` or `offline` |
| `POST /api/tools` | `name`, `arguments` object | Validated deterministic task result; allowed tools below |
| `POST /api/receipts` | CSV `text`, `reference` | Repeat-safe reviewed grocery import; not OCR |
| `POST /api/inventory/corrections` | `name`, `quantity`, `unit`, `reference` | Repeat-safe stock correction and event history |
| `POST /api/tasks/<32-hex-id>/approval` | Empty object | Owner-only sandbox bill/journey commit; rejects research, recipes and handoff drafts |
| `POST /api/tasks/<32-hex-id>/cancellation` | Empty object | Cancel eligible pending task; no real-world reversal |
| `POST /api/tasks/<32-hex-id>/completion` | Empty object | Recipe meal completion; estimated stock deduction once |
| `POST /api/browser/tasks` | `goal`≤2000, optional `url`, `mode`, `model`, `session`, `request_id` | Persisted `web_research` task, initially `planned` |
| `POST /api/browser/tasks/<32-hex-id>/steps` | Integer `version`, optional free `model` | Current/saved task after one bounded step; recoverable errors can be HTTP 200 with task `needs_input` |

No separate hosted `GET /api/tasks/<id>` is implemented; retrieve tasks through `/api/state`. No hosted `/api/speech/*` routes are implemented. Do not derive route availability merely from frontend controls or local adapter code.

27 October addition: state includes `integrations.model_health` for currently permitted model IDs. It records the most recent completion outcome/code/time/duration seen by this application process, becomes stale after five minutes and resets on restart. GET state/Refresh connection status does not initiate inference. A `responding` request observation is not verified task success. See [model adapters](model-adapters.md).

## Core task/result shape

```json
{
  "id": "32-character-hex-id",
  "kind": "web_research",
  "actor": "owner",
  "session": "demo",
  "status": "planned",
  "args": {"goal": "Inspect this page", "version": 0},
  "result": {"summary": "Prepared", "mode": "public_browser"},
  "created_at": "UTC ISO timestamp",
  "updated_at": "UTC ISO timestamp"
}
```

This is an abbreviated explanatory shape, not a complete literal response schema. Kind-specific fields are defined by source/tests; clients must not assume all tasks have receipts, amounts, recipe ingredients or research versions. A `succeeded` research task means the research/inspection operation finished; it does not mean a flight arrived or an external transaction executed.

Errors normally use `{"error":{"code":"...","message":"..."}}`. Relevant statuses:422 validation/policy;403 cross-origin/ownership/model permission;404 absent task/route;409 invalid state/conflict;429 budget/workspace/provider limit;502 provider/invalid response;503 configuration/service unavailable. Research catches many integration errors and saves them as task state with `result.last_error`; inspect task status as well as HTTP status.

## Tool arguments and effects

All deterministic tools accept optional `language` in `en`, `ta`, `ml`, `kn`, `hi`. Extra arguments are rejected. Hosted callers cannot inject an arbitrary household actor. `cook` in local/MCP policy may use inventory/recipe/suggestion tools only.

| Tool | Required / important arguments | Effect and limits |
| --- | --- | --- |
| `train_status` | `train_number`:5 digits; `date`:YYYY-MM-DD journey start from origin | Actual configured provider or explicit local fixtures; inspect mode/source/update time |
| `bill_preview` | `account`: `DEMO-...` | Sandbox bill only, pending human approval |
| `booking_preview` | `origin`, `destination`≤80, `date` | Sandbox quote; no real availability/ticket |
| `recipe_plan` | `recipe`: `tomato-rice`, `dal`, `upma`; optional integer servings1–12, boolean `less_spicy` | Saves plan, checks stock, does not consume |
| `dish_suggestions` | No additional fields | Curated inventory/history-based suggestions |
| `inventory_list` | No additional fields | Current workspace inventory |
| `checkout_handoff` | `kind`: `bill`/`food`; `merchant_url`:public homepage; `details`≤1000 | Unverified draft/manual provider handoff; cannot approve to execute |

The main model loop additionally receives `start_web_research(goal, url?)` when hosted research is injected. It queues a task and is not a direct `/api/tools` domain tool. Research model steps use `browse_public_page`, `finish_research` and `request_handoff`; these are not unrestricted public tool endpoints. Model schemas never expose approval or meal-completion authority.

Receipt CSV permits 1–100 rows, each `item,quantity,unit`; quantity must be positive. Units normalize kg→g and l→ml; pieces use `pcs`. Import reference≤100 is deduplicated with a content fingerprint. Corrections set an absolute balance while appending the corresponding event. These quantities remain estimates.

## Research examples

Start direct inspection:

```json
{"goal":"Inspect the official Python homepage","url":"https://www.python.org/","mode":"inspect","session":"demo","request_id":"new-unique-request"}
```

Send that to `/api/browser/tasks`, then use its returned task ID and `args.version` at `/steps`:

```json
{"version":0}
```

`inspect` requires a public URL and can finish without LLM inference. `agent` can start with a URL (first read is direct) or no URL (model needed to choose a source). A stale version returns current state without replaying a completed step. Terminal `succeeded`/`cancelled`/`failed` tasks do not advance. Retry recoverable failures with the current version; retries count toward six saved steps. Start request IDs must retain the same payload; changed content conflicts.

The final source-backed answer requires an inspected observed page, non-error status and matching quote. A blocked page cannot support a completed answer. Page content is not trusted instructions. Sources can be public but stale or wrong; see freshness rules and task-specific evaluation.

## Private worker contract

`GET /health` and `POST /observe` exist on the **IAM-protected** browser service. A website visitor should never call it directly. The website runtime obtains an ID token for the configured service URL.

```json
{"url":"https://www.python.org/","actions":[{"type":"fill","selector":"#id-search-field","value":"asyncio"},{"type":"click","selector":"#submit"}]}
```

Only `url` and `actions` are accepted. At most 6 actions; types `fill`, `click`, `select`; selectors≤250; values≤200. No code/evaluate, cookies, credentials, household context or API secrets. Worker JSON body≤24 KB; public URL≤2000. Observations include title/text, bounded controls/links, final URL, timestamp, HTTP status and `observed`/`needs_input`. Not all websites support this profile.

## Extension rules

New public auth/channel/media/approval APIs require explicit request/response contracts, ownership context, replay/error semantics, expiry/retention and meaningful tests. Version new external contracts rather than silently changing anonymous-console semantics. Target names in architecture/backlog are proposals, not already available routes.
