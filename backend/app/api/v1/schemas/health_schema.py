"""Esquemas de datos para la verificación de salud del sistema."""

from pydantic import BaseModel, ConfigDict, Field
from app.api.v1.schemas.response_schema import ApiResponse
from app.core.constants import HealthStatus


class HealthDataSchema(BaseModel):
    """Datos puntuales del estado del servicio.

    Attributes:
        status: Estado operativo del backend (healthy, degraded, unhealthy).
        environment: Entorno de despliegue (development, testing, production).
        version: Versión del software backend.
    """

    model_config = ConfigDict(frozen=True)

    status: HealthStatus = Field(
        ...,
        description="Estado operativo actual del backend",
    )
    environment: str = Field(
        ...,
        description="Entorno de ejecución de la aplicación",
    )
    version: str = Field(
        ...,
        description="Versión del software",
    )


# Respuesta estándar para el endpoint de salud
HealthResponseSchema = ApiResponse[HealthDataSchema]
