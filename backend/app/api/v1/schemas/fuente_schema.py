"""Esquema de datos canónico para trazabilidad de fuentes según Principio 3."""

from typing import Literal

from pydantic import BaseModel, Field


class FuenteItemSchema(BaseModel):
    """Esquema para representar la trazabilidad y procedencia de un dato.

    Attributes:
        fuente: Nombre de la entidad, organismo o cálculo de origen.
        fecha_actualizacion: Fecha de corte del dato en formato YYYY-MM-DD.
        estado_fuente: Disponibilidad operativa de la fuente.
        tipo: Clasificación metodológica ('observado', 'calculado', 'proyeccion').
        metodologia_url: Enlace a la ficha metodológica técnica o institucional.
    """

    fuente: str = Field(
        ...,
        description="Nombre oficial de la fuente u organismo emisor.",
        examples=["ILOSTAT", "INDEC — EPH"],
    )
    fecha_actualizacion: str = Field(
        ...,
        description="Fecha de última actualización en formato ISO (YYYY-MM-DD).",
        examples=["2026-09-30"],
    )
    estado_fuente: Literal["activa", "desactualizada", "no_disponible"] = Field(
        default="activa",
        description="Estado de vigencia operativa de la fuente.",
    )
    tipo: Literal["observado", "calculado", "proyeccion"] = Field(
        default="observado",
        description="Naturaleza estadística del dato según Principio 3.",
    )
    metodologia_url: str | None = Field(
        default=None,
        description="URL técnica con la ficha metodológica si está disponible.",
    )
