"""Esquemas Pydantic para el módulo de alertas tempranas y cambios significativos."""

from typing import Literal

from pydantic import BaseModel, Field

from app.api.v1.schemas.response_schema import ApiResponse


class AlertaItemDto(BaseModel):
    """Representación de una alerta o variación estadística significativa."""

    id: str = Field(..., description="Identificador único del evento de alerta.")
    pais: str = Field(..., description="Código ISO-3 del país.")
    indicador: str = Field(..., description="Slug del indicador que generó la alerta.")
    periodo: str = Field(
        ..., description="Período temporal en el que ocurrió el cambio."
    )
    variacion_pct: float = Field(..., description="Porcentaje de cambio interperíodo.")
    nivel: Literal["bajo", "medio", "alto"] = Field(
        default="medio", description="Severidad de la alerta."
    )
    titulo: str = Field(..., description="Título sintético de la alerta.")
    descripcion: str = Field(
        ..., description="Detalle contextual de la variación detectada."
    )


class AlertasDataSchema(BaseModel):
    """Payload de alertas activas o cambios significativos."""

    alertas: list[AlertaItemDto] = Field(default_factory=list)


AlertasResponseSchema = ApiResponse[AlertasDataSchema]
