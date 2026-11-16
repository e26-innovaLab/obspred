"""Esquemas Pydantic para el módulo de métricas, gráficos y análisis comparativo."""

from typing import Literal

from pydantic import BaseModel, Field

from app.api.v1.schemas.response_schema import ApiResponse
from app.api.v1.schemas.trazabilidad_schema import TrazabilidadFuenteSchema

# ==============================================================================
# 1. Series Temporales (/metricas/series)
# ==============================================================================


class PuntoSerieDto(BaseModel):
    """Punto individual en una serie temporal histórica."""

    periodo: str = Field(..., description="Período temporal (ej. '2026-Q1').")
    valor: float | None = Field(
        None, description="Valor del indicador (null si no hay dato)."
    )
    tipo: str = Field(
        default="observado", description="Tipo de observación estadística."
    )


class SerieItemDto(BaseModel):
    """Serie temporal correspondiente a un país e indicador específico."""

    pais: str = Field(..., description="Código ISO 3166-1 alpha-3 del país.")
    indicador: str = Field(..., description="Identificador o slug del indicador.")
    nombre: str = Field(..., description="Denominación legible del indicador.")
    unidad: str = Field(..., description="Unidad de medida (ej. '%', 'avisos').")
    frecuencia: str = Field(
        default="trimestral", description="Periodicidad de la serie."
    )
    puntos: list[PuntoSerieDto] = Field(
        default_factory=list, description="Lista ordenada de puntos."
    )
    fuentes: list[TrazabilidadFuenteSchema] = Field(
        default_factory=list, description="Fuentes asociadas."
    )


class MetricasSeriesDataSchema(BaseModel):
    """Payload para endpoint de series temporales."""

    series: list[SerieItemDto] = Field(
        default_factory=list, description="Colección de series por país."
    )


MetricasSeriesResponseSchema = ApiResponse[MetricasSeriesDataSchema]


# ==============================================================================
# 2. Proyecciones Estadísticas (/metricas/proyecciones)
# ==============================================================================


class PuntoProyeccionDto(BaseModel):
    """Punto estimado a futuro con intervalo de confianza."""

    periodo: str = Field(..., description="Período futuro proyectado.")
    valor: float = Field(..., description="Valor central proyectado.")
    limite_inferior: float = Field(
        ..., description="Límite inferior del intervalo de confianza."
    )
    limite_superior: float = Field(
        ..., description="Límite superior del intervalo de confianza."
    )


class MetricasProyeccionesDataSchema(BaseModel):
    """Payload para proyecciones estadísticas según Principio 5."""

    pais: str = Field(..., description="Código ISO-3 del país.")
    indicador: str = Field(..., description="Slug del indicador.")
    unidad: str = Field(..., description="Unidad de medida.")
    historico: list[PuntoSerieDto] = Field(
        default_factory=list, description="Serie histórica de referencia."
    )
    proyeccion: list[PuntoProyeccionDto] = Field(
        default_factory=list, description="Puntos futuros proyectados."
    )
    proyectable: bool = Field(
        ..., description="Indica si se cumple la condición de serie suficiente."
    )
    motivo_no_proyectable: str | None = Field(
        None, description="Explicación si no se puede proyectar."
    )
    metodo: str = Field(default="Regresión lineal sobre serie trimestral observada")
    nivel_confianza: float = Field(
        default=0.8, description="Nivel de confianza estadística (0-1)."
    )
    periodos_historicos: int = Field(
        default=0, description="Cantidad de observaciones históricas comparables."
    )
    fuentes: list[TrazabilidadFuenteSchema] = Field(
        default_factory=list, description="Trazabilidad de la serie."
    )


MetricasProyeccionesResponseSchema = ApiResponse[MetricasProyeccionesDataSchema]


# ==============================================================================
# 3. KPIs Resumen (/metricas/kpis)
# ==============================================================================


class KpiItemDto(BaseModel):
    """Elemento individual de tarjeta KPI con variación y sparkline."""

    indicador: str = Field(..., description="Identificador único del KPI.")
    nombre: str = Field(..., description="Título legible del KPI.")
    unidad: str = Field(..., description="Unidad de medida.")
    periodo: str | None = Field(None, description="Período del último dato reportado.")
    valor: float | None = Field(
        None, description="Valor numérico en el período vigente."
    )
    periodo_anterior: str | None = Field(
        None, description="Período comparativo anterior."
    )
    valor_anterior: float | None = Field(
        None, description="Valor en el período previo."
    )
    variacion_abs: float | None = Field(
        None, description="Diferencia absoluta entre períodos."
    )
    variacion_pct: float | None = Field(
        None, description="Porcentaje de variación relativo."
    )
    tendencia: Literal["crecimiento", "estabilidad", "caida"] | None = Field(
        None, description="Dirección cualitativa."
    )
    sentido_positivo: Literal["sube", "baja"] = Field(
        default="sube", description="Indica si un incremento representa una mejora."
    )
    sparkline: list[float | None] = Field(
        default_factory=list, description="Últimos puntos para mini gráfico."
    )
    fuente: TrazabilidadFuenteSchema = Field(
        ..., description="Trazabilidad de la fuente del dato."
    )


