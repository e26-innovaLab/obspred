"""Pruebas de integración para el endpoint GET /indicadores."""

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.constants import INDICADORES_ROUTE


@pytest.mark.asyncio
async def test_get_indicadores_sin_filtros(async_client: AsyncClient) -> None:
    """Verifica que la consulta sin parámetros retorne 200 con la envoltura ApiResponse.

    Args:
        async_client: Cliente HTTP asíncrono de pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICADORES_ROUTE}"
    response = await async_client.get(url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"] == []
    assert payload["errors"] is None
    assert "timestamp" in payload
    assert payload["meta"]["total"] == 0
    assert payload["meta"]["extra"]["filtros"]["pais"] is None


@pytest.mark.asyncio
async def test_get_indicadores_con_filtros_vacios(
    async_client: AsyncClient,
) -> None:
    """Verifica que query params vacíos (?pais=&sector=...) sean admitidos y limpiados.

    Args:
        async_client: Cliente HTTP asíncrono de pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICADORES_ROUTE}"
    params = {
        "pais": "",
        "sector": "",
        "ocupacion": "",
        "desde": "",
        "hasta": "",
    }
    response = await async_client.get(url, params=params)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"] == []
    assert payload["meta"]["extra"]["filtros"]["pais"] is None
    assert payload["meta"]["extra"]["filtros"]["sector"] is None
    assert payload["meta"]["extra"]["filtros"]["ocupacion"] is None


@pytest.mark.asyncio
async def test_get_indicadores_con_filtros_completos(
    async_client: AsyncClient,
) -> None:
    """Verifica que los filtros suministrados se reflejen adecuadamente en metadatos.

    Args:
        async_client: Cliente HTTP asíncrono de pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICADORES_ROUTE}"
    params = {
        "pais": "ARG",
        "sector": "Tecnología",
        "ocupacion": "Desarrollador de software",
        "desde": "2024-Q1",
        "hasta": "2024-Q4",
    }
    response = await async_client.get(url, params=params)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"] == []
    assert payload["meta"]["extra"]["filtros"]["pais"] == "ARG"
    assert payload["meta"]["extra"]["filtros"]["sector"] == "Tecnología"
    assert (
        payload["meta"]["extra"]["filtros"]["ocupacion"]
        == "Desarrollador de software"
    )
    assert payload["meta"]["extra"]["filtros"]["desde"] == "2024-Q1"
    assert payload["meta"]["extra"]["filtros"]["hasta"] == "2024-Q4"


@pytest.mark.asyncio
async def test_get_indicadores_sanitiza_espacios_en_blanco(
    async_client: AsyncClient,
) -> None:
    """Verifica que espacios periféricos se eliminen y cadenas vacías sean None.

    Args:
        async_client: Cliente HTTP asíncrono de pruebas.
    """
    url = f"{settings.api_v1_prefix}{INDICADORES_ROUTE}"
    params = {
        "pais": "  URY  ",
        "sector": "   ",
    }
    response = await async_client.get(url, params=params)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["meta"]["extra"]["filtros"]["pais"] == "URY"
    assert payload["meta"]["extra"]["filtros"]["sector"] is None
