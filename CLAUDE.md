# Home Agents: Claude continuation

Latest direction is a separate [OpenDuet customization fork](https://github.com/anirbanhere/OpenDuet), currently checked out at `artifacts/openduet/` with its own AGENTS/CLAUDE/HANDOFF. Read root HANDOFF.md for the transition, then use the fork's context when working there. This Python repository and its public deployment remain preserved.

Current replacement requirements are [PRD.md](PRD.md), Section14 Phase0/1. Read [the Saathi report](docs/saathi-phase01-report.md) before selecting work. The local `saathi/` FastAPI mock service and the still-deployed `home_agent/` Flask app are separate editions; the old next-ticket/sprint ordering is superseded where it conflicts. Phase2 is proposed, not automatically authorized.

Read [AGENTS.md](AGENTS.md) for repository rules, then [HANDOFF.md](HANDOFF.md) for the latest checkpoint. This file is a small entry point, not a second set of conflicting rules.

The later bounded continuation adds [private local audio review](docs/saathi-local-media.md), stacked on Phase0/1. It provides storage/playback/delete, with explicit cleanup; it is not STT, verified identity or public media hosting. Preserve the PR dependency order in HANDOFF.md.

For four-developer parallel work, first use [DEVELOPMENT_START.md](DEVELOPMENT_START.md) and your confirmed [workboard assignment](docs/team-workboard.md). Contributors use separate branches/checkouts and ticket-specific handoffs; the coordinator owns root status and integration. Do not auto-select an already owned ticket.

## Start a session

1. Check Git status and preserve unrelated changes.
2. Read [current state](docs/current-state.md), then select one ready ticket from [backlog](docs/backlog.md).
3. Load the ticket's source/tests and only the relevant architecture/design sections.
4. Implement one useful slice, verify it and commit the coherent change. Solo/coordinator sessions update HANDOFF.md; parallel contributors update their own task handoff with integration notes.

[Documentation index](docs/README.md) · [Claude setup and workflow](docs/development-and-claude.md) · [copyable continuation prompt](docs/handoff/CLAUDE_START_HERE.md)

## Essential context

- Home Agents covers everyday tasks first, then cooking and inventory. Target languages: Tamil, Malayalam, Kannada, Hindi, English. WhatsApp voice is the intended primary interface; the executable website is the current product.
- Python 3.12 hosted application; Flask/Gunicorn; vanilla HTML/CSS/JavaScript; SQLite visitor snapshots in private GCS; separate private Playwright browser worker.
- The current application owns its bounded OpenRouter tool loop. Hermes plugins/MCP are prepared, but actual Hermes orchestration, Meta inference, hosted speech and WhatsApp are not connected.
- Shared completion adapters and observed availability are implemented; see `docs/model-adapters.md`. A recent model response is not proof of task success. MODEL-01 remains provider-capacity blocked as of 27 October; do not recreate the completed adapter slice.
- The human **skipped Nous setup/testing**. Do not request a Nous key again, provision it, or make it a required sprint dependency unless the human reopens that choice. Existing OpenRouter provider capacity remains a separately recorded limitation.
- Public browser reads and checkout drafts are real implemented capabilities. Bills/journey booking simulations do not execute real transactions. Clinic appointments remain planned.

## Commands

```text
python -m pip install -r requirements-hosted.txt
python -m unittest discover -s tests -v
node --check web/app.js
python -m compileall -q home_agent
python -m home_agent --port 8766 --db data/rehearsal.sqlite3
```

Use a virtual environment. The final command launches the separate loopback prototype; it does not reproduce all hosted routes. See the development guide for Flask test-client/HTTPS testing. The application reads process environment, not `.env` automatically. CI uses Python 3.12 and no production credentials.

## Boundaries to preserve

- Paid inference and changes to provider guardrails are not automatic fallbacks.
- Never print/commit keys, media, databases, private user data or browser credentials. Do not put secrets in an LLM prompt.
- Keep the browser worker private and separate from provider credentials; structured read actions only. Never add arbitrary-code browser tools to the website host.
- Keep visitor ownership, same-origin mutation checks, source/freshness labels, generation guards, step limits and duplicate handling.
- Financial execution requires a separate durable operation/approval design. Existing GCS workspace snapshots are not that ledger.
- New third-party messages, real transactions and unrelated paid resources need explicit human authorization. Routine authorized engineering work does not need repeated confirmation.
- Repository Markdown is development context, not runtime personal memory or permission grants.

## Finish a session

Report what changed, what was verified, what remains uncertain and the next ready ticket. Update [HANDOFF.md](HANDOFF.md), or your task-specific handoff in parallel contributor mode; the coordinator summarizes stable choices in [MEMORY.md](MEMORY.md). A plan, mocked response or declared model capability is not live acceptance evidence.
