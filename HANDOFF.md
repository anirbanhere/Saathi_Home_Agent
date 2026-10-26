# Home Agents development handoff

Updated: 26 October 2026, Asia/Kolkata. Active branch: `codex/home-agent-demo`.

## Immediate objective

Maintain the deployed public GCP website and finish live free-model tool verification. The canonical source repository is `https://github.com/anirbanhere/Saathi_Home_Agent`, preserving its public visibility. Application source, agent context files, history and CI are synchronized there.

Current user priority: connect live train running status. RailRadar provider verification succeeded, the direct form and shared tool are implemented, and production rollout is in progress. This work is explicitly authorized independently of the pending LLM provider access.

## Completed locally

- Added a bounded OpenRouter tool/observation loop; paid model IDs are rejected.
- Added a Flask public boundary with secure anonymous visitor cookies, same-origin mutation checks, isolated workspaces, and application rate limits.
- Added durable per-visitor SQLite snapshots in private Cloud Storage with generation guards. Successful responses follow persistence.
- Browser includes free-model selection and visible agent action evidence. Original fixtures/sandbox labels remain.
- Model-access fix: a cached server-side OpenRouter `/models/user` lookup now filters the selector to key-permitted, zero-priced free models with tools/tool_choice support. Blocked or stale model IDs are rejected before inference. Cache lifetime is 60 seconds; lookup failures do not restore unverified hardcoded options. UI separates configured access from provider capacity.
- Train update: `home_agent/trains.py` implements RailRadar with identity/freshness validation, two-minute cache, bounded requests and no fixture fallback on failure. Activity includes a direct lookup that works without the LLM. The AI tool uses the same adapter and must preserve source/update/freshness. 62 Python tests passed, including direct hosted lookup without model access. Actual provider calls returned a fresh running report for 12627 and a stale completed report for 12069.
- 48 Python tests passed, including hosted isolation, restart persistence, repeat-safe approvals, snapshot conflicts, rejected cross-origin requests and model boundaries. JavaScript syntax/markup checks passed. Hosted dependency audit found no known vulnerabilities.
- Following the reported NVIDIA error, 54 Python tests passed, including catalog filtering/cache/error handling and rejecting blocked models before inference. JavaScript syntax check passed. Fix build `8c3e9e77-66ad-4c41-8fa7-73bd1c34820c` is deployed as `home-agents-00004-7mn`. Public checks verified the key-scoped catalog and a 403 `MODEL_NOT_ALLOWED` for stale NVIDIA selection before inference. CI passed for `b10aea86cd5486c322e27988e9bcbca8a64c2ed4`, run `40337885812`.
- Public HTTPS tools were verified with a fresh sample workspace: recipe plan, meal completion, saved inventory, duplicate sandbox approval, and separate visitor isolation. Browser loaded the real hosted state and model controls; successful live inference remains unverified.
- Previously created and pushed private GitHub repository `anirbanbiswas91/home-agents`; `main` is its default branch. CI passed for `fa0b72387a110ac84c0acdab4f3c06cb233d517e` (run `40334299072`). Agent context, domain skills and workflow are included. This is historical evidence, not the currently selected repository.
- Migration complete: pushed the application, agent files, CI and history to public `anirbanhere/Saathi_Home_Agent`; `main` is its default branch. GitHub CLI is authenticated as `anirbanhere`, with ADMIN access. `origin` points there; `previous-origin` preserves the earlier repository. Public-push source/history credential scans passed. New-repository CI passed for `83dde072139063e1134a7aa07cb44ae86bb912e3`, run `40336291687`.

## Cloud progress

- Enabled Cloud Run, Cloud Build, Artifact Registry and Secret Manager APIs.
- Runtime service identity: `home-agents-runtime@sathi-home-agent.iam.gserviceaccount.com`.
- Build service identity: `home-agents-build@sathi-home-agent.iam.gserviceaccount.com`.
- Private state bucket: `sathi-home-agent-demo-state-59012364414`.
- Private build/source/log bucket: `sathi-home-agent-build-59012364414`.
- Image repository: `us-central1-docker.pkg.dev/sathi-home-agent/home-agents`.
- Key is in Secret Manager as `home-agents-openrouter-key`; never print/read it into handoff.
- Railway key is in Secret Manager as `home-agents-railradar-key`, version 1; runtime accessor grant is scoped to this secret. Production YAML selects `HOME_AGENT_TRAIN_PROVIDER=railradar`. Deploy with both secret references; never paste the actual key in source or CLI arguments.
- A project-wide builder grant was rejected by approval review. It was replaced by repository-scoped artifact writer and build-bucket object access plus bucket metadata read. No project-wide builder grant was applied.
- Public URL: `https://home-agents-xswei7prnq-uc.a.run.app`.
- Current ready revision: `home-agents-00004-7mn`, image build `8c3e9e77-66ad-4c41-8fa7-73bd1c34820c`. Previous working revision: `home-agents-00003-qzh` (older fixed model selector). The first revision had an environment-argument parsing failure; do not use it for rollback.
- Final browser UI labels/model controls verified, with no console errors/warnings on successful load. Narrow-window layout had no horizontal overflow at the actual 500px viewport; smaller device widths were not newly verified.
- Always use `--env-vars-file=deploy/gcp/env.yaml`. An unquoted comma-separated PowerShell argument previously merged the bucket and model into one invalid value.

## Current inference dependency

The OpenRouter key is valid. Its filtered catalog initially allowed only `google/gemma-4-26b-a4b-it:free`. That provider returned HTTP 429 with `upstream_provider_shared_pool`; account metadata reported 50 free requests remaining. A different model returned a guardrail rejection. The user said they will add Gemma 4 31B and Nemotron 3 Super free variants; this is not yet confirmation that they saved the change. Recheck the filtered catalog before selecting alternatives. Never weaken account guardrails or enable paid fallback.

Latest diagnostic: NVIDIA Nemotron 3 Super free is still in the public catalog, but a synthetic request returned HTTP 404 explicitly stating “Model blocked by guardrail.” The key-scoped catalog still lists only Gemma 4 26B. The website's former hardcoded dropdown was also a bug because it advertised blocked choices; the fix above addresses that UI/server boundary without changing account guardrails. The new RailRadar tool/form bypasses the LLM dependency for train queries; production verification is pending at this checkpoint.

## Next actions

Repository migration is complete. Do not repeat authentication, repository creation or initial source migration. Preserve the earlier repository and its remote.
1. Await confirmation that additional free models were allowed; the latest filtered-catalog check still returned Gemma 4 26B only. The final public synthetic inference request also returned HTTP 429.
2. When available, select an allowed alternative through Connections (or update `deploy/gcp/env.yaml` and the service default), then complete a synthetic-only live tool loop. This is the remaining inference acceptance condition, not a reason to claim a mock is live.
3. Update this handoff and deployment evidence after that real inference check. The website/tools/GitHub work is already deployed and verified; do not restart infrastructure setup.
4. Keep `.env`, artifacts, databases and Sites checkout excluded. Continue WhatsApp, speech and clinic-calendar work only after the current model-to-tool acceptance condition is resolved or the human explicitly changes priority.

## Scope and evidence limits

The posted Limbo reference was opened and its launch description/video frame inspected. It is product inspiration; its internal architecture and broad capability claims are unverified. Relevant ideas: personality, memory, visible progress. Do not claim to have audited its implementation or add a hardware track automatically.

Appointment tools, live payments/tickets, WhatsApp, hosted speech, and true family sharing are not shipped. The hosted loop is application code, not a connected Hermes runtime. Follow `AGENTS.md` and the latest deployment record before changing these statements.
