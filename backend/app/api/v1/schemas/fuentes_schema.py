"""Esquemas Pydantic para la consulta y serialización de fuentes de datos."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ApiResponse
from app.core.constants import FuenteEstado


class FuenteCreateSchema(BaseModel):
    """Estructura para crear una fuente de datos."""

    model_config = ConfigDict(frozen=True)

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre de la fuente de datos",
    )

    descripcion: str | None = Field(
        default=None,
        max_length=255,
        description="Descripción de la fuente de datos",
    )

    url: str | None = Field(
        default=None,
        max_length=255,
        description="URL de la fuente de datos",
    )

    ultima_actualizacion: datetime | None = Field(
        default=None,
        description="Fecha y hora de la última actualización",
    )


class FuenteItemSchema(FuenteCreateSchema):
    """Estructura de respuesta con los datos de una fuente."""

    id: int = Field(
        ...,
        description="Identificador único de la fuente de datos",
    )

    estado: FuenteEstado = Field(
        description="Estado de la fuente de datos",
    )

    model_config = ConfigDict(frozen=True)


FuentesResponseSchema = ApiResponse[list[FuenteItemSchema]]
FuenteResponseSchema = ApiResponse[FuenteItemSchema]
