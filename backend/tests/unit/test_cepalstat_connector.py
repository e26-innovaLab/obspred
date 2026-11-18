"""Pruebas unitarias completas para el conector de CEPALSTAT API."""

from datetime import date
from typing import Any

import httpx
import pytest

from app.domain.interfaces.external_connector import RawIndicatorRecord
from app.infrastructure.connectors.cepalstat_connector import CepalstatConnector


@pytest.fixture
def real_cepalstat_snapshot_payload() -> dict[str, Any]:
    """Snapshot fiel al esquema real de CEPALSTAT (basado en indicador 127)."""
    return {
        "header": {
            "status": 200,
            "message": "SUCCESS",
            "lang": "es",
        },
        "body": {
            "metadata": {
                "indicator_id": 127,
                "indicator_name": "Tasa de desocupación por sexo",
                "theme": "Estadísticas e Indicadores Sociales",
                "area": "Desocupación",
                "unit": "Tasa anual media",
                "definition": "Población desocupada como % de la población activa.",
                "calculation_methodology": "Porcentaje de desocupados sobre PEA.",
                "decimals": 1,
                "last_update": "Dec 19 2025  1:14PM",
            },
            "dimensions": [
                {
                    "id": 144,
                    "name": "Sexo__ESTANDAR",
                    "members": [
                        {"id": 146, "name": "Ambos sexos"},
                        {"id": 265, "name": "Hombres"},
                        {"id": 266, "name": "Mujeres"},
                    ],
                },
                {
                    "id": 29117,
                    "name": "Años__ESTANDAR",
                    "members": [
                        {"id": 29180, "name": "2022"},
                        {"id": 29181, "name": "2023"},
                        {"id": 29182, "name": "2024"},
                    ],
                },
                {
                    "id": 208,
                    "name": "País__ESTANDAR",
                    "members": [
                        {"id": 216, "name": "Argentina"},
                        {"id": 224, "name": "Chile"},
                        {"id": 258, "name": "Uruguay"},
                        {"id": 218, "name": "Brasil"},
                    ],
                },
            ],
            "data": [
                # Argentina 2022 - Ambos sexos (VÁLIDO)
                {
                    "value": "6.8",
                    "source_id": 36,
                    "notes_ids": "15084,15090",
                    "iso3": "ARG",
                    "dim_208": 216,
                    "dim_144": 146,
                    "dim_29117": 29180,
                },
                # Argentina 2022 - Hombres (Descartado para no duplicar tasa nacional)
                {
                    "value": "7.5",
                    "source_id": 36,
                    "iso3": "ARG",
                    "dim_208": 216,
                    "dim_144": 265,
                    "dim_29117": 29180,
                },
                # Uruguay 2022 - Ambos sexos, iso3 en None con dim_208 presente (VÁLIDO)
                {
                    "value": "7.9",
                    "source_id": 36,
                    "iso3": None,
                    "dim_208": 258,
                    "dim_144": 146,
                    "dim_29117": 29180,
                },
                # Chile 2022 - Ambos sexos (VÁLIDO)
                {
                    "value": "8.1",
                    "source_id": 36,
                    "iso3": "CHL",
                    "dim_208": 224,
                    "dim_144": 146,
                    "dim_29117": 29180,
                },
                # Brasil 2022 - Fuera de alcance (Debe descartarse)
                {
                    "value": "9.2",
                    "source_id": 36,
                    "iso3": "BRA",
                    "dim_208": 218,
                    "dim_144": 146,
                    "dim_29117": 29180,
                },
                # Argentina 2023 - Valor nulo / guion (Debe descartarse limpiamente)
                {
                    "value": "-",
                    "source_id": 36,
                    "iso3": "ARG",
                    "dim_208": 216,
                    "dim_144": 146,
                    "dim_29117": 29181,
                },
                # Chile 2024 - Ambos sexos (VÁLIDO)
                {
                    "value": "8.3",
                    "source_id": 36,
                    "iso3": "CHL",
                    "dim_208": 224,
                    "dim_144": 146,
                    "dim_29117": 29182,
                },
            ],
        },
    }


@pytest.fixture
def real_quarterly_snapshot_payload() -> dict[str, Any]:
    """Snapshot con dimensiones trimestrales reales (basado en indicador 2182)."""
    return {
        "header": {"status": 200, "message": "SUCCESS"},
        "body": {
            "metadata": {
                "indicator_id": 2182,
                "indicator_name": "Tasa de desocupación trimestral",
                "last_update": "2025-10-15",
            },
            "dimensions": [
                {
                    "id": 208,
                    "name": "País__ESTANDAR",
                    "members": [{"id": 216, "name": "Argentina"}],
                },
                {
                    "id": 26677,
                    "name": "Trimestre",
                    "members": [
                        {"id": 26681, "name": "T1"},
                        {"id": 26680, "name": "T2"},
                    ],
                },
                {
                    "id": 29117,
                    "name": "Años__ESTANDAR",
                    "members": [{"id": 29182, "name": "2024"}],
                },
            ],
            "data": [
                {
                    "value": "7.1",
                    "iso3": "ARG",
                    "dim_208": 216,
                    "dim_26677": 26681,
                    "dim_29117": 29182,
                },
                {
                    "value": "7.6",
                    "iso3": "ARG",
                    "dim_208": 216,
                    "dim_26677": 26680,
                    "dim_29117": 29182,
                },
            ],
        },
    }


