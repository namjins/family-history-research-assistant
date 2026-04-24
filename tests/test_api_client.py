"""Tests for :mod:`fhra.api.client` — retry logic, query building, auth headers."""

from __future__ import annotations

import time
from pathlib import Path

import httpx
import pytest

from fhra.api import FamilySearchClient, FamilySearchError, _build_query
from fhra.auth import TokenSet
from fhra.config import Config


def _cfg(tmp_path: Path) -> Config:
    return Config(
        client_id="test-cid",
        redirect_uri="http://localhost:5000/cb",
        environment="integration",
        db_path=tmp_path / "db.sqlite",
        token_cache_path=tmp_path / "tokens.json",
    )


def _live_token() -> TokenSet:
    return TokenSet(
        access_token="at-1",
        token_type="Bearer",
        expires_at=time.time() + 3600,
        refresh_token="rt-1",
    )


# ---- Query builder -----------------------------------------------------------


def test_build_query_drops_empty_values() -> None:
    q = _build_query(givenName="Hans", surname=None, birthPlace="Amsterdam")
    # dict iteration order is insertion order in Python 3.7+
    assert q == 'givenName:"Hans" birthPlace:"Amsterdam"'


def test_build_query_required_prefix() -> None:
    q = _build_query(required=True, givenName="Hans", surname="Snijman")
    assert q == '+givenName:"Hans" +surname:"Snijman"'


def test_build_query_empty_when_all_none() -> None:
    assert _build_query() == ""


# ---- search validation -------------------------------------------------------


def test_search_persons_requires_some_term(tmp_path: Path) -> None:
    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})),
    )
    try:
        with pytest.raises(ValueError, match="at least one"):
            client.search_persons()
    finally:
        client.close()


# ---- Auth header / endpoint routing ------------------------------------------


def test_bearer_header_and_accept_set(tmp_path: Path) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("Authorization")
        captured["accept"] = request.headers.get("Accept")
        captured["user_agent"] = request.headers.get("User-Agent")
        captured["path"] = request.url.path
        return httpx.Response(200, json={"users": [{"id": "u1"}]})

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        client.get_current_user()
    finally:
        client.close()
    assert captured["auth"] == "Bearer at-1"
    assert captured["accept"] == "application/x-gedcomx-v1+json"
    assert captured["path"] == "/platform/users/current"
    # Compliance: FSI requires we be "transparent about your identity" — keep User-Agent set.
    assert captured["user_agent"] is not None
    assert captured["user_agent"].startswith("fhra/")


def test_get_person_with_relationships_uses_query_param(tmp_path: Path) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        return httpx.Response(200, json={})

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        client.get_person_with_relationships("L123-ABC")
    finally:
        client.close()
    assert captured["path"] == "/platform/tree/persons-with-relationships"
    assert captured["params"]["person"] == "L123-ABC"


# ---- Retry logic -------------------------------------------------------------


def test_retries_on_429_with_retry_after(tmp_path: Path) -> None:
    attempts: list[int] = [0]
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts[0] += 1
        if attempts[0] < 3:
            return httpx.Response(429, headers={"Retry-After": "2"}, text="slow down")
        return httpx.Response(200, json={"ok": True})

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda s: sleeps.append(s),
        max_retries=5,
        base_delay=0.1,
    )
    try:
        data = client.get_current_user()
    finally:
        client.close()
    assert data == {"ok": True}
    assert attempts[0] == 3
    # Retry-After=2 honored on both retries
    assert sleeps == [2.0, 2.0]


def test_retries_on_5xx(tmp_path: Path) -> None:
    attempts: list[int] = [0]
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts[0] += 1
        if attempts[0] == 1:
            return httpx.Response(503, text="unavailable")
        if attempts[0] == 2:
            return httpx.Response(502, text="bad gateway")
        return httpx.Response(200, json={"ok": True})

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda s: sleeps.append(s),
        max_retries=5,
        base_delay=0.1,
        max_delay=5.0,
    )
    try:
        data = client.get_current_user()
    finally:
        client.close()
    assert data == {"ok": True}
    assert attempts[0] == 3
    assert len(sleeps) == 2
    # Exponential backoff: attempt 0 base=0.1..0.2, attempt 1 base=0.2..0.3 (jitter)
    assert 0.1 <= sleeps[0] <= 0.3
    assert 0.2 <= sleeps[1] <= 0.4


def test_no_retry_on_4xx_other_than_429(tmp_path: Path) -> None:
    attempts: list[int] = [0]

    def handler(request: httpx.Request) -> httpx.Response:
        attempts[0] += 1
        return httpx.Response(404, text="not found")

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda _s: None,
    )
    try:
        with pytest.raises(FamilySearchError) as excinfo:
            client.get_person("NOPE")
    finally:
        client.close()
    assert excinfo.value.status == 404
    assert attempts[0] == 1, "404 must not retry"


