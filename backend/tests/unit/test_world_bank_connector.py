"""Pruebas unitarias para el conector de World Bank Indicators API."""

from datetime import date
from typing import Any

import httpx
import pytest

from app.domain.interfaces.external_connector import RawIndicatorRecord
from app.infrastructure.connectors.world_bank_connector import (
    WorldBankConnector,
)


class MockTransport(httpx.AsyncBaseTransport):
    """Transporte mock para simular respuestas HTTP de World Bank API."""

    def __init__(
        self,
        status_code: int = 200,
        payload: Any = None,
        raise_timeout: bool = False,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.raise_timeout = raise_timeout
        self.request_count = 0

    async def handle_async_request(
        self, request: httpx.Request
    ) -> httpx.Response:
        self.request_count += 1
        if self.raise_timeout:
            raise httpx.ReadTimeout("Timeout simulado", request=request)

        import json

        content = json.dumps(self.payload).encode("utf-8")
        return httpx.Response(
            status_code=self.status_code,
            content=content,
            headers={"Content-Type": "application/json"},
            request=request,
        )


@pytest.fixture
def sample_world_bank_response() -> list[Any]:
    """Fixture con respuesta representativa de World Bank Indicators API."""
    header = [
        {
            "page": 1,
            "pages": 1,
            "per_page": 1000,
            "total": 3,
            "sourceid": "2",
            "sourcename": "World Development Indicators",
            "lastupdated": "2024-03-28",
        }
    ]
    data = [
        {
            "indicator": {
                "id": "SL.UEM.TOTL.ZS",
                "value": "Unemployment, total (% of total labor force)",
            },
            "country": {"id": "AR", "value": "Argentina"},
            "countryiso3code": "ARG",
            "date": "2023",
            "value": 6.14,
            "unit": "",
            "obs_status": "",
            "decimal": 0,
        },
        {
            "indicator": {
                "id": "SL.UEM.TOTL.ZS",
                "value": "Unemployment, total (% of total labor force)",
            },
            "country": {"id": "UY", "value": "Uruguay"},
            "countryiso3code": "URY",
            "date": "2023",
            "value": 8.05,
            "unit": "",
            "obs_status": "",
            "decimal": 0,
        },
        {
            "indicator": {
                "id": "SL.UEM.TOTL.ZS",
                "value": "Unemployment, total (% of total labor force)",
            },
            "country": {"id": "CL", "value": "Chile"},
            "countryiso3code": "CHL",
            "date": "2023",
            "value": None,  # Debe ser descartado por valor nulo
            "unit": "",
            "obs_status": "",
            "decimal": 0,
        },
    ]
    return [header[0], data]


@pytest.mark.asyncio
async def test_world_bank_source_name() -> None:
    """Verifica que el nombre de la fuente corresponda a la denominación oficial."""
    connector = WorldBankConnector()
    assert connector.source_name == "World Bank"


@pytest.mark.asyncio
async def test_world_bank_configurable_base_url_and_timeout() -> None:
    """Verifica que la URL base y el timeout sean configurables."""
    connector = WorldBankConnector(
        base_url="https://mock-wb.example.com/api/",
        timeout=12.5,
    )
    assert connector.base_url == "https://mock-wb.example.com/api"
    assert connector.timeout == 12.5



@pytest.mark.asyncio
async def test_world_bank_resolve_indicator_codes() -> None:
    """Verifica la resolución tanto de códigos directos como de slugs amigables."""
    connector = WorldBankConnector()

    # Todos los códigos por defecto
    all_codes = connector._resolve_indicator_codes(None)
    assert "SL.UEM.TOTL.ZS" in all_codes

    # Resolución por slug
    resolved_by_slug = connector._resolve_indicator_codes(["tasa_desempleo"])
    assert resolved_by_slug == ["SL.UEM.TOTL.ZS"]

    # Resolución por código
    resolved_by_code = connector._resolve_indicator_codes(["NY.GDP.PCAP.CD"])
    assert resolved_by_code == ["NY.GDP.PCAP.CD"]


def test_world_bank_build_date_param() -> None:
    """Verifica la construcción del parámetro de rango temporal."""
    assert WorldBankConnector._build_date_param("2020", "2023") == "2020:2023"
    assert "2020:" in WorldBankConnector._build_date_param("2020", None)
    assert WorldBankConnector._build_date_param(None, "2024") == "2010:2024"
    assert WorldBankConnector._build_date_param(None, None) == "2015:2024"


def test_world_bank_parse_update_date() -> None:
    """Verifica el parseo de fecha ISO o fallback a fecha actual."""
    d = WorldBankConnector._parse_update_date("2024-03-28")
    assert d == date(2024, 3, 28)

    fallback_d = WorldBankConnector._parse_update_date("invalida")
    assert fallback_d == date.today()

    none_d = WorldBankConnector._parse_update_date(None)
    assert none_d == date.today()


@pytest.mark.asyncio
async def test_world_bank_check_health_exitoso() -> None:
    """Verifica que check_health devuelva True ante respuesta 200 con payload válido."""
    transport = MockTransport(status_code=200, payload=[{"page": 1}, []])
    client = httpx.AsyncClient(transport=transport)
    connector = WorldBankConnector(client=client)

    healthy = await connector.check_health()
    assert healthy is True


@pytest.mark.asyncio
async def test_world_bank_check_health_fallido() -> None:
    """Verifica que check_health devuelva False si el endpoint falla."""
    transport = MockTransport(status_code=500, payload={"error": "server error"})
    client = httpx.AsyncClient(transport=transport)
    connector = WorldBankConnector(client=client)

    healthy = await connector.check_health()
    assert healthy is False


@pytest.mark.asyncio
async def test_world_bank_fetch_indicators_exitoso(
    sample_world_bank_response: list[dict[str, Any]],
) -> None:
    """Verifica la extracción, filtrado de nulos y normalización de registros."""
    transport = MockTransport(status_code=200, payload=sample_world_bank_response)
    client = httpx.AsyncClient(transport=transport)
    connector = WorldBankConnector(client=client)

    records: list[RawIndicatorRecord] = await connector.fetch_indicators(
        paises=["ARG", "URY", "CHL"],
        indicadores=["tasa_desempleo"],
        periodo_desde="2023",
        periodo_hasta="2023",
    )

    # 3 items en payload, 1 era nulo -> quedan 2 válidos (ARG y URY)
    assert len(records) == 2

    rec_arg = next(r for r in records if r.pais == "ARG")
    assert rec_arg.indicador == "tasa_desempleo"
    assert rec_arg.periodo == "2023"
    assert rec_arg.valor == 6.14
    assert rec_arg.tipo == "observado"
    assert rec_arg.fuente == "World Bank"
    assert rec_arg.fecha_actualizacion == date(2024, 3, 28)
    assert rec_arg.metadatos["world_bank_code"] == "SL.UEM.TOTL.ZS"

    rec_ury = next(r for r in records if r.pais == "URY")
    assert rec_ury.valor == 8.05


@pytest.mark.asyncio
async def test_world_bank_fetch_indicators_error_red() -> None:
    """Verifica manejo resiliente ante error de timeout de red sin quebrar."""
    transport = MockTransport(raise_timeout=True)
    client = httpx.AsyncClient(transport=transport)
    connector = WorldBankConnector(client=client)

    records = await connector.fetch_indicators(
        indicadores=["tasa_desempleo"],
    )
    # Devuelve lista vacía y no propaga excepción no controlada
    assert records == []
