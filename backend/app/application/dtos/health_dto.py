"""DTOs para el reporte de salud y disponibilidad de servicios externos."""

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import HealthStatus


class ExternalServiceHealthDTO(BaseModel):
    """Representación del estado operativo de un servicio o conector externo.

    Attributes:
        source_id: Identificador normalizado del conector.
        name: Denominación oficial de la fuente externa.
        status: Estado operativo del servicio (healthy o unhealthy).
        is_available: Booleano que indica si el servicio respondió exitosamente.
        latency_ms: Tiempo de respuesta en milisegundos.
        url: URL base o endpoint consultado.
        error: Detalle descriptivo si ocurrió un error en la verificación.
    """

    model_config = ConfigDict(frozen=True)

    source_id: str = Field(..., description="Identificador único del conector")
    name: str = Field(..., description="Denominación de la fuente externa")
    status: HealthStatus = Field(..., description="Estado operativo del servicio")
    is_available: bool = Field(
        ..., description="Indica si el servicio respondió satisfactoriamente"
    )
    latency_ms: float = Field(..., description="Latencia de respuesta en milisegundos")
    url: str = Field(..., description="URL base o endpoint de consulta")
    error: str | None = Field(
        default=None,
        description="Mensaje de error si la verificación falló",
    )


class ExternalServicesHealthReportDTO(BaseModel):
    """Reporte consolidado del estado de salud de todos los conectores externos.

    Attributes:
        overall_status: Estado general consolidado (healthy, degraded, unhealthy).
        total_services: Cantidad total de servicios externos evaluados.
        healthy_count: Cantidad de servicios funcionando correctamente.
        unhealthy_count: Cantidad de servicios con problemas o no disponibles.
        services: Detalle individual de cada servicio evaluado.
    """

    model_config = ConfigDict(frozen=True)

    overall_status: HealthStatus = Field(..., description="Estado general consolidado")
    total_services: int = Field(
        ..., description="Cantidad total de servicios externos evaluados"
    )
    healthy_count: int = Field(
        ..., description="Cantidad de servicios funcionando correctamente"
    )
    unhealthy_count: int = Field(
        ..., description="Cantidad de servicios con problemas o no disponibles"
    )
    services: list[ExternalServiceHealthDTO] = Field(
        ..., description="Detalle individual por servicio"
    )
