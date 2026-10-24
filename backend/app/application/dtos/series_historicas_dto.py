"""DTOs para la consulta y respuesta de series temporales históricas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsultaSerieHistoricaDTO:
    """Parámetros de entrada validados para consultar una serie."""

    pais: str
    indicador: str
    sector: str | None = None
    periodo_desde: str | None = None
    periodo_hasta: str | None = None


@dataclass(frozen=True)
class PuntoSerieDTO:
    """Representación de un punto temporal individual en la capa de aplicación."""

    periodo: str
    valor: float
    tipo: str
    fuente: str


@dataclass(frozen=True)
class SerieHistoricaResultadoDTO:
    """Resultado estructurado retornado por el caso de uso."""

    pais: str
    indicador: str
    sector: str | None
    total_observaciones: int
    observaciones: list[PuntoSerieDTO]
