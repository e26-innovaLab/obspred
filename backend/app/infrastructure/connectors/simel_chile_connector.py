"""Adaptador de infraestructura para SIMEL Chile (Sistema de Información Laboral).

Provee capacidades de:
1. Conexión directa a la API oficial SDMX RESTful de SIMEL (.Stat Suite del INE Chile)
   en https://sdmx.ine.gob.cl/rest/data/ según la Guía Oficial de Uso del INE.
2. Diagnóstico del portal web interactivo (Huawei Cloud WAF / HTTP 418).
3. Normalización de exportaciones tabulares (CSV) y respuestas SDMX a registros de
   dominio RawIndicatorRecord para el Observatorio.
"""

import csv
import io
import re
from datetime import date
from typing import Any, Final

import httpx

from app.core.config import settings
from app.core.constants import (
    DEFAULT_SIMEL_CHILE_BASE_URL,
    DEFAULT_SIMEL_CHILE_SOURCE,
    DEFAULT_SIMEL_CHILE_TIMEOUT_SECONDS,
    DEFAULT_SIMEL_SDMX_BASE_URL,
    PaisCodigo,
    SectorEstrategico,
    TipoIndicador,
)
from app.core.logging import logger
from app.domain.exceptions.simel_exceptions import (
    InvalidSimelCsvException,
    SimelWafBlockedException,
)
from app.domain.interfaces.external_connector import (
    IExternalDataConnector,
    RawIndicatorRecord,
)


