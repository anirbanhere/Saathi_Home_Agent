# Stable project memory

Last updated: 26 October 2026, Asia/Kolkata.

- Product name: Home Agents. Saathi is a reference product brief, not an automatic rename.
- Three domains: everyday tasks first, then cooking and inventory. Original languages: Tamil, Malayalam, Kannada, Hindi; English is also required.
- Intended primary interface: WhatsApp voice. Immediate delivery priority: a public website with running Python and executable model-driven tools.
- Models must be interchangeable. Initial preference is OpenRouter free inference, with a Meta adapter once access is ready. No automatic paid fallback.
- The user selected an owned, clearly labeled demo clinic calendar for a later appointment workflow. Do not claim an external clinic integration.
- GCP project: `sathi-home-agent`, number `59012364414`; selected region: `us-central1`. Billing is linked. The user reported INR 15,000 resources, but exact remaining credit/expiry/quotas have not been verified.
- Website access: public link sharing is authorized. Browser workspaces remain separate until real household identity/sharing is implemented.
- Current website placement: Cloud Run plus private Cloud Storage visitor snapshots. ADR-002 supersedes the VM recommendation for the immediate website; a continuous WhatsApp worker may need a different placement later.
- Canonical GitHub repository: `https://github.com/anirbanhere/Saathi_Home_Agent`, explicitly selected by the user; its existing visibility is public. The earlier `anirbanbiswas91/home-agents` repository is historical. The user requested agent context/handoff/skills files and AI-assisted maintenance. Keep the original repository intact unless asked to remove it.
- The Sites edition is an earlier browser-local offline demo; the GCP backend is a separate deployment.
- WhatsApp route/eligibility, open-weight speech deployment, live train/booking/payment providers, and actual Hermes integration remain unverified or unconnected unless newer handoff evidence says otherwise.

Only store non-sensitive, durable project facts here. See `HANDOFF.md` for changing work state and docs/decisions for architectural rationale.
