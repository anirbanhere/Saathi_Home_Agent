# GCP operations and recovery runbook

Status: current resource inventory plus procedures. Baseline evidence is26 October 2026; re-inspect live configuration before a rollout. A documentation change does not require a cloud deployment. No new resources are provisioned by this document.

## Resource inventory

| Resource | Recorded configuration |
| --- | --- |
| Project / number / region | `sathi-home-agent` / `59012364414` / `us-central1` |
| Public service | `home-agents`, [website](https://home-agents-xswei7prnq-uc.a.run.app/) |
| Public runtime identity | `home-agents-runtime@sathi-home-agent.iam.gserviceaccount.com` |
| Public revision / image build | `home-agents-00007-r6f` / `7f41ad49-a6a6-40d7-a9a4-7c91844f7b8a` |
| Previous website rollback revision | `home-agents-00006-x47` |
| Private browser service | `home-agents-browser`, `https://home-agents-browser-59012364414.us-central1.run.app` |
| Browser runtime identity | `home-agents-browser@sathi-home-agent.iam.gserviceaccount.com` |
| Browser revision / build | `home-agents-browser-00001-w2m` / `0604bf8b-5c08-4f48-84d5-a2b4d8f5f07f` |
| Builder identity | `home-agents-build@sathi-home-agent.iam.gserviceaccount.com` |
| State bucket | `sathi-home-agent-demo-state-59012364414`, private visitor snapshots |
| Build/source/log bucket | `sathi-home-agent-build-59012364414`, private |
| Artifact Registry prefix | `us-central1-docker.pkg.dev/sathi-home-agent/home-agents` |
| Provider secrets | `home-agents-openrouter-key:1`, `home-agents-railradar-key:1` |

Website baseline: CPU 1, memory 512Mi, concurrency 8, max instances1/min 0, request timeout 240s; Gunicorn1 worker/8 threads/230s. Browser: CPU 1, memory 1Gi, concurrency 1, max 1/min 0, timeout 120s; Gunicorn1 worker/1 thread/110s. Read deployed settings rather than assuming these numbers never change.

Website runtime has scoped state-bucket access, accessor on the individual provider secrets and `run.invoker` on the browser service. Browser identity has no mounted secrets/project-data roles. Builder access is scoped to the existing artifact repository and private build bucket. Do not replace narrow roles with project-wide editor/build permissions to solve an error.

## Environment ownership

| Variable | Where used | Handling |
| --- | --- | --- |
| `HOME_AGENT_STATE_BUCKET` | Hosted visitor persistence | Literal value in `deploy/gcp/env.yaml`; omit/use local store only for deliberate development |
| `OPENROUTER_MODEL` | Hosted preferred model | Preference must still pass live key catalogue; no unverified fallback |
| `HOME_AGENT_TRAIN_PROVIDER` | Domain train tool | Production `railradar`; local explicit `fixture` only |
| `HOME_AGENT_BROWSER_WORKER_URL` | Private client | Fixed HTTPS Cloud Run service URL, workload ID token auth |
| `OPENROUTER_API_KEY`, `RAILRADAR_API_KEY` | Website provider requests | Secret Manager references; never literal deployment env values |
| `HOME_AGENT_PUBLIC_ORIGIN` | Optional hosted origin restriction | Must match the actual served origin when configured |
| `HOME_AGENT_VISITOR_DIR` | Local hosted-development storage | Not the durable GCP state location |
| `MODEL_API_KEY`, `META_MODEL`, `META_BASE_URL` | Optional local Meta adapter | Unverified; hosted service does not become Meta-connected merely by setting these |
| `HOME_AGENT_ASR_URL`, `HOME_AGENT_TTS_URL`, `HOME_AGENT_SPEECH_KEY` | Optional local speech adapter | No hosted speech routes currently; never claim connected from env alone |

No Nous configuration is required; the human skipped it. `.env.example` is a reference, and `.env` is ignored/not automatically loaded by the application.

## Preflight before any source build

1. Check Git status/target branch and existing test results. Review the intended runtime change and rollback.
2. Use `gcloud meta list-files-for-upload --verbosity=error` as a separate read-only step. Inspect its output before invoking a source build.
3. Scan the exact selected content for credential/private-data matches without printing secret values. Report only paths/counts. `.gcloudignore` is an allowlist; `.env`, Git metadata, databases, media, `artifacts/`, `sites/` and agent memory must stay excluded.
4. Verify current cloud identities, secret **references**, resource scope and budget/credits. Do not read/export secret payloads just to inspect configuration.
5. Build only after manifest/scan review. Never combine an unreviewed upload and a later scan as if the scan prevented exposure.

## Reproducible builds and rollout

Website build, using the existing scoped identity and private source staging:

```powershell
gcloud builds submit . --project=sathi-home-agent --region=us-central1 --config=cloudbuild.yaml --service-account=projects/sathi-home-agent/serviceAccounts/home-agents-build@sathi-home-agent.iam.gserviceaccount.com --gcs-source-staging-dir=gs://sathi-home-agent-build-59012364414/source
```

Worker uses the same command with `--config=cloudbuild-browser.yaml`, after its own verified manifest. Website image name is `website:BUILD_ID`; worker is `browser:BUILD_ID` under the repository prefix. Replace `BUILD_ID` with the successful actual build ID; do not deploy a build still working/failed. Record image and source commit.

Website update, preserving literal YAML and **both** quoted secret references:

```powershell
gcloud run services update home-agents --project=sathi-home-agent --region=us-central1 --image=us-central1-docker.pkg.dev/sathi-home-agent/home-agents/website:BUILD_ID --env-vars-file=deploy/gcp/env.yaml --set-secrets='OPENROUTER_API_KEY=home-agents-openrouter-key:1,RAILRADAR_API_KEY=home-agents-railradar-key:1'
```

PowerShell previously misparsed an unquoted comma-separated environment argument and merged values. Keep literal env in YAML and quote the secret list. Verify non-secret values and secret-reference names after update.

Private worker update:

```powershell
gcloud run services update home-agents-browser --project=sathi-home-agent --region=us-central1 --image=us-central1-docker.pkg.dev/sathi-home-agent/home-agents/browser:BUILD_ID --service-account=home-agents-browser@sathi-home-agent.iam.gserviceaccount.com --cpu=1 --memory=1Gi --concurrency=1 --min-instances=0 --max-instances=1 --timeout=120
```

The existing worker must remain IAM protected. If creating/recreating it under separately authorized recovery work, explicitly deny unauthenticated access and grant only website-runtime service-scoped invocation; do not copy the public website IAM policy. Do not attach provider secrets to the worker.

### Post-deploy smoke

- Public HTTPS health, expected ready revision and non-secret configuration/reference checks.
- Fresh synthetic visitor direct tool + persisted result + second-visitor isolation.
- Public site→private worker observation; unauthenticated direct worker request denied.
- Changed UI actually exercised, source/transaction labels checked, no unexpected console/network failures.
- If model behavior changed, an actual synthetic model/tool call or explicitly recorded provider block; do not infer acceptance from health.
- Record timestamp, commit, build/revision, evidence and rollback in HANDOFF.md/release docs.

## Diagnosis and recovery

| Symptom | Check | Safe response |
| --- | --- | --- |
| Model429 | Key-permitted catalogue, provider capacity vs app budget | Retain evidence; bounded retry or permitted free choice; direct tools remain usable |
| Model403/404 | Account permission/model availability | Do not advertise blocked choices or relax guardrails automatically |
| Browser401/403 from service | IAM invoker binding, runtime identity, token audience/configured URL | Repair exact service-scoped auth; never make worker public |
| Target page 403/CAPTCHA | Actual page state/HTTP evidence | Manual handoff/alternative supported source; no bypass claim |
| Save409 | GCS generation conflict | Refresh authoritative workspace; never blindly replay an external commit |
| Storage503 | Bucket name/access, request failures, temporary limits | Preserve data, inspect redacted errors; do not delete snapshots to unblock |
| Lost workspace | Browser cookie/expiry, correct service/bucket | No account recovery exists yet; do not map supplied IDs into other workspaces |
| Speech button fails hosted | Route/integration matrix | Hosted speech is not shipped; implement its scoped boundary instead of setting a flag |

Rollback a website code release by routing traffic to a **verified existing** prior revision, after checking compatibility:

```powershell
gcloud run services update-traffic home-agents --project=sathi-home-agent --region=us-central1 --to-revisions=home-agents-00006-x47=100
```

Do not overwrite newer snapshots as part of code rollback. The first malformed-env revision is not a recovery target. Future schema/operation changes require their own compatible migration/rollback plan; never roll back a financial ledger by restoring an old workspace blindly.

## Backups, spend and incident ownership

GCS persistence and generation guards are not a verified backup/restore or deletion policy. Inspect versioning/soft deletion/lifecycle/retention actually configured, then rehearse restore to a separate restricted environment. Anonymous cookie expiry is not state deletion. Establish explicit ownership/retention before real household data collection.

Reported INR 15,000 credits have unverified remaining balance/expiry. Active compute, large browser-image builds/storage, media, network, database and speech experiments can consume credits despite free model tokens. Zero minimum instances/max 1 limits resources but not all charges; process-local request budgets reset on restart. Check actual usage, budgets/alerts and resource caps before expansion. Budget alerts are not a hard spend stop.

For incidents, record affected revision/time/scope, normalized errors and task IDs without private payloads. Disable the affected integration or route back to a known revision where safe, preserve evidence/state, and document restoration. The human/operator owns cloud billing/account decisions; the implementing engineer owns deployment evidence and rollback readiness.
