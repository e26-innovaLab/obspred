"""Pruebas unitarias para el servicio de aplicación IndiceEmpleabilidadService."""

from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.application.services.indice_empleabilidad_service import (
    IndiceEmpleabilidadService,
)
from app.core.constants import OrdenRanking
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


@pytest.mark.asyncio
async def test_service_get_ranking_orden_score_con_nulos(
    mock_repository: AsyncMock,
) -> None:
    """Verifica ordenamiento por score descendente y desempate por puestos."""
    e1 = IndiceEmpleabilidad(
        ocupacion_id="dev-software",
        ocupacion_nombre="Desarrollador/a",
        score=85.0,
        nivel="Muy Alto",
        dimensiones=[],
        puestos_disponibles=None,
        pais="ARG",
        fuente="INDEC",
    )
    e2 = IndiceEmpleabilidad(
        ocupacion_id="analista-datos",
        ocupacion_nombre="Analista de datos",
        score=85.0,
        nivel="Muy Alto",
        dimensiones=[],
        puestos_disponibles=500,
        pais="ARG",
        fuente="INDEC",
    )
    e3 = IndiceEmpleabilidad(
        ocupacion_id="operador-planta",
        ocupacion_nombre="Operador",
        score=75.0,
        nivel="Alto",
        dimensiones=[],
        puestos_disponibles=1200,
        pais="ARG",
        fuente="INDEC",
    )
    mock_repository.get_ranking.return_value = [e1, e2, e3]

    service = IndiceEmpleabilidadService(repository=mock_repository)
    dtos = await service.get_ranking_multi_pais(
        paises=["ARG"], orden=OrdenRanking.SCORE
    )

    # e2 (85.0, 500 puestos) > e1 (85.0, None puestos) > e3 (75.0, 1200 puestos)
    assert len(dtos) == 3
    assert dtos[0].ocupacion_id == "analista-datos"
    assert dtos[0].indice_empleabilidad == 85.0
    assert dtos[0].puestos_disponibles == 500

    assert dtos[1].ocupacion_id == "dev-software"
    assert dtos[1].indice_empleabilidad == 85.0
    assert dtos[1].puestos_disponibles is None

    assert dtos[2].ocupacion_id == "operador-planta"
    assert dtos[2].indice_empleabilidad == 75.0
    assert dtos[2].puestos_disponibles == 1200


@pytest.mark.asyncio
async def test_service_get_ranking_orden_puestos_nulls_last(
    mock_repository: AsyncMock,
) -> None:
    """Verifica orden por puestos descendente con NULLS LAST y desempate por score."""
    e1 = IndiceEmpleabilidad(
        ocupacion_id="dev-software",
        ocupacion_nombre="Desarrollador/a",
        score=90.0,
        nivel="Muy Alto",
        dimensiones=[],
        puestos_disponibles=None,
        pais="ARG",
        fuente="INDEC",
    )
    e2 = IndiceEmpleabilidad(
        ocupacion_id="analista-datos",
        ocupacion_nombre="Analista de datos",
        score=80.0,
        nivel="Muy Alto",
        dimensiones=[],
        puestos_disponibles=500,
        pais="ARG",
        fuente="INDEC",
    )
    e3 = IndiceEmpleabilidad(
        ocupacion_id="operador-planta",
        ocupacion_nombre="Operador",
        score=75.0,
        nivel="Alto",
        dimensiones=[],
        puestos_disponibles=1200,
        pais="ARG",
        fuente="INDEC",
    )
    mock_repository.get_ranking.return_value = [e1, e2, e3]

    service = IndiceEmpleabilidadService(repository=mock_repository)
    dtos = await service.get_ranking_multi_pais(
        paises=["ARG"], orden=OrdenRanking.PUESTOS
    )

    # e3 (1200) > e2 (500) > e1 (None al final)
    assert len(dtos) == 3
    assert dtos[0].ocupacion_id == "operador-planta"
    assert dtos[0].puestos_disponibles == 1200

    assert dtos[1].ocupacion_id == "analista-datos"
    assert dtos[1].puestos_disponibles == 500

    assert dtos[2].ocupacion_id == "dev-software"
    assert dtos[2].puestos_disponibles is None
    assert dtos[2].indice_empleabilidad == 90.0
