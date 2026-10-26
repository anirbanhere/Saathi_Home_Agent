# ADR-001: Voice-first Home Agents with replaceable models on GCP

Status: Proposed technical design; user product constraints and demo-calendar choice confirmed.
Date: 26 October 2026.

## Context

Home Agents has an offline browser prototype with reusable tools and SQLite persistence. The Saathi reference brief supplies a focused appointment workflow but assumes a Meta reasoning model and Modal inference. The user requires model interchangeability, predominantly WhatsApp voice use, the original four Indian languages, and consideration of available GCP resources. Meta API access is pending.

## Decision

Use one application-owned task engine with three domain profiles. Hermes runs bounded, isolated model/tool loops; application code owns identity, permission checks, approvals, execution, receipts, reminders, and recovery. Separate the reasoning, ASR, TTS, vision, and messaging contracts. Start with an evaluated free-only OpenRouter reasoning profile, retain a Meta adapter, and test provider switching with persistent task state.

Make appointment booking against an owned, clearly labeled demo clinic calendar the first complete workflow. A slot selection requires explicit action approval before commit. Keep cooking and inventory in scope after that vertical slice.

Propose one Compute Engine application host with persistent-disk SQLite and consistent off-host backups for the hackathon. Keep speech independently deployable. Use private Cloud Storage for media and Secret Manager for credentials. Migrate the state store to PostgreSQL before multiple application hosts. Confirm actual GCP credits, quotas, pricing, and channel eligibility before provisioning.

## Alternatives considered

| Alternative | Assessment |
| --- | --- |
| Fixed Muse plus Modal GPU | Adds model access and hosting assumptions; conflicts with the user's interchangeable-model and GCP direction |
| Run every component in Cloud Run with local SQLite | Stateless compute is useful, but local writable storage is not durable and a continuous bridge has a different lifecycle |
| Cloud Run plus managed PostgreSQL immediately | Good managed alternative for an official HTTP-only channel; additional baseline cost and migration work before the first workflow |
| Three independent agents and databases | Duplicates identity, memory, approvals, and kitchen state; unnecessary coordination for this scope |
| Expose the present localhost HTTP server publicly | Its trusted single-owner boundary is unsuitable for a hosted multi-user service |
| Treat generic OpenAI-compatible URLs as full model compatibility | Tool support, language quality, context limits, output schemas, and retry semantics still differ |

## Consequences

Changing providers should require configuration/adapter work and evaluation, not rewriting booking tools. It does not guarantee identical results across models. Durable application state prevents a model swap from becoming a second booking attempt.

The VM approach is economical in architecture complexity but requires patching, supervision, backup, and recovery. SQLite deliberately limits the first deployment to one application host. Speech latency and GPU costs must be measured; open weights do not imply free inference.

WhatsApp eligibility for a general-purpose assistant serving Indian numbers remains unresolved. The unofficial Hermes bridge is a prototype option with stated risks, not an automatic production decision. Development can proceed against the same backend through a labeled web voice client.

## Revisit when

- The messaging provider confirms the supported WhatsApp route and outbound reminder requirements.
- Actual project quotas, regional costs, or speech benchmarks favor a different GCP topology.
- Concurrency or availability requires multiple application hosts and PostgreSQL.
- A Meta model is available and official hackathon rules establish required model usage.

See `../home-agents-redesign.md` for source links, contracts, privacy boundaries, and migration details.
