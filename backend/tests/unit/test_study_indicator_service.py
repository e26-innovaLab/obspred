"""Pruebas unitarias para StudyIndicatorService.

Demuestra la ventaja clave del patrón Service con Clean Architecture:
La lógica de negocio se prueba al 100% en memoria en milisegundos,
usando mocks del repositorio y sin necesidad de levantar FastAPI ni una base de datos.
"""

from unittest.mock import AsyncMock

import pytest

from app.application.dtos.study_indicator_dto import (
    CreateStudyIndicatorDTO,
    StudyIndicatorFilterDTO,
)
from app.application.services.study_indicator_service import StudyIndicatorService
from app.domain.entities.study_indicator import StudyIndicator
from app.domain.exceptions.base import DomainException, EntityNotFoundException


@pytest.mark.asyncio
async def test_get_indicator_by_id_success() -> None:
    """Verifica que el servicio retorne la entidad cuando existe en el repositorio."""
    # 1. Arrange: Simulamos el repositorio con AsyncMock
    mock_indicator = StudyIndicator(
        id="ind-01",
        name="Empleo en TI",
        country="AR",
        sector="Tecnología",
        value=50000.0,
        unit="puestos",
        source="INDEC",
    )
    mock_repository = AsyncMock()
    mock_repository.get_by_id.return_value = mock_indicator

    service = StudyIndicatorService(repository=mock_repository)

    # 2. Act: Invocamos el servicio
    result = await service.get_indicator_by_id("ind-01")

    # 3. Assert: Comprobamos el resultado y que se llamó al repositorio
    assert result.id == "ind-01"
    assert result.name == "Empleo en TI"
    mock_repository.get_by_id.assert_awaited_once_with(indicator_id="ind-01")


@pytest.mark.asyncio
async def test_get_indicator_by_id_raises_not_found() -> None:
    """Verifica que el servicio lance EntityNotFoundException si no existe."""
    mock_repository = AsyncMock()
    mock_repository.get_by_id.return_value = None

    service = StudyIndicatorService(repository=mock_repository)

    with pytest.raises(EntityNotFoundException) as exc_info:
        await service.get_indicator_by_id("ind-999")

    assert "ind-999" in str(exc_info.value)
    assert exc_info.value.entity_name == "StudyIndicator"


@pytest.mark.asyncio
async def test_create_indicator_success() -> None:
    """Verifica la creación exitosa cumpliendo todas las invariantes."""
    mock_repository = AsyncMock()
    # Hacemos que save devuelva la entidad que recibe
    mock_repository.save.side_effect = lambda entity: entity

    service = StudyIndicatorService(repository=mock_repository)
    dto = CreateStudyIndicatorDTO(
        name="Crecimiento Salarial",
        country="CL",
        sector="Tecnología",
        value=4.5,
        unit="%",
        source="INE Chile",
    )

    created = await service.create_indicator(dto)

    assert created.country == "CL"
    assert created.value == 4.5
    assert created.id.startswith("ind-")
    mock_repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_indicator_rejects_unsupported_country() -> None:
    """Verifica que el servicio aplique la regla de negocio de alcance regional."""
    mock_repository = AsyncMock()
    service = StudyIndicatorService(repository=mock_repository)

    dto = CreateStudyIndicatorDTO(
        name="Indicador Externo",
        country="BR",  # Brasil no forma parte de AR, CL, UY en el MVP
        sector="Tecnología",
        value=10.0,
        unit="%",
        source="IBGE",
    )

    with pytest.raises(DomainException) as exc_info:
        await service.create_indicator(dto)

    assert "El país 'BR' no está soportado" in str(exc_info.value)
    mock_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_indicator_rejects_negative_value() -> None:
    """Verifica que el servicio rechace valores numéricos negativos."""
    mock_repository = AsyncMock()
    service = StudyIndicatorService(repository=mock_repository)

    dto = CreateStudyIndicatorDTO(
        name="Tasa de Empleo",
        country="UY",
        sector="Salud",
        value=-5.0,  # Regla de negocio: no negativo
        unit="%",
        source="INE UY",
    )

    with pytest.raises(DomainException) as exc_info:
        await service.create_indicator(dto)

    assert "no puede ser negativo" in str(exc_info.value)
    mock_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_indicators_passes_filters() -> None:
    """Verifica que el servicio normalice y envíe los filtros al repositorio."""
    mock_repository = AsyncMock()
    mock_repository.list_all.return_value = []

    service = StudyIndicatorService(repository=mock_repository)
    filters = StudyIndicatorFilterDTO(country="ar", sector="Tecnología")

    await service.list_indicators(filters=filters)

    # Verifica que el código de país se haya normalizado a mayúsculas ("AR")
    mock_repository.list_all.assert_awaited_once_with(
        country="AR", sector="Tecnología"
    )
