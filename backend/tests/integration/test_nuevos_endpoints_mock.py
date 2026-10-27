"""Pruebas de integración para los nuevos endpoints de frontend con ApiResponse."""

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.constants import (
    ALERTAS_ROUTE,
    BRECHAS_ROUTE,
    CATALOGO_ROUTE,
    INDICE_EMPLEABILIDAD_ROUTE,
    METRICAS_ROUTE,
)


@pytest.mark.asyncio
async def test_metricas_series_endpoint(async_client: AsyncClient) -> None:
    """Verifica que el endpoint /metricas/series responda según contrato."""
    url = f"{settings.api_v1_prefix}{METRICAS_ROUTE}/series"
    response = await async_client.get(
        url, params={"indicador": "puestos_demandados", "pais": "ARG,URY"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "series" in payload["data"]
    assert len(payload["data"]["series"]) == 2
    assert payload["data"]["series"][0]["pais"] == "ARG"


@pytest.mark.asyncio
async def test_metricas_proyecciones_endpoint(async_client: AsyncClient) -> None:
    """Verifica que /metricas/proyecciones responda con estructura válida."""
    url = f"{settings.api_v1_prefix}{METRICAS_ROUTE}/proyecciones"
    response = await async_client.get(
        url, params={"indicador": "tasa_desempleo", "pais": "ARG", "horizonte": 2}
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["proyectable"] is True
    assert len(payload["data"]["proyeccion"]) == 2


@pytest.mark.asyncio
async def test_metricas_kpis_endpoint(async_client: AsyncClient) -> None:
    """Verifica que el endpoint /metricas/kpis devuelva tarjetas con sparklines."""
    url = f"{settings.api_v1_prefix}{METRICAS_ROUTE}/kpis"
    response = await async_client.get(
        url,
        params={
            "indicadores": "tasa_desempleo,puestos_demandados",
            "pais": "ARG",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["kpis"]) == 2


@pytest.mark.asyncio
async def test_metricas_ranking_endpoint(async_client: AsyncClient) -> None:
    """Verifica que el endpoint /metricas/ranking responda por dimensión."""
    url = f"{settings.api_v1_prefix}{METRICAS_ROUTE}/ranking"
    response = await async_client.get(
        url,
        params={
            "dimension": "sector",
            "indicador": "puestos_demandados",
            "pais": "ARG",
            "limite": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["items"]) == 3


@pytest.mark.asyncio
async def test_metricas_comparativa_endpoint(async_client: AsyncClient) -> None:
    """Verifica que el endpoint /metricas/comparativa retorne valores por país."""
    url = f"{settings.api_v1_prefix}{METRICAS_ROUTE}/comparativa"
    response = await async_client.get(
        url,
        params={
            "indicadores": "tasa_desempleo,salario_real_indice",
            "pais": "ARG,URY,CHL",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["indicadores"]) == 2


@pytest.mark.asyncio
async def test_metricas_mapa_calor_endpoint(async_client: AsyncClient) -> None:
    """Verifica la generación de la matriz de celdas para mapa de calor."""
    url = f"{settings.api_v1_prefix}{METRICAS_ROUTE}/mapa-calor"
    response = await async_client.get(
        url,
        params={"indicador": "tasa_desempleo", "pais": "ARG,URY,CHL"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "celdas" in payload["data"]
    assert len(payload["data"]["columnas"]) == 3


@pytest.mark.asyncio
async def test_catalogo_endpoint(async_client: AsyncClient) -> None:
    """Verifica que /catalogo provea países, sectores, ocupaciones e indicadores."""
    url = f"{settings.api_v1_prefix}{CATALOGO_ROUTE}"
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["paises"]) == 3
    assert len(payload["data"]["sectores"]) == 5
    assert len(payload["data"]["ocupaciones"]) >= 10


@pytest.mark.asyncio
async def test_alertas_endpoint(async_client: AsyncClient) -> None:
    """Verifica la respuesta del listado de alertas."""
    url = f"{settings.api_v1_prefix}{ALERTAS_ROUTE}"
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert "alertas" in payload["data"]


@pytest.mark.asyncio
async def test_brechas_endpoint(async_client: AsyncClient) -> None:
    """Verifica la respuesta del análisis de brechas formativas."""
    url = f"{settings.api_v1_prefix}{BRECHAS_ROUTE}"
    response = await async_client.get(url, params={"sector": "tecnologia"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["habilidades"]) > 0


@pytest.mark.asyncio
async def test_indice_empleabilidad_ranking_endpoint(
    async_client: AsyncClient,
) -> None:
    """Verifica que /indice-empleabilidad/ranking devuelva la tabla comparativa."""
    url = f"{settings.api_v1_prefix}{INDICE_EMPLEABILIDAD_ROUTE}/ranking"
    response = await async_client.get(url, params={"pais": "ARG,URY"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["ocupaciones"]) > 0
