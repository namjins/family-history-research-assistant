"""``fhra`` CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from fhra.auth import load_token, login_interactive, refresh_if_needed, save_token
from fhra.config import load_config
from fhra.db.connection import init_db

app = typer.Typer(help="Family History Research Assistant CLI")
db_app = typer.Typer(help="Local working-copy database")
auth_app = typer.Typer(help="FamilySearch authentication")
gedcom_app = typer.Typer(help="GEDCOM import/export")
app.add_typer(db_app, name="db")
app.add_typer(auth_app, name="auth")
app.add_typer(gedcom_app, name="gedcom")


@db_app.command("init")
def db_init() -> None:
    """Create/migrate the local SQLite database."""
    cfg = load_config()
    init_db(cfg.db_path)
    typer.echo(f"Initialized DB at {cfg.db_path}")


@gedcom_app.command("import")
def gedcom_import(gedcom_path: Path) -> None:
    """Import a GEDCOM file into the local working copy."""
    from fhra.gedcom import import_gedcom

    cfg = load_config()
    init_db(cfg.db_path)
    stats = import_gedcom(cfg.db_path, gedcom_path)
    typer.echo(json.dumps(stats.as_dict(), indent=2))


@auth_app.command("login")
def auth_login() -> None:
    """Interactive OAuth2 login against FamilySearch."""
    cfg = load_config()
    token = login_interactive(cfg)
    save_token(cfg.token_cache_path, token)
    typer.echo(f"Logged in. Token cached at {cfg.token_cache_path}")


@auth_app.command("whoami")
def auth_whoami() -> None:
    """Verify cached token by calling /platform/users/current."""
    from fhra.api import FamilySearchClient

    cfg = load_config()
    token = load_token(cfg.token_cache_path)
    if token is None:
        typer.secho("No cached token — run `fhra auth login`.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    token = refresh_if_needed(cfg, token)
    with FamilySearchClient(cfg, token) as client:
        typer.echo(json.dumps(client.get_current_user(), indent=2))


@auth_app.command("status")
def auth_status() -> None:
    """Show local token status without calling FamilySearch."""
    cfg = load_config()
    token = load_token(cfg.token_cache_path)
    if token is None:
        typer.echo("No cached token.")
        raise typer.Exit(code=1)
    typer.echo(
        json.dumps(
            {
                "environment": token.environment,
                "expires_at": token.expires_at,
                "expired": token.is_expired(),
                "scope": token.scope,
                "has_refresh_token": bool(token.refresh_token),
            },
            indent=2,
        )
    )


@app.command("serve")
def serve() -> None:
    """Run the MCP server (stdio transport)."""
    from fhra.mcp_server import run

    run()


if __name__ == "__main__":
    app()
