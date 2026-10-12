"""Pruebas unitarias para el repositorio SqlAlchemyIndicadorRepository."""

from datetime import date
from typing import List

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.domain.interfaces.external_connector import RawIndicatorRecord
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.repositories.indicador_repository import (
    SqlAlchemyIndicadorRepository,
)


@pytest.fixture
async def in_memory_session() -> AsyncSession:
    """Provee una sesión SQLite en memoria con esquema creado para pruebas unitarias."""
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
async def test_indicador_repository_upsert_batch_e_idempotencia(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica inserción inicial y actualización idempotente de registros."""
    repo = SqlAlchemyIndicadorRepository(session=in_memory_session)

    initial_records: List[RawIndicatorRecord] = [
        RawIndicatorRecord(
            pais="ARG",
            sector=None,
            ocupacion=None,
            indicador="tasa_desempleo",
            periodo="2023",
            valor=6.1,
            tipo="observado",
            fuente="World Bank",
            fecha_actualizacion=date(2024, 1, 15),
        ),
        RawIndicatorRecord(
            pais="CHL",
            sector="Tecnología",
            ocupacion=None,
            indicador="usuarios_internet",
            periodo="2023",
            valor=90.2,
            tipo="observado",
            fuente="World Bank",
            fecha_actualizacion=date(2024, 1, 15),
        ),
    ]

    # Inserción inicial
    inserted_count = await repo.upsert_batch(initial_records)
    assert inserted_count == 2

    # Verificación en BD
    found = await repo.get_by_filters(pais="ARG")
    assert len(found) == 1
    assert found[0].valor == 6.1
    assert found[0].indicador == "tasa_desempleo"

    # Segunda ejecución con valor actualizado (upsert)
    updated_records: List[RawIndicatorRecord] = [
        RawIndicatorRecord(
            pais="ARG",
            sector=None,
            ocupacion=None,
            indicador="tasa_desempleo",
            periodo="2023",
            valor=6.3,  # Valor corregido
            tipo="observado",
            fuente="World Bank",
            fecha_actualizacion=date(2024, 6, 1),
        )
    ]

    persisted_updated = await repo.upsert_batch(updated_records)
    assert persisted_updated == 1

    # Debe seguir existiendo un único registro para ARG, con valor actualizado
    after_update = await repo.get_by_filters(pais="ARG")
    assert len(after_update) == 1
    assert after_update[0].valor == 6.3
    assert after_update[0].fecha_actualizacion == date(2024, 6, 1)


@pytest.mark.asyncio
async def test_indicador_repository_get_by_filters_jerarquia(
    in_memory_session: AsyncSession,
) -> None:
    """Verifica que el filtrado jerárquico responda correctamente por país y período."""
    repo = SqlAlchemyIndicadorRepository(session=in_memory_session)

    records: List[RawIndicatorRecord] = [
        RawIndicatorRecord(
            pais="ARG",
            sector="Tecnología",
            ocupacion=None,
            indicador="usuarios_internet",
            periodo="2021",
            valor=85.0,
            tipo="observado",
            fuente="World Bank",
            fecha_actualizacion=date(2024, 1, 1),
        ),
        RawIndicatorRecord(
            pais="ARG",
            sector="Tecnología",
            ocupacion=None,
            indicador="usuarios_internet",
            periodo="2023",
            valor=88.5,
            tipo="observado",
            fuente="World Bank",
            fecha_actualizacion=date(2024, 1, 1),
        ),
        RawIndicatorRecord(
            pais="URY",
            sector="Servicios",
            ocupacion=None,
            indicador="empleo_servicios",
            periodo="2023",
            valor=72.0,
            tipo="observado",
            fuente="World Bank",
            fecha_actualizacion=date(2024, 1, 1),
        ),
    ]

    await repo.upsert_batch(records)

    # Filtrar por país ARG
    arg_results = await repo.get_by_filters(pais="ARG")
    assert len(arg_results) == 2

    # Filtrar por país ARG y rango desde 2022
    arg_desde_2022 = await repo.get_by_filters(pais="ARG", desde="2022")
    assert len(arg_desde_2022) == 1
    assert arg_desde_2022[0].periodo == "2023"

    # Filtrar por sector Servicios
    servicios = await repo.get_by_filters(sector="Servicios")
    assert len(servicios) == 1
    assert servicios[0].pais == "URY"
