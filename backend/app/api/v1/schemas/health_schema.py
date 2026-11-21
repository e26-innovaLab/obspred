"""Esquemas de datos para la verificación de salud del sistema."""

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ApiResponse
from app.core.constants import HealthStatus


class HealthDataSchema(BaseModel):
    """Datos puntuales del estado del servicio interno.

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


class ExternalServiceStatusSchema(BaseModel):
    """Estado de salud individual de un servicio o fuente externa.

    Attributes:
        source_id: Identificador normalizado de la fuente externa.
        name: Denominación oficial del servicio externo.
        status: Estado operativo del servicio (healthy o unhealthy).
        is_available: Booleano indicando si respondió con éxito.
        latency_ms: Tiempo de respuesta en milisegundos.
        url: URL base o endpoint evaluado.
        error: Mensaje de error descriptivo si el servicio no está disponible.
    """

    model_config = ConfigDict(frozen=True)

    source_id: str = Field(
        ...,
        description="Identificador único del conector externo",
    )
    name: str = Field(
        ...,
        description="Denominación de la fuente externa",
    )
    status: HealthStatus = Field(
        ...,
        description="Estado operativo actual del servicio",
    )
    is_available: bool = Field(
        ...,
        description="Indica si la fuente externa está disponible y operativa",
    )
    latency_ms: float = Field(
        ...,
        description="Tiempo de respuesta en milisegundos (ms)",
    )
    url: str = Field(
        ...,
        description="URL base o endpoint de consulta",
    )
    error: str | None = Field(
        default=None,
        description="Detalle del error en caso de indisponibilidad",
    )


class ExternalServicesHealthDataSchema(BaseModel):
    """Reporte consolidado de salud de todas las fuentes externas.

    Attributes:
        overall_status: Estado general consolidado (healthy, degraded, unhealthy).
        total_services: Cantidad total de fuentes externas verificadas.
        healthy_count: Cantidad de fuentes operativas.
        unhealthy_count: Cantidad de fuentes con fallos.
        services: Lista con el detalle de cada fuente externa.
    """

    model_config = ConfigDict(frozen=True)

    overall_status: HealthStatus = Field(
        ...,
        description="Estado general consolidado del ecosistema de fuentes externas",
    )
    total_services: int = Field(
        ...,
        description="Cantidad total de fuentes externas evaluadas",
    )
    healthy_count: int = Field(
        ...,
        description="Cantidad de fuentes externas operativas",
    )
    unhealthy_count: int = Field(
        ...,
        description="Cantidad de fuentes externas degradadas o caídas",
    )
    services: list[ExternalServiceStatusSchema] = Field(
        ...,
        description="Listado detallado del estado de cada fuente externa",
    )


# Respuestas estándar con envoltorio canónico ApiResponse
HealthResponseSchema = ApiResponse[HealthDataSchema]
ExternalServicesHealthResponseSchema = ApiResponse[ExternalServicesHealthDataSchema]