def test_cepalstat_source_name_and_id() -> None:
    """Verifica denominación oficial e identificador del conector."""
    connector = CepalstatConnector()
    assert connector.source_name == "CEPALSTAT"
    assert connector.source_id == "cepalstat"


def test_cepalstat_verified_indicator_ids() -> None:
    """Verifica que el catálogo use IDs reales verificados y excluya IDs falsos."""
    connector = CepalstatConnector()
    verified_ids = set(connector.INDICATOR_MAPPINGS.keys())

    # Debe contener los IDs reales verificados
    assert "127" in verified_ids
    assert "2182" in verified_ids
    assert "2470" in verified_ids
    assert "2205" in verified_ids
    assert "99" in verified_ids

    # NO debe contener códigos genéricos ni alias erróneos
    assert "SL_TLF_UEM" not in verified_ids
    assert "NY_GDP_PCAP_CD" not in verified_ids
    assert "2222" not in verified_ids  # 2222 era crecimiento del PIB, no desempleo
    assert "2221" not in verified_ids  # 2221 era PIB por actividad


def test_cepalstat_resolve_indicator_codes() -> None:
    """Verifica resolución correcta de slugs a IDs numéricos reales."""
    connector = CepalstatConnector()

    # Por defecto debe retornar los IDs principales verificados
    default_ids = connector._resolve_indicator_codes(None)
    assert default_ids == ["127", "2470", "2205", "99"]

    # Resolución por slug
    assert connector._resolve_indicator_codes(["tasa_desempleo"]) == ["127"]
    assert connector._resolve_indicator_codes(["tasa_desempleo_trimestral"]) == ["2182"]
    assert connector._resolve_indicator_codes(["pib_per_capita"]) == ["2205"]
    assert connector._resolve_indicator_codes(["participacion_laboral"]) == ["2470"]
    assert connector._resolve_indicator_codes(["matricula_terciaria"]) == ["99"]

    # Indicador inexistente debe ser ignorado limpiamente sin romper
    assert connector._resolve_indicator_codes(["indicador_inexistente"]) == []


def test_cepalstat_normalize_country_code() -> None:
    """Verifica normalización exhaustiva con nombres, códigos ISO e IDs de CEPALSTAT."""
    connector = CepalstatConnector()

    # Argentina
    assert connector._normalize_country_code("Argentina") == "ARG"
    assert connector._normalize_country_code("argentina") == "ARG"
    assert connector._normalize_country_code("arg") == "ARG"
    assert connector._normalize_country_code("13") == "ARG"
    assert connector._normalize_country_code("216") == "ARG"

    # Uruguay
    assert connector._normalize_country_code("Uruguay") == "URY"
    assert connector._normalize_country_code("uy") == "URY"
    assert connector._normalize_country_code("858") == "URY"
    assert connector._normalize_country_code("258") == "URY"

    # Chile
    assert connector._normalize_country_code("Chile") == "CHL"
    assert connector._normalize_country_code("cl") == "CHL"
    assert connector._normalize_country_code("152") == "CHL"
    assert connector._normalize_country_code("224") == "CHL"

    # Fuera de alcance
    assert connector._normalize_country_code("Colombia") is None
    assert connector._normalize_country_code(None) is None


def test_cepalstat_parse_update_date() -> None:
    """Verifica extracción y parseo de fecha real de corte según Principio 3."""
    # Formato nativo de CEPALSTAT: 'Dec 19 2025  1:14PM'
    d1 = CepalstatConnector._parse_update_date("Dec 19 2025  1:14PM")
    assert d1 == date(2025, 12, 19)

    # Formato ISO: '2025-10-15'
    d2 = CepalstatConnector._parse_update_date("2025-10-15")
    assert d2 == date(2025, 10, 15)

    # Formato común: '15/10/2025'
    d3 = CepalstatConnector._parse_update_date("15/10/2025")
    assert d3 == date(2025, 10, 15)

    # Invalido o None hace fallback controlado
    assert isinstance(CepalstatConnector._parse_update_date(None), date)
    assert isinstance(CepalstatConnector._parse_update_date("invalido"), date)


def test_cepalstat_period_in_range_logic() -> None:
    """Verifica comparación de períodos temporales sin fallas de orden de cadenas."""
    # Rango anual
    assert CepalstatConnector._is_period_in_range("2022", "2020", "2024") is True
    assert CepalstatConnector._is_period_in_range("2019", "2020", "2024") is False
    assert CepalstatConnector._is_period_in_range("2025", "2020", "2024") is False

    # Registro trimestral con límite anual
    assert CepalstatConnector._is_period_in_range("2024-Q1", "2024", "2024") is True
    assert CepalstatConnector._is_period_in_range("2024-Q4", "2024", "2024") is True
    assert CepalstatConnector._is_period_in_range("2023-Q4", "2024", "2024") is False

    # Registro trimestral con límite trimestral específico
    assert (
        CepalstatConnector._is_period_in_range("2024-Q2", "2024-Q1", "2024-Q3")
        is True
    )
    assert (
        CepalstatConnector._is_period_in_range("2024-Q4", "2024-Q1", "2024-Q3")
        is False
    )


