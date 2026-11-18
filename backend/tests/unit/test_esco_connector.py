"""Pruebas unitarias para el conector de taxonomías ESCO (Comisión Europea)."""

import json
from typing import Any

import httpx
import pytest

from app.core.constants import (
    DEFAULT_ESCO_SOURCE,
    DEFAULT_HTTP_USER_AGENT,
    TipoIndicador,
)
from app.infrastructure.connectors.esco_connector import EscoConnector


class MockEscoTransport(httpx.AsyncBaseTransport):
    """Transporte HTTP mock para simular respuestas de la API de ESCO."""

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
def sample_esco_response() -> dict[str, Any]:
    """Fixture con respuesta representativa de búsqueda en ESCO."""
    return {
        "_embedded": {
            "results": [
                {
                    "title": "desarrollador de software / desarrolladora de software",
                    "uri": "http://data.europa.eu/esco/occupation/52c6f140-5e36-4d0f",
                    "status": "released",
                },
                {
                    "title": "ingeniero de software / ingeniera de software",
                    "uri": "http://data.europa.eu/esco/occupation/b5f3d4a2-1111-2222",
                    "status": "released",
                },
            ]
        }
    }


@pytest.mark.asyncio
async def test_esco_connector_check_health_ok(
    sample_esco_response: dict[str, Any],
) -> None:
    """Verifica que check_health retorne True si la API responde 200 con _embedded."""
    # Verificamos que el conector configure headers por defecto
    default_connector = EscoConnector()
    assert default_connector._headers["User-Agent"] == DEFAULT_HTTP_USER_AGENT
    assert default_connector._headers["Accept"] == "application/json"

    transport = MockEscoTransport(status_code=200, payload=sample_esco_response)
    async with httpx.AsyncClient(transport=transport) as client:
        connector = EscoConnector(client=client)
        assert await connector.check_health() is True
        assert len(transport.requests) == 1


@pytest.mark.asyncio
async def test_esco_connector_check_health_error() -> None:
    """Verifica que check_health retorne False ante error HTTP o excepción."""
    transport = MockEscoTransport(status_code=500, payload={"error": "server error"})
    async with httpx.AsyncClient(transport=transport) as client:
        connector = EscoConnector(client=client)
        assert await connector.check_health() is False

    transport_exc = MockEscoTransport(
        raise_exception=httpx.ConnectError("No se pudo conectar")
    )
    async with httpx.AsyncClient(transport=transport_exc) as client:
        connector_exc = EscoConnector(client=client)
        assert await connector_exc.check_health() is False


@pytest.mark.asyncio
async def test_esco_connector_fetch_indicators_contrato_y_metadatos(
    sample_esco_response: dict[str, Any],
) -> None:
    """Verifica que fetch_indicators cumpla estrictamente con el contrato de datos:
    - tipo == TipoIndicador.OBSERVADO (cumple principio 3/5).
    - metadatos contiene 'tipo_registro' == 'catalogo_taxonomico'.
    - fuente oficial igual a DEFAULT_ESCO_SOURCE.
    """
    transport = MockEscoTransport(status_code=200, payload=sample_esco_response)
    async with httpx.AsyncClient(transport=transport) as client:
        connector = EscoConnector(client=client)
        records = await connector.fetch_indicators(indicadores=["desarrollador"])

    assert len(records) > 0
    # Iteró por occupation y skill -> cada uno generó 2 resultados
    for record in records:
        assert record.tipo == TipoIndicador.OBSERVADO
        assert record.fuente == DEFAULT_ESCO_SOURCE
        assert record.metadatos["tipo_registro"] == "catalogo_taxonomico"
        assert "uri" in record.metadatos
        assert "query_busqueda" in record.metadatos
        assert record.metadatos["query_busqueda"] == "desarrollador"
        assert record.valor == 0.0

    # Ocupaciones extraídas tienen ocupacion poblada
    ocupaciones = [r for r in records if r.indicador == "taxonomia_occupation"]
    assert len(ocupaciones) == 2
    assert ocupaciones[0].ocupacion == (
        "desarrollador de software / desarrolladora de software"
    )

    # Skills extraídas no tienen ocupacion
    skills = [r for r in records if r.indicador == "taxonomia_skill"]
    assert len(skills) == 2
    assert all(s.ocupacion is None for s in skills)


@pytest.mark.asyncio
async def test_esco_connector_fetch_indicators_resiliente_a_fallas() -> None:
    """Verifica que fallas en una consulta individual no corten el procesamiento."""
    transport = MockEscoTransport(status_code=500, payload={"error": "Fallo"})
    async with httpx.AsyncClient(transport=transport) as client:
        connector = EscoConnector(client=client)
        records = await connector.fetch_indicators(indicadores=["test_fallido"])
        assert records == []
