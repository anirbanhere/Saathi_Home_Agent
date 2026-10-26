# ADR-002: Deploy the executable website before WhatsApp integration

Status: Accepted for the public demo.
Date: 26 October 2026.

## Context

The user clarified that the immediate priority is a website running the Python tools with free-model inference. WhatsApp voice remains the longer-term product direction. The continuous WhatsApp worker that motivated ADR-001's VM is not required for this first website.

## Decision

Use Cloud Run in `us-central1` for the public Flask/Gunicorn service, with zero minimum instances and a one-instance limit. Keep each anonymous browser workspace in a separate private Cloud Storage SQLite snapshot, guarded by object generations. Temporary container storage is only a working copy. Use Secret Manager for the OpenRouter key and accept free model routes only. Keep the current deterministic tool contracts and human-controlled action commits.

The bounded model/tool/observation loop is implemented in the application. It does not claim to be a connected Hermes runtime. Preserve the existing local prototype and separate browser-only Sites edition. Source is maintained in the user-requested private GitHub repository with agent context files and CI.

Repository update: the user subsequently selected the existing public repository `https://github.com/anirbanhere/Saathi_Home_Agent`. That selection supersedes the original private repository destination without changing the hosted architecture.

## Consequences

This delivers a public HTTPS Python application without an always-connected bridge or always-on VM. Per-visitor snapshots reuse the existing SQLite tools and provide durable demo state with optimistic conflict rejection. They must not be used to coordinate external irreversible effects; real bookings/payments require a transactional operation ledger and stronger identity/approval design. Anonymous cookie ownership does not provide shared household accounts.

OpenRouter free capacity and guardrails can block inference even when the website and tools are healthy. Show those errors clearly; do not substitute paid inference or claim live model success without evidence. GCP hosting/build/storage may consume credits.

## Supersession boundary

This supersedes ADR-001's VM placement for the immediate website. Its provider separation, application-owned state/approval, multilingual goals, and later WhatsApp worker design remain useful future requirements. See `../hosted-deployment.md` for actual deployment and verification.