class MetricasKpisDataSchema(BaseModel):
    """Payload para tarjetas resumen de indicadores."""

    kpis: list[KpiItemDto] = Field(
        default_factory=list, description="Listado de KPIs solicitados."
    )


MetricasKpisResponseSchema = ApiResponse[MetricasKpisDataSchema]


# ==============================================================================
# 4. Rankings (/metricas/ranking)
# ==============================================================================


class RankingItemDto(BaseModel):
    """Ítem clasificado en el ranking."""

    id: str = Field(..., description="Identificador del sector, ocupación o habilidad.")
    nombre: str = Field(..., description="Denominación legible.")
    valor: float | None = Field(None, description="Métrica de ordenamiento.")
    variacion_pct: float | None = Field(
        None, description="Variación porcentual interperíodo."
    )
    tendencia: Literal["crecimiento", "estabilidad", "caida"] | None = Field(None)


class MetricasRankingDataSchema(BaseModel):
    """Payload para rankings dimensionales."""

    dimension: str = Field(
        ..., description="Dimensión clasificada ('sector', 'ocupacion', 'habilidad')."
    )
    indicador: str = Field(..., description="Indicador evaluado.")
    unidad: str = Field(..., description="Unidad de medida.")
    periodo: str = Field(..., description="Período al que corresponde el ranking.")
    items: list[RankingItemDto] = Field(
        default_factory=list, description="Registros ordenados."
    )
    fuentes: list[TrazabilidadFuenteSchema] = Field(
        default_factory=list, description="Fuentes de los datos."
    )


MetricasRankingResponseSchema = ApiResponse[MetricasRankingDataSchema]


# ==============================================================================
# 5. Comparativa Multi-país (/metricas/comparativa)
# ==============================================================================


class ComparativaValorPaisDto(BaseModel):
    """Último valor registrado de un país para una métrica."""

    pais: str = Field(..., description="Código ISO-3 del país.")
    valor: float | None = Field(None, description="Valor del indicador.")
    periodo: str | None = Field(
        None, description="Período específico del dato reportado."
    )
    fuente: TrazabilidadFuenteSchema | None = Field(
        None, description="Fuente del dato del país."
    )


class ComparativaIndicadorDto(BaseModel):
    """Comparación de un indicador a través de múltiples países."""

    indicador: str = Field(..., description="Slug del indicador.")
    nombre: str = Field(..., description="Nombre del indicador.")
    unidad: str = Field(..., description="Unidad de medida.")
    valores: list[ComparativaValorPaisDto] = Field(default_factory=list)


class MetricasComparativaDataSchema(BaseModel):
    """Payload para tarjetas comparativas de países."""

    indicadores: list[ComparativaIndicadorDto] = Field(default_factory=list)


MetricasComparativaResponseSchema = ApiResponse[MetricasComparativaDataSchema]


# ==============================================================================
# 6. Mapa de Calor (/metricas/mapa-calor)
# ==============================================================================


class MapaCalorFilaDto(BaseModel):
    """Definición de fila en la matriz de calor."""

    id: str = Field(..., description="Slug o código de la fila (ej. sector).")
    nombre: str = Field(..., description="Denominación visual de la fila.")


class MapaCalorCeldaDto(BaseModel):
    """Celda individual de la matriz."""

    fila: str = Field(..., description="ID de la fila.")
    columna: str = Field(..., description="Código ISO-3 del país (columna).")
    valor: float | None = Field(None, description="Valor medido.")
    variacion_pct: float | None = Field(None, description="Variación porcentual.")


class MetricasMapaCalorDataSchema(BaseModel):
    """Payload para matriz sector x país."""

    indicador: str = Field(..., description="Indicador evaluado.")
    nombre: str = Field(..., description="Nombre del indicador.")
    unidad: str = Field(..., description="Unidad de medida.")
    periodo: str = Field(..., description="Período representativo.")
    filas: list[MapaCalorFilaDto] = Field(default_factory=list)
    columnas: list[str] = Field(
        default_factory=list, description="Lista de países ISO-3."
    )
    celdas: list[MapaCalorCeldaDto] = Field(default_factory=list)
    fuentes: list[TrazabilidadFuenteSchema] = Field(default_factory=list)


MetricasMapaCalorResponseSchema = ApiResponse[MetricasMapaCalorDataSchema]
