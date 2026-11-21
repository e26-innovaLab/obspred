"""Pruebas de integración para el endpoint dinámico /catalogo."""

from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import CATALOGO_ROUTE
from app.infrastructure.persistence.models.indicador import IndicadorModel


@pytest.mark.asyncio
async def test_catalogo_endpoint_estructura_y_autoseed(
    async_client: AsyncClient,
) -> None:
    """Verifica que /catalogo autosiembre datos y devuelva ApiResponse."""
    url = f"{settings.api_v1_prefix}{CATALOGO_ROUTE}"
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["message"] == "Catálogo de taxonomías recuperado con éxito."
    assert "timestamp" in payload

    data = payload["data"]
    assert "paises" in data
    assert "sectores" in data
    assert "ocupaciones" in data
    assert "indicadores" in data
    assert "periodos" in data

    # Verificación de datos sembrados automáticamente
    assert len(data["paises"]) == 3
    assert {p["id"] for p in data["paises"]} == {"ARG", "URY", "CHL"}

    assert len(data["sectores"]) == 5
    assert len(data["ocupaciones"]) == 20
    assert len(data["indicadores"]) == 4

    # Sin observaciones en la BD de test, min y max deben ser None
    assert data["periodos"]["min"] is None
    assert data["periodos"]["max"] is None


@pytest.mark.asyncio
async def test_catalogo_endpoint_con_periodos_reales(
    async_client: AsyncClient,
    test_db_session: AsyncSession,
) -> None:
    """Verifica que el rango temporal refleje los períodos de las observaciones."""
    # Insertar observaciones de prueba
    hoy = date(2025, 1, 1)
    obs_antigua = IndicadorModel(
        pais="ARG",
        indicador="tasa_desempleo",
        periodo="2020-Q1",
        valor=10.5,
        tipo="observado",
        fuente="EPH",
        fecha_actualizacion=hoy,
    )
    obs_reciente = IndicadorModel(
        pais="CHL",
        indicador="tasa_desempleo",
        periodo="2025-Q3",
        valor=8.2,
        tipo="observado",
        fuente="INE",
        fecha_actualizacion=hoy,
    )
    test_db_session.add_all([obs_antigua, obs_reciente])
    await test_db_session.commit()

    url = f"{settings.api_v1_prefix}{CATALOGO_ROUTE}"
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["periodos"]["min"] == "2020-Q1"
    assert payload["data"]["periodos"]["max"] == "2025-Q3"
