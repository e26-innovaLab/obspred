"""Pruebas unitarias para ExternalServicesHealthService."""

from unittest.mock import AsyncMock

import pytest

from app.application.services.external_services_health_service import (
    ExternalServicesHealthService,
)
from app.core.constants import HealthStatus
from app.domain.interfaces.external_connector import IExternalDataConnector


def create_mock_connector(
    name: str,
    source_id: str,
    is_healthy: bool = True,
    base_url: str = "https://example.com/api",
    raises_exception: bool = False,
) -> IExternalDataConnector:
    """Crea un conector mockeado que implementa IExternalDataConnector."""
    mock = AsyncMock(spec=IExternalDataConnector)
    type(mock).source_name = name
    mock.source_id = source_id
    mock.base_url = base_url

    if raises_exception:
        mock.check_health.side_effect = RuntimeError("Conexión rechazada por timeout")
    else:
        mock.check_health.return_value = is_healthy

    return mock


@pytest.mark.asyncio
async def test_all_connectors_healthy_returns_healthy_overall_status() -> None:
    """Verifica que el estado global sea HEALTHY con todos los conectores OK."""
    c1 = create_mock_connector("World Bank", "world_bank", is_healthy=True)
    c2 = create_mock_connector("SIMEL Chile", "simel_chile", is_healthy=True)
    c3 = create_mock_connector("Datos Argentina", "datos_argentina", is_healthy=True)

    service = ExternalServicesHealthService(connectors=[c1, c2, c3])
    report = await service.check_all_services()

    assert report.overall_status == HealthStatus.HEALTHY
    assert report.total_services == 3
    assert report.healthy_count == 3
    assert report.unhealthy_count == 0
    assert len(report.services) == 3
    assert all(s.is_available for s in report.services)
    assert all(s.status == HealthStatus.HEALTHY for s in report.services)
    assert all(s.latency_ms >= 0 for s in report.services)


@pytest.mark.asyncio
async def test_partial_connectors_failure_returns_degraded_overall_status() -> None:
    """Verifica que el estado global sea DEGRADED cuando al menos un conector falla."""
    c1 = create_mock_connector("World Bank", "world_bank", is_healthy=True)
    c2 = create_mock_connector("SIMEL Chile", "simel_chile", is_healthy=False)
    c3 = create_mock_connector("Datos Argentina", "datos_argentina", is_healthy=True)

    service = ExternalServicesHealthService(connectors=[c1, c2, c3])
    report = await service.check_all_services()

    assert report.overall_status == HealthStatus.DEGRADED
    assert report.total_services == 3
    assert report.healthy_count == 2
    assert report.unhealthy_count == 1

    simel_report = next(s for s in report.services if s.source_id == "simel_chile")
    assert simel_report.is_available is False
    assert simel_report.status == HealthStatus.UNHEALTHY
    assert simel_report.error is not None


@pytest.mark.asyncio
async def test_all_connectors_failure_returns_unhealthy_overall_status() -> None:
    """Verifica que el estado global sea UNHEALTHY si todos fallan."""
    c1 = create_mock_connector("World Bank", "world_bank", is_healthy=False)
    c2 = create_mock_connector("SIMEL Chile", "simel_chile", is_healthy=False)

    service = ExternalServicesHealthService(connectors=[c1, c2])
    report = await service.check_all_services()

    assert report.overall_status == HealthStatus.UNHEALTHY
    assert report.total_services == 2
    assert report.healthy_count == 0
    assert report.unhealthy_count == 2


@pytest.mark.asyncio
async def test_connector_exception_is_handled_gracefully() -> None:
    """Verifica que excepciones en el chequeo se capturen de forma resiliente."""
    c1 = create_mock_connector("World Bank", "world_bank", is_healthy=True)
    c2 = create_mock_connector("SIMEL Chile", "simel_chile", raises_exception=True)

    service = ExternalServicesHealthService(connectors=[c1, c2])
    report = await service.check_all_services()

    assert report.overall_status == HealthStatus.DEGRADED
    assert report.healthy_count == 1
    assert report.unhealthy_count == 1

    failed = next(s for s in report.services if s.source_id == "simel_chile")
    assert failed.is_available is False
    assert "timeout" in str(failed.error).lower()


@pytest.mark.asyncio
async def test_empty_connectors_returns_healthy() -> None:
    """Verifica comportamiento cuando no hay conectores registrados."""
    service = ExternalServicesHealthService(connectors=[])
    report = await service.check_all_services()

    assert report.overall_status == HealthStatus.HEALTHY
    assert report.total_services == 0
    assert report.healthy_count == 0
    assert report.unhealthy_count == 0
    assert report.services == []


@pytest.mark.asyncio
async def test_connector_timeout_is_handled_gracefully() -> None:
    """Verifica que un conector lento sea cancelado sin bloquear el reporte."""
    import asyncio

    async def _slow_check() -> bool:
        await asyncio.sleep(1.0)
        return True

    mock_slow = AsyncMock(spec=IExternalDataConnector)
    type(mock_slow).source_name = "Slow Service"
    mock_slow.source_id = "slow_service"
    mock_slow.base_url = "https://example.com/slow"
    mock_slow.check_health.side_effect = _slow_check

    service = ExternalServicesHealthService(connectors=[mock_slow], timeout=0.05)
    report = await service.check_all_services()

    assert report.overall_status == HealthStatus.UNHEALTHY
    assert report.unhealthy_count == 1
    slow_service = report.services[0]
    assert slow_service.is_available is False
    assert slow_service.error is not None
    assert "agotado" in slow_service.error.lower()
