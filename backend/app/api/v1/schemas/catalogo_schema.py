"""Esquemas Pydantic para el catálogo de taxonomías, entidades y filtros globales."""

from pydantic import BaseModel, Field

from app.api.v1.schemas.response_schema import ApiResponse


class PaisCatalogoDto(BaseModel):
    """Representación de un país habilitado en el Observatorio."""

    id: str = Field(..., description="Código ISO 3166-1 alpha-3 (ej. 'ARG').")
    nombre: str = Field(..., description="Nombre oficial del país.")


class SectorCatalogoDto(BaseModel):
    """Sector estratégico prioritario."""

    id: str = Field(..., description="Slug canónico del sector (ej. 'tecnologia').")
    nombre: str = Field(..., description="Denominación legible.")
    isic: list[str] = Field(
        default_factory=list,
        description="Códigos de clasificación ISIC/CIIU asociados.",
    )


class OcupacionCatalogoDto(BaseModel):
    """Ocupación normalizada vinculada a un sector."""

    id: str = Field(..., description="Slug canónico de la ocupación.")
    nombre: str = Field(..., description="Título legible de la ocupación.")
    sector: str = Field(..., description="Slug del sector al que pertenece.")
    isco: str | None = Field(
        default=None, description="Código de clasificación ISCO-08."
    )


class IndicadorCatalogoDto(BaseModel):
    """Definición y metadatos de un indicador disponible."""

    id: str = Field(..., description="Slug identificador del indicador.")
    nombre: str = Field(..., description="Nombre del indicador.")
    unidad: str = Field(..., description="Unidad de medida.")
    frecuencias: list[str] = Field(
        default_factory=list,
        description="Frecuencias disponibles (anual, trimestral, mensual).",
    )
    desagregaciones: list[str] = Field(
        default_factory=list,
        description="Dimensiones de filtro aplicables (pais, sector, ocupacion).",
    )
    descripcion: str | None = Field(
        default=None, description="Nota conceptual o metodológica."
    )


class PeriodosRangoDto(BaseModel):
    """Rango cronológico global cubierto por los datos disponibles."""

    min: str = Field(..., description="Período más antiguo disponible (ej. '2018-Q1').")
    max: str = Field(
        ..., description="Período más reciente disponible (ej. '2026-Q2')."
    )


class CatalogoDataSchema(BaseModel):
    """Payload completo con todas las taxonomías del sistema."""

    paises: list[PaisCatalogoDto] = Field(default_factory=list)
    sectores: list[SectorCatalogoDto] = Field(default_factory=list)
    ocupaciones: list[OcupacionCatalogoDto] = Field(default_factory=list)
    indicadores: list[IndicadorCatalogoDto] = Field(default_factory=list)
    periodos: PeriodosRangoDto


CatalogoResponseSchema = ApiResponse[CatalogoDataSchema]
