"""Objetos de Transferencia de Datos (DTOs) para el caso de estudio de indicadores."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateStudyIndicatorDTO:
    """Datos de entrada necesarios para registrar un nuevo indicador.

    Attributes:
        name: Nombre del indicador.
        country: Código de país (AR, CL, UY).
        sector: Sector económico.
        value: Valor numérico inicial.
        unit: Unidad de medida.
        source: Fuente oficial del dato.
    """

    name: str
    country: str
    sector: str
    value: float
    unit: str
    source: str


@dataclass
class StudyIndicatorFilterDTO:
    """Filtros aplicables a la consulta de indicadores.

    Attributes:
        country: Filtro por código de país.
        sector: Filtro por sector.
    """

    country: Optional[str] = None
    sector: Optional[str] = None
