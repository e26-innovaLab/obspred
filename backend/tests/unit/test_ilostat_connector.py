"""Pruebas unitarias para el conector de datos laborales ILOSTAT (OIT)."""

import httpx
import pytest

from app.core.constants import (
    DEFAULT_ILOSTAT_SOURCE,
    IndicadorSlug,
    PaisCodigo,
    TipoIndicador,
)
from app.infrastructure.connectors.ilostat_connector import ILOSTATConnector


class MockILOSTATTransport(httpx.AsyncBaseTransport):
    """Transporte mock para simular respuestas CSV de ILOSTAT API."""

    def __init__(
        self,
        status_code: int = 200,
        csv_text: str = "",
        raise_exception: Exception | None = None,
    ) -> None:
        self.status_code = status_code
        self.csv_text = csv_text
        self.raise_exception = raise_exception
        self.requests: list[httpx.Request] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.raise_exception:
            raise self.raise_exception

        return httpx.Response(
            status_code=self.status_code,
            text=self.csv_text,
            headers={"Content-Type": "text/csv; charset=utf-8"},
            request=request,
        )


@pytest.fixture
def sample_ilostat_csv() -> str:
    """Fixture con filas CSV representativas de ILOSTAT para desempleo."""
    # Fila 3 ignorada por sexo (sex!=SEX_T), fila 6 ignorada por obs_value vacío
    return (
        "ref_area,indicator,sex,classif1,time,obs_value,obs_status\n"
        "ARG,UNE_DEAP_SEX_AGE_RT_A,SEX_T,AGE_AGGREGATE_YGE15,2023,6.14,A\n"
        "ARG,UNE_DEAP_SEX_AGE_RT_A,SEX_F,AGE_AGGREGATE_YGE15,2023,7.50,A\n"
        "URY,UNE_DEAP_SEX_AGE_RT_A,SEX_T,AGE_AGGREGATE_YGE15,2023,8.05,A\n"
        "CHL,UNE_DEAP_SEX_AGE_RT_A,SEX_T,AGE_AGGREGATE_YGE15,2021,8.70,A\n"
        "CHL,UNE_DEAP_SEX_AGE_RT_A,SEX_T,AGE_AGGREGATE_YGE15,2024,8.30,A\n"
        "ARG,UNE_DEAP_SEX_AGE_RT_A,SEX_T,AGE_AGGREGATE_YGE15,2024,,ND\n"
    )


def test_ilostat_resolve_indicator_codes() -> None:
    """Verifica resolución de códigos desde slugs o directos."""
    connector = ILOSTATConnector()

    all_codes = connector._resolve_indicator_codes(None)
    assert "UNE_DEAP_SEX_AGE_RT_A" in all_codes

    by_slug = connector._resolve_indicator_codes([IndicadorSlug.TASA_DESEMPLEO])
    assert by_slug == ["UNE_DEAP_SEX_AGE_RT_A"]

    by_code = connector._resolve_indicator_codes(["EMP_TEMP_SEX_ECO_NB_A"])
    assert by_code == ["EMP_TEMP_SEX_ECO_NB_A"]


@pytest.mark.asyncio
async def test_ilostat_check_health_ok() -> None:
    """Verifica check_health cuando la respuesta contiene ref_area y status 200."""
    csv_ping = "ref_area,indicator,time,obs_value\nARG,UNE_DEAP_SEX_AGE_RT_A,2023,6.1\n"
    transport = MockILOSTATTransport(status_code=200, csv_text=csv_ping)
    async with httpx.AsyncClient(transport=transport) as client:
        connector = ILOSTATConnector(client=client)
        assert await connector.check_health() is True


@pytest.mark.asyncio
async def test_ilostat_check_health_fallo() -> None:
    """Verifica que check_health retorne False ante error 500 o red."""
    transport_err = MockILOSTATTransport(status_code=500, csv_text="Error interno")
    async with httpx.AsyncClient(transport=transport_err) as client:
        connector_err = ILOSTATConnector(client=client)
        assert await connector_err.check_health() is False

    transport_exc = MockILOSTATTransport(
        raise_exception=httpx.ConnectError("Connection refused")
    )
    async with httpx.AsyncClient(transport=transport_exc) as client:
        connector_exc = ILOSTATConnector(client=client)
        assert await connector_exc.check_health() is False


@pytest.mark.asyncio
async def test_ilostat_fetch_indicators_parseo_y_filtros(
    sample_ilostat_csv: str,
) -> None:
    """Verifica extracción, parseo CSV, filtros de sexo/edad y rango temporal."""
    transport = MockILOSTATTransport(status_code=200, csv_text=sample_ilostat_csv)
    async with httpx.AsyncClient(transport=transport) as client:
        connector = ILOSTATConnector(client=client)
        records = await connector.fetch_indicators(
            paises=[PaisCodigo.ARG, PaisCodigo.URY, PaisCodigo.CHL],
            indicadores=[IndicadorSlug.TASA_DESEMPLEO],
            periodo_desde="2022",
            periodo_hasta="2024",
        )

    # Deberían quedar: ARG 2023 (6.14), URY 2023 (8.05), CHL 2024 (8.30)
    # CHL 2021 queda filtrado por periodo_desde="2022"
    # SEX_F queda filtrado
    # obs_value vacío queda filtrado
    assert len(records) == 3

    for r in records:
        assert r.tipo == TipoIndicador.OBSERVADO
        assert r.fuente == DEFAULT_ILOSTAT_SOURCE
        assert r.indicador == IndicadorSlug.TASA_DESEMPLEO

    arg_rec = next(r for r in records if r.pais == "ARG")
    assert arg_rec.valor == 6.14
    assert arg_rec.periodo == "2023"

    ury_rec = next(r for r in records if r.pais == "URY")
    assert ury_rec.valor == 8.05

    chl_rec = next(r for r in records if r.pais == "CHL")
    assert chl_rec.valor == 8.30
    assert chl_rec.periodo == "2024"
