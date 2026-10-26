# Home Agent

Current product design: [WhatsApp voice and interchangeable models on GCP](docs/home-agents-redesign.md), with an [ordered delivery plan](tasks/voice-first-plan.md). These describe the next architecture; the runnable prototype below retains its current behavior.

Public website: **https://home-agents-xswei7prnq-uc.a.run.app**. Deployment project: [`sathi-home-agent` in `us-central1`](docs/gcp-setup.md). See the deployment record for actual tool checks and current free-provider availability.

A household-agent prototype with a hosted Python website and a separate offline local console. The hosted version supports live OpenRouter free-model reasoning, validated tool calls, private per-visitor persistence, kitchen workflows and explicit sandbox approvals. Actual inference depends on provider availability and account guardrails.

## Hosted application and AI-assisted maintenance

See [hosted deployment](docs/hosted-deployment.md) for the website runtime, deployment record, persistence limits and rollback. Hosted dependencies are in `requirements-hosted.txt`; the local console below remains dependency-free. Neither version currently connects WhatsApp, external clinic booking, real payment/ticket providers, or hosted speech.

Coding agents start with [AGENTS.md](AGENTS.md) and [HANDOFF.md](HANDOFF.md). [SOUL.md](SOUL.md) describes product behavior; [MEMORY.md](MEMORY.md) holds stable development decisions. Domain engineering guides live in `skills/*/SKILL.md`, and GitHub CI runs the tests without production credentials. These Markdown files support development context; they are not automatically loaded as runtime personal memory.

## Run

Requires Python 3.11 or newer. The application has **no third-party Python or JavaScript runtime dependencies**.

```powershell
cd "C:\Users\anirban\Documents\ChatGPT\Home Agent"
python -m home_agent
```

Open http://127.0.0.1:8765. Stop with Ctrl+C. State is stored in `data/home-agent.sqlite3` and survives restarts.

For a separate clean demo without deleting existing data:

```powershell
python -m home_agent --port 8766 --db data/rehearsal.sqlite3
```

## What works now

- Responsive browser console with conversation, kitchen, task history, and explicit connection status.
- A small offline phrase router and templates for the four requested languages. Dates and train/account identifiers are validated. Follow-ups retain missing fields and requests are deduplicated by message reference.
- Train fixtures for 12627, 12623, and 12658; unknown trains fail honestly. **None are live train positions.**
- Electricity bill and journey-booking simulators. An owner reviews a task, explicitly approves it, and receives a `SANDBOX-` reference. Concurrent/repeated approval executes once.
- Grocery CSV ingestion, g/kg and ml/l normalization, bill deduplication, stock correction, and an append-only inventory event history.
- Three curated recipes: tomato rice, simple dal, and vegetable upma. Serving counts and chilli reduction affect ingredient requirements. Cooking plans and suggestions do not deduct stock. Marking a meal cooked deducts estimated usage atomically and once; insufficient stock prevents partial deductions.
- Optional direct Meta Muse adapter with validated tool calls. It requires your API key and has not been tested against a live Meta account.
- A stdio MCP server exposes the same tools to Hermes with a fixed owner/cook role. No approval, payment execution, or inventory mutation tools are exposed to the model. The server has protocol and tool tests; an actual Hermes session has not yet been paired.
- Optional JSON speech-service adapters and audio-file input. They require a separately running Indic ASR/TTS service. No speech weights are downloaded or bundled.

## Try it

1. Select Tamil, Malayalam, Kannada, or Hindi and use a conversation starter. You can also enter `train 12627 2026-11-01` or `pay electricity bill DEMO-1042`.
2. Review the bill task. Approve the sandbox action, then inspect its source, reference, and history.
3. In Kitchen, add the example grocery text. Submit the same reference twice; stock increases once.
4. Create a cooking plan for two people with less chilli. Inspect ingredients, then mark cooked and check the inventory event history.
5. In Activity, create and approve or cancel a sandbox journey.

Offline mode is deliberately narrow. It does not understand arbitrary vernacular requests. Recipe instructions are currently English, with localized introductory/status templates. No fluent-speaker review or speech benchmark has been performed.

## Verify

```powershell
python -m unittest discover -s tests -v
python -m evals.run
python -m compileall -q home_agent
node --check web/app.js
```

Node is needed only for the optional JavaScript syntax check. HTTP integration tests use temporary loopback servers and may need network-sandbox permission in an agent runner. Test databases are isolated under the ignored `data/test-temp/` directory.

## Connect the models

See [docs/integrations.md](docs/integrations.md) for direct Muse setup, Hermes MCP configuration, the WhatsApp path, and Indic speech endpoint contracts. `.env.example` is a reference; the program reads process environment variables and does not automatically load `.env` files.

## Demo boundaries

This is a **single-owner, loopback-only demo**, not a public server or a multi-user authentication system. The browser console is trusted as the local owner; the configured MCP role is the server's authority. Do not expose port 8765 through a public tunnel. Browser requests are protected against cross-origin writes and unexpected Host headers, but local processes remain trusted.

WhatsApp messaging, YouTube/video understanding, grocery-image OCR, live railway information, real bookings/payments, and actual Indic inference are **not connected**. The UI labels these boundaries. Synthetic evaluation results measure the offline phrase router only.

No accounts were paired and no messages were sent to your cook or other contacts. No credentials are included in the repository.

## Project map

```text
home_agent/     SQLite workflows, HTTP server, Muse/speech adapters, MCP server
web/            Browser console (HTML, CSS, JavaScript)
tests/          Workflow, provider-contract, HTTP and markup tests
evals/          Four-language offline phrase-routing evaluation
docs/           Architecture, integration instructions, demo script, limitations
tasks/          Original plan and implementation status
data/           Generated local databases/results, ignored by Git
```
