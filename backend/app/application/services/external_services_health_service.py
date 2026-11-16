"""Servicio de aplicación para evaluar concurrentemente la salud de conectores externos.

Orquesta la ejecución asíncrona paralela de las verificaciones de disponibilidad
operativa y latencia en todos los conectores configurados del Observatorio.
"""

import asyncio
import time
from collections.abc import Sequence

from app.application.dtos.health_dto import (
    ExternalServiceHealthDTO,
    ExternalServicesHealthReportDTO,
)
from app.core.constants import HealthStatus
from app.core.logging import logger
from app.domain.interfaces.external_connector import IExternalDataConnector


class ExternalServicesHealthService:
    """Orquestador de verificación de salud de servicios y conectores externos."""

    def __init__(self, connectors: Sequence[IExternalDataConnector]) -> None:
        """Inicializa el servicio con los adaptadores a monitorear.

        Args:
            connectors: Colección de adaptadores que implementan IExternalDataConnector.
        """
        self._connectors = connectors

    async def _check_single_connector(
        self, connector: IExternalDataConnector
    ) -> ExternalServiceHealthDTO:
        """Verifica la conectividad de un único conector y mide su latencia en ms.

        Args:
            connector: Instancia del conector a evaluar.

        Returns:
            ExternalServiceHealthDTO: Resultado detallado del estado del servicio.
        """
        source_id = getattr(
            connector,
            "source_id",
            connector.source_name.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_"),
        )
        url = getattr(connector, "base_url", "")
        start_time = time.perf_counter()

        try:
            is_healthy = await connector.check_health()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            status = HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY
            error = (
                None
                if is_healthy
                else "El servicio no superó la verificación de salud."
            )
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.warning(
                "Fallo en verificación de salud para %s: %s",
                connector.source_name,
                exc,
            )
            is_healthy = False
            status = HealthStatus.UNHEALTHY
            error = str(exc)

        return ExternalServiceHealthDTO(
            source_id=source_id,
            name=connector.source_name,
            status=status,
            is_available=is_healthy,
            latency_ms=elapsed_ms,
            url=str(url),
            error=error,
        )

    async def check_all_services(self) -> ExternalServicesHealthReportDTO:
        """Ejecuta en paralelo la verificación de salud de todos los conectores.

        Returns:
            ExternalServicesHealthReportDTO: Reporte consolidado con estado global
                y lista de resultados.
        """
        if not self._connectors:
            return ExternalServicesHealthReportDTO(
                overall_status=HealthStatus.HEALTHY,
                total_services=0,
                healthy_count=0,
                unhealthy_count=0,
                services=[],
            )

        tasks = [self._check_single_connector(conn) for conn in self._connectors]
        results: list[ExternalServiceHealthDTO] = await asyncio.gather(*tasks)

        healthy_count = sum(1 for r in results if r.is_available)
        total_services = len(results)
        unhealthy_count = total_services - healthy_count

        if healthy_count == total_services:
            overall_status = HealthStatus.HEALTHY
        elif healthy_count == 0:
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED

        return ExternalServicesHealthReportDTO(
            overall_status=overall_status,
            total_services=total_services,
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count,
            services=results,
        )
