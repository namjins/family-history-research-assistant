"""Tests for the MCP server — tool registration, local tools, PII redaction, sync_log."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from fhra.config import Config
from fhra.db import open_db, upsert_fact, upsert_person
from fhra.mcp_server.server import build_server


def _cfg(tmp_db_path: Path, tmp_path: Path) -> Config:
    return Config(
        client_id="cid",
        redirect_uri="http://localhost:5000/cb",
        environment="integration",
        db_path=tmp_db_path,
        token_cache_path=tmp_path / "tokens.json",
    )


def _call_tool(server, name: str, **kwargs):
    """Invoke a FastMCP tool by name and return parsed JSON output.

    FastMCP ``call_tool`` is async; we wrap it for sync test usage. It returns
    a list of content blocks; we extract the text from each and parse JSON.
    """
    async def _run():
        return await server.call_tool(name, kwargs)

    result = asyncio.run(_run())
    # The exact shape is ([content_blocks], meta). Each content block has a ``text`` field.
    blocks = result[0] if isinstance(result, tuple) else result
    text = "".join(getattr(b, "text", "") for b in blocks)
    return json.loads(text)


# ---- Registration -----------------------------------------------------------


def test_expected_tools_registered(tmp_db_path: Path, tmp_path: Path) -> None:
    server = build_server(_cfg(tmp_db_path, tmp_path))
    tool_names = {t.name for t in asyncio.run(server.list_tools())}
    expected = {
        "local_search_persons",
        "local_get_person",
        "local_get_relationships",
        "local_recent_sync_events",
        "fs_whoami",
        "fs_get_person",
        "fs_get_person_with_relationships",
        "fs_get_person_sources",
        "fs_get_person_matches",
        "fs_get_ancestry",
        "fs_search_persons",
        "fs_search_records",
        "fs_place_search",
    }
    assert expected <= tool_names, f"missing tools: {expected - tool_names}"


# ---- local_search_persons: PII redaction ------------------------------------


def test_local_search_redacts_living_by_default(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    with open_db(tmp_db_path) as conn:
        p = upsert_person(
            conn, surname="Snijman", given_names="Marc", is_living=True, notes="sensitive"
        )
        upsert_fact(
            conn, person_id=p, fact_type="BIRT", date_raw="1 JAN 1990", origin="local_edit"
        )

    server = build_server(_cfg(tmp_db_path, tmp_path))
    results = _call_tool(server, "local_search_persons", surname="snijman")
    assert len(results) == 1
    row = results[0]
    assert row["given_names"] == "Marc"
    assert row.get("is_living") == 1
    assert "notes" not in row
    assert "_redacted" in row


def test_local_search_includes_living_when_flag_set(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    with open_db(tmp_db_path) as conn:
        upsert_person(
            conn, surname="Snijman", given_names="Marc", is_living=True, notes="ok to see"
        )

    server = build_server(_cfg(tmp_db_path, tmp_path))
    results = _call_tool(
        server, "local_search_persons", surname="snijman", include_living=True
    )
    assert results[0]["notes"] == "ok to see"


# ---- local_get_person -------------------------------------------------------


def test_local_get_person_by_fs_id(tmp_db_path: Path, tmp_path: Path) -> None:
    with open_db(tmp_db_path) as conn:
        p = upsert_person(
            conn, fs_person_id="L999-ZZZ", surname="Historical"
        )
        upsert_fact(conn, person_id=p, fact_type="BIRT", date_raw="1850", origin="gedcom")

    server = build_server(_cfg(tmp_db_path, tmp_path))
    data = _call_tool(server, "local_get_person", fs_person_id="L999-ZZZ")
    assert data["surname"] == "Historical"
    assert any(f["fact_type"] == "BIRT" for f in data["facts"])


def test_local_get_person_requires_an_id(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    server = build_server(_cfg(tmp_db_path, tmp_path))
    data = _call_tool(server, "local_get_person")
    assert "error" in data


def test_local_get_person_not_found(tmp_db_path: Path, tmp_path: Path) -> None:
    server = build_server(_cfg(tmp_db_path, tmp_path))
    data = _call_tool(server, "local_get_person", fs_person_id="NO-SUCH")
    assert data == {"error": "Person not found"}


def test_local_get_person_redacts_living(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    with open_db(tmp_db_path) as conn:
        upsert_person(
            conn, fs_person_id="LIVE-1", surname="Current",
            is_living=True, notes="private",
        )

    server = build_server(_cfg(tmp_db_path, tmp_path))
    data = _call_tool(server, "local_get_person", fs_person_id="LIVE-1")
    assert "notes" not in data
    assert "facts" not in data, "living person shouldn't include facts in redacted form"


# ---- fs_* tools: no token → auth error --------------------------------------


def test_fs_tool_without_token_returns_auth_error(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    server = build_server(_cfg(tmp_db_path, tmp_path))
    data = _call_tool(server, "fs_whoami")
    assert data["error"] == "auth"


def test_fs_auth_error_is_logged(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    server = build_server(_cfg(tmp_db_path, tmp_path))
    _call_tool(server, "fs_whoami")  # will fail with auth error
    events = _call_tool(server, "local_recent_sync_events")
    assert len(events) >= 1
    assert events[0]["action"] == "whoami"
    payload = json.loads(events[0]["payload"])
    assert payload["status"] == "auth_error"


def test_fs_get_person_accepts_if_none_match_arg(
    tmp_db_path: Path, tmp_path: Path
) -> None:
    """Regression: fs_get_person and fs_get_person_with_relationships must expose
    ``if_none_match`` as a tool arg so callers can do conditional GETs."""
    server = build_server(_cfg(tmp_db_path, tmp_path))
    tools = {t.name: t for t in asyncio.run(server.list_tools())}

    person_tool = tools["fs_get_person"]
    schema = person_tool.inputSchema
    assert "if_none_match" in schema["properties"], schema

    rel_tool = tools["fs_get_person_with_relationships"]
    schema = rel_tool.inputSchema
    assert "if_none_match" in schema["properties"], schema
