"""MCP server exposing local-DB + FamilySearch tools to Claude."""

from fhra.mcp_server.server import build_server, run

__all__ = ["build_server", "run"]
