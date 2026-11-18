"""Conector oficial para la API de CEPALSTAT (CEPAL / Naciones Unidas)."""

import asyncio
from datetime import date
from typing import Any, Final

import httpx

from app.core.constants import (
    DEFAULT_CEPALSTAT_BASE_URL,
    DEFAULT_CEPALSTAT_SOURCE,
    DEFAULT_CEPALSTAT_TIMEOUT_SECONDS,
    DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS,
    PaisCodigo,
    TipoIndicador,
)
from app.core.logging import logger
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)


class CepalstatConnector(IExternalDataConnector):
    """Adaptador de infraestructura para consumir la API de CEPALSTAT.

    Provee extracción y normalización de indicadores macroeconómicos, laborales
    y socioeducativos armonizados para los países del Observatorio (Argentina,
    Uruguay y Chile).
    """

    DEFAULT_BASE_URL: Final[str] = DEFAULT_CEPALSTAT_BASE_URL
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_CEPALSTAT_TIMEOUT_SECONDS
    DEFAULT_COUNTRIES: Final[list[str]] = [
        PaisCodigo.ARG,
        PaisCodigo.URY,
        PaisCodigo.CHL,
    ]

    # Mapeo de códigos de países y variantes a código ISO 3166-1 alpha-3
    COUNTRY_MAPPINGS: Final[dict[str, str]] = {
        "ARG": "ARG",
        "AR": "ARG",
        "ARGENTINA": "ARG",
        "13": "ARG",
        "032": "ARG",
        "URY": "URY",
        "UY": "URY",
        "URUGUAY": "URY",
        "858": "URY",
        "CHL": "CHL",
        "CL": "CHL",
        "CHILE": "CHL",
        "152": "CHL",
    }

    # Catálogo de indicadores oficiales verificados y su mapeo al modelo de dominio
    INDICATOR_MAPPINGS: Final[dict[str, dict[str, Any]]] = {
        "SL_TLF_UEM": {
            "slug": "tasa_desempleo",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de desempleo nacional total (%)",
        },
        "SL_TLF_ACT": {
            "slug": "participacion_laboral",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de participación en la actividad económica (%)",
        },
        "NY_GDP_PCAP_CD": {
            "slug": "pib_per_capita",
            "sector": None,
            "ocupacion": None,
            "nombre": "Producto Interno Bruto por habitante (US$ a precios actuales)",
        },
        "SE_ENR_TERT": {
            "slug": "matricula_terciaria",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de matrícula en educación superior o terciaria (%)",
        },
        "EMP_SERV": {
            "slug": "empleo_servicios",
            "sector": "servicios",
            "ocupacion": None,
            "nombre": "Empleo en el sector de servicios (% del total)",
        },
        "EMP_IND": {
            "slug": "empleo_industria",
            "sector": "industria",
            "ocupacion": None,
            "nombre": "Empleo en el sector de la industria (% del total)",
        },
        # Alias numéricos reconocidos en CEPALSTAT
        "2222": {
            "slug": "tasa_desempleo",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de desempleo nacional total (%)",
        },
        "2221": {
            "slug": "participacion_laboral",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de participación en la actividad económica (%)",
        },
        "2200": {
            "slug": "pib_per_capita",
            "sector": None,
            "ocupacion": None,
            "nombre": "Producto Interno Bruto por habitante (US$ a precios actuales)",
        },
        "2250": {
            "slug": "matricula_terciaria",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de matrícula en educación superior o terciaria (%)",
        },
    }

    def __init__(
        self,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector oficial de CEPALSTAT.

        Args:
            base_url: URL base opcional de la API v1 de CEPALSTAT.
            client: Cliente asíncrono inyectable de httpx (útil para pruebas).
            timeout: Tiempo máximo de espera en segundos para solicitudes HTTP.
        """
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._custom_client = client
        self._timeout = timeout
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; ObservatorioPredictivo/1.0; "
                "+https://github.com/innova-lab/obspred)"
            ),
            "Accept": "application/json",
        }

    @property
    def source_name(self) -> str:
        """Nombre oficial de la fuente institucional."""
        return DEFAULT_CEPALSTAT_SOURCE

    @property
    def source_id(self) -> str:
        """Identificador normalizado para reportes de disponibilidad."""
        return "cepalstat"

    @property
    def base_url(self) -> str:
        """URL base configurada para la API."""
        return self._base_url

    @property
    def timeout(self) -> float:
        """Tiempo de espera configurado en segundos."""
        return self._timeout

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea un cliente HTTP asíncrono para la conexión."""
        if self._custom_client is not None:
            return self._custom_client
        return httpx.AsyncClient(
            headers=self._headers,
            timeout=self._timeout,
        )

    async def fetch_indicators(
        self,
        paises: list[str] | None = None,
        indicadores: list[str] | None = None,
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        """Extrae y transforma datos de CEPALSTAT API a modelos normalizados.

        Args:
            paises: Lista de códigos ISO de país (ej. ['ARG', 'URY', 'CHL']).
            indicadores: Lista de códigos o slugs de indicadores a solicitar.
            periodo_desde: Año inicial de búsqueda (ej. '2015').
            periodo_hasta: Año final de búsqueda (ej. '2024').

        Returns:
            list[RawIndicatorRecord]: Registros normalizados listos para persistencia.
        """
        target_countries = [p.upper() for p in (paises or self.DEFAULT_COUNTRIES)]
        target_indicator_codes = self._resolve_indicator_codes(indicadores)

        records: list[RawIndicatorRecord] = []
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            tasks: list[Any] = []
            for code in target_indicator_codes:
                indicator_meta = self.INDICATOR_MAPPINGS[code]
                url = f"{self._base_url}/indicator/{code}/data?lang=es&format=json"
                tasks.append(
                    self._fetch_indicator_series(
                        client=client,
                        url=url,
                        indicator_code=code,
                        indicator_meta=indicator_meta,
                        target_countries=target_countries,
                        periodo_desde=periodo_desde,
                        periodo_hasta=periodo_hasta,
                    )
                )

            series_results = await asyncio.gather(*tasks, return_exceptions=True)
            for code, res in zip(target_indicator_codes, series_results, strict=True):
                if isinstance(res, Exception):
                    logger.error(
                        "Error consultando indicador %s en CEPALSTAT API: %s",
                        code,
                        str(res),
                    )
                elif isinstance(res, list):
                    records.extend(res)
        finally:
            if should_close_client:
                await client.aclose()

        return records

    async def _fetch_indicator_series(
        self,
        client: httpx.AsyncClient,
        url: str,
        indicator_code: str,
        indicator_meta: dict[str, Any],
        target_countries: list[str],
        periodo_desde: str | None,
        periodo_hasta: str | None,
    ) -> list[RawIndicatorRecord]:
        """Ejecuta la solicitud HTTP para un indicador específico de CEPALSTAT.

        Args:
            client: Cliente HTTP asíncrono.
            url: Endpoint de datos con parámetros.
            indicator_code: Código o ID del indicador en CEPALSTAT.
            indicator_meta: Metadatos asociados al indicador.
            target_countries: Lista de países filtrados (en ISO3).
            periodo_desde: Año mínimo opcional.
            periodo_hasta: Año máximo opcional.

        Returns:
            list[RawIndicatorRecord]: Registros normalizados del indicador.
        """
        try:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        except (httpx.TimeoutException, httpx.HTTPError) as exc:
            logger.warning(
                "Fallo al consultar indicador %s en CEPALSTAT (%s): %s",
                indicator_code,
                url,
                str(exc),
            )
            return []

        return self._parse_cepalstat_payload(
            payload=payload,
            indicator_code=indicator_code,
            indicator_meta=indicator_meta,
            target_countries=target_countries,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
        )

    def _parse_cepalstat_payload(
        self,
        payload: dict[str, Any],
        indicator_code: str,
        indicator_meta: dict[str, Any],
        target_countries: list[str],
        periodo_desde: str | None,
        periodo_hasta: str | None,
    ) -> list[RawIndicatorRecord]:
        """Parsea y normaliza el JSON de respuesta devuelto por la API de CEPALSTAT.

        Args:
            payload: Diccionario de respuesta de la API.
            indicator_code: Código del indicador consultado.
            indicator_meta: Configuración del indicador en el modelo del Observatorio.
            target_countries: Lista de países objetivo (ISO-3).
            periodo_desde: Año inicial opcional.
            periodo_hasta: Año final opcional.

        Returns:
            list[RawIndicatorRecord]: Registros normalizados.
        """
        records: list[RawIndicatorRecord] = []
        if not isinstance(payload, dict):
            return records

        body = payload.get("body", payload)
        if not isinstance(body, dict):
            return records

        raw_data = body.get("data", [])
        if not isinstance(raw_data, list):
            return records

        # Mapa de dimensiones de países para resolución de IDs numéricos o nombres
        dimensions = body.get("dimensions", [])
        country_dim_map: dict[str, str] = {}
        if isinstance(dimensions, list):
            for dim in dimensions:
                if isinstance(dim, dict) and dim.get("id") in (
                    "country",
                    "pais",
                    "area",
                    "332",
                ):
                    for val in dim.get("values", []):
                        if isinstance(val, dict):
                            val_id = str(val.get("id", "")).strip()
                            iso_code = (
                                val.get("iso3")
                                or val.get("code")
                                or val.get("name", "")
                            )
                            resolved = self._normalize_country_code(str(iso_code))
                            if resolved:
                                country_dim_map[val_id] = resolved

        fecha_actualizacion = date.today()

        for item in raw_data:
            if not isinstance(item, dict):
                continue

            raw_value = item.get("valor") if "valor" in item else item.get("value")
            if raw_value is None:
                continue

            try:
                valor = float(raw_value)
            except (ValueError, TypeError):
                continue

            dims = (
                item.get("dimensions")
                if isinstance(item.get("dimensions"), dict)
                else {}
            )

            raw_country = (
                item.get("country")
                or item.get("pais")
                or item.get("iso3")
                or dims.get("country")
                or dims.get("pais")
                or dims.get("area")
                or dims.get("332")
            )
            raw_country_str = str(raw_country).strip() if raw_country else ""

            # Resolver país usando dimension map o fallback general
            pais = country_dim_map.get(
                raw_country_str,
                self._normalize_country_code(raw_country_str),
            )
            if not pais or pais not in target_countries:
                continue

            raw_periodo = (
                item.get("year")
                or item.get("periodo")
                or dims.get("year")
                or dims.get("periodo")
                or dims.get("time_period")
            )
            periodo = str(raw_periodo).strip() if raw_periodo else ""
            if not periodo:
                continue

            # Filtros temporales si aplican
            if periodo_desde and periodo < periodo_desde:
                continue
            if periodo_hasta and periodo > periodo_hasta:
                continue

            record = RawIndicatorRecord(
                pais=pais,
                sector=indicator_meta.get("sector"),
                ocupacion=indicator_meta.get("ocupacion"),
                indicador=indicator_meta["slug"],
                periodo=periodo,
                trimestre=None,
                valor=valor,
                tipo=TipoIndicador.OBSERVADO,
                fuente=self.source_name,
                fecha_actualizacion=fecha_actualizacion,
                metadatos={
                    "cepalstat_code": indicator_code,
                    "indicator_label": indicator_meta.get("nombre"),
                },
            )
            records.append(record)

        return records

    async def check_health(self) -> bool:
        """Verifica conectividad y disponibilidad de la API de CEPALSTAT.

        Returns:
            bool: True si la API responde 200 OK con payload válido,
                False de lo contrario.
        """
        ping_url = f"{self._base_url}/thematic-tree?lang=es&format=json"
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(
                ping_url,
                timeout=DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS,
            )
            if response.status_code == 200:
                payload = response.json()
                return isinstance(payload, dict) or isinstance(payload, list)
            return False
        except Exception as exc:
            logger.warning("Check health fallido en CEPALSTAT API: %s", str(exc))
            return False
        finally:
            if should_close_client:
                await client.aclose()

    def _resolve_indicator_codes(self, requested: list[str] | None) -> list[str]:
        """Resuelve códigos oficiales a partir de slugs canónicos o códigos directos."""
        if not requested:
            # Retorna códigos principales (sin duplicar slugs)
            primary_codes = [
                "SL_TLF_UEM",
                "SL_TLF_ACT",
                "NY_GDP_PCAP_CD",
                "SE_ENR_TERT",
            ]
            return [c for c in primary_codes if c in self.INDICATOR_MAPPINGS]

        slug_to_code: dict[str, str] = {}
        for code, meta in self.INDICATOR_MAPPINGS.items():
            slug = meta["slug"]
            if slug not in slug_to_code:
                slug_to_code[slug] = code

        resolved: list[str] = []
        seen: set[str] = set()

        for req in requested:
            if req in self.INDICATOR_MAPPINGS:
                code = req
            elif req in slug_to_code:
                code = slug_to_code[req]
            else:
                logger.warning("Indicador '%s' no reconocido en CEPALSTAT.", req)
                continue

            if code not in seen:
                seen.add(code)
                resolved.append(code)

        return resolved or ["SL_TLF_UEM", "SL_TLF_ACT", "NY_GDP_PCAP_CD", "SE_ENR_TERT"]

    def _normalize_country_code(self, raw_code: str) -> str | None:
        """Normaliza un código o nombre de país a código ISO 3166-1 alpha-3."""
        if not raw_code:
            return None
        cleaned = raw_code.strip().upper()
        return self.COUNTRY_MAPPINGS.get(cleaned)
