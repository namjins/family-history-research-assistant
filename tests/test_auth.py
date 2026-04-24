"""Tests for :mod:`fhra.auth.oauth`."""

from __future__ import annotations

import base64
import hashlib
import json
import time
from pathlib import Path

import httpx
import pytest

from fhra.auth import (
    AuthError,
    TokenSet,
    load_token,
    pkce_pair,
    refresh_if_needed,
    save_token,
    token_from_payload,
)
from fhra.auth.oauth import _CallbackCatcher
from fhra.config import Config


# ---- PKCE --------------------------------------------------------------------


def test_pkce_verifier_minimum_length() -> None:
    for _ in range(10):
        verifier, challenge = pkce_pair()
        assert len(verifier) >= 43, "RFC 7636 requires verifier length 43..128"
        assert len(verifier) <= 128


def test_pkce_challenge_matches_sha256_of_verifier() -> None:
    verifier, challenge = pkce_pair()
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    assert challenge == expected


def test_pkce_pair_is_random() -> None:
    pairs = {pkce_pair()[0] for _ in range(5)}
    assert len(pairs) == 5, "pkce verifiers must not collide"


# ---- TokenSet ----------------------------------------------------------------


def test_token_from_payload_parses_all_fields() -> None:
    payload = {
        "access_token": "at-1",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "rt-1",
        "scope": "openid profile",
    }
    t = token_from_payload(payload, environment="integration")
    assert t.access_token == "at-1"
    assert t.token_type == "Bearer"
    assert t.refresh_token == "rt-1"
    assert t.scope == "openid profile"
    assert t.environment == "integration"
    assert t.expires_at > time.time()


def test_token_from_payload_defaults_when_missing() -> None:
    t = token_from_payload({"access_token": "at-1"}, environment="beta")
    assert t.token_type == "Bearer"
    assert t.refresh_token is None
    assert t.scope is None
    # default expires_in is 3600
    assert t.expires_at > time.time() + 3500


def test_token_is_expired_respects_leeway() -> None:
    t = TokenSet(
        access_token="x",
        token_type="Bearer",
        expires_at=time.time() + 10,  # expires in 10s
    )
    # Default leeway is 30s → already considered expired
    assert t.is_expired()
    # With small leeway, still valid
    assert not t.is_expired(leeway_seconds=0)


def test_token_is_expired_future_token() -> None:
    t = TokenSet(access_token="x", token_type="Bearer", expires_at=time.time() + 7200)
    assert not t.is_expired()


# ---- save_token / load_token --------------------------------------------------


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    t = TokenSet(
        access_token="at",
        token_type="Bearer",
        expires_at=time.time() + 1000,
        refresh_token="rt",
        scope="openid",
        environment="integration",
    )
    save_token(path, t)
    loaded = load_token(path)
    assert loaded is not None
    assert loaded.access_token == "at"
    assert loaded.refresh_token == "rt"
    assert loaded.environment == "integration"


def test_save_token_restrictive_perms(tmp_path: Path) -> None:
    path = tmp_path / "tokens.json"
    t = TokenSet(access_token="at", token_type="Bearer", expires_at=time.time() + 1000)
    save_token(path, t)
    mode = path.stat().st_mode & 0o777
    assert mode == 0o600


def test_load_token_missing_returns_none(tmp_path: Path) -> None:
    assert load_token(tmp_path / "nope.json") is None


# ---- refresh_if_needed --------------------------------------------------------


def _cfg(tmp_path: Path, *, client_id: str | None = "cid") -> Config:
    return Config(
        client_id=client_id,
        redirect_uri="http://localhost:5000/cb",
        environment="integration",
        db_path=tmp_path / "db.sqlite",
        token_cache_path=tmp_path / "tokens.json",
    )


