"""Pruebas unitarias para CatalogoService."""

from unittest.mock import AsyncMock

import pytest

from app.application.dtos.catalogo_dto import (
    IndicadorCatalogoDTO,
    OcupacionCatalogoDTO,
    PaisCatalogoDTO,
    PeriodosRangoDTO,
    SectorCatalogoDTO,
)
from app.application.services.catalogo_service import CatalogoService
from app.domain.interfaces.catalogo_repository import ICatalogoRepository


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mock del repositorio ICatalogoRepository."""
    repo = AsyncMock(spec=ICatalogoRepository)
    repo.get_paises.return_value = [
        PaisCatalogoDTO(id="ARG", nombre="Argentina"),
        PaisCatalogoDTO(id="URY", nombre="Uruguay"),
    ]
    repo.get_sectores.return_value = [
        SectorCatalogoDTO(id="tecnologia", nombre="Tecnología", isic=["J"]),
    ]
    repo.get_ocupaciones.return_value = [
        OcupacionCatalogoDTO(
            id="dev-software",
            nombre="Desarrollador/a",
            sector="tecnologia",
            isco="2512",
        ),
    ]
    repo.get_indicadores.return_value = [
        IndicadorCatalogoDTO(
            id="tasa_desempleo",
            nombre="Tasa de desempleo",
            unidad="%",
            frecuencias=["anual"],
            desagregaciones=["pais"],
            descripcion="Nota metodológica.",
        ),
    ]
    repo.get_rango_periodos.return_value = PeriodosRangoDTO(
        min="2018-Q1", max="2026-Q2"
    )
    repo.seed_catalogo_inicial.return_value = {
        "paises": 3,
        "sectores": 5,
        "ocupaciones": 20,
        "indicadores": 4,
    }
    return repo


@pytest.mark.asyncio
async def test_get_catalogo_flujo_normal(mock_repository: AsyncMock) -> None:
    """Verifica que el servicio orqueste la consulta y retorne el DTO consolidado."""
    service = CatalogoService(repository=mock_repository)
    result = await service.get_catalogo()

    assert len(result.paises) == 2
    assert result.paises[0].id == "ARG"
    assert len(result.sectores) == 1
    assert result.sectores[0].id == "tecnologia"
    assert len(result.ocupaciones) == 1
    assert result.ocupaciones[0].id == "dev-software"
    assert len(result.indicadores) == 1
    assert result.indicadores[0].id == "tasa_desempleo"
    assert result.periodos.min == "2018-Q1"
    assert result.periodos.max == "2026-Q2"
    mock_repository.seed_catalogo_inicial.assert_not_called()


@pytest.mark.asyncio
async def test_get_catalogo_auto_seeding_cuando_vacio(
    mock_repository: AsyncMock,
) -> None:
    """Verifica que si no hay países cargados, ejecute automáticamente el seed."""
    # Primera llamada a get_paises retorna vacío, segunda retorna datos
    mock_repository.get_paises.side_effect = [
        [],
        [PaisCatalogoDTO(id="ARG", nombre="Argentina")],
    ]

    service = CatalogoService(repository=mock_repository)
    result = await service.get_catalogo()

    mock_repository.seed_catalogo_inicial.assert_awaited_once()
    assert len(result.paises) == 1
    assert result.paises[0].id == "ARG"


@pytest.mark.asyncio
async def test_get_catalogo_periodos_vacios(mock_repository: AsyncMock) -> None:
    """Verifica que una base sin observaciones devuelva periodos con min y max nulos."""
    mock_repository.get_rango_periodos.return_value = PeriodosRangoDTO(
        min=None, max=None
    )

    service = CatalogoService(repository=mock_repository)
    result = await service.get_catalogo()

    assert result.periodos.min is None
    assert result.periodos.max is None


@pytest.mark.asyncio
async def test_get_ocupaciones_por_sector(mock_repository: AsyncMock) -> None:
    """Verifica el filtrado de ocupaciones delegando al repositorio."""
    service = CatalogoService(repository=mock_repository)
    ocupaciones = await service.get_ocupaciones_por_sector("tecnologia")

    assert len(ocupaciones) == 1
    assert ocupaciones[0].sector == "tecnologia"
    mock_repository.get_ocupaciones.assert_awaited_once_with(sector_id="tecnologia")
