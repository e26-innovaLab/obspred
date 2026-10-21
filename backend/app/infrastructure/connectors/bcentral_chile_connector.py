"""Adaptador de infraestructura para consumir series del Banco Central de Chile (SIETE REST WS)."""

from datetime import date
import json
from typing import Any, Final
import httpx

from app.core.config import settings
from app.core.constants import (
    DEFAULT_BCENTRAL_CHILE_BASE_URL,
    DEFAULT_BCENTRAL_CHILE_SOURCE,
    DEFAULT_BCENTRAL_CHILE_TIMEOUT_SECONDS,
    PaisCodigo,
    TipoIndicador,
)
from app.core.logging import logger
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)


class BCentralChileConnector(IExternalDataConnector):
    """Adaptador de infraestructura para consumir SIETE REST WS del Banco Central de Chile.

    Provee extracción y normalización de indicadores laborales, económicos
    y productivos para Chile (CHL) mediante autenticación BDE.
    """

    DEFAULT_BASE_URL: Final[str] = DEFAULT_BCENTRAL_CHILE_BASE_URL
    DEFAULT_COUNTRIES: list[str] = [
        PaisCodigo.CHL,
    ]
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_BCENTRAL_CHILE_TIMEOUT_SECONDS

    # Catálogo de indicadores oficiales verificados y su mapeo al modelo de dominio
    INDICATOR_MAPPINGS: dict[str, dict[str, Any]] = {
        # --- Dimensión Laboral ---
        "F049.DES.TAS.HIST.10.M": {
            "slug": "tasa_desocupacion",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tasas de desocupación nacional (serie histórica)",
            "unidad": "porcentaje",
        },
        "F049.RMU.IND.HIST.81.M": {
            "slug": "indice_remuneraciones",
            "sector": None,
            "ocupacion": None,
            "nombre": "Índice de Remuneraciones histórico",
            "unidad": "indice",
        },
        # --- Dimensión Productiva ---
        "F032.IMC.IND.Z.Z.EP18.Z.Z.0.M": {
            "slug": "imacec",
            "sector": "Productivo General",
            "ocupacion": None,
            "nombre": "Índice Mensual de Actividad Económica (IMACEC base 2018)",
            "unidad": "indice",
        },
        # --- Dimensión Económica ---
        "F073.TCO.PRE.Z.D": {
            "slug": "dolar_observado",
            "sector": None,
            "ocupacion": None,
            "nombre": "Tipo de cambio nominal (dólar observado CLP/USD)",
            "unidad": "clp",
        },
        "F074.IPC.VAR.Z.Z.C.M": {
            "slug": "inflacion_ipc",
            "sector": None,
            "ocupacion": None,
            "nombre": "IPC General histórico variación mensual",
            "unidad": "porcentaje",
        },
    }

    def __init__(
        self,
        base_url: str | None = None,
        user: str | None = None,
        password: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector del Banco Central de Chile."""
        self._base_url = (
            base_url
            or getattr(settings, "bcentral_chile_base_url", None)
            or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self._user = user or getattr(settings, "bcentral_chile_user", "")
        self._password = password or getattr(settings, "bcentral_chile_pass", "")
        self._custom_client = client
        self._timeout = timeout

    @property
    def source_name(self) -> str:
        """Nombre oficial de la fuente institucional."""
        return DEFAULT_BCENTRAL_CHILE_SOURCE

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
        return httpx.AsyncClient(timeout=self._timeout)

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
                logger.warning("Indicador '%s' no reconocido en BCentral Chile.", req)

        return resolved or list(self.INDICATOR_MAPPINGS.keys())

    @staticmethod
    def _build_date_params(desde: str | None, hasta: str | None) -> tuple[str, str]:
        """Normaliza los parámetros firstdate y lastdate en formato YYYY-MM-DD."""
        current_year = date.today().year
        first = (
            f"{desde}-01-01" if desde and len(desde) == 4 else (desde or "2020-01-01")
        )
        last = (
            f"{hasta}-12-31"
            if hasta and len(hasta) == 4
            else (hasta or f"{current_year}-12-31")
        )
        return first, last

    async def check_health(self) -> bool:
        """Verifica conectividad y credenciales con SIETE REST WS."""
        current_year = date.today().year
        # Serie de control: Dólar observado para primeros días del año
        params = {
            "user": self._user,
            "pass": self._password,
            "firstdate": f"{current_year}-01-01",
            "lastdate": f"{current_year}-01-10",
            "timeseries": "F073.TCO.PRE.Z.D",
            "function": "GetSeries",
        }
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(self._base_url, params=params)
            if response.status_code != 200:
                return False

            try:
                raw_text = response.content.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = response.content.decode("latin-1")

            data = json.loads(raw_text)
            return data.get("Codigo") == 0
        except Exception as exc:
            logger.warning(
                "Check health fallido en Banco Central de Chile: %s", str(exc)
            )
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
        """Extrae y transforma observaciones de SIETE a modelos normalizados RawIndicatorRecord."""
        if paises:
            norm_countries = [
                p.value if hasattr(p, "value") else str(p).upper() for p in paises
            ]
            if (
                PaisCodigo.CHL.value not in norm_countries
                and "CHL" not in norm_countries
            ):
                return []

        target_series_codes = self._resolve_indicator_codes(indicadores)
        first_date, last_date = self._build_date_params(periodo_desde, periodo_hasta)

        records: list[RawIndicatorRecord] = []
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            for series_code in target_series_codes:
                indicator_meta = self.INDICATOR_MAPPINGS[series_code]
                params = {
                    "user": self._user,
                    "pass": self._password,
                    "firstdate": first_date,
                    "lastdate": last_date,
                    "timeseries": series_code,
                    "function": "GetSeries",
                }

                try:
                    response = await client.get(self._base_url, params=params)
                    response.raise_for_status()

                    # Decodificación protegida contra acentos de la API
                    try:
                        raw_text = response.content.decode("utf-8")
                    except UnicodeDecodeError:
                        raw_text = response.content.decode("latin-1")

                    data = json.loads(raw_text)
                except Exception as exc:
                    logger.error(
                        "Error en petición HTTP a SIETE para serie %s: %s",
                        series_code,
                        str(exc),
                    )
                    continue

                if data.get("Codigo") != 0:
                    logger.error(
                        "Error devuelto por SIETE al consultar %s: %s",
                        series_code,
                        data.get("Descripcion"),
                    )
                    continue

                series_data = data.get("Series", {})
                observations: list[dict[str, Any]] = series_data.get("Obs", [])
                hoy = date.today()

                for obs in observations:
                    raw_val = obs.get("value")
                    date_str = obs.get("indexDateString")

                    if raw_val is None or raw_val == "":
                        continue

                    try:
                        valor = float(str(raw_val).replace(",", "."))
                    except (ValueError, TypeError):
                        continue

                    # Formato habitual devuelto por SIETE: 'DD-MM-YYYY'
                    periodo = str(date_str)
                    if date_str and "-" in date_str:
                        parts = date_str.split("-")
                        if len(parts) == 3:
                            periodo = parts[
                                2
                            ]  # Año representativo para agregación anual

                    record = RawIndicatorRecord(
                        pais=PaisCodigo.CHL.value,
                        sector=indicator_meta.get("sector"),
                        ocupacion=indicator_meta.get("ocupacion"),
                        indicador=indicator_meta["slug"],
                        periodo=periodo,
                        valor=valor,
                        tipo=TipoIndicador.OBSERVADO,
                        fuente=self.source_name,
                        fecha_actualizacion=hoy,
                        metadatos={
                            "series_code": series_code,
                            "descrip_esp": series_data.get("descripEsp"),
                            "indicator_label": indicator_meta.get("nombre"),
                            "unidad": indicator_meta.get("unidad"),
                            "index_date_string": date_str,
                            "status_code": obs.get("statusCode"),
                        },
                    )
                    records.append(record)
        finally:
            if should_close_client:
                await client.aclose()

        return records
