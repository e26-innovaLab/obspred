""" Esquemas Pydantic para la consulta y serialización de fuentes de datos. """

from typing import Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.api.v1.schemas.response_schema import ApiResponse
from app.domain.enums.fuente_estado import FuenteEstado


class FuenteItemSchema(BaseModel):
    """
     Estructura 
    """
    model_config = ConfigDict(frozen=True)


    id:int = Field(
        ...,
        description="Identificador único de la fuente de datos",
    )

    nombre: str = Field(
        ...,
        description="Nombre de la fuente de datos",
    )

    descripcion: Optional[str] = Field(
        None,
        description="Descripción de la fuente de datos",
    )

    url: Optional[str] = Field(
        None,
        description="URL de la fuente de datos",
    )

    ultima_actualizacion: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora de la última actualización de la fuente de datos",
    )

    estado: FuenteEstado = Field(
        ...,
        description="Estado de la fuente de datos (activo, desactualizado, no disponible)",
    )


FuentesResponseSchema = ApiResponse[List[FuenteItemSchema]]