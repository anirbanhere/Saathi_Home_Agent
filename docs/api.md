# Local HTTP API

Base URL: `http://127.0.0.1:8765`. This is the trusted local-owner interface, not a public API. Hermes uses the separate stdio MCP interface.

POST requests require `Content-Type: application/json` and `X-Home-Agent: local-console`. Origin, if present, must match the local host; Host must match localhost/127.0.0.1 and the bound port. The server does not enable cross-origin requests. JSON bodies are capped at 8 MB.

| Method | Path | Body / purpose |
| --- | --- | --- |
| GET | `/api/health` | Local server liveness |
| GET | `/api/state?session=demo` | Bounded bootstrap snapshot: 50 recent tasks, 40 session messages, 30 inventory events, stock, recipes and non-secret configuration flags |
| POST | `/api/messages` | `text`, optional `language`, `session`, `request_id`, `engine` (`offline` or `muse`) |
| POST | `/api/tools` | `name` and `arguments`; see home_agent/contracts.py |
| POST | `/api/tasks/{id}/approval` | `{}`; local human approval of a sandbox bill/booking |
| POST | `/api/tasks/{id}/cancellation` | `{}`; cancel a pending task |
| POST | `/api/tasks/{id}/completion` | `{}`; record a planned recipe as actually cooked and deduct estimated ingredients |
| POST | `/api/receipts` | `reference` and `text` containing `item,quantity,unit` CSV lines |
| POST | `/api/inventory/corrections` | `name`, `quantity`, `unit`, `reference`; set a corrected absolute balance |
| POST | `/api/speech/transcriptions` | `audio_base64`, `mime_type`, `language`; requires configured ASR service |
| POST | `/api/speech/syntheses` | `text`, `language`; requires configured TTS service |

All times are UTC ISO timestamps; the offline dialogue resolves today/tomorrow using Asia/Kolkata. Dates supplied to tools use YYYY-MM-DD. Hindi `kal` is intentionally not assigned a date automatically.

Errors have the consistent form `{"error":{"code":"VALIDATION_ERROR","message":"..."}}`. Validation uses 422, missing resources 404, forbidden operations 403, state/replay conflicts 409, missing integration configuration 503 and upstream failures 502. Internal stack traces are not returned to clients.

Task states are `needs_input`, `awaiting_approval`, `planned`, `succeeded`, `failed`, and `cancelled`. No live provider has been integrated, so the prototype does not yet implement uncertain external transaction reconciliation.

The bootstrap snapshot is bounded, not a paginated historical export. All task records remain in SQLite. Add a paginated history API before expanding beyond this local demo.

Money is integer paise. Inventory quantities normalize to g, ml or pcs; decimal pieces can represent partially used ingredients. Recipe amounts and consumption remain estimates. A repeated message, receipt or correction reference with different content fails rather than silently overwriting a prior operation.
