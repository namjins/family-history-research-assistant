"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from fhra.config import Config
from fhra.db.connection import init_db


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """A fresh, schema-loaded SQLite DB in a temp directory."""
    path = tmp_path / "fhra.db"
    init_db(path)
    return path


@pytest.fixture
def config(tmp_path: Path, tmp_db_path: Path) -> Config:
    """A Config pointing at a temp DB + token cache, integration env, stub client id."""
    return Config(
        client_id="test-client-id",
        redirect_uri="http://localhost:5000/auth/familysearch/complete",
        environment="integration",
        db_path=tmp_db_path,
        token_cache_path=tmp_path / "tokens.json",
    )


MINIMAL_GEDCOM = """0 HEAD
1 SOUR RootsMagic
2 VERS 10.0
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @S1@ SOUR
1 TITL 1900 United States Federal Census
1 AUTH National Archives
1 PUBL Washington, DC: NARA, 1900
0 @S2@ SOUR
1 TITL Netherlands Civil Registration
1 AUTH Nationaal Archief
0 @I1@ INDI
1 NAME Hans /Snijman/
1 SEX M
1 _FSFTID L123-ABC
1 BIRT
2 DATE 1 JAN 1900
2 PLAC Amsterdam, Noord-Holland, Netherlands
2 SOUR @S2@
3 PAGE entry 42
3 QUAY 3
1 DEAT
2 DATE 1970
2 PLAC Amsterdam, Netherlands
0 @I2@ INDI
1 NAME Anneke /de Vries/
1 SEX F
1 REFN L456-DEF
2 TYPE FamilySearch
1 BIRT
2 DATE 5 MAR 1902
2 PLAC Rotterdam, Netherlands
0 @I3@ INDI
1 NAME Marc /Snijman/
1 SEX M
1 BIRT
2 DATE 1 JAN 1950
2 PLAC Amsterdam, Netherlands
2 SOUR @S1@
3 PAGE sheet 12, line 34
1 OCCU
2 DATE 1980
2 SOUR Inline free-text source citation
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 MARR
2 DATE 15 JUN 1925
2 PLAC Amsterdam, Netherlands
0 TRLR
"""


@pytest.fixture
def sample_gedcom(tmp_path: Path) -> Path:
    """A small GEDCOM file exercising persons, events, FSIDs, sources, families."""
    path = tmp_path / "sample.ged"
    path.write_text(MINIMAL_GEDCOM, encoding="utf-8")
    return path
