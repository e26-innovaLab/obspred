"""Pruebas de integración para los endpoints de salud y raíz."""

import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.core.constants import HEALTH_CHECK_ROUTE, ROOT_ROUTE, HealthStatus


@pytest.mark.asyncio
async def test_root_endpoint_returns_ok(async_client: AsyncClient) -> None:
    """Verifica que el endpoint raíz responda con código 200 y metadatos básicos.

    Args:
        async_client: Cliente HTTP asíncrono para ejecutar la solicitud.
    """
    response = await async_client.get(ROOT_ROUTE)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "online"
    assert payload["name"] == settings.app_name


@pytest.mark.asyncio
async def test_health_check_endpoint_returns_healthy(
    async_client: AsyncClient,
) -> None:
    """Verifica que el endpoint de salud responda con estado 'healthy' y estructura válida.

    Args:
        async_client: Cliente HTTP asíncrono para ejecutar la solicitud.
    """
    health_url = f"{settings.api_v1_prefix}{HEALTH_CHECK_ROUTE}"
    response = await async_client.get(health_url)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == HealthStatus.HEALTHY.value
    assert payload["environment"] == settings.app_env.value
    assert "timestamp" in payload
