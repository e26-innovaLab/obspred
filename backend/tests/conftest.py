"""Configuración y fixtures compartidas para la suite de pruebas con Pytest."""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.dependencies import provide_db_session
from app.infrastructure.persistence.database import Base
from app.main import app


@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Genera una sesión asíncrona de base de datos aislada en memoria SQLite."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def async_client(
    test_db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture que proporciona un cliente HTTP asíncrono para pruebas de integración.

    Args:
        test_db_session: Sesión transaccional en memoria SQLite.

    Yields:
        AsyncClient: Cliente HTTP conectado a la aplicación FastAPI en memoria.
    """

    async def _override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_db_session

    app.dependency_overrides[provide_db_session] = _override_get_db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client
    app.dependency_overrides.pop(provide_db_session, None)
