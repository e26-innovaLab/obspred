"""Pruebas unitarias para AlertaService."""

from unittest.mock import AsyncMock

import pytest

from app.application.services.alertas_service import AlertaService
from app.infrastructure.persistence.models.indicador import IndicadorModel


@pytest.fixture
def mock_indicador_repository() -> AsyncMock:
    """Fixture que provee un repositorio mockeado para indicadores."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_alerta_service_genera_alerta_cuando_variacion_supera_umbral(
    mock_indicador_repository: AsyncMock,
) -> None:
    """Verifica que se detecten alertas si la variación
    porcentual supera los umbrales.
    """
    rec1 = IndicadorModel(
        pais="ARG",
        sector="tecnologia",
        ocupacion="dev-software",
        indicador="tasa_desempleo",
        fuente="INDEC",
        periodo="2025-Q1",
        valor=10.0,
        tipo="observado",
    )
    rec2 = IndicadorModel(
        pais="ARG",
        sector="tecnologia",
        ocupacion="dev-software",
        indicador="tasa_desempleo",
        fuente="INDEC",
        periodo="2025-Q2",
        valor=11.0,  # +10% de variación -> nivel alto (>= 8.0)
        tipo="observado",
    )
    mock_indicador_repository.get_by_filters.return_value = [rec1, rec2]

    service = AlertaService(indicador_repository=mock_indicador_repository)
    alertas = await service.get_alertas(pais="ARG")

    assert len(alertas) == 1
    assert alertas[0].pais == "ARG"
    assert alertas[0].indicador == "tasa_desempleo"
    assert alertas[0].nivel == "alto"
    assert alertas[0].variacion_pct == 10.0


@pytest.mark.asyncio
async def test_alerta_service_sin_variacion_no_genera_alerta(
    mock_indicador_repository: AsyncMock,
) -> None:
    """Verifica que variaciones pequeñas (<5%) no generen alertas."""
    rec1 = IndicadorModel(
        pais="ARG",
        sector="tecnologia",
        ocupacion="dev-software",
        indicador="tasa_desempleo",
        fuente="INDEC",
        periodo="2025-Q1",
        valor=10.0,
        tipo="observado",
    )
    rec2 = IndicadorModel(
        pais="ARG",
        sector="tecnologia",
        ocupacion="dev-software",
        indicador="tasa_desempleo",
        fuente="INDEC",
        periodo="2025-Q2",
        valor=10.2,  # +2% de variación -> no supera 5%
        tipo="observado",
    )
    mock_indicador_repository.get_by_filters.return_value = [rec1, rec2]

    service = AlertaService(indicador_repository=mock_indicador_repository)
    alertas = await service.get_alertas(pais="ARG")

    assert len(alertas) == 0
