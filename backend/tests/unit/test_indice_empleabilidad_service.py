"""Pruebas unitarias para el servicio de aplicación IndiceEmpleabilidadService."""

from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.application.services.indice_empleabilidad_service import (
    IndiceEmpleabilidadService,
)
from app.domain.entities.indice_empleabilidad import (
    DimensionIndice,
    EvolucionIndicePunto,
    IndiceEmpleabilidad,
)
from app.domain.exceptions.base import EntityNotFoundException
from app.domain.exceptions.indice_empleabilidad import InvalidOccupationException
from app.domain.interfaces.indice_empleabilidad_repository import (
    IIndiceEmpleabilidadRepository,
)


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Fixture que crea un mock asíncrono para el repositorio."""
    return AsyncMock(spec=IIndiceEmpleabilidadRepository)


@pytest.mark.asyncio
async def test_service_get_indice_exitoso(mock_repository: AsyncMock) -> None:
    """Verifica que el servicio retorne el DTO mapeado correctamente."""
    entity = IndiceEmpleabilidad(
        ocupacion_id="dev-software",
        ocupacion_nombre="Desarrollador/a de software",
        score=81.3,
        nivel="Muy Alto",
        dimensiones=[
            DimensionIndice(
                nombre="Demanda de puestos",
                valor=88.0,
                peso=0.35,
                descripcion="Alta demanda",
            ),
        ],
        tipo="calculado",
        fuente="INDEC / Secretaría de Trabajo",
        fecha_actualizacion=date(2026, 9, 30),
        metodologia="Metodología v1",
        pais="ARG",
        sector="tecnologia",
        periodo="2026-Q1",
        evolucion=[
            EvolucionIndicePunto(periodo="2025-Q3", valor=78.1),
        ],
    )
    mock_repository.get_by_ocupacion.return_value = entity

    service = IndiceEmpleabilidadService(repository=mock_repository)
    dto = await service.get_indice_por_ocupacion(
        ocupacion="dev-software",
        pais="ARG",
        sector="tecnologia",
        periodo="2026-Q1",
    )

    assert dto.ocupacion_id == "dev-software"
    assert dto.ocupacion_nombre == "Desarrollador/a de software"
    assert dto.score == 81.3
    assert dto.nivel == "Muy Alto"
    assert len(dto.dimensiones) == 1
    assert dto.dimensiones[0].nombre == "Demanda de puestos"
    assert dto.tipo == "calculado"
    assert dto.fuente == "INDEC / Secretaría de Trabajo"
    assert len(dto.evolucion) == 1
    assert dto.evolucion[0].periodo == "2025-Q3"
    mock_repository.get_by_ocupacion.assert_awaited_once_with(
        ocupacion="dev-software",
        pais="ARG",
        sector="tecnologia",
        periodo="2026-Q1",
    )


@pytest.mark.asyncio
async def test_service_get_indice_ocupacion_vacia(
    mock_repository: AsyncMock,
) -> None:
    """Verifica que si la ocupación está vacía se lance InvalidOccupationException."""
    service = IndiceEmpleabilidadService(repository=mock_repository)

    with pytest.raises(InvalidOccupationException, match="no puede estar vacío"):
        await service.get_indice_por_ocupacion(ocupacion="   ")

    mock_repository.get_by_ocupacion.assert_not_called()


@pytest.mark.asyncio
async def test_service_get_indice_no_encontrado(
    mock_repository: AsyncMock,
) -> None:
    """Verifica que si la ocupación no existe se lance EntityNotFoundException."""
    mock_repository.get_by_ocupacion.return_value = None
    service = IndiceEmpleabilidadService(repository=mock_repository)

    with pytest.raises(EntityNotFoundException) as exc_info:
        await service.get_indice_por_ocupacion(ocupacion="ocupacion-desconocida")

    assert exc_info.value.entity_name == "Occupation"
    assert exc_info.value.entity_id == "ocupacion-desconocida"