def test_refresh_noop_when_not_expired(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    t = TokenSet(
        access_token="at",
        token_type="Bearer",
        expires_at=time.time() + 3600,
        refresh_token="rt",
    )
    out = refresh_if_needed(cfg, t)
    assert out is t, "unchanged token should be the same object"


def test_refresh_raises_when_expired_and_no_refresh_token(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    t = TokenSet(access_token="at", token_type="Bearer", expires_at=time.time() - 1)
    with pytest.raises(AuthError, match="re-run login"):
        refresh_if_needed(cfg, t)


def test_refresh_raises_when_client_id_missing(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, client_id=None)
    t = TokenSet(
        access_token="at",
        token_type="Bearer",
        expires_at=time.time() - 1,
        refresh_token="rt",
    )
    with pytest.raises(AuthError, match="FHRA_CLIENT_ID"):
        refresh_if_needed(cfg, t)


def test_refresh_success_persists_new_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _cfg(tmp_path)
    old = TokenSet(
        access_token="old",
        token_type="Bearer",
        expires_at=time.time() - 1,
        refresh_token="old-rt",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/cis-web/oauth2/v3/token")
        data = dict(x.split("=") for x in request.content.decode().split("&"))
        assert data["grant_type"] == "refresh_token"
        assert data["refresh_token"] == "old-rt"
        return httpx.Response(
            200,
            json={
                "access_token": "new",
                "token_type": "Bearer",
                "expires_in": 3600,
                # omit refresh_token to verify carry-over
            },
        )

    transport = httpx.MockTransport(handler)
    # Patch httpx.Client to inject our transport.
    real_client = httpx.Client

    def client_with_transport(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr("fhra.auth.oauth.httpx.Client", client_with_transport)

    refreshed = refresh_if_needed(cfg, old)
    assert refreshed.access_token == "new"
    assert refreshed.refresh_token == "old-rt", "refresh_token carried over when server omits it"
    # Token was persisted to disk
    loaded = load_token(cfg.token_cache_path)
    assert loaded is not None
    assert loaded.access_token == "new"


def test_refresh_surfaces_http_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _cfg(tmp_path)
    t = TokenSet(
        access_token="at",
        token_type="Bearer",
        expires_at=time.time() - 1,
        refresh_token="rt",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="invalid_grant")

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client

    def client_with_transport(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)

    monkeypatch.setattr("fhra.auth.oauth.httpx.Client", client_with_transport)
    with pytest.raises(AuthError, match="Token refresh failed"):
        refresh_if_needed(cfg, t)


# ---- Callback catcher state isolation ----------------------------------------


def test_callback_catcher_has_instance_state() -> None:
    """Regression: _CallbackCatcher.result must be per-instance, not class-level."""
    c1 = _CallbackCatcher("localhost", 5000)
    c2 = _CallbackCatcher("localhost", 5000)
    # Poke the private field to simulate a prior completed flow on c1.
    c1._result = {"code": "stale", "state": "s1"}  # type: ignore[attr-defined]
    assert c2._result is None, "new catcher must not see stale result from prior instance"  # type: ignore[attr-defined]


# ---- offline_access scope ----------------------------------------------------


def test_default_scopes_include_offline_access() -> None:
    """Regression: native apps need offline_access to get refresh tokens."""
    from fhra.auth.oauth import DEFAULT_SCOPES

    assert "offline_access" in DEFAULT_SCOPES


def test_login_authorize_url_includes_offline_access_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End-to-end: the actual authorize URL sent to the browser must request offline_access."""
    from fhra.auth import login_interactive
    from fhra.auth.oauth import AuthError

    cfg = _cfg(tmp_path)
    captured_urls: list[str] = []

    def fake_open(url: str) -> bool:
        captured_urls.append(url)
        return True

    monkeypatch.setattr("fhra.auth.oauth.webbrowser.open", fake_open)

    # Short-circuit the callback wait so we don't spin up an HTTP server.
    def fake_wait(self, timeout_seconds: int):
        raise AuthError("stop — test captured the auth URL already")

    monkeypatch.setattr(
        "fhra.auth.oauth._CallbackCatcher.wait_for_redirect", fake_wait
    )

    with pytest.raises(AuthError):
        login_interactive(cfg)

    assert len(captured_urls) == 1
    url = captured_urls[0]
    # urlencode quotes the scope; look for either form.
    assert "scope=offline_access" in url or "scope=offline%5Faccess" in url
    assert "code_challenge_method=S256" in url
    assert "response_type=code" in url
