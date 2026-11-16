"""Esquemas Pydantic para el módulo de tendencias, series temporales y proyecciones."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.response_schema import ApiResponse


class TipoDato(StrEnum):
    """Clasificación del tipo de dato en la serie temporal."""

    HISTORICO = "historico"
    PROYECCION = "proyeccion"


class PuntoSerie(BaseModel):
    """Punto individual en la serie temporal histórica."""

    model_config = ConfigDict(frozen=True)

    periodo: str = Field(..., description="Período temporal (ej. 'T1 2025')")
    valor: float = Field(..., description="Magnitud numérica registrada")
    es_destacado: bool = Field(
        default=False,
        description="Indicador de punto singular o cambio relevante para la UI",
    )


class PuntoProyeccion(BaseModel):
    """Punto estimado con intervalo de confianza proyectado."""

    model_config = ConfigDict(frozen=True)

    periodo: str = Field(..., description="Período proyectado")
    valor_estimado: float = Field(..., description="Valor puntual estimado")
    valor_inferior: float | None = Field(
        default=None, description="Límite inferior del intervalo de confianza"
    )
    valor_superior: float | None = Field(
        default=None, description="Límite superior del intervalo de confianza"
    )


class CambioSignificativo(BaseModel):
    """Alerta o variación relevante detectada en un período."""

    model_config = ConfigDict(frozen=True)

    periodo: str = Field(..., description="Período en el que ocurrió el cambio")
    titulo: str = Field(..., description="Título sintético de la variación")
    descripcion: str = Field(..., description="Detalle explicativo del evento")
    tipo_alerta: str | None = Field(
        default="info", description="Clasificación visual de severidad"
    )


class MetadatosFuente(BaseModel):
    """Información de trazabilidad del origen del dato según Principio 3."""

    model_config = ConfigDict(frozen=True)

    fuente: str = Field(..., description="Organismo o fuente proveedora")
    fecha: str = Field(..., description="Fecha de publicación o corte")
    metodologia: str | None = Field(
        default=None, description="Metodología aplicada para el cálculo"
    )


class TendenciasDataSchema(BaseModel):
    """Payload de datos con series históricas, proyecciones y cambios significativos."""

    model_config = ConfigDict(frozen=True)

    pais: str = Field(..., description="Nombre del país o código ISO")
    sector: str = Field(..., description="Sector de actividad económica")
    ocupacion: str = Field(..., description="Categoría u ocupación laboral")
    indicador: str = Field(..., description="Tipo de indicador consultado")
    serie_historica: list[PuntoSerie] = Field(
        ..., description="Puntos observados cronológicamente"
    )
    cambios_significativos: list[CambioSignificativo] = Field(
        ..., description="Eventos o saltos de tendencia identificados"
    )
    proyeccion: list[PuntoProyeccion] = Field(
        ..., description="Puntos proyectados a futuro"
    )
    metadatos_historico: MetadatosFuente = Field(
        ..., description="Trazabilidad del segmento histórico"
    )
    metadatos_proyeccion: MetadatosFuente = Field(
        ..., description="Trazabilidad de la metodología proyectiva"
    )


# Alias para retrocompatibilidad
TendenciasResponse = TendenciasDataSchema

# Respuesta canónica estándar bajo el Envelope Pattern ApiResponse
TendenciasResponseSchema = ApiResponse[TendenciasDataSchema]
