# Current state and evidence

Baseline inspected: source commit `6f4eb4a`, 26 October 2026. This is a code/documentation audit of the existing release, not a fresh availability guarantee. Consult HANDOFF.md for later changes.

## Running editions

| Edition | Entry point | State | Important distinction |
| --- | --- | --- | --- |
| Public GCP website | `home_agent/hosted.py:create_app` | Private per-visitor GCS snapshots | Python backend, free-model integration, real public browser worker and railway adapter |
| Local console | `python -m home_agent` / `server.py` | One local SQLite database | Trusted loopback owner, offline/Muse routes and optional speech adapter; not all hosted routes |
| Earlier Sites demo | Separate `sites/` managed checkout | Browser-local demonstration state | Does not run Python or acquire the GCP backend implicitly |

Public app: [Home Agents](https://home-agents-xswei7prnq-uc.a.run.app/). Source: [Saathi_Home_Agent](https://github.com/anirbanhere/Saathi_Home_Agent).

## Capability matrix

| Capability | Actual status | Evidence/source | Remaining boundary |
| --- | --- | --- | --- |
| Free OpenRouter planning | Implemented/deployed | `agent_loop.py`, `test_agent_loop.py` | Last real inference attempts returned 429; no successful full live model/tool journey claimed |
| Key-permitted model selector | Implemented/deployed | `model_catalog.py`, `test_model_catalog.py` | Catalogue permission is not provider availability; last permitted choice was Gemma 4 26B free |
| Public page inspection | Live verified | `browser_worker.py`, public website→worker checks | Public HTTPS/read profile; some sites deny access |
| Research progress/resume/cancel | Implemented/deployed | `research.py`, research/hosted tests | Browser client drives requests; no unattended background progress |
| AI browser reasoning/quoted answer | Implemented, mocked tests pass | `research.py` | Successful live model→browser→answer acceptance pending capacity |
| Train running reports | Live verified | `trains.py`, `live-trains.md` | Third-party reports, not guaranteed GPS; freshness labels essential |
| Bill and journey booking | Sandbox only | `service.py`, workflow tests | No money moved, no ticket issued |
| Food/bill handoff draft | Implemented/deployed | `checkout_handoff`, draft tests | Unverified details; provider completes manually; no application execution approval |
| Inventory | Implemented/deployed | `store.py`, service/workflow tests | Estimates, one visitor workspace; not a shared family account |
| Cooking | Implemented/deployed | Curated tomato rice/dal/upma | No YouTube understanding; English base steps; no validated Indic speech |
| Receipt ingestion | Reviewed CSV text works | `import_receipt` | No image OCR, bill-image extraction or autonomous purchase detection |
| Hermes | Prepared/unverified | stdio MCP and restricted plugin | Real source runtime/session and hosted state bridge not connected |
| Meta Muse | Local adapter, unverified | `integrations.py` | API access deferred; no verified Meta inference in hosted app |
| ASR/TTS | Local JSON contracts only | `speech_request`, integration tests | No hosted routes/services or downloaded open weights |
| WhatsApp | Planned | Design only | No paired number, webhook ingress, actual messaging or reminders |
| Owned demo clinic | Planned | User selected owned calendar | No clinic tables, tools, booking or cancellation implementation |
| Real family identity/sharing | Planned | Current cookie isolation only | No login, cross-device recovery, memberships or channel binding |
| Nous candidate models | Catalog verified, testing skipped | Latest human decision after discovery | No Nous key or inference tests; do not request setup again |

## Release evidence

- Website revision `home-agents-00007-r6f`, image build `7f41ad49-a6a6-40d7-a9a4-7c91844f7b8a`.
- Previous verified website revision `home-agents-00006-x47` is the recorded rollback target.
- Private browser revision `home-agents-browser-00001-w2m`, image build `0604bf8b-5c08-4f48-84d5-a2b4d8f5f07f`.
- Existing implementation baseline: 80 Python unit/API tests; JavaScript syntax; dependency audit reported no known vulnerabilities at that checkpoint. This is dated evidence, not a permanent vulnerability guarantee.
- [Implementation CI passed](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40358466068) for `4644463f9a5648b7a59727a8e877f4a239690069`.
- Actual worker read Python.org and filled/submitted its search. Public app persisted evidence and handled duplicate step requests. Private worker rejected unauthenticated access 403.
- Actual IndiGo page returned403 and `needs_input`; no live flight result was established. OpenRouter 429 preserved inspected source evidence.

## Repository map

| Responsibility | Source | Tests |
| --- | --- | --- |
| Domain tools / roles / approvals | `service.py`, `contracts.py`, `store.py` under `home_agent/` | `test_workflows.py`, `test_checkout_handoff.py` |
| Model catalogue / bounded turn | `model_catalog.py`, `agent_loop.py` | `test_model_catalog.py`, `test_agent_loop.py` |
| Public HTTP / persistence | `hosted.py`, `cloud_state.py` | `test_hosted.py`, `test_cloud_state.py` |
| Browser / egress policy | `browser_worker.py`, `browser_proxy.py`, `browser_policy.py`, `browser_client.py` | `test_browser_policy.py`, `test_browser_worker.py` |
| Resumable research | `research.py` | `test_browser_research.py`, `test_browser_hosted.py` |
| Railway provider | `trains.py` | `test_trains.py` |
| Local edition / optional adapters | `server.py`, `integrations.py`, `mcp.py` | `test_http.py`, `test_integrations.py` |
| Web interface | `web/` | `test_ui_markup.py`, actual browser checks |
| Hermes plugin | `integrations/hermes-public-browser/` | `test_hermes_browser_plugin.py` |

## Do not restart completed work

Use the existing repository, cloud project, state bucket, service identities and private worker. Do not recreate infrastructure, migrate to the earlier repository, change public visibility, substitute train fixtures on provider failure, or present skipped Nous onboarding as a blocker. New sprint planning starts from these facts.
