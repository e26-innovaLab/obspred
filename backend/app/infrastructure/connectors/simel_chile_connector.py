"""Adaptador de infraestructura para SIMEL Chile (Sistema de Información Laboral).

Provee capacidades de diagnóstico de conectividad ante el WAF de Huawei Cloud
(HTTP 418) y normalización de archivos de datos exportados desde el portal
oficial del INE Chile / Mesa de Estadísticas del Trabajo a registros de dominio
RawIndicatorRecord.
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

    Implementa el contrato IExternalDataConnector gestionando las particularidades
    técnicas del portal de SIMEL (protección activa por Web Application Firewall
    de Huawei Cloud) y ofreciendo un motor desacoplado de normalización de exportaciones
    tabulares (CSV) generadas por su explorador interactivo.
    """

    DEFAULT_BASE_URL: Final[str] = DEFAULT_SIMEL_CHILE_BASE_URL
    DEFAULT_SOURCE_NAME: Final[str] = DEFAULT_SIMEL_CHILE_SOURCE
    DEFAULT_TIMEOUT_SECONDS: Final[float] = DEFAULT_SIMEL_CHILE_TIMEOUT_SECONDS
    DEFAULT_COUNTRIES: Final[list[str]] = [PaisCodigo.CHL]

    # Mapeo de términos de sectores de SIMEL / CAENES a sectores estratégicos
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

    # Mapeo de términos de indicadores de SIMEL a slugs canónicos
    INDICATOR_SLUG_MAPPINGS: Final[dict[str, str]] = {
        "tasa de desocupacion": "tasa_desempleo",
        "tasa de desocupación": "tasa_desempleo",
        "desocupacion": "tasa_desempleo",
        "desempleo": "tasa_desempleo",
        "tasa de ocupacion": "tasa_ocupacion",
        "tasa de ocupación": "tasa_ocupacion",
        "ocupados": "empleo_total",
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
        "feb - abr": "Q1-Q2",
        "mar - may": "Q2",
        "abr - jun": "Q2",
        "abr-jun": "Q2",
        "may - jul": "Q2-Q3",
        "jun - ago": "Q3",
        "jul - sep": "Q3",
        "jul-sep": "Q3",
        "ago - oct": "Q3-Q4",
        "sep - nov": "Q4",
        "oct - dic": "Q4",
        "oct-dic": "Q4",
    }

    def __init__(
        self,
        base_url: str | None = None,
        client: httpx.AsyncClient | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Inicializa el conector de SIMEL Chile.

        Args:
            base_url: URL base opcional del portal de SIMEL.
            client: Cliente HTTP asíncrono preconfigurado opcional (para testing).
            timeout: Límite de tiempo en segundos para las solicitudes.
        """
        self._base_url = (
            base_url
            or getattr(settings, "simel_chile_base_url", None)
            or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self._custom_client = client
        self._timeout = timeout
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            ),
        }

    @property
    def source_name(self) -> str:
        """Denominación oficial de la fuente institucional."""
        return self.DEFAULT_SOURCE_NAME

    @property
    def base_url(self) -> str:
        """URL base configurada para SIMEL."""
        return self._base_url

    @property
    def timeout(self) -> float:
        """Tiempo de espera configurado en segundos."""
        return self._timeout

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea una instancia de cliente HTTP asíncrono.

        Returns:
            httpx.AsyncClient: Cliente HTTP preparado para ejecución.
        """
        if self._custom_client is not None:
            return self._custom_client
        return httpx.AsyncClient(
            headers=self._headers,
            timeout=self._timeout,
            follow_redirects=True,
        )

    async def check_health(self) -> bool:
        """Verifica la conectividad y evalúa la presencia del WAF de Huawei Cloud.

        Detecta si el portal oficial responde con HTTP 418 (código asignado
        por el WAF ante clientes sin sesión interactiva de navegador) o si
        se encuentra plenamente accesible.

        Returns:
            bool: True si el portal responde con HTTP 200 sin bloqueos,
                False si se detecta bloqueo por WAF o fallo de conexión.
        """
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(self._base_url)

            # Verificación explícita de WAF Huawei Cloud
            has_waf_cookie = any("hwwaf" in k.lower() for k in response.cookies.keys())
            has_waf_header = "block-event-id" in response.headers or any(
                "hwwaf" in k.lower() for k in response.headers.keys()
            )

            if response.status_code == 418 or has_waf_cookie or has_waf_header:
                logger.warning(
                    "SIMEL Chile health check: Bloqueo activo por Huawei Cloud WAF "
                    "(Status: %d, WAF Cookie: %s, Server: %s). "
                    "El acceso desatendido REST directo está restringido. "
                    "Se debe utilizar la ingesta por archivo exportado.",
                    response.status_code,
                    has_waf_cookie,
                    response.headers.get("server", "desconocido"),
                )
                return False

            if response.is_success:
                return True

            logger.warning(
                "SIMEL Chile health check devolvió código no exitoso: %d",
                response.status_code,
            )
            return False

        except Exception as exc:
            logger.warning(
                "SIMEL Chile health check fallido por excepción de red: %s",
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
        """Intenta extraer indicadores desde el portal remoto de SIMEL Chile.

        Dado que SIMEL cuenta con protección perimetral activa por WAF que impide
        extracciones REST sin sesión interactiva, este método ejecuta la comprobación
        y eleva SimelWafBlockedException con las instrucciones de mitigación.

        Args:
            paises: Lista opcional de códigos de países a consultar.
            indicadores: Lista opcional de indicadores a sincronizar.
            periodo_desde: Período inicial opcional.
            periodo_hasta: Período final opcional.

        Returns:
            list[RawIndicatorRecord]: Lista de indicadores normalizados si la fuente
                respondiese exitosamente sin bloqueo.

        Raises:
            SimelWafBlockedException: Al detectar el bloqueo por WAF de Huawei Cloud.
        """
        should_close_client = self._custom_client is None
        client = await self._get_client()

        try:
            response = await client.get(self._base_url)
            if response.status_code == 418 or "block-event-id" in response.headers:
                logger.error(
                    "Fallo de sincronización automática con SIMEL Chile: "
                    "Huawei Cloud WAF denegó la solicitud HTTP con código 418."
                )
                raise SimelWafBlockedException()

            response.raise_for_status()
            # Si el WAF permitiera el paso en algún entorno, retornamos lista vacía
            # para no romper el flujo del orquestador genérico.
            return []
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 418:
                raise SimelWafBlockedException() from exc
            raise
        except httpx.RequestError as exc:
            logger.error("Error de comunicación de red con SIMEL Chile: %s", str(exc))
            raise
        finally:
            if should_close_client:
                await client.aclose()

    def parse_simel_csv(
        self,
        content: str | bytes,
        filename: str = "simel_export.csv",
    ) -> list[RawIndicatorRecord]:
        """Parsea y normaliza un archivo CSV exportado desde el portal de SIMEL Chile.

        Lee datos estructurados de indicadores laborales generados por SIMEL / INE,
        limpia formatos numéricos (comas y puntos decimales), asocia sectores
        económicos estratégicos y períodos, generando registros RawIndicatorRecord.

        Args:
            content: Contenido binario o cadena del archivo CSV exportado.
            filename: Nombre original del archivo para propósitos de trazabilidad.

        Returns:
            list[RawIndicatorRecord]: Colección de indicadores de dominio normalizados.

        Raises:
            InvalidSimelCsvException: Si el archivo está vacío, no se puede decodificar
                o no contiene columnas mínimas reconocibles.
        """
        text_content = self._decode_content(content=content, filename=filename)
        if not text_content.strip():
            raise InvalidSimelCsvException(
                filename=filename,
                reason="El contenido del archivo está vacío.",
            )

        delimiter = self._detect_delimiter(text_content)
        reader = csv.reader(io.StringIO(text_content), delimiter=delimiter)

        headers = None
        for row in reader:
            if not row or not any(field.strip() for field in row):
                continue
            # Detectamos primera fila con múltiples columnas como encabezado
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
                # Omitir la fila de encabezados
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
            reason="Codificación de texto no compatible (se intentó UTF-8 y Latin-1).",
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
        periodo = self._normalize_period(raw_periodo)

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
        # Manejo de coma decimal estándar hispano (ej: 8,5 -> 8.5, 1.250,5 -> 1250.5)
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _normalize_period(self, period_str: str) -> str:
        """Normaliza descripciones de trimestres móviles o años."""
        clean = period_str.strip()
        lower = clean.lower()

        # Búsqueda de año (4 dígitos)
        match_year = re.search(r"\b(20\d\d)\b", clean)
        year = match_year.group(1) if match_year else ""

        for key, q in self.TRIMESTRE_MAPPINGS.items():
            if key in lower:
                return f"{year}-{q}" if year else q

        # Si ya viene en formato 2024-Q1 o 2024-01 o simplemente el año
        return clean

    def _normalize_indicator_slug(self, raw_indicador: str) -> str:
        """Convierte denominaciones de indicadores a slugs canónicos."""
        clean = raw_indicador.strip().lower()
        for pattern, slug in self.INDICATOR_SLUG_MAPPINGS.items():
            if pattern in clean:
                return slug

        # Generación de slug seguro por defecto
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
