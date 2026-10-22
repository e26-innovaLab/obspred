"""Esquemas Pydantic para el subsistema de Series Temporales Históricas."""

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ResponseMeta


class PuntoSerieItemSchema(BaseModel):
    """Representación serializable de un punto temporal individual."""

    model_config = ConfigDict(from_attributes=True)

    periodo: str = Field(
        ...,
        description="Período o marca temporal del dato (ej. '2024', '2024-Q1').",
        examples=["2024-03"],
    )
    valor: float = Field(
        ...,
        description="Valor cuantitativo del indicador observado en el período.",
        examples=[7.5],
    )
    tipo: str = Field(
        default="observado",
        description="Clasificación metodológica del dato.",
        examples=["observado"],
    )
    fuente: str = Field(
        default="",
        description="Organismo o entidad de origen del dato.",
        examples=["INE"],
    )


class SerieHistoricaDataSchema(BaseModel):
    """Estructura de datos transportada en la propiedad 'data' de la respuesta."""

    model_config = ConfigDict(from_attributes=True)

    pais: str = Field(
        ...,
        description="Código ISO3 del país consultado.",
        examples=["ARG"],
    )
    indicador: str = Field(
        ...,
        description="Identificador estándar del indicador analizado.",
        examples=["tasa_desempleo"],
    )
    sector: str | None = Field(
        default=None,
        description="Sector económico específico si aplicó filtro.",
        examples=["tecnologia"],
    )
    total_observaciones: int = Field(
        ...,
        description="Cantidad total de observaciones contenidas en la serie.",
        examples=[21],
    )
    observaciones: list[PuntoSerieItemSchema] = Field(
        default_factory=list,
        description="Listado cronológico de observaciones de la serie.",
    )


class SeriesHistoricasFilterSchema(BaseModel):
    """Parámetros query para el filtrado de series históricas."""

    pais: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Código ISO3 del país (ej. 'ARG', 'CHL', 'URY').",
        examples=["ARG"],
    )
    indicador: str = Field(
        ...,
        min_length=1,
        description="Identificador del indicador socioeconómico o laboral.",
        examples=["tasa_desempleo"],
    )
    sector: str | None = Field(
        default=None,
        description="Sector productivo o laboral (opcional).",
    )
    desde: str | None = Field(
        default=None,
        description="Período inicial del rango temporal.",
        examples=["2020"],
    )
    hasta: str | None = Field(
        default=None,
        description="Período final del rango temporal.",
        examples=["2024"],
    )


class SeriesHistoricasResponseSchema(BaseModel):
    """Contrato final devuelto por el endpoint de series históricas."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(
        default=True,
        description="Indica si la solicitud fue exitosa.",
    )
    status_code: int = Field(
        default=200,
        description="Código de estado HTTP de la respuesta.",
    )
    message: str = Field(
        default="Serie histórica recuperada con éxito.",
        description="Mensaje legible para el usuario o cliente.",
    )
    data: SerieHistoricaDataSchema | None = Field(
        default=None,
        description="Contenido principal con las observaciones de la serie.",
    )
    meta: ResponseMeta | None = Field(
        default=None,
        description="Metadatos contextuales sobre el total de registros y filtros.",
    )
    errors: list[dict[str, str | None]] | None = Field(
        default=None,
        description="Listado de detalles de error en caso de fallo.",
    )


# Asegura que Pydantic v2 resuelva cualquier referencia diferida en tiempo de carga
SeriesHistoricasResponseSchema.model_rebuild()
