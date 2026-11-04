"""Conector de infraestructura para consumir series de tiempo de Datos Argentina."""

from datetime import date
from typing import Any, Final

import httpx

from app.core.constants import PaisCodigo, TipoIndicador
from app.core.logging import logger
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)

from app.core.constants import (
    PaisCodigo,
    DEFAULT_DATOS_ARGENTINA_BASE_URL,
    DEFAULT_DATOS_ARGENTINA_SOURCE_NAME,
    DEFAULT_DATOS_ARGENTINA_TIMEOUT_SECONDS,
)


class DatosArgentinaConnector(IExternalDataConnector):
    """Adaptador para consultar indicadores de la API Series de Tiempo."""

    DEFAULT_BASE_URL: Final[str] = DEFAULT_DATOS_ARGENTINA_BASE_URL
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_DATOS_ARGENTINA_TIMEOUT_SECONDS
    SOURCE_NAME: Final[str] = DEFAULT_DATOS_ARGENTINA_SOURCE_NAME

    # Los IDs son identificadores reales obtenidos mediante la API /search.
    INDICATOR_MAPPINGS: Final[dict[str, dict[str, Any]]] = {
        # Empleo registrado
        "empleo_registrado_total": {
            "id": "156.1_TLTAL_0_0_5",
            "nombre": "Total empleo registrado",
            "sector": None,
            "ocupacion": None,
            "unidad": "puestos de trabajo",
            "frecuencia": "trimestral",
            "dimension_geografica": "nacional",
        },
        "empleo_registrado_industria": {
            "id": "155.1_ISTRIARIA_C_0_0_9",
            "nombre": "Empleo registrado privado en industria",
            "sector": "Industria",
            "ocupacion": None,
            "unidad": "puestos de trabajo",
            "frecuencia": "trimestral",
            "dimension_geografica": "nacional",
        },
        # Encuesta Permanente de Hogares (EPH)
        "tasa_actividad_total": {
            "id": "42.1_EPAT_0_A_27",
            "nombre": "Tasa de actividad total",
            "sector": None,
            "ocupacion": None,
            "unidad": "porcentaje",
            "frecuencia": "anual",
            "dimension_geografica": "pendiente_de_verificar",
        },
        "tasa_empleo_total": {
            "id": "42.1_EPET_0_A_24",
            "nombre": "Tasa de empleo total",
            "sector": None,
            "ocupacion": None,
            "unidad": "porcentaje",
            "frecuencia": "anual",
            "dimension_geografica": "pendiente_de_verificar",
        },
        "tasa_desocupacion_total": {
            "id": "42.1_EPDT_0_A_30",
            "nombre": "Tasa de desocupación total",
            "sector": None,
            "ocupacion": None,
            "unidad": "porcentaje",
            "frecuencia": "anual",
            "dimension_geografica": "pendiente_de_verificar",
        },
        "tasa_subocupacion_total": {
            "id": "42.1_EPST_0_A_30",
            "nombre": "Tasa de subocupación total",
            "sector": None,
            "ocupacion": None,
            "unidad": "porcentaje",
            "frecuencia": "anual",
            "dimension_geografica": "pendiente_de_verificar",
        },
        "tasa_subocupacion_demandante": {
            "id": "42.1_EPSTD_0_A_41",
            "nombre": "Tasa de subocupación demandante",
            "sector": None,
            "ocupacion": None,
            "unidad": "porcentaje",
            "frecuencia": "anual",
            "dimension_geografica": "pendiente_de_verificar",
        },
        "tasa_subocupacion_no_demandante": {
            "id": "42.1_EPSTND_0_A_44",
            "nombre": "Tasa de subocupación no demandante",
            "sector": None,
            "ocupacion": None,
            "unidad": "porcentaje",
            "frecuencia": "anual",
            "dimension_geografica": "pendiente_de_verificar",
        },
    }

    def __init__(
        self,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._custom_client = client
        self._timeout = timeout

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def base_url(self) -> str:
        return self._base_url

    async def _get_client(self) -> httpx.AsyncClient:
        if self._custom_client is not None:
            return self._custom_client

        return httpx.AsyncClient(
            timeout=self._timeout,
            headers={"Accept": "application/json"},
        )

    async def check_health(self) -> bool:
        """Comprueba si la API de Datos Argentina está disponible."""
        client = await self._get_client()
        should_close = self._custom_client is None

        try:
            response = await client.get(
                f"{self._base_url}/search/",
                params={"q": "empleo", "limit": 1},
            )
            response.raise_for_status()
            return isinstance(response.json(), dict)

        except (httpx.HTTPError, ValueError) as exc:
            logger.warning(
                "Check health fallido en Datos Argentina: %s",
                str(exc),
            )
            return False

        finally:
            if should_close:
                await client.aclose()

    async def search_series(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Busca series disponibles por nombre o palabra clave."""
        client = await self._get_client()
        should_close = self._custom_client is None

        try:
            response = await client.get(
                f"{self._base_url}/search/",
                params={"q": query, "limit": limit},
            )
            response.raise_for_status()
            return response.json()

        finally:
            if should_close:
                await client.aclose()

    async def fetch_indicators(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        """Consulta series configuradas y normaliza sus valores."""

        target_countries = paises or [PaisCodigo.ARG]

        # Este conector consume series de Argentina.
        if PaisCodigo.ARG not in target_countries:
            return []

        requested = indicadores or list(self.INDICATOR_MAPPINGS.keys())

        records: list[RawIndicatorRecord] = []
        client = await self._get_client()
        should_close = self._custom_client is None

        try:
            for slug in requested:
                metadata = self.INDICATOR_MAPPINGS.get(slug)

                if metadata is None:
                    logger.warning(
                        "Indicador '%s' no configurado en Datos Argentina.",
                        slug,
                    )
                    continue

                try:
                    params = {
                        "ids": metadata["id"],
                        "format": "json",
                        "metadata": "full",
                    }

                    if periodo_desde:
                        params["start_date"] = periodo_desde

                    if periodo_hasta:
                        params["end_date"] = periodo_hasta

                    response = await client.get(
                        f"{self._base_url}/series/",
                        params=params,
                    )

                    response.raise_for_status()

                    records.extend(
                        self._parse_series_payload(
                            payload=response.json(),
                            slug=slug,
                            metadata=metadata,
                        )
                    )

                except (httpx.HTTPError, ValueError, KeyError) as exc:
                    logger.error(
                        "Error consultando '%s' en Datos Argentina: %s",
                        slug,
                        str(exc),
                    )

        finally:
            if should_close:
                await client.aclose()

        return records

    def _parse_series_payload(
        self,
        payload: dict[str, Any],
        slug: str,
        metadata: dict[str, Any],
    ) -> list[RawIndicatorRecord]:
        """Convierte los valores de una serie al modelo normalizado."""

        records: list[RawIndicatorRecord] = []

        fecha_extraccion = date.today()

        for row in payload.get("data", []):
            if not isinstance(row, list) or len(row) < 2:
                continue

            periodo = str(row[0])[:10]
            raw_value = row[1]

            if raw_value is None:
                continue

            try:
                valor = float(raw_value)
            except (ValueError, TypeError):
                continue

            if not periodo:
                continue

            # La API devuelve las tasas como fracciones.
            # Ejemplo: 0.03325 equivale a 3.325 %.
            if metadata["unidad"] == "porcentaje":
                valor *= 100

            records.append(
                RawIndicatorRecord(
                    pais=PaisCodigo.ARG,
                    sector=metadata.get("sector"),
                    ocupacion=metadata.get("ocupacion"),
                    indicador=slug,
                    periodo=periodo,
                    valor=valor,
                    tipo=TipoIndicador.OBSERVADO,
                    fuente=self.source_name,
                    # Temporalmente este campo representa la extracción.
                    # La fecha real de actualización de la fuente no está
                    # disponible todavía en la normalización actual.
                    fecha_actualizacion=fecha_extraccion,
                    metadatos={
                        "series_id": metadata["id"],
                        "indicator_label": metadata.get("nombre"),
                        "unidad": metadata["unidad"],
                        "frecuencia": metadata["frecuencia"],
                        "dimension_geografica": metadata["dimension_geografica"],
                        "fecha_extraccion": fecha_extraccion.isoformat(),
                        "fecha_actualizacion_fuente": None,
                    },
                )
            )

        return records
