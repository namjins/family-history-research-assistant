"""MCP server exposing genealogy tools to Claude.

Tool surface:

  Local working copy (always available):
    - local_search_persons
    - local_get_person
    - local_get_relationships
    - local_recent_sync_events

  FamilySearch (requires FHRA_CLIENT_ID + `fhra auth login`):
    - fs_whoami
    - fs_get_person
    - fs_get_person_with_relationships
    - fs_get_person_sources
    - fs_get_person_matches
    - fs_get_ancestry
    - fs_search_persons
    - fs_search_records
    - fs_place_search

Read-only by design. Writes to the shared tree are a later milestone, gated
behind an explicit review workflow.

## PII handling

Local tools redact living-person details by default — only id/name/sex/is_living
are returned. Pass ``include_living=True`` to bypass (for legitimate research
on a living person's own records).

## Audit log

Every FamilySearch API call writes a row into the local ``sync_log`` table with
endpoint, params, and status. Inspect via ``local_recent_sync_events``.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from fhra.api import ApiResponse, FamilySearchClient, FamilySearchError
from fhra.auth import AuthError, load_token, refresh_if_needed
from fhra.config import Config, load_config
from fhra.db import (
    find_person_by_fs_id,
    get_facts_for_person,
    get_person,
    get_relationships_for_person,
    log_sync_event,
    open_db,
    recent_sync_events,
    redact_if_living,
    search_persons,
)

log = logging.getLogger(__name__)


class _FSClientPool:
    """Holds a single FamilySearchClient for the life of the MCP server.

    Lazy — only constructs on first use so the server can start without a
    client_id or cached token, and those tools just return an auth error
    until the user logs in.
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._client: FamilySearchClient | None = None

    def get(self) -> FamilySearchClient:
        if self._client is None:
            token = load_token(self._config.token_cache_path)
            if token is None:
                raise AuthError(
                    "No cached FamilySearch token. Run `fhra auth login` first."
                )
            token = refresh_if_needed(self._config, token)
            self._client = FamilySearchClient(self._config, token)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None