class SimelChileConnector(IExternalDataConnector):
    """Adaptador para el Sistema de Información del Mercado Laboral (SIMEL Chile).

    Implementa el contrato IExternalDataConnector consultando la API SDMX RESTful
    oficial de .Stat Suite administrada por el Instituto Nacional de Estadísticas
    (INE Chile) y soportando la ingesta de exportaciones tabulares generadas desde
    el explorador interactivo.
    """

    DEFAULT_BASE_URL: Final[str] = DEFAULT_SIMEL_CHILE_BASE_URL
    DEFAULT_SDMX_BASE_URL: Final[str] = DEFAULT_SIMEL_SDMX_BASE_URL
    DEFAULT_SOURCE_NAME: Final[str] = DEFAULT_SIMEL_CHILE_SOURCE
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_SIMEL_CHILE_TIMEOUT_SECONDS
    DEFAULT_COUNTRIES: Final[list[str]] = [PaisCodigo.CHL]

    # Mapeo de ramas CIIU4 / CAENES a sectores estratégicos del Observatorio
    RAMA_LETTER_MAPPINGS: Final[dict[str, str]] = {
        "J": SectorEstrategico.TECNOLOGIA,
        "Q": SectorEstrategico.SALUD,
        "D": SectorEstrategico.ENERGIA,
        "B": SectorEstrategico.ENERGIA,
        "I": SectorEstrategico.TURISMO,
        "M": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
    }

    # Mapeo de términos de sectores de SIMEL a sectores estratégicos
    SECTOR_MAPPINGS: Final[dict[str, str]] = {
        "informacion y comunicaciones": SectorEstrategico.TECNOLOGIA,
        "información y comunicaciones": SectorEstrategico.TECNOLOGIA,
        "tecnologia": SectorEstrategico.TECNOLOGIA,
        "tecnología": SectorEstrategico.TECNOLOGIA,
        "actividades de atencion de la salud humana": SectorEstrategico.SALUD,
        "actividades de atención de la salud humana": SectorEstrategico.SALUD,
        "salud humana": SectorEstrategico.SALUD,
        "salud": SectorEstrategico.SALUD,
        "suministro de electricidad": SectorEstrategico.ENERGIA,
        "electricidad, gas, vapor": SectorEstrategico.ENERGIA,
        "explotacion de minas y canteras": SectorEstrategico.ENERGIA,
        "explotación de minas y canteras": SectorEstrategico.ENERGIA,
        "mineria": SectorEstrategico.ENERGIA,
        "energía": SectorEstrategico.ENERGIA,
        "energia": SectorEstrategico.ENERGIA,
        "actividades de alojamiento y de servicio de comidas": (
            SectorEstrategico.TURISMO
        ),
        "alojamiento y comidas": SectorEstrategico.TURISMO,
        "turismo": SectorEstrategico.TURISMO,
        "actividades profesionales, cientificas y tecnicas": (
            SectorEstrategico.ECONOMIA_CONOCIMIENTO
        ),
        "actividades profesionales, científicas y técnicas": (
            SectorEstrategico.ECONOMIA_CONOCIMIENTO
        ),
        "economia del conocimiento": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
        "economía del conocimiento": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
    }

    # Flujos de datos (Dataflows) SDMX del INE priorizados para el Observatorio
    SDMX_DATAFLOW_CONFIG: Final[list[dict[str, Any]]] = [
        {
            "dataflow": "DF_TDES_SEXO",
            "dimension_key": "M.TDES._T.AS",
            "indicador": "tasa_desempleo",
            "sector": None,
            "unidad": "porcentaje",
        },
        {
            "dataflow": "DF_TOCU_SEXO",
            "dimension_key": "M.TOCU._T.AS",
            "indicador": "tasa_ocupacion",
            "sector": None,
            "unidad": "porcentaje",
        },
        {
            "dataflow": "DF_TP_SEXO",
            "dimension_key": "M.TP._T.AS",
            "indicador": "tasa_participacion",
            "sector": None,
            "unidad": "porcentaje",
        },
        {
            "dataflow": "DF_OCURAMA_RAMA_SEXO",
            "dimension_key": "M.OCURAMA._T.AS.J",
            "indicador": "empleo_sector",
            "sector": SectorEstrategico.TECNOLOGIA,
            "unidad": "personas",
        },
        {
            "dataflow": "DF_OCURAMA_RAMA_SEXO",
            "dimension_key": "M.OCURAMA._T.AS.Q",
            "indicador": "empleo_sector",
            "sector": SectorEstrategico.SALUD,
            "unidad": "personas",
        },
        {
            "dataflow": "DF_OCURAMA_RAMA_SEXO",
            "dimension_key": "M.OCURAMA._T.AS.D",
            "indicador": "empleo_sector",
            "sector": SectorEstrategico.ENERGIA,
            "unidad": "personas",
        },
        {
            "dataflow": "DF_OCURAMA_RAMA_SEXO",
            "dimension_key": "M.OCURAMA._T.AS.I",
            "indicador": "empleo_sector",
            "sector": SectorEstrategico.TURISMO,
            "unidad": "personas",
        },
        {
            "dataflow": "DF_OCURAMA_RAMA_SEXO",
            "dimension_key": "M.OCURAMA._T.AS.M",
            "indicador": "empleo_sector",
            "sector": SectorEstrategico.ECONOMIA_CONOCIMIENTO,
            "unidad": "personas",
        },
    ]

    # Mapeo de términos de indicadores de SIMEL a slugs canónicos
    INDICATOR_SLUG_MAPPINGS: Final[dict[str, str]] = {
        "tasa de desocupacion": "tasa_desempleo",
        "tasa de desocupación": "tasa_desempleo",
        "tdes": "tasa_desempleo",
        "desocupacion": "tasa_desempleo",
        "desempleo": "tasa_desempleo",
        "tasa de ocupacion": "tasa_ocupacion",
        "tasa de ocupación": "tasa_ocupacion",
        "tocu": "tasa_ocupacion",
        "ocupados": "empleo_total",
        "ocurama": "empleo_sector",
        "ocupados por rama": "empleo_sector",
        "ocupados segun rama": "empleo_sector",
        "ocupados según rama": "empleo_sector",
        "ocupados por grupo ocupacional": "empleo_ocupacion",
        "tasa de participacion": "tasa_participacion",
        "tasa de participación": "tasa_participacion",
        "fuerza de trabajo": "fuerza_trabajo",
        "presion laboral": "tasa_presion_laboral",
        "presión laboral": "tasa_presion_laboral",
    }

    # Mapeo de trimestres móviles textuales a notación canónica trimestral
    TRIMESTRE_MAPPINGS: Final[dict[str, str]] = {
        "ene - mar": "Q1",
        "ene-mar": "Q1",
        "abr - jun": "Q2",
        "abr-jun": "Q2",
        "jul - sep": "Q3",
        "jul-sep": "Q3",
        "oct - dic": "Q4",
        "oct-dic": "Q4",
    }

    def __init__(
        self,
        base_url: str | None = None,
        sdmx_base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector de SIMEL Chile.

        Args:
            base_url: URL base opcional del portal interactivo de SIMEL.
            sdmx_base_url: URL base opcional de la API SDMX del INE (.Stat Suite).
            client: Cliente HTTP asíncrono opcional (para testing o aislamiento).
            timeout: Tiempo máximo de espera en segundos por llamada.
        """
        self._portal_base_url = (
            base_url
            or getattr(settings, "simel_chile_base_url", None)
            or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self._sdmx_base_url = (
            sdmx_base_url
            or getattr(settings, "simel_chile_sdmx_base_url", None)
            or self.DEFAULT_SDMX_BASE_URL
        ).rstrip("/")
        self._custom_client = client
        self._timeout = timeout
        self._headers = {
            "User-Agent": "ObsPred-Backend/1.0 (SIMEL INE Chile Connector)",
            "Accept": "application/vnd.sdmx.data+csv,text/csv,text/plain;q=0.9,*/*",
        }

    @property
    def source_name(self) -> str:
        """Denominación oficial de la fuente institucional."""
        return self.DEFAULT_SOURCE_NAME

    @property
    def base_url(self) -> str:
        """URL base configurada para la API SDMX de SIMEL / INE."""
        return self._sdmx_base_url

    @property
    def portal_url(self) -> str:
        """URL del portal web interactivo de SIMEL."""
        return self._portal_base_url

    @property
    def timeout(self) -> float:
        """Tiempo de espera configurado en segundos."""
        return self._timeout

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea una instancia de cliente HTTP asíncrono."""
        if self._custom_client is not None:
            return self._custom_client
        return httpx.AsyncClient(
            headers=self._headers,
            timeout=self._timeout,
            follow_redirects=True,
        )

    async def check_health(self) -> bool:
        """Verifica la disponibilidad operativa de la API oficial de SIMEL.

        Consulta el catálogo de flujos de datos (dataflow) de la API SDMX oficial
        del INE Chile (`https://sdmx.ine.gob.cl/rest/dataflow/CL01`).

        Returns:
            bool: True si la API oficial SDMX responde satisfactoriamente (HTTP 200),
                False si ocurre un fallo de conexión o timeout.
        """
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            # Consulta al catálogo SDMX oficial del INE
            catalog_url = f"{self._sdmx_base_url}/dataflow/CL01"
            response = await client.get(catalog_url)
            if response.is_success:
                logger.info(
                    "SIMEL Chile SDMX API (INE) operativa y accesible (Status: %d).",
                    response.status_code,
                )
                return True

            logger.warning(
                "SIMEL Chile SDMX API devolvió status no exitoso: %d",
                response.status_code,
            )
            return False

        except Exception as exc:
            logger.warning(
                "SIMEL Chile SDMX health check fallido por excepción de red: %s",
                str(exc),
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
        """Extrae indicadores oficiales en vivo desde la API SDMX de SIMEL / INE.

        Consume los flujos de datos oficiales de .Stat Suite para Chile (CL01),
        extrayendo desempleo, ocupación, participación laboral y empleo por
        sectores estratégicos.

        Args:
            paises: Lista opcional de países (filtra únicamente Chile 'CHL').
            indicadores: Lista opcional de slugs de indicadores a sincronizar.
            periodo_desde: Período inicial opcional (ej. '2023').
            periodo_hasta: Período final opcional (ej. '2024').

        Returns:
            list[RawIndicatorRecord]: Colección inmutable de registros normalizados.

        Raises:
            SimelWafBlockedException: Si el endpoint estuviese temporalmente bloqueado.
        """
        if paises and PaisCodigo.CHL not in paises:
            return []

        should_close_client = self._custom_client is None
        client = await self._get_client()
        records: list[RawIndicatorRecord] = []

        try:
            for conf in self.SDMX_DATAFLOW_CONFIG:
                target_slug = conf["indicador"]
                if indicadores and target_slug not in indicadores:
                    continue

                dataflow = conf["dataflow"]
                dimension_key = conf["dimension_key"]
                query_url = (
                    f"{self._sdmx_base_url}/data/CL01,{dataflow},1.0/"
                    f"{dimension_key}?format=csv"
                )
                if periodo_desde:
                    query_url += f"&startPeriod={periodo_desde}"
                if periodo_hasta:
                    query_url += f"&endPeriod={periodo_hasta}"

                try:
                    resp = await client.get(query_url)
                    if resp.status_code == 418:
                        raise SimelWafBlockedException()

                    resp.raise_for_status()
                    series_records = self._parse_sdmx_csv(
                        csv_text=resp.text,
                        indicador_default=target_slug,
                        sector_default=conf["sector"],
                    )
                    records.extend(series_records)
                except SimelWafBlockedException:
                    raise
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 418:
                        raise SimelWafBlockedException() from exc
                    logger.warning(
                        "Error al consultar dataflow '%s' en SIMEL SDMX: %s",
                        dataflow,
                        str(exc),
                    )
                except Exception as exc:
                    logger.warning(
                        "Fallo al procesar serie SDMX '%s': %s",
                        dataflow,
                        str(exc),
                    )

            logger.info(
                "Extracción SDMX de SIMEL Chile completada: %d registros.",
                len(records),
            )
            return records
        finally:
            if should_close_client:
                await client.aclose()

    def parse_simel_csv(
        self,
        content: str | bytes,
        filename: str = "simel_export.csv",
    ) -> list[RawIndicatorRecord]:
        """Parsea y normaliza un archivo CSV exportado desde SIMEL o de su API SDMX.

        Admite tanto la estructura tabular generada por el Explorador de Datos
        de SIMEL como el formato exportado por la API REST SDMX de .Stat Suite.

        Args:
            content: Contenido binario o cadena del archivo CSV.
            filename: Nombre original del archivo para fines de trazabilidad.

        Returns:
            list[RawIndicatorRecord]: Colección de indicadores de dominio normalizados.

        Raises:
            InvalidSimelCsvException: Si el archivo está vacío o sin columnas válidas.
        """
        text_content = self._decode_content(content=content, filename=filename)
        if not text_content.strip():
            raise InvalidSimelCsvException(
                filename=filename,
                reason="El contenido del archivo está vacío.",
            )

        # Si el CSV proviene de la API SDMX (.Stat Suite), usamos el parser específico
        if "OBS_VALUE" in text_content and "TIME_PERIOD" in text_content:
            return self._parse_sdmx_csv(csv_text=text_content)

        # De lo contrario, usamos el parser del explorador interactivo
        delimiter = self._detect_delimiter(text_content)
        reader = csv.reader(io.StringIO(text_content), delimiter=delimiter)

        headers = None
        for row in reader:
            if not row or not any(field.strip() for field in row):
                continue
            cleaned_row = [c.strip().lower() for c in row]
            if len(cleaned_row) >= 2:
                headers = cleaned_row
                break

        if not headers:
            raise InvalidSimelCsvException(
                filename=filename,
                reason="No se localizó una fila válida de encabezados.",
            )

        col_indices = self._resolve_column_indices(headers=headers, filename=filename)
        dict_reader = csv.DictReader(
            io.StringIO(text_content),
            delimiter=delimiter,
            fieldnames=headers,
        )

        records: list[RawIndicatorRecord] = []
        is_first = True

        for row_num, row in enumerate(dict_reader, start=1):
            if is_first:
                is_first = False
                continue

            record = self._transform_row_to_record(
                row=row,
                col_indices=col_indices,
                row_num=row_num,
            )
            if record is not None:
                records.append(record)

        if not records:
            raise InvalidSimelCsvException(
                filename=filename,
                reason="No se extrajo ninguna observación válida con valor numérico.",
            )

        logger.info(
            "Archivo SIMEL '%s' procesado con éxito: %d registros normalizados.",
            filename,
            len(records),
        )
        return records

    def _parse_sdmx_csv(
        self,
        csv_text: str,
        indicador_default: str = "indicador_laboral",
        sector_default: str | None = None,
    ) -> list[RawIndicatorRecord]:
        """Parsea el formato CSV devuelto por la API SDMX de .Stat Suite."""
        reader = csv.DictReader(io.StringIO(csv_text))
        records: list[RawIndicatorRecord] = []

        for _row_num, row in enumerate(reader, start=1):
            raw_val = (row.get("OBS_VALUE") or "").strip()
            parsed_val = self._parse_numeric_value(raw_val)
            if parsed_val is None:
                continue

            raw_time = (row.get("TIME_PERIOD") or "").strip()
            if not raw_time:
                continue
            periodo, trimestre = self._parse_sdmx_time_and_quarter(raw_time)
            if not periodo:
                continue

            raw_ind = (row.get("INDICADOR") or "").strip()
            indicador_slug = (
                self._normalize_indicator_slug(raw_ind)
                if raw_ind
                else indicador_default
            )

            # Mapeo de sector por columna RAMA
            rama_letter = (row.get("RAMA") or "").strip()
            sector = (
                self.RAMA_LETTER_MAPPINGS.get(rama_letter, sector_default)
                if rama_letter
                else sector_default
            )

            sexo = (row.get("SEXO") or "").strip()
            area = (row.get("AREA_REF") or "").strip()
            unidad = (row.get("UNIDAD") or "").strip()

            metadata: dict[str, Any] = {
                "fuente_primaria": (
                    row.get("FUENTE")
                    or "Encuesta Nacional de Empleo (ENE) - SIMEL Chile"
                ),
                "dataflow": row.get("DATAFLOW", ""),
                "area_referencia": area,
                "sexo": sexo,
                "unidad_medida": unidad,
            }

            records.append(
                RawIndicatorRecord(
                    pais=PaisCodigo.CHL,
                    sector=sector,
                    ocupacion=None,
                    indicador=indicador_slug,
                    periodo=periodo,
                    trimestre=trimestre,
                    valor=parsed_val,
                    tipo=TipoIndicador.OBSERVADO,
                    fuente=self.DEFAULT_SOURCE_NAME,
                    fecha_actualizacion=date.today(),
                    metadatos=metadata,
                )
            )

        return records

    @staticmethod
    def _extract_trimestre(periodo: str | None) -> str | None:
        """Extrae la notación de trimestre (ej. 'Q1', 'Q2') si existe en el período."""
        if not periodo:
            return None
        match = re.search(r"Q([1-4])", periodo, re.IGNORECASE)
        return f"Q{match.group(1)}" if match else None

    def _parse_sdmx_time_and_quarter(
        self, time_str: str
    ) -> tuple[str | None, str | None]:
        """Traduce formatos temporales SDMX a período (año) y trimestre.

        Solo mapea los trimestres cerrados oficiales del calendario:
        - Mes 03 (Ene-Mar) -> ('YYYY', 'Q1')
        - Mes 06 (Abr-Jun) -> ('YYYY', 'Q2')
        - Mes 09 (Jul-Sep) -> ('YYYY', 'Q3')
        - Mes 12 (Oct-Dic) -> ('YYYY', 'Q4')
        Los trimestres móviles intermedios retornan (None, None).
        """
        clean = time_str.strip()
        if "/P3M" in clean or "/P1M" in clean:
            date_part = clean.split("/")[0]
            parts = date_part.split("-")
            if len(parts) >= 2:
                year = parts[0]
                month = int(parts[1])
                quarter_map = {3: "Q1", 6: "Q2", 9: "Q3", 12: "Q4"}
                if month in quarter_map:
                    return year, quarter_map[month]
                return None, None
        return clean, self._extract_trimestre(clean)

    def _normalize_sdmx_time_period(self, time_str: str) -> str | None:
        p, _ = self._parse_sdmx_time_and_quarter(time_str)
        return p

    def _decode_content(self, content: str | bytes, filename: str) -> str:
        """Decodifica el contenido binario probando codificaciones comunes."""
        if isinstance(content, str):
            return content

        for encoding in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise InvalidSimelCsvException(
            filename=filename,
            reason="Codificación no compatible (se intentó UTF-8 y Latin-1).",
        )

    def _detect_delimiter(self, text: str) -> str:
        """Determina si el delimitador CSV es coma, punto y coma o tabulación."""
        first_lines = "\n".join(text.splitlines()[:5])
        if first_lines.count(";") > first_lines.count(","):
            return ";"
        if first_lines.count("\t") > first_lines.count(","):
            return "\t"
        return ","

    def _resolve_column_indices(
        self,
        headers: list[str],
        filename: str,
    ) -> dict[str, str]:
        """Mapea los nombres de columnas presentes a los campos de dominio."""
        resolved: dict[str, str] = {}

        for h in headers:
            clean = (
                h.strip()
                .lower()
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            if any(k in clean for k in ["indicador", "metrica", "tema", "variable"]):
                resolved.setdefault("indicador", h)
            elif any(
                k in clean for k in ["periodo", "trimestre", "anio", "fecha", "tiempo"]
            ):
                resolved.setdefault("periodo", h)
            elif any(k in clean for k in ["valor", "dato", "cifra", "observacion"]):
                resolved.setdefault("valor", h)
            elif any(k in clean for k in ["sector", "rama", "actividad", "caenes"]):
                resolved.setdefault("sector", h)
            elif any(k in clean for k in ["ocupacion", "grupo", "oficio", "ciuo"]):
                resolved.setdefault("ocupacion", h)
            elif any(k in clean for k in ["sexo", "genero"]):
                resolved.setdefault("sexo", h)
            elif any(k in clean for k in ["unidad", "medida"]):
                resolved.setdefault("unidad", h)

        if "periodo" not in resolved or "valor" not in resolved:
            raise InvalidSimelCsvException(
                filename=filename,
                reason=(
                    "Faltan columnas requeridas obligatorias ('periodo' y 'valor'). "
                    f"Columnas detectadas: {headers}"
                ),
            )

        return resolved

    def _transform_row_to_record(
        self,
        row: dict[str, str | None],
        col_indices: dict[str, str],
        row_num: int,
    ) -> RawIndicatorRecord | None:
        """Transforma una fila del diccionario CSV a RawIndicatorRecord."""
        raw_val = (row.get(col_indices["valor"]) or "").strip()
        parsed_val = self._parse_numeric_value(raw_val)
        if parsed_val is None:
            return None

        raw_periodo = (row.get(col_indices["periodo"]) or "").strip()
        if not raw_periodo:
            return None
        periodo, trimestre = self._parse_csv_period_and_quarter(raw_periodo)

        raw_indicador = (
            row.get(col_indices.get("indicador", "")) or "indicador_laboral"
        ).strip()
        indicador_slug = self._normalize_indicator_slug(raw_indicador)

        raw_sector = (row.get(col_indices.get("sector", "")) or "").strip() or None
        normalized_sector = self._map_sector(raw_sector) if raw_sector else None

        raw_ocupacion = (
            row.get(col_indices.get("ocupacion", "")) or ""
        ).strip() or None

        raw_sexo = (row.get(col_indices.get("sexo", "")) or "").strip() or None
        raw_unidad = (row.get(col_indices.get("unidad", "")) or "").strip() or None

        metadata: dict[str, Any] = {
            "archivo_origen": "SIMEL Chile CSV Export",
            "fila_csv": row_num,
            "fuente_primaria": "Encuesta Nacional de Empleo (ENE) - INE Chile",
        }
        if raw_sector:
            metadata["sector_original"] = raw_sector
        if raw_sexo:
            metadata["sexo"] = raw_sexo
        if raw_unidad:
            metadata["unidad_medida"] = raw_unidad

        return RawIndicatorRecord(
            pais=PaisCodigo.CHL,
            sector=normalized_sector,
            ocupacion=raw_ocupacion,
            indicador=indicador_slug,
            periodo=periodo,
            trimestre=trimestre,
            valor=parsed_val,
            tipo=TipoIndicador.OBSERVADO,
            fuente=self.DEFAULT_SOURCE_NAME,
            fecha_actualizacion=date.today(),
            metadatos=metadata,
        )

    def _parse_numeric_value(self, val_str: str) -> float | None:
        """Limpia cadenas numéricas con comas o porcentajes a float."""
        if not val_str or val_str in ["-", "...", "nan", "null"]:
            return None

        cleaned = val_str.replace("%", "").strip()
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _parse_csv_period_and_quarter(self, period_str: str) -> tuple[str, str | None]:
        """Normaliza descripciones de períodos en CSV separando año y trimestre."""
        clean = period_str.strip()
        lower = clean.lower()

        match_year = re.search(r"\b(20\d\d)\b", clean)
        year = match_year.group(1) if match_year else clean

        for key, q in self.TRIMESTRE_MAPPINGS.items():
            if key in lower:
                return year, q

        match_q = re.search(r"Q([1-4])", clean, re.IGNORECASE)
        trimestre = f"Q{match_q.group(1)}" if match_q else None
        return year, trimestre

    def _normalize_period(self, period_str: str) -> str:
        p, _ = self._parse_csv_period_and_quarter(period_str)
        return p

    def _normalize_indicator_slug(self, raw_indicador: str) -> str:
        """Convierte denominaciones de indicadores a slugs canónicos."""
        clean = raw_indicador.strip().lower()
        for pattern, slug in self.INDICATOR_SLUG_MAPPINGS.items():
            if pattern in clean:
                return slug

        slug = re.sub(r"[^\w\s-]", "", clean).strip()
        return re.sub(r"[-\s]+", "_", slug)[:100]

    def _map_sector(self, raw_sector: str) -> str | None:
        """Asocia la rama de actividad de SIMEL al sector estratégico."""
        clean = raw_sector.strip().lower()
        if clean in ["total", "nacional", "pais", "todos"]:
            return None
        clean_no_punct = re.sub(r"[^\w\s]", "", clean)
        for term, sector_enum in self.SECTOR_MAPPINGS.items():
            term_no_punct = re.sub(r"[^\w\s]", "", term)
            if term in clean or term_no_punct in clean_no_punct:
                return sector_enum.value
        return raw_sector
