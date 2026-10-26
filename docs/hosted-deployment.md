# Hosted Python website

Updated: 26 October 2026. Public Python service: https://home-agents-xswei7prnq-uc.a.run.app . Tool execution and persistence are verified; live free-provider inference remains subject to the dependency recorded below.

## Runtime

The website serves the actual Python application on Cloud Run in `us-central1`, rather than the earlier browser-only Sites edition. `Dockerfile` uses Gunicorn and the Flask factory in `home_agent/hosted.py`. The public configuration references the OpenRouter credential through Secret Manager; the key is not returned to browsers.

`agent_loop.py` performs at most three inference requests and two validated tool calls per turn, giving observations back to the model. It is an application-owned loop; Hermes is not connected. Available tools read inventory, suggest dishes, create recipe plans, read train fixtures, and prepare sandbox bills/journeys. Human controls execute sandbox approvals and record estimated meal consumption. Real payments, ticket issuance, clinic booking, WhatsApp and hosted speech are not connected.

Only explicitly free model routes are accepted. The UI allows model selection. Account guardrails and upstream availability still apply. Provider 429 responses are shown as a busy/quota state; there is no paid fallback or silent offline substitution. An in-process limiter caps this service at 15 model calls/minute and 45/day while the process is alive; it resets on restart and is not an account-wide quota ledger. OpenRouter's own limits remain authoritative.

## Visitor data

Each visitor receives an unguessable 256-bit, Secure, HttpOnly, same-site browser cookie. The credential selects a separate SQLite snapshot object in a private Cloud Storage bucket; a different visitor cannot access the same inventory, tasks or approvals. Browser-cookie access is anonymous; it does not implement user login, shared household membership or cross-device recovery. Limit 100 messages and 5 MB per workspace. Users should enter demonstration data while this public prototype is being evaluated.

Per-request local database files are temporary. Saved state lives in Cloud Storage, using generation-match writes to reject concurrent stale snapshots. Success is returned only after save. This preserves the existing deterministic SQLite tools for a small hosted demo and survives instance replacement. It is not a transactional store for external irreversible effects: do not connect live payments or external bookings to this snapshot execution boundary. Those need the durable operations/approval design in `home-agents-redesign.md`.

## Resources and permissions

- Project `sathi-home-agent`, region `us-central1`.
- State bucket `sathi-home-agent-demo-state-59012364414`: public access prevented; runtime identity has object access on this bucket only.
- Build/source/log bucket `sathi-home-agent-build-59012364414`: private; builder identity has bucket-scoped object and metadata access.
- Artifact Registry repository `home-agents`: builder identity has repository-scoped writer access.
- Secret `home-agents-openrouter-key`: runtime identity has accessor permission on this secret only.
- Runtime and builder identities are separate. No exported service-account keys and no project-wide builder grant.
- Cloud Run target: one maximum instance, zero minimum instances, one CPU, 512 MiB, request-based execution, 240-second request timeout. Build/storage/hosting can consume GCP credits even though model routes are free.

## Reproduce

Install `requirements-hosted.txt` for hosted development. For local smoke tests, use Flask's test client or a local HTTPS proxy; the production visitor cookie is deliberately Secure and must not be weakened for public deployment. `python -m home_agent` continues to run the original localhost-only console separately.

Before building, inspect `gcloud meta list-files-for-upload`. The allowlist includes only Python runtime sources, web assets, Dockerfile, hosted requirements and Cloud Build configuration. It excludes `.env`, recordings, artifacts, databases, Git metadata and agent memory files.

Build with `gcloud builds submit . --config=cloudbuild.yaml --gcs-source-staging-dir=gs://sathi-home-agent-build-59012364414/source --service-account=projects/sathi-home-agent/serviceAccounts/home-agents-build@sathi-home-agent.iam.gserviceaccount.com --project=sathi-home-agent`. Deploy the resulting immutable image to the `home-agents` Cloud Run service with the runtime identity, `--env-vars-file=deploy/gcp/env.yaml`, and `--set-secrets=OPENROUTER_API_KEY=home-agents-openrouter-key:1`. Use the YAML file instead of an unquoted comma-separated environment argument in PowerShell; that was observed to join two values incorrectly. Verify the deployed non-secret environment fields before smoke testing. Check tests and authenticated build status before deploying.

## Verification and rollback

Required checks: public HTTPS health; actual browser workflow; separate visitor isolation; approval replay; persisted state after a new request/revision; real synthetic-only free-model/tool execution; no browser errors; GitHub CI.

Keep the previous verified Cloud Run revision before subsequent releases. Roll back by routing service traffic to that revision. If inference is unavailable, expose the truthful error and let the user explicitly choose offline mode. A rollback must not overwrite newer workspace snapshots. Bucket retention/lifecycle policy and any soft-deletion delay should be documented when configured; no automatic deletion policy is assumed here.

## Deployment record

- URL: https://home-agents-xswei7prnq-uc.a.run.app . Public invocation is scoped to this Cloud Run service.
- Verified working revision: `home-agents-00002-cjn`; image build `467d435a-7a75-4a98-ad6d-6d3a917385c0`.
- First revision had a malformed combined environment value from PowerShell; the YAML configuration corrected it. Use the second verified revision, not the first, for rollback.
- Public HTTPS checks passed: health, synthetic recipe plan and meal completion, saved inventory, persisted sandbox approval with duplicate protection, and separate anonymous visitor state.
- 48 Python tests passed. JavaScript syntax/markup checks passed. Hosted dependency audit reported no known vulnerabilities.
- The browser loaded the actual hosted state and model controls. A live model request returned the provider's 429; complete a successful synthetic tool loop after a permitted provider becomes available before claiming live inference acceptance.
- Key validation succeeded. Its filtered catalog initially allowed only Gemma 4 26B free; that upstream provider was rate-limited while account metadata still reported the 50-request allowance. Adding alternate free models is pending the user's settings update. No provider guardrails were modified by this app.
- Final UI-only source build `4da2e8be-7c97-441a-a9c3-8f5a14a905c5` is in progress; update this record after its deployment and browser checks.
