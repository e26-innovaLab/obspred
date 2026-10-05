"""Entidad de dominio para indicadores de estudio pedagógico."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class StudyIndicator:
    """Representa un indicador socioeconómico o laboral en el dominio.

    Attributes:
        id: Identificador único del indicador.
        name: Nombre descriptivo del indicador.
        country: Código del país (AR, CL, UY).
        sector: Sector económico asociado (Tecnología, Salud, etc.).
        value: Valor numérico actual del indicador.
        unit: Unidad de medida (%, USD, puestos).
        source: Fuente oficial del dato (INDEC, INE, etc.).
        updated_at: Fecha y hora de la última actualización.
    """

    id: str
    name: str
    country: str
    sector: str
    value: float
    unit: str
    source: str
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Inicializa valores por defecto posteriores a la construcción."""
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
