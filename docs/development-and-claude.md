# Development setup and Claude continuation

Use this repository directly; a separate documentation-only repository would split code and context. Root [CLAUDE.md](../CLAUDE.md) is the entry point for Claude Code or a manually loaded Claude project. This pack has not been executed inside Claude; its source paths, commands and links are verified separately.

For four parallel developers, use [DEVELOPMENT_START.md](../DEVELOPMENT_START.md) and the confirmed [team workboard](team-workboard.md) before this general setup. The parallel protocol overrides this page's solo task-selection/root-handoff steps: contributors use one assigned ticket, separate checkout/branch and their own [task handoff](handoff/DEVELOPER_SESSION_TEMPLATE.md); the coordinator integrates and updates shared status.

## First hour on a new machine

```powershell
git clone https://github.com/anirbanhere/Saathi_Home_Agent.git
cd Saathi_Home_Agent
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-hosted.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --check web/app.js
```

POSIX equivalent:

```sh
git clone https://github.com/anirbanhere/Saathi_Home_Agent.git
cd Saathi_Home_Agent
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-hosted.txt
.venv/bin/python -m unittest discover -s tests -v
node --check web/app.js
```

Use a clean environment without production provider variables for unit tests. CI uses Python 3.12; Node is needed for the syntax check, not for a frontend build. There is no npm project/build command or React framework to install. The core offline console is standard-library Python; hosted Flask/GCS dependencies are separate.

On Windows agents whose default temporary directory is restricted, set Python's `tempfile.tempdir` to an existing task-specific ignored directory before test discovery. Some HTTP/proxy tests bind loopback sockets and need sandbox network permission. Investigate environment restrictions rather than disabling failing tests.

## Run the local edition

```powershell
.\.venv\Scripts\python.exe -m home_agent --port 8766 --db data/rehearsal.sqlite3
```

Open `http://127.0.0.1:8766`. Use a new database/port for a clean rehearsal; do not delete existing state. This is the separate trusted-owner local edition with offline/Muse and local speech adapter routes. Hosted OpenRouter/research routes are not present here even though the shared frontend can display their forms. Keep the loopback server off public tunnels.

## Test the hosted edition locally

Use Flask's HTTPS test client for deterministic API behavior; it correctly models the production Secure cookie without weakening it:

```python
import tempfile
from pathlib import Path
from home_agent.cloud_state import VisitorState
from home_agent.hosted import create_app

with tempfile.TemporaryDirectory() as folder:
    app = create_app(VisitorState(root=Path(folder), bucket=""))
    client = app.test_client()
    origin = "https://example.test"
    client.get("/api/state", base_url=origin)
    response = client.post(
        "/api/tools",
        json={"name": "inventory_list", "arguments": {}},
        base_url=origin,
        headers={"Origin": origin, "X-Home-Agent": "local-console"},
    )
    assert response.status_code == 200
```

Run the snippet in a clean synthetic environment with no OpenRouter credential if you want zero external discovery calls. Tests already inject catalogs/transports for this purpose. For interactive hosted UI development, run Flask bound only to loopback behind a trusted local HTTPS setup; keep the Secure cookie and origin checks. A plain-HTTP experiment failing cookie initialization does not justify weakening production policy.

Optional loopback Flask startup (HTTPS proxy remains a separate local setup):

```text
python -m flask --app home_agent.hosted:create_app run --host 127.0.0.1 --port 8780
```

## Browser worker development

`requirements-browser.txt` is independent of hosted requirements. Unit tests do not require a downloaded Chromium because the import is lazy. To run actual local Chromium, install the browser requirements and Playwright's Chromium runtime in an isolated environment; use the official `Browser.Dockerfile` for a reproducible Linux worker. Never attach a personal browser profile.

The actual worker must preserve the public proxy/policy and fresh context. Do not solve local connectivity failures by turning off SSRF checks, exposing worker IAM or copying production secrets into its process. Hosted client calls require a suitable service identity/ID token; ordinary user ADC is not necessarily enough. See [operations](operations-runbook.md) and the existing Hermes plugin README.

## Environment and secrets

`.env.example` documents variable names. The app does **not** automatically load `.env`. Use an appropriate trusted process-environment/secret injection mechanism; do not paste real values into committed examples, test output or chat. The original workstation's ignored `.env` is not available from a fresh clone, and another assistant should not assume it is.

Current production credentials are Secret Manager references. Use synthetic transports without keys for normal tests. Live model/provider smoke tests require a fresh synthetic workspace and an authorized configured provider; use only permitted free model IDs. Nous setup was skipped and must not become an onboarding requirement.

## Claude session workflow

1. Read CLAUDE.md, AGENTS.md and the latest HANDOFF; use the index to load only relevant designs.
2. Select one ready backlog ticket. State its input→outcome, dependencies and specific files/tests. Preserve unrelated changes.
3. Inspect source/tests before proposing new modules. Follow existing validation/error/ownership conventions; use parameterized SQL and typed/validated boundaries.
4. Implement an independently verifiable slice. Avoid combined framework rewrites, formatting churn or speculative extra providers.
5. Run checks relevant to changed behavior. Use real browser verification for UI changes and actual provider evidence for live claims; mocks remain explicitly contract evidence.
6. Review correctness/security/architecture/readability, scan staged content for credentials, commit coherent changes and update handoff/ticket evidence.
7. Deploy only when necessary within authorized scope, using the runbook and known rollback. Documentation changes do not require a cloud deployment.

If Claude is used through a chat interface without repository tools, attach the small entry files and relevant ticket/source sections. Ask it to produce a reviewable patch against exact paths, then apply and verify locally; do not assume it has read the entire repository or executed tests. Use the [copyable starting prompt](handoff/CLAUDE_START_HERE.md).

## Context and memory discipline

AGENTS.md contains engineering rules, SOUL.md product behavior, MEMORY.md stable choices, HANDOFF.md changing state, and the backlog implementation intent. None is automatically loaded as product-user memory or authority. Store dates/commits/evidence pointers, not private recordings, API outputs containing secrets or copied conversations. At a context switch, write the exact next command/file/acceptance gap rather than “continue work.”
