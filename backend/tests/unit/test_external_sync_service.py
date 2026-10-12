"""Pruebas unitarias para el servicio de aplicación ExternalSyncService."""

from datetime import date
from typing import List, Optional
from unittest.mock import AsyncMock

import pytest

from app.application.services.external_sync_service import ExternalSyncService
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)
from app.domain.interfaces.indicador_repository import IIndicadorRepository


class FakeConnector(IExternalDataConnector):
    """Implementación fake de IExternalDataConnector para pruebas."""

    def __init__(self, records: Optional[List[RawIndicatorRecord]] = None) -> None:
        self.records = records or []
        self.should_fail = False

    @property
    def source_name(self) -> str:
        return "Fake Provider"

    async def fetch_indicators(
        self,
        paises: Optional[List[str]] = None,
        indicadores: Optional[List[str]] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
    ) -> List[RawIndicatorRecord]:
        if self.should_fail:
            raise ConnectionError("Error de conexión simulado")
        return self.records

    async def check_health(self) -> bool:
        return not self.should_fail


@pytest.mark.asyncio
async def test_external_sync_service_exitoso() -> None:
    """Verifica el flujo exitoso de obtención y persistencia."""
    sample_records = [
        RawIndicatorRecord(
            pais="ARG",
            sector=None,
            ocupacion=None,
            indicador="tasa_desempleo",
            periodo="2023",
            valor=6.5,
            tipo="observado",
            fuente="Fake Provider",
            fecha_actualizacion=date.today(),
        )
    ]
    connector = FakeConnector(records=sample_records)
    repo_mock = AsyncMock(spec=IIndicadorRepository)
    repo_mock.upsert_batch.return_value = 1

    service = ExternalSyncService(connector=connector, repository=repo_mock)
    result = await service.sync_data(paises=["ARG"])

    assert result.status == "success"
    assert result.source == "Fake Provider"
    assert result.total_fetched == 1
    assert result.total_persisted == 1
    assert result.countries_synced == ["ARG"]
    assert result.indicators_synced == ["tasa_desempleo"]
    assert result.error_message is None
    repo_mock.upsert_batch.assert_called_once_with(sample_records)


@pytest.mark.asyncio
async def test_external_sync_service_sin_registros() -> None:
    """Verifica comportamiento cuando el conector no retorna registros."""
    connector = FakeConnector(records=[])
    repo_mock = AsyncMock(spec=IIndicadorRepository)

    service = ExternalSyncService(connector=connector, repository=repo_mock)
    result = await service.sync_data()

    assert result.status == "success"
    assert result.total_fetched == 0
    assert result.total_persisted == 0
    repo_mock.upsert_batch.assert_not_called()


@pytest.mark.asyncio
async def test_external_sync_service_fallo_capturado() -> None:
    """Verifica captura y reporte de errores sin quebrar ejecución."""
    connector = FakeConnector()
    connector.should_fail = True
    repo_mock = AsyncMock(spec=IIndicadorRepository)

    service = ExternalSyncService(connector=connector, repository=repo_mock)
    result = await service.sync_data()

    assert result.status == "failed"
    assert result.total_fetched == 0
    assert result.total_persisted == 0
    assert "Error de conexión simulado" in (result.error_message or "")
