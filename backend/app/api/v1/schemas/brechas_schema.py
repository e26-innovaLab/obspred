from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import (
    ApiResponse,
)
from app.core.constants import PaisCodigo, SectorEstrategico


class TipoDatoBrecha(StrEnum):
    OBSERVADO = "observado"
    CALCULADO = "calculado"
    ESTIMADO = "estimado"


class TipoHabilidad(StrEnum):
    TECNICA = "tecnica"
    BLANDA = "blanda"


class NivelBrecha(StrEnum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class MetadatosFuente(BaseModel):
    """Trazabilidad exigida por el brief y el equipo de Data."""

    model_config = ConfigDict(frozen=True)
    fuente: str = Field(
        ...,
        description="Organismo o taxonomía de origen",
        examples=["SENCE SABE / ESCO"],
    )
    fecha_actualizacion: str = Field(
        ..., description="Fecha de corte del dato", examples=["2026-09-30"]
    )
    metodologia: str | None = Field(
        None,
        description="Aclaración metodológica o taxonomía de referencia",
        examples=["Taxonomía de referencia ESCO con demanda observada en avisos SABE."],
    )


class HabilidadBrechaItem(BaseModel):
    """Representa una barra del gráfico Demanda vs Oferta formativa."""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        frozen=True,
    )

    habilidad: str = Field(
        ..., description="Nombre de la habilidad", examples=["Trabajo en equipo remoto"]
    )
    demanda: float = Field(
        ..., description="Intensidad de demanda del mercado (0-100)", examples=[92.0]
    )
    oferta_formativa: float = Field(
        ...,
        alias="ofertaFormativa",
        description="Porcentaje de oferta formativa",
        examples=[28.0],
    )
    emergente: bool = Field(
        False,
        alias="emergente",
        description="Indica si destaca en la lista de habilidades emergentes",
    )
    brecha: float = Field(
        ...,
        description="Diferencia neta calculada entre demanda y oferta formativa",
        examples=[64.0],
    )


class HabilidadBrechaCreateItem(BaseModel):
    """Payload para registrar una habilidad evaluada en una ocupación."""

    model_config = ConfigDict(populate_by_name=True)

    habilidad: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nombre de la habilidad requerida",
        examples=["Cloud computing"],
    )
    demanda: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Puntaje o porcentaje de demanda observada",
        examples=[94.0],
    )
    oferta_formativa: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        alias="ofertaFormativa",
        description="Puntaje o porcentaje de cobertura formativa",
        examples=[45.0],
    )
    emergente: bool = Field(
        False,
        description="Indica si es una habilidad de reciente emergencia",
        examples=[True],
    )


class BrechaGuardarPayloadSchema(BaseModel):
    """Payload para guardar o actualizar las habilidades de una ocupación."""

    habilidades: list[HabilidadBrechaCreateItem] = Field(
        ...,
        min_length=1,
        description="Listado de habilidades a persistir para la ocupación",
    )
    pais: str = Field(
        default=PaisCodigo.ARG.value,
        description="Código ISO del país asociado",
        examples=[PaisCodigo.ARG.value],
    )
    sector: str | None = Field(
        default=SectorEstrategico.TECNOLOGIA.value,
        description="Sector estratégico de la ocupación",
        examples=[SectorEstrategico.TECNOLOGIA.value],
    )


class BrechasDataSchema(BaseModel):
    """Contrato de respuesta para la pantalla de Brechas de habilidades."""

    model_config = ConfigDict(frozen=True)

    pais: str = Field(
        ...,
        description="Código de país consultado (ARG, URY, CHL)",
        examples=[PaisCodigo.ARG.value],
    )
    sector: str | None = Field(
        None,
        description="Sector económico",
        examples=[SectorEstrategico.TECNOLOGIA.value],
    )
    ocupacion: str = Field(
        ..., description="Ocupacion analizada", examples=["desarrollador_software"]
    )
    habilidades: list[HabilidadBrechaItem] = Field(
        ..., description="Listado de habilidades para el gráfico comparativo"
    )
    metadatos: MetadatosFuente


# Envoltorio tipado de respuesta estándar para el endpoint
BrechasResponseSchema = ApiResponse[BrechasDataSchema]
