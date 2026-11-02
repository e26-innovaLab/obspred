"""Adaptador de infraestructura para consumir taxonomías de ESCO (Comisión Europea)."""

from datetime import date
from typing import Final

import httpx

from app.core.constants import (
    DEFAULT_ESCO_BASE_URL,
    DEFAULT_ESCO_SOURCE,
    DEFAULT_ESCO_TIMEOUT_SECONDS,
)
from app.core.logging import logger
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)


class EscoConnector(IExternalDataConnector):
    """Adaptador para búsqueda y normalización de

    ocupaciones y habilidades desde ESCO.
    """

    DEFAULT_BASE_URL: Final[str] = (
        DEFAULT_ESCO_BASE_URL or "https://ec.europa.eu/esco/api/search"
    )
    DEFAULT_SOURCE_NAME: Final[str] = DEFAULT_ESCO_SOURCE or "ESCO"
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_ESCO_TIMEOUT_SECONDS or 30.0

    def __init__(
        self,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector de ESCO."""
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._custom_client = client
        self._timeout = timeout
        self._headers = {
            "Accept": "application/json",
            "User-Agent": "ObsPred-Backend/1.0",
        }

    @property
    def source_name(self) -> str:
        """Nombre oficial de la fuente institucional."""
        return self.DEFAULT_SOURCE_NAME

    @property
    def base_url(self) -> str:
        """URL base configurada para la API."""
        return self._base_url

    @property
    def timeout(self) -> float:
        """Tiempo de espera configurado en segundos."""
        return self._timeout

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea un cliente HTTP asíncrono."""
        if self._custom_client is not None:
            return self._custom_client
        return httpx.AsyncClient(
            headers=self._headers,
            timeout=self._timeout,
        )

    async def check_health(self) -> bool:
        """Verifica conectividad y disponibilidad de la API de ESCO."""
        params = {
            "text": "desarrollador",
            "type": "occupation",
            "language": "es",
            "limit": 1,
        }
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(self._base_url, params=params)
            if response.status_code == 200 and "_embedded" in response.json():
                return True
            return False
        except Exception as exc:
            logger.warning("Check health fallido en ESCO API: %s", str(exc))
            return False
        finally:
            if should_close_client:
                await client.aclose()

    async def fetch_indicators(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        """Extrae taxonomías de ESCO y las normaliza."""
        queries = indicadores or ["desarrollador", "analista", "ingeniero"]
        records: list[RawIndicatorRecord] = []

        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            for query in queries:
                for tipo in ["occupation", "skill"]:
                    params = {
                        "text": query,
                        "type": tipo,
                        "language": "es",
                        "limit": 5,
                    }
                    try:
                        response = await client.get(self._base_url, params=params)
                        response.raise_for_status()
                        data = response.json()
                        results = data.get("_embedded", {}).get("results", [])

                        for item in results:
                            title = item.get("title", "")
                            uri = item.get("uri", "")

                            record = RawIndicatorRecord(
                                pais="GLOBAL",
                                sector=None,
                                ocupacion=title if tipo == "occupation" else None,
                                indicador=f"taxonomia_{tipo}",
                                periodo="actual",
                                valor=0.0,
                                tipo="catalogo",
                                fuente=self.source_name,
                                fecha_actualizacion=date.today(),
                                metadatos={"uri": uri, "query_busqueda": query},
                                detalles=item,
                            )
                            records.append(record)
                    except Exception as exc:
                        logger.error(
                            "Error consultando ESCO para query '%s' (%s): %s",
                            query,
                            tipo,
                            str(exc),
                        )
        finally:
            if should_close_client:
                await client.aclose()

        return records
