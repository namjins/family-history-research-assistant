"""Tests for :mod:`fhra.config`."""

from __future__ import annotations

from pathlib import Path

import pytest

from fhra.config import Config, load_config


def _env(monkeypatch: pytest.MonkeyPatch, **kwargs: str) -> None:
    for k, v in kwargs.items():
        monkeypatch.setenv(k, v)


@pytest.mark.parametrize(
    "environment, expected_api, expected_identity",
    [
        ("integration", "https://api-integ.familysearch.org", "https://integration.familysearch.org"),
        ("beta", "https://apibeta.familysearch.org", "https://identbeta.familysearch.org"),
        ("production", "https://api.familysearch.org", "https://ident.familysearch.org"),
    ],
)
def test_env_urls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    environment: str,
    expected_api: str,
    expected_identity: str,
) -> None:
    _env(monkeypatch, FHRA_ENV=environment, FHRA_CLIENT_ID="cid")
    monkeypatch.setenv("FHRA_DB_PATH", str(tmp_path / "fhra.db"))
    monkeypatch.setenv("FHRA_TOKEN_CACHE", str(tmp_path / ".tokens.json"))
    cfg = load_config()
    assert cfg.environment == environment
    assert cfg.api_base == expected_api
    assert cfg.oauth_authorize_url.startswith(expected_identity)
    assert cfg.oauth_token_url.startswith(expected_identity)
    assert cfg.oauth_authorize_url.endswith("/cis-web/oauth2/v3/authorization")
    assert cfg.oauth_token_url.endswith("/cis-web/oauth2/v3/token")


def test_default_environment_is_integration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FHRA_ENV", raising=False)
    monkeypatch.setenv("FHRA_DB_PATH", str(tmp_path / "fhra.db"))
    cfg = load_config()
    assert cfg.environment == "integration"


def test_invalid_environment_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FHRA_ENV", "prod")  # should be 'production'
    with pytest.raises(ValueError, match="FHRA_ENV"):
        load_config()


def test_client_id_default_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FHRA_CLIENT_ID", raising=False)
    monkeypatch.setenv("FHRA_DB_PATH", str(tmp_path / "fhra.db"))
    cfg = load_config()
    assert cfg.client_id is None


def test_db_path_and_token_cache_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom_db = tmp_path / "custom.db"
    custom_tokens = tmp_path / "my-tokens.json"
    monkeypatch.setenv("FHRA_DB_PATH", str(custom_db))
    monkeypatch.setenv("FHRA_TOKEN_CACHE", str(custom_tokens))
    cfg = load_config()
    assert cfg.db_path == custom_db
    assert cfg.token_cache_path == custom_tokens


def test_config_dataclass_is_frozen() -> None:
    cfg = Config(
        client_id=None,
        redirect_uri="http://localhost:5000/cb",
        environment="integration",
        db_path=Path("/tmp/x"),
        token_cache_path=Path("/tmp/t"),
    )
    with pytest.raises(Exception):
        cfg.environment = "beta"  # type: ignore[misc]
