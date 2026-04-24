"""OAuth2 Authorization Code Flow against FamilySearch.

FamilySearch Desktop apps use the standard authorization code flow with PKCE.
We spin up a short-lived localhost HTTP server to catch the redirect, exchange
the code for tokens, and cache the result on disk. No client secret is required
for Desktop apps.
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import logging
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx

from fhra.config import Config

log = logging.getLogger(__name__)

# Requesting `offline_access` is what gets FamilySearch to issue a refresh token
# to a PKCE native-app flow. Without it, refresh tokens are only issued when the
# user ticks "private computer" on the consent page, which we can't rely on.
# Source: developers.familysearch.org/main/docs/authentication
DEFAULT_SCOPES = "offline_access"


class AuthError(RuntimeError):
    pass


@dataclass
class TokenSet:
    access_token: str
    token_type: str
    expires_at: float               # epoch seconds
    refresh_token: str | None = None
    scope: str | None = None
    environment: str = "integration"

    def is_expired(self, leeway_seconds: int = 30) -> bool:
        return time.time() + leeway_seconds >= self.expires_at


def save_token(path: Path, token: TokenSet) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(token), indent=2))
    # Best-effort restrictive perms; not a substitute for keychain storage.
    try:
        path.chmod(0o600)
    except OSError:
        pass


def load_token(path: Path) -> TokenSet | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return TokenSet(**data)


def pkce_pair() -> tuple[str, str]:
    """Generate a PKCE (verifier, challenge) pair. Verifier is 43+ chars."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


class _CallbackCatcher:
    """Captures the first OAuth redirect on a short-lived HTTP server.

    Each instance holds its own result; using a fresh instance per login avoids
    the stale-state bug of class-level globals on a retry.
    """

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._result: dict[str, str] | None = None
        self._lock = threading.Lock()
        # Build a handler class bound to this instance.
        catcher = self

        class _Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urllib.parse.urlparse(self.path)
                params = dict(urllib.parse.parse_qsl(parsed.query))
                with catcher._lock:
                    if catcher._result is None:
                        catcher._result = params
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                body = (
                    "<html><body><h2>FamilySearch login complete.</h2>"
                    "<p>You can close this tab.</p></body></html>"
                )
                self.wfile.write(body.encode())

            def log_message(self, *_args: Any) -> None:  # silence default logging
                return

        self._handler_cls = _Handler

    def wait_for_redirect(self, timeout_seconds: int) -> dict[str, str]:
        server = http.server.HTTPServer((self._host, self._port), self._handler_cls)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            deadline = time.time() + timeout_seconds
            while time.time() < deadline:
                with self._lock:
                    if self._result is not None:
                        return self._result
                time.sleep(0.2)
            raise AuthError("Timed out waiting for FamilySearch auth redirect.")
        finally:
            server.shutdown()


def _open_browser_with_fallback(url: str) -> None:
    opened = False
    try:
        opened = webbrowser.open(url)
    except webbrowser.Error as e:
        log.warning("webbrowser.open failed: %s", e)
    if not opened:
        msg = (
            "Could not automatically open a browser. Open this URL manually:\n"
            f"  {url}\n"
        )
        print(msg, file=sys.stderr)


def login_interactive(config: Config) -> TokenSet:
    """Run the browser-based auth code flow and return a fresh token."""
    if not config.client_id:
        raise AuthError(
            "FHRA_CLIENT_ID is not set. Get a Desktop app key from the "
            "FamilySearch Solution Provider portal and set it in .env."
        )

    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(16)

    parsed = urllib.parse.urlparse(config.redirect_uri)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5000

    authorize_params = {
        "client_id": config.client_id,
        "response_type": "code",
        "redirect_uri": config.redirect_uri,
        "state": state,
        "scope": DEFAULT_SCOPES,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{config.oauth_authorize_url}?{urllib.parse.urlencode(authorize_params)}"

    catcher = _CallbackCatcher(host, port)
    _open_browser_with_fallback(auth_url)
    result = catcher.wait_for_redirect(timeout_seconds=300)

    if result.get("state") != state:
        raise AuthError("OAuth state mismatch — possible CSRF. Aborting.")
    if "error" in result:
        raise AuthError(
            f"Authorization error: {result['error']} {result.get('error_description','')}"
        )
    code = result.get("code")
    if not code:
        raise AuthError(f"No code in redirect: {result!r}")

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            config.oauth_token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config.redirect_uri,
                "client_id": config.client_id,
                "code_verifier": verifier,
            },
            headers={"Accept": "application/json"},
        )
    if resp.status_code != 200:
        raise AuthError(f"Token exchange failed ({resp.status_code}): {resp.text}")
    return token_from_payload(resp.json(), config.environment)


def refresh_if_needed(config: Config, token: TokenSet) -> TokenSet:
    """Refresh the token if close to expiry. Returns the (possibly new) token."""
    if not token.is_expired():
        return token
    if not token.refresh_token:
        raise AuthError(
            "Access token expired and no refresh token available — re-run login."
        )
    if not config.client_id:
        raise AuthError("FHRA_CLIENT_ID is not set.")

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            config.oauth_token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": token.refresh_token,
                "client_id": config.client_id,
            },
            headers={"Accept": "application/json"},
        )
    if resp.status_code != 200:
        raise AuthError(f"Token refresh failed ({resp.status_code}): {resp.text}")
    new_token = token_from_payload(resp.json(), config.environment)
    # Some OAuth servers don't re-issue refresh tokens; carry over ours.
    if not new_token.refresh_token:
        new_token.refresh_token = token.refresh_token
    save_token(config.token_cache_path, new_token)
    return new_token


def token_from_payload(payload: dict[str, Any], environment: str) -> TokenSet:
    expires_in = int(payload.get("expires_in", 3600))
    return TokenSet(
        access_token=payload["access_token"],
        token_type=payload.get("token_type", "Bearer"),
        expires_at=time.time() + expires_in,
        refresh_token=payload.get("refresh_token"),
        scope=payload.get("scope"),
        environment=environment,
    )
