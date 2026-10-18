"""Adaptador de infraestructura para consumir indicadores laborales de ILOSTAT (OIT)."""

import asyncio
import csv
import io
from datetime import date
from typing import Any, Final

import httpx

from app.core.constants import (
    DEFAULT_ILOSTAT_BASE_URL,
    DEFAULT_ILOSTAT_SOURCE,
    DEFAULT_ILOSTAT_TIMEOUT_SECONDS,
    PaisCodigo,
    TipoIndicador,
)
from app.core.logging import logger
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)


class ILOSTATConnector(IExternalDataConnector):
    """Adaptador para extracción y normalización de datos laborales de ILOSTAT."""

    DEFAULT_BASE_URL: Final[str] = DEFAULT_ILOSTAT_BASE_URL
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_ILOSTAT_TIMEOUT_SECONDS
    DEFAULT_COUNTRIES: Final[list[str]] = [
        PaisCodigo.ARG,
        PaisCodigo.URY,
        PaisCodigo.CHL,
    ]

    INDICATOR_MAPPINGS: Final[dict[str, dict[str, Any]]] = {
        "UNE_DEAP_SEX_AGE_RT_A": {
            "slug": "tasa_desempleo",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasa de desocupación armonizada por sexo y edad (%)",
        },
        "EMP_TEMP_SEX_ECO_NB_A": {
            "slug": "empleo_sector",
            "sector": "ISIC_REV4",
            "ocupacion": None,
            "nombre": "Empleo por actividad económica (CNAE / ISIC)",
        },
        "EMP_TEMP_SEX_OCU_NB_A": {
            "slug": "empleo_ocupacion",
            "sector": None,
            "ocupacion": "ISCO_08",
            "nombre": "Empleo por ocupación estandarizada (CIUO / ISCO)",
        },
        "EAR_4MTH_SEX_ECO_CUR_NB_A": {
            "slug": "salario_medio",
            "sector": "ISIC_REV4",
            "ocupacion": None,
            "nombre": "Salario medio mensual en moneda local",
        },
    }

    def __init__(
        self,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector de ILOSTAT."""
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._custom_client = client
        self._timeout = timeout
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/csv,text/plain;q=0.9,*/*;q=0.8",
        }

    @property
    def source_name(self) -> str:
        """Nombre oficial de la fuente institucional."""
        return DEFAULT_ILOSTAT_SOURCE

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

    async def check_health(self) -> bool:
        """Verifica conectividad y disponibilidad del servicio rplumber."""
        ping_url = f"{self._base_url}/"
        params = {
            "id": "UNE_DEAP_SEX_AGE_RT_A",
            "ref_area": "ARG",
            "format": ".csv",
        }
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(ping_url, params=params)
            if response.status_code == 200 and "ref_area" in response.text.lower():
                return True
            return False
        except Exception as exc:
            logger.warning("Check health fallido en ILOSTAT API: %s", str(exc))
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
        """Extrae y transforma datos de ILOSTAT a modelos normalizados."""
        target_countries = paises or self.DEFAULT_COUNTRIES
        countries_param = "+".join(target_countries)

        target_indicator_codes = self._resolve_indicator_codes(indicadores)

        records: list[RawIndicatorRecord] = []
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            tasks = []
            for code in target_indicator_codes:
                indicator_meta = self.INDICATOR_MAPPINGS[code]
                params = {
                    "id": code,
                    "ref_area": countries_param,
                    "format": ".csv",
                }
                tasks.append(
                    self._fetch_indicator_series(
                        client=client,
                        params=params,
                        indicator_code=code,
                        indicator_meta=indicator_meta,
                        periodo_desde=periodo_desde,
                        periodo_hasta=periodo_hasta,
                    )
                )

            series_results = await asyncio.gather(*tasks, return_exceptions=True)
            for code, res in zip(target_indicator_codes, series_results, strict=True):
                if isinstance(res, Exception):
                    logger.error(
                        "Error consultando indicador %s en ILOSTAT: %s",
                        code,
                        str(res),
                    )
                elif isinstance(res, list):
                    records.extend(res)
        finally:
            if should_close_client:
                await client.aclose()

        return records

    def _resolve_indicator_codes(self, requested: list[str] | None) -> list[str]:
        """Resuelve códigos oficiales a partir de códigos directos o slugs."""
        if not requested:
            return list(self.INDICATOR_MAPPINGS.keys())

        slug_to_code = {
            meta["slug"]: code for code, meta in self.INDICATOR_MAPPINGS.items()
        }

        resolved: list[str] = []
        for req in requested:
            if req in self.INDICATOR_MAPPINGS:
                resolved.append(req)
            elif req in slug_to_code:
                resolved.append(slug_to_code[req])
            else:
                logger.warning("Indicador '%s' no reconocido en ILOSTAT.", req)

        return resolved or list(self.INDICATOR_MAPPINGS.keys())

    async def _fetch_indicator_series(
        self,
        client: httpx.AsyncClient,
        params: dict[str, str],
        indicator_code: str,
        indicator_meta: dict[str, Any],
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
        max_retries: int = 2,
    ) -> list[RawIndicatorRecord]:
        """Ejecuta la solicitud HTTP con reintentos para una serie."""
        response_text: str | None = None

        for attempt in range(max_retries + 1):
            try:
                response = await client.get(self._base_url, params=params)
                response.raise_for_status()
                response_text = response.text
                break
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < max_retries:
                    backoff = 1.5 * (attempt + 1)
                    logger.warning(
                        "Fallo transitorio en ILOSTAT (%s). Reintento en %.1fs: %s",
                        indicator_code,
                        backoff,
                        str(exc),
                    )
                    await asyncio.sleep(backoff)
                else:
                    raise

        if not response_text:
            return []

        return self._parse_csv_payload(
            csv_text=response_text,
            indicator_code=indicator_code,
            indicator_meta=indicator_meta,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
        )

    def _parse_csv_payload(
        self,
        csv_text: str,
        indicator_code: str,
        indicator_meta: dict[str, Any],
        periodo_desde: str | None = None,
        periodo_hasta: str | None = None,
    ) -> list[RawIndicatorRecord]:
        """Parsea el texto CSV devuelto por rplumber."""
        records: list[RawIndicatorRecord] = []

        # Limpiamos el caracter BOM invisible del inicio del texto:
        clean_csv = csv_text.lstrip("\ufeff")

        reader = csv.DictReader(io.StringIO(clean_csv))
        hoy = date.today()

        for row in reader:
            raw_val = row.get("obs_value")
            if not raw_val or raw_val.strip() == "":
                continue

            try:
                valor = float(raw_val)
            except ValueError:
                continue

            iso3 = (row.get("ref_area") or "").strip().upper()
            periodo = (row.get("time") or "").strip()

            if not iso3 or not periodo:
                continue

            if periodo_desde and periodo < periodo_desde:
                continue
            if periodo_hasta and periodo > periodo_hasta:
                continue

            if indicator_meta["slug"] == "tasa_desempleo":
                sex = row.get("sex", "")
                classif1 = row.get("classif1", "")
                if sex != "SEX_T":
                    continue
                valid_classes = (
                    "AGE_YTHADULT_YGE15",
                    "AGE_AGGREGATE_YGE15",
                    "TOTAL",
                )
                if not any(k in classif1 for k in valid_classes):
                    continue

            record = RawIndicatorRecord(
                pais=iso3,
                sector=indicator_meta.get("sector"),
                ocupacion=indicator_meta.get("ocupacion"),
                indicador=indicator_meta["slug"],
                periodo=periodo,
                valor=valor,
                tipo=TipoIndicador.OBSERVADO,
                fuente=self.source_name,
                fecha_actualizacion=hoy,
                metadatos={
                    "ilostat_code": indicator_code,
                    "indicator_label": indicator_meta.get("nombre"),
                    "obs_status": row.get("obs_status"),
                    "classif1": row.get("classif1"),
                },
            )
            records.append(record)

        return records
