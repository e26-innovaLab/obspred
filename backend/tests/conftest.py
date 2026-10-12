"""Configuración y fixtures compartidas para la suite de pruebas con Pytest."""

from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture que proporciona un cliente HTTP asíncrono para pruebas de integración.

    Yields:
        AsyncClient: Cliente HTTP conectado a la aplicación FastAPI en memoria.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
