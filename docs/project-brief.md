# Project Brief — Family History Research Assistant

## One-line summary

A local-first tool and agent suite for rigorous family history research against the
FamilySearch API, with a SQLite working copy so curated changes can be reviewed before
being pushed to the shared tree.

## Who this is for

The primary user is a single researcher (the author) who:

- Maintains a family tree primarily on FamilySearch (the shared tree)
- Uses RootsMagic 11 locally as a personal genealogy database
- Is a member of The Church of Jesus Christ of Latter-day Saints — temple/ordinance
  workflows and Church terminology are part of the context
- Wants AI assistance that is **rigorous, source-backed, and conservative about
  conclusions**, not a chatbot that invents relationships

Secondary audience (if open-sourced): other careful genealogists who want agent-assisted
research without ceding evidence judgment to the model.

## Problem statement

Genealogy research is mostly about three things that don't fit well in existing tools:

1. **Evidence correlation** — tying facts together across records, flagging conflicts,
   distinguishing direct from indirect from negative evidence.
2. **Source discipline** — never concluding more than the records support, always
   tracing claims back to the source.
3. **Tree maintenance** — keeping a shared tree clean: merging duplicates carefully,
   attaching missing sources, fixing unsupported relationships, without clobbering other
   researchers' work.

RootsMagic and FamilySearch's native UI handle (1) and (3) partially but leave the
researcher to do all of (2) manually. There's no good place where an AI can help
*without being dangerous* — invented citations and unsupported merges corrupt the tree.

This project's design answer: a **working-copy model** (local SQLite is the research
workspace, FamilySearch is not the in-progress source of truth) plus **specialized
agents** whose prompts enforce evidence discipline.

## Current state (as of 2026-04-24)

### What's built

- **Python package** (`src/fhra`) with:
  - `db/` — SQLite schema and query helpers for the local working copy
  - `gedcom/` — GEDCOM → SQLite importer (RootsMagic 11 exports tested)
  - `auth/` — OAuth2 Authorization Code Flow with PKCE for Desktop apps
  - `api/` — FamilySearch REST client with retry / backoff / rate limiting
  - `mcp_server/` — MCP server exposing local + FamilySearch tools to Claude
  - `cli.py` — `fhra` CLI (db init, gedcom import, auth, serve)
- **Six specialized agents** under `.claude/agents/`: genealogy-researcher,
  source-evaluator, duplicate-analyzer, locality-planner, tree-reconciler, proof-writer,
  narrative-writer.
- **Test suite**: 82 tests passing across config, DB, GEDCOM importer, OAuth, API client,
  MCP server.
- **Imported tree**: 4,696 persons, 7,699 relationships, 13,566 facts, all with
  FamilySearch PIDs. No sources attached on the GEDCOM side — filling that gap is the
  first research goal.

### What's not built

- **No UI.** Today the interface is the CLI plus Claude (via the MCP server). This is
  what the next planning pass is for.
