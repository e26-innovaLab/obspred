"""Pruebas unitarias para BrechaService."""

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.application.dtos.brecha_dto import HabilidadComparadaCreateDTO
from app.application.services.brecha_service import BrechaService
from app.domain.exceptions.brecha_exceptions import OcupacionNoEncontradaError
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.repositories.brecha_repository import (
    SQLAlchemyBrechaRepository,
)


@pytest.fixture
async def in_memory_session() -> AsyncSession:
    """Provee una sesión SQLite en memoria con esquema creado para pruebas."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    await test_engine.dispose()


@pytest.mark.asyncio
async def test_brecha_service_auto_seeds_canonical_occupation(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica que si la DB está vacía, se auto-persisten las ocupaciones
    del catálogo.
    """
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)
    service = BrechaService(repository=repo)

    dtos = await service.get_by_ocupation("desarrollador_software")
    assert len(dtos) > 0
    assert any(d.habilidad == "Cloud computing" for d in dtos)
    assert all(hasattr(d, "brecha") for d in dtos)

    # Verificamos que realmente se persistieron en el repositorio
    in_db = await repo.get_by_ocupation("desarrollador_software")
    assert len(in_db) == len(dtos)


@pytest.mark.asyncio
async def test_brecha_service_unknown_occupation_raises(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica que una ocupación inexistente lance OcupacionNoEncontradaError."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)
    service = BrechaService(repository=repo)

    with pytest.raises(OcupacionNoEncontradaError):
        await service.get_by_ocupation("astronauta_marte")


@pytest.mark.asyncio
async def test_brecha_service_empty_occupation_raises(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica que una ocupación vacía lance OcupacionNoEncontradaError."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)
    service = BrechaService(repository=repo)

    with pytest.raises(OcupacionNoEncontradaError):
        await service.get_by_ocupation("   ")


@pytest.mark.asyncio
async def test_brecha_service_save_custom_habilidades(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica la persistencia explícita de habilidades para una ocupación."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)
    service = BrechaService(repository=repo)

    payload = [
        HabilidadComparadaCreateDTO(
            habilidad="Rust",
            demanda=90.0,
            oferta_formativa=30.0,
            emergente=True,
        ),
        HabilidadComparadaCreateDTO(
            habilidad="C++",
            demanda=75.0,
            oferta_formativa=80.0,
            emergente=False,
        ),
    ]

    saved = await service.save_habilidades_por_ocupacion(
        "desarrollador_sistemas", payload
    )
    assert len(saved) == 2

    rust = next(h for h in saved if h.habilidad == "Rust")
    assert rust.brecha == 60.0
    assert rust.emergente is True

    cpp = next(h for h in saved if h.habilidad == "C++")
    assert cpp.brecha == 0.0


@pytest.mark.asyncio
async def test_brecha_service_seed_catalogo(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica la siembra global de ocupaciones base."""
    repo = SQLAlchemyBrechaRepository(db=in_memory_session)
    service = BrechaService(repository=repo)

    seeded_count = await service.seed_catalogo()
    assert seeded_count >= 5

    ocupaciones = await repo.get_all_ocupaciones()
    assert "desarrollador_software" in ocupaciones
    assert "analista_datos" in ocupaciones
