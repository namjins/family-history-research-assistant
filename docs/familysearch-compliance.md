# FamilySearch Solutions Program — Compliance Reference

This is the project's authoritative reference for what we are and aren't allowed to do
under the FamilySearch International (FSI) Solutions Program Agreement and Terms &
Conditions (the "Agreement"; version **v6, last updated 2020-11-25**).

FSI publishes the current Agreement at
[www.familysearch.org/developers/docs/agreement-log](https://www.familysearch.org/developers/docs/agreement-log).
**Updates take effect 60 days after posting** — someone (human, not agent) needs to check
that URL periodically and update this doc if the Agreement changes.

Direct quotes from the Agreement are in *italics*. Everything else is our interpretation.

## Program levels — which tier we're in

Three levels exist:

| Level | For | Production API? | Business entity required? | Annual fee |
| --- | --- | --- | --- | --- |
| **Innovator** | Individuals doing dev | No — Integration / Beta only | **No** — individuals allowed | None |
| Registered Solution Provider | Business entities | No (read-only access) | Yes (EIN or equivalent) | $199 |
| Compatible Solution Provider | Business entities in production | Yes, after compat review | Yes | $199 |

**Our target tier: Innovator.** That's the only tier available to an individual researcher.

Consequences:

- **Term is 9 months** (vs 1 year for the paid tiers), with no documented renewal mechanism
  — we'll need to re-apply.
- *"You will not be granted access to the FSI Production API."* Read and write on production
  is blocked at the legal tier, not just the app-key tier.
- *"Innovators may only be granted access to the FSI Beta API or the Integration API."*
- **No processing fee and no annual fee.**
- If we ever want Production access: must transition to Compatible Solution Provider **and
  establish a business entity** first.
- Development activities as an Innovator are *"for your own benefit and account, and are
  not for the benefit or account of FSI"* — no intellectual-property claims flow to FSI.

## Hard ceilings on what our code can do

These are walls, not guidelines. Crossing them materially breaches the Agreement.

- **No Production API access while we're an Innovator.** Any "write to the live shared tree"
  feature is legally blocked until we upgrade tiers. Design around this: all writes must be
  stageable locally and only sent when/if we ever have Production access.
- **No bulk copying of FSI data.** *"Your Solution must not allow the copying of data from
  any of the FSI APIs without FSI's prior written consent, except for the non-commercial
  and personal use of the end user."* A "dump everything to CSV" feature is out; a single
  user viewing/analyzing their own tree is in.
- **No robots, spiders, scraping.** *"You agree not to use, or allow or facilitate the use
  of, any alternative means, such as robots, spiders, scraping, or other technology, to
  access, query, or use FSI's website, the FSI APIs, or any data from FSI's website or any
  of the FSI APIs."* All data flows must go through the documented API.
- **No reverse engineering.** Of other Solutions, FSI's website, FSI APIs, or any FSI
  service/product.
- **No displaying FSI content outside our Solution.** Third-party display of historical
  record content is prohibited (see
  [project-brief.md](project-brief.md#constraints)).
- **No exceeding reasonable bandwidth.** FSI may rate-limit, block, or terminate access if
  we use unreasonable bandwidth. Our API client honors `Retry-After` on 429s and backs off
  on 5xxs — keep it that way.

## Obligations we must meet

- **Be transparent about identity.** Our HTTP client must identify itself via User-Agent.
  (Implemented: the `FamilySearchClient` sends
  `User-Agent: fhra/{version} (+family-history-research-assistant)`.)
- **Make it easy to contact us.** Once we have any published Solution surface, include
  support contact info.
- **Privacy law compliance.** Abide by all applicable privacy laws worldwide. If the
  Solution ever collects personal information from users beyond the primary researcher,
  we need a privacy policy. International data transfers require consent / data-transfer
  agreements.
- **Living-person privacy.** Living persons are private by default on FamilySearch; our
  local DB redacts them by default in the MCP layer. Don't regress this.
- **Indemnification.** We indemnify FSI against claims arising from our Solution,
  violations of law, privacy breaches, IP infringement.
- **Non-commercial end-user data use.** *"Data derived from or through FSI is for the
  personal and non-commercial use of your end users."* If we ever add multi-user features,
  we must prohibit end users from selling/leasing/sublicensing data derived from FSI.
- **24-hour breach notification.** *"If you or your Solution suffers a security breach
  potentially affecting FSI's data, the FSI APIs, or Digital Content, you must notify FSI
  of such security breach as soon as reasonably practicable, but in no event more than 24
  hours after discovery of such breach."* Note: this only kicks in for Compatible Solution
  Providers / Innovators with API access. If we're that tier and discover a breach,
  contact `devsupport@familysearch.org` within 24 hours and cooperate with forensic
  investigation.
- **Confidentiality.** Any non-public FSI information shared with us in the course of the
  Program (e.g. internal docs, pre-release API info) is Confidential Information — do not
  disclose, do not use beyond the Program. Obligation survives termination of the
  Agreement.
- **No publicity without written approval.** Do not publicly claim FSI endorsement or put
  FSI in marketing without per-instance written authorization. The Program Logo may only
  be used per FSI's Trademark Usage Guidelines at `FamilySearch.org/brand`.
- **Developer key is single-use.** *"Any developer key provided to you that allows you
  access to an FSI API is for your use only, and must be kept strictly confidential."*
  Our `.env` file is gitignored; keep it that way. Never commit the key.

## Compatibility testing (for the day we upgrade)

If/when we move from Innovator → Compatible Solution Provider, FSI requires pre-release
review: *"Your new, updated, or revised Solution will not be implemented or allowed to go
live without the prior written approval of FSI."*

That means any CI/CD to a real user base requires per-release sign-off from FSI. This is
a significant operational constraint — plan for it before building a release pipeline.

## On termination

If the Agreement ends (expires, we cancel, they cancel, or either side breaches):

- We lose access to all FSI APIs immediately.
- *"You must immediately cease using the data."* This includes any data we've fetched and
  still have locally. Practically: we'd need to purge FamilySearch-origin rows from our
  local DB. Our `origin` column on `facts` and `person_sources` makes this cleanly
  doable — delete `WHERE origin = 'familysearch'`.
- We lose the Program Logo license; must remove any branding.
- We must return or destroy any Confidential Information, with limited exceptions for
  legally-required retention or archival backups (still under confidentiality).
- We cannot continue to call ourselves a Solution Provider / Program participant.

Either party can terminate for any reason with **30 days notice**. Uncured material breach
is a **10-day cure window**.

## Jurisdiction

Utah law; Salt Lake County, Utah courts.

## Application logistics (for the user, not the code)

- Apply at [www.familysearch.org/innovate/apply](https://www.familysearch.org/innovate/apply).
- As an individual, target the **Innovator** tier in the application description.
- No business entity is required at this tier; the form's "Company Name" can be the
  project name.
- No fee. 9-month term.
- After acceptance, register a **Desktop** app in the Solutions Community with redirect
  URI `http://localhost:5000/auth/familysearch/complete`. Key is immediately enabled for
  Integration; Beta access is requested separately.

## Change tracking

When FSI updates the Agreement, someone should:

1. Read the diff at the agreement-log URL.
2. Update this doc with the new version date and any changed obligations.
3. Audit the codebase against the new terms — especially anything in the "Hard ceilings"
   section above.
4. Open a follow-up task for any new obligation that requires code or docs changes.

Updates take effect **60 days after posting** — so there is time, but not indefinite time.
