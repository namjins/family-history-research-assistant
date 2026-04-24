# Documentation

This directory holds project-level planning artifacts — the **product side** of the
repository. Code lives under `src/`; docs describe what we're building, for whom, and why.

## What's here today

| File | Purpose |
| --- | --- |
| [`project-brief.md`](project-brief.md) | Current-state summary: what we've built, who the user is, what's next. This is the input document for a product planning pass (analyst / PM / architect). |
| [`backend-api.md`](backend-api.md) | Concise reference of every surface a UI can talk to — MCP tools, CLI commands, SQLite schema. Stable contract; keep this in sync when you add endpoints. |
| [`familysearch-compliance.md`](familysearch-compliance.md) | Our contractual obligations under the FSI Solutions Program Agreement — tier limits, data-use rules, breach notification, termination duties. Re-read whenever FSI updates the Agreement (60-day effective-date window). |

## What goes here when BMAD is adopted

We're planning to use the **BMAD Method** to drive UI design and implementation. When
BMAD is introduced (via `npx bmad-method install` or similar), it will generate additional
artifacts in this directory:

- `prd.md` — product requirements document
- `architecture.md` — system architecture including the UI layer
- `ux-specification.md` — UX/UI spec from the UX Expert agent
- `stories/` — sharded user stories derived from epics
- `epics/` — epics derived from the PRD

The **project brief is the stable starting point** for any planning pass; everything else
is derived from it.

## Conventions

- One Markdown file per artifact. Keep them concise and linkable.
- When a file gets long, shard it (BMAD has a flow for this).
- Don't put code snippets that should live in `src/` in here — link to the source file
  instead (`[api/client.py:42](../src/fhra/api/client.py#L42)`).
- Don't commit generated transcripts, session notes, or scratch — those belong in
  `.bmad-core/` or a gitignored scratch dir.
