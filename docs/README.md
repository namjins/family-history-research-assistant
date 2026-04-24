# Documentation

This directory holds project-level planning artifacts — the **product side** of the
repository. Code lives under `src/`; docs describe what we're building, for whom, and why.

## What's here today

| File | Purpose |
| --- | --- |
| [`project-brief.md`](project-brief.md) | Current-state summary: what we've built, who the user is, what's next. This is the input document for a product planning pass (analyst / PM / architect). |
| [`backend-api.md`](backend-api.md) | Concise reference of every surface a UI can talk to — MCP tools, CLI commands, SQLite schema. Stable contract; keep this in sync when you add endpoints. |
| [`familysearch-compliance.md`](familysearch-compliance.md) | Our contractual obligations under the FSI Solutions Program Agreement — tier limits, data-use rules, breach notification, termination duties. Re-read whenever FSI updates the Agreement (60-day effective-date window). |

## BMAD-generated artifacts

**BMAD Method v6.3+ writes to `_bmad-output/`, not here.** We're planning to use BMAD to
drive UI design and implementation. When BMAD agents are run, they produce:

- `_bmad-output/planning-artifacts/` — PRD, architecture, UX specification, epics
- `_bmad-output/implementation-artifacts/` — sharded stories, implementation plans

**Don't hand-edit those generated artifacts.** Re-run the relevant BMAD agent (via
Claude Code Skills under `.claude/skills/bmad-agent-*`) if the underlying inputs change.

The **project brief in this directory is the stable starting point** — everything BMAD
generates is derived from it.

## Conventions

- One Markdown file per artifact. Keep them concise and linkable.
- When a file gets long, shard it (BMAD has a flow for this).
- Don't put code snippets that should live in `src/` in here — link to the source file
  instead (`[api/client.py:42](../src/fhra/api/client.py#L42)`).
- Don't commit generated transcripts, session notes, or scratch — those belong in
  `.bmad-core/` or a gitignored scratch dir.
