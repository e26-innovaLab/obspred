"""DTOs para operaciones de sincronización e ingesta de datos externos."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExternalSyncResultDTO(BaseModel):
    """Resultado estructurado de una sincronización de servicio externo.

    Attributes:
        source: Denominación de la fuente externa sincronizada.
        status: Estado final de la operación ('success', 'partial', 'failed').
        total_fetched: Cantidad total de registros obtenidos desde el origen remoto.
        total_persisted: Cantidad de registros persistidos en la base de datos.
        execution_time_seconds: Duración total de la sincronización en segundos.
        countries_synced: Lista de códigos de países procesados.
        indicators_synced: Lista de claves de indicadores procesados.
        error_message: Detalle del error en caso de fallo.
    """

    model_config = ConfigDict(frozen=True)

    source: str = Field(
        ...,
        description="Identificador o denominación de la fuente oficial",
    )
    status: str = Field(
        ...,
        description="Estado de la sincronización: 'success', 'partial' o 'failed'",
    )
    total_fetched: int = Field(
        ...,
        description="Total de registros extraídos del servicio externo",
    )
    total_persisted: int = Field(
        ...,
        description="Total de registros persistidos o actualizados en base de datos",
    )
    execution_time_seconds: float = Field(
        ...,
        description="Tiempo transcurrido en segundos",
    )
    countries_synced: List[str] = Field(
        default_factory=list,
        description="Países involucrados en la extracción",
    )
    indicators_synced: List[str] = Field(
        default_factory=list,
        description="Indicadores procesados en la extracción",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Mensaje descriptivo en caso de error durante la ejecución",
    )
