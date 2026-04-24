"""Shared logging setup.

Call :func:`configure_logging` once from CLI / server entry points. Library
modules should just `logging.getLogger(__name__)` — they don't configure.

Respects ``FHRA_LOG_LEVEL`` (e.g. ``DEBUG``, ``INFO``, default ``INFO``).
Logs go to stderr so they don't interfere with stdout JSON output from CLI
commands or MCP stdio transport.
"""

from __future__ import annotations

import logging
import os
import sys


def configure_logging(level: str | None = None) -> None:
    resolved = (level or os.getenv("FHRA_LOG_LEVEL") or "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, resolved, logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
        force=True,
    )
