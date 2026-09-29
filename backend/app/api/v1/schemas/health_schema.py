"""Esquema de respuesta para el estado de salud de la API."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import HealthStatus


class HealthResponseSchema(BaseModel):
    """Modelo de salida para el endpoint de verificación de salud.

    Attributes:
        status: Estado operativo del servicio (healthy, degraded, unhealthy).
        environment: Entorno en el que se ejecuta la aplicación.
        version: Versión actual del backend.
        timestamp: Marca temporal UTC de la verificación.
    """

    model_config = ConfigDict(frozen=True)

    status: HealthStatus = Field(
        ...,
        description="Estado operativo actual del backend",
    )
    environment: str = Field(
        ...,
        description="Entorno de despliegue",
    )
    version: str = Field(
        ...,
        description="Versión del software",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Marca temporal UTC de la consulta",
    )
