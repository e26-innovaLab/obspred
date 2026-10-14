"""Pruebas de integración para endpoint POST /ingesta/sync/world-bank."""

from collections.abc import Generator
from datetime import date

import pytest
from httpx import AsyncClient

from app.api.dependencies import provide_world_bank_connector
from app.core.config import settings
from app.core.constants import (
    DEFAULT_WORLD_BANK_SOURCE,
    INDICADORES_ROUTE,
    INGESTA_ROUTE,
    INGESTA_SYNC_WORLD_BANK_ROUTE,
    ApiErrorCode,
    PaisCodigo,
    SyncStatus,
    TipoIndicador,
)
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)
from app.main import app


class MockWorldBankConnector(IExternalDataConnector):
    """Mock de WorldBankConnector para tests de integración."""

    @property
    def source_name(self) -> str:
        return DEFAULT_WORLD_BANK_SOURCE

    async def fetch_indicators(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        return [
            RawIndicatorRecord(
                pais=PaisCodigo.ARG,
                sector=None,
                ocupacion=None,
                indicador="tasa_desempleo",
                periodo="2023",
                valor=6.14,
                tipo=TipoIndicador.OBSERVADO,
                fuente=DEFAULT_WORLD_BANK_SOURCE,
                fecha_actualizacion=date(2024, 3, 28),
            ),
            RawIndicatorRecord(
                pais=PaisCodigo.URY,
                sector=None,
                ocupacion=None,
                indicador="tasa_desempleo",
                periodo="2023",
                valor=8.05,
                tipo=TipoIndicador.OBSERVADO,
                fuente=DEFAULT_WORLD_BANK_SOURCE,
                fecha_actualizacion=date(2024, 3, 28),
            ),
        ]

    async def check_health(self) -> bool:
        return True


@pytest.fixture(autouse=True)
def override_connector_dependency() -> Generator[None, None, None]:
    """Aísla las llamadas de red externas inyectando el mock del conector."""
    app.dependency_overrides[provide_world_bank_connector] = lambda: (
        MockWorldBankConnector()
    )
    yield
    app.dependency_overrides.pop(provide_world_bank_connector, None)


@pytest.mark.asyncio
async def test_sync_world_bank_endpoint_e_integracion_indicadores(
    async_client: AsyncClient,
) -> None:
    """Verifica que el sync persista datos y que luego GET /indicadores los retorne."""
    sync_url = f"{settings.api_v1_prefix}{INGESTA_ROUTE}{INGESTA_SYNC_WORLD_BANK_ROUTE}"
    sync_payload = {
        "paises": [PaisCodigo.ARG, PaisCodigo.URY],
        "indicadores": ["tasa_desempleo"],
        "periodo_desde": "2023",
        "periodo_hasta": "2023",
    }

    sync_response = await async_client.post(sync_url, json=sync_payload)
    assert sync_response.status_code == 200

    body = sync_response.json()
    assert body["success"] is True
    assert body["data"]["source"] == DEFAULT_WORLD_BANK_SOURCE
    assert body["data"]["status"] == SyncStatus.SUCCESS
    assert body["data"]["total_fetched"] == 2
    assert body["data"]["total_persisted"] == 2
    assert PaisCodigo.ARG in body["data"]["countries_synced"]
    assert "tasa_desempleo" in body["data"]["indicators_synced"]

    # Consultamos GET /indicadores para verificar que el dato quedó visible y trazable
    indicadores_url = f"{settings.api_v1_prefix}{INDICADORES_ROUTE}"
    get_response = await async_client.get(indicadores_url, params={"pais": "ARG"})
    assert get_response.status_code == 200

    get_body = get_response.json()
    assert get_body["success"] is True
    assert get_body["meta"]["total"] == 1

    item = get_body["data"][0]
    assert item["pais"] == "ARG"
    assert item["indicador"] == "tasa_desempleo"
    assert item["periodo"] == "2023"
    assert item["valor"] == 6.14
    assert item["tipo"] == "observado"
    assert item["fuente"] == "World Bank"
    assert item["fecha_actualizacion"] == "2024-03-28"


class FailingMockConnector(IExternalDataConnector):
    """Mock de conector que simula fallo de red."""

    @property
    def source_name(self) -> str:
        return DEFAULT_WORLD_BANK_SOURCE

    async def fetch_indicators(self, **kwargs) -> list[RawIndicatorRecord]:
        raise ConnectionError("Fallo de timeout en World Bank API")

    async def check_health(self) -> bool:
        return False


@pytest.mark.asyncio
async def test_sync_world_bank_endpoint_error_servicio_externo(
    async_client: AsyncClient,
) -> None:
    """Verifica que fallos remotos retornen HTTP 502 con ApiResponse de error."""
    app.dependency_overrides[provide_world_bank_connector] = lambda: (
        FailingMockConnector()
    )
    try:
        sync_url = (
            f"{settings.api_v1_prefix}{INGESTA_ROUTE}{INGESTA_SYNC_WORLD_BANK_ROUTE}"
        )
        response = await async_client.post(sync_url, json={})
        assert response.status_code == 502

        payload = response.json()
        assert payload["success"] is False
        assert payload["status_code"] == 502
        assert payload["data"] is None
        assert payload["errors"] is not None
        assert payload["errors"][0]["code"] == ApiErrorCode.EXTERNAL_SERVICE_ERROR
        assert "timeout" in payload["errors"][0]["detail"].lower()
    finally:
        app.dependency_overrides.pop(provide_world_bank_connector, None)
