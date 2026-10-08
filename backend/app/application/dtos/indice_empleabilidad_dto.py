"""Objetos de transferencia de datos (DTOs) para el Índice de Empleabilidad."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class DimensionIndiceDTO:
    """DTO representativo de una dimensión ponderada del índice."""

    nombre: str
    valor: float
    peso: float
    descripcion: Optional[str] = None


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
    dimensiones: List[DimensionIndiceDTO]
    tipo: str
    fuente: str
    fecha_actualizacion: date
    metodologia: str
    pais: Optional[str] = None
    sector: Optional[str] = None
    periodo: Optional[str] = None
    evolucion: List[EvolucionIndicePuntoDTO] = field(default_factory=list)