- **No FamilySearch write path.** The architecture is read-only; a curated
  review-before-push workflow is explicitly a later milestone — and see the
  [tier ceiling below](#tier-ceiling).
- **No live FamilySearch calls yet.** The Solution Provider application is the critical
  path blocker; the API client is tested against mocks only.

### Tier ceiling

The FSI Solutions Program Agreement defines three tiers. As an individual researcher we
apply to the **Innovator** tier, which has two hard ceilings worth planning around:

1. **No Production API access.** *"Innovators may only be granted access to the FSI Beta
   API or the Integration API."* The Production API — the one that writes to the real
   shared tree — is legally off-limits at this tier. Upgrading to Compatible Solution
   Provider (for Production access) requires **establishing a business entity** and
   passing FSI's compatibility review.
2. **No record-content display.** FamilySearch prohibits third-party apps from rendering
   indexed record fields, transcriptions, or images — users must be redirected to
   FamilySearch.org. See the constraint list below.

For most of what we want to do — reading the shared tree, analyzing ancestors, surfacing
duplicates, running reconciliation — Beta access is enough. Beta contains an old snapshot
of production data, so real deceased ancestors are findable there. Writes to real live
data are a larger, later milestone that probably requires tier upgrade.

Full obligations: [`docs/familysearch-compliance.md`](familysearch-compliance.md).

## Next milestone: a useful UI

This is what we're preparing to plan via BMAD.

### What the UI needs to enable

At a minimum, it should let the researcher:

1. **See the tree as a navigable graph** — start at a person, walk ancestors / descendants,
   see who has facts, sources, or problems flagged.
2. **See local-vs-FamilySearch diffs** for any person or line, with the output of the
   `tree-reconciler` agent surfaced visually.
3. **Queue research tasks** — the `research_tasks` table exists in the schema; today
   nothing exposes it.
4. **Review agent findings** — when an agent runs a reconciliation, duplicate analysis,
   or research pass, the UI should surface the finding with clear provenance (which
   records were consulted, what the agent concluded, what the unresolved risks are)
   rather than burying it in a chat transcript.
5. **Stage edits** locally before pushing them to FamilySearch, with a visible "changes
   pending review" queue. This is where the working-copy discipline becomes visible.
6. **View the audit log** (`sync_log`) — every FamilySearch API call is recorded; the
   UI should make that inspectable.

### What it does NOT need to do

- Re-implement GEDCOM import UI — CLI is fine for that.
- Replace RootsMagic for bulk tree editing — RootsMagic is the heavy editor; this tool is
  for research, cleanup, and review.
- Be a web app for anyone else to use — local-first, single user.

### Open architectural questions for the planning pass

- **Packaging**: desktop app (Tauri / Electron), local web UI served from Python on
  localhost, or TUI (Textual)? OAuth already uses a browser callback, so a local web
  UI adds zero new auth plumbing. Desktop wrapping adds distribution complexity but
  could feel more polished.
- **Frontend stack**: if web, vanilla HTML + HTMX is minimum-viable; React / Svelte
  if the graph visualization gets rich.
- **Agent UX**: how should agent findings be rendered? As persistent "research notes"
  attached to a person? As a streaming transcript? Both?
- **Write path UX**: what does "review pending changes" look like when there may be
  many small edits across many persons?

## Constraints

- **FamilySearch API compliance**: Full contractual reference at
  [`docs/familysearch-compliance.md`](familysearch-compliance.md). Key rules the UI and
  any pipeline must respect: honor 429 Retry-After; log every API call; gate writes behind
  explicit confirmation; no bulk export of FSI data; no scraping; identify ourselves via
  User-Agent.
- **No third-party display of historical record content.** FamilySearch explicitly
  prohibits third-party apps from showing indexed record fields, transcriptions, or
  images from the historical-records collection (verified 2026-04-24 against
  [Integrating Hints](https://developers.familysearch.org/main/docs/integrating-hints)).
  What a UI **may** render: person-match summary (persona name, collection title, record
  ID, match score, confidence, status). What it **must not** render: full record detail.
  The UI must link out to FamilySearch.org for full viewing. Designing a record-detail
  screen would fail the Compatible Solution review. The Bulk Record Broker (BRB) program
  permits local record copies but requires a separate agreement; that's not our path.
- **Privacy**: living-person details must not leak. Local DB already supports this
  (`is_living` column + `redact_if_living` helper).
- **No invented data**: any UI feature that generates text from the model must cite
  sources and must never fabricate film numbers, citations, or URLs. This is a
  product-level rule, enforced in the agent system prompts today.
- **LDS terminology**: use full Church name; be respectful in temple/ordinance contexts.

## Non-goals

- Social / collaboration features. This tool is single-user.
- Tree hosting. FamilySearch is the shared tree; we don't replace it.
- Full GEDCOM editor. RootsMagic already does that.
- Mobile. Desktop/laptop only.
