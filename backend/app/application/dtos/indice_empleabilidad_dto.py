"""Objetos de transferencia de datos (DTOs) para el Índice de Empleabilidad."""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class DimensionIndiceDTO:
    """DTO representativo de una dimensión ponderada del índice."""

    nombre: str
    valor: float
    peso: float
    descripcion: str | None = None


@dataclass(frozen=True)
class EvolucionIndicePuntoDTO:
    """DTO representativo de un punto en la evolución temporal del índice."""

    periodo: str
    valor: float


@dataclass(frozen=True)
class IndiceEmpleabilidadDTO:
    """DTO desacoplado con la respuesta integral del Índice de Empleabilidad."""

    ocupacion_id: str
    ocupacion_nombre: str
    score: float
    nivel: str
    dimensiones: list[DimensionIndiceDTO]
    tipo: str
    fuente: str
    fecha_actualizacion: date
    metodologia: str
    pais: str | None = None
    sector: str | None = None
    periodo: str | None = None
    evolucion: list[EvolucionIndicePuntoDTO] = field(default_factory=list)


@dataclass(frozen=True)
class OcupacionRankingDTO:
    """DTO representativo de una fila de ocupación en el ranking."""

    ocupacion_id: str
    nombre: str
    puestos_disponibles: int | None
    indice_empleabilidad: float
    pais: str
    fuente: str
