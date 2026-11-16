"""Pruebas de integración para los endpoints de salud y raíz con ApiResponse."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api.dependencies import provide_external_services_health_service
from app.application.dtos.health_dto import (
    ExternalServiceHealthDTO,
    ExternalServicesHealthReportDTO,
)
from app.application.services.external_services_health_service import (
    ExternalServicesHealthService,
)
from app.core.config import settings
from app.core.constants import (
    HEALTH_CHECK_ROUTE,
    HEALTH_EXTERNAL_ROUTE,
    HEALTH_SERVICES_ROUTE,
    ROOT_ROUTE,
    HealthStatus,
)
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint_returns_standard_response(
    async_client: AsyncClient,
) -> None:
    """Verifica que el endpoint raíz responda con código 200 y ApiResponse.

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
    """Verifica que /health responda con la envoltura estándar y estado 'healthy'.

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


@pytest.mark.asyncio
async def test_external_services_health_endpoint_returns_standard_response(
    async_client: AsyncClient,
) -> None:
    """Verifica que /health/services responda con ApiResponse y conectores."""
    mock_service = AsyncMock(spec=ExternalServicesHealthService)
    mock_service.check_all_services.return_value = ExternalServicesHealthReportDTO(
        overall_status=HealthStatus.HEALTHY,
        total_services=2,
        healthy_count=2,
        unhealthy_count=0,
        services=[
            ExternalServiceHealthDTO(
                source_id="world_bank",
                name="World Bank",
                status=HealthStatus.HEALTHY,
                is_available=True,
                latency_ms=120.5,
                url="https://api.worldbank.org/v2",
                error=None,
            ),
            ExternalServiceHealthDTO(
                source_id="simel_chile",
                name="SIMEL - INE Chile",
                status=HealthStatus.HEALTHY,
                is_available=True,
                latency_ms=95.0,
                url="https://www.simel.gob.cl",
                error=None,
            ),
        ],
    )

    app.dependency_overrides[provide_external_services_health_service] = lambda: (
        mock_service
    )

    try:
        services_url = f"{settings.api_v1_prefix}{HEALTH_SERVICES_ROUTE}"
        response = await async_client.get(services_url)

        assert response.status_code == 200
        payload = response.json()
        assert payload["success"] is True
        assert payload["status_code"] == 200
        assert payload["data"]["overall_status"] == HealthStatus.HEALTHY.value
        assert payload["data"]["total_services"] == 2
        assert payload["data"]["healthy_count"] == 2
        assert len(payload["data"]["services"]) == 2
        assert payload["data"]["services"][0]["source_id"] == "world_bank"
        assert payload["data"]["services"][0]["is_available"] is True
        assert "timestamp" in payload

        # Verificar también ruta alias /health/external
        ext_url = f"{settings.api_v1_prefix}{HEALTH_EXTERNAL_ROUTE}"
        res_ext = await async_client.get(ext_url)
        assert res_ext.status_code == 200
        assert res_ext.json()["success"] is True

    finally:
        app.dependency_overrides.pop(provide_external_services_health_service, None)