@pytest.mark.asyncio
async def test_cepalstat_check_health_exitoso() -> None:
    """Verifica que check_health use la ruta ligera de metadata del indicador 127."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json={"header": {}, "body": {}})
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    healthy = await connector.check_health()
    assert healthy is True


@pytest.mark.asyncio
async def test_cepalstat_fetch_indicators_with_real_snapshot(
    real_cepalstat_snapshot_payload: dict[str, Any],
) -> None:
    """Verifica extracción, fecha real de actualización y metadatos."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=real_cepalstat_snapshot_payload)
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    records: list[RawIndicatorRecord] = await connector.fetch_indicators(
        paises=["argentina", "ury", "152"],  # Mezcla de nombres, códigos e IDs
        indicadores=["tasa_desempleo"],
    )

    # De los 7 items:
    # 1. ARG 2022 Ambos sexos -> VÁLIDO
    # 2. ARG 2022 Hombres -> Descartado (sexo != ambos sexos)
    # 3. URY 2022 Ambos sexos (iso3 None, dim_208: 258) -> VÁLIDO
    # 4. CHL 2022 Ambos sexos -> VÁLIDO
    # 5. BRA 2022 -> Descartado (fuera de target_countries)
    # 6. ARG 2023 Valor '-' -> Descartado
    # 7. CHL 2024 Ambos sexos -> VÁLIDO
    assert len(records) == 4

    paises_obtenidos = {r.pais for r in records}
    assert paises_obtenidos == {"ARG", "URY", "CHL"}

    # Trazabilidad de fecha real de corte
    rec_arg = next(r for r in records if r.pais == "ARG")
    assert rec_arg.fecha_actualizacion == date(2025, 12, 19)
    assert rec_arg.valor == 6.8
    assert rec_arg.periodo == "2022"
    assert rec_arg.trimestre is None
    assert rec_arg.fuente == "CEPALSTAT"
    assert rec_arg.metadatos["cepalstat_indicator_id"] == "127"
    assert rec_arg.metadatos["unit"] == "Tasa anual media"
    assert rec_arg.detalles["decimals"] == 1


@pytest.mark.asyncio
async def test_cepalstat_fetch_quarterly_indicator(
    real_quarterly_snapshot_payload: dict[str, Any],
) -> None:
    """Verifica resolución dinámica de dimensiones trimestrales T1/T2 -> Q1/Q2."""
    mock_transport = httpx.MockTransport(
        lambda req: httpx.Response(200, json=real_quarterly_snapshot_payload)
    )
    client = httpx.AsyncClient(transport=mock_transport)
    connector = CepalstatConnector(client=client)

    records = await connector.fetch_indicators(
        indicadores=["tasa_desempleo_trimestral"],
    )

    assert len(records) == 2
    rec1 = records[0]
    assert rec1.periodo == "2024-Q1"
    assert rec1.trimestre == "Q1"
    assert rec1.valor == 7.1

    rec2 = records[1]
    assert rec2.periodo == "2024-Q2"
    assert rec2.trimestre == "Q2"
    assert rec2.valor == 7.6


@pytest.mark.asyncio
async def test_cepalstat_negative_cases() -> None:
    """Verifica manejo defensivo ante 404, 400, HTML no JSON y timeout sin quebrar."""
    # 1. 404 Not Found
    trans_404 = httpx.MockTransport(lambda r: httpx.Response(404, text="Not Found"))
    c1 = CepalstatConnector(client=httpx.AsyncClient(transport=trans_404))
    assert await c1.fetch_indicators(indicadores=["127"]) == []

    # 2. 400 Bad Request
    trans_400 = httpx.MockTransport(lambda r: httpx.Response(400, text="Bad Request"))
    c2 = CepalstatConnector(client=httpx.AsyncClient(transport=trans_400))
    assert await c2.fetch_indicators(indicadores=["127"]) == []

    # 3. HTML / Error 502 no JSON (JSONDecodeError capturado)
    trans_html = httpx.MockTransport(
        lambda r: httpx.Response(
            502,
            headers={"Content-Type": "text/html"},
            text="<html>Bad Gateway</html>",
        )
    )
    c3 = CepalstatConnector(client=httpx.AsyncClient(transport=trans_html))
    assert await c3.fetch_indicators(indicadores=["127"]) == []

    # 4. Timeout de red
    def raise_timeout(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Timeout en CEPALSTAT", request=req)

    trans_to = httpx.MockTransport(raise_timeout)
    c4 = CepalstatConnector(client=httpx.AsyncClient(transport=trans_to))
    assert await c4.fetch_indicators(indicadores=["127"]) == []
