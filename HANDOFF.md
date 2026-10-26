# Home Agents development handoff

Updated: 26 October 2026, Asia/Kolkata. Active branch: `codex/home-agent-demo`.

## Immediate objective

Latest user request: update the hybrid API/browser/account-handoff plan and implement as far as practical. The website now has a real private Chromium worker, resumable public research and bill/food handoff drafts. The canonical source repository is `https://github.com/anirbanhere/Saathi_Home_Agent`, preserving its public visibility.

Latest release details: `docs/hybrid-browser.md`, spec `docs/hybrid-agent-spec.md`, delivery plan `tasks/hybrid-agent-plan.md`. Live railway functionality remains deployed. The permitted LLM provider still returns 429; no successful live model-to-browser answer is claimed.

## Latest hybrid checkpoint

- Deployed website revision `home-agents-00007-r6f`, build `7f41ad49-a6a6-40d7-a9a4-7c91844f7b8a`. Previous verified website revision `home-agents-00006-x47` is the rollback target.
- Private worker `home-agents-browser`, revision `home-agents-browser-00001-w2m`, build `0604bf8b-5c08-4f48-84d5-a2b4d8f5f07f`. Dedicated identity `home-agents-browser@sathi-home-agent.iam.gserviceaccount.com`, no mounted secrets/project-data roles. Its only invoker binding grants the website runtime access; public access returned403. Configuration lives in `deploy/gcp/env.yaml`; both existing model/railway secret refs remain.
- Structured public-page worker uses actual Chromium1.64.1, fresh context and DNS-validated/pinned public-IP proxy; no arbitrary model code/account login/transaction capability. Worker memory1Gi, CPU1, concurrency1, max1/min0.
- `ResearchTasks` supports visitor-owned start/step/resume/cancel, persisted version/source/trace, free-model authorization and exact-quote source validation. Direct page inspection requires no model. Six steps maximum, 20 tasks per visitor. Browser API routes `/api/browser/tasks` and `/api/browser/tasks/<id>/steps`; task cancellation uses existing endpoint. Steps are client/request-driven; closing the tab stops further steps after the current request.
- Assistant tool `start_web_research` queues research; UI advances it. Existing model behavior remains bounded/free-only. `checkout_handoff` is an owner-only bill/food draft with validated provider URL and review checklist, never approve-to-execute or a receipt.
- 80 Python tests passed. Actual private worker read a public page and filled/submitted Python.org search. Public website→private worker→saved evidence, repeat-step handling and checkout draft verified with fresh synthetic visitors. Actual browser form displayed completion/source history with no console errors/warnings. Browser dependency audit found no known vulnerabilities. Implementation GitHub CI passed for `4644463f9a5648b7a59727a8e877f4a239690069`, run `40358466068`; all source/plans are pushed to canonical `main`. Final public health and ready revision were verified after rollout.
- Actual synthetic free-model research inspected Python.org, then paused with `RATE_LIMITED`/429 and retained its source. Only Gemma4 26B remains key-permitted. No paid fallback or guardrail change. IndiGo returned403/Access Denied; worker correctly produced `needs_input`, not a flight report.
- Restricted Hermes plugin added in `integrations/hermes-public-browser/`, registration/handler validated. Inspected upstream commit `d49e2ebbaed42718659c13f82c04cde7d8ab10bd` requires PM-managed Python3.14; do not install an unrelated PyPI package into this app's3.12 environment. Actual Hermes runtime/session and hosted task-state integration remain unverified.

## Completed locally