def _log_call(
    config: Config,
    *,
    action: str,
    fs_person_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Best-effort audit-log write. Never crashes the tool call if logging fails."""
    try:
        with open_db(config.db_path) as conn:
            log_sync_event(
                conn, action=action, fs_person_id=fs_person_id, payload=payload
            )
    except Exception as e:  # noqa: BLE001
        log.warning("sync_log write failed for %s: %s", action, e)


def _api_response_to_dict(resp: ApiResponse) -> dict[str, Any]:
    """Flatten an :class:`ApiResponse` into a JSON-serializable dict for tool output."""
    return {
        "body": resp.body,
        "etag": resp.etag,
        "status": resp.status,
        "not_modified": resp.not_modified,
    }


def build_server(config: Config | None = None) -> FastMCP:
    cfg = config or load_config()
    mcp = FastMCP("fhra")
    pool = _FSClientPool(cfg)

    # ------------ Local working-copy tools ----------------------------------

    @mcp.tool()
    def local_search_persons(
        surname: str | None = None,
        given_names: str | None = None,
        include_living: bool = False,
        limit: int = 25,
    ) -> str:
        """Search the local working-copy DB by surname and/or given names (substring).

        Living persons are redacted unless ``include_living=True``.
        """
        with open_db(cfg.db_path) as conn:
            rows = search_persons(
                conn, surname=surname, given_names=given_names, limit=limit
            )
        if not include_living:
            rows = [redact_if_living(r) for r in rows]
        return json.dumps(rows, indent=2, default=str)

    @mcp.tool()
    def local_get_person(
        person_id: str | None = None,
        fs_person_id: str | None = None,
        include_living: bool = False,
    ) -> str:
        """Fetch a person from the local DB by internal id or FamilySearch PID.

        Returns the person, all known facts, and all relationships.
        Living persons are redacted unless ``include_living=True``.
        """
        with open_db(cfg.db_path) as conn:
            if fs_person_id:
                person = find_person_by_fs_id(conn, fs_person_id)
            elif person_id:
                person = get_person(conn, person_id)
            else:
                return json.dumps({"error": "Provide person_id or fs_person_id"})
            if not person:
                return json.dumps({"error": "Person not found"})
            facts = get_facts_for_person(conn, person["id"])
            rels = get_relationships_for_person(conn, person["id"])

        if not include_living and person.get("is_living"):
            result = redact_if_living(person)
        else:
            result = {**person, "facts": facts, "relationships": rels}
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    def local_get_relationships(person_id: str) -> str:
        """Relationships involving a local-DB person (parent-child and spouse)."""
        with open_db(cfg.db_path) as conn:
            rows = get_relationships_for_person(conn, person_id)
        return json.dumps(rows, indent=2, default=str)

    @mcp.tool()
    def local_recent_sync_events(limit: int = 25) -> str:
        """Return recent entries from the FamilySearch audit log (``sync_log``)."""
        with open_db(cfg.db_path) as conn:
            rows = recent_sync_events(conn, limit=limit)
        return json.dumps(rows, indent=2, default=str)

    # ------------ FamilySearch API tools -----------------------------------

    def _safely(
        action: str,
        fn: Callable[[FamilySearchClient], Any],
        *,
        fs_person_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        payload: dict[str, Any] = {"endpoint": action}
        if params:
            payload["params"] = params
        try:
            client = pool.get()
            data = fn(client)
            payload["status"] = "ok"
            _log_call(cfg, action=action, fs_person_id=fs_person_id, payload=payload)
            return json.dumps(data, indent=2)
        except AuthError as e:
            payload["status"] = "auth_error"
            _log_call(cfg, action=action, fs_person_id=fs_person_id, payload=payload)
            return json.dumps({"error": "auth", "message": str(e)})
        except FamilySearchError as e:
            payload["status"] = f"http_{e.status}"
            payload["endpoint_path"] = e.endpoint
            _log_call(cfg, action=action, fs_person_id=fs_person_id, payload=payload)
            return json.dumps(
                {
                    "error": "familysearch",
                    "status": e.status,
                    "endpoint": e.endpoint,
                    "body": e.body[:1000],
                }
            )

    @mcp.tool()
    def fs_whoami() -> str:
        """Verify FamilySearch auth and return the current user profile."""
        return _safely("whoami", lambda c: c.get_current_user())

    @mcp.tool()
    def fs_get_person(fs_person_id: str, if_none_match: str | None = None) -> str:
        """Fetch a person from the FamilySearch shared tree.

        Returns ``{"body": ..., "etag": ..., "not_modified": bool}`` so callers
        can cache the ETag and pass it as ``if_none_match`` on the next call to
        short-circuit unchanged reads.
        """
        return _safely(
            "get_person",
            lambda c: _api_response_to_dict(
                c.get_person(fs_person_id, if_none_match=if_none_match)
            ),
            fs_person_id=fs_person_id,
        )

    @mcp.tool()
    def fs_get_person_with_relationships(
        fs_person_id: str, if_none_match: str | None = None
    ) -> str:
        """Person + immediate parents, spouses, and children.

        Supports conditional GET via ``if_none_match``; see :func:`fs_get_person`.
        """
        return _safely(
            "get_person_with_relationships",
            lambda c: _api_response_to_dict(
                c.get_person_with_relationships(
                    fs_person_id, if_none_match=if_none_match
                )
            ),
            fs_person_id=fs_person_id,
        )

    @mcp.tool()
    def fs_get_person_sources(fs_person_id: str) -> str:
        """Sources attached to a FamilySearch person."""
        return _safely(
            "get_person_sources",
            lambda c: c.get_person_sources(fs_person_id),
            fs_person_id=fs_person_id,
        )

    @mcp.tool()
    def fs_get_person_matches(fs_person_id: str) -> str:
        """Record-hint matches for a FamilySearch person."""
        return _safely(
            "get_person_matches",
            lambda c: c.get_person_matches(fs_person_id),
            fs_person_id=fs_person_id,
        )

    @mcp.tool()
    def fs_get_ancestry(fs_person_id: str, generations: int = 4) -> str:
        """Pedigree (self + ancestors) for a FamilySearch person."""
        return _safely(
            "get_ancestry",
            lambda c: c.get_ancestry(fs_person_id, generations=generations),
            fs_person_id=fs_person_id,
            params={"generations": generations},
        )

    @mcp.tool()
    def fs_search_persons(
        given_name: str | None = None,
        surname: str | None = None,
        birth_place: str | None = None,
        birth_date: str | None = None,
        death_place: str | None = None,
        death_date: str | None = None,
        father_surname: str | None = None,
        mother_surname: str | None = None,
        spouse_surname: str | None = None,
        count: int = 20,
    ) -> str:
        """Search the FamilySearch Family Tree for persons."""
        params = {
            "given_name": given_name,
            "surname": surname,
            "birth_place": birth_place,
            "birth_date": birth_date,
            "death_place": death_place,
            "death_date": death_date,
            "father_surname": father_surname,
            "mother_surname": mother_surname,
            "spouse_surname": spouse_surname,
            "count": count,
        }
        return _safely(
            "search_persons",
            lambda c: c.search_persons(**{k: v for k, v in params.items() if v is not None}),
            params={k: v for k, v in params.items() if v is not None},
        )

    @mcp.tool()
    def fs_search_records(
        given_name: str | None = None,
        surname: str | None = None,
        place: str | None = None,
        birth_date: str | None = None,
        death_date: str | None = None,
        collection: str | None = None,
        count: int = 20,
    ) -> str:
        """Search historical records (censuses, vital records, etc.)."""
        params = {
            "given_name": given_name,
            "surname": surname,
            "place": place,
            "birth_date": birth_date,
            "death_date": death_date,
            "collection": collection,
            "count": count,
        }
        return _safely(
            "search_records",
            lambda c: c.search_records(**{k: v for k, v in params.items() if v is not None}),
            params={k: v for k, v in params.items() if v is not None},
        )

    @mcp.tool()
    def fs_place_search(text: str, count: int = 10) -> str:
        """Search the FamilySearch place authority."""
        return _safely(
            "place_search",
            lambda c: c.place_search(text, count=count),
            params={"text": text, "count": count},
        )

    # Expose pool for tests / graceful shutdown.
    mcp._fhra_pool = pool  # type: ignore[attr-defined]
    return mcp


def run() -> None:
    from fhra.logging_config import configure_logging

    configure_logging()
    server = build_server()
    try:
        server.run()
    finally:
        pool = getattr(server, "_fhra_pool", None)
        if pool is not None:
            pool.close()
