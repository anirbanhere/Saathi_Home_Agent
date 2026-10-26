# Hybrid Home Agents: browser, APIs and controlled transactions

Date: 26 October 2026. User authorized implementation as far as practical.

## Product direction

One conversational assistant chooses an existing API tool, public web/browser research, or a user/account handoff. Users should not need a developer API key for every ordinary request. The application operator maintains shared data-provider connections; users connect personal accounts only when required. Existing RailRadar and kitchen tools remain useful capabilities.

The immediate browser release handles public information through a separate worker. Flight-status research is a representative task, but a page that contains only a schedule, search snippet or login challenge must not become a fabricated live flight result. Purchases and payment execution remain outside this public read-only profile.

## Implementation slices

1. Deploy an isolated browser worker without LLM/railway secrets or project data permissions. Use a fresh browser context per request and structured actions; do not execute arbitrary model-written Python/JavaScript on the credential-bearing application host.
2. Add resumable, visitor-owned research tasks with observable steps, source URLs, timestamps, bounded model/browser budgets and explicit blocked/handoff outcomes. Browser execution uses supported public sites first, with HTTPS/DNS/method guards. No authenticated browsing or hidden credentials in this release.
3. Connect the free-model reasoning layer to browser observations. Keep model choice replaceable and enforce the existing key-permitted free catalog. Browser observations are untrusted evidence, never instructions. A model outage preserves task state and allows manual page inspection rather than inventing completion.
4. Add a Hermes-facing structured-tool bridge on the same worker policy. Connect an actual pinned Hermes runtime only after installation/tool isolation and a live model run are verified. Do not claim the current application-owned loop is Hermes.
5. Add draft bill/food-order handoffs with exact recipient/items/address/total confirmation as appropriate. A draft or approval is not a payment/order receipt. New authenticated sessions and external financial effects require stronger user identity, durable operation storage, exact-action approval and provider verification.
6. Extend isolated persistent account sessions, user login/OTP handoff, approved checkout, reconciliation, cancellation and background scheduling. Migrate financial operations away from the demo's whole-workspace snapshots before enabling irreversible external effects.

## Architecture and trust boundaries

The existing Cloud Run website owns anonymous visitor identity, task history, approvals and provider credentials. A private Cloud Run browser service receives only a public URL and bounded structured read actions, never full household context or API keys. Its dedicated runtime identity has no project-data roles. The website may invoke that one worker through service-scoped IAM. Browser results return through the website's visitor boundary.

Research task steps are request-driven and persisted between requests. Closing the page pauses progress; reopening can resume. True autonomous background execution requires a durable job delivery service later. A failed response or interrupted browser attempt is recoverable for read-only work; no assumption of exactly-once remote execution is made.

The first policy supports public HTTPS pages, no private/reserved IPs or custom ports, no credentials in URLs, GET/HEAD network traffic, no downloads, no persistent cookies, no password/payment fields, no account login, and no purchase/payment submissions. A CONNECT proxy resolves and validates every destination, then connects to the checked numeric public IP to avoid DNS rebinding. Unsupported sites, blocked network methods, CAPTCHA and login requirements become explicit handoffs. Method/path/button guards reduce unintended effects but do not prove every public site's GET requests are side-effect free. This profile has no authenticated account session; enabling account access requires a new policy. This is a bounded browser capability, not a promise that every website works.

## State and evidence

Research tasks retain goal, selected model, current step/version, observed pages, source time, browser action trace, summary and outcome. Steps cannot read another visitor's task or change a succeeded/cancelled task. Observations have size limits. Results link to inspected pages and distinguish page evidence from the model's interpretation. Search results alone do not verify a live flight's position, delay or cancellation.

Proposed task states: planned, running, needs_input, succeeded, failed, cancelled. Handoff is represented by needs_input with a reason and validated destination. Model-generated claims never authorize a transaction.

## Validation

Add meaningful unit/API tests for ownership, step limits, cancellation/replay, blocked URLs and IPs, disallowed methods/actions, malformed worker/model responses, source provenance, model unavailability and handoff. Run the existing Python suite and JavaScript syntax checks. Test the actual browser process against a public page and an interactive local test fixture; then test the private worker through the public website. Live inference acceptance remains separate from mocked loop tests.

Commands: `python -m unittest discover -s tests -v`; `node --check web/app.js`. Worker container build/deploy commands and exact runtime versions are recorded with the implemented deployment files. Do not put secrets or login profiles in source, CI or container images.

## Sources and decision boundaries

[Hermes embedding](https://hermes-agent.nousresearch.com/docs/guides/python-library) requires its supported source environment. Its built-in browser executes model-written code, motivating isolation and restricted tool exposure for this public product. [Hermes browser](https://hermes-agent.nousresearch.com/docs/user-guide/features/browser), [Playwright network controls](https://playwright.dev/python/docs/network), [Cloud Run browser automation](https://docs.cloud.google.com/run/docs/browser-automation).

This spec supersedes the earlier API-per-capability-first delivery sequence. The earlier voice/clinic design remains a future domain roadmap. Current implementation evidence belongs in HANDOFF.md and hosted-deployment.md.
