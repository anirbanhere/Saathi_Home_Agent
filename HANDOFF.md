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
- Created and pushed private GitHub repository `anirbanbiswas91/home-agents`; `main` is the default branch. CI passed for `fa0b72387a110ac84c0acdab4f3c06cb233d517e` (run `40334299072`). Agent context, domain skills and workflow are included.

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
- Current ready revision: `home-agents-00003-qzh`, image build `4da2e8be-7c97-441a-a9c3-8f5a14a905c5`. Previous verified working revision: `home-agents-00002-cjn`. The first revision had an environment-argument parsing failure; do not use it for rollback.
- Final browser UI labels/model controls verified, with no console errors/warnings on successful load. Narrow-window layout had no horizontal overflow at the actual 500px viewport; smaller device widths were not newly verified.
- Always use `--env-vars-file=deploy/gcp/env.yaml`. An unquoted comma-separated PowerShell argument previously merged the bucket and model into one invalid value.

## Current inference dependency

The OpenRouter key is valid. Its filtered catalog initially allowed only `google/gemma-4-26b-a4b-it:free`. That provider returned HTTP 429 with `upstream_provider_shared_pool`; account metadata reported 50 free requests remaining. A different model returned a guardrail rejection. The user said they will add Gemma 4 31B and Nemotron 3 Super free variants; this is not yet confirmation that they saved the change. Recheck the filtered catalog before selecting alternatives. Never weaken account guardrails or enable paid fallback.

## Next actions

1. Await confirmation that additional free models were allowed; the latest filtered-catalog check still returned Gemma 4 26B only. The final public synthetic inference request also returned HTTP 429.
2. When available, select an allowed alternative through Connections (or update `deploy/gcp/env.yaml` and the service default), then complete a synthetic-only live tool loop. This is the remaining inference acceptance condition, not a reason to claim a mock is live.
3. Update this handoff and deployment evidence after that real inference check. The website/tools/GitHub work is already deployed and verified; do not restart infrastructure setup.
4. Keep `.env`, artifacts, databases and Sites checkout excluded. Continue WhatsApp, speech and clinic-calendar work only after the current model-to-tool acceptance condition is resolved or the human explicitly changes priority.

## Scope and evidence limits

The posted Limbo reference was opened and its launch description/video frame inspected. It is product inspiration; its internal architecture and broad capability claims are unverified. Relevant ideas: personality, memory, visible progress. Do not claim to have audited its implementation or add a hardware track automatically.

Appointment tools, live payments/tickets, WhatsApp, hosted speech, and true family sharing are not shipped. The hosted loop is application code, not a connected Hermes runtime. Follow `AGENTS.md` and the latest deployment record before changing these statements.
