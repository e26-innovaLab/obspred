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
ROOT_ROUTE: Final[str] = "/"

# Identificación y versiones base
DEFAULT_API_VERSION: Final[str] = "v1"
PROJECT_IDENTIFIER: Final[str] = "obspred"
