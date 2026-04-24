"""Tests for the DB layer (schema, queries, redaction, sync_log)."""

from __future__ import annotations

from pathlib import Path

import pytest

from fhra.db import (
    delete_gedcom_facts_for_person,
    delete_gedcom_person_sources_for_person,
    find_person_by_fs_id,
    get_facts_for_person,
    get_person,
    get_relationships_for_person,
    init_db,
    link_person_source,
    log_sync_event,
    open_db,
    recent_sync_events,
    redact_if_living,
    search_persons,
    upsert_fact,
    upsert_person,
    upsert_relationship,
    upsert_source,
)


# ---- Basic CRUD --------------------------------------------------------------


def test_init_creates_all_tables(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        names = {r["name"] for r in rows}
    required = {
        "persons", "facts", "relationships", "sources", "person_sources",
        "research_tasks", "sync_log", "schema_meta",
    }
    assert required <= names


def test_init_is_idempotent(tmp_db_path: Path) -> None:
    init_db(tmp_db_path)
    init_db(tmp_db_path)  # second call must not fail
    with open_db(tmp_db_path) as conn:
        version = conn.execute(
            "SELECT value FROM schema_meta WHERE key = 'version'"
        ).fetchone()
    assert version["value"] == "1"


def test_upsert_person_dedupe_by_gedcom_xref(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        p1 = upsert_person(conn, gedcom_xref="@I1@", surname="Snijman")
        p2 = upsert_person(conn, gedcom_xref="@I1@", given_names="Hans")
        assert p1 == p2
        row = get_person(conn, p1)
        assert row["surname"] == "Snijman"
        assert row["given_names"] == "Hans"


def test_upsert_person_dedupe_by_fs_id_takes_precedence(tmp_db_path: Path) -> None:
    """fs_person_id match wins over gedcom_xref match."""
    with open_db(tmp_db_path) as conn:
        a = upsert_person(conn, fs_person_id="L111-AAA", gedcom_xref="@I1@")
        # Even with a different xref, matching fs_person_id → same row
        b = upsert_person(conn, fs_person_id="L111-AAA", gedcom_xref="@I99@")
        assert a == b


def test_find_person_by_fs_id(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        upsert_person(conn, fs_person_id="L123-ABC", surname="Snijman")
        row = find_person_by_fs_id(conn, "L123-ABC")
        assert row is not None
        assert row["surname"] == "Snijman"
        assert find_person_by_fs_id(conn, "NO-SUCH") is None


# ---- Search ------------------------------------------------------------------


def test_search_persons_surname_substring(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        upsert_person(conn, surname="Snijman", given_names="Hans")
        upsert_person(conn, surname="Snijman", given_names="Marc")
        upsert_person(conn, surname="De Vries", given_names="Anneke")
        hits = search_persons(conn, surname="snij")
        assert {h["given_names"] for h in hits} == {"Hans", "Marc"}


def test_search_persons_both_filters(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        upsert_person(conn, surname="Smith", given_names="John")
        upsert_person(conn, surname="Smith", given_names="Jane")
        upsert_person(conn, surname="Jones", given_names="John")
        hits = search_persons(conn, surname="smith", given_names="john")
        assert len(hits) == 1
        assert hits[0]["surname"] == "Smith"
        assert hits[0]["given_names"] == "John"


def test_search_persons_empty_filter_returns_all(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        upsert_person(conn, surname="A")
        upsert_person(conn, surname="B")
        hits = search_persons(conn, limit=10)
        assert len(hits) == 2


def test_search_persons_limit_respected(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        for i in range(10):
            upsert_person(conn, surname=f"Test{i:02d}")
        hits = search_persons(conn, limit=3)
        assert len(hits) == 3


# ---- Facts -------------------------------------------------------------------


def test_upsert_and_get_facts(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        p = upsert_person(conn, surname="X")
        upsert_fact(
            conn,
            person_id=p,
            fact_type="BIRT",
            date_raw="1 JAN 1900",
            place_raw="Amsterdam",
            origin="gedcom",
        )
        upsert_fact(
            conn,
            person_id=p,
            fact_type="DEAT",
            date_raw="1970",
            place_raw="Amsterdam",
            origin="gedcom",
        )
        facts = get_facts_for_person(conn, p)
        tags = {f["fact_type"] for f in facts}
        assert tags == {"BIRT", "DEAT"}


def test_delete_gedcom_facts_preserves_other_origins(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        p = upsert_person(conn, surname="X")
        upsert_fact(conn, person_id=p, fact_type="BIRT", origin="gedcom")
        upsert_fact(conn, person_id=p, fact_type="OCCU", origin="local_edit")
        upsert_fact(conn, person_id=p, fact_type="DEAT", origin="familysearch")
        deleted = delete_gedcom_facts_for_person(conn, p)
        assert deleted == 1
        remaining = get_facts_for_person(conn, p)
        assert {f["origin"] for f in remaining} == {"local_edit", "familysearch"}


# ---- Relationships -----------------------------------------------------------


def test_relationship_upsert_is_idempotent(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        a = upsert_person(conn, surname="Parent")
        b = upsert_person(conn, surname="Child")
        r1 = upsert_relationship(
            conn, rel_type="parent_child", person1_id=a, person2_id=b, role1="father"
        )
        r2 = upsert_relationship(
            conn, rel_type="parent_child", person1_id=a, person2_id=b, role1="father"
        )
        assert r1 == r2


def test_get_relationships_returns_both_sides(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        a = upsert_person(conn, surname="Parent")
        b = upsert_person(conn, surname="Child")
        upsert_relationship(
            conn, rel_type="parent_child", person1_id=a, person2_id=b,
        )
        # Both sides return the same row
        assert len(get_relationships_for_person(conn, a)) == 1
        assert len(get_relationships_for_person(conn, b)) == 1


# ---- Sources -----------------------------------------------------------------


def test_upsert_source_dedupes_by_gedcom_xref(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        s1 = upsert_source(conn, gedcom_xref="@S1@", title="Census")
        s2 = upsert_source(conn, gedcom_xref="@S1@", author="NARA")
        assert s1 == s2
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (s1,)).fetchone()
        assert row["title"] == "Census"
        assert row["author"] == "NARA"


def test_upsert_source_dedupes_by_fs_source_id(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        s1 = upsert_source(conn, fs_source_id="FS123", title="A")
        s2 = upsert_source(conn, fs_source_id="FS123", title="B")
        assert s1 == s2


def test_link_person_source_idempotent(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        p = upsert_person(conn, surname="X")
        s = upsert_source(conn, title="Source")
        link_person_source(conn, person_id=p, source_id=s, page="p1")
        link_person_source(conn, person_id=p, source_id=s, page="p1")
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM person_sources WHERE person_id = ?", (p,)
        ).fetchone()
        assert count["c"] == 1


def test_link_person_source_fact_id_differentiates(tmp_db_path: Path) -> None:
    """Same (person, source) with different fact_id should coexist."""
    with open_db(tmp_db_path) as conn:
        p = upsert_person(conn, surname="X")
        s = upsert_source(conn, title="Source")
        f1 = upsert_fact(conn, person_id=p, fact_type="BIRT", origin="gedcom")
        f2 = upsert_fact(conn, person_id=p, fact_type="DEAT", origin="gedcom")
        link_person_source(conn, person_id=p, source_id=s, fact_id=f1)
        link_person_source(conn, person_id=p, source_id=s, fact_id=f2)
        link_person_source(conn, person_id=p, source_id=s, fact_id=None)
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM person_sources WHERE person_id = ?", (p,)
        ).fetchone()
        assert count["c"] == 3


def test_delete_gedcom_person_sources_origin_scoped(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        p = upsert_person(conn, surname="X")
        s = upsert_source(conn, title="Source")
        link_person_source(conn, person_id=p, source_id=s, origin="gedcom", page="p1")
        link_person_source(
            conn, person_id=p, source_id=s, origin="familysearch", page="p2"
        )
        deleted = delete_gedcom_person_sources_for_person(conn, p)
        assert deleted == 1
        remaining = conn.execute(
            "SELECT origin FROM person_sources WHERE person_id = ?", (p,)
        ).fetchall()
        assert [r["origin"] for r in remaining] == ["familysearch"]


# ---- Sync log ----------------------------------------------------------------


def test_sync_log_insert_and_read(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        log_sync_event(
            conn,
            action="get_person",
            fs_person_id="L123-ABC",
            payload={"endpoint": "get_person", "status": "ok"},
        )
        log_sync_event(
            conn,
            action="search_persons",
            payload={"endpoint": "search_persons", "status": "ok"},
        )
        rows = recent_sync_events(conn, limit=10)
        assert len(rows) == 2
        assert rows[0]["action"] == "search_persons", "newest first"
        assert rows[1]["fs_person_id"] == "L123-ABC"


def test_sync_log_respects_limit(tmp_db_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        for i in range(5):
            log_sync_event(conn, action=f"action_{i}")
        assert len(recent_sync_events(conn, limit=3)) == 3


# ---- PII redaction -----------------------------------------------------------


def test_redact_if_living_hides_sensitive_fields() -> None:
    person = {
        "id": "abc",
        "fs_person_id": "L123",
        "given_names": "Jane",
        "surname": "Doe",
        "sex": "F",
        "is_living": 1,
        "notes": "secret",
        "last_synced_at": "2026-04-24",
        "created_at": "x",
        "updated_at": "y",
    }
    redacted = redact_if_living(person)
    assert redacted["given_names"] == "Jane"
    assert redacted["is_living"] == 1
    assert "notes" not in redacted
    assert "last_synced_at" not in redacted
    assert "_redacted" in redacted


def test_redact_if_living_passes_through_dead_person() -> None:
    person = {"id": "x", "given_names": "Old", "surname": "Person", "is_living": 0, "notes": "fine"}
    assert redact_if_living(person) == person


# ---- open_db actually closes -------------------------------------------------


def test_open_db_closes_connection(tmp_db_path: Path) -> None:
    """Regression: open_db must close the connection on exit."""
    with open_db(tmp_db_path) as conn:
        pass
    with pytest.raises(Exception):
        # Using a closed connection should raise ProgrammingError.
        conn.execute("SELECT 1")  # noqa: F821 — deliberate post-close access
