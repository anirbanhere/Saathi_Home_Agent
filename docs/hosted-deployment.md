# Hosted Python website

Updated: 26 October 2026. Public Python service: https://home-agents-xswei7prnq-uc.a.run.app . Tool execution and persistence are verified; live free-provider inference remains subject to the dependency recorded below.

## Runtime

The website serves the actual Python application on Cloud Run in `us-central1`, rather than the earlier browser-only Sites edition. `Dockerfile` uses Gunicorn and the Flask factory in `home_agent/hosted.py`. The public configuration references separate OpenRouter and RailRadar credentials through Secret Manager; neither key is returned to browsers.

`agent_loop.py` performs at most three inference requests and two validated tool calls per turn, giving observations back to the model. It is an application-owned loop; Hermes is not connected. Available tools read inventory, suggest dishes, create recipe plans, fetch RailRadar train reports (fixtures in explicitly selected local development), and prepare sandbox bills/journeys. Activity's direct railway form does not require an LLM response. Human controls execute sandbox approvals and record estimated meal consumption. Real payments, ticket issuance, clinic booking, WhatsApp and hosted speech are not connected.

Only explicitly free model routes are accepted. The selector is populated from the configured key's `/models/user` catalog, requiring zero prompt/completion pricing and tools/tool_choice support. The backend rejects a selected ID absent from that catalog before inference. Successful catalog lookups are cached for 60 seconds, failures for 15; failure offers no unverified fallback choices. Permission to use a model does not establish upstream capacity. Provider 429 responses are shown as a busy/quota state; there is no paid fallback or silent offline substitution. An in-process limiter caps this service at 15 model calls/minute and 45/day while the process is alive; it resets on restart and is not an account-wide quota ledger. OpenRouter's own limits remain authoritative.

