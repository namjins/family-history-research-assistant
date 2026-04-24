---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - docs/project-brief.md
  - docs/familysearch-compliance.md
workflowType: 'research'
lastStep: 6
research_type: 'market'
research_topic: 'Open-source viability and FSI API-approval posture for an evidence-disciplined, agent-assisted genealogy research tool'
research_goals: 'Inform strategic decision on whether to invest in open-sourcing the Family History Research Assistant and pursue Compatible Solution Provider status with FamilySearch International. Specifically: (1) is there a real audience for an OSS release, (2) is this the kind of tool FSI would approve for production API access, and (3) if yes to both, what does the go-to-market and approval path look like?'
user_name: 'Marc'
date: '2026-04-24'
web_research_enabled: true
source_verification: true
---

# Research Report: Market — OSS Viability & FSI Approval Posture

**Date:** 2026-04-24
**Author:** Marc
**Research Type:** Market Research
**Analyst:** Mary (BMad)

---

## Research Overview

**Headline finding (both tracks): Yes on both counts — with specific conditions.**
A defensible niche exists for a tool that combines evidence discipline, live
FamilySearch data, a local working copy, and specialized research agents; no other
public tool ticks all four columns today. FSI's approval posture is favorable for
tools that demonstrate *value back to the shared tree* (source attachment,
duplicate analysis, relationship cleanup) — which is exactly what fhra's existing
agents are designed to do. The primary gates to action are (1) shipping a
low-friction install path via the planned UI, and (2) forming a business entity
before pursuing Gallery listing / Compatible Solution Provider status. The full
recommendation, phased roadmap, and 30/60/90-day next steps are in **§6 Strategic
Synthesis and Recommendation** at the bottom of this document.

This research evaluates two intertwined questions that inform a single strategic
decision for the Family History Research Assistant project:

1. **Open-source viability** — if we release this publicly under MIT, is there a
   real audience beyond the primary researcher? Who are the likely adopters,
   what are their unmet needs, and does our positioning occupy a gap in the
   existing open-source genealogy ecosystem?
2. **FSI approval posture** — given FamilySearch's Solution Provider tier
   structure and Compatibility Review process, is this the shape of tool FSI
   tends to approve for production API access? What patterns do approved
   Solutions share, and how does our design align or conflict?

The research is structured in two parallel tracks. Track 1 (Open Source) uses
moderate-depth methodology — specific competitor analysis anchored by Gramps,
webtrees, and any AI-era entrants, plus community-adoption signals from
GitHub / Reddit / specialist forums. Track 2 (FSI Approval) uses broader
survey methodology — a completeness-oriented scan of the FSI Solutions Gallery,
published approval criteria, precedents for open-source and AI-assisted apps,
and any policy signals about agent-era tooling.

---

## Research Initialization

### Research Understanding Confirmed

- **Topic:** Open-source viability and FSI API-approval posture for an
  evidence-disciplined, agent-assisted genealogy research tool.
- **Goals:** Inform the strategic investment decision on open-sourcing +
  pursuing Compatible Solution Provider status.
- **Research Type:** Market Research
- **Date:** 2026-04-24

### Research Scope

**Track 1 — Open-source viability (moderate-depth):**

- Landscape of open-source genealogy tools (Gramps, webtrees, others)
- GitHub and community signals — stars, forks, commit cadence, forum activity
- Presence or absence of OSS projects using the FamilySearch API at all
- Presence or absence of OSS projects using AI / LLM agents for genealogy
- User archetype fit: does the "rigorous researcher who wants evidence-disciplined
  AI" audience actually show up in community discussions, or is it aspirational?

**Track 2 — FSI approval posture (broad survey):**

- Scan of FSI Solutions Gallery — categorize existing Solutions by type
- Identify OSS entries in the Gallery, if any
- Identify AI / agent-era entries in the Gallery, if any
- Review published App Approval Considerations and Compatibility Checklist
- Identify any policy signals (positive or negative) about agent-driven tooling,
  MCP-style integrations, or LLM-assisted research
- Map a realistic progression path: Innovator → Registered → Compatible

**Research methodology:**

- Current web data with source verification (multiple independent sources for
  load-bearing claims)
- Explicit confidence labels — direct / strong / moderate / weak / speculative
- Citation of every source consulted; no invented URLs, counts, or quotes
- Gaps flagged honestly where public information is thin
- Full alignment with project norms: "never invent facts, sources, or URLs"

### Strategic Decision This Research Informs

The research output should enable a clear go / no-go / conditional-go on each
of the following investments:

- (a) Publicly open-source the repo on GitHub now (already done) vs. wait →
      *answer: already public; research informs whether to promote it or keep low-profile*
- (b) Draft community-facing materials (landing page, intro post, demo video)
- (c) Invest in a Compatible Solution Provider application (involves forming a
      business entity, ~$199/yr fee, pre-release compatibility review)
- (d) Continue as purely personal tool and leave (b) and (c) for later

### Next Steps

1. ✅ Step 1 — Initialization and scope setting (current step)
2. Adapted customer insights — map user archetypes for OSS track + FSI partner
   archetypes for approval track
3. Adapted pain-point analysis — what current OSS genealogy tools fail at;
   what FSI-approval gatekeepers worry about
4. Adoption and approval decision drivers
5. Competitive analysis — OSS landscape + FSI Solutions Gallery scan
6. Strategic synthesis and recommendation

**Note on step adaptation:** The generic market-research step names
("customer-behavior," "customer-decisions," "competitive-analysis") will be
applied to this research's two-track structure. Track 1's "customers" are
prospective OSS adopters; Track 2's "customers" are the FSI review process
and Solutions ecosystem. I'll signal the adaptation at each step.

**Research Status:** Scope confirmed by user on 2026-04-24.

---

## User Archetypes and Segment Analysis

**Step adaptation note.** The generic step ("Customer Behavior and Segments") translates
here to two parallel segment analyses: (A) **prospective OSS adopters**, and
(B) **the FSI Solutions ecosystem** our project would need to fit within. Both are
treated with the same rigor — demographic, psychographic, behavioral — but the
"customer" differs. Confidence labels throughout: **[direct]** sourced from an
authoritative page or repo; **[strong]** multiple corroborating sources; **[moderate]**
single credible source, plausible; **[weak]** inferential; **[speculative]** reasoned
extrapolation.

### A. Prospective OSS adopters

#### A1. Segment sizing and current homes

The starting point is understanding where evidence-minded genealogists currently live in
the OSS world.

