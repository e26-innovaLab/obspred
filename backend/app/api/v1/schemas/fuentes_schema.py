"""Esquemas Pydantic para trazabilidad, catálogo de fuentes y auditoría metodológica."""

from typing import Literal

from pydantic import BaseModel, Field

from app.api.v1.schemas.response_schema import ApiResponse


class FuenteAuditoriaDto(BaseModel):
    """Ficha informativa y estado de actualización de una fuente externa."""

    id: str = Field(
        ..., description="Identificador corto de la fuente (ej. 'ilostat')."
    )
    nombre: str = Field(..., description="Nombre formal del organismo o base de datos.")
    descripcion: str = Field(..., description="Alcance y descripción de la fuente.")
    paises: list[str] = Field(
        default_factory=list, description="Países cubiertos (ISO-3)."
    )
    tipo_acceso: Literal["api", "dataset", "scraping", "manual"] = Field(
        default="api", description="Mecanismo técnico de ingesta."
    )
    frecuencia: str = Field(
        ..., description="Frecuencia típica de publicación de la fuente."
    )
    ultima_actualizacion: str = Field(
        ..., description="Fecha de corte del último dato cargado."
    )
    proxima_actualizacion: str = Field(
        ..., description="Estimación de fecha para la siguiente publicación."
    )
    estado_fuente: Literal["activa", "desactualizada", "no_disponible"] = Field(
        default="activa", description="Estado operativo actual de la conexión/fuente."
    )
    url: str | None = Field(
        default=None, description="Enlace oficial al portal de la fuente."
    )
    indicadores_alimentados: list[str] = Field(
        default_factory=list,
        description="Lista de indicadores nutridos por esta fuente.",
    )


class MetodologiaDto(BaseModel):
    """Documentación y fichas metodológicas de cálculo y proyecciones."""

    id: str = Field(..., description="Identificador único del documento metodológico.")
    titulo: str = Field(..., description="Título de la metodología aplicada.")
    resumen: str = Field(
        ..., description="Síntesis conceptual y operativa del cálculo."
    )
    url: str | None = Field(
        default=None, description="Enlace al documento técnico o PDF."
    )


class FuentesDataSchema(BaseModel):
    """Payload de auditoría de fuentes y metodologías institucionales."""

    fuentes: list[FuenteAuditoriaDto] = Field(default_factory=list)
    metodologias: list[MetodologiaDto] = Field(default_factory=list)


FuentesResponseSchema = ApiResponse[FuentesDataSchema]
