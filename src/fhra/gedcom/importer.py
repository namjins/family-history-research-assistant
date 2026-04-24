"""Import a GEDCOM file into the local working-copy database.

Uses ``ged4py`` for parsing. Handles the FamilySearch-pulled GEDCOM format from
RootsMagic, including FSIDs (typically carried as REFN with TYPE FamilySearch,
or as a ``_FSFTID`` / ``_FSID`` custom tag depending on exporter).

**Idempotency**: re-running the importer against the same file produces the same
database state for persons, facts, relationships, and source links *that came
from this GEDCOM*. For each person we first remove their existing
``origin='gedcom'`` facts and source-links, then re-insert — so FS-synced and
locally-edited facts are preserved across re-imports.

**Sources**: level-0 ``SOUR`` records are imported into the ``sources`` table;
citation pointers on individuals and on individual events create rows in
``person_sources``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from ged4py.parser import GedcomReader

from fhra.db.connection import open_db, transaction
from fhra.db.queries import (
    delete_gedcom_facts_for_person,
    delete_gedcom_person_sources_for_person,
    link_person_source,
    upsert_fact,
    upsert_person,
    upsert_relationship,
    upsert_source,
)

log = logging.getLogger(__name__)

_FACT_TAGS = {
    "BIRT", "DEAT", "CHR", "BURI", "CREM",
    "MARR", "DIV", "ENGA",
    "RESI", "OCCU", "EDUC", "RELI",
    "IMMI", "EMIG", "NATU",
    "CENS", "PROB", "WILL",
    "GRAD", "RETI",
}


@dataclass
class ImportStats:
    persons: int = 0
    facts: int = 0
    relationships: int = 0
    families: int = 0
    sources: int = 0
    source_links: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "persons": self.persons,
            "facts": self.facts,
            "relationships": self.relationships,
            "families": self.families,
            "sources": self.sources,
            "source_links": self.source_links,
        }


def _extract_fs_person_id(indi) -> str | None:
    """Look for a FamilySearch person ID on an individual.

    FamilySearch GEDCOM exports may carry the PID in several ways:
      - ``REFN`` with a child ``TYPE`` of 'FamilySearch' or 'FSID'
      - custom tags ``_FSFTID`` or ``_FSID``
    """
    for tag in ("_FSFTID", "_FSID"):
        sub = indi.sub_tag(tag)
        if sub is not None and sub.value:
            return str(sub.value).strip()

    for refn in indi.sub_tags("REFN"):
        type_sub = refn.sub_tag("TYPE")
        type_val = (type_sub.value or "").lower() if type_sub else ""
        if type_val in {"familysearch", "fsid", "fs"} and refn.value:
            return str(refn.value).strip()
    return None


def _name_parts(indi) -> tuple[str | None, str | None]:
    name = indi.name
    if name is None:
        return None, None
    given = name.given or None
    surname = name.surname or None
    return given, surname


def _sex(indi) -> str | None:
    sub = indi.sub_tag("SEX")
    if sub is None or not sub.value:
        return None
    v = str(sub.value).strip().upper()
    return v if v in {"M", "F", "U"} else None


def _import_source_records(parser, conn, xref_to_source_id: dict[str, str]) -> int:
    """Pass 0: import level-0 SOUR records into the sources table.

    Returns the count of imported sources.
    """
    count = 0
    for sour in parser.records0("SOUR"):
        title = _tag_value(sour, "TITL")
        author = _tag_value(sour, "AUTH")
        publication = _tag_value(sour, "PUBL")
        # REPO is a pointer to a repository record; capture the raw ref for now.
        repo_sub = sour.sub_tag("REPO")
        repository = str(repo_sub.value) if repo_sub and repo_sub.value else None

        source_id = upsert_source(
            conn,
            gedcom_xref=sour.xref_id,
            title=title,
            author=author,
            publication=publication,
            repository=repository,
        )
        xref_to_source_id[sour.xref_id] = source_id
        count += 1
    return count


def _tag_value(record, tag: str) -> str | None:
    sub = record.sub_tag(tag)
    if sub is None or not sub.value:
        return None
    return str(sub.value).strip()


def _link_citations(
    record,
    conn,
    *,
    person_id: str,
    fact_id: str | None,
    xref_to_source_id: dict[str, str],
) -> int:
    """For a given GEDCOM record (person or event), link any ``SOUR`` citations
    to ``person_sources``. Returns count of links created.

    Uses ``follow=False`` so pointer citations (``SOUR @S1@``) keep their raw
    ``@S1@`` value instead of being auto-dereferenced into the Source record.
    Inline citations (``SOUR Some free text``) also come through as raw.
    """
    count = 0
    for sour_ref in record.sub_tags("SOUR", follow=False):
        value = str(sour_ref.value).strip() if sour_ref.value else ""
        source_id: str | None = None
        if value.startswith("@") and value.endswith("@"):
            source_id = xref_to_source_id.get(value)
        elif value:
            # Inline source — create an ad-hoc source row using the free text.
            source_id = upsert_source(conn, title=value)

        if source_id is None:
            continue

        page = _tag_value(sour_ref, "PAGE")
        quality = _tag_value(sour_ref, "QUAY")
        note = _tag_value(sour_ref, "NOTE")
        link_person_source(
            conn,
            person_id=person_id,
            source_id=source_id,
            fact_id=fact_id,
            page=page,
            quality=quality,
            notes=note,
            origin="gedcom",
        )
        count += 1
    return count


def _import_events(
    conn,
    person_id: str,
    record,
    xref_to_source_id: dict[str, str],
    stats: ImportStats,
) -> None:
    """Walk child records on an individual/family, importing recognized facts
    and linking any SOUR citations attached to each fact.
    """
    for sub in record.sub_records:
        tag = sub.tag
        if tag not in _FACT_TAGS:
            continue
        date_raw = _tag_value(sub, "DATE")
        place_raw = _tag_value(sub, "PLAC")
        value = str(sub.value).strip() if sub.value else None
        fact_id = upsert_fact(
            conn,
            person_id=person_id,
            fact_type=tag,
            date_raw=date_raw,
            place_raw=place_raw,
            value=value,
            origin="gedcom",
            origin_ref=f"{record.xref_id}:{tag}",
        )
        stats.facts += 1
        stats.source_links += _link_citations(
            sub,
            conn,
            person_id=person_id,
            fact_id=fact_id,
            xref_to_source_id=xref_to_source_id,
        )


def import_gedcom(db_path: Path, gedcom_path: Path) -> ImportStats:
    """Import a GEDCOM file into the SQLite working copy at ``db_path``.

    Idempotent for persons, facts, relationships, and source-links that
    originated from GEDCOM.
    """
    stats = ImportStats()
    xref_to_id: dict[str, str] = {}
    xref_to_source_id: dict[str, str] = {}

    with open_db(db_path) as conn, transaction(conn):
        with GedcomReader(str(gedcom_path)) as parser:
            # Pass 0: source records
            stats.sources = _import_source_records(parser, conn, xref_to_source_id)

            # Pass 1: individuals — facts and person-level citations
            for indi in parser.records0("INDI"):
                given, surname = _name_parts(indi)
                person_id = upsert_person(
                    conn,
                    fs_person_id=_extract_fs_person_id(indi),
                    gedcom_xref=indi.xref_id,
                    given_names=given,
                    surname=surname,
                    sex=_sex(indi),
                )
                xref_to_id[indi.xref_id] = person_id
                stats.persons += 1

                # Idempotency: clear this person's previous GEDCOM-origin facts
                # and source-links before re-inserting.
                delete_gedcom_facts_for_person(conn, person_id)
                delete_gedcom_person_sources_for_person(conn, person_id)

                _import_events(conn, person_id, indi, xref_to_source_id, stats)

                # Person-level SOUR citations (not attached to a specific fact).
                stats.source_links += _link_citations(
                    indi,
                    conn,
                    person_id=person_id,
                    fact_id=None,
                    xref_to_source_id=xref_to_source_id,
                )

            # Pass 2: families → parent-child + spouse relationships
            # Use follow=False so HUSB/WIFE/CHIL come through as raw pointers
            # (".value" is '@I1@', not the dereferenced Individual record).
            for fam in parser.records0("FAM"):
                stats.families += 1
                husb_sub = fam.sub_tag("HUSB", follow=False)
                wife_sub = fam.sub_tag("WIFE", follow=False)
                husb_xref = str(husb_sub.value).strip() if husb_sub and husb_sub.value else None
                wife_xref = str(wife_sub.value).strip() if wife_sub and wife_sub.value else None
                husb_id = xref_to_id.get(husb_xref) if husb_xref else None
                wife_id = xref_to_id.get(wife_xref) if wife_xref else None

                if husb_id and wife_id:
                    upsert_relationship(
                        conn,
                        rel_type="spouse",
                        person1_id=husb_id,
                        person2_id=wife_id,
                        role1="spouse",
                        role2="spouse",
                        origin="gedcom",
                        origin_ref=fam.xref_id,
                    )
                    stats.relationships += 1

                for chil in fam.sub_tags("CHIL", follow=False):
                    chil_xref = str(chil.value).strip() if chil.value else None
                    child_id = xref_to_id.get(chil_xref) if chil_xref else None
                    if child_id is None:
                        continue
                    if husb_id:
                        upsert_relationship(
                            conn,
                            rel_type="parent_child",
                            person1_id=husb_id,
                            person2_id=child_id,
                            role1="father",
                            role2="child",
                            origin="gedcom",
                            origin_ref=fam.xref_id,
                        )
                        stats.relationships += 1
                    if wife_id:
                        upsert_relationship(
                            conn,
                            rel_type="parent_child",
                            person1_id=wife_id,
                            person2_id=child_id,
                            role1="mother",
                            role2="child",
                            origin="gedcom",
                            origin_ref=fam.xref_id,
                        )
                        stats.relationships += 1
    return stats
