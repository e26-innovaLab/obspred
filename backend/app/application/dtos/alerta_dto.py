"""DTOs para el servicio de alertas y detección de variaciones."""

from pydantic import BaseModel, Field

from app.core.constants import AlertaNivel


class AlertaItemDto(BaseModel):
    """Representación de una alerta o variación estadística significativa."""

    id: str = Field(..., description="Identificador único del evento de alerta.")
    pais: str = Field(..., description="Código ISO-3 del país.")
    indicador: str = Field(..., description="Slug del indicador que generó la alerta.")
    periodo: str = Field(
        ..., description="Período temporal en el que ocurrió el cambio."
    )
    variacion_pct: float = Field(..., description="Porcentaje de cambio interperíodo.")
    nivel: AlertaNivel = Field(
        default=AlertaNivel.MEDIO, description="Severidad de la alerta."
    )
    titulo: str = Field(..., description="Título sintético de la alerta.")
    descripcion: str = Field(
        ..., description="Detalle contextual de la variación detectada."
    )
