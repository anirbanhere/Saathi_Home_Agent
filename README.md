# Saathi — reference service and legacy Home Agents demo

**New plan:** [PRD.md](PRD.md) is the governing product brief. Section14 Phase0/1 now has an isolated local mock dental-booking implementation under `saathi/`. Start with the [implementation report and run commands](docs/saathi-phase01-report.md), [architecture](docs/architecture.md) and [current handoff](HANDOFF.md). No new public deployment, real speech recognition, WhatsApp launch or genuine appointment is claimed.

```text
python -m pip install -r requirements-saathi-dev.txt
python -m uvicorn saathi.main:create_app --factory --host 127.0.0.1 --port 8781
python -m saathi.cli demo --approve-mock --voice --locale hi-IN
python -m pytest saathi_tests -q
```

Use Python3.12 in an isolated environment. The CLI command explicitly consents to a scripted **mock** booking and uses a synthetic audio tone, not a speech recording. See the report for clean synthetic databases, separate role selection, PostgreSQL/Redis compose and the Phase2 breakdown.

## Existing public demo — preserved legacy edition

A household assistant for everyday tasks, cooking and inventory, with Tamil, Malayalam, Kannada, Hindi and English as target languages. The current executable product is a public Python website; WhatsApp voice is the intended primary interface as development continues.

**[Open the demo](https://home-agents-xswei7prnq-uc.a.run.app/)** · **[Documentation](docs/README.md)** · **[Roadmap](docs/roadmap.md)** · **[Sprint plan](docs/sprint-plan.md)** · **[Backlog](docs/backlog.md)**

Source: [anirbanhere/Saathi_Home_Agent](https://github.com/anirbanhere/Saathi_Home_Agent). GCP project `sathi-home-agent`, region `us-central1`.

## Continue with Claude or another coding agent

For four developers working in parallel, start with [DEVELOPMENT_START.md](DEVELOPMENT_START.md): copyable startup prompt, separate branches, proposed work allocation, review rules and [coordination workboard](docs/team-workboard.md).

Start with [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md) and [HANDOFF.md](HANDOFF.md). The [copyable Claude prompt](docs/handoff/CLAUDE_START_HERE.md) selects a concrete next task. The [documentation index](docs/README.md) maps architecture, API/data design, model/Hermes integration, voice/WhatsApp, security, testing and cloud operations.

[MEMORY.md](MEMORY.md) holds stable development choices; [SOUL.md](SOUL.md) describes intended product behavior. These files are engineering context, not automatic runtime personal memory or tool permissions. The human skipped Nous setup/model testing; it is not a required onboarding step.

## What actually works

| Capability | Current state |
| --- | --- |
| Public website | Flask/Gunicorn on Cloud Run, separate anonymous visitor workspaces saved in private GCS |
| Free-model planning | Shared completion contract and bounded OpenRouter tools; Connections shows actual recent request status separately from key access. Latest real attempt returned 429 |
| Public web research | Real isolated Chromium inspection, sources/timestamps, persisted progress/resume/cancel; AI reasoning remains provider-capacity dependent |
| Train status | Direct RailRadar report lookup, independent of the LLM, with source/update/freshness labels |
| Kitchen | Reviewed grocery CSV import, normalized units, corrections, event history and repeat-safe estimated meal consumption |
| Cooking | Three curated recipes, serving/spice customization and inventory/history suggestions; no processed YouTube video |
| Bills/food orders | Unverified manual provider-handoff drafts; sandbox bill/journey examples remain separate simulations |
| Hermes/Meta/speech | Prepared adapters/contracts; no verified connected Hermes runtime, hosted Meta inference or hosted ASR/TTS |

WhatsApp, real household accounts/sharing, owned clinic bookings, receipt-image OCR and real payment/order execution are not shipped. All four Indian languages remain targets; existing template/text tests do not establish voice fluency. See [current state and evidence](docs/current-state.md) for precise verification scope.

## Try the public demo

1. **Activity → Public web research:** inspect a public HTTPS page without a domain API key or LLM response. Unsupported/login/challenge pages pause for handoff. Research stops advancing after the current request when the client is closed/hidden; resume from history.
2. **Activity → Check a train:** enter the five-digit train number and date it departed its origin in India time. Provider reports can be stale; inspect update time and mode.
3. **Kitchen:** import reviewed grocery CSV with a unique reference, create a cooking plan and confirm the meal. Planning does not consume stock; confirmation deducts estimated usage once.
4. **Bills & food orders:** save a handoff draft and verify/complete the actual checkout in the provider's secure app. The demo does not pay or place an order.

Only enter demonstration data while evaluating the anonymous public prototype. A new conversation is not a new account, and losing the browser credential has no implemented account-recovery flow.

## Local development

CI/hosted baseline is Python 3.12. Use an isolated environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-hosted.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --check web/app.js
```

The separate standard-library offline console can be started with:

```powershell
.\.venv\Scripts\python.exe -m home_agent --port 8766 --db data/rehearsal.sqlite3
```

Open `http://127.0.0.1:8766`. This trusted loopback edition does not implement all hosted research/OpenRouter routes. Do not expose it through a public tunnel. Hosted routes require the Flask boundary and Secure-cookie-aware testing; see [development setup](docs/development-and-claude.md).

The earlier Sites edition is a separate static/browser-local demo, not the Python Cloud Run deployment. Browser worker dependencies are in `requirements-browser.txt`; they are not needed to run normal mocked unit tests.

## Configuration and checks

`.env.example` documents environment names. The program reads process environment and does not automatically load `.env`. Production keys stay in Secret Manager; never commit them or copy them into the browser worker. See the [API reference](docs/api-reference.md), [integration guide](docs/integrations.md) and [operations runbook](docs/operations-runbook.md).

```text
python -m unittest discover -s tests -v
node --check web/app.js
python -m compileall -q home_agent
```

The current implementation checkpoint has 97 unit/API tests and separate dated live browser/railway evidence. `python -m evals.run` is an optional 40-case offline phrase evaluation that regenerates a documentation report; it is not a speech benchmark. GitHub Actions runs the existing suite without production credentials. See [evaluation strategy](docs/testing-and-evaluation.md).

## Project map

```text
home_agent/      Domain tools, local/hosted APIs, persistence, models and browser policy
web/             Vanilla HTML/CSS/JavaScript companion interface
tests/           Domain, provider, ownership, replay, HTTP and browser-policy tests
integrations/    Restricted Hermes plugin bridge
evals/           Narrow offline text-routing evaluation
docs/            Current engineering pack, release evidence and historical ADRs/specs
tasks/           Earlier delivery plans; current selection comes from docs/backlog.md
skills/          Domain engineering guides
deploy/gcp/      Non-secret deployment target/environment configuration
data/, artifacts/ Generated local state/evidence, ignored by Git
```
