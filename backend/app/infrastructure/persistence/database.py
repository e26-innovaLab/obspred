"""Configuración del motor de base de datos y fábrica de sesiones asíncronas."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Motor asíncrono configurado a partir de variables de entorno
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
)

# Fábrica de sesiones asíncronas
async_session_factory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Clase base declarativa para futuros modelos ORM
Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador asíncrono para inyectar sesiones de base de datos.

    Yields:
        AsyncSession: Sesión transaccional activa vinculada al ciclo de vida del request.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
