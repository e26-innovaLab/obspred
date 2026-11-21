"""Pruebas unitarias para el repositorio SqlAlchemyIndiceEmpleabilidadRepository."""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.constants import (
    INDICE_EMPLEABILIDAD_PESOS_DEFAULT,
    DimensionIndiceNombre,
)
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.models.indicador import IndicadorModel
from app.infrastructure.persistence.repositories import (
    SqlAlchemyIndiceEmpleabilidadRepository,
)


@pytest.mark.asyncio
async def test_repository_get_by_ocupacion_catalogo() -> None:
    """Verifica la resolución directa desde el catálogo metodológico."""
    repo = SqlAlchemyIndiceEmpleabilidadRepository(session=None)
    entity = await repo.get_by_ocupacion(
        ocupacion="dev-software",
        pais="ARG",
        sector="tecnologia",
        periodo="2026-Q1",
    )

    assert entity is not None
    assert entity.ocupacion_id == "dev-software"
    assert entity.ocupacion_nombre == "Desarrollador/a de software"
    assert entity.pais == "ARG"
    assert "INDEC" in entity.fuente
    assert len(entity.dimensiones) == 4
    assert len(entity.evolucion) >= 3


@pytest.mark.asyncio
async def test_repository_get_by_ocupacion_aliases() -> None:
    """Verifica que alias y nombres normalizados resuelvan a la misma entidad."""
    repo = SqlAlchemyIndiceEmpleabilidadRepository(session=None)

    e1 = await repo.get_by_ocupacion("desarrollador-de-software")
    e2 = await repo.get_by_ocupacion("Desarrollador de software")
    e3 = await repo.get_by_ocupacion("software developer")

    assert e1 is not None and e1.ocupacion_id == "dev-software"
    assert e2 is not None and e2.ocupacion_id == "dev-software"
    assert e3 is not None and e3.ocupacion_id == "dev-software"


@pytest.mark.asyncio
async def test_repository_fuente_por_pais() -> None:
    """Verifica que la fuente trazable refleje el país seleccionado."""
    repo = SqlAlchemyIndiceEmpleabilidadRepository(session=None)

    e_arg = await repo.get_by_ocupacion("enfermeria", pais="ARG")
    e_chl = await repo.get_by_ocupacion("enfermeria", pais="CHL")
    e_ury = await repo.get_by_ocupacion("enfermeria", pais="URY")
    e_gen = await repo.get_by_ocupacion("enfermeria", pais=None)
    e_chile_nombre = await repo.get_by_ocupacion("enfermeria", pais="Chile")
    e_desconocido = await repo.get_by_ocupacion("enfermeria", pais="pais-desconocido")

    assert e_arg is not None and "INDEC" in e_arg.fuente
    assert e_chl is not None and "SENCE" in e_chl.fuente
    assert e_ury is not None and "INE Uruguay" in e_ury.fuente
    assert e_gen is not None and "Armonizadas" in e_gen.fuente
    assert e_chile_nombre is not None and "SENCE" in e_chile_nombre.fuente
    assert e_desconocido is not None and "Armonizadas" in e_desconocido.fuente


@pytest.mark.asyncio
async def test_repository_ocupacion_inexistente() -> None:
    """Verifica que una ocupación no existente retorne None."""
    repo = SqlAlchemyIndiceEmpleabilidadRepository(session=None)
    entity = await repo.get_by_ocupacion("ocupacion-inexistente-1234")
    assert entity is None


@pytest.mark.asyncio
async def test_repository_exists_ocupacion() -> None:
    """Verifica la comprobación de existencia de ocupaciones en catálogo."""
    repo = SqlAlchemyIndiceEmpleabilidadRepository(session=None)
    assert await repo.exists_ocupacion("analista-datos") is True
    assert await repo.exists_ocupacion("Analista de datos") is True
    assert await repo.exists_ocupacion("inexistente_total") is False


