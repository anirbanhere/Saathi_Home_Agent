# ADR-0004: Saathi foundation and channel gates

Date:27 October2026. Status: Accepted for the user-authorized Phase0/1 implementation; public launch/vendor eligibility remains unapproved.

## Decision

Adopt [PRD.md](../../PRD.md) as the new product requirements. Add an isolated FastAPI/Pydantic/SQLAlchemy service under `saathi/`, with PostgreSQL/Alembic as the relational deployment target and Redis as an optional wake-up/health service. Use SQLite only for local deterministic demo/unit tests. Do not replace or migrate the existing deployed Flask/GCS visitor edition in this phase. Its prior design is preserved in [legacy architecture](../legacy-home-agents-architecture.md).

Business logic owns identities, grants, canonical previews, approvals, task versions, durable operations and outbox. Model roles, speech and channels are separate typed interfaces. Every Phase1 booking is an owned MOCK clinic operation, labeled throughout. Real outbound actions remain disabled; a configuration flag alone cannot create provider clearance.

Hermes is optional and not required by the domain/channel contract. Its [official Cloud API documentation](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud) describes a direct official gateway; it does not establish Saathi's contractual eligibility. No unofficial bridge is introduced.

`WHATSAPP_PRODUCTION_ELIGIBLE=false` is the default, and this release implements no public WhatsApp registration or webhook executor. [WhatsApp messaging policy](https://whatsappbusiness.com/policy/) has channel/content requirements. The [terms URL](https://www.whatsapp.com/legal/business-solution-terms) redirected to a blocked Facebook login during27 October research. The PRD's detailed country-exception claim is therefore not independently reconfirmed here. Obtain current authoritative terms and offering-specific policy/legal review before changing the gate; do not infer Indian eligibility from another jurisdiction's proceedings.

## Consequences and evidence boundaries

- Keep existing public demo available while the new local service matures; no hidden production migration.
- SQL transactions/unique constraints persist mock effects and outbox atomically. Real nontransactional provider operations later need explicit reconciliation.
- Docker daemon was unavailable during initial local discovery. Compose and PostgreSQL tests must report actual executed evidence separately from SQLite/offline schema checks.
- Sarvam/ElevenLabs adapters can be contract-tested without keys. Mock audio fixture lookup is not speech recognition; live language-quality acceptance remains separate.
- Later public identity, media retention/deletion, real booking providers, template delivery and platform clearance are Phase2 gates.
