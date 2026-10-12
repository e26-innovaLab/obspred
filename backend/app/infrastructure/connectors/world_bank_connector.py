"""Conector oficial para la API del Banco Mundial (World Bank Indicators API)."""

import asyncio
from datetime import date
from typing import Any, Dict, List, Optional

import httpx

from app.core.logging import logger
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)


class WorldBankConnector(IExternalDataConnector):
    """Adaptador de infraestructura para consumir World Bank Indicators API.

    Provee extracción y normalización de indicadores macroeconómicos y socioeconómicos
    para los países miembros del Observatorio (Argentina, Uruguay, Chile) sin requerir
    clave de API de autenticación.
    """

    DEFAULT_BASE_URL: str = "https://api.worldbank.org/v2"
    DEFAULT_COUNTRIES: List[str] = ["ARG", "URY", "CHL"]
    DEFAULT_TIMEOUT_SECONDS: float = 30.0

    # Catálogo de indicadores oficiales verificados y su mapeo al modelo de dominio
    INDICATOR_MAPPINGS: Dict[str, Dict[str, Any]] = {
        "SL.UEM.TOTL.ZS": {
            "slug": "tasa_desempleo",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de desocupación total (% de fuerza laboral)",
        },
        "SL.TLF.CACT.ZS": {
            "slug": "participacion_laboral",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de participación en la fuerza laboral (%)",
        },
        "SL.EMP.TOTL.SP.ZS": {
            "slug": "empleo_poblacion",
            "sector": None,
            "ocupacion": None,
            "nombre": "Relación empleo-población (% de mayores de 15)",
        },
        "SL.SRV.EMPL.ZS": {
            "slug": "empleo_servicios",
            "sector": "Servicios",
            "ocupacion": None,
            "nombre": "Empleo en servicios (% del empleo total)",
        },
        "SL.IND.EMPL.ZS": {
            "slug": "empleo_industria",
            "sector": "Industria",
            "ocupacion": None,
            "nombre": "Empleo en industria (% del empleo total)",
        },
        "NY.GDP.PCAP.CD": {
            "slug": "pib_per_capita",
            "sector": None,
            "ocupacion": None,
            "nombre": "PIB per cápita (US$ a precios actuales)",
        },
        "SE.TER.ENRR": {
            "slug": "matricula_terciaria",
            "sector": None,
            "ocupacion": None,
            "nombre": "Inscripción en educación terciaria (% bruto)",
        },
        "IT.NET.USER.ZS": {
            "slug": "usuarios_internet",
            "sector": "Tecnología",
            "ocupacion": None,
            "nombre": "Población con acceso a Internet (%)",
        },
    }

    def __init__(
        self,
        base_url: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector del Banco Mundial.

        Args:
            base_url: URL base opcional de la API (por defecto v2 oficial).
            client: Cliente asíncrono inyectable de httpx (útil para tests).
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
        return "World Bank"

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
        paises: Optional[List[str]] = None,
        indicadores: Optional[List[str]] = None,
        periodo_desde: Optional[str] = None,
        periodo_hasta: Optional[str] = None,
    ) -> List[RawIndicatorRecord]:
        """Extrae y transforma datos de World Bank API a modelos normalizados.

        Args:
            paises: Lista de códigos ISO de país (ej. ['ARG', 'URY', 'CHL']).
            indicadores: Lista de códigos o slugs de indicadores a solicitar.
            periodo_desde: Año inicial de búsqueda (ej. '2015').
            periodo_hasta: Año final de búsqueda (ej. '2024').

        Returns:
            List[RawIndicatorRecord]: Registros normalizados listos para persistencia.
        """
        target_countries = paises or self.DEFAULT_COUNTRIES
        countries_param = ";".join(target_countries)

        # Mapeo inverso de slugs a códigos del Banco Mundial si el usuario pasó slugs
        target_indicator_codes = self._resolve_indicator_codes(indicadores)

        # Parámetro de rango temporal (date=2015:2024)
        date_param = self._build_date_param(periodo_desde, periodo_hasta)

        records: List[RawIndicatorRecord] = []
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            for code in target_indicator_codes:
                indicator_meta = self.INDICATOR_MAPPINGS[code]
                url = (
                    f"{self._base_url}/country/{countries_param}/indicator/{code}"
                    f"?format=json&per_page=1000"
                )
                if date_param:
                    url += f"&date={date_param}"

                try:
                    indicator_records = await self._fetch_indicator_series(
                        client=client,
                        url=url,
                        indicator_code=code,
                        indicator_meta=indicator_meta,
                    )
                    records.extend(indicator_records)
                except Exception as exc:
                    logger.error(
                        "Error consultando indicador %s en World Bank API: %s",
                        code,
                        str(exc),
                    )
        finally:
            if should_close_client:
                await client.aclose()

        return records

    async def _fetch_indicator_series(
        self,
        client: httpx.AsyncClient,
        url: str,
        indicator_code: str,
        indicator_meta: Dict[str, Any],
        max_retries: int = 2,
    ) -> List[RawIndicatorRecord]:
        """Ejecuta la solicitud HTTP con reintentos para una serie específica.

        Args:
            client: Cliente HTTP asíncrono.
            url: Endpoint completo con parámetros.
            indicator_code: Código identificador del Banco Mundial.
            indicator_meta: Metadatos de mapeo para el indicador.
            max_retries: Número de reintentos en caso de fallos transitorios.

        Returns:
            List[RawIndicatorRecord]: Registros procesados de la serie.
        """
        response_data: Optional[List[Any]] = None

        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, list) and len(payload) >= 2:
                    response_data = payload
                    break
                else:
                    logger.warning(
                        "Respuesta inesperada de World Bank API para %s: %s",
                        indicator_code,
                        payload,
                    )
                    return []
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < max_retries:
                    backoff = 1.5 * (attempt + 1)
                    logger.warning(
                        "Fallo transitorio en WB (%s). Reintento en %.1fs: %s",
                        url,
                        backoff,
                        str(exc),
                    )
                    await asyncio.sleep(backoff)
                else:
                    raise

        if not response_data:
            return []

        header_info = response_data[0] if isinstance(response_data[0], dict) else {}
        last_updated_str = header_info.get("lastupdated")
        fecha_actualizacion = self._parse_update_date(last_updated_str)

        raw_items = response_data[1]
        records: List[RawIndicatorRecord] = []

        if not isinstance(raw_items, list):
            return records

        for item in raw_items:
            # Descartamos registros sin valor observado disponible
            if not isinstance(item, dict) or item.get("value") is None:
                continue

            iso3 = item.get("countryiso3code")
            if not iso3 and isinstance(item.get("country"), dict):
                iso3 = item["country"].get("id")
            if not iso3:
                continue

            periodo = str(item.get("date", "")).strip()
            valor = float(item["value"])

            record = RawIndicatorRecord(
                pais=iso3.upper(),
                sector=indicator_meta.get("sector"),
                ocupacion=indicator_meta.get("ocupacion"),
                indicador=indicator_meta["slug"],
                periodo=periodo,
                valor=valor,
                tipo="observado",
                fuente=self.source_name,
                fecha_actualizacion=fecha_actualizacion,
                metadatos={
                    "world_bank_code": indicator_code,
                    "indicator_label": indicator_meta.get("nombre"),
                    "source_id": header_info.get("sourceid"),
                },
            )
            records.append(record)

        return records

    async def check_health(self) -> bool:
        """Verifica conectividad y disponibilidad de World Bank API.

        Returns:
            bool: True si responde 200 OK con payload válido, False de lo contrario.
        """
        ping_url = (
            f"{self._base_url}/country/ARG/indicator/SL.UEM.TOTL.ZS"
            f"?format=json&per_page=1"
        )
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(ping_url)
            if response.status_code == 200:
                payload = response.json()
                return isinstance(payload, list) and len(payload) >= 1
            return False
        except Exception as exc:
            logger.warning("Check health fallido en World Bank API: %s", str(exc))
            return False
        finally:
            if should_close_client:
                await client.aclose()

    def _resolve_indicator_codes(
        self, requested: Optional[List[str]]
    ) -> List[str]:
        """Resuelve códigos oficiales a partir de códigos directos o slugs."""
        if not requested:
            return list(self.INDICATOR_MAPPINGS.keys())

        slug_to_code = {
            meta["slug"]: code for code, meta in self.INDICATOR_MAPPINGS.items()
        }

        resolved: List[str] = []
        for req in requested:
            if req in self.INDICATOR_MAPPINGS:
                resolved.append(req)
            elif req in slug_to_code:
                resolved.append(slug_to_code[req])
            else:
                logger.warning("Indicador '%s' no reconocido en World Bank.", req)

        return resolved or list(self.INDICATOR_MAPPINGS.keys())

    @staticmethod
    def _build_date_param(
        desde: Optional[str], hasta: Optional[str]
    ) -> Optional[str]:
        """Construye el parámetro date=XXXX:YYYY requerido por la API."""
        if desde and hasta:
            return f"{desde}:{hasta}"
        if desde:
            return f"{desde}:{date.today().year}"
        if hasta:
            return f"2010:{hasta}"
        return "2015:2024"

    @staticmethod
    def _parse_update_date(date_str: Optional[str]) -> date:
        """Parsea la fecha de actualización reportada o devuelve la fecha actual."""
        if not date_str:
            return date.today()
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            return date.today()
