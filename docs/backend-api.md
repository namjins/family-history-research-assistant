# Backend API Reference

What a UI (or any other consumer) can call. This is the stable contract between the Python
backend and whatever frontend we build. Keep this in sync when you add endpoints, MCP
tools, or schema tables.

## Surface area at a glance

The backend exposes three layers:

1. **Python library** — direct imports from `fhra.*`. Most useful for tests and for
   in-process UIs.
2. **CLI** — `fhra` command (see [src/fhra/cli.py](../src/fhra/cli.py)).
3. **MCP server** — stdio JSON-RPC, suitable for Claude and any other MCP client. This
   is the primary surface for agent-driven UIs.

A web UI would most likely run the MCP server in-process OR call the Python library
directly, depending on architecture. The MCP surface is the most stable and the
best-documented, so lean on it first.

## Data model

SQLite file at `data/fhra.db`. Schema: [src/fhra/db/schema.sql](../src/fhra/db/schema.sql).

| Table | Rows (today) | What it is |
| --- | ---: | --- |
| `persons` | 4,696 | Individuals, identified by internal UUID, with `fs_person_id` (FamilySearch PID) and `gedcom_xref`. |
| `facts` | 13,566 | Events/attributes on a person: BIRT, DEAT, MARR, RESI, etc. Each has `origin` (`gedcom` \| `familysearch` \| `local_edit`). |
| `relationships` | 7,699 | Parent-child and spouse edges. Directional via `role1`/`role2`. |
| `sources` | 0 | Source citations. Empty on the current GEDCOM — filling this is a research goal. |
| `person_sources` | 0 | Many-to-many link between persons/facts and sources. Unique on `(person, source, fact_id, origin)` so the same citation can exist with different provenance. |
| `research_tasks` | 0 | Research to-do queue, linked to persons. Not yet exposed in any UI. |
| `sync_log` | 0 | Append-only audit of FamilySearch API calls — endpoint, params, status. |

### Origin discipline

The `origin` column on facts and `person_sources` is load-bearing:

- `gedcom` — imported from a GEDCOM file. Gets wiped and re-inserted on re-import.
- `familysearch` — fetched via the API. Survives GEDCOM re-imports.
- `local_edit` — added or edited by the user in this tool. Survives everything.

Any UI write path must respect this: user edits go in as `local_edit`, never as `gedcom`.

## MCP tools

See [../CLAUDE.md](../CLAUDE.md) for the full tool inventory with argument descriptions.
Summary here:

### Local (no auth required)

| Tool | Signature |
| --- | --- |
| `local_search_persons` | `(surname?, given_names?, include_living=False, limit=25) -> JSON` |
| `local_get_person` | `(person_id?, fs_person_id?, include_living=False) -> JSON` |
| `local_get_relationships` | `(person_id) -> JSON` |
| `local_recent_sync_events` | `(limit=25) -> JSON` |

Living persons are redacted by default. Pass `include_living=True` to bypass.

### FamilySearch (requires `fhra auth login`)

| Tool | Signature |
| --- | --- |
| `fs_whoami` | `() -> JSON` |
| `fs_get_person` | `(fs_person_id) -> JSON` |
| `fs_get_person_with_relationships` | `(fs_person_id) -> JSON` |
| `fs_get_person_sources` | `(fs_person_id) -> JSON` |
| `fs_get_person_matches` | `(fs_person_id) -> JSON` |
| `fs_get_ancestry` | `(fs_person_id, generations=4) -> JSON` |
| `fs_search_persons` | `(given_name?, surname?, birth_place?, birth_date?, death_place?, death_date?, father_surname?, mother_surname?, spouse_surname?, count=20) -> JSON` |
| `fs_search_records` | `(given_name?, surname?, place?, birth_date?, death_date?, collection?, count=20) -> JSON` |
| `fs_place_search` | `(text, count=10) -> JSON` |

Every `fs_*` call appends a row to `sync_log`.

## CLI commands

| Command | Purpose |
| --- | --- |
| `fhra db init` | Apply schema (idempotent). |
| `fhra gedcom import <path>` | Import a GEDCOM file into the local working copy. Idempotent for gedcom-origin data; preserves `familysearch` and `local_edit`. |
| `fhra auth login` | Browser-based OAuth2 flow against FamilySearch. Caches token at `data/.tokens.json`. |
| `fhra auth whoami` | Verify cached token by calling `/platform/users/current`. |
| `fhra auth status` | Local-only token status (no network call). |
| `fhra serve` | Run the MCP server over stdio. |

## Python library — key modules

| Module | Exports |
| --- | --- |
| `fhra.config.load_config` | Parses env vars into a typed `Config`. |
| `fhra.db` | `open_db`, `init_db`, and all query helpers (`upsert_person`, `search_persons`, `upsert_fact`, `upsert_relationship`, `upsert_source`, `link_person_source`, `log_sync_event`, `recent_sync_events`, `redact_if_living`, …). |
| `fhra.gedcom.import_gedcom` | The GEDCOM → SQLite importer. Returns `ImportStats`. |
| `fhra.auth` | `login_interactive`, `refresh_if_needed`, `load_token`, `save_token`, `TokenSet`. |
| `fhra.api.FamilySearchClient` | REST client. Injectable `transport` and `sleep` for testing. |
| `fhra.mcp_server.build_server` | Construct a `FastMCP` instance (injectable config, for tests). |

## What's deliberately not here

- **Write-to-FamilySearch endpoints.** The REST client implements only reads. Adding
  writes is gated on Production access + a review workflow design.
- **Place authority caching.** Every `fs_place_search` call hits the API. A cache layer
  is straightforward to add when we care about it.
- **Real-time streaming of agent output.** Each MCP tool returns JSON in one shot.
  A streaming UI would need a separate transport.
