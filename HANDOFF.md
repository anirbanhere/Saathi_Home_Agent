# Home Agents development handoff

Updated: 26 October 2026, Asia/Kolkata. Active branch: `codex/home-agent-demo`.

## Immediate objective

Deploy a public website in GCP using live free models to execute the available tools, and push a maintainable private GitHub repository with agent context files. Keep this ahead of additional architecture planning or WhatsApp/hardware expansion.

## Completed locally

- Added a bounded OpenRouter tool/observation loop; paid model IDs are rejected.
- Added a Flask public boundary with secure anonymous visitor cookies, same-origin mutation checks, isolated workspaces, and application rate limits.
- Added durable per-visitor SQLite snapshots in private Cloud Storage with generation guards. Successful responses follow persistence.
- Browser includes free-model selection and visible agent action evidence. Original fixtures/sandbox labels remain.
- 48 Python tests passed, including hosted isolation, restart persistence, repeat-safe approvals, snapshot conflicts, rejected cross-origin requests and model boundaries. JavaScript syntax/markup checks passed. Hosted dependency audit found no known vulnerabilities.
- Public HTTPS tools were verified with a fresh sample workspace: recipe plan, meal completion, saved inventory, duplicate sandbox approval, and separate visitor isolation. Browser loaded the real hosted state and model controls; successful live inference remains unverified.
- Created private GitHub repository `anirbanbiswas91/home-agents`; origin is connected. Source push is pending.

## Cloud progress

- Enabled Cloud Run, Cloud Build, Artifact Registry and Secret Manager APIs.
- Runtime service identity: `home-agents-runtime@sathi-home-agent.iam.gserviceaccount.com`.
- Build service identity: `home-agents-build@sathi-home-agent.iam.gserviceaccount.com`.
- Private state bucket: `sathi-home-agent-demo-state-59012364414`.
- Private build/source/log bucket: `sathi-home-agent-build-59012364414`.
- Image repository: `us-central1-docker.pkg.dev/sathi-home-agent/home-agents`.
- Key is in Secret Manager as `home-agents-openrouter-key`; never print/read it into handoff.
- A project-wide builder grant was rejected by approval review. It was replaced by repository-scoped artifact writer and build-bucket object access plus bucket metadata read. No project-wide builder grant was applied.
- Public URL: `https://home-agents-xswei7prnq-uc.a.run.app`.
- Verified working revision: `home-agents-00002-cjn`, image build `467d435a-7a75-4a98-ad6d-6d3a917385c0`. The first revision had an environment-argument parsing failure; do not use it for rollback.
- Final UI build `4da2e8be-7c97-441a-a9c3-8f5a14a905c5` succeeded and has been submitted for deployment. Confirm the latest revision and update this handoff after browser checks.
- Always use `--env-vars-file=deploy/gcp/env.yaml`. An unquoted comma-separated PowerShell argument previously merged the bucket and model into one invalid value.

## Current inference dependency

The OpenRouter key is valid. Its filtered catalog initially allowed only `google/gemma-4-26b-a4b-it:free`. That provider returned HTTP 429 with `upstream_provider_shared_pool`; account metadata reported 50 free requests remaining. A different model returned a guardrail rejection. The user said they will add Gemma 4 31B and Nemotron 3 Super free variants; this is not yet confirmation that they saved the change. Recheck the filtered catalog before selecting alternatives. Never weaken account guardrails or enable paid fallback.

## Next actions

1. Verify final deployed UI labels, model controls, mobile layout and browser console. Runtime and model-selection fixes are already in source.
2. Complete a synthetic-only live tool call once a permitted free provider is available. This is the remaining inference acceptance condition, not a reason to claim a mock is live.
3. Update deployment records and this handoff with the latest revision and any new verification.
4. Push the private GitHub repository and check CI. Source credential scan passed; keep `.env`, artifacts, databases and Sites checkout excluded.

## Scope and evidence limits

The posted Limbo reference was opened and its launch description/video frame inspected. It is product inspiration; its internal architecture and broad capability claims are unverified. Relevant ideas: personality, memory, visible progress. Do not claim to have audited its implementation or add a hardware track automatically.

Appointment tools, live payments/tickets, WhatsApp, hosted speech, and true family sharing are not shipped. The hosted loop is application code, not a connected Hermes runtime. Follow `AGENTS.md` and the latest deployment record before changing these statements.
