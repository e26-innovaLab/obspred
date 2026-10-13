"""Servicio de aplicación para coordinar la sincronización de fuentes externas."""

import time

from app.application.dtos.sync_dto import ExternalSyncResultDTO
from app.core.logging import logger
from app.domain.interfaces.external_connector import IExternalDataConnector
from app.domain.interfaces.indicador_repository import IIndicadorRepository


class ExternalSyncService:
    """Orquestador de sincronización y normalización de indicadores externos.

    Aplica el principio de inversión de dependencias recibiendo el conector
    específico (puerto IExternalDataConnector) y el repositorio de persistencia
    (puerto IIndicadorRepository).
    """

    def __init__(
        self,
        connector: IExternalDataConnector,
        repository: IIndicadorRepository,
    ) -> None:
        """Inicializa el servicio de orquestación de ingesta.

        Args:
            connector: Adaptador del servicio externo a consultar.
            repository: Repositorio de destino para persistencia de indicadores.
        """
        self._connector = connector
        self._repository = repository

    async def sync_data(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> ExternalSyncResultDTO:
        """Ejecuta el ciclo de extracción, validación y persistencia idempotente.

        Args:
            paises: Lista opcional de países a sincronizar.
            indicadores: Lista opcional de indicadores a sincronizar.
            periodo_desde: Período inicial opcional (ej. '2020').
            periodo_hasta: Período final opcional (ej. '2024').

        Returns:
            ExternalSyncResultDTO: Métricas y resultado final del proceso.
        """
        source_name = self._connector.source_name
        start_time = time.perf_counter()

        logger.info(
            "Iniciando sincronización para fuente '%s' (países: %s, indicadores: %s)",
            source_name,
            paises,
            indicadores,
        )

        try:
            # 1. Extracción y transformación mediante el conector
            raw_records = await self._connector.fetch_indicators(
                paises=paises,
                indicadores=indicadores,
                periodo_desde=periodo_desde,
                periodo_hasta=periodo_hasta,
            )

            total_fetched = len(raw_records)
            if total_fetched == 0:
                logger.warning(
                    "Fuente '%s' no devolvió datos para los criterios provistos.",
                    source_name,
                )
                duration = time.perf_counter() - start_time
                return ExternalSyncResultDTO(
                    source=source_name,
                    status="success",
                    total_fetched=0,
                    total_persisted=0,
                    execution_time_seconds=round(duration, 3),
                    countries_synced=paises or [],
                    indicators_synced=indicadores or [],
                    error_message="Sin registros para los criterios provistos.",
                )

            # 2. Persistencia idempotente en el repositorio
            total_persisted = await self._repository.upsert_batch(raw_records)

            # Extraemos países e indicadores únicos efectivamente obtenidos
            countries_found = sorted(list({r.pais for r in raw_records}))
            indicators_found = sorted(list({r.indicador for r in raw_records}))

            duration = time.perf_counter() - start_time
            logger.info(
                "Sincronización de '%s' finalizada: %d obtenidos, %d guardados (%.2fs)",
                source_name,
                total_fetched,
                total_persisted,
                duration,
            )

            return ExternalSyncResultDTO(
                source=source_name,
                status="success",
                total_fetched=total_fetched,
                total_persisted=total_persisted,
                execution_time_seconds=round(duration, 3),
                countries_synced=countries_found,
                indicators_synced=indicators_found,
            )

        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.exception(
                "Fallo crítico durante la sincronización de '%s': %s",
                source_name,
                str(exc),
            )
            return ExternalSyncResultDTO(
                source=source_name,
                status="failed",
                total_fetched=0,
                total_persisted=0,
                execution_time_seconds=round(duration, 3),
                countries_synced=paises or [],
                indicators_synced=indicadores or [],
                error_message=str(exc),
            )
