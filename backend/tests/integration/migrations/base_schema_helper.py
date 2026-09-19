import asyncio, os, sys
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

# Baseline (fdde4f4) api_keys schema: NO uq_api_keys_user_name constraint
DDL = [
    sa.text("DROP TABLE IF EXISTS api_keys CASCADE"),
    sa.text("DROP TABLE IF EXISTS \"user\" CASCADE"),
    sa.text("CREATE TABLE IF NOT EXISTS \"user\" (id SERIAL PRIMARY KEY, email VARCHAR(50) UNIQUE NOT NULL, hashed_password VARCHAR(100) NOT NULL, is_superuser BOOLEAN DEFAULT FALSE NOT NULL, email_verified BOOLEAN DEFAULT FALSE NOT NULL, created_at TIMESTAMP DEFAULT now(), updated_at TIMESTAMP DEFAULT now(), is_deleted BOOLEAN DEFAULT FALSE)"),
    sa.text("CREATE TABLE IF NOT EXISTS api_keys (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES \"user\"(id), name VARCHAR(100) NOT NULL, key_hash VARCHAR(255) UNIQUE NOT NULL, is_active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT now(), updated_at TIMESTAMP DEFAULT now())"),
]

async def m():
    e = create_async_engine(os.environ["H_URL"])
    async with e.begin() as c:
        for ddl in DDL:
            await c.execute(ddl)
    await e.dispose()

asyncio.run(m())
