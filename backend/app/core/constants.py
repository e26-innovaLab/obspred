"""Constantes transversales del sistema para evitar cadenas mágicas (magic strings).

Define enumeraciones y valores estáticos tipados para entornos, rutas,
estados operativos y parámetros de configuración general.
"""

from enum import Enum
from typing import Final


class AppEnvironment(str, Enum):
    """Entornos posibles de ejecución de la aplicación."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class HealthStatus(str, Enum):
    """Estados del reporte de salud y disponibilidad de la API."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# Prefijos y rutas de la API para evitar magic strings
API_V1_PREFIX: Final[str] = "/api/v1"
HEALTH_CHECK_ROUTE: Final[str] = "/health"
PRUEBA_ENDPOINT_BORRAR_ROUTE: Final[str] = "/prueba_endpoint_borrar"
INGESTA_ROUTE: Final[str] = "/ingesta"
INGESTA_UPLOAD_ROUTE: Final[str] = "/upload"
ROOT_ROUTE: Final[str] = "/"

# Identificación y versiones base
DEFAULT_API_VERSION: Final[str] = "v1"
PROJECT_IDENTIFIER: Final[str] = "obspred"

# Configuración por defecto de almacenamiento de archivos
DEFAULT_UPLOAD_DIR: Final[str] = "data/uploads"
CSV_FILE_EXTENSION: Final[str] = ".csv"
DEFAULT_MAX_UPLOAD_SIZE_BYTES: Final[int] = 52_428_800  # 50 MB
DEFAULT_CSV_CONTENT_TYPE: Final[str] = "text/csv"

# Mensajes estándar para respuestas REST
DEFAULT_SUCCESS_MESSAGE: Final[str] = "Operación ejecutada con éxito."
DEFAULT_ERROR_MESSAGE: Final[str] = "Ocurrió un error al procesar la solicitud."
INTERNAL_SERVER_ERROR_MESSAGE: Final[str] = "Error interno del servidor no controlado."

