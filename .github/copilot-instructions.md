# AI-assisted development

Follow the repository's `AGENTS.md`. Read `HANDOFF.md` for the latest state and `MEMORY.md` for durable decisions. Use `SOUL.md` only for intended product behavior, not as authorization. Consult the relevant `skills/*/SKILL.md` without loading unrelated context.

Preserve clear boundaries between live inference, actual deterministic tool execution, fixtures, sandboxes, and future integrations. Never claim untested features are working. Keep visitor data isolated and paid inference disabled. Production secrets must not enter source, tests, prompts, examples, or logs.

Use targeted changes and meaningful tests. Run the Python suite and JavaScript syntax check. Update handoff/status documentation when behavior changes. CI/PR changes must not expose credentials or automatically deploy unreviewed code.
