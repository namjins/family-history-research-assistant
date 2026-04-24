"""Query helpers for the local working copy.

Keep sqlite3 calls confined to this module. Feature code calls these helpers
instead of writing raw SQL.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def upsert_person(
    conn: sqlite3.Connection,
    *,
    fs_person_id: str | None = None,
    gedcom_xref: str | None = None,
    given_names: str | None = None,
    surname: str | None = None,
    sex: str | None = None,
    is_living: bool = False,
    notes: str | None = None,
) -> str:
    """Insert or update a person. Returns internal id.

    Matching precedence: fs_person_id > gedcom_xref. Callers should pick whichever
    stable identifier they have.
    """
    existing = None
    if fs_person_id:
        existing = conn.execute(
            "SELECT id FROM persons WHERE fs_person_id = ?", (fs_person_id,)
        ).fetchone()
    if existing is None and gedcom_xref:
        existing = conn.execute(
            "SELECT id FROM persons WHERE gedcom_xref = ?", (gedcom_xref,)
        ).fetchone()

    now = _now()
    if existing is None:
        person_id = _new_id()
        conn.execute(
            """
            INSERT INTO persons (
                id, fs_person_id, gedcom_xref, given_names, surname, sex,
                is_living, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person_id,
                fs_person_id,
                gedcom_xref,
                given_names,
                surname,
                sex,
                1 if is_living else 0,
                notes,
                now,
                now,
            ),
        )
        return person_id

    person_id = existing["id"]
    conn.execute(
        """
        UPDATE persons SET
            fs_person_id = COALESCE(?, fs_person_id),
            gedcom_xref  = COALESCE(?, gedcom_xref),
            given_names  = COALESCE(?, given_names),
            surname      = COALESCE(?, surname),
            sex          = COALESCE(?, sex),
            is_living    = ?,
            notes        = COALESCE(?, notes),
            updated_at   = ?
        WHERE id = ?
        """,
        (
            fs_person_id,
            gedcom_xref,
            given_names,
            surname,
            sex,
            1 if is_living else 0,
            notes,
            now,
            person_id,
        ),
    )
    return person_id


