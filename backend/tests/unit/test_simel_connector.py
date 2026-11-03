"""Pruebas unitarias para el conector de SIMEL Chile y su parser de CSV."""

import httpx
import pytest

from app.core.constants import (
    DEFAULT_SIMEL_CHILE_SOURCE,
    PaisCodigo,
    SectorEstrategico,
    TipoIndicador,
)
from app.domain.exceptions.simel_exceptions import (
    InvalidSimelCsvException,
    SimelWafBlockedException,
)
from app.infrastructure.connectors.simel_chile_connector import (
    SimelChileConnector,
)


@pytest.fixture
def sample_simel_csv() -> str:
    """Genera contenido CSV de prueba con formato de SIMEL Chile."""
    return (
        "Periodo,Indicador,Rama_Actividad,Grupo_Ocupacional,Sexo,Unidad_Medida,Valor\n"
        "Ene - Mar 2024,Tasa de desocupación,Total,Total,Total,Porcentaje,8.7\n"
        "Ene - Mar 2024,Ocupados según rama,Información y comunicaciones,"
        "P,T,M,184.2\n"
        "Ene - Mar 2024,Ocupados según rama,"
        "Actividades de atención de la salud humana,T,T,M,495.8\n"
        "Ene - Mar 2024,Ocupados según rama,Suministro de electricidad,"
        "T,T,M,68.4\n"
        "Ene - Mar 2024,Ocupados según rama,"
        "Actividades de alojamiento y de servicio de comidas,S,T,M,428.1\n"
        "Ene - Mar 2024,Ocupados según rama,"
        "Actividades profesionales científicas y técnicas,P,T,M,315.6\n"
        "Abr - Jun 2024,Tasa de ocupación,Total,Total,Total,Porcentaje,56.8\n"
    )


def test_connector_initialization_and_properties() -> None:
    """Verifica la inicialización de atributos y denominación de la fuente."""
    connector = SimelChileConnector()
    assert connector.source_name == DEFAULT_SIMEL_CHILE_SOURCE
    assert "simel.gob.cl" in connector.base_url
    assert connector.timeout > 0


@pytest.mark.asyncio
async def test_check_health_success() -> None:
    """Verifica que check_health retorne True ante un código HTTP 200 sin WAF."""
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(200, text="OK"))
    async with httpx.AsyncClient(transport=mock_transport) as client:
        connector = SimelChileConnector(client=client)
        result = await connector.check_health()
        assert result is True


@pytest.mark.asyncio
async def test_check_health_detects_huawei_waf_418() -> None:
    """Verifica detección de bloqueo HTTP 418 del WAF de Huawei Cloud."""
    mock_transport = httpx.MockTransport(
        lambda request: httpx.Response(
            418,
            headers={"Server": "CW", "block-event-id": "32-nil"},
            text="WAF Block",
        )
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        connector = SimelChileConnector(client=client)
        result = await connector.check_health()
        assert result is False


@pytest.mark.asyncio
async def test_check_health_connection_error() -> None:
    """Verifica que check_health maneje errores de red retornando False."""

    def raise_error(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Network unreachable")

    mock_transport = httpx.MockTransport(raise_error)
    async with httpx.AsyncClient(transport=mock_transport) as client:
        connector = SimelChileConnector(client=client)
        result = await connector.check_health()
        assert result is False


@pytest.mark.asyncio
async def test_fetch_indicators_raises_simel_waf_blocked_exception() -> None:
    """Verifica que fetch_indicators lance SimelWafBlockedException ante WAF."""
    mock_transport = httpx.MockTransport(
        lambda request: httpx.Response(
            418,
            headers={"Server": "CW"},
            text="WAF Block",
        )
    )
    async with httpx.AsyncClient(transport=mock_transport) as client:
        connector = SimelChileConnector(client=client)
        with pytest.raises(SimelWafBlockedException) as exc_info:
            await connector.fetch_indicators(paises=["CHL"])
        assert "Huawei Cloud" in str(exc_info.value)
        assert "418" in str(exc_info.value)


def test_parse_simel_csv_success(sample_simel_csv: str) -> None:
    """Verifica la correcta transformación y normalización de un CSV de SIMEL."""
    connector = SimelChileConnector()
    records = connector.parse_simel_csv(sample_simel_csv, filename="test.csv")

    assert len(records) == 7

    desempleo = records[0]
    assert desempleo.pais == PaisCodigo.CHL
    assert desempleo.indicador == "tasa_desempleo"
    assert desempleo.periodo == "2024-Q1"
    assert desempleo.valor == 8.7
    assert desempleo.tipo == TipoIndicador.OBSERVADO
    assert desempleo.fuente == DEFAULT_SIMEL_CHILE_SOURCE
    assert desempleo.sector is None  # Total mapea a None

    # Verificación de sectores estratégicos mapeados
    sectores_esperados = {
        SectorEstrategico.TECNOLOGIA,
        SectorEstrategico.SALUD,
        SectorEstrategico.ENERGIA,
        SectorEstrategico.TURISMO,
        SectorEstrategico.ECONOMIA_CONOCIMIENTO,
    }
    sectores_obtenidos = {r.sector for r in records if r.sector is not None}
    assert sectores_esperados.issubset(sectores_obtenidos)


def test_parse_simel_csv_semicolon_and_latin1_encoding() -> None:
    """Verifica soporte para punto y coma y codificación Latin-1 / CP1252."""
    connector = SimelChileConnector()
    csv_latin1 = (
        "Trimestre;Variable;Rama_Actividad;Cifra\n"
        "Ene - Mar 2024;Tasa de desocupación;Información y comunicaciones;7,4\n"
    ).encode("latin-1")

    records = connector.parse_simel_csv(csv_latin1, filename="export_latin1.csv")
    assert len(records) == 1
    rec = records[0]
    assert rec.valor == 7.4
    assert rec.periodo == "2024-Q1"
    assert rec.sector == SectorEstrategico.TECNOLOGIA


def test_parse_simel_csv_empty_raises_exception() -> None:
    """Verifica que un archivo vacío lance InvalidSimelCsvException."""
    connector = SimelChileConnector()
    with pytest.raises(InvalidSimelCsvException) as exc_info:
        connector.parse_simel_csv("", filename="vacio.csv")
    assert "vacío" in str(exc_info.value).lower()


def test_parse_simel_csv_missing_columns_raises_exception() -> None:
    """Verifica que un CSV sin columnas lance InvalidSimelCsvException."""
    connector = SimelChileConnector()
    csv_invalido = "ColumnaA,ColumnaB\n1,2\n"
    with pytest.raises(InvalidSimelCsvException) as exc_info:
        connector.parse_simel_csv(csv_invalido, filename="sin_columnas.csv")
    assert "Faltan columnas" in str(exc_info.value)
