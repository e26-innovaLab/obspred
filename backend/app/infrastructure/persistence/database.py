"""Configuración del motor de base de datos y fábrica de sesiones asíncronas.

Soporta conexiones nativas a PostgreSQL (mediante asyncpg) y fallback local
en SQLite con pooling optimizado y verificación de liveness (pool_pre_ping).
"""

from typing import Any, AsyncGenerator, Dict
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Argumentos base del motor
engine_options: Dict[str, Any] = {
    "echo": settings.database_echo,
    "future": True,
}

# Configuración de pool de conexiones para PostgreSQL (u otros motores cliente-servidor)
if not settings.database_url.startswith("sqlite"):
    engine_options.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
        }
    )

# Motor asíncrono preparado para PostgreSQL (asyncpg) o SQLite (aiosqlite)
engine = create_async_engine(
    settings.database_url,
    **engine_options,
)

# Fábrica de sesiones asíncronas
async_session_factory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Clase base declarativa para los modelos ORM
Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador asíncrono para inyectar sesiones de base de datos en peticiones HTTP.

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
