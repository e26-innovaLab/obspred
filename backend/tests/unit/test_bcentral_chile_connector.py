"""Pruebas unitarias para el conector del Banco Central de Chile (SIETE REST WS)."""

import json
from typing import Any

import httpx
import pytest

from app.core.constants import (
    DEFAULT_BCENTRAL_CHILE_SOURCE,
    IndicadorSlug,
    PaisCodigo,
    TipoIndicador,
)
from app.infrastructure.connectors.bcentral_chile_connector import (
    BCentralChileConnector,
)


class MockBCentralTransport(httpx.AsyncBaseTransport):
    """Transporte mock para simular respuestas de SIETE REST WS."""

    def __init__(
        self,
        status_code: int = 200,
        payload: Any = None,
        raise_exception: Exception | None = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.raise_exception = raise_exception
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.raise_exception:
            raise self.raise_exception

        content = json.dumps(self.payload).encode("utf-8")
        return httpx.Response(
            status_code=self.status_code,
            content=content,
            headers={"Content-Type": "application/json"},
            request=request,
        )


@pytest.fixture
def sample_bcentral_series_response() -> dict[str, Any]:
    """Respuesta exitosa representativa de GetSeries en SIETE."""
    return {
        "Codigo": 0,
        "Descripcion": "Operación exitosa",
        "Series": {
            "descripEsp": "Tasas de desocupación nacional",
            "Obs": [
                {
                    "indexDateString": "01-01-2024",
                    "value": "8.4",
                    "statusCode": "OK",
                },
                {
                    "indexDateString": "01-02-2024",
                    "value": "8.5",
                    "statusCode": "OK",
                },
                {
                    "indexDateString": "01-03-2024",
                    "value": "",  # Debe ignorarse limpiamente
                    "statusCode": "ND",
                },
            ],
        },
    }


def test_bcentral_resolve_indicator_codes() -> None:
    """Verifica la resolución de series a partir de códigos directos o slugs."""
    connector = BCentralChileConnector()

    # Todos los códigos por defecto
    all_codes = connector._resolve_indicator_codes(None)
    assert "F049.DES.TAS.HIST.10.M" in all_codes

    # Por slug de dominio
    resolved_slug = connector._resolve_indicator_codes(
        [IndicadorSlug.TASA_DESOCUPACION]
    )
    assert resolved_slug == ["F049.DES.TAS.HIST.10.M"]

    # Por código directo
    resolved_code = connector._resolve_indicator_codes(
        ["F032.IMC.IND.Z.Z.EP18.Z.Z.0.M"]
    )
    assert resolved_code == ["F032.IMC.IND.Z.Z.EP18.Z.Z.0.M"]


def test_bcentral_build_date_params() -> None:
    """Verifica la construcción y normalización de fechas firstdate y lastdate."""
    f1, l1 = BCentralChileConnector._build_date_params("2021", "2024")
    assert f1 == "2021-01-01"
    assert l1 == "2024-12-31"

    f2, l2 = BCentralChileConnector._build_date_params("2022-03-01", "2023-09-30")
    assert f2 == "2022-03-01"
    assert l2 == "2023-09-30"


@pytest.mark.asyncio
async def test_bcentral_check_health_ok() -> None:
    """Verifica que check_health retorne True ante respuesta con Codigo == 0."""
    payload = {"Codigo": 0, "Descripcion": "OK"}
    transport = MockBCentralTransport(status_code=200, payload=payload)
    async with httpx.AsyncClient(transport=transport) as client:
        connector = BCentralChileConnector(client=client)
        assert await connector.check_health() is True


@pytest.mark.asyncio
async def test_bcentral_check_health_fallo_credenciales_o_red() -> None:
    """Verifica que check_health retorne False ante error en SIETE o de red."""
    payload_error = {"Codigo": 1, "Descripcion": "Credenciales inválidas"}
    transport = MockBCentralTransport(status_code=200, payload=payload_error)
    async with httpx.AsyncClient(transport=transport) as client:
        connector = BCentralChileConnector(client=client)
        assert await connector.check_health() is False

    transport_500 = MockBCentralTransport(status_code=500, payload={})
    async with httpx.AsyncClient(transport=transport_500) as client:
        connector_500 = BCentralChileConnector(client=client)
        assert await connector_500.check_health() is False


@pytest.mark.asyncio
async def test_bcentral_fetch_indicators_pais_fuera_de_alcance() -> None:
    """Verifica que si se piden países que no incluyan Chile, retorne lista vacía."""
    connector = BCentralChileConnector()
    records = await connector.fetch_indicators(paises=["ARG", "URY"])
    assert records == []


@pytest.mark.asyncio
async def test_bcentral_fetch_indicators_contrato_y_parseo(
    sample_bcentral_series_response: dict[str, Any],
) -> None:
    """Verifica la extracción y contrato de dominio para registros de BCentral Chile."""
    transport = MockBCentralTransport(
        status_code=200, payload=sample_bcentral_series_response
    )
    async with httpx.AsyncClient(transport=transport) as client:
        connector = BCentralChileConnector(client=client)
        records = await connector.fetch_indicators(
            paises=["CHL"],
            indicadores=[IndicadorSlug.TASA_DESOCUPACION],
        )

    # 3 observaciones en el fixture: 2 válidas y 1 vacía que se descarta
    assert len(records) == 2

    for r in records:
        assert r.pais == PaisCodigo.CHL.value
        assert r.indicador == IndicadorSlug.TASA_DESOCUPACION
        assert r.tipo == TipoIndicador.OBSERVADO
        assert r.fuente == DEFAULT_BCENTRAL_CHILE_SOURCE
        assert r.periodo == "2024"
        assert r.metadatos["series_code"] == "F049.DES.TAS.HIST.10.M"

    assert records[0].valor == 8.4
    assert records[1].valor == 8.5
