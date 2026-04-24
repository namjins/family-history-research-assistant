-- Local working-copy schema for the Family History Research Assistant.
-- This is the research workspace; FamilySearch is not source of truth for in-progress work.
-- Curated changes are reviewed and pushed out to FamilySearch via the API layer.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Individuals in the local working copy.
CREATE TABLE IF NOT EXISTS persons (
    id              TEXT PRIMARY KEY,         -- internal UUID
    fs_person_id    TEXT UNIQUE,              -- FamilySearch PID (e.g. KW12-ABC)
    gedcom_xref     TEXT,                     -- original GEDCOM @I123@
    given_names     TEXT,
    surname         TEXT,
    sex             TEXT CHECK (sex IN ('M','F','U') OR sex IS NULL),
    is_living       INTEGER NOT NULL DEFAULT 0,
    notes           TEXT,
    last_synced_at  TEXT,                     -- ISO-8601 of last FS fetch
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_persons_surname      ON persons(surname);
CREATE INDEX IF NOT EXISTS idx_persons_given        ON persons(given_names);
CREATE INDEX IF NOT EXISTS idx_persons_gedcom_xref  ON persons(gedcom_xref);

-- A fact / event / attribute attached to a person (birth, death, residence, occupation...).
CREATE TABLE IF NOT EXISTS facts (
    id                TEXT PRIMARY KEY,
    person_id         TEXT NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    fact_type         TEXT NOT NULL,          -- GEDCOM tag: BIRT, DEAT, MARR, RESI, OCCU, ...
    date_raw          TEXT,                   -- original date string from GEDCOM/FS
    date_normalized   TEXT,                   -- ISO-8601 where parseable
    place_raw         TEXT,
    place_normalized  TEXT,
    value             TEXT,                   -- occupation name, residence detail, etc.
    evidence_quality  TEXT,                   -- 'direct' | 'indirect' | 'negative' | 'inferred'
    origin            TEXT NOT NULL,          -- 'gedcom' | 'familysearch' | 'local_edit'
    origin_ref        TEXT,                   -- GEDCOM line anchor or FS conclusion id
    created_at        TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_facts_person      ON facts(person_id);
CREATE INDEX IF NOT EXISTS idx_facts_type        ON facts(fact_type);

-- Relationships: parent-child and spouse. Symmetric rows are not stored;
-- queries take direction into account via role1/role2.
CREATE TABLE IF NOT EXISTS relationships (
    id          TEXT PRIMARY KEY,
    rel_type    TEXT NOT NULL CHECK (rel_type IN ('parent_child','spouse')),
    person1_id  TEXT NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    person2_id  TEXT NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    role1       TEXT,                          -- 'father' | 'mother' | 'spouse'
    role2       TEXT,                          -- 'child' | 'spouse'
    origin      TEXT NOT NULL,
    origin_ref  TEXT,
    created_at  TEXT NOT NULL,
    UNIQUE (rel_type, person1_id, person2_id)
);

CREATE INDEX IF NOT EXISTS idx_rel_person1 ON relationships(person1_id);
CREATE INDEX IF NOT EXISTS idx_rel_person2 ON relationships(person2_id);

-- Sources / citations.
CREATE TABLE IF NOT EXISTS sources (
    id            TEXT PRIMARY KEY,
    fs_source_id  TEXT UNIQUE,
    gedcom_xref   TEXT UNIQUE,         -- original @S1@ anchor from GEDCOM
    title         TEXT,
    author        TEXT,
    publication   TEXT,
    citation      TEXT,
    url           TEXT,
    repository    TEXT,
    notes         TEXT,
    created_at    TEXT NOT NULL
);

-- Many-to-many link between persons/facts and sources.
CREATE TABLE IF NOT EXISTS person_sources (
    person_id  TEXT NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    source_id  TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    fact_id    TEXT REFERENCES facts(id) ON DELETE CASCADE,
    page       TEXT,                    -- citation detail (page, entry, etc.)
    quality    TEXT,                    -- GEDCOM QUAY: 0..3 or freeform
    notes      TEXT,
    origin     TEXT NOT NULL DEFAULT 'gedcom'
);

-- Include origin so the same (person, source, fact) claim can coexist with
-- different provenance (e.g. imported once from GEDCOM, later also attached on
-- FamilySearch). Without origin in the key, the second would silently no-op.
CREATE UNIQUE INDEX IF NOT EXISTS idx_person_sources_unique
    ON person_sources(person_id, source_id, COALESCE(fact_id, ''), origin);
CREATE INDEX IF NOT EXISTS idx_person_sources_origin ON person_sources(origin);

-- Research task log.
CREATE TABLE IF NOT EXISTS research_tasks (
    id          TEXT PRIMARY KEY,
    person_id   TEXT REFERENCES persons(id) ON DELETE SET NULL,
    goal        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','in_progress','done','abandoned')),
    notes       TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_person ON research_tasks(person_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON research_tasks(status);

-- Append-only log of API activity against FamilySearch.
CREATE TABLE IF NOT EXISTS sync_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    fs_person_id   TEXT,
    action         TEXT NOT NULL,             -- 'fetched' | 'pushed' | 'merged' | 'reviewed'
    payload        TEXT,                      -- JSON
    occurred_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sync_log_fs_pid ON sync_log(fs_person_id);
