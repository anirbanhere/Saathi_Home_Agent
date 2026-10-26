# Hybrid agent delivery

Current priority: public browser capability and resumable tasks, preserving existing live train/kitchen features. See `../docs/hybrid-agent-spec.md`.

1. Browser policy and worker contracts; tests first.
2. Actual Chromium worker, isolated service identity and private invocation.
3. Visitor-owned research task start/step/resume/cancel, bounded free-model reasoning and evidence.
4. Browser UI, direct public-page inspection and status/handoff visibility.
5. Shared structured tool bridge for Hermes; verify actual runtime before advertising connection.
6. Draft checkout handoffs; continue authenticated/financial execution only with required identity, supported account access and durable operation controls.
7. Public deployment, real browser tests, synthetic live inference if available, CI and handoff.

Acceptance: one real public-page/browser workflow without a new domain API key; validated observations and source links; page/worker failures remain explicit; no secret-bearing runtime browser, cross-visitor leakage, private-address requests or transaction execution. A flight lookup that encounters a blocked/login-only page reports that limitation rather than calling a schedule live.

Completion evidence and remaining work will be filled as each slice is verified. The user has authorized implementation; routine dependency/deployment decisions within this scope do not need repeated approval.

## Verified checkpoint

- Slices 1–4 shipped: private Chromium worker; public-IP proxy; visitor-owned start/step/resume/cancel; model-planned structured actions with source/quote validation; direct inspection; public UI and durable task history.
- Slice 5 prepared: restricted Hermes plugin registration and handler verified; actual Hermes source runtime/model session remains pending.
- Slice 6 shipped for drafts only: owner-only bill/food handoff records, provider links and required-review checklist. Approval cannot execute these drafts. Actual external transactions are not enabled.
- 80 Python tests passed. Actual worker read/form navigation, public website→private worker invocation, persistence and duplicate-step handling passed. Public UI inspection passed without console errors. Free model still returns 429; IndiGo's public page returned 403 and correctly required handoff.
- See `../docs/hybrid-browser.md` and `../HANDOFF.md` for deployment identities, revisions and remaining acceptance work.