The initial fixed dropdown advertised NVIDIA even though the key's guardrail blocked it. The observed NVIDIA 404 was reproduced with synthetic text and confirmed to be a guardrail rejection, rather than a missing public model. This motivated key-scoped catalog filtering. See [OpenRouter's filtered catalog API](https://openrouter.ai/docs/api/api-reference/models/list-models-filtered-by-user-provider-preferences-privacy-settings-and-guardrails).

## Visitor data

Each visitor receives an unguessable 256-bit, Secure, HttpOnly, same-site browser cookie. The credential selects a separate SQLite snapshot object in a private Cloud Storage bucket; a different visitor cannot access the same inventory, tasks or approvals. Browser-cookie access is anonymous; it does not implement user login, shared household membership or cross-device recovery. Limit 100 messages and 5 MB per workspace. Users should enter demonstration data while this public prototype is being evaluated.

Per-request local database files are temporary. Saved state lives in Cloud Storage, using generation-match writes to reject concurrent stale snapshots. Success is returned only after save. This preserves the existing deterministic SQLite tools for a small hosted demo and survives instance replacement. It is not a transactional store for external irreversible effects: do not connect live payments or external bookings to this snapshot execution boundary. Those need the durable operations/approval design in `home-agents-redesign.md`.

## Resources and permissions

- Project `sathi-home-agent`, region `us-central1`.
- State bucket `sathi-home-agent-demo-state-59012364414`: public access prevented; runtime identity has object access on this bucket only.
- Build/source/log bucket `sathi-home-agent-build-59012364414`: private; builder identity has bucket-scoped object and metadata access.
- Artifact Registry repository `home-agents`: builder identity has repository-scoped writer access.
- Secret `home-agents-openrouter-key`: runtime identity has accessor permission on this secret only.
- Secret `home-agents-railradar-key`: separate runtime accessor grant scoped to this railway credential; production selects the RailRadar provider.
- Runtime and builder identities are separate. No exported service-account keys and no project-wide builder grant.
- Cloud Run target: one maximum instance, zero minimum instances, one CPU, 512 MiB, request-based execution, 240-second request timeout. Build/storage/hosting can consume GCP credits even though model routes are free.

## Reproduce

Install `requirements-hosted.txt` for hosted development. For local smoke tests, use Flask's test client or a local HTTPS proxy; the production visitor cookie is deliberately Secure and must not be weakened for public deployment. `python -m home_agent` continues to run the original localhost-only console separately.

Before building, inspect `gcloud meta list-files-for-upload`. The allowlist includes only Python runtime sources, web assets, Dockerfile, hosted requirements and Cloud Build configuration. It excludes `.env`, recordings, artifacts, databases, Git metadata and agent memory files.

Build with `gcloud builds submit . --config=cloudbuild.yaml --gcs-source-staging-dir=gs://sathi-home-agent-build-59012364414/source --service-account=projects/sathi-home-agent/serviceAccounts/home-agents-build@sathi-home-agent.iam.gserviceaccount.com --project=sathi-home-agent`. Deploy the resulting immutable image to the `home-agents` Cloud Run service with the runtime identity, `--env-vars-file=deploy/gcp/env.yaml`, and `--set-secrets='OPENROUTER_API_KEY=home-agents-openrouter-key:1,RAILRADAR_API_KEY=home-agents-railradar-key:1'`. Preserve both secret references. Use the YAML file for literal environment values and quote the comma-separated secret-reference argument in PowerShell; an unquoted environment argument previously joined two values incorrectly. Verify deployed non-secret fields and secret references before smoke testing. Check tests and authenticated build status before deploying.

## Verification and rollback

Required checks: public HTTPS health; actual browser workflow; separate visitor isolation; approval replay; persisted state after a new request/revision; real synthetic-only free-model/tool execution; no browser errors; GitHub CI.

Keep the previous verified Cloud Run revision before subsequent releases. Roll back by routing service traffic to that revision. If inference is unavailable, expose the truthful error and let the user explicitly choose offline mode. A rollback must not overwrite newer workspace snapshots. Bucket retention/lifecycle policy and any soft-deletion delay should be documented when configured; no automatic deletion policy is assumed here.

## Deployment record

- URL: https://home-agents-xswei7prnq-uc.a.run.app . Public invocation is scoped to this Cloud Run service.
- Current ready revision: `home-agents-00010-w5z`; image build `db1242d9-a0cd-42de-8102-a6c22607bb73`. Previous working revision: `home-agents-00009-xhz` (final adapter/status release). Private browser worker and hybrid rollout evidence: [hybrid-browser.md](hybrid-browser.md).
- First revision had a malformed combined environment value from PowerShell; the YAML configuration corrected it. Use the second verified revision, not the first, for rollback.
- Public HTTPS checks passed: health, synthetic recipe plan and meal completion, saved inventory, persisted sandbox approval with duplicate protection, and separate anonymous visitor state.
- 48 Python tests passed. JavaScript syntax/markup checks passed. Hosted dependency audit reported no known vulnerabilities.
- The browser loaded the actual hosted state and model controls. A live model request returned the provider's 429; complete a successful synthetic tool loop after a permitted provider becomes available before claiming live inference acceptance.
- Key validation succeeded. Its filtered catalog initially allowed only Gemma 4 26B free; that upstream provider was rate-limited while account metadata still reported the 50-request allowance. Adding alternate free models is pending the user's settings update. No provider guardrails were modified by this app.
- Final hosted UI loaded correctly, including provider choice and server-storage labels. No console errors/warnings were present after the successful page load. A narrow browser viewport had no horizontal overflow; a requested 390px window was constrained to 500px, so this does not establish a 390px device test.
- Canonical source repository: https://github.com/anirbanhere/Saathi_Home_Agent . Source, agent context files and history are synchronized to `main`, with GitHub Actions enabled. CI passed for `83dde072139063e1134a7aa07cb44ae86bb912e3`: https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40336291687 . Repository-documentation changes do not change the deployed image.
- Final synthetic inference request through the public website still returned the truthful HTTP 429 response. Live model-to-tool acceptance remains pending; no paid or offline fallback was substituted.
- Model-permission fix verified on the public service: catalog is authenticated/verified and lists only Gemma 4 26B for the current key; a stale NVIDIA selection returns 403 `MODEL_NOT_ALLOWED` before inference. 54 Python tests and JavaScript syntax checks passed. Fix CI: https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40337885812 . This fixes selection/error handling; it does not enable a model blocked in the provider account or create a live train-status integration.
- Railway update: 62 tests passed; actual RailRadar reports verified locally and through the public website, including persisted direct-tool results independent of the LLM. See [railway integration](live-trains.md) for source, timestamps, stale/estimated handling and free-tier limits. Both production secret references and the selected railway provider were verified.
- Hybrid release: 80 tests, dependency audit, actual private Chromium reads/form actions, public website persistence/repeat-step checks and real UI inspection passed. Implementation CI: https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40358466068 . Worker remains private and has no mounted secrets; primary secret references were preserved. Actual model research paused on429 with evidence retained, and a blocked airline page became a handoff. See [hybrid operations](hybrid-browser.md) for current behavior and remaining limits.

- 27 October adapter release: shared OpenRouter/local Meta completion contracts, normalized failures and process-local observed availability. 97 tests and release CI passed: https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40396119648 . Real UI/provider429 updated the banner; status refresh/direct recipe/browser inspection used no new inference. Final metadata-fix revision health/direct inventory and secret references verified. Meta remains synthetic-contract evidence; live free inference remains blocked. See [adapter details](model-adapters.md).

- 27 October QA-02 release: `home-agents-00010-w5z`, build `db1242d9-a0cd-42de-8102-a6c22607bb73`, source `08d0bbe`. Result/history cancellation synchronization, task focus recovery and retained research-source rendering verified locally and on the public website. 97 tests and [implementation CI](https://github.com/anirbanhere/Saathi_Home_Agent/actions/runs/40458455826) passed. Actual390/768/1440px Activity geometry and synthetic outage/keyboard evidence are in [QA-02 verification](qa02-usability.md). Public health, recipe persistence and private-worker page inspection passed; provider secrets preserved. No new live inference/voice/transaction claim.
