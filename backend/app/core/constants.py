"""Constantes transversales del sistema para evitar cadenas mágicas (magic strings).

Define enumeraciones y valores estáticos fuertemente tipados para entornos,
códigos de error, taxonomías de dominio, rutas de la API, almacenamiento
de ingesta y mensajes estándar del sistema.
"""

from enum import StrEnum
from typing import Final

# ==============================================================================
# 1. Identificación y Versión del Proyecto
# ==============================================================================

PROJECT_IDENTIFIER: Final[str] = "obspred"
DEFAULT_API_VERSION: Final[str] = "v1"
DEFAULT_APP_VERSION: Final[str] = "0.1.0"


# ==============================================================================
# 2. Entornos de Ejecución, Estados Operativos y Errores de API
# ==============================================================================


class AppEnvironment(StrEnum):
    """Entornos posibles de ejecución de la aplicación."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class HealthStatus(StrEnum):
    """Estados del reporte de salud y disponibilidad de la API."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class SyncStatus(StrEnum):
    """Estados del ciclo de vida de operaciones de sincronización de datos."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class FuenteEstado(StrEnum):
    """Estados posibles de frescura y disponibilidad de una fuente de datos."""

    ACTIVA = "activa"
    DESACTUALIZADA = "desactualizada"
    NO_DISPONIBLE = "no_disponible"


class ApiErrorCode(StrEnum):
    """Códigos de clasificación estandarizados para errores devueltos por la API."""

    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    DOMAIN_RULE_VIOLATION = "DOMAIN_RULE_VIOLATION"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    HTTP_EXCEPTION = "HTTP_EXCEPTION"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


# ==============================================================================
# 3. Taxonomías de Dominio: Trazabilidad, Niveles y Sectores
# ==============================================================================


class PaisCodigo(StrEnum):
    """Códigos ISO 3166-1 alpha-3 oficiales para los países del Observatorio."""

    ARG = "ARG"
    URY = "URY"
    CHL = "CHL"


class SectorEstrategico(StrEnum):
    """Identificadores de los 5 sectores estratégicos priorizados."""

    TECNOLOGIA = "tecnologia"
    SALUD = "salud"
    ENERGIA = "energia"
    TURISMO = "turismo"
    ECONOMIA_CONOCIMIENTO = "economia-conocimiento"


class TipoIndicador(StrEnum):
    """Clasificación metodológica de procedencia del dato según Principio 3."""

    OBSERVADO = "observado"
    CALCULADO = "calculado"
    PROYECCION = "proyeccion"


class IndicadorSlug(StrEnum):
    """Identificadores canónicos normalizados para indicadores del Observatorio."""

    TASA_DESEMPLEO = "tasa_desempleo"
    TASA_DESOCUPACION = "tasa_desocupacion"
    TASA_EMPLEO = "tasa_empleo"
    TASA_OCUPACION = "tasa_ocupacion"
    TASA_PARTICIPACION = "tasa_participacion"
    PARTICIPACION_LABORAL = "participacion_laboral"
    SALARIO_REAL_INDICE = "salario_real_indice"
    PUESTOS_DEMANDADOS = "puestos_demandados"
    EMPLEO_REGISTRADO_TOTAL = "empleo_registrado_total"
    PIB_PER_CAPITA = "pib_per_capita"
    MATRICULA_TERCIARIA = "matricula_terciaria"
    INDICE_EMPLEABILIDAD = "indice_empleabilidad"
    EMPLEO_SECTOR = "empleo_sector"
    EMPLEO_OCUPACION = "empleo_ocupacion"
    SALARIO_MEDIO = "salario_medio"
    INDICE_REMUNERACIONES = "indice_remuneraciones"
    IMACEC = "imacec"
    USUARIOS_INTERNET = "usuarios_internet"
    BRECHA_HABILIDADES = "brecha_habilidades"
    EMPLEO_TOTAL = "empleo_total"


class OrdenRanking(StrEnum):
    """Criterios de ordenamiento para el ranking de ocupaciones."""

    SCORE = "score"
    PUESTOS = "puestos"


def normalizar_pais_codigo(raw: str | None) -> PaisCodigo | None:
    """Normaliza cadenas sueltas o códigos ISO a PaisCodigo canónico.

    Acepta formatos estándar ISO 3166-1 (alpha-2, alpha-3, numérico) y nombres
    en español ('AR', 'ARG', 'Argentina', 'CL', 'CHL', 'Chile', 'UY', 'URY', 'Uruguay')
    sin importar espacios o mayúsculas/minúsculas.

    Args:
        raw: Código o nombre del país a normalizar.

    Returns:
        PaisCodigo | None: Miembro del enum canónico o None si no es reconocido.
    """
    if not raw:
        return None
    val = raw.strip().upper()
    if val in (PaisCodigo.ARG, "AR", "ARGENTINA", "032"):
        return PaisCodigo.ARG
    if val in (PaisCodigo.CHL, "CL", "CHILE", "152"):
        return PaisCodigo.CHL
    if val in (PaisCodigo.URY, "UY", "URUGUAY", "858"):
        return PaisCodigo.URY
    return None


class NivelEmpleabilidad(StrEnum):
    """Escala cualitativa del Índice de Empleabilidad según score numérico."""

    MUY_ALTO = "Muy Alto"
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"


class DimensionIndiceNombre(StrEnum):
    """Denominaciones canónicas de las 4 dimensiones del Índice de Empleabilidad."""

    DEMANDA_PUESTOS = "Demanda de puestos"
    ESTABILIDAD_SALARIAL = "Estabilidad salarial"
    COBERTURA_FORMATIVA = "Cobertura formativa"
    CRECIMIENTO_RECIENTE = "Crecimiento reciente"


INDICADOR_INDICE_EMPLEABILIDAD: Final[str] = "indice_empleabilidad"
DEFAULT_INDICE_METODOLOGIA_FUENTE: Final[str] = (
    "Observatorio Predictivo / Fuentes Oficiales Armonizadas"
)

INDICE_EMPLEABILIDAD_PESOS_DEFAULT: Final[dict[DimensionIndiceNombre, float]] = {
    DimensionIndiceNombre.DEMANDA_PUESTOS: 0.35,
    DimensionIndiceNombre.ESTABILIDAD_SALARIAL: 0.25,
    DimensionIndiceNombre.COBERTURA_FORMATIVA: 0.20,
    DimensionIndiceNombre.CRECIMIENTO_RECIENTE: 0.20,
}


# ==============================================================================
# 4. Umbrales Estadísticos y Reglas de Negocio para Alertas
# ==============================================================================


class AlertaNivel(StrEnum):
    """Nivel de severidad para eventos de alerta estadística."""

    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class AlertaTipo(StrEnum):
    """Clasificación del tipo de evento de alerta detectado."""

    VARIACION_SIGNIFICATIVA = "variacion_significativa"
    # Reservado metodológicamente para futura detección de reversión de tendencia
    # o quiebre de signo interperíodo:
    CAMBIO_TENDENCIA = "cambio_tendencia"


# Umbral de variación porcentual para alerta media
UMBRAL_ALERTA_MEDIO: Final[float] = 5.0

# Umbral de variación porcentual para alerta alta
UMBRAL_ALERTA_ALTO: Final[float] = 8.0


# ==============================================================================
# 5. Prefijos y Rutas HTTP de la API (Endpoints REST)
# ==============================================================================

# Rutas base y documentación
ROOT_ROUTE: Final[str] = "/"
API_V1_PREFIX: Final[str] = "/api/v1"
DOCS_ROUTE: Final[str] = "/docs"
REDOC_ROUTE: Final[str] = "/redoc"

# Recursos principales v1
HEALTH_CHECK_ROUTE: Final[str] = "/health"
HEALTH_SERVICES_ROUTE: Final[str] = f"{HEALTH_CHECK_ROUTE}/services"
HEALTH_EXTERNAL_ROUTE: Final[str] = f"{HEALTH_CHECK_ROUTE}/external"
INDICADORES_ROUTE: Final[str] = "/indicadores"
INDICE_EMPLEABILIDAD_ROUTE: Final[str] = "/indice-empleabilidad"
METRICAS_ROUTE: Final[str] = "/metricas"
TENDENCIAS_ROUTE: Final[str] = "/tendencias"
BRECHAS_ROUTE: Final[str] = "/brechas"
CATALOGO_ROUTE: Final[str] = "/catalogo"
ALERTAS_ROUTE: Final[str] = "/alertas"
FUENTE_ROUTE: Final[str] = "/fuentes"
INGESTA_ROUTE: Final[str] = "/ingesta"

# Subrutas de Ingesta y Carga de Archivos
INGESTA_UPLOAD_ROUTE: Final[str] = "/upload"
INGESTA_UPLOAD_SIMEL_ROUTE: Final[str] = f"{INGESTA_UPLOAD_ROUTE}/simel"
INGESTA_SYNC_ROUTE: Final[str] = "/sync"
INGESTA_SYNC_WORLD_BANK_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/world-bank"
INGESTA_SYNC_BCENTRAL_CHILE_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/bcentral-chile"
INGESTA_SYNC_DATOS_ARGENTINA_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/datos-argentina"
INGESTA_SYNC_SIMEL_CHILE_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/simel-chile"
INGESTA_SYNC_ILOSTAT_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/ilostat"
INGESTA_SYNC_ESCO_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/esco"
INGESTA_SYNC_CEPALSTAT_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/cepalstat"


# ==============================================================================
# 6. Etiquetas (Tags) para OpenAPI / Swagger
# ==============================================================================

OPENAPI_TAG_ROOT: Final[str] = "Root"
OPENAPI_TAG_HEALTH: Final[str] = "Health"
OPENAPI_TAG_INDICADORES: Final[str] = "Indicadores"
OPENAPI_TAG_INDICE_EMPLEABILIDAD: Final[str] = "Indice de Empleabilidad"
OPENAPI_TAG_METRICAS: Final[str] = "Métricas"
OPENAPI_TAG_TENDENCIAS: Final[str] = "Tendencias"
OPENAPI_TAG_BRECHAS: Final[str] = "Brechas"
OPENAPI_TAG_CATALOGO: Final[str] = "Catálogo"
OPENAPI_TAG_ALERTAS: Final[str] = "Alertas"
OPENAPI_TAG_FUENTE: Final[str] = "Fuentes de Datos"
OPENAPI_TAG_INGESTA: Final[str] = "Ingesta"


# ==============================================================================
# 7. Configuración de Ingesta y Almacenamiento Local de Archivos
# ==============================================================================

DEFAULT_UPLOAD_DIR: Final[str] = "data/uploads"
CSV_FILE_EXTENSION: Final[str] = ".csv"
DEFAULT_CSV_CONTENT_TYPE: Final[str] = "text/csv"
DEFAULT_MAX_UPLOAD_SIZE_BYTES: Final[int] = 52_428_800  # 50 MB
JSON_SERIALIZATION_MODE: Final[str] = "json"


# ==============================================================================
# 8. Conectores Externos y Fuentes Oficiales
# ==============================================================================

DEFAULT_HTTP_USER_AGENT: Final[str] = (
    f"ObsPred-Backend/{DEFAULT_APP_VERSION} "
    "(innova.lab Grupo 5; Observatorio Predictivo Socioeconomico)"
)

# Denominaciones canónicas oficiales de fuentes por país y ámbito
DEFAULT_INDEC_SOURCE: Final[str] = (
    "INDEC — Encuesta Permanente de Hogares / Secretaría de Trabajo"
)
DEFAULT_SENCE_CHILE_SOURCE: Final[str] = "SENCE — SABE / INE Chile — ENE y SIMEL"
DEFAULT_INE_URUGUAY_SOURCE: Final[str] = "INE Uruguay — ECH / ANEP — DGETP-UTU"
DEFAULT_REGIONAL_ARMONIZADAS_SOURCE: Final[str] = (
    "SENCE-SABE / INDEC / INE / OIT (Fuentes Oficiales Armonizadas)"
)
DEFAULT_ILOSTAT_CEPALSTAT_SOURCE: Final[str] = "ILOSTAT / CEPALSTAT Armonizado"

# Banco Mundial (World Bank Indicators API)
DEFAULT_WORLD_BANK_SOURCE: Final[str] = "World Bank"
DEFAULT_WORLD_BANK_BASE_URL: Final[str] = "https://api.worldbank.org/v2"
DEFAULT_WORLD_BANK_TIMEOUT_SECONDS: Final[float] = 30.0

# SIMEL (Sistema de Información Laboral - Chile / INE)
DEFAULT_SIMEL_CHILE_SOURCE: Final[str] = "SIMEL - INE Chile"
DEFAULT_SIMEL_CHILE_BASE_URL: Final[str] = "https://www.simel.gob.cl"
DEFAULT_SIMEL_SDMX_BASE_URL: Final[str] = "https://sdmx.ine.gob.cl/rest"
DEFAULT_SIMEL_CHILE_TIMEOUT_SECONDS: Final[float] = 30.0

# Datos Argentina (API de Datos Abiertos del Gobierno Argentino)
DEFAULT_DATOS_ARGENTINA_SOURCE_NAME: Final[str] = "Datos Argentina"
DEFAULT_DATOS_ARGENTINA_BASE_URL: Final[str] = "https://apis.datos.gob.ar/series/api"
DEFAULT_DATOS_ARGENTINA_TIMEOUT_SECONDS: Final[float] = 30.0

# Banco Central de Chile (SIETE REST WS)
DEFAULT_BCENTRAL_CHILE_SOURCE: Final[str] = "Banco Central de Chile"
DEFAULT_BCENTRAL_CHILE_BASE_URL: Final[str] = (
    "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
)
DEFAULT_BCENTRAL_CHILE_TIMEOUT_SECONDS: Final[float] = 30.0

# ILOSTAT (Organización Internacional del Trabajo - OIT)
DEFAULT_ILOSTAT_SOURCE: Final[str] = "ILOSTAT"
DEFAULT_ILOSTAT_BASE_URL: Final[str] = "https://rplumber.ilo.org/data/indicator/"
DEFAULT_ILOSTAT_TIMEOUT_SECONDS: Final[float] = 60.0

# ESCO (Clasificación Europea de Capacidades, Competencias y Ocupaciones)
DEFAULT_ESCO_SOURCE: Final[str] = "ESCO"
DEFAULT_ESCO_BASE_URL: Final[str] = "https://ec.europa.eu/esco/api/search"
DEFAULT_ESCO_TIMEOUT_SECONDS: Final[float] = 30.0

# CEPALSTAT (Comisión Económica para América Latina y el Caribe)
DEFAULT_CEPALSTAT_SOURCE: Final[str] = "CEPALSTAT"
DEFAULT_CEPALSTAT_BASE_URL: Final[str] = (
    "https://api-cepalstat.cepal.org/cepalstat/api/v1"
)
DEFAULT_CEPALSTAT_TIMEOUT_SECONDS: Final[float] = 30.0

# Timeout para verificación de salud / ping en conectores externos
DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS: Final[float] = 10.0

# Brechas de Habilidades
DEFAULT_BRECHAS_SOURCE: Final[str] = "SENCE SABE / ESCO"
DEFAULT_BRECHAS_METODOLOGIA: Final[str] = (
    "Taxonomía de referencia ESCO con demanda observada en avisos SABE."
)
DEFAULT_BRECHAS_METODOLOGIA_PERSISTIDA: Final[str] = (
    "Taxonomía ESCO con demanda y oferta formativa persistida en base de datos."
)
BRECHAS_GET_SUCCESS_MESSAGE: Final[str] = "Brechas de habilidades obtenidas con éxito."
BRECHAS_SAVE_SUCCESS_MESSAGE: Final[str] = (
    "Brechas de habilidades persistidas con éxito."
)


# ==============================================================================
# 9. Mensajes Estándar para Respuestas REST (ApiResponse)
# ==============================================================================

DEFAULT_SUCCESS_MESSAGE: Final[str] = "Operación ejecutada con éxito."
DEFAULT_ERROR_MESSAGE: Final[str] = "Ocurrió un error al procesar la solicitud."
INTERNAL_SERVER_ERROR_MESSAGE: Final[str] = "Error interno del servidor no controlado."
DATABASE_UNAVAILABLE_MESSAGE: Final[str] = (
    "No se pudo establecer conexión con el servicio de base de datos."
)
DATABASE_UNAVAILABLE_DETAIL: Final[str] = (
    "El servicio de base de datos se encuentra fuera de línea o inaccesible. "
    "Verifique que el servidor de base de datos esté activo y accesible."
)


# ==============================================================================
# Exportaciones Públicas (__all__)
# ==============================================================================

__all__ = [
    # 1. Identificación y Versión
    "PROJECT_IDENTIFIER",
    "DEFAULT_API_VERSION",
    "DEFAULT_APP_VERSION",
    # 2. Entornos, Salud, Estados y Códigos de Error
    "AppEnvironment",
    "HealthStatus",
    "SyncStatus",
    "FuenteEstado",
    "ApiErrorCode",
    # 3. Taxonomías de Dominio
    "PaisCodigo",
    "SectorEstrategico",
    "TipoIndicador",
    "IndicadorSlug",
    "OrdenRanking",
    "normalizar_pais_codigo",
    "NivelEmpleabilidad",
    "DimensionIndiceNombre",
    "INDICADOR_INDICE_EMPLEABILIDAD",
    "DEFAULT_INDICE_METODOLOGIA_FUENTE",
    "INDICE_EMPLEABILIDAD_PESOS_DEFAULT",
    # 4. Umbrales de Alertas
    "AlertaNivel",
    "AlertaTipo",
    "UMBRAL_ALERTA_MEDIO",
    "UMBRAL_ALERTA_ALTO",
    # 5. Rutas HTTP
    "ROOT_ROUTE",
    "API_V1_PREFIX",
    "DOCS_ROUTE",
    "REDOC_ROUTE",
    "HEALTH_CHECK_ROUTE",
    "HEALTH_SERVICES_ROUTE",
    "HEALTH_EXTERNAL_ROUTE",
    "INDICADORES_ROUTE",
    "INDICE_EMPLEABILIDAD_ROUTE",
    "METRICAS_ROUTE",
    "TENDENCIAS_ROUTE",
    "BRECHAS_ROUTE",
    "CATALOGO_ROUTE",
    "ALERTAS_ROUTE",
    "FUENTE_ROUTE",
    "INGESTA_ROUTE",
    "INGESTA_UPLOAD_ROUTE",
    "INGESTA_UPLOAD_SIMEL_ROUTE",
    "INGESTA_SYNC_ROUTE",
    "INGESTA_SYNC_WORLD_BANK_ROUTE",
    "INGESTA_SYNC_BCENTRAL_CHILE_ROUTE",
    "INGESTA_SYNC_DATOS_ARGENTINA_ROUTE",
    "INGESTA_SYNC_SIMEL_CHILE_ROUTE",
    "INGESTA_SYNC_ILOSTAT_ROUTE",
    "INGESTA_SYNC_ESCO_ROUTE",
    # 6. OpenAPI Tags
    "OPENAPI_TAG_ROOT",
    "OPENAPI_TAG_HEALTH",
    "OPENAPI_TAG_INDICADORES",
    "OPENAPI_TAG_INDICE_EMPLEABILIDAD",
    "OPENAPI_TAG_METRICAS",
    "OPENAPI_TAG_TENDENCIAS",
    "OPENAPI_TAG_BRECHAS",
    "OPENAPI_TAG_CATALOGO",
    "OPENAPI_TAG_ALERTAS",
    "OPENAPI_TAG_FUENTE",
    "OPENAPI_TAG_INGESTA",
    # 7. Almacenamiento e Ingesta
    "DEFAULT_UPLOAD_DIR",
    "CSV_FILE_EXTENSION",
    "DEFAULT_CSV_CONTENT_TYPE",
    "DEFAULT_MAX_UPLOAD_SIZE_BYTES",
    "JSON_SERIALIZATION_MODE",
    # 8. Conectores Externos y Fuentes
    "DEFAULT_HTTP_USER_AGENT",
    "DEFAULT_INDEC_SOURCE",
    "DEFAULT_SENCE_CHILE_SOURCE",
    "DEFAULT_INE_URUGUAY_SOURCE",
    "DEFAULT_REGIONAL_ARMONIZADAS_SOURCE",
    "DEFAULT_ILOSTAT_CEPALSTAT_SOURCE",
    "DEFAULT_WORLD_BANK_SOURCE",
    "DEFAULT_WORLD_BANK_BASE_URL",
    "DEFAULT_WORLD_BANK_TIMEOUT_SECONDS",
    "DEFAULT_SIMEL_CHILE_SOURCE",
    "DEFAULT_SIMEL_CHILE_BASE_URL",
    "DEFAULT_SIMEL_SDMX_BASE_URL",
    "DEFAULT_SIMEL_CHILE_TIMEOUT_SECONDS",
    "DEFAULT_DATOS_ARGENTINA_SOURCE_NAME",
    "DEFAULT_DATOS_ARGENTINA_BASE_URL",
    "DEFAULT_DATOS_ARGENTINA_TIMEOUT_SECONDS",
    "DEFAULT_BCENTRAL_CHILE_SOURCE",
    "DEFAULT_BCENTRAL_CHILE_BASE_URL",
    "DEFAULT_BCENTRAL_CHILE_TIMEOUT_SECONDS",
    "DEFAULT_ILOSTAT_SOURCE",
    "DEFAULT_ILOSTAT_BASE_URL",
    "DEFAULT_ILOSTAT_TIMEOUT_SECONDS",
    "DEFAULT_ESCO_SOURCE",
    "DEFAULT_ESCO_BASE_URL",
    "DEFAULT_ESCO_TIMEOUT_SECONDS",
    "DEFAULT_HEALTH_CHECK_TIMEOUT_SECONDS",
    "DEFAULT_BRECHAS_SOURCE",
    "DEFAULT_BRECHAS_METODOLOGIA",
    "DEFAULT_BRECHAS_METODOLOGIA_PERSISTIDA",
    "BRECHAS_GET_SUCCESS_MESSAGE",
    "BRECHAS_SAVE_SUCCESS_MESSAGE",
    # 9. Mensajes
    "DEFAULT_SUCCESS_MESSAGE",
    "DEFAULT_ERROR_MESSAGE",
    "INTERNAL_SERVER_ERROR_MESSAGE",
    "DATABASE_UNAVAILABLE_MESSAGE",
    "DATABASE_UNAVAILABLE_DETAIL",
]