- Added a bounded OpenRouter tool/observation loop; paid model IDs are rejected.
- Added a Flask public boundary with secure anonymous visitor cookies, same-origin mutation checks, isolated workspaces, and application rate limits.
- Added durable per-visitor SQLite snapshots in private Cloud Storage with generation guards. Successful responses follow persistence.
- Browser includes free-model selection and visible agent action evidence. Original fixtures/sandbox labels remain.
- Model-access fix: a cached server-side OpenRouter `/models/user` lookup now filters the selector to key-permitted, zero-priced free models with tools/tool_choice support. Blocked or stale model IDs are rejected before inference. Cache lifetime is 60 seconds; lookup failures do not restore unverified hardcoded options. UI separates configured access from provider capacity.
- Train update: `home_agent/trains.py` implements RailRadar with identity/freshness validation, two-minute cache, bounded requests and no fixture fallback on failure. Activity includes a direct lookup that works without the LLM. The AI tool uses the same adapter and must preserve source/update/freshness. 62 Python tests passed, including direct hosted lookup without model access. Actual provider calls returned a fresh running report for 12627 and a stale completed report for 12069. The public service returned a fresh 12627 report and persisted it in task history; production train config and both secret references were verified. Train integration CI passed for `ddcad12397f7b455ab9d9f30080b1f96c45ddfa5`, run `40347816704`.
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
- Current ready revision: `home-agents-00007-r6f`, image build `7f41ad49-a6a6-40d7-a9a4-7c91844f7b8a`. Previous working revision: `home-agents-00006-x47` (initial hybrid release). The first revision had an environment-argument parsing failure; do not use it for rollback. Private worker details are in the latest checkpoint above.
- Final browser UI labels/model controls verified, with no console errors/warnings on successful load. Narrow-window layout had no horizontal overflow at the actual 500px viewport; smaller device widths were not newly verified.
- Always use `--env-vars-file=deploy/gcp/env.yaml`. An unquoted comma-separated PowerShell argument previously merged the bucket and model into one invalid value.

## Current inference dependency

The OpenRouter key is valid. Its filtered catalog initially allowed only `google/gemma-4-26b-a4b-it:free`. That provider returned HTTP 429 with `upstream_provider_shared_pool`; account metadata reported 50 free requests remaining. A different model returned a guardrail rejection. The user said they will add Gemma 4 31B and Nemotron 3 Super free variants; this is not yet confirmation that they saved the change. Recheck the filtered catalog before selecting alternatives. Never weaken account guardrails or enable paid fallback.

Latest diagnostic: NVIDIA Nemotron 3 Super free is still in the public catalog, but a synthetic request returned HTTP 404 explicitly stating “Model blocked by guardrail.” The key-scoped catalog still lists only Gemma 4 26B. The website's former hardcoded dropdown was also a bug because it advertised blocked choices; the fix above addresses that UI/server boundary without changing account guardrails. The deployed RailRadar tool/form bypasses the LLM dependency for train queries; public provider lookup and persistence are verified.

## Next actions

Repository migration is complete. Do not repeat authentication, repository creation or initial source migration. Preserve the earlier repository and its remote.
1. Recheck the key-permitted catalog after the user allows additional free models; currently Gemma4 26B only and actual inference returns429. Then verify a synthetic real model→browser→quoted answer and assistant→queued research journey. Do not call mocked tests live inference evidence.
2. Connect the restricted Hermes plugin in a separate supported source environment with only its browser toolset, workload identity and no personal context. Verify a real model session before advertising Hermes connected. Do not reinstall infrastructure or move arbitrary-code tools onto the website host.
3. Extend task/background/account identity before WhatsApp or authenticated transactions. Scope real payments/orders separately with durable operation/approval/reconciliation storage; current drafts deliberately require manual provider completion.
4. Keep `.env`, artifacts, databases and Sites checkout excluded. Railway integration remains complete. Continue voice/clinic roadmap only according to the user's next priority; preserve existing model guardrails and sandbox labels.

## Scope and evidence limits

The posted Limbo reference was opened and its launch description/video frame inspected. It is product inspiration; its internal architecture and broad capability claims are unverified. Relevant ideas: personality, memory, visible progress. Do not claim to have audited its implementation or add a hardware track automatically.

Appointment tools, live payments/tickets, WhatsApp, hosted speech, and true family sharing are not shipped. The hosted loop is application code, not a connected Hermes runtime. Follow `AGENTS.md` and the latest deployment record before changing these statements.
