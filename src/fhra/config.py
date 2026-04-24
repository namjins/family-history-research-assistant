"""Runtime configuration — loaded from env vars, overridable in tests."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    client_id: str | None
    redirect_uri: str
    environment: str  # integration | beta | production
    db_path: Path
    token_cache_path: Path

    @property
    def api_base(self) -> str:
        return _ENV_BASES[self.environment]["api"]

    @property
    def oauth_authorize_url(self) -> str:
        return _ENV_BASES[self.environment]["authorize"]

    @property
    def oauth_token_url(self) -> str:
        return _ENV_BASES[self.environment]["token"]


# Identity host serves OAuth; platform host serves the REST API.
# Verified by direct probe 2026-04-24: `apibeta.familysearch.org/platform/users/current`
# returns 401 (real API); `beta.familysearch.org/platform/users/current` returns 403.
# The fs-js-lite JS SDK uses `beta.familysearch.org` for the platform host but that is
# stale — the authoritative value is `apibeta.familysearch.org`, consistent with the older
# developer docs at www.familysearch.org/developers/docs/.
_ENV_BASES: dict[str, dict[str, str]] = {
    "integration": {
        "api": "https://api-integ.familysearch.org",
        "authorize": "https://integration.familysearch.org/cis-web/oauth2/v3/authorization",
        "token": "https://integration.familysearch.org/cis-web/oauth2/v3/token",
    },
    "beta": {
        "api": "https://apibeta.familysearch.org",
        "authorize": "https://identbeta.familysearch.org/cis-web/oauth2/v3/authorization",
        "token": "https://identbeta.familysearch.org/cis-web/oauth2/v3/token",
    },
    "production": {
        "api": "https://api.familysearch.org",
        "authorize": "https://ident.familysearch.org/cis-web/oauth2/v3/authorization",
        "token": "https://ident.familysearch.org/cis-web/oauth2/v3/token",
    },
}


def load_config() -> Config:
    load_dotenv()
    environment = os.getenv("FHRA_ENV", "integration").strip().lower()
    if environment not in _ENV_BASES:
        raise ValueError(
            f"FHRA_ENV must be one of {list(_ENV_BASES)}; got {environment!r}"
        )

    db_path = Path(os.getenv("FHRA_DB_PATH") or REPO_ROOT / "data" / "fhra.db")
    token_cache_path = Path(
        os.getenv("FHRA_TOKEN_CACHE") or REPO_ROOT / "data" / ".tokens.json"
    )

    return Config(
        client_id=os.getenv("FHRA_CLIENT_ID"),
        redirect_uri=os.getenv(
            "FHRA_REDIRECT_URI", "http://localhost:5000/auth/familysearch/complete"
        ),
        environment=environment,
        db_path=db_path,
        token_cache_path=token_cache_path,
    )
