# ADR-003: Add an isolated public browser beside provider APIs

Status: Accepted for the public demo. Date: 26 October 2026.

The user wants agentic tasks without creating an integration key for each information request. APIs remain useful for reliable structured data, while suitable public pages can support broader research. Browsing on the website host would unnecessarily expose model/railway credentials and household state.

Use a separate private Cloud Run Chromium worker, dedicated identity with no project-data grants, and service-scoped invocation from the website. Only public URLs and bounded structured read actions cross that boundary. A public-IP CONNECT proxy, fresh contexts and URL/method/field/action guards constrain execution. No authenticated sessions or arbitrary model-written browser code run on the website host.

Persist research as visitor-owned, versioned steps in the existing snapshot store. The website client advances requests and can resume; no background-execution guarantee is made. Preserve observations on failures. Require an inspected source and matching quote before accepting a model's final research answer; reject blocked-page evidence. This is provenance validation, not independent verification of every generated claim.

Prepare unverified bill/food drafts and hand off to the provider for real checkout. Strong identity, supported account access, exact-action approval, durable operations/idempotency and provider reconciliation must precede financial execution. The current snapshot workspace is appropriate for read-only research and drafts, not external financial commits.

Prepare a restricted Hermes plugin using the shared worker contract. Keep actual Hermes connection explicitly unverified until a supported upstream source runtime and real model session pass. The public website's current orchestrator remains application-owned.
