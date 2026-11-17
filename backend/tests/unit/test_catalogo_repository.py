"""Pruebas unitarias para SqlAlchemyCatalogoRepository."""

from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.models.catalogo import CatalogoPaisModel
from app.infrastructure.persistence.models.indicador import IndicadorModel
from app.infrastructure.persistence.repositories.catalogo_repository import (
    SqlAlchemyCatalogoRepository,
)


@pytest.mark.asyncio
async def test_seed_catalogo_inicial_idempotente(
    test_db_session: AsyncSession,
) -> None:
    """Verifica que el seed cargue datos y sea estrictamente idempotente."""
    repo = SqlAlchemyCatalogoRepository(session=test_db_session)

    # Primera ejecución: debe insertar registros
    stats_1 = await repo.seed_catalogo_inicial()
    assert stats_1["paises"] == 3
    assert stats_1["sectores"] == 5
    assert stats_1["ocupaciones"] == 20
    assert stats_1["indicadores"] == 4

    # Segunda ejecución: no debe duplicar ni lanzar error de unicidad
    stats_2 = await repo.seed_catalogo_inicial()
    assert stats_2["paises"] == 0
    assert stats_2["sectores"] == 0
    assert stats_2["ocupaciones"] == 0
    assert stats_2["indicadores"] == 0


@pytest.mark.asyncio
async def test_get_paises_orden_y_activos(test_db_session: AsyncSession) -> None:
    """Verifica orden por campo orden y exclusión de registros inactivos."""
    repo = SqlAlchemyCatalogoRepository(session=test_db_session)
    await repo.seed_catalogo_inicial()

    # Desactivar un país para probar filtro activo
    pais_chl = await test_db_session.get(CatalogoPaisModel, "CHL")
    assert pais_chl is not None
    pais_chl.activo = False
    await test_db_session.commit()

    paises = await repo.get_paises()
    assert len(paises) == 2
    assert [p.id for p in paises] == ["ARG", "URY"]


@pytest.mark.asyncio
async def test_get_sectores_y_ocupaciones_con_filtro(
    test_db_session: AsyncSession,
) -> None:
    """Verifica la recuperación de sectores y el filtrado por sector de ocupaciones."""
    repo = SqlAlchemyCatalogoRepository(session=test_db_session)
    await repo.seed_catalogo_inicial()

    sectores = await repo.get_sectores()
    assert len(sectores) == 5
    tec = next(s for s in sectores if s.id == "tecnologia")
    assert "J" in tec.isic

    # Todas las ocupaciones
    todas = await repo.get_ocupaciones()
    assert len(todas) == 20

    # Filtradas por sector tecnología
    tec_ocupaciones = await repo.get_ocupaciones(sector_id="tecnologia")
    assert len(tec_ocupaciones) == 4
    assert all(o.sector == "tecnologia" for o in tec_ocupaciones)


@pytest.mark.asyncio
async def test_get_indicadores(test_db_session: AsyncSession) -> None:
    """Verifica que se recuperen los indicadores maestros con sus frecuencias."""
    repo = SqlAlchemyCatalogoRepository(session=test_db_session)
    await repo.seed_catalogo_inicial()

    indicadores = await repo.get_indicadores()
    assert len(indicadores) == 4
    ids = [i.id for i in indicadores]
    assert "tasa_desempleo" in ids
    assert "puestos_demandados" in ids


@pytest.mark.asyncio
async def test_get_rango_periodos_base_vacia(
    test_db_session: AsyncSession,
) -> None:
    """Verifica que una base sin observaciones devuelva min=None y max=None."""
    repo = SqlAlchemyCatalogoRepository(session=test_db_session)
    rango = await repo.get_rango_periodos()
    assert rango.min is None
    assert rango.max is None


@pytest.mark.asyncio
async def test_get_rango_periodos_formatos_mixtos(
    test_db_session: AsyncSession,
) -> None:
    """Verifica cálculo cronológico con períodos mixtos (anual, ISO, QX)."""
    repo = SqlAlchemyCatalogoRepository(session=test_db_session)

    # Insertar observaciones de prueba con distintos formatos
    hoy = date(2024, 1, 1)
    obs1 = IndicadorModel(
        pais="ARG",
        indicador="empleo",
        periodo="2019",
        valor=100.0,
        tipo="observado",
        fuente="Test",
        fecha_actualizacion=hoy,
    )
    obs2 = IndicadorModel(
        pais="ARG",
        indicador="empleo",
        periodo="2024-07-01",
        valor=105.0,
        tipo="observado",
        fuente="Test",
        fecha_actualizacion=hoy,
    )
    obs3 = IndicadorModel(
        pais="URY",
        indicador="empleo",
        periodo="2021-Q2",
        valor=50.0,
        tipo="observado",
        fuente="Test",
        fecha_actualizacion=hoy,
    )
    obs4 = IndicadorModel(
        pais="CHL",
        indicador="empleo",
        periodo="2023",
        trimestre="Q4",
        valor=70.0,
        tipo="observado",
        fuente="Test",
        fecha_actualizacion=hoy,
    )

    test_db_session.add_all([obs1, obs2, obs3, obs4])
    await test_db_session.commit()

    rango = await repo.get_rango_periodos()
    assert rango.min == "2019"
    assert rango.max == "2024-Q3"
