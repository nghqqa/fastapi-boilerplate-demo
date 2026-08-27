"""SEEDED-RISK exposure tests.

test_historical_duplicates_upgrade_fails MUST FAIL (deterministic defect
reproduction) until the migration dedupes historical rows - see
PR_DESCRIPTION.md acceptance criteria.
"""
import os
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

pytestmark = pytest.mark.anyio
BACKEND = Path(__file__).resolve().parents[2]


@pytest.fixture
def sync_url(test_db_url):
    u = test_db_url
    if "postgresql" in u:
        u = u.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    return u


def _prepare(url):
    from src.infrastructure.database.base import Base
    from src.modules import user as _u, api_keys as _k  # noqa: F401 register
    eng = create_engine(url)
    Base.metadata.create_all(eng)
    return eng


def _seed_duplicates(eng):
    from src.modules.user.models import User
    from src.modules.api_keys.models import APIKey
    with Session(eng) as s:
        u = User(email="demo@local", hashed_password="x")
        s.add(u); s.flush()
        s.add_all([
            APIKey(user_id=u.id, name="prod", key_hash="h1"),
            APIKey(user_id=u.id, name="prod", key_hash="h2"),
        ])
        s.commit()
        return u.id


def _run_upgrade(url):
    from alembic import command
    from alembic.config import Config
    os.environ["DATABASE_URL"] = url
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "migrations"))
    command.stamp(cfg, "base")
    command.upgrade(cfg, "head")


def _uqs(eng):
    insp = sa.inspect(eng)
    return [u["name"] for u in insp.get_unique_constraints("api_keys")]


async def test_empty_db_upgrade_succeeds(sync_url):
    eng = _prepare(sync_url)
    _run_upgrade(sync_url)
    assert "uq_api_keys_user_name" in _uqs(eng)


async def test_historical_duplicates_upgrade_fails(sync_url):
    """SEEDED DEFECT reproducer: duplicate (user_id, name) rows are legal
    pre-change; unfixed migration fails deterministically."""
    eng = _prepare(sync_url)
    _seed_duplicates(eng)
    with pytest.raises(Exception, match="[Uu]nique|[Ii]ntegrity"):
        _run_upgrade(sync_url)
