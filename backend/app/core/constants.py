"""Constantes transversales del sistema para evitar cadenas mágicas (magic strings).

Define enumeraciones y valores estáticos fuertemente tipados para entornos,
rutas de la API, almacenamiento de ingesta y mensajes estándar del sistema.
"""

from enum import Enum
from typing import Final

# ==============================================================================
# 1. Identificación y Versión del Proyecto
# ==============================================================================

PROJECT_IDENTIFIER: Final[str] = "obspred"
DEFAULT_API_VERSION: Final[str] = "v1"


# ==============================================================================
# 2. Entornos de Ejecución y Estados Operativos
# ==============================================================================

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


# ==============================================================================
# 3. Prefijos y Rutas HTTP de la API
# ==============================================================================

ROOT_ROUTE: Final[str] = "/"
API_V1_PREFIX: Final[str] = "/api/v1"
HEALTH_CHECK_ROUTE: Final[str] = "/health"
INDICADORES_ROUTE: Final[str] = "/indicadores"
INDICE_EMPLEABILIDAD_ROUTE: Final[str] = "/indice-empleabilidad"
INGESTA_ROUTE: Final[str] = "/ingesta"
INGESTA_UPLOAD_ROUTE: Final[str] = "/upload"
PRUEBA_ENDPOINT_BORRAR_ROUTE: Final[str] = "/prueba_endpoint_borrar"


# ==============================================================================
# 4. Configuración de Ingesta y Almacenamiento de Archivos
# ==============================================================================

DEFAULT_UPLOAD_DIR: Final[str] = "data/uploads"
CSV_FILE_EXTENSION: Final[str] = ".csv"
DEFAULT_CSV_CONTENT_TYPE: Final[str] = "text/csv"
DEFAULT_MAX_UPLOAD_SIZE_BYTES: Final[int] = 52_428_800  # 50 MB


# ==============================================================================
# 5. Mensajes Estándar para Respuestas REST (ApiResponse)
# ==============================================================================

DEFAULT_SUCCESS_MESSAGE: Final[str] = "Operación ejecutada con éxito."
DEFAULT_ERROR_MESSAGE: Final[str] = "Ocurrió un error al procesar la solicitud."
INTERNAL_SERVER_ERROR_MESSAGE: Final[str] = (
    "Error interno del servidor no controlado."
)


# ==============================================================================
# Exportaciones Públicas
# ==============================================================================

__all__ = [
    # Identificación
    "PROJECT_IDENTIFIER",
    "DEFAULT_API_VERSION",
    # Entornos y Salud
    "AppEnvironment",
    "HealthStatus",
    # Rutas
    "ROOT_ROUTE",
    "API_V1_PREFIX",
    "HEALTH_CHECK_ROUTE",
    "INDICADORES_ROUTE",
    "INDICE_EMPLEABILIDAD_ROUTE",
    "INGESTA_ROUTE",
    "INGESTA_UPLOAD_ROUTE",
    "PRUEBA_ENDPOINT_BORRAR_ROUTE",
    # Almacenamiento e Ingesta
    "DEFAULT_UPLOAD_DIR",
    "CSV_FILE_EXTENSION",
    "DEFAULT_CSV_CONTENT_TYPE",
    "DEFAULT_MAX_UPLOAD_SIZE_BYTES",
    # Mensajes
    "DEFAULT_SUCCESS_MESSAGE",
    "DEFAULT_ERROR_MESSAGE",
    "INTERNAL_SERVER_ERROR_MESSAGE",
]
