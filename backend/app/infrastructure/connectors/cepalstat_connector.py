"""Conector oficial para la API de CEPALSTAT (CEPAL / Naciones Unidas)."""

import asyncio
import json
from datetime import date, datetime
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
    Uruguay y Chile) utilizando los identificadores oficiales verificados.
    """

    DEFAULT_BASE_URL: Final[str] = DEFAULT_CEPALSTAT_BASE_URL
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_CEPALSTAT_TIMEOUT_SECONDS
    DEFAULT_COUNTRIES: Final[list[str]] = [
        PaisCodigo.ARG,
        PaisCodigo.URY,
        PaisCodigo.CHL,
    ]

    # Mapeo de códigos, nombres y IDs oficiales de CEPALSTAT a ISO 3166-1 alpha-3
    COUNTRY_MAPPINGS: Final[dict[str, str]] = {
        "ARG": "ARG",
        "AR": "ARG",
        "ARGENTINA": "ARG",
        "13": "ARG",
        "032": "ARG",
        "216": "ARG",  # ID oficial de Argentina en Dim 208 (País__ESTANDAR)
        "URY": "URY",
        "UY": "URY",
        "URUGUAY": "URY",
        "858": "URY",
        "258": "URY",  # ID oficial de Uruguay en Dim 208 (País__ESTANDAR)
        "CHL": "CHL",
        "CL": "CHL",
        "CHILE": "CHL",
        "152": "CHL",
        "224": "CHL",  # ID oficial de Chile en Dim 208 (País__ESTANDAR)
    }

    # Catálogo verificado de indicadores oficiales de CEPALSTAT (IDs numéricos reales)
    INDICATOR_MAPPINGS: Final[dict[str, dict[str, Any]]] = {
        "127": {
            "slug": "tasa_desempleo",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de desocupación por sexo",
            "unidad": "Tasa anual media (%)",
            "frecuencia": "anual",
        },
        "2182": {
            "slug": "tasa_desempleo_trimestral",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de desocupación trimestral",
            "unidad": "Porcentaje (%)",
            "frecuencia": "trimestral",
        },
        "2470": {
            "slug": "participacion_laboral",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de participación en la fuerza de trabajo, por sexo",
            "unidad": "Porcentaje (%)",
            "frecuencia": "anual",
        },
        "2205": {
            "slug": "pib_per_capita",
            "sector": None,
            "ocupacion": None,
            "nombre": (
                "Producto interno bruto (PIB) total anual por habitante a precios "
                "corrientes en dólares"
            ),
            "unidad": "Dólares corrientes por habitante",
            "frecuencia": "anual",
        },
        "99": {
            "slug": "matricula_terciaria",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa bruta de matrícula de nivel terciario, por sexo",
            "unidad": "Porcentaje (%)",
            "frecuencia": "anual",
        },
    }

    DEFAULT_INDICATOR_IDS: Final[list[str]] = ["127", "2470", "2205", "99"]

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
            paises: Lista de códigos, nombres o identificadores de país.
            indicadores: Lista de IDs numéricos verificados o slugs canónicos.
            periodo_desde: Año o período inicial de búsqueda (ej. '2015', '2020-Q1').
            periodo_hasta: Año o período final de búsqueda (ej. '2024', '2024-Q4').

        Returns:
            list[RawIndicatorRecord]: Registros normalizados listos para persistencia.
        """
        # Normalización exhaustiva de países objetivo
        raw_target_countries = [
            self._normalize_country_code(p)
            for p in (paises or self.DEFAULT_COUNTRIES)
        ]
        target_countries = {p for p in raw_target_countries if p is not None}
        if not target_countries:
            logger.warning("Ningún país objetivo válido especificado para CEPALSTAT.")
            return []

        target_indicator_codes = self._resolve_indicator_codes(indicadores)
        if not target_indicator_codes:
            logger.warning(
                "Ningún indicador válido reconocido en el catálogo de CEPALSTAT."
            )
            return []

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
                        "Error no controlado consultando indicador %s en CEPALSTAT: %s",
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
        target_countries: set[str],
        periodo_desde: str | None,
        periodo_hasta: str | None,
    ) -> list[RawIndicatorRecord]:
        """Ejecuta la solicitud HTTP para un indicador específico de CEPALSTAT.

        Args:
            client: Cliente HTTP asíncrono.
            url: Endpoint de datos con parámetros.
            indicator_code: ID numérico del indicador en CEPALSTAT.
            indicator_meta: Metadatos asociados al indicador.
            target_countries: Conjunto de países filtrados (en ISO-3).
            periodo_desde: Período mínimo opcional.
            periodo_hasta: Período máximo opcional.

        Returns:
            list[RawIndicatorRecord]: Registros normalizados del indicador.
        """
        try:
            response = await client.get(url)
            if response.status_code == 404:
                logger.warning(
                    "Indicador %s no encontrado en CEPALSTAT (HTTP 404): %s",
                    indicator_code,
                    url,
                )
                return []
            if response.status_code == 400:
                logger.warning(
                    "Solicitud incorrecta para indicador %s en CEPALSTAT "
                    "(HTTP 400): %s",
                    indicator_code,
                    url,
                )
                return []
            response.raise_for_status()

            try:
                payload = response.json()
            except json.JSONDecodeError as json_err:
                logger.error(
                    "Respuesta de CEPALSTAT no es JSON válido para indicador %s "
                    "(Status %d, Content-Type: %s): %s",
                    indicator_code,
                    response.status_code,
                    response.headers.get("content-type"),
                    str(json_err),
                )
                return []

        except httpx.TimeoutException as exc:
            logger.warning(
                "Timeout en CEPALSTAT consultando indicador %s (%s): %s",
                indicator_code,
                url,
                str(exc),
            )
            return []
        except httpx.HTTPError as exc:
            logger.warning(
                "Fallo HTTP en CEPALSTAT consultando indicador %s (%s): %s",
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
        target_countries: set[str],
        periodo_desde: str | None,
        periodo_hasta: str | None,
    ) -> list[RawIndicatorRecord]:
        """Parsea y normaliza el esquema real devuelto por la API de CEPALSTAT.

        Resuelve dinámicamente las dimensiones a través de sus metadatos y miembros
        (País, Año, Trimestre, Sexo), respetando la fecha de corte real del origen.

        Args:
            payload: Diccionario de respuesta de la API.
            indicator_code: Código del indicador consultado.
            indicator_meta: Configuración del indicador en el modelo del Observatorio.
            target_countries: Conjunto de países objetivo (ISO-3).
            periodo_desde: Período inicial opcional.
            periodo_hasta: Período final opcional.

        Returns:
            list[RawIndicatorRecord]: Registros normalizados.
        """
        records: list[RawIndicatorRecord] = []
        if not isinstance(payload, dict):
            return records

        body = payload.get("body", payload)
        if not isinstance(body, dict):
            return records

        metadata = body.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        # Extracción y parseo de la fecha real de actualización según Principio 3
        raw_last_update = metadata.get("last_update")
        fecha_actualizacion = self._parse_update_date(raw_last_update)

        raw_data = body.get("data", [])
        if not isinstance(raw_data, list):
            logger.warning(
                "Payload de CEPALSTAT para indicador %s no contiene lista 'data'.",
                indicator_code,
            )
            return records

        # 1. Resolver dinámicamente el significado de dimensiones y miembros
        dimensions = body.get("dimensions", [])
        country_dim_id: str | None = None
        year_dim_id: str | None = None
        quarter_dim_id: str | None = None
        sex_dim_id: str | None = None

        country_member_map: dict[str, str] = {}
        year_member_map: dict[str, str] = {}
        quarter_member_map: dict[str, str] = {}
        sex_member_map: dict[str, str] = {}

        if isinstance(dimensions, list):
            for dim in dimensions:
                if not isinstance(dim, dict):
                    continue
                d_id = str(dim.get("id", ""))
                d_name = str(dim.get("name", "")).lower()
                members = dim.get("members", [])
                if not isinstance(members, list):
                    continue

                # Dimensión País / Área
                if any(
                    k in d_name for k in ["país", "pais", "country", "área", "area"]
                ) or d_id in ("208", "332"):
                    country_dim_id = d_id
                    for m in members:
                        if isinstance(m, dict):
                            country_member_map[str(m.get("id"))] = str(
                                m.get("name", "")
                            )
                # Dimensión Año
                elif (
                    any(k in d_name for k in ["año", "ano", "year"])
                    or d_id == "29117"
                ):
                    year_dim_id = d_id
                    for m in members:
                        if isinstance(m, dict):
                            year_member_map[str(m.get("id"))] = str(
                                m.get("name", "")
                            )
                # Dimensión Trimestre
                elif (
                    any(k in d_name for k in ["trimestre", "quarter"])
                    or d_id == "26677"
                ):
                    quarter_dim_id = d_id
                    for m in members:
                        if isinstance(m, dict):
                            q_name = str(m.get("name", "")).upper()
                            q_clean = (
                                q_name.replace("T", "Q") if "T" in q_name else q_name
                            )
                            quarter_member_map[str(m.get("id"))] = q_clean
                # Dimensión Sexo
                elif any(k in d_name for k in ["sexo", "sex"]) or d_id == "144":
                    sex_dim_id = d_id
                    for m in members:
                        if isinstance(m, dict):
                            sex_member_map[str(m.get("id"))] = str(
                                m.get("name", "")
                            )

        # 2. Procesar observaciones de datos reales
        for item in raw_data:
            if not isinstance(item, dict):
                continue

            # Extracción y validación estricta del valor numérico
            raw_value = item.get("value")
            if (
                raw_value is None
                or raw_value == ""
                or raw_value == "-"
                or raw_value == "..."
            ):
                continue

            try:
                valor = float(raw_value)
            except (ValueError, TypeError):
                continue

            # Resolución de país: usa iso3 directo si viene presente, o la dimensión
            raw_iso3 = item.get("iso3")
            pais: str | None = None
            if raw_iso3:
                pais = self._normalize_country_code(raw_iso3)

            if not pais and country_dim_id:
                member_id = str(item.get(f"dim_{country_dim_id}", ""))
                country_name = country_member_map.get(member_id)
                pais = self._normalize_country_code(country_name or member_id)

            if not pais or pais not in target_countries:
                continue

            # Filtrar por dimensión Sexo: para el indicador agregado nacional,
            # seleccionamos "Ambos sexos" o "Total" para no triplicar registros
            if sex_dim_id:
                member_id = str(item.get(f"dim_{sex_dim_id}", ""))
                sex_name = sex_member_map.get(member_id, "").lower()
                if "ambos" not in sex_name and "total" not in sex_name:
                    continue

            # Resolución del año
            year: str | None = None
            if year_dim_id:
                member_id = str(item.get(f"dim_{year_dim_id}", ""))
                year = year_member_map.get(member_id)
            if not year:
                year = str(item.get("year", "")).strip() or None
            if not year:
                continue

            # Resolución del trimestre si aplica
            trimestre: str | None = None
            if quarter_dim_id:
                member_id = str(item.get(f"dim_{quarter_dim_id}", ""))
                trimestre = quarter_member_map.get(member_id)

            periodo = f"{year}-{trimestre}" if trimestre else year

            # Filtrado temporal robusto considerando años y trimestres
            if not self._is_period_in_range(periodo, periodo_desde, periodo_hasta):
                continue

            record = RawIndicatorRecord(
                pais=pais,
                sector=indicator_meta.get("sector"),
                ocupacion=indicator_meta.get("ocupacion"),
                indicador=indicator_meta["slug"],
                periodo=periodo,
                trimestre=trimestre,
                valor=valor,
                tipo=TipoIndicador.OBSERVADO,
                fuente=self.source_name,
                fecha_actualizacion=fecha_actualizacion,
                metadatos={
                    "cepalstat_indicator_id": indicator_code,
                    "indicator_name": (
                        metadata.get("indicator_name") or indicator_meta.get("nombre")
                    ),
                    "unit": metadata.get("unit") or indicator_meta.get("unidad"),
                    "theme": metadata.get("theme"),
                    "area": metadata.get("area"),
                    "source_id": item.get("source_id"),
                    "last_update_raw": raw_last_update,
                },
                detalles={
                    "definition": metadata.get("definition"),
                    "calculation_methodology": metadata.get("calculation_methodology"),
                    "decimals": metadata.get("decimals"),
                    "notes_ids": item.get("notes_ids"),
                },
            )
            records.append(record)

        return records

    async def check_health(self) -> bool:
        """Verifica conectividad y disponibilidad de la API de CEPALSTAT.

        Realiza una consulta ligera al endpoint de metadatos del indicador 127.

        Returns:
            bool: True si la API responde 200 OK con payload válido,
                False de lo contrario.
        """
        ping_url = f"{self._base_url}/indicator/127/metadata?lang=es&format=json"
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(
                ping_url,
                timeout=DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS,
            )
            if response.status_code == 200:
                payload = response.json()
                return isinstance(payload, dict) and "body" in payload
            return False
        except Exception as exc:
            logger.warning("Check health fallido en CEPALSTAT API: %s", str(exc))
            return False
        finally:
            if should_close_client:
                await client.aclose()

    def _resolve_indicator_codes(self, requested: list[str] | None) -> list[str]:
        """Resuelve IDs numéricos a partir de slugs canónicos o IDs directos."""
        if not requested:
            return list(self.DEFAULT_INDICATOR_IDS)

        slug_to_code: dict[str, str] = {
            meta["slug"]: code for code, meta in self.INDICATOR_MAPPINGS.items()
        }

        resolved: list[str] = []
        seen: set[str] = set()

        for req in requested:
            req_str = str(req).strip()
            if req_str in self.INDICATOR_MAPPINGS:
                code = req_str
            elif req_str in slug_to_code:
                code = slug_to_code[req_str]
            else:
                logger.warning(
                    "Indicador '%s' no reconocido en el catálogo de CEPALSTAT.",
                    req,
                )
                continue

            if code not in seen:
                seen.add(code)
                resolved.append(code)

        return resolved

    def _normalize_country_code(self, raw_code: Any) -> str | None:
        """Normaliza un código, nombre o ID de país a código ISO 3166-1 alpha-3."""
        if raw_code is None:
            return None
        cleaned = str(raw_code).strip().upper()
        return self.COUNTRY_MAPPINGS.get(cleaned)

    @staticmethod
    def _parse_update_date(date_str: str | None) -> date:
        """Parsea la fecha de actualización real reportada por CEPALSTAT.

        Soporta:
        - Formato CEPAL: 'Dec 19 2025  1:14PM'
        - Formato ISO: '2025-12-19'
        - Formato común: '19/12/2025'
        """
        if not date_str or not isinstance(date_str, str):
            logger.warning("Fecha de actualización vacía en metadata de CEPALSTAT.")
            return date.today()

        cleaned = " ".join(date_str.strip().split())

        # 1. Formato CEPAL 'Dec 19 2025 1:14PM'
        try:
            return datetime.strptime(cleaned, "%b %d %Y %I:%M%p").date()
        except ValueError:
            pass

        # 2. Formato ISO 'YYYY-MM-DD'
        try:
            return date.fromisoformat(cleaned[:10])
        except ValueError:
            pass

        # 3. Formato 'DD/MM/YYYY'
        try:
            return datetime.strptime(cleaned[:10], "%d/%m/%Y").date()
        except ValueError:
            pass

        logger.warning(
            "No se pudo parsear fecha de actualización de CEPALSTAT: '%s'. "
            "Usando fecha actual como fallback.",
            date_str,
        )
        return date.today()

    @staticmethod
    def _parse_period_key(period_str: str) -> tuple[int, int]:
        """Convierte una cadena de período en tupla comparable (año, trimestre)."""
        clean = str(period_str).strip().upper()
        if "-" in clean:
            parts = clean.split("-", 1)
            try:
                year = int(parts[0])
                q_part = parts[1].replace("Q", "").replace("T", "").strip()
                quarter = int(q_part) if q_part.isdigit() else 0
                return (year, quarter)
            except (ValueError, TypeError):
                pass
        try:
            return (int(clean), 0)
        except (ValueError, TypeError):
            return (0, 0)

    @classmethod
    def _is_period_in_range(
        cls,
        periodo: str,
        desde: str | None,
        hasta: str | None,
    ) -> bool:
        """Determina si un período se encuentra dentro del rango solicitado."""
        p_year, p_q = cls._parse_period_key(periodo)
        if p_year == 0:
            return True

        if desde:
            d_year, d_q = cls._parse_period_key(desde)
            if d_year > 0:
                if d_q == 0:
                    if p_year < d_year:
                        return False
                else:
                    if (p_year, p_q) < (d_year, d_q):
                        return False

        if hasta:
            h_year, h_q = cls._parse_period_key(hasta)
            if h_year > 0:
                if h_q == 0:
                    if p_year > h_year:
                        return False
                else:
                    if (p_year, p_q) > (h_year, h_q):
                        return False

        return True