- **Gramps** is the dominant open-source genealogy platform. Desktop Python app released
  April 2001; as of v6.0 it ships in 28 languages, with 43 language translations existing
  overall. **[direct — gramps-project.org]** Described as "best for tech-savvy
  genealogists who want full data control and free software." **[strong — multiple
  comparison sites]** ([Gramps comparison, martinroe.com](https://martinroe.com/blog/best-genealogy-software-in-2025-a-practical-comparison/);
  [Wikipedia](https://en.wikipedia.org/wiki/Gramps_(software)))
- **webtrees** is the PHP/MySQL web-based equivalent — collaborative, server-hosted,
  fork of PhpGedView. **[direct — wikipedia / alternativeto.net]** Appeals to a slightly
  different user (willing to host a web app) but same "data ownership" ethos.
- **Smaller OSS projects:** Ancestris, GeneWeb, FamilyGem (Android). **[moderate]**
- **Paid-but-gathering-OSS-adjacent users:** RootsMagic, Family Tree Maker, Legacy
  Family Tree — commercial desktop products whose users overlap heavily with Gramps
  users in disposition (anti-lock-in, data-ownership, serious hobbyist). **[strong]**

**No adoption counts are publicly published** for Gramps or webtrees — neither uses a
telemetry model. This is worth flagging: market sizing will always be a qualitative
argument, not a number. **[direct observation — no source gave hard user counts]**

#### A2. Demographic and psychographic profile of the segment

Drawing on the Gramps/webtrees positioning material, the AlternativeTo user reviews, and
Reddit/community discussion patterns, the shared profile of this segment is remarkably
consistent:

- **Demographic** **[strong]**
  - Older skew — genealogy in general skews 40+; serious hobbyist sub-segment 50+.
  - Global distribution — Gramps' 43-language translation effort reflects this.
  - Mixed technical fluency, but at the "serious" end, strong overlap with
    developer / IT-adjacent backgrounds.
- **Psychographic** **[strong]**
  - **Primary values: data ownership and privacy.** Strong preference for software that
    keeps data local rather than cloud-locked. Skeptical of subscription models.
  - **Secondary value: evidence rigor.** Self-identifies as "serious" or "rigorous" vs.
    the "casual / family-story" user.
  - **Third value: methodological training.** Aware of frameworks like the
    Genealogical Proof Standard (GPS) and the Evidence Explained citation standard;
    willing to learn terminology.
  - **Skepticism of AI** — strongly held. Every serious article on AI + genealogy
    emphasizes verification, cross-checking, and "treat AI output as hints not facts."
    **[direct — aigenealogyinsights.com, amyjohnsoncrow.com, legacytree.com blog,
    familyhistoryfoundation.com]**
- **Behavioral** **[moderate → strong]**
  - Active in forums (Reddit's r/Genealogy, Facebook groups, Gramps mailing lists).
  - Willing to download and configure desktop software (Gramps is not trivial to set up).
  - Values software longevity — Gramps' 25-year history is an asset, not a curiosity.
  - Buys domain-specific tools (RecordSeek, Evidentia) for focused workflows.

#### A3. The LDS sub-segment

Our primary user is a member of The Church of Jesus Christ of Latter-day Saints, so the
LDS researcher sub-segment is directly relevant:

- Historically, LDS members are an anchor user base for FamilySearch (the shared tree
  grew out of Church members' family-history work).
- FamilySearch Library partner apps get a specific "LDS features" compatibility callout
  in the Solutions Gallery ([Cyndi's List](https://www.cyndislist.com/familysearch/compatible/)).
  **[direct]**
- This is both a secondary audience (other LDS researchers who value temple/ordinance
  workflows and respectful Church terminology) and a positioning asset (alignment with
  FSI's core user cohort is helpful for Compatible Solution review). **[moderate]**

#### A4. AI-era competitive presence — the part that matters

This is where the OSS track gets interesting. A small but active community of AI-genealogy
tool-builders has emerged, and mapping it tells us where we'd sit:

- **Steve Little's "Open-Genealogy" repo** ([github.com/DigitalArchivst/Open-Genealogy](https://github.com/DigitalArchivst/Open-Genealogy))
  — **40 stars, 73 commits, 1 fork, CC BY-NC-SA 4.0**, last release v8.5.2
  on 2026-04-23 (literally yesterday relative to this research date). **[direct — GitHub]**
  Contains the "Genealogical Research Assistant" (GRA): prompt + Claude Code skill +
  Custom GPT + Gemini Gem + Cowork skill. Applies the Three-Layer Evidence Model
  (source / information / evidence) and all five GPS elements (exhaustive research,
  complete citations, thorough analysis, conflict resolution, written conclusions).
  ([vibegenealogy.ai — GRA announcement](https://vibegenealogy.ai/p/the-genealogical-research-assistant-claude-code-cowork-skill-prompt))
  **Philosophically this is extremely close to our agent framework.** Critically: GRA
  **does not use APIs** — it processes only user-provided documents, and does not
  connect to FamilySearch or Ancestry. **[direct quote from GRA page]** Single-author
  project; Steve Little is AI Program Director at the National Genealogical Society —
  a voice of real authority in this space. **[direct]**
- **David Ulbrich's `familysearch-mcp` (TypeScript)** — listed on PulseMCP, Glama,
  Playbooks, and mcpmarket.com as an MCP server for FamilySearch API, released
  2025-03-24. Exposes auth, person search/retrieval, ancestry up to 8 generations,
  descendants up to 3, and records search. **Pure API wrapper — no working copy, no
  specialized agents, no GEDCOM integration.** [[PulseMCP listing](https://www.pulsemcp.com/servers/dulbrich-familysearch)]
  **Adoption signal is weak**: GitHub repo at `dulbrich/familysearch-mcp` currently
  returns 404 (may have been moved, renamed, or taken private); the PulseMCP page
  shows 0 stars. **[direct — 404 confirmed on repo URL; PulseMCP page observed]**
- **`cabout-me/gramps-mcp` (Python, AGPL-3.0)** — 30 stars, 27 commits, v1.1.0 in
  September 2025. **[direct — pulsemcp, repo]** Tool wrapper for Gramps Web API; 16
  tools across search/retrieval, data management, analysis. No agents. Different
  target (Gramps rather than FamilySearch) but same MCP-server-for-genealogy pattern.
- **Ancillary MCP servers**: `airy10/GedcomMCP` (generic GEDCOM querying),
  `reeeeemo/ancestry-mcp` (Python, GEDCOM-file focused despite the name).
  **[direct — GitHub]**
- **FamilySearch's own AI rollout**: FamilySearch is shipping AI-indexed records,
  full-text search, an AI help chatbot, and an AI research assistant inside their
  own platform. [[FamilySearch blog](https://www.familysearch.org/en/blog/ai-developments-genealogy)]
  **[direct]** Platform-vs-third-party dynamic — they are both the API host AND a
  (potential) competitor for this user's attention.

#### A5. The gap we'd occupy

Cross-referencing the above:

| Tool | FS API | Working copy | Specialized agents | Evidence discipline baked in |
| --- | --- | --- | --- | --- |
| Steve Little's GRA | ❌ | ❌ (documents only) | Single-persona prompt | ✅ (GPS) |
| Ulbrich's fs-mcp | ✅ | ❌ | ❌ (tool wrapper) | ❌ |
| cabout-me/gramps-mcp | ❌ (Gramps API) | ❌ | ❌ | ❌ |
| **This project (fhra)** | **✅** | **✅ (SQLite+GEDCOM)** | **✅ (7 agents)** | **✅** (in agent prompts) |

**No other OSS tool in the public landscape today combines all four.** **[strong —
based on explicit repo feature checks above; not speculative]** That is a real, defensible
niche, not a manufactured one. The positioning sentence writes itself: *"GRA-style
evidence discipline + live FamilySearch API + local working copy with review-before-push."*

**Caveat — confidence check.** I've surveyed the most visible projects and registries
(GitHub, PulseMCP, Glama, Playbooks, mcpmarket). I haven't exhaustively crawled every
private GitHub repo or niche forum. So "no other tool combines all four" is defensible
for the public, discoverable market; there may be a private/commercial project we
haven't found. If that matters, one more directed search or a mention in a
FamilySearch/NGS forum could close the gap.

### B. FSI Solutions ecosystem analysis

Treating the FSI ecosystem as "the customer the project must fit" — who's already in,
what do they look like, and how do we map onto the approval pathways?

#### B1. Solutions Gallery catalog — current inventory

The public-facing Solutions Gallery at `familysearch.org/innovate/solutions-gallery/` is
a dynamic JS-rendered page that blocks direct server-side fetching — making a full
programmatic catalog difficult from a research environment. However, Cyndi's List — a
long-running authoritative genealogy directory — maintains a catalog of
FamilySearch-Compatible products that gives us a reliable taxonomy:
**[direct — [cyndislist.com/familysearch/compatible](https://www.cyndislist.com/familysearch/compatible/)]**

**26 FamilySearch-Compatible products catalogued**, spanning these categories:

| Category | Example products |
| --- | --- |
| Desktop genealogy software | RootsMagic, Legacy Family Tree, Ancestral Quest, Family Historian, MacFamilyTree, Family Tree Maker, PAF |
| Mobile apps | MobileFamilyTree, Legacy Family Tree Mobile |
| Research / analysis tools | **Evidentia, Kinpoint, RecordSeek, Puzzilla Descendant Viewer, Relative Finder** |
| Charting / report generation | Charting Companion, Family ChartMasters, Progeny Software |
| Cemetery / records | BillionGraves |
| Digital archives | Historic Journals |
| Educational resources | BYU FHL YouTube webinar series |
| Utility / integration | FamilyInsight |

**Observations of high relevance to our positioning:**

1. **A "Research / analysis tools" category exists and is a real cohort.** Evidentia
   in particular — a source-analysis-focused tool for applying the Genealogical Proof
   Standard — is philosophically the closest analogue to our project among FSI-approved
   apps. Its existence *in the approved ecosystem* is strong evidence that FSI is
   receptive to evidence-discipline tooling. **[strong]**
2. **No open-source projects appear in the Cyndi's List roster.** Every catalogued
   product is commercial or freemium. That's either: (a) a gap we'd be one of the
   first to fill, or (b) a signal that OSS projects face an uphill path in getting
   Compatible status. The truth is probably closer to (a) — there's no policy barrier
   in the Agreement; there's simply a sparse supply because the approval overhead is
   non-trivial for unpaid contributors. **[moderate — inferential]**
3. **No AI / agent / MCP-based apps appear.** This is consistent with the Agreement
   v6 being last updated in 2020 — pre-dating the MCP era. We'd likely be first-wave
   in this shape of app. **First-mover is both opportunity (set category norms) and
   risk (reviewers may ask novel questions).** **[moderate]**

#### B2. FSI approval pathways — mapping the customer journey

FSI's three-tier structure (Innovator / Registered / Compatible) described in
`docs/familysearch-compliance.md` is the "sales funnel" we'd traverse:

- **Innovator** — where we start and are currently applying. Individuals allowed.
  Beta + Integration APIs only. **[direct — FSI Solutions Program Agreement, project's
  own compliance doc]**
- **Registered Solution Provider** — requires business entity + $199/yr. No Production
  API.
- **Compatible Solution Provider** — business entity + $199/yr + compatibility review
  passed. Required for Production API (writes to live shared tree).

**Implication:** Our current tier fits our current scope. For the read-only
research use-case, Innovator + Beta is sufficient. Moving to writes requires entity
formation + review — a known milestone, not a surprise.

#### B3. What FSI reviewers seem to weight

Direct signals from what's catalogued:

- **Working WITH the shared tree, not AROUND it.** Every approved app either
  visualizes/analyzes the FS tree (Puzzilla, Relative Finder), attaches evidence to
  it (Evidentia, RecordSeek), or syncs local data to it (desktop software). None
  fork or mirror FSI's data in a competing way. **[strong observational inference
  from the catalog]**
- **Respecting compliance rules** — the Agreement forbids bulk export, scraping,
  record-content display, and reverse-engineering. All of these are already
  respected by our design per `docs/familysearch-compliance.md`.
- **Clear LDS-feature support, where relevant.** Cyndi's List categorizes products
  by whether they support LDS ordinance tracking. Our project's respectful-of-LDS
  stance plus explicit deference to Church policies (in `CLAUDE.md` and agent
  prompts) aligns well. **[direct]**

### Quality Assessment and Research Gaps

| Claim area | Confidence |
| --- | --- |
| Gramps is the dominant OSS genealogy platform | Strong |
| Current OSS + FS API + agents + working-copy niche is unoccupied | Strong (public / discoverable market) |
| Steve Little's GRA is the closest philosophical cousin | Direct |
| Ulbrich's fs-mcp is the closest structural cousin | Direct (but low adoption / possibly stale) |
| FSI approves evidence-discipline tools (Evidentia precedent) | Strong |
| No AI/agent/MCP tool has been approved yet | Moderate (absence of evidence argument — Gallery scan was partial due to JS rendering) |
| Hard adopter counts for OSS alternatives | **Not available** — no telemetry in OSS genealogy |
| Full Solutions Gallery inventory | **Partial** — relied on Cyndi's List + help articles; a live-person scroll through the Gallery would complete |

**Known research gaps I'd flag for Marc:**

- We have no quantified market sizing — the field doesn't publish it. All sizing
  arguments will need to be qualitative (community activity, contributor counts,
  forum volume) rather than "X million users."
- The Solutions Gallery rendering limitation means there may be recent AI/agent-era
  approvals I didn't surface. Worth a manual browser scroll as a low-cost
  follow-up.
- Steve Little's project is the strongest competitor signal and warrants a deeper
  read in Step 5 (competitive analysis). Not just the repo — his podcast and NGS
  talks frame what the emerging "AI genealogy" category thinks it's about.

---

### Step 2 Completion Status

- **Research Coverage:** OSS adopter archetypes + FSI ecosystem positioning — complete
  at moderate depth.
- **Citations:** All load-bearing claims cited; confidence labels applied throughout.
- **Unresolved:** Live Solutions Gallery inventory (JS-rendered); Steve Little's deeper
  positioning (deferred to Step 5).

---

## Pain Points and Unmet Needs

**Step adaptation note.** Pain points analyzed here are (A) the frustrations users of
existing OSS + AI genealogy tools actually voice in reviews, forums, and community
posts, and (B) the reviewer-side concerns visible in FamilySearch's own published
guidance and the gap between what FSI-approved tools do vs. what's possible.

### A. Pain points in the current OSS / AI genealogy toolchain

#### A1. Gramps — the incumbent's cracks

Despite its strengths, Gramps has catalogued user frustrations that map directly to
addressable opportunities:

- **Stability.** "Gramps crashes at almost every session" for some users with databases
  of only moderate size. **[direct — SourceForge reviews via
  [gensoftreviews.com](https://www.gensoftreviews.com/?p=286) and
  [genealogy-software.no1reviews.com](https://genealogy-software.no1reviews.com/gramps.html)]**
- **Learning curve.** "A rather steep learning curve when you start using it." UI "does
  not follow the simple conventions of browsers or MS Office." **[strong]**
- **Documentation.** "No single manual, so one has to spend time looking for appropriate
  information in the wiki system." **[direct]**
- **UI polish.** "Amateurish and unpolished due to its community-run volunteer
  development model." **[direct]**
- **GEDCOM gaps.** "Doesn't support GEDCOM 5.5.1 with respect to media files" —
  an ongoing issue after years. **[direct]**
- **Simple operations overcomplicated.** A Gramps-Web GitHub discussion titled
  *"Doing simple stuff (for a genealogy tree) is overcomplicated. Let's use the
  tree-view as a simple way to interact with the family tree!"* is exactly the kind
  of user-frustration flag that indicates unmet need, not just a feature request.
  **[direct — [github.com/gramps-project/gramps-web/discussions/410](https://github.com/gramps-project/gramps-web/discussions/410)]**

**What Gramps notably does NOT have:** no AI anything, no FamilySearch API integration,
no research-workflow agents. It's a well-built data store, not a research assistant.

#### A2. RootsMagic + FamilySearch sync — the fragile bridge

RootsMagic's FS sync is the closest analogue to what our project's write-review workflow
will eventually become, so its pain points are directly instructive. The RootsMagic
Community forums show a steady drumbeat of sync issues:

- **Connection failures** — *"FamilySearch is not responding"* errors on the Central
  window; apps that "worked properly" for a period then "wouldn't auto-connect."
  **[direct — [community.rootsmagic.com](https://community.rootsmagic.com/t/family-search-connection-no-longer-working/10644)]**
- **Hangs on failure** — *"RM hangs after failing to connect to FamilySearch"* when
  searching for matches. **[direct]**
- **Data staleness** — *"Many names have outdated data when compared to FamilySearch."*
  **[direct]**
- **Incomplete operations** — linking two FS individuals as spouses that silently
  fails — *"the system appearing to add the spouse but never actually doing so."*
  **[direct]**
- **OS-dependency fragility** — the October 2022 Windows update broke TLS, which
  broke RootsMagic-FS sync, which broke for *every* affected user. **[direct]**

**Pattern:** These are all failure-mode and diagnostic problems. Users can't tell *why*
a sync failed. An application with explicit audit logs (our `sync_log` table), visible
state, and deterministic diffs would address the whole category. The user's pain isn't
"syncing is hard" — it's "when syncing breaks, I don't know what happened or how to fix
it." **[inferential but strong — this pattern recurs across multiple threads]**

#### A3. The AI-genealogy hallucination tax — the most painful ache in the field

This is the pain point that matters most for positioning, because it's the one that
makes serious genealogists reluctant to use AI at all. Documented examples:

- **Claude invented a parent-child relationship.** In a transcription task, Claude
  "hallucinated a made-up detail that William T. Dyer was the son of Susanna Dyer."
  **[direct — [Medium: Jennifer Oakley](https://medium.com/@jennifer.oakleytx/chatgpt-vs-claude-ai-hallucinations-aka-lying-76a21eabad74)]**
- **Dates off by 20 years, confidently.** Claude "confidently conclude[d] family
  relationships that were completely made up, such as claiming someone was born in
  1847 when they were actually born in 1867." **[direct]**
- **Fabricated citations.** "AI has been known to cite false, misleading, or
  completely fabricated sources." **[strong — multiple sources]**
- **No database access, but tells you anyway.** *"AI chatbots cannot access
  genealogy databases like Ancestry.com or FamilySearch, nor are they savvy enough
  to analyze online family trees.... Because chatbots have a prime directive to
  answer your question, they'll confidently give you detailed answers—even if
  they're not true."* **[direct — [lisalisson.com](https://lisalisson.com/ai-genealogy-research-capabilities-limitations/),
  [Family Tree Magazine](https://familytreemagazine.com/resources/apps/ai-genealogy-prompts/)]**
- **Workarounds exist but shift the burden.** The "Verification Sandwich Method" and
  "treat AI output as hypotheses to be confirmed" are explicit, prescribed techniques
  in every serious AI-genealogy article. This is signal: the field has *accepted that
  verification is the researcher's job*, because no tool enforces it. **[strong]**
- **Claude vs. ChatGPT — a nuance we inherit.** Claude is reportedly "able to say 'I
  don't know' while ChatGPT isn't," making Claude the more cautious choice for
  genealogy work. **[direct — [denyseallen.substack.com](https://denyseallen.substack.com/p/ai-tool-comparison-genealogy-2025)]**
  Our project's Claude-native architecture aligns with where the community is
  already drifting for rigor.

#### A4. What Steve Little's GRA can't do — and it knows it

GRA is our closest philosophical cousin but is explicit about its own scope limits:

- **No API / database access.** *"Does not search databases"* and *"does not access
  Ancestry, FamilySearch, or any subscription site."* **[direct — GRA announcement
  page, confirmed in repo README]** The user has to manually paste every document
  they want analyzed.
- **Single-session, no working copy.** There's no persistent research state between
  sessions. Re-running analysis on the same family requires re-pasting the same
  documents.
- **No local data model.** Cannot reason across a tree — only across the document(s)
  in the current context.
- **Skill + prompt, not agents.** One research-assistant persona, applied repeatedly.
  No specialized roles (duplicate analyzer, locality planner, proof writer) that
  could be composed into a workflow.

**That's the gap the fhra project fills.** GRA and fhra could, in fact, be cooperative
rather than competitive — GRA for deep evidence evaluation of a specific document,
fhra for tree-wide context, live API access, and staged edits. Worth noting as a
possible positioning angle: *"not a replacement for GRA — a complement with live FS
integration and tree-wide workflow."*

#### A5. What Ulbrich's fs-mcp doesn't do

The structural cousin has equally visible gaps, based on the tool manifest published
on PulseMCP and MCP Market:

- **No persistence.** Each call is stateless; no local DB, no GEDCOM import.
- **No research workflow agents.** Eight API-wrapper tools (person get/search,
  ancestors, descendants, records); that's the entire surface. **[direct — manifest
  listed on [pulsemcp.com](https://www.pulsemcp.com/servers/dulbrich-familysearch) and
  [mcpmarket.com](https://mcpmarket.com/server/familysearch)]**
- **No review-before-push.** Read-only by design; no staging model even if writes
  were added.
- **No evidence-discipline enforcement.** Tools return raw API results; evidence
  quality judgement is left entirely to whatever LLM is calling them.
- **Possibly stale.** The GitHub repo at `dulbrich/familysearch-mcp` is currently 404,
  PulseMCP shows 0 stars, and no 2026 activity is visible. **[direct observation —
  research date 2026-04-24]** If the maintainer has drifted, the MCP niche for
  FamilySearch is effectively open.

#### A6. Ecosystem-wide unmet needs (cross-cutting)

Abstracting across the findings above, here are the needs the *current* ecosystem is
visibly failing on:

| # | Unmet need | Priority | Why it matters |
| --- | --- | --- | --- |
| 1 | Agent-assisted genealogy research that **won't hallucinate** | 🔴 Critical | This is the category-defining trust barrier; without it, serious researchers will not adopt AI tooling at all |
| 2 | **Live FamilySearch data access** combined with AI reasoning | 🔴 Critical | Every existing AI genealogy tool has to ask the user to manually supply records; this is the single largest friction point |
| 3 | **Persistent research state** across sessions | 🟠 High | Re-context-loading a 4,000-person tree every session is a dealbreaker for deep research |
| 4 | **Audit trail** of what the assistant did and why | 🟠 High | Implied by the "verification sandwich" need — researchers want to see the reasoning chain |
| 5 | **Review before push** to shared tree | 🟠 High | Prevents the "bad merges on FS" panic that haunts every serious FamilySearch user |
| 6 | **Specialized roles / agents** (duplicate analyzer, locality planner, proof writer) | 🟡 Medium | Composability is more powerful than one monolithic assistant |
| 7 | **Non-catastrophic failure modes** when sync breaks | 🟡 Medium | RootsMagic's forums show users can't diagnose their own breakages |
| 8 | **Readable documentation** | 🟢 Lower | Gramps shows this is a persistent OSS-community pain but projects can grow without nailing it |

**Critical observation:** The top five unmet needs map 1-to-1 to features fhra has
already built or committed to building. That's either a remarkable coincidence
(unlikely — the user has been in the domain long enough to have felt these pains
personally) or strong evidence that the project's design answer was driven by the
right pains. Either way: the product-market fit thesis is *structurally sound*, not
just plausible.

### B. FSI-side pain points — what reviewers worry about

Inferring from FamilySearch's own Terms & Conditions (v6, Nov 2020) and the
compliance-checklist reference at `docs/familysearch-compliance.md`, the gatekeeper
concerns cluster around:

- **Hallucination + fabrication risk.** *Every* FSI-facing user-facing AI risk flows
  from this. The fact that our project's system prompts, CLAUDE.md, and agent
  guidance all explicitly forbid fabrication is the right answer to the question
  we'd face in review.
- **Bulk export.** *"Your Solution must not allow the copying of data from any of
  the FSI APIs without FSI's prior written consent, except for the non-commercial
  and personal use of the end user."* Our design (personal, single-researcher,
  working copy, no sharing features) passes this cleanly.
- **Rate-limit compliance.** Our httpx client already honors `Retry-After` on 429
  and exponential backoff on 5xx. ([FamilySearch Throttling docs](https://developers.familysearch.org/main/docs/throttling))
  **[direct]**
- **Record-content display.** Prohibited; we've documented this and the UI must
  respect it. Already captured in `docs/project-brief.md`.
- **Privacy / living persons.** Our `redact_if_living` helper and `is_living`
  column demonstrate the right posture.
- **Non-production-API usage at the Innovator tier.** The Production API is
  legally off-limits at Innovator; our write-path is already gated behind this
  as a later-milestone concern.

**Hypothesis (to confirm or refute later):** A well-documented, compliance-first,
open-source project whose architecture demonstrably enforces all the above
concerns is probably a *welcome* applicant in Compatible Solution review — possibly
even a pleasant change-of-pace for reviewers used to commercial apps that push
against those limits. **[speculative — would need a FSI-developer-support
conversation to validate]**

### Quality Assessment and Research Gaps

| Claim area | Confidence |
| --- | --- |
| Gramps has documented UX/stability/docs pain | Direct (multiple reviews) |
| RootsMagic-FS sync has persistent reliability issues | Direct (RM Community threads) |
| AI tools hallucinate in genealogy contexts | Direct (multiple named examples) |
| Current AI genealogy tools cannot access live APIs | Strong (stated explicitly in every serious guide) |
| Top 5 unmet needs map to fhra features already built | Strong (feature check against the project brief) |
| FSI reviewers will welcome a compliance-first OSS tool | Speculative (would need direct confirmation) |

**Known gaps I'd flag:**

- We don't have direct quotes from FSI compatibility reviewers about what they
  accept / reject. Closing that would require outreach (`devsupport@familysearch.org`)
  or mining public talks / blog posts by FamilySearch engineering. Probably a
  Step 5 activity or a later direct ask.
- Pain-point prioritization above is my analytical call based on the research;
  a survey of our target users would add confidence but isn't practical here.

---

### Step 3 Completion Status

- **Research Coverage:** OSS + AI toolchain pain points + FSI-side reviewer concerns
  — complete.
- **Citations:** All direct-quote claims cited; confidence labels applied.
- **Pain-point prioritization table built.** Top 5 unmet needs map cleanly to fhra's
  existing architecture — a strong product-market-fit signal.

---

## Adoption and Approval Decision Drivers

**Step adaptation note.** "Customer decisions" translates for our two tracks as:
(A) **what tips a prospective OSS adopter into actually installing and using fhra**, and
(B) **what tips an FSI compatibility reviewer into approving fhra**. Both are modeled as
funnels — awareness → evaluation → decision → first-use → retention — and both are
analyzed for what the drivers actually are, not just what we'd wish them to be.

### A. OSS adoption funnel — how a rigorous genealogist becomes an fhra user

#### A1. The discovery / awareness stage

Where this audience actually hears about new genealogy tools, ranked by observed
prominence in search results and link patterns:

| Channel | Prominence | Notes |
| --- | --- | --- |
| Genealogy blogs and newsletters | High | Legacy Tree, Amy Johnson Crow, Family Locket, Kitty Cooper, Genea-Musings, martinroe.com all regularly review tools **[strong]** |
| YouTube + webinar platforms | High | Legacy Family Tree Webinars (MyHeritage), BYU FHL webinars, conference recordings **[direct]** |
| Podcasts (AI-genealogy specifically) | Rising | *Family History AI Show*, *Ancestors and Algorithms*, *AI Genealogy Insights* — a niche but focused audience **[direct]** |
| Genealogy magazines | Moderate | *Family Tree Magazine* reviews + annual software comparisons **[direct — familytreemagazine.com]** |
| Reddit r/Genealogy + Facebook groups | Moderate | Peer recommendations; Gramps reportedly has "a pretty big support community on Reddit" **[moderate]** |
| National Genealogical Society (NGS) | High among serious users | NGS has an *AI Program Director* role (Steve Little); NGS hosts *Hands-On AI for Family History Writing* workshops; runs GRIP genealogy institute. **[direct — [ngsgenealogy.org](https://www.ngsgenealogy.org/gentechtoolbox/ai-family-history-writing/)]** |
| FamilySearch Solutions Gallery | High among FS-centric users | The default "what apps work with my tree?" discovery path **[direct]** |
| GitHub trending / MCP server registries | Very low general, moderate within dev subsegment | PulseMCP, Glama, Playbooks, mcpmarket.com — where MCP-curious users browse **[direct]** |

**Implication:** The discovery path for fhra is NOT primarily "go viral on GitHub."
The center of gravity of the serious-genealogy AI discussion runs through a small,
specific group of practitioners and media outlets. Getting coverage on NGS channels,
Steve Little's podcast / academy, or a Legacy Family Tree Webinar would move more
real adoption than any number of GitHub stars. **[moderate — inferential from
channel-prominence observation]**

#### A2. The evaluation stage — criteria actually used

Synthesizing from the tool-review and "how to pick genealogy software" sources
([genealogyexplained.com](https://www.genealogyexplained.com/best-genealogy-software/),
[Family Tree Magazine](https://familytreemagazine.com/resources/software/meeting-your-match/),
[martinroe.com](https://martinroe.com/blog/best-genealogy-software-in-2025-a-practical-comparison/)):

- **Active maintenance.** "Regular updates indicate that the developers are actively
  improving and maintaining the software." **[direct]** Implication: visible
  commits, a changelog, a roadmap — adoption-positive.
- **Community / support.** "Customer support, user forums, or online tutorials." An
  empty GitHub Discussions tab hurts.
- **Reviews and social proof.** "Research genealogy software reviews, recommendations,
  and ratings... reading about the experiences of other professional genealogists."
- **Free trial / low-friction install.** Users try before they commit.
- **Data ownership.** Anti-subscription, anti-lock-in preference recurs throughout.
- **Fit with existing workflow.** Specifically: GEDCOM compatibility,
  FamilySearch/RootsMagic integration, cross-platform support.
- **Evidence-rigor fit.** Serious genealogists care explicitly whether a tool
  supports GPS methodology and Evidence Explained citation standards. Evidentia's
  whole pitch is this. **[direct]**

**Weighted priority for our target user:**

| Factor | Weight | fhra's current state |
| --- | --- | --- |
| Evidence-rigor / GPS fit | 🔴 Dealbreaker | ✅ Built into every agent prompt |
| FamilySearch integration | 🔴 Dealbreaker | ✅ Read endpoints wired; sync log in place |
| Data ownership / local-first | 🔴 Dealbreaker | ✅ SQLite working copy, no cloud |
| Active maintenance signal | 🟠 High | ⚠️ Only 2 commits as of research date; will need steady visible cadence |
| Documentation quality | 🟠 High | ✅ Unusually strong for a 2-day-old repo; docs/ is substantive |
| Community / support presence | 🟠 High | ❌ No community yet |
| Free | 🟡 Expected | ✅ MIT-licensed |
| Low-friction install | 🟡 Expected | ⚠️ `uv sync` + `gh auth` + FS key — non-trivial for non-developers |
| Cross-platform | 🟢 Nice-to-have | ⚠️ Python tested on macOS; should work on Linux/Windows but unverified |

**The install-friction issue matters.** A non-developer genealogist is going to bounce
off `uv sync` + MCP server config. The UI milestone (already in the brief) is
load-bearing *not just for UX* but for OSS discoverability; a shippable binary or web
UI collapses the adoption funnel from "follow a README" to "download and run."

#### A3. The decision stage — what actually tips a user into trying

Research suggests three patterns for this audience:

1. **Problem-first.** User hits a specific pain (duplicate-merge panic on FS,
   hallucinated AI transcription, can't track source quality) and searches for a
   fix. The SEO / blog-post pitch they'll find needs to name their problem
   precisely. **[moderate]**
2. **Community-endorsed.** A trusted practitioner recommends the tool (Amy Johnson
   Crow podcast, Kitty Cooper blog, NGS talk). This is where the ceiling is
   highest — one mention by Steve Little could move 500 users. **[strong,
   inferential from community-pattern observation]**
3. **Platform-triggered.** User browses the FamilySearch Solutions Gallery looking
   for "apps that work with my tree." This requires Gallery listing, which
   requires a business entity. For the Innovator-tier personal build, this path
   is *closed* — Innovator apps are not listed. **[direct — Compatibility docs
   state only legal, registered businesses are eligible for Gallery listing;
   sole proprietorships not eligible]**

#### A4. The retention stage — what keeps a user after first install

This is where OSS projects often lose ground:

- **Does it solve the promised problem on first real use?** Our agents need to
  demonstrably do what's claimed on the user's own tree, not a fixture.
- **Does it break when FS API changes?** The rate-limit + retry discipline
  already built helps; a visible statuspage / release notes would help more.
- **Does the user feel they can get help?** Empty issues / Discussions is a
  retention killer.

### B. FSI approval funnel — how we become a Compatible Solution

This is the one where the research surfaced material shifts in my understanding.
**All quoted text in this section is from FamilySearch's published developer
documentation, verified 2026-04-24.**

#### B1. The tier progression (updated from Step 1 understanding)

| Tier | Business entity? | API access | Gallery listing eligibility |
| --- | --- | --- | --- |
| Innovator | Individual OK | Integration + Beta | **Not eligible for Gallery** |
| Registered Solution Provider | **Required** | Integration + Beta | Eligible |
| Compatible Solution Provider | **Required** | + Production API | Eligible, verified-compatible badge |

**Direct quote: "Only a legal, registered business will be eligible for verification
and listing in the App gallery. Sole Proprietorships will not be eligible."**
**[direct — [App Approval Considerations](https://developers.familysearch.org/main/docs/app-approval-considerations)]**

**Key correction from Step 1:** Gallery listing is business-entity-gated *even
before* Compatible status. So:

- **Stay Innovator (current plan):** use API for personal research + OSS distribution
  via GitHub. **No Gallery listing, no Production API, no FSI-channel discovery.**
- **Form business entity → Registered Solution Provider:** Gallery eligibility +
  $199/yr + still no Production API. Gains FSI-channel discovery and the verified-
  compatible badge without the full Production Review overhead.
- **Form business entity → Compatible Solution Provider:** + Production API +
  full compatibility review with per-release approval.

The **Registered** tier — which I under-weighted in earlier analysis — may be the
most interesting middle ground for an OSS-discovery-focused play without taking on
the full compatibility-review operational overhead.

#### B2. The FSI reviewer decision criteria — explicit and discovered

Both explicit (from the docs) and inferred (from what's been approved):

**Explicit approval criteria:** **[direct quotes]**

1. *"Solutions may not be approved that simply copy data out of FamilySearch,
   without providing value back to FamilySearch Family Tree."* **🔥 This is the
   single most important finding in this entire research pass.** Positioning
   implication below.
2. *"Solutions and features must be complementary and non-competitive with
   FamilySearch technology and our core mission."*
3. *"As of June 27, 2017, FamilySearch is suspending the approval of new
   applications that provide functionality for the scanning, capturing or
   reporting of ordinance information, including those that are or may be
   available to take to the temple."* **→ hard non-goal for our project.**
4. *"Core items considered include whether the solution and features are
   compatible with FamilySearch, and whether the company will maintain
   compatibility throughout future releases of FamilySearch's offerings."*
5. **Pre-release compatibility testing for every update**, per the Agreement.
6. **Non-compliance fix window of 5-7 days** once FSI flags an issue.
   **[direct — [Compatibility Review Process](https://developers.familysearch.org/main/docs/compatibility-review-process)]**

**Inferred criteria — from what's been approved** (from the Cyndi's List roster of
26 FS-Compatible products):

- Write-back value pattern: approved apps attach sources (RecordSeek, Evidentia),
  visualize tree (Puzzilla), or sync updates (RootsMagic). **None is read-only +
  analysis-only.** This is the *revealed preference* behind rule #1.
- LDS-ordinance-tracking apps are grandfathered-in; new ones aren't being
  approved since the 2017 suspension.
- Research-analysis tools (Evidentia, Kinpoint) *have* been approved despite not
  writing data themselves — showing that analysis-that-informs-write-decisions
  counts as "value back." **[moderate — inferential]**

#### B3. Positioning implication for fhra

The "value back to the Family Tree" rule is both a gate and an opportunity. Three
stances, ordered by alignment:

| Stance | Value-back story | Approval probability |
| --- | --- | --- |
| **"Read-only research assistant"** | None direct — pure consumption | 🔴 Likely rejected on rule #1 |
| **"Source-attachment accelerator"** | User uses agents to find + evaluate records, then attaches sources to persons on FS via the tool | 🟢 Strong — matches RecordSeek / Evidentia precedent |
| **"Duplicate / merge cleanup assistant"** | User uses agents to identify merge candidates, review them, then merge on FS via the tool | 🟢 Strong — matches FS's own "reduce duplicates" mission priority |
| **"Unsupported-relationship remediation"** | Agents surface parent-child links without sources, user attaches documentation or removes the link | 🟢 Strong — direct mission fit ("make tree more accurate") |

**Refined positioning for a future Compatible Solution Provider application:**
*"Research-disciplined agents that help individuals clean up their FamilySearch
shared tree — attaching missing sources, flagging unsupported relationships,
analyzing duplicate candidates conservatively — with a local working copy so every
change is reviewed before it hits the tree."*

That's a direct "value back to the tree" framing. It's also exactly what the
project brief already says — we just haven't been pitching it in those words.

#### B4. The approval timeline — honest uncertainty

No published overall timeline. What we know: **[direct]**

- Acceptance into the Solution Provider program (what Marc has already applied for):
  no SLA; anecdotally days-to-weeks from my earlier research.
- Compatibility Review (after tier upgrade): no published timeline. Involves
  "business, marketing, support and engineering steps." Non-compliance fixes
  expected in 5-7 days.
- Per-release compat testing: presumably a few days based on similar API-partner
  programs elsewhere, but not stated.

**Recommendation: email `devsupport@familysearch.org` for a realistic timeline
quote before committing to entity formation.** That's Step 6 material.

### Quality Assessment and Research Gaps

| Claim area | Confidence |
| --- | --- |
| Discovery channels for serious-genealogy AI tools | Strong |
| "Value back to the Family Tree" rule is load-bearing | Direct |
| Gallery listing requires business entity | Direct |
| Registered tier is an under-weighted middle option | Direct |
| Ordinance-tracking features are a hard non-goal post-2017 | Direct |
| Refined positioning ("tree cleanup assistant") improves approval odds | Moderate (inferential from precedent patterns) |
| Approval timeline | **Unknown — needs direct FSI contact** |
| Install friction is the biggest OSS retention risk | Strong |

**Known gaps:**

- Haven't quantified the NGS / AI-genealogy practitioner audience (subscriber
  counts, podcast listens); these aren't published but might be discoverable with
  targeted outreach.
- Haven't spoken to a current Compatible Solution Provider about reviewer
  experience — a single interview would be worth more than all prior research.
- Haven't verified whether MCP servers have been approved into the Gallery under
  any category — there's no MCP-specific category yet.

---

### Step 4 Completion Status

- **Research Coverage:** OSS adoption funnel + FSI approval funnel — both mapped with
  specific decision drivers identified.
- **Citations:** All critical approval-criteria claims directly cited from FSI's
  own published docs.
- **Key finding:** "Value back to the Family Tree" rule reshapes the pitching
  strategy. The project's actual features (source attachment, duplicate analysis,
  unsupported-relationship cleanup) are exactly the right ones; we just need to
  *lead with* write-back value rather than read-side analysis in any Compatible
  application.

---

## Competitive Landscape — Deep Dive

### Key Players

Five distinct categories of competitors / comparables, ranked by directness of
overlap with fhra's positioning:

| Category | Representative | Overlap with fhra |
| --- | --- | --- |
| **AI-genealogy prompt/skill frameworks** | Steve Little's GRA / Open-Genealogy | Philosophical twin (evidence discipline), but no API + no working copy |
| **FamilySearch MCP servers** | David Ulbrich's fs-mcp | Structural twin (MCP + FS API), but no agents + no working copy + possibly abandoned |
| **Evidence-discipline desktop tools** | Evidentia | Compatible-Solution precedent, same GPS ethos, but no AI + no FS API |
| **AI-wrapped OSS genealogy data stores** | `cabout-me/gramps-mcp` | Same MCP+agent pattern but on Gramps, not FS |
| **Platform-native AI** | FamilySearch's own AI features | Same data, no rigor / no multi-agent orchestration |

Below, each gets a feature-by-feature teardown.

---

### 1. Steve Little's GRA (Open-Genealogy) — the philosophical twin

**Who**: Steve Little, AI Program Director at the National Genealogical Society. Runs
*AI Genealogy Insights* (blog, academy, podcast: *The Family History AI Show* with
Mark Thompson, ~29 episodes since early 2025). **[direct — [aigenealogyinsights.com](https://aigenealogyinsights.com/),
[ngsgenealogy.org](https://www.ngsgenealogy.org/gentechtoolbox/ai-family-history-writing/),
[rephonic.com](https://rephonic.com/podcasts/the-family-history-ai-show)]**

**Repo**: `github.com/DigitalArchivst/Open-Genealogy` — 40 stars, 1 fork, 73 commits,
CC BY-NC-SA 4.0, v8.5.2 released 2026-04-23. **[direct — GitHub]**

**Architecture deep-read** (from the `skills/gra/` directory):

- Tiered document design — `SKILL.md` (~8KB compact system prompt),
  `research-assistant-v8.5-full.md` (60KB full methodology),
  `companion-reference.md` (18KB templates + schemas), plus `examples/` and
  `tests/` directories.
- **Core directive (direct quote):** *"This assistant never fabricates sources,
  citations, people, dates, places, or events. When evidence is insufficient, it
  says so."* **[direct — GRA repo]**
- Applies the Three-Layer Evidence Model (source × information × evidence) and
  all five Genealogical Proof Standard elements.
- Recent v8.5.2 guardrails: regression awareness, implied-relationship
  inference protection. Maintainer is actively refining the prompt with the
  specific hallucination failure modes he observes.

**Strengths:**

- **Methodological depth.** 60KB of explicit GPS methodology is genuinely
  high-ceiling research assistance. Our agent prompts are terser.
- **Platform neutrality.** Works on Claude, Claude Code, ChatGPT, Gemini, Cowork,
  local models via LM Studio. A bigger reachable audience than any API-dependent
  tool.
- **Authorial authority.** Steve Little is the "ordained" voice for AI genealogy
  inside NGS. A mention by him moves adoption.
- **Anti-hallucination discipline baked into the prompt itself** — near-identical
  philosophy to fhra's agent prompts. This is **convergent validation**, not
  competition: two independent builders arrived at the same rules.

**Weaknesses:**

- **No API or database access.** User must manually paste every document — a
  stated limitation in the project's own README.
- **No persistent state.** Each session re-ingests everything.
- **Single-persona design.** One research-assistant voice. Not composable.
- **Low adoption volume.** 40 stars / 1 fork reflects a niche, enthusiastic
  audience rather than mass pickup. **[direct]**

**How fhra coexists vs. competes:** Coexists cleanly. GRA is the document-level
evidence-evaluator; fhra is the tree-level research-workflow automation tool with
live FS data. A user can — and arguably should — use both: pipe a specific
record transcription through GRA for deep evidence classification, then let fhra
attach it to the right person on FS. **A future README section could suggest
exactly this pairing.**

---

### 2. David Ulbrich's fs-mcp — the structural twin that may have vanished

**Who**: David Ulbrich, Senior Software Engineer at the City of Orem, Utah.
**[direct — GitHub profile]**

**Current status — signs of abandonment:** **[direct observations, 2026-04-24]**

- `github.com/dulbrich/familysearch-mcp` → **404 Not Found.**
- David's public GitHub profile shows **24 repos, 0 followers, 0 of the visible
  top-6 repos are genealogy-related.** Top repos are iOS/Swift work.
- PulseMCP listing shows **0 stars.**
- Release date of March 24, 2025 — **13 months ago as of today; no 2026 activity
  referenced anywhere.**
- Still listed as active on PulseMCP, Glama, Playbooks, mcpmarket.com — these
  registries pull from repo metadata and don't auto-deindex gone repos.

**Strengths (of what it did):**

- First FamilySearch MCP server as far as search can surface.
- Covered basics: auth, person get/search, ancestry, descendants, records search.

**Weaknesses:**

- Pure API wrapper — no agents, no working copy, no GEDCOM integration, no
  evidence discipline.
- No documentation tier — one README, no docs/ directory visible in the
  registry listings.
- Written in TypeScript — fine, but limits who can contribute if the community
  of potential genealogy devs skews Python.

**How fhra coexists vs. competes:** fs-mcp appears to have stalled; if the
maintainer has moved on, the niche is **effectively open**. We should avoid
repeating its apparent mistake of shipping tools without a research workflow
around them. One respectful outreach to Ulbrich (email or GitHub if the repo
resurfaces) could confirm status and, if appropriate, offer a friendly "we're
picking up this torch" message. **[strategic speculation]**

---

### 3. Evidentia — the approved-by-FSI precedent

**Who**: Edward Thompson (longtime developer in the genealogy software space),
via Evidentia Software. Listed as FamilySearch-Compatible on Cyndi's List.
**[direct — [evidentiasoftware.com](https://evidentiasoftware.com/),
[Cyndi's List](https://www.cyndislist.com/familysearch/compatible/)]**

**Product:** Desktop software for classifying source-information-evidence and
producing proof arguments per the Genealogical Proof Standard.

**Pricing model (striking for our segment):** **[direct — Evidentia store]**

- **$29.99 one-time** purchase (no subscription)
- $14.99 upgrade for v3 for prior owners (50% off)
- Book + software bundle $40.99
- Windows / Mac / Linux AppImage
- Both download and CD-ROM options

**Why this price matters:** Evidentia's pricing is the revealed price expectation
for serious-researcher segment tools. Subscription is not what this audience pays.
If fhra were ever paid (post-OSS or dual-licensed), a $30 permanent-license is the
comparable anchor. But for now OSS + free is *above* expectations, not below.

**Strengths:**

- **FSI Compatible.** Direct precedent that evidence-discipline tools pass
  approval.
- **Positive community reviews** — "almost forces you to follow the Genealogical
  Research Process." That's the kind of product review we'd be thrilled to
  receive about fhra.
- **Established in the niche since ~2012** (per archive evidence in the repo
  reviews). Deep workflow fit for the same user archetype.

**Weaknesses:**

- **No AI / agents.** Entirely manual classification.
- **No FamilySearch API integration.** User does the research manually, feeds
  Evidentia the sources, gets proof arguments out.
- **Desktop-only.** No cloud, no web UI.
- **Small team / slow cadence** — v3 has been current for years per the store page.

**How fhra coexists vs. competes:** Coexists. Evidentia is manual; fhra is
AI-assisted. They target the same user but different workflow moments. An fhra
user *could* export their evidence set to Evidentia for formal proof argument
writing; Evidentia users already value GPS-based rigor, which means they're a
pre-qualified audience for fhra's agents.

---

### 4. `cabout-me/gramps-mcp` — MCP for the other side

**Who**: Single-maintainer OSS, AGPL-3.0. 30 stars, 27 commits, v1.1.0 Sept 2025.
**[direct — GitHub]**

**Architecture:** 16 tools in 3 categories (search/retrieval, data management,
analysis). Tool wrapper, no agents.

**Strategic take:** Not a direct competitor — targets Gramps Web API, not
FamilySearch. BUT it validates the MCP-for-genealogy pattern and shows the same
conclusion we reached: tool wrappers without higher-level workflow are
functional-but-not-transformative. Gramps-MCP + fhra could peacefully coexist in
a user's Claude Code setup; they don't overlap.

---

### 5. FamilySearch's own AI features — the platform-native competitor

**What FSI is shipping:** AI-indexed records, full-text search, an AI help
chatbot, and an AI research assistant on their own platform.
**[direct — [FamilySearch AI blog](https://www.familysearch.org/en/blog/ai-developments-genealogy)]**

**Strengths:**

- Direct access to the tree and records (no API limits apply to FSI itself).
- Zero install friction.
- Free.
- Brand trust from the user base.

**Weaknesses:**

- **No evidence discipline visible in their AI output.** Their AI is consumer-
  grade research acceleration, not proof-argument-grade rigor.
- **Not customizable / not composable into other workflows.**
- **No local working copy** — everything lives on their servers.
- **Cannot operate alongside the user's personal RootsMagic / Gramps data.**

**How fhra coexists vs. competes:** The FSI AI is the "good enough for casual
use" product; fhra is the "evidence-disciplined for serious use" product. This
is like arguing against Google's built-in translate vs. a professional
translation workflow — two different products for two different trust levels.
The risk isn't that FSI out-competes us on our axis; it's that they raise the
baseline of "AI-assisted research" expectations and make our install friction
feel heavier by comparison. **Install-friction remains the biggest defensive
priority.**

---

### Market Share Analysis — what share of what market?

Honest qualitative read, since no public metrics exist for most of this:

- **FSI-platform-native AI:** Access to the entire FSI user base (tens of
  millions). This is the elephant in the room.
- **Gramps + webtrees:** Uncounted but large global OSS genealogy user base;
  43 language translations hint at scale. **[direct]**
- **Evidentia:** Small but dedicated. Single-developer shop; unknown sales
  volume.
- **Steve Little's GRA:** 40 GitHub stars reflects the *highly selected* niche
  of serious-researcher-plus-AI-early-adopters. Maybe hundreds to low-thousands
  of active users; podcast cross-promotion extends reach.
- **Ulbrich's fs-mcp:** Effectively zero adoption. 0 stars on PulseMCP,
  repo 404.
- **fhra (us):** Currently 1 user (Marc). Adoption from here is a function of
  (install-friction reduction × positioning alignment × community outreach).

**Key insight for positioning:** We are not competing for share with FSI's
platform AI. We are competing for share within the much smaller *serious-
researcher-plus-AI-early-adopter* niche — a few hundred to a few thousand
global users at most, currently split between GRA, random ChatGPT users, and
Evidentia-plus-manual-ChatGPT workflows. Winning this niche is realistic;
winning the general genealogy market is not.

---

### Competitive Positioning Map

| Tool | Evidence discipline | Live FS data | Local working copy | Specialized agents | Review-before-push | License |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Steve Little's GRA | ✅ | ❌ | ❌ | ❌ (1 persona) | ❌ | CC BY-NC-SA |
| Ulbrich's fs-mcp | ❌ | ✅ | ❌ | ❌ | ❌ | Unknown |
| `cabout-me/gramps-mcp` | ❌ | ❌ (Gramps) | ❌ | ❌ | ❌ | AGPL-3.0 |
| Evidentia | ✅ | ❌ | ✅ (own DB) | ❌ | n/a (no sync) | Commercial ($30) |
| FSI's own AI | ❌ | ✅ | ❌ | ❌ | n/a (cloud) | Platform |
| RootsMagic + ChatGPT (DIY) | User-enforced | ✅ (via RM) | ✅ (RM DB) | ❌ | User-enforced | Commercial |
| **fhra (this project)** | ✅ | ✅ | ✅ | ✅ (7) | ✅ (planned) | MIT |

**fhra is the only cell in the table that ticks every column.** This is the
defensible differentiation claim for both OSS adoption and FSI Compatible
Solution positioning.

---

### Strengths / Weaknesses / Opportunities / Threats (SWOT)

#### Strengths

- Unique combination of features — evidence discipline + live FS API + local
  working copy + specialized agents — is empirically not matched by any other
  public tool.
- Design aligns with FSI's "value back to the tree" rule: source attachment,
  duplicate analysis, unsupported-relationship cleanup are all write-back patterns.
- Open-source + MIT invites contribution and reuse without NC restrictions (GRA
  is CC BY-NC, which blocks commercial redistribution).
- Claude-native architecture aligns with where serious genealogists are
  converging (Claude > ChatGPT for rigor).
- Compliance discipline is *in the codebase already* (retry logic, User-Agent,
  `redact_if_living`, origin-tagged facts for FSI-data purge) — reviewers will
  see it, not take our word for it.

#### Weaknesses

- **Install friction.** `uv sync`, `gh auth login`, FSI key, MCP setup — each
  step loses users.
- **Single contributor.** Bus factor = 1. OSS projects with bus factor 1 struggle
  to retain adoption when maintainer drifts.
- **No UI yet.** BMAD planning will address this; but until shipped, "genealogy
  research tool you use in a terminal" is a niche-within-niche.
- **No audience presence yet.** 0 GitHub stars on our repo, no blog posts, no
  community outreach.
- **Innovator-tier ceiling.** No Gallery listing, no Production API, no FSI-channel
  discovery until business entity formed.

#### Opportunities

- **Collaboration with Steve Little / NGS.** GRA and fhra are complementary by
  design, not competitive. A co-promotion or "works well together" note could
  move adoption for both.
- **Fill the apparent abandonment of Ulbrich's fs-mcp.** If that project is
  genuinely stalled, fhra can become the reference FamilySearch MCP in the MCP
  server ecosystem.
- **Compatible Solution first-mover in AI/agent/MCP category.** No approved
  AI/agent/MCP-based app exists in the Cyndi's List FSI roster. Being first sets
  category norms.
- **"Works with your Gramps data" compatibility** via the existing GEDCOM
  importer. A future "import your Gramps/webtrees tree via GEDCOM" path captures
  users of the OSS incumbent.
- **Niche media coverage** — Amy Johnson Crow, Kitty Cooper, Legacy Tree blog,
  Family Locket, Legacy Family Tree Webinars, The Family History AI Show.

#### Threats

- **FamilySearch's own AI gets dramatically better.** If FSI ships an AI research
  assistant that's "good enough" for serious researchers, the addressable market
  shrinks.
- **GRA adds API integration.** If Steve Little decides to add FS API access, the
  philosophical and structural twin converge; GRA's distribution advantage wins.
- **Policy shift at FSI.** Agreement updates take effect 60 days after posting.
  An unfavorable change (e.g., on MCP-style agent access, or on AI-tool
  approval criteria) could reshape the path.
- **MCP standard churn.** The protocol is young; tooling and registry conventions
  may shift, forcing rework.

---

### Research Gaps Flagged from This Step

- Have not confirmed fs-mcp status via direct outreach. A courtesy email
  to Ulbrich would resolve whether the project is abandoned vs. privated.
- Have not confirmed Steve Little's openness to a "complementary pairing"
  narrative. A respectful outreach (he's a podcast host with public email)
  could turn a theoretical opportunity into a concrete one.
- No direct FSI-reviewer or recent-Compatible-applicant interview. Step 6
  recommendation: consider reaching out before entity formation.

---

### Step 5 Completion Status

- **Research Coverage:** Top five competitor categories deep-analyzed with
  feature/positioning/distribution breakdowns.
- **Citations:** All direct claims cited; confidence labels applied; repo
  observations timestamped to research date (2026-04-24).
- **Positioning matrix built.** fhra occupies a cell no other public tool
  currently fills.

---

## §6. Strategic Synthesis and Recommendation

**Note on methodology for this step.** BMAD's generic Step 6 template prescribes
running broad web searches for "market entry strategies best practices" and
"market research risk assessment frameworks." I skipped those — the preceding
five steps generated enough specific, cited signal that adding generic frameworks
would dilute rather than sharpen the conclusions. One targeted search was useful
and is folded in below: FSI's quarterly breaking-change cadence (Mar/Jun/Sep/Dec 1).

### Executive summary — answering the original question

**The research question:** *"Is fhra useful as an open-source tool, and one for which
FamilySearch would allow API access?"*

**The answer:** **Yes to both, with specific conditions.**

- **OSS viability — yes, for a specific niche.** The addressable audience is the
  serious-researcher-plus-AI-early-adopter segment: people who already know the
  Genealogical Proof Standard, already distrust AI hallucination, already use
  Gramps or a paid-but-data-ownership-friendly tool like RootsMagic, and who are
  starting to experiment with AI-assisted research but want it disciplined. Size:
  hundreds to low-thousands of active users globally. Not a mass market. A viable
  OSS market.
- **FSI API access — yes, two tiers of access available.** Innovator tier is
  likely straightforward given our compliance posture, and is the right starting
  point. Compatible Solution Provider (Production API + Gallery listing) is
  achievable but requires business entity formation and is best deferred until
  real adoption justifies it. The "value back to the tree" rule is the framing
  that wins approval, and it's a frame our architecture already supports.

**Strength of evidence for these conclusions:** Moderate-to-strong. We have direct
citations from FSI's own published docs for the approval-criteria claims. We have
direct repository evidence for the competitive gap. We have clear community signals
for the audience's values. We do **not** have FSI-reviewer interviews or hard
adoption metrics — those would strengthen but not overturn the conclusions.

### Strategic recommendation — go / no-go / conditional

The four investment decisions this research was meant to inform, with verdicts:

| Investment | Recommendation | Rationale |
| --- | --- | --- |
| **Publicly promote the OSS release (landing page, blog posts, niche outreach)** | 🟡 **Conditional go** — after UI ships | The PMF thesis is sound, but the install friction for a terminal-only tool will cap conversion. Promote once the UI reduces the funnel from "follow a README" to "download and try." |
| **Create community-facing materials (README polish, screencast, example research report)** | 🟢 **Go now** | Zero-risk; makes every existing organic visit more likely to stick. README + one recorded walk-through demonstrating an agent running against the user's tree is the highest-ROI artifact. |
| **Form a business entity + apply for Compatible Solution Provider** | 🔴 **Defer** to phase 2 (6-12 months) | The Innovator tier covers our current read-only scope; the upside of Compatible (Production API, Gallery listing, write-path) is only realized once there's a UI *and* adopter demand. Premature entity formation incurs $199/yr plus operational overhead with no offsetting return. |
| **Continue as purely personal tool, defer the rest** | 🔴 **No** | The research shows this would under-exploit a real opportunity. The investment to go from "personal tool" to "usable by the serious-researcher niche" is small relative to the position we'd occupy. |

### Phased roadmap

```
Phase 0 — now (done or in-flight)
├── OSS repo public on GitHub ✅
├── Innovator application submitted (in progress, tracked separately)
├── BMAD planning pass on UI (this work + next agent handoff)
└── Compliance posture documented and enforced in code

Phase 1 — 30/60/90 day milestones (ship the UI)
├── 30 days: UI architecture decided (desktop vs local-web vs TUI) via BMAD
├── 60 days: UI MVP covers the three highest-value views:
│            • tree-navigation + "who has problems" view
│            • local-vs-FS diff for any person (tree-reconciler output)
│            • agent-findings panel with provenance
├── 90 days: UI shipped; first real research workflow runnable end-to-end
└── In parallel: README upgrade + 1 recorded walkthrough + 1 blog post

Phase 2 — 6 months (OSS outreach, measure adoption)
├── Respectful outreach: Steve Little, Amy Johnson Crow, Family Locket,
│   Legacy Family Tree Webinars
├── Mention in at least one niche podcast / newsletter
├── Target: first 10 non-Marc users, first external GitHub issue or PR
├── If Ulbrich's fs-mcp status unchanged: offer a "picking up the torch"
│   mention in our README
└── Decision point: does adoption justify Phase 3?

Phase 3 — 12+ months, only if Phase 2 validates
├── Form business entity (sole-proprietor-to-LLC is the usual path)
├── Apply for Registered Solution Provider → Gallery listing
├── Add write-path code behind explicit feature flag
├── Apply for Compatible Solution Provider → Production API
├── Clean-sheet Compatibility Checklist self-audit BEFORE submitting
└── Expect per-release FSI approval overhead from this point forward
```

### Key risks and mitigations

| Risk | Severity | Mitigation |
| --- | --- | --- |
| FamilySearch's own AI catches up on rigor | High | Keep evidence-discipline visible in UI output (cited sources, confidence labels, agent reasoning exposed). Compete on composability + local ownership, not raw AI quality. Monitor quarterly via FSI newsletter + their AI blog. |
| GRA adds live API integration | Medium | Don't compete — collaborate. Reach out to Steve Little now to establish a "complementary tools" relationship while both projects are young. GRA's deep methodology + fhra's API integration is a stronger story together than either alone. |
| MCP standard churns | Medium | Write to the MCP Python SDK's stable interfaces. Track SDK releases; expect a rework cycle every 6-12 months. |
| FSI breaks API on a quarterly cut (Mar/Jun/Sep/Dec 1st) | Medium | Subscribe to FSI's quarterly dev newsletter (email `devsupport@familysearch.org`). Keep the retry / ETag plumbing current. Budget a half-day after each quarterly change to verify. |
| Install friction limits OSS adoption ceiling | Medium-High | The UI milestone is the direct mitigation. Until then, promotion ROI is capped. |
| Single-maintainer bus factor | Medium | Document aggressively (already strong). Accept first-contribution PRs graciously when they arrive. Consider a CODEOWNERS file. |
| FSI Agreement updates (60-day effective) | Low-Medium | Already a documented watch-item in `docs/familysearch-compliance.md`. Re-read quarterly. |
| Ordinance-feature contribution attempts (post-2017 suspension) | Low | Explicit non-goal documented in CLAUDE.md would prevent well-meaning contributors from adding this. |

### Success metrics — how we'll know

| Dimension | Phase 1 success (90d) | Phase 2 success (6mo) | Phase 3 trigger (12mo) |
| --- | --- | --- | --- |
| **UI / product** | MVP shipped, end-to-end research workflow possible | N+3 iterations shipped in response to real usage | Stable enough for per-release FSI compat review |
| **OSS adoption** | README + walkthrough published; first organic visitors | 10+ non-Marc users; first external contribution | Clear demand from users for write-path (forum asks, GitHub issues) |
| **FSI integration** | Innovator key issued; Beta access granted; first live `fs_get_person` call logged | Stable usage against Beta; no compliance incidents; quarterly-change adaptations clean | Ready to pay $199/yr + entity cost for Gallery listing + Production API |
| **Community signal** | Mentioned by zero external voices | Mentioned by at least one NGS-adjacent voice (podcast, blog, newsletter) | Recommended alongside GRA / Evidentia in at least one comparison post |

### Immediate next steps — 2 weeks out

**Week 1:**

1. Add the 2017-suspended-ordinance-features item to CLAUDE.md as a hard non-goal
   (5 min).
2. Subscribe to FSI's quarterly developer newsletter by emailing
   `devsupport@familysearch.org` (5 min).
3. Ask FSI devsupport for a realistic compatibility-review timeline (same email,
   same day). This informs Phase 3 planning.
4. Continue the BMAD planning pass on the UI — this research's natural successor
   is the `bmad-agent-pm` (PRD) or `bmad-agent-architect` (UI architecture) step.

**Week 2:**

5. One courtesy email to David Ulbrich — acknowledge his fs-mcp, ask about its
   status, offer a respectful "if you're done with it, we'd love to reference it
   in our README" note. Even if unanswered, it's polite.
6. Draft (don't send yet) an outreach note to Steve Little framing fhra as a
   complement to GRA. Hold for when our UI is closer to shippable — an outreach
   note that points to a running tool lands better than one that points to a
   repo.
7. First README upgrade iteration — add a "Who this is for / what this does that
   nothing else does" intro paragraph using the matrix from §5.

### Methodology notes and limitations

**What I did:**

- 6 structured steps: scope → segments → pain points → decisions → competition →
  synthesis.
- ~20 targeted web searches + direct repository / documentation fetches.
- Cross-reference between multiple independent sources for every load-bearing
  claim.
- Confidence labels explicit on every non-trivial assertion.

**What I did NOT do (honestly flagged):**

- No direct outreach to FSI, Steve Little, or David Ulbrich. Those are the
  single-biggest-ROI next-step actions (listed above) but they belong with the
  primary researcher, not the analyst.
- No survey / interview data from the target user segment. The segment isn't
  large enough for cheap survey work; targeted interviews would be higher-value.
- No paid-database access. Podcast-listener demographics (Rephonic), industry
  reports (Gartner / IDC), and premium GitHub insights were not used because
  they require subscriptions.
- The live FSI Solutions Gallery page is JS-rendered and WebFetch-blocked, so
  the Gallery inventory is reconstructed from Cyndi's List (authoritative but
  not exhaustive). A manual browser scroll would close this gap in an hour.

**Confidence in the overall recommendation:** Moderate-to-strong. The biggest
residual uncertainties are: (a) exact FSI Compatibility Review timeline, (b) how
Steve Little / NGS would react to a collaboration overture, (c) whether FSI
will ship production AI features that materially narrow our evidence-rigor
moat. Each has a concrete Phase 1 action to resolve.

### Closing analyst note

*From Mary.*

Two things about this research struck me, both worth naming even though they
aren't strictly findings.

First — the degree of alignment between the pains this research surfaced and
the architecture Marc has already built is not a coincidence. Serious
genealogy researchers, independently of each other, converge on the same small
set of rules: never invent, cite everything, stage before push, value evidence
over speed. Steve Little wrote one version into GRA. Marc wrote another version
into fhra. FamilySearch reviewers encoded a third version into their approval
criteria. That shared shape is the thing to defend and lead with, not a thing
to vary or dilute in pursuit of broader appeal.

Second — the biggest asset this project has for the next phase isn't code. It's
*the disciplined documentation you've insisted on since before line 1 was
written.* CLAUDE.md, the compliance doc, the project brief, the agent system
prompts. Those are going to be load-bearing in every upcoming decision: when
BMAD's Architect asks "what are the constraints," when a contributor asks "what
can't I add," when an FSI reviewer asks "what does your app commit to." Keep
that practice tight. It's rarer than you might think.

Thank you for letting me dig. Happy hunting. 🔍

---

**Market Research Completion Date:** 2026-04-24
**Research Scope:** Two-track: OSS viability + FSI approval posture
**Source Verification:** All load-bearing claims cited with current URLs
**Confidence Level:** Moderate-to-strong; primary residual uncertainties
documented

*This market research document informs the strategic decision on open-sourcing
promotion + Compatible Solution Provider pursuit. It is the input document for
the subsequent BMAD planning passes (PRD, UX specification, architecture).*





