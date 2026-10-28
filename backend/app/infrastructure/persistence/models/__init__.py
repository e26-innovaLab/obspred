"""Modelos de datos relacionales basados en SQLAlchemy."""

from app.infrastructure.persistence.models.brecha_model import HabilidadBrechaModel
from app.infrastructure.persistence.models.fuente import FuenteModel
from app.infrastructure.persistence.models.indicador import IndicadorModel

__all__ = [
    "IndicadorModel",
    "FuenteModel",
    "HabilidadBrechaModel",
]
