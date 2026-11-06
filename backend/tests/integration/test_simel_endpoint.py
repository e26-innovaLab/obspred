"""Pruebas de integración para endpoints de SIMEL Chile."""

from datetime import date

import pytest
from httpx import AsyncClient

from app.api.dependencies import provide_simel_chile_connector
from app.core.config import settings
from app.core.constants import (
    DEFAULT_SIMEL_CHILE_SOURCE,
    INDICADORES_ROUTE,
    INGESTA_ROUTE,
    INGESTA_SYNC_SIMEL_CHILE_ROUTE,
    INGESTA_UPLOAD_SIMEL_ROUTE,
    PaisCodigo,
    SectorEstrategico,
    SyncStatus,
    TipoIndicador,
)
from app.domain.exceptions.simel_exceptions import SimelWafBlockedException
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)
from app.infrastructure.connectors.simel_chile_connector import (
    SimelChileConnector,
)
from app.main import app


class MockSimelBlockedConnector(IExternalDataConnector):
    """Mock que reproduce el bloqueo por WAF de Huawei Cloud."""

    @property
    def source_name(self) -> str:
        return DEFAULT_SIMEL_CHILE_SOURCE

    async def fetch_indicators(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        raise SimelWafBlockedException()

    async def check_health(self) -> bool:
        return False


class MockSimelSuccessConnector(SimelChileConnector):
    """Mock que simula extracción exitosa para pruebas de sincronización."""

    async def fetch_indicators(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        return [
            RawIndicatorRecord(
                pais=PaisCodigo.CHL,
                sector=SectorEstrategico.TECNOLOGIA,
                ocupacion="Desarrollador",
                indicador="empleo_sector",
                periodo="2024-Q1",
                valor=185.0,
                tipo=TipoIndicador.OBSERVADO,
                fuente=DEFAULT_SIMEL_CHILE_SOURCE,
                fecha_actualizacion=date.today(),
            )
        ]

    async def check_health(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_sync_simel_chile_waf_blocked_returns_502(
    async_client: AsyncClient,
) -> None:
    """Verifica que el intento de sync contra SIMEL retorne 502 Bad Gateway."""
    app.dependency_overrides[provide_simel_chile_connector] = lambda: (
        MockSimelBlockedConnector()
    )
    try:
        url = f"{settings.api_v1_prefix}{INGESTA_ROUTE}{INGESTA_SYNC_SIMEL_CHILE_ROUTE}"
        response = await async_client.post(url, json={})
        assert response.status_code == 502
        body = response.json()
        assert body["success"] is False
        assert any(
            "Huawei Cloud" in err["detail"] or "WAF" in err["detail"]
            for err in body["errors"]
        )
    finally:
        app.dependency_overrides.pop(provide_simel_chile_connector, None)


@pytest.mark.asyncio
async def test_sync_simel_chile_success(
    async_client: AsyncClient,
) -> None:
    """Verifica que si la extracción es permitida, persista y devuelva 200 OK."""
    app.dependency_overrides[provide_simel_chile_connector] = lambda: (
        MockSimelSuccessConnector()
    )
    try:
        url = f"{settings.api_v1_prefix}{INGESTA_ROUTE}{INGESTA_SYNC_SIMEL_CHILE_ROUTE}"
        response = await async_client.post(url, json={})
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["source"] == DEFAULT_SIMEL_CHILE_SOURCE
        assert body["data"]["status"] == SyncStatus.SUCCESS
        assert body["data"]["total_persisted"] == 1
    finally:
        app.dependency_overrides.pop(provide_simel_chile_connector, None)


@pytest.mark.asyncio
async def test_upload_simel_csv_file_success_and_query_indicators(
    async_client: AsyncClient,
) -> None:
    """Verifica la carga de un CSV de SIMEL, parseo, persistencia y consulta."""
    csv_content = (
        "Periodo,Indicador,Rama_Actividad,Grupo_Ocupacional,Sexo,Unidad,Valor\n"
        "2024-Q2,Tasa de desocupación,Total,Total,Total,Porcentaje,8.4\n"
        "2024-Q2,Ocupados según rama,Información y comunicaciones,"
        "Prof,Total,Miles,190.5\n"
    ).encode()

    upload_url = f"{settings.api_v1_prefix}{INGESTA_ROUTE}{INGESTA_UPLOAD_SIMEL_ROUTE}"
    files = {
        "file": (
            "simel_test_upload.csv",
            csv_content,
            "text/csv",
        )
    }

    response = await async_client.post(upload_url, files=files)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["source"] == DEFAULT_SIMEL_CHILE_SOURCE
    assert body["data"]["total_persisted"] == 2
    assert "CHL" in body["data"]["countries_synced"]

    # Consultamos el indicador recién persistido en /indicadores
    query_url = f"{settings.api_v1_prefix}{INDICADORES_ROUTE}?pais=CHL&trimestre=Q2"
    query_resp = await async_client.get(query_url)
    assert query_resp.status_code == 200
    query_body = query_resp.json()
    assert query_body["success"] is True
    assert len(query_body["data"]) >= 1
    assert query_body["data"][0]["fuente"] == DEFAULT_SIMEL_CHILE_SOURCE
    assert query_body["data"][0]["periodo"] == "2024"
    assert query_body["data"][0]["trimestre"] == "Q2"
    assert query_body["data"][0]["valor"] == 8.4