def test_retries_exhausted_raises(tmp_path: Path) -> None:
    attempts: list[int] = [0]

    def handler(request: httpx.Request) -> httpx.Response:
        attempts[0] += 1
        return httpx.Response(503, text="down")

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda _s: None,
        max_retries=2,
        base_delay=0.0,
    )
    try:
        with pytest.raises(FamilySearchError) as excinfo:
            client.get_current_user()
    finally:
        client.close()
    assert excinfo.value.status == 503
    assert attempts[0] == 3, "initial attempt + 2 retries"


def test_retries_on_transient_network_error(tmp_path: Path) -> None:
    attempts: list[int] = [0]

    def handler(request: httpx.Request) -> httpx.Response:
        attempts[0] += 1
        if attempts[0] == 1:
            raise httpx.ConnectError("connection reset")
        return httpx.Response(200, json={"ok": True})

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda _s: None,
        max_retries=3,
        base_delay=0.0,
    )
    try:
        data = client.get_current_user()
    finally:
        client.close()
    assert data == {"ok": True}
    assert attempts[0] == 2


def test_network_error_retries_exhausted(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout")

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda _s: None,
        max_retries=1,
        base_delay=0.0,
    )
    try:
        with pytest.raises(FamilySearchError, match="network error"):
            client.get_current_user()
    finally:
        client.close()


def test_malformed_retry_after_falls_back_to_backoff(tmp_path: Path) -> None:
    """An HTTP-date Retry-After must not crash; fall back to exponential backoff."""
    attempts: list[int] = [0]
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts[0] += 1
        if attempts[0] == 1:
            return httpx.Response(
                429, headers={"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}, text=""
            )
        return httpx.Response(200, json={})

    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(handler),
        sleep=lambda s: sleeps.append(s),
        max_retries=2,
        base_delay=0.1,
    )
    try:
        client.get_current_user()
    finally:
        client.close()
    assert attempts[0] == 2
    assert len(sleeps) == 1
    # We fell back to computed backoff (0.1 base + jitter), not 0
    assert 0.1 <= sleeps[0] <= 0.3


# ---- Empty / no-content responses --------------------------------------------


def test_204_returns_empty_dict(tmp_path: Path) -> None:
    client = FamilySearchClient(
        _cfg(tmp_path),
        _live_token(),
        transport=httpx.MockTransport(lambda r: httpx.Response(204)),
    )
    try:
        assert client.get_current_user() == {}
    finally:
        client.close()


# ---- ETag support on get_person / get_person_with_relationships / get_person_changes


def test_get_person_returns_api_response_with_etag(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"persons": [{"id": "L123-ABC"}]},
            headers={"ETag": '"abc123"'},
        )

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        resp = client.get_person("L123-ABC")
    finally:
        client.close()
    assert resp.status == 200
    assert resp.etag == '"abc123"'
    assert not resp.not_modified
    assert resp.body["persons"][0]["id"] == "L123-ABC"


def test_get_person_sends_if_none_match_and_handles_304(tmp_path: Path) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["if_none_match"] = request.headers.get("If-None-Match")
        return httpx.Response(304, headers={"ETag": '"abc123"'})

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        resp = client.get_person("L123-ABC", if_none_match='"abc123"')
    finally:
        client.close()
    assert captured["if_none_match"] == '"abc123"'
    assert resp.status == 304
    assert resp.not_modified
    assert resp.body == {}
    assert resp.etag == '"abc123"'


def test_get_person_with_relationships_supports_conditional_get(
    tmp_path: Path,
) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["if_none_match"] = request.headers.get("If-None-Match")
        return httpx.Response(304, headers={"ETag": '"xyz"'})

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        resp = client.get_person_with_relationships(
            "L123-ABC", if_none_match='"xyz"'
        )
    finally:
        client.close()
    assert captured["if_none_match"] == '"xyz"'
    assert resp.not_modified


def test_get_person_changes_supports_conditional_get(tmp_path: Path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        # Also verify the Atom accept header is used.
        assert request.headers.get("Accept") == "application/x-gedcomx-atom+json"
        return httpx.Response(200, json={"entries": []}, headers={"ETag": '"ch-1"'})

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        resp = client.get_person_changes("L123-ABC")
    finally:
        client.close()
    assert resp.etag == '"ch-1"'
    assert resp.body["entries"] == []


def test_no_if_none_match_header_when_etag_not_provided(tmp_path: Path) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["if_none_match"] = request.headers.get("If-None-Match")
        return httpx.Response(200, json={"persons": []})

    client = FamilySearchClient(
        _cfg(tmp_path), _live_token(), transport=httpx.MockTransport(handler)
    )
    try:
        client.get_person("L123-ABC")
    finally:
        client.close()
    assert captured["if_none_match"] is None, (
        "If-None-Match must not be sent unless the caller provided an ETag"
    )
