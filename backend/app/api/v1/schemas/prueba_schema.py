"""Esquemas Pydantic para el controlador temporal de prueba CRUD."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.api.v1.schemas.response_schema import ApiResponse


class PruebaPayloadSchema(BaseModel):
    """Modelo para recibir datos en operaciones POST y PUT simuladas."""

    name: Optional[str] = Field(
        default=None,
        description="Nombre de prueba",
    )
    description: Optional[str] = Field(
        default=None,
        description="Descripción de prueba",
    )


class PruebaItemData(BaseModel):
    """Datos devueltos en la carga útil (data) de la operación simulada.

    Attributes:
        method: Verbo HTTP ejecutado.
        item_id: Identificador opcional del ítem manipulado.
        payload: Datos simulados recibidos en la petición si aplica.
    """

    model_config = ConfigDict(frozen=True)

    method: str = Field(
        ...,
        description="Verbo HTTP ejecutado",
    )
    item_id: Optional[str] = Field(
        default=None,
        description="Identificador del ítem si aplica",
    )
    payload: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Datos opcionales recibidos o simulados",
    )


# Respuesta estándar para el endpoint de prueba CRUD
PruebaResponseSchema = ApiResponse[PruebaItemData]
