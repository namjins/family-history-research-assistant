"""Tests for the GEDCOM → SQLite importer."""

from __future__ import annotations

from pathlib import Path

from fhra.db import (
    find_person_by_fs_id,
    get_facts_for_person,
    get_relationships_for_person,
    open_db,
    search_persons,
)
from fhra.gedcom.importer import import_gedcom


def test_basic_import_counts(tmp_db_path: Path, sample_gedcom: Path) -> None:
    stats = import_gedcom(tmp_db_path, sample_gedcom)
    assert stats.persons == 3
    assert stats.families == 1
    assert stats.sources == 2
    # facts: Hans BIRT+DEAT, Anneke BIRT, Marc BIRT+OCCU = 5
    assert stats.facts == 5
    # relationships: husb+wife + 2 parent-child (father-child, mother-child)
    assert stats.relationships == 3
    # source_links: Hans BIRT→S2, Marc BIRT→S1, Marc OCCU→inline = 3
    assert stats.source_links == 3


def test_persons_identified_and_named(tmp_db_path: Path, sample_gedcom: Path) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        hits = search_persons(conn, surname="Snijman")
        assert len(hits) == 2
        assert {h["given_names"] for h in hits} == {"Hans", "Marc"}


def test_fsid_extraction_via_fsftid(tmp_db_path: Path, sample_gedcom: Path) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        hans = find_person_by_fs_id(conn, "L123-ABC")
        assert hans is not None
        assert hans["given_names"] == "Hans"


def test_fsid_extraction_via_refn(tmp_db_path: Path, sample_gedcom: Path) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        anneke = find_person_by_fs_id(conn, "L456-DEF")
        assert anneke is not None
        assert anneke["surname"] == "de Vries"


def test_facts_captured_with_date_and_place(
    tmp_db_path: Path, sample_gedcom: Path
) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        hans = find_person_by_fs_id(conn, "L123-ABC")
        facts = get_facts_for_person(conn, hans["id"])
        birt = [f for f in facts if f["fact_type"] == "BIRT"][0]
        assert birt["date_raw"] == "1 JAN 1900"
        assert birt["place_raw"].startswith("Amsterdam")
        assert birt["origin"] == "gedcom"


def test_family_relationships_imported(tmp_db_path: Path, sample_gedcom: Path) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        hans = find_person_by_fs_id(conn, "L123-ABC")
        rels = get_relationships_for_person(conn, hans["id"])
        types = sorted(r["rel_type"] for r in rels)
        # Hans is husband (spouse) + father of Marc (parent_child)
        assert types == ["parent_child", "spouse"]


def test_sources_imported(tmp_db_path: Path, sample_gedcom: Path) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        rows = conn.execute(
            "SELECT gedcom_xref, title, author FROM sources "
            "WHERE gedcom_xref IS NOT NULL ORDER BY gedcom_xref"
        ).fetchall()
        assert [r["gedcom_xref"] for r in rows] == ["@S1@", "@S2@"]
        assert "1900 United States" in rows[0]["title"]
        assert rows[0]["author"] == "National Archives"


def test_fact_source_link_with_page_and_quality(
    tmp_db_path: Path, sample_gedcom: Path
) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        hans = find_person_by_fs_id(conn, "L123-ABC")
        row = conn.execute(
            """
            SELECT ps.page, ps.quality, s.gedcom_xref
            FROM person_sources ps
            JOIN sources s ON ps.source_id = s.id
            JOIN facts f ON ps.fact_id = f.id
            WHERE ps.person_id = ? AND f.fact_type = 'BIRT'
            """,
            (hans["id"],),
        ).fetchone()
        assert row is not None
        assert row["gedcom_xref"] == "@S2@"
        assert row["page"] == "entry 42"
        assert row["quality"] == "3"


def test_inline_source_citation_handled(
    tmp_db_path: Path, sample_gedcom: Path
) -> None:
    """Marc's OCCU has an inline free-text SOUR — should still create a source+link."""
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        marc_hits = [
            h for h in search_persons(conn, surname="Snijman", given_names="Marc")
        ]
        assert len(marc_hits) == 1
        marc = marc_hits[0]
        row = conn.execute(
            """
            SELECT s.title FROM person_sources ps
            JOIN sources s ON ps.source_id = s.id
            JOIN facts f ON ps.fact_id = f.id
            WHERE ps.person_id = ? AND f.fact_type = 'OCCU'
            """,
            (marc["id"],),
        ).fetchone()
        assert row is not None
        assert "Inline free-text" in row["title"]


def test_reimport_idempotent_for_facts(
    tmp_db_path: Path, sample_gedcom: Path
) -> None:
    """Re-importing the same file must not duplicate facts."""
    first = import_gedcom(tmp_db_path, sample_gedcom)
    second = import_gedcom(tmp_db_path, sample_gedcom)
    assert first.facts == second.facts
    with open_db(tmp_db_path) as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM facts").fetchone()
        assert total["c"] == first.facts


def test_reimport_preserves_non_gedcom_facts(
    tmp_db_path: Path, sample_gedcom: Path
) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        hans = find_person_by_fs_id(conn, "L123-ABC")
        # Simulate a user-added fact from local editing or a FS sync
        from fhra.db import upsert_fact

        upsert_fact(
            conn, person_id=hans["id"], fact_type="RESI", value="noted manually",
            origin="local_edit",
        )
        conn.commit()
    import_gedcom(tmp_db_path, sample_gedcom)  # re-import
    with open_db(tmp_db_path) as conn:
        hans = find_person_by_fs_id(conn, "L123-ABC")
        facts = get_facts_for_person(conn, hans["id"])
        assert any(
            f["origin"] == "local_edit" and f["fact_type"] == "RESI" for f in facts
        ), "local_edit fact must survive a GEDCOM re-import"


def test_reimport_idempotent_for_source_links(
    tmp_db_path: Path, sample_gedcom: Path
) -> None:
    import_gedcom(tmp_db_path, sample_gedcom)
    import_gedcom(tmp_db_path, sample_gedcom)
    with open_db(tmp_db_path) as conn:
        total = conn.execute(
            "SELECT COUNT(*) AS c FROM person_sources"
        ).fetchone()
        assert total["c"] == 3
