"""Pruebas de integración para los endpoints de salud y raíz con estándar ApiResponse."""

import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.core.constants import HEALTH_CHECK_ROUTE, ROOT_ROUTE, HealthStatus


@pytest.mark.asyncio
async def test_root_endpoint_returns_standard_response(
    async_client: AsyncClient,
) -> None:
    """Verifica que el endpoint raíz responda con código 200 y el formato estándar ApiResponse.

    Args:
        async_client: Cliente HTTP asíncrono para ejecutar la solicitud.
    """
    response = await async_client.get(ROOT_ROUTE)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"]["status"] == "online"
    assert payload["data"]["name"] == settings.app_name
    assert "timestamp" in payload


@pytest.mark.asyncio
async def test_health_check_endpoint_returns_standard_response(
    async_client: AsyncClient,
) -> None:
    """Verifica que el endpoint de salud responda con la envoltura estándar y estado 'healthy'.

    Args:
        async_client: Cliente HTTP asíncrono para ejecutar la solicitud.
    """
    health_url = f"{settings.api_v1_prefix}{HEALTH_CHECK_ROUTE}"
    response = await async_client.get(health_url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status_code"] == 200
    assert payload["data"]["status"] == HealthStatus.HEALTHY.value
    assert payload["data"]["environment"] == settings.app_env.value
    assert payload["errors"] is None
    assert "timestamp" in payload
