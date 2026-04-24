# Family History Research Assistant

Tooling for rigorous family history research against the FamilySearch API, with a local
SQLite working-copy model: curated changes flow *out* to FamilySearch after review, never
auto-sync.

## Layout

```
src/fhra/
  auth/         OAuth2 (Authorization Code Flow, Desktop app, localhost redirect)
  api/          FamilySearch REST client
  gedcom/       GEDCOM ↔ SQLite importer
  db/           SQLite schema, migrations, query helpers
  mcp_server/   MCP server exposing local + FamilySearch tools to Claude
  cli.py        `fhra` CLI entry point
tests/          Pytest suite (config, db, gedcom, auth, api, mcp_server)
data/           Local SQLite DB + GEDCOM files (gitignored)
docs/           Product-side planning artifacts (project brief, API reference, …)
.claude/agents/ Specialized genealogy agents
```

## Prerequisites

- Python 3.11+
- A FamilySearch developer app key (Desktop type). Requires acceptance into the
  [FamilySearch Solution Provider program](https://developers.familysearch.org). Until the
  key arrives, everything that hits the API will be blocked — but the local working copy
  and GEDCOM import work standalone.

## Setup

Preferred: [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run fhra --help
```

Or with plain pip:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
fhra --help
```

## Environment variables

Create a `.env` file at the project root:

```
FHRA_CLIENT_ID=your-familysearch-app-key
FHRA_REDIRECT_URI=http://localhost:5000/auth/familysearch/complete
FHRA_ENV=integration      # integration | beta | production
FHRA_DB_PATH=data/fhra.db
```

## Common commands

```sh
fhra db init                           # create/migrate the local SQLite DB
fhra gedcom import data/my-tree.ged    # import GEDCOM into local working copy
fhra auth login                        # OAuth2 browser flow, caches token
fhra auth whoami                       # verify token / show current user
fhra serve                             # run the MCP server
```

## Agents

Specialized research agents live under `.claude/agents/`. They are available in Claude Code
sessions within this repo via the `Agent` tool.

| Agent | Purpose |
| --- | --- |
| `genealogy-researcher` | Full research workflow for a person or question |
| `source-evaluator` | Assess what a single record does and does not prove |
| `duplicate-analyzer` | Conservative merge-candidate analysis |
| `locality-planner` | Build locality guides and record-set inventories |
| `tree-reconciler` | Diff local working copy vs FamilySearch, produce cleanup plan |
| `proof-writer` | Draft proof summaries and proof arguments |
| `narrative-writer` | Write ancestor snapshots and family-line narratives |

## Documentation

Product-side planning artifacts live in [`docs/`](docs/):

- [`docs/project-brief.md`](docs/project-brief.md) — what we're building, for whom, and
  the next milestone. The starting point for any planning pass.
- [`docs/backend-api.md`](docs/backend-api.md) — the stable contract a UI (or any other
  consumer) can rely on: MCP tools, CLI commands, SQLite schema.

We're planning to use the **BMAD Method** (`npx bmad-method install`) to drive UI design
and implementation. When BMAD is introduced it will generate additional artifacts
(`prd.md`, `architecture.md`, `ux-specification.md`, `stories/`) under `docs/`.

## Status

- ✅ Local working copy: schema, GEDCOM import, query helpers
- ✅ OAuth2 + FamilySearch API client (retry, backoff, sync_log)
- ✅ MCP server with 13 tools (4 local, 9 FamilySearch)
- ✅ 7 specialized research agents
- ⏳ FamilySearch Solution Provider key (application pending)
- ⏭️ UI — next milestone, will be planned via BMAD
- ⏭️ Write-to-FamilySearch review workflow
