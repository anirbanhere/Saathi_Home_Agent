# Risks, unresolved decisions and ownership

Baseline: 26 October 2026. “Owner” denotes a responsibility, not a person already assigned. Review at each sprint planning/release. A risk being documented does not authorize a new provider, spend or external action.

| ID | Risk / unresolved decision | Current evidence | Response / next ticket | Owner |
| --- | --- | --- | --- | --- |
| R01 | Free-model capacity blocks real planning | Actual OpenRouter 429; last key catalogue permits one model | `MODEL-01` diagnostics and truthful degraded utility; no paid fallback | Engineer; human owns account choices |
| R02 | Provider access changes over time | Catalogue checks necessary; Nous setup explicitly skipped | Keep live key-scoped discovery; do not reopen Nous without request | Engineer |
| R03 | Hermes adapter mistaken for connected runtime | Only MCP/plugin tests, not an actual session | `HERMES-01` isolated proof, then task bridge | Engineer |
| R04 | Website automation denied or incomplete | IndiGo 403; public GET/HEAD profile intentionally limited | Supported sources/API/manual handoff; do not promise universal flight/order support | Product/engineer |
| R05 | Anonymous snapshots used for real external writes | No durable operation/approval ledger or identity | `FOUND-01`, `IDENT-01`, `TXN-01`; keep financial execution disabled | Engineer/human activation owner |
| R06 | Lost bearer cookie loses practical workspace access | No login/cross-device recovery | Explicit limitations now; workspace-claim design with identity | Product/engineer |
| R07 | Process-local budgets mistaken for durable quotas | Reset on restart; max 1 is not hard spend cap | `OPS-02`, actual billing monitoring, future durable budgets | Cloud operator |
| R08 | Speech quality/hardware/license unknown | No real open-weight deployment or four-language benchmark | `VOICE-01` measurement before hardware commitments | Engineer + language reviewers |
| R09 | WhatsApp route unsuitable for groups or hosting | No chosen/paired transport; original cook-group idea | `WA-01` evidence/ADR; direct-message PoC first | Human account owner + engineer |
| R10 | Proposed10-day scope exceeds actual capacity | One engineer; external access/review not guaranteed | Sprint scope cuts; preserve honest working demo | Product owner |
| R11 | Snapshot/media retention and restoration unverified | Cookie TTL is not deletion; no completed restore policy | `OPS-01`/`02`, `MEDIA-01`, beta deletion gate | Cloud operator/engineer |
| R12 | Legacy docs confuse deployed and proposed systems | Local-only README and VM-first historical plan | This pack's edition/status index, `DOC-01` | Engineer |
| R13 | Language dropdown/template scores overstate voice capability |40 narrow offline text cases; no native speech review | `VOICE-03`, `EVAL-01`; per-locale evidence labels | Product/language reviewers |
| R14 | Prompt injection or evidence quote overstated as truth | Page text untrusted; exact quote only anchors provenance | Policy tests plus task/source-specific validation, `QA-03` | Engineer |
| R15 | Event eligibility/Meta usage requirements unknown | Acceptance/user window known, current official rules unverified | `DEMO-01`: independently verify rules and actual Meta access | Human submission owner |
| R16 | Future store migration corrupts ownership/history | Current 7-table snapshot schema, no migration tooling | Staging fixture/backup/restore/cutover before production | Engineer |
| R17 | Long requests and workspace locks limit throughput | Model/browser calls occur in request; striped process locks | Measure before scaling, then durable jobs; keep work bounded | Engineer |
| R18 | Public media brings private data before consent/ownership | Hosted speech/media paths absent | `MEDIA-01` before public upload rollout | Product/engineer |

## Decisions already settled

- Product name Home Agents; source repository remains `anirbanhere/Saathi_Home_Agent`, public visibility preserved.
- Agent3 first; Agent1/2 remain shared-foundation domains. Tamil/Malayalam/Kannada/Hindi plus English are targets.
- Use GCP `sathi-home-agent`, `us-central1`; current website and isolated browser use Cloud Run.
- Models interchangeable, free-only hosted inference by default, no guardrail relaxation or paid fallback.
- Owned demo clinic calendar when appointments are built; no real clinic provider implied.
- Browser APIs and manual checkout handoffs complement reliable domain APIs.
- Nous setup/testing skipped. Meta access deferred. Do not repeatedly ask for skipped setup.

## Decisions to make only when their implementation is selected

1. Transactional store/schema tooling/placement and migration ownership; record a new ADR.
2. Verified authentication and anonymous-workspace claim mechanism.
3. WhatsApp route, approved number/test recipient, eligibility/group limits and session placement.
4. Exact ASR/TTS weights/version/licence/hardware after benchmark.
5. Durable job delivery and outbox retry/reconciliation mechanism.
6. Media/state/log/backup retention and evaluation-recording consent.
7. Provider-neutral runtime contract and conditions for making Hermes the production orchestrator.
8. Any real checkout provider and activation authority, separately from the demo plan.

Do not invent answers to account/provider decisions that require unavailable evidence. Continue independent ready tickets, preserve scoped implementation and record the smallest missing input. Reopen architectural decisions with a dated ADR explaining new evidence, rather than rewriting history silently.
