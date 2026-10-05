"""Pruebas de integración para los endpoints de StudyIndicator.

Comprueba que:
1. El controlador y el servicio interactúan correctamente a través de HTTP.
2. Las excepciones de dominio se traducen a respuestas estándar ApiResponse.
"""

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.constants import STUDY_INDICATORS_ROUTE


@pytest.mark.asyncio
async def test_list_study_indicators_api(async_client: AsyncClient) -> None:
    """Verifica que el endpoint GET retorne los indicadores en formato ApiResponse."""
    url = f"{settings.api_v1_prefix}{STUDY_INDICATORS_ROUTE}"
    response = await async_client.get(url)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1


@pytest.mark.asyncio
async def test_get_study_indicator_by_id_success(async_client: AsyncClient) -> None:
    """Verifica la consulta por ID de un indicador preexistente."""
    url = f"{settings.api_v1_prefix}{STUDY_INDICATORS_ROUTE}/ind-ar-01"
    response = await async_client.get(url)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == "ind-ar-01"
    assert body["data"]["country"] == "AR"


@pytest.mark.asyncio
async def test_get_study_indicator_by_id_not_found(async_client: AsyncClient) -> None:
    """Verifica que la EntityNotFoundException se transforme en HTTP 404 ApiResponse."""
    url = f"{settings.api_v1_prefix}{STUDY_INDICATORS_ROUTE}/ind-inexistente-999"
    response = await async_client.get(url)

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["status_code"] == 404
    assert body["data"] is None
    assert body["errors"][0]["code"] == "ENTITY_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_study_indicator_domain_validation_failure(
    async_client: AsyncClient,
) -> None:
    """Verifica que la DomainException devuelva HTTP 400 ApiResponse."""
    url = f"{settings.api_v1_prefix}{STUDY_INDICATORS_ROUTE}"
    payload = {
        "name": "Indicador en Brasil",
        "country": "BR",  # No soportado
        "sector": "Tecnología",
        "value": 12.0,
        "unit": "%",
        "source": "IBGE",
    }
    response = await async_client.post(url, json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["status_code"] == 400
    assert body["errors"][0]["code"] == "DOMAIN_RULE_VIOLATION"
    assert "El país 'BR' no está soportado" in body["errors"][0]["detail"]


@pytest.mark.asyncio
async def test_create_study_indicator_success(async_client: AsyncClient) -> None:
    """Verifica la creación exitosa a través de la API retornando HTTP 201."""
    url = f"{settings.api_v1_prefix}{STUDY_INDICATORS_ROUTE}"
    payload = {
        "name": "Nuevos Empleos en Energía Renovable",
        "country": "UY",
        "sector": "Energía",
        "value": 3500.0,
        "unit": "Puestos",
        "source": "Ministerio de Industria UY",
    }
    response = await async_client.post(url, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["status_code"] == 201
    assert body["data"]["country"] == "UY"
    assert body["data"]["sector"] == "Energía"
    assert body["data"]["id"].startswith("ind-")
