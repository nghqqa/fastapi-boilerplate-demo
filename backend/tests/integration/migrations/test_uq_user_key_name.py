"""SEeded-RISK exposure tests (deterministic).

Base (pre-PR) schema is created by the BASELINE tree's models via a
pre-baked helper script (base_schema_helper.py), so the constraint under
test can only come from migration demo0001 itself.
Alembic also runs as subprocess — no in-process settings leakage.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.asyncio
HERE = Path(__file__).resolve().parent
BACKEND = HERE.parents[2]  # backend/
BASELINE_TREE = os.environ.get("P14_BASELINE_TREE", "")
HELPER = HERE / "base_schema_helper.py"

needs_baseline = pytest.mark.skipif(
    not BASELINE_TREE, reason="P14_BASELINE_TREE must point at the pre-PR tree")


def _make_base(url):
    r = subprocess.run(
        [sys.executable, str(HELPER), BASELINE_TREE],
        env=dict(os.environ, H_URL=url), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-400:]


async def _seed_dupes(url):
    eng = create_async_engine(url)
    from sqlalchemy import text
    async with eng.begin() as c:
        r = await c.execute(text(
            "INSERT INTO \"user\" (email, hashed_password, is_superuser, email_verified) "
            "VALUES ('demo@local','x',false,false) RETURNING id"))
        uid = r.scalar()
        await c.execute(text(
            "INSERT INTO api_keys (user_id, name, key_hash) "
            "VALUES (:u,'prod','h1'),(:u,'prod','h2')"), {"u": uid})
    await eng.dispose()


def _alembic(url, *args):
    return subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(BACKEND / "alembic.ini"), *args],
        cwd=str(BACKEND), env=dict(os.environ, DATABASE_URL=url),
        capture_output=True, text=True)


async def _uqs(url):
    eng = create_async_engine(url)
    def chk(c):
        return [u["name"] for u in sa.inspect(c).get_unique_constraints("api_keys")]
    async with eng.connect() as c:
        out = await c.run_sync(chk)
    await eng.dispose()
    return out


@needs_baseline
async def test_empty_db_upgrade_succeeds(test_db_url):
    _make_base(test_db_url)
    assert _alembic(test_db_url, "stamp", "base").returncode == 0
    up = _alembic(test_db_url, "upgrade", "head")
    assert up.returncode == 0, (up.stdout + up.stderr)[-400:]
    assert "uq_api_keys_user_name" in await _uqs(test_db_url)


@needs_baseline
async def test_historical_duplicates_upgrade_fails(test_db_url):
    """SEEDED DEFECT reproducer: duplicate (user_id,name) rows legal
    pre-change; unfixed migration demo0001 fails deterministically."""
    _make_base(test_db_url)
    await _seed_dupes(test_db_url)
    assert _alembic(test_db_url, "stamp", "base").returncode == 0
    up = _alembic(test_db_url, "upgrade", "head")
    assert up.returncode != 0
    err = up.stdout + up.stderr
    assert ("23505" in err) or ("unique" in err.lower()) or ("duplicate" in err.lower()), err[-500:]
    assert "uq_api_keys_user_name" not in await _uqs(test_db_url)