@pytest.mark.asyncio
async def test_repository_con_registros_en_bd() -> None:
    """Verifica la consulta y agregación de indicadores persistidos en base de datos."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        # Insertar registro de ocupación no presente en el catálogo estático
        nuevo_indicador = IndicadorModel(
            pais="ARG",
            sector="Biotecnología",
            ocupacion="Bioinformático Especialista",
            indicador="indice_empleabilidad",
            periodo="2026-Q1",
            valor=87.5,
            tipo="calculado",
            fuente="Ministerio de Ciencia / CONICET",
            fecha_actualizacion=date(2026, 9, 30),
        )
        session.add(nuevo_indicador)
        await session.commit()

        repo = SqlAlchemyIndiceEmpleabilidadRepository(session=session)
        assert await repo.exists_ocupacion("Bioinformático Especialista") is True

        entity = await repo.get_by_ocupacion(
            ocupacion="Bioinformático Especialista",
            pais="ARG",
        )
        assert entity is not None
        assert entity.ocupacion_nombre == "Bioinformático Especialista"
        assert entity.score == 87.5
        assert entity.nivel == "Muy Alto"
        assert entity.fuente == "Ministerio de Ciencia / CONICET"
        assert entity.sector == "Biotecnología"

        # Verificar que las dimensiones usan los pesos canónicos y suman 1.0
        assert len(entity.dimensiones) == 4
        assert sum(d.peso for d in entity.dimensiones) == pytest.approx(1.0)
        pesos_dict = {d.nombre: d.peso for d in entity.dimensiones}
        assert (
            pesos_dict[DimensionIndiceNombre.DEMANDA_PUESTOS]
            == INDICE_EMPLEABILIDAD_PESOS_DEFAULT[DimensionIndiceNombre.DEMANDA_PUESTOS]
        )
        assert (
            pesos_dict[DimensionIndiceNombre.ESTABILIDAD_SALARIAL]
            == INDICE_EMPLEABILIDAD_PESOS_DEFAULT[
                DimensionIndiceNombre.ESTABILIDAD_SALARIAL
            ]
        )
        assert (
            pesos_dict[DimensionIndiceNombre.COBERTURA_FORMATIVA]
            == INDICE_EMPLEABILIDAD_PESOS_DEFAULT[
                DimensionIndiceNombre.COBERTURA_FORMATIVA
            ]
        )
        assert (
            pesos_dict[DimensionIndiceNombre.CRECIMIENTO_RECIENTE]
            == INDICE_EMPLEABILIDAD_PESOS_DEFAULT[
                DimensionIndiceNombre.CRECIMIENTO_RECIENTE
            ]
        )


@pytest.mark.asyncio
async def test_repository_ocupacion_catalogo_en_bd_sin_sector_resuelve_canonico() -> (
    None
):
    """Verifica que si una ocupación del catálogo se encuentra en BD sin sector,
    el canon_sector se resuelva desde el catálogo y nunca retorne 'general'.
    """
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        # Desarrollador/a de software vive en catálogo con sector "tecnologia".
        # Lo insertamos en BD con sector=None para simular registro sin sector.
        registro_sin_sector = IndicadorModel(
            pais="ARG",
            sector=None,
            ocupacion="Desarrollador/a de software",
            indicador="demanda_puestos",
            periodo="2026-Q1",
            valor=80.0,
            tipo="observado",
            fuente="INDEC",
            fecha_actualizacion=date(2026, 9, 30),
        )
        session.add(registro_sin_sector)
        await session.commit()

        repo = SqlAlchemyIndiceEmpleabilidadRepository(session=session)
        entity = await repo.get_by_ocupacion("Desarrollador/a de software", pais="ARG")

        assert entity is not None
        assert entity.sector != "general"
        assert entity.sector == "tecnologia"


@pytest.mark.asyncio
async def test_repository_get_ranking_catalogo() -> None:
    """Verifica que get_ranking retorne ocupaciones por país con puestos None."""
    repo = SqlAlchemyIndiceEmpleabilidadRepository(session=None)
    items = await repo.get_ranking(paises=["ARG", "URY"], sector="tecnologia")

    assert len(items) == 8  # 4 ocupaciones de tecnología x 2 países
    for item in items:
        assert item.sector == "tecnologia"
        assert item.pais in ["ARG", "URY"]
        assert item.puestos_disponibles is None
        assert 0.0 <= item.score <= 100.0
