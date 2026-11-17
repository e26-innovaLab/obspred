"""DTOs para la capa de aplicación del catálogo de taxonomías y filtros."""

from pydantic import BaseModel, ConfigDict, Field


class PaisCatalogoDTO(BaseModel):
    """Representación de un país disponible en el catálogo."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Código ISO 3166-1 alpha-3 del país.")
    nombre: str = Field(..., description="Nombre oficial del país.")


class SectorCatalogoDTO(BaseModel):
    """Sector productivo prioritario."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Slug canónico del sector.")
    nombre: str = Field(..., description="Denominación legible del sector.")
    isic: list[str] = Field(
        default_factory=list,
        description="Códigos de clasificación ISIC/CIIU asociados.",
    )


class OcupacionCatalogoDTO(BaseModel):
    """Ocupación normalizada vinculada a un sector estratégico."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Slug identificador de la ocupación.")
    nombre: str = Field(..., description="Título legible de la ocupación.")
    sector: str = Field(..., description="Slug del sector al que pertenece.")
    isco: str | None = Field(
        default=None,
        description="Código de clasificación ISCO-08 si aplica.",
    )


class IndicadorCatalogoDTO(BaseModel):
    """Definición y metadatos de un indicador socioeconómico disponible."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Slug identificador del indicador.")
    nombre: str = Field(..., description="Nombre descriptivo del indicador.")
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
        default=None,
        description="Descripción metodológica o nota conceptual.",
    )


class PeriodosRangoDTO(BaseModel):
    """Rango cronológico global cubierto por las observaciones disponibles."""

    model_config = ConfigDict(frozen=True)

    min: str | None = Field(
        default=None,
        description="Período más antiguo disponible con observaciones (ej. '2018-Q1').",
    )
    max: str | None = Field(
        default=None,
        description="Período más reciente disponible con observaciones.",
    )


class CatalogoDataDTO(BaseModel):
    """Agregado completo de taxonomías del catálogo unificado."""

    model_config = ConfigDict(frozen=True)

    paises: list[PaisCatalogoDTO] = Field(default_factory=list)
    sectores: list[SectorCatalogoDTO] = Field(default_factory=list)
    ocupaciones: list[OcupacionCatalogoDTO] = Field(default_factory=list)
    indicadores: list[IndicadorCatalogoDTO] = Field(default_factory=list)
    periodos: PeriodosRangoDTO
