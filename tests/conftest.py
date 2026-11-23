import os

# Set test env BEFORE importing app modules
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_USER", "user")
os.environ.setdefault("POSTGRES_PASSWORD", "password")
os.environ.setdefault("POSTGRES_DB", "hw_final_db")
os.environ.setdefault("REDIS_DB", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.database import Base, engine, get_db
from app.redis_client import redis_client
from app.main import app


@pytest_asyncio.fixture
async def client():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Use real DB sessions (no override) so commits persist
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean tables after test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    if redis_client:
        await redis_client.flushdb()


@pytest_asyncio.fixture
async def auth_client(client):
    """Client helper: registers a user, logs in, returns (client, token, user_data)."""
    return client
