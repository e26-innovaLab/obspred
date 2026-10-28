from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import (
    ApiResponse,
)


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
        opulate_by_name=True,
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


class BrechasDataSchema(BaseModel):
    """Contrato de respuesta para la pantalla de Brechas de habilidades."""

    model_config = ConfigDict(frozen=True)

    pais: str = Field(
        ..., description="Código de país consultado (ARG, URY, CHL)", examples=["ARG"]
    )
    sector: str | None = Field(
        None, description="Sector económico", examples=["Tecnologias"]
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
