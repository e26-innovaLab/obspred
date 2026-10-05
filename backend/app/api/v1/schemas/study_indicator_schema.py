"""Esquemas Pydantic para el endpoint pedagógico de indicadores."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ApiResponse


class StudyIndicatorResponseData(BaseModel):
    """Esquema de salida de un indicador individual."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Identificador único del indicador")
    name: str = Field(..., description="Nombre descriptivo del indicador")
    country: str = Field(..., description="Código ISO del país (AR, CL, UY)")
    sector: str = Field(..., description="Sector económico asociado")
    value: float = Field(..., description="Valor numérico actual")
    unit: str = Field(..., description="Unidad de medida")
    source: str = Field(..., description="Fuente oficial del indicador")
    updated_at: Optional[datetime] = Field(
        None, description="Fecha y hora de actualización"
    )


class CreateStudyIndicatorPayload(BaseModel):
    """Esquema del payload JSON para registrar un indicador."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nombre descriptivo del indicador",
        json_schema_extra={"example": "Empleo Formal en Software"},
    )
    country: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Código de 2 letras del país (AR, CL, UY)",
        json_schema_extra={"example": "AR"},
    )
    sector: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Sector estratégico",
        json_schema_extra={"example": "Tecnología"},
    )
    value: float = Field(
        ...,
        description="Valor numérico (debe ser mayor o igual a 0)",
        json_schema_extra={"example": 145000.0},
    )
    unit: str = Field(
        ...,
        max_length=50,
        description="Unidad de medida",
        json_schema_extra={"example": "Puestos de trabajo"},
    )
    source: str = Field(
        ...,
        max_length=100,
        description="Fuente de la información",
        json_schema_extra={"example": "Secretaría de Trabajo"},
    )


# Tipos de respuesta estándar ApiResponse
StudyIndicatorApiResponse = ApiResponse[StudyIndicatorResponseData]
StudyIndicatorListApiResponse = ApiResponse[list[StudyIndicatorResponseData]]