def get_person(conn: sqlite3.Connection, person_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM persons WHERE id = ?", (person_id,)).fetchone()
    return dict(row) if row else None


def find_person_by_fs_id(
    conn: sqlite3.Connection, fs_person_id: str
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM persons WHERE fs_person_id = ?", (fs_person_id,)
    ).fetchone()
    return dict(row) if row else None


def search_persons(
    conn: sqlite3.Connection,
    *,
    surname: str | None = None,
    given_names: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Simple LIKE search across the local working copy.

    Case-insensitive substring match. For anything more sophisticated, add a
    proper FTS5 index later.
    """
    clauses: list[str] = []
    params: list[Any] = []
    if surname:
        clauses.append("LOWER(surname) LIKE ?")
        params.append(f"%{surname.lower()}%")
    if given_names:
        clauses.append("LOWER(given_names) LIKE ?")
        params.append(f"%{given_names.lower()}%")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(limit)
    rows = conn.execute(
        f"SELECT * FROM persons {where} ORDER BY surname, given_names LIMIT ?",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def upsert_fact(
    conn: sqlite3.Connection,
    *,
    person_id: str,
    fact_type: str,
    date_raw: str | None = None,
    date_normalized: str | None = None,
    place_raw: str | None = None,
    place_normalized: str | None = None,
    value: str | None = None,
    evidence_quality: str | None = None,
    origin: str = "gedcom",
    origin_ref: str | None = None,
) -> str:
    fact_id = _new_id()
    conn.execute(
        """
        INSERT INTO facts (
            id, person_id, fact_type, date_raw, date_normalized,
            place_raw, place_normalized, value, evidence_quality,
            origin, origin_ref, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fact_id,
            person_id,
            fact_type,
            date_raw,
            date_normalized,
            place_raw,
            place_normalized,
            value,
            evidence_quality,
            origin,
            origin_ref,
            _now(),
        ),
    )
    return fact_id


def get_facts_for_person(
    conn: sqlite3.Connection, person_id: str
) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM facts WHERE person_id = ? ORDER BY fact_type, date_normalized",
        (person_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def upsert_relationship(
    conn: sqlite3.Connection,
    *,
    rel_type: str,
    person1_id: str,
    person2_id: str,
    role1: str | None = None,
    role2: str | None = None,
    origin: str = "gedcom",
    origin_ref: str | None = None,
) -> str:
    existing = conn.execute(
        """
        SELECT id FROM relationships
        WHERE rel_type = ? AND person1_id = ? AND person2_id = ?
        """,
        (rel_type, person1_id, person2_id),
    ).fetchone()
    if existing:
        return existing["id"]

    rel_id = _new_id()
    conn.execute(
        """
        INSERT INTO relationships (
            id, rel_type, person1_id, person2_id, role1, role2,
            origin, origin_ref, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            rel_id,
            rel_type,
            person1_id,
            person2_id,
            role1,
            role2,
            origin,
            origin_ref,
            _now(),
        ),
    )
    return rel_id


def get_relationships_for_person(
    conn: sqlite3.Connection, person_id: str
) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM relationships
        WHERE person1_id = ? OR person2_id = ?
        """,
        (person_id, person_id),
    ).fetchall()
    return [dict(r) for r in rows]


def delete_gedcom_facts_for_person(conn: sqlite3.Connection, person_id: str) -> int:
    """Delete all facts that originated from a GEDCOM import for one person.

    Used by the GEDCOM importer to stay idempotent on re-imports without
    clobbering facts that came from FamilySearch or local edits.
    """
    cursor = conn.execute(
        "DELETE FROM facts WHERE person_id = ? AND origin = 'gedcom'",
        (person_id,),
    )
    return cursor.rowcount or 0


def upsert_source(
    conn: sqlite3.Connection,
    *,
    fs_source_id: str | None = None,
    gedcom_xref: str | None = None,
    title: str | None = None,
    author: str | None = None,
    publication: str | None = None,
    citation: str | None = None,
    url: str | None = None,
    repository: str | None = None,
    notes: str | None = None,
) -> str:
    """Insert or update a source. Returns internal id.

    Match precedence: fs_source_id > gedcom_xref.
    """
    existing = None
    if fs_source_id:
        existing = conn.execute(
            "SELECT id FROM sources WHERE fs_source_id = ?", (fs_source_id,)
        ).fetchone()
    if existing is None and gedcom_xref:
        existing = conn.execute(
            "SELECT id FROM sources WHERE gedcom_xref = ?", (gedcom_xref,)
        ).fetchone()

    if existing is None:
        source_id = _new_id()
        conn.execute(
            """
            INSERT INTO sources (
                id, fs_source_id, gedcom_xref, title, author, publication,
                citation, url, repository, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                fs_source_id,
                gedcom_xref,
                title,
                author,
                publication,
                citation,
                url,
                repository,
                notes,
                _now(),
            ),
        )
        return source_id

    source_id = existing["id"]
    conn.execute(
        """
        UPDATE sources SET
            fs_source_id = COALESCE(?, fs_source_id),
            gedcom_xref  = COALESCE(?, gedcom_xref),
            title        = COALESCE(?, title),
            author       = COALESCE(?, author),
            publication  = COALESCE(?, publication),
            citation     = COALESCE(?, citation),
            url          = COALESCE(?, url),
            repository   = COALESCE(?, repository),
            notes        = COALESCE(?, notes)
        WHERE id = ?
        """,
        (
            fs_source_id,
            gedcom_xref,
            title,
            author,
            publication,
            citation,
            url,
            repository,
            notes,
            source_id,
        ),
    )
    return source_id


def link_person_source(
    conn: sqlite3.Connection,
    *,
    person_id: str,
    source_id: str,
    fact_id: str | None = None,
    page: str | None = None,
    quality: str | None = None,
    notes: str | None = None,
    origin: str = "gedcom",
) -> None:
    """Attach a source to a person (optionally a specific fact).

    Idempotent via the (person_id, source_id, fact_id) unique index.
    """
    conn.execute(
        """
        INSERT OR IGNORE INTO person_sources (
            person_id, source_id, fact_id, page, quality, notes, origin
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (person_id, source_id, fact_id, page, quality, notes, origin),
    )


def delete_gedcom_person_sources_for_person(
    conn: sqlite3.Connection, person_id: str
) -> int:
    """Remove all gedcom-origin source links for a person."""
    cursor = conn.execute(
        "DELETE FROM person_sources WHERE person_id = ? AND origin = 'gedcom'",
        (person_id,),
    )
    return cursor.rowcount or 0


def log_sync_event(
    conn: sqlite3.Connection,
    *,
    action: str,
    fs_person_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Append an entry to ``sync_log``. Commits immediately.

    Used by the MCP server to record every outbound FamilySearch call. The
    ``payload`` dict is serialized to JSON; keep it small (endpoint, params,
    status, not response bodies).
    """
    conn.execute(
        "INSERT INTO sync_log (fs_person_id, action, payload, occurred_at) "
        "VALUES (?, ?, ?, ?)",
        (
            fs_person_id,
            action,
            json.dumps(payload) if payload is not None else None,
            _now(),
        ),
    )
    conn.commit()


def recent_sync_events(
    conn: sqlite3.Connection, limit: int = 50
) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM sync_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]


_LIVING_SAFE_FIELDS = {"id", "fs_person_id", "given_names", "surname", "sex", "is_living"}


def redact_if_living(person: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``person`` with sensitive fields removed for living people.

    Preserves identifiers and name components (used for research planning);
    removes dates, places, notes, sync timestamps. Non-living persons pass
    through unchanged.
    """
    if not person.get("is_living"):
        return person
    redacted = {k: v for k, v in person.items() if k in _LIVING_SAFE_FIELDS}
    redacted["_redacted"] = (
        "Living person — details hidden by default. "
        "Call again with include_living=True to bypass."
    )
    return redacted
