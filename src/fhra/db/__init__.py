"""SQLite working copy — schema, migrations, and query helpers."""

from fhra.db.connection import connect, init_db, open_db, transaction
from fhra.db.queries import (
    delete_gedcom_facts_for_person,
    delete_gedcom_person_sources_for_person,
    find_person_by_fs_id,
    get_facts_for_person,
    get_person,
    get_relationships_for_person,
    link_person_source,
    log_sync_event,
    recent_sync_events,
    redact_if_living,
    search_persons,
    upsert_fact,
    upsert_person,
    upsert_relationship,
    upsert_source,
)

__all__ = [
    "connect",
    "delete_gedcom_facts_for_person",
    "delete_gedcom_person_sources_for_person",
    "find_person_by_fs_id",
    "get_facts_for_person",
    "get_person",
    "get_relationships_for_person",
    "init_db",
    "link_person_source",
    "log_sync_event",
    "open_db",
    "recent_sync_events",
    "redact_if_living",
    "search_persons",
    "transaction",
    "upsert_fact",
    "upsert_person",
    "upsert_relationship",
    "upsert_source",
]
