"""FamilySearch REST client.

Thin wrapper around httpx that:
  - attaches the bearer token
  - auto-refreshes when it expires
  - prefers ``application/x-gedcomx-v1+json`` (the FS native format)
  - retries with backoff on transient failures (429, 5xx, network errors)
  - honors ``Retry-After`` on 429 responses
  - surfaces errors as :class:`FamilySearchError`

Only read endpoints are implemented in the first pass. Write endpoints come
after Production access is granted and a review workflow is in place.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from fhra import __version__ as _fhra_version
from fhra.auth import TokenSet, refresh_if_needed
from fhra.config import Config

log = logging.getLogger(__name__)

GEDCOMX_JSON = "application/x-gedcomx-v1+json"
FS_ATOM = "application/x-gedcomx-atom+json"

# FSI's Terms require us to be "transparent about your identity"; this header
# identifies our solution to FamilySearch ops so they can correlate and contact.
USER_AGENT = f"fhra/{_fhra_version} (+family-history-research-assistant)"

# Retry policy tunables — overridable for tests.
DEFAULT_MAX_RETRIES = 5
DEFAULT_BASE_DELAY = 1.0      # seconds
DEFAULT_MAX_DELAY = 30.0      # seconds
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


class FamilySearchError(RuntimeError):
    def __init__(self, status: int, body: str, endpoint: str) -> None:
        super().__init__(f"FamilySearch {endpoint} → {status}: {body[:500]}")
        self.status = status
        self.body = body
        self.endpoint = endpoint


@dataclass
class ApiResponse:
    """Rich response wrapper returned by ETag-supporting endpoints.

    ``body`` is the parsed JSON (``{}`` on 304 or 204).
    ``etag`` is the raw ``ETag`` header value (quotes preserved) if present.
    ``status`` is the HTTP status code.

    FamilySearch documents ETags on Persons, Relationships, and Change History
    only. Other endpoints return ``dict[str, Any]`` directly to keep the common
    path simple.
    """

    body: dict[str, Any] = field(default_factory=dict)
    etag: str | None = None
    status: int = 200

    @property
    def not_modified(self) -> bool:
        return self.status == 304


class FamilySearchClient:
    def __init__(
        self,
        config: Config,
        token: TokenSet,
        *,
        transport: httpx.BaseTransport | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        sleep: Any = time.sleep,
    ) -> None:
        self._config = config
        self._token = token
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._sleep = sleep
        self._client = httpx.Client(
            base_url=config.api_base,
            timeout=30.0,
            headers={
                "Accept": GEDCOMX_JSON,
                "User-Agent": USER_AGENT,
            },
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "FamilySearchClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # ---- low-level ---------------------------------------------------------

    def _compute_backoff(self, attempt: int, retry_after: str | None) -> float:
        """Return the number of seconds to sleep before retrying.

        ``attempt`` is 0 for the first retry.
        """
        if retry_after:
            # Retry-After may be seconds or an HTTP date. We only handle seconds.
            try:
                return min(float(retry_after), self._max_delay)
            except ValueError:
                pass
        # Exponential backoff with jitter.
        delay = self._base_delay * (2 ** attempt)
        jitter = random.uniform(0, self._base_delay)
        return min(delay + jitter, self._max_delay)

    def _request_full(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        accept: str = GEDCOMX_JSON,
        json: dict[str, Any] | None = None,
        if_none_match: str | None = None,
    ) -> ApiResponse:
        """Low-level request returning an :class:`ApiResponse` with ETag + status.

        Handles retries on 429/5xx/network errors. Returns ``ApiResponse`` with
        ``status=304`` and empty body when the server signals Not Modified.
        """
        self._token = refresh_if_needed(self._config, self._token)
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._token.access_token}",
            "Accept": accept,
        }
        if if_none_match:
            headers["If-None-Match"] = if_none_match

        last_status: int | None = None
        last_body: str = ""
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._client.request(
                    method, path, params=params, json=json, headers=headers
                )
            except (httpx.TransportError, httpx.TimeoutException) as e:
                if attempt >= self._max_retries:
                    raise FamilySearchError(0, f"network error: {e}", path) from e
                delay = self._compute_backoff(attempt, None)
                log.warning(
                    "FS %s %s network error (attempt %d/%d): %s — retrying in %.1fs",
                    method, path, attempt + 1, self._max_retries + 1, e, delay,
                )
                self._sleep(delay)
                continue

            etag = resp.headers.get("ETag")

            if resp.status_code == 304:
                return ApiResponse(body={}, etag=etag, status=304)

            if resp.is_success:
                if resp.status_code == 204 or not resp.content:
                    return ApiResponse(body={}, etag=etag, status=resp.status_code)
                return ApiResponse(body=resp.json(), etag=etag, status=resp.status_code)

            last_status = resp.status_code
            last_body = resp.text

            if resp.status_code in RETRYABLE_STATUSES and attempt < self._max_retries:
                delay = self._compute_backoff(
                    attempt, resp.headers.get("Retry-After")
                )
                log.warning(
                    "FS %s %s → %d (attempt %d/%d) — retrying in %.1fs",
                    method, path, resp.status_code,
                    attempt + 1, self._max_retries + 1, delay,
                )
                self._sleep(delay)
                continue

            # Non-retryable or retries exhausted.
            raise FamilySearchError(resp.status_code, resp.text, path)

        # Loop exits only via return/raise — the trailing raise satisfies type checkers.
        raise FamilySearchError(
            last_status or 0, last_body or "retries exhausted", path
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        accept: str = GEDCOMX_JSON,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Convenience wrapper for endpoints that don't care about ETags."""
        return self._request_full(
            method, path, params=params, accept=accept, json=json
        ).body

    # ---- read endpoints (first pass) --------------------------------------

    def get_current_user(self) -> dict[str, Any]:
        """``GET /platform/users/current`` — verify auth is working."""
        return self._request("GET", "/platform/users/current")

    def get_person(
        self, fs_person_id: str, *, if_none_match: str | None = None
    ) -> ApiResponse:
        """Fetch a single person by FS PID.

        Supports conditional GET via ``if_none_match``. Returns an
        :class:`ApiResponse`; callers should read ``.body`` for the person
        document and ``.etag`` to cache for the next conditional request.
        If the server returns 304, ``not_modified`` is True and ``body`` is ``{}``.
        """
        return self._request_full(
            "GET",
            f"/platform/tree/persons/{fs_person_id}",
            if_none_match=if_none_match,
        )

    def get_person_with_relationships(
        self, fs_person_id: str, *, if_none_match: str | None = None
    ) -> ApiResponse:
        """Fetch a person plus immediate parents, spouses, and children.

        Supports conditional GET; see :meth:`get_person`.
        """
        return self._request_full(
            "GET",
            "/platform/tree/persons-with-relationships",
            params={"person": fs_person_id},
            if_none_match=if_none_match,
        )

    def get_person_sources(self, fs_person_id: str) -> dict[str, Any]:
        return self._request("GET", f"/platform/tree/persons/{fs_person_id}/sources")

    def get_person_memories(self, fs_person_id: str) -> dict[str, Any]:
        return self._request("GET", f"/platform/tree/persons/{fs_person_id}/memories")

    def get_person_matches(self, fs_person_id: str) -> dict[str, Any]:
        """Potential record matches (Record Hints) for a person."""
        return self._request("GET", f"/platform/tree/persons/{fs_person_id}/matches")

    def get_person_changes(
        self, fs_person_id: str, *, if_none_match: str | None = None
    ) -> ApiResponse:
        """Change history for a person — useful for reviewing edits to the shared tree.

        Supports conditional GET; see :meth:`get_person`.
        """
        return self._request_full(
            "GET",
            f"/platform/tree/persons/{fs_person_id}/changes",
            accept=FS_ATOM,
            if_none_match=if_none_match,
        )

    def get_ancestry(self, fs_person_id: str, generations: int = 4) -> dict[str, Any]:
        """Fetch an ancestral pedigree (self + ancestors)."""
        return self._request(
            "GET",
            "/platform/tree/ancestry",
            params={"person": fs_person_id, "generations": generations},
        )

    def search_persons(
        self,
        *,
        given_name: str | None = None,
        surname: str | None = None,
        birth_place: str | None = None,
        birth_date: str | None = None,
        death_place: str | None = None,
        death_date: str | None = None,
        father_given: str | None = None,
        father_surname: str | None = None,
        mother_given: str | None = None,
        mother_surname: str | None = None,
        spouse_given: str | None = None,
        spouse_surname: str | None = None,
        count: int = 20,
    ) -> dict[str, Any]:
        """Person search in the FamilySearch Family Tree."""
        q = _build_query(
            givenName=given_name,
            surname=surname,
            birthPlace=birth_place,
            birthDate=birth_date,
            deathPlace=death_place,
            deathDate=death_date,
            fatherGivenName=father_given,
            fatherSurname=father_surname,
            motherGivenName=mother_given,
            motherSurname=mother_surname,
            spouseGivenName=spouse_given,
            spouseSurname=spouse_surname,
        )
        if not q:
            raise ValueError("search_persons requires at least one search term")
        return self._request(
            "GET",
            "/platform/tree/search",
            params={"q": q, "count": count},
            accept=FS_ATOM,
        )

    def search_records(
        self,
        *,
        given_name: str | None = None,
        surname: str | None = None,
        place: str | None = None,
        birth_date: str | None = None,
        death_date: str | None = None,
        collection: str | None = None,
        count: int = 20,
    ) -> dict[str, Any]:
        """Historical records search (censuses, vital records, etc.)."""
        q = _build_query(
            required=True,
            givenName=given_name,
            surname=surname,
            anyPlace=place,
            birthLikeDate=birth_date,
            deathLikeDate=death_date,
            collection=collection,
        )
        if not q:
            raise ValueError("search_records requires at least one search term")
        return self._request(
            "GET",
            "/platform/records/search",
            params={"q": q, "count": count},
            accept=FS_ATOM,
        )

    def get_place(self, place_id: str) -> dict[str, Any]:
        return self._request("GET", f"/platform/places/description/{place_id}")

    def place_search(self, text: str, count: int = 10) -> dict[str, Any]:
        return self._request(
            "GET",
            "/platform/places/search",
            params={"q": f'name:"{text}"', "count": count},
            accept=FS_ATOM,
        )


def _build_query(*, required: bool = False, **terms: str | None) -> str:
    """Assemble a FamilySearch q-string from (term → value) kwargs.

    Empty values are dropped. If ``required=True``, each term is prefixed with ``+``
    (records search uses required terms). Exported for unit testing.
    """
    prefix = "+" if required else ""
    parts = [f'{prefix}{name}:"{value}"' for name, value in terms.items() if value]
    return " ".join(parts)
