"""Pruebas unitarias para el conector oficial de CEPALSTAT API."""

from datetime import date
from typing import Any

import httpx
import pytest

from app.domain.interfaces.external_connector import RawIndicatorRecord
from app.infrastructure.connectors.cepalstat_connector import CepalstatConnector


@pytest.fixture
def sample_cepalstat_payload() -> dict[str, Any]:
    """Fixture con una respuesta representativa de CEPALSTAT API v1."""
    return {
        "header": {
            "status": 200,
            "message": "SUCCESS",
            "lang": "es",
        },
        "body": {
            "indicator": {
                "id": 2222,
                "code": "SL_TLF_UEM",
                "name": "Tasa de desocupación abierta",
            },
            "dimensions": [
                {
                    "id": "country",
                    "name": "País",
                    "values": [
                        {"id": "13", "name": "Argentina", "iso3": "ARG"},
                        {"id": "858", "name": "Uruguay", "iso3": "URY"},
                        {"id": "152", "name": "Chile", "iso3": "CHL"},
                        {"id": "076", "name": "Brasil", "iso3": "BRA"},
                    ],
                },
                {
                    "id": "year",
                    "name": "Año",
                    "values": [
                        {"id": "2021", "name": "2021"},
                        {"id": "2022", "name": "2022"},
                        {"id": "2023", "name": "2023"},
                    ],
                },
            ],
            "data": [
                {
                    "valor": 6.8,
                    "dimensions": {
                        "country": "13",
                        "year": "2022",
                    },
                },
                {
                    "valor": 7.9,
                    "dimensions": {
                        "country": "858",
                        "year": "2022",
                    },
                },
                {
                    "valor": 8.1,
                    "dimensions": {
                        "country": "CHL",
                        "year": "2022",
                    },
                },
                {
                    "valor": 9.2,
                    "dimensions": {
                        "country": "BRA",  # Fuera de alcance del Observatorio
                        "year": "2022",
                    },
                },
                {
                    "valor": None,  # Observación nula: debe descartarse limpiamente
                    "dimensions": {
                        "country": "ARG",
                        "year": "2023",
                    },
                },
            ],
        },
    }


def test_cepalstat_source_name_and_id() -> None:
    """Verifica denominación oficial e identificador del conector."""
    connector = CepalstatConnector()
    assert connector.source_name == "CEPALSTAT"
    assert connector.source_id == "cepalstat"


def test_cepalstat_configurable_base_url_and_timeout() -> None:
    """Verifica que la URL base y el timeout se configuren adecuadamente."""
    connector = CepalstatConnector(
        base_url="https://mock-cepal.org/api/v1/",
        timeout=15.0,
    )
    assert connector.base_url == "https://mock-cepal.org/api/v1"
    assert connector.timeout == 15.0


def test_cepalstat_resolve_indicator_codes() -> None:
    """Verifica la resolución de slugs canónicos y códigos oficiales de CEPALSTAT."""
    connector = CepalstatConnector()

    # Por defecto
    default_codes = connector._resolve_indicator_codes(None)
    assert "SL_TLF_UEM" in default_codes
    assert "NY_GDP_PCAP_CD" in default_codes

    # Por slug
    resolved_slug = connector._resolve_indicator_codes(["tasa_desempleo"])
    assert resolved_slug == ["SL_TLF_UEM"]

    # Por código directo
    resolved_code = connector._resolve_indicator_codes(["SE_ENR_TERT"])
    assert resolved_code == ["SE_ENR_TERT"]

    # Por alias numérico
    resolved_numeric = connector._resolve_indicator_codes(["2222"])
    assert resolved_numeric == ["2222"]


def test_cepalstat_normalize_country_code() -> None:
    """Verifica normalización de nombres y códigos al formato ISO 3166-1 alpha-3."""
    connector = CepalstatConnector()

    assert connector._normalize_country_code("Argentina") == "ARG"
    assert connector._normalize_country_code("ARG") == "ARG"
    assert connector._normalize_country_code("13") == "ARG"
    assert connector._normalize_country_code("Uruguay") == "URY"
    assert connector._normalize_country_code("858") == "URY"
    assert connector._normalize_country_code("Chile") == "CHL"
    assert connector._normalize_country_code("152") == "CHL"
    assert connector._normalize_country_code("Colombia") is None


@pytest.mark.asyncio
async def test_cepalstat_check_health_exitoso() -> None:
    """Verifica check_health positivo cuando la API responde 200 OK con JSON válido."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"thematic_tree": []})
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    healthy = await connector.check_health()
    assert healthy is True


@pytest.mark.asyncio
async def test_cepalstat_check_health_fallido() -> None:
    """Verifica check_health negativo cuando la API responde error de servidor."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(500, json={"error": "Internal Error"})
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    healthy = await connector.check_health()
    assert healthy is False


@pytest.mark.asyncio
async def test_cepalstat_fetch_indicators_exitoso(
    sample_cepalstat_payload: dict[str, Any],
) -> None:
    """Verifica extracción, normalización y exclusión de nulos y otros países."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_cepalstat_payload)
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    records: list[RawIndicatorRecord] = await connector.fetch_indicators(
        paises=["ARG", "URY", "CHL"],
        indicadores=["tasa_desempleo"],
    )

    # De los 5 items:
    # - ARG 2022 (valor 6.8): VÁLIDO
    # - URY 2022 (valor 7.9): VÁLIDO
    # - CHL 2022 (valor 8.1): VÁLIDO
    # - BRA 2022: Omitido (no está en target_countries)
    # - ARG 2023: Omitido (valor None)
    assert len(records) == 3

    paises_obtenidos = {r.pais for r in records}
    assert paises_obtenidos == {"ARG", "URY", "CHL"}

    rec_arg = next(r for r in records if r.pais == "ARG")
    assert rec_arg.indicador == "tasa_desempleo"
    assert rec_arg.periodo == "2022"
    assert rec_arg.valor == 6.8
    assert rec_arg.tipo == "observado"
    assert rec_arg.fuente == "CEPALSTAT"
    assert rec_arg.fecha_actualizacion == date.today()
    assert rec_arg.metadatos["cepalstat_code"] == "SL_TLF_UEM"


@pytest.mark.asyncio
async def test_cepalstat_fetch_indicators_with_date_filters(
    sample_cepalstat_payload: dict[str, Any],
) -> None:
    """Verifica filtrado por rango temporal periodo_desde y periodo_hasta."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=sample_cepalstat_payload)
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    # Filtrar solo año 2025 (no coincide ninguno)
    empty_records = await connector.fetch_indicators(
        indicadores=["tasa_desempleo"],
        periodo_desde="2025",
        periodo_hasta="2026",
    )
    assert len(empty_records) == 0

    # Filtrar coincidiendo con 2022
    records_2022 = await connector.fetch_indicators(
        indicadores=["tasa_desempleo"],
        periodo_desde="2022",
        periodo_hasta="2022",
    )
    assert len(records_2022) == 3


@pytest.mark.asyncio
async def test_cepalstat_fetch_indicators_network_error() -> None:
    """Verifica manejo defensivo ante timeout de red sin lanzar excepciones."""

    def raise_timeout(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Timeout simulado en CEPALSTAT", request=req)

    mock_transport = httpx.MockTransport(raise_timeout)
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    records = await connector.fetch_indicators(
        indicadores=["tasa_desempleo"],
    )
    assert records == []
