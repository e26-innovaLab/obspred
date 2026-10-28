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


class ApiErrorCode(StrEnum):
    """Códigos de clasificación estandarizados para errores devueltos por la API."""

    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    DOMAIN_RULE_VIOLATION = "DOMAIN_RULE_VIOLATION"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    HTTP_EXCEPTION = "HTTP_EXCEPTION"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


class SyncStatus(StrEnum):
    """Estados del ciclo de vida de operaciones de sincronización de datos."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


# ==============================================================================
# 3. Taxonomías de Dominio: Trazabilidad, Niveles y Sectores
# ==============================================================================


class TipoIndicador(StrEnum):
    """Clasificación metodológica de procedencia del dato según Principio 3."""

    OBSERVADO = "observado"
    CALCULADO = "calculado"
    PROYECCION = "proyeccion"


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


INDICADOR_INDICE_EMPLEABILIDAD: Final[str] = "indice_empleabilidad"
DEFAULT_INDICE_METODOLOGIA_FUENTE: Final[str] = (
    "Observatorio Predictivo / Fuentes Oficiales Armonizadas"
)


# ==============================================================================
# 4. Prefijos y Rutas HTTP de la API
# ==============================================================================

ROOT_ROUTE: Final[str] = "/"
API_V1_PREFIX: Final[str] = "/api/v1"
HEALTH_CHECK_ROUTE: Final[str] = "/health"
INDICADORES_ROUTE: Final[str] = "/indicadores"
INDICE_EMPLEABILIDAD_ROUTE: Final[str] = "/indice-empleabilidad"
INGESTA_ROUTE: Final[str] = "/ingesta"
INGESTA_UPLOAD_ROUTE: Final[str] = "/upload"
PRUEBA_ENDPOINT_BORRAR_ROUTE: Final[str] = "/prueba_endpoint_borrar"
BRECHAS_ROUTE: Final[str] = "/brechas"
INGESTA_SYNC_ROUTE: Final[str] = "/sync"
INGESTA_SYNC_WORLD_BANK_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/world-bank"
TENDENCIAS_ROUTE: Final[str] = "/tendencias"
DOCS_ROUTE: Final[str] = "/docs"
REDOC_ROUTE: Final[str] = "/redoc"
INGESTA_SYNC_ILOSTAT_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/ilostat"
INGESTA_SYNC_BCENTRAL_CHILE_ROUTE: Final[str] = f"{INGESTA_SYNC_ROUTE}/bcentral-chile"
METRICAS_ROUTE: Final[str] = "/metricas"
CATALOGO_ROUTE: Final[str] = "/catalogo"
ALERTAS_ROUTE: Final[str] = "/alertas"
FUENTE_ROUTE: Final[str] = "/fuentes"


# Tags para OpenAPI / Swagger
OPENAPI_TAG_ROOT: Final[str] = "Root"
OPENAPI_TAG_HEALTH: Final[str] = "Health"
OPENAPI_TAG_INDICADORES: Final[str] = "Indicadores"
OPENAPI_TAG_INDICE_EMPLEABILIDAD: Final[str] = "Indice de Empleabilidad"
OPENAPI_TAG_INGESTA: Final[str] = "Ingesta"
OPENAPI_TAG_METRICAS: Final[str] = "Métricas"
OPENAPI_TAG_CATALOGO: Final[str] = "Catálogo"
OPENAPI_TAG_ALERTAS: Final[str] = "Alertas"
OPENAPI_TAG_FUENTE: Final[str] = "Fuentes de Datos"
OPENAPI_TAG_BRECHAS: Final[str] = "Brechas de Habilidades"


# ==============================================================================
# 5. Configuración de Ingesta y Almacenamiento de Archivos
# ==============================================================================

DEFAULT_UPLOAD_DIR: Final[str] = "data/uploads"
CSV_FILE_EXTENSION: Final[str] = ".csv"
DEFAULT_CSV_CONTENT_TYPE: Final[str] = "text/csv"
DEFAULT_MAX_UPLOAD_SIZE_BYTES: Final[int] = 52_428_800  # 50 MB
JSON_SERIALIZATION_MODE: Final[str] = "json"


# ==============================================================================
# 6. Configuración de Conectores Externos y APIs Oficiales
# ==============================================================================

DEFAULT_WORLD_BANK_SOURCE: Final[str] = "World Bank"
DEFAULT_WORLD_BANK_BASE_URL: Final[str] = "https://api.worldbank.org/v2"
DEFAULT_WORLD_BANK_TIMEOUT_SECONDS: Final[float] = 30.0

# Constantes de configuración para conector ILOSTAT (OIT)
DEFAULT_ILOSTAT_SOURCE: Final[str] = "ILOSTAT"
DEFAULT_ILOSTAT_BASE_URL: Final[str] = "https://rplumber.ilo.org/data/indicator/"
DEFAULT_ILOSTAT_TIMEOUT_SECONDS: Final[float] = 60.0

# Constantes de configuración para conector Banco Central de Chile (SIETE REST WS)
DEFAULT_BCENTRAL_CHILE_SOURCE: Final[str] = "Banco Central de Chile"
DEFAULT_BCENTRAL_CHILE_BASE_URL: Final[str] = (
    "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
)
DEFAULT_BCENTRAL_CHILE_TIMEOUT_SECONDS: Final[float] = 30.0


# Constantes de configuración para Brechas de Habilidades
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
# 7. Mensajes Estándar para Respuestas REST (ApiResponse)
# ==============================================================================

DEFAULT_SUCCESS_MESSAGE: Final[str] = "Operación ejecutada con éxito."
DEFAULT_ERROR_MESSAGE: Final[str] = "Ocurrió un error al procesar la solicitud."
INTERNAL_SERVER_ERROR_MESSAGE: Final[str] = "Error interno del servidor no controlado."


# ==============================================================================
# 8.Constantes de Estado de los fuentes de datos externas
# ==============================================================================
class FuenteEstado(StrEnum):
    """Enum que representa los posibles estados de una fuente de datos."""

    ACTIVA = "activa"
    DESACTUALIZADA = "desactualizada"
    NO_DISPONIBLE = "no_disponible"


# ==============================================================================
# Exportaciones Públicas
# ==============================================================================

__all__ = [
    # Identificación y Versión
    "PROJECT_IDENTIFIER",
    "DEFAULT_API_VERSION",
    "DEFAULT_APP_VERSION",
    # Entornos, Salud y Códigos de Error
    "AppEnvironment",
    "HealthStatus",
    "ApiErrorCode",
    "SyncStatus",
    # Taxonomías de Dominio
    "TipoIndicador",
    "NivelEmpleabilidad",
    "DimensionIndiceNombre",
    "PaisCodigo",
    "SectorEstrategico",
    "INDICADOR_INDICE_EMPLEABILIDAD",
    "DEFAULT_INDICE_METODOLOGIA_FUENTE",
    # Rutas HTTP
    "ROOT_ROUTE",
    "API_V1_PREFIX",
    "HEALTH_CHECK_ROUTE",
    "INDICADORES_ROUTE",
    "INDICE_EMPLEABILIDAD_ROUTE",
    "INGESTA_ROUTE",
    "INGESTA_UPLOAD_ROUTE",
    "INGESTA_SYNC_ROUTE",
    "INGESTA_SYNC_WORLD_BANK_ROUTE",
    "BRECHAS_ROUTE",
    "TENDENCIAS_ROUTE",
    "METRICAS_ROUTE",
    "CATALOGO_ROUTE",
    "ALERTAS_ROUTE",
    "DOCS_ROUTE",
    "REDOC_ROUTE",
    "INGESTA_SYNC_BCENTRAL_CHILE_ROUTE",
    "FUENTE_ROUTE",
    # OpenAPI Tags
    "OPENAPI_TAG_ROOT",
    "OPENAPI_TAG_HEALTH",
    "OPENAPI_TAG_INDICADORES",
    "OPENAPI_TAG_INDICE_EMPLEABILIDAD",
    "OPENAPI_TAG_INGESTA",
    "OPENAPI_TAG_METRICAS",
    "OPENAPI_TAG_CATALOGO",
    "OPENAPI_TAG_ALERTAS",
    "OPENAPI_TAG_BRECHAS",
    "OPENAPI_TAG_FUENTE",
    "FuenteEstado",
    # Almacenamiento e Ingesta
    "DEFAULT_UPLOAD_DIR",
    "CSV_FILE_EXTENSION",
    "DEFAULT_CSV_CONTENT_TYPE",
    "DEFAULT_MAX_UPLOAD_SIZE_BYTES",
    "JSON_SERIALIZATION_MODE",
    # Conectores Externos
    "DEFAULT_WORLD_BANK_SOURCE",
    "DEFAULT_WORLD_BANK_BASE_URL",
    "DEFAULT_WORLD_BANK_TIMEOUT_SECONDS",
    "DEFAULT_ILOSTAT_SOURCE",
    "DEFAULT_ILOSTAT_BASE_URL",
    "DEFAULT_ILOSTAT_TIMEOUT_SECONDS",
    "DEFAULT_BCENTRAL_CHILE_SOURCE",
    "DEFAULT_BCENTRAL_CHILE_BASE_URL",
    "DEFAULT_BCENTRAL_CHILE_TIMEOUT_SECONDS",
    # Brechas
    "DEFAULT_BRECHAS_SOURCE",
    "DEFAULT_BRECHAS_METODOLOGIA",
    "DEFAULT_BRECHAS_METODOLOGIA_PERSISTIDA",
    "BRECHAS_GET_SUCCESS_MESSAGE",
    "BRECHAS_SAVE_SUCCESS_MESSAGE",
    # Mensajes
    "DEFAULT_SUCCESS_MESSAGE",
    "DEFAULT_ERROR_MESSAGE",
    "INTERNAL_SERVER_ERROR_MESSAGE",
]
