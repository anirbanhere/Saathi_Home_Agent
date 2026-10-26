# Model and messaging integrations

## Direct Meta Model API adapter

This adapter lets the local UI use Muse to select the household tools. It does **not** run Hermes. The separate MCP path below supports Hermes as the orchestrator.

Configure the environment in the same terminal that starts the server. Supply the key locally, not in chat or source control:

```powershell
$secureModelKey = Read-Host "Meta Model API key" -AsSecureString
$env:MODEL_API_KEY = [System.Net.NetworkCredential]::new('', $secureModelKey).Password
$env:META_MODEL = 'muse-spark-1.3'
python -m home_agent
```

In Connections, choose Meta Model API. A configured key is not proof of a working connection: send a request, inspect the actual tool trace, and validate multi-turn behavior. The adapter uses the documented `/v1/chat/completions` protocol with function tool schemas and bounded output. Configuration defaults to `https://api.meta.ai/v1`; `META_BASE_URL` can change it. HTTPS is required except for explicit loopback inference endpoints; redirects are rejected.

The model can create a bill/booking preview, inspect inventory, look up a fixture, and create cooking plans. It cannot approve transactions, execute real payments, or mark meals cooked. Human action in the local UI owns those transitions. If the provider is unavailable, the request fails explicitly; it never silently falls back and claims to have used Muse.

Status: boundary tests use simulated provider responses; no actual Meta credentials were available during this build.

## Hermes MCP tools

Hermes is already installed on the development machine, but its personal configuration was not changed. Add a project-specific MCP entry to your chosen Hermes profile when ready. Use the actual absolute Python executable for your installation; this machine uses `C:/Python314/python.exe`.

```yaml
mcp_servers:
  home_agent:
    command: "C:/Python314/python.exe"
    args:
      - "-u"
      - "C:/Users/anirban/Documents/ChatGPT/Home Agent/run_mcp.py"
    env:
      HOME_AGENT_DB: "C:/Users/anirban/Documents/ChatGPT/Home Agent/data/home-agent.sqlite3"
      HOME_AGENT_ROLE: "owner"
```

The absolute entry-point script works independently of Hermes's current directory. The MCP process and browser console share the same SQLite file. Choose `HOME_AGENT_ROLE: cook` for a cooking/inventory-only server; the default is cook. Configure that role in trusted server configuration, not in model-supplied arguments.

Tools: `train_status`, `bill_preview`, `booking_preview`, `recipe_plan`, `dish_suggestions`, `inventory_list`, and `task_status`. Cook-role discovery only exposes household tools plus `task_status`, which checks access before returning a task. Human approvals and inventory commits are intentionally absent from the model's tool catalog.

Then configure Hermes's custom provider using the Meta endpoint, API key, and the model available to your account. Validate actual tool discovery, follow-ups, and output language with the real provider before claiming the complete stack works.

The MCP implementation supports newline-delimited stdio JSON-RPC, initialize, notifications, ping, tools/list, and tools/call. Protocol/tool behavior is tested; it is not advertised as a complete implementation of optional MCP features.

## WhatsApp

Use Hermes's gateway after the model/tool loop is verified. This build does not pair WhatsApp accounts, start a messaging gateway, or send any external messages.

Hermes documents a personal Baileys bridge and an official Business Cloud adapter. The personal bridge is unofficial and may be restricted or break. The official business route has eligibility/use restrictions, and Hermes's documented Cloud adapter currently only handles direct messages. Do not promise integration into an existing cook's group until that exact path is tested.

Important: the local UI's single-owner trust model is not suitable as a public webhook. A production WhatsApp adapter must verify signatures or trusted bridge identity, map sender IDs to server-owned roles, deduplicate deliveries, and route approval to a verified owner. The current transaction approval path remains the local console.

## Indic speech adapters

No model is bundled. Run your selected Indic ASR/TTS service separately, then point the application at its JSON endpoints:

```powershell
$env:HOME_AGENT_ASR_URL = 'http://127.0.0.1:9001/transcribe'
$env:HOME_AGENT_TTS_URL = 'http://127.0.0.1:9001/synthesize'
python -m home_agent
```

These URLs are examples, not services this project has started. For hosted services use HTTPS. Optional `HOME_AGENT_SPEECH_KEY` is sent as a bearer token to the configured endpoints. Requests have a 45-second timeout. Check license/upstream terms for the exact weights you deploy.

### Transcription contract

Request: `{"audio_base64":"...","mime_type":"audio/ogg","language":"ta"}`.

Response: `{"text":"ரயில் 12627 நிலை","language":"ta"}`.

The requested language is retained in the local app. Supported language codes: `ta`, `ml`, `kn`, `hi`, `en`. Audio is capped at 5 MB. Supported input MIME types: audio/webm, audio/ogg, audio/wav, audio/mpeg, audio/mp4. Review transcribed text before sending; transcription does not automatically authorize an action.

### Synthesis contract

Request: `{"text":"...","language":"ta"}`.

Response: `{"audio_base64":"...","mime_type":"audio/wav"}`.

Audio is capped at 5 MB. Accepted output MIME types are audio/wav, audio/mpeg, audio/ogg, audio/webm. Browser playback requires a user click. Actual pronunciation, accents, code mixing, and latency remain to be evaluated against real speech models.

## Primary documentation consulted

New restricted browser bridge: [`integrations/hermes-public-browser/README.md`](../integrations/hermes-public-browser/README.md). It uses the same private browser client and policy as hosted research, without arbitrary-code tools. This plugin is prepared and handler-tested; actual Hermes orchestration remains unverified. The earlier MCP household server remains a separate local integration.

- [Hermes MCP configuration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)
- [Meta Chat Completions](https://dev.meta.ai/docs/protocols/chat-completions)
- [MCP stdio transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
- [Hermes WhatsApp](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp)
- [Hermes Cloud adapter](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud)
- [Python SQLite](https://docs.python.org/3.14/library/sqlite3.html)
- [Python HTTP server](https://docs.python.org/3.14/library/http.server.html): used for local prototyping only.
