"""Inyectores de dependencias para los endpoints de la API."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.database import get_db_session


async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesión de base de datos asíncrona por cada petición.

    Yields:
        AsyncSession: Sesión de SQLAlchemy lista para transacciones.
    """
    async for session in get_db_session():
        yield session
