"""Test fixtures — fresh sqlite DB per test."""

from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Point config to a temporary data dir + sqlite BEFORE importing app.
_TMP = tempfile.mkdtemp(prefix="nexus-console-test-")
os.environ["CONSOLE_DATA_DIR"] = _TMP
os.environ["CONSOLE_DEPLOYMENTS_DIR"] = f"{_TMP}/deployments"
os.environ["CONSOLE_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app  # noqa: E402
from app.db import get_db  # noqa: E402
from app.models.db import Base  # noqa: E402


@pytest.fixture
async def engine():
    e = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield e
    await e.dispose()


@pytest.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def _get_db():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_db] = _get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
