"""Esquemas Pydantic para el módulo de alertas tempranas y cambios significativos."""

from pydantic import BaseModel, Field

from app.api.v1.schemas.response_schema import ApiResponse
from app.application.dtos.alerta_dto import AlertaItemDto

__all__ = ["AlertaItemDto", "AlertasDataSchema", "AlertasResponseSchema"]


class AlertasDataSchema(BaseModel):
    """Payload de alertas activas o cambios significativos."""

    alertas: list[AlertaItemDto] = Field(default_factory=list)


AlertasResponseSchema = ApiResponse[AlertasDataSchema]
